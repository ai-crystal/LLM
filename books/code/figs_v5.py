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


FIGS = {
    "01": fig_01_pipeline,
    "03": fig_03_taxonomy,
    "05": fig_05_batch,
    "07": fig_07_grpo,
    "10": fig_10_mask,
    "11": fig_11_async,
}


def main(argv):
    keys = [a for a in argv[1:] if not a.startswith("-")] or list(FIGS)
    for k in keys:
        FIGS[k]()


if __name__ == "__main__":
    main(sys.argv)
