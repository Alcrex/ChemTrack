from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
RAW_SCREEN = ASSETS / "chemtrack-running-raw.png"
SCREEN = ASSETS / "chemtrack-dashboard.png"
SCREEN_TOP = ASSETS / "chemtrack-overview-top.png"
SCREEN_BOTTOM = ASSETS / "chemtrack-overview-bottom.png"
SCREEN_SIDE = ASSETS / "chemtrack-navigation.png"
GITHUB_SCREEN = ASSETS / "chemtrack-github-repository.png"
OUTPUT = ROOT / "ChemTrack_可行性与需求规格说明书_合并汇报_最终版.pptx"


W, H = 13.333, 7.5
BG = RGBColor(248, 250, 248)
WHITE = RGBColor(255, 255, 255)
INK = RGBColor(18, 47, 49)
MUTED = RGBColor(103, 123, 119)
LINE = RGBColor(218, 230, 225)
TEAL = RGBColor(28, 92, 87)
TEAL_LIGHT = RGBColor(224, 241, 236)
AMBER = RGBColor(231, 161, 59)
AMBER_LIGHT = RGBColor(255, 244, 216)
CORAL = RGBColor(226, 111, 98)
CORAL_LIGHT = RGBColor(255, 235, 231)
PINK = RGBColor(215, 119, 150)
BLUE = RGBColor(78, 144, 196)
PURPLE = RGBColor(125, 111, 184)


def crop_assets():
    if not RAW_SCREEN.exists():
        raise FileNotFoundError(RAW_SCREEN)
    if not GITHUB_SCREEN.exists():
        raise FileNotFoundError(GITHUB_SCREEN)
    with Image.open(RAW_SCREEN) as image:
        # The browser chrome occupies the first 120 px and the taskbar the last 48 px.
        app = image.crop((0, 120, image.width, image.height - 48))
        app.save(SCREEN)
        app.crop((230, 0, app.width, 540)).save(SCREEN_TOP)
        app.crop((230, 470, app.width, app.height)).save(SCREEN_BOTTOM)
        app.crop((0, 0, 260, app.height)).save(SCREEN_SIDE)


def set_bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def box(slide, x, y, w, h, fill=WHITE, line=LINE, radius=True, transparency=0):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.fill.transparency = transparency
    shape.line.color.rgb = line
    shape.line.width = Pt(0.8)
    if radius:
        shape.adjustments[0] = 0.08
    return shape


def line(slide, x1, y1, x2, y2, color=LINE, width=1.2, dash=None):
    shape = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(x1), Inches(y1), Inches(x2), Inches(y2),
    )
    shape.line.color.rgb = color
    shape.line.width = Pt(width)
    if dash:
        shape.line.dash_style = dash
    return shape


