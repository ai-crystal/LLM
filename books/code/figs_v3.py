# -*- coding: utf-8 -*-
r"""《大模型技术全景 · 预训练篇》（第三卷）插图，共 6 张。

运行：
    python books/code/figs_v3.py          # 全部重画
    python books/code/figs_v3.py 03 06    # 只画指定编号

输出：
    books/v3-pretrain/images/03/pipeline-funnel.png
    books/v3-pretrain/images/04/minhash-band.png
    books/v3-pretrain/images/06/bpe-steps.png
    books/v3-pretrain/images/08/chinchilla.png
    books/v3-pretrain/images/10/memory-split.png
    books/v3-pretrain/images/11/spike-rollback.png

尺寸约定：画布宽 5.2 in ≈ 132 mm，与版心同宽；1 单位 = 0.5 in，
所以方形色块画出来就是方的，288 dpi 出图约 1497 px。

图里不写标题（标题在 md 图注里），文字一律避开线条。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np

from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L, NAVY_XL,
                      RED, TEAL, box, arrow, plt, setup)
from matplotlib.colors import to_rgb
from matplotlib.patches import Polygon, Rectangle

ROOT = HERE.parent
OUTDIR = ROOT / "v3-pretrain" / "images"

W = 5.2                      # 画布宽（英寸）
DPI = 288
FS = 8.5
FS_S = 7.2


def _install_cjk_weights() -> None:
    """Noto Sans SC 是可变字体，matplotlib 只解析到 weight=100，汉字掉回
    DejaVu 变豆腐块。这里实例化 400/700 两个静态字重，缓存在 build/fonts/。"""
    from matplotlib import font_manager
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    src = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
    if not src.exists():
        return
    cache = ROOT / "build" / "fonts"
    cache.mkdir(parents=True, exist_ok=True)
    for wght, style in ((400, "Regular"), (700, "Bold")):
        out = cache / f"NotoSansSC-{style}.ttf"
        if not out.exists():
            vf = TTFont(str(src))
            instantiateVariableFont(vf, {"wght": wght}, updateFontNames=True).save(str(out))
        try:
            font_manager.fontManager.addfont(str(out))
        except Exception:
            pass


_install_cjk_weights()


# ---------------------------------------------------------------- 小工具

def tint(color, f):
    """把颜色向白色混：f=1 原色，f=0 纯白。"""
    r, g, b = to_rgb(color)
    return (1 - f + r * f, 1 - f + g * f, 1 - f + b * f)


def canvas(h_in: float):
    """固定宽度画布；1 单位 = 0.5 in，等比例。"""
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


def txt(ax, x, y, s, fs=FS, color=INK, ha="center", va="center",
        weight="normal", rot=0, z=8, **kw):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, rotation=rot, rotation_mode="anchor",
                   zorder=z, **kw)


def note(ax, x, y, s, fs=FS_S, color=GRAY, ha="center", va="center", **kw):
    return txt(ax, x, y, s, fs=fs, color=color, ha=ha, va=va,
               linespacing=1.5, **kw)


def save(fig, rel: str):
    dst = OUTDIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image
    with Image.open(dst) as im:          # 去 alpha：PDF 与 Word 粘贴都不出透明底
        im.convert("RGB").save(dst, dpi=(DPI, DPI))
    with Image.open(dst) as im:
        print(f"saved {dst.relative_to(ROOT)}  {im.width}x{im.height} px")


# ---------------------------------------------------------------- 03 流水线漏斗

def fig_03_funnel():
    """单快照 30 亿条记录 → 2.2 亿篇文档；条宽按 log10 文档数映射。"""
    rows = [
        ("抓取记录",       3.0e9, "—"),
        ("200 且 text/html", 2.1e9, "70%"),
        ("正文 ≥ 200 字",   1.4e9, "67%"),
        ("英文 p > 0.65",   7.0e8, "50%"),
        ("规则过滤",        4.6e8, "66%"),
        ("行级去重",        3.9e8, "85%"),
        ("文档级去重",      2.2e8, "56%"),
    ]
    fig, ax = canvas(3.30)

    x0 = 3.35
    unit = 2.05                  # 每个数量级 2.05 单位
    base = 8.0
    hbar = 0.40
    ytop = 5.30
    dy = 0.60

    note(ax, 1.55, 5.86, "工序", color=GRAY)
    note(ax, 7.30, 5.86, "文档数", ha="left", color=GRAY)
    note(ax, 10.30, 5.86, "保留率", ha="right", color=GRAY)

    for i, (lab, v, keep) in enumerate(rows):
        y = ytop - i * dy
        wid = 0.55 + (np.log10(v) - base) * unit
        fc = tint(NAVY, 0.95 - 0.10 * i)
        ax.add_patch(Rectangle((x0, y - hbar / 2), wid, hbar, facecolor=fc,
                               edgecolor="none", zorder=3))
        txt(ax, 0.16, y, lab, ha="left", fs=FS - 0.7)
        mant, exp = f"{v:.1e}".split("e")
        txt(ax, x0 + wid + 0.12, y, f"{mant}e{int(exp)}", ha="left",
            fs=FS - 0.7, color=INK)
        if keep != "—":
            txt(ax, 10.30, y, keep, ha="right", fs=FS - 0.7, color=GOLD)

    note(ax, 5.2, 0.86,
         r"累计保留 7.3%：$2.2\times10^{8}$ 篇 × 700 token"
         r" $=1.5\times10^{11}$，96 个快照约 $1.5\times10^{13}$",
         fs=FS_S, color=GRAY)
    note(ax, 5.2, 0.40, "条宽按文档数的对数映射，不是线性", fs=FS_S, color=GRAY)

    save(fig, "03/pipeline-funnel.png")


# ---------------------------------------------------------------- 08 等算力线

def fig_08_chinchilla():
    """N-D 平面上的等损失曲线与 1e23 FLOPs 约束线；三种配方落点。"""
    setup()
    fig = plt.figure(figsize=(W, 3.05))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.128, 0.175, 0.845, 0.700])

    N = np.logspace(9, 12.2, 300)
    D = np.logspace(9.4, 13.3, 300)
    NN, DD = np.meshgrid(N, D)
    L = 1.69 + 406.4 / NN ** 0.34 + 410.7 / DD ** 0.28

    levels = [1.85, 1.90, 1.95, 2.00, 2.10, 2.25]
    cs = ax.contour(NN, DD, L, levels=levels, colors=NAVY_L,
                    linewidths=0.55, zorder=2)
    ax.clabel(cs, fmt="%.2f", fontsize=6.2, inline=True, inline_spacing=2)

    nc = np.logspace(9, 12.2, 200)
    ax.plot(nc, 1e23 / (6 * nc), color=RED, lw=1.0, zorder=4)

    pts = [
        (1.35e10, 1.23e12, "1"),
        (2.9e10, 5.8e11, "2"),
        (7.8e10, 2.1e11, "3"),
    ]
    for x, y, lab in pts:
        ax.plot([x], [y], marker="o", ms=3.4, color=INK, zorder=6)
        ax.text(x * 1.28, y * 1.45, lab, fontsize=FS_S, color=INK,
                ha="center", va="bottom", zorder=7)

    note_txt = ("① 曲面最优：13.5B 参数 / 1.2T token"
                + chr(10) + "② 20 token 口诀：29B / 0.58T"
                + chr(10) + "③ Kaplan 口径：78B / 0.21T")
    ax.text(0.035, 0.045, note_txt,
            transform=ax.transAxes, fontsize=FS_S, color=INK,
            ha="left", va="bottom", linespacing=1.55, zorder=8)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(9e9, 1.6e12)
    ax.set_ylim(2e9, 1.4e13)
    ax.set_xlabel(r"非嵌入参数量 $N$", fontsize=FS, labelpad=1)
    ax.set_ylabel(r"训练 token 数 $D$", fontsize=FS, labelpad=1)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2,
                   labelsize=FS - 1)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.grid(True, color=LGRAY, lw=0.35, alpha=0.5)

    fig.text(0.55, 0.955, r"红线：$6ND=10^{23}$ FLOPs；细线：等损失（nat/token）",
             fontsize=FS_S, color=GRAY, ha="center", va="center")
    save(fig, "08/chinchilla.png")


# ---------------------------------------------------------------- 06 BPE 三步

def fig_06_bpe():
    """20 词小语料上走三步：每步省下的 token 数正好等于选中对的频次。"""
    fig, ax = canvas(3.35)

    txt(ax, 0.18, 6.30, "语料：20 个词、总频次 48、初始 290 个 token",
        ha="left", fs=FS - 0.5)

    rows = [
        ("初始", "", "290"),
        ("第 1 步", "(e, s) 频次 18", "272"),
        ("第 2 步", "(es, t) 频次 18", "254"),
        ("第 3 步", "(est, </w>) 频次 18", "236"),
    ]
    toks = [
        ["n", "e", "w", "e", "s", "t", "</w>"],
        ["n", "e", "w", "es", "t", "</w>"],
        ["n", "e", "w", "est", "</w>"],
        ["n", "e", "w", "est</w>"],
    ]

    ytop = 5.35
    dy = 1.30
    cw = 0.72
    x_seq = 3.42

    note(ax, 1.05, 5.88, "步骤与选中的对", color=GRAY)
    note(ax, x_seq + 3.5 * cw, 5.88, "newest 的 token 序列", color=GRAY)
    note(ax, 9.50, 5.88, "语料 token 数", color=GRAY)

    for i, ((lab, pair, cnt), seq) in enumerate(zip(rows, toks)):
        y = ytop - i * dy
        txt(ax, 0.18, y + 0.20, lab, ha="left", fs=FS - 0.4,
            weight="bold" if lab.startswith("第") else "normal")
        if pair:
            note(ax, 0.18, y - 0.24, pair, ha="left", fs=FS_S, color=GOLD)

        x = x_seq
        for j, t in enumerate(seq):
            inside = (j == 3) and i > 0
            ax.add_patch(Rectangle((x, y - 0.30), cw, 0.60,
                                   facecolor=tint(GOLD, 0.55) if inside else BG,
                                   edgecolor=GOLD if inside else LGRAY,
                                   linewidth=0.9 if inside else 0.5, zorder=3))
            txt(ax, x + cw / 2, y, t, fs=FS - 1.8,
                color="#5A4318" if inside else INK)
            x += cw + 0.05

        txt(ax, 9.50, y, cnt, fs=FS, color=INK)

    note(ax, 5.20, 0.62,
         "每步省下的 token 数正好等于选中对的频次：18、18、18",
         fs=FS_S)
    note(ax, 5.20, 0.24,
         "三步共少 54 个 token（19%），词表只多了 3 项",
         fs=FS_S)

    save(fig, "06/bpe-steps.png")


# ---------------------------------------------------------------- 04 MinHash 分带

def fig_04_minhash():
    """三种 (r, b) 取法下的命中概率曲线；r 控陡度，b 控位置。"""
    setup()
    fig = plt.figure(figsize=(W, 2.85))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.115, 0.215, 0.862, 0.715])

    J = np.linspace(0.30, 1.0, 400)
    curves = [(5, 20, NAVY_L, "-"), (8, 14, NAVY, "-"), (10, 10, GOLD, "-")]
    for r, b, color, ls in curves:
        P = 1 - (1 - J ** r) ** b
        ax.plot(J, P, color=color, lw=1.1, ls=ls,
                label=f"$r={r}$, $b={b}$")

    ax.axvline(0.75, color=GRAY, lw=0.6, ls=(0, (3, 2.5)), zorder=1)
    ax.text(0.755, 0.06, "0.75", fontsize=FS_S, color=GRAY, ha="left")

    for r, b in ((5, 20), (8, 14), (10, 10)):
        P = 1 - (1 - 0.75 ** r) ** b
        ax.plot([0.75], [P], marker="o", ms=2.6, color=INK, zorder=5)

    ax.set_xlim(0.30, 1.0)
    ax.set_ylim(0, 1.06)
    ax.set_xticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("真实 Jaccard 相似度", fontsize=FS, labelpad=2)
    ax.set_ylabel("被列为候选的概率", fontsize=FS, labelpad=2)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2,
                   labelsize=FS - 0.5)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="upper right", frameon=False, fontsize=FS_S,
              handlelength=1.6, labelspacing=0.35)

    fig.text(0.5, 0.975, "同一个 $k$ 下，$(r,b)$ 只改变曲线形状",
             fontsize=FS_S, color=GRAY, ha="center", va="center")
    save(fig, "04/minhash-band.png")


# ---------------------------------------------------------------- 10 显存明细

def fig_10_memory():
    """70B、TP×PP=64 时每卡显存：切优化器省下的那几 GB，远小于激活。"""
    fig, ax = canvas(2.85)

    rows = [
        ("无 ZeRO", 2.2, 2.2, 13.1, 23.0),
        ("ZeRO-1", 2.2, 2.2, 1.62, 23.0),
        ("ZeRO-2", 2.2, 0.07, 1.62, 23.0),
        ("ZeRO-3", 0.07, 0.07, 0.41, 23.0),
    ]
    labels = ["权重 bf16", "梯度 bf16", "优化器 + fp32 主权重", "激活与临时区"]
    colors = [NAVY, NAVY_L, GOLD, TEAL]

    x0 = 2.45
    scale = 0.135
    hbar = 0.50
    ytop = 4.34
    dy = 0.74

    for i, (name, w, g, o, a) in enumerate(rows):
        y = ytop - i * dy
        txt(ax, 2.28, y, name, ha="right", fs=FS - 0.5)
        left = x0
        for val, c in zip((w, g, o, a), colors):
            ax.add_patch(Rectangle((left, y - hbar / 2), val * scale, hbar,
                                   facecolor=tint(c, 0.85), edgecolor="white",
                                   linewidth=0.6, zorder=3))
            left += val * scale
        txt(ax, left + 0.12, y, f"{w + g + o + a:.1f} GB", ha="left",
            fs=FS - 0.8)

    for j, (lab, c) in enumerate(zip(labels, colors)):
        cx = 0.30 + (j % 2) * 4.55
        cy = 5.18 - (j // 2) * 0.38
        ax.add_patch(Rectangle((cx, cy - 0.09), 0.26, 0.18,
                               facecolor=tint(c, 0.85), edgecolor="none",
                               zorder=3))
        txt(ax, cx + 0.36, cy, lab, ha="left", fs=FS - 1.3)

    note(ax, 5.20, 0.86, "70B、TP×PP=64：三级 ZeRO 只省 4.0 GB，"
                         "激活却占 23.0 GB", fs=FS_S)
    note(ax, 5.20, 0.40, "每卡 80 GB，这套配置的瓶颈在算力而不是显存",
         fs=FS_S, color=GRAY)

    save(fig, "10/memory-split.png")


# ---------------------------------------------------------------- 11 尖峰与回滚

def fig_11_spike():
    """一次尖峰的时间线：跳升、平台、回滚、永久落后。"""
    setup()
    fig = plt.figure(figsize=(W, 2.75))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.118, 0.185, 0.862, 0.680])

    # 参考轨迹：没出事的话
    xr = np.linspace(11800, 13600, 200)
    yr = 1.94 - 0.15 * (xr - 11800) / 1800.0

    # 实际轨迹
    x1 = np.linspace(11800, 12000, 30)
    y1 = 1.94 - 0.02 * (x1 - 11800) / 200.0
    x2 = np.linspace(12002, 12060, 30)
    y2 = 2.86 - 0.30 * (x2 - 12002) / 58.0 + 0.13 * np.sin((x2 - 12002) / 4.0)
    x3 = np.linspace(12060, 12500, 60)
    y3 = 2.56 - 0.48 * (1 - np.exp(-(x3 - 12060) / 120.0))
    x4 = np.linspace(12500, 13600, 120)
    y4 = 1.93 - 0.10 * (x4 - 12500) / 1100.0

    ax.plot(xr, yr, color=GRAY, lw=0.9, ls=(0, (4, 2.5)), zorder=2,
            label="参考轨迹（未出事）")
    ax.plot(x1, y1, color=NAVY, lw=1.2, zorder=4)
    ax.plot([12000, 12000], [1.92, 2.86], color=RED, lw=1.2, zorder=4)
    ax.plot(x2, y2, color=RED, lw=1.2, zorder=4)
    ax.plot(x3, y3, color=RED, lw=1.2, zorder=4)
    ax.plot(x4, y4, color=NAVY, lw=1.2, zorder=4)
    # 回滚：从平台直接落回检查点的损失
    ax.plot([12500, 12500], [2.08, 1.93], color=GOLD, lw=1.1, ls="-", zorder=3)
    ax.plot([12500], [1.93], marker="v", ms=4.0, color=GOLD, zorder=6)

    ax.annotate("尖峰", xy=(12030, 2.72), xytext=(12160, 3.06),
                fontsize=FS_S, color=RED, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.annotate("平台：参数停在那里", xy=(12300, 2.10), xytext=(12380, 2.36),
                fontsize=FS_S, color=RED, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.annotate("回滚 + 跳 300 批", xy=(12500, 2.00), xytext=(12630, 1.755),
                fontsize=FS_S, color="#7A5C1E", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=GOLD, lw=0.6))
    ax.annotate("落后 0.04", xy=(13500, 1.80), xytext=(13120, 1.99),
                fontsize=FS_S, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.5))

    ax.set_xlim(11750, 13650)
    ax.set_ylim(1.70, 3.15)
    ax.set_xlabel("训练步数", fontsize=FS, labelpad=1)
    ax.set_ylabel("训练损失", fontsize=FS, labelpad=1)
    ax.set_yticks([1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0])
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2,
                   labelsize=FS - 1)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)
    ax.legend(loc="upper right", frameon=False, fontsize=FS_S,
              handlelength=1.8, bbox_to_anchor=(0.998, 0.998))
    save(fig, "11/spike-rollback.png")


# ---------------------------------------------------------------- main

FIGS = {
    "03": fig_03_funnel,
    "04": fig_04_minhash,
    "06": fig_06_bpe,
    "08": fig_08_chinchilla,
    "10": fig_10_memory,
    "11": fig_11_spike,
}


def main() -> None:
    picks = sys.argv[1:] or list(FIGS)
    for key in picks:
        f = FIGS.get(key)
        if f is None:
            raise SystemExit(f"没有编号 {key}（可用：{', '.join(FIGS)}）")
        f()


if __name__ == "__main__":
    main()
