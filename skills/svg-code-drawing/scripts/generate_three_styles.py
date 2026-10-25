# -*- coding: utf-8 -*-
"""生成 three-styles.html：同一台储罐的三种视觉风格，全部纯代码（SVG）绘制，不调文生图。
用法: uv run python generate_three_styles.py [输出目录]
"""
import math

FONT = "'Segoe UI','Helvetica Neue',Arial,'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif"
FONT_HAND = "'Segoe Print','楷体',cursive"


def panel_pencil():
    刻线 = []
    y = 172
    i = 0
    while y < 346:
        x0 = 244 + (i % 3) * 3
        刻线.append(f'<line x1="{x0}" y1="{y}" x2="272" y2="{y - 15}"/>')
        y += 14
        i += 1
    排线 = "".join(刻线)
    return f'''<svg viewBox="0 0 700 500" xmlns="http://www.w3.org/2000/svg" width="700" height="500" style="max-width:100%;height:auto">
<defs>
  <filter id="wob1" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="4.5" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="grain1" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
</defs>
<rect width="700" height="500" fill="#fcfcf6"/>
<rect width="700" height="500" filter="url(#grain1)" opacity="0.13"/>
<g filter="url(#wob1)" fill="none" stroke="#4a4a4a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
  <path d="M55,420 Q350,414 645,418"/>
  <path d="M95,426 Q350,421 610,424" stroke-width="1.5"/>
  <ellipse cx="200" cy="150" rx="75" ry="22"/>
  <ellipse cx="200" cy="150" rx="66" ry="17"/>
  <path d="M125,150 L125,350"/>
  <path d="M275,150 L275,350"/>
  <path d="M125,350 Q200,379 275,350"/>
  <path d="M125,240 Q200,263 275,240" stroke-width="1.5"/>
  <path d="M148,371 L142,414"/><path d="M252,371 L258,414"/>
  <path d="M131,414 L154,414"/><path d="M245,414 L270,414"/>
  <path d="M58,76 L322,76"/>
  <path d="M112,68 L124,76 L112,84"/>
  <path d="M200,76 L200,127"/>
  <path d="M200,376 L200,408 L444,408 L444,401"/>
  <circle cx="470" cy="374" r="26"/>
  <circle cx="470" cy="374" r="10"/>
  <rect x="500" y="354" width="88" height="40" rx="5"/>
  <path d="M496,374 L500,374"/>
  <path d="M532,358 L532,390" stroke-width="1.5"/>
  <path d="M546,358 L546,390" stroke-width="1.5"/>
  <path d="M560,358 L560,390" stroke-width="1.5"/>
  <path d="M462,401 L462,415" stroke-width="1.8"/>
  <path d="M478,401 L478,415" stroke-width="1.8"/>
  <path d="M522,395 L522,415" stroke-width="1.8"/>
  <path d="M574,395 L574,415" stroke-width="1.8"/>
  <path d="M433,415 L617,415"/>
  <path d="M470,348 L470,326 L618,326"/>
  <path d="M606,318 L620,326 L606,334"/>
  <circle cx="352" cy="196" r="30" fill="#fcfcf6"/>
  <path d="M325,212 L281,234" stroke-dasharray="7 6"/>
  <g stroke="#6b6b6b" stroke-width="1.4">{排线}</g>
</g>
<g font-family="{FONT_HAND}" fill="#4a4a4a">
  <text x="24" y="37" font-size="21" font-weight="bold">① 铅笔素描</text>
  <text x="352" y="205" font-size="24" text-anchor="middle">LI</text>
  <text x="146" y="456" font-size="17" transform="rotate(-1.5 146 456)">T-101 储罐</text>
  <text x="452" y="456" font-size="17" transform="rotate(-1 452 456)">P-101 隔膜泵</text>
  <text x="58" y="59" font-size="15">进料</text>
  <text x="630" y="331" font-size="15">出料</text>
</g>
</svg>'''


def iso(x, y, z, ox=350, oy=400):
    """等轴测投影：x 右下、z 左下、y 向上。"""
    s30, c30 = 0.5, math.sqrt(3) / 2
    return ox + (x - z) * c30, oy + (x + z) * s30 - y


