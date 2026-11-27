# -*- coding: utf-8 -*-
"""《大模型技术全景 · 可解释性与评测篇》（第十一卷）插图。

运行：
    python books/code/figs_v11.py          # 全部重画
    python books/code/figs_v11.py 02       # 只画指定编号

输出：
    books/v11-interpret/images/NN/xxx.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.colors import to_rgb
from matplotlib.transforms import blended_transform_factory

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L,
                      NAVY_XL, RED, TEAL, arrow, box, plt, setup)

# Noto Sans SC 在本机只注册到 weight=100，小字会发虚；换雅黑，缩到 130 mm 后仍实。
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v11-interpret" / "images"

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
                   zorder=8, linespacing=1.5, **kw)


def save(fig, rel: str):
    dst = OUTDIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dst, dpi=DPI, facecolor="white")
    plt.close(fig)
    from PIL import Image
    with Image.open(dst) as im:
        im.convert("RGB").save(dst, dpi=(DPI, DPI))
        print(f"saved {dst.relative_to(ROOT)}  {im.width}×{im.height} px")


# ---------------------------------------------------------------- 01 诊断阶梯

def fig_01_ladder():
    """第 1 章：四层的成本阶梯，以及每层能排除什么。"""
    fig, ax = canvas(2.72)

    txt(ax, 0.22, 5.14, "层次", fs=FS_S - 0.4, color=GRAY, ha="left")
    txt(ax, 1.66, 5.14, "典型耗时", fs=FS_S - 0.4, color=GRAY, ha="left")
    txt(ax, 5.32, 5.14, "这一层能排除的假设", fs=FS_S - 0.4, color=GRAY, ha="left")
    ax.plot([0.22, 10.16], [5.02, 5.02], color=LGRAY, lw=0.8, zorder=2)

    rows = [
        ("行为层", "2 小时", 2.0, "「不是数据缺，是策略问题」", NAVY),
        ("表示层", "1 天", 8.0, "「信息进来了，只是没被取用」", TEAL),
        ("组件层", "1 周", 40.0, "「别的地方顶不上，只有它在管」", GOLD),
        ("电路层", "1 个月", 160.0, "只能验通一条路径，别的路仍在", RED),
    ]

    bx = 1.66
    for i, (name, label, hours, what, color) in enumerate(rows):
        y = 4.34 - i * 1.06
        box(ax, 0.22, y, 1.30, 0.62, name, fc=tint(color, 0.12), ec=color,
            lw=0.85, fs=FS - 0.9, weight="bold")
        w = 0.34 * hours ** 0.4
        ax.add_patch(plt.Rectangle((bx, y + 0.13), 2.74, 0.36,
                                   facecolor=tint(NAVY_XL, 0.28),
                                   edgecolor="none", zorder=2))
        ax.add_patch(plt.Rectangle((bx, y + 0.13), w, 0.36,
                                   facecolor=tint(color, 0.42), edgecolor=color,
                                   lw=0.7, zorder=3))
        note(ax, bx + w + 0.16, y + 0.31, label, fs=FS_S - 0.5, ha="left",
             color=color)
        note(ax, 5.32, y + 0.31, what, fs=FS_S - 0.5, ha="left")

    note(ax, 5.20, 0.74, "往下每走一层，成本约涨五倍，能排除的东西从「一类」缩到「一条」",
         fs=FS_S - 0.5)
    note(ax, 5.20, 0.46, "上一层能排除的假设，不要带到下一层去查", fs=FS_S - 0.5,
         color=NAVY)

    save(fig, "01/diag_ladder.png")


# ---------------------------------------------------------------- 02 探针

def fig_02_probe():
    """第 2 章：五步流程，下面接因果验证的四组对照。"""
    fig, ax = canvas(3.05)

    steps = [
        ("① 造对照数据", "两组只差一个属性"),
        ("② 取激活", "某层 · 某位置"),
        ("③ 训线性探针", "逻辑回归 + 交叉验证"),
        ("④ 层扫描", "准确率随层变化"),
        ("⑤ 均值差", "得到方向向量"),
    ]

    bw, bh, gap = 1.80, 0.86, 0.24
    y = 4.78
    x0 = 0.22
    for i, (head, sub) in enumerate(steps):
        cx = x0 + i * (bw + gap)
        box(ax, cx, y, bw, bh, "", fc=BG, ec=NAVY_L, lw=0.85)
        txt(ax, cx + bw / 2, y + bh - 0.24, head, fs=FS - 0.9, weight="bold")
        note(ax, cx + bw / 2, y + 0.24, sub, fs=FS_S - 0.9)
        if i < len(steps) - 1:
            arrow(ax, (cx + bw + 0.03, y + bh / 2),
                  (cx + bw + gap - 0.03, y + bh / 2), lw=0.9)

    note(ax, 5.20, 4.42, "数据决定结论上限；探针必须是线性的，位置要试三种", fs=FS_S - 0.4)

    ax.plot([0.22, 10.18], [4.12, 4.12], color=LGRAY, lw=0.8, zorder=2)
    txt(ax, 0.62, 3.84, "因果验证", fs=FS - 0.4, weight="bold")
    note(ax, 6.40, 3.84, "四组一起跑，缺一组结论就不成立", fs=FS_S - 0.4)

    rows = [
        ("无干预", 0.95, NAVY_L, "基线"),
        ("减去目标方向", 0.12, RED, "应大幅降"),
        ("加上目标方向", 0.98, GOLD, "应继续升"),
        ("减随机方向", 0.93, GRAY, "应无变化"),
        ("减正交方向", 0.94, GRAY, "应无变化"),
    ]

    bar_x, bar_max = 2.95, 4.05
    for i, (label, v, color, hint) in enumerate(rows):
        yy = 3.30 - i * 0.58
        txt(ax, 0.24, yy, label, fs=FS - 1.0, ha="left")
        ax.add_patch(plt.Rectangle((bar_x, yy - 0.15), bar_max, 0.30,
                                   facecolor=tint(NAVY_XL, 0.30),
                                   edgecolor="none", zorder=2))
        ax.add_patch(plt.Rectangle((bar_x, yy - 0.15), bar_max * v, 0.30,
                                   facecolor=tint(color, 0.55),
                                   edgecolor=color, lw=0.7, zorder=3))
        txt(ax, bar_x + bar_max * v + 0.32, yy, f"{v:.0%}", fs=FS_S - 0.6,
            color=color if color != GRAY else GRAY, weight="bold")
        note(ax, 8.30, yy, hint, fs=FS_S - 0.8, ha="left")

    note(ax, 5.20, 0.36,
         "只有加减目标方向才改变行为，才谈得上“这个方向在管这件事”", fs=FS_S - 0.4)

    save(fig, "02/probe_direction.png")


# ---------------------------------------------------------------- 02b 层扫描

def fig_02_sweep():
    """第 2 章：层扫描要三条线一起画——目标、控制任务、打乱标签。"""
    setup()
    fig = plt.figure(figsize=(W, 2.62))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.135, 0.215, 0.825, 0.755])

    layers = np.arange(0, 33)
    target = 0.50 + 0.43 / (1.0 + np.exp(-(layers - 7.6) / 1.55))
    target = target - 0.035 * np.clip(layers - 28, 0, 4)
    control = 0.55 + 0.065 * layers / 32.0
    rng = np.random.default_rng(7)
    shuffled = 0.50 + rng.normal(0, 0.008, layers.size)

    ax.fill_between(layers, 0.47, 0.53, color=tint(NAVY_XL, 0.55),
                    edgecolor="none", zorder=1,
                    label="打乱标签的 95% 带")
    ax.plot(layers, control, color=GOLD, lw=1.3, marker="s", ms=2.0,
            label="控制任务（长度）")
    ax.plot(layers, target, color=NAVY, lw=1.4, marker="o", ms=2.0,
            label="目标探针")
    ax.plot(layers, shuffled, color=GRAY, lw=0.9, zorder=4,
            label="打乱标签")

    ax.axhline(0.5, color=GRAY, lw=0.7, ls=(0, (4, 3)), zorder=1)

    x0 = 12.0
    ax.annotate("", xy=(x0, 0.905), xytext=(x0, 0.640),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9,
                                mutation_scale=7))
    ax.text(x0 - 0.5, 0.775, "差值\n26 点", ha="right", va="center",
            fontsize=6.4, color=RED, linespacing=1.3)

    ax.annotate("控制任务 = 混杂上限", xy=(27.0, 0.605), xytext=(18.6, 0.715),
                fontsize=6.2, color=GOLD, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=GOLD, lw=0.6,
                                shrinkA=2, shrinkB=2,
                                connectionstyle="arc3,rad=-0.2"))

    ax.set_xlim(-1.0, 33.5)
    ax.set_ylim(0.40, 1.06)
    ax.set_xticks([0, 8, 16, 24, 32])
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("层号", labelpad=2)
    ax.set_ylabel("探针准确率")
    ax.legend(loc="upper left", frameon=False, fontsize=6.2,
              handlelength=2.0, borderaxespad=0.5, ncol=1,
              labelspacing=0.32)

    save(fig, "02/layer_sweep.png")


# ---------------------------------------------------------------- 03 SAE

def fig_03_sae():
    """第 3 章：上半是 SAE 结构，下半是特征分裂与吸收。"""
    fig, ax = canvas(3.30)

    txt(ax, 1.18, 6.24, "稠密激活", fs=FS - 0.2, weight="bold")
    txt(ax, 3.24, 6.24, "稀疏特征", fs=FS - 0.2, weight="bold")
    txt(ax, 5.10, 6.24, "重建", fs=FS - 0.2, weight="bold")
    note(ax, 1.18, 5.97, "4096 维，几乎每维都有值", fs=FS_S - 0.9)
    note(ax, 3.24, 5.97, "131072 维，多数为 0", fs=FS_S - 0.9)
    note(ax, 5.10, 5.97, "误差要小", fs=FS_S - 0.9)

    # 稠密：满格
    box(ax, 0.20, 5.04, 1.95, 0.80, "", fc=tint(NAVY, 0.06), ec=NAVY, lw=0.9)
    for r in range(3):
        for c in range(14):
            ax.add_patch(plt.Rectangle(
                (0.30 + c * 0.126, 5.15 + r * 0.222), 0.112, 0.20,
                facecolor=tint(NAVY, 0.32), edgecolor=NAVY_L, lw=0.35, zorder=3))

    # 稀疏：一列小格，少数亮
    sx, sy = 2.56, 5.055
    cw, ch, cg, rg = 0.19, 0.052, 0.045, 0.013
    lit = {3, 17, 31, 46, 52, 68}
    for k in range(72):
        xx = sx + (k // 12) * (cw + cg)
        yy = sy + (11 - k % 12) * (ch + rg)
        on = k in lit
        ax.add_patch(plt.Rectangle(
            (xx, yy), cw, ch,
            facecolor=tint(GOLD, 0.80) if on else tint(LGRAY, 0.42),
            edgecolor=GOLD if on else LGRAY, lw=0.4, zorder=3))

    box(ax, 4.32, 5.04, 1.56, 0.80, "", fc=tint(TEAL, 0.06), ec=TEAL, lw=0.9)
    for r in range(3):
        for c in range(10):
            ax.add_patch(plt.Rectangle(
                (4.42 + c * 0.142, 5.15 + r * 0.222), 0.128, 0.20,
                facecolor=tint(TEAL, 0.30), edgecolor=TEAL, lw=0.35, zorder=3))

    arrow(ax, (2.18, 5.44), (2.52, 5.44), lw=1.0)
    arrow(ax, (3.96, 5.44), (4.28, 5.44), lw=1.0)

    txt(ax, 8.10, 5.60, "损失 = 重建误差 + λ × 稀疏程度", fs=FS - 0.2)
    note(ax, 8.10, 5.26, "λ 大 → 特征少而纯，重建变差", fs=FS_S - 0.6)
    note(ax, 8.10, 5.00, "λ 小 → 重建准，但字典退化成普通重编码", fs=FS_S - 0.6)
    note(ax, 5.20, 4.64,
         "解码器的每一列都要归一化，否则模型靠“放大列、缩小系数”绕开稀疏约束",
         fs=FS_S - 0.4)

    ax.plot([0.20, 10.20], [4.40, 4.40], color=LGRAY, lw=0.8, zorder=2)

    # 左：特征分裂
    txt(ax, 2.55, 3.96, "特征分裂", fs=FS - 0.2, weight="bold")
    note(ax, 2.55, 3.68, "字典越宽，一个概念拆成多个", fs=FS_S - 0.6)
    box(ax, 0.30, 2.00, 1.16, 0.62, "法语", fc=tint(NAVY, 0.12), ec=NAVY, lw=0.85)
    for label, yy in (("法语 · 文本", 2.46), ("法语 · 人名", 1.80), ("法语 · 地名", 1.14)):
        box(ax, 2.00, yy, 1.92, 0.52, label, fc=BG, ec=NAVY_L, lw=0.8, fs=FS - 1.4)
        arrow(ax, (1.50, 2.31), (1.96, yy + 0.26), lw=0.8)
    note(ax, 2.55, 0.62, "总量没变，可读性反而下降", fs=FS_S - 0.6)

    # 右：特征吸收
    txt(ax, 7.65, 3.96, "特征吸收", fs=FS - 0.2, weight="bold")
    note(ax, 7.65, 3.68, "更一般的特征把 α 顺带覆盖了", fs=FS_S - 0.6)
    box(ax, 5.30, 2.00, 1.26, 0.62, "概念 α", fc=tint(RED, 0.10), ec=RED, lw=0.85)
    box(ax, 7.55, 2.00, 2.36, 0.62, "一般特征 β", fc=tint(GOLD, 0.14), ec=GOLD, lw=0.85)
    arrow(ax, (6.60, 2.31), (7.51, 2.31), color=RED, lw=1.0, ls=(0, (3, 2)))
    note(ax, 7.05, 2.74, "α 出现时 β 也亮", fs=FS_S - 1.0, color=RED)
    note(ax, 7.65, 1.50, "结果：α 没有专属特征，重建却很好", fs=FS_S - 0.6)
    note(ax, 7.65, 0.62, "搜遍字典找不到 α，会误判“模型没有这个概念”", fs=FS_S - 0.6)

    save(fig, "03/sae_split_absorb.png")


# ---------------------------------------------------------------- 04 归纳头

def fig_04_induction():
    """第 4 章：两遍重复序列上的注意力斜线，以及上下游两个头。"""
    fig, ax = canvas(2.90)

    toks = ["t1", "t2", "t3", "t4", "t5", "t6"] * 2
    bw, gap = 0.62, 0.14
    pitch = bw + gap
    x0, y0, bh = 0.72, 4.92, 0.44

    for i, t in enumerate(toks):
        xx = x0 + i * pitch
        dup = i >= 6
        same = i % 6 == 3          # 两次出现的 t4
        target = i == 4            # 第一次 t4 的下一位（t5）
        fc = tint(GOLD, 0.55) if same else (
            tint(RED, 0.10) if target else (
                tint(NAVY_XL, 0.50) if dup else BG))
        ec = GOLD if same else (RED if target else NAVY_L)
        ax.add_patch(plt.Rectangle((xx, y0), bw, bh,
                                   facecolor=fc, edgecolor=ec, lw=0.8, zorder=3))
        txt(ax, xx + bw / 2, y0 + bh / 2, t, fs=FS_S - 0.6)

    txt(ax, x0 + 2.5 * pitch, 5.58, "第一遍", fs=FS_S - 0.4, color=GRAY)
    txt(ax, x0 + 8.5 * pitch, 5.58, "第二遍", fs=FS_S - 0.4, color=GRAY)
    ax.plot([x0 + 6 * pitch - gap / 2] * 2, [y0 - 0.08, y0 + bh + 0.08],
            color=LGRAY, lw=0.9, ls=(0, (3, 2)), zorder=2)

    xs = x0 + 9 * pitch + bw / 2      # 第二次的 t4
    xd = x0 + 4 * pitch + bw / 2      # 第一次 t4 的下一位
    yb = 4.34
    ax.plot([xs, xs, xd, xd], [y0 - 0.04, yb, yb, y0 - 0.04],
            color=RED, lw=1.1, zorder=4, solid_joinstyle="round")
    arrow(ax, (xd, yb + 0.22), (xd, y0 - 0.06), color=RED, lw=1.1)

    note(ax, 5.20, 4.06, "在第二次的 t4 上，注意力回到第一次 t4 的下一位（t5）",
         fs=FS_S - 0.4, color=RED)
    note(ax, 5.20, 3.80, "读到的内容是 t5，于是预测 t5", fs=FS_S - 0.4, color=RED)

    ax.plot([0.72, 9.70], [3.60, 3.60], color=LGRAY, lw=0.8, zorder=2)

    # 两个头串联
    box(ax, 0.22, 2.34, 2.90, 0.96, "", fc=tint(NAVY, 0.08), ec=NAVY, lw=0.85)
    txt(ax, 1.67, 3.10, "头 A（上一层）", fs=FS - 0.7, weight="bold")
    note(ax, 1.67, 2.84, "把“前一个 token 是什么”", fs=FS_S - 0.8)
    note(ax, 1.67, 2.60, "搬到当前位置", fs=FS_S - 0.8)

    box(ax, 3.50, 2.34, 2.90, 0.96, "", fc=tint(GOLD, 0.14), ec=GOLD, lw=0.85)
    txt(ax, 4.95, 3.10, "头 B（本层）", fs=FS - 0.7, weight="bold")
    note(ax, 4.95, 2.84, "用这个信息去匹配", fs=FS_S - 0.8)
    note(ax, 4.95, 2.60, "前文同样的位置", fs=FS_S - 0.8)

    box(ax, 6.78, 2.34, 3.40, 0.96, "", fc=tint(RED, 0.08), ec=RED, lw=0.85)
    txt(ax, 8.48, 3.10, "输出位置", fs=FS - 0.7, weight="bold")
    note(ax, 8.48, 2.84, "读到下一位的内容", fs=FS_S - 0.8)
    note(ax, 8.48, 2.60, "预测 = t5", fs=FS_S - 0.8)

    arrow(ax, (3.16, 2.82), (3.46, 2.82), lw=1.0)
    arrow(ax, (6.44, 2.82), (6.74, 2.82), lw=1.0)

    note(ax, 5.20, 1.92, "缺了头 A，头 B 拿不到“前一个是谁”，归纳就无从谈起", fs=FS_S - 0.4)
    note(ax, 5.20, 1.62, "关掉 B：重复序列损失上升，自然文本几乎不变；关掉 A：两种任务都掉",
         fs=FS_S - 0.6)
    note(ax, 5.20, 1.28, "这是最容易验证的一条电路：两个组件，两个可分开的干预实验",
         fs=FS_S - 0.6)
    note(ax, 5.20, 0.94, "顺序也要对：先定位上一 token 头，再找归纳头，反过来会白跑一轮",
         fs=FS_S - 0.6)

    save(fig, "04/induction_head.png")


# ---------------------------------------------------------------- 05 lens

def fig_05_lens():
    """第 5 章：两种 lens 的分层曲线（示意），标出各自的跳变层。"""
    setup()
    fig = plt.figure(figsize=(W, 2.78))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.145, 0.235, 0.815, 0.700])

    layers = np.arange(0, 33)
    vocab = 1.28e5

    def curve(enter, k):
        r = np.where(layers < enter, vocab, vocab * np.exp(-k * (layers - enter)))
        return np.maximum(r, 2.0)

    logit = curve(21.0, 1.02)
    tuned = curve(13.0, 0.575)

    ax.plot(layers, logit, color=NAVY, lw=1.4, marker="o", ms=2.3,
            label="logit lens")
    ax.plot(layers, tuned, color=GOLD, lw=1.4, marker="s", ms=2.3,
            label="tuned lens")

    ax.set_yscale("log")
    ax.invert_yaxis()
    ax.set_xlim(-1.0, 33.5)
    ax.set_ylim(4.0e5, 0.45)
    ax.set_xlabel("层号", labelpad=2)
    ax.set_ylabel("正确答案的排名（越低越好）")
    ax.set_xticks([0, 8, 16, 24, 32])
    ax.grid(True, which="major", color=LGRAY, lw=0.5, alpha=0.85)
    ax.grid(True, which="minor", color=LGRAY, lw=0.28, alpha=0.40)
    ax.legend(loc="upper left", frameon=False, fontsize=7.0,
              handlelength=2.2, borderaxespad=0.5)

    for x, col in ((13.0, GOLD), (21.0, NAVY)):
        ax.axvline(x, color=col, lw=0.85, ls=(0, (3, 2)), alpha=0.8)

    trans = blended_transform_factory(ax.transData, ax.transAxes)
    ax.text(13.0, 0.945, "13 层", transform=trans, ha="center", va="center",
            fontsize=6.4, color=GOLD, bbox=dict(facecolor="white", edgecolor="none", pad=1.2))
    ax.text(21.0, 0.945, "21 层", transform=trans, ha="center", va="center",
            fontsize=6.4, color=NAVY, bbox=dict(facecolor="white", edgecolor="none", pad=1.2))

    ax.text(0.045, 0.790, "示意：形状随模型与题目而变",
            transform=ax.transAxes, ha="left", va="center",
            fontsize=6.2, color=GRAY)

    save(fig, "05/lens_curves.png")


# ---------------------------------------------------------------- 06 污染

def fig_06_contamination():
    """第 6 章：四种检测方法各自能抓什么、抓不到什么。"""
    fig, ax = canvas(2.75)

    cols = [
        ("方法", 0.16, 1.80),
        ("能抓到", 2.04, 3.02),
        ("抓不到", 5.18, 3.02),
        ("成本", 8.32, 1.90),
    ]
    for label, cx, cw in cols:
        box(ax, cx, 4.86, cw, 0.44, label, fc=tint(NAVY, 0.14), ec=NAVY,
            lw=0.85, fs=FS - 1.0, weight="bold")

    rows = [
        ("n-gram 重叠", "测试题原文出现在语料里", "改写、模板、答案泄漏", "低", NAVY),
        ("损失异常", "模型对原表述异常熟悉", "通用解法模板的痕迹", "低", TEAL),
        ("改写测试", "对原表述的依赖", "原文照抄（改后仍对）", "中", GOLD),
        ("时间切分", "一切形式的泄漏", "无（但要持续出新题）", "高", RED),
    ]

    for i, (name, can, cannot, cost, color) in enumerate(rows):
        yy = 3.96 - i * 0.86
        box(ax, 0.16, yy, 1.80, 0.68, name, fc=tint(color, 0.12),
            ec=color, lw=0.85, fs=FS - 1.1, weight="bold")
        box(ax, 2.04, yy, 3.02, 0.68, can, fc=BG, ec=LGRAY, lw=0.7,
            fs=FS_S - 0.7)
        box(ax, 5.18, yy, 3.02, 0.68, cannot, fc=BG, ec=LGRAY, lw=0.7,
            fs=FS_S - 0.9, tc=GRAY)
        box(ax, 8.32, yy, 1.90, 0.68, cost, fc=tint(color, 0.08),
            ec=color, lw=0.7, fs=FS_S - 0.4)

    note(ax, 5.20, 1.02, "先用便宜的两项粗筛，抽最可疑的一小批做改写测试", fs=FS_S - 0.5)
    note(ax, 5.20, 0.72, "时间切分不是筛查手段，而是评测集设计的默认前提", fs=FS_S - 0.5)

    save(fig, "06/contamination.png")


# ---------------------------------------------------------------- 06b 校准

def fig_06_calibration():
    """第 6 章：判定模型的可靠性图，柱子是样本量，折线是实际通过率。"""
    setup()
    fig = plt.figure(figsize=(W, 2.55))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.135, 0.215, 0.700, 0.750])
    ax2 = ax.twinx()

    centers = np.array([0.55, 0.65, 0.75, 0.85, 0.95])
    acc = np.array([0.58, 0.62, 0.70, 0.71, 0.78])
    cnt = np.array([20, 45, 80, 120, 60])

    ax2.bar(centers, cnt, width=0.088, color=tint(NAVY_XL, 0.42),
            edgecolor=NAVY_L, lw=0.4, zorder=1)
    ax2.set_ylim(0, 400)
    ax2.set_yticks([0, 100, 200, 300])
    ax2.set_ylabel("样本数", color=GRAY, fontsize=7.0)
    ax2.tick_params(axis="y", labelsize=6.6, colors=GRAY)
    ax2.spines["top"].set_visible(False)

    ax.plot([0.45, 1.0], [0.45, 1.0], color=GRAY, lw=0.8, ls=(0, (4, 3)),
            zorder=3)
    ax.plot(centers, acc, color=RED, lw=1.4, marker="o", ms=2.6, zorder=5,
            label="实际通过率")
    ax.vlines(centers, acc, centers, color=RED, lw=0.7, ls=(0, (2, 2)),
              zorder=4)

    ax.text(1.005, 0.655, "判 0.95 的桶\n实际只过 78%", fontsize=6.2,
            color=RED, ha="right", va="center", linespacing=1.4)

    ax.text(0.455, 0.985, "ECE = 0.10", fontsize=7.2, color=NAVY,
            ha="left", va="top", weight="bold")
    ax.text(0.455, 0.945, "等于各桶偏差按样本量加权平均", fontsize=6.2,
            color=GRAY, ha="left", va="top")

    ax.set_xlim(0.45, 1.02)
    ax.set_ylim(0.45, 1.02)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("判定模型给出的分数", labelpad=2)
    ax.set_ylabel("人工判定通过率")
    ax.grid(True, color=LGRAY, lw=0.4, alpha=0.7)

    save(fig, "06/calibration.png")


# ---------------------------------------------------------------- 07 三级评测

def fig_07_stack():
    """第 7 章：三级评测，样本量涨一个数量级，可分辨差异缩一半。"""
    fig, ax = canvas(2.05)

    cards = [
        ("私有集回归", "300 条", "能分辨约 5 个点", "每天可跑", NAVY),
        ("发布前评测", "3000 条", "能分辨约 3 个点", "每次发版", GOLD),
        ("线上 A/B", "4.6 万用户", "能分辨 0.6 个点", "两周", RED),
    ]

    cw, ch, gap = 3.06, 1.95, 0.36
    y = 1.50
    for i, (title, big, d1, d2, color) in enumerate(cards):
        cx = 0.28 + i * (cw + gap)
        box(ax, cx, y, cw, ch, "", fc=tint(color, 0.09), ec=color, lw=0.9)
        txt(ax, cx + cw / 2, y + ch - 0.33, title, fs=FS - 0.4, weight="bold")
        txt(ax, cx + cw / 2, y + ch - 0.93, big, fs=12.0, color=color,
            weight="bold")
        note(ax, cx + cw / 2, y + 0.56, d1, fs=FS_S - 0.6)
        note(ax, cx + cw / 2, y + 0.28, d2, fs=FS_S - 0.9)
        if i < 2:
            arrow(ax, (cx + cw + 0.04, y + ch / 2),
                  (cx + cw + gap - 0.04, y + ch / 2), lw=1.0)

    note(ax, 5.20, 1.12,
         "自左向右：样本量涨一个数量级，能分辨的差异缩一半，周期从一天到两周",
         fs=FS_S - 0.5)
    note(ax, 5.20, 0.82, "绝大多数改动应该死在第一级，不必浪费两周的线上实验",
         fs=FS_S - 0.5)

    save(fig, "07/eval_stack.png")


# ---------------------------------------------------------------- 07b 功效

def fig_07_power():
    """第 7 章：样本量与能分辨的最小差异（80% 功效、双侧 5%）。"""
    setup()
    fig = plt.figure(figsize=(W, 2.52))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.135, 0.215, 0.775, 0.755])

    n = np.logspace(2, 6, 240)
    z = 1.96 + 0.84

    series = [(0.12, RED, "基线 12%（低频行为）"),
              (0.50, NAVY, "基线 50%（成对比较）"),
              (0.80, GOLD, "基线 80%（已成熟的问答）")]
    for p, color, label in series:
        mde = 100.0 * z * np.sqrt(2.0 * p * (1.0 - p) / n)
        ax.plot(n, mde, color=color, lw=1.35, label=label)

    marks = [(300, 0.12), (3000, 0.12), (46000, 0.12)]
    lines = []
    for nn, p in marks:
        mde = 100.0 * z * np.sqrt(2.0 * p * (1.0 - p) / nn)
        ax.plot([nn], [mde], color=RED, marker="o", ms=3.2, zorder=6)
        ax.vlines(nn, 0.25, mde, color=RED, lw=0.7, ls=(0, (2, 2)),
                  alpha=0.75, zorder=3)
        lines.append(f"{nn:,} 条  →  {mde:.1f} 点")

    ax.text(1.08e2, 0.92, "\n".join(lines), fontsize=6.4, color=RED,
            ha="left", va="top", linespacing=1.6)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(100, 1e6)
    ax.set_ylim(0.25, 30)
    ax.set_yticks([0.3, 1, 3, 10, 30])
    ax.set_yticklabels(["0.3", "1", "3", "10", "30"])
    ax.set_xlabel("每组样本量", labelpad=2)
    ax.set_ylabel("能分辨的最小差异（百分点）")
    ax.grid(True, which="major", color=LGRAY, lw=0.45, alpha=0.8)
    ax.legend(loc="upper right", frameon=False, fontsize=6.4,
              handlelength=2.0, borderaxespad=0.4)



    save(fig, "07/power_curve.png")


# ---------------------------------------------------------------- 08 串联防线

def fig_08_chain():
    """第 8 章：三层防线串联，漏过率相乘、代价相加。"""
    fig, ax = canvas(2.05)

    stages = [
        ("输入侧", "规则 + 分类器", "漏 30%", "误拒 1.0%", NAVY),
        ("表示侧", "方向 / 特征监控", "漏 50%", "误拒 2.0%", TEAL),
        ("输出侧", "过滤 + 判定模型", "漏 20%", "误拒 0.5%", GOLD),
    ]

    bw, bh, gap = 2.34, 0.92, 0.52
    x = 0.42
    for i, (name, how, miss, cost, color) in enumerate(stages):
        box(ax, x, 2.62, bw, bh, "", fc=tint(color, 0.10), ec=color, lw=0.9)
        txt(ax, x + bw / 2, 3.33, name, fs=FS - 0.7, weight="bold")
        note(ax, x + bw / 2, 3.05, how, fs=FS_S - 0.9)
        note(ax, x + bw / 2, 2.79, miss, fs=FS_S - 0.5, color=color)
        note(ax, x + bw / 2, 2.36, cost, fs=FS_S - 0.9)
        if i < 2:
            arrow(ax, (x + bw + 0.04, 3.08), (x + bw + gap - 0.04, 3.08), lw=0.9)
        x += bw + gap

    arrow(ax, (8.52, 3.08), (9.18, 3.08), lw=0.9)
    note(ax, 9.66, 3.20, "放行", fs=FS - 0.6, color=RED)
    note(ax, 9.62, 2.94, "3%", fs=13.0, color=RED, weight="bold")

    ax.plot([0.42, 9.92], [2.14, 2.14], color=LGRAY, lw=0.8, zorder=2)

    txt(ax, 5.20, 1.84, "0.30 × 0.50 × 0.20 = 0.030", fs=FS + 0.4)
    note(ax, 5.20, 1.52, "漏过率相乘：三层都漏才出事，所以是乘法", fs=FS_S - 0.4)
    note(ax, 5.20, 1.24, "1.0% + 2.0% + 0.5% = 3.5%", fs=FS_S - 0.2, color=RED)
    note(ax, 5.20, 0.96, "误拒率相加：任一层误杀，用户都会看到拒绝", fs=FS_S - 0.4)
    note(ax, 5.20, 0.58, "这就是「收益相乘、代价相加」：多一层挡的攻击变少，误杀的痛是累加的",
         fs=FS_S - 0.6)

    save(fig, "08/defense_chain.png")


FIGS = {
    "01": fig_01_ladder,
    "02": fig_02_probe,
    "02b": fig_02_sweep,
    "06b": fig_06_calibration,
    "07b": fig_07_power,
    "08": fig_08_chain,
    "03": fig_03_sae,
    "04": fig_04_induction,
    "05": fig_05_lens,
    "06": fig_06_contamination,
    "07": fig_07_stack,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
