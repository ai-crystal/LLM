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

import numpy as np
from matplotlib.colors import to_rgb

import figstyle as st
from figstyle import (BG, GOLD, GRAY, GREEN, INK, LGRAY, NAVY, NAVY_L,
                      NAVY_XL, RED, TEAL, arrow, box, plt, setup)

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


def plotcanvas(h_in: float, bottom=0.17):
    """带坐标轴的画布，同样固定宽度 5.2 in。"""
    setup()
    fig = plt.figure(figsize=(W, h_in))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.105, bottom, 0.875, 0.80 - bottom + 0.10])
    return fig, ax


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


# ---------------------------------------------------------------- 03 副作用

def fig_03_taxonomy():
    """第 3 章：四类副作用、机制、测法。"""
    fig, ax = canvas(2.55)

    note(ax, 5.20, 4.82,
         "四类副作用看着不相干，机制却是同一个：数据分布窄，模型容量大")

    for x, s in [(0.45, "现象"), (2.55, "机制"), (6.55, "怎么测")]:
        note(ax, x, 4.36, s, fs=FS_S, ha="left", color=GRAY)
    ax.plot([0.40, 10.05], [4.22, 4.22], color=LGRAY, lw=0.7, zorder=1)

    rows = [
        ("遗忘", "几万条窄数据把参数推窄", "同一批题上做配对比较", NAVY),
        ("过度拒答", "拒答样本退化成触发词", "无害但含敏感词的问题", TEAL),
        ("风格坍缩", "示范的风格本来就集中", "看长度与句式的分布", GOLD),
        ("谄媚", "偏好数据奖励了附和", "用户坚持错误时的改口率", RED),
    ]
    ys = [3.42, 2.72, 2.02, 1.32]
    for (name, mech, meas, color), y in zip(rows, ys):
        box(ax, 0.40, y, 1.95, 0.60, "", fc=tint(color, 0.12), ec=color, lw=0.8)
        txt(ax, 1.375, y + 0.30, name, fs=FS)
        txt(ax, 2.55, y + 0.30, mech, fs=FS_S + 0.3, ha="left")
        txt(ax, 6.55, y + 0.30, meas, fs=FS_S + 0.3, ha="left")

    note(ax, 5.20, 0.62,
         "对策也是同一套：控数据分布、控更新幅度、每一步都留一份评测")

    save(fig, "03/taxonomy.png")


# ---------------------------------------------------------------- 05 PPO

def fig_05_batch():
    """第 5 章：一个 batch 的四个阶段，以及四份权重带来的显存账。"""
    fig, ax = canvas(3.0)

    note(ax, 5.20, 5.74, "一个 batch 从采样到更新，四步都在这里")

    steps = [
        ("① 采样", "同一提示采 G 条"),
        ("② 打分", "RM 给每条一个分"),
        ("③ 归一化", "减均值、除标准差"),
        ("④ 裁剪更新", "同批数据用 μ 遍"),
    ]
    bw, bh = 2.20, 0.92
    xs = [1.28, 3.64, 6.00, 8.36]
    for (head, sub), cx in zip(steps, xs):
        box(ax, cx - bw / 2, 4.02, bw, bh, "", fc=tint(NAVY, 0.10), ec=NAVY_L)
        txt(ax, cx, 4.66, head, fs=FS, weight="bold")
        note(ax, cx, 4.28, sub, fs=FS_S)
    for i in range(3):
        arrow(ax, (xs[i] + bw / 2 + 0.03, 4.48), (xs[i + 1] - bw / 2 - 0.03, 4.48))

    tips = ["最贵，卡在带宽上", "一次前向，冻结", "±1.5 个标准差量级", "ρ 偏离 1 才生效"]
    for t, cx in zip(tips, xs):
        note(ax, cx, 3.68, t, fs=FS_S)

    note(ax, 0.30, 3.12, "7B 模型，bf16 权重，单位 GB", fs=FS_S, ha="left")

    sc = 0.028
    x0 = 1.55
    bars = [
        ("PPO", 2.28, [(56, NAVY), (168, NAVY_L), (28, GRAY)]),
        ("GRPO", 1.52, [(28, NAVY), (84, NAVY_L), (14, GRAY)]),
    ]
    for label, y, segs in bars:
        txt(ax, 1.42, y + 0.21, label, fs=FS, ha="right")
        x = x0
        for gb, color in segs:
            w = gb * sc
            box(ax, x, y, w, 0.42, "", fc=tint(color, 0.22), ec=color, lw=0.7, rounded=0.02)
            txt(ax, x + w / 2, y + 0.21, str(gb), fs=FS_S)
            x += w

    note(ax, 0.32, 1.14, "合计 252 GB，不含激活与 KV 缓存：8 张 80G 起步", fs=FS_S, ha="left")
    note(ax, 5.20, 0.72, "GRPO 把价值模型整个拿掉，显存减半，采样量翻 G 倍")

    save(fig, "05/ppo_batch.png")


