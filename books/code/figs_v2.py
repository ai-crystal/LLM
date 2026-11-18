# -*- coding: utf-8 -*-
r"""《大模型技术全景 · 基础篇》（第二卷）插图，共 5 张。

运行：
    python books/code/figs_v2.py          # 全部重画
    python books/code/figs_v2.py 05 07    # 只画指定编号

输出：
    books/v2-basics/images/01/ngram-sparsity.png
    books/v2-basics/images/03/rnn-unroll.png
    books/v2-basics/images/03/lstm-unroll.png
    books/v2-basics/images/04/additive-attention.png
    books/v2-basics/images/05/qkv.png
    books/v2-basics/images/07/multihead.png

尺寸约定：
    画布宽 5.2 in ≈ 132 mm，与正文版心（130 mm）一致，所以图上字号
    就是印刷字号，正文按 130 mm 置入时不必再缩放；288 dpi 出图，
    宽 1497 px，既满足“约 1500 px”，落到纸上也有约 290 dpi。
    坐标系单位取半英寸：1 单位 = 0.5 in，方形色块画出来就是方的。

读图顺序（也是脚本里的顺序）：
    01  n-gram 组合数 vs 语料覆盖 —— 柱间空白就是零概率
    03  RNN 沿时间展开 —— 蓝色前向、红色 BPTT 回流
    03b LSTM 沿时间展开 —— c 是加法传送带，h 仍要过矩阵
    04  加性注意力 —— 解码器状态对 4 个编码器状态的权重
    05  Q/K/V —— 从 T×d 到 T×p，再到 T×T 的注意力矩阵
    07  多头 —— d 切成 4 头，各自注意力，拼接后乘 W^O 混合
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np

from figstyle import (BG, GOLD, GRAY, INK, LGRAY, NAVY, NAVY_L, NAVY_XL, RED, TEAL,
                      box, arrow, plt, setup)
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle

ROOT = HERE.parent
OUTDIR = ROOT / "v2-basics" / "images"

W = 5.2                      # 画布宽（英寸）= 132 mm
DPI = 288                    # 5.2 in × 288 dpi ≈ 1497 px
FS = 8.5                     # 正文标签字号
FS_S = 7.2                   # 附注字号

HEAD_COLORS = [NAVY, GOLD, TEAL, GRAY]


def _install_cjk_weights() -> None:
    """Noto Sans SC 是可变字体，matplotlib 只能解析到 weight=100，
    汉字会掉回 DejaVu 变成豆腐块。这里从 VF 实例化 400/700 两个
    静态字重，家族名不变；结果缓存在 build/fonts/。"""
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
    """固定宽度画布；1 单位 = 0.5 in，等比例，方形不会被拉扁。"""
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
               linespacing=1.45, **kw)


def matrix(ax, x, y, w, h, rows, cols, color, ec=NAVY_L, lw=0.35, z=3):
    """行列色块；color 可以是颜色值，也可以是 f(r, c)。"""
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            fc = color(r, c) if callable(color) else color
            ax.add_patch(Rectangle((x + c * cw, y + (rows - 1 - r) * ch),
                                   cw, ch, facecolor=fc, edgecolor=ec,
                                   linewidth=lw, zorder=z))


def plate(ax, x, y, w, h, lab="", side="top", fs=FS, color=INK,
          ec=NAVY_L, lw=0.6, gap=0.10):
    """矩阵外框；名字写在框外，避免压住色块。"""
    ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=ec,
                           linewidth=lw, zorder=5))
    if not lab:
        return
    if side == "top":
        txt(ax, x + w / 2, y + h + gap, lab, fs=fs, color=color)
    elif side == "bottom":
        txt(ax, x + w / 2, y - gap, lab, fs=fs, color=color)
    elif side == "right":
        txt(ax, x + w + gap, y + h / 2, lab, fs=fs, color=color, ha="left")
    else:
        txt(ax, x - gap, y + h / 2, lab, fs=fs, color=color, ha="right")


def poly(ax, pts, color=NAVY, lw=0.9, ls="-", head=True, z=2, ms=8):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=z,
            solid_capstyle="round", solid_joinstyle="round")
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                    linestyle=ls, shrinkA=0, shrinkB=0,
                                    mutation_scale=ms), zorder=z)


def save(fig, rel: str):
    dst = OUTDIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, dpi=DPI, facecolor="white")
    plt.close(fig)
    # 去掉 alpha 通道：PDF 嵌入与 Word 粘贴时不会出透明背景
    from PIL import Image
    with Image.open(dst) as im:
        im.convert("RGB").save(dst, dpi=(DPI, DPI))
    with Image.open(dst) as im:
        print(f"saved {dst.relative_to(ROOT)}  {im.width}×{im.height} px")


# ---------------------------------------------------------------- 01 n-gram 稀疏性

def fig_01_ngram():
    """第 1 章：组合数按 V^n 长，实际覆盖停在 1e8~1e9，差值即零概率。"""
    setup()
    fig = plt.figure(figsize=(W, 2.95))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.105, 0.245, 0.872, 0.575])

    poss = [5e4, 2.5e9, 1.25e14, 6.25e18]
    seen = [5e4, 1.6e8, 4.6e8, 7.2e8]
    zero = ["0%", "94%", "99.9996%", "≈100%"]
    xs = np.arange(4)

    ax.set_yscale("log")
    ax.set_ylim(1.0e4, 2.2e20)

    ax.bar(xs - 0.17, poss, width=0.32, facecolor="white", edgecolor=NAVY,
           linewidth=0.9, hatch="//////", zorder=3,
           label=r"$V^{n}$：可能的组合数")
    ax.bar(xs + 0.17, seen, width=0.32, facecolor=GOLD, edgecolor="#8A6A33",
           linewidth=0.7, zorder=4, label="10 亿词语料实际出现")

    # 零概率信息带：压在全部柱子之上
    ax.axhline(2.4e19, color=LGRAY, lw=0.6, ls=(0, (3, 3)), zorder=1)
    for x, s in zip(xs, zero):
        ax.text(x, 8.6e19, s, fontsize=FS_S, color=RED, ha="center",
                va="center", zorder=6)
    ax.text(-0.80, 8.6e19, "零概率", fontsize=FS_S, color=RED, ha="left",
            va="center", zorder=6)

    # 语料规模参照：覆盖数不可能超过它
    ax.axhline(1e9, color=GRAY, lw=0.6, ls=(0, (4, 2.5)), zorder=2)
    ax.text(-0.78, 1.12e9, r"语料总量 $10^{9}$ 词", fontsize=6.8, color=GRAY,
            ha="left", va="bottom")

    ax.set_xticks(xs)
    ax.set_xticklabels(["1-gram", "2-gram", "3-gram", "4-gram"], fontsize=FS)
    ax.set_yticks([1e5, 1e8, 1e11, 1e14, 1e17, 1e20])
    ax.set_yticklabels([r"$10^{5}$", r"$10^{8}$", r"$10^{11}$",
                        r"$10^{14}$", r"$10^{17}$", r"$10^{20}$"],
                       fontsize=FS - 0.5)
    ax.minorticks_off()
    ax.set_ylabel("数量（对数轴）", fontsize=FS, labelpad=2)
    ax.set_xlim(-1.02, 3.55)
    ax.tick_params(axis="both", length=2.5, width=0.6, color=GRAY, pad=2)
    ax.spines["left"].set_color(GRAY)
    ax.spines["bottom"].set_color(GRAY)

    fig.text(0.5, 0.968, r"组合数涨到 $10^{18}$，实际覆盖停在 $10^{8}$ 量级",
             fontsize=FS + 0.5, color=INK, ha="center", va="center")
    fig.text(0.5, 0.915, "词表 5 万词、语料 10 亿词；红字是该阶 n-gram 中"
                         "从没出现过的组合占比",
             fontsize=FS_S, color=GRAY, ha="center", va="center")

    ax.legend(loc="upper center", bbox_to_anchor=(0.52, -0.205), ncol=2,
              frameon=False, fontsize=FS_S, handlelength=1.5,
              columnspacing=1.6, handletextpad=0.5)

    save(fig, "01/ngram-sparsity.png")


# ---------------------------------------------------------------- 03 RNN 展开

def fig_03_rnn():
    """第 3 章：h0→h3 横向展开；红色虚线是 BPTT 的反向梯度通路。"""
    fig, ax = canvas(3.05)

    cols = [1.45, 3.85, 6.25, 8.65]
    bw, bh = 1.30, 0.95
    y_h, y_x, y_l = 2.45, 0.95, 4.30

    # 共享权重括线
    ax.annotate("", xy=(cols[0] - 0.66, 5.42), xytext=(cols[-1] + 0.66, 5.42),
                arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.6,
                                shrinkA=0, shrinkB=0, mutation_scale=7),
                zorder=2)
    note(ax, 5.05, 5.62, r"同一组 $W_x$、$W_h$ 在每个时间步复用")

    for i, cx in enumerate(cols):
        box(ax, cx - 0.62, y_l, 1.24, 0.55, f"损失 $L_{i}$", fs=FS - 0.3,
            fc=tint(GOLD, 0.16), ec=GOLD)
        box(ax, cx - bw / 2, y_h, bw, bh, f"$h_{i}$", fs=FS + 2.5,
            fc=tint(NAVY, 0.20), ec=NAVY, lw=0.9, weight="bold")
        box(ax, cx - 0.55, y_x, 1.10, 0.55, f"$x_{i}$", fs=FS, fc=BG,
            ec=NAVY_L)

        arrow(ax, (cx, y_x + 0.57), (cx, y_h - 0.02), lw=0.9)
        arrow(ax, (cx, y_h + bh + 0.02), (cx, y_l - 0.02), lw=0.9)
        note(ax, cx + 0.09, (y_h + bh + y_l) / 2, f"$\\hat{{y}}_{i}$",
             color=GRAY, ha="left")

        if i < 3:
            arrow(ax, (cx + bw / 2 + 0.02, y_h + bh / 2),
                  (cols[i + 1] - bw / 2 - 0.02, y_h + bh / 2), lw=1.1)
            # BPTT：同一条边的反向，紧贴 h 行下方
            arrow(ax, (cols[i + 1] - bw / 2 - 0.10, 2.08),
                  (cx + bw / 2 + 0.10, 2.08), color=RED, lw=0.9,
                  ls=(0, (3.2, 2.0)), style="-|>")

    note(ax, 5.05, 0.22,
         r"红色虚线：BPTT 把 $\partial L/\partial h_t$ 沿时间反向送回，"
         r"每步再乘一次 $W_h^{\top}$", color=RED)
    note(ax, 0.30, 2.93, "前向", color=NAVY, ha="left")
    note(ax, 9.92, 2.93, r"$\cdots$", fs=11, color=GRAY, ha="left")

    save(fig, "03/rnn-unroll.png")


# ---------------------------------------------------------------- 03 LSTM 展开

def fig_03_lstm():
    """第 3 章：LSTM 三个时刻；c 是加法传送带，h 仍要穿过四组门。"""
    fig, ax = canvas(3.62)

    cols = [2.55, 5.30, 8.05]
    y_c, y_cell, y_h, y_x = 5.55, 2.85, 1.45, 0.42
    cw, chh = 1.72, 1.46            # 单元
    hw, hh = 0.95, 0.58             # h
    xw, xh = 0.95, 0.52             # x

    txt(ax, 5.20, 7.02, r"记忆带 $c$ 只做加法与逐元素乘法，$h$ 仍要穿过四组 $W$",
        fs=FS, color=INK)
    note(ax, 5.20, 6.62,
         r"红色虚线：$\partial L/\partial c$ 沿 $c$ 往回走，每步只乘一个门")
    note(ax, 5.20, 6.28,
         r"$c_t=f_t\odot c_{t-1}+i_t\odot\tilde c_t$：连乘项里只有门，没有矩阵；"
         r"$\partial L/\partial h$ 依旧乘 $W^{\top}$", fs=FS_S)

    # 起点
    box(ax, 0.22, y_c - 0.29, 0.95, 0.58, "$c_0$", fs=FS, fc="white",
        ec=LGRAY, tc=GRAY, lw=0.7)
    box(ax, 0.22, y_h, hw, hh, "$h_0$", fs=FS, fc="white",
        ec=LGRAY, tc=GRAY, lw=0.7)
    note(ax, 0.22, 0.22, r"$h_0=c_0=\mathbf{0}$", fs=FS_S, ha="left")

    for i, cx in enumerate(cols):
        t = i + 1
        # 单元
        box(ax, cx - cw / 2, y_cell, cw, chh, "", fc=tint(NAVY, 0.05),
            ec=NAVY_L, lw=0.7)
        note(ax, cx, y_cell + chh - 0.19, "LSTM 单元", color=INK, fs=FS - 0.5)
        chips = [(r"$f_{%d}$" % t, -0.44, 0.86), (r"$i_{%d}$" % t, 0.44, 0.86),
                 (r"$\tilde c_{%d}$" % t, -0.44, 0.36), (r"$o_{%d}$" % t, 0.44, 0.36)]
        for lab, dx, dy in chips:
            box(ax, cx + dx - 0.34, y_cell + dy - 0.17, 0.68, 0.34, lab,
                fs=FS - 1.0, fc="white", ec=NAVY_XL, lw=0.5, rounded=0.05)

        # 输入 x
        box(ax, cx - 0.50 - xw / 2, y_x, xw, xh, f"$x_{t}$", fs=FS, fc=BG,
            ec=NAVY_L)
        arrow(ax, (cx - 0.50, y_x + xh + 0.01), (cx - 0.44, y_cell - 0.02),
              lw=0.8)

        # h
        box(ax, cx + 0.32, y_h, hw, hh, f"$h_{t}$", fs=FS + 1.5,
            fc=tint(NAVY, 0.20), ec=NAVY, lw=0.9, weight="bold")
        arrow(ax, (cx + 0.34, y_cell - 0.02), (cx + 0.60, y_h + hh + 0.02),
              lw=0.9)
        # h_{t-1} → 单元（弧线进左侧）
        if i:
            px = cols[i - 1] + 0.32 + hw + 0.02
        else:
            px = 0.22 + hw + 0.02
        arrow(ax, (px, y_h + hh - 0.10), (cx - cw / 2 - 0.02, y_cell + 0.44),
              lw=0.8, rad=-0.16)

        # 记忆带：c_{t-1} ⊙ f_t ⊕ i_t⊙c̃_t → c_t
        src = cols[i - 1] + 0.04 if i else 0.22 + 0.95
        arrow(ax, (src, y_c), (cx - 0.02, y_c), lw=1.0)
        note(ax, cx - 0.52, y_c - 0.22, r"$\odot f_{%d}$" % t,
             color=TEAL, fs=FS_S)
        arrow(ax, (cx, y_cell + chh + 0.02), (cx, y_c - 0.03), lw=1.0)
        note(ax, cx + 0.10, (y_cell + chh + y_c) / 2 + 0.06,
             r"$i_{%d}\odot\tilde c_{%d}$" % (t, t),
             fs=FS_S, color=GOLD, ha="left")
        ax.plot([cx], [y_c], marker="o", ms=2.6, color=NAVY, zorder=6)

        # 反向：梯度沿 c 回传
        if i:
            arrow(ax, (cx, y_c + 0.40), (cols[i - 1], y_c + 0.40), color=RED,
                  lw=0.8, ls=(0, (3.2, 2.0)))

    note(ax, 9.72, y_c, r"$\cdots$", fs=11, color=GRAY, ha="left")

    save(fig, "03/lstm-unroll.png")


# ---------------------------------------------------------------- 04 加性注意力

def fig_04_additive_attention():
    """第 4 章：s_t 与 h_1..h_4 的连线上，线宽即注意力权重。"""
    fig, ax = canvas(3.20)

    hx = [1.55, 3.15, 4.75, 6.35]
    y_h, bh, bw = 2.15, 0.75, 1.30
    alpha = [0.06, 0.14, 0.52, 0.28]
    s_x, s_y, s_w, s_h = 3.55, 4.55, 1.70, 0.75
    c_x, c_w, bus_y = 7.72, 1.65, 1.30

    # 打分公式
    note(ax, 0.22, 6.04, r"$e_j=v^{\top}\tanh(W_s s_t + W_h h_j)$",
         color=INK, ha="left")
    note(ax, 0.22, 5.70, r"$\alpha_j=\mathrm{softmax}_j(e_j)$，线宽 $\propto\alpha_j$",
         ha="left")

    # 解码器状态
    box(ax, s_x - s_w / 2, s_y, s_w, s_h, "$s_t$", fs=FS + 2.5,
        fc=tint(GOLD, 0.22), ec=GOLD, lw=0.9, weight="bold")
    txt(ax, s_x - s_w / 2 - 0.14, s_y + s_h / 2, "解码器", fs=FS_S,
        color=GOLD, ha="right")

    # 编码器状态
    for i, x in enumerate(hx):
        box(ax, x - bw / 2, y_h, bw, bh, f"$h_{i + 1}$", fs=FS + 1.5,
            fc=tint(NAVY, 0.18), ec=NAVY)
    txt(ax, 0.62, y_h + bh / 2, "编码器", fs=FS_S, color=NAVY, rot=90)

    # 注意力连线：线宽 ∝ 权重；数值标在各自落点上方，互不遮挡
    for i, (x, a) in enumerate(zip(hx, alpha)):
        ar = arrow(ax, (s_x - 0.55 + 0.20 * i, s_y - 0.02),
                   (x, y_h + bh + 0.03), color=NAVY,
                   lw=0.4 + 5.2 * a, shrink=0)
        ar.set_alpha(0.32 + 0.68 * min(1.0, a / 0.52))
        txt(ax, x + 0.26, y_h + bh + 0.30, f"$\\alpha_{{{i + 1}}}={a:.2f}$",
            fs=6.6, color=NAVY if a > 0.3 else GRAY, ha="left")

    # 加权求和：4 个 h 汇到一条汇流线，再送进 c
    ax.plot([hx[0], c_x], [bus_y, bus_y], color=NAVY_L, lw=0.9, zorder=2)
    for x in hx:
        ax.plot([x, x], [y_h - 0.02, bus_y], color=NAVY_L, lw=0.7, zorder=2)
        ax.plot([x], [bus_y], marker="o", ms=2.2, color=NAVY_L, zorder=4)
    arrow(ax, (c_x - 0.62, bus_y), (c_x - 0.02, bus_y), color=NAVY_L, lw=0.9,
          shrink=0)
    txt(ax, 4.95, bus_y - 0.42, r"$\sum_j\alpha_{tj}h_j$", color=NAVY_L)

    box(ax, c_x, bus_y - 0.42, c_w, 0.84, "$c_t$", fs=FS + 2.5,
        fc=tint(GOLD, 0.30), ec=GOLD, lw=0.9, weight="bold")
    note(ax, c_x + c_w / 2, bus_y - 0.64, "上下文向量（定长）")

    save(fig, "04/additive-attention.png")


# ---------------------------------------------------------------- 05 Q/K/V

def fig_05_qkv():
    """第 5 章：X→Q/K/V；S=QK^T 是 T×T；softmax 逐行；A·V 回到 T×d_v。"""
    fig, ax = canvas(3.30)

    # X: T×d
    mx, my, mw, mh = 0.30, 2.10, 1.00, 2.60
    matrix(ax, mx, my, mw, mh, 6, 4,
           lambda r, c: tint(NAVY, 0.16 + 0.07 * ((r + c) % 3)), ec=NAVY_L)
    plate(ax, mx, my, mw, mh, "$X$", gap=0.14)
    note(ax, mx + mw / 2, my - 0.24, r"$T\times d$")

    # Q/K/V: T×d_k
    qx, qw, qh = 2.10, 0.95, 1.10
    ys = {"Q": 4.65, "K": 3.15, "V": 1.65}
    for k, yy in ys.items():
        base = GOLD if k == "V" else NAVY
        matrix(ax, qx, yy, qw, qh, 6, 3,
               lambda r, c, b=base: tint(b, 0.18 + 0.06 * ((r + c) % 3)),
               ec=NAVY_L)
        plate(ax, qx, yy, qw, qh, f"${k}$", fs=FS + 1, color=base)
        arrow(ax, (mx + mw + 0.02, my + mh / 2), (qx - 0.02, yy + qh / 2),
              lw=0.8)
    note(ax, qx + qw / 2, ys["V"] - 0.22, r"$T\times d_k$")

    # S = Q K^T
    sx, sy, sw = 4.05, 4.15, 1.70
    matrix(ax, sx, sy, sw, sw, 6, 6,
           lambda r, c: tint(NAVY, 0.10 + 0.62 * np.exp(-((r - c) ** 2) / 2.2)),
           ec=NAVY_L)
    plate(ax, sx, sy, sw, sw)
    arrow(ax, (qx + qw + 0.02, ys["Q"] + qh / 2), (sx - 0.02, sy + sw - 0.35),
          lw=0.8)
    arrow(ax, (qx + qw + 0.02, ys["K"] + qh / 2), (sx - 0.02, sy + 0.32), lw=0.8)
    txt(ax, sx - 0.16, sy + 0.62, r"$K^{\top}$", color=GRAY, ha="right")
    note(ax, sx + sw / 2, sy - 0.42, r"$S=QK^{\top}$", color=INK)
    note(ax, sx + sw / 2, sy - 0.68, r"$T\times T$")

    # softmax（逐行）
    ax_x, ay, aw = 6.60, 4.15, 1.70
    arrow(ax, (sx + sw + 0.02, sy + sw / 2), (ax_x - 0.02, ay + aw / 2), lw=0.8)
    note(ax, (sx + sw + ax_x) / 2, ay + aw / 2 + 0.18, "softmax")

    mat_a = np.array([[0.50, 0.20, 0.10, 0.10, 0.05, 0.05],
                      [0.25, 0.40, 0.15, 0.10, 0.05, 0.05],
                      [0.10, 0.30, 0.35, 0.15, 0.05, 0.05],
                      [0.08, 0.12, 0.35, 0.30, 0.10, 0.05],
                      [0.05, 0.05, 0.15, 0.35, 0.30, 0.10],
                      [0.05, 0.05, 0.05, 0.15, 0.30, 0.40]])
    matrix(ax, ax_x, ay, aw, aw, 6, 6,
           lambda r, c: tint(NAVY, min(1.0, 0.08 + 1.05 * mat_a[r, c])),
           ec=NAVY_L)
    plate(ax, ax_x, ay, aw, aw)
    note(ax, ax_x + aw / 2, ay + aw + 0.24, r"$A=\mathrm{softmax}(S)$，每行和为 1",
         color=INK)

    # O = A V
    ox, oy, ow, oh = 6.60, 1.55, 1.70, 1.35
    matrix(ax, ox, oy, ow, oh, 6, 3,
           lambda r, c: tint(NAVY, 0.12 + 0.10 * ((2 * r + c) % 4)), ec=NAVY_L)
    plate(ax, ox, oy, ow, oh)
    arrow(ax, (ax_x + aw / 2, ay - 0.02), (ox + ow / 2, oy + oh + 0.02), lw=0.9)
    txt(ax, ox + ow / 2 + 0.10, (ay + oy + oh) / 2, r"$\times V$",
        color=INK, ha="left")
    # V 从下方汇入 O
    poly(ax, [(qx + qw + 0.02, ys["V"] + qh / 2),
              (ox - 0.02, ys["V"] + qh / 2)], color=GOLD, lw=0.8)
    note(ax, ox + ow / 2, oy - 0.42, r"$O=AV$", color=INK)
    note(ax, ox + ow / 2, oy - 0.68, r"$T\times d_v$")

    # 形状账本
    lx, lrx = 8.80, 10.32
    note(ax, lx, 5.72, "形状", color=INK, ha="left")
    ax.plot([lx, lrx], [5.54, 5.54], color=LGRAY, lw=0.6)
    rows = [("$X$", r"$T\times d$"), ("$Q,K,V$", r"$T\times d_k$"),
            (r"$S,\ A$", r"$T\times T$"), ("$O$", r"$T\times d_v$")]
    for k, (a, b) in enumerate(rows):
        y = 5.26 - k * 0.40
        note(ax, lx, y, a, color=INK, ha="left")
        note(ax, lrx, y, b, color=NAVY, ha="right")
    note(ax, lx, 3.72, r"$T$：位置数", fs=6.9, ha="left", va="top")
    note(ax, lx, 3.44, r"$d$：模型宽度", fs=6.9, ha="left", va="top")
    note(ax, lx, 3.16, r"$d_k$：键维度", fs=6.9, ha="left", va="top")
    note(ax, lx, 2.88, r"$d_v$：值维度", fs=6.9, ha="left", va="top")

    save(fig, "05/qkv.png")


# ---------------------------------------------------------------- 07 多头

def fig_07_multihead():
    """第 7 章：4 个头各自 2 维，拼接 8 维，W^O 混回 8 维。"""
    fig, ax = canvas(3.80)

    # X: T×d，列按头着色
    x0, y0, xw = 0.30, 2.30, 0.95
    xh = 3.60
    matrix(ax, x0, y0, xw, xh, 8, 8,
           lambda r, c: tint(HEAD_COLORS[c // 2], 0.42 + 0.05 * (r % 3)),
           ec=NAVY_L, lw=0.3)
    plate(ax, x0, y0, xw, xh, "$X$", gap=0.16)
    note(ax, x0 + xw / 2, y0 - 0.26, r"$T\times d$")

    rows_y = [5.75, 4.25, 2.75, 1.25]
    rh = 1.30
    row_c = [y + rh / 2 for y in rows_y]

    # X 右侧的汇流线：同一块 X 同时接进 4 个头，避免虚线斜穿
    ax.plot([x0 + xw, 1.38], [y0 + xh / 2, y0 + xh / 2], color=NAVY_L, lw=0.9,
            zorder=2)
    ax.plot([1.38, 1.38], [row_c[-1], row_c[0]], color=NAVY_L, lw=0.9, zorder=2)
    for i, yc in enumerate(row_c):
        ax.plot([1.38, 1.50], [yc, yc], color=HEAD_COLORS[i], lw=0.9, zorder=2)

    for i, ry in enumerate(rows_y):
        col = HEAD_COLORS[i]
        ax.add_patch(Rectangle((1.52, ry), 4.10, rh, facecolor="#FBFBFC",
                               edgecolor=LGRAY, linewidth=0.6, zorder=1))
        txt(ax, 1.64, ry + rh / 2, f"头 {i + 1}", fs=7.5, color=col,
            ha="left", weight="bold")

        qx = 2.44
        for k, nm in enumerate(["$Q$", "$K$", "$V$"]):
            matrix(ax, qx + k * 0.44, ry + 0.28, 0.34, 0.62, 8, 2,
                   tint(col, 0.30 + 0.05 * k), ec=col, lw=0.3)
            txt(ax, qx + k * 0.44 + 0.17, ry + 1.05, nm, fs=6.8, color=col)

        arrow(ax, (3.80, ry + 0.59), (4.02, ry + 0.59), lw=0.6)

        # 注意力小方块：对角占优，表示这一头在看哪里
        matrix(ax, 4.06, ry + 0.36, 0.52, 0.52, 8, 8,
               lambda r, c, i=i: tint(col, 0.10 + 0.85 * np.exp(
                   -((r - (c + i) % 8) ** 2) / 1.2)), ec=LGRAY, lw=0.15)
        txt(ax, 4.32, ry + 1.04, "注意力", fs=6.4, color=GRAY)

        arrow(ax, (4.63, ry + 0.59), (4.87, ry + 0.59), lw=0.6)
        matrix(ax, 4.91, ry + 0.28, 0.34, 0.62, 8, 2, tint(col, 0.70),
               ec=col, lw=0.3)
        txt(ax, 5.08, ry + 1.05, f"$o_{i + 1}$", fs=6.8, color=col)

        # 每个头的输出独立汇入拼接块
        arrow(ax, (5.66, ry + rh / 2), (6.48, ry + rh / 2), lw=0.8, color=col)

    # 拼接
    cx, cw2 = 6.52, 0.78
    for i, ry in enumerate(rows_y):
        ax.add_patch(Rectangle((cx, ry), cw2, rh,
                               facecolor=tint(HEAD_COLORS[i], 0.55),
                               edgecolor="white", linewidth=0.6, zorder=3))
    plate(ax, cx, rows_y[-1], cw2, rows_y[0] + rh - rows_y[-1])
    note(ax, cx + cw2 / 2, rows_y[-1] - 0.26, "拼接")
    note(ax, cx + cw2 / 2, rows_y[-1] - 0.50, r"$T\times d$")

    # W^O
    wx, wy, ww, wh = 8.05, 3.55, 1.05, 1.05
    matrix(ax, wx, wy, ww, wh, 4, 4,
           lambda r, c: tint(HEAD_COLORS[c], 0.35 + 0.05 * (r % 3)), ec=GRAY,
           lw=0.3)
    plate(ax, wx, wy, ww, wh, "$W^{O}$", gap=0.14)
    note(ax, wx + ww / 2, wy - 0.24, r"$d\times d$")
    arrow(ax, (cx + cw2 + 0.02, 4.15), (wx - 0.02, 4.15), lw=0.9)

    # 输出
    ox, oy, ow, oh = 9.42, 2.55, 0.85, 3.20
    matrix(ax, ox, oy, ow, oh, 8, 4,
           lambda r, c: tint(NAVY, 0.14 + 0.10 * ((r + c) % 4)), ec=NAVY_L,
           lw=0.3)
    plate(ax, ox, oy, ow, oh, "输出", gap=0.16)
    note(ax, ox + ow / 2, oy - 0.24, r"$T\times d$")
    arrow(ax, (wx + ww + 0.02, 4.15), (ox - 0.02, 4.15), lw=0.9)

    note(ax, 0.30, 7.30, r"$d=8$，$h=4$，$d_k=d/h=2$", color=INK, ha="left")
    note(ax, 10.32, 7.30, r"各头读满 $d$ 维，只写 $d_k$ 维", ha="right")
    note(ax, 0.30, 0.52,
         r"每头一套 $W_Q,W_K,W_V$，参数合计仍是 $3d^2$；"
         r"$W^O$ 把各头的子空间混回一起", ha="left")

    save(fig, "07/multihead.png")


# ---------------------------------------------------------------- 入口

FIGS = {
    "01": fig_01_ngram,
    "03": fig_03_rnn,
    "03b": fig_03_lstm,
    "04": fig_04_additive_attention,
    "05": fig_05_qkv,
    "07": fig_07_multihead,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
