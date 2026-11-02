# 海报版式素材库

用于竖版海报、方版卡片、横版封面这类图文排版：五组配色、三套字阶、三种版式、一套卡片几何，数值可以直接写进 SVG。技术图、P&ID、论文多面板不要用这套，走各自对应的参考。

数值来源是 minimax-draw 的 design-kit（同作者），2026-11-02 吸收进来，原仓库已删除。字体名按这台机器的实际解析结果给了替代，写之前先跑 `scripts/check_font.py` 确认。

## 一、五组配色

每组九个角色，角色含义固定，换组只换颜色，不改用法。

| 组名 | bg 底色 | surface 卡片 | ink 主字 | muted 次字 | deep 主色 | mid 中间调 | soft 弱色 | line 描边 | accent 点缀 |
|---|---|---|---|---|---|---|---|---|---|
| 林地 forest | #ffffff | #f6f4ef | #1b241f | #5c6b62 | #344e41 | #588157 | #a3b18a | #dad7cd | #b07a4a |
| 暮色 dusk | #1b1524 | #241c30 | #f6ece0 | #b8a9a0 | #f2b880 | #d97a5a | #6d3a5c | #3a2f4a | #ffd88a |
| 石板 slate | #f7f9fb | #ffffff | #1f2933 | #52606d | #2f6f8f | #4a8fae | #a9c7d8 | #dbe4ec | #e07a5f |
| 墨白 ink | #0f0f0f | #1a1a1a | #f2ede4 | #a09a90 | #c8a45c | #a3843f | #4a4438 | #2c2a26 | #f2ede4 |
| 宣纸 paper | #f4f1ea | #fffdf8 | #23201b | #6f675c | #7a4b2a | #a86b3c | #d8c9b4 | #e0d8c8 | #2f4a3d |

角色怎么用：

1. bg 铺整张画布，surface 只给卡片、输入框、需要抬起一层的小块。
2. ink 写标题和正文主句，muted 写注释、副标题、页脚。
3. deep 是主色，用在标题强调和关键数字；mid 低一级，用在序号和小节标记；soft 只做光斑、底纹，不写字。
4. line 画分隔线和描边，粗细 1 到 2。
5. accent 是点缀，只出现在很小的地方，大面积铺会抢主色。

对比度：五组的 ink 落在 bg 上都在 14:1 以上，够用；muted 在 bg 上是 4.9 到 5.6:1，22px 以下会偏浅，正文尽量用 ink，muted 留给注释。

## 二、三套字阶

每套三个家族，八个字号档位。字号单位是 px，画布按 1200 到 1920 宽设计。

| 套名 | display 主标 | text 正文 | mono 数字 | display | h1 | h2 | lead | body | small | caption | numeral |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 书卷 editorial | 衬线 | 无衬线 | 等宽 | 132 | 84 | 56 | 34 | 28 | 22 | 18 | 96 |
| 现代 modern | 无衬线粗 | 无衬线 | 等宽 | 128 | 80 | 52 | 34 | 28 | 22 | 18 | 92 |
| 仿宋 classic | 仿宋 | 无衬线 | 等宽 | 124 | 78 | 52 | 34 | 28 | 22 | 18 | 90 |

字体名要按本机实际解析写，原名很多在这台机器上会落到同一个字体：

| 原设计写的 | 本机实际落到 | 建议写 |
|---|---|---|
| Noto Serif SC | Noto Sans CJK SC | Noto Serif CJK SC |
| Noto Sans SC | Noto Sans CJK SC | Noto Sans CJK SC |
| MiSans | Noto Sans CJK SC | Noto Sans CJK SC，或先装 MiSans |
| STZhongsong | Noto Sans CJK SC | FangSong SC（仿宋）或 Noto Serif CJK SC |
| JetBrains Mono | Noto Sans CJK SC | DejaVu Sans Mono 或 Liberation Mono |

书卷套要衬线，主标必须写 `Noto Serif CJK SC`，写 `Noto Serif SC` 会静默变成无衬线。等宽数字要确认字体真的等宽，否则序号和页码对不齐。

## 三、三种版式

| 名称 | 画布 | 边距 | 栏数 | 栏距 | 内容宽 | 单栏宽 |
|---|---|---|---|---|---|---|
| 竖版 poster | 1600×2000 | 140 | 12 | 24 | 1320 | 88.0 |
| 方版 square | 1200×1200 | 96 | 6 | 20 | 1008 | 151.3 |
| 横版 wide | 1920×1080 | 110 | 12 | 24 | 1700 | 119.7 |

单栏宽按 `(内容宽 - (栏数-1) × 栏距) / 栏数` 算出来的，改画布或边距要重算，不要沿用旧数。

## 四、卡片几何

标准卡片按三行正文设计，所有值相对卡片左上角。

