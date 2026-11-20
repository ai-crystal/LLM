# -*- coding: utf-8 -*-
"""《大模型技术全景 · 应用与 Agent 系统篇》（第八卷）插图。

运行：
    python books/code/figs_v8.py          # 全部重画
    python books/code/figs_v8.py 02 06    # 只画指定编号

输出：
    books/v8-apps/images/02/chunking.png
    books/v8-apps/images/04/hybrid.png
    books/v8-apps/images/06/eval-ranks.png
    books/v8-apps/images/08/loop.png
    books/v8-apps/images/09/state-machine.png
    books/v8-apps/images/10/drift.png

尺寸约定同其他册：画布宽 5.2 in ≈ 132 mm，1 单位 = 0.5 in，
288 dpi 出图，宽约 1497 px，按版心 130 mm 置入不必缩放。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle

from figstyle import (BG, GOLD, GRAY, INK, LGRAY, NAVY, NAVY_L, NAVY_XL, RED,
                      TEAL, arrow, box, plt, setup)

W = 5.2
DPI = 288
FS = 8.5
FS_S = 7.2

ROOT = HERE.parent
OUTDIR = ROOT / "v8-apps" / "images"

st_font = "Microsoft YaHei"


def tint(color, f):
    r, g, b = to_rgb(color)
    return (1 - f + r * f, 1 - f + g * f, 1 - f + b * f)


def canvas(h_in: float):
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, h_in))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 2 * W)
    ax.set_ylim(0, 2 * h_in)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.grid(False)
    return fig, ax


def txt(ax, x, y, s, fs=FS, color=INK, ha="center", va="center",
        weight="normal", z=8, **kw):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, zorder=z, linespacing=1.4, **kw)


def note(ax, x, y, s, fs=FS_S, color=GRAY, ha="center", va="center", **kw):
    return txt(ax, x, y, s, fs=fs, color=color, ha=ha, va=va, **kw)


def save(fig, rel: str):
    dst = OUTDIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image
    with Image.open(dst) as im:
        im.convert("RGB").save(dst, dpi=(DPI, DPI))
        print(f"saved {dst.relative_to(ROOT)}  {im.width}×{im.height} px")


# ---------------------------------------------------------------- 02 切块

def fig_02_chunking():
    """第 2 章：同一份文档，按结构切 vs 按固定长度切。"""
    fig, ax = canvas(3.05)

    y0, h_total = 1.10, 4.10
    sec_h = h_total / 3

    # 原文
    ax.add_patch(Rectangle((0.30, y0), 2.30, h_total, facecolor="white",
                           edgecolor=NAVY_L, lw=0.8, zorder=3))
    txt(ax, 1.45, y0 + h_total + 0.30, "退货政策原文", fs=FS)
    bands = [("3.1 适用范围", "官网及官方 App 下单"), ("3.2 时间限制", "45 日内，未拆封"),
             ("3.3 例外", "定制、生鲜、已激活")]
    for i, (t, s) in enumerate(bands):
        yb = y0 + h_total - (i + 1) * sec_h
        if i:
            ax.plot([0.30, 2.60], [yb + sec_h, yb + sec_h], color=LGRAY, lw=0.7,
                    zorder=4)
        txt(ax, 1.45, yb + sec_h * 0.68, t, fs=FS_S, weight="bold")
        txt(ax, 1.45, yb + sec_h * 0.30, s, fs=FS_S - 0.4, color=GRAY)

    # 结构切块
    xs = 3.10
    for i, (t, s) in enumerate(bands):
        yb = y0 + h_total - (i + 1) * sec_h
        box(ax, xs, yb + 0.04, 2.55, sec_h - 0.08, "",
            fc=tint(GOLD, 0.10), ec=GOLD, lw=0.8)
        txt(ax, xs + 1.275, yb + sec_h * 0.66, t, fs=FS_S, weight="bold")
        txt(ax, xs + 1.275, yb + sec_h * 0.30, s, fs=FS_S - 0.4, color=GRAY)
    txt(ax, xs + 1.275, y0 + h_total + 0.30, "按标题切：3 块", fs=FS)
    note(ax, xs + 1.275, y0 - 0.34, "标题写进块的正文，语义不丢")

    # 固定长度切块
    xf = 6.20
    bh = 1.00
    labels = ["适用范围：官网及 App 下单",
              "…下单。签收后 45 日内…",
              "…未拆封且不影响二次销售…",
              "…生鲜、已激活电子产品不适用"]
    for i in range(4):
        yb = y0 + h_total - (i + 1) * bh
        bad = i in (1,)
        box(ax, xf, yb + 0.02, 2.85, bh - 0.04, "",
            fc=tint(RED, 0.08) if bad else BG,
            ec=RED if bad else NAVY_L, lw=0.8)
        txt(ax, xf + 1.42, yb + bh / 2, labels[i], fs=FS_S - 1.0,
            color=RED if bad else INK)
    txt(ax, xf + 1.42, y0 + h_total + 0.30, "按固定长度切：4 块", fs=FS)
    note(ax, xf + 1.42, y0 - 0.34, "有一块跨了两个小节，标题也丢了")

    # 跳节标记：在红色块内画出被切断的位置
    ycut = y0 + h_total - 2 * bh + 0.68
    ax.plot([xf + 0.10, xf + 2.75], [ycut, ycut], color=RED, lw=0.8,
            ls=(0, (2.5, 2)), zorder=5)

    save(fig, "02/chunking.png")


# ---------------------------------------------------------------- 04 混合检索

def fig_04_hybrid():
    """第 4 章：两路召回、融合、重排，以及各段的候选数与延迟量级。"""
    fig, ax = canvas(2.85)

    cy = 3.45
    bw, bh = 1.60, 0.86
    xs = [0.20, 2.22, 4.24, 6.26, 8.28]

    # 1 查询
    box(ax, xs[0], cy - bh / 2, bw, bh, "查询\n+ 改写", fc=BG, ec=NAVY_L)
    # 2 两路
    box(ax, xs[1], cy + 0.34, bw, 0.72, "BM25\n关键词", fc=tint(GOLD, 0.12),
        ec=GOLD)
    box(ax, xs[1], cy - 1.06, bw, 0.72, "向量\n语义", fc=tint(TEAL, 0.10),
        ec=TEAL)
    # 3 融合
    box(ax, xs[2], cy - bh / 2, bw, bh, "RRF 融合\n取前 30", fc=BG, ec=NAVY_L)
    # 4 重排
    box(ax, xs[3], cy - bh / 2, bw, bh, "交叉编码\n取前 5", fc=tint(NAVY, 0.10),
        ec=NAVY)
    # 5 组装
    box(ax, xs[4], cy - bh / 2, bw, bh, "拼进提示\n2500 token", fc=BG, ec=NAVY_L)

    arrow(ax, (xs[0] + bw + 0.02, cy), (xs[1] - 0.06, cy + 0.70), rad=-0.12)
    arrow(ax, (xs[0] + bw + 0.02, cy), (xs[1] - 0.06, cy - 0.70), rad=0.12)
    arrow(ax, (xs[1] + bw + 0.02, cy + 0.70), (xs[2] - 0.04, cy + 0.18), rad=-0.10)
    arrow(ax, (xs[1] + bw + 0.02, cy - 0.70), (xs[2] - 0.04, cy - 0.18), rad=0.10)
    arrow(ax, (xs[2] + bw + 0.02, cy), (xs[3] - 0.04, cy))
    arrow(ax, (xs[3] + bw + 0.02, cy), (xs[4] - 0.04, cy))

    # 候选数
    note(ax, xs[1] + bw / 2, cy + 1.30, "各 50", fs=FS_S)
    note(ax, xs[2] + bw / 2, cy + 0.62, "50 + 50 → 30", fs=FS_S)
    note(ax, xs[3] + bw / 2, cy + 0.62, "30 → 5", fs=FS_S)

    # 延迟条
    ys = 1.05
    ax.plot([0.20, 9.88], [ys, ys], color=LGRAY, lw=0.7, zorder=2)
    lat = [("15 ms", 0), ("25 ms", 1), ("5 ms", 2), ("80 ms", 3), ("3 ms", 4)]
    for s, i in lat:
        txt(ax, xs[i] + bw / 2, ys + 0.28, s, fs=FS_S,
            color=RED if i == 3 else GRAY, weight="bold" if i == 3 else "normal")
    note(ax, 5.05, ys - 0.34, "单次请求各段耗时（经验值，取排序模型 50 候选）")

    save(fig, "04/hybrid.png")


# ---------------------------------------------------------------- 06 评测

def fig_06_ranks():
    """第 6 章：8 条查询里正确段落的排名，以及三个指标怎么算。"""
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, 2.95))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.145, 0.275, 0.825, 0.635])

    ranks = [1, 2, 4, 7, 12, 18, 25, 25]     # 25 表示前 20 里没有
    labels = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]

    ax.axvspan(0.5, 5.5, color=tint(GOLD, 0.16), zorder=0, lw=0)
    ax.axvspan(5.5, 20.5, color=tint(NAVY, 0.07), zorder=0, lw=0)
    ax.axvspan(20.5, 26.5, color=tint(RED, 0.06), zorder=0, lw=0)
    ax.set_xlim(0.5, 26.5)
    ax.set_ylim(-0.7, 7.7)
    ax.set_yticks(range(8))
    ax.set_yticklabels(labels)
    ax.set_xticks([1, 5, 10, 20, 25])
    ax.set_xticklabels(["1", "5", "10", "20", ">20"])
    ax.grid(axis="x", color=LGRAY, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    for i, r in enumerate(ranks):
        if r > 20:
            c, m = RED, "x"
        elif r <= 5:
            c, m = GOLD, "o"
        else:
            c, m = NAVY, "o"
        ax.plot([r], [i], marker=m, ms=6.0, color=c, mew=1.3, zorder=5)
        ax.plot([0.6, r], [i, i], color=LGRAY, lw=0.6, zorder=1)

    ax.text(3.0, 7.45, "前 5", fontsize=FS_S, color=GOLD, ha="center")
    ax.text(13.0, 7.45, "前 20", fontsize=FS_S, color=NAVY, ha="center")
    ax.text(23.5, 7.45, "未召回", fontsize=FS_S, color=RED, ha="center")

    fig.text(0.5, 0.130, "召回@5 = 3/8 = 0.375　　召回@20 = 6/8 = 0.750",
             fontsize=FS_S, color=INK, ha="center", va="center")
    fig.text(0.5, 0.035,
             "MRR = (1 + 1/2 + 1/4 + 1/7 + 1/12 + 1/18) / 8 = 0.254",
             fontsize=FS_S, color=INK, ha="center", va="center")

    save(fig, "06/eval-ranks.png")


# ---------------------------------------------------------------- 08 Agent 循环

def fig_08_loop():
    """第 8 章：三段循环、终止检查、以及四条退出路径。"""
    fig, ax = canvas(3.15)

    y, bh = 4.35, 0.95
    boxes = [(0.35, 2.05, "想", "计划下一步", BG, NAVY_L),
             (3.55, 2.05, "做", "调一个工具", tint(GOLD, 0.12), GOLD),
             (6.75, 2.05, "看", "读结果", tint(TEAL, 0.10), TEAL)]
    for x, w, l, sub, fc, ec in boxes:
        box(ax, x, y, w, bh, "", fc=fc, ec=ec)
        txt(ax, x + w / 2, y + bh * 0.68, l, fs=FS, weight="bold")
        note(ax, x + w / 2, y + bh * 0.28, sub, fs=FS_S - 0.4)

    arrow(ax, (2.44, y + bh / 2), (3.51, y + bh / 2))
    arrow(ax, (5.64, y + bh / 2), (6.71, y + bh / 2))

    # 终止检查
    gx, gw, gy, gh = 3.55, 2.05, 2.55, 0.80
    box(ax, gx, gy, gw, gh, "终止检查", fc=tint(RED, 0.08), ec=RED)

    ax.plot([7.775, 7.775, 5.66], [y, gy + gh / 2, gy + gh / 2],
            color=NAVY, lw=0.9, zorder=2)
    arrow(ax, (5.98, gy + gh / 2), (5.64, gy + gh / 2))

    ax.plot([gx, 1.375, 1.375], [gy + gh / 2, gy + gh / 2, y - 0.02],
            color=NAVY, lw=0.9, zorder=2)
    arrow(ax, (1.375, gy + gh / 2), (1.375, y - 0.02))
    note(ax, 2.55, gy + gh / 2 + 0.20, "继续", fs=FS_S, color=NAVY)

    # 退出总线
    bus_y = 2.02
    ax.plot([4.575, 4.575], [gy, bus_y], color=INK, lw=0.8, zorder=2)
    ax.plot([1.30, 8.50], [bus_y, bus_y], color=INK, lw=0.8, zorder=2)

    exits = [("完成", "#4F7A5B"), ("失败 → 重试 ≤3 次", GOLD),
             ("连续失败 → 换一条路", NAVY_L), ("不可恢复 → 转人工", RED)]
    ew, eh, ey = 2.15, 0.85, 0.85
    centers = [1.30, 3.70, 6.10, 8.50]
    for (s_, c), cx in zip(exits, centers):
        box(ax, cx - ew / 2, ey, ew, eh, s_, fc=tint(c, 0.08), ec=c, fs=FS_S - 0.6)
        arrow(ax, (cx, bus_y), (cx, ey + eh + 0.02), color=c, lw=0.8)

    note(ax, 5.05, 0.32, "任一条件命中即退出循环，不再调模型", fs=FS_S)

    save(fig, "08/loop.png")


# ---------------------------------------------------------------- 09 状态机

def fig_09_state():
    """第 9 章：四个状态的流转、回退，以及每一步都要落盘的事件日志。"""
    fig, ax = canvas(2.70)

    y, bh = 3.72, 0.95
    bw = 1.85
    xs = [0.30, 2.62, 4.94, 7.26]
    labels = ["收集需求", "确认方案", "执行", "验收"]
    subs = ["问清 3 件事", "用户点头", "逐条调用", "逐项核对"]

    for i, (l, s_) in enumerate(zip(labels, subs)):
        c = NAVY if i < 3 else "#4F7A5B"
        box(ax, xs[i], y, bw, bh, "", fc=tint(c, 0.08), ec=c)
        txt(ax, xs[i] + bw / 2, y + bh * 0.66, l, fs=FS, weight="bold")
        note(ax, xs[i] + bw / 2, y + bh * 0.27, s_, fs=FS_S - 0.6)

    for i in range(3):
        arrow(ax, (xs[i] + bw + 0.03, y + bh / 2), (xs[i + 1] - 0.04, y + bh / 2))

    # 回退：验收不通过 → 确认方案
    yb = y - 0.86
    ax.plot([xs[3] + bw / 2, xs[3] + bw / 2], [y, yb], color=RED, lw=0.8,
            ls=(0, (3, 2)), zorder=2)
    ax.plot([xs[3] + bw / 2, xs[1] + bw / 2], [yb, yb], color=RED,
            lw=0.8, ls=(0, (3, 2)), zorder=2)
    arrow(ax, (xs[1] + bw / 2, yb), (xs[1] + bw / 2, y - 0.05),
          color=RED, lw=0.8, ls=(0, (3, 2)))
    note(ax, xs[2] + bw / 2, yb + 0.30, "验收不通过：退回上一个状态，不从头开始",
         fs=FS_S - 0.4, color=RED)

    # 事件日志
    ly = 0.34
    ax.add_patch(Rectangle((0.30, ly), 8.81, 1.15, facecolor=tint(GOLD, 0.08),
                           edgecolor=GOLD, lw=0.8, zorder=3))
    txt(ax, 0.55, ly + 1.40, "事件日志：每次状态变化追加一行，恢复时重放",
        fs=FS_S - 0.2, color=GOLD, ha="left")
    rows = ["step   state    action                result",
            "03     执行     查询订单 A12          已付款",
            "04     执行     退款 A12 金额 299     成功，单号 R77821"]
    for i, r in enumerate(rows):
        txt(ax, 0.55, ly + 0.86 - i * 0.32, r, fs=FS_S - 1.1, ha="left",
            color=INK)

    save(fig, "09/state-machine.png")


# ---------------------------------------------------------------- 10 趋势

def fig_10_drift():
    """第 10 章：召回率缓慢下滑，阈值告警一直不响，趋势才看得见。"""
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, 2.55))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.145, 0.235, 0.835, 0.63])

    weeks = np.arange(1, 15)
    base = np.linspace(0.880, 0.810, 14)
    noise = np.array([0.006, -0.010, 0.008, 0.004, -0.006, 0.010, -0.004,
                      0.002, -0.008, 0.006, 0.004, -0.006, 0.008, -0.002])
    r20 = base + noise

    ax.axhline(0.80, color=RED, lw=0.9, ls=(0, (4, 3)), zorder=2)
    ax.text(1.15, 0.806, "告警阈值 0.80", fontsize=FS_S - 0.4, color=RED,
            va="bottom")

    ax.plot(weeks, r20, color=NAVY, lw=1.4, marker="o", ms=3.2, zorder=4)
    ax.plot(weeks, base, color=GOLD, lw=0.9, ls=(0, (5, 3)), zorder=3)

    ax.set_xlim(0.5, 14.5)
    ax.set_ylim(0.762, 0.912)
    ax.set_xticks([1, 4, 7, 10, 13])
    ax.set_yticks([0.78, 0.80, 0.84, 0.88])
    ax.set_xlabel("上线后第几周", fontsize=8)
    ax.text(1.1, 0.904, "召回率 @20", fontsize=FS_S, color=GRAY, va="top")
    ax.grid(color=LGRAY, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    ax.annotate("14 周掉了 7 个点\n阈值 0.80 一次都没响",
                xy=(12, r20[11]), xytext=(7.4, 0.868),
                fontsize=FS_S - 0.4, color=GRAY,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.6,
                                shrinkA=2, shrinkB=4))

    save(fig, "10/drift.png")


FIGS = {
    "02": fig_02_chunking,
    "04": fig_04_hybrid,
    "06": fig_06_ranks,
    "08": fig_08_loop,
    "09": fig_09_state,
    "10": fig_10_drift,
}


def main(argv):
    keys = argv[1:] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
