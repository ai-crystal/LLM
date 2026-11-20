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


FIGS = {
    "01": fig_01_four_ways,
    "02": fig_02_zero_stages,
    "03": fig_03_tp_split,
    "04": fig_04_bubble,
    "05": fig_05_memory_scale,
    "06": fig_06_overlap,
    "07": fig_07_formats,
    "08": fig_08_ckpt_interval,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
