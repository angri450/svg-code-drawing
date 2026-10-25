# 防错与通用技法

## 生成方式

复杂图用 Python 列表法：逐行 append 字符串再 join 写进文件，避免截断、转义、语法错误，不用 heredoc。
涉及投影、采样、循环排线时用 Python 生成，坐标可计算、可调参；手写坐标改一处动全身。

生成器：`scripts/generate-from-template.py <类型> <输出svg> '<json>'`，14 个类型名（agent/architecture/class/comparison/data-flow/er-diagram/flowchart/memory/mind-map/network-topology/sequence/state-machine/timeline/use-case）。未知类型报错并列出清单。
类型名只决定画布尺寸预设和标题栏样式，布局全靠 JSON 传入的节点坐标与连线；同一份数据传 architecture 与 flowchart 出图逐字节相同。

JSON 的键名写错不报错，内容直接不画出来。写之前按这份对照：

| 键 | 位置 | 写法 |
|---|---|---|
| `title` / `subtitle` | 顶层 | 标题栏文字 |
| `style` | 顶层 | 1 到 7，对应 `references/style-1` 到 `style-7` |
| `font_en` / `font_cn` | 顶层 | 字体名，先用 `check_font.py` 确认本机装没装 |
| `nodes[]` | 顶层 | 每项给 `id`、`kind`、`label`、`x`、`y`、`width`、`height`，可选 `sublabel`、`rx`、`fill`、`stroke`、`glow`、`cylinder_rings` |
| `arrows[]` | 顶层 | 每项给 `source`、`target`（都是节点 id）、`label`，可选 `source_port`、`target_port`、`route_points`、`flow`、`color`、`stroke_dasharray` |
| `containers[]` | 顶层 | 每项给 `label`、`x`、`y`、`width`、`height`，可选 `subtitle`、`side_label`、`fill`、`stroke` |
| `legend[]` | 顶层 | 每项给 `label`、`flow`、`color`；图例带底衬在顶层加 `legend_box` |

连线写 `source` 和 `target`，不是 `from` 和 `to`。写错键名不报错，连线直接不画出来。`source_port` 和 `target_port` 取 left/right/top/bottom，不写就自动判断方向；`route_points` 给出中间转折点，用来避开别的节点。`flow` 取 read/control 之类，决定线色。

生成器自己会做好的事，不用再写后处理脚本：

- 标签底衬的宽度按中英分别算：中文一个字宽，英文 0.58 个字宽。中文标签不会溢出底衬。
- 根元素带 `role="img"` 和 `aria-labelledby`，`<title>` 是第一个子元素。多张图放一页时给每张不同的 `title_id`。
- 图例的线样跟着图里走：哪一类连线是虚线，图例里那一类也画虚线，疏密照抄。图例项也可以自己写 `stroke_dasharray`。
- 圆柱里的两圈装饰椭圆会横穿文字，所以有字的圆柱不画那两圈，想画就写 `cylinder_rings: true`。

导入器只搬内容，不转换：源坐标、配色、字体弃掉，按本 skill 规则重排。

- `scripts/mermaid_to_svg.py`：flowchart 子集，含 subgraph、边标签、回流环自拆；不认 classDef/style。
- `scripts/drawio_to_svg.py`：压缩与未压缩双形态；泳道语义与精细 mxgraph 图形降级。
- 导入必须报告保真账：合并、降级、丢弃了什么逐条告知用户；不凭空造组件，不静默丢组件。

## 通用技法

- viewBox 定画布（逻辑图 960x600，工程图 700x500）；容器加 `style="max-width:100%;height:auto"` 做响应式。
- id 全文档唯一：多画板一页时 filter/gradient/pattern/clipPath 的 id 加画板前缀，否则滤镜串引用。
- CJK 字体栈带 fallback 链，英文名在前、中文名在后：`'Segoe UI','Helvetica Neue',Arial,'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif`；雅黑只在 Windows 有，缺链换机会掉字。链上的名字本机必须先跑 `check_font.py --check` 查一遍，没装的字体名会被静默回退，中文可能出日文字形。
- 文字字号不小于 12；引出线标注右对齐 `text-anchor="end"`。
- 椭圆弧不用硬凑 A 命令 sweep flag：用 Q 二次曲线（控制点取弧顶下 4/3 处）或采样 polyline。

