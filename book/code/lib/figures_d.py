# -*- coding: utf-8 -*-
"""第 16 章插图：榜单定位图与成本-性能前沿。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from figstyle import (NAVY, NAVY_L, NAVY_XL, GOLD, GOLD_L, INK, GRAY, LGRAY,
                      BG, GREEN, RED, TEAL, canvas, diagram, save, setup)


def f_p16_map():
    setup()
    fig, ax = plt.subplots(figsize=(6.0, 3.9))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.12)

    ax.set_xlim(0.5, 10.5)
    ax.set_ylim(0.5, 10.5)
    ax.set_xlabel("任务离真实工作的距离  →", fontsize=9.6)
    ax.set_ylabel("评测的可复现性  →", fontsize=9.6)
    ax.set_xticks([]); ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_color(LGRAY)

    ax.add_patch(Rectangle((6.2, 6.2), 4.2, 4.2, facecolor=GREEN, alpha=0.05, lw=0))
    ax.text(8.3, 10.15, "真实且可复现", fontsize=9.2, color=GREEN, ha="center")
    ax.text(2.2, 10.15, "可复现，但离工作远", fontsize=9.2, color=GRAY, ha="center")
    ax.text(8.4, 1.0, "真实，但难复现", fontsize=9.2, color=GRAY, ha="center")

    pts = [
        ("MMLU 类", 1.9, 9.0, NAVY, (8, 6)),
        ("HLE", 2.9, 8.5, NAVY, (8, -10)),
        ("ARC-AGI-2", 3.6, 9.3, NAVY, (8, 4)),
        ("LiveBench", 5.0, 9.4, TEAL, (8, 4)),
        ("HELM", 5.4, 8.0, TEAL, (-10, -14)),
        ("LMArena", 5.4, 3.0, GOLD, (8, 4)),
        ("SWE-bench", 7.4, 7.4, RED, (8, 2)),
        ("τ-bench", 7.9, 6.2, RED, (8, -8)),
        ("Terminal-Bench", 8.5, 5.3, RED, (8, -2)),
        ("OSWorld", 8.9, 4.3, RED, (8, -10)),
        ("GDPval", 9.5, 3.4, GOLD, (-12, -14)),
    ]
    for name, x, y, c, off in pts:
        ax.scatter([x], [y], s=46, color=c, edgecolor="white", linewidth=0.6, zorder=4)
        ha = "right" if off[0] < 0 else "left"
        ax.annotate(name, (x, y), xytext=off, textcoords="offset points",
                    fontsize=9.2, color=INK, zorder=5, ha=ha)

    ax.annotate("", xy=(10.3, 6.1), xytext=(0.8, 6.1),
                arrowprops=dict(arrowstyle="-", color=LGRAY, lw=0.8, ls=(0, (3, 3))))
    ax.annotate("", xy=(6.1, 10.3), xytext=(6.1, 0.8),
                arrowprops=dict(arrowstyle="-", color=LGRAY, lw=0.8, ls=(0, (3, 3))))

    save(fig, "p16-leaderboard-map")


def f_p16_cost():
    setup()
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    fig.subplots_adjust(left=0.10, right=0.975, top=0.9, bottom=0.16)

    # 示意数据：横轴成本（美元/百万 token，对数），纵轴综合得分
    models = [
        ("A", 0.12, 52), ("B", 0.28, 60), ("C", 0.45, 63), ("D", 1.1, 68),
        ("E", 2.4, 71), ("F", 4.8, 66), ("G", 9.5, 72), ("H", 0.9, 58),
        ("I", 6.5, 63),
    ]
    for name, x, y in models:
        ax.scatter([x], [y], s=42, color=NAVY, edgecolor="white", linewidth=0.6, zorder=4)
        ax.annotate(name, (x, y), xytext=(5, 5), textcoords="offset points",
                    fontsize=9.2, color=INK)

    # 帕累托前沿
    front = [("A", 0.12, 52), ("B", 0.28, 60), ("C", 0.45, 63), ("D", 1.1, 68),
             ("E", 2.4, 71), ("G", 9.5, 72)]
    xs = [p[1] for p in front]
    ys = [p[2] for p in front]
    ax.step(xs, ys, where="post", color=GOLD, lw=1.2, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(0.08, 20)
    ax.set_ylim(48, 76)
    ax.set_xlabel("每百万 token 的综合成本（美元，对数轴）", fontsize=9.4)
    ax.set_ylabel("综合得分", fontsize=9.4)
    ax.grid(True, axis="both", color=LGRAY, lw=0.5, alpha=0.7)

    ax.annotate("同分不同价：\nF 比 D 贵四倍，分还低两分", xy=(4.8, 66), xytext=(2.6, 51.6),
                fontsize=9.2, color=GRAY, ha="left",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=0.7,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(0.12, 74.6, "金色阶梯为帕累托前沿：同价最高分，或同分最低价",
            fontsize=8.8, color=GOLD)

    save(fig, "p16-cost-frontier")


if __name__ == "__main__":
    f_p16_map()
    f_p16_cost()
    print("done")
