# 手绘风格 SVG 配方库

每种风格由背景、线条、滤镜、文字四部分组成。通用手抖层参数在 SKILL.md 风格 1，各风格只列差异项。

## 1. 白板马克笔（whiteboard）

适合快速草图、头脑风暴图。

- 背景：`#ffffff`，可加大号灰字"白板反光"（大圆角矩形 opacity 0.03）。
- 线条：粗 3-4px、`stroke-linecap="round"`，四色：蓝 `#1d4ed8`、红 `#dc2626`、绿 `#16a34a`、黑 `#111827`。
- 手抖：`baseFrequency="0.02" scale="2.5"`，抖动幅度克制。
- 填充：用略歪斜的路径（相对轮廓偏移 2px、opacity 0.25）模拟涂色出边，不用规整实心块。
- 文字：`'Segoe Print','Comic Sans MS',cursive`，用线条同色。
- 点缀：箭头尾部带小回勾，问号、感叹号手写在旁边。

## 2. 黑板粉笔（chalkboard）

适合教学图、公式推导图。

- 背景：深绿 `#1f3d2b` 或深蓝黑 `#0f172a`，叠一层低透明度噪点。
- 线条：粉笔白 `#f5f5f4`，点缀黄 `#fef3c7`、青 `#a5f3fc`；粗 2.5-3px。
- 粉笔质感滤镜：噪点做遮罩，让笔画断断续续。

```xml
<filter id="chalk">
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="4" seed="9" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="3" result="d"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" result="grain"/>
  <feColorMatrix in="grain" type="matrix"
    values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.2 0 0 0 -0.25" result="mask"/>
  <feComposite in="d" in2="mask" operator="in"/>
</filter>
```

- 文字：`'Segoe Print','楷体',cursive`，同样过 chalk 滤镜。
- 擦痕：白色大椭圆 opacity 0.04，随意放两三个。

## 3. 蓝图（blueprint）

适合架构文档、正式技术图。style-3 也是这个方向，两者可互换。

- 背景：`#0d2b52`，叠网格：细格 20px `rgba(255,255,255,0.05)` + 粗格 100px `rgba(255,255,255,0.10)`（两层 `<pattern>`）。
- 线条：浅蓝白 `#cfe8ff` 为主、亮蓝 `#7dd3fc` 强调；细 1.5px，不加手抖。
- 文字：等宽 `Consolas,'Courier New',monospace`。
- 图框：右下角标准标题栏（图名/比例/日期三格矩形），四周边框双线。
- 尺寸标注：细实线+箭头+数字。

## 4. 钢笔淡彩（ink & wash）

适合报告封面图、概念示意图。

- 墨线层：手抖 `baseFrequency="0.015" scale="4"`，黑 `#1a1a1a`，粗 1.8px，允许断笔（部分段落故意不闭合）。
- 水彩层：同形状复制两份，底层填色晕开，上层画墨线。`bleed` 由 `feGaussianBlur stdDeviation="3"` 加位移 (2,2) 模拟颜料出界。

```xml
<path d="..." fill="#93c5fd" opacity="0.55" filter="url(#bleed)"/>
<path d="..." fill="none" stroke="#1a1a1a" stroke-width="1.8" filter="url(#wob)"/>
```

- 颜料低饱和：赭石 `#d6b789`、青灰 `#9db4c0`、暗绿 `#8fa88f`，故意盖不满轮廓。
- 纸纹：米白 `#fbf8f1` 加细噪点 opacity 0.10。

## 5. 方格纸几何（graph paper）

适合公式图、坐标图、教学场景。

- 背景：白 + 淡蓝格线 5mm（20px，`#93c5fd55`），每 5 格一根深线（100px，`#60a5fa88`）。
- 线条：蓝黑墨水 `#1e3a8a` 或铅笔灰 `#4b5563`；手抖极轻 `scale="1.5"`。
- 图形沿格线对齐，坐标轴画在格线上；关键点用实心圆点标在格点。
- 文字：手写体，公式用 `font-style="italic"` 近似。

## 6. 铜版雕刻（etching）

适合正式出版物插图、复古风海报。

- 纸底：奶油色 `#f4efe2`，无噪点。
- 线条：纯黑 `#000`，细 0.8-1px，不加手抖。
- 交叉排线是两个 pattern：

```xml
<pattern id="hatchA" width="6" height="6" patternTransform="rotate(45)"><line .../></pattern>
<pattern id="hatchB" width="6" height="6" patternTransform="rotate(135)"><line .../></pattern>
```

暗部叠 A+B 双向交叉，中间调只 A，亮部留白；用不同线距（4/6/10px）出三档灰阶。
- 装饰：图外框一圈细双线，图注用衬线体 `'Georgia',serif` 小字居中。

## 7. 极简线稿（minimal line art）

适合产品文档、官网配图。

- 背景：纯白或 Notion 奶白 `#ffffff`。
- 线条：统一 1.5px 纯黑 `#111111`，圆角端点，不加手抖、不排线、不阴影。
- 装饰：形状复制一份填高饱和色（黄 `#ffd166`、粉 `#ff8fab`、蓝 `#8ecae6` 任选一），相对轮廓错位 (-4, +4)，opacity 1。
- 留白：元素间距至少 60px，元素数量从少。
- 文字：系统无衬线 `'Inter','Segoe UI'`，灰 `#555`。

## 8. 3D 等轴测插画（isometric illustration）

适合宣传图、产品插图，介于工程图和效果图之间。

- 投影：复用 SKILL.md 风格 2 的 iso 函数（30° 等轴测）。
- 与工程剖面的区别：不标注、不剖切，靠色块分面亮暗，顶面最亮、左面中、右面暗（各面同色系差 20% 明度）。
- 轮廓：黑描边 2px（贴纸感）或无描边（柔和感），面与面之间可留 1px 白缝。
- 配色：低饱和马卡龙系，一页不超过 4 个色相。
- 阴影：地面平行四边形纯色 `#000` opacity 0.08，不模糊。

## 风格选型速查

| 场景 | 推荐风格 |
|---|---|
| 会议草图、快速沟通 | 白板马克笔 |
| 教学、公式、讲解 | 黑板粉笔 / 方格纸几何 |
| 正式技术文档、架构文档 | 蓝图 / 极简线稿 |
| 报告封面、杂志插图 | 钢笔淡彩 |
| 出版物、复古风 | 铜版雕刻 |
| 产品官网、宣传 | 极简线稿 / 3D 等轴测 |
| 工程设备图、P&ID、剖面 | SKILL.md 工程三件套（铅笔素描/剖面/效果图） |
