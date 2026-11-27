# -*- coding: utf-8 -*-
"""《大模型技术全景》第一卷（入门篇）插图。

运行： <python> books/code/figs_v1.py
输出： books/v1-intro/images/{02,03,06,07,08}/*.png
      200 dpi，宽约 1500 px，供 GitHub 网页显示与 PDF 嵌入。

字号与尺寸约定
--------------
画布宽 7.5 in（190 mm，200 dpi 下 1500 px），排版时缩到正文 130 mm 宽，
缩放系数约 0.68。所以脚本里的 12 pt 印在纸上约 8.2 pt、11 pt 约 7.5 pt，
落在 8–9 pt 的插图字号区间。不要为了“看着大”把画布调大——那会让印刷后的字变小。

所有图只用方框、箭头、柱、点、矩阵小块表达结构，文字只做标签。
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import figstyle as st  # noqa: E402  (同一目录下的统一样式)

# Noto Sans SC 在本机只注册了 Thin（可变字体只报 weight=100），小字会发虚；
# 换成雅黑，保证缩到 130 mm 后笔画仍然实。
st.FONT = "Microsoft YaHei"

ROOT = HERE.parent                       # books/
IMGROOT = ROOT / "v1-intro" / "images"   # books/v1-intro/images

BASE = 12.0     # ≙ 印刷 8.2 pt
SMALL = 11.0    # ≙ 印刷 7.5 pt
TINY = 10.0     # ≙ 印刷 6.8 pt
DPI = 200


# ---------------------------------------------------------------- 通用小工具
def save_png(fig, rel: str) -> None:
    """保存 PNG，并用 PIL 复核实际像素尺寸。"""
    out = IMGROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=DPI, facecolor="white", bbox_inches="tight",
                pad_inches=0.02)
    plt.close(fig)
    from PIL import Image
    with Image.open(out) as im:          # 压成 RGB（去掉 alpha），印刷与 PDF 都更稳
        rgb = im.convert("RGB")
    rgb.save(out, dpi=(DPI, DPI), optimize=True)
    w, h = rgb.size
    print(f"  saved {rel}  {w}x{h} px  ({w / DPI * 25.4:.0f} mm 宽)")


def node(ax, x, y, w, h, title, sub="", fc="#FFFFFF", ec=st.NAVY_L,
         tc=st.INK, sc=st.GRAY, lw=0.9, z=3):
    """两行方框：主标签 + 小注释（图形元素，不是文字块）。"""
    st.box(ax, x, y, w, h, "", fc=fc, ec=ec, lw=lw, zorder=z)
    ax.text(x + w / 2, y + h * 0.64 if sub else y + h / 2, title, ha="center",
            va="center", fontsize=BASE, color=tc, zorder=z + 1)
    if sub:
        ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center",
                fontsize=TINY - 0.5, color=sc, zorder=z + 1)


def bracket(ax, x0, x1, y, text, color=st.NAVY, fs=SMALL, tick=0.11,
            linespacing=1.5, below=True):
    """开口朝上的方括号 + 说明；below=True 时说明写在括号下方。"""
    ax.plot([x0, x0, x1, x1], [y + tick, y, y, y + tick], color=color,
            lw=0.8, solid_capstyle="butt", zorder=2)
    ax.text((x0 + x1) / 2, y - 0.09 if below else y + tick + 0.05, text,
            ha="center", va="top" if below else "bottom", fontsize=fs,
            color=color, linespacing=linespacing, zorder=3)


# ---------------------------------------------------------------- 图 1 生成循环
def fig_generation_loop() -> None:
    """读图顺序：
    ① 顶排从左到右走一遍：文本 → 分词 → 嵌入 → N 层 → 打分（这一遍是 prefill）；
    ② 右侧采样抽出 1 个 token；
    ③ 沿底部箭头回到输入框（decode 循环，每次只加 1 个 token）；
    ④ 菱形判断是否遇到结束符，是则输出整段。
    """
    fig, ax = st.diagram(7.5, 4.30, xlim=(0, 10), ylim=(0.18, 5.42))

    top, h = 3.78, 0.95
    ymid = top + h / 2

    # ① 主链路
    node(ax, 0.10, top, 1.85, h, "输入文本", "整段提示词",
         fc=st.BG, ec=st.GRAY)
    node(ax, 2.22, top, 1.42, h, "分词", "切成 token")
    node(ax, 3.92, top, 1.42, h, "嵌入", "查表得到向量")
    node(ax, 5.62, top, 1.80, h, "N 层", "注意力 + 前馈",
         fc=st.NAVY, ec=st.NAVY, tc="white", sc=st.NAVY_XL)
    node(ax, 7.70, top, 2.20, h, "打分", "每个 token 一分", ec=st.GOLD)
    node(ax, 7.70, 2.50, 2.20, 0.92, "采样", "按概率抽一个",
         fc=st.GOLD_L, ec=st.GOLD)

    for x0, x1 in [(1.95, 2.22), (3.64, 3.92), (5.34, 5.62), (7.42, 7.70)]:
        st.arrow(ax, (x0, ymid), (x1, ymid))
    st.arrow(ax, (8.80, top), (8.80, 3.42))          # ② 打分 → 采样

    # KV 缓存旁注（指向 N 层）
    st.box(ax, 5.30, 2.55, 2.10, 0.86, "", fc="#FFFFFF", ec=st.NAVY_L,
           lw=0.7, zorder=2)
    ax.text(6.35, 3.25, "KV 缓存", ha="center", va="center", fontsize=TINY,
            color=st.NAVY, zorder=4)
    ax.text(6.35, 2.94, "历史位置只算一次\n之后每步只追加", ha="center",
            va="center", fontsize=TINY - 1.4, color=st.GRAY, zorder=4,
            linespacing=1.45)
    st.arrow(ax, (6.35, 3.41), (6.35, 3.76), color=st.NAVY_L, lw=0.7,
             ls=(0, (2, 2)))

    # ③ 回路：采样 → 判断 → 追加回输入
    ax.plot([8.80, 8.80], [2.50, 1.55], color=st.NAVY, lw=1.0, zorder=2)
    st.arrow(ax, (8.80, 1.55), (6.66, 1.55))

    dia = mpatches.Polygon([(6.02, 1.90), (6.66, 1.55), (6.02, 1.20), (5.38, 1.55)],
                           closed=True, facecolor="#FFFFFF", edgecolor=st.NAVY,
                           linewidth=0.9, zorder=4)
    ax.add_patch(dia)
    ax.text(6.02, 1.55, "结束符？", ha="center", va="center", fontsize=TINY,
            color=st.INK, zorder=5)
    ax.text(5.26, 1.62, "否", ha="right", va="bottom", fontsize=TINY,
            color=st.NAVY)

    ax.plot([5.38, 1.10], [1.55, 1.55], color=st.NAVY, lw=1.0, zorder=2)
    st.arrow(ax, (1.10, 1.55), (1.10, 3.76))

    ax.text(3.30, 1.66, "新 token 追加到序列末尾", ha="center", va="bottom",
            fontsize=SMALL, color=st.NAVY)
    ax.text(3.10, 1.42, "decode：每步只算 1 个新 token，共 N 步 → 出字间隔",
            ha="center", va="top", fontsize=TINY - 1.0, color=st.GRAY)

    # ④ 判断为“是”时的出口
    st.arrow(ax, (6.02, 1.20), (6.02, 1.02))
    ax.text(6.14, 1.11, "是", ha="left", va="center", fontsize=TINY, color=st.NAVY)
    st.box(ax, 4.95, 0.34, 2.14, 0.66, "输出整段文本", fc=st.BG, ec=st.GRAY,
           fs=SMALL)

    bracket(ax, 0.10, 9.90, 4.86,
            "prefill：整段输入一次算完，只做一次 → 首字延迟", below=False)

    save_png(fig, "02/generation-loop.png")


# ---------------------------------------------------------------- 图 2 训练四段
def fig_training_stages() -> None:
    """读图顺序：
    ① 从左到右四个阶段（数据 → 预训练 → 后训练 → 部署）；
    ② 每个框内的三行是这一步做的工序；
    ③ 框下浅底一句是“改变了什么”；
    ④ 再下一行六个小方块是参数改动比例（填色越多改得越多）；
    ⑤ 最下方括号：知识在哪一段定型。
    """
    fig, ax = st.diagram(7.5, 3.95, xlim=(0, 10), ylim=(0.80, 5.10))

    cols = [0.05, 2.60, 5.15, 7.70]
    w = 2.12
    stages = [
        dict(no="1", name="数据", color=st.GOLD,
             items=["网页 · 书 · 代码 · 论文", "抽正文 · 去重 · 过滤",
                    "质量筛 · 去污染 · 配比"],
             change="决定它\n知道什么、不知道什么", filled=0, tag="不动"),
        dict(no="2", name="预训练", color=st.NAVY,
             items=["猜下一个 token", "几万亿 token 过一遍",
                    "几千张卡跑几个月"],
             change="从不会说话\n到会续写、记住事实", filled=6, tag="全部"),
        dict(no="3", name="后训练", color=st.NAVY_L,
             items=["指令微调：学会做事", "偏好对齐：学会取舍",
                    "样本少，几轮迭代"],
             change="从会续写\n到肯照做、有分寸", filled=2, tag="少量"),
        dict(no="4", name="部署", color=st.TEAL,
             items=["量化：fp16 → 4 bit", "批处理：连续调度填满",
                    "KV 缓存：按长度涨"],
             change="更快更便宜\n不改它懂什么", filled=0, tag="不变"),
    ]

    for x, s in zip(cols, stages):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, 4.52), 0.40, 0.40, boxstyle="round,pad=0,rounding_size=0.06",
            facecolor=s["color"], edgecolor="none", zorder=3))
        ax.text(x + 0.20, 4.72, s["no"], ha="center", va="center",
                fontsize=TINY, color="white", zorder=4)
        ax.text(x + 0.52, 4.72, s["name"], ha="left", va="center",
                fontsize=BASE + 0.5, color=st.INK, weight="bold", zorder=4)

        st.box(ax, x, 3.26, w, 1.12, "", fc="#FFFFFF", ec=st.LGRAY, lw=0.8)
        for i, t in enumerate(s["items"]):
            yy = 4.12 - i * 0.285
            ax.plot([x + 0.13], [yy], marker="o", ms=2.0, color=s["color"], zorder=4)
            ax.text(x + 0.26, yy, t, ha="left", va="center",
                    fontsize=TINY - 0.8, color=st.INK, zorder=4)

        st.box(ax, x, 2.40, w, 0.66, "", fc=st.BG, ec=st.LGRAY, lw=0.6)
        ax.text(x + w / 2, 2.73, s["change"], ha="center", va="center",
                fontsize=TINY - 0.5, color=st.INK, linespacing=1.5, zorder=4)

        ax.text(x, 2.07, "参数", ha="left", va="center", fontsize=TINY - 1.4,
                color=st.GRAY, zorder=4)
        for k in range(6):
            on = k < s["filled"]
            ax.add_patch(mpatches.Rectangle(
                (x + 0.44 + k * 0.20, 1.98), 0.15, 0.15,
                facecolor=s["color"] if on else "#FFFFFF",
                edgecolor=st.LGRAY if not on else s["color"], lw=0.6, zorder=4))
        ax.text(x + w, 2.05, s["tag"], ha="right", va="center",
                fontsize=TINY - 0.6, color=s["color"], zorder=4)

    for x in cols[:-1]:
        st.arrow(ax, (x + w + 0.06, 3.82), (x + w + 0.40, 3.82), lw=1.1)

    bracket(ax, 0.05, 4.72, 1.78,
            "知识在这一段定型；之后只改行为，很难再塞新事实", fs=TINY - 1.0)

    ax.text(0.05, 0.98, "■", color=st.NAVY, fontsize=TINY - 1, va="center")
    ax.text(0.30, 0.98, "该阶段被更新的参数比例（6 格中填色数）",
            fontsize=TINY - 1.4, color=st.GRAY, va="center")
    ax.text(9.85, 0.98, "算力投入：2 > 3 > 1 > 4", ha="right", va="center",
            fontsize=TINY - 1.4, color=st.GRAY)

    save_png(fig, "05/training-stages.png")


# ---------------------------------------------------------------- 图 3 成本拆解
def fig_cost_breakdown() -> None:
    """读图顺序：
    ① 下栏四根等高柱：每个 token 都要把全量权重重读一遍，与上下文无关；
    ② 上栏四根柱：KV 缓存读取量，随上下文线性增长；
    ③ 柱顶小字：KV 占“单步读取总量”的份额，128K 时已到两成。
    """
    st.setup()
    fig = plt.figure(figsize=(7.86, 4.20))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.6, 1.0], hspace=0.30)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    fig.subplots_adjust(left=0.105, right=0.975, top=0.90, bottom=0.155)

    labels = ["1K", "8K", "32K", "128K"]
    kv = [0.33, 2.6, 10.2, 41.0]
    pct = [0.2, 1.8, 6.8, 22.6]
    xpos = np.arange(len(labels))

    # ② KV 缓存：线性增长
    ax1.bar(xpos, kv, 0.44, color=st.GOLD, edgecolor=st.GOLD, linewidth=0.6,
            zorder=3)
    ax1.plot(xpos, kv, color=st.GOLD, lw=0.8, ls=(0, (3, 2)), zorder=4,
             marker="o", ms=2.6, mfc="white", mec=st.GOLD, mew=0.8)
    for x, v, p in zip(xpos, kv, pct):
        ax1.text(x, v + 2.0, f"{v:g} GB\n占 {p:g}%", ha="center", va="bottom",
                 fontsize=TINY - 0.8, color=st.INK, linespacing=1.5, zorder=5)
    ax1.set_ylim(0, 52)
    ax1.set_yticks([0, 20, 40])
    ax1.set_ylabel("KV 缓存 / GB", fontsize=SMALL)
    ax1.set_title("每生成 1 个 token，显存里要搬多少数据", fontsize=BASE,
                  color=st.INK, pad=8, loc="left")
    ax1.tick_params(labelbottom=False)
    ax1.grid(axis="x", visible=False)
    ax1.text(0.42, 38.0, "KV = 320 KB × 上下文长度\n上下文 ×4，KV 也 ×4；外推 1M ≈ 320 GB",
             fontsize=TINY - 1.2, color=st.GRAY, ha="left", va="center",
             linespacing=1.6)

    # ① 权重：恒定
    ax2.bar(xpos, [140] * 4, 0.44, color=st.NAVY_XL, edgecolor=st.NAVY_L,
            linewidth=0.6, zorder=3)
    for x in xpos:
        ax2.text(x, 145, "140 GB", ha="center", va="bottom",
                 fontsize=TINY - 0.8, color=st.NAVY, zorder=5)
    ax2.set_ylim(0, 200)
    ax2.set_yticks([0, 140])
    ax2.set_ylabel("权重 / GB", fontsize=SMALL)
    ax2.set_xticks(xpos)
    ax2.set_xticklabels(labels)
    ax2.set_xlabel("上下文长度 / token", fontsize=SMALL, color=st.INK)
    ax2.grid(axis="x", visible=False)
    ax2.set_title("四根等高：每步都要重读全量权重，与上下文无关", fontsize=SMALL - 1.0,
                  color=st.NAVY, pad=6, loc="left")

    save_png(fig, "16/cost-breakdown.png")


# ---------------------------------------------------------------- 二维定位图
def map_frame(ax, xname, yname, xends, yends, corners, fill="quad"):
    """带箭头的两根轴 + 很淡的分区背景 + 四角提示。"""
    if fill == "quad":
        for (x0, y0, c) in [(0, 5, "#FFFFFF"), (5, 5, "#FFFFFF"),
                            (0, 0, st.BG), (5, 0, st.BG)]:
            ax.add_patch(mpatches.Rectangle((x0, y0), 5, 5, facecolor=c,
                                            edgecolor="none", zorder=0))
    else:  # 从白到浅蓝的斜向渐变，暗示“越靠右上越好”
        cmap = LinearSegmentedColormap.from_list("g", ["#FFFFFF", st.NAVY_XL])
        xx, yy = np.meshgrid(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
        g = 0.5 * (xx + yy)          # 左下 0（白）→ 右上 1（浅蓝）
        ax.imshow(g, extent=(0, 10, 0, 10), origin="lower", cmap=cmap,
                  vmin=0, vmax=1, alpha=0.72, aspect="auto", zorder=0,
                  interpolation="bilinear")

    ax.plot([5, 5], [0, 10], color=st.LGRAY, lw=0.6, ls=(0, (3, 3)), zorder=1)
    ax.plot([0, 10], [5, 5], color=st.LGRAY, lw=0.6, ls=(0, (3, 3)), zorder=1)

    st.arrow(ax, (-0.2, -0.2), (10.45, -0.2), color=st.GRAY, lw=0.9, shrink=0)
    st.arrow(ax, (-0.2, -0.2), (-0.2, 10.45), color=st.GRAY, lw=0.9, shrink=0)

    ax.text(5.0, -2.02, xname, ha="center", va="top", fontsize=SMALL,
            color=st.INK)
    ax.text(0.0, -0.45, xends[0], ha="left", va="top", fontsize=SMALL - 1.5,
            color=st.GRAY)
    ax.text(10.0, -0.45, xends[1], ha="right", va="top", fontsize=SMALL - 1.5,
            color=st.GRAY)

    ax.text(-1.28, 5.0, yname, ha="center", va="center", fontsize=SMALL,
            color=st.INK, rotation=90)
    ax.text(-0.42, 0.00, yends[0], ha="right", va="bottom", fontsize=SMALL - 1.5,
            color=st.GRAY)
    ax.text(-0.42, 10.00, yends[1], ha="right", va="top", fontsize=SMALL - 1.5,
            color=st.GRAY)

    for (cx, cy), txt, ha, va in corners:
        ax.text(cx, cy, txt, ha=ha, va=va, fontsize=TINY - 1.6,
                color="#AEB3BC", zorder=1)


def label_at(ax, px, py, cx, cy, name, tag, color):
    """画一个数据点，并在 (cx, cy) 放一个自适应宽度的标签盒 + 引导线。"""
    t1 = ax.text(cx, cy + 0.22, name, ha="center", va="center", fontsize=SMALL,
                 color=color, weight="bold", zorder=6)
    t2 = ax.text(cx, cy - 0.26, tag, ha="center", va="center",
                 fontsize=TINY - 2.0, color=st.GRAY, zorder=6)
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    b1 = inv.transform(t1.get_window_extent(r).get_points())
    b2 = inv.transform(t2.get_window_extent(r).get_points())
    x0 = min(b1[0][0], b2[0][0]) - 0.14
    x1 = max(b1[1][0], b2[1][0]) + 0.14
    y0 = min(b1[0][1], b2[0][1]) - 0.10
    y1 = max(b1[1][1], b2[1][1]) + 0.10
    ax.add_patch(mpatches.FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0,
        boxstyle="round,pad=0,rounding_size=0.10", facecolor="white",
        edgecolor=color, linewidth=0.7, zorder=4, alpha=0.95))

    tx = min(max(px, x0), x1)
    ty = min(max(py, y0), y1)
    ax.plot([px], [py], marker="o", ms=5.0, color=color, mec="white", mew=0.9,
            zorder=7)
    ax.plot([px, tx], [py, ty], color=color, lw=0.6, ls=(0, (2, 2)), zorder=3)


# ---------------------------------------------------------------- 图 4 三种用法
def fig_usage_modes() -> None:
    """读图顺序：
    ① 横轴是改动程度（左：一个参数都不动；右：把参数改掉）；
    ② 纵轴是外部依赖（下：不需要外部系统；上：要接索引、工具或多轮调度）；
    ③ 四个点各落在一格，点下小字是它擅长的事。
    """
    fig, ax = st.diagram(7.5, 4.85, xlim=(-1.62, 10.6), ylim=(-2.3, 10.8))
    map_frame(ax, "改动程度", "外部依赖", ("不改参数", "改参数"), ("无", "重"),
              [((0.15, 10.55), "轻改 · 重依赖", "left", "top"),
               ((9.95, 10.55), "重改 · 重依赖", "right", "top"),
               ((0.15, 0.15), "轻改 · 轻依赖", "left", "bottom"),
               ((9.95, 0.15), "重改 · 轻依赖", "right", "bottom")])

    label_at(ax, 1.55, 2.05, 1.60, 3.70, "提示", "写清要求与格式", st.NAVY_L)
    label_at(ax, 8.30, 1.85, 8.30, 3.45, "微调", "把行为烧进权重", st.GOLD)
    label_at(ax, 2.40, 6.90, 2.60, 8.25, "RAG", "先查资料再回答", st.TEAL)
    label_at(ax, 4.35, 9.30, 6.85, 9.15, "智能体", "调工具、多轮执行", st.RED)

    save_png(fig, "15/usage-modes.png")


# ---------------------------------------------------------------- 图 5 评测版图
def fig_eval_landscape() -> None:
    """读图顺序：
    ① 横轴是任务真实性（左：离真实工作远；右：就是真实工作本身）；
    ② 纵轴是可复现性（下：别人无法重跑；上：程序判分、可复现）；
    ③ 四个点是一个来回的取舍，右上角虚线框是“理想但还没有通用方案”的空缺。
    """
    fig, ax = st.diagram(7.5, 4.85, xlim=(-1.62, 10.6), ylim=(-2.3, 10.8))
    map_frame(ax, "任务真实性", "可复现性",
              ("离真实工作远", "就是真实工作"), ("低", "高"),
              [((0.15, 10.55), "可复现 · 不真实", "left", "top"),
               ((9.95, 0.15), "真实 · 不可复现", "right", "bottom")],
              fill="grad")

    # 理想区：右上角空白
    ax.add_patch(mpatches.Rectangle((8.55, 9.00), 1.45, 1.55, facecolor="white",
                                    edgecolor=st.NAVY_L, lw=0.7,
                                    ls=(0, (4, 3)), zorder=2, alpha=0.9))
    ax.text(9.28, 9.78, "理想区", ha="center", va="center", fontsize=TINY - 2,
            color=st.NAVY, zorder=3)

    label_at(ax, 1.30, 8.60, 2.95, 7.15, "MMLU", "57 学科选择题", st.NAVY_L)
    label_at(ax, 7.35, 8.45, 5.55, 9.70, "SWE-bench", "真 issue，跑测试判分", st.TEAL)
    label_at(ax, 4.20, 3.30, 2.65, 3.35, "竞技场", "人投票，偏爱长与好看", st.GOLD)
    label_at(ax, 8.40, 1.55, 8.40, 3.15, "私有评测", "自家数据，无法复现", st.RED)

    save_png(fig, "19/eval-landscape.png")


# ================================================================ 新增图
# 下面四张按 5.2 in 宽（≈132 mm）画，排版时基本原大，字号即印刷字号。
W5 = 5.2
FS5 = 8.6
FS5S = 7.3


def canvas5(h_in: float):
    """固定 5.2 in 宽的满幅画布，1 数据单位 = 0.5 in。"""
    st.setup()
    fig = plt.figure(figsize=(W5, h_in))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 2 * W5)
    ax.set_ylim(0, 2 * h_in)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.grid(False)
    return fig, ax


def txt5(ax, x, y, s, fs=FS5, color=st.INK, ha="center", va="center",
         weight="normal", z=8):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   weight=weight, zorder=z, linespacing=1.42)


def note5(ax, x, y, s, fs=FS5S, color=st.GRAY, ha="center", va="center", **kw):
    return ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
                   zorder=8, linespacing=1.45, **kw)


def save5(fig, rel: str) -> None:
    out = IMGROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=288, facecolor="white")
    plt.close(fig)
    from PIL import Image
    with Image.open(out) as im:
        rgb = im.convert("RGB")
    rgb.save(out, dpi=(288, 288), optimize=True)
    print(f"  saved {rel}  {rgb.width}x{rgb.height} px")


# ---------------------------------------------------------------- 图 6 想多久
def fig_thinking_budget() -> None:
    """读图顺序：
    ① 上栏蓝线：正确率随思考长度的变化，前段陡、后段平；
    ② 下栏金柱：成本随思考长度线性上涨；
    ③ 中间的竖虚线是“收益已经不多、钱还在涨”的位置。
    """
    st.setup()
    fig = plt.figure(figsize=(W5, 3.15))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.5, 1.0], hspace=0.16)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    fig.subplots_adjust(left=0.085, right=0.975, top=0.965, bottom=0.135)

    xpos = np.arange(4)
    labels = ["0.5K", "2K", "8K", "32K"]
    acc = [43, 61, 70, 72]
    cost = [1, 4, 16, 64]

    ax1.plot(xpos, acc, color=st.NAVY, lw=1.4, marker="o", ms=4.2,
             mfc="white", mew=1.1, zorder=4)
    ax1.set_ylim(30, 84)
    ax1.set_yticks([])
    ax1.set_ylabel("同批题上的正确率", fontsize=FS5S + 0.6, color=st.INK,
                   labelpad=4)
    ax1.tick_params(axis="both", which="both", labelbottom=False,
                    length=0)
    ax1.grid(axis="y", color=st.LGRAY, lw=0.45, alpha=0.7)
    ax1.grid(axis="x", visible=False)
    ax1.spines["left"].set_visible(False)

    ax1.annotate("想得越多，错得越少", xy=(0.34, 50.0), xytext=(1.30, 36.0),
                 fontsize=FS5S, color=st.NAVY,
                 arrowprops=dict(arrowstyle="-|>", lw=0.7, color=st.NAVY_L))
    ax1.annotate("多数题的收益在前一段收完", xy=(1.92, 69.2),
                 xytext=(0.55, 79.5), fontsize=FS5S, color=st.GRAY,
                 arrowprops=dict(arrowstyle="-|>", lw=0.6, color=st.LGRAY))
    ax1.annotate("再翻四倍，只多一两点", xy=(2.94, 71.7), xytext=(2.05, 58.0),
                 fontsize=FS5S, color=st.GRAY,
                 arrowprops=dict(arrowstyle="-|>", lw=0.6, color=st.LGRAY))

    for a in (ax1, ax2):
        a.axvline(1.72, color=st.GOLD, lw=0.7, ls=(0, (3, 2)), zorder=1)

    ax2.bar(xpos, cost, 0.38, color=st.GOLD_L, edgecolor=st.GOLD, lw=0.7,
            zorder=3)
    for x, v in zip(xpos, cost):
        ax2.text(x, v + 2.4, f"{v}×", ha="center", va="bottom",
                 fontsize=FS5S, color=st.INK, zorder=5)
    ax2.set_ylim(0, 82)
    ax2.set_yticks([])
    ax2.set_ylabel("单次成本", fontsize=FS5S + 0.6, color=st.INK, labelpad=10)
    ax2.set_xticks(xpos)
    ax2.set_xticklabels(labels, fontsize=FS5S)
    ax2.set_xlabel("思考长度 / token", fontsize=FS5S + 0.6, color=st.INK)
    ax2.grid(axis="x", visible=False)
    ax2.grid(axis="y", visible=False)
    ax2.tick_params(axis="both", which="both", length=0)
    ax2.spines["left"].set_visible(False)

    save5(fig, "07/thinking-budget.png")


# ---------------------------------------------------------------- 图 7 多模态 token 成本
def fig_multimodal_tokens() -> None:
    """读图顺序：
    ① 四根横柱，同一把尺子（token 数）；
    ② 文字那根最短，视频那根最长；
    ③ 柱右的数字是量级估计，不是精确值。
    """
    st.setup()
    fig, ax = plt.subplots(figsize=(W5, 2.78))
    fig.subplots_adjust(left=0.245, right=0.955, top=0.955, bottom=0.175)

    names = ["一段文字\n约 1000 字", "一张图\n1024×1024", "一分钟语音\n16 kHz",
             "一分钟视频\n每秒 1 帧"]
    vals = [1.5, 1.2, 3.0, 60.0]
    colors = [st.NAVY_XL, st.NAVY_L, st.TEAL, st.GOLD]
    ypos = np.arange(len(names))[::-1]

    ax.barh(ypos, vals, 0.52, color=colors, edgecolor=[st.NAVY_L, st.NAVY_L,
                                                       st.TEAL, st.GOLD],
            lw=0.7, zorder=3)
    for y, v in zip(ypos, vals):
        ax.text(v + 1.5, y, f"≈{v:g}K", va="center", ha="left",
                fontsize=FS5S + 0.4, color=st.INK, zorder=5)

    ax.set_yticks(ypos)
    ax.set_yticklabels(names, fontsize=FS5S)
    ax.set_xlim(0, 74)
    ax.set_xticks([0, 20, 40, 60])
    ax.set_xticklabels(["0", "20K", "40K", "60K"], fontsize=FS5S)
    ax.set_xlabel("一次送进模型的 token 数", fontsize=FS5S + 0.6, color=st.INK)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="both", length=0)
    ax.spines["left"].set_visible(False)

    ax.text(63.5, 3.34, "按每秒 1 帧、每帧约 1K 估；\n每秒 30 帧就是两百万量级",
            ha="right", va="bottom", fontsize=FS5S - 0.4, color=st.GRAY,
            linespacing=1.5, zorder=5)

    save5(fig, "10/multimodal-tokens.png")


# ---------------------------------------------------------------- 图 8 智能体循环
def fig_agent_loop() -> None:
    """读图顺序：
    ① 中间三个方框转一圈：看状态 → 调工具 → 观察 → 再来一轮；
    ② 右上出口是“判断能答了”；
    ③ 左侧三条是护栏，缺一条就会出事故。
    """
    fig, ax = canvas5(3.05)

    bw, bh = 3.05, 1.02
    cx0, cy0 = 5.05, 4.10
    boxes = [
        (cx0, cy0, "模型看一眼当前状态", "目标 + 历史 + 工具结果", st.NAVY),
        (cx0 + 3.55, cy0 - 1.55, "选一个工具", "参数由它生成", st.GOLD),
        (cx0, cy0 - 3.10, "观察返回结果", "写回上下文，算新状态", st.TEAL),
    ]
    for (cx, cy, head, sub, color) in boxes:
        st.box(ax, cx - bw / 2, cy - bh / 2, bw, bh, "", fc="#FFFFFF",
               ec=color, lw=0.9, zorder=4)
        txt5(ax, cx, cy + 0.17, head, fs=FS5, color=st.INK, weight="bold")
        note5(ax, cx, cy - 0.24, sub, fs=FS5S - 0.5)

    st.arrow(ax, (cx0 + bw / 2 + 0.05, cy0 - 0.14),
             (cx0 + 3.55 - bw / 2 - 0.05, cy0 - 1.02), rad=-0.14)
    st.arrow(ax, (cx0 + 3.55 - bw / 2 - 0.05, cy0 - 2.06),
             (cx0 + bw / 2 + 0.05, cy0 - 2.88), rad=-0.14)
    st.arrow(ax, (cx0 - bw / 2 - 0.05, cy0 - 2.88),
             (cx0 - bw / 2 - 0.05, cy0 - 0.16), rad=0.0)
    note5(ax, cx0 - 1.80, cy0 - 1.55, "再来\n一轮", fs=FS5S - 0.8)

    st.box(ax, 8.45, 4.80, 1.95, 0.90, "", fc=st.BG, ec=st.NAVY_L, lw=0.8,
           zorder=4)
    txt5(ax, 9.42, 5.25, "给出答复", fs=FS5 - 0.4)
    note5(ax, 9.42, 4.96, "或转人工", fs=FS5S - 0.5)
    st.arrow(ax, (cx0 + 0.55, cy0 + bh / 2 + 0.04), (8.40, 5.24), rad=-0.12)
    note5(ax, 7.78, 5.62, "判断能答了", fs=FS5S - 0.6)

    guard = ["步数上限：超过就停", "工具白名单：只开必要的", "不可逆动作要人确认"]
    for i, g in enumerate(guard):
        y = 2.75 - i * 0.50
        ax.plot([0.32], [y], marker="s", ms=2.8, color=st.RED, zorder=5)
        note5(ax, 0.52, y, g, fs=FS5S - 0.7, ha="left", color=st.GRAY)

    save5(fig, "12/agent-loop.png")


# ---------------------------------------------------------------- 图 9 两阶段
def fig_two_stage() -> None:
    """读图顺序：
    ① 横轴是时间，红虚线是“第一个字出现”的时刻；
    ② 左边宽块是预填充：整段输入一次算完，算力打满；
    ③ 右边一串小方块是解码：每步只出一个字，卡在读权重；
    ④ 下方两条标注写的是各自的瓶颈。
    """
    fig, ax = canvas5(2.30)

    x0, y0, h = 0.55, 1.86, 1.10
    st.box(ax, x0, y0, 2.62, h, "", fc=st.NAVY_XL, ec=st.NAVY_L, lw=0.9)
    txt5(ax, x0 + 1.31, y0 + 0.70, "预填充", fs=FS5 + 0.4, weight="bold")
    note5(ax, x0 + 1.31, y0 + 0.24, "整段输入并行算一遍", fs=FS5S - 0.5)

    xd = x0 + 2.86
    for i in range(7):
        st.box(ax, xd + i * 0.40, y0 + 0.30, 0.30, 0.50, "", fc=st.GOLD_L,
               ec=st.GOLD, lw=0.7, rounded=0.04)
    txt5(ax, xd + 1.42, y0 + 1.02, "解码：一步一个字", fs=FS5, weight="bold")
    note5(ax, xd + 1.42, y0 - 0.02, "每步都要把全部权重读一遍", fs=FS5S - 0.5)

    st.arrow(ax, (x0 - 0.14, y0 - 0.40), (10.05, y0 - 0.40), color=st.GRAY, lw=0.8)
    note5(ax, 9.95, y0 - 0.60, "时间", fs=FS5S - 0.6, ha="right")

    ax.plot([x0 + 2.72, x0 + 2.72], [y0 - 0.34, y0 + h + 0.20],
            color=st.RED, lw=0.9, ls=(0, (3, 2)), zorder=3)
    note5(ax, x0 + 2.82, y0 + h + 0.34, "第一个字", fs=FS5S - 0.4,
          ha="left", color=st.RED)

    bracket(ax, x0, x0 + 2.62, y0 + h + 0.10,
            "首字延迟：随输入长度线性增长", fs=FS5S - 0.5, below=False)
    bracket(ax, x0 + 2.95, 9.90, y0 + h + 0.10,
            "出字间隔：基本是常数", fs=FS5S - 0.5, below=False, color=st.GOLD)

    ax.text(0.55, 0.62, "■", color=st.NAVY, fontsize=FS5S - 1.0, va="center")
    note5(ax, 0.94, 0.62, "计算单元吃满，输入越长越久", fs=FS5S - 0.6, ha="left")
    ax.text(5.15, 0.62, "■", color=st.GOLD, fontsize=FS5S - 1.0, va="center")
    note5(ax, 5.54, 0.62, "计算单元大部分时间在等数据", fs=FS5S - 0.6, ha="left")

    save5(fig, "18/two-stage.png")




# ---------------------------------------------------------------- 图 10 采样温度
def fig_sampling_temperature() -> None:
    """读图顺序：
    ① 五行是同一个上文的五个候选，分数从高到低；
    ② 左列低温：概率几乎全压在第一名；右列高温：长尾也留了门；
    ③ 最下一排是各抽五次的结果。
    """
    fig, ax = canvas5(2.62)

    names = ["好", "热", "不错", "冷", "转账"]
    lo = [0.86, 0.10, 0.03, 0.008, 0.002]
    hi = [0.42, 0.25, 0.19, 0.10, 0.04]
    ys = [4.42, 3.75, 3.08, 2.41, 1.74]
    scale = 2.30

    txt5(ax, 2.55, 5.02, "温度 0.2", fs=FS5 + 0.2, weight="bold")
    note5(ax, 2.55, 4.72, "保守：几乎总选第一", fs=FS5S - 0.4)
    txt5(ax, 7.25, 5.02, "温度 1.0", fs=FS5 + 0.2, weight="bold")
    note5(ax, 7.25, 4.72, "放开：长尾也有机会", fs=FS5S - 0.4)

    lotext = ["86%", "10%", "3.0%", "0.8%", "0.2%"]
    for n, pl, ph, y, lt in zip(names, lo, hi, ys, lotext):
        note5(ax, 2.18, y, n, fs=FS5, ha="right", color=st.INK)
        wl = max(pl * scale, 0.03)
        ax.add_patch(mpatches.Rectangle((2.30, y - 0.18), wl, 0.36,
                                        facecolor=st.NAVY_XL,
                                        edgecolor=st.NAVY_L, lw=0.6, zorder=3))
        note5(ax, 2.30 + wl + 0.10, y, lt, fs=FS5S - 0.5,
              ha="left", color=st.INK)

        wh = max(ph * scale, 0.03)
        ax.add_patch(mpatches.Rectangle((7.00, y - 0.18), wh, 0.36,
                                        facecolor=st.GOLD_L,
                                        edgecolor=st.GOLD, lw=0.6, zorder=3))
        note5(ax, 7.00 + wh + 0.10, y, f"{ph * 100:.0f}%",
              fs=FS5S - 0.5, ha="left", color=st.INK)

    note5(ax, 2.30, 1.26, "下面两个几乎抽不到，\n但“几乎”不等于“不会”",
          fs=FS5S - 0.6, ha="left")

    txt5(ax, 0.30, 0.72, "抽五次", fs=FS5S, ha="left")
    picks_lo = ["好", "好", "好", "好", "好"]
    picks_hi = ["好", "热", "好", "冷", "热"]
    for i, (a, b) in enumerate(zip(picks_lo, picks_hi)):
        st.box(ax, 1.62 + i * 0.62, 0.54, 0.52, 0.36, "", fc="#FFFFFF",
               ec=st.NAVY_L, lw=0.7)
        txt5(ax, 1.88 + i * 0.62, 0.72, a, fs=FS5S - 1.0, color=st.NAVY)
        st.box(ax, 6.30 + i * 0.62, 0.54, 0.52, 0.36, "", fc="#FFFFFF",
               ec=st.GOLD, lw=0.7)
        txt5(ax, 6.56 + i * 0.62, 0.72, b, fs=FS5S - 1.0, color=st.GOLD)
    note5(ax, 3.55, 0.26, "同一个上文，五次一样", fs=FS5S - 1.0)
    note5(ax, 8.05, 0.26, "同一个上文，三次不同", fs=FS5S - 1.0)

    save5(fig, "01/sampling-temperature.png")


# ---------------------------------------------------------------- 图 11 数据漏斗
def fig_data_funnel() -> None:
    """读图顺序：
    ① 五级台阶从上到下，宽度按字节数的对数画；
    ② 右侧是这一步之后的量；③ 底下一句结论。
    """
    fig, ax = canvas5(2.95)

    stages = [
        ("抓取网页", "100 亿个页面，含 HTML", "10 PB", 8.65, st.NAVY_XL),
        ("抽出正文", "只留文字，扔掉标签脚本", "150 TB", 5.05, "#B7C6DE"),
        ("去重", "转载、镜像、模板页归并", "90 TB", 4.55, st.NAVY_L),
        ("质量筛选", "只留打分靠前的三成", "27 TB", 3.35, st.NAVY),
        ("转成 token", "体积几乎不变，单位换了", "13.5 万亿", 3.35, st.GOLD),
    ]
    ytop = 5.24
    for i, (name, sub, val, wdt, color) in enumerate(stages):
        y = ytop - i * 0.86
        ax.add_patch(mpatches.Rectangle((0.45, y - 0.52), wdt, 0.62,
                                        facecolor=color, edgecolor="none",
                                        zorder=3))
        dark = color in (st.NAVY, st.GOLD, st.NAVY_L)
        txt5(ax, 0.68, y - 0.04, name, fs=FS5, ha="left",
             color="white" if dark else st.INK, weight="bold")
        note5(ax, 0.68, y - 0.32, sub, fs=FS5S - 1.0, ha="left",
              color="#E9ECF1" if dark else st.GRAY)
        note5(ax, 0.45 + wdt + 0.18, y - 0.18, val, fs=FS5S, ha="left",
              color=st.INK, weight="bold")

    for i in range(4):
        y0 = ytop - i * 0.86 - 0.52
        st.arrow(ax, (0.62, y0 - 0.02), (0.62, y0 - 0.20), color=st.GRAY, lw=0.7)

    note5(ax, 0.45, 0.66, "宽度按对数画：从 10 PB 到 150 TB 已经是一百倍",
          fs=FS5S - 0.8, ha="left")
    note5(ax, 10.05, 0.66, "最终约为初始体量的千分之一", fs=FS5S - 0.8,
          ha="right", color=st.GOLD)

    save5(fig, "04/data-funnel.png")


# ---------------------------------------------------------------- 图 12 显存
def fig_params_memory() -> None:
    """读图顺序：
    ① 上表：参数量乘精度，就是权重的 GB 数；红框是装不进一张 80 GB 卡的格子；
    ② 下段：每个并发请求还要按上下文长度另占一份缓存。
    """
    fig, ax = canvas5(3.32)

    cols = [("16 位", 2.55), ("8 位", 4.75), ("4 位", 6.95)]
    for name, x in cols:
        txt5(ax, x + 1.00, 5.92, name, fs=FS5S, color=st.GRAY)

    rows = [("7B", 14, 7, 3.5), ("70B", 140, 70, 35), ("405B", 810, 405, 202)]
    ys = [5.02, 4.22, 3.42]
    for (name, a, b, c), y in zip(rows, ys):
        note5(ax, 2.35, y, name, fs=FS5, ha="right", color=st.INK)
        for val, (_, x) in zip((a, b, c), cols):
            big = val > 80
            st.box(ax, x, y - 0.28, 2.00, 0.56, "", fc="#FFFFFF",
                   ec=st.RED if big else st.LGRAY, lw=0.8)
            txt5(ax, x + 1.00, y, f"{val:g} GB", fs=FS5 - 0.3,
                 color=st.RED if big else st.INK)

    note5(ax, 5.00, 2.94, "红框：一张 80 GB 卡装不下，要切开或换精度",
          fs=FS5S - 0.8, ha="center", color=st.RED)

    ax.plot([0.45, 10.05], [2.72, 2.72], color=st.LGRAY, lw=0.7, zorder=2)
    txt5(ax, 0.45, 2.46, "每个并发请求，还要按长度占一份缓存",
         fs=FS5S + 0.1, ha="left", weight="bold")
    note5(ax, 10.05, 2.46, "320 KB / token", fs=FS5S - 0.6, ha="right",
          color=st.GOLD)

    kvs = [("8K", "2.6 GB", 1.10), ("32K", "10.2 GB", 2.55),
           ("128K", "41 GB", 4.95)]
    for i, (lab, val, wdt) in enumerate(kvs):
        y = 1.86 - i * 0.50
        note5(ax, 1.35, y, lab, fs=FS5S, ha="right", color=st.INK)
        ax.add_patch(mpatches.Rectangle((1.45, y - 0.14), wdt, 0.28,
                                        facecolor=st.GOLD_L, edgecolor=st.GOLD,
                                        lw=0.6, zorder=3))
        note5(ax, 1.55 + wdt, y, val, fs=FS5S - 0.4, ha="left")

    note5(ax, 7.30, 1.40, "70B 的 4 位权重占 35 GB，\n"
                          "80 GB 卡剩 45 GB：\n"
                          "一万上下文开 14 个，\n"
                          "三万二千只能开 4 个",
          fs=FS5S - 0.9, ha="left")

    save5(fig, "08/params-memory.png")


# ---------------------------------------------------------------- 图 13 上下文成本
def fig_context_cost() -> None:
    """读图顺序：
    ① 横轴是对数尺的上下文长度；② 蓝线是首字延迟，随长度线性涨；
    ③ 灰线是放在中间那段信息的命中率（示意），越靠右越低；
    ④ 竖虚线是“检索取三段”的位置：延迟只剩一个零头。
    """
    st.setup()
    fig, ax = plt.subplots(figsize=(W5, 2.90))
    fig.subplots_adjust(left=0.105, right=0.885, top=0.955, bottom=0.175)

    x = np.array([1, 3, 8, 32, 128])
    delay = x * 0.13
    recall = [0.96, 0.92, 0.86, 0.74, 0.61]

    ax.plot(x, delay, color=st.NAVY, lw=1.5, marker="o", ms=4.0,
            mfc="white", mew=1.0, zorder=4)
    ax.set_xscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v}K" for v in x], fontsize=FS5S)
    ax.set_xlabel("上下文长度 / token", fontsize=FS5S + 0.5, color=st.INK)
    ax.set_ylim(0, 19)
    ax.set_yticks([0, 5, 10, 15])
    ax.set_ylabel("首字延迟 / 秒", fontsize=FS5S + 0.5, color=st.NAVY)
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="both", length=0, labelsize=FS5S)

    for xi, yi in zip(x, delay):
        ax.text(xi, yi + 0.9, f"{yi:g}s", ha="center", va="bottom",
                fontsize=FS5S - 0.8, color=st.NAVY, zorder=5)

    ax2 = ax.twinx()
    ax2.plot(x, recall, color=st.GRAY, lw=1.2, ls=(0, (4, 2)), marker="s",
             ms=3.2, mfc="white", mew=0.8, zorder=3)
    ax2.set_ylim(0.4, 1.02)
    ax2.set_yticks([0.5, 0.7, 0.9])
    ax2.set_yticklabels(["50%", "70%", "90%"], fontsize=FS5S, color=st.GRAY)
    ax2.set_ylabel("中间位置信息的命中率", fontsize=FS5S, color=st.GRAY,
                   labelpad=4)
    ax2.spines["right"].set_visible(True)
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(length=0)
    ax2.grid(False)

    ax.axvline(3, color=st.GOLD, lw=0.9, ls=(0, (3, 2)), zorder=1)
    ax.annotate("检索只取三段\n≈3K token，0.4 秒", xy=(3, 0.55),
                xytext=(4.3, 6.6), fontsize=FS5S - 0.6, color=st.GOLD,
                linespacing=1.6,
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=st.GOLD))
    ax.annotate("整份塞进去\n22 万 token，29 秒", xy=(128, 16.6),
                xytext=(13.0, 12.4), fontsize=FS5S - 0.6, color=st.NAVY,
                linespacing=1.6, ha="left",
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=st.NAVY_L))
    ax.annotate("越靠中间越容易被漏掉", xy=(128, 0.66), xytext=(12.0, 2.9),
                fontsize=FS5S - 0.6, color=st.GRAY, ha="left",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=st.GRAY))


    save5(fig, "09/context-cost.png")


# ---------------------------------------------------------------- 图 14 生态
def fig_ecosystem() -> None:
    """读图顺序：
    ① 三列是三种拿法；② 四行是“给了你什么”，实心表示给；
    ③ 最后一排是你能做的事。多数“开源”只填了第一格。
    """
    fig, ax = canvas5(2.72)

    cols = [("闭源 API", 1.95), ("开放权重", 4.85), ("完全开源", 7.75)]
    for name, x in cols:
        txt5(ax, x + 1.30, 5.02, name, fs=FS5 + 0.2, weight="bold")

    rows = [("权重", 4.26), ("训练代码", 3.66), ("数据配比", 3.06),
            ("数据集", 2.46)]
    fills = [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]]
    for name, y in rows:
        note5(ax, 1.80, y, name, fs=FS5S, ha="right", color=st.INK)

    for ci, (_, x) in enumerate(cols):
        for ri, (_, y) in enumerate(rows):
            on = fills[ci][ri]
            ax.add_patch(mpatches.Rectangle((x + 1.13, y - 0.17), 0.34, 0.34,
                                            facecolor=st.NAVY if on else "#FFFFFF",
                                            edgecolor=st.NAVY if on else st.LGRAY,
                                            lw=0.7, zorder=3))
        note5(ax, x + 1.30, 1.76, "你能做", fs=FS5S - 1.4, color=st.GRAY)

    notes = ["只能调接口", "微调·量化·合并", "复现训练"]
    for (_, x), n in zip(cols, notes):
        st.box(ax, x + 0.10, 1.06, 2.40, 0.50, "", fc="#FFFFFF",
               ec=st.LGRAY, lw=0.7)
        txt5(ax, x + 1.30, 1.31, n, fs=FS5S - 0.6)

    note5(ax, 5.20, 0.60, "叫“开源”的模型，九成以上只填了第一行的第一格",
          fs=FS5S - 0.6, color=st.GOLD)

    save5(fig, "20/ecosystem.png")


# ---------------------------------------------------------------- 图 15 越狱与防御
def fig_jailbreak() -> None:
    """读图顺序：
    ① 每行是一次攻击、它主要打哪一层、那一层的防线；
    ② 从上往下，防线从“模型自己”移到“系统外面”，越往下越硬。
    """
    fig, ax = canvas5(3.10)

    txt5(ax, 1.72, 5.60, "攻", fs=FS5S + 0.8, color=st.RED, weight="bold")
    txt5(ax, 5.20, 5.60, "被打的那一层", fs=FS5S + 0.8, color=st.NAVY,
         weight="bold")
    txt5(ax, 8.62, 5.60, "防", fs=FS5S + 0.8, color=st.TEAL, weight="bold")

    rows = [
        ("角色扮演、虚构场景", "模型自己的拒绝", "看措辞，最容易被绕", 4.62),
        ("换语言、换编码", "输入过滤", "分类器加规范化", 3.64),
        ("网页文档里藏指令", "权限切分", "读的地方不许写", 2.66),
        ("多轮铺垫再要动作", "人工确认", "不可逆动作转人工", 1.68),
    ]
    for atk, layer, sub, y in rows:
        st.box(ax, 0.30, y - 0.36, 2.90, 0.72, "", fc="#FFFFFF", ec=st.RED,
               lw=0.8)
        txt5(ax, 1.75, y, atk, fs=FS5S - 0.6, color=st.INK)
        st.arrow(ax, (3.26, y), (3.62, y), color=st.RED, lw=0.8)

        st.box(ax, 3.68, y - 0.40, 3.05, 0.80, "", fc=st.BG, ec=st.NAVY,
               lw=0.9)
        txt5(ax, 5.20, y + 0.14, layer, fs=FS5S, color=st.NAVY, weight="bold")
        note5(ax, 5.20, y - 0.18, sub, fs=FS5S - 1.0)

        st.arrow(ax, (6.78, y), (7.14, y), color=st.TEAL, lw=0.8)

    defs = ["训练时教它拒绝", "先规范化再判", "读写权限分开", "只放行可撤回的"]
    for (_, _, _, y), d in zip(rows, defs):
        st.box(ax, 7.20, y - 0.36, 2.85, 0.72, "", fc="#FFFFFF", ec=st.TEAL,
               lw=0.8)
        txt5(ax, 8.62, y, d, fs=FS5S - 0.6, color=st.TEAL)

    st.arrow(ax, (0.62, 0.98), (0.62, 5.08), color=st.GRAY, lw=0.8)
    note5(ax, 0.78, 0.82, "越往上越靠模型，越往下越靠系统", fs=FS5S - 1.0,
          ha="left")

    save5(fig, "21/jailbreak-defense.png")


# ---------------------------------------------------------------- 图 16 上下文账单
def fig_context_bill() -> None:
    """读图顺序：
    ① 两根轴都是对数尺，所以“长度翻十倍、钱翻十倍”画出来是一条直线；
    ② 深蓝线是整份塞进去；浅蓝虚线是同样的整份、但命中前缀缓存；
    ③ 金色横线是检索只取三段，与文档多长无关；
    ④ 右侧竖箭头标出同一份 300K 文档的三档价钱。
    """
    st.setup()
    fig, ax = plt.subplots(figsize=(W5, 2.95))
    fig.subplots_adjust(left=0.105, right=0.975, top=0.945, bottom=0.185)

    x = np.array([3, 10, 30, 100, 300])      # 千 token
    whole = x * 0.008                        # 8 元 / 百万 token
    cached = whole * 0.10
    retr = np.full_like(whole, 0.024)

    ax.plot(x, whole, color=st.NAVY, lw=1.5, marker="o", ms=3.6,
            mfc="white", mew=1.0, zorder=4)
    ax.plot(x[2:], cached[2:], color=st.NAVY_L, lw=1.2, ls=(0, (4, 2)),
            marker="s", ms=2.8, mfc="white", mew=0.8, zorder=4)
    ax.plot(x, retr, color=st.GOLD, lw=1.3, marker="^", ms=3.2,
            mfc="white", mew=0.9, zorder=5)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(["3K", "10K", "30K", "100K", "300K"],
                       fontsize=FS5S)
    ax.set_xlim(2.5, 1500)
    ax.set_ylim(0.015, 4.2)
    ax.set_yticks([0.03, 0.1, 0.3, 1, 3])
    ax.set_yticklabels(["0.03", "0.1", "0.3", "1", "3"])
    ax.set_xlabel("一次送进去的上下文长度 / token", fontsize=FS5S + 0.6)
    ax.set_ylabel("单次输入费 / 元", fontsize=FS5S + 0.6)
    ax.tick_params(length=0, labelsize=FS5S)
    ax.grid(axis="x", visible=False)

    for xr, yr, lab, col in [(360, 2.40, "整份塞", st.NAVY),
                             (360, 0.24, "整份＋缓存", st.NAVY_L),
                             (360, 0.024, "检索三段", st.GOLD)]:
        ax.text(xr, yr, lab, ha="left", va="center", fontsize=FS5S - 1.2,
                color=col, zorder=6)

    ax.text(2.8, 3.30, "两根轴都是对数尺：直线就是“成比例”", ha="left",
            va="center", fontsize=FS5S - 1.2, color=st.GRAY)

    save5(fig, "16/context-bill.png")


# ---------------------------------------------------------------- 图 17 错误分层
def fig_error_layers() -> None:
    """读图顺序：
    ① 四行是四类错误，从“你的问题”排到“服务端的问题”；
    ② 中间是典型状态码；右侧是该不该重试；
    ③ 底下一句：200 只说明这一跳通了。
    """
    fig, ax = canvas5(2.80)

    txt5(ax, 1.80, 5.05, "哪一层出的问题", fs=FS5S + 0.2, color=st.NAVY,
         weight="bold")
    txt5(ax, 4.72, 5.05, "典型码", fs=FS5S + 0.2, color=st.NAVY,
         weight="bold")
    txt5(ax, 8.10, 5.05, "怎么做", fs=FS5S + 0.2, color=st.NAVY,
         weight="bold")

    rows = [
        ("请求形状", "400 · 404", "不重试；改字段、核模型名", st.RED, 4.12),
        ("身份与配额", "401 · 403 · 429", "换钥匙；429 才退避重试",
         st.GOLD, 3.20),
        ("内容策略", "200，没有正文", "看结束原因与拦截字段", st.TEAL, 2.28),
        ("服务端", "500 · 529 · 断流", "重试，并切备用供应商", st.NAVY, 1.36),
    ]
    for name, code, act, col, y in rows:
        st.box(ax, 0.30, y - 0.38, 3.00, 0.76, "", fc="#FFFFFF", ec=col,
               lw=0.9)
        txt5(ax, 1.80, y, name, fs=FS5S - 0.4, color=st.INK, weight="bold")

        st.box(ax, 3.44, y - 0.38, 2.56, 0.76, "", fc=st.BG, ec=st.LGRAY,
               lw=0.7)
        txt5(ax, 4.72, y, code, fs=FS5S - 0.8, color=st.INK)

        st.box(ax, 6.14, y - 0.38, 3.96, 0.76, "", fc="#FFFFFF", ec=st.LGRAY,
               lw=0.7)
        txt5(ax, 8.12, y, act, fs=FS5S - 0.8, color=st.INK)

    st.arrow(ax, (0.62, 1.00), (0.62, 4.56), color=st.GRAY, lw=0.8, zorder=1)
    note5(ax, 0.30, 0.74, "越往下越不怪你", fs=FS5S - 1.4, ha="left")
    note5(ax, 0.30, 0.34, "200 只说明这一跳送到了；错误事件、"
                          "半截回答、缺结束标记都在 200 之后",
          fs=FS5S - 1.4, ha="left")

    save5(fig, "17/error-layers.png")


# ---------------------------------------------------------------- 图 20 自建与否
def fig_build_vs_api() -> None:
    """读图顺序：
    ① 横轴是每天的请求数，纵轴是每月成本；
    ② 蓝线是 API：过原点，按量付费；
    ③ 两条横线是自建：只算卡、以及卡加一个人；
    ④ 两个交点就是“该自己扛机器”的门槛。
    """
    st.setup()
    fig, ax = plt.subplots(figsize=(W5, 2.78))
    fig.subplots_adjust(left=0.115, right=0.972, top=0.945, bottom=0.185)

    d = np.linspace(0, 100, 60)               # 千次 / 天
    api = d * 0.99                            # 千元 / 月
    ax.plot(d, api, color=st.NAVY, lw=1.5, zorder=4)
    ax.axhline(15.3, color=st.GOLD, lw=1.2, ls=(0, (5, 3)), zorder=3)
    ax.axhline(45.6, color=st.RED, lw=1.1, ls=(0, (2, 2)), zorder=3)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 30, 60, 90])
    ax.set_xlabel("每天请求数 / 千次", fontsize=FS5S + 0.6)
    ax.set_ylabel("每月成本 / 千元", fontsize=FS5S + 0.6)
    ax.tick_params(length=0, labelsize=FS5S)
    ax.grid(axis="x", visible=False)

    for xv, yv in [(15.5, 15.3), (46.0, 45.6)]:
        ax.plot([xv, xv], [0, yv], color=st.GRAY, lw=0.7, ls=(0, (2, 2)))
    ax.text(14.4, 2.2, "1.5 万次", fontsize=FS5S - 0.8, color=st.GRAY,
            ha="right")
    ax.text(45.1, 8.5, "4.6 万次", fontsize=FS5S - 0.8, color=st.GRAY,
            ha="right")

    ax.text(52, 5.5, "API：每千次 990 元\n一次三千 token 输入",
            fontsize=FS5S - 1.2, color=st.NAVY, ha="left", va="center",
            linespacing=1.6)
    ax.text(2.0, 18.5, "自建：两张卡", fontsize=FS5S - 1.0, color=st.GOLD,
            ha="left", va="bottom")
    ax.text(2.0, 48.5, "自建＋一个人维护", fontsize=FS5S - 1.0, color=st.RED,
            ha="left", va="bottom")
    ax.text(2.0, 70.0, "交点左边租，右边才值得自己扛", fontsize=FS5S - 1.2,
            color=st.GRAY, ha="left", va="center")

    save5(fig, "20/build-vs-api.png")


# ---------------------------------------------------------------- 图 22 生态分层
def fig_ecosystem_stack() -> None:
    """读图顺序：
    ① 五层从下往上：芯片 → 框架 → 模型 → 工具 → 应用；
    ② 每层左边是名字，中间是这一层在做什么，右边落在哪几章；
    ③ 越往下越接近物理，越往上越接近业务。
    """
    fig, ax = canvas5(3.35)

    rows = [
        ("应用", "客服 · 审阅 · 编码助手", "入门 / 应用", st.NAVY, 5.60),
        ("工具与中间层", "检索 · MCP · 评测集", "应用 / 评测", st.NAVY_L,
         4.42),
        ("模型", "闭源接口 · 开放权重", "基础 / 对齐 / 安全 / 多模态",
         st.TEAL, 3.24),
        ("训练与推理框架", "并行切分 · 批调度 · 量化", "结构 / 推理部署",
         st.GOLD, 2.06),
        ("芯片与集群", "加速卡 · 网络 · 机房", "数据与规模 / 训练工程",
         st.GRAY, 0.88),
    ]
    for name, what, ref, col, ytop in rows:
        st.box(ax, 0.34, ytop, 2.30, 0.94, "", fc=col, ec=col, lw=0.8)
        txt5(ax, 1.49, ytop + 0.47, name, fs=FS5S - 0.4, color="white",
             weight="bold")
        st.box(ax, 2.82, ytop, 7.28, 0.94, "", fc="#FFFFFF", ec=st.LGRAY,
               lw=0.7)
        note5(ax, 3.04, ytop + 0.47, what, fs=FS5S - 0.4, color=st.INK,
              ha="left")
        note5(ax, 9.92, ytop + 0.47, ref, fs=FS5S - 1.8, ha="right")

    st.arrow(ax, (0.18, 0.98), (0.18, 6.42), color=st.GRAY, lw=0.8)
    note5(ax, 0.38, 0.42, "越往下越接近物理，越往上越接近业务",
          fs=FS5S - 1.4, ha="left")
    note5(ax, 10.10, 0.42, "同一册会横跨两层，按章分开看",
          fs=FS5S - 1.4, ha="right")

    save5(fig, "22/ecosystem-stack.png")


if __name__ == "__main__":
    fig_generation_loop()
    fig_training_stages()
    fig_cost_breakdown()
    fig_usage_modes()
    fig_eval_landscape()
    fig_thinking_budget()
    fig_multimodal_tokens()
    fig_agent_loop()
    fig_two_stage()
    fig_sampling_temperature()
    fig_data_funnel()
    fig_params_memory()
    fig_context_cost()
    fig_ecosystem()
    fig_jailbreak()
    fig_context_bill()
    fig_error_layers()
    fig_build_vs_api()
    fig_ecosystem_stack()
    print("done.")
