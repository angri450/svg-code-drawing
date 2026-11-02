---
name: svg-code-drawing
description: 用 SVG 代码画图：工程示意图、技术图、论文多面板图、单页信息图，也能把 24 种版式排成整份 PPT。触发词：画图、示意图、架构图、流程图、P&ID、论文配图、信息图、手绘风、SVG、PPT、演示文稿、deck。
license: Apache-2.0
compatibility: Python 3.9+；PNG 导出支持 resvg-py / rsvg-convert / cairosvg / Chromium 任一
metadata:
  version: 3.1.1
---

# SVG 代码制图

不调文生图，纯代码写 SVG。文字用系统字体直排，结构坐标逐点计算。

本 skill 负责单张图。要做多页演示文稿，走本工作区的 `code/ppt_styles`：25 个版式骨架、16 套风格、直接输出 .pptx，见路线图最后一行。

## 路线图（按需加载）

| 要做的事 | 去处 |
|---|---|
| 工程图（P&ID/设备/剖面/三维效果） | [references/engineering-three-styles.md](references/engineering-three-styles.md)，基准脚本 `scripts/generate_three_styles.py` |
| 手绘风（白板/粉笔/蓝图/水彩/方格纸/铜版雕刻/极简线稿/3D 等轴测） | [references/hand-drawn-styles.md](references/hand-drawn-styles.md) |
| 技术图（架构/流程/时序/ER/状态机/甘特等 14 类型） | [references/diagram-types.md](references/diagram-types.md)，骨架 `templates/`（10 种，供手写起底，生成器只读取 viewBox），生成器 `scripts/generate-from-template.py` |
| 论文/期刊多面板图（Cell/Nature 风、信息图、Graphical Abstract） | `references/academic/` 三份：journal-spec 版面数字、figure-workflow 工作流与图注、components 组件库；`scripts/academic_figure.py` 生成 mm 坐标骨架与 2-3 个变体；正样数据 `examples/academic-panels.json`、`examples/academic-arrows.json`；成品范例 `scripts/example_cell_figure.py`；投稿审计 `scripts/audit_figure.py`（字号 pt、色数、色盲、统计口径） |
| 信息图（一页一个数据故事：大数字 + 比例条 + 刻度 + 结论） | [references/infographic.md](references/infographic.md)，生成器 `scripts/build_infographic.py`，样例 `examples/infographic-metric.json` 与 `examples/infographic-metric.svg` |
| 海报/卡片/封面（竖版 1600×2000、方版 1200×1200、横版 1920×1080，五组配色、三套字阶、卡片几何） | [references/poster-layout-kit.md](references/poster-layout-kit.md) |
| 自由曲线（河流、飘带、山脊、卷轴这类「像活的」曲线） | [references/curve-composition.md](references/curve-composition.md)，生成器 `scripts/curve_builder.py`，样例 `examples/curve-river.json` |
| 画风质感（吉卜力/日漫/水彩氛围底） | [references/hybrid-pipeline.md](references/hybrid-pipeline.md)，底图走 MiniMax 出图通道，SVG 线稿与文字叠印，合成脚本 `scripts/compose_layers.py` |
| 读图评审、在图上框选/点选标注 | [references/annotation-review.md](references/annotation-review.md)，脚本 `scripts/annotate_html.py` |
| 多页 PPT / 演示文稿（25 版式、16 风格、输出 .pptx） | 本工作区 `code/ppt_styles`：先在 `gallery.html` 选版式和风格，导出 JSON，再跑 `python code/ppt_styles/build_deck.py decks/deck.json out.pptx`；单页要整张成品图时，用本 skill 的 `compose_layers.py` 合成、`export_png.py` 导出，deck 里写 `image` 字段；只是版式内某处放照片则写 `photo`。生成后的检查项见 [references/pptx-pitfalls.md](references/pptx-pitfalls.md) |
| pptx 零件（图片形态、图片墙、蜂巢、三线表） | [references/pptx-parts.md](references/pptx-parts.md)，选择界面在 `code/ppt_styles/parts.html`，页面 spec 里用 `parts` 字段调用 |
| 技术图配色 | `references/style-1..7*.md`，默认 style-1；选型见 style-diagram-matrix.md |
| 字体（中英混排、.ttc 集合规避、字体检查） | [references/fonts.md](references/fonts.md)，脚本 `scripts/check_font.py` |
| 布局尺寸算术（居中、基线 0.35、盒高 3×字号、连接线、交付自查） | [references/layout-arithmetic.md](references/layout-arithmetic.md) |
| 生成方式、防错、坑速查、可移植模式、布局最佳实践 | [references/pitfalls.md](references/pitfalls.md)、[references/svg-layout-best-practices.md](references/svg-layout-best-practices.md) |
| 导入现成图（mermaid、draw.io） | `scripts/mermaid_to_svg.py`、`scripts/drawio_to_svg.py` |
| 动画、交互、图表、地图、图标 sprite | [references/svg-beyond-drawing.md](references/svg-beyond-drawing.md) |
| 产品图标 | [references/icons.md](references/icons.md) |

