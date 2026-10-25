# -*- coding: utf-8 -*-
"""drawio (.drawio / mxGraphModel XML) → house style SVG 草稿。
支持：未压缩与压缩（base64+raw-deflate）两种 diagram 内嵌；顶点（矩形/圆角/椭圆/
菱形/圆柱/云）与带 source/target 的边；value 里的富文本剥成纯文本。
不支持（如实报）：泳道折叠语义、edgeArray 弯折点重算（沿用 exit/entry 近似直线）、
mxgraph.* 精细图形（降级为矩形）、样式里的渐变。
用法: uv run python drawio_to_svg.py <file.drawio> [out.svg] [--title 标题]
产出后照例 validate_svg.py + 渲染核对。
"""
import base64
import re
import sys
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path

字体栈 = "'Segoe UI','Helvetica Neue',Arial,'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif"
默认填充, 默认描边, 文字色 = "#f8fafc", "#334155", "#1e293b"
字号 = 13


def 拿模型(路径: Path) -> str:
    文 = 路径.read_text(encoding="utf-8", errors="replace")
    if "<mxGraphModel" in 文:
        return 文
    m = re.search(r"<diagram[^>]*>([^<]+)</diagram>", 文)
    if not m:
        raise SystemExit("Error: 文件里既无 mxGraphModel 也无 diagram 内容")
    数据 = base64.b64decode(m.group(1).strip())
    try:
        return zlib.decompress(数据, -15).decode("utf-8")  # raw deflate
    except zlib.error:
        return zlib.decompress(数据).decode("utf-8")  # 兜 zlib 带头


def 剥文本(v: str) -> str:
    if not v:
        return ""
    t = re.sub(r"<[^>]+>", " ", v)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", t).strip()


def 文宽(s: str) -> float:
    cjk = sum(1 for ch in s if ord(ch) > 0x2E79)
    return cjk * 字号 + (len(s) - cjk) * 字号 * 0.5


def 解析样式(s: str) -> dict:
    d = {}
    for kv in (s or "").split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            d[k] = v
        elif kv:
            d.setdefault("_flag", "")
            d["_flag"] += "|" + kv
    return d


