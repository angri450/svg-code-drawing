# -*- coding: utf-8 -*-
"""三层布景一键合成：底图 + 配件（自动抠白底）+ 线稿层 → 单文件 SVG [+PNG]。

MOSS 版：配件默认不做去水印处理；素材确实带水印时显式加 --remove-watermark。
全程零看图：自检全用数字报告（不透明占比/包围盒/尺寸），人只看数字。
用法:
  uv run python moss_compose.py --bg 底.png --svg 线稿.svg --out 成品.svg [--png 成品.png] [--wide 1600]
    --prop 配件.png:x:y:h   可多次；x/y/h 为线稿 viewBox 单元（不写 x:y:h 则自动居中底部，h=60）
    --remove-watermark       去掉配件右下水印区（默认不做）
    --watermark-box x1,y1,x2,y2  自定义水印区，像素坐标，自动开启去水印
    --renderer auto|resvg|rsvg|chrome  PNG 导出渲染器，默认 auto（resvg → rsvg → chrome）
示例:
  uv run --with opencv-python-headless --with numpy --with resvg-py python moss_compose.py \
    --bg bg.png --svg pid.svg --out final.svg --png final.png \
    --prop worker.png:612:373:72 --prop cat.png:238:396:46
  uv run python moss_compose.py --bg bg.png --svg pid.svg --out final.svg --remove-watermark
"""
import argparse
import base64
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


def 抠白裁边(
    src: Path,
    remove_watermark: bool = False,
    watermark_box: Optional[tuple[int, int, int, int]] = None,
) -> tuple[bytes, int, int, float]:
    """近白连通域抠底 + 可选去右下水印 + alpha bbox 裁边。返回 (PNG字节, 宽, 高, 不透明占比)。"""
    bgr = cv2.imread(str(src))
    if bgr is None:
        raise SystemExit(f"Error: 读不到配件图 {src}")
    h, w = bgr.shape[:2]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    near_white = (hsv[:, :, 2] > 228) & (hsv[:, :, 1] < 30)
    num, lab = cv2.connectedComponents(near_white.astype(np.uint8), connectivity=4)
    border = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    border.discard(0)
    bg = np.isin(lab, list(border))
    alpha = cv2.GaussianBlur(np.where(bg, 0, 255).astype(np.uint8), (3, 3), 0)

    if remove_watermark:
        if watermark_box is None:
            x1, y1, x2, y2 = int(w * 0.80), int(h * 0.93), w, h
        else:
            x1, y1, x2, y2 = watermark_box
            if not (0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h):
                raise SystemExit(
                    f"Error: watermark-box {watermark_box} 超出配件图 {w}x{h}"
                )
        # 扩 2px，吃掉高斯模糊在边界留下的半透明晕边，避免裁边时把水印区又包回来
        halo = 2
        alpha[max(0, y1 - halo):min(h, y2 + halo), max(0, x1 - halo):min(w, x2 + halo)] = 0

    out = np.dstack([bgr, alpha])
    ys, xs = np.where(alpha > 12)
    if not len(xs):
        raise SystemExit(f"Error: {src.name} 抠图后全透明（不透明占比 0），配件生成有问题")
    pad = 6
    out = out[max(0, ys.min() - pad):min(h, ys.max() + pad), max(0, xs.min() - pad):min(w, xs.max() + pad)]
    ok, buf = cv2.imencode(".png", out)
    if not ok:
        raise SystemExit(f"Error: {src.name} PNG 编码失败")
    占比 = float((out[:, :, 3] > 128).mean())
    return buf.tobytes(), out.shape[1], out.shape[0], 占比


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def 水印框(value: str) -> tuple[int, int, int, int]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("watermark-box 需要 x1,y1,x2,y2 四个整数")
    try:
        box = tuple(int(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError("watermark-box 必须是整数像素坐标")
    return box  # type: ignore[return-value]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--svg", required=True, help="线稿 SVG（会被剥掉自己的纯色底）")
    ap.add_argument("--prop", action="append", default=[], help="配件图[:x:y:h]，可多次")
    ap.add_argument("--out", required=True)
    ap.add_argument("--png", default=None)
    ap.add_argument("--wide", type=int, default=1600)
    ap.add_argument(
        "--renderer",
        choices=["auto", "resvg", "rsvg", "chrome"],
        default="auto",
        help="PNG 导出渲染器，默认 auto（resvg → rsvg → chrome）",
    )
    ap.add_argument(
        "--remove-watermark",
        action="store_true",
        help="去掉配件右下水印区（默认不做；默认区域为右下 20%% 宽 × 7%% 高）",
    )
    ap.add_argument(
        "--watermark-box",
        type=水印框,
        default=None,
        metavar="x1,y1,x2,y2",
        help="自定义水印区，像素坐标，自动开启去水印",
    )
    args = ap.parse_args()

    remove_watermark = args.remove_watermark or args.watermark_box is not None

    线稿 = Path(args.svg).read_text(encoding="utf-8")
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', 线稿)
    if not vb:
        raise SystemExit("Error: 线稿缺 viewBox")
    W, H = float(vb.group(1)), float(vb.group(2))

    inner = re.sub(r"^.*?<svg[^>]*>", "", 线稿, flags=re.S).replace("</svg>", "")
    inner = re.sub(r'<rect[^>]*fill="#[fF]{6}"[^>]*/>', "", inner, count=1)

    底 = Path(args.bg).read_bytes()
    图层 = [f'<image href="data:image/png;base64,{b64(底)}" x="0" y="0" width="{W:g}" '
            f'height="{H:g}" preserveAspectRatio="xMidYMid slice"/>']

    print(f"画布 {W:g}×{H:g}" + ("（去水印）" if remove_watermark else ""))
    for spec in args.prop:
        # 从右往左剥 :x:y:h——Windows 盘符 C: 也在冒号，从左切会碎
        parts = spec.rsplit(":", 3)
        if len(parts) == 4 and all(v.replace(".", "", 1).isdigit() for v in parts[1:]):
            路径, px, py, phh = Path(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
        else:
            路径, px, py, phh = Path(spec), None, None, 60.0
        png字节, pw, ph, 占比 = 抠白裁边(
            路径,
            remove_watermark=remove_watermark,
            watermark_box=args.watermark_box,
        )
        if 占比 < 0.10:
            raise SystemExit(f"Error: {路径.name} 不透明占比 {占比:.0%} < 10%，抠漏了，别用")
        if px is not None:
            pass
        elif px is None:
            px, py = W / 2 - phh * pw / ph / 2, H - phh - 10
        pww = phh * pw / ph
        图层.append(f'<image href="data:image/png;base64,{b64(png字节)}" x="{px:g}" y="{py:g}" '
                    f'width="{pww:g}" height="{phh:g}"/>')
        print(f"配件 {路径.name}: {pw}×{ph} 抠后 不透明={占比:.0%} → 放置 x={px:g} y={py:g} {pww:.1f}×{phh:g}")

    图层.append(inner)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" width="{W:g}" height="{H:g}">\n'
           + "\n".join(图层) + "\n</svg>\n")
    p = Path(args.out)
    p.write_text(out, encoding="utf-8")
    元素数 = out.count("<") // 2
    print(f"✓ {p}  {p.stat().st_size // 1024} KB  含配件 {len(args.prop)} 个")

    if args.png:
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "export_png.py"),
                            str(p), args.png, str(args.wide), "--renderer", args.renderer],
                           capture_output=True, text=True)
        print((r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else f"png exit={r.returncode}")


if __name__ == "__main__":
    main()
