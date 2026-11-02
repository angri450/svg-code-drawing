#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据驱动信息图：一份 JSON 规格 → 一张 1536×864 SVG。

用法:
  python build_infographic.py spec.json out.svg

设计空间固定 1536×864，输出 SVG 的 width/height 可另设；文字和坐标按设计空间排。
底图留透明，交给 compose_layers.py 叠纸面底图。
"""
import argparse
import html
import json
import sys
from pathlib import Path

DESIGN_W, DESIGN_H = 1536, 864

DEFAULTS = {
    "colors": {
        "accent": "#8E1B2A",
        "bright": "#C8102E",
        "ink": "#3F3F3F",
        "muted": "#6B6B6B",
        "hairline": "#D8D2C6",
    },
    "fonts": {
        "serif": "Noto Serif CJK SC",
        "sans": "Noto Sans CJK SC",
    },
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def fmt_num(value: float) -> str:
    value = float(value)
    if abs(value) >= 10:
        return f"{value:.0f}"
    if abs(value) >= 1:
        return f"{value:.1f}"
    return f"{value:.2f}"


def build(spec: dict) -> str:
    width = int(spec.get("width", DESIGN_W))
    height = int(spec.get("height", DESIGN_H))
    colors = {**DEFAULTS["colors"], **spec.get("colors", {})}
    fonts = {**DEFAULTS["fonts"], **spec.get("fonts", {})}
    serif = f"'{fonts['serif']}', serif"
    sans = f"'{fonts['sans']}', sans-serif"

    eyebrow = spec.get("eyebrow", "")
    title = spec.get("title", "信息图")
    subtitle = spec.get("subtitle", "")
    metric = spec.get("metric", {})
    bar = spec.get("bar", {})
    segments = bar.get("segments", [])
    if not segments:
        raise ValueError("bar.segments 不能为空")
    values = [float(seg["value"]) for seg in segments]
    if any(v <= 0 for v in values):
        raise ValueError("bar.segments[].value 必须大于 0")
    total = float(bar.get("total") or sum(values))
    if total <= 0:
        raise ValueError("bar.total 必须大于 0")

    left = 96
    rule_y = 290
    bar_x, bar_y, bar_w, bar_h = 600, 360, 840, 64

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {DESIGN_W} {DESIGN_H}" '
        f'width="{width}" height="{height}" role="img" aria-labelledby="info-title">',
        f'<title id="info-title">{esc(title)}</title>',
        f'<g font-family="{sans}">',
    ]

    if eyebrow:
        parts.append(
            f'<text x="{left}" y="96" font-size="22" fill="{colors["accent"]}" '
            f'letter-spacing="6">{esc(eyebrow)}</text>'
        )
    parts.append(
        f'<text x="{left}" y="190" font-family="{serif}" font-size="64" '
        f'font-weight="700" fill="{colors["accent"]}">{esc(title)}</text>'
    )
    if subtitle:
        parts.append(
            f'<text x="{left + 4}" y="252" font-size="28" fill="{colors["muted"]}">'
            f'{esc(subtitle)}</text>'
        )
    parts.append(
        f'<line x1="{left}" y1="{rule_y}" x2="700" y2="{rule_y}" '
        f'stroke="{colors["bright"]}" stroke-width="3"/>'
    )

    if metric:
        value = metric.get("value", "")
        label = metric.get("label", "")
        if value:
            parts.append(
                f'<text x="{left}" y="450" font-family="{serif}" font-size="140" '
                f'font-weight="700" fill="{colors["accent"]}">{esc(value)}</text>'
            )
        if label:
            parts.append(
                f'<text x="{left + 4}" y="500" font-size="24" fill="{colors["muted"]}">'
                f'{esc(label)}</text>'
            )

    x = bar_x
    for index, seg in enumerate(segments):
        value = values[index]
        seg_w = bar_w * value / total
        pct = value / total * 100
        color = seg.get("color") or (colors["hairline"] if index == 0 else colors["accent"])
        text_color = seg.get("text_color") or ("#3F3F3F" if index == 0 else "#FFFFFF")
        label = f'{seg.get("label", "")} {fmt_num(value)}{seg.get("suffix", "")}'.strip()
        parts.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{color}"/>'
        )
        if seg_w >= 160:
            cx = x + seg_w / 2
            parts.append(
                f'<text x="{cx:.1f}" y="{bar_y - 28}" font-size="22" fill="{colors["muted"]}" '
                f'text-anchor="middle">{esc(label)}</text>'
            )
            parts.append(
                f'<text x="{cx:.1f}" y="{bar_y + 42}" font-size="26" fill="{text_color}" '
                f'text-anchor="middle">{pct:.1f}%</text>'
            )
        else:
            parts.append(
                f'<text x="{x + 12:.1f}" y="{bar_y - 28}" font-size="22" fill="{colors["muted"]}">'
                f'{esc(label)} · {pct:.1f}%</text>'
            )
        x += seg_w

    if bar.get("caption"):
        parts.append(
            f'<text x="{bar_x}" y="{bar_y + 92}" font-size="22" fill="{colors["muted"]}">'
            f'{esc(bar["caption"])}</text>'
        )

    ticks = spec.get("ticks", {})
    count = int(ticks.get("count", 0))
    if count > 0:
        for index in range(count):
            tx = left + index * 30
            parts.append(
                f'<rect x="{tx}" y="540" width="5" height="30" fill="{colors["bright"]}"/>'
            )
        line_end = left + (count - 1) * 30 + 5
        parts.append(
            f'<line x1="{left}" y1="578" x2="{line_end}" y2="578" '
            f'stroke="{colors["hairline"]}" stroke-width="1"/>'
        )
        if ticks.get("label"):
            parts.append(
                f'<text x="{left}" y="612" font-size="22" fill="{colors["muted"]}">'
                f'{esc(ticks["label"])}</text>'
            )

    if spec.get("takeaway"):
        parts.append(
            f'<text x="{left}" y="700" font-family="{serif}" font-size="32" '
            f'font-weight="700" fill="{colors["accent"]}">{esc(spec["takeaway"])}</text>'
        )
    if spec.get("source"):
        parts.append(
            f'<text x="{left}" y="790" font-size="18" fill="{colors["muted"]}">'
            f'{esc(spec["source"])}</text>'
        )

    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="JSON 规格")
    ap.add_argument("out", help="输出 SVG")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error: 读不了 {spec_path}: {exc}")
        sys.exit(1)
    try:
        svg = build(spec)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Error: 规格有问题: {exc}")
        sys.exit(1)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"✓ {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
