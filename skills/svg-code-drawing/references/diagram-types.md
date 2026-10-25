# 技术图图型库（布局规则、形状语汇、箭头语义）

## 图型与布局规则

| 图型 | 布局要点 | 骨架模板 |
|---|---|---|
| 架构图 | 分水平层（Client→Gateway→Services→Data），虚线容器分组，箭头顺数据流，viewBox 960x600（高栈 960x800） | templates/architecture.svg |
| 数据流 | 每条箭头标注数据类型，主路径 2.5px 实线，控制流虚线，按语义着色 | templates/data-flow.svg |
| 流程图 | 上下为主、宽则左右；菱形=决策、圆角矩形=进程、平行四边形=I/O；网格吸附 x120/y80px | templates/flowchart.svg |
| 时序图 | 参与者竖 lifeline（顶部标签+虚线），消息横箭头自上而下；loop/alt 用左上角标签的框；高度=80+消息数×50 | templates/sequence.svg |
| 类图 | 三格盒（类名/属性/方法）；继承=实线+空心三角，实现=虚线+空心三角，聚合=空心菱形，组合=实心菱形；父类在上 | — |
| ER 图 | 实体=标题栏矩形（主键下划线），关系=菱形（has/belongs），基数标 1/N/0..\*；识别关系实线、非识别虚线 | templates/er-diagram.svg |
| 状态机 | 圆角矩形=状态；实心圆=初态、同心圆=终态；守卫 [条件] 在箭头上，动作用 `event [guard] / action` | templates/state-machine.svg |
| 时间线/甘特 | 横轴时间、纵轴任务；圆角条按类别着色，里程碑菱形+上方标签；960x400 | templates/timeline.svg |
| 对比矩阵 | 行高 40、列宽≥120、表头 50；支持格浅绿 `#dcfce7`+✓，隔行 `#f9fafb`；最多 5 列 | templates/comparison-matrix.svg |
| 思维导图 | 中心 (480,280)，一级分支 360/N 度均布，二级偏移 30-45°；连线用三次贝塞尔曲线 | — |
| 用例图 | 火柴人在系统边界外，椭圆用例≥140x60；<<include>>/<<extend>> 虚线箭头 | templates/use-case.svg |
| 网络拓扑 | 路由圆+叉、交换机矩形+箭头格、服务器机架、防火墙砖纹、云路径；分区虚线容器标 DMZ/内网 | — |
| Agent 架构 | 输入层/推理核心/记忆层/工具层/输出层；迭代推理用环形弧箭头；记忆三类视觉分开 | — |
| 记忆架构 | 写路径与读路径分色；Working→Short→Long→External 分层；操作标 store()/retrieve()/forget() | — |

UML 14 型映射：组件/部署/包/复合结构→架构图；活动→流程图（加 fork/join 粗横条）；通信→时序图换轴；交互概览→流程+时序片段。

## 形状语汇（跨图型统一）

用户=圆+火柴体；LLM=圆角矩形+强调色；Agent/调度器=六边形或双框；短期记忆=虚线框（易失）；长期记忆=圆柱（持久）；向量库=圆柱+内部三横线；图数据库=三圆交叠；工具=齿轮状矩形；API/网关=单框六边形；队列=横向管道；文件=折角矩形；决策=菱形（仅流程图）；外部服务=虚线框；数据=平行四边形。

## 箭头语义（2 种以上必配图例）

| 流 | 色 | 线 | 虚线 |
|---|---|---|---|
| 主数据流 | 蓝 #2563eb | 2px | 无 |
| 控制/触发 | 橙 #ea580c | 1.5px | 无 |
| 记忆读 | 绿 #059669 | 1.5px | 无 |
| 记忆写 | 绿 #059669 | 1.5px | 5,3 |
| 异步/事件 | 灰 #6b7280 | 1.5px | 4,2 |
| 变换/嵌入 | 紫 #7c3aed | 1px | 无 |
| 反馈/循环 | 紫 #7c3aed | 1.5px 曲线 | 无 |

## 常用架构模式

RAG 管线：Query→Embed→VectorSearch→Retrieve→Augment→LLM→Response。
Agentic RAG：上者加 Agent 循环与 Tool use。
Agentic Search：Query→Planner→[Search/Calculator/Code]→Synthesizer→Response。
Agent 记忆类型：Sensory→Working(context)→Episodic→Semantic→Procedural。
Multi-Agent：Orchestrator→[SubA/SubB/SubC]→Aggregator→Output。
Tool Call：LLM→Tool Selector→Execution→Result Parser→LLM（循环）。
