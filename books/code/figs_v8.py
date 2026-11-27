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


# ---------------------------------------------------------------- 01 成本交叉

def fig_01_cost():
    """第 1 章：全塞与检索的月成本随日调用量变化，及交叉点。"""
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, 2.70))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.155, 0.255, 0.815, 0.650])

    q = np.logspace(1, np.log10(6000), 200)
    full = 135.0 * q                       # 4.5 元/次 × 30 天
    rag = 5500.0 + 10.8 * q                # 摊薄的开发成本 + 0.36 元/次×30

    ax.plot(q, full, color=RED, lw=1.3, zorder=4)
    ax.plot(q, rag, color=NAVY, lw=1.3, zorder=4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10, 6000)
    ax.set_ylim(200, 1.2e6)

    qc = 5500 / (135 - 10.8)
    ax.plot([qc], [135 * qc], marker="o", ms=5.0, color=GOLD, zorder=6)
    ax.annotate("交叉点 44 次/天",
                xy=(qc, 135 * qc), xytext=(105, 1750),
                fontsize=FS_S - 0.4, color=GOLD,
                arrowprops=dict(arrowstyle="-", color=GOLD, lw=0.6,
                                shrinkA=2, shrinkB=4))

    ax.annotate("全塞：135 元 × 日调用量",
                xy=(3400, 135 * 3400), xytext=(620, 3.2e5),
                fontsize=FS_S - 0.4, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6,
                                shrinkA=2, shrinkB=4))
    ax.annotate("检索：5500 + 10.8 元 × 日调用量",
                xy=(90, 5500 + 10.8 * 90), xytext=(17, 22000),
                fontsize=FS_S - 0.4, color=NAVY,
                arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.6,
                                shrinkA=2, shrinkB=4))

    ax.axvspan(10, qc, color=tint(GOLD, 0.10), zorder=0, lw=0)
    ax.text(21, 330, "量小：全塞更省钱", fontsize=FS_S - 0.6, color=GRAY)

    ax.set_xlabel("每天问答次数（对数）", fontsize=8)
    ax.set_ylabel("月成本 / 元（对数）", fontsize=8)
    ax.set_xticks([10, 30, 100, 300, 1000, 3000])
    ax.set_xticklabels(["10", "30", "100", "300", "1000", "3000"])
    ax.grid(color=LGRAY, lw=0.5, alpha=0.7, which="major")
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    fig.text(0.5, 0.055, "开发成本 3 万元按 12 个月摊薄，月维护 3000 元",
             fontsize=FS_S - 0.6, color=GRAY, ha="center")

    save(fig, "01/cost-curve.png")


# ---------------------------------------------------------------- 03 内存规模