def pt(t_deg, y, rad):
    t = math.radians(t_deg)
    return iso(rad * math.cos(t), y, rad * math.sin(t))


def arc(t1, t2, y, rad, n=20):
    return [pt(t1 + (t2 - t1) * i / n, y, rad) for i in range(n + 1)]


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def panel_cutaway():
    r, rin, yl, yh, yf = 70, 62, 40, 170, 110
    t1, t2, h = 12, 78, 200

    底前弧 = poly(arc(-45, 135, 0, r))
    顶椭圆点 = poly(arc(0, 360, h, r, n=32))
    rx, ry = r * math.sqrt(2) * math.sqrt(3) / 2, r * math.sqrt(2) / 2

    气相 = poly(arc(t1, t2, yh, rin) + arc(t2, t1, yl, rin))
    液相 = poly(arc(t1, t2, yf, rin) + arc(t2, t1, yl, rin))
    液面 = poly(arc(t1, t2, yf, rin))
    外框 = poly(arc(t1, t2, yh, r) + arc(t2, t1, yl, r))
    内框 = poly(arc(t1, t2, yh, rin) + arc(t2, t1, yl, rin))

    液位点 = pt(45, (yl + yf) / 2, rin)
    壁厚点 = pt(t2, 155, r)

    return f'''<svg viewBox="0 0 700 500" xmlns="http://www.w3.org/2000/svg" width="700" height="500" style="max-width:100%;height:auto">
<defs>
  <pattern id="hw2" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="8" height="8" fill="#f6f2ea"/>
    <line x1="0" y1="0" x2="0" y2="8" stroke="#7a7168" stroke-width="1.3"/>
  </pattern>
</defs>
<rect width="700" height="500" fill="#ffffff"/>
<ellipse cx="350" cy="452" rx="130" ry="20" fill="#000000" opacity="0.08"/>
<polyline points="{底前弧}" fill="none" stroke="#555" stroke-width="2"/>
<line x1="264.4" y1="400" x2="264.4" y2="200" stroke="#555" stroke-width="2"/>
<line x1="435.6" y1="400" x2="435.6" y2="200" stroke="#555" stroke-width="2"/>
<polygon points="{顶椭圆点}" fill="#e9eef2" stroke="#555" stroke-width="2"/>
<polygon points="{气相}" fill="#eef2f6" stroke="#4a4a4a" stroke-width="1.8"/>
<polygon points="{液相}" fill="#cfe6f2" stroke="none"/>
<polyline points="{液面}" fill="none" stroke="#7db3d0" stroke-width="2"/>
<path d="M {外框} Z M {内框} Z" fill="url(#hw2)" fill-rule="evenodd" stroke="#4a4a4a" stroke-width="1.8"/>
<ellipse cx="350" cy="158" rx="13" ry="7.5" fill="none" stroke="#555" stroke-width="2"/>
<line x1="337" y1="158" x2="337" y2="202" stroke="#555" stroke-width="2"/>
<line x1="363" y1="158" x2="363" y2="202" stroke="#555" stroke-width="2"/>
<g stroke="#777" stroke-width="1.4" fill="none">
  <path d="M{液位点[0]:.0f},{液位点[1]:.0f} L470,332"/>
  <path d="M{壁厚点[0]:.0f},{壁厚点[1]:.0f} L205,252"/>
  <path d="M264,310 L172,342"/>
</g>
<g font-family="{FONT}" fill="#333" font-size="15">
  <text x="476" y="337">液位 60%</text>
  <text x="200" y="248" text-anchor="end">筒体壁厚（剖面线）</text>
  <text x="167" y="347" text-anchor="end">筒体</text>
  <text x="24" y="36" font-size="20" font-weight="bold">② 三维剖面（等轴测 · 局部剖视）</text>
  <text x="80" y="457" font-size="13">剖面（筒体金属壁）</text>
</g>
<rect x="40" y="442" width="34" height="18" fill="url(#hw2)" stroke="#4a4a4a" stroke-width="1.4"/>
</svg>'''


