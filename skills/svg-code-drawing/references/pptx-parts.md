# pptx 的零件：图片形态与表格

零件是版式里的可替换单元，决定图片长什么样、表格怎么排。下面是形状规格与函数签名。

页面 spec 里用 `parts` 字段调用，两种写法：

**图片类用字符串 id**，替换版式里已有的图片位。

**叠加类用对象**，版式画完再叠上去，坐标和数据自己定：

```json
{ "page": 2, "layout": "statement-offset", "photo": "page_images/ridge.png",
  "parts": [
    "honeycomb-6",
    { "id": "capsule", "x": 200, "y": 62, "text": "2025 · 秋" },
    { "id": "hairline", "x": 96, "y": 655, "w": 420, "label": "分节" }
  ] }
```

## 图片形态

`mask_picture(slide, path, x, y, w, h, shape=..., fx=..., fy=...)`

| shape | 说明 | 适合 |
|---|---|---|
| `rect` | 矩形 | 贴边对齐 |
| `rounded` | 圆角 14% | 卡片化信息区 |
| `circle` | 圆形 | 头像、章节图标、时间线节点 |
| `hexagon` | 六边形 | 并列三到四个 |
| `parallelogram` | 平行四边形 | 流程、趋势 |
| `arch` | 拱形 | 封面、人物页 |

`fx` / `fy` 控制取原图哪个位置，同一张照片做多个形状时内容不会重复。

## 图片组合

`grid_picture(slide, path, x, y, w, h, cols=2, rows=2, gap=8, shape="rounded")`
N×N 图片墙，每格取原图不同区域。

`honeycomb_picture(slide, path, x, y, w, h, gap=0.05, cols=3, rows=2)`
六边形蜂巢，第二行错位半个步长，格子之间均匀留缝。

## 表格

`three_line_table(slide, p, x, y, w, rows, ratios, row_h=46)`
三线表：顶线 2.5 磅、表头下 1 磅、底线 2.5 磅，没有竖线。`ratios` 是各列宽度占比。

没有用 python-pptx 的表格对象，因为单元格边框要绕着 XML 设，`a:tcPr` 里 `lnL`、`lnR`、`lnT`、`lnB` 的插入顺序有讲究，写错会报文件损坏。直接用线条画更可控。

## 比例

- 文字区与图片区取 1 比 1.3。标准黄金分割 1 比 1.618 在文字较长时放不下。
- 形状要配接近正方的框，竖长框会把六边形和圆形拉瘦。
- 组合件的间隔系数 0.05 到 0.09，越大越散。
- 形状裁切后不要加矩形白边，会露出四个角。

