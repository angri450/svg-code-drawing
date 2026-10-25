# SVG 的进阶用法

静态绘图是本 skill 的主业。这份参考收录动效、交互、数据三个方向的能力，用户提出相关诉求时加载。

## 1. 动画：SMIL

SMIL（`<animate>`/`<animateTransform>`/`<animateMotion>`）是 SVG 原生动画，声明式、无需 JS、可沿 path 运动。CSS 只有 offset-path 近似，做不了任意路径运动。

```xml
<circle r="8" fill="#2563eb">
  <animateMotion dur="4s" repeatCount="indefinite" path="M0,0 C50,-80 150,80 200,0"/>
</circle>
```

技术图场景：数据流动画（沿管线跑的小圆点）、流程走向演示、加载态。
选型：简单属性、颜色、变换用 CSS keyframes；沿路径运动或多属性同步用 SMIL；复杂序列编排用 SMIL begin 偏移拼接，不引库。

边界：SVG 作为 `<img>` 或背景图引用时，SMIL 与 CSS 动画都不播，必须内联进 HTML。

## 2. 交互：内联才有 DOM

同一份 SVG 的三种引入方式：

- `<img src>` 或 CSS background：纯图片，无交互、无动画、无样式覆盖。
- `<object>` 或 `<iframe>`：独立文档，可动画，跨文档脚本受限。
- 内联进 HTML：完整 DOM，CSS/JS/事件全部可用。

技术图场景：可点击的架构图（点组件显示详情）、hover 高亮依赖链、可折叠的层级图。
CSS 可做轻交互：`.node:hover { fill: #dbeafe; }` 加 `transition`，无需 JS。
`<title>` 元素给节点做原生 tooltip。

## 3. 图表：d3 生态的底层

d3、Highcharts、ECharts 的 SVG 渲染模式都输出 SVG。SVG 图表可被屏幕阅读器读取、可用 CSS 定制、可进 DOM 联动。
小数据量图表（少于 50 点）直接手写 SVG 柱状图或折线图，不引库。

## 4. 地图：区域路径即数据通道

每个行政区一条 path、id 对接数据，按数值填色（choropleth），hover 显示 tooltip。路径数据从公开 GeoJSON 转（d3-geo 或在线转换器）。

## 5. 图标系统：sprite + currentColor

一份 SVG 定义多个 `<symbol id="ico-x">`，用 `<use href="#ico-x">` 引用。单 HTTP 请求，`fill="currentColor"` 让图标跟随文字颜色，CSS 可控。相比 icon font，语义、多色、无障碍都更好。

## 6. 滤镜的边界用法

- `feImage` + `feBlend`：纹理叠加（纸张、布料做旧）。
- `feTile`：小 pattern 铺大面。
- `feMorphology`（erode/dilate）：蚀刻边缘、光晕收缩。
- CSS `filter: url(#id)`：HTML 元素也能过 SVG 滤镜。
- `mix-blend-mode`：模式叠底、正片叠水彩层。

## 7. 其他

- `foreignObject`：SVG 里嵌完整 HTML（MathML 公式、异形排版）。
- viewBox 动画：改变 viewBox 数值实现镜头推拉摇移。
- 打印：SVG 是矢量，放大不糊，海报、手册插图可直接交付 SVG。
- SEO：内联 SVG 的文字是真文字，可被搜索和复制。
- 文件大小：简单图形通常小于 2KB 且 gzip 友好；复杂插画可能比 PNG 大。
- 不适用场景：照片、照片级复杂渐变、超过 5k 点的散点图（DOM 会卡），交给位图或 Canvas。
