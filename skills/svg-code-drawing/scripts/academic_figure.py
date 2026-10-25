# -*- coding: utf-8 -*-
"""期刊多面板图骨架生成器：mm 坐标、Wong 色板、布局算法、箭头预检、色盲检查。
用法: uv run python academic_figure.py --journal nature --variant A --panels panels.json [--arrows arrows.json] --out fig.svg
panels.json: [{"label":"a","type":"placeholder","desc":"EIS Nyquist","width_ratio":0.34,"height":55,"arrow_to_next":true}]
type 可选 placeholder(虚线数据位) / blank(空面板) / battery(电池截面示意)
arrows.json: [{"from":"a","to":"b","label":"Characterize"}]
不传 --arrows 时按 arrow_to_next 自动连。
"""
import argparse
import json
import math
import sys
from pathlib import Path

WONG = {"a1": "#0072B2", "a2": "#E69F00", "a3": "#009E73", "a4": "#D55E00"}
JOURNALS = {"nature": 183, "cell": 174, "science": 174, "acs": 177.8, "ieee": 181.9, "elsevier": 190}
LABEL_OFFSET_Y, HEAD_ROOM, MARGIN = 2.5, 7.0, 6.0

def R(v): return round(v, 1)

def lum(hx):
    r, g, b = (int(hx.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def 色盲检查(colors):
    # Wong 板色相可辨即安全，亮度比判据只拦红绿对
    警 = []
    for i, c1 in enumerate(colors):
        for c2 in colors[i+1:]:
            r1, g1, b1 = (int(c1[j:j+2], 16) for j in (1, 3, 5))
            r2, g2, b2 = (int(c2[j:j+2], 16) for j in (1, 3, 5))
            红绿 = ((r1 > 120 and g1 < 100 and r2 < 100 and g2 > 120) or
                    (r2 > 120 and g2 < 100 and r1 < 100 and g1 > 120))
            if 红绿:
                l1, l2 = lum(c1), lum(c2)
                比 = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
                if 比 < 2.0:
                    警.append(f"色盲预警: 红绿对 {c1}/{c2} 亮度比 {比:.1f}")
    return 警

def 文宽(s, 字号=2.2):
    cjk = sum(1 for ch in s if ord(ch) > 0x2E79)
    return cjk * 字号 + (len(s) - cjk) * 字号 * 0.55

def 箭头预检(箭s):
    警 = []
    for i, a in enumerate(箭s):
        长 = math.hypot(a["x2"] - a["x1"], a["y2"] - a["y1"])
        if 长 < 10:
            警.append(f"箭头{i}: 长 {长:.1f}mm < 10mm 下限，改布局")
        elif 长 < 16 and a.get("label"):
            警.append(f"箭头{i}: 长 {长:.1f}mm 放不下标签 '{a['label']}'")
    return 警

def defs():
    return ('<defs>'
            '<marker id="arrow-std" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" '
            'orient="auto-start-reverse" markerUnits="strokeWidth"><path d="M0 0 L10 5 L0 10 z" fill="#333"/></marker>'
            '<marker id="arrow-bold" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4.5" markerHeight="4.5" '
            'orient="auto-start-reverse" markerUnits="strokeWidth"><path d="M0 1 L9 5 L0 8 z" fill="#0072B2"/></marker>'
            '<pattern id="ph-hatch" patternUnits="userSpaceOnUse" width="3" height="3" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="3" stroke="#DDD" stroke-width="0.5"/></pattern>'
            '</defs>')

def 面板(label, p):
    x, y, w, h = R(p["x"]), R(p["y"]), R(p["w"]), R(p["h"])
    型 = p.get("type", "placeholder")
    parts = [f'<g id="panel-{label}">',
             f'<text x="{x}" y="{R(y - LABEL_OFFSET_Y)}" font-family="Helvetica,Arial,sans-serif" '
             f'font-size="2.8" font-weight="bold" fill="#000">{label}</text>']
    cx, cy = R(x + w / 2), R(y + h / 2)
    if 型 == "placeholder":
        desc = p.get("desc", "Data panel")
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F5F5F5" stroke="#999" '
                     'stroke-width="0.3" stroke-dasharray="2.5,2" rx="1.5"/>')
        parts.append(f'<text x="{cx}" y="{R(cy - 1)}" font-family="Helvetica,Arial,sans-serif" font-size="2.6" '
                     f'fill="#333" text-anchor="middle" font-weight="bold">{desc}</text>')
        parts.append(f'<text x="{R(x + w - 2)}" y="{R(y + h - 2)}" font-family="Helvetica,Arial,sans-serif" '
                     f'font-size="1.8" fill="#BBB" text-anchor="end">{w:.0f}×{h:.0f} mm</text>')
    elif 型 == "blank":
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="#BBB" '
                     'stroke-width="0.3" rx="1.5"/>')
    elif 型 == "battery":
        parts.append(电池截面(x + w * 0.1, y + h * 0.25, w * 0.8, h * 0.4))
    parts.append("</g>")
    return "\n".join(parts)

def 电池截面(x, y, w, h):
    层 = [("Cu", "#D4A574", 1), ("Anode", "#555", 1.5), ("Sep.", "#F2F2F2", 0.6),
          ("Cathode", WONG["a1"], 1.5), ("Al", "#C0C0C0", 1)]
    总 = sum(l[2] for l in 层)
    out, cx = [], x
    for i, (名, 色, 权) in enumerate(层):
        lw = w * 权 / 总
        out.append(f'<rect x="{R(cx)}" y="{R(y)}" width="{R(lw)}" height="{R(h)}" fill="{色}" stroke="#333" stroke-width="0.15"/>')
        ly = y + h + (2.2 if i % 2 == 0 else 4.6)  # 隔层错行，防窄层标签相撞
        out.append(f'<text x="{R(cx + lw/2)}" y="{R(ly)}" font-family="Helvetica,Arial,sans-serif" '
                   f'font-size="1.8" fill="#333" text-anchor="middle">{名}</text>')
        cx += lw
    return "".join(out)

