# -*- coding: utf-8 -*-
"""《大模型技术全景 · 架构改造篇》（第四卷）插图。

运行：
    python books/code/figs_v4.py          # 全部重画
    python books/code/figs_v4.py 01       # 只画指定编号

输出：
    books/v4-architecture/images/NN/xxx.png
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L,
                      NAVY_XL, RED, TEAL, arrow, box, plt, setup)

# Noto Sans SC 在本机只注册到 weight=100，小字会发虚；换雅黑，缩到 130 mm 后仍实。
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v4-architecture" / "images"

W = 5.2                    # 画布宽 5.2 in ≈ 132 mm
DPI = 288
FS = 8.5
FS_S = 7.2
FS_XS = 6.4


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


def plot_at(h_in: float, rect):
    """带坐标轴的画布；rect = (left, bottom, width, height)，单位是图幅比例。"""
    setup()
    fig = plt.figure(figsize=(W, h_in))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes(rect)
    return fig, ax


def tint(color, f):
    r, g, b = to_rgb(color)
    return (1 - f + r * f, 1 - f + g * f, 1 - f + b * f)


def txt(ax, x, y, s, fs=FS, color=INK, ha="center", va="center",
        weight="normal", z=8, rotation=0, ls=1.4):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, zorder=z, linespacing=ls, rotation=rotation)


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


def _eng(x, _=None):
    """日志轴刻度：1、10、100 …"""
    if x >= 1:
        return f"{int(x)}"
    return f"{x:g}"


# ---------------------------------------------------------------- 01 缓存预算

def fig_01_cache_budget():
    """第 1 章：一张卡 60 GB 缓存池里，并发数与上下文长度的反比关系。"""
    fig, ax = plot_at(3.15, (0.135, 0.175, 0.815, 0.735))

    T = np.logspace(3, 5.5, 400)
    pool = 60e9
    cfgs = [
        ("满多头 2.6 MiB", 2.6 * 1024 * 1024, NAVY, 1.0),
        ("GQA-8 320 KiB", 320 * 1024, TEAL, 1.0),
        ("MLA 92 KiB", 92 * 1024, GOLD, 1.0),
        ("MQA 40 KiB", 40 * 1024, GREEN, 1.0),
    ]
    for lab, c, col, lw in cfgs:
        ax.plot(T, pool / (c * T), color=col, lw=1.5, label=lab, zorder=4)

    ax.axhline(1.0, color=RED, lw=0.8, ls=(0, (4, 2.5)), zorder=2)
    ax.text(1.1e3, 1.28, "一个请求都装不下", fontsize=FS_XS, color=RED,
            ha="left", va="bottom")

    for x, name in [(8192, "8K"), (32768, "32K"), (131072, "128K")]:
        ax.axvline(x, color=LGRAY, lw=0.6, ls=":", zorder=1)
        ax.text(x, 0.070, name, fontsize=FS_XS, color=GRAY, ha="center",
                va="bottom")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e3, 3.2e5)
    ax.set_ylim(0.06, 300)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.xaxis.set_major_formatter(FuncFormatter(_eng))
    ax.set_yticks([0.1, 1, 10, 100])
    ax.yaxis.set_major_formatter(FuncFormatter(_eng))
    ax.set_xlabel("上下文长度 T（token）", fontsize=FS_S)
    ax.set_ylabel("池内并发 B", fontsize=FS_S)
    ax.tick_params(labelsize=FS_XS, length=2.5)
    ax.grid(True, which="major", color=LGRAY, lw=0.4, alpha=0.8)
    ax.legend(loc="upper right", fontsize=FS_XS, frameon=False,
              handlelength=1.6, labelspacing=0.35, borderpad=0.2)
    ax.set_title("B·T·c = 60 GB：并发与长度只能二选一", fontsize=FS,
                 color=INK, pad=5)

    save(fig, "01/cache-budget.png")


# ---------------------------------------------------------------- 02 三种头数

def fig_02_kv_shapes():
    """第 2 章：留几份键值——四种方案的缓存与解码强度。"""
    fig, ax = canvas(3.15)

    txt(ax, 5.20, 6.02, "同一层、同一位置，存的键值份数不同", fs=FS, weight="bold")
    note(ax, 5.20, 5.72, "70B：64 个查询头、每头 128 维、80 层；浅格为查询头，实条为缓存", fs=FS_XS)

    rows = [
        ("MHA", 64, 2662, 1, NAVY, "每头一对，缓存最胖"),
        ("GQA-8", 8, 320, 8, TEAL, "八头一组，共用一对"),
        ("MQA", 1, 40, 64, GREEN, "全体共用一对"),
        ("MLA", 1, 92, 240, GOLD, "不共享头，共享潜向量"),
    ]

    x0, step = 1.92, 0.0497
    y = 4.86
    for name, n_kv, kib, strength, col, memo in rows:
        txt(ax, 0.52, y + 0.18, name, fs=FS_S + 0.6, ha="left", weight="bold",
            color=col)

        # 查询头：64 个小方格（浅色）
        for i in range(64):
            ax.add_patch(Rectangle((x0 + i * step, y + 0.28), step - 0.010, 0.15,
                                   facecolor=tint(col, 0.30), edgecolor="none",
                                   zorder=3))

        # 键值份数（实色）
        span = 64 * step
        wid = span / max(n_kv, 1)
        for i in range(n_kv):
            ax.add_patch(Rectangle((x0 + i * wid + 0.012, y - 0.06),
                                   max(wid - 0.024, 0.035), 0.17,
                                   facecolor=col, edgecolor="none",
                                   alpha=0.88, zorder=3))
        txt(ax, x0, y - 0.20, f"{n_kv} 份键值", fs=FS_XS, color=GRAY, ha="left")

        # 数字栏
        txt(ax, 6.15, y + 0.22, f"{kib:,} KiB/token", fs=FS_S, ha="left")
        txt(ax, 8.75, y + 0.18, f"强度 {strength}", fs=FS_S, ha="left", color=col)
        note(ax, 6.15, y - 0.14, memo, fs=FS_XS, ha="left")

        if name != rows[-1][0]:
            ax.plot([0.50, 9.95], [y - 0.36, y - 0.36], color=LGRAY, lw=0.5,
                    zorder=1)
        y -= 1.10

    txt(ax, 5.20, 0.42, "缓存 ∝ 键值份数；强度 = 查询头数 / 键值头数，MLA 靠矩阵吸收补回来",
        fs=FS_XS, color=INK)

    save(fig, "02/kv-shapes.png")


# ---------------------------------------------------------------- 03 分块 IO

def fig_03_flash_io():
    """第 3 章：朴素注意力与分块注意力的 HBM 流量。"""
    fig, ax = plot_at(3.15, (0.135, 0.175, 0.815, 0.725))

    T = np.logspace(3, 5.2, 400)
    H, d, Br = 32, 128, 128
    naive = 8 * T ** 2 * H                      # S、P 各写读一遍
    tiled = 4 * T * d * H                       # K、V 各读一遍（片外复用）

    ax.plot(T, naive, color=RED, lw=1.6, zorder=4,
            label="朴素：$8T^2H$ 字节")
    ax.plot(T, tiled, color=TEAL, lw=1.6, zorder=4,
            label="分块：$4TdH$ 字节")

    for x, lbl in [(8192, "8K"), (32768, "32K")]:
        nv = float(8 * x ** 2 * H)
        tl = float(4 * x * d * H)
        ax.plot([x, x], [tl, nv], color=GRAY, lw=0.6, ls=":", zorder=2)
        ax.plot([x], [nv], marker="o", ms=3.0, color=RED, zorder=5)
        ax.plot([x], [tl], marker="o", ms=3.0, color=TEAL, zorder=5)
        ax.text(x * 1.12, np.sqrt(nv * tl), f"{nv/tl:.0f}×", fontsize=FS_XS,
                color=INK, ha="left", va="center")

    ax.text(1500, 3.4e11, "68 GB 的 $T\\times T$ 矩阵\n从不落地", fontsize=FS_XS,
            color=RED, ha="left", va="top", linespacing=1.4)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e3, 1.6e5)
    ax.set_ylim(1e7, 3e12)
    ax.set_xticks([1e3, 1e4, 1e5])
    ax.xaxis.set_major_formatter(FuncFormatter(_eng))
    ax.set_yticks([1e8, 1e9, 1e10, 1e11, 1e12])
    ax.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _: {1e8: "0.1 GB", 1e9: "1 GB", 1e10: "10 GB",
                      1e11: "100 GB", 1e12: "1 TB"}.get(v, "")))
    ax.set_xlabel("序列长度 T（token）", fontsize=FS_S)
    ax.set_ylabel("一层注意力的 HBM 流量", fontsize=FS_S)
    ax.tick_params(labelsize=FS_XS, length=2.5)
    ax.grid(True, which="major", color=LGRAY, lw=0.4, alpha=0.8)
    ax.legend(loc="upper left", fontsize=FS_XS, frameon=False,
              handlelength=1.6, labelspacing=0.35, borderpad=0.2)
    ax.set_title("平方项留在片上，流量就从 $T^2$ 掉到 $T$", fontsize=FS,
                 color=INK, pad=5)

    save(fig, "03/flash-io.png")


# ---------------------------------------------------------------- 05 梯度失衡

def fig_04_norm_gradient():
    """第 5 章：Post-LN 与 Pre-LN 的层间梯度失衡（示意量级）。"""
    fig, ax = plot_at(3.25, (0.115, 0.215, 0.845, 0.700))

    L = 24
    layer = np.arange(1, L + 1)
    # 示意曲线：按两条已知特征画——Post-LN 末端恒定、输入端按几何速度衰减到 1/60；
    # Pre-LN 各层量级相当，只随 sqrt(L) 缓慢下降。
    post = 1.6 * (1 / 1.195) ** (L - layer)
    pre = 1.0 * (layer / L) ** 0.5 * 0.55 + 0.42

    ax.plot(layer, post, color=RED, lw=1.6, marker="o", ms=2.4,
            label="Post-LN：末端 1.6，首层只剩 1/60")
    ax.plot(layer, pre, color=TEAL, lw=1.6, marker="s", ms=2.2,
            label="Pre-LN：层间相差不到 2 倍")

    ax.set_yscale("log")
    ax.set_xlim(0, L + 1)
    ax.set_ylim(0.020, 3.0)
    ax.set_xlabel("层号（1 = 最靠近输入）", fontsize=FS_S)
    ax.set_ylabel("回传到该层的梯度范数（相对值）", fontsize=FS_S)
    ax.tick_params(labelsize=FS_XS, length=2.5)
    ax.grid(True, which="major", color=LGRAY, lw=0.4, alpha=0.75)
    ax.legend(loc="lower right", fontsize=FS_XS, frameon=False,
              handlelength=1.6, labelspacing=0.35, borderpad=0.2)

    ax.annotate("", xy=(1.15, 0.034), xytext=(1.15, 1.55),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.8,
                                shrinkA=0, shrinkB=0))
    ax.text(1.7, 0.22, "同样一次更新，\n两端差 60 倍", fontsize=FS_XS, color=RED,
            ha="left", va="center", linespacing=1.4)

    ax.set_title("归一化摆在残差内还是外，差的是一个数量级", fontsize=FS,
                 color=INK, pad=5)

    fig.text(0.5, 0.035, "纵轴为示意量级，按两条已知特征绘制",
             fontsize=FS_XS, color=GRAY, ha="center")

    save(fig, "05/norm-gradient.png")


# ---------------------------------------------------------------- 06 MoE 负载

def fig_05_moe_load():
    """第 6 章：专家负载的长尾与容量因子换来的丢弃。"""
    setup()
    fig = plt.figure(figsize=(W, 3.30))
    fig.patch.set_facecolor("white")
    ax1 = fig.add_axes([0.095, 0.185, 0.395, 0.665])
    ax2 = fig.add_axes([0.605, 0.185, 0.355, 0.665])

    rng = np.random.default_rng(7)
    E = 64
    load = rng.lognormal(mean=0.0, sigma=0.45, size=E)
    load = load / load.mean()
    load = np.sort(load)[::-1]
    cf = 1.25
    cap = cf
    drop = float(np.maximum(load - cap, 0).sum() / load.sum() * 100)

    cols = [RED if v > cap else tint(NAVY, 0.35) for v in load]
    ax1.bar(np.arange(E), load, width=0.86, color=cols, edgecolor="none")
    ax1.axhline(cap, color=GOLD, lw=1.0, ls=(0, (4, 2)))
    ax1.axhline(1.0, color=GRAY, lw=0.7, ls=":")

    ax1.text(63.2, cap + 0.05, "容量 1.25×均值", fontsize=FS_XS, color=GOLD,
             ha="right", va="bottom")
    ax1.text(63.2, 1.04, "平均负载", fontsize=FS_XS, color=GRAY,
             ha="right", va="bottom")
    ax1.annotate("超出的 token 被丢\n（这一层走残差）",
                 xy=(13.0, cap + 0.02), xytext=(20.0, 2.10),
                 fontsize=FS_XS, color=RED, ha="left", va="center",
                 linespacing=1.4,
                 arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7,
                                 shrinkA=1, shrinkB=2))

    ax1.set_xlim(-0.8, E - 0.2)
    ax1.set_ylim(0, 2.85)
    ax1.set_xlabel("专家（按负载排序）", fontsize=FS_S)
    ax1.set_ylabel("收到的 token / 均值", fontsize=FS_S)
    ax1.tick_params(labelsize=FS_XS, length=2.5)
    ax1.grid(True, axis="y", color=LGRAY, lw=0.4, alpha=0.75)
    ax1.set_title("负载是长尾的", fontsize=FS_S, color=INK, pad=4)

    f = np.linspace(1.0, 2.0, 200)
    drop_curve = np.array([np.maximum(load - x, 0).sum() / load.sum() * 100
                           for x in f])
    ax2.plot(f, drop_curve, color=RED, lw=1.5)
    ax2.plot([cf], [drop], marker="o", ms=3.4, color=RED, zorder=5)
    ax2.annotate(f"cf = 1.25\n丢弃 {drop:.0f}%", xy=(cf, drop),
                 xytext=(cf + 0.13, drop + 5.0), fontsize=FS_XS,
                 color=RED, ha="left", va="bottom", linespacing=1.4,
                 arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7,
                                 shrinkA=1, shrinkB=3))
    ax2.set_xlim(1.0, 2.0)
    ax2.set_ylim(0, 30)
    ax2.set_xlabel("容量因子", fontsize=FS_S)
    ax2.set_ylabel("被丢弃的 token 占比（%）", fontsize=FS_S)
    ax2.tick_params(labelsize=FS_XS, length=2.5)
    ax2.grid(True, color=LGRAY, lw=0.4, alpha=0.75)
    ax2.set_title("余量买的是丢弃率", fontsize=FS_S, color=INK, pad=4)

    fig.text(0.5, 0.032, "负载分布为示意；真实系统靠辅助损失把丢弃率压到 1% 以下",
             fontsize=FS_XS, color=GRAY, ha="center")

    save(fig, "06/moe-load.png")


# ---------------------------------------------------------------- 09 循环门控

def fig_06_loop_gate():
    """第 9 章：循环残差的门控曲线与准确率随循环深度的走势。"""
    setup()
    fig = plt.figure(figsize=(W, 3.20))
    fig.patch.set_facecolor("white")
    ax1 = fig.add_axes([0.105, 0.195, 0.375, 0.655])
    ax2 = fig.add_axes([0.615, 0.195, 0.350, 0.655])

    t = np.arange(0, 30)
    base = 0.56
    g = np.full(30, 0.40)
    g[12:14] = np.linspace(0.40, 0.91, 2)
    g[14] = 0.91
    g[15:20] = np.linspace(0.91, base, 5)
    g[20:] = base
    ax1.plot(t, g, color=TEAL, lw=1.6, marker="o", ms=2.2)
    ax1.axhline(base, color=GRAY, lw=0.7, ls=":")
    ax1.text(27.6, base + 0.02, "1−β = 0.56", fontsize=FS_XS, color=GRAY,
             ha="right", va="bottom")
    ax1.axvspan(0, 11.5, color=tint(NAVY, 0.08), zorder=0)
    ax1.axvspan(16.5, 29.5, color=tint(GOLD, 0.12), zorder=0)
    ax1.text(5.8, 0.86, "搜索", fontsize=FS_S, color=NAVY)
    ax1.text(23.0, 0.86, "维持", fontsize=FS_S, color=GOLD)
    ax1.annotate("解出的那一步\nγ = 0.91", xy=(14, 0.91), xytext=(16.2, 0.70),
                 fontsize=FS_XS, color=TEAL, ha="left", va="center",
                 linespacing=1.4,
                 arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=0.7,
                                 shrinkA=1, shrinkB=3))
    ax1.set_xlim(-0.5, 29.5)
    ax1.set_ylim(0.30, 1.0)
    ax1.set_xlabel("更新步", fontsize=FS_S)
    ax1.set_ylabel("门控 γ", fontsize=FS_S)
    ax1.tick_params(labelsize=FS_XS, length=2.5)
    ax1.grid(True, color=LGRAY, lw=0.4, alpha=0.7)
    ax1.set_title("门控自己学会\"什么时候停\"", fontsize=FS_S, color=INK, pad=4)

    layers = np.array([468, 936, 1872, 3744, 7488, 24960])
    trm = np.array([62.2, 66.0, 58.1, 55.4, 54.0, 53.0])
    infi = np.array([78.4, 86.5, 90.9, 92.0, 92.4, 92.7])
    ax2.plot(layers, trm, color=RED, lw=1.5, marker="o", ms=2.6,
             label="接着跑")
    ax2.plot(layers, infi, color=TEAL, lw=1.5, marker="s", ms=2.4,
             label="循环残差")
    ax2.set_xscale("log")
    ax2.set_xlim(400, 3.0e4)
    ax2.set_ylim(48, 98)
    ax2.set_xticks([468, 1872, 7488, 24960])
    ax2.xaxis.set_major_formatter(FuncFormatter(_eng))
    ax2.set_xlabel("块应用次数（等效深度）", fontsize=FS_S)
    ax2.set_ylabel("Sudoku-Extreme 通过率（%）", fontsize=FS_S)
    ax2.tick_params(labelsize=FS_XS, length=2.5)
    ax2.grid(True, color=LGRAY, lw=0.4, alpha=0.75)
    ax2.legend(loc="lower left", fontsize=FS_XS, frameon=False,
               handlelength=1.6, labelspacing=0.3, borderpad=0.15)
    ax2.annotate("不再变好", xy=(1872, 58.1), xytext=(1500, 74),
                 fontsize=FS_XS, color=RED, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7,
                                 shrinkA=1, shrinkB=3))
    ax2.set_title("同一底座，只换连接方式", fontsize=FS_S, color=INK, pad=4)

    fig.text(0.5, 0.028, "数据为第一章引用的公开报告值；700 万参数级模型、pass@2",
             fontsize=FS_XS, color=GRAY, ha="center")

    save(fig, "09/loop-gate.png")


FIGS = {
    "01": fig_01_cache_budget,
    "02": fig_02_kv_shapes,
    "03": fig_03_flash_io,
    "05": fig_04_norm_gradient,
    "06": fig_05_moe_load,
    "09": fig_06_loop_gate,
}


def main(argv):
    keys = argv[1:] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
