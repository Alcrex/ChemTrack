<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 软件工程课程教师与同学、实验中心管理人员
- objective: 让听众理解 ChemTrack 的问题价值、需求边界、三种分析模型和可落地实现路径
- core_message: ChemTrack 把采购、库存、领用、使用、处置和审计连成一条可追溯责任链
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: pyramid, instructional
- mode_behavior: 先给结论与问题代价，再拆解需求与可行性，用 DFD、ER、状态转换解释设计，最后用真实业务链和分工收束。

## visual_style
- visual_style: custom
- visual_style_behavior: 深墨绿背景、近白正文、青色主流程、琥珀风险色；细网格、编号轨道、无阴影几何面板、状态芯片和连接线形成实验室控制台式审查界面。

## colors
- bg: #0E2422
- secondary_bg: #163C38
- primary: #BFE7D8
- accent: #57C7B0
- secondary_accent: #F2B866
- text: #F5F7F4
- secondary_text: #A8C1BB
- divider: #2A5650

## typography
- font_family: Microsoft YaHei, Aptos, Arial
- title_family: Microsoft YaHei, Aptos Display, Arial
- body_family: Microsoft YaHei, Aptos, Arial
- data_family: Cascadia Mono, Consolas, monospace
- body: 22
- small_heading: 17
- title: 34
- subtitle: 20
- annotation: 14
- footnote: 12

## icons
- library: none
- inventory: none

## page_rhythm
- P01: breathing
- P02: breathing
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: breathing
- P11: breathing
- P12: breathing

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
