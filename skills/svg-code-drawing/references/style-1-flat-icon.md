# Style 1: Flat Icon (Default)

参考 draw.io 默认风格与 Apple 文档插图。

## Colors

```
Background:     #ffffff
Box fill:       #ffffff
Box stroke:     #d1d5db  (gray-300)
Box radius:     8px
Text primary:   #111827  (gray-900)
Text secondary: #6b7280  (gray-500)

Semantic arrow colors (pick by flow type):
  Flow A (main):   #2563eb  (blue-600)
  Flow B (alt):    #dc2626  (red-600)
  Flow C (data):   #16a34a  (green-600)
  Flow D (async):  #9333ea  (purple-600)

Icon accent backgrounds:
  Blue tint:   #eff6ff / #dbeafe
  Red tint:    #fef2f2 / #fee2e2
  Green tint:  #f0fdf4 / #dcfce7
  Purple tint: #faf5ff / #ede9fe
  Orange tint: #fff7ed / #fed7aa
  Teal tint:   #f0fdfa / #ccfbf1
```

## Typography

```
font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC',
             'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   14px labels, 12px sub-labels, 16px titles
font-weight: 400 normal, 600 semi-bold for titles
```

## Box Shapes

标准节点、强调底色节点、数据库圆柱、终端框、用户形状：

```xml
<rect rx="8" ry="8" fill="#ffffff" stroke="#d1d5db" stroke-width="1.5"/>
<rect rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>
```

数据库用圆柱 path。终端框 rx=4、fill=#111827、stroke=#374151。用户用圆形或圆角矩形加图标。

## Arrows

```xml
<defs>
  <marker id="arrow-blue" markerWidth="10" markerHeight="7"
          refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>
  </marker>
  <marker id="arrow-red" markerWidth="10" markerHeight="7"
          refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#dc2626"/>
  </marker>
</defs>

<line stroke="#2563eb" stroke-width="1.5" marker-end="url(#arrow-blue)"/>
<path stroke="#2563eb" stroke-width="1.5" fill="none" marker-end="url(#arrow-blue)"/>
```

## Legend

使用多种箭头颜色时，左下角放图例：

```xml
<g transform="translate(20, 560)">
  <line x1="0" y1="8" x2="30" y2="8" stroke="#2563eb" stroke-width="1.5"
        marker-end="url(#arrow-blue)"/>
  <text x="36" y="12" fill="#6b7280" font-size="12">Agent flow</text>
  <line x1="0" y1="24" x2="30" y2="24" stroke="#dc2626" stroke-width="1.5"
        marker-end="url(#arrow-red)"/>
  <text x="36" y="28" fill="#6b7280" font-size="12">RAG flow</text>
</g>
```

## SVG Template

样式表只用系统字体，不用 `@import`，因为渲染器（resvg、librsvg、Chromium）都不抓外部资源。

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 600"
     width="960" height="600">
  <style>
    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }
  </style>
  <defs>
  </defs>
  <rect width="960" height="600" fill="#ffffff"/>
  <text x="480" y="40" text-anchor="middle" font-size="16" font-weight="600" fill="#111827">Diagram Title</text>
</svg>
```
