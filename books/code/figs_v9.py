# -*- coding: utf-8 -*-
"""《大模型技术全景 · 多模态与生成篇》（第九卷）插图。

运行：
    python books/code/figs_v9.py          # 全部重画
    python books/code/figs_v9.py 01 07    # 只画指定编号

输出：
    books/v9-multimodal/images/01/tokens.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.colors import to_rgb

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L,
                      NAVY_XL, RED, TEAL, arrow, box, plt, setup)

# 小字用雅黑，缩到 130 mm 后不发虚
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v9-multimodal" / "images"

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


# ---------------------------------------------------------------- 01 token

def fig_01_tokens():
    """第 1 章：边长与 token 数的平方关系，A4 扫描件落在哪。"""
    fig, ax = canvas(2.62)

    txt(ax, 5.20, 5.00, "边长翻一倍，块数变四倍", fs=FS + 0.8)
    note(ax, 5.20, 4.70, "按 14 像素切块，纵轴为对数刻度")

    y0, y1 = 0.72, 4.08          # 对应 100 → 100000
    xl, xr = 1.62, 9.92

    def ypos(n):
        return y0 + (math.log10(n) - 2.0) / 3.0 * (y1 - y0)

    for n, lab in ((100, "100"), (1000, "1k"), (10000, "1万"), (100000, "10万")):
        y = ypos(n)
        ax.plot([xl, xr], [y, y], color=LGRAY, lw=0.6, zorder=1)
        note(ax, xl - 0.12, y, lab, fs=FS_S, ha="right")

    cases = [
        ("224²", 256, NAVY_L),
        ("336²", 576, NAVY_L),
        ("448²", 1024, NAVY_L),
        ("896²", 4096, TEAL),
        ("1024²", 5329, TEAL),
        ("A4 扫描", 44678, GOLD),
    ]
    xs = [2.28, 3.60, 4.92, 6.24, 7.56, 8.88]
    for (lab, n, color), cx in zip(cases, xs):
        h = ypos(n) - y0
        box(ax, cx - 0.48, y0, 0.96, h, "", fc=tint(color, 0.18),
            ec=color, lw=0.9, rounded=0.03)
        txt(ax, cx, ypos(n) + 0.16, f"{n:,}", fs=FS_S, color=INK)
        note(ax, cx, y0 - 0.26, lab, fs=FS_S)

    note(ax, xr, 0.14, "A4 按 300 dpi 扫描为 2480×3508 像素", fs=FS_S - 0.4, ha="right")
    ax.plot([xl, xr], [y0, y0], color=GRAY, lw=0.8, zorder=2)

    save(fig, "01/tokens.png")


# ---------------------------------------------------------------- 02 对比学习

def fig_02_contrast():
    """第 2 章：一个批次就是一个相似度矩阵，对角线是唯一正样本。"""
    fig, ax = canvas(2.30)

    txt(ax, 5.20, 4.36, "一个批次 = 一个相似度矩阵", fs=FS + 0.8)
    note(ax, 5.20, 4.06, "只有对角线上是真正的图与文")

    n = 5
    cw = 0.52
    left, bottom = 0.86, 0.92
    for i in range(n):
        for j in range(n):
            pos = (i == j)
            ax.add_patch(plt.Rectangle(
                (left + j * cw, bottom + (n - 1 - i) * cw), cw, cw,
                facecolor=tint(NAVY, 0.72) if pos else tint(GRAY, 0.10),
                edgecolor="white", lw=1.4, zorder=3))
    note(ax, left + n * cw / 2, bottom - 0.30, "文本编码 n 条", fs=FS_S)
    note(ax, left - 0.20, bottom + n * cw / 2, "图像\n编码 m 条",
         fs=FS_S, ha="center", rotation=90)

    note(ax, 5.20, bottom - 0.56,
         "对角线是正样本，其余全为负样本", fs=FS_S - 0.2, color=NAVY)

    arrow(ax, (4.60, 2.20), (5.32, 2.20), lw=0.9)

    txt(ax, 7.62, 3.52, "批次大小决定负样本数", fs=FS, weight="bold")
    rows = [
        ("n = 1024", "每个样本 1023 个负样本"),
        ("n = 8192", "每个样本 8191 个负样本"),
        ("n = 32768", "每个样本 3.2 万个负样本"),
    ]
    for k, (a, b) in enumerate(rows):
        y = 2.92 - k * 0.62
        txt(ax, 6.06, y, a, fs=FS_S, ha="left", color=NAVY)
        txt(ax, 7.42, y, b, fs=FS_S - 0.2, ha="left", color=INK)
    note(ax, 7.62, 1.08, "批次再大，矩阵也只装得下 n² 个格子", fs=FS_S)
    note(ax, 7.62, 0.74, "所以这类训练靠堆卡，不靠堆参数", fs=FS_S)

    save(fig, "02/contrast.png")


# ---------------------------------------------------------------- 03 三阶段

def fig_03_stages():
    """第 3 章：三阶段里谁冻结、谁训练、数据量级。"""
    fig, ax = canvas(2.24)

    txt(ax, 5.20, 4.20, "每一阶段解冻的东西不一样", fs=FS + 0.8)
    note(ax, 5.20, 3.90, "灰为冻结，深色为参与训练")

    stages = [
        ("第一阶段", "对齐", ["连接层", "视觉编码器", "语言模型"],
         [1, 0, 0], "几亿图文对", "学会翻译"),
        ("第二阶段", "指令微调", ["连接层", "视觉编码器", "语言模型"],
         [1, 0, 1], "百万级问答", "学会答题"),
        ("第三阶段", "偏好对齐", ["连接层", "视觉编码器", "语言模型"],
         [1, 0, 1], "十万级比较", "修行为"),
    ]

    bw, bh = 2.42, 0.46
    for cx, (name, sub, blocks, flags, data, goal) in zip([2.10, 5.20, 8.30], stages):
        txt(ax, cx, 3.42, name, fs=FS + 0.2, weight="bold")
        note(ax, cx, 3.14, sub, fs=FS_S)
        for k, (b, on) in enumerate(zip(blocks, flags)):
            y = 2.44 - k * 0.60
            fc = tint(NAVY, 0.16) if on else tint(GRAY, 0.08)
            ec = NAVY if on else LGRAY
            box(ax, cx - bw / 2, y, bw, bh, b, fc=fc, ec=ec,
                tc=INK if on else GRAY, fs=FS_S, rounded=0.04)
        note(ax, cx, 0.88, data, fs=FS_S)
        note(ax, cx, 0.58, goal, fs=FS_S, color=NAVY)

    save(fig, "03/stages.png")


# ---------------------------------------------------------------- 04 CTC

def fig_04_ctc():
    """第 4 章：CTC 的格子与一条合法路径。"""
    fig, ax = canvas(2.18)

    txt(ax, 5.20, 4.12, "CTC 把所有路径都加起来", fs=FS + 0.8)
    note(ax, 5.20, 3.82, "横轴是帧，纵轴是输出字符加一个空白")

    labels = ["空", "你", "好", "吗"]
    T = 6
    cw, ch = 0.60, 0.52
    left, bottom = 0.92, 0.80

    for j in range(T):
        for i, lab in enumerate(labels):
            ax.add_patch(plt.Rectangle(
                (left + j * cw, bottom + i * ch), cw, ch,
                facecolor="white", edgecolor=LGRAY, lw=0.7, zorder=2))
    for i, lab in enumerate(labels):
        note(ax, left - 0.22, bottom + i * ch + ch / 2, lab, fs=FS_S, ha="right")
    for j in range(T):
        note(ax, left + j * cw + cw / 2, bottom - 0.26, f"t{j + 1}", fs=FS_S)

    # 一条合法路径：∅ 你 ∅ 好 好 吗
    path = [(0, 0), (1, 1), (2, 0), (3, 2), (4, 2), (5, 3)]
    pts = [(left + j * cw + cw / 2, bottom + i * ch + ch / 2) for j, i in path]
    for p, q in zip(pts, pts[1:]):
        arrow(ax, p, q, color=NAVY, lw=1.2, shrink=6)
    for p in pts:
        ax.plot([p[0]], [p[1]], marker="o", ms=3.4, color=NAVY, zorder=9)

    note(ax, left + T * cw / 2, 0.24,
         "压掉空白、合并重复，路径输出「你好吗」", fs=FS_S)

    txt(ax, 7.86, 3.02, "约束", fs=FS, weight="bold")
    lines = [
        "同一字符重复出现，",
        "中间必须隔一个空白，",
        "否则「好」和「好好」分不开。",
    ]
    for k, s in enumerate(lines):
        note(ax, 7.86, 2.62 - k * 0.34, s, fs=FS_S)
    note(ax, 7.86, 1.32, "帧与帧之间假设独立，", fs=FS_S)
    note(ax, 7.86, 1.02, "所以可以对每一帧并行算。", fs=FS_S)

    save(fig, "04/ctc.png")


# ---------------------------------------------------------------- 06 视频

def fig_06_video():
    """第 6 章：两遍看视频，第一遍便宜，第二遍贵。"""
    fig, ax = canvas(2.32)

    txt(ax, 5.20, 4.36, "两遍看视频", fs=FS + 0.8)
    note(ax, 5.20, 4.06, "第一遍用来定位，第二遍才看得清")

    stages = [
        ("音频轨", "ASR 转文字", "约 2 万 token", NAVY),
        ("稀疏帧", "每 5 秒一帧", "约 18 万 token", TEAL),
        ("候选片段", "加密到 2 帧/秒", "约 8 万 token", GOLD),
    ]
    bw, bh = 2.52, 1.12
    xs = [1.52, 5.20, 8.88]
    for (name, how, cost, color), cx in zip(stages, xs):
        box(ax, cx - bw / 2, 1.86, bw, bh, "", fc=tint(color, 0.12),
            ec=color, lw=0.9, rounded=0.05)
        txt(ax, cx, 2.72, name, fs=FS + 0.4, weight="bold")
        note(ax, cx, 2.42, how, fs=FS_S, color=INK)
        note(ax, cx, 2.06, cost, fs=FS_S)

    for i in range(2):
        arrow(ax, (xs[i] + bw / 2 + 0.04, 2.42),
              (xs[i + 1] - bw / 2 - 0.04, 2.42), lw=1.0)

    note(ax, 5.20, 1.42, "第一遍覆盖全片，第二遍只看命中的四十秒", fs=FS_S)
    note(ax, 5.20, 1.08, "第一遍的结果可以缓存，同一段视频只算一次", fs=FS_S, color=NAVY)

    save(fig, "06/two-pass.png")


# ---------------------------------------------------------------- 07 扩散

def fig_07_diffusion():
    """第 7 章：前向加噪的两条曲线，加潜空间的压缩比。"""
    fig, ax = canvas(2.34)

    txt(ax, 5.20, 4.38, "前向是一条有公式的路", fs=FS + 0.8)
    note(ax, 5.20, 4.08, "信号越来越弱，噪声越来越强，两者平方和为 1")

    x0, x1 = 1.10, 5.86
    y0, y1 = 1.22, 3.46

    ax.plot([x0, x1], [y0 - 0.10, y0 - 0.10], color=GRAY, lw=0.8)
    ax.plot([x0, x0], [y0 - 0.10, y1], color=GRAY, lw=0.8)

    N = 60
    sig, noi = [], []
    for k in range(N + 1):
        t = k / N
        # 线性 beta，从 1e-4 到 0.02 的和，简化为余弦形式便于画图
        ab = math.cos((t + 0.008) / 1.008 * math.pi / 2) ** 2
        sig.append((x0 + t * (x1 - x0), y0 + ab * (y1 - y0)))
        noi.append((x0 + t * (x1 - x0), y0 + (1 - ab) * (y1 - y0)))

    ax.plot([p[0] for p in sig], [p[1] for p in sig], color=NAVY, lw=1.4, zorder=5)
    ax.plot([p[0] for p in noi], [p[1] for p in noi], color=GOLD, lw=1.4, zorder=5)

    txt(ax, 3.10, 3.10, "信号权重", fs=FS_S, color=NAVY, ha="left")
    txt(ax, 5.42, 2.42, "噪声权重", fs=FS_S, color=GOLD, ha="right")

    note(ax, 1.10, 0.94, "t = 0　原图", fs=FS_S)
    note(ax, 5.86, 0.94, "t = T　纯噪声", fs=FS_S, ha="right")
    note(ax, 3.48, 0.56, "采样时从右往左走，每一步减掉一点预测噪声", fs=FS_S)

    # 右侧：潜空间压缩
    txt(ax, 8.06, 3.62, "潜空间的压缩比", fs=FS, weight="bold")
    bx, by = 6.44, 1.62
    ax.add_patch(plt.Rectangle((bx, by), 1.55, 1.55, facecolor=tint(NAVY, 0.14),
                               edgecolor=NAVY, lw=0.9, zorder=3))
    ax.add_patch(plt.Rectangle((bx + 1.66, by + 0.10), 0.19, 0.19,
                               facecolor=tint(GOLD, 0.35), edgecolor=GOLD,
                               lw=0.9, zorder=3))
    note(ax, bx + 0.78, by + 0.78, "1024²", fs=FS_S, color=NAVY)
    note(ax, bx + 1.78, by - 0.20, "128²", fs=FS_S, color=GOLD)
    note(ax, 8.20, 1.08, "3.1M 个数 → 65k 个数", fs=FS_S, color=INK)
    note(ax, 8.20, 0.80, "面积小 1/64，通道多一个，净剩 1/48", fs=FS_S)

    save(fig, "07/noising.png")


# ---------------------------------------------------------------- 08 流匹配

def fig_08_flow():
    """第 8 章：弯曲路径与直线路径，步数差在哪。"""
    fig, ax = canvas(2.20)

    txt(ax, 5.20, 4.06, "路径越直，步子越大", fs=FS + 0.8)
    note(ax, 5.20, 3.76, "同样从噪声走到图，左边绕弯，右边直着走")

    # 左：扩散的弯路径
    note(ax, 2.72, 3.40, "扩散：逐步去噪", fs=FS, color=NAVY)
    pts = []
    for k in range(9):
        t = k / 8
        pts.append((1.06 + t * 2.86, 1.02 + 1.58 * (1 - (1 - t) ** 2) ** 1.5))
    for p, q in zip(pts, pts[1:]):
        arrow(ax, p, q, color=NAVY, lw=0.9, shrink=4)
    ax.plot([pts[0][0]], [pts[0][1]], marker="o", ms=5, color=GRAY, zorder=9)
    ax.plot([pts[-1][0]], [pts[-1][1]], marker="s", ms=5, color=NAVY, zorder=9)
    note(ax, 1.06, 0.78, "噪声", fs=FS_S)
    note(ax, 3.96, 0.78, "数据", fs=FS_S)
    note(ax, 2.72, 0.38, "50 步，每步都要完整前向", fs=FS_S)

    # 右：流匹配的直线
    note(ax, 7.68, 3.40, "流匹配：沿直线积分", fs=FS, color=GOLD)
    p0, p1 = (6.02, 1.02), (8.88, 2.60)
    for k in range(4):
        a = (p0[0] + (p1[0] - p0[0]) * k / 4, p0[1] + (p1[1] - p0[1]) * k / 4)
        b = (p0[0] + (p1[0] - p0[0]) * (k + 1) / 4,
             p0[1] + (p1[1] - p0[1]) * (k + 1) / 4)
        arrow(ax, a, b, color=GOLD, lw=1.2, shrink=4)
    ax.plot([p0[0]], [p0[1]], marker="o", ms=5, color=GRAY, zorder=9)
    ax.plot([p1[0]], [p1[1]], marker="s", ms=5, color=GOLD, zorder=9)
    note(ax, 6.02, 0.78, "噪声", fs=FS_S)
    note(ax, 8.88, 0.78, "数据", fs=FS_S)
    note(ax, 7.68, 0.38, "4 到 8 步就能落在同一处", fs=FS_S)

    save(fig, "08/paths.png")


# ---------------------------------------------------------------- 09 统一

def fig_09_unify():
    """第 9 章：三种折中，差别在中间用什么通信。"""
    fig, ax = canvas(2.28)

    txt(ax, 5.20, 4.28, "三种折中", fs=FS + 0.8)
    note(ax, 5.20, 3.98, "差别在于两个模型之间用什么传话")

    cols = [
        ("串接", "文本", "理解模型 → 提示词 → 生成模型", GRAY),
        ("统一输入", "共享前缀", "同一模型看，扩散模型画", TEAL),
        ("共享主干", "隐状态", "一个主干，两个输出头", GOLD),
    ]
    for (name, mid, desc, color), cx in zip(cols, [1.90, 5.20, 8.50]):
        txt(ax, cx, 3.18, name, fs=FS + 0.2, weight="bold")
        box(ax, cx - 1.02, 2.34, 2.04, 0.46, "理解", fc=tint(NAVY, 0.12),
            ec=NAVY, fs=FS_S, rounded=0.04)
        box(ax, cx - 1.02, 1.56, 2.04, 0.46, mid, fc=tint(color, 0.16),
            ec=color, fs=FS_S, rounded=0.04)
        box(ax, cx - 1.02, 0.78, 2.04, 0.46, "生成", fc=tint(GOLD, 0.12),
            ec=GOLD, fs=FS_S, rounded=0.04)
        for y in (2.34, 1.56):
            arrow(ax, (cx, y), (cx, y - 0.24), lw=0.9)
        note(ax, cx, 0.38, desc, fs=FS_S - 0.4, color=INK)

    save(fig, "09/three-ways.png")


FIGS = {
    "01": fig_01_tokens,
    "02": fig_02_contrast,
    "03": fig_03_stages,
    "04": fig_04_ctc,
    "06": fig_06_video,
    "07": fig_07_diffusion,
    "08": fig_08_flow,
    "09": fig_09_unify,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
