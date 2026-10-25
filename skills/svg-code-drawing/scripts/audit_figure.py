# -*- coding: utf-8 -*-
"""期刊图审计：字号 pt 合规、面板字母、色数、色盲对比、图注统计口径。
用法: uv run python audit_figure.py <fig.svg> [--journal nature]
判定基于实际 width 单位：width="183mm" 视为 mm 坐标；纯数字按 96dpi px 折算。
退出码 0=过，1=有 error 级问题（warn 不计）。
"""
import re
import sys
from pathlib import Path

def lum(hx):
    r, g, b = (int(hx.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    p = Path(sys.argv[1])
    文 = p.read_text(encoding="utf-8", errors="replace")
    err, warn = [], []

    if "viewBox" not in 文:
        err.append("缺 viewBox")
    mm模式 = bool(re.search(r'width="[\d.]+mm"', 文))

    for m in re.finditer(r'font-size="([\d.]+)"', 文):
        v = float(m.group(1))
        pt = v / 0.3528 if mm模式 else v * 0.75
        if pt < 5:
            err.append(f"字号 {v} ≈ {pt:.1f}pt < 5pt 下限")
            break
        if pt > 10.5:
            warn.append(f"字号 {v} ≈ {pt:.1f}pt > 10pt（面板字母上限）")
            break

    字母们 = re.findall(r'font-weight="bold"[^>]*>([A-Za-z])<', 文) + \
             re.findall(r'>([A-Za-z])</text>[^<]*font-weight="bold"', 文)
    if not 字母们 and "Figure" not in 文 and "Fig." not in 文:
        warn.append("未检测到面板字母（多面板图应有 a/b/c…）")

    def 有彩(hx):
        r, g, b = (int(hx[j:j+2], 16) for j in (1, 3, 5))
        return max(r, g, b) - min(r, g, b) > 40  # 灰阶/近灰不计彩色数
    色 = set(x.lower() for x in re.findall(r'fill="(#[0-9a-fA-F]{6})"', 文))
    色 = {c for c in 色 if 有彩(c)}
    if len(色) > 7:
        err.append(f"可见色 {len(色)} 种 > 7 上限")
    色列 = sorted(色)
    for i, c1 in enumerate(色列):
        for c2 in 色列[i+1:]:
            r1, g1, b1 = (int(c1[j:j+2], 16) for j in (1, 3, 5))
            r2, g2, b2 = (int(c2[j:j+2], 16) for j in (1, 3, 5))
            红绿 = ((r1 > 120 and g1 < 100 and r2 < 100 and g2 > 120) or
                    (r2 > 120 and g2 < 100 and r1 < 100 and g1 > 120))
            if 红绿:
                比 = (max(lum(c1), lum(c2)) + 0.05) / (min(lum(c1), lum(c2)) + 0.05)
                if 比 < 2.0:
                    err.append(f"红绿对 {c1}/{c2} 亮度比 {比:.1f} < 2.0，色盲不可辨")

    if re.search(r"Figure\s*\d|Fig\.\s*\d", 文) and not re.search(r"n\s*=\s*\d|±", 文):
        warn.append("有图注但缺统计口径（n = / ±）")

    for e in err:
        print(f"[ERR] {e}")
    for w in warn:
        print(f"[WARN] {w}")
    print(f"审计 {p.name}: {len(err)} err / {len(warn)} warn（mm模式={mm模式}, 色={len(色)}）")
    sys.exit(1 if err else 0)

if __name__ == "__main__":
    main()
