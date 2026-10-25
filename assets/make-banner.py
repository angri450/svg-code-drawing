#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 svg-code-drawing 仓库宣传图一：能力总览（深色渐变横幅）。"""

W, H = 1200, 620
FONT = "'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif"

out = []
out.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'role="img" aria-labelledby="figTitle figDesc" xml:lang="zh-CN" style="max-width:100%;height:auto">'
)
out.append('<title id="figTitle">SVG 代码制图能力总览</title>')
out.append('<desc id="figDesc">四大能力：技术图 14 类、工程示意图、手绘风 8 种、论文多面板图</desc>')

# ---------- defs ----------
out.append('<defs>')
out.append('  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">')
out.append('    <stop offset="0" stop-color="#0b1020"/>')
out.append('    <stop offset="0.52" stop-color="#1e1b4b"/>')
out.append('    <stop offset="1" stop-color="#312e81"/>')
out.append('  </linearGradient>')
out.append('  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">')
out.append('    <stop offset="0" stop-color="#7c3aed" stop-opacity="0.35"/>')
out.append('    <stop offset="1" stop-color="#7c3aed" stop-opacity="0"/>')
out.append('  </radialGradient>')
out.append('  <linearGradient id="cardStroke" x1="0" y1="0" x2="0" y2="1">')
out.append('    <stop offset="0" stop-color="#a78bfa" stop-opacity="0.42"/>')
out.append('    <stop offset="1" stop-color="#a78bfa" stop-opacity="0.10"/>')
out.append('  </linearGradient>')
out.append('</defs>')

# ---------- 背景 ----------
out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>')
out.append('<ellipse cx="1050" cy="80" rx="320" ry="220" fill="url(#glow)"/>')
out.append('<ellipse cx="120" cy="580" rx="280" ry="180" fill="url(#glow)" opacity="0.55"/>')

# 点阵装饰（右上）
dots = []
for row in range(5):
    for col in range(8):
        x = 830 + col * 34
        y = 40 + row * 34
        dots.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#a78bfa" opacity="0.18"/>')
out.append('<g>' + ''.join(dots) + '</g>')

# ---------- 顶部标题 ----------
out.append(
    f'<text x="{W/2}" y="88" text-anchor="middle" font-family="{FONT}" font-size="13" '
    f'letter-spacing="6" fill="#a78bfa">SVG CODE DRAWING</text>'
)
out.append(
    f'<text x="{W/2}" y="150" text-anchor="middle" font-family="{FONT}" font-size="46" '
    f'font-weight="700" fill="#ffffff">SVG 代码制图</text>'
)
out.append(
    f'<text x="{W/2}" y="192" text-anchor="middle" font-family="{FONT}" font-size="16" '
    f'fill="#94a3b8">不调文生图，纯代码写 SVG，文字不乱码</text>'
)

# ---------- 四栏能力卡片 ----------
CARDS = [
    {
        "x": 40, "accent": "#a78bfa",
        "title": "技术图 14 类",
        "lines": ["架构 · 流程 · 时序", "ER · 状态机 · 时间线", "对比矩阵 · 思维导图", "网络拓扑 · 用例图"],
    },
    {
        "x": 325, "accent": "#60a5fa",
        "title": "工程示意图",
        "lines": ["P&amp;ID · 工艺流程", "设备图 · 剖面图", "立体效果", "配方：铅笔 / 剖面 / 渐变"],
    },
    {
        "x": 610, "accent": "#fb923c",
        "title": "手绘风 8 种",
        "lines": ["白板 · 粉笔 · 蓝图", "水彩 · 方格纸", "铜版雕刻 · 极简线稿", "3D 等轴测"],
    },
    {
        "x": 895, "accent": "#34d399",
        "title": "论文多面板图",
        "lines": ["Cell / Nature 风", "信息图", "Graphical Abstract", "投稿审计：字号 · 色盲"],
    },
]

CARD_Y, CARD_W, CARD_H = 238, 265, 280


