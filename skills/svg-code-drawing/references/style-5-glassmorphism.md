# Style 5: Glassmorphism

深色渐变上的磨砂玻璃卡片，适合产品站、发布会、首屏。

## Colors

```
Background gradient: #0d1117 → #161b22 → #0d1117 (diagonal)

Glass card:
  fill:           rgba(255,255,255,0.05)
  stroke:         rgba(255,255,255,0.15)
  backdrop-filter: blur(12px)  [SVG 用 feGaussianBlur]
  box-radius:     12px

Text primary:   #f0f6fc
Text secondary: #8b949e
Text gradient:  linearGradient on text fill for hero labels

Accent glows:
  Blue glow:    #58a6ff  / rgba(88,166,255,0.3)
  Purple glow:  #bc8cff  / rgba(188,140,255,0.3)
  Green glow:   #3fb950  / rgba(63,185,80,0.3)
  Orange glow:  #f78166  / rgba(247,129,102,0.3)
```

## Background

```xml
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"   stop-color="#0d1117"/>
    <stop offset="50%"  stop-color="#161b22"/>
    <stop offset="100%" stop-color="#0d1117"/>
  </linearGradient>
  <radialGradient id="glow-blue" cx="30%" cy="40%" r="40%">
    <stop offset="0%" stop-color="rgba(88,166,255,0.15)"/>
    <stop offset="100%" stop-color="rgba(88,166,255,0)"/>
  </radialGradient>
  <radialGradient id="glow-purple" cx="70%" cy="60%" r="35%">
    <stop offset="0%" stop-color="rgba(188,140,255,0.12)"/>
    <stop offset="100%" stop-color="rgba(188,140,255,0)"/>
  </radialGradient>
</defs>
<rect width="960" height="600" fill="url(#bg)"/>
<rect width="960" height="600" fill="url(#glow-blue)"/>
<rect width="960" height="600" fill="url(#glow-purple)"/>
```

## Glass Card Effect

SVG 没有真正的 backdrop-filter，用多层矩形模拟：内阴影、玻璃主体、顶部高光线。

```xml
<defs>
  <filter id="glass-blur">
    <feGaussianBlur in="SourceGraphic" stdDeviation="0.5"/>
  </filter>
</defs>

<rect rx="12" fill="rgba(255,255,255,0.03)" stroke="none"/>
<rect rx="12" fill="rgba(255,255,255,0.06)"
      stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
<line stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
```

## Typography

```
font-family: 'Inter', -apple-system, 'SF Pro Display', 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   14px labels, 12px sublabels, 20px hero title
font-weight: 400 normal, 600 semi-bold, 700 bold titles
```

## Gradient Text

```xml
<defs>
  <linearGradient id="text-grad-blue" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#58a6ff"/>
    <stop offset="100%" stop-color="#bc8cff"/>
  </linearGradient>
</defs>
<text fill="url(#text-grad-blue)" font-weight="700" font-size="20">
  AI Pipeline
</text>
```

## Arrows

```xml
<defs>
  <marker id="arrow-blue" markerWidth="8" markerHeight="6"
          refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#58a6ff"/>
  </marker>
</defs>
<path stroke="#58a6ff" stroke-width="1.5" fill="none"
      opacity="0.8" marker-end="url(#arrow-blue)"/>
```

## SVG Template

字体只用系统栈，不用 `@import`，避免离线渲染失效。

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 600"
     width="960" height="600">
  <style>
    text { font-family: 'Inter', -apple-system, 'SF Pro Display', 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; fill: #f0f6fc; }
  </style>
  <defs>
  </defs>
</svg>
```
