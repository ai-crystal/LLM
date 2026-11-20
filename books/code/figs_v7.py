# -*- coding: utf-8 -*-
"""《大模型技术全景 · 推理与部署篇》（第七卷）插图。

运行：
    python books/code/figs_v7.py          # 全部重画
    python books/code/figs_v7.py 03       # 只画指定编号

输出：
    books/v7-inference/images/01/two-phases.png
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle

import figstyle as st
from figstyle import (BG, GOLD, GRAY, INK, LGRAY, NAVY, NAVY_L, NAVY_XL,
                      RED, TEAL, arrow, box, plt, setup)

# Noto Sans SC 在本机只注册到 weight=100，小字会发虚；换雅黑，缩到 130 mm 后仍实。
st.FONT = "Microsoft YaHei"

ROOT = Path(__file__).resolve().parent.parent      # books/
OUTDIR = ROOT / "v7-inference" / "images"

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
        weight="normal", z=8, rotation=0):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, zorder=z, linespacing=1.4, rotation=rotation)


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


# ---------------------------------------------------------------- 01 两个阶段

def fig_01_two_phases():
    """第 1 章：预填充吃算力，解码吃带宽；一条时间轴上的两个指标。"""
    fig, ax = canvas(3.10)

    # 左：预填充
    box(ax, 0.30, 2.70, 4.55, 2.95, "", fc=tint(NAVY, 0.05), ec=NAVY_L, lw=0.9)
    txt(ax, 2.575, 5.38, "预填充", fs=FS + 1.2, weight="bold")
    note(ax, 2.575, 5.10, "把整段提示一次压成状态")

    for i in range(7):
        y = 3.74 + i * 0.185
        ax.add_patch(Rectangle((0.62, y), 1.55, 0.13, facecolor=tint(NAVY, 0.30),
                               edgecolor="none", zorder=4))
    txt(ax, 1.395, 3.46, "2000 行", fs=FS_S, color=GRAY)
    txt(ax, 2.85, 4.32, "×", fs=FS + 2, color=GRAY)
    ax.add_patch(Rectangle((3.06, 3.62), 0.34, 1.36, facecolor=tint(NAVY, 0.55),
                           edgecolor="none", zorder=4))
    txt(ax, 3.23, 3.38, "d×d 权重", fs=FS_S, color=GRAY)
    txt(ax, 2.575, 2.96, "(2000×d)·(d×d)，一次乘完", fs=FS_S, color=INK)

    # 右：解码
    box(ax, 5.55, 2.70, 4.55, 2.95, "", fc=tint(GOLD, 0.07), ec=GOLD, lw=0.9)
    txt(ax, 7.825, 5.38, "解码", fs=FS + 1.2, weight="bold")
    note(ax, 7.825, 5.10, "一步只算一行，但要把权重读完")

    ax.add_patch(Rectangle((5.87, 4.34), 1.55, 0.13, facecolor=tint(GOLD, 0.45),
                           edgecolor="none", zorder=4))
    txt(ax, 6.645, 4.06, "1 行", fs=FS_S, color=GRAY)
    txt(ax, 7.85, 4.40, "×", fs=FS + 2, color=GRAY)
    ax.add_patch(Rectangle((8.15, 3.62), 0.34, 1.36, facecolor=tint(NAVY, 0.55),
                           edgecolor="none", zorder=4))
    txt(ax, 8.32, 3.38, "同一份权重", fs=FS_S, color=GRAY)

    txt(ax, 7.825, 2.96, "算 1 行和算 64 行，读的字节一样多", fs=FS_S, color=INK)

    txt(ax, 2.575, 2.34, "吃算力，卡在 FLOPs", fs=FS - 0.2, color=NAVY)
    txt(ax, 7.825, 2.34, "吃带宽，卡在 GB/s", fs=FS - 0.2, color=GOLD)

    # 时间轴
    y0 = 1.62
    ax.plot([0.55, 9.85], [y0, y0], color=LGRAY, lw=0.9, zorder=1)
    ax.plot([0.55, 2.05], [y0, y0], color=NAVY, lw=2.6, zorder=3)
    ax.plot([2.05, 9.85], [y0, y0], color=GOLD, lw=2.6, zorder=3)
    for x in (0.55, 2.05, 9.85):
        ax.plot([x], [y0], marker="o", ms=3.4, color=INK, zorder=5)
    txt(ax, 0.55, y0 - 0.28, "请求到达", fs=FS_S, ha="center")
    txt(ax, 2.05, y0 + 0.30, "第一个 token", fs=FS_S, ha="center")
    txt(ax, 9.90, y0 - 0.28, "全部输出完", fs=FS_S, ha="center")

    ax.annotate("", xy=(0.62, 0.78), xytext=(2.00, 0.78),
                arrowprops=dict(arrowstyle="<|-|>", color=NAVY, lw=0.9,
                                shrinkA=0, shrinkB=0))
    txt(ax, 1.31, 0.48, "TTFT 首字延迟", fs=FS_S, color=NAVY)

    ax.annotate("", xy=(3.05, 0.78), xytext=(3.85, 0.78),
                arrowprops=dict(arrowstyle="<|-|>", color=GOLD, lw=0.9,
                                shrinkA=0, shrinkB=0))
    txt(ax, 5.62, 0.78, "TPOT 每 token 间隔，整条时间轴上字出来的密度",
        fs=FS_S, color=GOLD, ha="left")

    save(fig, "01/two-phases.png")


# ---------------------------------------------------------------- 02 显存账本

def fig_02_kv_budget():
    """第 2 章：一张卡的显存四块，以及分页缓存把碎片变成块内浪费。"""
    fig, ax = canvas(2.75)

    # 左：显存堆叠条
    txt(ax, 2.55, 5.14, "显存被四块瓜分", fs=FS, weight="bold")
    note(ax, 2.55, 4.86, "80 GB 卡，7B 模型，FP16 权重，2K 上下文", fs=FS_S)

    x0, wbar = 0.55, 1.10
    total = 80.0
    bar_h = 3.45
    segs = [
        ("权重 14 GB", 14, NAVY, 0.55),
        ("KV 缓存 42 GB", 42, TEAL, 0.22),
        ("激活 12 GB", 12, GOLD, 0.30),
        ("框架与碎片 12 GB", 12, GRAY, 0.14),
    ]
    y = 0.95
    for lab, gb, c, f in segs:
        h = gb / total * bar_h
        ax.add_patch(Rectangle((x0, y), wbar, h, facecolor=tint(c, f),
                               edgecolor=c, lw=0.7, zorder=4))
        y += h
    ax.plot([x0 + wbar + 0.10, x0 + wbar + 0.10], [0.95, 0.95 + bar_h],
            color=GRAY, lw=0.7)

    lab_top = 0.95 + bar_h
    for lab, gb, c, f in reversed(segs):
        h = gb / total * bar_h
        txt(ax, x0 + wbar + 0.24, lab_top - h / 2, lab, fs=FS_S, color=INK, ha="left")
        lab_top -= h

    note(ax, 2.55, 0.52, "优化顺序从下往上：碎片 → 激活 → 缓存 → 权重", fs=FS_S)

    # 右：分页块表
    txt(ax, 7.75, 5.14, "分页：逻辑连续，物理分散", fs=FS, weight="bold")

    bw, gap, bh = 0.46, 0.07, 0.52
    cx0 = 6.16

    txt(ax, 5.52, 3.82, "逻辑", fs=FS_S, color=GRAY, ha="left")
    for i in range(5):
        ax.add_patch(Rectangle((cx0 + i * (bw + gap), 3.56), bw, bh,
                               facecolor=tint(NAVY, 0.16), edgecolor=NAVY_L, lw=0.7))
        txt(ax, cx0 + i * (bw + gap) + bw / 2, 3.82, f"{i}", fs=FS_S - 0.8)

    txt(ax, 5.52, 2.21, "物理", fs=FS_S, color=GRAY, ha="left")
    slots = {0: 3, 1: 0, 2: 6, 3: 1, 4: 5}
    for i in range(7):
        px = cx0 + i * (bw + gap)
        ax.add_patch(Rectangle((px, 1.95), bw, bh, facecolor="white",
                               edgecolor=LGRAY, lw=0.6, zorder=2))
    for i, s in slots.items():
        px = cx0 + s * (bw + gap)
        ax.add_patch(Rectangle((px, 1.95), bw, bh, facecolor=tint(TEAL, 0.28),
                               edgecolor=TEAL, lw=0.8, zorder=3))
        txt(ax, px + bw / 2, 2.21, f"{i}", fs=FS_S - 0.8)

    for i, s in slots.items():
        p0 = (cx0 + i * (bw + gap) + bw / 2, 3.52)
        p1 = (cx0 + s * (bw + gap) + bw / 2, 2.51)
        arrow(ax, p0, p1, color=GRAY, lw=0.45, rad=0.0, shrink=1)

    note(ax, 7.75, 1.56,
         "块大小 16 个 token，每个请求一张块表", fs=FS_S)
    note(ax, 7.75, 1.28,
         "最坏浪费 15 个 token 的槽位，好过给每条请求预留 4096", fs=FS_S)

    save(fig, "02/kv-budget.png")


# ---------------------------------------------------------------- 03 静态批 vs 连续批

def fig_03_batching():
    """第 3 章：静态批的空转与连续批的填空。"""
    fig, ax = canvas(3.10)

    x0, k = 0.95, 0.92          # 时间 t → x
    row_h, gap = 0.24, 0.05
    T = 8.9

    def bar(y, a, b, color, f, lw=0.5, hatch=False):
        xa, xb = x0 + a * k, x0 + b * k
        if hatch:
            ax.add_patch(Rectangle((xa, y), xb - xa, row_h, facecolor="white",
                                   edgecolor=LGRAY, lw=0.5, hatch="////", zorder=2))
        else:
            ax.add_patch(Rectangle((xa, y), xb - xa, row_h,
                                   facecolor=tint(color, f), edgecolor=color,
                                   lw=lw, zorder=4))

    # ---- 静态批
    txt(ax, 0.55, 5.90, "静态批", fs=FS, weight="bold", ha="left")
    note(ax, 10.05, 5.90, "整批等最长的那个，其余空转", fs=FS_S, ha="right")

    top1 = 5.62
    static_len = [2.2, 3.4, 4.8, 6.2, 7.5, 8.9]
    for i, L in enumerate(static_len):
        y = top1 - i * (row_h + gap) - row_h
        bar(y, 0, L, NAVY, 0.30)
        bar(y, L, T, NAVY, 0.05, hatch=True)
    bot1 = top1 - 6 * (row_h + gap)

    ax.plot([x0 + T * k, x0 + T * k], [bot1 - 0.04, top1 + 0.10], color=RED, lw=0.8)
    txt(ax, x0 + T * k + 0.22, (bot1 + top1) / 2, "整批一起结束", fs=FS_S - 0.8,
        color=RED, ha="center", va="center", rotation=90)

    # ---- 连续批
    txt(ax, 0.55, 3.50, "连续批", fs=FS, weight="bold", ha="left")
    note(ax, 10.05, 3.50, "每步一换：谁跑完谁走，空位给新来的", fs=FS_S, ha="right")

    top2 = 3.22
    lanes = [
        [(0.0, 2.2, NAVY), (2.2, 6.5, TEAL)],
        [(0.0, 3.4, NAVY), (3.4, 8.9, TEAL)],
        [(0.0, 4.8, NAVY), (4.8, 7.4, TEAL)],
        [(0.0, 6.2, NAVY)],
        [(0.0, 7.5, NAVY)],
        [(0.0, 8.9, NAVY)],
    ]
    for i, segs in enumerate(lanes):
        y = top2 - i * (row_h + gap) - row_h
        for a, b, c in segs:
            bar(y, a, b, c, 0.28, lw=0.6)
    bot2 = top2 - 6 * (row_h + gap)

    txt(ax, 0.55, bot2 - 0.44,
        "斜线是空转的槽位，仍占显存、仍在算，只是产出无效", fs=FS_S, ha="left")
    txt(ax, 0.55, bot2 - 0.74,
        "深色是首批请求，浅色是后来填进同一个槽位的请求", fs=FS_S, ha="left")
    txt(ax, 0.55, bot2 - 1.04,
        "两排的横轴是同一段时间，上排的总产出只有下排的一半", fs=FS_S,
        color=GRAY, ha="left")

    save(fig, "03/batching-timeline.png")


# ---------------------------------------------------------------- 05 量化粒度

def fig_05_granularity():
    """第 5 章：一个缩放因子管多少个数。"""
    fig, ax = canvas(2.05)

    panels = [
        ("每张量", "整层一个 s", "all"),
        ("每通道", "每个输出通道一个 s", "row"),
        ("每组（128）", "每 128 个权重一个 s", "pair"),
    ]
    cells = 4          # 4×4 网格
    cell = 0.42
    labels = [
        "额外开销 ≈ 0 bit/权重",
        "额外开销 ≈ 16/4096 ≈ 0.004 bit",
        "额外开销 ≈ 16/128 = 0.125 bit",
    ]

    x0 = 0.55
    span = (10.40 - 0.55) / 3
    for k, ((name, desc, mode), extra) in enumerate(zip(panels, labels)):
        cx = x0 + span * k + span / 2
        gx = cx - cells * cell / 2
        gy = 1.42

        for r in range(cells):
            for c in range(cells):
                ax.add_patch(Rectangle((gx + c * cell, gy + r * cell),
                                       cell - 0.03, cell - 0.03,
                                       facecolor=tint(NAVY, 0.12),
                                       edgecolor=NAVY_L, lw=0.5, zorder=3))
        # 分组框
        if mode == "all":
            ax.add_patch(Rectangle((gx - 0.04, gy - 0.04),
                                   cells * cell + 0.05, cells * cell + 0.05,
                                   facecolor="none", edgecolor=RED, lw=1.0, zorder=5))
        elif mode == "row":
            for r in range(cells):
                ax.add_patch(Rectangle((gx - 0.04, gy + r * cell - 0.04),
                                       cells * cell + 0.05, cell + 0.02,
                                       facecolor="none", edgecolor=TEAL, lw=0.9, zorder=5))
        else:
            for r in range(cells):
                for h in range(2):
                    ax.add_patch(Rectangle((gx + h * 2 * cell - 0.04,
                                            gy + r * cell - 0.04),
                                           2 * cell + 0.01, cell + 0.02,
                                           facecolor="none", edgecolor=GOLD, lw=0.8, zorder=5))

        txt(ax, cx, 3.52, name, fs=FS, weight="bold")
        note(ax, cx, 3.26, desc, fs=FS_S)
        note(ax, cx, 0.98, extra, fs=FS_S - 0.2)
        note(ax, cx, 0.74, ["最省，误差最大", "常用折中", "4 位量化的默认"][k],
             fs=FS_S - 0.2, color=[GRAY, GRAY, INK][k])

    note(ax, 5.20, 0.28, "框线围起来的格子共用一个缩放因子；格子越少，误差越小，元数据越多",
         fs=FS_S)

    save(fig, "05/granularity.png")


# ---------------------------------------------------------------- 07 投机解码

def fig_07_spec_decode():
    """第 7 章：小模型猜四个，大模型一次前向验证，收下三个再加一个修正。"""
    fig, ax = canvas(2.55)

    bw, gap, bh = 1.60, 0.22, 0.62
    x0 = 1.36
    y_a, y_b, y_c = 4.15, 2.95, 1.55

    def cell(i, y, label, color, f, lw=0.9, fs=FS):
        x = x0 + i * (bw + gap)
        box(ax, x, y, bw, bh, "", fc=tint(color, f), ec=color, lw=lw)
        txt(ax, x + bw / 2, y + bh / 2, label, fs=fs, color=INK)
        return x

    # 草稿
    txt(ax, 0.45, y_a + bh / 2, "草稿", fs=FS + 0.4, weight="bold", ha="left")
    for i, (w, ok) in enumerate(zip(["春", "江", "潮", "水"], [1, 1, 1, 0])):
        c = TEAL if ok else RED
        cell(i, y_a, w, c, 0.18 if ok else 0.10, fs=FS + 0.8)
    note(ax, x0, 3.90, "小模型连跑四步，成本约主模型一步的 5%", fs=FS_S, ha="left")

    # 验证
    txt(ax, 0.45, y_b + bh / 2, "验证", fs=FS + 0.4, weight="bold", ha="left")
    for i, ok in enumerate([1, 1, 1, 0]):
        c = TEAL if ok else RED
        cell(i, y_b, "接受" if ok else "拒绝", c, 0.0, lw=1.0, fs=FS_S + 0.4)
    xc = x0 + 4 * (bw + gap)
    box(ax, xc, y_b, 1.34, bh, "", fc=tint(GOLD, 0.20), ec=GOLD, lw=1.0)
    txt(ax, xc + 0.67, y_b + bh / 2, "修正", fs=FS_S + 0.4, color=INK)
    note(ax, x0, 2.70, "主模型一次前向同时验证四个位置", fs=FS_S, ha="left")
    note(ax, xc + 0.67, 2.78, "拒绝后换成", fs=FS_S, color=GRAY)
    note(ax, xc + 0.67, 2.56, "主模型的采样", fs=FS_S, color=GRAY)

    arrow(ax, (8.52, y_a - 0.05), (8.52, y_b + bh + 0.05), color=NAVY, lw=1.0, shrink=0)

    # 产出
    txt(ax, 0.45, y_c + bh / 2, "产出", fs=FS + 0.4, weight="bold", ha="left")
    for i, w in enumerate(["春", "江", "潮", "水"]):
        c = TEAL if i < 3 else GOLD
        cell(i, y_c, w, c, 0.26, fs=FS + 0.8)
    note(ax, x0, 1.10,
         "一步产出四个 token：被接受的是小模型原样，被拒的位置由大模型补一个",
         fs=FS_S, ha="left")

    save(fig, "07/spec-decode.png")


# ---------------------------------------------------------------- 08 PD 分离

def fig_08_pd_split():
    """第 8 章：预填充池、传输层、解码池。"""
    fig, ax = canvas(2.55)

    # 预填充池
    box(ax, 0.35, 1.55, 3.05, 2.95, "", fc=tint(NAVY, 0.06), ec=NAVY_L, lw=0.9)
    txt(ax, 1.875, 4.28, "预填充池", fs=FS + 0.8, weight="bold")
    note(ax, 1.875, 4.00, "算力优先", fs=FS_S)
    for i, lab in enumerate(["卡 0", "卡 1", "卡 2"]):
        box(ax, 0.62, 3.42 - i * 0.58, 2.50, 0.44,
            lab, fc=tint(NAVY, 0.16), ec=NAVY_L, lw=0.6, fs=FS_S)
    note(ax, 1.875, 2.02, "每张卡吃一块长提示", fs=FS_S)
    note(ax, 1.875, 1.76, "算完立刻把 KV 交出去", fs=FS_S)

    # 解码池
    box(ax, 7.00, 1.55, 3.05, 2.95, "", fc=tint(GOLD, 0.08), ec=GOLD, lw=0.9)
    txt(ax, 8.525, 4.28, "解码池", fs=FS + 0.8, weight="bold")
    note(ax, 8.525, 4.00, "显存与带宽优先", fs=FS_S)
    for i, lab in enumerate(["卡 0", "卡 1", "卡 2"]):
        box(ax, 7.27, 3.42 - i * 0.58, 2.50, 0.44,
            lab, fc=tint(GOLD, 0.22), ec=GOLD, lw=0.6, fs=FS_S)
    note(ax, 8.525, 2.02, "每张卡挂几十条会话的长缓存", fs=FS_S)
    note(ax, 8.525, 1.76, "可以开投机解码", fs=FS_S)

    # 传输层
    box(ax, 3.62, 2.36, 3.16, 1.32, "", fc=tint(TEAL, 0.08), ec=TEAL, lw=0.9)
    txt(ax, 5.20, 3.36, "KV 传输", fs=FS, weight="bold")
    note(ax, 5.20, 3.06, "1.5 GB / 请求", fs=FS_S)
    note(ax, 5.20, 2.80, "400 Gbps IB → 29 ms", fs=FS_S)
    note(ax, 5.20, 2.54, "25 Gbps 以太网 → 480 ms", fs=FS_S, color=RED)

    arrow(ax, (3.44, 3.02), (3.58, 3.02), lw=1.1)
    arrow(ax, (6.82, 3.02), (6.96, 3.02), lw=1.1)

    # 下方说明
    ax.plot([0.55, 9.85], [1.22, 1.22], color=LGRAY, lw=0.7)
    txt(ax, 5.20, 0.94, "收益：两边的配置各自拉满，扩容可以分开做，干扰消失",
        fs=FS_S, color=INK)
    txt(ax, 5.20, 0.66, "代价：多一次传输，缓存不能自然共享，低负载时利用率更差",
        fs=FS_S, color=INK)
    txt(ax, 5.20, 0.34, "分界线：预填充占总计算三成以上，且长提示经常把解码卡住",
        fs=FS_S, color=GRAY)

    save(fig, "08/pd-split.png")


# ---------------------------------------------------------------- 09 容量倒推

def fig_09_capacity_flow():
    """第 9 章：从流量到卡数的五步倒推。"""
    fig, ax = canvas(1.95)

    steps = [
        ("流量", "100 万请求/天\n峰值 58 QPS", "2000 in / 300 out", NAVY, 0.10),
        ("三个约束", "算力 15 台\n带宽 5 台\n显存 3 台", "各自算，不混算", TEAL, 0.12),
        ("取最大", "15 台", "瓶颈在预填充", GOLD, 0.16),
        ("加冗余", "N+1 → 16\n跨区 → 32", "故障域与可用性", RED, 0.12),
        ("折成本", "256 卡\n$4 / 百万 token", "与定价对比", GRAY, 0.10),
    ]

    bw, bh = 1.72, 1.62
    xs = [0.42 + i * 1.96 for i in range(5)]
    y = 1.62

    for (name, mid, bot, c, f), x in zip(steps, xs):
        box(ax, x, y, bw, bh, "", fc=tint(c, f), ec=c, lw=0.9)
        txt(ax, x + bw / 2, y + bh - 0.24, name, fs=FS - 0.4, weight="bold")
        txt(ax, x + bw / 2, y + bh / 2 - 0.06, mid, fs=FS_S - 0.3)
        note(ax, x + bw / 2, y + 0.22, bot, fs=FS_S - 0.8)

    for i in range(4):
        arrow(ax, (xs[i] + bw + 0.02, y + bh / 2), (xs[i + 1] - 0.02, y + bh / 2),
              lw=0.9, shrink=0)

    note(ax, 5.20, 1.12, "峰值系数是最贵的参数：从 5 降到 2，机器数从 15 台降到 6 台",
         fs=FS_S)
    note(ax, 5.20, 0.82, "三个约束里最大的那个决定买多少卡，其余两个决定该优化哪里",
         fs=FS_S)
    note(ax, 5.20, 0.50, "第 15 台和第 16 台之间的差价，通常等于一整轮量化的工程投入",
         fs=FS_S, color=GRAY)

    save(fig, "09/capacity-flow.png")


FIGS = {
    "01": fig_01_two_phases,
    "02": fig_02_kv_budget,
    "03": fig_03_batching,
    "05": fig_05_granularity,
    "07": fig_07_spec_decode,
    "08": fig_08_pd_split,
    "09": fig_09_capacity_flow,
}


if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for key in want:
        FIGS[key]()