# ---------------------------------------------------------------- 07 GRPO

def fig_07_grpo():
    """第 7 章：组内归一化怎么替代价值模型。"""
    fig, ax = canvas(3.0)

    note(ax, 5.20, 5.82, "同一道题采 8 条，只看组内相对好坏")

    box(ax, 0.22, 2.94, 1.50, 1.10, "", fc=tint(NAVY, 0.10), ec=NAVY_L)
    txt(ax, 0.97, 3.66, "一道题", fs=FS, weight="bold")
    note(ax, 0.97, 3.30, "同一 prompt", fs=FS_S)

    scores = [1, 0, 1, 1, 0, 0, 1, 0]
    ys = [4.94, 4.44, 3.94, 3.44, 2.94, 2.44, 1.94, 1.44]
    for i, (s, y) in enumerate(zip(scores, ys)):
        color = GREEN if s else RED
        box(ax, 1.90, y, 1.72, 0.38, "", fc=tint(color, 0.13), ec=color, lw=0.7)
        txt(ax, 2.06, y + 0.19, f"回答 {i + 1}", fs=FS_S, ha="left")
        txt(ax, 3.48, y + 0.19, "对" if s else "错", fs=FS, ha="right", color=color)
        arrow(ax, (1.72, 3.49), (1.90, y + 0.19), lw=0.5, color=GRAY, shrink=1)

    note(ax, 3.82, 5.44, "优势", fs=FS_S, ha="left", color=GRAY)
    for s, y in zip(scores, ys):
        txt(ax, 4.00, y + 0.19, "+1.0" if s else "−1.0", fs=FS,
            color=GREEN if s else RED, ha="left")

    arrow(ax, (4.60, 3.24), (4.96, 3.24))
    box(ax, 4.96, 2.80, 2.05, 0.88, "", fc=tint(GOLD, 0.12), ec=GOLD)
    note(ax, 5.985, 3.24, "每个 token 都带\n这同一个优势", fs=FS_S)

    note(ax, 7.36, 4.56, "省掉价值模型：", fs=FS_S, ha="left", color=INK)
    for k, line in enumerate(["组内均值就是基线", "标准差顺手做了归一化", "少一份权重与前向"]):
        note(ax, 7.36, 4.16 - k * 0.36, line, fs=FS_S, ha="left")
    note(ax, 7.36, 2.58, "代价：每组要采 G 条；\n全对或全错时优势为零", fs=FS_S, ha="left")

    note(ax, 5.20, 1.00, "8 条里 4 对 4 错最理想：全对、全错都没有梯度", fs=FS_S)

    save(fig, "07/grpo.png")


# ---------------------------------------------------------------- 10 掩码

def fig_10_mask():
    """第 10 章：一条轨迹里哪些 token 算损失。"""
    fig, ax = canvas(2.75)

    note(ax, 5.20, 5.30, "同一条轨迹，两种掩码方式，训出来的模型完全不同")

    rows = ["用户请求", "思考", "工具调用", "观察（报错输出）", "最终回答"]
    mask = [False, True, True, False, True]
    ys = [4.16, 3.58, 3.00, 2.42, 1.84]

    for x0, head, good in [(0.25, "只算模型写的部分", True),
                           (5.35, "整条轨迹一起算", False)]:
        txt(ax, x0 + 1.55, 4.94, head, fs=FS, weight="bold")
        for name, ok, y in zip(rows, mask, ys):
            if ok:
                fc, ec, mark = tint(GREEN, 0.13), GREEN, "算"
            elif good:
                fc, ec, mark = BG, LGRAY, "不算"
            else:
                fc, ec, mark = tint(RED, 0.12), RED, "不该算"
            box(ax, x0, y, 3.10, 0.44, "", fc=fc, ec=ec, lw=0.7)
            txt(ax, x0 + 0.16, y + 0.22, name, fs=FS_S, ha="left")
            note(ax, x0 + 2.96, y + 0.22, mark, fs=FS_S, ha="right", color=ec)

    note(ax, 5.20, 1.34, "把观察也当目标，模型学会的是预测测试输出，而不是修代码")
    note(ax, 5.20, 0.78, "灰＝不算损失　绿＝算　红＝不该算却算了", fs=FS_S)

    save(fig, "10/mask.png")