def icon(kind, cx, cy, accent):
    """卡片顶部小图示，56px 高。"""
    g = []
    if kind == "flow":  # 技术图：三块 + 箭头
        for i in range(3):
            x = cx - 78 + i * 62
            fill = accent if i == 1 else "rgba(255,255,255,0.06)"
            stroke = accent if i == 1 else "rgba(255,255,255,0.35)"
            g.append(f'<rect x="{x}" y="{cy-16}" width="44" height="32" rx="7" fill="{fill}" '
                     f'fill-opacity="{"0.85" if i == 1 else "1"}" stroke="{stroke}" stroke-width="1.4"/>')
            if i < 2:
                ax = x + 44
                g.append(f'<line x1="{ax+4}" y1="{cy}" x2="{ax+14}" y2="{cy}" stroke="{accent}" stroke-width="1.8"/>')
                g.append(f'<path d="M {ax+14} {cy-3.4} L {ax+20} {cy} L {ax+14} {cy+3.4} Z" fill="{accent}"/>')
    elif kind == "pipe":  # 工程图：管道 + 阀门
        g.append(f'<rect x="{cx-80}" y="{cy-9}" width="120" height="18" rx="4" fill="none" stroke="{accent}" stroke-width="1.8"/>')
        g.append(f'<path d="M {cx+40} {cy-9} l 0 18 M {cx+40} {cy} l 26 0" stroke="{accent}" stroke-width="1.8" fill="none"/>')
        g.append(f'<circle cx="{cx+40}" cy="{cy}" r="7" fill="none" stroke="{accent}" stroke-width="1.8"/>')
        g.append(f'<path d="M {cx-80} {cy-22} l 0 -8 l 16 0" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" fill="none"/>')
    elif kind == "hand":  # 手绘风：抖动的波浪线 + 笔
        g.append(f'<path d="M {cx-80} {cy+8} C {cx-50} {cy-16}, {cx-30} {cy+18}, {cx-2} {cy-6} '
                 f'S {cx+40} {cy-14}, {cx+62} {cy-4}" fill="none" stroke="{accent}" stroke-width="2.4" '
                 f'stroke-linecap="round" opacity="0.9"/>')
        g.append(f'<path d="M {cx-80} {cy+18} C {cx-46} {cy+2}, {cx-20} {cy+26}, {cx+10} {cy+6} '
                 f'S {cx+46} {cy+2}, {cx+66} {cy+10}" fill="none" stroke="{accent}" stroke-width="1.6" '
                 f'stroke-linecap="round" opacity="0.45"/>')
    elif kind == "panels":  # 论文图：2x2 面板
        for i in range(4):
            x = cx - 74 + (i % 2) * 78
            y = cy - 26 + (i // 2) * 30
            fill = accent if i == 0 else "rgba(255,255,255,0.05)"
            g.append(f'<rect x="{x}" y="{y}" width="66" height="24" rx="4" fill="{fill}" '
                     f'fill-opacity="{"0.8" if i == 0 else "1"}" stroke="rgba(255,255,255,0.3)" stroke-width="1.2"/>')
            if i == 0:
                g.append(f'<text x="{x+33}" y="{y+16}" text-anchor="middle" font-family="{FONT}" '
                         f'font-size="12" font-weight="700" fill="#0b1020">A</text>')
    return '<g>' + ''.join(g) + '</g>'


icons = ["flow", "pipe", "hand", "panels"]
for card, ic in zip(CARDS, icons):
    x = card["x"]
    accent = card["accent"]
    out.append(
        f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="16" '
        f'fill="rgba(255,255,255,0.045)" stroke="url(#cardStroke)" stroke-width="1.2"/>'
    )
    out.append(icon(ic, x + CARD_W / 2, CARD_Y + 52, accent))
    out.append(
        f'<text x="{x + CARD_W/2}" y="{CARD_Y + 122}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="19" font-weight="700" fill="#ffffff">{card["title"]}</text>'
    )
    out.append(
        f'<line x1="{x+26}" y1="{CARD_Y+142}" x2="{x+CARD_W-26}" y2="{CARD_Y+142}" '
        f'stroke="rgba(255,255,255,0.12)" stroke-width="1"/>'
    )
    for i, line in enumerate(card["lines"]):
        out.append(
            f'<text x="{x + CARD_W/2}" y="{CARD_Y + 176 + i*30}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="13.5" fill="#cbd5e1">{line}</text>'
        )

# ---------- 底部数字胶囊 ----------
PILLS = ["14 种技术图", "8 种手绘风", "7 套配色", "10 类校验", "10 个模板"]


def text_width(s, size):
    w = 0.0
    for ch in s:
        w += size * (1.0 if ord(ch) > 0x2E80 else 0.58)
    return w


pill_size, pad, gap = 13.5, 17, 12
widths = [text_width(p, pill_size) + pad * 2 for p in PILLS]
total = sum(widths) + gap * (len(PILLS) - 1)
x = (W - total) / 2
pill_y, pill_h = 552, 34
for p, w in zip(PILLS, widths):
    out.append(
        f'<rect x="{x}" y="{pill_y}" width="{w}" height="{pill_h}" rx="{pill_h/2}" '
        f'fill="rgba(124,58,237,0.18)" stroke="rgba(167,139,250,0.35)" stroke-width="1"/>'
    )
    out.append(
        f'<text x="{x + w/2}" y="{pill_y + 22}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{pill_size}" fill="#c4b5fd">{p}</text>'
    )
    x += w + gap

out.append('</svg>')

import os

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.svg")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("✓ banner.svg 生成完成")
