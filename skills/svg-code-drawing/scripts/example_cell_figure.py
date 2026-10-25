# -*- coding: utf-8 -*-
"""Cell/Nature 风格多面板图 v2：留白最小化、7pt 等效字号、色盲安全板、分层 id。
用法: uv run python 测试/cell-style-v2.py [输出.svg]
"""
import math
import sys
from pathlib import Path

F = "Helvetica,Arial,sans-serif"
INK = "#111111"
GRAY = "#9A9A9A"
BLUE = "#0072B2"
RULE = "#C9CFD6"
AXIS = "#333333"
NUC = "#7B8FB5"


def t(x, y, s, size=12, anchor="start", weight=None, fill=INK):
    w = f' font-weight="{weight}"' if weight else ""
    s2 = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{w}>{s2}</text>'


def main():
    出 = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cell-figure.svg")
    L = []
    W, H = 940, 615
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    L.append('<defs><marker id="ah" markerWidth="8" markerHeight="6.4" refX="7" refY="3.2" orient="auto">'
             f'<polygon points="0 0,8 3.2,0 6.4" fill="{AXIS}"/></marker></defs>')
    L.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    L.append(f'<g font-family="{F}">')

    L.append('<g id="panel-a">')
    L.append(t(24, 26, "A", 14, weight="bold"))
    L.append(f'<rect x="60" y="100" width="340" height="420" rx="12" fill="#FAFBFC" stroke="{RULE}" stroke-width="1.2"/>')
    L.append('<rect x="70" y="104" width="320" height="10" fill="#E9EDF2"/>')
    L.append(f'<line x1="70" y1="104" x2="390" y2="104" stroke="{AXIS}" stroke-width="1.3"/>')
    L.append(f'<line x1="70" y1="114" x2="390" y2="114" stroke="{AXIS}" stroke-width="1.3"/>')
    L.append(f'<rect x="230" y="96" width="13" height="32" rx="6.5" fill="#6B7280"/>')
    L.append(f'<rect x="250" y="96" width="13" height="32" rx="6.5" fill="#6B7280"/>')
    L.append(f'<circle cx="246" cy="72" r="9" fill="{BLUE}"/>')
    L.append(t(264, 76, "Ligand", 12))
    L.append(f'<line x1="246" y1="84" x2="246" y2="95" stroke="{AXIS}" stroke-width="1.4" marker-end="url(#ah)"/>')
    L.append(f'<circle cx="290" cy="92" r="9" fill="#ffffff" stroke="{AXIS}" stroke-width="1.2"/>')
    L.append(t(290, 96, "1", 12, anchor="middle", weight="bold"))
    L.append(t(272, 138, "Receptor", 12))
    L.append(f'<path d="M246,130 C246,180 220,200 196,217" fill="none" stroke="{AXIS}" stroke-width="1.5" marker-end="url(#ah)"/>')
    L.append(f'<circle cx="276" cy="176" r="9" fill="#ffffff" stroke="{AXIS}" stroke-width="1.2"/>')
    L.append(t(276, 180, "2", 12, anchor="middle", weight="bold"))
    L.append(f'<circle cx="170" cy="262" r="52" fill="#EDF1F8" stroke="{NUC}" stroke-width="1.3"/>')
    L.append(f'<circle cx="190" cy="245" r="9" fill="{NUC}" opacity="0.55"/>')
    L.append(t(170, 296, "Nucleus", 12, anchor="middle", fill="#333333"))
    L.append(f'<line x1="170" y1="314" x2="170" y2="430" stroke="{AXIS}" stroke-width="1.5" marker-end="url(#ah)"/>')
    L.append(f'<circle cx="143" cy="380" r="9" fill="#ffffff" stroke="{AXIS}" stroke-width="1.2"/>')
    L.append(t(143, 384, "3", 12, anchor="middle", weight="bold"))
    L.append(f'<rect x="120" y="435" width="100" height="36" rx="6" fill="#ffffff" stroke="{NUC}" stroke-width="1.3"/>')
    L.append(t(170, 458, "Gene X", 12, anchor="middle", fill="#222222"))
    L.append('</g>')

    L.append('<g id="panel-b">')
    L.append(t(456, 26, "B", 14, weight="bold"))
    x0, xb, ytop = 505, 900, 70
    v2y = lambda v: 250 - v * 1.8
    L.append(f'<line x1="{x0}" y1="{ytop}" x2="{x0}" y2="{v2y(0):.1f}" stroke="{AXIS}" stroke-width="1.3"/>')
    L.append(f'<line x1="{x0}" y1="{v2y(0):.1f}" x2="{xb}" y2="{v2y(0):.1f}" stroke="{AXIS}" stroke-width="1.3"/>')
    for v in (0, 25, 50, 75, 100):
        y = v2y(v)
        L.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 - 4}" y2="{y:.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(t(x0 - 8, y + 4, str(v), 12, anchor="end"))
    组1 = [(560, 45, 6), (610, 52, 5), (660, 48, 7)]
    组2 = [(760, 78, 5), (810, 85, 6), (860, 80, 5)]
    for x, v, e in 组1:
        L.append(f'<rect x="{x}" y="{v2y(v):.1f}" width="34" height="{v2y(0) - v2y(v):.1f}" fill="{GRAY}"/>')
    for x, v, e in 组2:
        L.append(f'<rect x="{x}" y="{v2y(v):.1f}" width="34" height="{v2y(0) - v2y(v):.1f}" fill="{BLUE}"/>')
    for x, v, e in 组1 + 组2:
        cx = x + 17
        L.append(f'<line x1="{cx}" y1="{v2y(v - e):.1f}" x2="{cx}" y2="{v2y(v + e):.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(f'<line x1="{cx - 6}" y1="{v2y(v + e):.1f}" x2="{cx + 6}" y2="{v2y(v + e):.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(f'<line x1="{cx - 6}" y1="{v2y(v - e):.1f}" x2="{cx + 6}" y2="{v2y(v - e):.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
    L.append(f'<path d="M627,86 L627,78 L827,78 L827,86" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    L.append(t(727, 70, "**", 13, anchor="middle", weight="bold"))
    L.append(t(627, 266, "Ctrl", 12, anchor="middle"))
    L.append(t(827, 266, "Treat", 12, anchor="middle"))
    L.append(f'<text x="470" y="160" font-size="12" text-anchor="middle" fill="{INK}" transform="rotate(-90 470 160)">Relative signal</text>')
    L.append('</g>')

    L.append('<g id="panel-c">')
    L.append(t(456, 308, "C", 14, weight="bold"))
    y0c, y1c = 520, 350
    cvy = lambda v: y0c - v * 1.7
    xd = lambda d: 535 + (math.log10(d) + 1) / 3 * 345
    L.append(f'<line x1="{x0}" y1="{y1c}" x2="{x0}" y2="{y0c}" stroke="{AXIS}" stroke-width="1.3"/>')
    L.append(f'<line x1="{x0}" y1="{y0c}" x2="{xb}" y2="{y0c}" stroke="{AXIS}" stroke-width="1.3"/>')
    for v in (0, 50, 100):
        y = cvy(v)
        L.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 - 4}" y2="{y:.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(t(x0 - 8, y + 4, str(v), 12, anchor="end"))
    曲线 = []
    for i in range(61):
        d = 10 ** (-1 + 3 * i / 60)
        v = 10 + 85 / (1 + 8 / d)
        曲线.append(f"{xd(d):.1f},{cvy(v):.1f}")
    L.append(f'<polyline points="{" ".join(曲线)}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    for d in (0.1, 1, 3, 10, 30, 100):
        v = 10 + 85 / (1 + 8 / d)
        x, y = xd(d), cvy(v)
        L.append(f'<line x1="{x:.1f}" y1="{cvy(v - 5):.1f}" x2="{x:.1f}" y2="{cvy(v + 5):.1f}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{INK}"/>')
    for d, lab in ((0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        x = xd(d)
        L.append(f'<line x1="{x:.1f}" y1="{y0c}" x2="{x:.1f}" y2="{y0c + 4}" stroke="{AXIS}" stroke-width="1.1"/>')
        L.append(t(x, y0c + 18, lab, 12, anchor="middle"))
    L.append(t(705, y0c + 42, "Dose (µM)", 12, anchor="middle"))
    L.append(f'<text x="470" y="435" font-size="12" text-anchor="middle" fill="{INK}" transform="rotate(-90 470 435)">Response (%)</text>')
    L.append('</g>')

    L.append(t(24, 584, "Figure 1. Ligand binding activates receptor signaling and induces Gene X expression. (A) Scheme of ligand–receptor–nucleus signaling. (B) Relative signal,", 12))
    L.append(t(24, 600, "mean ± s.e.m., n = 3 independent experiments; ** P < 0.01 versus Ctrl (two-sided t-test). (C) Dose–response curve, mean ± s.e.m.", 12))
    L.append('</g>')
    L.append('</svg>')
    出.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ {出}  ({出.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
