<!-- ppt-master-schema: design-spec/v1 -->
# chemtrack_design - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | chemtrack_design |
| Canvas Format | PPT 16:9 (1280×720) |
| Page Count | 12 |
| Target Audience | 软件工程课程教师与同学、实验中心管理人员 |
| Communication Intent | 用 ChemTrack 的真实实现说明校园实验室危化品管理系统如何从问题定义走到可落地设计，并完成课程要求的可行性、需求规格和三种建模方法汇报。 |
| Desired Audience Outcome | 听众能够在 10 分钟内理解系统为什么值得做、系统做什么、如何保证安全，以及三张模型图如何支撑后续开发。 |
| Core Message / Ask / Action | ChemTrack 把采购、库存、领用、使用、处置和审计连成一条可追溯责任链；请按“需求—模型—实现—演示”顺序评审本方案。 |
| Delivery Context | 2026-09-16 起课堂分组汇报，投影观看，约 10 分钟。 |
| Artifact Afterlife | 课堂汇报 PPT、课程设计文档骨架、后续答辩和系统演示提纲。 |
| Reading Mode | balanced |
| Content Strategy | 结论先行、证据分层：先说明风险与价值，再给出需求与可行性，随后用 DFD / ER / 状态图解释设计，最后回到演示闭环与分工。 |
| Design Style | 技术审查式自由设计：深色实验台背景、细线网格、状态标签、流程节点和克制的风险色。 |
| AI Image Acquisition Path | not applicable; no external imagery required |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | disabled — user requested PPT deliverable without narration notes |
| Custom Animations | disabled — static classroom deck |
| Narration Audio | disabled — no audio output requested |
| Created Date | 2026-09-12 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280×720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px outer margin; 48 px footer safe area |
| Content Area | x=64..1216, y=56..664 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Visual style**: custom
- **Theme**: 实验台上的安全操作系统：像实验室控制台一样严谨，用状态、责任链和证据块组织信息。
- **Tone**: 冷静、可信、可审查；风险色只用于需要行动的节点。
- **Mode Behavior**: 先抛出系统结论与问题代价，再拆解需求与可行性，随后用三种模型解释设计，最后用一条真实业务链收束。
- **Visual Style Behavior**: 深墨绿大底配近白文字，细网格与竖向编号线贯穿全 deck；内容以无阴影的几何面板、圆角状态芯片、流程连接线和少量琥珀风险标记构成，保持高对比和投影可读性。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #0E2422 | 实验台深色底，承载全局结构 |
| Secondary background | #163C38 | 内容面板与分区带 |
| Primary | #BFE7D8 | 标题、主流程、正向状态 |
| Accent | #57C7B0 | 关键数字、连接线、选中态 |
| Secondary accent | #F2B866 | 风险、预警、待处理状态 |
| Body text | #F5F7F4 | 正文与图中标签 |
| Secondary text | #A8C1BB | 说明、来源、次级信息 |
| Divider | #2A5650 | 网格、边界、分隔线 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 紧凑、可信、适合投影 | Microsoft YaHei | Aptos Display | Arial |
| Body | 中性、清晰、适合表格和图形 | Microsoft YaHei | Aptos | Arial |
| Data | 等宽、便于状态与 API 识别 | Cascadia Mono | Cascadia Mono | Consolas |

- **Title stack**: Microsoft YaHei, Aptos Display, Arial
- **Body stack**: Microsoft YaHei, Aptos, Arial
- **Data stack**: Cascadia Mono, Consolas, monospace

### Font Size Hierarchy

| Purpose | Size |
| --- | --- |
| Body | 22 |
| Small heading | 17 |
| Page title | 34 |
| Subtitle | 20 |
| Annotation | 14 |
| Footnote | 12 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 左上标题先给结论，中央给结构或模型，右侧 / 底部给证据与行动提示。
- **Composition tendency**: 大面积深色字段 + 一条固定编号轨道；图形页使用 2–3 个主区块，避免卡片堆叠。
- **Cross-page continuity**: 每页保留页码、短眉题和一条薄青色基线；模型页复用“节点—连接—状态芯片”语法，数据页复用“指标—解释—动作”语法。
- **Spacing posture**: 中等留白，图形页偏密，结论页偏呼吸；页边距、圆角和连接线粗细固定。
- **Spacing anchors**: page margin 64 px; block gap 24 px; column gutter 32 px; corner radius 10 px; body leading 30 px.