# ---------------------------------------------------------------- 11 异步

def fig_11_async():
    """第 11 章：同步采样与异步采样的时间线。"""
    fig, ax = canvas(2.45)

    note(ax, 5.20, 4.66, "同步等环境，异步让训练卡不空转")

    txt(ax, 1.54, 3.79, "同步", fs=FS, ha="right")
    x = 1.70
    for _ in range(3):
        w = 1.92
        box(ax, x, 3.50, w, 0.58, "", fc=tint(GRAY, 0.10), ec=GRAY)
        note(ax, x + w / 2, 3.79, "采样并等环境", fs=FS_S - 0.3)
        x += w
        w = 0.72
        box(ax, x, 3.50, w, 0.58, "", fc=tint(NAVY, 0.16), ec=NAVY)
        note(ax, x + w / 2, 3.79, "训练", fs=FS_S - 0.3)
        x += w

    txt(ax, 1.54, 2.27, "异步", fs=FS, ha="right")
    box(ax, 1.70, 2.38, 8.60, 0.30, "", fc=tint(GRAY, 0.10), ec=GRAY, rounded=0.02)
    note(ax, 6.00, 2.53, "采样：几百个容器一直跑", fs=FS_S - 0.3)
    box(ax, 1.70, 1.86, 8.60, 0.30, "", fc=tint(NAVY, 0.16), ec=NAVY, rounded=0.02)
    note(ax, 6.00, 2.01, "训练：吃上一批轨迹，几乎不停", fs=FS_S - 0.3)

    note(ax, 5.20, 1.42, "同步的利用率 ≈ 训练时间 ÷ (训练 + 采样 + 等环境)")
    note(ax, 5.20, 0.78, "异步把等待藏进另一批数据里，代价是轨迹的陈旧度", fs=FS_S)

    save(fig, "11/async.png")


# ---------------------------------------------------------------- 02 数据流水线

def fig_02_data():
    """第 2 章：三段流水线与每段的留存率。"""
    fig, ax = canvas(2.62)

    note(ax, 5.20, 5.02, "一万二千条示范，是从十万条原始数据里筛出来的")

    cols = [
        ("① 采集", "100,000 条", NAVY, 0.10,
         ["真实流量 60%", "强模型 30%", "人写 10% 定标准"]),
        ("② 过滤", "23,000 条", TEAL, 0.12,
         ["模板统一留 62%", "去重又留 66%", "核对又留 90%"]),
        ("③ 配比", "12,000 条", GOLD, 0.14,
         ["20 个任务桶", "3 档目标长度", "拒答样本 12%"]),
    ]
    bw, bh = 3.05, 2.02
    xs = [0.34, 3.66, 6.98]
    for (head, num, color, f, lines), x in zip(cols, xs):
        box(ax, x, 2.22, bw, 2.12, "", fc=tint(color, f), ec=color, lw=0.9)
        txt(ax, x + 0.20, 4.10, head, fs=FS + 0.4, ha="left", weight="bold")
        txt(ax, x + 0.20, 3.74, num, fs=FS + 2.6, ha="left", color=color)
        ax.plot([x + 0.20, x + bw - 0.20], [3.54, 3.54], color=color, lw=0.6)
        for k, line in enumerate(lines):
            note(ax, x + 0.20, 3.14 - k * 0.36, line, fs=FS_S, ha="left")

    for i in range(2):
        arrow(ax, (xs[i] + bw + 0.03, 3.30), (xs[i + 1] - 0.03, 3.30), lw=1.0)
        mid = (xs[i] + bw + xs[i + 1]) / 2
        note(ax, mid, 3.56, "×0.23" if i == 0 else "×0.52", fs=FS_S - 0.4)

    note(ax, 5.20, 1.94, "留存率 23% 看着亏，它换来的是两件事", fs=FS_S)
    for k, line in enumerate([
            "一个 epoch 只有 480 万 token，单卡约半小时；",
            "每一桶的配比可控，不靠运气。"]):
        note(ax, 0.42, 1.46 - k * 0.38, line, fs=FS_S, ha="left")

    note(ax, 5.20, 0.50, "先筛再混：十万条直接混着训，配比是筛不动的")

    save(fig, "02/data_pipeline.png")


