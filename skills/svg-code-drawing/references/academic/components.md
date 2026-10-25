# 学术图组件库（Python 生成 SVG 的配方）

坐标全部用 mm，`R(v)=round(v,1)`。可执行版在 `scripts/academic_figure.py`。

## 头与图层

```python
def svg_header(w, h):  # mm
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
            f'viewBox="0 0 {w} {h}">')
```

面板分组用 `<g id="panel-a">`。图层顺序：背景、内容、标签、箭头。

## defs

标准箭头、开三角、加粗箭头、T 杠、占位斜纹：

```xml
<marker id="arrow-std" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4"
        markerHeight="4" orient="auto-start-reverse" markerUnits="strokeWidth">
  <path d="M0 0 L10 5 L0 10 z" fill="#333"/></marker>
<marker id="arrow-open" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4"
        markerHeight="4" orient="auto-start-reverse" markerUnits="strokeWidth">
  <path d="M0 0 L10 5 L0 10" fill="none" stroke="#333"/></marker>
<marker id="arrow-bold" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4"
        markerHeight="4" orient="auto-start-reverse" markerUnits="strokeWidth">
  <path d="M0 0 L10 5 L0 10 z" fill="#0072B2"/></marker>
<marker id="tbar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4"
        markerHeight="4" orient="auto-start-reverse" markerUnits="strokeWidth">
  <line x1="5" y1="0" x2="5" y2="10" stroke="#333" stroke-width="2"/></marker>
<pattern id="ph-hatch" patternUnits="userSpaceOnUse" width="3" height="3"
         patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="3"
         stroke="#DDD" stroke-width=".5"/></pattern>
```

标准箭头用于数据流，开三角用于注释，加粗箭头用于流程主路径，T 杠用于抑制/失活。

## 面板字母

```python
LABEL_OFFSET_Y = 2.5   # 基线在内容区顶边上方
HEAD_ROOM = 7.0        # 第一排面板上方预留
# <text x=内容x y=内容y-2.5 font-size="2.8" font-weight="bold">a</text>
```

## 图元

- 数据占位框：虚线圆角矩形 fill #F5F5F5，居中标题与副题，尺寸标注放框内右下角。
- 示意盒：白底圆角矩形 stroke 0.4，居中标签 2.2mm；先量标签宽再定盒宽（CJK 按 1×字号，ASCII 按 0.5×字号）。
- 流程步骤：实心圆（accent 色）加白字序号，下方标签。
- 比例尺：横线 0.6，两端 1mm 竖帽，居中标签（如 `10 µm`）。
- 色例：3mm 小色块，右侧 2mm 处标签，纵向间距 5mm。

## 箭头纪律

1. 全长至少 10mm；带标签至少 16mm；两端距元素至少 3mm。
2. 面板间距要走箭头时留至少 18mm（3+12+3）。
3. 标签：横箭头上方 3.5mm 居中；竖箭头左侧 3.5mm 右对齐；斜线放中点左上；不压线。
4. 拐弯用 Q 曲线圆角（半径 3mm）或 C 曲线，不用尖直角。
5. 生成前跑 pre-flight：`len<10` 报警并改布局（脚本内置）。

```python
def flow_arrow(x1, y1, x2, y2, label=None):
    # 横向:标签 y-3.5/middle；纵向:标签 x-3.5/end；斜体 2.2mm
```

## 布局算法

- `horizontal(panels, w=183, arrow_gap=20)`：单行按 width_ratio 分宽。
- `grid(panels, cols=2, gap_x=20, gap_y=12)`：列间距 20 留箭头位。
- `hierarchical(hero_ratio=0.5)`：主面板占半宽，其余右栏纵排。
- `top_bottom(top, bottom, gap_y=20)`：示意排上、数据排下。

边距 6mm；第一排上方加 5mm 字母头空。

## 色彩工具

```python
PRESETS = {'wong': {'a1':'#0072B2','a2':'#E69F00','a3':'#009E73','a4':'#D55E00'},
           'acs': …, 'nature_blues': …, 'monochrome': …}
```

- 用户给 1–2 色时，用 `shift_hue(30°/60°)` 派生三、四号色。
- `check_colorblind_safety(colors)`：两两相对亮度比小于 2.0 报警；红绿配必须加亮度差或图案。
- 派生规则：text=#222；arrow=accent1 压暗 30%；占位填充=accent1 提亮 95%。

## 质量要求

层序为背景、内容、标签、箭头；文字 containment 自检；不用彩色文字和装饰渐变；数据区用黑白灰加 Wong 板，示意区才允许浅填充。