## VI. Icon Usage Specification

- **Primary bundled library**: none
- **Brand-logo library**: omit

| Icon Path | Suitable Scenarios |
| --- | --- |
| none | 使用可编辑的圆点、线段、编号和状态芯片替代图标，确保课堂投影清晰。 |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| 03 | table | feasibility-matrix | 经济、技术、操作、社会 / 法律四维可行性矩阵 |
| 04 | table | requirement-map | 功能需求按生命周期分层 |
| 05 | table | nfr-contract | 性能、可靠性、错误处理、接口和约束 |
| 07 | diagram | dfd-context-level1 | 顶层数据流与 1 层处理分解 |
| 08 | diagram | er-core | 核心实体、基数和审计链 |
| 09 | diagram | lifecycle-state | 主状态链与异常分支 |
| 10 | diagram | demo-flow | 从采购到处置的课堂演示路径 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## IX. Content Outline

### Part 1: 价值与可行性

#### Slide 01 - ChemTrack：把危化品管理变成一条可追溯责任链

- **Audience move**: 从“这是一个课程作业”转为“这是一个能把安全责任闭环化的系统方案”。
- **Relationships**: 标题、责任链短语、项目元信息形成由结论到身份的顺序。
- **Composition**: 大标题占左侧三分之二；右侧用六段连续节点表达采购→库存→领用→使用→处置→审计。
- **Title**: ChemTrack：把危化品管理变成一条可追溯责任链
- **Core message**: 这不是单点库存页面，而是覆盖危化品全生命周期的校园实验室管理系统。
- **Content**: 校园实验室危化品全生命周期管理系统；软件工程课程设计汇报；2026-09-16；状态：MVP 已可运行。

#### Slide 02 - 先解决责任链断裂，再谈功能堆叠

- **Audience move**: 从“人工台账和分散沟通”转为“明确的系统问题定义与成功标准”。
- **Relationships**: 现状痛点与系统目标一一对应，目标最终汇聚到可追溯责任链。
- **Composition**: 左侧三条断裂链路，右侧三条对应目标，中间用一条竖向风险线分隔。
- **Title**: 先解决责任链断裂，再谈功能堆叠
- **Core message**: 危化品风险来自跨角色、跨状态的信息断裂，系统价值在于把每次动作留下证据。
- **Content**: 现状：库存、领用、归还、危废和异常分散；风险：过期、库存不足、越权、责任追踪困难；目标：一套台账、分级审批、事务库存、异常闭环、不可删除审计。

### Part 2: 可行性与需求规格

#### Slide 03 - 四维可行性：MVP 先落地，再扩展治理能力

- **Audience move**: 从“想做”转为“经济、技术、操作、社会 / 法律都有落点”。
- **Relationships**: 四个可行性维度共同支撑“现在可做、后续可扩展”的结论。
- **Composition**: 2×2 四象限矩阵，每格一个结论句与两条证据，底部给出总体判断。
- **Title**: 四维可行性：MVP 先落地，再扩展治理能力
- **Core message**: 复用校园已有技术与基础设施，先用低成本 MVP 建立闭环，后续再补齐认证、通知和移动端。
- **Content**: 经济：复用 Spring Boot、Vue、MySQL 与校园服务器，成本集中在部署、备份、培训；技术：成熟技术栈支持事务、RBAC、预警扫描与审计；操作：角色边界清晰，演示数据模式降低培训门槛；社会 / 法律：对齐危化品台账、危废转运、最小权限、留痕和个人信息保护。

#### Slide 04 - 功能需求：八个模块覆盖一条完整生命周期

- **Audience move**: 从“系统愿景”转为“每个角色在每个节点具体做什么”。
- **Relationships**: 八个功能模块按采购→使用→治理的生命周期顺序排列，并由审计横向贯穿。
- **Composition**: 横向生命周期带 + 下方角色责任条；用青色表示主链，琥珀色表示风险治理。
- **Title**: 功能需求：八个模块覆盖一条完整生命周期
- **Core message**: 功能不是并列菜单，而是围绕批次状态和责任主体组织的一条业务链。
- **Content**: P1 用户与角色；P2 档案与批次库存；P3 采购、验收、入库；P4 领用申请与分级审批；P5 出库、使用、归还；P6 库存、有效期、异常预警；P7 废弃物处置；P8 审计与统计报表。关键规则：高风险试剂必须教师审批 + 管理员复核。

