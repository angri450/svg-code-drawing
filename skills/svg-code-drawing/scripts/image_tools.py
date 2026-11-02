# -*- coding: utf-8 -*-
"""图像工具集：读图、裁切、裁白边、缩放、标注。

PIL 的胶水活都封好：EXIF 方向摆正、按扩展名选编码器、中文标注字体查找、
坐标边界检查、输出命名。省掉每次现写这几行。

用法:
  python image_tools.py info 图.png
  python image_tools.py crop 图.png --box 100,100,500,400 [--norm] [--out 出.png]
  python image_tools.py trim 图.png [--pad 8] [--tolerance 8] [--out 出.png]
  python image_tools.py resize 图.png --width 800 [--out 出.png]
  python image_tools.py annotate 图.png --box 100,100,500,400[:标签[:#ff0000]] ...

依赖 PIL：
  uv run --with pillow python image_tools.py ...

基础工具（open_image、save_image、norm_to_pixel、draw_boxes、find_font、
default_output_path）吸收自 Qwen-MM-Plugins（Apache-2.0，github.com/QwenLM/
Qwen-MM-Plugins 的 src/shared/image.py、src/shared/content.py、
src/capabilities/core/producers/），改造为命令行工具。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# 多框标注的默认配色，轮流用。
COLORS = [
    (255, 0, 0),
    (0, 128, 255),
    (0, 160, 0),
    (255, 128, 0),
    (160, 0, 200),
    (0, 160, 160),
    (200, 0, 100),
    (90, 90, 90),
]


def 错误(msg: str) -> None:
    sys.stderr.write(f"Error: {msg}\n")
    sys.exit(1)


def 检查PIL() -> None:
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "需要 PIL。用 uv 运行：\n"
            "  uv run --with pillow python image_tools.py ...\n"
        )
        sys.exit(2)


# ---------- 基础工具 ----------

def open_image(path: str):
    """打开图片，按 EXIF 方向摆正；EXIF 读不了就保留存储的像素。"""
    from PIL import Image, ImageOps

    img = Image.open(path)
    try:
        orientation = img.getexif().get(0x0112, 1)
    except Exception:
        return img
    if orientation in range(2, 9):
        img = ImageOps.exif_transpose(img)
    return img


_EXT_FORMAT = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "tiff": "TIFF",
    "tif": "TIFF",
}


def save_image(img, output_path: str, quality: int = 95) -> None:
    """按扩展名选编码器保存。JPEG 只吃 RGB/L，其他模式先转，不然保存报错。"""
    ext = os.path.splitext(output_path)[1].lower().lstrip(".")
    fmt = _EXT_FORMAT.get(ext, "PNG")
    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    save_kwargs = {"quality": quality} if fmt == "JPEG" else {}
    img.save(output_path, format=fmt, **save_kwargs)


def default_output_path(src: str, suffix: str) -> str:
    """同目录加后缀：foo.png → foo_cropped.png。"""
    p = Path(src)
    return str(p.with_stem(p.stem + suffix))


def norm_to_pixel(bbox: list[int], img_w: int, img_h: int) -> list[int]:
    """0 到 1000 归一化框转像素坐标。"""
    nx1, ny1, nx2, ny2 = bbox
    return [
        round(nx1 / 1000 * img_w),
        round(ny1 / 1000 * img_h),
        round(nx2 / 1000 * img_w),
        round(ny2 / 1000 * img_h),
    ]


def find_font(size: int):
    """找支持中文的字体，找不到就用系统默认。"""
    from PIL import ImageFont

    patterns = [
        "/usr/share/fonts/**/Noto*CJK*.ttc",
        "/usr/share/fonts/**/wqy*.ttc",
        "/usr/share/fonts/**/Noto*CJK*.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/**/*DejaVu*Bold*.ttf",
    ]
    if sys.platform == "win32":
        windir = os.environ.get("SYSTEMROOT", r"C:\Windows")
        fonts = os.path.join(windir, "Fonts")
        patterns = [
            os.path.join(fonts, "msyh*.ttc"),
            os.path.join(fonts, "simhei.ttf"),
            os.path.join(fonts, "simsun.ttc"),
            os.path.join(fonts, "arial*.ttf"),
        ] + patterns

    import glob

    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()


def draw_boxes(img, detections: list[dict]):
    """在图的副本上画框和标签。

    每个框：{"bbox_pixel": [x1,y1,x2,y2], "label": 文字, "color": (r,g,b)}。
    标签和颜色可省，颜色省了按调色板轮换，多框之间分得开。
    """
    from PIL import ImageDraw

    annotated = img.copy()
    draw = ImageDraw.Draw(annotated)

    short_edge = min(img.width, img.height)
    line_width = max(2, short_edge // 200)
    font = find_font(max(14, short_edge // 40))

    for i, det in enumerate(detections):
        color = det.get("color") or COLORS[i % len(COLORS)]
        x1, y1, x2, y2 = det["bbox_pixel"]
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        label = det.get("label") or ""
        if label:
            tb = draw.textbbox((0, 0), label, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            label_y = max(0, y1 - th - 6)
            draw.rectangle([x1, label_y, x1 + tw + 6, label_y + th + 6], fill=color)
            draw.text((x1 + 3, label_y + 2), label, fill=(255, 255, 255), font=font)

    return annotated


def hex_to_rgb(hex_str: str):
    """'#ff0000' 转 (255, 0, 0)；格式不对返回 None（走调色板）。"""
    if not hex_str:
        return None
    h = hex_str.lstrip("#")
    if len(h) != 6:
        return None
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return None


def content_bbox(img, tolerance: int = 8):
    """内容边界框：跟白色背景有差异的像素范围。全白返回 None。"""
    from PIL import Image, ImageChops

    rgb = img.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert("L")
    mask = diff.point(lambda p: 255 if p > tolerance else 0)
    return mask.getbbox()


def 解析框(spec: str, w: int, h: int, norm: bool) -> list[int]:
    """解析 'x1,y1,x2,y2'（可选 --norm 归一化）并夹进画布范围。"""
    try:
        x1, y1, x2, y2 = (int(v) for v in spec.split(","))
    except ValueError:
        错误(f"框格式：x1,y1,x2,y2（四个整数），收到 {spec!r}")
    if norm:
        x1, y1, x2, y2 = norm_to_pixel([x1, y1, x2, y2], w, h)
    if x1 >= x2 or y1 >= y2:
        错误(f"框无效：x1 要小于 x2，y1 要小于 y2，收到 [{x1},{y1},{x2},{y2}]")
    x1, x2 = max(0, min(x1, w)), max(0, min(x2, w))
    y1, y2 = max(0, min(y1, h)), max(0, min(y2, h))
    if x2 <= x1 or y2 <= y1:
        错误(f"框在画布外，裁不出内容。画布 {w}x{h}，夹取后 [{x1},{y1},{x2},{y2}]")
    return [x1, y1, x2, y2]


# ---------- 子命令 ----------

def cmd_info(args) -> None:
    img = open_image(args.image)
    w, h = img.size
    print(f"文件: {args.image}")
    print(f"尺寸: {w} x {h}（宽 x 高）")
    print(f"模式: {img.mode}")
    bbox = content_bbox(img, args.tolerance)
    if bbox:
        x1, y1, x2, y2 = bbox
        print(f"内容范围: [{x1},{y1},{x2},{y2}]，宽 {x2 - x1} 高 {y2 - y1}")
        print(f"四周留白: 左 {x1} 上 {y1} 右 {w - x2} 下 {h - y2}")
    else:
        print("内容范围: 全背景（没找到非白像素）")


def cmd_crop(args) -> None:
    img = open_image(args.image)
    w, h = img.size
    x1, y1, x2, y2 = 解析框(args.box, w, h, args.norm)
    cropped = img.crop((x1, y1, x2, y2))
    out = args.out or default_output_path(args.image, "_cropped")
    save_image(cropped, out)
    print(f"裁切: [{x1},{y1},{x2},{y2}] → {out}（{cropped.width} x {cropped.height}）")


def cmd_trim(args) -> None:
    img = open_image(args.image)
    w, h = img.size
    bbox = content_bbox(img, args.tolerance)
    if not bbox:
        错误("整张图都是背景色，没有可裁的内容")
    x1, y1, x2, y2 = bbox
    pad = max(0, args.pad)
    x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
    x2, y2 = min(w, x2 + pad), min(h, y2 + pad)
    trimmed = img.crop((x1, y1, x2, y2))
    out = args.out or default_output_path(args.image, "_trimmed")
    save_image(trimmed, out)
    print(f"裁白边: {w} x {h} → {trimmed.width} x {trimmed.height}，{out}")


def cmd_resize(args) -> None:
    from PIL import Image

    img = open_image(args.image)
    w, h = img.size
    if args.width and args.height:
        nw, nh = args.width, args.height
    elif args.width:
        nw = args.width
        nh = max(1, round(h * nw / w))
    elif args.height:
        nh = args.height
        nw = max(1, round(w * nh / h))
    else:
        错误("给 --width 或 --height，至少一个")
    resized = img.resize((nw, nh), Image.LANCZOS)
    out = args.out or default_output_path(args.image, f"_{nw}w")
    save_image(resized, out)
    print(f"缩放: {w} x {h} → {nw} x {nh}，{out}")


def cmd_annotate(args) -> None:
    img = open_image(args.image)
    w, h = img.size
    detections = []
    for spec in args.box:
        parts = spec.split(":")
        x1, y1, x2, y2 = 解析框(parts[0], w, h, args.norm)
        detections.append(
            {
                "bbox_pixel": [x1, y1, x2, y2],
                "label": parts[1] if len(parts) > 1 else "",
                "color": hex_to_rgb(parts[2]) if len(parts) > 2 else None,
            }
        )
    annotated = draw_boxes(img, detections)
    out = args.out or default_output_path(args.image, "_annotated")
    save_image(annotated, out)
    print(f"标注 {len(detections)} 个框: {out}（{annotated.width} x {annotated.height}）")


def main() -> None:
    检查PIL()
    ap = argparse.ArgumentParser(description="图像工具集：读图、裁切、裁白边、缩放、标注")
    sub = ap.add_subparsers(dest="命令", required=True)

    p = sub.add_parser("info", help="读图：尺寸、模式、内容范围、四周留白")
    p.add_argument("image")
    p.add_argument("--tolerance", type=int, default=8, help="背景判定阈值，默认 8")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("crop", help="按框裁切")
    p.add_argument("image")
    p.add_argument("--box", required=True, help="x1,y1,x2,y2")
    p.add_argument("--norm", action="store_true", help="框按 0 到 1000 归一化")
    p.add_argument("--out", default=None, help="输出路径，默认同目录加 _cropped")
    p.set_defaults(func=cmd_crop)

    p = sub.add_parser("trim", help="裁白边：按内容范围自动裁")
    p.add_argument("image")
    p.add_argument("--pad", type=int, default=0, help="四周保留的像素，默认 0")
    p.add_argument("--tolerance", type=int, default=8, help="背景判定阈值，默认 8")
    p.add_argument("--out", default=None, help="输出路径，默认同目录加 _trimmed")
    p.set_defaults(func=cmd_trim)

    p = sub.add_parser("resize", help="缩放")
    p.add_argument("image")
    p.add_argument("--width", type=int, default=None)
    p.add_argument("--height", type=int, default=None)
    p.add_argument("--out", default=None, help="输出路径，默认同目录加 _<宽>w")
    p.set_defaults(func=cmd_resize)

    p = sub.add_parser("annotate", help="画框标注")
    p.add_argument("image")
    p.add_argument("--box", action="append", required=True,
                   help="x1,y1,x2,y2[:标签[:#颜色]]，可多次")
    p.add_argument("--norm", action="store_true", help="框按 0 到 1000 归一化")
    p.add_argument("--out", default=None, help="输出路径，默认同目录加 _annotated")
    p.set_defaults(func=cmd_annotate)

    args = ap.parse_args()
    if not Path(args.image).is_file():
        错误(f"文件不存在: {args.image}")
    args.func(args)


if __name__ == "__main__":
    main()
