# -*- coding: utf-8 -*-
"""重叠与出框视觉障碍检测（提示性检查，不阻断交付）。

三类检测：
  T1 文字-文字：两个 <text> 的估算包围盒相交。
  T2 文字-图形：文字盒被后面画的填充图形盖住（压色），或被足够粗的线穿带。
  T3 出框：文字超出它所属容器的边框，或超出画布 viewBox。

渲染层像素对比度检查（渐变/半透明这类坐标算不出的情况）本期不做，
接口以 --render 占位保留，后续版本实现。

估算说明：无字体度量，CJK 与宽标点字宽按 1.0em、拉丁大写与数字按 0.66em、
小写按 0.55em、窄字符按 0.32em，基线上方 0.75em、下方 0.10em。
所以文字宽度是估算值，出框判定留 --edge-tol 余量。

用法: python check_overlap.py <fig.svg> [--json 输出路径] [--tol 1.0] [--edge-tol 1.0]
退出码: 0=正常（有无提示都是 0，提示级不判失败）, 2=解析错误。
"""
import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://www.w3.org/2000/svg}"


# ---------- 颜色与样式 ----------

def _hex(c):
    c = c.strip()
    if c.startswith("#"):
        if len(c) == 4:
            c = "#" + "".join(x * 2 for x in c[1:])
        if re.fullmatch(r"#[0-9a-fA-F]{6}", c):
            return c.lower()
        return None
    m = re.fullmatch(r"rgba?\(([^)]*)\)", c)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        try:
            r, g, b = (int(float(parts[i])) if "." not in parts[i] else round(float(parts[i]) * 255) for i in range(3))
            a = float(parts[3]) if len(parts) > 3 else 1.0
            if a < 0.15:
                return None
            return "#%02x%02x%02x" % (r, g, b)
        except (ValueError, IndexError):
            return None
    if c in ("none", ""):
        return None
    named = {"white": "#ffffff", "black": "#000000", "red": "#ff0000",
             "blue": "#0000ff", "green": "#008000", "gray": "#808080", "grey": "#808080"}
    return named.get(c.lower())


