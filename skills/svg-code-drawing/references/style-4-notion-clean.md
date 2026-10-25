# Style 4: Notion Clean

极简文档风，适合嵌入 Notion、Confluence、GitHub wiki。

## Colors

```
Background:     #ffffff
Box fill:       #f9fafb  (gray-50) or #ffffff
Box stroke:     #e5e7eb  (gray-200)
Box radius:     4px

Text primary:   #111827  (gray-900)
Text secondary: #374151  (gray-700)
Text muted:     #9ca3af  (gray-400)
Text label:     #6b7280  (gray-500), uppercase, 11px

Accent:
  Blue:   #3b82f6 (arrows only)
  Gray:   #d1d5db (dividers)
```

## Design Principles

- 不用装饰图标，只用矩形、圆、菱形等几何形状。
- 留白充足，元素间距 24px 以上。
- 所有连线用单一蓝色 #3b82f6。
- 分区标题与节点类型标签用大写。
- 不用投影。

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
             'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei',
             'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   14px labels, 11px uppercase type labels, 18px title
font-weight: 400 normal, 500 medium for node labels
```

## Box Styles

```xml
<rect rx="4" fill="#f9fafb" stroke="#e5e7eb" stroke-width="1"/>
<text fill="#111827" font-size="14" font-weight="500">Label</text>

<text fill="#9ca3af" font-size="11"
      font-weight="500" letter-spacing="0.08em">DATABASE</text>

<rect rx="4" fill="none" stroke="#e5e7eb" stroke-width="1"
      stroke-dasharray="4,3"/>
```

## Arrows

```xml
<defs>
  <marker id="arrow-blue" markerWidth="8" markerHeight="6"
          refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#3b82f6"/>
  </marker>
</defs>
<line stroke="#3b82f6" stroke-width="1.5"
      marker-end="url(#arrow-blue)"/>
<line stroke="#d1d5db" stroke-width="1"
      stroke-dasharray="4,3"/>
```

## SVG Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 560"
     width="960" height="560">
  <style>
    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }
  </style>
  <defs>
  </defs>
  <rect width="960" height="560" fill="#ffffff"/>
</svg>
```

## Sizing Guide

- 节点框最小 120×40px，推荐 160×48px。
- 标题在左上角，18px，gray-900，距边 32px。
- 水平间距至少 80px，垂直间距至少 60px。