#### Slide 05 - 非功能需求：安全性优先于“看起来能用”

- **Audience move**: 从“做哪些功能”转为“系统怎样才算可靠”。
- **Relationships**: 性能、可靠性、错误处理、接口、约束和逆向需求共同定义验收边界。
- **Composition**: 左侧指标条，右侧五行合同式需求；底部突出三条不可违反的逆向约束。
- **Title**: 非功能需求：安全性优先于“看起来能用”
- **Core message**: 对危化品系统，库存一致性、权限边界和可恢复性比单纯页面数量更关键。
- **Content**: 性能：常用查询 ≤2 秒，审批 / 出库 ≤3 秒；可靠性：事务一致、外键约束、审计不可删除、每日备份；错误处理：参数校验、库存不足拦截、重复审批冲突、非法状态迁移提示；接口：Vue 浏览器、REST API、MySQL、校园统一认证预留；逆向约束：库存不得小于 0、过期批次不得正常领用、普通用户不得改库存 / 审计。

### Part 3: 体系结构与三种建模

#### Slide 06 - 体系结构：角色、服务与数据存储各司其职

- **Audience move**: 从“需求清单”转为“需求如何映射到实现结构”。
- **Relationships**: 角色通过 Vue 前端进入 Spring Boot API，服务层以 JDBC 事务访问 MySQL，审计和预警横向回流。
- **Composition**: 三层架构纵向堆叠，左右放角色入口和横向治理能力；连接线强调数据边界。
- **Title**: 体系结构：角色、服务与数据存储各司其职
- **Core message**: 前端负责协作体验，后端负责规则与事务，数据库负责约束与留痕。
- **Content**: 角色入口：学生、教师、管理员、安全负责人；前端：Vue 3 + Vite；服务：Spring Boot 3.4 + Java 17 + JDBC；数据：MySQL 8，核心表 users / chemicals / requests / approval_records / usage_records / disposals / alerts / audit_logs；治理横切：权限、预警、审计、报表。

#### Slide 07 - 数据流图 DFD：从外部角色到 8 个业务处理

- **Audience move**: 从“模块名称”转为“输入、处理、输出和数据存储的流动关系”。
- **Relationships**: 外部实体→系统处理→数据存储→通知 / 报表，主链按 P1–P8 顺序展开。
- **Composition**: 上半部上下文图，下半部 1 层分解；实体用描边框，处理用青色节点，数据存储用深色胶囊。
- **Title**: 数据流图 DFD：从外部角色到 8 个业务处理
- **Core message**: 每个关键动作都有来源、处理责任和落库去向，系统不会只停留在“页面按钮”。
- **Content**: 顶层外部实体：学生、指导教师、实验室管理员、学院安全负责人、校园统一认证；主要数据流：领用申请、审批结果、入库信息、库存查询、异常上报、预警通知、统计报表；1 层处理：P1 用户与角色，P2 档案库存，P3 采购入库，P4 领用审批，P5 出库使用归还，P6 风险预警，P7 废弃处置，P8 审计报表；数据存储：D1 用户库、D2 档案库、D3 批次库存库、D4 领用记录库、D5 审批记录库、D6 审计日志库。
- **Visualization**: dfd-context-level1
- **Native-ready**: dfd-context-level1=no

#### Slide 08 - ER 图：围绕 Chemical 与 Request 建立可追溯关系

- **Audience move**: 从“数据在流动”转为“数据如何被稳定建模、关联和约束”。
- **Relationships**: Chemical 连接 Batch / Request / Usage / Alert / Disposal；Request 连接 ApprovalRecord 与 UsageRecord；User 连接 Request 与 AuditLog。
- **Composition**: 中心实体 Chemical / Request，左右展开责任与治理实体，连线上标 1:N / 1:1 / 0..N。
- **Title**: ER 图：围绕 Chemical 与 Request 建立可追溯关系
- **Core message**: 业务闭环的关键不是表多，而是每个批次、每次申请、每次审批和每次审计都能互相追溯。
- **Content**: 核心实体：User、Role、Laboratory、Chemical、Batch、Location、Request、Approval、Usage、Disposal、Alert、AuditLog；关键基数：User 1:N Request；Chemical 1:N Request / Usage / Alert / Disposal；Request 1:N ApprovalRecord；Request 1:1 UsageRecord；UsageRecord 1:0..N Disposal；User 1:N AuditLog；约束：batch_no 唯一、quantity ≥ 0、外键完整。
- **Visualization**: er-core
- **Native-ready**: er-core=no

