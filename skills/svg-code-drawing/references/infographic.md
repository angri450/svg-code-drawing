# 信息图：一页一个数据故事

适合“一个大数字 + 一条比例 + 一组刻度 + 一句结论”的信息图。不是仪表盘，也不是三栏卡片；一页只讲一个量。

## 设计系统

- 画布 1536×864，16:9。
- 纸面：象牙白，出图通道出的细纤维纹理；右侧可留一条暗红边。
- 标题和大数字：Noto Serif CJK SC Bold（思源宋体），深红 `#8E1B2A`。
- 正文、标签、来源：Noto Sans CJK SC（思源黑体），炭灰 `#3F3F3F` / 灰 `#6B6B6B`。
- 细线：亮红 `#C8102E`；辅助线：`#D8D2C6`。
- 标题用 `/` 分隔信息块，例如“一张图 / 25步 / 616秒”，比逗号更紧凑。

## 数据规格

```json
{
  "eyebrow": "推理时间账",
  "title": "一张图 / 25步 / 616秒",
  "subtitle": "MiniMax 生图 · 1536×864",
  "metric": { "value": "22.55s", "label": "每步采样" },
  "bar": {
    "total": 616.3,
    "caption": "总耗时 616s",
    "segments": [
      { "label": "加载与编码", "value": 52.6, "suffix": "s", "color": "#D8D2C6" },
      { "label": "采样", "value": 563.7, "suffix": "s", "color": "#8E1B2A" }
    ]
  },
  "ticks": { "count": 25, "label": "25 步 × 22.55s" },
  "takeaway": "采样占 91.5%，瓶颈在 DiT 前向，不在加载。",
  "source": "数据：本地单次运行，1536×864，25 步，CFG 3，seed 42。"
}
```

字段说明：

| 字段 | 作用 |
|---|---|
| `eyebrow` | 左上角小标签 |
| `title` | 主标题，建议用 `/` 分隔 2-3 段 |
| `subtitle` | 口径、设备、尺寸 |
| `metric` | 大数字和下方标签 |
| `bar.total` | 比例条总量；不写就按 segments 求和 |
| `bar.segments` | 2-4 段，`value` 必须大于 0；窄段标签在上方，宽段标签和百分比在条内 |
| `bar.caption` | 条下方总量说明 |
| `ticks` | 刻度数量和标签；`count=0` 不画 |
| `takeaway` | 一句话结论，放在下部 |
| `source` | 数据来源/口径，放最底部 |
| `colors` / `fonts` | 可选覆盖默认配色和字体 |

完整样例见 `examples/infographic-metric.json`，生成结果见 `examples/infographic-metric.svg`。

## 生成 SVG

```bash
python scripts/build_infographic.py examples/infographic-metric.json out.svg
```

生成器负责：

- 按 `bar.total` 算每段宽度和百分比。
- 宽段（≥160px）标签居中在条上方，百分比在条内；窄段标签放条上方，并把百分比并进标签。
- 按 `ticks.count` 画 25 个刻度，间距 30px。
- 标题、大数字、结论用衬线；其余用黑体。
- 输出透明底 SVG，交给 `compose_layers.py` 叠纸面。

## 纸面底图

信息图的底图只要纸，不要内容。prompt 模板：

> A clean warm ivory paper background for a high-end consulting infographic. Very subtle natural fiber texture, soft diffused daylight from the upper left, a faint deep crimson vertical accent at the far right edge, generous empty space across the center and left, no text, no objects, no charts, no dark blocks, no shadows, minimal, calm, editorial, high resolution.

走 MiniMax 出图通道，`aspect_ratio` 用 `16:9`，`resolution` 用 `2K`：

```bash
mcode-tools connector call connector__matrix__generate_image --args-file 纸面参数.json
```

```json
{"requests": [{"prompt": "上面那段英文 prompt", "aspect_ratio": "16:9", "resolution": "2K"}]}
```

跑完先目检：中央和左侧必须是干净纸面，不能有物体、文字、深色块；右侧暗红边可以有，但不能压到正文区。

## 合成与验收

```bash
uv run --with opencv-python-headless --with numpy --with resvg-py python scripts/compose_layers.py \
  --bg paper.png --svg out.svg --out final.svg --png final.png --wide 1536 --renderer resvg
```

验收：

1. `validate_svg.py final.svg` 全部通过。
2. 标题、大数字、比例条、刻度、结论、来源都完整，没有压边或重叠。
3. 缩到目标尺寸（PPT 投屏约 1280 宽）后，最小字号仍可读。
4. 数据口径和 `source` 对得上；不要把示例数字当真实数据。

## 标注回改

```bash
uv run --with pillow python scripts/annotate_html.py final.png --out review.html --title "信息图评审"
```

把 review.html 发布成链接或发给用户，用户框选/点选后导出 JSON。拿到 JSON 后按坐标改 SVG：

- 位置/字号/颜色类意见：直接改 `out.svg` 或 spec，重跑 `build_infographic.py`。
- 数据类意见：改 spec 的 `value`/`total`/`ticks`，不要手改 SVG 里的数字。
- 底图类意见（纸太脏、暗块侵入）：重出纸面底图，不动 SVG。

每轮只合成一次；改完重新导出 PNG，再生成一份新的标注页给用户复查。

## 边界

- 设计空间固定 1536×864；要别的画幅，先缩放 viewBox，不要直接改坐标。
- 生成器不自动换行；标题太长就手动断成两行或改用 `/` 分段。
- 大数字控制在 6 个字符内；超过 6 个字符会撞到右侧比例条，缩短数值或换单位。
- 副标题一行建议不超过 45 个字符，太长会顶到画布右边。
- 窄段太多时标签可能挤；超过 4 段建议改成横向条形+图例，或拆成两张图。
- 信息图适合“一个量”；多个并列指标不要硬塞进一张，拆页或换图表类型。
