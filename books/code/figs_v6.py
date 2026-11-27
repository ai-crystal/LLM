# -*- coding: utf-8 -*-
"""《大模型技术全景 · 安全与攻破篇》（第六卷）插图。

运行：
    python books/code/figs_v6.py          # 全部重画
    python books/code/figs_v6.py 03       # 只画指定编号

输出：
    books/v6-safety/images/03/search_loop.png
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.colors import to_rgb

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L, RED,
                      TEAL, arrow, box, plt, setup)

# 雅黑在小字号下比 Noto Sans SC 清晰，缩到 130 mm 后仍实。
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v6-safety" / "images"

W = 5.2                    # 画布宽 5.2 in ≈ 132 mm
DPI = 288
FS = 8.5
FS_S = 7.0


def canvas(h_in: float):
    """固定宽度画布，1 单位 = 0.5 in。"""
    setup()
    fig = plt.figure(figsize=(W, h_in))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 2 * W)
    ax.set_ylim(0, 2 * h_in)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.grid(False)
    return fig, ax


def tint(color, f):
    r, g, b = to_rgb(color)
    return (1 - f + r * f, 1 - f + g * f, 1 - f + b * f)


def txt(ax, x, y, s, fs=FS, color=INK, ha="center", va="center",
        weight="normal", z=8):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, zorder=z, linespacing=1.4)


def note(ax, x, y, s, fs=FS_S, color=GRAY, ha="center", va="center", **kw):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   zorder=8, linespacing=1.45, **kw)


def save(fig, rel: str):
    dst = OUTDIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image
    with Image.open(dst) as im:
        im.convert("RGB").save(dst, dpi=(DPI, DPI))
        print(f"saved {dst.relative_to(ROOT)}  {im.width}×{im.height} px")


# ---------------------------------------------------------------- 03 三条搜索回路

def fig_03_search_loop():
    """第 3 章：三种自动化攻击，反馈信号接在哪里。"""
    fig, ax = canvas(4.55)

    rows = [
        ("GCG", "白盒",
         ["后缀 s", "算梯度取候选", "逐个试、留最优"],
         "反馈取自模型内部：损失可微，一次前向几十毫秒",
         NAVY, 7.90),
        ("PAIR", "黑盒",
         ["攻击者模型", "目标模型", "判定器"],
         "反馈是判定器给的成败标签：粗，但只要有 API 就能跑",
         TEAL, 5.60),
        ("AutoDAN", "黑盒",
         ["初始模板群", "变异与交叉", "按得分选择"],
         "反馈是适应度打分，同时要求提示读起来像人话",
         GOLD, 3.30),
    ]

    bw, bh = 2.35, 0.86
    xs = [2.45, 5.05, 7.65]
    for name, kind, steps, fb, color, y in rows:
        txt(ax, 0.62, y + bh / 2 + 0.19, name, fs=FS + 0.2, color=color,
            ha="left", weight="bold")
        note(ax, 0.62, y + bh / 2 - 0.20, kind, fs=FS_S, ha="left")
        ax.add_patch(plt.Rectangle((0.40, y), 0.055, bh,
                                   facecolor=color, edgecolor="none", zorder=3))

        for s, x in zip(steps, xs):
            box(ax, x, y, bw, bh, "", fc=tint(color, 0.10), ec=color, lw=0.9)
            txt(ax, x + bw / 2, y + bh / 2, s, fs=FS - 0.7)
        for i in range(2):
            arrow(ax, (xs[i] + bw + 0.02, y + bh / 2),
                  (xs[i + 1] - 0.02, y + bh / 2), lw=1.0, color=color)

        # 回路：从最后一格底部绕回第一格底部
        x_from = xs[2] + bw / 2
        x_to = xs[0] + bw / 2
        yb = y - 0.34
        ax.add_line(plt.Line2D([x_from, x_from], [y, yb], color=color, lw=0.9,
                               zorder=2))
        ax.add_line(plt.Line2D([x_from, x_to], [yb, yb], color=color, lw=0.9,
                               zorder=2))
        arrow(ax, (x_to, yb), (x_to, y), color=color, lw=0.9)
        note(ax, 5.55, yb - 0.30, fb, fs=FS_S, color=GRAY)

    note(ax, 5.55, 2.10,
         "回路每转一圈就要多一次前向或一次调用，预算直接决定成功率", fs=FS_S)
    txt(ax, 5.55, 1.55, "白盒的“试”便宜，黑盒的“试”要钱；所以黑盒方法更依赖判定器给方向",
        fs=FS - 1.0, color=INK)
    note(ax, 5.55, 0.95,
         "PAIR 一条链走到黑，TAP 同时铺开几支再剪枝——用查询数换成功率", fs=FS_S)

    save(fig, "03/search_loop.png")


# ---------------------------------------------------------------- 04 双模型架构

def fig_04_dual_model():
    """第 4 章：读内容的模型不能行动，行动的模型看不到原文。"""
    fig, ax = canvas(2.95)

    # 上行：不可信内容 -> 读取器 -> 结构化字段
    box(ax, 0.50, 3.95, 2.40, 1.30, "", fc=tint(NAVY_L, 0.10), ec=NAVY_L)
    txt(ax, 1.70, 4.94, "不可信内容", fs=FS - 0.4)
    note(ax, 1.70, 4.40, "网页 / 邮件 / 工单\n工具返回 / 代码注释", fs=FS_S)

    box(ax, 3.55, 3.95, 2.45, 1.30, "", fc=tint(NAVY, 0.08), ec=NAVY)
    txt(ax, 4.78, 4.98, "读取器", fs=FS - 0.2, weight="bold")
    note(ax, 4.78, 4.38, "只做抽取，工具全部禁用\n被骗也做不了事", fs=FS_S)

    box(ax, 6.65, 3.95, 3.10, 1.30, "", fc=tint(GOLD, 0.10), ec=GOLD)
    txt(ax, 8.20, 4.92, "结构化字段", fs=FS - 0.4)
    note(ax, 8.20, 4.34, "标题 / 单号 / 摘要\n是否包含请求（布尔）", fs=FS_S)

    arrow(ax, (2.92, 4.60), (3.53, 4.60), lw=1.0, color=NAVY)
    arrow(ax, (6.02, 4.60), (6.63, 4.60), lw=1.0, color=GOLD)

    # 下行：用户原话 + 字段 -> 决策器 -> 执行
    box(ax, 0.50, 1.55, 2.40, 1.10, "", fc=BG, ec=GRAY)
    txt(ax, 1.70, 2.38, "用户原话", fs=FS - 0.4)
    note(ax, 1.70, 1.92, "唯一可信的指令来源", fs=FS_S)

    box(ax, 3.55, 1.45, 2.95, 1.30, "", fc=tint(TEAL, 0.09), ec=TEAL)
    txt(ax, 5.02, 2.42, "决策器", fs=FS - 0.2, weight="bold")
    note(ax, 5.02, 1.90, "只看字段与用户原话\n拥有工具权限", fs=FS_S)

    box(ax, 7.75, 1.55, 2.00, 1.10, "", fc=BG, ec=GRAY)
    txt(ax, 8.75, 2.38, "执行", fs=FS - 0.4)
    note(ax, 8.75, 1.92, "工具调用 / 回答", fs=FS_S)

    arrow(ax, (2.92, 2.10), (3.53, 2.10), lw=1.0, color=GRAY)
    arrow(ax, (6.52, 2.10), (7.73, 2.10), lw=1.0, color=TEAL)

    # 字段下行进入决策器
    ax.add_line(plt.Line2D([6.90, 6.90], [3.95, 3.05], color=GOLD, lw=1.0, zorder=2))
    ax.add_line(plt.Line2D([6.90, 6.55], [3.05, 3.05], color=GOLD, lw=1.0, zorder=2))
    arrow(ax, (6.55, 3.05), (6.55, 2.77), color=GOLD, lw=1.0)

    note(ax, 5.20, 0.88,
         "原始文本进不了决策器：注入最多变成摘要里的半句话，且拿不到工具", fs=FS_S)
    note(ax, 5.20, 0.40,
         "代价是信息损失——代码审查、合同比对这类任务需要原文，用不了这套", fs=FS_S)

    save(fig, "04/dual_model.png")


# ---------------------------------------------------------------- 04 外泄通道

def fig_04_exfil():
    """第 4 章：一条字符串出去的路不止一条，每类通道配一个闸门。"""
    fig, ax = canvas(2.06)

    box(ax, 0.35, 1.35, 1.95, 2.05, "", fc=tint(NAVY, 0.08), ec=NAVY)
    txt(ax, 1.32, 3.00, "模型输出", fs=FS - 0.2, weight="bold")
    note(ax, 1.32, 2.50, "一段字符串\n几百到两千字符", fs=FS_S)
    note(ax, 1.32, 1.80, "真正发请求的\n往往是别的组件", fs=FS_S, color=RED)

    rows = [
        ("Markdown 图片", "前端渲染即发请求", "渲染走代理，只放行白名单", 3.40),
        ("链接与预览", "服务端替用户去访问", "关掉服务端预览", 2.80),
        ("工具参数", "数据不进回答，进参数", "参数 schema 只许枚举", 2.20),
        ("文件名与路径", "同步盘或后续流程读取", "写盘目录受控", 1.60),
        ("子域名", "数据编码进域名前缀", "出站日志记全量 URL", 1.00),
    ]

    for name, how, gate, y in rows:
        box(ax, 2.50, y, 1.95, 0.50, "", fc="white", ec=NAVY_L, lw=0.8)
        txt(ax, 3.47, y + 0.25, name, fs=FS - 1.4)
        arrow(ax, (2.30, y + 0.25), (2.48, y + 0.25), lw=0.9, color=NAVY_L)

        box(ax, 4.75, y, 2.75, 0.50, "", fc=tint(GREEN, 0.10), ec=GREEN, lw=0.8)
        txt(ax, 6.12, y + 0.25, gate, fs=FS - 1.4)
        arrow(ax, (4.47, y + 0.25), (4.73, y + 0.25), lw=0.9, color=GRAY)

        note(ax, 7.58, y + 0.25, how, fs=FS_S, ha="left")

    ax.add_patch(plt.Rectangle((9.95, 0.92), 0.05, 3.00, facecolor=RED,
                               edgecolor="none", zorder=3))
    ax.text(10.16, 2.42, "外网", fontsize=FS - 0.8, color=RED, rotation=90,
            ha="center", va="center", zorder=8)

    note(ax, 4.90, 0.55, "五个闸门里关掉任意两个，一条外泄链就断了；只关一个通常不够", fs=FS_S)
    note(ax, 4.90, 0.18, "排查顺序：先问“谁会替这段字符串发请求”，再问“那道门有没有配”", fs=FS_S)

    save(fig, "04/exfil_channels.png")


# ---------------------------------------------------------------- 05 窄带

def fig_05_narrow_band():
    """第 5 章：对齐只改了请求空间里很窄的一段。"""
    fig, ax = canvas(1.80)

    def strip(y, label, seg_label, seg_color, seg_tint, note_text):
        box(ax, 2.55, y, 5.35, 0.62, "", fc=BG, ec=LGRAY, lw=0.8)
        txt(ax, 5.22, y + 0.31, "绝大多数请求：照常回答", fs=FS - 1.0, color=GRAY)
        box(ax, 8.05, y, 1.25, 0.62, "", fc=seg_tint, ec=seg_color, lw=0.9)
        txt(ax, 8.67, y + 0.31, seg_label, fs=FS - 1.0, color=seg_color)
        txt(ax, 2.40, y + 0.31, label, fs=FS - 1.0, ha="right", weight="bold")
        note(ax, 8.67, y - 0.32, note_text, fs=FS_S)

    strip(2.28, "对齐之后", "拒绝", RED, tint(RED, 0.14), "拒答率被抬起来")
    strip(1.00, "再微调 200 条", "照做", GOLD, tint(GOLD, 0.16), "同一小段被压回去")

    ax.add_line(plt.Line2D([9.55, 9.55], [1.00, 1.62], color=GRAY, lw=0.7,
                           linestyle=(0, (2, 2))))
    ax.add_line(plt.Line2D([9.55, 9.55], [2.28, 2.90], color=GRAY, lw=0.7,
                           linestyle=(0, (2, 2))))
    ax.text(9.80, 1.95, "同一段", fontsize=FS_S, color=GRAY, rotation=90,
            ha="center", va="center")

    note(ax, 5.20, 0.28,
         "改动量很小，一张消费级卡一小时就够；通用能力几乎不变，所以没人察觉", fs=FS_S)

    save(fig, "05/narrow_band.png")


# ---------------------------------------------------------------- 08 防御栈

def fig_10_defense_stack():
    """第 10 章：四层防御的失效方式各不相同，才构成冗余。"""
    fig, ax = canvas(2.55)

    rows = [
        ("训练层", NAVY, "让模型倾向拒绝：SFT、对抗训练、拒绝方向",
         "被人微调覆盖"),
        ("推理层", TEAL, "输入输出分类器、改写、困惑度过滤",
         "像正常文本的攻击"),
        ("系统层", GOLD, "最小权限、出站白名单、金额上限、二次确认",
         "内部人与供应链"),
        ("监控层", RED, "行为基线、告警、审计日志",
         "第一次发生的事"),
    ]

    ys = [3.70, 2.75, 1.80, 0.85]
    for (name, color, does, blind), y in zip(rows, ys):
        box(ax, 0.95, y, 1.55, 0.78, "", fc=tint(color, 0.12), ec=color, lw=0.9)
        txt(ax, 1.72, y + 0.39, name, fs=FS - 0.4, color=INK, weight="bold")

        box(ax, 2.65, y, 4.40, 0.78, "", fc="white", ec=LGRAY, lw=0.8)
        txt(ax, 4.85, y + 0.39, does, fs=FS - 1.7)

        box(ax, 7.15, y, 2.85, 0.78, "", fc=tint(RED, 0.06), ec=LGRAY, lw=0.8)
        note(ax, 8.57, y + 0.39, "管不了：" + blind, fs=FS_S, color=GRAY)

    arrow(ax, (0.55, 4.55), (0.55, 0.68), color=GRAY, lw=1.2)
    ax.text(0.28, 2.60, "一次注入请求", fontsize=FS_S, color=GRAY, rotation=90,
            ha="center", va="center")

    note(ax, 5.25, 0.34,
         "四层的失效方式不同，才构成冗余；失效方式相同的多层，只是重复", fs=FS_S)

    save(fig, "10/defense_stack.png")


# ---------------------------------------------------------------- 10 三个通道

def fig_12_modalities():
    """第 12 章：多一层解析，就多一个检查点该放哪的问题。"""
    fig, ax = canvas(2.38)

    rows = [
        ("图像", NAVY, "商品图 / 截图 / 发票", "编码器 + OCR",
         "像素变成 token", 3.62),
        ("语音", TEAL, "录音 / 客服电话", "转写 + 说话人分离",
         "对话上下文", 2.22),
        ("代码", GOLD, "仓库 / issue / CI 日志", "文件解析 + 检索",
         "上下文 + 可执行", 0.82),
    ]

    bw, bh = 1.95, 0.85
    for name, color, src, parse, out, y in rows:
        txt(ax, 0.55, y + bh / 2 + 0.15, name, fs=FS, color=color,
            ha="left", weight="bold")
        ax.add_patch(plt.Rectangle((0.42, y), 0.055, bh, facecolor=color,
                                   edgecolor="none", zorder=3))

        box(ax, 1.95, y, bw, bh, "", fc="white", ec=LGRAY, lw=0.8)
        txt(ax, 2.92, y + bh / 2, src, fs=FS - 1.7)

        box(ax, 4.25, y, bw + 0.25, bh, "", fc=tint(color, 0.10), ec=color, lw=0.9)
        txt(ax, 5.32, y + bh / 2, parse, fs=FS - 1.5)

        box(ax, 6.95, y, 2.15, bh, "", fc=BG, ec=LGRAY, lw=0.8)
        txt(ax, 8.02, y + bh / 2, out, fs=FS - 1.5)

        arrow(ax, (3.92, y + bh / 2), (4.23, y + bh / 2), lw=0.9, color=GRAY)
        arrow(ax, (6.47, y + bh / 2), (6.93, y + bh / 2), lw=0.9, color=GREEN)

    # 审核关口画在“解析之后、进上下文之前”
    ax.add_line(plt.Line2D([6.70, 6.70], [0.70, 4.50], color=GREEN, lw=1.6,
                           linestyle=(0, (4, 2)), zorder=4))

    note(ax, 5.40, 0.36,
         "三层解析最后都汇成一段文本；审核要点应该在绿色关口，而不是文件上传的入口", fs=FS_S)

    save(fig, "12/modalities.png")


# ---------------------------------------------------------------- 01 攻击面地图

def fig_01_attack_surface():
    """第 1 章：六个可下手的面，以及每个面需要什么权限。"""
    fig, ax = canvas(3.45)

    rows = [
        ("① 输入", NAVY, "越狱、注入、超长、坏格式",
         "任何能发请求的人", 5.80),
        ("② 周边数据", TEAL, "检索库 / 工具返回 / 网页",
         "能往这份内容里写字的人", 4.85),
        ("③ 模型本体", GOLD, "微调、消融、权重投毒",
         "有训练或权重权限的人", 3.90),
        ("④ 工具与权限", RED, "越权调用、往外发参数",
         "集成方，而且常常给多", 2.95),
        ("⑤ 输出", GREEN, "外泄、包装成结论的错误",
         "会替这串字符发请求的组件", 2.00),
        ("⑥ 系统边界", NAVY_L, "计费、限流、日志、审计",
         "运维与账号体系", 1.05),
    ]

    for name, color, what, who, y in rows:
        ax.add_patch(plt.Rectangle((0.35, y), 0.05, 0.75, facecolor=color,
                                   edgecolor="none", zorder=3))
        txt(ax, 0.52, y + 0.375, name, fs=FS - 1.0, ha="left", weight="bold")
        box(ax, 1.72, y, 3.60, 0.75, "", fc="white", ec=LGRAY, lw=0.8)
        txt(ax, 3.52, y + 0.375, what, fs=FS - 1.7)
        box(ax, 5.55, y, 4.35, 0.75, "", fc=tint(color, 0.09), ec=color, lw=0.8)
        note(ax, 7.72, y + 0.375, who, fs=FS_S, color=GRAY)

    box(ax, 0.35, 0.28, 9.55, 0.58, "", fc=tint(RED, 0.07), ec=RED, lw=0.8)
    txt(ax, 5.12, 0.57,
        "一条链串三层：② 网页里写一句 → ④ 模型读到并调工具 → ⑤ 前端渲染图片把数据带走",
        fs=FS - 1.5, color=INK)

    save(fig, "01/attack_surface.png")


# ---------------------------------------------------------------- 02 模板衰减

def _frame(ax, x0, y0, w, h, ymax, yticks, xlabels, xlabel, ylabel):
    """在固定画布里画一个带刻度线的坐标系（不借助 matplotlib 的 axes）。"""
    ax.plot([x0, x0 + w], [y0, y0], color=GRAY, lw=0.9, zorder=2)
    ax.plot([x0, x0], [y0, y0 + h], color=GRAY, lw=0.9, zorder=2)
    for v in yticks:
        y = y0 + v / ymax * h
        ax.plot([x0, x0 + w], [y, y], color=LGRAY, lw=0.6, zorder=1)
        ax.plot([x0 - 0.10, x0], [y, y], color=GRAY, lw=0.7, zorder=2)
        note(ax, x0 - 0.22, y, f"{v:g}", fs=FS_S, ha="right")
    n = len(xlabels)
    for i, s in enumerate(xlabels):
        x = x0 + (i / (n - 1)) * w if n > 1 else x0
        ax.plot([x, x], [y0, y0 - 0.10], color=GRAY, lw=0.7, zorder=2)
        note(ax, x, y0 - 0.34, s, fs=FS_S)
    note(ax, x0 + w / 2, y0 - 0.72, xlabel, fs=FS_S)
    ax.text(x0 - 1.05, y0 + h / 2, ylabel, fontsize=FS_S, color=GRAY,
            rotation=90, ha="center", va="center", zorder=8)
    return (lambda xv, i, k: x0 + xv / (k - 1) * w), (lambda v: y0 + v / ymax * h)


def fig_02_template_decay():
    """第 2 章：同一套模板随模型版本衰减，衰减率决定手法的寿命。"""
    fig, ax = canvas(3.35)

    X, Y = _frame(ax, 1.55, 1.70, 6.40, 3.55, 45,
                  [0, 15, 30, 45], ["0", "1", "2", "3", "4", "5"],
                  "模型更新次数（次）", "同一模板的成功率（%）")

    ks = 6
    curves = [
        ("原样照抄", 42, 0.60, RED),
        ("换场景、换语言", 42, 0.75, GOLD),
        ("只留手法，重新实现", 40, 0.98, NAVY),
    ]
    for label, p0, g, color in curves:
        pts = [(X(t, 0, ks), Y(p0 * g ** t)) for t in range(ks)]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color,
                lw=1.5, zorder=4, marker="o", ms=2.6)
        ex, ey = pts[-1]
        txt(ax, ex + 0.16, ey, label, fs=FS_S - 0.4, color=color, ha="left")

    note(ax, 1.55, 0.66,
         "曲线按 p·γ^t 算：p 取公开报告同一量级（四成上下），γ 是每轮安全数据清洗后的残留比例",
         fs=FS_S, ha="left")
    note(ax, 1.55, 0.36,
         "γ=0.60 时五轮后只剩 3%，γ=0.98 时几乎不掉；差别不在模板，在背后是不是可重新实现的手法",
         fs=FS_S, ha="left")

    save(fig, "02/template_decay.png")


# ---------------------------------------------------------------- 03 查询预算

def fig_03_budget_asr():
    """第 3 章：查询预算换成成功率，三条路的曲线形状不同。"""
    fig, ax = canvas(3.35)

    X, Y = _frame(ax, 1.70, 1.70, 7.10, 3.55, 100,
                  [0, 25, 50, 75, 100], ["1", "10", "100", "1000"],
                  "每条请求的查询预算（次，对数轴）", "成功率（%）")

    import math

    budgets = [1, 2, 3, 5, 8, 12, 20, 30, 50, 80, 120, 200, 350, 600, 1000]
    curves = [
        ("GCG（白盒）", 90, 130.0, NAVY),
        ("TAP（多分支）", 78, 28.0, TEAL),
        ("PAIR（单链）", 66, 9.0, GOLD),
    ]
    for label, A, tau, color in curves:
        pts = [(X(math.log10(b), 0, 4), Y(A * (1 - math.exp(-b / tau))))
               for b in budgets]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color,
                lw=1.5, zorder=4, marker="o", ms=2.2)

    # 图例放在右下角的空白区（三条曲线在高预算区都已经爬到上方）
    for i, (label, A, tau, color) in enumerate(curves):
        yy = 2.42 - i * 0.32
        ax.plot([5.45, 5.82], [yy, yy], color=color, lw=1.5, zorder=5)
        txt(ax, 5.92, yy, label, fs=FS_S, ha="left", color=color)

    xb = X(math.log10(30), 0, 4)
    ax.plot([xb, xb], [1.70, 1.70 + 3.55 * 0.80], color=RED, lw=0.8,
            ls=(0, (3, 2)), zorder=3)
    note(ax, xb - 0.14, 4.78, "30 次：常见预算上限", fs=FS_S,
         ha="right", color=RED)

    note(ax, 1.70, 0.66,
         "三条曲线都按 A·(1−e^(−b/τ)) 拟合：GCG 的 A=90/τ=130，TAP 78/28，PAIR 66/9",
         fs=FS_S, ha="left")
    note(ax, 1.70, 0.36,
         "预算翻十倍，成功率涨得比直觉慢；所以“预算内是否成功”必须写清预算",
         fs=FS_S, ha="left")

    save(fig, "03/budget_asr.png")


# ---------------------------------------------------------------- 06 正交化

def fig_06_orthogonalize():
    """第 6 章：把写矩阵里沿拒绝方向的分量减掉，几何上是什么。"""
    import math

    fig, ax = canvas(2.90)

    o = (1.90, 1.85)
    ang = 55.0 * math.pi / 180.0
    ux, uy = math.cos(ang), math.sin(ang)

    tip_r = (o[0] + 3.35 * ux, o[1] + 3.35 * uy)
    arrow(ax, o, tip_r, color=RED, lw=1.3)
    txt(ax, tip_r[0], tip_r[1] + 0.30, "拒绝方向 r（单位向量）", fs=FS_S,
        color=RED, ha="center")

    w = (2.15, 0.80)
    tip_w = (o[0] + w[0], o[1] + w[1])
    arrow(ax, o, tip_w, color=NAVY, lw=1.4)
    txt(ax, tip_w[0] + 0.14, tip_w[1] + 0.20, "w", fs=FS + 0.8, color=NAVY,
        ha="left", weight="bold")

    d = w[0] * ux + w[1] * uy
    proj = (o[0] + d * ux, o[1] + d * uy)
    ax.plot([tip_w[0], proj[0]], [tip_w[1], proj[1]], color=GRAY, lw=0.8,
            ls=(0, (3, 2)), zorder=3)
    arrow(ax, o, proj, color=GOLD, lw=1.4, style="<|-|>")

    wp = (w[0] - d * ux, w[1] - d * uy)
    arrow(ax, o, (o[0] + wp[0], o[1] + wp[1]), color=TEAL, lw=1.4)
    txt(ax, o[0] + wp[0] + 0.12, o[1] + wp[1] - 0.26, "w'", fs=FS + 0.8,
        color=TEAL, ha="left", weight="bold")

    note(ax, 0.45, 0.42,
         "金色是沿拒绝方向的分量，青色是消融之后剩下的部分", fs=FS_S, ha="left")

    rows = [
        ("λ = 0.5", "拒绝率掉一半，能力不动", 4.55),
        ("λ = 0.8", "多数模型的拐点前一档", 3.85),
        ("λ = 1.0", "拒绝归零，开始跑题", 3.15),
    ]
    for name, why, y in rows:
        box(ax, 6.05, y - 0.26, 1.20, 0.52, "", fc="white", ec=LGRAY, lw=0.8)
        txt(ax, 6.65, y, name, fs=FS_S)
        note(ax, 7.38, y, why, fs=FS_S, ha="left")

    txt(ax, 6.05, 2.35, "w' = w - λ r (r^T w)", fs=FS + 0.4, ha="left")
    note(ax, 6.05, 1.95, "λ=1 时 w' 与 r 正交，", fs=FS_S, ha="left")
    note(ax, 6.05, 1.67, "这一行再也写不出拒绝分量", fs=FS_S, ha="left")
    note(ax, 6.05, 1.15, "扫 λ 的判据不是拒绝率，", fs=FS_S, ha="left")
    note(ax, 6.05, 0.87, "而是能力集开始掉头的那一档", fs=FS_S, ha="left")
    note(ax, 6.05, 0.43, "保范数：把 w' 缩回原长度，否则", fs=FS_S, ha="left")
    note(ax, 6.05, 0.18, "整条残差流的尺度都会漂移", fs=FS_S, ha="left")

    save(fig, "06/orthogonalize.png")


# ---------------------------------------------------------------- 11 红队流水线

def fig_11_pipeline():
    """第 11 章：红队从一次测试变成一条流水线，缺一环就退化成一次性动作。"""
    fig, ax = canvas(3.40)

    stages = [
        ("① 威胁模型", "资产、攻击者、入口、影响\n产物是一张表，不是一段话", NAVY),
        ("② 生成攻击", "内部红队 / 外部众测 / 赏金\n三路来源按阶段配比", TEAL),
        ("③ 执行记录", "固定预算、多个种子、判定器版本\n每条留八个字段", GOLD),
        ("④ 判定", "人工标两百条校准判定器\n报一致率，不报感觉", GREEN),
        ("⑤ 归因", "模型 / 提示 / 权限 / 审核\n四选一，才能派工", RED),
        ("⑥ 回归入库", "同一批重测 + 新手法保留\n攻击集只增不减", NAVY_L),
    ]

    ys = [5.95, 5.00, 4.05, 3.10, 2.15, 1.20]
    for (name, body, color), y in zip(stages, ys):
        box(ax, 1.20, y, 5.30, 0.72, "", fc=tint(color, 0.10), ec=color, lw=0.9)
        txt(ax, 1.36, y + 0.36, name, fs=FS - 1.3, ha="left", weight="bold")
        note(ax, 3.18, y + 0.36, body, fs=FS_S - 0.3, ha="left")

    for i in range(5):
        arrow(ax, (3.85, ys[i] - 0.02), (3.85, ys[i + 1] + 0.74),
              color=GRAY, lw=1.0)

    ax.add_line(plt.Line2D([6.50, 6.95], [1.56, 1.56], color=RED, lw=1.0,
                           zorder=2))
    ax.add_line(plt.Line2D([6.95, 6.95], [1.56, 5.36], color=RED, lw=1.0,
                           zorder=2, ls=(0, (3, 2))))
    arrow(ax, (6.95, 5.36), (6.52, 5.36), color=RED, lw=1.0)
    note(ax, 7.08, 5.62, "新手法入库", fs=FS_S, color=RED, ha="left")

    lines = [
        (3.62, "报告里值得看的四个数："),
        (3.30, "新发现的有效问题"),
        (3.02, "复现率"),
        (2.74, "从报告到修复的时间"),
        (2.46, "残余风险条数"),
        (2.02, "没有拦截率——它在"),
        (1.74, "固定攻击集上只会变好"),
    ]
    for y, s_ in lines:
        note(ax, 7.35, y, s_, fs=FS_S, ha="left",
             color=RED if y < 2.2 else GRAY)

    note(ax, 3.85, 0.62,
         "缺第 ⑥ 步，前五步只证明“那天没被攻破”", fs=FS_S)
    note(ax, 3.85, 0.30, "——这是红队最常见的退化方式", fs=FS_S)

    save(fig, "11/redteam_pipeline.png")


FIGS = {
    "01": fig_01_attack_surface,
    "02": fig_02_template_decay,
    "03": fig_03_search_loop,
    "03b": fig_03_budget_asr,
    "04a": fig_04_dual_model,
    "04b": fig_04_exfil,
    "05": fig_05_narrow_band,
    "06": fig_06_orthogonalize,
    "10": fig_10_defense_stack,
    "11": fig_11_pipeline,
    "12": fig_12_modalities,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