#### Slide 09 - 状态转换图：主链清晰，异常可回退、可冻结

- **Audience move**: 从“静态数据结构”转为“状态如何在事件驱动下演进”。
- **Relationships**: 主生命周期按时间顺序推进；过期、库存不足、泄漏、驳回和归还异常作为分支状态回到治理节点。
- **Composition**: 中央一条高亮状态带，底部以琥珀色分支挂接异常状态与触发事件。
- **Title**: 状态转换图：主链清晰，异常可回退、可冻结
- **Core message**: 状态机把“谁能做什么”变成可验证的迁移规则，避免高风险操作跳步。
- **Content**: 主链：待采购 → 采购中 → 待验收 → 已入库 → 可领用 → 申请待审批 → 教师已审批 → 管理员已复核 → 已发放 → 使用中 → 已归还 → 待处置 → 已处置；异常：已过期、冻结、库存不足、审批驳回、归还数量不一致、泄漏上报、存储异常；触发：到货、验收通过、审批、发放、实验开始、归还登记、处置完成、有效期到期、发现泄漏。
- **Visualization**: lifecycle-state
- **Native-ready**: lifecycle-state=no

### Part 4: 演示闭环与落地

#### Slide 10 - 一次演示跑通全链路：从采购到处置

- **Audience move**: 从“模型看起来合理”转为“系统已经能按闭环演示”。
- **Relationships**: 采购、领用、审批、出库、归还、预警、处置、审计按真实课堂操作顺序串联。
- **Composition**: 贯穿全页的 8 步横向时间线；每步只保留动作、责任人和产生的记录。
- **Title**: 一次演示跑通全链路：从采购到处置
- **Core message**: MVP 的完成度用一条可操作、可审计的责任链证明，而不是用功能数量证明。
- **Content**: ①管理员创建采购申请；②验收后生成批次档案；③张同学提交浓硫酸领用；④王老师审批实验方案；⑤高风险申请由管理员复核；⑥办理发放并扣减库存；⑦登记实际使用量与归还量；⑧扫描库存 / 有效期预警并登记危废处置；每一步写入 audit_logs。
- **Visualization**: demo-flow
- **Native-ready**: demo-flow=no

#### Slide 11 - 风险治理与下一阶段：把“可运行”变成“可运营”

- **Audience move**: 从“课程作业交付”转为“可持续运营和扩展的产品路线”。
- **Relationships**: 风险扫描 → 异常处理 → 审计留痕 → 报表复盘，下一阶段能力从治理闭环向身份与通知扩展。
- **Composition**: 左侧闭环圆环，右侧三列 roadmap：现在 / 下一步 / 后续。
- **Title**: 风险治理与下一阶段：把“可运行”变成“可运营”
- **Core message**: 当前 MVP 已覆盖关键闭环，下一步优先补身份、权限、通知和移动采集，而不是继续堆孤立页面。
- **Content**: 当前：库存不足、即将 / 已过期、存储异常、危废处置、审计报表；下一步：JWT 登录、细粒度 RBAC、管理员冻结 / 编辑、二维码扫码、消息通知；后续：移动端、电子签名、批次级追踪、校级安全数据看板；运营指标：闭环时长、异常关闭率、过期批次率、审计完整率。

#### Slide 12 - 组员分工与汇报节奏

- **Audience move**: 从“系统方案”转为“团队如何在 9 月 16 日完成交付”。
- **Relationships**: 组员角色与交付物一一对应，时间节点按素材整理→模型绘制→联调演示→课堂汇报顺序排列。
- **Composition**: 左侧四行分工表，右侧竖向时间轴与最终 takeaway。
- **Title**: 组员分工与汇报节奏
- **Core message**: 分工围绕文档、前端、后端、建模与汇报形成闭环，名字可在课前直接替换。
- **Content**: 成员 A：可行性研究、需求规格与讲稿；成员 B：Vue 前端与演示数据；成员 C：Spring Boot API、事务与数据库；成员 D：DFD / ER / 状态图、PPT 视觉与现场汇报；时间线：9/12 素材冻结 → 9/13 模型与 PPT 初版 → 9/15 联调和演示彩排 → 9/16 分组汇报；答辩 takeaway：ChemTrack 用“状态 + 责任 + 审计”把危化品安全管理变成可验证的软件系统。

## X. Speaker Notes Requirements

- **Generation**: disabled
