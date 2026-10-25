# 工程示意图三件套配方

基准实现：`scripts/generate_three_styles.py`，同一储罐三种风格一页出齐，`uv run python` 直接运行。

## E1 铅笔素描

三层叠加：

1. 手抖：`feTurbulence`（fractalNoise, baseFrequency≈0.018）接 `feDisplacementMap`（scale≈4.5），套在所有图形的外层 `<g filter>`。scale 调手感：3 工整，5 随意，8 以上接近心电图。
2. 纸纹：`feTurbulence`（baseFrequency≈0.9）+ `feColorMatrix saturate=0`，整页铺，opacity≈0.13。
3. 手写体：标注 `font-family:'Segoe Print','楷体',cursive`，标题带 1 度微旋转。

工程语汇：设备单线主体；仪表泡圆圈+位号；信号线 `stroke-dasharray="7 6"`；流向 V 形箭头；罐体阴影用右下侧一排 45 度短排线（手放 12 根，不用 clipPath 循环生成，容易越界）。
文字单独成组，不套手抖滤镜，否则中文抖到不可读。

## E2 三维剖面（等轴测）

投影与开窗用初等数学：

```
等轴测投影:  sx = ox + (x - z) * cos30°    sy = oy + (x + z) * sin30° - y
圆柱表面点:  P(t°, y) = iso(r·cos t, y, r·sin t)
屏幕上的圆柱: 顶/底是椭圆，rx = r·√2·cos30° ≈ 1.225r，ry = r·√2·sin30° ≈ 0.707r
轮廓切点:    t=135°（左）与 t=-45°（右），投影后 y 偏移为 0，侧壁线是纯竖直线
```

局部剖视开窗：取正面角度区间（如 t∈[12°,78°]，正面中心 t=45°），窗口上下缘两个 y 值。

- 内腔：内半径 `r_in = r-8` 沿窗口上下缘采样闭合成多边形。
- 液相：同法，上缘降到液位 y。
- 壁厚剖面线：外轮廓（r）与内轮廓（r_in）两个同构多边形拼进一个 `path`，`fill-rule="evenodd"`，填 45 度斜线 `<pattern>`。
- 画序：底前弧 → 两侧轮廓竖线 → 顶椭圆（不透明填充盖住后壁）→ 内腔 → 液相 → 液面线 → 剖面框。

标注引出线加 `text-anchor="end"`，关键项为壁厚、液位、剖面图例。

## E3 三维效果图（渐变着色）

- 背景竖向浅渐变；地面椭圆阴影 `opacity≈0.3` + `feGaussianBlur stdDeviation≈7`。
- 罐身横向 linearGradient 金属色标：`#6e777d → #b9c2c9 → #f2f6f8 → #ffffff → #dde4e9 → #a8b2b9 → #7c858c → #5c646a`（暗-亮-高光-中-暗，高光偏左 1/3）。
- 顶部椭圆径向渐变；人孔法兰两层椭圆+四螺栓点。
- 竖向高光条：窄圆角矩形白 fill + 高斯模糊，叠在罐身左 1/3。
