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

def fig_08_defense_stack():
    """第 8 章：四层防御的失效方式各不相同，才构成冗余。"""
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

    save(fig, "08/defense_stack.png")


# ---------------------------------------------------------------- 10 三个通道

def fig_10_modalities():
    """第 10 章：多一层解析，就多一个检查点该放哪的问题。"""
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

    save(fig, "10/modalities.png")


FIGS = {
    "03": fig_03_search_loop,
    "04a": fig_04_dual_model,
    "04b": fig_04_exfil,
    "05": fig_05_narrow_band,
    "08": fig_08_defense_stack,
    "10": fig_10_modalities,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