# ---------------------------------------------------------------- 04 偏好对

def fig_04_pairs():
    """第 4 章：从 4000 条提示到 5600 对可用偏好数据。"""
    fig, ax = canvas(2.62)

    note(ax, 5.20, 5.04, "一对偏好数据要过四道手，才配进训练集")

    steps = [
        ("提示", "4,000", "真实流量抽取"),
        ("回答", "12,000", "每条采 3 个"),
        ("候选对", "8,000", "同长度档配对"),
        ("可用对", "5,600", "一致率筛过"),
    ]
    bw, bh = 2.14, 1.70
    xs = [0.28, 2.72, 5.16, 7.60]
    for (head, num, sub), x in zip(steps, xs):
        box(ax, x, 2.60, bw, bh, "", fc=tint(NAVY, 0.09), ec=NAVY_L)
        txt(ax, x + bw / 2, 3.94, head, fs=FS, weight="bold")
        txt(ax, x + bw / 2, 3.40, num, fs=FS + 3.0, color=NAVY)
        note(ax, x + bw / 2, 2.88, sub, fs=FS_S - 0.6)
    for i in range(3):
        arrow(ax, (xs[i] + bw + 0.03, 3.44), (xs[i + 1] - 0.03, 3.44))

    note(ax, 5.20, 2.16, "标注量按“对”算，成本按“判断”算", fs=FS_S)
    rows = [
        "8,000 对 × 2 人 × 2 个顺序 = 32,000 次判断",
        "每次 3.5 分钟 → 1,867 小时 ≈ 0.93 人年",
        "按 20 美元/小时 → 约 3.7 万美元",
    ]
    for k, line in enumerate(rows):
        note(ax, 0.42, 1.72 - k * 0.38, line, fs=FS_S, ha="left")

    note(ax, 5.20, 0.40, "一致率 75% 不是标注员的水平，是任务本身的模糊度")

    save(fig, "04/pairs.png")


# ---------------------------------------------------------------- 05 四模型

def fig_05_models():
    """第 5 章：PPO 的四份权重，谁训练、谁冻结、每 batch 调几次。"""
    fig, ax = canvas(2.62)

    note(ax, 5.20, 4.92, "四份权重同时在场，只有两份在存梯度")
    note(ax, 5.20, 4.52, "箭头是每次更新要跑的前向；μ 是同一批数据的复用遍数",
         fs=FS_S - 0.6)

    box(ax, 0.40, 1.62, 2.45, 1.30, "", fc=tint(NAVY, 0.14), ec=NAVY, lw=1.0)
    txt(ax, 1.625, 2.62, "策略 πθ", fs=FS + 1.2, weight="bold")
    note(ax, 1.625, 2.26, "训练中", fs=FS_S)
    note(ax, 1.625, 1.92, "采样、生成", fs=FS_S)

    boxes = [
        (3.48, "奖励模型 rφ", "冻结", "每 batch 1 次前向", TEAL),
        (2.50, "参考模型 πref", "冻结", "复用 μ 次", GOLD),
        (1.52, "价值模型 Vψ", "训练中", "复用 μ 次", RED),
    ]
    for y, name, tag, calls, color in boxes:
        box(ax, 5.55, y - 0.30, 3.05, 0.60, "", fc=tint(color, 0.11), ec=color)
        txt(ax, 5.70, y + 0.13, name, fs=FS_S + 0.4, ha="left")
        note(ax, 5.70, y - 0.14, tag + "　" + calls, fs=FS_S - 0.6, ha="left")
        arrow(ax, (2.90, y), (5.50, y), lw=0.8, style="<|-|>")

    note(ax, 4.20, 3.62, "y 与 r", fs=FS_S - 0.6)
    note(ax, 4.20, 2.64, "逐 token 概率", fs=FS_S - 0.6)
    note(ax, 4.20, 1.66, "前缀与优势", fs=FS_S - 0.6)

    note(ax, 5.20, 0.94, "四份都训要 448 GB：56 权重 + 56 梯度 + 336 优化器")
    note(ax, 5.20, 0.56, "冻结两份只要 252 GB，省下的全是梯度与优化器状态",
         fs=FS_S)

    save(fig, "05/four_models.png")