## 工作流

0. 语义先行：一句话写清这张图要传达的机制。每个形状对应一个能命名的真实概念，叫不出名字的删掉。节点上限 9，超过拆成两张图。
1. 分类：实物/设备/P&ID/剖面走工程示意图；逻辑/架构/流程走技术逻辑图。按路线图加载对应 reference。
2. 选风格与字体：工程图用 E1 铅笔、E2 剖面、E3 渐变三套配方；手绘风八选一；技术图默认 style-1。字体按需指定，`font_en` 与 `font_cn` 两个参数做中英混排；写名字前先跑 `scripts/check_font.py` 查解析结果，避开 .ttc 集合取错变体（索引 0 常是日文）和未装字体的静默回退，见 fonts.md。
3. 生成：技术图用 `scripts/build_diagram.py` 起步（生成、校验、导出一条命令），信息图先写 JSON 规格再用 `scripts/build_infographic.py` 出 SVG，工程图写 Python 脚本（列表法），有现成稿走导入器。命令见 pitfalls.md。
4. 校验：`uv run python scripts/validate_svg.py <svg>`（10 类检查）。目标为 PPT/打印/HMI 时加 `--portable`。
5. 人机交互审查（所有路线以这一步收尾）：同一台机器时，产物经 `bundle_html.py` 打成 HTML 壳（剥固定宽高、响应式缩放、内联 DOM 可点选）→ 在产物目录起 `uv run python -m http.server 8897`（文件名用 ASCII，中文名在 http.server 上 404）→ 浏览器工具开 `http://127.0.0.1:8897/<文件>.html` → 用户点选元素 → 改线稿坐标 → 重新合成 → 刷新复查。浏览器不在同一台机器时，不要发 `127.0.0.1`，改用 `scripts/annotate_html.py` 生成单文件标注页，用户框选/点选并导出 JSON。验收两条：元素、关系、文字齐全；缩到目标介质实际尺寸仍可读。裸开 SVG 有两个问题：固定宽高会缩成小块并留白边；裸 SVG 文档无法点选。
6. 交付：用户确认后运行 `export_png.py`（resvg-py / rsvg-convert / cairosvg / Chromium 自动降级出 PNG），保留原 SVG/HTML；用 `uv run` 时加 `--with resvg-py`，本机已装 resvg-py。`extract_brand.py` 可选，用于站点配色对齐。

## 判定：走哪一半

| 用户要的 | 走法 |
|---|---|
| 架构图/流程图/时序图/ER/UML/状态机/时间线/矩阵/思维导图/网络拓扑 | 技术逻辑图：diagram-types.md + 配色 references |
| 设备图/P&ID/工艺流程/剖面/立体效果/手绘氛围 | 工程示意图：engineering-three-styles.md |
| 说不清 | 逻辑关系走技术图；实物/设备走工程图 |
| 多页演示文稿、一套 deck、统一风格 | 不走单图流程，改用 `code/ppt_styles` |

## 响应契约

- 画面与页面不加署名、来源、水印类文案（含生成器默认值）。
- svg 带 `role="img"` 与 `aria-labelledby`，`<title>` 为第一个子元素。
- 导入产物逐条报告合并、降级、丢弃。
- 字体：中英混排时 font_en 在前、font_cn 在后；SVG 根元素带 `xml:lang="zh-CN"`，多语言字体按简中字形渲染。