def text(slide, value, x, y, w, h, size=16, color=INK, bold=False,
         align=PP_ALIGN.LEFT, font="Microsoft YaHei", valign=MSO_ANCHOR.TOP,
         margin=0.02, italic=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_after = Pt(0)
    run = p.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return shape


def rich_text(slide, runs, x, y, w, h, size=16, color=INK, align=PP_ALIGN.LEFT,
              valign=MSO_ANCHOR.TOP, margin=0.02):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_after = Pt(0)
    for value, run_color, bold in runs:
        run = p.add_run()
        run.text = value
        run.font.name = "Microsoft YaHei"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = run_color
    return shape


def pill(slide, value, x, y, w, fill=TEAL_LIGHT, color=TEAL):
    box(slide, x, y, w, 0.28, fill, fill, True)
    text(slide, value, x, y + 0.02, w, 0.22, 9, color, True, PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def section_header(slide, kicker, title, subtitle, number):
    text(slide, kicker.upper(), 0.55, 0.34, 4.8, 0.22, 9, TEAL, True)
    text(slide, title, 0.55, 0.68, 11.9, 0.52, 27, INK, True)
    text(slide, subtitle, 0.58, 1.27, 11.2, 0.28, 11, MUTED)
    line(slide, 0.55, 1.70, 12.78, 1.70, LINE, 0.9)
    text(slide, f"CHEMTRACK  /  {number:02d}", 11.25, 7.13, 1.5, 0.18, 8, MUTED, True, PP_ALIGN.RIGHT)


def footer(slide, number):
    text(slide, "顾峰鸣 Web 版  ·  张誉诚 Release 桌面端", 0.55, 7.13, 5.0, 0.18, 8, MUTED)
    text(slide, f"{number:02d}", 12.35, 7.13, 0.43, 0.18, 8, MUTED, True, PP_ALIGN.RIGHT)


def add_stat(slide, x, y, w, label, value, note, color):
    box(slide, x, y, w, 1.15, WHITE, LINE)
    line(slide, x, y, x + w, y, color, 2.5)
    text(slide, label, x + 0.15, y + 0.17, w - 0.3, 0.18, 10, MUTED)
    text(slide, value, x + 0.15, y + 0.38, w - 0.3, 0.37, 27, INK, True)
    text(slide, note, x + 0.15, y + 0.87, w - 0.3, 0.16, 9, MUTED)


def add_bullet(slide, x, y, w, title, body, color=TEAL):
    box(slide, x, y, 0.23, 0.23, color, color, True)
    text(slide, "", x, y, 0.23, 0.23)
    text(slide, title, x + 0.35, y - 0.01, w - 0.35, 0.24, 13, INK, True)
    text(slide, body, x + 0.35, y + 0.27, w - 0.35, 0.44, 10, MUTED)


def add_node(slide, x, y, w, h, title, body, fill=WHITE, accent=TEAL):
    box(slide, x, y, w, h, fill, LINE)
    line(slide, x, y, x + w, y, accent, 2.3)
    text(slide, title, x + 0.14, y + 0.16, w - 0.28, 0.23, 12, INK, True)
    text(slide, body, x + 0.14, y + 0.48, w - 0.28, h - 0.58, 9, MUTED)


def entity_box(slide, x, y, w, h, title, fields, accent=TEAL, fill=WHITE):
    box(slide, x, y, w, h, fill, LINE)
    box(slide, x, y, w, 0.34, accent, accent, False)
    text(slide, title, x + 0.08, y + 0.08, w - 0.16, 0.16, 10, WHITE, True, PP_ALIGN.CENTER)
    for i, field in enumerate(fields):
        text(slide, field, x + 0.12, y + 0.48 + i * 0.23, w - 0.24, 0.16, 8.5, INK if i == 0 else MUTED, i == 0)


def flow_label(slide, value, x, y, w, color=TEAL):
    box(slide, x, y, w, 0.24, RGBColor(247, 250, 248), RGBColor(247, 250, 248))
    text(slide, value, x, y + 0.035, w, 0.14, 8, color, True, PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def transition(slide, x1, y1, x2, y2, label, color=TEAL, label_x=None, label_y=None, label_w=1.0):
    line(slide, x1, y1, x2, y2, color, 1.6)
    if label:
        flow_label(slide, label, label_x if label_x is not None else (x1 + x2) / 2 - label_w / 2,
                   label_y if label_y is not None else (y1 + y2) / 2 - 0.12, label_w, color)


def add_image_card(slide, path, x, y, w, h, caption, accent=TEAL):
    box(slide, x, y, w, h, WHITE, LINE)
    content_x, content_y = x + 0.07, y + 0.07
    content_w, content_h = w - 0.14, h - 0.52
    with Image.open(path) as image:
        image_w, image_h = image.size
    scale = min(content_w / image_w, content_h / image_h)
    render_w, render_h = image_w * scale, image_h * scale
    render_x = content_x + (content_w - render_w) / 2
    render_y = content_y + (content_h - render_h) / 2
    slide.shapes.add_picture(str(path), Inches(render_x), Inches(render_y), width=Inches(render_w), height=Inches(render_h))
    line(slide, x + 0.07, y + h - 0.39, x + w - 0.07, y + h - 0.39, accent, 1.4)
    text(slide, caption, x + 0.12, y + h - 0.31, w - 0.24, 0.2, 9, INK, True)


def build():
    crop_assets()
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    blank = prs.slide_layouts[6]

    # 1 Cover
    slide = prs.slides.add_slide(blank)
    set_bg(slide, RGBColor(252, 253, 251))
    slide.shapes.add_picture(str(ASSETS / "taffy-background.png"), Inches(7.2), Inches(0), width=Inches(6.2), height=Inches(7.5)) if (ASSETS / "taffy-background.png").exists() else None
    box(slide, 0.58, 0.62, 1.25, 0.33, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "SOFTWARE ENGINEERING", 0.67, 0.69, 1.07, 0.15, 7, TEAL, True, PP_ALIGN.CENTER)
    text(slide, "ChemTrack", 0.58, 1.40, 6.0, 0.74, 42, INK, True)
    text(slide, "把危化品管理变成一条可追溯责任链", 0.62, 2.32, 6.25, 0.48, 22, TEAL, True)
    text(slide, "可行性研究与需求规格说明书汇报", 0.65, 3.05, 5.5, 0.32, 14, MUTED)
    text(slide, "顾峰鸣：Web 版     张誉诚：Release 桌面端", 0.65, 3.55, 6.1, 0.25, 11, MUTED)
    box(slide, 0.65, 5.48, 11.8, 0.76, WHITE, LINE)
    stages = [("采购", TEAL), ("入库", BLUE), ("领用", AMBER), ("使用", PURPLE), ("归还", CORAL), ("处置", PINK), ("审计", TEAL)]
    start = 0.93
    for i, (label, color) in enumerate(stages):
        cx = start + i * 1.63
        box(slide, cx, 5.70, 0.72, 0.28, color, color)
        text(slide, label, cx, 5.735, 0.72, 0.18, 9, WHITE, True, PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        if i < len(stages) - 1:
            line(slide, cx + 0.75, 5.84, cx + 1.50, 5.84, LINE, 1.2)
    text(slide, "2026.09  ·  课程设计答辩版", 0.65, 6.73, 4.0, 0.2, 9, MUTED)
    text(slide, "WEB  ×  DESKTOP RELEASE", 9.3, 6.73, 3.25, 0.2, 9, TEAL, True, PP_ALIGN.RIGHT)

    # 2 Problem and value
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "01 / 问题与价值", "责任链断裂，比功能不足更危险", "危化品风险来自跨角色、跨状态的信息断裂；系统目标是把每一批次的证据链连接起来。", 2)
    box(slide, 0.65, 2.10, 5.75, 3.85, CORAL_LIGHT, CORAL_LIGHT)
    text(slide, "现状断点", 0.95, 2.38, 2.1, 0.28, 16, CORAL, True)
    add_bullet(slide, 0.98, 2.95, 4.85, "信息分散", "账本、表格、口头记录各自独立，库存和有效期无法联动。", CORAL)
    add_bullet(slide, 0.98, 3.80, 4.85, "审批脱节", "申请、教师审批、管理员复核缺少统一的状态与证据。", CORAL)
    add_bullet(slide, 0.98, 4.65, 4.85, "责任难追", "使用、归还、处置和异常分散，出问题时难以还原链路。", CORAL)
    box(slide, 6.92, 2.10, 5.75, 3.85, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "ChemTrack 的回答", 7.22, 2.38, 3.0, 0.28, 16, TEAL, True)
    add_bullet(slide, 7.25, 2.95, 4.85, "一套台账", "批次、CAS、有效期、存储要求和二维码统一建档。", TEAL)
    add_bullet(slide, 7.25, 3.80, 4.85, "分级审批", "高风险试剂必须教师审批 + 管理员复核。", TEAL)
    add_bullet(slide, 7.25, 4.65, 4.85, "可追溯闭环", "从采购到处置持续留痕，风险中心主动提示和收敛。", TEAL)
    text(slide, "每一批危化品都能回答：从哪里来、谁批准、谁使用、剩多少、如何处置。", 1.0, 6.35, 11.2, 0.3, 17, INK, True, PP_ALIGN.CENTER)
    footer(slide, 2)

    # 3 Feasibility
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "02 / 可行性研究", "经济、技术、操作、社会与法律可行性", "MVP 已跑通，当前重点是把可运行原型转成可部署、可治理、可审计的校园实验室系统。", 3)
    dims = [
        ("经济", "低成本复用", "已有前后端与桌面端成果，部署与软件采购成本可控。", AMBER),
        ("技术", "路线成熟", "Java 17 + Spring Boot 3.4 + Vue 3 + Vite + MySQL 8 已跑通。", BLUE),
        ("操作", "角色贴合", "学生、教师、管理员、安全负责人按业务路径分区操作。", TEAL),
        ("社会", "降低遗漏", "把安全责任从个人记忆转成流程证据，管理更透明。", PURPLE),
        ("法律", "制度复核", "覆盖安全能力，最终制度口径与法律适用由学校审核。", CORAL),
    ]
    for i, (label, title_, body_, color) in enumerate(dims):
        x = 0.66 + i * 2.52
        box(slide, x, 2.25, 2.18, 3.55, WHITE, LINE)
        box(slide, x, 2.25, 2.18, 0.16, color, color, False)
        text(slide, f"0{i+1}", x + 0.16, 2.58, 0.46, 0.38, 25, color, True)
        text(slide, label, x + 0.16, 3.10, 1.75, 0.24, 14, INK, True)
        text(slide, title_, x + 0.16, 3.47, 1.75, 0.22, 10, color, True)
        text(slide, body_, x + 0.16, 3.90, 1.78, 1.20, 10, MUTED)
        pill(slide, "可验证", x + 0.16, 5.22, 0.70, TEAL_LIGHT, TEAL)
    box(slide, 0.66, 6.12, 12.0, 0.52, INK, INK)
    text(slide, "总判定  /  方案可行，下一阶段重点转向认证、备份、安全和合规治理。", 0.9, 6.24, 11.5, 0.20, 13, WHITE, True, PP_ALIGN.CENTER)
    footer(slide, 3)

    # 4 Architecture / dual delivery
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "03 / 系统边界与接口", "双端交付，统一一套业务责任链", "Web 版面向浏览器操作；Release 桌面端用 WPF + WebView2 封装，二者通过 REST API 连接同一套业务数据。", 4)
    add_node(slide, 0.75, 2.35, 2.40, 1.38, "Web 版", "Vue 3 + Vite\n总览、档案、审批、预警、审计", TEAL_LIGHT, TEAL)
    add_node(slide, 0.75, 4.25, 2.40, 1.38, "Release 桌面端", ".NET 8 WPF + WebView2\n启动后端、健康检查、回收进程", AMBER_LIGHT, AMBER)
    add_node(slide, 5.10, 3.25, 2.55, 1.55, "REST API", "健康检查\n业务状态流转\n事务与审计", WHITE, BLUE)
    add_node(slide, 9.35, 3.25, 2.60, 1.55, "MySQL 8", "users · chemicals\nrequests · usages\naudit_logs · alerts", WHITE, PURPLE)
    line(slide, 3.20, 3.04, 5.10, 3.92, TEAL, 2.0)
    line(slide, 3.20, 4.94, 5.10, 4.13, AMBER, 2.0)
    line(slide, 7.65, 4.03, 9.35, 4.03, BLUE, 2.0)
    text(slide, "统一状态 / 统一约束 / 统一留痕", 4.30, 5.55, 4.75, 0.28, 16, TEAL, True, PP_ALIGN.CENTER)
    box(slide, 0.80, 6.16, 11.95, 0.53, WHITE, LINE)
    text(slide, "角色边界：学生提交与归还  ·  教师审批高风险申请  ·  管理员复核、发放、入库  ·  安全负责人处理异常与废弃物", 1.02, 6.31, 11.5, 0.18, 10, MUTED, align=PP_ALIGN.CENTER)
    footer(slide, 4)

    # 5 Lifecycle
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "04 / 业务闭环", "从采购到处置：每个状态都有下一位责任人", "正常链持续记录批次、审批、库存、使用与处置；异常路径负责阻断、预警和闭环处理。", 5)
    labels = [("01", "采购", TEAL), ("02", "入库", BLUE), ("03", "领用", AMBER), ("04", "使用", PURPLE), ("05", "归还", CORAL), ("06", "预警", PINK), ("07", "处置", TEAL), ("08", "审计", INK)]
    for i, (n, lab, color) in enumerate(labels):
        x = 0.75 + i * 1.55
        if i < len(labels) - 1:
            line(slide, x + 0.67, 3.18, x + 1.52, 3.18, LINE, 1.5)
        box(slide, x, 2.58, 1.32, 1.20, WHITE, LINE)
        box(slide, x + 0.14, 2.78, 0.44, 0.30, color, color)
        text(slide, n, x + 0.14, 2.84, 0.44, 0.15, 8, WHITE, True, PP_ALIGN.CENTER)
        text(slide, lab, x + 0.14, 3.24, 1.05, 0.23, 13, INK, True)
    box(slide, 0.78, 4.45, 5.85, 1.35, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "正常链", 1.03, 4.70, 1.0, 0.22, 13, TEAL, True)
    text(slide, "待采购 → 采购中 → 待验收 → 已入库 → 可领用 → 分级审批 → 已发放 → 使用中 → 已归还 → 待处置 → 已处置", 1.03, 5.08, 5.25, 0.45, 10, INK)
    box(slide, 6.82, 4.45, 5.78, 1.35, CORAL_LIGHT, CORAL_LIGHT)
    text(slide, "异常分支", 7.07, 4.70, 1.1, 0.22, 13, CORAL, True)
    text(slide, "库存不足 / 已过期 / 审批驳回 / 归还不一致 / 泄漏 / 存储异常", 7.07, 5.08, 5.05, 0.22, 10, INK)
    text(slide, "→ 阻断正常领用，生成预警或异常事件，进入处理与审计闭环", 7.07, 5.38, 5.05, 0.22, 10, MUTED)
    footer(slide, 5)

    # 6 Functional requirements
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "05 / 需求规格", "功能需求：围绕危化品全生命周期形成闭环", "每个核心动作都有角色边界、状态变化、数据对象和审计记录。", 6)
    reqs = [
        ("FR-01", "批次档案", "CAS、有效期、存储要求、二维码和位置", TEAL),
        ("FR-02", "采购入库", "申请 → 审批 → 采购中 → 验收 → 入库", BLUE),
        ("FR-03", "领用审批", "普通试剂单级审批，高风险双重审批", AMBER),
        ("FR-04", "出库与使用", "办理发放时事务扣减库存，建立使用记录", PURPLE),
        ("FR-05", "归还登记", "实际使用量、归还量、异常说明与库存回补", CORAL),
        ("FR-06", "风险与审计", "预警、异常、废弃物和汇总报表全程留痕", PINK),
    ]
    for i, (code, title_, body_, color) in enumerate(reqs):
        row, col = divmod(i, 3)
        x = 0.75 + col * 4.18
        y = 2.25 + row * 1.72
        box(slide, x, y, 3.70, 1.34, WHITE, LINE)
        box(slide, x, y, 0.12, 1.34, color, color, False)
        text(slide, code, x + 0.26, y + 0.19, 0.75, 0.20, 9, color, True)
        text(slide, title_, x + 0.26, y + 0.47, 2.9, 0.25, 14, INK, True)
        text(slide, body_, x + 0.26, y + 0.82, 3.10, 0.31, 10, MUTED)
    box(slide, 0.75, 6.02, 11.84, 0.52, INK, INK)
    text(slide, "验收口径：角色可执行  ·  状态可追踪  ·  库存可校验  ·  关键动作可审计", 0.95, 6.17, 11.4, 0.18, 13, WHITE, True, PP_ALIGN.CENTER)
    footer(slide, 6)

    # 7 Quality and boundaries
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "06 / 需求规格说明书", "非功能需求：性能、可靠性、可用性、出错处理", "安全系统不仅要完成操作，还要在边界条件下保持可预测、可恢复、可解释。", 7)
    quality = [("性能", "课堂演示规模下列表与查询即时反馈", "接口响应与边界数据测试", BLUE), ("可靠性", "出库、归还使用事务，库存不能小于 0", "异常回滚与日志核对", TEAL), ("可用性", "后端未启动时进入演示数据模式", "断后端与恢复场景演示", AMBER), ("出错处理", "越权、过期、库存不足时阻断提交", "错误提示与阻断规则", CORAL)]
    for i, (label, body_, verify, color) in enumerate(quality):
        x = 0.75 + i * 3.08
        box(slide, x, 2.20, 2.72, 1.75, WHITE, LINE)
        text(slide, label, x + 0.18, 2.42, 1.3, 0.22, 14, color, True)
        text(slide, body_, x + 0.18, 2.80, 2.30, 0.54, 10, INK)
        text(slide, "验证  /  " + verify, x + 0.18, 3.54, 2.30, 0.25, 9, MUTED)
    box(slide, 0.75, 4.35, 11.85, 1.55, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "可靠性与可用性证据", 1.02, 4.62, 2.8, 0.22, 13, TEAL, True)
    text(slide, "事务保障：出库、归还、审批状态一致；健康检查：/api/health 明确服务状态；演示回退：后端未启动时可进入演示数据模式；审计事实：关键动作不可删除。", 1.02, 5.02, 11.15, 0.42, 10, INK)
    footer(slide, 7)

    # 8 Requirements boundary: interface, constraints, reverse requirements, future requests
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "07 / 需求规格说明书", "接口需求、约束、逆向需求与将来可能提出的要求", "把系统必须连接什么、必须遵守什么、绝不能做什么、未来如何扩展一次说清。", 8)
    box(slide, 0.72, 2.15, 3.88, 3.85, WHITE, LINE)
    box(slide, 0.72, 2.15, 3.88, 0.12, BLUE, BLUE, False)
    text(slide, "接口需求", 0.98, 2.48, 1.6, 0.24, 15, BLUE, True)
    text(slide, "前端 / 桌面端 → REST API → MySQL", 0.98, 2.88, 3.0, 0.22, 10, INK, True)
    text(slide, "读接口\nGET /health · /dashboard · /chemicals\nGET /requests · /usages · /alerts\nGET /incidents · /disposals · /audit\n\n写接口\nPOST /requests · /procurements\nPATCH /approve · /reject · /issue · /return\nPOST /alerts/refresh", 0.98, 3.30, 3.10, 2.10, 9.5, MUTED)
    box(slide, 4.77, 2.15, 3.78, 3.85, CORAL_LIGHT, CORAL_LIGHT)
    box(slide, 4.77, 2.15, 3.78, 0.12, CORAL, CORAL, False)
    text(slide, "约束 + 逆向需求", 5.03, 2.48, 2.5, 0.24, 15, CORAL, True)
    text(slide, "业务约束", 5.03, 2.90, 1.2, 0.18, 10, CORAL, True)
    text(slide, "高风险试剂必须教师审批 + 管理员复核\n库存不能小于 0\n实际使用量 + 归还量 ≤ 发放量\n普通用户不能修改历史审计", 5.03, 3.20, 3.02, 0.96, 9.5, INK)
    text(slide, "系统绝不能", 5.03, 4.42, 1.3, 0.18, 10, CORAL, True)
    text(slide, "绕过审批直接出库\n删除关键审计事实\n让过期批次进入正常领用\n把演示数据当真实台账", 5.03, 4.72, 3.02, 0.78, 9.5, INK)
    box(slide, 8.72, 2.15, 3.88, 3.85, AMBER_LIGHT, AMBER_LIGHT)
    box(slide, 8.72, 2.15, 3.88, 0.12, AMBER, AMBER, False)
    text(slide, "将来可能提出的要求", 8.98, 2.48, 3.0, 0.24, 15, AMBER, True)
    text(slide, "统一认证与 JWT 登录\n细粒度角色权限与通知中心\n多实验室 / 多校区部署\n二维码、移动端、电子签名\n报表导出与自动备份\n法规规则可配置、可审计", 8.98, 3.05, 3.05, 1.65, 10, INK)
    pill(slide, "先满足边界，再扩展能力", 9.00, 5.30, 2.25, WHITE, AMBER)
    footer(slide, 8)

    # 9 DFD evidence
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "08 / 需求分析建模", "数据流图（DFD）：外部实体、处理过程、数据存储与数据流", "以“领用申请 → 分级审批 → 发放扣减 → 使用归还 → 预警审计”为主线，展示数据如何穿过系统。", 9)
    # External entities
    entity_box(slide, 0.62, 2.25, 1.85, 0.86, "学生", ["领用申请 / 归还"], AMBER, AMBER_LIGHT)
    entity_box(slide, 0.62, 3.52, 1.85, 0.86, "指导教师", ["高风险审批"], AMBER, AMBER_LIGHT)
    entity_box(slide, 0.62, 4.79, 1.85, 0.86, "管理员 / 安全负责人", ["入库 / 复核 / 处置"], AMBER, AMBER_LIGHT)
    # Processing nodes
    add_node(slide, 3.05, 2.12, 2.24, 1.05, "P1 档案与入库", "批次、库存、有效期", TEAL_LIGHT, TEAL)
    add_node(slide, 3.05, 3.55, 2.24, 1.05, "P2 领用与审批", "申请、教师审批、管理员复核", TEAL_LIGHT, TEAL)
    add_node(slide, 3.05, 4.98, 2.24, 1.05, "P3 使用与归还", "发放扣减、实际用量、回补", TEAL_LIGHT, TEAL)
    add_node(slide, 6.05, 3.55, 2.24, 1.05, "P4 风险与处置", "预警、异常、危废流程", CORAL_LIGHT, CORAL)
    add_node(slide, 6.05, 4.98, 2.24, 1.05, "P5 审计与报表", "关键动作、统计摘要", CORAL_LIGHT, CORAL)
    # Data stores
    entity_box(slide, 9.10, 2.10, 3.10, 0.72, "D1 用户 / 角色库", ["users · roles"], BLUE, WHITE)
    entity_box(slide, 9.10, 3.08, 3.10, 0.72, "D2 危化品 / 批次库存库", ["chemicals · batches"], BLUE, WHITE)
    entity_box(slide, 9.10, 4.06, 3.10, 0.72, "D3 申请 / 审批 / 使用库", ["requests · approvals · usages"], BLUE, WHITE)
    entity_box(slide, 9.10, 5.04, 3.10, 0.72, "D4 预警 / 处置 / 审计库", ["alerts · disposals · audit_logs"], BLUE, WHITE)
    # Labeled flows
    transition(slide, 2.47, 2.68, 3.05, 3.98, "申请", AMBER, 2.50, 3.02, 0.62)
    transition(slide, 2.47, 3.95, 3.05, 4.05, "审批意见", AMBER, 2.42, 3.72, 0.78)
    transition(slide, 2.47, 5.22, 3.05, 5.45, "操作指令", AMBER, 2.44, 5.00, 0.76)
    transition(slide, 5.29, 2.65, 9.10, 3.44, "入库 / 库存", TEAL, 6.15, 2.78, 1.00)
    transition(slide, 5.29, 4.08, 9.10, 4.42, "申请 / 审批", TEAL, 6.12, 4.08, 1.00)
    transition(slide, 5.29, 5.50, 9.10, 4.42, "使用记录", TEAL, 6.05, 5.18, 0.90)
    transition(slide, 5.29, 4.08, 6.05, 4.08, "异常条件", CORAL, 5.38, 3.78, 0.86)
    transition(slide, 8.29, 4.08, 9.10, 5.40, "预警 / 处置", CORAL, 8.18, 4.56, 1.00)
    transition(slide, 8.29, 5.50, 9.10, 5.40, "审计结果", CORAL, 8.22, 5.65, 0.94)
    text(slide, "读写数据流：前端 / 桌面端提交操作，核心处理校验状态与库存，数据存储保留业务事实。", 0.82, 6.34, 11.8, 0.26, 11, INK, True, PP_ALIGN.CENTER)
    footer(slide, 9)

    # 10 ER model
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "09 / 需求分析建模", "实体-联系图（ER）：申请单连接责任、库存、使用与处置", "实体、主键 / 外键和基数关系来自 ChemTrack 的业务表设计；申请单是审批责任的中心。", 10)
    entity_box(slide, 0.70, 2.10, 2.20, 1.52, "User / Role", ["PK user_id", "name · role", "1:N Request", "1:N AuditLog"], AMBER, AMBER_LIGHT)
    entity_box(slide, 4.04, 2.10, 2.48, 1.52, "Chemical / Batch", ["PK chemical_id", "CAS · batch_no", "expiry · quantity", "1:N Request / Alert"], PURPLE, WHITE)
    entity_box(slide, 8.05, 2.10, 2.42, 1.52, "Request", ["PK request_id", "FK chemical_id", "amount · status", "applicant · supervisor"], TEAL, TEAL_LIGHT)
    entity_box(slide, 1.18, 4.60, 2.30, 1.52, "ApprovalRecord", ["PK approval_id", "FK request_id", "stage · approver", "decision · time"], BLUE, WHITE)
    entity_box(slide, 4.58, 4.60, 2.24, 1.52, "UsageRecord", ["PK usage_id", "FK request_id", "issued · actual", "returned · abnormal"], CORAL, CORAL_LIGHT)
    entity_box(slide, 8.15, 4.60, 2.22, 1.52, "Disposal", ["PK disposal_id", "FK chemical_id", "waste · amount", "status · company"], PINK, WHITE)
    entity_box(slide, 11.05, 3.35, 1.62, 1.52, "Alert", ["PK alert_id", "FK chemical_id", "level · status", "created_at"], AMBER, AMBER_LIGHT)
    transition(slide, 2.90, 2.78, 8.05, 2.78, "1:N 申请", AMBER, 4.95, 2.54, 1.00)
    transition(slide, 6.52, 2.78, 8.05, 2.78, "1:N 批次", PURPLE, 6.68, 2.54, 0.92)
    transition(slide, 9.25, 3.62, 5.70, 4.60, "1:1 使用", TEAL, 7.00, 3.82, 0.92)
    transition(slide, 5.28, 3.62, 2.30, 4.60, "1:N 审批", BLUE, 3.10, 3.84, 0.92)
    transition(slide, 5.28, 3.62, 5.70, 4.60, "1:1 发放", CORAL, 5.24, 3.96, 0.92)
    transition(slide, 5.28, 3.62, 8.15, 4.60, "0..N 处置", PINK, 7.18, 4.00, 1.05)
    transition(slide, 10.47, 2.80, 11.05, 3.72, "1:N 预警", AMBER, 10.20, 3.08, 0.92)
    text(slide, "对应数据表：users · chemicals · procurements · requests · approval_records · usage_records · incidents · disposals · alerts · audit_logs", 0.82, 6.46, 11.8, 0.20, 9.5, MUTED, align=PP_ALIGN.CENTER)
    footer(slide, 10)

    # 11 State machine
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "10 / 需求分析建模", "状态转换图：状态、触发事件与异常分支", "状态决定下一步权限、库存行为和审计动作；每次转换都有明确触发事件。", 11)
    states = [("待采购", AMBER), ("采购中", BLUE), ("待验收", BLUE), ("已入库", TEAL), ("可领用", TEAL), ("待审批", AMBER), ("已复核", PURPLE), ("已发放", CORAL), ("使用中", PURPLE), ("已归还", TEAL), ("待处置", PINK), ("已处置", INK)]
    for i, (lab, color) in enumerate(states):
        row = 0 if i < 6 else 1
        col = i if i < 6 else i - 6
        x = 0.70 + col * 2.06
        y = 2.15 + row * 1.10
        box(slide, x, y, 1.54, 0.68, WHITE, LINE)
        box(slide, x, y, 1.54, 0.10, color, color, False)
        text(slide, lab, x + 0.07, y + 0.27, 1.40, 0.17, 10.5, INK, True, PP_ALIGN.CENTER)
        if col > 0:
            labels = ["采购申请", "采购完成", "到货验收", "入库登记", "提交申请"] if row == 0 else ["审批通过", "管理员复核", "办理发放", "实验开始", "归还登记"]
            transition(slide, x - 0.50, y + 0.34, x - 0.08, y + 0.34, labels[col - 1], TEAL if row == 0 else PURPLE, x - 1.32, y - 0.04, 0.78)
    # Cross-row and exception transition
    transition(slide, 5.25, 2.83, 0.70, 3.59, "进入审批链", AMBER, 5.26, 3.08, 0.92)
    box(slide, 0.78, 4.88, 12.0, 0.80, CORAL_LIGHT, CORAL_LIGHT)
    text(slide, "异常状态", 1.03, 5.12, 1.0, 0.20, 12, CORAL, True)
    text(slide, "已过期 / 冻结 · 库存不足 · 审批驳回 · 归还不一致 · 泄漏 / 存储异常", 2.12, 5.12, 5.6, 0.20, 10, INK)
    text(slide, "阻断领用", 8.08, 5.12, 0.78, 0.20, 10, CORAL, True)
    transition(slide, 8.85, 5.22, 9.70, 5.22, "生成预警", CORAL, 8.92, 4.88, 0.82)
    transition(slide, 10.55, 5.22, 12.10, 5.22, "上报 / 审计", CORAL, 10.63, 4.88, 0.92)
    footer(slide, 11)

    # 11 Screenshot overview
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "11 / 实现与演示", "运行总览：风险、库存、审批和生命周期在同一屏", "以下为 ChemTrack 前端实际运行界面截图；当前项目支持后端在线与演示数据模式两种展示路径。", 12)
    box(slide, 0.70, 2.05, 8.30, 4.45, WHITE, LINE)
    slide.shapes.add_picture(str(SCREEN), Inches(0.78), Inches(2.13), width=Inches(8.14), height=Inches(3.87))
    text(slide, "真实运行界面  /  运行总览", 0.95, 6.14, 3.0, 0.20, 9, TEAL, True)
    add_stat(slide, 9.35, 2.18, 1.54, "批次档案", "4", "已建档可追溯", TEAL)
    add_stat(slide, 11.05, 2.18, 1.54, "库存预警", "1", "低于安全线", AMBER)
    add_stat(slide, 9.35, 3.58, 1.54, "待审批", "1", "高风险需复核", CORAL)
    add_stat(slide, 11.05, 3.58, 1.54, "有效预警", "2", "建议今日处理", PINK)
    box(slide, 9.35, 5.10, 3.24, 1.20, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "截图可见的证据", 9.58, 5.32, 2.4, 0.20, 12, TEAL, True)
    text(slide, "侧栏导航 · 风险雷达 · 最近申请\n全生命周期步骤 · 角色切换 · 待办入口", 9.58, 5.66, 2.55, 0.43, 10, INK)
    footer(slide, 12)

    # 12 Screenshot crops
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "11 / 实现与演示", "界面证据：从“看见风险”到“留下记录”", "把同一份运行界面拆成三个操作证据区，便于在答辩中对应需求和验收口径。", 13)
    add_image_card(slide, SCREEN_TOP, 0.68, 2.10, 4.00, 3.45, "总览指标  /  批次、库存、审批、预警", TEAL)
    add_image_card(slide, SCREEN_BOTTOM, 4.82, 2.10, 4.00, 3.45, "风险雷达 + 最近申请  /  待办聚合", CORAL)
    add_image_card(slide, SCREEN_SIDE, 8.96, 2.10, 3.70, 3.45, "生命周期导航  /  统一入口", AMBER)
    box(slide, 0.80, 5.88, 11.85, 0.53, WHITE, LINE)
    text(slide, "页面 → REST API → 数据库表 → 审计记录：每一次操作都可以在链路上定位。", 1.00, 6.04, 11.4, 0.18, 13, INK, True, PP_ALIGN.CENTER)
    footer(slide, 13)

    # 13 Desktop release
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "12 / 双端交付", "Release 桌面端：把 Web 能力封装成可启动产品", "桌面端不是另一套业务逻辑，而是 WPF 壳 + WebView2 + 后端进程管理，共享同一套接口和数据。", 14)
    box(slide, 0.78, 2.15, 7.25, 3.85, WHITE, LINE)
    box(slide, 1.08, 2.45, 6.65, 3.20, RGBColor(236, 241, 239), LINE)
    text(slide, "ChemTrack 化危品管理平台", 1.32, 2.70, 4.3, 0.25, 13, INK, True)
    text(slide, "WPF Window", 6.05, 2.72, 1.2, 0.18, 9, MUTED, True, PP_ALIGN.RIGHT)
    slide.shapes.add_picture(str(SCREEN_TOP), Inches(1.32), Inches(3.18), width=Inches(6.18), height=Inches(2.15))
    line(slide, 8.75, 2.70, 8.75, 5.55, LINE, 1.0)
    add_bullet(slide, 9.18, 2.40, 3.1, "启动后端", "启动时检查 /api/health；未就绪则拉起 backend JAR。", TEAL)
    add_bullet(slide, 9.18, 3.55, 3.1, "加载界面", "EnsureCoreWebView2Async 后导航到本地服务。", BLUE)
    add_bullet(slide, 9.18, 4.70, 3.1, "退出回收", "窗口关闭时回收后端进程，减少遗留服务。", AMBER)
    box(slide, 0.80, 6.28, 11.85, 0.45, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "桌面端交付价值：降低课堂启动门槛，同时保留 Web 端持续迭代能力。", 1.0, 6.40, 11.4, 0.18, 11, TEAL, True, PP_ALIGN.CENTER)
    footer(slide, 14)

    # 14 Repository evidence
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "13 / 项目交付证据", "代码、数据、桌面端与文档统一沉淀在 GitHub 仓库", "仓库截图展示了 ChemTrack 的实际项目结构：系统实现与需求分析材料并行管理，便于协作、验收和后续迭代。", 15)
    box(slide, 0.68, 2.05, 8.15, 4.45, WHITE, LINE)
    slide.shapes.add_picture(str(GITHUB_SCREEN), Inches(0.76), Inches(2.13), width=Inches(7.99), height=Inches(3.79))
    text(slide, "GitHub 仓库实况  /  ChemTrack", 0.96, 6.14, 3.2, 0.20, 9, TEAL, True)
    box(slide, 9.22, 2.15, 3.36, 1.15, TEAL_LIGHT, TEAL_LIGHT)
    text(slide, "协作成果", 9.48, 2.38, 1.4, 0.21, 13, TEAL, True)
    text(slide, "代码、数据库脚本、桌面端和文档集中管理", 9.48, 2.75, 2.72, 0.30, 10, INK)
    box(slide, 9.22, 3.58, 3.36, 1.15, AMBER_LIGHT, AMBER_LIGHT)
    text(slide, "版本证据", 9.48, 3.81, 1.4, 0.21, 13, AMBER, True)
    text(slide, "分支、提交记录和协作者信息支撑过程可追溯", 9.48, 4.18, 2.72, 0.30, 10, INK)
    box(slide, 9.22, 5.01, 3.36, 1.15, CORAL_LIGHT, CORAL_LIGHT)
    text(slide, "交付价值", 9.48, 5.24, 1.4, 0.21, 13, CORAL, True)
    text(slide, "从课堂原型走向可共享、可复现的工程成果", 9.48, 5.61, 2.72, 0.30, 10, INK)
    footer(slide, 15)

    # 14 Demo evidence
    slide = prs.slides.add_slide(blank); set_bg(slide); section_header(slide, "14 / 课堂演示", "一条真实路径，证明需求可以落地", "每一步都能在前端页面、REST API、数据库表和审计记录中定位。", 16)
    rows = [
        ("01", "采购入库", "新建批次", "POST /procurements", "procurements", "状态推进"),
        ("02", "提交申请", "领用审批", "POST /requests", "requests", "申请待审批"),
        ("03", "教师审批", "分级审批", "PATCH /approve", "approval_records", "教师已审批"),
        ("04", "管理员复核", "高风险二次确认", "PATCH /approve", "approval_records", "可办理发放"),
        ("05", "办理发放", "出库扣减", "PATCH /issue", "usage_records", "库存变化"),
        ("06", "使用归还", "实际量与回补", "PATCH /return", "usage_records", "归还留痕"),
        ("07", "风险扫描", "库存 / 有效期", "POST /alerts/refresh", "alerts", "生成预警"),
        ("08", "查看审计", "证据汇总", "GET /audit", "audit_logs", "动作不可删除"),
    ]
    headers = [("序号", 0.82, 0.56), ("动作", 1.48, 1.42), ("页面能力", 2.90, 1.52), ("接口", 4.42, 2.28), ("数据对象", 6.70, 2.15), ("验收结果", 8.85, 3.50)]
    for h, x, w in headers:
        box(slide, x, 2.12, w, 0.43, INK, INK, False)
        text(slide, h, x + 0.05, 2.23, w - 0.10, 0.16, 9, WHITE, True, PP_ALIGN.CENTER)
    for i, row in enumerate(rows):
        y = 2.55 + i * 0.48
        fill = WHITE if i % 2 == 0 else RGBColor(242, 247, 244)
        values = [row[0], row[1], row[2], row[3], row[4], row[5]]
        for (val, (_, x, w)) in zip(values, headers):
            box(slide, x, y, w, 0.46, fill, LINE, False)
            text(slide, val, x + 0.06, y + 0.13, w - 0.12, 0.17, 8.5, INK if i % 2 == 0 else TEAL, i == 0 and val == row[0], PP_ALIGN.CENTER)
    box(slide, 9.05, 6.58, 3.55, 0.35, AMBER_LIGHT, AMBER_LIGHT)
    text(slide, "状态推进 + 库存变化 + 留痕", 9.10, 6.67, 3.45, 0.15, 9, AMBER, True, PP_ALIGN.CENTER)
    footer(slide, 16)

    # 16 conclusion
    slide = prs.slides.add_slide(blank); set_bg(slide, RGBColor(242, 248, 246))
    box(slide, 0.62, 0.62, 0.95, 0.30, TEAL, TEAL)
    text(slide, "FINAL CHECK", 0.70, 0.68, 0.79, 0.14, 8, WHITE, True, PP_ALIGN.CENTER)
    text(slide, "可行、可验收、可持续演进", 0.62, 1.36, 7.3, 0.62, 31, INK, True)
    text(slide, "ChemTrack 已具备课程设计所需的可运行 MVP，需求边界和演进路径清晰。", 0.66, 2.20, 7.4, 0.28, 13, MUTED)
    conclusions = [
        ("可行性", "技术与操作已验证，经济可控，社会价值明确；法律方向需制度复核。", TEAL),
        ("需求", "功能、性能、可靠性、可用性、异常、接口、约束、逆向与未来要求均有落点。", AMBER),
        ("实现", "Vue + Spring Boot + MySQL 与 DFD / ER / 状态模型保持一致。", CORAL),
    ]
    for i, (title_, body_, color) in enumerate(conclusions):
        x = 0.68 + i * 3.95
        box(slide, x, 3.18, 3.35, 1.56, WHITE, LINE)
        box(slide, x, 3.18, 3.35, 0.13, color, color, False)
        text(slide, f"0{i+1}", x + 0.20, 3.52, 0.43, 0.30, 22, color, True)
        text(slide, title_, x + 0.78, 3.56, 2.18, 0.22, 14, INK, True)
        text(slide, body_, x + 0.20, 4.05, 2.90, 0.45, 10, MUTED)
    box(slide, 0.68, 5.45, 11.72, 0.82, INK, INK)
    text(slide, "答辩检查句", 0.96, 5.68, 1.25, 0.20, 11, AMBER, True)
    text(slide, "每一个需求是否都有角色、状态、数据、接口和验收证据？", 2.44, 5.62, 9.55, 0.28, 18, WHITE, True)
    text(slide, "ChemTrack  /  Web × Desktop Release  /  2026.09", 0.68, 6.82, 6.0, 0.20, 9, TEAL, True)
    text(slide, "感谢聆听", 10.60, 6.75, 1.80, 0.32, 18, INK, True, PP_ALIGN.RIGHT)

    prs.save(OUTPUT)
    print("deck_written")


if __name__ == "__main__":
    build()
