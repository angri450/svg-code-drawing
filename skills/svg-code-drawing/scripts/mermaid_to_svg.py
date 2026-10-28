# -*- coding: utf-8 -*-
"""Mermaid flowchart 子集 → house style SVG（草稿级，布局是分层网格不是 mermaid 原排版）。
支持：graph/flowchart 头 + TD/TB/LR/RL 方向；节点形状 [] () {} (()) [()] >]；
边 --> --- -.-> ==> 与 |边标签|；链式 A-->B-->C；subgraph 分组；%% 注释。
不支持（如实报）：classDef/style/点击回调/多图混排/百分比尺寸。
用法: uv run python mermaid_to_svg.py <in.mmd> [out.svg] [--title 标题]
产出后仍要跑 validate_svg.py + 渲染核对——导入器只保结构，不保审美。
"""
import re
import sys
from pathlib import Path

字体栈 = "'Times New Roman','FangSong SC',serif"
节点色, 文字色, 边色 = "#f8fafc", "#1e293b", "#2563eb"
描边 = "#334155"
字号 = 14


def 文宽(s: str) -> float:
    """CJK 1×字号 + ASCII 0.5×字号（house 宽度估算）"""
    cjk = sum(1 for ch in s if ord(ch) > 0x2E79)
    return cjk * 字号 + (len(s) - cjk) * 字号 * 0.5


节点令牌 = re.compile(
    r"([A-Za-z_][\w]*)\s*(?:\[\(([^)]*)\)\]|\[\[([^\]]*)\]\]|\[((?:[^\]]|\\])*)\]|\(\(([^)]*)\)\)|\{([^}]*)\}|\(([^)]*)\)|\>([^\]]*)\])?"
)
边令牌 = re.compile(r"(-\.->|==>|-->|---)\s*(?:\|([^|]*)\|)?")


def 解析(text: str):
    方向, 节点, 边, 组 = "TD", {}, [], {}
    行 = [l.strip() for l in text.splitlines()]
    i = 0
    while i < len(行):
        l = 行[i]
        i += 1
        if not l or l.startswith("%%"):
            continue
        m = re.match(r"^(?:graph|flowchart)\s+([A-Z]{2})", l)
        if m:
            方向 = m.group(1)
            continue
        if re.match(r"^(classDef|style|linkStyle|click|direction|end)\b", l):
            continue
        if l.startswith("subgraph"):
            m = re.match(r"subgraph\s+([\w]+)(?:\[([^\]]*)\])?", l)
            if m:
                gid, 标 = m.group(1), m.group(2) or m.group(1)
                ids = []
                while i < len(行) and 行[i] != "end":
                    ids += [t[0] for t in 节点令牌.findall(行[i])]
                    i += 1
                组[gid] = {"标": 标, "ids": list(dict.fromkeys(ids))}
            continue
        串 = l
        位置 = 0
        上一节点 = None
        待边 = None
        while 位置 < len(串):
            串 = 串[位置:]
            位置 = 0
            mb = 边令牌.match(串)
            if mb:
                待边 = (mb.group(1), mb.group(2))
                位置 = mb.end()
                continue
            mn = 节点令牌.match(串)
            if mn:
                nid = mn.group(1)
                形 = next((g for g in mn.groups()[1:] if g is not None), None)
                if 形 is not None:
                    形 = 形.strip().strip("/")  # [/x/] 平行四边形写法：斜杠不是标签内容
                节点.setdefault(nid, {"标": 形 if 形 is not None else nid})
                if 上一节点 and 待边:
                    边.append((上一节点, nid, 待边[1] or "", 待边[0]))
                上一节点, 待边 = nid, None
                位置 = mn.end()
                continue
            位置 = 1  # 跳过无法识别的字符
    return 方向, 节点, 边, 组


def 布局(方向, 节点, 边):
    邻 = {n: [] for n in 节点}
    for a, b, *_ in 边:
        邻.setdefault(a, []).append(b)
    状态, 回边 = {}, set()

    def dfs(u):
        状态[u] = 1
        for v in 邻.get(u, []):
            if 状态.get(v) == 1:
                回边.add((u, v))
            elif 状态.get(v) is None:
                dfs(v)
        状态[u] = 2

    for n in 节点:
        if 状态.get(n) is None:
            dfs(n)

    上限 = max(1, len(节点) - 1)
    层 = {n: 0 for n in 节点}
    for _ in range(len(节点) + 1):
        变 = False
        for a, b, *_ in 边:
            if (a, b) in 回边:
                continue
            if b in 层 and 层.get(a, 0) + 1 > 层[b] and 层.get(a, 0) + 1 <= 上限:
                层[b] = 层[a] + 1
                变 = True
        if not 变:
            break
    布局.回边 = 回边
    每层 = {}
    for n, r in 层.items():
        每层.setdefault(r, []).append(n)
    横 = 方向 in ("LR", "RL")
    位 = {}
    层间距, 节距 = 220, 150
    for r, ids in sorted(每层.items()):
        for k, n in enumerate(ids):
            x, y = (r * 层间距 + 80, k * 节距 + 80) if 横 else (k * 层间距 + 80, r * 节距 + 80)
            位[n] = (x, y)
    return 位, 横


