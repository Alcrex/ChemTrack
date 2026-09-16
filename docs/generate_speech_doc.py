from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


OUT = Path(__file__).with_name("ChemTrack_演讲稿.docx")


def xml_text(value: str) -> str:
    return escape(value, quote=False)


def run(text: str, *, bold: bool = False, color: str | None = None, size: int | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{xml_text(text)}</w:t></w:r>"


def para(text: str = "", style: str = "Normal", *, before: int = 0, after: int = 160,
         line: int = 320, align: str | None = None, keep: bool = False) -> str:
    ppr = [f'<w:pStyle w:val="{style}"/>',
           f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>']
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if keep:
        ppr.append("<w:keepNext/>")
    content = run(text)
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{content}</w:p>"


def rich_para(parts: list[tuple[str, dict]], style: str = "Normal", *, after: int = 160,
             line: int = 320, align: str | None = None) -> str:
    ppr = [f'<w:pStyle w:val="{style}"/>',
           f'<w:spacing w:after="{after}" w:line="{line}" w:lineRule="auto"/>']
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{''.join(run(t, **opts) for t, opts in parts)}</w:p>"


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(rows: list[list[str]], widths: list[int] | None = None) -> str:
    widths = widths or [sum([9000]) // len(rows[0])] * len(rows[0])
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="B7CCC6"/>'
        '<w:left w:val="single" w:sz="6" w:color="B7CCC6"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="B7CCC6"/>'
        '<w:right w:val="single" w:sz="6" w:color="B7CCC6"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D8E5E1"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D8E5E1"/></w:tblBorders>'
    )
    out = [f'<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/>{borders}</w:tblPr><w:tblGrid>']
    out.extend(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out.append('</w:tblGrid>')
    for row_index, row in enumerate(rows):
        out.append('<w:tr>')
        for col_index, cell in enumerate(row):
            shade = 'E8F3EF' if row_index == 0 else 'FFFFFF'
            out.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[col_index]}" w:type="dxa"/>'
                f'<w:shd w:fill="{shade}"/></w:tcPr>'
                + rich_para([(cell, {"bold": row_index == 0, "color": "123A35" if row_index == 0 else None})],
                            "TableText", after=60, line=260)
                + '</w:tc>'
            )
        out.append('</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out)


SLIDES = [
    (
        "01｜开场：把危化品管理变成一条可追溯责任链",
        "这一页先说明我们为什么做 ChemTrack。它不是一个只展示库存数量的页面，而是一套面向校园实验室的危化品全生命周期管理系统。我们把采购、库存、领用、使用、处置和审计串成一条责任链。\n\n对每一次关键动作，系统都希望回答四个问题：谁在什么状态下做了什么，库存因此发生了什么变化，以及这次动作留下了什么证据。当前项目已经完成可运行 MVP，接下来我会从问题、可行性、需求、模型和实现五个方面展开。",
        "预计时长：35 秒",
        "切页提示：指向右侧的采购—库存—领用—使用—处置—审计链条，强调“全生命周期”和“责任证据”。",
    ),
    (
        "02｜问题定义：责任链断裂比功能不足更危险",
        "危化品管理真正的风险，往往不是系统少了一个按钮，而是信息在角色和状态之间断开了。现实中，采购、库存和领用可能分别记录；教师审批、管理员复核和学生使用之间也可能依赖口头确认；一旦发生过期、库存不足或异常处置，就很难还原完整过程。\n\n因此，ChemTrack 的目标不是简单地把纸质台账搬到网页上，而是建立一套统一台账、分级审批和闭环留痕机制。每一批危化品都应该能够回答：它从哪里来、谁批准过、谁使用过、还剩多少，以及最后如何处置。",
        "预计时长：50 秒",
        "切页提示：先讲左侧三个断点，再讲右侧三个系统目标，最后落到“每一批都能回答五个问题”。",
    ),
    (
        "03｜可行性：MVP 先落地，再扩展治理能力",
        "从可行性来看，我们把判断拆成四个维度。第一，经济上复用 Spring Boot、Vue 和 MySQL 等现有技术栈，校园服务器部署，软件采购成本可控。第二，技术上已经跑通 Java 17、Spring Boot 3.4、Vue 3、Vite 和 MySQL 8 的组合，事务、预警和审计都有实现基础。\n\n第三，操作上按学生、教师和管理员划分路径，页面按照采购、领用、风险和处置组织，学习成本相对清晰。第四，社会和法律方向上，系统能够支持台账、审批、最小权限和留痕，但具体法律适用和学校制度口径仍需要安全管理部门复核。综合判断是：现在可以做、可以演示、可以验收，治理能力再逐步扩展。",
        "预计时长：50 秒",
        "切页提示：讲到法律时明确“方向可行，但制度必须复核”，体现项目边界意识。",
    ),
    (
        "04｜功能需求：八个模块覆盖一条完整生命周期",
        "功能需求围绕生命周期组织，而不是把系统做成一排互相独立的菜单。采购入库负责申请、审批和验收；档案库存负责批次、有效期和存放位置；领用审批负责申请和分级审核；出库使用负责发放和使用记录；归还登记记录实际使用量并回补库存；风险预警发现库存、有效期和异常问题；废弃处置记录暂存、转运和完成；审计报表则汇总关键动作和管理结果。\n\n其中有两条关键规则：高风险试剂必须经过教师审批和管理员复核，所有关键动作都要写入审计日志，普通用户不能修改库存和历史记录。我们的验收口径也对应四点：角色可执行、状态可追踪、库存可校验、关键动作可审计。",
        "预计时长：55 秒",
        "切页提示：沿着 01 到 07 的生命周期顺序讲，最后重点落在 08 审计报表和两条业务规则。",
    ),
    (
        "05｜非功能需求：把“能运行”变成“可依赖”",
        "对安全场景来说，能完成一次操作还不够，还要保证系统在正常和异常情况下都可预测。性能上，课堂演示规模下常用查询需要即时反馈，审批和出库要有明确的成功或失败返回。可靠性上，出库和归还涉及库存变化，必须使用事务，库存不能小于零，审计事实不能被删除。\n\n可用性上，后端没有启动时，前端可以进入演示数据模式；健康检查通过后，再切换到真实 MySQL 数据。出错处理上，要拦截越权、过期、库存不足和归还数量不一致等情况。也就是说，我们验收的不只是“按钮能不能点”，还包括能否阻断错误、恢复状态并留下证据。",
        "预计时长：55 秒",
        "切页提示：这一页不要逐字读指标，抓住“性能、可靠性、可用性、出错处理”四个关键词和“可预测、可恢复、可审计”的结论。",
    ),
    (
        "06｜需求边界：接口、约束、逆向需求与未来要求",
        "为了让需求可以落到代码上，我们又明确了接口和边界。系统通过 REST API 连接前端、后端和数据库，覆盖健康检查、总览、危化品档案、采购、申请、使用记录、预警、异常、处置、审计和报表；审批、驳回、发放、归还和预警刷新等写操作也有对应接口。\n\n约束比功能清单更重要：普通用户不能修改库存和历史审计，高风险试剂不能绕过双重审批，发放和归还必须在事务中完成，实际使用量与归还量不能超过发放量。逆向需求则明确系统绝对不能出现什么。未来可以继续补充 JWT 登录、细粒度权限、消息通知、移动端、报表和法规规则配置，但这些属于下一阶段，不影响当前 MVP 的闭环验证。",
        "预计时长：55 秒",
        "切页提示：讲“逆向需求”时停顿一下，强调“不能绕过、不能负库存、不能删除、不能混淆演示数据”。",
    ),
    (
        "07｜DFD：角色、处理和数据存储形成可追踪链路",
        "接下来进入建模证据。数据流图回答的是：不同角色把什么信息交给系统，系统经过哪些处理，又把结果保存到哪里。外部角色包括学生、指导教师、实验室管理员、安全负责人以及校园统一认证。系统内部拆成八个处理：用户与角色、档案库存、采购入库、领用审批、出库归还、风险预警、废弃处置和审计报表。\n\n这些处理最终落到用户库、危化品档案库、批次库存库、领用记录库、审批记录库和审计日志库等数据存储中。这样，从申请、审批结果、入库信息到异常上报和统计报表，都能找到来源、处理责任和落库去向。",
        "预计时长：50 秒",
        "切页提示：按“外部实体—八个处理—数据存储—关键数据流”的顺序指图，避免在图上来回跳。",
    ),
    (
        "08｜ER：关键实体围绕申请单和化学品连接",
        "实体关系图进一步说明数据如何绑定。Chemical 和 Batch 代表危化品档案与具体批次，Request 是审批责任的中心，审批记录用于承载多阶段决策，UsageRecord 记录发放后的实际使用事实，Disposal 记录处置证据，Alert 和 Incident 记录风险与异常，AuditLog 则保留操作人、动作、对象和时间。\n\n这里的重点不是表越多越好，而是每个动作都能互相追溯。例如，一个申请能够找到对应批次、审批人和使用记录；一个使用记录能够回到申请和库存；一个处置记录能够回到来源和批次。数据库约束进一步保证批次号唯一、库存不小于零、外键完整，并让申请和使用记录保持一对一关系。",
        "预计时长：50 秒",
        "切页提示：重点解释 Request 是责任中心，UsageRecord 是使用事实，AuditLog 是不可删除的证据链。",
    ),
    (
        "09｜状态图：正常链和异常分支并存",
        "状态图把“谁能做什么”变成可验证的状态迁移。正常情况下，危化品从待采购、采购中、待验收、已入库、可领用，进入申请待审批；经过教师审批和管理员复核后才能发放，随后进入使用中、已归还、待处置和已处置。\n\n系统同时处理异常分支。批次过期或被冻结时，要阻断正常领用；库存不足时生成严重预警；审批驳回后回到申请修改；归还不一致、泄漏或存储异常则上报事件并进入处理闭环。每一次迁移都对应一个业务事件，例如到货、验收、审批、发放、归还、处置完成或发现泄漏。这样，状态不仅是页面上的标签，也是权限、库存行为和审计动作的依据。",
        "预计时长：55 秒",
        "切页提示：先沿主链走一遍，再补充右侧异常分支，突出“异常不是跳出系统，而是进入闭环”。",
    ),
    (
        "10｜课堂演示：用一条真实路径证明需求可落地",
        "下面用一条完整业务路径验证前面的需求和模型。第一步由管理员发起采购并推进入库，第二步建立批次档案；第三步由学生提交领用申请；第四步由教师审批；第五步由管理员复核；第六步办理发放，系统在事务中扣减库存并创建使用记录；第七步查看使用记录，登记实际使用量和归还量；最后进入风险扫描、异常处理和废弃处置。\n\n这条路径中，每一步都能同时在四个层面找到证据：前端页面上能操作，REST API 有对应请求，数据库有 requests、usage_records、alerts 和 audit_logs 等记录，页面状态和库存也会同步变化。课堂演示时我会按这个顺序操作，重点展示审批状态推进、库存变化、归还登记和审计日志。",
        "预计时长：1 分 20 秒",
        "切页提示：此页进入系统操作；按“采购入库 → 新建申请 → 教师审批 → 管理员复核 → 发放 → 使用记录 → 风险中心 → 审计”执行。",
    ),
    (
        "11｜实现映射：技术栈与需求一一对应",
        "实现层面，前端使用 Vue 3 和 Vite，提供总览、危化品档案、采购入库、领用审批、风险中心、废弃处置和审计等页面；服务层使用 Spring Boot 3.4、Java 17、REST Controller、Validation、JDBC 和健康检查；数据层使用 MySQL 8 保存用户、危化品、采购、申请、审批、使用、异常、处置、预警和审计数据。\n\n目前已经覆盖生命周期闭环、风险预警、角色演示和审计展示。下一阶段的重点是身份认证、细粒度权限、通知、移动端和更完整的法规配置。这里要区分“当前 MVP 已完成”和“未来增强项”：前者用于证明课程设计可运行，后者用于说明系统如何继续走向可运营。",
        "预计时长：45 秒",
        "切页提示：左侧讲技术分层，右侧讲已实现与下一阶段，明确不要把 JWT、移动端等规划说成当前成果。",
    ),
    (
        "12｜结论：可行、可验收、可持续演进",
        "最后总结三点。第一，可行性上，技术和操作已经验证，经济成本可控，社会价值明确，法律方向保留制度复核边界。第二，需求上，功能、性能、可靠性、可用性、异常、接口、约束、逆向需求和未来要求都找到了对应落点。第三，实现上，Vue、Spring Boot 和 MySQL 与 DFD、ER 和状态模型保持一致，并通过一条真实业务链完成验证。\n\n所以，ChemTrack 不是把几个页面拼在一起，而是用状态、责任和审计把危化品安全管理变成可验证的软件系统。我们最后留下一个答辩检查句：每一个需求，是否都有角色、状态、数据、接口和验收证据？谢谢大家，欢迎提问。",
        "预计时长：50 秒",
        "切页提示：结尾停留在三条答辩结论和最后一句检查句，不要急着退出放映。",
    ),
]


def styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos" w:eastAsia="Microsoft YaHei"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="183A36"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:widowControl/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos" w:eastAsia="Microsoft YaHei"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="220"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="40"/><w:szCs w:val="40"/><w:color w:val="123A35"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="160"/><w:jc w:val="center"/></w:pPr><w:rPr><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="5B7770"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="80" w:after="180"/></w:pPr><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display" w:eastAsia="Microsoft YaHei"/><w:b/><w:sz w:val="30"/><w:szCs w:val="30"/><w:color w:val="123A35"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="90"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="2C7566"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="480" w:right="480"/><w:spacing w:before="100" w:after="180"/></w:pPr><w:rPr><w:i/><w:color w:val="2C7566"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/><w:basedOn w:val="Normal"/><w:rPr><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:basedOn w:val="Normal"/><w:rPr><w:sz w:val="19"/><w:szCs w:val="19"/><w:color w:val="5B7770"/></w:rPr></w:style>
</w:styles>'''


def document_xml() -> str:
    body: list[str] = []
    body.append(para("ChemTrack 演讲稿", "Title", after=120, line=320, align="center"))
    body.append(para("软件工程课程设计汇报", "Subtitle", after=70, line=300, align="center"))
    body.append(para("依据《ChemTrack_可行性与需求规格说明书汇报》整理", "Subtitle", after=420, line=300, align="center"))
    body.append(table([
        ["项目", "校园实验室危化品全生命周期管理系统"],
        ["预计时长", "约 10 分钟（含系统演示）"],
        ["汇报主线", "问题 → 可行性 → 需求 → 模型 → 实现"],
        ["演讲重点", "状态、责任、库存变化与审计证据"],
    ], [1800, 7200]))
    body.append(para("使用说明", "Heading2", before=360, after=100, keep=True))
    body.append(para("每个“第 X 页”对应 PPT 的一页。正文可直接照读；“切页提示”用于提醒讲解重点和系统操作，不需要在台上逐字朗读。演示时以 PPT 第 10 页的业务顺序为准。", "Normal", after=180))
    body.append(rich_para([("开场建议：", {"bold": True, "color": "2C7566"}), ("先用一句话说明系统价值，再进入问题定义，不要一开始就介绍技术栈。", {})], "Quote", after=220))
    body.append(page_break())

    for index, (title, speech, duration, cue) in enumerate(SLIDES, 1):
        body.append(para(title, "Heading1", after=120, keep=True))
        body.append(para(duration, "Caption", after=100))
        body.append(para("演讲正文", "Heading2", before=80, after=80, keep=True))
        for paragraph in speech.split("\n\n"):
            body.append(para(paragraph, "Normal", after=150, line=340))
        body.append(para("演示 / 切页提示", "Heading2", before=180, after=80, keep=True))
        body.append(rich_para([("提示：", {"bold": True, "color": "C37B2B"}), (cue, {})], "Quote", after=100, line=300))
        if index != len(SLIDES):
            body.append(page_break())

    body.append(page_break())
    body.append(para("附录｜演示前快速检查", "Heading1", after=160))
    body.append(table([
        ["检查项", "确认内容"],
        ["前端", "npm run dev，浏览器可打开 http://localhost:5173"],
        ["后端", "mvn spring-boot:run，健康检查 http://localhost:8080/api/health"],
        ["数据库", "MySQL 已初始化 database/schema.sql，密码通过 CHEMTRACK_DB_PASSWORD 提供"],
        ["演示顺序", "采购入库 → 新建申请 → 教师审批 → 管理员复核 → 发放 → 使用记录 → 风险中心 → 审计"],
        ["兜底方案", "后端未启动时使用前端演示数据模式；不要把演示数据称为真实台账"],
    ], [1800, 7200]))
    body.append(para("答辩时可以反复回到这句话：每一个需求是否都有角色、状态、数据、接口和验收证据？", "Quote", before=260, after=0, line=340))

    sect = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1200" w:right="1200" '
        'w:bottom="1200" w:left="1200" w:header="600" w:footer="600" w:gutter="0"/>'
        '<w:footerReference w:type="default" r:id="rIdFooter"/><w:cols w:space="720"/></w:sectPr>'
    )
    body.append(sect)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<w:body>{"".join(body)}</w:body></w:document>'
    )


def content_types() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>'''


def rels() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def document_rels() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''


def footer_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:color w:val="7B918B"/><w:sz w:val="17"/></w:rPr><w:t>ChemTrack 演讲稿  ·  </w:t></w:r>
  <w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
</w:ftr>'''


def main() -> None:
    with ZipFile(OUT, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types())
        docx.writestr("_rels/.rels", rels())
        docx.writestr("word/document.xml", document_xml())
        docx.writestr("word/styles.xml", styles_xml())
        docx.writestr("word/footer1.xml", footer_xml())
        docx.writestr("word/_rels/document.xml.rels", document_rels())
    print(OUT)


if __name__ == "__main__":
    main()
