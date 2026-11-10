#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成不超过 5 页的实验报告 PDF。"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

ROOT = Path(__file__).resolve().parent
OUT_PDF = ROOT / "实验报告.pdf"
FIG = ROOT / "figures"
GITHUB = "https://github.com/zwyzq/AI-Experiment2-Search"
# 若尚未建库，生成后请把上面的地址改成实际仓库 URL 并重新运行本脚本。

FONT_CANDIDATES = [
    # macOS
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0, 1),
    ("/System/Library/Fonts/PingFang.ttc", 0, 1),
    ("/Library/Fonts/Songti.ttc", 0, 1),
    # Linux (box)
    ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", None, None),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2, 3),
    ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 2, 3),
]


def register_fonts():
    last_err = None
    for path, idx, bold_idx in FONT_CANDIDATES:
        p = Path(path)
        if not p.exists():
            continue
        try:
            if path.endswith(".ttf"):
                pdfmetrics.registerFont(TTFont("CN", path))
                pdfmetrics.registerFont(TTFont("CNBold", path))
                return
            pdfmetrics.registerFont(TTFont("CN", path, subfontIndex=idx or 0))
            pdfmetrics.registerFont(TTFont("CNBold", path, subfontIndex=bold_idx if bold_idx is not None else (idx or 0)))
            return
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"未找到可用中文字体: {last_err}")


def styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=ss["Title"], fontName="CNBold", fontSize=15,
            leading=20, alignment=TA_CENTER, spaceAfter=3, textColor=colors.HexColor("#111111"),
        ),
        "meta": ParagraphStyle(
            "M", parent=ss["Normal"], fontName="CN", fontSize=10,
            leading=14, alignment=TA_CENTER, spaceAfter=1, textColor=colors.HexColor("#222222"),
        ),
        "h1": ParagraphStyle(
            "H1", parent=ss["Normal"], fontName="CNBold", fontSize=11,
            leading=15, textColor=colors.HexColor("#153A62"),
        ),
        "h2": ParagraphStyle(
            "H2", parent=ss["Normal"], fontName="CNBold", fontSize=10,
            leading=13, spaceBefore=4, spaceAfter=2, textColor=colors.HexColor("#1A365D"),
        ),
        "body": ParagraphStyle(
            "B", parent=ss["Normal"], fontName="CN", fontSize=9,
            leading=13, alignment=TA_LEFT, firstLineIndent=18, spaceAfter=2,
            textColor=colors.HexColor("#222222"),
        ),
        "body0": ParagraphStyle(
            "B0", parent=ss["Normal"], fontName="CN", fontSize=9,
            leading=13, alignment=TA_LEFT, firstLineIndent=0, spaceAfter=2,
            textColor=colors.HexColor("#222222"),
        ),
        "caption": ParagraphStyle(
            "C", parent=ss["Normal"], fontName="CN", fontSize=8,
            leading=10, alignment=TA_CENTER, spaceBefore=1, spaceAfter=3,
            textColor=colors.HexColor("#444444"),
        ),
        "footer": ParagraphStyle(
            "F", parent=ss["Normal"], fontName="CN", fontSize=8,
            leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#666666"),
        ),
        "cell": ParagraphStyle(
            "Cel", parent=ss["Normal"], fontName="CN", fontSize=8,
            leading=10.5, alignment=TA_CENTER, textColor=colors.HexColor("#222222"),
        ),
        "cell_l": ParagraphStyle(
            "CelL", parent=ss["Normal"], fontName="CN", fontSize=8,
            leading=10.5, alignment=TA_LEFT, textColor=colors.HexColor("#222222"),
        ),
        "cellb": ParagraphStyle(
            "CelB", parent=ss["Normal"], fontName="CNBold", fontSize=8,
            leading=10.5, alignment=TA_CENTER, textColor=colors.HexColor("#222222"),
        ),
    }


def P(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


ACCENT = colors.HexColor("#2B6CB0")
HEAD_BG = colors.HexColor("#E8F0F8")
ROW_ALT = colors.HexColor("#F7F9FC")
LINE = colors.HexColor("#B8C7D9")


def heading(text, s):
    bar = Table(
        [[P(text, s["h1"])]],
        colWidths=[17.4 * cm],
    )
    bar.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), HEAD_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return [Spacer(1, 6), bar, Spacer(1, 3)]


