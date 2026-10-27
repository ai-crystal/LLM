# -*- coding: utf-8 -*-
"""A 组插图（第 1–9 章，共 16 张）。

运行： python tools/make_figures_a.py
输出： figures/<name>.pdf（矢量）
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from figstyle import *  # noqa: F401,F403
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- 小工具

# 印刷字号系数：书里把插图缩到 130mm，字号要按此系数放大才不缩水。
# 每个绘图函数开头用 `global SCALE; SCALE = x` 设定。
SCALE = 1.0


def _fs(x):
    return x * SCALE


def _scale_rc():
    plt.rcParams.update({
        "font.size": 9 * SCALE,
        "axes.titlesize": 10 * SCALE,
        "axes.labelsize": 9 * SCALE,
        "xtick.labelsize": 8 * SCALE,
        "ytick.labelsize": 8 * SCALE,
        "legend.fontsize": 8 * SCALE,
    })


def canvas(w: float = 6.4, h: float = 3.5):
    setup()
    _scale_rc()
    fig, ax = plt.subplots(figsize=(w, h))
    fig.subplots_adjust(left=0.09, right=0.975, top=0.9, bottom=0.14)
    return fig, ax


def diagram(w: float = 6.4, h: float = 3.2, xlim=(0, 10), ylim=(0, 5)):
    setup()
    _scale_rc()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.grid(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


_box0 = box


def box(ax, x, y, w, h, text="", fc=BG, ec=NAVY_L, tc=INK, fs=8.5,
        lw=0.8, rounded=0.08, weight="normal", zorder=3, alpha=1.0):
    return _box0(ax, x, y, w, h, text, fc=fc, ec=ec, tc=tc, fs=_fs(fs),
                 lw=lw, rounded=rounded, weight=weight, zorder=zorder,
                 alpha=alpha)


def note(ax, x, y, s, fs=7.5, color=GRAY, ha="center", va="center", rot=0, **kw):
    return ax.text(x, y, s, fontsize=_fs(fs), color=color, ha=ha, va=va,
                   rotation=rot, rotation_mode="anchor", zorder=6, **kw)

def leader(ax, p0, p1, color=LGRAY, lw=0.6):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw, zorder=1,
            solid_capstyle="butt")

def poly(ax, pts, color=NAVY_L, lw=0.9, ls="-", arrowhead=True):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=2,
            solid_capstyle="round", solid_joinstyle="round")
    if arrowhead:
        arrow(ax, pts[-2], pts[-1], color=color, lw=lw, ls=ls, shrink=0)
    else:
        ax.plot(xs[-1:], ys[-1:], color=color, lw=lw, ls=ls, zorder=2)

def logx(ax, ticks, labels=None, minor=False):
    ax.set_xticks(ticks)
    if labels:
        ax.set_xticklabels(labels)
    ax.set_xlim(min(ticks) * 0.82, max(ticks) * 1.22)
    if not minor:
        ax.minorticks_off()

# ---------------------------------------------------------------- 版面

def save(fig, name: str) -> None:  # noqa: F811
    """覆盖 figstyle.save：出血边从 0.04in 加到 0.10in。

    书里按 130mm 缩版印刷，0.04in 边只剩 0.7mm，看起来像被裁切。
    """
    FIGDIR.mkdir(exist_ok=True)
    out = FIGDIR / f"{name}.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("saved", out.name)


# ---------------------------------------------------------------- 1-1

def fig_p1_attention_bottleneck():
    global SCALE
    SCALE = 1.1
    fig, ax = diagram(6.5, 3.3, xlim=(0, 10), ylim=(0, 5.08))

    note(ax, 0.15, 4.85, "RNN：整句压成一个向量", fs=8, ha="left")
    note(ax, 5.35, 4.85, "注意力：每步直连所有源词", fs=8, ha="left")

    words = ["昨天", "在", "图书馆", "读书"]
    xs = [0.2, 1.15, 2.10, 3.05]
    for i, (w, x) in enumerate(zip(words, xs)):
        box(ax, x, 4.05, 0.85, 0.5, w, fs=8.2, fc=BG)
        if i < 3:
            arrow(ax, (x + 0.87, 4.30), (xs[i + 1] - 0.02, 4.30), lw=0.8)
    note(ax, 1.55, 3.62, "逐词读入，状态递推", fs=7.2, ha="left")

    # 压缩成一个向量
    box(ax, 2.05, 2.30, 1.45, 0.62, "单一向量 $c$", fs=8.2, fc=NAVY_XL, ec=NAVY)
    arrow(ax, (3.47, 4.03), (3.47, 2.96), lw=0.9)
    note(ax, 3.60, 3.45, "压缩", fs=7.2, ha="left")

    # 解码器
    dec = ["$t$=1\n在", "$t$=2\n看", "$t$=3\n书"]
    for i, x in enumerate([1.15, 2.15, 3.15]):
        box(ax, x, 1.15, 0.90, 0.55, dec[i], fs=7.6, fc=BG)
        arrow(ax, (2.78, 2.28), (x + 0.45, 1.74), lw=0.8, rad=0.04)
    note(ax, 2.55, 0.55, "每步都读同一个 $c$", fs=7.2)

    # ---------------- 右：注意力
    src = ["昨天", "在", "图书馆", "读书"]
    sxs = [5.35, 6.40, 7.45, 8.50]
    for w, x in zip(src, sxs):
        box(ax, x, 0.75, 0.95, 0.55, w, fs=8.2, fc=BG)

    dcs = ["步 1", "步 2", "步 3"]
    dcx = [5.90, 7.10, 8.30]
    for w, x in zip(dcs, dcx):
        box(ax, x, 3.65, 1.05, 0.55, w, fs=8.2, fc=BG)

    wts = [[0.55, 0.15, 0.20, 0.10],
           [0.10, 0.45, 0.35, 0.10],
           [0.10, 0.15, 0.20, 0.55]]
    for i, x in enumerate(dcx):
        for j, sx in enumerate(sxs):
            w = wts[i][j]
            a = arrow(ax, (x + 0.525, 3.63), (sx + 0.475, 1.32), color=NAVY,
                      lw=0.3 + 3.6 * w, shrink=1)
            a.set_alpha(0.25 + 0.75 * w)
    note(ax, 7.40, 0.35, "权重正比于线宽", fs=7.2)

    save(fig, "p1-attention-bottleneck")

# ---------------------------------------------------------------- 2-1

def fig_p2_transformer_block():
    global SCALE
    SCALE = 1.11
    fig, ax = diagram(6.4, 4.6, xlim=(0, 10), ylim=(0, 7.19))
    cx = 1.95

    box(ax, 1.25, 0.45, 1.40, 0.50, "输入 $x$", fs=8.2, fc=BG)
    box(ax, 1.35, 1.30, 1.20, 0.45, "LN", fs=8.2, fc=BG)
    box(ax, 1.25, 2.05, 1.40, 0.55, "多头注意力", fs=8.2, fc=NAVY_XL, ec=NAVY)
    box(ax, 1.73, 2.73, 0.44, 0.44, "+", fs=9, rounded=0.22,
        fc=BG, ec=NAVY, lw=0.9)
    box(ax, 1.35, 3.55, 1.20, 0.45, "LN", fs=8.2, fc=BG)
    box(ax, 1.25, 4.30, 1.40, 0.55, "FFN（SwiGLU）", fs=7.0, fc=NAVY_XL, ec=NAVY)
    box(ax, 1.73, 4.98, 0.44, 0.44, "+", fs=9, rounded=0.22,
        fc=BG, ec=NAVY, lw=0.9)
    box(ax, 1.25, 5.85, 1.40, 0.50, "输出 → 下一层", fs=7.8, fc=BG)

    for y0, y1 in [(0.95, 1.30), (1.75, 2.05), (2.60, 2.75),
                   (3.17, 3.55), (4.00, 4.30), (4.85, 5.00), (5.42, 5.85)]:
        arrow(ax, (cx, y0), (cx, y1), lw=0.9)

    # 残差旁路
    poly(ax, [(1.25, 1.12), (0.46, 1.12), (0.46, 2.95), (1.71, 2.95)])
    poly(ax, [(1.25, 3.38), (0.86, 3.38), (0.86, 5.20), (1.71, 5.20)])
    note(ax, 0.66, 1.95, "残差连接", fs=7.2, rot=90)

    # 右侧标注
    leader(ax, (2.72, 2.32), (2.94, 2.32))
    note(ax, 3.02, 2.32, "MHSA  $4d^2$", fs=8, color=INK, ha="left")
    leader(ax, (2.72, 4.57), (2.94, 4.57))
    note(ax, 3.02, 4.57, "FFN  $8d^2$", fs=8, color=INK, ha="left")
    leader(ax, (2.58, 1.52), (2.94, 1.52))
    note(ax, 3.02, 1.52, "LN 置于子层之前（Pre-LN）", fs=8, color=INK, ha="left")
    note(ax, 3.02, 0.68, "残差流：每层只做增量写入", fs=8, color=INK, ha="left")

    # 参数账本
    box(ax, 5.70, 2.30, 3.95, 3.12, "", fc=BG, ec=NAVY_L)
    note(ax, 5.92, 5.12, "参数账本（$d=4096$，$L=32$）", fs=8, color=INK, ha="left")
    leader(ax, (5.92, 4.92), (9.42, 4.92), color=LGRAY)
    rows = [("注意力 $4d^2$", "67M"), ("FFN $8d^2$", "134M"),
            ("每层 $12d^2$", "201M"), ("$L$ 层合计", "6.4B")]
    for k, (a, b) in enumerate(rows):
        y = 4.55 - k * 0.56
        note(ax, 5.92, y, a, fs=8, color=INK, ha="left")
        note(ax, 9.42, y, b, fs=8, color=NAVY, ha="right")
    note(ax, 5.92, 2.62, "不含嵌入与输出层", fs=7.2, ha="left")

    save(fig, "p2-transformer-block")

# ---------------------------------------------------------------- 2-2

def fig_p2_attention_cost():
    global SCALE
    SCALE = 1.0
    fig, ax = canvas(6.2, 3.35)
    fig.subplots_adjust(left=0.115, right=0.975, top=0.905, bottom=0.155)
    T = np.logspace(np.log10(420), np.log10(1.9e5), 500)
    attn = 5.0e5 * T ** 2
    lin = 1.0e9 * T

    ax.loglog(T, attn, color=NAVY, lw=1.7)
    ax.loglog(T, lin, color=GOLD, lw=1.7)

    ax.set_xlim(430, 2.1e5)
    ax.set_ylim(5e10, 3e16)
    ax.set_yticks([1e11, 1e12, 1e13, 1e14, 1e15, 1e16])
    ax.set_xticks([1e3, 4e3, 1.6e4, 6.4e4, 1.28e5])
    ax.set_xticklabels(["1K", "4K", "16K", "64K", "128K"])
    ax.minorticks_off()
    ax.tick_params(axis="y", labelsize=8.5)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.set_xlabel("序列长度 $T$（token）", fontsize=8.5)
    ax.set_ylabel("计算量（FLOPs，相对单位）", fontsize=8.5)

    for xv in (4e3, 1.28e5):
        ax.axvline(xv, color=LGRAY, lw=0.8, ls=(0, (4, 3)), zorder=1)

    ax.plot([2e3], [2e12], "o", ms=4.5, color=INK, zorder=5)
    ax.annotate("交叉点\n$T\\approx2$K", xy=(2e3, 2e12), xytext=(2.9e3, 1.1e11),
                fontsize=8.5, color=INK, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=GRAY,
                                shrinkA=1, shrinkB=3))

    ax.text(2.6e4, 2.4e14, "注意力 $\\propto T^2$", fontsize=8.5, color=NAVY,
            ha="left", va="top")
    ax.text(1.3e4, 2.8e12, "FFN 与投影 $\\propto T$", fontsize=8.5, color=GOLD,
            ha="left", va="top")
    ax.text(1.95e5, 3.0e11, "$T$=128K 时注意力约为线性项的 64 倍", fontsize=8.5,
            color=GRAY, ha="right", va="center")

    save(fig, "p2-attention-cost")

# ---------------------------------------------------------------- 3-1

def fig_p3_scaling_law():
    global SCALE
    SCALE = 1.0
    setup()
    fig, axs = plt.subplots(1, 3, figsize=(6.2, 2.92), sharey=True)
    fig.subplots_adjust(left=0.118, right=0.955, top=0.845, bottom=0.225,
                        wspace=0.30)

    N = np.logspace(8, 12, 200)
    D = np.logspace(10, 13, 200)
    C = np.logspace(19, 25, 200)
    LN = 12.66 * N ** -0.076
    LD = 26.60 * D ** -0.095
    LC = 26.67 * C ** -0.050

    specs = [
        (axs[0], N, LN, "参数量 $N$", "−0.076",
         [1e8, 1e10, 1e12], ["$10^{8}$", "$10^{10}$", "$10^{12}$"]),
        (axs[1], D, LD, "数据量 $D$（token）", "−0.095",
         [1e10, 1e11, 1e12, 1e13],
         ["$10^{10}$", "$10^{11}$", "$10^{12}$", "$10^{13}$"]),
        (axs[2], C, LC, "计算量 $C$（FLOPs）", "−0.050",
         [1e19, 1e21, 1e23, 1e25],
         ["$10^{19}$", "$10^{21}$", "$10^{23}$", "$10^{25}$"]),
    ]
    for ax, X, Y, xlab, slope, ticks, labs in specs:
        ax.loglog(X, Y, color=NAVY, lw=1.7)
        ax.set_xticks(ticks)
        ax.set_xticklabels(labs, fontsize=8.5)
        ax.set_xlim(ticks[0] * 0.70, ticks[-1] * 1.34)
        ax.minorticks_off()
        ax.tick_params(axis="y", labelsize=8.5)
        ax.set_xlabel(xlab, fontsize=8.5)
        ax.text(0.97, 0.93, "斜率 " + slope, transform=ax.transAxes,
                fontsize=8.5, color=NAVY, ha="right", va="top")

    axs[0].set_ylim(1.45, 3.25)
    axs[0].set_yticks([1.5, 2.0, 2.5, 3.0])
    axs[0].set_yticklabels(["1.5", "2.0", "2.5", "3.0"])
    axs[0].minorticks_off()
    axs[0].set_ylabel("验证损失 $L$（nats/token）", fontsize=8.5)
    fig.text(0.52, 0.945, "双对数坐标下近似为直线：规模每增 10 倍，损失按固定指数下降",
             fontsize=8.5, color=GRAY, ha="center", va="center")

    save(fig, "p3-scaling-law")

# ---------------------------------------------------------------- 3-2

def fig_p3_chinchilla():
    global SCALE
    SCALE = 1.18
    fig, ax = canvas(6.4, 3.7)

    E, A, B = 1.69, 406.4, 410.7
    al, be = 0.34, 0.28

    def loss(n, d):
        return E + A / n ** al + B / d ** be

    N = np.logspace(7.6, 12.12, 500)
    Cs = [1e20, 1e21, 1e22, 1e23]
    minima = []
    for C in Cs:
        D = C / (6 * N)
        m = (D > 3e9) & (D < 4e13)
        L = loss(N[m], D[m])
        ax.semilogx(N[m], L, color=NAVY, lw=1.2, alpha=0.95, zorder=3)
        k = int(np.argmin(L))
        minima.append((N[m][k], L[k]))

    mx = [p[0] for p in minima]
    my = [p[1] for p in minima]
    ax.plot(mx, my, ls=(0, (5, 3)), color=GOLD, lw=1.3, zorder=4)
    ax.plot(mx, my, "o", ms=3.4, color=GOLD, zorder=5)

    n70, d70 = 70e9, 1.4e12
    l70 = loss(n70, d70)
    ax.plot([n70], [l70], "o", ms=8.5, mfc="white", mec="none", zorder=6)
    ax.plot([n70], [l70], "o", ms=5, mfc="white", mec=RED, mew=1.2, zorder=7)
    ax.annotate("70B / 1.4T（$C\\approx6\\times10^{23}$）", xy=(n70, l70),
                xytext=(2.6e10, 1.745), fontsize=_fs(7.5), color=RED, ha="left",
                va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=RED,
                                shrinkA=2, shrinkB=4))

    ax.text(5.5e7, 3.24,
            "每条曲线：算力 $C=6ND$ 固定（$C=10^{20}\\sim10^{23}$）", fontsize=_fs(7.5),
            color=GRAY, ha="left", va="center")
    ax.text(5.5e7, 3.10, "虚线连接各曲线的最优点", fontsize=_fs(7.5), color=GOLD,
            ha="left", va="center")

    ax.set_xlim(4e7, 1.4e12)
    ax.set_ylim(1.70, 3.36)
    ax.set_xlabel("参数量 $N$")
    ax.set_ylabel("验证损失 $L$（nats/token）")
    ax.set_xticks([1e8, 1e9, 1e10, 1e11, 1e12])
    ax.set_xticklabels(["100M", "1B", "10B", "100B", "1T"])
    ax.set_yticks([1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0])
    ax.minorticks_off()

    save(fig, "p3-chinchilla")

# ---------------------------------------------------------------- 4-1

def fig_p4_data_pipeline():
    global SCALE
    SCALE = 1.25
    fig, ax = diagram(6.6, 3.1, xlim=(0, 10.3), ylim=(0, 4.84))

    stages = ["原始网页", "正文抽取", "语言识别", "去重", "质量过滤", "去污染", "配比"]
    keep = [100, 78, 72, 46, 21, 19, 19]
    n = len(stages)
    w, gap = 1.16, 0.245
    x0 = 0.30
    note(ax, x0, 4.56, "清洗流水线（从左到右）", fs=7.5, ha="left")

    for i, s in enumerate(stages):
        x = x0 + i * (w + gap)
        fc = NAVY_XL if i in (3, 5) else BG
        box(ax, x, 3.00, w, 0.72, s, fs=7.9, fc=fc)
        note(ax, x + w / 2, 3.92, f"{i + 1}", fs=7, color=GRAY)
        if i < n - 1:
            arrow(ax, (x + w + 0.01, 3.36), (x + w + gap - 0.01, 3.36), lw=0.9)

        h = 1.05 * keep[i] / 100.0
        ax.add_patch(Rectangle((x + w / 2 - 0.48, 1.55), 0.96, h,
                               facecolor=GOLD if keep[i] > 40 else GOLD_L,
                               edgecolor="none", zorder=3))
        note(ax, x + w / 2, 1.28, f"{keep[i]}%", fs=7.5,
             color=INK if keep[i] > 40 else GRAY)

    ax.plot([0.30, 10.05], [1.55, 1.55], color=LGRAY, lw=0.8, zorder=1)
    note(ax, 0.30, 0.72, "合计只剩约 19%：去重与质量过滤损失最大", fs=7.5,
         ha="left", color=INK)
    note(ax, 10.15, 0.72, "比例为示意值", fs=7.2, ha="right")

    save(fig, "p4-data-pipeline")

# ---------------------------------------------------------------- 4-2

def fig_p4_dedup():
    global SCALE
    SCALE = 1.10
    fig, ax = canvas(6.4, 3.4)
    x = np.logspace(10, 12.62, 400)
    ded = 1.66 + 1.15 * (x / 1e10) ** -0.15
    nod = 2.02 + 0.90 * (x / 1e10) ** -0.07 + 0.012 * np.sin(x / 1.1e11) \
        + 0.007 * np.sin(x / 3.7e10)

    ax.semilogx(x, nod, color=RED, lw=1.6)
    ax.semilogx(x, ded, color=TEAL, lw=1.8)

    ax.annotate("重复样本让收益提前饱和", xy=(1.6e11, 2.775),
                xytext=(3.2e10, 2.95), fontsize=7.5, color=RED, ha="left",
                va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=RED, shrinkA=2,
                                shrinkB=3))
    ax.text(1.02e10, 2.955, "未去重", fontsize=8, color=RED, ha="left",
            va="bottom")
    ax.text(3.2e12, 2.06, "去重后", fontsize=8, color=TEAL, ha="right", va="top")

    ax.set_xlim(9e9, 4.5e12)
    ax.set_ylim(1.95, 3.06)
    ax.set_xticks([1e10, 1e11, 1e12])
    ax.set_xticklabels(["10B", "100B", "1T"])
    ax.minorticks_off()
    ax.set_xlabel("累计训练 token 数")
    ax.set_ylabel("验证损失（nats/token）")

    save(fig, "p4-dedup")

# ---------------------------------------------------------------- 5-1

def fig_p5_bpe():
    global SCALE
    SCALE = 1.2
    fig, ax = diagram(6.5, 3.2, xlim=(0, 10), ylim=(0, 4.92))

    rows = [("low", 5), ("lower", 2), ("newest", 6), ("widest", 3)]
    note(ax, 0.30, 4.55, "① 统计相邻对频次", fs=7.5, ha="left")

    ys = [3.95, 3.22, 2.49, 1.76]
    hl = {("newest", 3), ("newest", 4), ("widest", 3), ("widest", 4)}
    for (word, f), y in zip(rows, ys):
        for k, ch in enumerate(word):
            x = 0.85 + k * 0.50
            hot = (word, k) in hl
            box(ax, x, y - 0.21, 0.42, 0.42, ch, fs=8.2,
                fc="white" if hot else BG,
                ec=RED if hot else NAVY_L, lw=1.15 if hot else 0.8)
        note(ax, 4.32, y, f"×{f}", fs=8, color=INK)

    note(ax, 0.30, 0.92,
         "红色为最高频相邻对 $(e,s)$：共 9 次，全语料一起替换", fs=7.5,
         ha="left", color=INK)

    # 右：词表增量
    note(ax, 5.45, 4.55, "② 更新词表并重新切分", fs=7.5, ha="left")
    box(ax, 5.45, 3.52, 2.35, 0.62, "$es$    id 256", fs=8.5, fc=GOLD_L, ec=GOLD)
    note(ax, 5.45, 3.26, "合并后重新切分", fs=7.2, ha="left")

    note(ax, 5.45, 2.72, "newest", fs=7.5, ha="left")
    seq = [("n", 0.42), ("e", 0.42), ("w", 0.42), ("es", 0.88), ("t", 0.42)]
    x = 6.22
    for ch, bw in seq:
        hot = ch == "es"
        box(ax, x, 2.50, bw, 0.44, ch, fs=8.2,
            fc=GOLD_L if hot else BG, ec=GOLD if hot else NAVY_L,
            lw=1.1 if hot else 0.8)
        x += bw + 0.10

    note(ax, 5.45, 1.90, "widest → w i d · es · t", fs=7.5, ha="left", color=INK)
    note(ax, 5.45, 1.24, "每轮只合并一个对，重复到词表达标", fs=7.2, ha="left")

    save(fig, "p5-bpe")

# ---------------------------------------------------------------- 5-2

def fig_p5_vocab():
    global SCALE
    SCALE = 1.0
    fig, ax = canvas(6.2, 3.45)
    fig.subplots_adjust(left=0.115, right=0.870, top=0.905, bottom=0.16)
    V = np.logspace(np.log10(8e3), np.log10(5e5), 400)
    seqlen = 30 + 1000 * (V / 3.2e4) ** -0.28
    emb = 2 * V * 4096 / 1e9

    ax.axvspan(3.2e4, 1.28e5, color=GOLD, alpha=0.12, zorder=0, lw=0)
    ax.semilogx(V, seqlen, color=TEAL, lw=1.8, zorder=3)
    ax.set_xlim(8e3, 5.5e5)
    ax.set_ylim(350, 1700)
    ax.set_xlabel("词表大小 $V$", fontsize=8.5)
    ax.set_ylabel("平均序列长度（token）", color=TEAL, fontsize=8.5)
    ax.tick_params(axis="y", colors=TEAL, labelsize=8.5)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.set_xticks([8e3, 3.2e4, 1e5, 5e5])
    ax.set_xticklabels(["8K", "32K", "100K", "500K"])
    ax.minorticks_off()

    ax2 = ax.twinx()
    ax2.plot(V, emb, color=GOLD, lw=1.6)
    ax2.set_ylim(0, 5.2)
    ax2.set_ylabel("嵌入参数（B）", color=GOLD, fontsize=8.5)
    ax2.tick_params(axis="y", colors=GOLD, labelsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.grid(False)

    ax.text(1.22e5, 1660, "常用区间 32K–128K", fontsize=8.5, color=GOLD,
            ha="right", va="top")
    ax.text(1.9e5, 470, "序列变短", fontsize=8.5, color=TEAL, ha="left",
            va="top")
    ax2.text(1.02e4, 1.15, "嵌入参数随 $V$ 线性增长", fontsize=8.5, color=GOLD,
             ha="left", va="center")

    save(fig, "p5-vocab")

# ---------------------------------------------------------------- 6-1

def fig_p6_rope():
    global SCALE
    SCALE = 1.05
    fig, ax = diagram(6.4, 4.14, xlim=(-1.35, 2.55), ylim=(-0.80, 1.72))
    ax.set_aspect("equal")

    ax.annotate("", xy=(2.42, 0), xytext=(-0.35, 0),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=GRAY,
                                mutation_scale=8))
    ax.annotate("", xy=(0, 1.66), xytext=(0, -0.22),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=GRAY,
                                mutation_scale=8))

    a_m, a_n = np.deg2rad(28), np.deg2rad(74)
    L_q, L_k = 1.95, 1.45
    q = np.array([L_q * np.cos(a_m), L_q * np.sin(a_m)])
    k = np.array([L_k * np.cos(a_n), L_k * np.sin(a_n)])

    arrow(ax, (0, 0), q, color=NAVY, lw=1.6, shrink=0)
    arrow(ax, (0, 0), k, color=GOLD, lw=1.6, shrink=0)

    def arc(r, t0, t1, color, lw=0.9, ls="-"):
        t = np.linspace(t0, t1, 80)
        ax.plot(r * np.cos(t), r * np.sin(t), color=color, lw=lw, ls=ls,
                zorder=2)

    arc(0.55, 0, a_m, NAVY)
    arc(0.88, 0, a_n, GOLD)
    arc(1.18, a_m, a_n, RED, lw=1.0, ls=(0, (3, 2)))

    note(ax, 0.72, 0.17, r"$m\theta$", fs=8.5, color=NAVY, ha="left")
    note(ax, 0.74, 0.66, r"$n\theta$", fs=8.5, color=GOLD, ha="left")
    note(ax, 0.60, 1.24, r"$\Delta\theta=(n-m)\theta$", fs=8.5, color=RED,
         ha="left")

    note(ax, q[0] + 0.06, q[1] + 0.09, r"$q_m$（位置 $m$）", fs=8, color=NAVY,
         ha="left", va="bottom")
    note(ax, k[0] + 0.10, k[1] + 0.10, r"$k_n$（位置 $n$）", fs=8, color=GOLD,
         ha="left", va="bottom")

    note(ax, -1.30, -0.40, r"$\langle q_m,\,k_n\rangle$ 只依赖角度差 $(n-m)\theta$",
         fs=8.5, color=INK, ha="left")
    note(ax, -1.30, -0.68, "同一次旋转同时作用于 $q$ 与 $k$，点积不变", fs=7.5,
         ha="left")

    save(fig, "p6-rope")

# ---------------------------------------------------------------- 6-2

def fig_p6_wavelength():
    global SCALE
    SCALE = 1.19
    fig, ax = canvas(6.4, 3.4)
    i = np.arange(1, 65)
    lam = 2 * np.pi * 10000 ** (2 * (i - 1) / 128)

    ax.semilogy(i, lam, color=NAVY, lw=1.8)
    ax.plot([1, 64], [2 * np.pi, lam[-1]], "o", ms=3.6, color=NAVY)
    ax.set_xlim(0, 68)
    ax.set_ylim(3.4, 3.0e5)
    ax.set_xlabel("维度对序号 $i$（共 64 对，$d=128$）")
    ax.set_ylabel("波长 $\\lambda_i=2\\pi/\\theta_i$")
    ax.set_yticks([10, 100, 1e3, 1e4, 1e5])
    ax.set_yticklabels(["$10$", "$10^2$", "$10^3$", "$10^4$", "$10^5$"])
    ax.set_xticks([1, 8, 16, 32, 48, 64])
    ax.minorticks_off()

    ax.text(1.7, 4.7, "$2\\pi$", fontsize=_fs(8), color=INK, ha="left", va="center")
    ax.annotate("上限 $10^4\\cdot2\\pi$", xy=(64, lam[-1]), xytext=(49, 1.05e5),
                fontsize=_fs(7.5), color=INK, ha="center", va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=GRAY, shrinkA=2,
                                shrinkB=3))

    ax.annotate("高频维：短波长\n编码局部位置", xy=(8, lam[7]), xytext=(2.0, 3.0e3),
                fontsize=_fs(7.5), color=NAVY, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=NAVY_L, shrinkA=3,
                                shrinkB=4))
    ax.annotate("低频维：长波长\n负责长距离", xy=(56.5, 1.75e4), xytext=(31, 26),
                fontsize=_fs(7.5), color=NAVY, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=NAVY_L, shrinkA=3,
                                shrinkB=4))

    save(fig, "p6-wavelength")

# ---------------------------------------------------------------- 7-1

def fig_p7_kv_cache():
    global SCALE
    SCALE = 1.0
    setup()
    fig, axs = plt.subplots(1, 2, figsize=(6.2, 3.5),
                            gridspec_kw={"width_ratios": [1.0, 1.18]})
    fig.subplots_adjust(left=0.115, right=0.975, top=0.855, bottom=0.315,
                        wspace=0.30)

    ax = axs[0]
    names = ["MHA", "GQA", "MQA"]
    heads = [64, 8, 1]
    bars = ax.bar(range(3), heads, width=0.55,
                  color=[NAVY, GOLD, TEAL], edgecolor="none", zorder=3)
    for b, v in zip(bars, heads):
        ax.text(b.get_x() + b.get_width() / 2, v + 2.0, str(v), ha="center",
                va="bottom", fontsize=8.5, color=INK)
    ax.set_xticks(range(3))
    ax.set_xticklabels(names, fontsize=8.5)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.set_ylim(0, 84)
    ax.set_ylabel("每层 KV 头数", fontsize=8.5)
    ax.set_title("KV 头数", fontsize=8.5)
    ax.grid(axis="x", visible=False)

    ax = axs[1]
    names = ["MHA", "GQA", "MQA", "MLA"]
    gb = [68.7, 8.6, 1.1, 2.4]
    cols = [NAVY, GOLD, TEAL, NAVY_XL]
    bars = ax.bar(range(4), gb, width=0.55, color=cols, edgecolor="none",
                  zorder=3)
    bars[3].set_hatch("////")
    bars[3].set_edgecolor(NAVY)
    bars[3].set_linewidth(0.5)
    for b, v in zip(bars, gb):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.8, f"{v:g}", ha="center",
                va="bottom", fontsize=8.5, color=INK)
    ax.set_xticks(range(4))
    ax.set_xticklabels(names, fontsize=8.5)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.set_ylim(0, 84)
    ax.set_ylabel("KV 缓存（GB）", fontsize=8.5)
    ax.set_title("32K 上下文缓存", fontsize=8.5)
    ax.grid(axis="x", visible=False)

    fig.text(0.5, 0.175, "70B：64 层，64 头，head_dim 128，fp16，上下文 32K",
             fontsize=8.5, color=GRAY, ha="center", va="center")
    fig.text(0.5, 0.075,
             "MHA 需 69 GB，单卡放不下；MLA 用 512 维潜向量压缩，"
             "无独立 KV 头，仅为 MHA 的 1/29",
             fontsize=8.5, color=GRAY, ha="center", va="center")

    save(fig, "p7-kv-cache")

# ---------------------------------------------------------------- 7-2

def fig_p7_flash():
    global SCALE
    SCALE = 1.03
    fig, ax = diagram(6.2, 3.57, xlim=(0, 10), ylim=(0, 5.75))

    # 左：完整矩阵
    note(ax, 0.22, 5.45, "标准注意力：一次算完", fs=8.5, ha="left")
    note(ax, 0.22, 5.05, "中间矩阵 $T\\times T$ 常驻 HBM", fs=8.5, ha="left")

    x0, y0, cell, n = 0.78, 1.62, 0.44, 6
    for r in range(n):
        for c in range(n):
            ax.add_patch(Rectangle((x0 + c * cell, y0 + r * cell), cell, cell,
                                   facecolor=NAVY_XL, edgecolor="white",
                                   lw=0.7, alpha=0.85, zorder=2))
    arrow(ax, (x0, y0 - 0.24), (x0 + n * cell, y0 - 0.24), lw=0.7, color=GRAY)
    note(ax, x0 + n * cell / 2, y0 - 0.46, "$T$", fs=8.5)
    arrow(ax, (x0 - 0.24, y0), (x0 - 0.24, y0 + n * cell), lw=0.7, color=GRAY)
    note(ax, x0 - 0.46, y0 + n * cell / 2, "$T$", fs=8.5, rot=90)
    note(ax, x0 + n * cell / 2, y0 + n * cell / 2, "$S$", fs=14, color=NAVY)
    note(ax, x0 + n * cell / 2, 0.82, "显存与带宽都是 $O(T^2)$", fs=8.5,
         color=RED)

    # 右：分块
    note(ax, 4.35, 5.45, "FlashAttention：分块搬运", fs=8.5, ha="left")
    note(ax, 4.35, 5.05, "每块算完即丢，不落 HBM", fs=8.5, ha="left")

    box(ax, 4.45, 3.30, 5.35, 1.42, "", fc="#EEF1F7", ec=NAVY_L)
    note(ax, 4.60, 4.52, "SRAM（片上，百 KB 级）", fs=8.5, ha="left")
    box(ax, 4.60, 3.70, 0.72, 0.50, "$Q_i$", fs=8.5, fc="white", ec=NAVY)
    box(ax, 5.55, 3.70, 1.00, 0.50, r"$K_j\,V_j$", fs=8.5, fc="white", ec=NAVY)
    box(ax, 6.82, 3.70, 1.05, 0.50, "$O_i$", fs=8.5, fc="white", ec=NAVY)
    arrow(ax, (5.35, 3.95), (5.52, 3.95), lw=0.8)
    arrow(ax, (6.58, 3.95), (6.79, 3.95), lw=0.8)
    note(ax, 5.20, 3.46, "在线 softmax，逐块累加 $O_i$", fs=8.5, ha="left")

    box(ax, 4.45, 0.60, 5.35, 1.22, "", fc=BG, ec=GRAY)
    note(ax, 4.60, 1.66, "HBM（显存，GB 级）", fs=8.5, ha="left")
    box(ax, 4.60, 0.78, 1.10, 0.50, "$Q_1 \\cdots Q_T$", fs=8.5, fc="white")
    box(ax, 5.95, 0.78, 1.15, 0.50, "$K/V$ 全部", fs=8.5, fc="white")
    box(ax, 7.35, 0.78, 1.00, 0.50, "$O$ 写回", fs=8.5, fc="white")

    arrow(ax, (5.15, 1.32), (4.98, 3.26), lw=0.9)
    arrow(ax, (6.52, 1.32), (6.06, 3.26), lw=0.9)
    arrow(ax, (7.70, 3.26), (7.92, 1.34), lw=0.9, color=GOLD)
    note(ax, 5.70, 2.52, "按块载入", fs=8.5)
    note(ax, 8.18, 2.52, "写回", fs=8.5, ha="left")

    note(ax, 7.10, 0.26, "外层循环 $i$ 扫 $Q$ 块，内层循环 $j$ 扫 $K/V$ 块",
         fs=8.5)

    save(fig, "p7-flash")

# ---------------------------------------------------------------- 8-1

def fig_p8_preln():
    global SCALE
    SCALE = 1.23
    fig, ax = diagram(6.4, 3.5, xlim=(0, 10), ylim=(0, 5.45))

    note(ax, 2.20, 5.10, "Post-LN", fs=8.5, color=INK)
    note(ax, 2.20, 4.82, "LN 在残差内", fs=7.2)
    note(ax, 7.20, 5.10, "Pre-LN", fs=8.5, color=INK)
    note(ax, 7.20, 4.82, "LN 在子层之前", fs=7.2)

    # Post-LN
    box(ax, 1.45, 0.45, 1.50, 0.45, "$x$", fs=8.2)
    box(ax, 1.45, 1.25, 1.50, 0.55, "子层", fs=8.2, fc=NAVY_XL, ec=NAVY)
    box(ax, 2.00, 2.15, 0.40, 0.40, "+", fs=9, rounded=0.2, ec=NAVY)
    box(ax, 1.45, 2.90, 1.50, 0.45, "LN", fs=8.2)
    box(ax, 1.45, 3.85, 1.50, 0.50, "输出", fs=8.2)
    for y0, y1 in [(0.90, 1.25), (1.80, 2.13), (2.55, 2.90), (3.35, 3.85)]:
        arrow(ax, (2.20, y0), (2.20, y1), lw=0.9)
    poly(ax, [(1.45, 1.06), (1.03, 1.06), (1.03, 2.35), (1.98, 2.35)])
    note(ax, 0.82, 1.72, "残差", fs=7, rot=90)

    # Pre-LN
    box(ax, 6.45, 0.45, 1.50, 0.45, "$x$", fs=8.2)
    box(ax, 6.45, 1.20, 1.50, 0.45, "LN", fs=8.2)
    box(ax, 6.45, 2.10, 1.50, 0.55, "子层", fs=8.2, fc=NAVY_XL, ec=NAVY)
    box(ax, 7.00, 3.00, 0.40, 0.40, "+", fs=9, rounded=0.2, ec=NAVY)
    box(ax, 6.45, 3.80, 1.50, 0.50, "输出", fs=8.2)
    for y0, y1 in [(0.90, 1.20), (1.65, 2.10), (2.65, 2.98), (3.40, 3.80)]:
        arrow(ax, (7.20, y0), (7.20, y1), lw=0.9)
    poly(ax, [(6.45, 0.70), (6.02, 0.70), (6.02, 3.20), (6.98, 3.20)])
    note(ax, 5.80, 2.10, "残差", fs=7, rot=90)

    # 梯度路径
    arrow(ax, (3.32, 4.35), (3.32, 0.32), color=RED, lw=1.0, ls=(0, (4, 2)))
    note(ax, 3.48, 2.30, "梯度须穿过 LN", fs=7.2, color=RED, rot=90)
    arrow(ax, (8.44, 4.30), (8.44, 0.32), color=RED, lw=1.0, ls=(0, (4, 2)))
    note(ax, 8.60, 2.30, "梯度沿残差直通", fs=7.2, color=RED, rot=90)

    note(ax, 5.00, 0.02, "$+$ 逐元素相加　·　子层 = 注意力 / FFN　·　红色虚线 = 反向传播",
         fs=7.2)
    ax.set_ylim(-0.22, 5.45)

    save(fig, "p8-preln")

# ---------------------------------------------------------------- 9-1

def fig_p9_moe():
    global SCALE
    SCALE = 1.16
    fig, ax = diagram(6.6, 3.56, xlim=(0, 10), ylim=(0.55, 5.95))

    note(ax, 0.25, 5.72, "MoE 层（8 专家，top-2）", fs=8, ha="left")

    ty = [4.42, 3.80, 3.18, 2.56]
    for k, y in enumerate(ty):
        box(ax, 0.25, y, 1.00, 0.45, f"$t_{k + 1}$", fs=8.2)
        arrow(ax, (1.27, y + 0.22), (1.74, 3.62 + (0.10 * (1.5 - k))), lw=0.7)

    box(ax, 1.76, 3.18, 1.15, 0.88, "Router\nsoftmax", fs=7.4, fc=NAVY_XL,
        ec=NAVY)
    note(ax, 0.75, 5.05, "输入 token", fs=7.2)

    ys = [5.35 - k * 0.63 for k in range(8)]
    act = {1, 6}
    for k, y in enumerate(ys):
        on = k in act
        box(ax, 3.35, y, 1.10, 0.44, f"$E_{k + 1}$", fs=8,
            fc=NAVY_XL if on else LGRAY,
            ec=NAVY if on else GRAY,
            tc=INK if on else GRAY, lw=0.9 if on else 0.7)
        if on:
            arrow(ax, (2.93, 3.55 if k == 1 else 3.45), (3.33, y + 0.22), lw=0.9)
            arrow(ax, (4.45, y + 0.22), (5.05, 3.42 if k == 1 else 3.20), lw=0.9)

    box(ax, 5.05, 3.11, 0.40, 0.40, "$\\Sigma$", fs=9, rounded=0.2, ec=NAVY)
    note(ax, 4.73, 4.18, "0.6", fs=7, color=NAVY,
         bbox=dict(fc="white", ec="none", pad=1.0))
    note(ax, 4.73, 2.49, "0.4", fs=7, color=NAVY,
         bbox=dict(fc="white", ec="none", pad=1.0))
    arrow(ax, (5.47, 3.31), (5.70, 3.31), lw=0.9)
    box(ax, 5.72, 2.98, 1.10, 0.66, "输出 $y$", fs=8.2)

    box(ax, 7.20, 4.45, 2.65, 1.30,
        "总参数 47B\n每 token 激活 13B\n激活比 28%", fs=8, fc=BG, ec=NAVY_L)
    note(ax, 7.20, 4.10, "其余 6 个专家不参与本次计算", fs=7.2, ha="left")
    box(ax, 7.20, 3.38, 0.36, 0.28, "", fc=LGRAY, ec=GRAY, lw=0.7)
    note(ax, 7.66, 3.52, "未激活（灰显）", fs=7.2, ha="left")
    note(ax, 7.20, 2.75, "激活参数只与 top-$k$ 有关，\n总参数决定容量", fs=7.5,
         ha="left")
    note(ax, 7.20, 1.95, "每个专家是一个独立的 FFN 子层", fs=7.2, ha="left")

    save(fig, "p9-moe")

# ---------------------------------------------------------------- 9-2

def fig_p9_load_balance():
    global SCALE
    SCALE = 1.0
    setup()
    fig, axs = plt.subplots(1, 2, figsize=(6.2, 3.55), sharey=True)
    fig.subplots_adjust(left=0.105, right=0.975, top=0.855, bottom=0.355,
                        wspace=0.10)

    x = np.arange(8)
    bal = np.array([12.6, 12.4, 12.5, 12.3, 12.7, 12.5, 12.6, 12.4])
    col = np.array([82.0, 3.0, 2.0, 4.0, 2.0, 3.0, 2.0, 2.0])

    ax = axs[0]
    ax.bar(x, bal, width=0.62, color=NAVY, zorder=3)
    ax.axhline(12.5, color=GOLD, lw=0.9, ls=(0, (4, 3)), zorder=4)
    ax.set_title("均衡：各专家约 12.5%", fontsize=8.5)
    ax.set_ylabel("分到的 token 占比（%）", fontsize=8.5)
    ax.text(-0.45, 16.0, "理想均衡线", fontsize=8.5, color=GOLD, ha="left",
            va="bottom")

    ax = axs[1]
    colors = [NAVY, NAVY] + [LGRAY] * 6
    edges = ["none", "none"] + [GRAY] * 6
    ax.bar(x, col, width=0.62, color=colors, edgecolor=edges, lw=0.6, zorder=3)
    ax.axhline(12.5, color=GOLD, lw=0.9, ls=(0, (4, 3)), zorder=4)
    ax.set_title("塌缩：token 挤向少数专家", fontsize=8.5)
    ax.text(-0.45, 85.5, "过载", fontsize=8.5, color=RED, ha="left", va="bottom")
    ax.text(7.45, 18.5, "其余专家闲置（≤4%）", fontsize=8.5, color=GRAY,
            ha="right", va="bottom")

    for ax in axs:
        ax.set_ylim(0, 95)
        ax.set_xticks(x)
        ax.set_xticklabels([f"$E_{i + 1}$" for i in x], fontsize=8.5)
        ax.tick_params(axis="y", labelsize=8.5)
        ax.set_xlabel("专家", fontsize=8.5)
        ax.grid(axis="x", visible=False)

    fig.text(0.5, 0.205,
             r"$L_{\mathrm{aux}} = \alpha \cdot N \cdot \sum_{i=1}^{N} f_i \cdot P_i$",
             fontsize=10.5, color=INK, ha="center", va="center")
    fig.text(0.5, 0.075,
             "分到专家 $i$ 的 token 比例 $f_i$ 与路由概率均值 $P_i$ "
             "同时偏大时，惩罚最重",
             fontsize=8.5, color=GRAY, ha="center", va="center")

    save(fig, "p9-load-balance")


# ---------------------------------------------------------------- entry

ALL = [
    fig_p1_attention_bottleneck,
    fig_p2_transformer_block,
    fig_p2_attention_cost,
    fig_p3_scaling_law,
    fig_p3_chinchilla,
    fig_p4_data_pipeline,
    fig_p4_dedup,
    fig_p5_bpe,
    fig_p5_vocab,
    fig_p6_rope,
    fig_p6_wavelength,
    fig_p7_kv_cache,
    fig_p7_flash,
    fig_p8_preln,
    fig_p9_moe,
    fig_p9_load_balance,
]


if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"\n{len(ALL)} figures done -> {FIGDIR}")