def fig_03_memory():
    """第 3 章：三种精度下，索引内存随块数的增长。"""
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, 2.55))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.155, 0.255, 0.815, 0.645])

    ns = np.array([1e5, 1e6, 1e7])
    dim = 1024
    fp32 = ns * dim * 4 / 1024 ** 3
    int8 = ns * dim * 1 / 1024 ** 3
    bin1 = ns * dim / 8 / 1024 ** 3

    x = np.arange(3)
    w = 0.24
    for i, (v, c, lab) in enumerate([(fp32, RED, "FP32"),
                                     (int8, NAVY, "INT8"),
                                     (bin1, TEAL, "二值 1 bit")]):
        b = ax.bar(x + (i - 1) * w, v, w * 0.92, color=c, alpha=0.85,
                   label=lab, zorder=4, lw=0)
        for r, val in zip(b, v):
            ax.text(r.get_x() + r.get_width() / 2, val * 1.12,
                    f"{val:.2g}", ha="center", va="bottom",
                    fontsize=FS_S - 1.4, color=c)

    ax.axhline(16, color=GRAY, lw=0.8, ls=(0, (4, 3)), zorder=3)
    ax.text(2.44, 17, "单机 16 GB", fontsize=FS_S - 1.0, color=GRAY,
            ha="right")
    ax.axhline(64, color=GRAY, lw=0.8, ls=(0, (4, 3)), zorder=3)
    ax.text(2.44, 67, "单机 64 GB", fontsize=FS_S - 1.0, color=GRAY,
            ha="right")

    ax.set_yscale("log")
    ax.set_ylim(5, 170)
    ax.set_xticks(x)
    ax.set_xticklabels(["10 万块", "100 万块", "1000 万块"])
    ax.set_ylabel("索引内存 / GB（对数）", fontsize=8)
    ax.grid(axis="y", color=LGRAY, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(frameon=False, ncol=3, loc="upper left",
              fontsize=FS_S - 0.8, handlelength=1.1)

    fig.text(0.5, 0.045, "1024 维，只计向量本身；HNSW 图结构另加 5%–10%",
             fontsize=FS_S - 0.8, color=GRAY, ha="center")

    save(fig, "03/memory-scale.png")


# ---------------------------------------------------------------- 04 检索漏斗

def fig_04_funnel():
    """第 4 章：从一百万块到五段，每一级剩多少、花多久。"""
    fig, ax = canvas(2.55)

    rows = [
        ("全库 100 万块", "ANN 实际比较约 3000 个", 1000000, "25 ms", NAVY_XL),
        ("两路各 50，去重后 78", "BM25 命中 + 向量命中", 78, "5 ms", NAVY_L),
        ("RRF 取前 30", "融合两路排名", 30, "1 ms", GOLD),
        ("重排取前 5", "逐条打分，不能靠加机器摊薄", 5, "80 ms", RED),
    ]

    x0, top = 0.30, 4.30
    rh, gap = 0.78, 0.30
    maxw = 6.40

    for i, (name, sub, n, ms, c) in enumerate(rows):
        y = top - i * (rh + gap)
        w = maxw * (np.log10(n) / 6.0) ** 1.15
        w = max(w, 0.55)
        ax.add_patch(Rectangle((x0, y), w, rh, facecolor=tint(c, 0.28),
                               edgecolor=c, lw=0.8, zorder=3))
        txt(ax, x0 + 0.18, y + rh * 0.66, f"{n:,}" if n >= 1000 else str(n),
            fs=FS_S + 2.2, color=INK, ha="left", weight="bold")
        txt(ax, x0 + 0.18, y + rh * 0.26, name, fs=FS_S - 0.6, color=INK,
            ha="left")
        txt(ax, x0 + w + 0.24, y + rh * 0.62, sub, fs=FS_S - 1.0, color=GRAY,
            ha="left")
        note(ax, x0 + w + 0.24, y + rh * 0.24, ms, fs=FS_S - 0.4,
             color=RED if i == 3 else GRAY, ha="left")
        if i:
            txt(ax, x0 - 0.04, y + rh + gap / 2,
                f"×{rows[i - 1][2] / n:.2f}", fs=FS_S - 1.4, color=GRAY,
                ha="right")

    note(ax, 5.05, 0.52, "横向长度按块数的对数折算，不是等比", fs=FS_S - 1.0)
    note(ax, 5.05, 0.22, "红色是延迟大头：30 条候选的重排", fs=FS_S - 1.0,
         color=RED)

    save(fig, "04/funnel.png")


# ---------------------------------------------------------------- 05 提示预算

def fig_05_budget():
    """第 5 章：8K 窗口里六段预算怎么切。"""
    fig, ax = canvas(2.35)

    parts = [("系统规则", 300, NAVY), ("资料 5 段", 2400, GOLD),
             ("对话历史", 1500, TEAL), ("用户问题", 200, NAVY_L),
             ("输出预留", 800, RED), ("余量", 2800, LGRAY)]
    total = sum(p[1] for p in parts)
    x0, y0, H = 0.30, 3.32, 0.92
    span = 9.80

    x = x0
    for name, v, c in parts:
        w = span * v / total
        ax.add_patch(Rectangle((x, y0), w, H, facecolor=tint(c, 0.25),
                               edgecolor=c, lw=0.8, zorder=3))
        if w > 0.85:
            txt(ax, x + w / 2, y0 + H * 0.62, name, fs=FS_S - 0.6)
            txt(ax, x + w / 2, y0 + H * 0.28, str(v), fs=FS_S - 1.2, color=GRAY)
        x += w

    note(ax, x0 + span * 5200 / total - 0.9, y0 + H + 0.30,
         "已用 5200", fs=FS_S - 0.6, color=INK)
    note(ax, x0 + span * 6600 / total + 0.5, y0 + H + 0.30,
         "留 2800 应付长问题、多轮与长资料", fs=FS_S - 0.8, color=GRAY)

    for i, (name, v, c) in enumerate(parts):
        col, row = i % 2, i // 2
        lx = 0.34 + col * 4.95
        ly = 2.30 - row * 0.62
        ax.add_patch(Rectangle((lx, ly), 0.34, 0.30, facecolor=tint(c, 0.25),
                               edgecolor=c, lw=0.8, zorder=3))
        txt(ax, lx + 0.48, ly + 0.15, f"{name}　{v} token", fs=FS_S - 0.6,
            ha="left")

    note(ax, 5.05, 0.22, "中文按 1 字约 1.5 token 折算：300 token ≈ 200 字",
         fs=FS_S - 1.0)

    save(fig, "05/prompt-budget.png")


# ---------------------------------------------------------------- 06 样本量

def fig_06_samples():
    """第 6 章：95% 置信区间随样本量收缩。"""
    setup()
    plt.rcParams["font.sans-serif"] = [st_font, "DejaVu Sans"]
    fig = plt.figure(figsize=(W, 2.50))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.150, 0.270, 0.820, 0.640])

    p = 0.78
    n = np.arange(30, 601)
    hw = 1.96 * np.sqrt(p * (1 - p) / n) * 100

    ax.plot(n, hw, color=NAVY, lw=1.4, zorder=4)
    ax.fill_between(n, hw, 0, color=tint(NAVY, 0.10), zorder=2, lw=0)
    ax.axhline(3.0, color=GOLD, lw=0.9, ls=(0, (4, 3)), zorder=3)
    ax.text(590, 3.4, "±3 个点", fontsize=FS_S - 0.8, color=GOLD, ha="right")

    for nn in (50, 100, 187, 500):
        v = 1.96 * np.sqrt(p * (1 - p) / nn) * 100
        ax.plot([nn], [v], marker="o", ms=4.2,
                color=RED if nn < 187 else NAVY, zorder=6)
        ax.text(nn, v + 0.60, f"±{v:.1f}", fontsize=FS_S - 1.2,
                color=RED if nn < 187 else NAVY, ha="center")

    ax.set_xlim(30, 600)
    ax.set_ylim(0, 13.5)
    ax.set_xlabel("评测集样本量 n", fontsize=8)
    ax.set_ylabel("95% 区间半宽 / 百分点", fontsize=8)
    ax.grid(color=LGRAY, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    fig.text(0.5, 0.055,
             "p = 0.78 时的抽样误差；n = 50 时一次改动涨 5 个点，分不清真假",
             fontsize=FS_S - 0.8, color=GRAY, ha="center")

    save(fig, "06/sample-size.png")


# ---------------------------------------------------------------- 07 并行

def fig_07_parallel():
    """第 7 章：三个无依赖工具，串行与并行的等待时间。"""
    fig, ax = canvas(2.40)

    x0, span = 1.55, 7.55

    def X(ms):
        return x0 + span * ms / 900.0

    rtt = 40
    calls = [("查订单", 300, NAVY), ("查物流", 250, GOLD),
             ("查优惠券", 200, TEAL)]

    y_s, hh = 3.60, 0.60
    t = 0.0
    for name, d, c in calls:
        ax.add_patch(Rectangle((X(t), y_s), X(t + rtt) - X(t), hh,
                               facecolor=tint(GRAY, 0.12), edgecolor=LGRAY,
                               lw=0.7, zorder=3))
        t += rtt
        ax.add_patch(Rectangle((X(t), y_s), X(t + d) - X(t), hh,
                               facecolor=tint(c, 0.22), edgecolor=c,
                               lw=0.8, zorder=3))
        txt(ax, (X(t) + X(t + d)) / 2, y_s + hh / 2, name, fs=FS_S - 1.2)
        t += d
    txt(ax, x0 - 0.12, y_s + hh / 2, "串行", fs=FS_S, ha="right",
        weight="bold")
    txt(ax, X(870) + 0.16, y_s + hh / 2, "870 ms", fs=FS_S - 0.4, ha="left",
        color=RED, weight="bold")
    ax.plot([X(870), X(870)], [y_s - 0.10, y_s + hh + 0.10], color=RED, lw=0.8,
            zorder=5)

    y_p = 2.38
    ax.add_patch(Rectangle((X(0), y_p), X(rtt) - X(0), hh,
                           facecolor=tint(GRAY, 0.12), edgecolor=LGRAY,
                           lw=0.7, zorder=3))
    for i, (name, d, c) in enumerate(calls):
        yy = y_p + hh - 0.20 * i - 0.10
        ax.add_patch(Rectangle((X(rtt), yy), X(rtt + d) - X(rtt), 0.15,
                               facecolor=tint(c, 0.22), edgecolor=c,
                               lw=0.8, zorder=3))
        txt(ax, X(rtt + d) + 0.16, yy + 0.075, name, fs=FS_S - 1.4, ha="left")
    txt(ax, x0 - 0.12, y_p + hh / 2, "并行", fs=FS_S, ha="right",
        weight="bold")
    txt(ax, X(340) + 1.70, y_p + hh / 2, "340 ms", fs=FS_S - 0.4, ha="left",
        color=NAVY, weight="bold")
    ax.plot([X(340), X(340)], [y_p - 0.06, y_p + hh + 0.06], color=NAVY, lw=0.8,
            zorder=5)

    ay = 1.78
    ax.plot([X(0), X(900)], [ay, ay], color=GRAY, lw=0.7, zorder=2)
    for ms in (0, 200, 400, 600, 800):
        ax.plot([X(ms), X(ms)], [ay, ay - 0.09], color=GRAY, lw=0.7, zorder=2)
        note(ax, X(ms), ay - 0.26, str(ms), fs=FS_S - 1.6)
    note(ax, X(450), ay - 0.52, "毫秒；浅灰格子是网络往返 40 ms", fs=FS_S - 1.2)
    note(ax, 5.05, 0.42, "并行的等待取最长者，成本仍按三次调用付", fs=FS_S - 0.8)

    save(fig, "07/parallel.png")


FIGS = {
    "01": fig_01_cost,
    "03": fig_03_memory,
    "05": fig_05_budget,
    "07": fig_07_parallel,
    "funnel": fig_04_funnel,
    "samples": fig_06_samples,
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