def make_table(data, col_widths):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
            ]
        )
    )
    return t


def img(name, width_cm, height_ratio=0.52):
    p = FIG / name
    if not p.exists():
        return Spacer(1, 1)
    w = width_cm * cm
    im = Image(str(p), width=w, height=w * height_ratio)
    im.hAlign = "CENTER"
    return im


def add_page_number(canvas, doc):
    canvas.saveState()
    page, total = canvas.getPageNumber(), doc.page_count
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(1.6 * cm, 13.5 * mm, A4[0] - 1.6 * cm, 13.5 * mm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(A4[0] / 2, 8 * mm, f"第 {page} 页 / 共 {total} 页")
    canvas.restoreState()


class CountedDoc(SimpleDocTemplate):
    page_count = 0

    def handle_documentBegin(self):
        super().handle_documentBegin()
        # first pass records page count via afterFlowable / build twice
        pass


def build_story(s):
    story = []
    story.append(P("当代人工智能实验课 · 实验二：搜索算法", s["title"]))
    story.append(P("姓名：钟尉　　学号：10245501461", s["meta"]))
    story.append(P(f"<b>GitHub 仓库：</b><font color='#1A56A0'>{GITHUB}</font>", s["meta"]))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceAfter=4))

    # 1
    story += heading("1. 实验目标与算法设计", s)
    story.append(P(
        "本实验实现 A* 搜索与 Alpha-Beta 剪枝，并完成迷宫寻路、加权地形、博弈树求值及宝藏分配综合题。"
        "所有官方样例均已复现。报告重点不在复述定义，而在对照实验：启发函数、搜索深度与访问顺序如何改变节点数和决策。",
        s["body"],
    ))
    story.append(P(
        "<b>A*</b> 的状态为网格坐标。优先队列按 <font face='Courier'>f=g+h</font> 弹出节点；"
        "<font face='Courier'>g</font> 为从起点累计的路径代价，<font face='Courier'>h</font> 为启发估计。"
        "四方向移动；发现更优 <font face='Courier'>g</font> 时允许重新入堆，以保证即使启发函数略不可采纳也能得到最优解。"
        "实验记录扩展节点数（真正弹出并展开的次数）。",
        s["body"],
    ))
    story.append(P(
        "<b>Minimax / Alpha-Beta</b> 从根节点（MAX）递归。MAX 取子节点最大值，MIN 取最小值；叶节点返回静态得分。"
        "Alpha-Beta 维护窗口 <font face='Courier'>[alpha, beta]</font>：MAX 在 <font face='Courier'>v &gt;= beta</font> 时剪枝，"
        "MIN 在 <font face='Courier'>v &lt;= alpha</font> 时剪枝。同一局面不同访问顺序不改变最终值，但会显著改变剪枝次数。",
        s["body"],
    ))

    # 2
    story += heading("2. 题目一：迷宫寻路", s)
    story.append(P(
        "单位代价、四方向、障碍为 X。启发函数采用曼哈顿距离，满足可采纳且一致，因此 A* 返回最短路。"
        "官方样例得到路径 "
        "<font face='Courier'>[(0,0),(0,1),(0,2),(1,2),(1,3),(1,4),(2,4),(3,4)]</font>，"
        "长度 7，与讲义一致。路径先沿首行绕开 (1,1) 处障碍，再下行至 E，没有迂回。",
        s["body"],
    ))
    story.append(P("2.1 启发函数对照", s["h2"]))
    story.append(
        make_table(
            [
                [P("<b>场景</b>", s["cellb"]), P("<b>h=0 扩展数</b>", s["cellb"]),
                 P("<b>曼哈顿扩展数</b>", s["cellb"]), P("<b>路径长度</b>", s["cellb"]),
                 P("<b>节点降幅</b>", s["cellb"])],
                [P("官方 5*5 迷宫", s["cell"]), P("17", s["cell"]), P("14", s["cell"]),
                 P("7", s["cell"]), P("17.6%", s["cell"])],
                [P("自设 15*15", s["cell"]), P("168", s["cell"]), P("117", s["cell"]),
                 P("28", s["cell"]), P("30.4%", s["cell"])],
                [P("自设 21*21", s["cell"]), P("317", s["cell"]), P("143", s["cell"]),
                 P("40", s["cell"]), P("54.9%", s["cell"])],
                [P("自设 31*31", s["cell"]), P("461", s["cell"]), P("310", s["cell"]),
                 P("60", s["cell"]), P("32.8%", s["cell"])],
            ],
            [3.6 * cm, 3.4 * cm, 3.6 * cm, 3.2 * cm, 3.6 * cm],
        )
    )
    story.append(Spacer(1, 3))
    story.append(img("p1_heuristic_nodes.png", 16.2, 0.48))
    story.append(P("图1　不同规模迷宫上，h=0 与曼哈顿距离的扩展节点数", s["caption"]))
    story.append(P(
        "h=0 时 A* 退化为 Dijkstra，需向四周均匀扩展；曼哈顿距离把搜索“拉向”终点，"
        "在官方小地图上只少扩 3 个节点，因为可达区域本身很小。"
        "自设带随机障碍的更大迷宫中，差距被放大：21*21 时曼哈顿扩展数约为 Dijkstra 的一半。"
        "降幅并非随规模单调上升（31*31 为 32.8%），说明障碍布局会改变启发函数的引导效率："
        "当最短路必须绕行时，h 对真实剩余代价的低估增多，需要扩展的节点也会增加。两条启发均得到相同路径长度，验证了可采纳性。",
        s["body"],
    ))

    # 3
    story += heading("3. 题目二：加权地形", s)
    story.append(P(
        "进入格子 B 的代价等于 B 的地形权值；讲义规定终点 E 的进入代价为 0。"
        "官方地图上 A* 给出路径 "
        "<font face='Courier'>(0,0)->(1,0)->(2,0)->(3,0)->(3,1)->(3,2)->(4,2)->(4,3)->(4,4)</font>，"
        "累计代价 1+1+1+1+1+1+1+0=<b>7</b>，与预期一致。"
        "该路径刻意避开权值为 8 的“沼泽”，宁可多走几步平原。",
        s["body"],
    ))
    story.append(P("3.1 启发函数可采纳性", s["h2"]))
    story.append(P(
        "若仍用普通曼哈顿距离 h=d，相当于假设每一步代价至少为 1。但最后一步进入 E 的代价是 0，"
        "当节点与 E 相邻时真实剩余代价为 0，而 h=1，<b>启发函数不再可采纳</b>。"
        "可采纳的修正是 h=max(0, d-1)*c_min（本图 c_min=1），即只估计到达 E 之前必须支付的正代价。"
        "对照结果：h=0 扩展 15 个节点；普通曼哈顿与“曼哈顿-1”均扩展 11 个节点，三者都得到最优代价 7。"
        "普通曼哈顿仍找到最优，是因为实现中允许更优 g 值重新入堆，不满足可采纳性时算法仍可能正确，只是失去“第一次弹出即为最优”的理论保证，最坏情况下还可能扩展更多节点。"
        "因此本实验默认采用可采纳的“曼哈顿-1”。",
        s["body"],
    ))

    # 4
    story += heading("4. 题目三：Alpha-Beta 剪枝", s)
    story.append(P(
        "按讲义从左至右求值：最底层 MAX 分别取 max(3,5)=5、max(6,9)=9、max(1,2)=2；"
        "上一层 MIN 取 min(5,9)=5 与 min(9,2)=2；根节点 MAX 取 max(5,2)=<b>5</b>，与预期一致。",
        s["body"],
    ))
    story.append(
        make_table(
            [
                [P("<b>树 / 顺序</b>", s["cellb"]), P("<b>方法</b>", s["cellb"]),
                 P("<b>访问节点</b>", s["cellb"]), P("<b>叶子</b>", s["cellb"]),
                 P("<b>剪枝次数</b>", s["cellb"]), P("<b>结果</b>", s["cellb"])],
                [P("官方树 · 从左到右", s["cell_l"]), P("Minimax", s["cell"]),
                 P("15", s["cell"]), P("8", s["cell"]), P("0", s["cell"]), P("5", s["cell"])],
                [P("官方树 · 从左到右", s["cell_l"]), P("Alpha-Beta", s["cell"]),
                 P("14", s["cell"]), P("7", s["cell"]), P("2", s["cell"]), P("5", s["cell"])],
                [P("官方树 · 叶最大值升序", s["cell_l"]), P("Alpha-Beta", s["cell"]),
                 P("11", s["cell"]), P("5", s["cell"]), P("2", s["cell"]), P("5", s["cell"])],
                [P("官方树 · 叶最大值降序", s["cell_l"]), P("Alpha-Beta", s["cell"]),
                 P("15", s["cell"]), P("8", s["cell"]), P("1", s["cell"]), P("5", s["cell"])],
                [P("随机树 深度5 分支3", s["cell_l"]), P("Minimax", s["cell"]),
                 P("364", s["cell"]), P("243", s["cell"]), P("0", s["cell"]), P("15", s["cell"])],
                [P("同上 · 原顺序", s["cell_l"]), P("Alpha-Beta", s["cell"]),
                 P("202", s["cell"]), P("119", s["cell"]), P("38", s["cell"]), P("15", s["cell"])],
            ],
            [4.6 * cm, 2.6 * cm, 2.4 * cm, 2.2 * cm, 2.4 * cm, 2.2 * cm],
        )
    )
    story.append(Spacer(1, 2))
    story.append(P(
        "官方树很小，从左到右时右分支第一个子树估值偏高，beta 无法立刻收紧，因此只少访问 1 个节点。"
        "把子节点按叶最大值<b>升序</b>排列后，MIN 更早遇到小值，窗口更快收缩，访问降至 11；反之降序几乎没有收益。"
        "这说明“看起来更优的大值优先”并不总对：顺序应让<b>当前行棋方尽早推出接近最终值的边界</b>。"
        "自设完整三叉树（243 片叶）上，Alpha-Beta 将访问量从 364 降到 202（约 44.5%），剪枝优势才稳定显现。",
        s["body"],
    ))
    row = Table(
        [[img("p3_order_nodes.png", 8.4, 0.52), img("p3_random_tree.png", 8.4, 0.52)]],
        colWidths=[8.7 * cm, 8.7 * cm],
    )
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(row)
    story.append(P("图2　官方树不同访问顺序的节点数（左）；随机大树上的剪枝效率（右）", s["caption"]))

    # 5
    story += heading("5. 题目四：竞争环境下的宝藏分配", s)
    story.append(P("5.1 距离矩阵与状态表示", s["h2"]))
    story.append(P(
        "用加权 A* 计算 A、B、T1-T4 两两之间的最小进入代价（起点不付费，A/B/T 所在格代价为 1）。"
        "矩阵对称，符合无向移动。A 到 T2 最近（代价 4），到 T1 最远（10）；B 到 T3 最近（4），到 T4 较远（10）。",
        s["body"],
    ))
    story.append(
        make_table(
            [
                [P(f"<b>{c}</b>", s["cellb"]) for c in ["", "A", "B", "T1", "T2", "T3", "T4"]],
                [P("A", s["cellb"]), P("0", s["cell"]), P("12", s["cell"]), P("10", s["cell"]),
                 P("4", s["cell"]), P("8", s["cell"]), P("8", s["cell"])],
                [P("B", s["cellb"]), P("12", s["cell"]), P("0", s["cell"]), P("8", s["cell"]),
                 P("8", s["cell"]), P("4", s["cell"]), P("10", s["cell"])],
                [P("T1", s["cellb"]), P("10", s["cell"]), P("8", s["cell"]), P("0", s["cell"]),
                 P("6", s["cell"]), P("6", s["cell"]), P("12", s["cell"])],
                [P("T2", s["cellb"]), P("4", s["cell"]), P("8", s["cell"]), P("6", s["cell"]),
                 P("0", s["cell"]), P("6", s["cell"]), P("6", s["cell"])],
                [P("T3", s["cellb"]), P("8", s["cell"]), P("4", s["cell"]), P("6", s["cell"]),
                 P("6", s["cell"]), P("0", s["cell"]), P("6", s["cell"])],
                [P("T4", s["cellb"]), P("8", s["cell"]), P("10", s["cell"]), P("12", s["cell"]),
                 P("6", s["cell"]), P("6", s["cell"]), P("0", s["cell"])],
            ],
            [2.2 * cm] + [2.5 * cm] * 6,
        )
    )
    story.append(P("表　A、B 与四座宝藏的 6*6 最短代价矩阵", s["caption"]))
    story.append(P(
        "博弈状态记录：双方当前位置（用标签表示）、剩余宝藏集合、累计得分、当前行动者。"
        "选择宝藏 T_i 时，Gain=V_i - d(p, T_i)，玩家移动到该宝藏，位置更新。"
        "到达深度上限或宝藏取完时，以 U = Score_A - Score_B 作为评价值。"
        "A 的即时首步收益为：T1/T3/T4 均为 -1，仅 T2 为 +2（6-4）。若只看一步，似乎应抢 T2。",
        s["body"],
    ))

    story.append(P("5.2 深度 H=2 与 H=4 的决策差异", s["h2"]))
    story.append(
        make_table(
            [
                [P("<b>A 的首步</b>", s["cellb"]), P("<b>即时收益</b>", s["cellb"]),
                 P("<b>H=2 的 U</b>", s["cellb"]), P("<b>H=2 时 B 应对</b>", s["cellb"]),
                 P("<b>H=4 的 U</b>", s["cellb"]), P("<b>H=4 时 B 应对</b>", s["cellb"])],
                [P("T1", s["cell"]), P("-1", s["cell"]), P("-4", s["cell"]), P("T3", s["cell"]),
                 P("-5", s["cell"]), P("T3", s["cell"])],
                [P("T2", s["cell"]), P("+2", s["cell"]), P("<b>-1（最优）</b>", s["cell"]), P("T3", s["cell"]),
                 P("1", s["cell"]), P("T3", s["cell"])],
                [P("T3", s["cell"]), P("-1", s["cell"]), P("-2", s["cell"]), P("T1", s["cell"]),
                 P("<b>3（最优）</b>", s["cell"]), P("T1", s["cell"])],
                [P("T4", s["cell"]), P("-1", s["cell"]), P("-4", s["cell"]), P("T3", s["cell"]),
                 P("-7", s["cell"]), P("T3", s["cell"])],
            ],
            [2.6 * cm, 2.6 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 3.2 * cm],
        )
    )
    story.append(Spacer(1, 3))
    row = Table(
        [[img("p4_first_moves.png", 8.4, 0.52), img("p4_search_nodes.png", 8.4, 0.52)]],
        colWidths=[8.7 * cm, 8.7 * cm],
    )
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(row)
    story.append(P("图3　各首步在 H=2/H=4 下的最优 U（左）；H=4 时搜索方法与顺序的节点数（右）", s["caption"]))
    story.append(P(
        "<b>H=2</b> 只向下看两步（A 再 B），剩余两座宝藏不进入估值。A 取 T2（+2）后，B 会取离自己更近的 T3（7-4=+3），"
        "U=2-3=<b>-1</b>。若 A 改取 T3（-1），B 取 T1（+1），U=-2，反而更差。所以浅层搜索的最优首步是 T2。"
        "<b>H=4</b> 能看完整四回合。最优主变例为：A 取 T3（-1），B 取 T1（+1），A 再取 T2（6-6=0），B 只剩 T4（7-12=-5），"
        "最终 Score_A=-1、Score_B=-4，U=<b>3</b>。"
        "若 A 仍按浅层策略开局 T2，后续为 B-T3、A-T1、B-T4，U 仅为 1，劣于 3。",
        s["body"],
    ))
    story.append(P(
        "差异的关键是 <b>T3 对 B 的战略价值</b>：T3 距 B 只有 4，B 的即时收益高达 +3。"
        "H=2 看不见“抢走 T3 之后，B 将被赶到远处的 T4 并付出负收益”；"
        "H=4 则允许 A 用一步看似吃亏的抢夺，换取后手把 B 的总分压到 -4。"
        "这是有限深度截断造成的典型短视，也说明综合题必须把搜索深度与终局估值一起讨论，而不能只比较首步即时 Gain。",
        s["body"],
    ))

    story.append(P("5.3 剪枝与访问顺序", s["h2"]))
    story.append(P(
        "H=4 时 Minimax 无论顺序都访问 65 个节点（完整博弈树固定）。"
        "Alpha-Beta 在自然顺序（T1-T4）下访问 47，逆序 46；按当前玩家<b>即时收益降序</b>排序后进一步降至 <b>37</b>（约减少 43%），"
        "升序则几乎不剪枝（63，接近未剪枝）。"
        "收益降序往往让 MAX 先走出高 U 分支、MIN 先走出低 U 分支，从而更快抬高 alpha 或压低 beta。"
        "H=2、H=4 在所有顺序下得到相同的最优首步与 U，说明剪枝只影响开销，不影响正确性。",
        s["body"],
    ))

    # 6
    story += heading("6. 自设对照、结论与局限", s)
    story.append(P(
        "除官方样例外，本实验还设置了三组对照：（1）随机障碍迷宫，观察规模与绕行对启发函数增益的影响；"
        "（2）完整三叉随机博弈树，避免官方树过小导致“剪枝几乎无用”的误判；"
        "（3）综合题中以即时收益排序作为移动排序启发式，验证“好顺序”可在不改结果的前提下再节省约两成节点。"
        "这些对照表明：算法改进是否可见，高度依赖实例规模与分支结构，不能只依据单个官方样例下结论。",
        s["body"],
    ))
    story.append(P(
        "结论：A* 在单位代价网格上用曼哈顿距离即可稳定求最短路，规模越大相对 Dijkstra 的节点优势通常越明显；"
        "加权且规定 E 代价为 0 时，必须修正启发函数以保持可采纳。"
        "Alpha-Beta 的收益随树深与分支因子增大而显现，且强烈依赖访问顺序。"
        "综合题中，H=2 选择 T2（U=-1）、H=4 选择 T3（U=3），差异来自能否预见“抢走对方高效宝藏”的长期效果。",
        s["body"],
    ))
    story.append(P(
        "局限：未实现一致性启发下的 closed 集严格优化与双向 A*；博弈搜索未加入置换表与迭代加深；"
        "综合题的估值在非终局深度直接使用当前 U，没有启发性终局估计。"
        "后续可尝试更紧的加权启发、历史启发排序或对截断局面做一步期望估值。",
        s["body"],
    ))
    story.append(Spacer(1, 4))
    story.append(P(
        "实验环境：Python 3 / 标准库 heapq；对照实验随机种子 42。完整代码与复现说明见 GitHub 仓库。",
        s["footer"],
    ))
    return story


def build():
    register_fonts()
    s = styles()
    story = build_story(s)

    # 先空跑统计页数
    class _Doc(SimpleDocTemplate):
        pass

    page_count = {"n": 0}

    def _count(canvas, doc):
        page_count["n"] = max(page_count["n"], canvas.getPageNumber())

    tmp = ROOT / "_tmp_count.pdf"
    doc1 = SimpleDocTemplate(
        str(tmp),
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.7 * cm,
        title="实验二：搜索算法 - 钟尉",
        author="钟尉",
    )
    doc1.build(story, onFirstPage=_count, onLaterPages=_count)
    total = page_count["n"]

    # 正式输出
    story = build_story(s)

    class Doc(SimpleDocTemplate):
        page_count = total

    doc = Doc(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.7 * cm,
        title="实验二：搜索算法 - 钟尉",
        author="钟尉",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    if tmp.exists():
        tmp.unlink()
    print(f"Wrote {OUT_PDF}  pages={total}")
    if total > 5:
        raise SystemExit(f"ERROR: report has {total} pages, must be <= 5")


if __name__ == "__main__":
    build()
