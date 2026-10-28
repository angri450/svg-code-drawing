# -*- coding: utf-8 -*-
"""SVG → PNG 导出：resvg → rsvg-convert → cairosvg → Chromium/Edge 自动降级。

用法:
  python export_png.py <in.svg> [out.png] [目标宽px，默认1600] [--renderer auto|resvg|rsvg|cairo|chrome]

渲染器:
  resvg    优先 resvg 可执行文件，其次 Python 包 resvg-py（pip install resvg-py）
  rsvg     librsvg 的 rsvg-convert（apt install librsvg2-bin）
  cairo    Python 包 cairosvg（pip install cairosvg），纯 Python 无外部依赖
  chrome   Edge/Chrome headless 截图
  auto     按 resvg → rsvg → cairo → chrome 顺序尝试

cairosvg 单独用时有个坑：它算 SVG marker 的朝向角时，路径只有一个点
（起点终点重合）会算出 None，接着 rotate(None) 崩掉。降级路径里先把这类
退化 path 的 marker 属性摘掉，其余图形照常渲染。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def find_browser():
    候选 = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in 候选:
        if os.path.isfile(p):
            return p
    for 名 in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge", "chrome"):
        w = shutil.which(名)
        if w:
            return w
    return None


def read_viewbox(svg: Path):
    文 = svg.read_text(encoding="utf-8", errors="replace")[:2000]
    m = re.search(r'viewBox="([\d.\-\s]+)"', 文)
    if m:
        parts = [float(x) for x in m.group(1).split()]
        if len(parts) == 4:
            return parts[2], parts[3]
    w = re.search(r'width="(\d+(?:\.\d+)?)"', 文)
    h = re.search(r'height="(\d+(?:\.\d+)?)"', 文)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    return 960.0, 600.0


def render_resvg(svg: Path, out: Path, width: int, height: int) -> bool:
    exe = shutil.which("resvg")
    if exe:
        try:
            r = subprocess.run(
                [exe, "--width", str(width), str(svg), str(out)],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0 and out.is_file() and out.stat().st_size > 0:
                print(f"✓ {out}  ({out.stat().st_size} bytes, {width}x{height}, resvg)")
                return True
            print(f"  resvg 失败: {(r.stderr or r.stdout).strip()[:220]}")
        except Exception as e:
            print(f"  resvg 失败: {e}")

    try:
        import resvg_py
    except ImportError:
        return False

    try:
        vw, _ = read_viewbox(svg)
        zoom = width / vw
        png = bytes(resvg_py.svg_to_bytes(svg_path=str(svg), zoom=zoom))
        out.write_bytes(png)
        if out.is_file() and out.stat().st_size > 0:
            print(f"✓ {out}  ({out.stat().st_size} bytes, {width}x{height}, resvg-py)")
            return True
    except Exception as e:
        print(f"  resvg-py 失败: {e}")
    return False


def render_rsvg(svg: Path, out: Path, width: int, height: int) -> bool:
    exe = shutil.which("rsvg-convert")
    if not exe:
        return False
    try:
        r = subprocess.run(
            [exe, "-w", str(width), "-o", str(out), str(svg)],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0 and out.is_file() and out.stat().st_size > 0:
            print(f"✓ {out}  ({out.stat().st_size} bytes, {width}x{height}, rsvg-convert)")
            return True
        print(f"  rsvg-convert 失败: {(r.stderr or r.stdout).strip()[:220]}")
    except Exception as e:
        print(f"  rsvg-convert 失败: {e}")
    return False


def 摘掉退化箭头(svg: Path) -> Path:
    """把只有起点、终点重合的 path 上的 marker 属性去掉，另存一份。

    cairosvg 算 marker 朝向角时，单点 path 算不出角度，rotate(None) 直接崩。
    这种 path 本身画不出箭头，摘掉 marker 不影响画面。
    """
    文本 = svg.read_text(encoding="utf-8", errors="replace")

    def 判断(match: re.Match) -> str:
        整段 = match.group(0)
        d = re.search(r'\sd="([^"]*)"', 整段)
        if not d:
            return 整段
        点 = re.findall(r'-?\d+(?:\.\d+)?', d.group(1))
        if len(点) < 2:
            return 整段
        # 只有一组坐标即 M x,y：起终点重合，算不出朝向角
        if len(点) == 2:
            return re.sub(r'\smarker-(start|mid|end)="[^"]*"', "", 整段)
        return 整段

    改后 = re.sub(r'<path\b[^>]*/?>', 判断, 文本)
    if 改后 == 文本:
        return svg
    临时 = Path(tempfile.mkdtemp(prefix="svg2png-")) / "no-degenerate-marker.svg"
    临时.write_text(改后, encoding="utf-8")
    return 临时


def render_cairosvg(svg: Path, out: Path, width: int, height: int) -> bool:
    try:
        import cairosvg
    except ImportError:
        return False

    for 源 in (svg, 摘掉退化箭头(svg)):
        try:
            cairosvg.svg2png(url=str(源), write_to=str(out), output_width=width)
            if out.is_file() and out.stat().st_size > 0:
                print(f"✓ {out}  ({out.stat().st_size} bytes, {width}x{height}, cairosvg)")
                return True
        except Exception as e:
            print(f"  cairosvg 失败: {type(e).__name__}: {e}")
        if 源 is not svg:
            continue
    return False


def render_chrome(svg: Path, out: Path, width: int, height: int) -> bool:
    浏览器 = find_browser()
    if not 浏览器:
        return False

    临时profile = tempfile.mkdtemp(prefix="svg2png-")
    try:
        壳 = Path(临时profile) / "wrap.html"
        壳.write_text(
            '<!doctype html><meta charset="utf-8">'
            "<style>html,body{margin:0;padding:0}img{width:100%;display:block}</style>"
            f'<img src="{svg.as_uri()}">',
            encoding="utf-8",
        )
        命令 = [
            浏览器, "--headless=new", "--disable-gpu", "--no-first-run",
            "--hide-scrollbars",
            f"--user-data-dir={临时profile}",
            f"--window-size={width},{height}",
            f"--screenshot={out}",
            壳.as_uri(),
        ]
        try:
            r = subprocess.run(命令, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            print("  chrome 失败: 超时(90s)")
            return False
        for _ in range(30):
            if out.is_file() and out.stat().st_size > 0:
                break
            time.sleep(0.5)
        if out.is_file() and out.stat().st_size > 0:
            print(f"✓ {out}  ({out.stat().st_size} bytes, {width}x{height}, chrome)")
            return True
        print(f"  chrome 失败: exit={r.returncode} {(r.stderr or r.stdout).strip()[:220]}")
        return False
    except Exception as e:
        print(f"  chrome 失败: {e}")
        return False
    finally:
        shutil.rmtree(临时profile, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("svg", help="输入 SVG")
    ap.add_argument("png", nargs="?", help="输出 PNG，默认与 SVG 同名")
    ap.add_argument("width", nargs="?", type=int, default=1600, help="目标宽 px，默认 1600")
    ap.add_argument(
        "--renderer",
        choices=["auto", "resvg", "rsvg", "cairo", "chrome"],
        default="auto",
        help="渲染器，默认 auto（resvg → rsvg → cairo → chrome）",
    )
    args = ap.parse_args()

    源 = Path(args.svg).resolve()
    if not 源.is_file():
        print(f"Error: 找不到 {源}")
        sys.exit(1)
    输出 = Path(args.png).resolve() if args.png else 源.with_suffix(".png")
    输出.parent.mkdir(parents=True, exist_ok=True)

    vw, vh = read_viewbox(源)
    if vw <= 0 or vh <= 0:
        print("Error: viewBox 宽高无效")
        sys.exit(1)
    高 = max(1, round(args.width * vh / vw))

    顺序 = ["resvg", "rsvg", "cairo", "chrome"] if args.renderer == "auto" else [args.renderer]
    for 名称 in 顺序:
        if 名称 == "resvg":
            ok = render_resvg(源, 输出, args.width, 高)
        elif 名称 == "rsvg":
            ok = render_rsvg(源, 输出, args.width, 高)
        elif 名称 == "cairo":
            ok = render_cairosvg(源, 输出, args.width, 高)
        else:
            ok = render_chrome(源, 输出, args.width, 高)
        if ok:
            return

    print("Error: 没有可用的 SVG 渲染器。至少装一个：")
    print("  pip install resvg-py")
    print("  sudo apt install librsvg2-bin")
    print("  pip install cairosvg")
    print("  或安装 Chromium/Chrome")
    sys.exit(2)


if __name__ == "__main__":
    main()