def main():
    args = list(sys.argv[1:])
    标题 = "drawio 导入草稿"
    if "--title" in args:
        i = args.index("--title")
        标题 = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        sys.exit(1)
    源 = Path(args[0]).resolve()
    if not 源.is_file():
        raise SystemExit(f"Error: 找不到 {源}")
    出 = Path(args[1]).resolve() if len(args) > 1 else 源.with_suffix(".svg")

    模型 = 拿模型(源)
    root = ET.fromstring(模型)
    def 标(el):
        return el.tag.split("}")[-1]

    cells = [el for el in root.iter() if 标(el) == "mxCell"]
    geo = {}
    parent = {}
    info = {}
    for c in cells:
        cid = c.get("id")
        parent[cid] = c.get("parent")
        info[cid] = {"值": 剥文本(c.get("value", "")), "样式": 解析样式(c.get("style", "")),
                     "源": c.get("source"), "目标": c.get("target"), "边": c.get("edge") == "1"}
        for g in c:
            if 标(g) == "mxGeometry":
                geo[cid] = (float(g.get("x", 0) or 0), float(g.get("y", 0) or 0),
                            float(g.get("width", 0) or 0), float(g.get("height", 0) or 0))

    平移 = {}
    for c in cells:
        cid = c.get("id")
        for g in c:
            if 标(g) == "mxGeometry":
                for p in g:
                    if 标(p) == "mxPoint" and p.get("as") == "translate":
                        平移[cid] = (float(p.get("x", 0) or 0), float(p.get("y", 0) or 0))

    def 绝对(cid, 深=0):
        if 深 > 10 or cid not in geo:
            return None
        x, y, w, h = geo[cid]
        px = parent.get(cid)
        if px and px in geo:
            基 = 绝对(px, 深 + 1)
            if 基:
                tx, ty = 平移.get(px, (0, 0))
                return (基[0] + tx + x, 基[1] + ty + y, w, h)
        return (x, y, w, h)

    顶点 = {}
    for cid, g in geo.items():
        if info[cid]["边"]:
            continue
        A = 绝对(cid)
        if A and A[2] > 0:
            顶点[cid] = A
    边们 = [cid for cid, i in info.items() if i["边"] and i["源"] and i["目标"]]

    if not 顶点:
        raise SystemExit("Error: 没解析到任何顶点（可能是不支持的文件形态）")

    xs = [a[0] + a[2] for a in 顶点.values()] + [a[0] for a in 顶点.values()]
    ys = [a[1] + a[3] for a in 顶点.values()] + [a[1] for a in 顶点.values()]
    高 = max(ys) + 70
    宽 = max(xs) + 70

    def 中(cid):
        x, y, w, h = 顶点[cid]
        return x + w / 2, y + h / 2

    def 贴边(cid, 对: tuple):
        """矩形边界与中心连线的交点——箭头贴边不悬空"""
        x, y, w, h = 顶点[cid]
        cx, cy = x + w / 2, y + h / 2
        dx, dy = 对[0] - cx, 对[1] - cy
        if dx == 0 and dy == 0:
            return cx, cy
        t = min((w / 2) / abs(dx) if dx else 9e9, (h / 2) / abs(dy) if dy else 9e9)
        return cx + dx * t, cy + dy * t

    L = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(宽)} {int(高)}" '
         f'width="{int(宽)}" height="{int(高)}">',
         '<defs><marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
         f'<polygon points="0 0,10 3.5,0 7" fill="{默认描边}"/></marker></defs>',
         '<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<text x="40" y="46" font-size="22" font-weight="700" fill="{文字色}" font-family="{字体栈}">{标题}</text>']

    for eid in 边们:
        a, b = info[eid]["源"], info[eid]["目标"]
        if a not in 顶点 or b not in 顶点:
            continue
        p1 = 贴边(a, 中(b))
        p2 = 贴边(b, 中(a))
        样 = info[eid]["样式"]
        dash = ' stroke-dasharray="6 4"' if 样.get("dashed") == "1" else ""
        col = 样.get("strokeColor", 默认描边)
        if col.startswith("#"):
            pass
        else:
            col = 默认描边
        L.append(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
                 f'stroke="{col}" stroke-width="1.8"{dash} marker-end="url(#arr)"/>')
        vy = info[eid]["值"]
        if vy:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 8
            tw = 文宽(vy) + 10
            L.append(f'<rect x="{mx-tw/2:.0f}" y="{my-11:.0f}" width="{tw:.0f}" height="17" '
                     'fill="#ffffff" opacity="0.92"/>')
            L.append(f'<text x="{mx:.0f}" y="{my+2:.0f}" font-size="12" fill="#475569" '
                     f'text-anchor="middle" font-family="{字体栈}">{vy}</text>')

    for cid, (x, y, w, h) in 顶点.items():
        样 = info[cid]["样式"]
        填 = 样.get("fillColor", 默认填充)
        if 填 in ("none", "default"):
            填 = "#ffffff"
        描 = 样.get("strokeColor", 默认描边)
        if not 描.startswith("#"):
            描 = 默认描边
        rx = 8 if 样.get("rounded") == "1" else 0
        if "ellipse" in 样.get("_flag", "") or 样.get("shape") == "ellipse":
            L.append(f'<ellipse cx="{x+w/2:.0f}" cy="{y+h/2:.0f}" rx="{w/2:.0f}" ry="{h/2:.0f}" '
                     f'fill="{填}" stroke="{描}" stroke-width="1.6"/>')
        elif "diamond" in 样.get("_flag", ""):
            cx, cy = x + w / 2, y + h / 2
            L.append(f'<polygon points="{cx:.0f},{y:.0f} {x+w:.0f},{cy:.0f} {cx:.0f},{y+h:.0f} '
                     f'{x:.0f},{cy:.0f}" fill="{填}" stroke="{描}" stroke-width="1.6"/>')
        else:
            L.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" '
                     f'fill="{填}" stroke="{描}" stroke-width="1.6"/>')
        标值 = info[cid]["值"]
        if 标值:
            行 = 标值.split(" ")
            L.append(f'<text x="{x+w/2:.0f}" y="{y+h/2+4:.0f}" font-size="{字号}" fill="{文字色}" '
                     f'text-anchor="middle" font-family="{字体栈}">{标值}</text>')
    L.append("</svg>")
    出.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ {出}  ({len(顶点)} 顶点 / {len(边们)} 边)")


if __name__ == "__main__":
    main()
