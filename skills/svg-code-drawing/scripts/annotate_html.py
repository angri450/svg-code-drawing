#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一张渲染图打成单文件标注页：图片内嵌，框选/点选，导出 JSON。

用法:
  python annotate_html.py 图.png [--out 图.review.html] [--title 图稿标注] [--quality 92] [--png]

特点:
  - 不依赖服务器、端口、外链；HTML 自带图片，双击或发布成链接即可打开。
  - 标注存浏览器 localStorage，可导出/复制 JSON，也可以再导入。
  - 坐标按图片实际像素记录，和 SVG viewBox 对齐，可直接回改线稿。
"""
import argparse
import base64
import html
import io
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: 需要 Pillow。先 pip install pillow，或用 uv run --with pillow 跑。")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "annotate_template.html"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", help="输入图片（PNG/JPG/WebP 等）")
    ap.add_argument("--out", default=None, help="输出 HTML，默认 <图片名>.review.html")
    ap.add_argument("--title", default="图稿标注", help="页面标题")
    ap.add_argument("--quality", type=int, default=92, help="JPEG 质量，默认 92")
    ap.add_argument("--png", action="store_true", help="内嵌 PNG（无损，但文件更大）")
    args = ap.parse_args()

    src = Path(args.image).resolve()
    if not src.is_file():
        print(f"Error: 找不到 {src}")
        sys.exit(1)
    if not TEMPLATE.is_file():
        print(f"Error: 缺少模板 {TEMPLATE}")
        sys.exit(1)

    im = Image.open(src)
    im.load()
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    width, height = im.size

    buf = io.BytesIO()
    if args.png:
        im.save(buf, "PNG", optimize=True)
        mime, ext = "image/png", "PNG"
    else:
        im.save(buf, "JPEG", quality=args.quality, subsampling=1, optimize=True)
        mime, ext = "image/jpeg", "JPEG"
    data_uri = f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    tpl = tpl.replace("__TITLE__", html.escape(args.title))
    tpl = tpl.replace("__WIDTH__", str(width)).replace("__HEIGHT__", str(height))
    tpl = tpl.replace("__IMAGE_NAME_JSON__", json.dumps(src.name, ensure_ascii=False))
    tpl = tpl.replace("__IMAGE_DATA__", data_uri)

    out = Path(args.out).resolve() if args.out else src.with_suffix(".review.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
    print(f"✓ {out}  ({out.stat().st_size // 1024} KB, {width}x{height}, {ext})")
    print("  浏览器打开或发布这个 HTML；标注后点“复制 JSON”或“导出 JSON”。")


if __name__ == "__main__":
    main()
