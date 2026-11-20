# -*- coding: utf-8 -*-
"""《大模型技术全景 · 对齐篇》（第五卷）插图。

运行：
    python books/code/figs_v5.py          # 全部重画
    python books/code/figs_v5.py 01       # 只画指定编号

输出：
    books/v5-alignment/images/01/pipeline.png
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.colors import to_rgb

import figstyle as st
from figstyle import (BG, GOLD, GRAY, INK, LGRAY, NAVY, NAVY_L, NAVY_XL,
                      RED, TEAL, arrow, box, plt, setup)

# Noto Sans SC 在本机只注册到 weight=100，小字会发虚；换雅黑，缩到 130 mm 后仍实。
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v5-alignment" / "images"

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


# ---------------------------------------------------------------- 01 流水线

def fig_01_pipeline():
    """第 1 章：四个阶段，数据从哪来、优化什么。"""
    fig, ax = canvas(2.55)

    txt(ax, 5.20, 4.72, "同一条流水线，四段不同的数据", fs=FS + 0.6)
    note(ax, 5.20, 4.40, "越往右，判定越硬，但能覆盖的任务越窄")

    stages = [
        ("预训练", "猜下一个词", "网页文本", NAVY, 0.10),
        ("指令微调", "照着示范答", "人工示范", TEAL, 0.12),
        ("偏好学习", "挑更好的那个", "成对比较", GOLD, 0.14),
        ("可验证 RL", "把事做对", "答案与单测", RED, 0.12),
    ]

    bw, bh = 1.95, 1.00
    y = 2.50
    xs = [1.45, 3.95, 6.45, 8.95]

    for (name, goal, data, color, f), cx in zip(stages, xs):
        box(ax, cx - bw / 2, y, bw, bh, "", fc=tint(color, f), ec=color, lw=0.9)
        txt(ax, cx, y + bh - 0.30, name, fs=FS + 0.8, color=INK, weight="bold")
        txt(ax, cx, y + 0.26, goal, fs=FS - 0.6, color=INK)
        note(ax, cx, y - 0.34, data, fs=FS_S)

    for i in range(3):
        arrow(ax, (xs[i] + bw / 2 + 0.04, y + bh / 2),
              (xs[i + 1] - bw / 2 - 0.04, y + bh / 2), lw=1.0)

    note(ax, 5.20, 1.62, "每一段在修的失效", fs=FS_S, ha="center")
    problems = ["不会听指令", "格式不对", "好坏不分", "会而不对"]
    for p, cx in zip(problems, xs):
        txt(ax, cx, 1.12, p, fs=FS - 0.8, color=GRAY)

    note(ax, 5.20, 0.46,
         "四段可以跳过，也可以换序；但每一段修的失效不同，不能互相替代", fs=FS_S)

    save(fig, "01/pipeline.png")


FIGS = {
    "01": fig_01_pipeline,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
