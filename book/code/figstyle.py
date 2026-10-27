# -*- coding: utf-8 -*-
"""全书插图统一样式。所有绘图脚本 import 本模块。"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
FIGDIR = ROOT / "figures"

# 与正文一致的色板
NAVY = "#1F3A6E"
NAVY_L = "#5B79A8"
NAVY_XL = "#C9D4E6"
GOLD = "#A88447"
GOLD_L = "#D8C39B"
INK = "#191A1C"
GRAY = "#6E7178"
LGRAY = "#D5D8DE"
BG = "#F5F6F8"
GREEN = "#4F7A5B"
RED = "#9B4A3F"
TEAL = "#2F6F73"

PALETTE = [NAVY, GOLD, TEAL, RED, GREEN, NAVY_L, "#7A6A9B"]


def _pick_font() -> str:
    candidates = [
        ("Noto Sans SC", "C:/Windows/Fonts/NotoSansSC-VF.ttf"),
        ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttc"),
        ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name, path in candidates:
        if name in available:
            return name
        if Path(path).exists():
            try:
                font_manager.fontManager.addfont(path)
                return font_manager.FontProperties(fname=path).get_name()
            except Exception:
                continue
    return "DejaVu Sans"


FONT = _pick_font()


def setup() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [FONT, "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.edgecolor": GRAY,
        "axes.linewidth": 0.7,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "axes.grid": True,
        "grid.color": LGRAY,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def canvas(w: float = 6.4, h: float = 3.5):
    setup()
    fig, ax = plt.subplots(figsize=(w, h))
    fig.subplots_adjust(left=0.09, right=0.975, top=0.9, bottom=0.14)
    return fig, ax


def diagram(w: float = 6.4, h: float = 3.2, xlim=(0, 10), ylim=(0, 5)):
    setup()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.grid(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def box(ax, x, y, w, h, text="", fc=BG, ec=NAVY_L, tc=INK, fs=8.5,
        lw=0.8, rounded=0.08, weight="normal", zorder=3, alpha=1.0):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rounded}",
                       linewidth=lw, edgecolor=ec, facecolor=fc,
                       zorder=zorder, alpha=alpha)
    ax.add_patch(p)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=tc, zorder=zorder + 1, weight=weight,
                linespacing=1.35)
    return p


def arrow(ax, p0, p1, color=NAVY, lw=1.0, style="-|>", rad=0.0,
          ls="-", zorder=2, shrink=2):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=9,
                        color=color, linewidth=lw, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}",
                        shrinkA=shrink, shrinkB=shrink, zorder=zorder)
    ax.add_patch(a)
    return a


def save(fig, name: str) -> None:
    FIGDIR.mkdir(exist_ok=True)
    out = FIGDIR / f"{name}.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("saved", out.name)