def _lum(hx):
    r, g, b = (int(hx[1 + i:3 + i], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


NAMED_INHERIT = {"fill", "stroke", "stroke-width", "font-size", "font-family",
                 "font-weight", "text-anchor"}


def _style_decls(svg):
    """<style> 文本 -> {selector: {prop: val}}。只处理 .class 与裸标签选择器。"""
    out = {}
    for st in svg.findall(NS + "style"):
        css = st.text or ""
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            sel = m.group(1).strip()
            props = {}
            for d in m.group(2).split(";"):
                if ":" in d:
                    k, v = d.split(":", 1)
                    props[k.strip().lower()] = v.strip()
            for s in sel.split(","):
                s = s.strip()
                if s:
                    out.setdefault(s, {}).update(props)
    return out


def _resolved_style(el, styles, parent):
    sty = dict(parent)
    sel = el.tag.replace(NS, "")
    if sel in styles:
        sty.update(styles[sel])
    cls = el.get("class", "")
    for c in cls.split():
        if "." + c in styles:
            sty.update(styles["." + c])
    for k, v in el.attrib.items():
        kk = k.lower()
        if kk in NAMED_INHERIT:
            sty[kk] = v
        elif kk == "style":
            for d in v.split(";"):
                if ":" in d:
                    a, b = d.split(":", 1)
                    a = a.strip().lower()
                    if a in NAMED_INHERIT:
                        sty[a] = b.strip()
    return sty


# ---------- 变换与数值 ----------

def _matrix(el, acc=(1, 0, 0, 1, 0, 0)):
    t = el.get("transform")
    if not t:
        return acc
    for m in re.finditer(r"(matrix|translate|scale|rotate|skewX|skewY)\(([^)]*)\)", t):
        kind, raw = m.group(1), m.group(2)
        try:
            v = [float(x) for x in re.split(r"[,\s]+", raw.strip()) if x]
        except ValueError:
            continue
        a, b, c, d, e, f = 1, 0, 0, 1, 0, 0
        if kind == "matrix" and len(v) == 6:
            a, b, c, d, e, f = v
        elif kind == "translate":
            e = v[0]
            f = v[1] if len(v) > 1 else 0
        elif kind == "scale":
            a = v[0]
            d = v[1] if len(v) > 1 else v[0]
        elif kind == "rotate" and v:
            deg = v[0]
            cx, cy = (v[1], v[2]) if len(v) == 3 else (0, 0)
            r = math.radians(deg)
            ca, sa = math.cos(r), math.sin(r)
            a, b, c, d = ca, sa, -sa, ca
            e, f = cx - ca * cx + sa * cy, cy - sa * cx - ca * cy
        else:
            continue
        a1, b1, c1, d1, e1, f1 = acc
        acc = (a1 * a + c1 * b, b1 * a + d1 * b,
               a1 * c + c1 * d, b1 * c + d1 * d,
               a1 * e + c1 * f + e1, b1 * e + d1 * f + f1)
    return acc


def _xform(mt, x, y):
    a, b, c, d, e, f = mt
    return (a * x + c * y + e, b * x + d * y + f)


def _scale_y(mt):
    a, b, c, d = mt[:4]
    return math.hypot(c, d) or math.hypot(a, b)


def _num(s, default=0.0):
    try:
        return float(re.sub(r"(px|pt|em|ex|cm|mm|in|%)$", "", str(s)))
    except (TypeError, ValueError):
        return default


# ---------- 收集元素 ----------

def _is_wide(ch):
    """CJK、全角标点、通用标点按全角宽度算。"""
    o = ord(ch)
    return (o >= 0x2E80 or (0x3000 <= o <= 0x303F) or
            (0xFF00 <= o <= 0xFFEF) or (0x2000 <= o <= 0x206F))


def _text_width(txt, fs):
    """估算文字宽度（按字体的 advance 宽度，不含首尾字形边距）。

    系数用 Edge/resvg 渲染后量实际墨迹标定，样本为 40px 长串，
    排除了首尾字形边距带来的误差：
      CJK 与全角标点  1.00 em
      拉丁大写        0.65 em
      数字            0.50 em
      拉丁小写        0.45 em
      窄字符与空格    0.28 em

    全角空格只做缩进、没有墨迹，但仍占位，按 1.00 em 计入。
    """
    w = 0.0
    for ch in txt:
        if _is_wide(ch):
            w += fs * 1.00
        elif ch in "iIljt.,:;'|!()[] ":
            w += fs * 0.28
        elif ch.isupper():
            w += fs * 0.65
        elif ch.isdigit():
            w += fs * 0.50
        else:
            w += fs * 0.45
    return max(w, fs * 0.5)


def _shape_bbox(el, tag, mt):
    if tag == "rect":
        x, y = _num(el.get("x")), _num(el.get("y"))
        w, h = _num(el.get("width")), _num(el.get("height"))
        if w <= 0 or h <= 0:
            return None
        p0, p1 = _xform(mt, x, y), _xform(mt, x + w, y + h)
    elif tag in ("circle", "ellipse"):
        cx, cy = _num(el.get("cx")), _num(el.get("cy"))
        if tag == "circle":
            rx = ry = _num(el.get("r"))
        else:
            rx, ry = _num(el.get("rx")), _num(el.get("ry"))
        if rx <= 0 or ry <= 0:
            return None
        p0, p1 = _xform(mt, cx - rx, cy - ry), _xform(mt, cx + rx, cy + ry)
    elif tag == "line":
        p0, p1 = (_xform(mt, _num(el.get("x1")), _num(el.get("y1"))),
                  _xform(mt, _num(el.get("x2")), _num(el.get("y2"))))
    elif tag == "path":
        d = el.get("d") or ""
        nums = re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", d)
        if len(nums) < 4:
            return None
        xs = [float(n) for n in nums[0::2]]
        ys = [float(n) for n in nums[1::2]]
        p0, p1 = _xform(mt, min(xs), min(ys)), _xform(mt, max(xs), max(ys))
    else:
        return None
    return (min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]))


