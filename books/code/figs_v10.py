# -*- coding: utf-8 -*-
"""《大模型技术全景 · 训练系统篇》（第十卷）插图。

运行：
    python books/code/figs_v10.py          # 全部重画
    python books/code/figs_v10.py 05       # 只画指定编号

输出：
    books/v10-systems/images/NN/xxx.png
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L,
                      NAVY_XL, RED, TEAL, arrow, box, plt, setup)

# 小字用雅黑更实（Noto 在本机只注册到细体，缩到 132 mm 后发虚）
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v10-systems" / "images"

W = 5.2                    # 画布宽 5.2 in ≈ 132 mm
DPI = 288
FS = 8.5
FS_S = 7.2


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
                   weight=weight, zorder=z, linespacing=1.45)


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


# ---------------------------------------------------------------- 01 四种切法

def _panel(ax, x, y, w, h, label, accent=NAVY):
    box(ax, x, y, w, h, "", fc="white", ec=LGRAY, lw=0.8, rounded=0.10)
    ax.add_patch(Rectangle((x + 0.10, y + h - 0.52), 0.07, 0.30,
                           facecolor=accent, edgecolor="none", zorder=6))
    txt(ax, x + 0.26, y + h - 0.37, label, fs=FS - 0.3, color=INK,
        ha="left", weight="bold")


def _chips(ax, xs, y, w, h, texts, color, fs=6.4):
    for x, t in zip(xs, texts):
        box(ax, x, y, w, h, t, fc=tint(color, 0.12), ec=color, lw=0.7, fs=fs)


def fig_01_four_ways():
    """第 1 章：四种切法各自切什么、通信在哪一拍、代价是什么。"""
    fig, ax = canvas(3.55)

    pw, ph = 4.65, 3.18
    x1, x2 = 0.35, 5.40
    y1, y2 = 3.70, 0.30

    # ---- ① 数据并行
    _panel(ax, x1, y1, pw, ph, "① 数据并行：切批次", NAVY)
    xs = [x1 + 0.28 + i * 1.06 for i in range(4)]
    _chips(ax, xs, y1 + 1.72, 0.94, 0.86,
           ["整份\n模型", "整份\n模型", "整份\n模型", "整份\n模型"], NAVY)
    for i, x in enumerate(xs):
        note(ax, x + 0.47, y1 + 1.58, f"批 $b_{i}$", fs=6.2, color=GRAY)
        arrow(ax, (x + 0.47, y1 + 1.50), (x + 0.47, y1 + 1.14), lw=0.8)
    box(ax, x1 + 0.28, y1 + 0.66, 4.10, 0.44, "梯度全归约，每步一次",
        fc=tint(GOLD, 0.14), ec=GOLD, fs=FS - 1.2)
    note(ax, x1 + 2.33, y1 + 0.34, "通信量 ≈ 2S，与卡数几乎无关", fs=6.3)

    # ---- ② 张量并行
    _panel(ax, x2, y1, pw, ph, "② 张量并行：切一层里的矩阵", TEAL)
    bx, by, bw, bh = x2 + 0.28, y1 + 1.72, 4.10, 0.86
    for i in range(4):
        seg = bw / 4
        box(ax, bx + i * seg, by, seg - 0.02, bh, "",
            fc=tint(TEAL, 0.10 + 0.06 * (i % 2)), ec=TEAL, lw=0.7)
        note(ax, bx + i * seg + seg / 2, by + bh / 2, f"$W_{i}$", fs=7.0,
             color=INK)
    note(ax, bx + bw / 2, by - 0.22, "同一层的权重，四张卡各拿一块", fs=6.3)
    box(ax, bx, y1 + 0.66, bw, 0.44, "每层两次全归约（前向 + 反向）",
        fc=tint(GOLD, 0.14), ec=GOLD, fs=FS - 1.2)
    note(ax, x2 + 2.33, y1 + 0.34, "必须落在 NVLink 机内域，跨机撑不住", fs=6.3)

    # ---- ③ 流水线并行
    _panel(ax, x1, y2, pw, ph, "③ 流水线并行：切层", GOLD)
    xs = [x1 + 0.28 + i * 1.06 for i in range(4)]
    _chips(ax, xs, y2 + 1.72, 0.94, 0.86,
           ["1–20", "21–40", "41–60", "61–80"], GOLD, fs=7.2)
    for i in range(3):
        arrow(ax, (xs[i] + 0.96, y2 + 2.15), (xs[i + 1] - 0.02, y2 + 2.15),
              lw=0.8, color=GOLD)
    note(ax, x1 + 2.33, y2 + 1.56, "每台机器 20 层，层边界传激活（量 $b\\,s\\,d$）",
         fs=6.3)
    box(ax, x1 + 0.28, y2 + 0.66, 4.10, 0.44, "只在层边界通信，可以跨机",
        fc=tint(GOLD, 0.14), ec=GOLD, fs=FS - 1.2)
    note(ax, x1 + 2.33, y2 + 0.34, "代价是气泡：$(P-1)/(M+P-1)$", fs=6.3)

    # ---- ④ 专家并行
    _panel(ax, x2, y2, pw, ph, "④ 专家并行：切专家（MoE）", RED)
    box(ax, x2 + 0.28, y2 + 2.38, 4.10, 0.28,
        "token 按路由结果被打散", fc=tint(RED, 0.06), ec=tint(RED, 0.35),
        lw=0.6, fs=6.2, rounded=0.04)
    xs = [x2 + 0.28 + i * 1.06 for i in range(4)]
    for x in xs:
        arrow(ax, (x2 + 2.33, y2 + 2.36), (x + 0.47, y2 + 2.22),
              lw=0.7, color=RED, rad=0.0)
    _chips(ax, xs, y2 + 1.40, 0.94, 0.80,
           ["专家\n0", "专家\n1", "专家\n2", "专家\n3"], RED, fs=6.2)
    note(ax, x2 + 2.33, y2 + 1.22, "每个 token 只去其中 1–2 个专家", fs=6.3)
    box(ax, x2 + 0.28, y2 + 0.62, 4.10, 0.38, "all-to-all，每步一次",
        fc=tint(RED, 0.12), ec=RED, fs=FS - 1.2)
    note(ax, x2 + 2.33, y2 + 0.34, "代价是负载不均与容量丢弃", fs=6.3)

    save(fig, "01/four-ways.png")


# ---------------------------------------------------------------- 02 ZeRO

def fig_02_zero_stages():
    """第 2 章：7B 模型在 8 卡上，ZeRO 每升一级，每卡显存掉多少。"""
    setup()
    fig = plt.figure(figsize=(W, 2.42))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.175, 0.185, 0.775, 0.735])

    labels = ["朴素数据并行", "ZeRO-1", "ZeRO-2", "ZeRO-3"]
    w = [14, 14, 14, 1.75]
    g = [14, 14, 1.75, 1.75]
    o = [84, 10.5, 10.5, 10.5]
    ys = np.arange(len(labels))[::-1].astype(float)

    ax.barh(ys, w, 0.52, color=NAVY, edgecolor="white", linewidth=0.6,
            zorder=3, label="权重（BF16）")
    ax.barh(ys, g, 0.52, left=w, color=TEAL, edgecolor="white", linewidth=0.6,
            zorder=3, label="梯度（BF16）")
    ax.barh(ys, o, 0.52, left=np.array(w) + np.array(g), color=GOLD,
            edgecolor="white", linewidth=0.6, zorder=3,
            label="优化器状态（FP32 动量 + 方差 + 主权重）")

    for y, a, b, c in zip(ys, w, g, o):
        tot = a + b + c
        ax.text(tot + 1.6, y, f"{tot:g} GB", fontsize=FS - 0.4, color=INK,
                va="center", ha="left", zorder=6)

    ax.axvline(80, color=RED, lw=0.9, ls=(0, (4, 2.5)), zorder=5)
    ax.text(79, 3.62, "单卡 80 GB", fontsize=FS_S, color=RED, ha="right",
            va="center", zorder=6)

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=FS - 0.3)
    ax.set_xlim(0, 128)
    ax.set_ylim(-0.62, 3.82)
    ax.set_xlabel("每卡显存（GB，BF16 权重与梯度 + FP32 优化器状态，不含激活）",
                  fontsize=6.6, labelpad=3)
    ax.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(axis="y", visible=False)

    ax.legend(loc="lower right", frameon=False, fontsize=6.2,
              handlelength=1.2, handletextpad=0.4, labelspacing=0.28)

    save(fig, "02/zero-stages.png")


# ---------------------------------------------------------------- 03 张量并行

def fig_03_tp_split():
    """第 3 章：按列切不通信，按行切要一次全归约。"""
    fig, ax = canvas(2.62)

    bx, bw = 2.10, 2.06
    seg = bw / 4
    cx = 5.20

    # ---- 上半：按列切
    ay = 3.98
    txt(ax, 0.15, ay, "按列切", fs=FS - 0.5, color=NAVY, ha="left",
        weight="bold")
    box(ax, 1.05, ay - 0.44, 0.62, 0.88, "$X$", fc=tint(NAVY, 0.10),
        ec=NAVY_L, fs=7.5)
    top, bh = ay + 0.55, 1.10
    for i in range(4):
        ax.add_patch(Rectangle((bx + i * seg, top - bh), seg - 0.02, bh,
                               facecolor=tint(TEAL, 0.10 + 0.07 * (i % 2)),
                               edgecolor=TEAL, linewidth=0.7, zorder=4))
        note(ax, bx + i * seg + seg / 2, top - bh / 2, f"$A_{i}$", fs=6.6,
             color=INK)
    note(ax, bx + bw / 2, top - bh - 0.24, "权重按列切成 4 份", fs=6.2)
    box(ax, 4.62, ay - 0.30, 0.42, 0.60, "$=$", fc="white", ec="none", fs=8)
    for i in range(4):
        ax.add_patch(Rectangle((cx + i * seg, top - bh), seg - 0.02, bh,
                               facecolor=tint(GOLD, 0.10 + 0.07 * (i % 2)),
                               edgecolor=GOLD, linewidth=0.7, zorder=4))
        note(ax, cx + i * seg + seg / 2, top - bh / 2, f"$Y_{i}$", fs=6.6,
             color=INK)
    note(ax, cx + bw / 2, top - bh - 0.24, "输出天然分成 4 份", fs=6.2)
    txt(ax, cx + bw + 0.30, ay, "不用\n通信", fs=FS - 0.8, color=GREEN,
        ha="left")

    # ---- 下半：按行切
    ay2 = 1.62
    txt(ax, 0.15, ay2, "按行切", fs=FS - 0.5, color=GOLD, ha="left",
        weight="bold")
    box(ax, 1.05, ay2 - 0.55, 0.62, 1.10, "$X$", fc=tint(NAVY, 0.10),
        ec=NAVY_L, fs=7.5)
    rh = 0.30
    for i in range(4):
        ax.add_patch(Rectangle((bx, ay2 + 0.62 - (i + 1) * rh), bw - 0.02,
                               rh - 0.03,
                               facecolor=tint(TEAL, 0.10 + 0.07 * (i % 2)),
                               edgecolor=TEAL, linewidth=0.7, zorder=4))
        note(ax, bx + 0.26, ay2 + 0.62 - (i + 0.5) * rh, f"$B_{i}$", fs=5.9,
             color=INK)
    note(ax, bx + bw / 2, ay2 - 0.86, "权重按行切成 4 份", fs=6.2)

    box(ax, 4.62, ay2 - 0.30, 0.42, 0.60, "$=$", fc="white", ec="none", fs=8)
    for i in range(4):
        yy = ay2 + 0.45 - i * 0.30
        box(ax, cx, yy - 0.13, 0.92, 0.26, f"部分和 {i + 1}",
            fc=tint(GOLD, 0.16), ec=GOLD, lw=0.6, fs=6.0, rounded=0.04)
        arrow(ax, (cx + 0.94, yy), (cx + 1.34, ay2), lw=0.6, color=GRAY)
    box(ax, cx + 1.36, ay2 - 0.20, 0.42, 0.40, "$\\sum$", fc="white",
        ec=RED, lw=0.9, fs=8.5, rounded=0.20)
    arrow(ax, (cx + 1.80, ay2), (cx + 2.10, ay2), lw=0.9, color=RED)
    box(ax, cx + 2.12, ay2 - 0.24, 0.58, 0.48, "$Y$", fc=tint(RED, 0.10),
        ec=RED, fs=7.5)
    txt(ax, cx + 2.90, ay2, "一次\n全归约", fs=FS - 0.8, color=RED, ha="left")

    note(ax, 5.20, 0.20,
         "一层 Transformer 是“列、行、列、行”四次投影，恰好两次全归约",
         fs=6.6)

    save(fig, "03/tp-split.png")


# ---------------------------------------------------------------- 04 流水线气泡

def fig_04_bubble():
    """第 4 章：同样 6 个微批，流水线级数越多，空转格子越多。"""
    fig, ax = canvas(2.95)

    cw, gap, chh = 0.38, 0.03, 0.36
    x0 = 1.02

    def grid(P, M, y_base, label):
        total = 2 * (M + P - 1)
        txt(ax, x0, y_base + P * (chh + 0.05) + 0.14, label, fs=FS - 0.6,
            color=INK, ha="left", weight="bold")
        for s in range(P):
            yy = y_base + (P - 1 - s) * (chh + 0.05)
            note(ax, x0 - 0.10, yy + chh / 2, f"卡{s}", fs=5.9, ha="right",
                 color=GRAY)
            for m in range(total):
                kind = None
                if s <= m <= s + M - 1:
                    kind = "F"
                elif (M + P - 1) + (P - 1 - s) <= m <= (M + P - 1) + (P - 1 - s) + M - 1:
                    kind = "B"
                x = x0 + m * (cw + gap)
                if kind == "F":
                    fc, ec, lab, tc = tint(NAVY, 0.18), NAVY_L, "前", INK
                elif kind == "B":
                    fc, ec, lab, tc = tint(GOLD, 0.26), GOLD, "反", INK
                else:
                    fc, ec, lab, tc = "white", LGRAY, "", "white"
                ax.add_patch(Rectangle((x, yy), cw, chh, facecolor=fc,
                                       edgecolor=ec, linewidth=0.55, zorder=4,
                                       hatch="" if kind else "/////"))
                if lab:
                    note(ax, x + cw / 2, yy + chh / 2, lab, fs=5.0, color=tc)

    grid(2, 6, 4.42, "2 级流水线 × 6 个微批：气泡 1/7 ≈ 14%")
    grid(6, 6, 0.92, "6 级流水线 × 6 个微批：气泡 5/11 ≈ 45%")

    note(ax, x0, 0.62, "时间 →", fs=6.0, ha="left")
    note(ax, 5.20, 0.24,
         "阴影格是卡在等下一段数据：级数越多气泡越大，微批越多气泡越小",
         fs=6.3)

    save(fig, "04/bubble.png")


# ---------------------------------------------------------------- 05 显存账

def fig_05_memory_scale():
    """第 5 章：三种规模的状态显存总量，和 ZeRO-3 摊到卡上之后。"""
    setup()
    fig = plt.figure(figsize=(W, 2.55))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.215, 0.135, 0.640, 0.690])

    models = ["7B · 8 卡", "70B · 64 卡", "400B · 512 卡"]
    total = [112, 1120, 6400]
    per = [14, 17.5, 12.5]
    ys = np.arange(3)[::-1].astype(float)

    ax.set_xscale("log")
    ax.barh(ys + 0.20, total, 0.34, color=tint(NAVY, 0.85), edgecolor=NAVY,
            linewidth=0.8, zorder=3, label="全部状态（16 字节/参数）")
    ax.barh(ys - 0.20, per, 0.34, color=GOLD, edgecolor="#8A6A33",
            linewidth=0.7, zorder=3, label="ZeRO-3 摊到每张卡")

    for y, t_, p_ in zip(ys, total, per):
        ax.text(t_ * 1.13, y + 0.20, f"{t_:,} GB", fontsize=6.8, color=NAVY,
                va="center", zorder=6)
        ax.text(p_ * 1.13, y - 0.20, f"{p_:g} GB", fontsize=6.8,
                color="#8A6A33", va="center", zorder=6)

    ax.axvline(80, color=RED, lw=0.9, ls=(0, (4, 2.5)), zorder=5)
    ax.text(74, 2.52, "单卡 80 GB", fontsize=6.6, color=RED, ha="right",
            va="center", zorder=6)

    ax.set_yticks(ys)
    ax.set_yticklabels(models, fontsize=7.4)
    ax.set_xlim(6, 40000)
    ax.set_ylim(-1.15, 2.62)
    ax.set_xlabel("GB（对数轴；BF16 权重 + FP32 优化器状态，不含激活）",
                  fontsize=6.6, labelpad=2)
    ax.set_xticks([10, 100, 1000, 10000])
    ax.set_xticklabels(["10", "100", "1k", "10k"], fontsize=6.8)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(axis="y", visible=False)

    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.52, 0.985), ncol=2,
               frameon=False, fontsize=6.4, handlelength=1.3,
               handletextpad=0.5, columnspacing=1.8)

    save(fig, "05/memory-scale.png")


# ---------------------------------------------------------------- 06 通信重叠

def fig_06_overlap():
    """第 6 章：反向传播里的通信，串行做和分桶重叠的区别。"""
    fig, ax = canvas(2.15)

    bw_, bh_ = 1.25, 0.55

    def blk(x, y, text, fc, ec, fs=6.2, w=bw_):
        box(ax, x, y, w, bh_, text, fc=fc, ec=ec, lw=0.7, fs=fs)

    # ① 串行：算完再接通信
    txt(ax, 0.22, 3.86, "① 算完再传", fs=FS - 0.6, ha="left", weight="bold")
    y1 = 3.06
    x = 1.95
    for lab in ["第 $L$ 层", "第 $L{-}1$ 层", "第 $L{-}2$ 层"]:
        blk(x, y1, lab, tint(NAVY, 0.16), NAVY_L)
        x += bw_ + 0.06
    blk(x, y1, "梯度全归约", tint(RED, 0.16), RED, fs=6.2, w=2.05)
    note(ax, x + 2.15, y1 + bh_ / 2, "← 这段算力空转", fs=6.2, ha="left",
         color=RED)

    # ② 分桶：通信压进下一层的计算
    txt(ax, 0.22, 2.50, "② 分桶重叠", fs=FS - 0.6, ha="left", weight="bold")
    y2 = 1.72
    x = 1.95
    for lab in ["第 $L$ 层", "第 $L{-}1$ 层", "第 $L{-}2$ 层", "第 $L{-}3$ 层"]:
        blk(x, y2, lab, tint(NAVY, 0.16), NAVY_L)
        ax.add_patch(Rectangle((x + 0.42, y2 - 0.19), bw_ * 0.78, 0.15,
                               facecolor=tint(TEAL, 0.28), edgecolor=TEAL,
                               linewidth=0.5, zorder=5))
        x += bw_ + 0.06
    note(ax, 1.95 + 0.42 + 0.48, y2 - 0.30, "发上一层", fs=5.6, color=TEAL,
         ha="left")

    note(ax, 1.95, 1.10,
         "每个桶一算完就发，通信被后一层的计算盖住", fs=6.3, ha="left")
    note(ax, 5.20, 0.52,
         "反向是按层的顺序出结果的，越早算完的层越早能传——这就是重叠成立的前提",
         fs=6.4)

    save(fig, "06/overlap.png")


# ---------------------------------------------------------------- 07 数值格式

def fig_07_formats():
    """第 7 章：位宽怎么分配，决定了范围还是精度。"""
    fig, ax = canvas(1.80)

    rows = [
        ("FP32", 1, 8, 23, "最稳，最慢"),
        ("TF32", 1, 8, 10, "范围同 FP32"),
        ("BF16", 1, 8, 7, "不溢出，3 位十进制"),
        ("FP16", 1, 5, 10, "上界 65504"),
        ("FP8 E4M3", 1, 4, 3, "上界 448，易下溢"),
        ("FP8 E5M2", 1, 5, 2, "精度只够放梯度"),
    ]

    unit = 0.200
    x0 = 1.62
    y = 3.12
    dy = 0.36

    for name, s, e, m, remark in rows:
        total = s + e + m
        note(ax, x0 - 0.14, y, name, fs=6.6, ha="right", color=INK)
        x = x0
        for width, color, lab in [(s, NAVY, ""), (e, GOLD, f"{e}"),
                                 (m, TEAL, f"{m}")]:
            wpx = width * unit
            ax.add_patch(Rectangle((x, y - 0.115), wpx - 0.015, 0.23,
                                   facecolor=tint(color, 0.22), edgecolor=color,
                                   linewidth=0.6, zorder=4))
            if lab and wpx > 0.34:
                note(ax, x + wpx / 2, y, lab, fs=5.9, color=INK)
            x += wpx
        note(ax, 8.10, y, f"{total} 位", fs=6.0, ha="left", color=GRAY)
        note(ax, 8.62, y, remark, fs=5.9, ha="left", color=GRAY)
        y -= dy

    lx = 1.52
    for color, lab in [(NAVY, "符号 1 位"), (GOLD, "指数：决定范围"),
                       (TEAL, "尾数：决定精度")]:
        ax.add_patch(Rectangle((lx, 0.38), 0.20, 0.12,
                               facecolor=tint(color, 0.22), edgecolor=color,
                               linewidth=0.6, zorder=4))
        note(ax, lx + 0.26, 0.44, lab, fs=6.1, ha="left", color=GRAY)
        lx += 2.05

    save(fig, "07/formats.png")


# ---------------------------------------------------------------- 08 检查点间隔

def fig_08_ckpt_interval():
    """第 8 章：检查点太稀丢工作，太密写盘本身变成开销。"""
    setup()
    fig = plt.figure(figsize=(W, 2.78))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.115, 0.325, 0.855, 0.640])

    T = np.logspace(np.log10(0.02), np.log10(6), 400)

    def eff(T, tw, tr, F):
        return 1.0 - (tw / T + (T / 2 + tr) / F)

    curves = [
        (0.0083, 0.10, 2.0, "7B：写盘 30 秒、恢复 6 分钟、两天一故障", NAVY),
        (0.0830, 0.20, 2.0, "400B：写盘 5 分钟、恢复 12 分钟、两天一故障", GOLD),
    ]
    for tw, tr, F, lab, color in curves:
        y = eff(T, tw, tr, F)
        ax.plot(T, y, color=color, lw=1.3, label=lab, zorder=4)
        tstar = np.sqrt(2 * tw * F)
        ystar = eff(tstar, tw, tr, F)
        ax.plot([tstar], [ystar], "o", ms=4.2, color=color, zorder=6,
                markeredgecolor="white", markeredgewidth=0.7)
        ax.annotate(f"{tstar * 60:.0f} 分钟\n{ystar * 100:.0f}%",
                    xy=(tstar, ystar), xytext=(tstar * 1.35, ystar - 0.10),
                    fontsize=6.6, color=color, ha="left", va="top",
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.6))

    ax.set_xscale("log")
    ax.set_xlim(0.02, 6)
    ax.set_ylim(0.30, 1.0)
    ax.set_xlabel("检查点间隔（小时，对数轴）", fontsize=FS - 0.5, labelpad=3)
    ax.set_ylabel("有效算力占比", fontsize=FS - 0.5, labelpad=4)
    ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticklabels(["40%", "50%", "60%", "70%", "80%", "90%", "100%"],
                       fontsize=6.8)
    ax.set_xticks([0.02, 0.05, 0.1, 0.25, 0.5, 1, 2, 4])
    ax.set_xticklabels(["1.2 分", "3 分", "6 分", "15 分", "30 分", "1 时",
                        "2 时", "4 时"], fontsize=6.8)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="lower center", bbox_to_anchor=(0.50, -0.385), ncol=1,
              frameon=False, fontsize=6.2, handlelength=1.6,
              handletextpad=0.5, labelspacing=0.22)

    save(fig, "08/ckpt-interval.png")


# ------------------------------------------------- 09 减项阶梯（第 1 章）

def fig_09_memory_waterfall():
    """第 1 章：7B 在单卡上逐项减，哪一级跨过 80 GB。"""
    setup()
    fig = plt.figure(figsize=(W, 2.62))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.345, 0.235, 0.610, 0.660])

    labels = ["16 字节\nBF16+FP32 主权重", "12 字节\n去主权重",
              "8 字节\n动量方差降 BF16", "6 字节\n8 位优化器",
              "2 字节\n只剩权重"]
    vals = [112, 84, 56, 42, 14]
    colors = [RED, RED, GOLD, TEAL, NAVY_L]
    ys = np.arange(len(vals))[::-1].astype(float)

    ax.barh(ys, vals, 0.56, color=colors, edgecolor="white", linewidth=0.7,
            zorder=3)
    for y, v, prev in zip(ys, vals, [None] + vals[:-1]):
        ax.text(v + 2.5, y, f"{v} GB", fontsize=7.0, color=INK,
                va="center", ha="left", zorder=6)
        if prev:
            ax.text(v - 3.0, y, f"−{prev - v}", fontsize=6.4, color="white",
                    va="center", ha="right", zorder=7)

    ax.axvline(80, color=INK, lw=0.9, ls=(0, (4, 2.5)), zorder=5)
    ax.text(78, 4.62, "单卡 80 GB", fontsize=6.5, color=INK, ha="right",
            va="center", zorder=6)

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=6.3)
    ax.set_xlim(0, 128)
    ax.set_ylim(-0.62, 4.86)
    ax.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax.set_xlabel("7B 模型的参数相关显存（GB，批与激活另计）", fontsize=6.6,
                  labelpad=2)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)

    save(fig, "01/memory-waterfall.png")


# ------------------------------------------------- 10 气泡与微批数（第 4 章）

def fig_10_bubble_curve():
    """第 4 章：1F1B 与交错式 1F1B，气泡随微批数怎么降。"""
    setup()
    fig = plt.figure(figsize=(W, 2.62))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.135, 0.235, 0.825, 0.640])

    M = np.arange(1, 65)
    curves = [
        (8, 1, "8 段，1F1B", NAVY, "-"),
        (8, 8, "8 段，交错 8 份", NAVY, (0, (4, 2))),
        (16, 1, "16 段，1F1B", GOLD, "-"),
        (16, 8, "16 段，交错 8 份", GOLD, (0, (4, 2))),
    ]
    for P, v, lab, color, ls in curves:
        y = (P - 1) / (M * v + P - 1) * 100
        ax.plot(M, y, color=color, lw=1.25, ls=ls, label=lab, zorder=4)

    ax.axhline(10, color=RED, lw=0.8, ls=(0, (2, 2)), zorder=3)
    ax.text(63, 11.6, "10%", fontsize=6.2, color=RED, ha="right")

    ax.set_xlim(1.6, 64)
    ax.set_ylim(0, 80)
    ax.set_xlabel("微批数 $M$", fontsize=FS - 0.6, labelpad=3)
    ax.set_ylabel("气泡占比", fontsize=FS - 0.6, labelpad=3)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_yticklabels(["0", "20%", "40%", "60%", "80%"], fontsize=6.8)
    ax.set_xticks([2, 4, 8, 16, 32, 64])
    ax.set_xticklabels(["2", "4", "8", "16", "32", "64"], fontsize=6.8)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="upper right", frameon=False, fontsize=6.1,
              handlelength=1.8, handletextpad=0.4, labelspacing=0.25,
              ncol=2, columnspacing=1.2)

    save(fig, "04/bubble-curve.png")


# ------------------------------------------------- 11 显存四块（第 5 章）

def fig_11_memory_parts():
    """第 5 章：不切分时，四个模型的状态与激活各占多少。"""
    setup()
    fig = plt.figure(figsize=(W, 2.48))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.185, 0.300, 0.760, 0.585])

    models = ["1.5B", "7B", "70B", "405B"]
    w = [3, 14, 140, 810]
    g = [3, 14, 140, 810]
    o = [18, 84, 840, 4860]
    a = [1.0, 18.5, 92.6, 291.0]
    ys = np.arange(len(models))[::-1].astype(float)
    left = np.zeros(len(models))

    for vals, color, lab in [(w, NAVY, "权重"), (g, TEAL, "梯度"),
                             (o, GOLD, "优化器状态"), (a, RED, "激活")]:
        ax.barh(ys, vals, 0.50, left=left, color=color, edgecolor="white",
                linewidth=0.6, zorder=3, label=lab)
        left = left + np.array(vals)

    for y, v in zip(ys, left):
        ax.text(v * 1.15, y, f"{v:,.0f} GB", fontsize=6.8, color=INK,
                va="center", ha="left", zorder=6)

    ax.axvline(80, color=INK, lw=0.9, ls=(0, (4, 2.5)), zorder=5)
    ax.text(76, 3.70, "单卡 80 GB", fontsize=6.2, color=INK, ha="right",
            va="center", zorder=6)

    ax.set_xscale("log")
    ax.set_xlim(1.2, 40000)
    ax.set_ylim(-0.75, 3.62)
    ax.set_yticks(ys)
    ax.set_yticklabels(models, fontsize=6.8)
    ax.set_xlabel("单卡显存（GB，对数轴；不切分、批 1、序列 4096）",
                  fontsize=6.5, labelpad=2)
    ax.set_xticks([10, 100, 1000, 10000])
    ax.set_xticklabels(["10", "100", "1000", "10000"], fontsize=6.6)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.52, -0.245), ncol=4,
              frameon=False, fontsize=6.2, handlelength=1.1,
              handletextpad=0.35, columnspacing=1.4)

    save(fig, "05/memory-parts.png")


# ------------------------------------------------- 12 环与树（第 6 章）

def fig_12_ring_tree():
    """第 6 章：小消息看延迟、大消息看带宽：环与树的交叉点。"""
    setup()
    fig = plt.figure(figsize=(W, 2.62))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.140, 0.235, 0.820, 0.640])

    N = np.arange(4, 1025)
    Wb = 25e9            # 25 GB/s
    L = 8e-6             # 单跳固定延迟 8 µs

    def t_ring(S):
        return (2 * S * (N - 1) / N / Wb + 2 * (N - 1) * L) * 1e3

    def t_tree(S):
        return (S * np.log2(N) / Wb + 2 * np.log2(N) * L) * 1e3

    for S, lab, color in [(4e6, "4 MB", NAVY), (1e8, "100 MB", GOLD)]:
        ax.plot(N, t_ring(S), color=color, lw=1.3, ls="-", zorder=4,
                label=f"环，{lab}")
        ax.plot(N, t_tree(S), color=color, lw=1.3, ls=(0, (4, 2)), zorder=4,
                label=f"树，{lab}")

    # 4 MB 的交叉点：延迟项占优，卡一多树就胜出
    diff = t_ring(4e6) - t_tree(4e6)
    idx = int(np.argmin(np.abs(diff)))
    n0 = N[idx]
    ax.plot([n0], [t_ring(4e6)[idx]], "o", ms=4.0, color=RED, zorder=7,
            markeredgecolor="white", markeredgewidth=0.7)
    ax.annotate(f"{n0} 卡附近相交", xy=(n0, t_ring(4e6)[idx]),
                xytext=(n0 * 1.05, 0.20), fontsize=6.3, color=RED,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(4, 1024)
    ax.set_ylim(0.05, 60)
    ax.set_xlabel("卡数 $N$（全归约，每卡梯度 $S$）", fontsize=6.6, labelpad=3)
    ax.set_ylabel("一次全归约耗时（ms）", fontsize=6.6, labelpad=3)
    ax.set_xticks([8, 32, 128, 512])
    ax.set_xticklabels(["8", "32", "128", "512"], fontsize=6.8)
    ax.set_yticks([0.1, 1, 10])
    ax.set_yticklabels(["0.1", "1", "10"], fontsize=6.8)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="lower right", frameon=False, fontsize=6.1, ncol=2,
              handlelength=1.9, handletextpad=0.4, columnspacing=1.0,
              labelspacing=0.25)

    save(fig, "06/ring-tree.png")


# ------------------------------------------------- 13 恢复时间（第 8 章）

def fig_13_recovery():
    """第 8 章：一次故障到重新开跑，时间花在哪四段。"""
    setup()
    fig = plt.figure(figsize=(W, 2.35))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.215, 0.290, 0.740, 0.600])

    models = ["1.5B·8 卡", "7B·8 卡", "70B·64 卡", "405B·256 卡"]
    detect = [0.5, 0.5, 1.0, 1.5]
    sched = [0.7, 0.8, 1.5, 3.0]
    read = [0.2, 0.6, 2.1, 6.5]
    redo = [0.3, 1.2, 4.0, 9.0]
    ys = np.arange(len(models))[::-1].astype(float)

    left = np.zeros(len(models))
    for vals, color, lab in [(detect, NAVY_L, "发现"), (sched, TEAL, "隔离与调度"),
                             (read, GOLD, "读检查点"),
                             (redo, RED, "回放到最新")]:
        ax.barh(ys, vals, 0.52, left=left, color=color, edgecolor="white",
                linewidth=0.6, zorder=3, label=lab)
        left = left + np.array(vals)

    for y, v in zip(ys, left):
        ax.text(v + 0.28, y, f"{v:.1f} 分", fontsize=6.8, color=INK,
                va="center", ha="left", zorder=6)

    ax.set_yticks(ys)
    ax.set_yticklabels(models, fontsize=6.6)
    ax.set_xlim(0, 24)
    ax.set_ylim(-0.60, 3.60)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("一次故障后恢复正常训练的时间（分钟）", fontsize=6.6,
                  labelpad=2)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.50, -0.30), ncol=4,
              frameon=False, fontsize=6.1, handlelength=1.1,
              handletextpad=0.35, columnspacing=1.2)

    save(fig, "08/recovery.png")


# ------------------------------------------------- 14 最小卡数（第 1 章）

def fig_14_min_cards():
    """第 1 章：三档规模、三档精度，各要多少张 80 GB 卡才装得下。"""
    fig, ax = canvas(2.66)

    cols = [(3.42, "16 字节"), (6.00, "12 字节"), (8.57, "9 字节")]
    for xc, lab in cols:
        txt(ax, xc, 4.92, lab, fs=FS - 0.4, weight="bold")

    rows = [
        ("400B", [("6400 GB", 107), ("4860 GB", 81), ("3645 GB", 60)]),
        ("70B", [("1120 GB", 19), ("840 GB", 14), ("630 GB", 11)]),
        ("7B", [("112 GB", 2), ("84 GB", 2), ("63 GB", 2)]),
    ]

    def shade(n):
        if n <= 4:
            return tint(NAVY, 0.10), INK
        if n <= 24:
            return tint(NAVY, 0.34), INK
        return tint(NAVY, 0.72), "white"

    for i, (name, cells) in enumerate(rows):
        y = 3.18 - i * 1.10
        txt(ax, 1.05, y + 0.50, name, fs=FS, weight="bold")
        for (xc, _), (g, n) in zip(cols, cells):
            fc, tc = shade(n)
            box(ax, xc - 1.24, y, 2.48, 1.00, fc=fc, ec="white", lw=1.0)
            txt(ax, xc, y + 0.66, g, fs=5.9, color=tc)
            txt(ax, xc, y + 0.29, f"{n} 张", fs=FS - 0.2, color=tc,
                weight="bold")

    note(ax, 5.05, 0.60,
         "卡数 = 参数相关显存 ÷ 60 GB（20 GB 留给激活、缓冲与碎片）",
         fs=6.3)
    note(ax, 5.05, 0.22,
         "同一行三列看“降精度能省几张卡”，同一列三行看规模翻几倍", fs=6.1)

    save(fig, "01/min-cards.png")


# ------------------------------------------------- 15 省显存的价钱（第 5 章）

def fig_15_price_of_gb():
    """第 5 章：每种省显存的手段，每省 1 GB 要付多少时间。"""
    setup()
    fig = plt.figure(figsize=(W, 2.58))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.135, 0.250, 0.830, 0.650])

    pts = [
        ("全量重计算", 18, 33, RED),
        ("8 位优化器", 42, 3, GOLD),
        ("ZeRO-2（8 卡）", 73.5, 0.5, NAVY),
        ("优化器状态卸载", 84, 60, RED),
        ("微批 4→1", 58, 22, GOLD),
        ("序列 8K→4K", 27, 1.5, NAVY),
    ]
    for lab, gb, pct, c in pts:
        ax.plot([gb], [pct], "o", ms=5.0, color=c, markeredgecolor="white",
                markeredgewidth=0.7, zorder=6)

    offs = {
        "全量重计算": (20.5, 38.0, "left"),
        "8 位优化器": (43, 8.2, "center"),
        "ZeRO-2（8 卡）": (73, 6.0, "center"),
        "优化器状态卸载": (81, 65.0, "right"),
        "微批 4→1": (60, 27.0, "left"),
        "序列 8K→4K": (27, 8.5, "center"),
    }
    for lab, gb, pct, c in pts:
        xt, yt, ha = offs[lab]
        ax.annotate(lab, xy=(gb, pct), xytext=(xt, yt),
                    fontsize=6.4, color=c, ha=ha, va="center")

    ax.fill_between([14, 110], [-3, -3], [12, 12], color=tint(NAVY, 0.07),
                    zorder=0, lw=0)
    ax.text(15.5, 15.8, "便宜区：多花不到一成时间", fontsize=6.2, color=NAVY,
            ha="left", va="center", zorder=7)

    ax.set_xscale("log")
    ax.set_xlim(14, 110)
    ax.set_ylim(-3, 68)
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.set_xticklabels(["20", "40", "60", "80", "100"], fontsize=6.8)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_yticklabels(["0", "20%", "40%", "60%"], fontsize=6.8)
    ax.set_xlabel("调一次能省下的显存（GB，7B 口径）", fontsize=6.6, labelpad=3)
    ax.set_ylabel("多花的训练时间", fontsize=6.6, labelpad=3)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    save(fig, "05/price-of-gb.png")


# ------------------------------------------------- 16 故障树（第 8 章）

def fig_16_fault_tree():
    """第 8 章：一次非计划停机往上追，四类原因各占多少、先看什么。"""
    fig, ax = canvas(2.55)

    box(ax, 4.05, 4.30, 2.30, 0.58, "作业非计划停机", fc=tint(RED, 0.12),
        ec=RED, fs=FS - 0.2, weight="bold")

    ax.plot([5.20, 5.20], [4.30, 3.86], color=GRAY, lw=0.8, zorder=1)
    ax.plot([1.30, 9.10], [3.86, 3.86], color=GRAY, lw=0.8, zorder=1)

    br = [
        (1.30, "显卡硬件", "四到五成", "Xid 与 ECC 计数", "先隔离再换卡"),
        (3.90, "网络", "两成", "端口错误计数", "看尾延迟分布"),
        (6.50, "节点与存储", "两成", "dmesg 与读超时", "换挂载点重试"),
        (9.10, "软件", "一成", "py-spy 抓栈", "查进程组规模"),
    ]
    for i, (xc, name, share, hint1, hint2) in enumerate(br):
        ax.plot([xc, xc], [3.86, 3.44], color=GRAY, lw=0.8, zorder=1)
        box(ax, xc - 1.12, 2.66, 2.24, 0.74,
            f"{name}\n{share}", fc=tint(NAVY, 0.10 + 0.03 * i),
            ec=NAVY_L, fs=6.6)
        note(ax, xc, 2.30, hint1, fs=5.9)
        note(ax, xc, 1.96, hint2, fs=5.9, color=NAVY)

    note(ax, 5.20, 1.40,
         "每一类都有自己的“第一眼看什么”，混在一起查会在四类之间来回跳",
         fs=6.3)
    ax.plot([1.30, 9.10], [1.10, 1.10], color=LGRAY, lw=0.7, zorder=1)
    note(ax, 5.20, 0.70,
         "软件类不占多数，却占了多数“第一次判断错误”：它能模仿前三类的全部症状",
         fs=6.2)

    save(fig, "08/fault-tree.png")


# ------------------------------------------------- 17 延迟占比（第 6 章）

def fig_17_latency_share():
    """第 6 章：消息越小、卡越多，全归约的时间越是被固定延迟吃掉。"""
    setup()
    fig = plt.figure(figsize=(W, 2.58))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.140, 0.240, 0.825, 0.655])

    S = np.logspace(0, 5, 240) * 1e6          # 每卡载荷，字节

    def share(N, alpha, Wb):
        delay = 2 * (N - 1) * alpha
        transfer = 2 * S * (N - 1) / N / Wb
        return delay / (delay + transfer) * 100

    curves = [
        (8, 10e-6, 300e9, "8 卡，机内", NAVY),
        (64, 25e-6, 50e9, "64 卡，跨机", GOLD),
        (512, 50e-6, 50e9, "512 卡，跨机", RED),
    ]
    for N, a, w, lab, c in curves:
        ax.plot(S / 1e6, share(N, a, w), color=c, lw=1.3, label=lab, zorder=4)

    ax.axhline(10, color=GRAY, lw=0.8, ls=(0, (2, 2)), zorder=3)
    ax.text(1.25, 13, "一成", fontsize=6.2, color=GRAY, ha="left")

    for N, a, w, lab, c in curves:
        y = share(N, a, w)
        idx = int(np.argmin(np.abs(y - 10)))
        ax.plot([S[idx] / 1e6], [10], "o", ms=3.6, color=c, zorder=7,
                markeredgecolor="white", markeredgewidth=0.6)

    ax.annotate("1.3 GB", xy=(1300, 10), xytext=(1600, 22),
                fontsize=6.3, color=RED, ha="left", va="center")
    ax.annotate("0.2 GB", xy=(216, 10), xytext=(30, 16),
                fontsize=6.3, color=NAVY, ha="left", va="center")
    ax.annotate("0.9 GB", xy=(870, 10), xytext=(150, 40),
                fontsize=6.3, color=GOLD, ha="left", va="center")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 1e5)
    ax.set_ylim(0.2, 100)
    ax.set_xlabel("每卡载荷 $S$（MB，对数轴）", fontsize=6.6, labelpad=3)
    ax.set_ylabel("延迟占全归约的比例", fontsize=6.6, labelpad=3)
    ax.set_xticks([1, 10, 100, 1000, 10000])
    ax.set_xticklabels(["1", "10", "100", "1000", "10000"], fontsize=6.8)
    ax.set_yticks([1, 10, 100])
    ax.set_yticklabels(["1%", "10%", "100%"], fontsize=6.8)
    ax.minorticks_off()
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="lower left", frameon=False, fontsize=6.1,
              handlelength=1.9, handletextpad=0.4, labelspacing=0.25)

    save(fig, "06/latency-share.png")


FIGS = {
    "01": fig_01_four_ways,
    "02": fig_02_zero_stages,
    "03": fig_03_tp_split,
    "04": fig_04_bubble,
    "05": fig_05_memory_scale,
    "06": fig_06_overlap,
    "07": fig_07_formats,
    "08": fig_08_ckpt_interval,
    "09": fig_09_memory_waterfall,
    "10": fig_10_bubble_curve,
    "11": fig_11_memory_parts,
    "12": fig_12_ring_tree,
    "13": fig_13_recovery,
    "14": fig_14_min_cards,
    "15": fig_15_price_of_gb,
    "16": fig_16_fault_tree,
    "17": fig_17_latency_share,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
