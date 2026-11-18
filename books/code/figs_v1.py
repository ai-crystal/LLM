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

    save_png(fig, "03/training-stages.png")


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

    save_png(fig, "06/cost-breakdown.png")


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

    save_png(fig, "07/usage-modes.png")


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

    save_png(fig, "08/eval-landscape.png")


if __name__ == "__main__":
    fig_generation_loop()
    fig_training_stages()
    fig_cost_breakdown()
    fig_usage_modes()
    fig_eval_landscape()
    print("done.")