def 布局(panels, variant, w_total):
    n = len(panels)
    if variant == "A":
        间距 = [20 if panels[i].get("arrow_to_next") else 6 for i in range(n - 1)]
        可宽 = w_total - 2 * MARGIN - sum(间距)
        x, 位 = MARGIN, []
        for i, p in enumerate(panels):
            pw = 可宽 * p.get("width_ratio", 1 / n)
            位.append({**p, "x": x, "y": MARGIN + 5, "w": pw, "h": p.get("height", 55)})
            x += pw + (间距[i] if i < n - 1 else 0)
        h = MARGIN + 5 + max(p["h"] for p in 位) + MARGIN
    elif variant == "B":
        列 = 2
        行 = math.ceil(n / 列)
        可宽 = w_total - 2 * MARGIN - 20
        cw = 可宽 / 列
        位 = []
        for i, p in enumerate(panels):
            位.append({**p, "x": MARGIN + (i % 列) * (cw + 20), "y": MARGIN + 5 + (i // 列) * (p.get("height", 55) + 12),
                       "w": cw, "h": p.get("height", 55)})
        h = MARGIN + 5 + 行 * (panels[0].get("height", 55) + 12) - 12 + MARGIN
    else:
        可宽 = w_total - 2 * MARGIN - 20
        hero = 可宽 * 0.5
        位 = [{**panels[0], "x": MARGIN, "y": MARGIN + 5, "w": hero, "h": panels[0].get("height", 55)}]
        侧h = (panels[0].get("height", 55) - (n - 2) * 6) / max(1, n - 1)
        for i, p in enumerate(panels[1:]):
            位.append({**p, "x": MARGIN + hero + 20, "y": MARGIN + 5 + i * (侧h + 6), "w": 可宽 - hero, "h": 侧h})
        h = MARGIN + 5 + panels[0].get("height", 55) + MARGIN
    return 位, w_total, R(h)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", default="nature", choices=sorted(JOURNALS))
    ap.add_argument("--variant", default="A", choices=list("ABC"))
    ap.add_argument("--panels", required=True)
    ap.add_argument("--arrows", default=None)
    ap.add_argument("--out", default="figure.svg")
    args = ap.parse_args()
    panels = json.loads(Path(args.panels).read_text(encoding="utf-8"))
    w_total = JOURNALS[args.journal]
    位, W, H = 布局(panels, args.variant, w_total)

    箭s = []
    if args.arrows:
        spec = json.loads(Path(args.arrows).read_text(encoding="utf-8"))
        m = {p["label"]: p for p in 位}
        for a in spec:
            f, t = m[a["from"]], m[a["to"]]
            箭s.append({"x1": R(f["x"] + f["w"] + 1), "y1": R(f["y"] + f["h"] / 2),
                        "x2": R(t["x"] - 1), "y2": R(t["y"] + t["h"] / 2), "label": a.get("label")})
    else:
        for i in range(len(位) - 1):
            if panels[i].get("arrow_to_next"):
                f, t = 位[i], 位[i + 1]
                # 目标在右侧同排→横箭头；换行/堆叠（目标在下方）→底到顶竖箭头
                if t["x"] > f["x"] + f["w"] * 0.5:
                    箭s.append({"x1": R(f["x"] + f["w"] + 1), "y1": R(f["y"] + f["h"] / 2),
                                "x2": R(t["x"] - 1), "y2": R(t["y"] + t["h"] / 2)})
                else:
                    箭s.append({"x1": R(f["x"] + f["w"] / 2), "y1": R(f["y"] + f["h"] + 1),
                                "x2": R(t["x"] + t["w"] / 2), "y2": R(t["y"] - 1)})

    用色 = {p2.get("fill", "#0072B2") for p2 in 位 if p2.get("type") == "battery"}
    用色 |= {"#0072B2"}  # 流程箭头恒用蓝
    警 = 箭头预检(箭s) + 色盲检查(sorted(用色))
    for w in 警:
        print(f"[警] {w}", file=sys.stderr)

    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         defs(), '<rect width="100%" height="100%" fill="#fff"/>',
         '<g font-family="Helvetica,Arial,sans-serif">']
    for p in 位:
        L.append(面板(p["label"], p))
    for a in 箭s:
        L.append(f'<line x1="{a["x1"]}" y1="{a["y1"]}" x2="{a["x2"]}" y2="{a["y2"]}" '
                 'stroke="#0072B2" stroke-width="0.55" marker-end="url(#arrow-bold)"/>')
        if a.get("label"):
            mx, my = (a["x1"] + a["x2"]) / 2, (a["y1"] + a["y2"]) / 2
            横 = abs(a["x2"] - a["x1"]) >= abs(a["y2"] - a["y1"])
            L.append(f'<text x="{R(mx if 横 else mx - 3.5)}" y="{R(my - 3.5 if 横 else my + 0.7)}" '
                     f'font-size="2.2" fill="#0072B2" font-style="italic" '
                     f'text-anchor="{"middle" if 横 else "end"}">{a.get("label", "")}</text>')
    L.append("</g></svg>")
    Path(args.out).write_text("\n".join(L), encoding="utf-8")
    print(f"✓ {args.out}  ({W}×{H}mm, {len(位)} 面板, {len(箭s)} 箭头, 警告 {len(警)})")

if __name__ == "__main__":
    main()