def 画(方向, 节点, 边, 组, 标题):
    位, 横 = 布局(方向, 节点, 边)
    if not 位:
        raise SystemExit("Error: 没解析出任何节点")
    size = {}
    for n, info in 节点.items():
        w = max(120, 文宽(info["标"]) + 36)
        size[n] = (w, 46)
    xs = [p[0] + size[n][0] for n, p in 位.items()] + [p[0] for p in 位.values()]
    ys = [p[1] + size[n][1] for n, p in 位.items()] + [p[1] for p in 位.values()]
    宽, 高 = max(xs) + 80, max(ys) + 80
    L = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(宽)} {int(高)}" width="{int(宽)}" height="{int(高)}">',
         '<defs><marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
         f'<polygon points="0 0,10 3.5,0 7" fill="{边色}"/></marker></defs>',
         f'<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<text x="40" y="46" font-size="22" font-weight="700" fill="{文字色}" font-family="{字体栈}">{标题}</text>']
    for gid, g in 组.items():
        成员 = [位[i] for i in g["ids"] if i in 位]
        if not 成员:
            continue
        x0 = min(p[0] for p in 成员) - 24
        y0 = min(p[1] for p in 成员) - 24
        x1 = max(p[0] + size[i][0] for i, p in ((i, 位[i]) for i in g["ids"] if i in 位)) + 24
        y1 = max(p[1] + size[i][1] for i, p in ((i, 位[i]) for i in g["ids"] if i in 位)) + 24
        L.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="10" fill="#f1f5f9" '
                 f'stroke="#94a3b8" stroke-dasharray="6 4"/>')
        L.append(f'<text x="{x0+8}" y="{y0+18}" font-size="12" fill="#64748b" font-family="{字体栈}">{g["标"]}</text>')
    for a, b, 标, 型 in 边:
        if a not in 位 or b not in 位:
            continue
        (ax, ay), (bx, by) = 位[a], 位[b]
        aw, ah = size[a]
        bw, bh = size[b]
        if 横:
            x1, y1 = ax + aw, ay + ah // 2
            x2, y2 = bx, by + bh // 2
        else:
            x1, y1 = ax + aw // 2, ay + ah
            x2, y2 = bx + bw // 2, by
        dash = ' stroke-dasharray="6 4"' if 型 == "-.->" else ""
        宽度 = 2.5 if 型 == "==>" else 1.8
        L.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{边色}" stroke-width="{宽度}" fill="none"{dash} '
                 'marker-end="url(#arr)"/>')
        if 标:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2 - 8
            tw = 文宽(标) + 10
            L.append(f'<rect x="{mx-tw/2}" y="{my-12}" width="{tw}" height="18" fill="#ffffff" opacity="0.92"/>')
            L.append(f'<text x="{mx}" y="{my+2}" font-size="12" fill="#475569" text-anchor="middle" '
                     f'font-family="{字体栈}">{标}</text>')
    for n, (x, y) in 位.items():
        w, h = size[n]
        info = 节点[n]
        L.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{节点色}" stroke="{描边}" stroke-width="1.6"/>')
        L.append(f'<text x="{x+w/2}" y="{y+h/2+5}" font-size="{字号}" fill="{文字色}" text-anchor="middle" '
                 f'font-family="{字体栈}">{info["标"]}</text>')
    L.append("</svg>")
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:]]
    标题 = "Mermaid 导入草稿"
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
    方向, 节点, 边, 组 = 解析(源.read_text(encoding="utf-8"))
    svg = 画(方向, 节点, 边, 组, 标题)
    出.write_text(svg, encoding="utf-8")
    print(f"✓ {出}  ({len(节点)} 节点 / {len(边)} 边 / {len(组)} 组, 方向 {方向})")


if __name__ == "__main__":
    main()