# ---------------------------------------------------------------- 06 log ratio

def fig_06_logratio():
    """第 6 章：log-ratio 的分布，以及 β 把 margin 推到哪个区间。"""
    fig = plt.figure(figsize=(W, 2.45))
    fig.patch.set_facecolor("white")
    setup()
    ax1 = fig.add_axes([0.095, 0.24, 0.40, 0.635])
    ax2 = fig.add_axes([0.605, 0.24, 0.375, 0.635])

    x = np.linspace(-9, 10, 400)
    for mu, sd, color, lab in [(-1.4, 2.4, RED, "落选回答"),
                               (4.0, 1.6, GREEN, "选中回答")]:
        y = np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
        ax1.fill_between(x, y, color=tint(color, 0.18), alpha=0.9, lw=0)
        ax1.plot(x, y, color=color, lw=1.0)
        ax1.plot([mu, mu], [0, np.exp(0) / (sd * np.sqrt(2 * np.pi)) * 0.92],
                 color=color, lw=0.7, ls=":")
        ax1.text(mu, np.exp(0) / (sd * np.sqrt(2 * np.pi)) + 0.015, lab,
                 fontsize=FS_S - 0.4, color=color, ha="center", va="bottom")

    ax1.set_xlim(-9, 10)
    ax1.set_ylim(0, 0.42)
    ax1.set_yticks([])
    ax1.set_xlabel("整条回答的 log ratio", fontsize=FS_S)
    ax1.set_title("分差 5.4：200 token 长的回答", fontsize=FS_S + 0.3, color=INK)
    ax1.grid(axis="y", visible=False)

    z = np.logspace(-2, 1, 200)
    loss = np.log1p(np.exp(-z))
    ax2.plot(z, loss, color=NAVY, lw=1.2)
    ax2.set_xscale("log")
    ax2.set_xlim(0.02, 10)
    ax2.set_ylim(0, 0.78)
    ax2.set_xlabel("margin = β × 5.4", fontsize=FS_S)
    ax2.set_ylabel("损失", fontsize=FS_S)
    ax2.set_title("同一份数据，三个 β", fontsize=FS_S + 0.3, color=INK)

    marks = [(0.054, "β=0.01", 0.095, 0.545, "left"),
             (0.54, "β=0.1", 0.74, 0.46, "left"),
             (5.4, "β=1", 1.25, 0.235, "right")]
    for zv, lab, tx, ty, ha in marks:
        lv = np.log1p(np.exp(-zv))
        ax2.plot([zv], [lv], "o", ms=3.4, color=RED, zorder=5)
        ax2.text(tx, ty, f"{lab}\n{lv:.2f}", fontsize=FS_S - 1.2, color=GRAY,
                 ha=ha, va="center")

    fig.text(0.5, 0.035, "β 的作用是把分差压进 0.5 到 2 这一段，太快太慢都没有梯度",
             fontsize=FS_S, color=GRAY, ha="center")

    save(fig, "06/logratio.png")


# ---------------------------------------------------------------- 07 组内标准差