def collect(svg):
    """按文档顺序返回元素列表，含包围盒、锚点与绘制样式。"""
    styles = _style_decls(svg)
    items = []

    def walk(el, mt, psty):
        sty = _resolved_style(el, styles, psty)
        mt = _matrix(el, mt)
        tag = el.tag.replace(NS, "")
        if tag == "text":
            x = _num(el.get("x"))
            y = _num(el.get("y"))
            fs = _num(sty.get("font-size"), 16) * _scale_y(mt)
            txt = "".join(el.itertext())
            anchor = sty.get("text-anchor", "start")
            tw = _text_width(txt, fs)
            x0, x1 = ((x - tw / 2, x + tw / 2) if anchor == "middle" else
                      (x - tw, x) if anchor == "end" else (x, x + tw))
            p0 = _xform(mt, x0, y - fs * 0.75)
            p1 = _xform(mt, x1, y + fs * 0.10)
            ap = _xform(mt, x, y)
            items.append({"kind": "text",
                          "bbox": (min(p0[0], p1[0]), min(p0[1], p1[1]),
                                   max(p0[0], p1[0]), max(p0[1], p1[1])),
                          "anchor": ap,
                          "text": txt.strip(), "fs": fs,
                          "fill": _hex(sty.get("fill", "#000000")) or "#000000"})
        elif tag in ("rect", "circle", "ellipse", "line", "path"):
            fill = _hex(sty.get("fill")) if "fill" in sty else "#000000"
            stroke = _hex(sty.get("stroke")) if "stroke" in sty else None
            sw = _num(sty.get("stroke-width"), 1.0) * _scale_y(mt)
            bb = _shape_bbox(el, tag, mt)
            if bb:
                if tag == "line":
                    # 水平/垂直线包围盒某一维为 0，按笔画厚度外扩，否则永不与文字相交
                    h = sw / 2.0
                    bb = (bb[0] - h, bb[1] - h, bb[2] + h, bb[3] + h)
                items.append({"kind": tag, "bbox": bb, "fill": fill,
                              "stroke": stroke, "sw": sw})
        for ch in el:
            if ch.tag.replace(NS, "") not in ("defs", "marker", "style", "title", "desc"):
                walk(ch, mt, sty)

    walk(svg, (1, 0, 0, 1, 0, 0), {})
    return items


def _viewbox(root):
    vb = root.get("viewBox")
    if not vb:
        return None
    parts = re.split(r"[,\s]+", vb.strip())
    try:
        v = [float(x) for x in parts if x]
    except ValueError:
        return None
    if len(v) != 4:
        return None
    return (v[0], v[1], v[0] + v[2], v[1] + v[3])


# ---------- 判定 ----------

def _inter(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, y0, x1, y1)


def _area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def _contains(box, pt, tol=0.0):
    return (box[0] - tol <= pt[0] <= box[2] + tol and
            box[1] - tol <= pt[1] <= box[3] + tol)


def _find_container(t, rects, max_area=None):
    """找出文字所属的容器。

    归属判据任一成立即可：锚点落在矩形内、文字盒中心落在矩形内。
    多个矩形都成立时取面积最小的那个，即最贴身的容器。
    max_area 给定时，面积超过它的矩形（整页底板）不参与归属。
    """
    tb = t["bbox"]
    cands = []
    for r in rects:
        rb = r["bbox"]
        if max_area is not None and _area(rb) > max_area:
            continue
        if _contains(rb, t["anchor"]) or _contains(rb, _center(tb)):
            cands.append(r)
    if not cands:
        return None
    return min(cands, key=lambda r: _area(r["bbox"]))


def _center(b):
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


def _sides(text_box, inner):
    """文字盒相对容器内框各边超出多少像素，正数表示出框。"""
    return {
        "left": inner[0] - text_box[0],
        "right": text_box[2] - inner[2],
        "top": inner[1] - text_box[1],
        "bottom": text_box[3] - inner[3],
    }


def check_overlap(items, tol):
    findings = []
    texts = [(i, it) for i, it in enumerate(items) if it["kind"] == "text"]

    # T1 文字-文字
    for a in range(len(texts)):
        ia, ta = texts[a]
        for b in range(a + 1, len(texts)):
            ib, tb = texts[b]
            ov = _inter(ta["bbox"], tb["bbox"])
            if not ov:
                continue
            smaller = min(_area(ta["bbox"]), _area(tb["bbox"])) or 1e-9
            frac = _area(ov) / smaller
            if frac > tol:
                findings.append({"type": "text-text",
                                 "a": ta["text"][:24], "b": tb["text"][:24],
                                 "overlap_pct": round(frac * 100, 1),
                                 "at": [round(x, 1) for x in ov]})

    # T2 文字被后画图形遮挡
    for idx, t in texts:
        for j in range(idx + 1, len(items)):
            g = items[j]
            if g["kind"] == "text":
                continue
            ov = _inter(t["bbox"], g["bbox"])
            if not ov:
                continue
            tarea = _area(t["bbox"]) or 1e-9
            if g["kind"] in ("rect", "circle", "ellipse") and g["fill"]:
                frac = _area(ov) / tarea
                if frac > 0.25 and _is_marker(g, t):
                    continue  # 刻意点在字上的小标记（着丝粒、序号点）
                if frac > 0.25:
                    sev = "cover" if frac > 0.6 else "partial"
                    # 不透明标签垫的豁免只对「文字比色块亮」的情形成立：
                    # 深色块压住深色字是真遮挡，不能放过
                    if sev == "cover" and _lum(t["fill"]) > _lum(g["fill"]) and _contrast(t["fill"], g["fill"]) >= 2.0:
                        continue  # 像是有意的不透明标签垫
                    findings.append({"type": "text-under-" + g["kind"],
                                     "a": t["text"][:24], "b": sev + " " + g["fill"],
                                     "overlap_pct": round(frac * 100, 1),
                                     "at": [round(x, 1) for x in ov]})
            elif g["stroke"] and g["sw"] >= 2.0 and _is_thin(g):
                findings.append({"type": "text-crossed-by-line",
                                 "a": t["text"][:24], "b": "stroke " + g["stroke"],
                                 "overlap_pct": round(_area(ov) / tarea * 100, 1),
                                 "at": [round(x, 1) for x in ov]})
    return findings