## 可移植模式（目标是 PPT/打印/HMI/PDF）

这些链路的渲染器对 `filter`/`mask`/`clipPath`/`foreignObject` 支持残缺或行为不一致，校验加 `--portable` 拦下。
代价：手绘风三件套降级或禁用（滤镜是手抖与纸纹的核心）。可移植模式改选极简线稿或蓝图，铅笔风只保留不依赖滤镜的部分（手写体、双线、排线）。屏幕交付用全效果，办公链路用干净线稿。

## 常见坑速查

| 症状 | 病灶 | 修法 |
|---|---|---|
| 某形状整个不出现、无报错 | 属性塞了非法语法（Python list repr） | validate_svg.py 会点名 |
| 铅笔字抖到不可读 | 文字组也套了手抖滤镜 | 文字单独成组，滤镜只套图形 |
| 多画板滤镜/填充互相串 | id 重复 | id 加画板前缀 |
| 图糊/被裁 | svg 容器没响应式 | `style="max-width:100%;height:auto"` |
| 弧线方向画反 | A 命令 sweep flag 猜错 | Q 曲线或采样 polyline |
| 交叉箭头糊成一团 | 没画跳弧 | 5px 半径同色弧跳过，多处错开半径 |
| 箭头标签压线看不清 | 标签没底衬 | 标签下垫不透明背景矩形 |
| 中文变成日文写法 | 字体名没装或取错 .ttc 变体 | check_font.py --check，写带地区后缀的精确名 |
| PNG 导出报错 | 本机无 rsvg-convert | export_png.py（Edge headless），或 magick |
| 导出的图几乎全是空白 | 直接渲染了没填内容的模板 | 模板是带 `{{占位符}}` 的起手稿，先用 generate-from-template.py 填内容 |
| magick 出图字体全变默认字体 | 字体列表第一个名字本机没装 | 换成 check_font.py 确认过的字体名打头 |
| 导出 PNG 有白边或不写出来 | Edge 先退进程后写文件、SVG 固定宽高 | export_png.py 内部已处理 |
| mermaid 环图灌成八千像素高 | 最长路径分层遇环膨胀 | mermaid_to_svg.py 内部已拆回边 |

## 本机的 PNG 渲染路径（实测）

两条能走通：

| 工具 | 命令 | 说明 |
|---|---|---|
| `scripts/export_png.py` | `python scripts/export_png.py 图.svg 图.png` | 默认首选。Edge headless，字体栈完整，尺寸可控 |
| `magick`（ImageMagick 7.1.2-32，自带 librsvg 2.40.20） | `magick -density 192 -background none 图.svg 图.png` | 备选。中文和布局都正常，出图与 Edge 基本一致 |

`cairosvg` 看着在，实际不能用：包装脚本在，但底层 DLL 加载失败，导入即报错。

用 magick 的两个注意点：

一、字体列表的第一个名字必须是本机装了的字体。magick 拿列表里的第一个名字当主字体，第一个没装就整份字体回退成 Sans，后面的名字不再尝试。web 字体栈 `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` 在本机必然回退成 Sans，文字全变默认字体。生成器的 style 字体栈第一个是 `'Helvetica Neue'`（macOS 字体），Windows 本机没装，magick 渲染会整份回退；要 magick 出图就把第一个换成 `check_font.py --check` 确认过的名字（如 `'Segoe UI'`），或者直接用 `export_png.py`。

二、`templates/` 里的原始文件是带 `{{TITLE}}` 这类占位符的起手模板，直接渲染出来的图几乎全是空白。那是模板没填，不是渲染失败，先跑 `generate-from-template.py` 填内容再渲染。

调试 magick 时盯这两行输出：`couldn't load font ... falling back to "Sans"` 是字体没匹配上；`CSS unrecoverable error` 是 CSS 解析器在某一行卡住、这一段 CSS 全部丢掉。
