# Style 6: Claude Official

参考 Anthropic Claude 博客的技术插图：暖色、圆角、低饱和。

## Colors

```
Background:     #f8f6f3  (warm cream)
Box fill:
  Blue tint:    #a8c5e6  (alert/input nodes)
  Green tint:   #9dd4c7  (agent nodes)
  Beige:        #f4e4c1  (infrastructure/bus)
  Gray tint:    #e8e6e3  (storage/state)
Box stroke:     #4a4a4a
Box radius:     12px
Text primary:   #1a1a1a
Text secondary: #6a6a6a
Text labels:    #5a5a5a

Semantic node colors:
  Input/Source:    #a8c5e6
  Agent/Process:   #9dd4c7
  Infrastructure:  #f4e4c1
  Storage/State:   #e8e6e3

Arrow color:     #5a5a5a
```

## Typography

```
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue',
             Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif
font-size:   16px node labels, 14px descriptions, 13px arrow labels
font-weight: 600 for node labels, 400 for descriptions, 700 for titles
```

## Box Shapes

```xml
<rect rx="12" ry="12" fill="#9dd4c7" stroke="#4a4a4a" stroke-width="2.5"/>
<rect rx="12" ry="12" fill="#a8c5e6" stroke="#4a4a4a" stroke-width="2.5"/>
<rect rx="12" ry="12" fill="#f4e4c1" stroke="#4a4a4a" stroke-width="2.5"/>
<rect rx="12" ry="12" fill="#e8e6e3" stroke="#4a4a4a" stroke-width="2.5"/>
```

## Arrows

```xml
<defs>
  <marker id="arrow-claude" markerWidth="8" markerHeight="8"
          refX="7" refY="4" orient="auto">
    <polygon points="0 0, 8 4, 0 8" fill="#5a5a5a"/>
  </marker>
</defs>

<line stroke="#5a5a5a" stroke-width="2" marker-end="url(#arrow-claude)"/>
<line stroke="#5a5a5a" stroke-width="2"/>
```

## Arrow Semantics

| Flow Type | Color | Stroke | Dash | Usage |
|-----------|-------|--------|------|-------|
| Primary data flow | #5a5a5a | 2px solid | none | Main request/response path |
| Memory write | #5a5a5a | 2px | `5,3` | Write/store operations |
| Memory read | #5a5a5a | 2px solid | none | Retrieval from store |
| Control/trigger | #5a5a5a | 1.5px | `3,2` | Event triggers |

```xml
<line stroke="#5a5a5a" stroke-width="2" marker-end="url(#arrow-claude)"/>
<line stroke="#5a5a5a" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrow-claude)"/>
```

## Arrow Labels

标签写具体技术动作，放在箭头中点：

```xml
<text x="..." y="..." fill="#5a5a5a" font-size="13" text-anchor="middle">
  store(embedding)
</text>
```

可用标签示例：`query(text)`、`retrieve(top_k=5)`、`embed(768d)`、`POST /api/search`。不用 "Process"、"Send"、"Get" 这类泛词。

## Node Content Guidelines

节点内容写技术细节：

- "Vector Store" 下面写 "768-dim embeddings" 与 "Cosine similarity"。
- "LLM" 下面写 "GPT-4"、"8K context"、"Temperature: 0.7"。
- "Memory" 下面写 "Redis Cache"、"TTL: 5min"、"Max: 4K tokens"。

不用 "Process data"、"Store information"、"Handle requests" 这类泛描述。

每个节点 2-3 行：组件名（16px 粗体）、技术细节（14px）、关键参数（14px，可选）。

## Layer Labels

多层架构在左侧加层标签：

```xml
<text x="30" y="130" fill="#6a6a6a" font-size="14" font-weight="600">Input</text>
<text x="30" y="290" fill="#6a6a6a" font-size="14" font-weight="600">Processing</text>
<text x="30" y="490" fill="#6a6a6a" font-size="14" font-weight="600">Storage</text>
```

每个标签对齐对应层的垂直中心。

## Legend Requirement

使用两种以上箭头样式或颜色时，右下角放图例：

```xml
<rect x="720" y="520" width="220" height="80" rx="8" ry="8"
      fill="#ffffff" stroke="#4a4a4a" stroke-width="1.5"/>
<text x="735" y="540" fill="#1a1a1a" font-size="13" font-weight="600">Legend</text>

<line x1="735" y1="555" x2="765" y2="555" stroke="#5a5a5a" stroke-width="2"/>
<text x="775" y="560" fill="#6a6a6a" font-size="12">Read operation</text>

<line x1="735" y1="570" x2="765" y2="570" stroke="#5a5a5a" stroke-width="2" stroke-dasharray="5,3"/>
<text x="775" y="575" fill="#6a6a6a" font-size="12">Write operation</text>
```

图例距边 20px。

## Layout Principles

- 节点边缘间距至少 80px。
- 同层节点水平对齐。
- 主流程自上而下。
- 构图保持左右平衡。
- 连线正交路由：先竖后横，或先横后竖。

## SVG Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 600"
     width="960" height="600">
  <style>
    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                   'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif;
    }
  </style>
  <defs>
    <marker id="arrow-claude" markerWidth="8" markerHeight="8"
            refX="7" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#5a5a5a"/>
    </marker>
    <filter id="shadow-soft">
      <feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#00000008"/>
    </filter>
  </defs>

  <rect width="960" height="600" fill="#f8f6f3"/>

  <text x="480" y="40" text-anchor="middle" fill="#1a1a1a"
        font-size="20" font-weight="700">Diagram Title</text>

  <rect x="100" y="100" width="180" height="80" rx="12" ry="12"
        fill="#9dd4c7" stroke="#4a4a4a" stroke-width="2.5"
        filter="url(#shadow-soft)"/>
  <text x="190" y="145" text-anchor="middle" fill="#1a1a1a"
        font-size="16" font-weight="600">Agent name</text>

  <line x1="190" y1="180" x2="190" y2="240"
        stroke="#5a5a5a" stroke-width="2" marker-end="url(#arrow-claude)"/>
  <text x="210" y="215" fill="#5a5a5a" font-size="13">Publish</text>
</svg>
```

## Design Philosophy

特点：奶油底色与柔和色块；高对比文字与充足留白；统一线宽与对齐；圆角与低饱和配色。

避免：生硬阴影或渐变、高饱和色、小于 2px 的线宽、拥挤布局。
