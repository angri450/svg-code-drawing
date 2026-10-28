# Style 7: OpenAI Official

参考 OpenAI 文档与研究插图的极简风格：白底、细边、精确。

## Color Palette

```
Background:     #ffffff
Primary text:   #0d0d0d
Secondary text: #6e6e80
Border:         #e5e5e5

Accent colors:
Green accent:   #10a37f  (OpenAI brand green)
Blue accent:    #1d4ed8  (links, actions)
Orange accent:  #f97316  (highlights, warnings)
Gray accent:    #71717a  (secondary elements)
```

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Times New Roman', Roboto, 'Times New Roman', 'FangSong SC', sans-serif
font-size:   16px node labels, 13px descriptions, 12px arrow labels
font-weight: 600 for titles, 500 for labels, 400 for descriptions
letter-spacing: -0.01em
```

只用系统字体栈。

## Node Boxes

白底、浅灰边、无阴影。可用 4px 彩色左边条做强调。

```xml
<rect x="100" y="100" width="180" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>

<rect x="100" y="100" width="180" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<rect x="100" y="100" width="4" height="80" rx="2" ry="2"
      fill="#10a37f"/>
```

技术要点：白底浅灰边；可选 4px 左侧色条；`rx="8"`；`stroke-width: 1.5`；不用渐变、阴影、装饰元素。

## Arrows

```xml
<defs>
  <marker id="arrow-oai" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#71717a"/>
  </marker>
  <marker id="arrow-oai-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#10a37f"/>
  </marker>
</defs>

<line x1="280" y1="140" x2="400" y2="140"
      stroke="#71717a" stroke-width="1.5" marker-end="url(#arrow-oai)"/>

<line x1="280" y1="140" x2="400" y2="140"
      stroke="#10a37f" stroke-width="1.5" marker-end="url(#arrow-oai-green)"/>
```

箭头规范：优先直线与正交路由；线宽 1.5；实心三角箭头；默认灰、主流程绿；可选/异步流用 `stroke-dasharray="4,3"`。

## Arrow Labels

```xml
<text x="340" y="133" text-anchor="middle" fill="#6e6e80" font-size="12">
  label
</text>
```

标签 12px、灰色 `#6e6e80`，不加背景矩形，放在箭头中点，用简短技术用语。

## Database Shapes

```xml
<ellipse cx="200" cy="100" rx="50" ry="12" fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<path d="M 150,100 L 150,140 Q 200,155 250,140 L 250,100"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<ellipse cx="200" cy="140" rx="50" ry="12" fill="none" stroke="#e5e5e5" stroke-width="1.5"/>
```

## Grouping Containers

```xml
<rect x="80" y="80" width="400" height="200" rx="8" ry="8"
      fill="none" stroke="#e5e5e5" stroke-width="1" stroke-dasharray="4,3"/>
<text x="90" y="97" fill="#6e6e80" font-size="12" font-weight="500">
  Group Label
</text>
```

## Node Content

```xml
<rect x="100" y="100" width="180" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
<text x="190" y="130" text-anchor="middle" fill="#0d0d0d"
      font-size="16" font-weight="600">
  Component Name
</text>
<text x="190" y="150" text-anchor="middle" fill="#6e6e80"
      font-size="13">
  Brief description
</text>
```

每个盒子 1-2 行；主标签 16px、600 权重、近黑色；描述 13px、400 权重、灰色；文字居中。

## Layout Principles

坐标吸附 8px 网格；水平间距 100px；垂直间距 120px；四周留白 40px 以上；不用装饰元素。
颜色只用于语义区分（品牌绿给主流程）。白盒白底，靠边框与标签区分。避免阴影、渐变、图案、图标；优先直线、正交路由、细线。

## SVG Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 600" width="960" height="600">
  <style>
    text { font-family: -apple-system, BlinkMacSystemFont, 'Times New Roman', Roboto, 'Times New Roman', 'FangSong SC', sans-serif; }
  </style>
  <defs>
    <marker id="arrow-oai" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#71717a"/>
    </marker>
    <marker id="arrow-oai-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#10a37f"/>
    </marker>
  </defs>

  <rect width="960" height="600" fill="#ffffff"/>

  <text x="480" y="30" text-anchor="middle" fill="#0d0d0d"
        font-size="20" font-weight="600">Diagram Title</text>

  <rect x="100" y="70" width="180" height="80" rx="8" ry="8"
        fill="#ffffff" stroke="#e5e5e5" stroke-width="1.5"/>
  <text x="190" y="100" text-anchor="middle" fill="#0d0d0d"
        font-size="16" font-weight="600">Component</text>
  <text x="190" y="120" text-anchor="middle" fill="#6e6e80"
        font-size="13">Description</text>

  <line x1="280" y1="110" x2="400" y2="110"
        stroke="#71717a" stroke-width="1.5" marker-end="url(#arrow-oai)"/>
  <text x="340" y="103" text-anchor="middle" fill="#6e6e80" font-size="12">label</text>
</svg>
```

## Design Philosophy

极简：白底白盒，只保留必要元素。精确：细线、8px 圆角、网格对齐。内容优先，无视觉噪音。品牌绿 `#10a37f` 只用于主流程。
避免阴影与渐变、彩色填充、超过 2px 的粗边、图标/图案/纹理、自定义字体。
