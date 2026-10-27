# -*- coding: utf-8 -*-
"""第六部插图：Attention Residuals 与 DSpark。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

from figstyle import (NAVY, NAVY_L, NAVY_XL, GOLD, GOLD_L, INK, GRAY, LGRAY,
                      BG, GREEN, RED, TEAL, box, arrow, diagram, save, setup)


def poly(ax, pts, color=NAVY, lw=1.0, ls="-", arrow_head=True):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs[:-1] + [xs[-1]], ys[:-1] + [ys[-1]], color=color, lw=lw, ls=ls,
            solid_capstyle="round", zorder=2)
    if arrow_head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                    shrinkA=0, shrinkB=0, mutation_scale=9),
                    zorder=3)


def f_p26_attnres():
    setup()
    fig = plt.figure(figsize=(6.2, 2.9))
    fig.patch.set_facecolor("white")

    def frame(ax, title):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
        ax.set_title(title, fontsize=9.8, color=INK, pad=3)

    # (a) 标准残差
    ax = fig.add_axes([0.005, 0.02, 0.315, 0.86])
    frame(ax, "标准残差：等权累加")
    ys = [1.2, 3.0, 4.8, 6.6, 8.4]
    labels = ["嵌入", "注意力", "前馈", "注意力", "输出"]
    for y, t in zip(ys, labels):
        box(ax, 3.2, y - 0.55, 4.2, 1.1, t, fc=BG if t != "注意力" else "#EDF1F8", fs=9.2)
    for i in range(len(ys) - 1):
        arrow(ax, (5.3, ys[i] + 0.55), (5.3, ys[i + 1] - 0.55), color=NAVY, lw=1.0)
    poly(ax, [(3.2, ys[1]), (1.4, ys[1]), (1.4, ys[4]), (3.2, ys[4])],
         color=GRAY, lw=0.8)
    ax.text(0.75, 5.2, "权重恒为 1", rotation=90, fontsize=8.4, color=GRAY, va="center")

    # (b) Full AttnRes
    ax = fig.add_axes([0.34, 0.02, 0.315, 0.86])
    frame(ax, "Full AttnRes：对全部历史 softmax")
    hist_y = [1.2, 2.9, 4.6, 6.3, 8.0]
    hist_l = ["$v_0$", "$v_1$", "$v_2$", "$v_3$", "$v_4$"]
    weights = [0.9, 0.6, 0.35, 0.2, 0.1]
    for y, t, w in zip(hist_y, hist_l, weights):
        ax.add_patch(Circle((2.2, y), 0.13, facecolor=GOLD, edgecolor="none", zorder=4))
        ax.text(2.55, y, t, fontsize=8.6, color=INK, va="center")
    box(ax, 5.4, 3.9, 4.2, 1.5, "第 $l$ 层\n输入", fc="#EDF1F8", fs=9.2)
    for y, w in zip(hist_y, weights):
        arrow(ax, (2.36, y), (5.4, 4.65), color=GOLD, lw=0.4 + 2.2 * w, shrink=2)
    ax.text(0.55, 4.9, "权重由 $w_l$ 与内容决定", rotation=90, fontsize=8.4,
            color=GOLD, va="center")

    # (c) Block AttnRes
    ax = fig.add_axes([0.675, 0.02, 0.315, 0.86])
    frame(ax, "Block AttnRes：只读块表示")
    blocks = [(0.9, 1.9, "块 0"), (3.1, 1.9, "块 1"), (5.3, 1.9, "块 2"),
              (7.5, 1.6, "块 3")]
    for y, h, t in blocks:
        box(ax, 1.2, y, 3.4, h, t, fc="#EDF1F8", fs=9.0)
    box(ax, 6.3, 3.7, 3.4, 1.5, "第 $l$ 层\n输入", fc="#EDF1F8", fs=9.2)
    for y, h, _ in blocks:
        arrow(ax, (4.6, y + h / 2), (6.3, 4.45), color=GOLD, lw=1.1, shrink=2)
    ax.text(0.5, 4.9, "块数 $N\\ll L$", rotation=90, fontsize=8.4, color=GOLD,
            va="center")

    save(fig, "p26-attnres")


def f_p27_dspark():
    fig, ax = diagram(6.7, 2.9, xlim=(0, 10), ylim=(0, 5.0))

    box(ax, 0.15, 2.55, 1.45, 0.95, "前缀", fc=BG, fs=9.4)
    box(ax, 1.95, 2.55, 2.05, 0.95, "并行主干\n一次前向", fc="#EDF1F8", fs=9.0)
    box(ax, 4.35, 2.55, 1.95, 0.95, "草稿 token\n+ 置信度", fc="#F7F1E3", ec=GOLD, fs=9.0)
    box(ax, 6.75, 2.55, 1.75, 0.95, "目标模型\n一次验证", fc="#EDF1F8", fs=9.0)
    box(ax, 8.85, 2.55, 1.0, 0.95, "接受\n+1", fc="#EAF0EA", ec=GREEN, fs=9.0)

    box(ax, 1.95, 1.25, 2.05, 0.85, "顺序头\n块内依赖", fc="#EDF1F8", fs=9.0)
    box(ax, 6.75, 1.25, 1.75, 0.85, "调度器" + chr(10) + "按负载定长度", fc=BG, fs=9.0)

    arrow(ax, (1.6, 3.02), (1.95, 3.02), color=NAVY)
    arrow(ax, (4.0, 3.02), (4.35, 3.02), color=NAVY)
    arrow(ax, (2.97, 2.55), (2.97, 2.10), color=NAVY, lw=0.9)
    arrow(ax, (3.0, 1.25), (4.35, 2.55), color=GRAY, lw=0.9, rad=-0.25)
    arrow(ax, (7.62, 2.10), (7.62, 2.55), color=GOLD, lw=1.0)
    arrow(ax, (6.3, 3.02), (6.75, 3.02), color=NAVY)
    arrow(ax, (8.5, 3.02), (8.85, 3.02), color=GREEN)

    # 反馈：沿底部回到前缀，不穿过任何方框
    poly(ax, [(9.35, 2.55), (9.35, 0.45), (0.87, 0.45), (0.87, 2.55)],
         color=LGRAY, lw=0.9)
    ax.text(5.0, 0.18, "已接受的 token 并入前缀，进入下一轮", fontsize=8.4,
            color=GRAY, ha="center")

    ax.text(4.3, 3.95, "草稿：K 个位置一次给出", fontsize=8.4, color=GRAY, ha="center")
    ax.text(5.32, 0.95, "置信度 → 前缀存活概率", fontsize=8.4, color=GRAY, ha="center")

    save(fig, "p27-dspark")


if __name__ == "__main__":
    f_p26_attnres()
    f_p27_dspark()
    print("done")