def fig_07_std():
    """第 7 章：组内归一化算出的优势，随通过率怎么变。"""
    fig, ax = plotcanvas(2.42, bottom=0.225)

    p = np.linspace(0.035, 0.965, 400)
    a_ok = np.sqrt((1 - p) / p)
    a_bad = np.sqrt(p / (1 - p))
    ax.plot(p, a_ok, color=GREEN, lw=1.2, label="答对样本的优势")
    ax.plot(p, a_bad, color=RED, lw=1.2, label="答错样本的优势")

    ks = np.arange(1, 8) / 8
    ax.plot(ks, np.sqrt((1 - ks) / ks), "o", ms=3.2, color=GREEN, zorder=5)
    ax.plot(ks, np.sqrt(ks / (1 - ks)), "o", ms=3.2, color=RED, zorder=5)

    ax.axvspan(0.2, 0.8, color=tint(GOLD, 0.13), zorder=0)
    ax.text(0.5, 0.12, "可用区", fontsize=FS_S - 0.6, color=GOLD, ha="center")
    ax.axvline(0.5, color=GRAY, lw=0.6, ls=":")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 3.4)
    ax.set_xlabel("组内通过率 p（G = 8）", fontsize=FS_S)
    ax.set_ylabel("|A|", fontsize=FS_S)
    ax.set_title("优势随通过率的两端翘起，梯度却越来越不可信",
                 fontsize=FS_S + 0.4, color=INK, pad=6)
    ax.legend(frameon=False, fontsize=FS_S - 0.8, loc="upper center")
    ax.text(0.055, 2.95, "p = 1/8\n只有一条正样本", fontsize=FS_S - 1.0,
            color=GRAY, ha="left", va="top")
    ax.text(0.955, 2.95, "p = 7/8\n只有一条负样本", fontsize=FS_S - 1.0,
            color=GRAY, ha="right", va="top")
    ax.tick_params(labelsize=FS_S - 0.8)

    fig.text(0.5, 0.028, "p = 0 或 1 时标准差为 0，整组优势为零：这类题白采",
             fontsize=FS_S - 0.4, color=GRAY, ha="center")

    save(fig, "07/group_std.png")


# ---------------------------------------------------------------- 10 轨迹时间线

def fig_10_timeline():
    """第 10 章：一条 20 步轨迹的时间构成与上下文增长。"""
    fig = plt.figure(figsize=(W, 2.55))
    fig.patch.set_facecolor("white")
    setup()
    ax = fig.add_axes([0.105, 0.235, 0.855, 0.63])
    ax2 = ax.twinx()

    tool = [0.2, 3.5, 0.2, 0.2, 3.2, 0.2, 0.2, 0.3, 2.8, 0.2,
            0.2, 0.2, 0.3, 3.4, 0.2, 0.2, 2.9, 0.2, 0.2, 3.1]
    gen = [0.6] * 20
    idx = np.arange(1, 21)
    ax.bar(idx, gen, color=tint(NAVY, 0.55), edgecolor=NAVY, lw=0.5, label="生成", width=0.66)
    ax.bar(idx, tool, bottom=gen, color=tint(GOLD, 0.45), edgecolor=GOLD,
           lw=0.5, label="工具执行", width=0.66)

    ctx = 400 + np.cumsum(gen) * 0 + np.array(
        [120] * 20) + np.cumsum(np.array(tool) * 260)
    ax2.plot(idx, ctx / 1000, color=RED, lw=1.1, marker="o", ms=2.2,
             label="上下文")
    ax2.set_ylim(0, 9.2)
    ax2.set_yticks([0, 3, 6, 9])
    ax2.set_ylabel("上下文 / 千 token", fontsize=FS_S - 0.4, color=RED)
    ax2.tick_params(axis="y", labelsize=FS_S - 0.8, colors=RED)
    ax2.spines["right"].set_color(RED)

    tg = sum(gen)
    tt = sum(tool)
    ax.set_xlim(0.3, 20.7)
    ax.set_ylim(0, 4.3)
    ax.set_xlabel("轨迹步数", fontsize=FS_S)
    ax.set_ylabel("单步墙钟 / 秒", fontsize=FS_S)
    ax.tick_params(labelsize=FS_S - 0.8)
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.legend(frameon=False, fontsize=FS_S - 0.9, loc="upper right", ncol=3,
              bbox_to_anchor=(1.0, 1.16))

    fig.text(0.5, 0.035,
             f"{tg:.0f} 秒生成与 {tt:.0f} 秒工具：工具占 {tt / (tg + tt):.0%}，"
             "采样时间是环境决定的",
             fontsize=FS_S, color=GRAY, ha="center")

    save(fig, "10/timeline.png")


FIGS = {
    "01": fig_01_pipeline,
    "02": fig_02_data,
    "03": fig_03_taxonomy,
    "04": fig_04_pairs,
    "05": fig_05_batch,
    "05b": fig_05_models,
    "06": fig_06_logratio,
    "07": fig_07_grpo,
    "07b": fig_07_std,
    "10": fig_10_mask,
    "10b": fig_10_timeline,
    "11": fig_11_async,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