def panel_render():
    return f'''<svg viewBox="0 0 700 500" xmlns="http://www.w3.org/2000/svg" width="700" height="500" style="max-width:100%;height:auto">
<defs>
  <linearGradient id="bg3" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f7f9fb"/><stop offset="1" stop-color="#e2e7ec"/>
  </linearGradient>
  <linearGradient id="body3" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#6e777d"/><stop offset="0.10" stop-color="#b9c2c9"/>
    <stop offset="0.22" stop-color="#f2f6f8"/><stop offset="0.34" stop-color="#ffffff"/>
    <stop offset="0.52" stop-color="#dde4e9"/><stop offset="0.74" stop-color="#a8b2b9"/>
    <stop offset="0.90" stop-color="#7c858c"/><stop offset="1" stop-color="#5c646a"/>
  </linearGradient>
  <radialGradient id="top3" cx="0.4" cy="0.35" r="0.8">
    <stop offset="0" stop-color="#fafcfd"/><stop offset="1" stop-color="#d3dae0"/>
  </radialGradient>
  <filter id="bl3" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="7"/>
  </filter>
</defs>
<rect width="700" height="500" fill="url(#bg3)"/>
<ellipse cx="350" cy="447" rx="158" ry="22" fill="#0a1420" opacity="0.30" filter="url(#bl3)"/>
<path d="M250,150 L250,400 Q350,445 450,400 L450,150 Z" fill="url(#body3)"/>
<ellipse cx="350" cy="150" rx="100" ry="34" fill="url(#top3)" stroke="#aeb7bd" stroke-width="2"/>
<path d="M250,150 A100,34 0 0 0 450,150" fill="none" stroke="#c2cad0" stroke-width="5"/>
<rect x="301" y="160" width="20" height="236" rx="10" fill="#ffffff" opacity="0.5" filter="url(#bl3)"/>
<rect x="330" y="108" width="40" height="46" fill="url(#body3)"/>
<ellipse cx="350" cy="108" rx="20" ry="7" fill="#e9eef2" stroke="#a9b2b8" stroke-width="1.5"/>
<rect x="450" y="322" width="52" height="36" fill="url(#body3)"/>
<rect x="470" y="316" width="12" height="48" rx="3" fill="#7d868c"/>
<ellipse cx="502" cy="340" rx="8" ry="18" fill="#c7cfd4" stroke="#9aa3a9" stroke-width="1.5"/>
<ellipse cx="350" cy="272" rx="30" ry="32" fill="#aeb8bf" stroke="#79828a" stroke-width="3"/>
<ellipse cx="350" cy="272" rx="20" ry="22" fill="#c8d0d6"/>
<circle cx="350" cy="246" r="4" fill="#6d767d"/>
<circle cx="350" cy="298" r="4" fill="#6d767d"/>
<circle cx="326" cy="272" r="4" fill="#6d767d"/>
<circle cx="374" cy="272" r="4" fill="#6d767d"/>
<g font-family="{FONT}" fill="#333" font-size="15">
  <text x="24" y="36" font-size="20" font-weight="bold">③ 三维效果图（渐变着色）</text>
</g>
</svg>'''


def main():
    html = f'''<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>同一台储罐 · 三种风格</title></head>
<body style="margin:0;background:#e9edf1;font-family:{FONT}">
<h1 style="margin:14px 20px;font-size:17px;font-weight:600">同一台储罐 · 三种视觉风格 —— 全部由代码绘制（未调用文生图）</h1>
<div style="display:flex;flex-wrap:wrap;gap:16px;padding:0 20px 24px">
  <div style="background:#fff;padding:8px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.15)">{panel_pencil()}</div>
  <div style="background:#fff;padding:8px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.15)">{panel_cutaway()}</div>
  <div style="background:#fff;padding:8px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.15)">{panel_render()}</div>
</div>
</body></html>'''
    import os
    import sys
    出目录 = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(出目录, exist_ok=True)
    路径 = os.path.abspath(os.path.join(出目录, "three-styles.html"))
    with open(路径, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已写出: {路径}")


if __name__ == "__main__":
    main()
