# -*- coding: utf-8 -*-
"""SVG → PNG 导出：用本机 Edge headless 截图（本机无 rsvg-convert 的替代链）。
用法: uv run python export_png.py <in.svg> [out.png] [目标宽px，默认1600]
依赖: Windows 上的 Edge（自动探测标准安装路径）；失败时打印排查线索并非零退出。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def 找浏览器():
    候选 = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for p in 候选:
        if os.path.isfile(p):
            return p
    for 名 in ("msedge", "chrome", "chromium"):
        w = shutil.which(名)
        if w:
            return w
    return None


def 读viewbox(svg: Path):
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


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    源 = Path(sys.argv[1]).resolve()
    if not 源.is_file():
        print(f"Error: 找不到 {源}")
        sys.exit(1)
    输出 = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else 源.with_suffix(".png")
    输出.parent.mkdir(parents=True, exist_ok=True)  # Edge 不会替不存在的目录建父目录
    目标宽 = int(sys.argv[3]) if len(sys.argv) > 3 else 1600

    浏览器 = 找浏览器()
    if not 浏览器:
        print("Error: 未找到 Edge/Chrome。装其一，或改走浏览器人工截图。")
        sys.exit(2)

    vw, vh = 读viewbox(源)
    高 = max(1, round(目标宽 * vh / vw))

    临时profile = tempfile.mkdtemp(prefix="svg2png-")
    try:
        壳 = Path(临时profile) / "wrap.html"
        壳.write_text(
            '<!doctype html><meta charset="utf-8">'
            "<style>html,body{margin:0;padding:0}img{width:100%;display:block}</style>"
            f'<img src="{源.as_uri()}">',
            encoding="utf-8",
        )
        命令 = [
            浏览器, "--headless=new", "--disable-gpu", "--no-first-run",
            "--hide-scrollbars",
            f"--user-data-dir={临时profile}",
            f"--window-size={目标宽},{高}",
            f"--screenshot={输出}",
            壳.as_uri(),
        ]
        import time
        try:
            r = subprocess.run(命令, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            print("Error: Edge headless 超时(90s)")
            sys.exit(3)
        for _ in range(30):
            if 输出.is_file() and 输出.stat().st_size > 0:
                break
            time.sleep(0.5)
        if not 输出.is_file() or 输出.stat().st_size == 0:
            print(f"Error: 未生成 PNG。exit={r.returncode}")
            print((r.stderr or r.stdout or "")[:800])
            sys.exit(4)
        print(f"✓ {输出}  ({输出.stat().st_size} bytes, {目标宽}x{高})")
    finally:
        shutil.rmtree(临时profile, ignore_errors=True)


if __name__ == "__main__":
    main()