def check_overflow(items, viewbox, edge_tol):
    """T3 出框：文字超出所属容器边框，或超出画布。"""
    findings = []
    rects = [it for it in items if it["kind"] == "rect"]
    texts = [it for it in items if it["kind"] == "text"]
    vb_area = _area(viewbox) if viewbox else 0.0

    for t in texts:
        # 超出画布
        if viewbox:
            ov = _sides(t["bbox"], viewbox)
            worst = max(ov.values())
            if worst > edge_tol:
                findings.append({"type": "text-out-of-viewbox",
                                 "a": t["text"][:24],
                                 "b": "viewBox",
                                 "overflow_px": round(worst, 1),
                                 "sides": {k: round(v, 1) for k, v in ov.items() if v > edge_tol},
                                 "at": [round(x, 1) for x in t["bbox"]]})

        # 整页底板不参与容器归属：文字超出它等同于超出画布，上面已经报过
        cap = vb_area * 0.60 if vb_area > 0 else None
        c = _find_container(t, rects, cap)
        if c is None:
            continue
        inset = c["sw"] / 2.0  # 边框线画在路径上，内侧才是可用区
        b = c["bbox"]
        inner = (b[0] + inset, b[1] + inset, b[2] - inset, b[3] - inset)
        ov = _sides(t["bbox"], inner)
        worst = max(ov.values())
        if worst > edge_tol:
            findings.append({"type": "text-overflow",
                             "a": t["text"][:24],
                             "b": "container",
                             "overflow_px": round(worst, 1),
                             "sides": {k: round(v, 1) for k, v in ov.items() if v > edge_tol},
                             "container": [round(x, 1) for x in b],
                             "at": [round(x, 1) for x in t["bbox"]]})
    return findings


def check_shapes(items, viewbox, edge_tol):
    """图形类检测：图形跑出画布、图形互相重叠。

    只看实心色块（rect/circle/ellipse/path 带 fill），
    线状元素（line、带 stroke 的 path）单独看，避免把连线交叉当重叠。
    """
    findings = []
    solids = [it for it in items if it["kind"] in ("rect", "circle", "ellipse") and it["fill"]]

    # 1) 图形跑出画布
    if viewbox:
        solid_area = _area(viewbox)
        for g in solids:
            # 铺满画布的底板贴着画布边是正常的，不报
            if solid_area > 0 and _area(g["bbox"]) >= 0.60 * solid_area:
                continue
            ov = _sides(g["bbox"], viewbox)
            worst = max(ov.values())
            if worst > edge_tol:
                findings.append({"type": "shape-out-of-viewbox",
                                 "a": g["kind"] + " " + g["fill"],
                                 "b": "viewBox",
                                 "overflow_px": round(worst, 1),
                                 "sides": {k: round(v, 1) for k, v in ov.items() if v > edge_tol},
                                 "at": [round(x, 1) for x in g["bbox"]]})

    # 2) 实心色块互相重叠
    # 排除铺满画布的底板，它跟所有东西都重叠，报出来全是噪声
    solid_area = _area(viewbox) if viewbox else 0.0
    panels = [g for g in solids
              if not (solid_area > 0 and _area(g["bbox"]) >= 0.60 * solid_area)]
    for i in range(len(panels)):
        for j in range(i + 1, len(panels)):
            a, b = panels[i], panels[j]
            ov = _inter(a["bbox"], b["bbox"])
            if not ov:
                continue
            # 包含关系（卡片里套小块）不算重叠
            if _contains(a["bbox"], _center(b["bbox"])) or _contains(b["bbox"], _center(a["bbox"])):
                continue
            smaller = min(_area(a["bbox"]), _area(b["bbox"])) or 1e-9
            frac = _area(ov) / smaller
            if frac <= 0.15:
                continue
            findings.append({"type": "shape-overlap",
                             "a": a["kind"] + " " + a["fill"],
                             "b": b["kind"] + " " + b["fill"],
                             "overlap_pct": round(frac * 100, 1),
                             "at": [round(x, 1) for x in ov]})
    return findings