| 项 | 值 | 说明 |
|---|---|---|
| height | 360 | 卡片高 |
| gap | 32 | 卡片间距 |
| radius | 28 | 圆角 |
| pad | 56 | 左右内边距 |
| strokeWidth | 1 | 描边 |
| numeralOffset | 56 | 序号基线，从卡片顶往下 |
| titleBaseline | 126 | 标题基线 |
| bodyFirst | 208 | 第一行正文基线 |
| bodyLeading | 48 | 正文行距 |

紧凑卡片用在横版或卡片多于三张时：

| 项 | 值 |
|---|---|
| height | 320 |
| gap | 24 |
| radius | 24 |
| pad | 36 |
| numeralScale | 0.66 |
| titleScale | 0.78 |
| bodyScale | 0.8 |
| numeralBaseline | 92 |
| titleBaseline | 158 |
| bodyFirst | 202 |
| bodyLeading | 36 |

360 高的卡片正好放三行正文：第一行 208，第二行 256，第三行 304，再往下就压到卡片底边。第四行开始要加高卡片，或者把行距缩到 40 以内。

其他零件：分隔线粗细 2；右上角光斑透明度 0.18 到 0.34；顶部小标签（kicker）字距 260；主标字距 20；页脚和内容之间留 96。

## 五、换算到 SVG

字距在 design-kit 里是千分之一 em，SVG 的 `letter-spacing` 用 px，换算公式：

```
letter-spacing = tracking / 1000 × font-size
```

kicker 在 18px 时是 4.68px，主标在 124px 时是 2.48px。

其余对应关系：

1. 圆角用 `rx`，数值就是 radius。
2. 描边用 `stroke-width`，数值就是 strokeWidth，颜色用 line。
3. 光斑用 `radialGradient`，中心颜色 soft，透明度 0.18 到 0.34，边缘透明度 0。
4. 卡片底用 surface，描边用 line，阴影不要加，这套设计靠底色分层，不靠投影。
5. 序号用 mono，颜色 mid；标题用 display，颜色 ink；正文用 text，颜色 muted 或 ink。

## 六、配方字段

写内容时只需要这几个字段，其余由版式和组件几何推出来。

| 字段 | 含义 |
|---|---|
| layout | poster、square、wide 三选一 |
| palette | forest、dusk、slate、ink、paper 五选一 |
| typography | editorial、modern、classic 三选一 |
| kicker | 顶部小标签，一行 |
| title | 主标题，一行 |
| lead | 导语，字符串数组，一行一条 |
| cards | 卡片数组，每项给 index、title、lines |
| footer | 页脚，给 left 和 right |
| accentAt | 光斑中心坐标 |
| accentRadius | 光斑半径 |
| accentOpacity | 光斑透明度，0.18 到 0.34 |
| accentColor | 光斑用哪个角色，默认 soft |
| numeralColor | 序号颜色，默认 mid |
| leadColor | 导语颜色，默认 muted |
| cardLayout | row 或 stack，不写按画布高度自动判断 |

## 七、最小示例

方版，宣纸配色，一张卡片，三个正文行。坐标按 1200×1200、边距 96、卡片高 360 算。

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" width="1200" height="1200">
  <rect width="1200" height="1200" fill="#f4f1ea"/>
  <text x="96" y="254" font-family="'Noto Serif CJK SC',serif" font-size="124" fill="#23201b" letter-spacing="2.48">读法</text>
  <text x="96" y="330" font-family="'Noto Sans CJK SC',sans-serif" font-size="28" fill="#6f675c">三层拆开，逐段过完再合起来。</text>
  <line x1="96" y1="382" x2="1104" y2="382" stroke="#e0d8c8" stroke-width="2"/>
  <rect x="96" y="440" width="1008" height="360" rx="28" fill="#fffdf8" stroke="#e0d8c8" stroke-width="1"/>
  <text x="152" y="496" font-family="'DejaVu Sans Mono',monospace" font-size="90" fill="#a86b3c">01</text>
  <text x="152" y="566" font-family="'Noto Serif CJK SC',serif" font-size="52" fill="#23201b">结构</text>
  <text x="152" y="648" font-family="'Noto Sans CJK SC',sans-serif" font-size="28" fill="#6f675c">段首尾句先看</text>
  <text x="152" y="696" font-family="'Noto Sans CJK SC',sans-serif" font-size="28" fill="#6f675c">标论点与例证</text>
  <text x="152" y="744" font-family="'Noto Sans CJK SC',sans-serif" font-size="28" fill="#6f675c">用三句话概括</text>
</svg>
```

## 八、使用边界

1. 这套只适合海报、卡片、封面。技术图、流程图、P&ID、论文多面板不要套，节点关系和标注规则不一样。
2. 正文 28px 是按 1200 宽画布定的，投到 1920 宽要按比例放大，别直接沿用。
3. 卡片高度按三行正文算，行数变了要改高度或行距，不要硬塞。
4. 光斑透明度超过 0.4 会压字，只放在没有文字的一角。
5. 配色一次只选一组，不要跨组借颜色，九个角色已经够用。
6. 这套没有校验脚本，生成后还要走 `scripts/validate_svg.py`，重点看文字是否溢出、对比度是否够。