def _dedupe(findings):
    """同一文字与同一目标的重复提示合并，保留最严重的一条。"""
    def sev(f):
        return f.get("overlap_pct") or f.get("overflow_px") or 0

    best = {}
    for f in findings:
        key = (f["type"], f["a"], f["b"].split(" ")[0])
        if key not in best or sev(f) > sev(best[key]):
            best[key] = f
    return sorted(best.values(), key=lambda f: -(sev(f)))


def _is_marker(g, t):
    """小而实心的圆点画在字上，多半是着丝粒、序号点这类刻意标记，不算遮挡。

    判据：填充圆/椭圆，直径不超过字号的 1.6 倍，且不带描边样式之外的文字。
    """
    if g["kind"] not in ("circle", "ellipse"):
        return False
    if not g["fill"]:
        return False
    bx0, by0, bx1, by1 = g["bbox"]
    w, h = bx1 - bx0, by1 - by0
    if w > t["fs"] * 1.6 or h > t["fs"] * 1.6:
        return False
    return max(w, h) > 0


def _is_thin(g):
    """图形包围盒短边接近笔画厚度时视为线状元素，避免大面积色块描边误报。"""
    bx0, by0, bx1, by1 = g["bbox"]
    thick = min(bx1 - bx0, by1 - by0)
    return thick <= g["sw"] * 3.0 + 2


def main():
    ap = argparse.ArgumentParser(description="重叠与出框视觉障碍检测（提示性，不阻断交付）")
    ap.add_argument("svg")
    ap.add_argument("--json", help="findings 另存 JSON 文件路径")
    ap.add_argument("--tol", type=float, default=1.0, help="文字-文字交叠面积占较小盒比例阈值，默认 1.0")
    ap.add_argument("--edge-tol", type=float, default=1.0, help="出框余量像素，默认 1.0")
    ap.add_argument("--render", action="store_true", help="渲染层像素检查（本版未实现，接口占位）")
    args = ap.parse_args()
    if args.render:
        print("--render 渲染层检查本期未实现，已按包围盒模式运行。", file=sys.stderr)
    p = Path(args.svg)
    try:
        root = ET.parse(p).getroot()
    except (ET.ParseError, OSError) as e:
        print("SVG 解析失败: %s" % e, file=sys.stderr)
        sys.exit(2)
    if root.tag != NS + "svg":
        print("根元素不是 <svg>", file=sys.stderr)
        sys.exit(2)
    items = collect(root)
    vb = _viewbox(root)
    findings = check_overlap(items, args.tol / 100.0)
    findings += check_overflow(items, vb, args.edge_tol)
    findings += check_shapes(items, vb, args.edge_tol)
    findings = _dedupe(findings)
    print("check_overlap: %s — 提示 %d 条（提示性检查，不判失败）" % (p.name, len(findings)))
    for f in findings:
        if f["type"] == "text-overflow":
            side = "、".join("%s %.1fpx" % (k, v) for k, v in f["sides"].items())
            print("  [出框] 「%s」 超出容器 %s %s   容器=%s" %
                  (f["a"], side, "", f["container"]))
        elif f["type"] == "text-out-of-viewbox":
            side = "、".join("%s %.1fpx" % (k, v) for k, v in f["sides"].items())
            print("  [出画布] 「%s」 超出 %s   文字盒=%s" % (f["a"], side, f["at"]))
        elif f["type"] == "shape-out-of-viewbox":
            side = "、".join("%s %.1fpx" % (k, v) for k, v in f["sides"].items())
            print("  [图形出画布] %s 超出 %s   图形盒=%s" % (f["a"], side, f["at"]))
        elif f["type"] == "shape-overlap":
            print("  [图形重叠] %s vs %s  交叠 %s%% @ %s" %
                  (f["a"], f["b"], f["overlap_pct"], f["at"]))
        else:
            print("  [%s] 「%s」 vs %s  交叠 %s%% @ %s" %
                  (f["type"], f["a"], f["b"], f["overlap_pct"], f["at"]))
    if args.json:
        Path(args.json).write_text(json.dumps(findings, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0)


if __name__ == "__main__":
    main()
