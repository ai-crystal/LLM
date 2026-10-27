# -*- coding: utf-8 -*-
"""《大模型技术全景》第二部分插图（第 10–25 章）。\n\n运行：\n    python tools/make_figures_b.py            # 全部重画\n    python tools/make_figures_b.py p10-memory # 只画某几张\n\n输出：figures/<name>.pdf（矢量 PDF，无 PNG 产物）\n"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import numpy as np

from figstyle import *  # noqa: F401,F403  (色板、canvas/diagram/box/arrow/save)

plt = sys.modules["matplotlib.pyplot"]


def _install_cjk_weights() -> None:
    """Noto Sans SC 是可变字体，matplotlib 只解析到 weight=100（过细、且无粗体）。\n    这里从 VF 实例化 Regular(400)/Bold(700) 静态字体并注册，家族名保持不变。\n    结果缓存在 build/fonts/，重复运行不再生成。"""
    try:
        from fontTools.ttLib import TTFont  # 仅在需要时导入
        from fontTools.varLib.instancer import instantiateVariableFont
    except ImportError:                     # 没有 fontTools 也不影响出图
        return
    from matplotlib import font_manager

    src = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
    if not src.exists():
        return
    cache = ROOT / "build" / "fonts"
    cache.mkdir(parents=True, exist_ok=True)
    for wght, style in ((400, "Regular"), (700, "Bold")):
        out = cache / f"NotoSansSC-{style}.ttf"
        if not out.exists():
            vf = TTFont(str(src))
            inst = instantiateVariableFont(vf, {"wght": wght}, updateFontNames=True)
            inst.save(str(out))
        try:
            font_manager.fontManager.addfont(str(out))
        except Exception:
            pass


_install_cjk_weights()

# ---------------------------------------------------------------- 公共小工具


def grid(ax, x, y, w, h, rows, cols, color_fn, ec=NAVY_L, lw=0.5, z=3):
    """按行列画矩阵小块；color_fn(r, c) 返回填充色。"""
    for r in range(rows):
        for c in range(cols):
            ax.add_patch(
                Rectangle(
                    (x + c * w / cols, y + r * h / rows),
                    w / cols,
                    h / rows,
                    facecolor=color_fn(r, c),
                    edgecolor=ec,
                    linewidth=lw,
                    zorder=z,
                )
            )


def hatch(ax, x, y, w, h, color=GRAY, z=4, density="////", alpha=0.5):
    """斜线阴影，用来表示“冻结 / 空闲 / 气泡”。"""
    ax.add_patch(
        Rectangle((x, y), w, h, facecolor="none", edgecolor=color,
                  hatch=density, linewidth=0, zorder=z, alpha=alpha)
    )


def title(ax, x, y, text, fs=8.6, color=NAVY):
    ax.text(x, y, text, fontsize=fs, color=color, weight="bold",
            ha="left", va="center", zorder=6)


def note(ax, x, y, text, fs=7.2, color=GRAY, ha="left", va="center", **kw):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, zorder=6, **kw)


def tag(ax, x, y, text, fs=7.0, color=INK, ha="center", va="center"):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, zorder=6)


def legend_swatch(ax, x, y, text, fc=BG, ec=NAVY_L, fs=7.2, w=0.34, h=0.2, hatch_=False):
    box(ax, x, y, w, h, "", fc=fc, ec=ec, lw=0.7, rounded=0.02)
    if hatch_:
        hatch(ax, x, y, w, h, color=GRAY, z=5)
    ax.text(x + w + 0.12, y + h / 2, text, fontsize=fs, color=INK,
            va="center", ha="left", zorder=6)


# ---------------------------------------------------------------- 第 10 章

def f_p10_parallel():
    """四种并行切分方式。"""
    fig, ax = diagram(6.0, 4.9, xlim=(0, 10.6), ylim=(0, 8.2))

    # ---- ① 数据并行
    title(ax, 0.25, 7.95, "① 数据并行 DP", fs=9.2)
    note(ax, 0.25, 7.56, "参数复制一份，数据切成 4 份", fs=8.2)
    for i, yy in enumerate([6.92, 6.30, 5.68, 5.06]):
        box(ax, 0.25, yy, 4.00, 0.46, "", fc=BG, ec=NAVY_L, lw=0.7)
        tag(ax, 0.45, yy + 0.23, f"卡 {i}", 8.2, NAVY, ha="left")
        tag(ax, 1.35, yy + 0.23, "全量 W", 8.2, INK, ha="left")
        tag(ax, 3.00, yy + 0.23, f"数据 D{i}", 8.2, GOLD, ha="left")
    arrow(ax, (4.45, 5.12), (4.45, 7.28), color=NAVY, lw=1.0, style="<|-|>", shrink=3)
    ax.text(4.62, 6.20, "梯度求和", fontsize=8.2, color=NAVY, rotation=90,
            va="center", ha="left", zorder=6)

    # ---- ② 张量并行
    title(ax, 5.55, 7.95, "② 张量并行 TP", fs=9.2)
    note(ax, 5.55, 7.56, "层内切矩阵，每层一次通信", fs=8.2)
    grid(ax, 5.60, 6.42, 1.15, 0.95, 3, 3, lambda r, c: NAVY_XL if c < 2 else GOLD_L)
    grid(ax, 7.05, 6.42, 1.15, 0.95, 3, 3, lambda r, c: NAVY_XL if r < 2 else GOLD_L)
    tag(ax, 6.18, 6.19, "按列切", 8.2, GRAY)
    tag(ax, 7.63, 6.19, "按行切", 8.2, GRAY)
    tag(ax, 6.92, 6.90, "×", 9.5, INK)
    box(ax, 8.50, 6.57, 1.45, 0.65, "部分和", fc=BG, ec=NAVY, fs=8.2)
    arrow(ax, (8.24, 6.89), (8.47, 6.89), color=NAVY, lw=0.9)
    legend_swatch(ax, 5.62, 5.82, "卡 0", fc=NAVY_XL, ec=NAVY_L, fs=8.2)
    legend_swatch(ax, 7.05, 5.82, "卡 1", fc=GOLD_L, ec=GOLD, fs=8.2)

    # ---- ③ 流水并行
    title(ax, 0.25, 4.24, "③ 流水并行 PP", fs=9.2)
    note(ax, 0.25, 3.86, "按层切段，段间只传激活", fs=8.2)
    for i, yy in enumerate([3.24, 2.52, 1.80, 1.08]):
        box(ax, 0.25, yy, 3.05, 0.48, f"阶段 {i}　层 {i*8}–{i*8+7}", fc=BG,
            ec=NAVY_L, fs=8.2)
        if i < 3:
            arrow(ax, (1.78, yy - 0.01), (1.78, yy - 0.22), color=NAVY, lw=1.0,
                  shrink=1)
    note(ax, 0.25, 0.66, "各段同时处理不同微批，负载不均已产生气泡", fs=8.2, color=GRAY)

    # ---- ④ 专家并行
    title(ax, 5.55, 4.24, "④ 专家并行 EP", fs=9.2)
    note(ax, 5.55, 3.86, "专家分卡，token 走 all-to-all", fs=8.2)
    box(ax, 5.60, 2.80, 0.85, 0.48, "token", fc=BG, ec=NAVY_L, fs=8.2)
    box(ax, 6.62, 2.75, 0.95, 0.58, "router", fc=NAVY_XL, ec=NAVY, fs=8.2)
    arrow(ax, (6.47, 3.04), (6.60, 3.04), color=NAVY, lw=0.8)
    for d, xx in enumerate([7.78, 8.42, 9.06, 9.70]):
        tag(ax, xx + 0.26, 2.34, f"卡{d}", 8.2, GRAY)
        for e in range(2):
            num = d * 2 + e
            hot = num in (0, 5)
            box(ax, xx, 3.02 - e * 0.50, 0.52, 0.42, str(num),
                fc=GOLD_L if hot else LGRAY, ec=GOLD if hot else GRAY,
                fs=8.2, rounded=0.04, lw=0.6)
    arrow(ax, (7.59, 3.04), (7.74, 3.04), color=NAVY, lw=0.8)
    note(ax, 5.55, 1.90, "每卡 2 个专家，金色为被选中的 top-2", fs=8.2)
    note(ax, 5.55, 1.50, "激活显存远小于总参数，代价是通信", fs=8.2, color=GRAY)
    save(fig, "p10-parallel")
def _sched_gpipe(P, M):
    """GPipe：所有微批的前向排完，再统一回传。"""
    rows = {i: [] for i in range(P)}
    for i in range(P):
        for m in range(M):
            rows[i].append((i + m, "F", m))
    for i in range(P):
        for m in range(M):
            rows[i].append((i + m + M + P - 1, "B", m))
    span = max(s[0] for i in range(P) for s in rows[i]) + 1
    work = sum(len(v) for v in rows.values())
    return rows, span, 1 - work / (P * span)


def _sched_1f1b(P, M):
    """1F1B：预热 P-i 个前向，之后一前一后交替，最后排空反向。"""
    rows = {i: [] for i in range(P)}
    for i in range(P):
        ops, t = [], i
        nf = nb = 0
        for _ in range(P - i):              # 预热
            ops.append((t, "F", nf)); nf += 1; t += 1
        while nf < M:                       # 稳态：B、F 交替
            ops.append((t, "B", nb)); nb += 1; t += 1
            ops.append((t, "F", nf)); nf += 1; t += 1
        while nb < M:                       # 排空
            ops.append((t, "B", nb)); nb += 1; t += 1
        rows[i] = ops
    span = max(s[0] for i in range(P) for s in rows[i]) + 1
    work = sum(len(v) for v in rows.values())
    return rows, span, 1 - work / (P * span)


def f_p10_pipeline():
    """GPipe 与 1F1B 的时间-设备甘特图。"""
    P, M = 4, 8
    g_rows, g_span, g_bub = _sched_gpipe(P, M)
    f_rows, f_span, f_bub = _sched_1f1b(P, M)

    fig, ax = diagram(6.0, 4.9, xlim=(-2.1, 25.6), ylim=(0, 9.2))

    def draw(rows, span, y_top, name, sub, bubble):
        title(ax, -2.05, y_top + 1.05, name, fs=9.2)
        note(ax, -2.05, y_top + 0.70, sub, fs=8.2)
        for i in range(P):
            yy = y_top - i * 0.72
            ax.add_patch(Rectangle((0, yy), span, 0.52, facecolor=BG,
                                   edgecolor="none", zorder=1))
            ax.text(-0.28, yy + 0.26, f"设备 {i}", fontsize=8.5, color=INK,
                    ha="right", va="center", zorder=6)
            busy = {s[0] for s in rows[i]}
            for t0, k, _m in rows[i]:
                box(ax, t0 + 0.05, yy + 0.05, 0.90, 0.42, k,
                    fc=NAVY if k == "F" else GOLD_L,
                    ec=NAVY if k == "F" else GOLD,
                    tc="white" if k == "F" else INK,
                    fs=8.2, rounded=0.03, lw=0.4)
            for tt in range(span):
                if tt not in busy:
                    hatch(ax, tt + 0.05, yy + 0.05, 0.90, 0.42, color=GRAY,
                          z=2, density="....", alpha=0.6)
        ax.text(span + 0.6, y_top - 1.15, f"气泡 {int(round(bubble*100))}%",
                fontsize=9.0, color=RED, ha="left", va="center", zorder=6)

    draw(g_rows, g_span, 7.80, "GPipe：先排完所有前向，再排所有反向",
         "每个阶段连续处理 8 个微批，切段时整段空闲", g_bub)
    draw(f_rows, f_span, 3.60, "1F1B：稳态中一次前向、一次反向交替",
         "前向一完成即回传，空闲被压到首尾", f_bub)

    ax.plot([0, 22], [1.05, 1.05], color=GRAY, lw=0.7, zorder=4)
    for tt in [0, 5, 10, 15, 20]:
        ax.plot([tt, tt], [0.97, 1.05], color=GRAY, lw=0.7, zorder=4)
        ax.text(tt + 0.4, 0.86, str(tt), fontsize=8.2, color=GRAY,
                ha="center", va="top", zorder=6)
    ax.text(23.8, 1.18, "时间（槽）", fontsize=8.2, color=GRAY, ha="right", va="bottom")

    note(ax, -2.05, 0.40, "M=8 微批，P=4 阶段", fs=8.2)
    legend_swatch(ax, 4.6, 0.32, "前向 F", fc=NAVY, ec=NAVY, fs=8.2)
    legend_swatch(ax, 7.4, 0.32, "反向 B", fc=GOLD_L, ec=GOLD, fs=8.2)
    legend_swatch(ax, 10.0, 0.32, "设备空闲（气泡）", fc=BG, ec=GRAY, hatch_=True, fs=8.2)
    save(fig, "p10-pipeline")
def f_p10_memory():
    """7B / 70B 在 Adam 混合精度下的显存构成（横向堆叠条）。"""
    setup()
    fig, axes = plt.subplots(2, 1, figsize=(6.0, 3.2),
                             gridspec_kw={"height_ratios": [1, 1]})
    fig.subplots_adjust(left=0.05, right=0.845, top=0.80, bottom=0.135, hspace=1.05)

    parts = [("参数 fp16", NAVY), ("梯度 fp16", NAVY_L),
             ("优化器状态 fp32 m / v", GOLD), ("激活值", TEAL)]
    panels = [
        (axes[0], "7B 模型 · bs=1，2K 上下文 · GB", [14, 14, 56, 28], 128,
         [0, 25, 50, 75, 100], "≈ 112 GB"),
        (axes[1], "70B 模型 · 同配置 · GB", [140, 140, 560, 280], 1280,
         [0, 400, 800, 1200], "≈ 1.1 TB"),
    ]
    for ax, name, vals, xmax, ticks, total in panels:
        left = 0
        for (lab, col), v in zip(parts, vals):
            ax.barh([0], [v], left=left, height=0.55, color=col,
                    edgecolor="white", linewidth=1.2, label=lab, zorder=3)
            ax.text(left + v / 2, 0, f"{v}", ha="center", va="center",
                    fontsize=8.5, color="white", zorder=5)
            left += v
        ax.set_xlim(0, xmax)
        ax.set_ylim(-0.50, 0.55)
        ax.set_yticks([])
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelsize=8.2)
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        ax.set_title(name, loc="left", fontsize=9, color=INK, pad=7)
        ax.text(left + xmax * 0.03, 0, total, fontsize=8.8, color=NAVY,
                va="center", ha="left", zorder=5)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False,
               fontsize=8.2, bbox_to_anchor=(0.5, 1.0), handlelength=1.0,
               columnspacing=1.2, borderaxespad=0.1)
    fig.text(0.5, 0.018, "优化器状态占一半以上：每参数 12 字节的 fp32 主权重与 m / v；"
             "单卡 80 GB 装不下 70B。", fontsize=8.2, color=GRAY, ha="center")
    save(fig, "p10-memory")


def f_p11_sft():
    """SFT 样本的损失遮罩：只对回答段计损失。"""
    fig, ax = diagram(6.0, 2.4, xlim=(-0.95, 10.05), ylim=(0, 3.7))

    # 消息块
    box(ax, 0.20, 2.30, 1.55, 0.62, "系统提示", fc=NAVY_XL, ec=NAVY_L, fs=8.2)
    box(ax, 1.90, 2.30, 1.55, 0.62, "用户指令", fc=GOLD_L, ec=GOLD, fs=8.2)
    for i in range(4):
        box(ax, 3.75 + i * 0.62, 2.30, 0.55, 0.62, f"$y_{i+1}$", fc=TEAL,
            ec=TEAL, tc="white", fs=8.2, rounded=0.03)
    ax.text(6.28, 2.61, "…", fontsize=9.0, color=GRAY, va="center", ha="left")

    # 掩码
    box(ax, 0.20, 1.55, 1.55, 0.42, "0", fc=LGRAY, ec=GRAY, tc=GRAY, fs=8.2)
    box(ax, 1.90, 1.55, 1.55, 0.42, "0", fc=LGRAY, ec=GRAY, tc=GRAY, fs=8.2)
    for i in range(4):
        box(ax, 3.75 + i * 0.62, 1.55, 0.55, 0.42, "1", fc=NAVY, ec=NAVY,
            tc="white", fs=8.2, rounded=0.03)

    note(ax, -0.90, 2.61, "消息", fs=8.5, color=INK)
    note(ax, -0.90, 1.76, "掩码", fs=8.5, color=INK)

    ax.plot([3.75, 3.75, 6.22, 6.22], [3.02, 3.14, 3.14, 3.02], color=TEAL, lw=0.8,
            zorder=5)
    tag(ax, 4.98, 3.28, "只有这 4 个位置计损失", 8.2, TEAL)

    box(ax, 6.50, 1.92, 3.48, 1.00,
        "$L=-\\Sigma_{t\\in\\mathrm{ans}}\\log \\pi_\\theta(y_t\\mid x,y_{<t})$",
        fc=BG, ec=TEAL, fs=8.6, lw=0.9)
    arrow(ax, (6.30, 1.95), (6.46, 2.25), color=TEAL, lw=0.8, shrink=1)

    note(ax, 0.20, 0.95, "不计损失的位置写 0（实现里常写 −100 作 ignore_index）。", fs=8.2, color=GRAY)
    note(ax, 0.20, 0.52, "标签右移一位，模型学的永远是下一个 token；系统与用户段只提供条件。",
         fs=8.2, color=GRAY)
    save(fig, "p11-sft")
def f_p12_rlhf():
    """RLHF 三阶段流水线。"""
    fig, ax = diagram(6.5, 3.4, xlim=(0, 10.2), ylim=(0, 5.7))

    stages = [
        (0.25, "① SFT　监督微调", "监督微调\n下一 token 预测\n\n得到策略 $\\pi_{SFT}$",
         "示范数据 $(x,y)$\n1 万–10 万条", NAVY),
        (3.75, "② 奖励模型 RM", "偏好对排序\nBradley–Terry\n\n$\\sigma(r(y_w)-r(y_l))$",
         "偏好对 $(x,y_w,y_l)$\n20 万–100 万条", GOLD),
        (7.25, "③ PPO　强化学习", "采样回答\n奖励打分 − KL 惩罚\n\n更新 $\\pi_\\theta$",
         "在线采样\n每条都由当前策略生成", TEAL),
    ]
    for x, ttl, body, data, col in stages:
        title(ax, x, 5.30, ttl, fs=8.2, color=col)
        box(ax, x, 3.15, 2.60, 1.72, body, fc=BG, ec=col, fs=7.2, lw=0.9)
        box(ax, x, 2.05, 2.60, 0.66, data, fc="white",
            ec=LGRAY, fs=6.8, rounded=0.04)
        ax.plot([x + 1.3, x + 1.3], [2.72, 3.15], color=LGRAY, lw=0.7,
                ls=(0, (2, 2)), zorder=4)

    arrow(ax, (2.88, 3.95), (3.72, 3.95), color=NAVY, lw=1.0)
    note(ax, 3.30, 4.24, "$\\pi_{SFT}$", fs=7.0, color=NAVY, ha="center")
    arrow(ax, (6.38, 3.95), (7.22, 3.95), color=GOLD, lw=1.0)
    note(ax, 6.80, 4.24, "冻结 $r_\\phi$", fs=7.0, color=GOLD, ha="center")

    note(ax, 0.25, 1.55, "三个阶段串行：前一段的产物是后一段的输入。", fs=7.2)
    note(ax, 0.25, 1.24, "代价是同时维护 4 个模型、流程最长、对超参最敏感；第 ① 步只在回答段计损失。",
         fs=7.2, color=GRAY)
    note(ax, 0.25, 0.90, "第 ② 步只用排序，不要求打分绝对值；第 ③ 步的奖励来自 ②，KL 拉住 ① 的分布防止跑偏。",
         fs=7.2, color=GRAY)
    save(fig, "p12-rlhf")


def f_p12_ppo():
    """PPO 的四个模型与数据流。"""
    fig, ax = diagram(6.5, 3.8, xlim=(0, 10), ylim=(0, 6.0))

    box(ax, 0.15, 4.10, 1.15, 0.62, "提示 $x$", fc=BG, ec=NAVY_L, fs=7.6)
    box(ax, 1.95, 3.95, 1.70, 1.00, "策略 $\\pi_\\theta$\n可训练", fc=NAVY_XL,
        ec=NAVY, fs=7.8, lw=1.0)
    box(ax, 4.15, 3.95, 1.40, 1.00, "回答 $y$", fc="white", ec=NAVY_L, fs=7.8)

    box(ax, 1.95, 2.30, 1.70, 0.90, "参考 $\\pi_{ref}$\n冻结", fc=LGRAY, ec=GRAY, fs=7.8)
    hatch(ax, 1.95, 2.30, 1.70, 0.90, color=GRAY, z=4, alpha=0.45)
    box(ax, 4.15, 2.30, 1.40, 0.90,
        "KL 惩罚\n同一 $y$ 上\n两模型各打一次分",
        fc=BG, ec=TEAL, fs=6.5)

    box(ax, 6.35, 4.60, 1.75, 0.72, "奖励 $r_\\phi$（冻结）", fc=LGRAY, ec=GRAY, fs=7.4)
    hatch(ax, 6.35, 4.60, 1.75, 0.72, color=GRAY, z=4, alpha=0.45)
    box(ax, 6.35, 3.25, 1.75, 0.72, "价值 $V_\\psi$（可训练）", fc=NAVY_XL,
        ec=NAVY, fs=7.4)
    box(ax, 8.50, 4.60, 1.35, 0.72, "标量 $r$", fc="white", ec=GOLD, fs=7.6)
    box(ax, 8.50, 3.25, 1.35, 0.72, "优势 $\\hat{A}$", fc="white", ec=GOLD, fs=7.6)

    box(ax, 5.60, 1.20, 4.20, 0.98,
        "最大化 $\\mathbb{E}[r]-\\beta\\,\\mathrm{KL}(\\pi_\\theta\\,\\|\\,\\pi_{ref})$\n"
        "梯度只回传到 $\\pi_\\theta$ 与 $V_\\psi$", fc=BG, ec=NAVY, fs=7.2, lw=0.9)

    arrow(ax, (1.32, 4.41), (1.93, 4.45), color=NAVY, lw=0.9)
    arrow(ax, (3.67, 4.45), (4.13, 4.45), color=NAVY, lw=0.9)
    arrow(ax, (5.57, 4.75), (6.33, 4.95), color=GOLD, lw=0.9)
    ax.text(5.80, 5.02, "打分", fontsize=6.6, color=GOLD, ha="center", va="bottom")
    arrow(ax, (5.57, 4.20), (6.33, 3.62), color=NAVY_L, lw=0.9)
    arrow(ax, (5.57, 4.05), (5.10, 3.22), color=TEAL, lw=0.9)
    arrow(ax, (3.67, 2.72), (4.13, 2.72), color=GRAY, lw=0.9)
    arrow(ax, (8.12, 4.96), (8.48, 4.96), color=GOLD, lw=0.9)
    arrow(ax, (9.17, 4.56), (9.17, 4.00), color=GOLD, lw=0.9)
    arrow(ax, (8.90, 3.21), (8.60, 2.20), color=GOLD, lw=0.9)
    arrow(ax, (5.55, 2.45), (6.30, 1.90), color=TEAL, lw=0.9)

    legend_swatch(ax, 0.35, 0.95, "可训练", fc=NAVY_XL, ec=NAVY)
    legend_swatch(ax, 0.35, 0.55, "冻结（无梯度）", fc=LGRAY, ec=GRAY, hatch_=True)
    note(ax, 0.35, 1.80, "显存 ≈ 4 份模型：\n2 份策略 + RM + 价值头", fs=7.2)
    save(fig, "p12-ppo")


# ---------------------------------------------------------------- 第 13 章

def f_p13_dpo():
    """RLHF 两步 vs DPO 一步，以及隐式奖励的等价关系。"""
    fig, ax = diagram(6.0, 3.5, xlim=(0, 10), ylim=(0, 5.6))

    ax.plot([5.02, 5.02], [0.95, 4.95], color=LGRAY, lw=0.8, ls=(0, (3, 3)), zorder=1)

    title(ax, 0.25, 5.25, "RLHF：先学奖励，再强化", fs=9.2)
    title(ax, 5.40, 5.25, "DPO：直接优化策略", fs=9.2)

    box(ax, 0.25, 4.45, 2.15, 0.55, "偏好对 $(x,y_w,y_l)$", fc=BG, ec=GRAY, fs=8.2)
    box(ax, 0.25, 3.35, 2.15, 0.68, "奖励模型 $r_\\phi$", fc=LGRAY, ec=GRAY, fs=8.2)
    box(ax, 0.25, 2.05, 2.15, 0.78, "PPO\n$\\max r_\\phi-\\beta\\mathrm{KL}$",
        fc=GOLD_L, ec=GOLD, fs=8.2)
    box(ax, 0.25, 1.15, 2.15, 0.55, "策略 $\\pi_\\theta$", fc=NAVY_XL, ec=NAVY, fs=8.2)
    arrow(ax, (1.32, 4.43), (1.32, 4.06), color=GRAY, lw=0.9)
    arrow(ax, (1.32, 3.33), (1.32, 2.86), color=GOLD, lw=0.9)
    arrow(ax, (1.32, 2.03), (1.32, 1.73), color=NAVY, lw=0.9)
    note(ax, 1.46, 3.10, "冻结", fs=8.2)

    box(ax, 5.40, 4.45, 2.15, 0.55, "偏好对 $(x,y_w,y_l)$", fc=BG, ec=GRAY, fs=8.2)
    box(ax, 5.35, 2.55, 4.35, 1.35,
        "同一对回答各算一次 logprob\n"
        "$L=-\\log\\sigma\\left(\\beta\\,(\\Delta_w-\\Delta_l)\\right)$\n"
        "$\\Delta=\\log\\pi_\\theta-\\log\\pi_{ref}$",
        fc=BG, ec=TEAL, fs=8.2, lw=0.9)
    box(ax, 5.40, 1.15, 2.80, 0.55, "策略 $\\pi_\\theta$（从 $\\pi_{ref}$ 起）",
        fc=NAVY_XL, ec=NAVY, fs=8.2)
    arrow(ax, (6.48, 4.43), (6.48, 3.93), color=TEAL, lw=0.9)
    arrow(ax, (6.70, 2.53), (6.70, 1.73), color=NAVY, lw=0.9)

    arrow(ax, (2.45, 3.69), (5.30, 3.69), color=TEAL, lw=1.0)
    note(ax, 3.88, 3.98, "隐式奖励 $r=\\beta\\log\\dfrac{\\pi_\\theta}{\\pi_{ref}}$",
         fs=8.2, color=TEAL, ha="center")

    note(ax, 0.25, 0.62, "DPO 省掉奖励模型与在线采样，但只用到偏好对信息，", fs=8.2, color=GRAY)
    note(ax, 0.25, 0.30, "对数据覆盖更敏感；RLHF 多两层模型，换来更细的控制。", fs=8.2, color=GRAY)
    save(fig, "p13-dpo")


def f_p14_grpo():
    """GRPO：组内采样、组内标准化得到优势。"""
    fig, ax = diagram(6.5, 3.9, xlim=(0, 10), ylim=(0, 6.2))
    title(ax, 0.25, 5.95, "一个提示采样 G 条回答，组内比较代替价值模型", fs=8.4)
    note(ax, 0.25, 5.66, "以 G=4 为例：同一提示、同一奖励函数，四条回答互相成为基线", fs=7.0)

    ys = [4.70, 3.98, 3.26, 2.54]
    box(ax, 0.25, 3.57, 0.82, 0.62, "提示\n$x$", fc=NAVY_XL, ec=NAVY, fs=7.2)
    rewards = ["1.0", "0.0", "0.6", "0.2"]
    advs = ["+1.1", "−1.2", "+0.4", "−0.9"]
    for i, yy in enumerate(ys):
        box(ax, 1.40, yy, 1.45, 0.52, f"回答 $o_{i+1}$", fc=BG, ec=NAVY_L, fs=7.2)
        arrow(ax, (1.09, 3.88), (1.38, yy + 0.26), color=NAVY, lw=0.7)
        box(ax, 3.10, yy, 0.82, 0.52, f"$r_{i+1}$={rewards[i]}", fc="white",
            ec=GOLD, fs=6.8)
        arrow(ax, (2.87, yy + 0.26), (3.08, yy + 0.26), color=GOLD, lw=0.8)

    note(ax, 5.32, 5.66, "组内标准化", fs=7.6, color=TEAL, ha="center")
    note(ax, 5.32, 5.38, "$\\hat{A}_i=(r_i-\\bar{r})/\\mathrm{std}(r)$", fs=7.2,
         ha="center", color=INK)
    box(ax, 4.32, 2.26, 2.00, 2.94, "", fc=BG, ec=TEAL, lw=0.9, alpha=0.55)
    for i, yy in enumerate(ys):
        note(ax, 5.32, yy + 0.26, f"$\\hat{{A}}_{i+1}$ = {advs[i]}", fs=7.0,
             ha="center", va="center", color=INK)

    box(ax, 6.80, 3.12, 2.85, 1.52,
        "策略梯度更新\n$\nabla_\\theta\\log\\pi_\\theta(o_i)\\hat{A}_i$\n"
        "同组 4 条一起更新", fc=NAVY_XL, ec=NAVY, fs=7.4, lw=1.0)
    arrow(ax, (6.36, 3.88), (6.76, 3.88), color=TEAL, lw=1.0)

    note(ax, 0.25, 1.72, "组内均值就是基线：G 条回答同题同奖励，横向可比；", fs=7.2)
    note(ax, 0.25, 1.43, "不需要价值模型，省下一份与策略同规模的显存。", fs=7.2, color=GRAY)
    note(ax, 0.25, 0.92, "注意：组内全对或全错时 std≈0，优势全为 0，该提示不产生梯度。",
         fs=7.2, color=RED)
    save(fig, "p14-grpo")


def f_p14_length():
    """训练过程中回答长度与准确率的分离。"""
    fig, ax = canvas(6.0, 3.0)
    fig.subplots_adjust(left=0.115, right=0.885, top=0.88, bottom=0.17)
    ax2 = ax.twinx()
    steps = np.arange(0, 1001, 10)
    length = 145 + 55 / (1 + np.exp(-(steps - 120) / 170)) + 640 / (1 + np.exp(-(steps - 630) / 105))
    acc = 41 + 21 * (1 - np.exp(-steps / 230))

    ax.axvspan(640, 1000, color=RED, alpha=0.06, lw=0, zorder=1)
    ax.plot(steps, length, color=NAVY, lw=1.4, zorder=4, label="平均回答长度")
    ax2.plot(steps, acc, color=GOLD, lw=1.4, ls="--", zorder=4, label="准确率")
    ax.axvline(640, color=GRAY, lw=0.7, ls=(0, (2, 3)), zorder=2)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1050)
    ax2.set_ylim(25, 80)
    ax.set_xlabel("训练步数", fontsize=8.5)
    ax.set_ylabel("平均回答长度（token）", color=NAVY, fontsize=8.5)
    ax2.set_ylabel("验证集准确率（%）", color=GOLD, fontsize=8.5)
    ax.tick_params(axis="both", labelsize=8.2)
    ax2.tick_params(axis="y", labelsize=8.2, colors=GOLD)
    ax.tick_params(axis="y", colors=NAVY)
    ax.set_axisbelow(True)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(GOLD)

    ax.annotate("长度失控区间", xy=(700, 800), fontsize=8.2, color=RED,
                ha="center", va="center")
    ax.annotate("奖励被钻空子：\n更长但不再更对", xy=(830, 250), fontsize=8.2,
                color=RED, ha="center", va="center")
    ax.annotate("准确率在此已饱和（≈62%）", xy=(662, 61.2), xycoords=ax2.transData,
                xytext=(330, 745), textcoords="data", fontsize=8.2, color=GOLD,
                ha="center",
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.8,
                                connectionstyle="arc3,rad=-0.2"))
    ax.annotate("长度 ≈150 → ≈840 token", xy=(975, 845), xytext=(620, 1015),
                fontsize=8.2, color=NAVY, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.8))

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8.2,
              bbox_to_anchor=(0.005, 1.0), handlelength=1.6)
    save(fig, "p14-length")


def f_p16_testtime():
    """采样次数与准确率：多数投票、验证器重排、单次采样。"""
    fig, ax = canvas(6.0, 3.1)
    ns = np.array([1, 2, 4, 8, 16, 32, 64])
    vanilla = np.array([61.5, 61.8, 62.0, 62.1, 62.0, 62.2, 62.1])
    maj = np.array([61.5, 66.0, 70.5, 73.5, 76.0, 77.5, 78.5])
    ver = np.array([61.5, 70.0, 76.0, 80.5, 84.0, 86.5, 88.0])

    ax.plot(ns, vanilla, color=GRAY, lw=1.2, marker="o", ms=2.6)
    ax.plot(ns, maj, color=NAVY, lw=1.4, marker="o", ms=2.6)
    ax.plot(ns, ver, color=RED, lw=1.4, marker="s", ms=2.4)

    ax.set_xscale("log", base=2)
    ax.set_xticks(ns)
    ax.set_xticklabels([str(v) for v in ns], fontsize=8.2)
    ax.minorticks_off()
    ax.set_xlim(0.85, 260)
    ax.set_ylim(49, 93)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.set_xlabel("采样次数 $n$（成本 ∝ n）", fontsize=8.5)
    ax.set_ylabel("准确率（%）", fontsize=8.5)
    ax.set_axisbelow(True)

    ax.text(70, 62.1, "单次采样\n（等价于 $n=1$）", fontsize=8.2, color=GRAY, va="center")
    ax.text(70, 78.5, "自洽投票", fontsize=8.4, color=NAVY, va="center")
    ax.text(70, 88.0, "验证器重排", fontsize=8.4, color=RED, va="center")

    ax.axvline(16, color=LGRAY, lw=1.0, ls=(0, (2, 3)), zorder=1)
    ax.text(1.0, 91.4, "三条曲线在 $n=1$ 处重合：增益全部来自多采样与选择。",
            fontsize=8.2, color=GRAY, va="top")
    ax.text(1.0, 51.4, "$n=16$ 时：自洽投票 +14.5 点，验证器重排再 +7 点。",
            fontsize=8.2, color=GRAY, va="bottom")
    save(fig, "p16-testtime")


def f_p17_tools():
    """工具调用循环与停止条件。"""
    fig, ax = diagram(6.0, 3.4, xlim=(0, 10.4), ylim=(0, 6.0))

    box(ax, 0.30, 4.45, 2.45, 0.80, "① 模型生成\n读消息，定下一步", fc=NAVY_XL,
        ec=NAVY, fs=8.2, lw=0.9)
    box(ax, 4.30, 4.45, 2.45, 0.80, "② 输出工具调用\n名字 + 参数 JSON", fc=BG,
        ec=NAVY_L, fs=8.2)
    box(ax, 4.30, 2.70, 2.45, 0.80, "③ 运行时执行\n校验 / 沙箱 / 超时", fc=BG,
        ec=NAVY_L, fs=8.2)
    box(ax, 0.30, 2.70, 2.45, 0.80, "④ 结果回填\n截断、结构化", fc=BG,
        ec=NAVY_L, fs=8.2)

    arrow(ax, (2.78, 4.85), (4.26, 4.85), color=NAVY, lw=1.0)
    arrow(ax, (5.52, 4.41), (5.52, 3.55), color=NAVY, lw=1.0)
    arrow(ax, (4.26, 3.10), (2.78, 3.10), color=NAVY, lw=1.0)
    arrow(ax, (1.52, 2.66), (1.52, 4.41), color=NAVY, lw=1.0)
    tag(ax, 3.52, 5.05, "工具调用", 8.2, NAVY)
    tag(ax, 5.70, 4.00, "执行", 8.2, NAVY, ha="left")
    tag(ax, 3.52, 2.90, "观察结果", 8.2, NAVY)
    tag(ax, 1.68, 3.55, "下一轮", 8.2, NAVY, ha="left")

    box(ax, 7.20, 2.55, 2.90, 2.70, "", fc=BG, ec=RED, lw=0.9)
    note(ax, 7.40, 4.92, "停止条件", fs=8.6, color=RED)
    note(ax, 7.40, 4.55, "· 给出最终答案\n· 到达步数上限\n· 工具超时或报错\n· 人工中断",
         fs=8.2, color=INK, va="top", linespacing=1.55)
    arrow(ax, (6.78, 4.85), (7.16, 4.85), color=RED, lw=0.9, ls=(0, (3, 2)))

    box(ax, 0.30, 0.95, 6.45, 0.95,
        "工具示例：检索、代码执行、数据库、HTTP API。\n"
        "结果都进上下文，token 预算决定循环能跑多长。", fc="white", ec=LGRAY, fs=8.2)
    note(ax, 0.30, 0.50, "读图顺序：① → ② → ③ → ④ 回到 ①；任一步都可触发右侧停止条件。",
         fs=8.2, color=GRAY)
    save(fig, "p17-tools")


def f_p18_multimodal():
    """图像 patch → ViT → 投影 → 与文本 token 拼接；早期 / 晚期融合对比。"""
    fig, ax = diagram(6.6, 4.1, xlim=(0, 11), ylim=(0, 6.2))
    rng = np.random.default_rng(7)

    # ---- 图像
    box(ax, 0.15, 3.95, 1.05, 1.05, "", fc="white", ec=GRAY, lw=0.7)
    for r in range(4):
        for c in range(4):
            v = rng.random()
            ax.add_patch(Rectangle((0.20 + c * 0.235, 4.00 + r * 0.235), 0.225, 0.225,
                                   facecolor=NAVY, alpha=0.25 + 0.5 * v,
                                   edgecolor="none", zorder=4))
    tag(ax, 0.68, 3.72, "图像", 7.2, INK)

    # ---- 切 patch：一块被单独框出
    for r in range(3):
        for c in range(3):
            hot = (r == 0 and c == 1)
            ax.add_patch(Rectangle((1.62 + c * 0.34, 4.02 + r * 0.34), 0.34, 0.34,
                                   facecolor=GOLD_L if hot else BG,
                                   edgecolor=GOLD if hot else LGRAY, lw=0.6, zorder=4))
    tag(ax, 2.13, 3.72, "切成 patch", 7.2, GRAY)

    box(ax, 3.15, 4.10, 1.30, 0.80, "ViT\n视觉编码器", fc=NAVY_XL, ec=NAVY, fs=7.2)
    box(ax, 4.85, 4.10, 1.05, 0.80, "投影层\nMLP", fc=BG, ec=NAVY_L, fs=7.2)

    # ---- 拼成同一序列：视觉 token + 文本 token
    seq_cols = [GOLD_L] * 3 + [NAVY_XL] * 5
    seq_ec = [GOLD] * 3 + [NAVY_L] * 5
    for i, (fc, ec) in enumerate(zip(seq_cols, seq_ec)):
        ax.add_patch(Rectangle((6.10 + i * 0.245, 4.22), 0.21, 0.52,
                               facecolor=fc, edgecolor=ec, lw=0.6, zorder=4))
    ax.plot([6.09, 6.84], [4.86, 4.86], color=GOLD, lw=0.7, zorder=5)
    ax.plot([6.09, 6.09, 6.84, 6.84], [4.86, 4.80, 4.80, 4.86], color=GOLD, lw=0.7, zorder=5)
    tag(ax, 6.47, 5.03, "视觉 ×3", 6.6, GOLD)
    ax.plot([6.86, 8.05], [4.86, 4.86], color=NAVY_L, lw=0.7, zorder=5)
    ax.plot([6.86, 6.86, 8.05, 8.05], [4.86, 4.80, 4.80, 4.86], color=NAVY_L, lw=0.7, zorder=5)
    tag(ax, 7.45, 5.03, "文本 token", 6.6, NAVY)
    tag(ax, 7.05, 3.96, "同一条序列，一起进 LLM", 6.6, GRAY)

    box(ax, 8.65, 3.95, 1.35, 1.05, "LLM\n（同一序列）", fc=NAVY, ec=NAVY,
        tc="white", fs=7.2)
    arrow(ax, (8.09, 4.48), (8.62, 4.48), color=NAVY, lw=0.9)
    arrow(ax, (1.22, 4.48), (1.58, 4.48), color=NAVY, lw=0.9)
    arrow(ax, (2.66, 4.48), (3.12, 4.48), color=NAVY, lw=0.9)
    arrow(ax, (4.47, 4.50), (4.82, 4.50), color=NAVY, lw=0.9)
    arrow(ax, (5.92, 4.50), (6.07, 4.50), color=NAVY, lw=0.9)

    # ---- 下方两种融法
    title(ax, 0.15, 2.90, "早期融合（主线做法）", fs=7.8)
    box(ax, 0.15, 1.95, 1.20, 0.50, "视觉 token", fc=GOLD_L, ec=GOLD, fs=6.8)
    box(ax, 0.15, 1.30, 1.20, 0.50, "文本 token", fc=NAVY_XL, ec=NAVY_L, fs=6.8)
    box(ax, 1.80, 1.45, 1.30, 0.85, "拼接后\n同一个\nTransformer", fc=BG, ec=NAVY, fs=6.6)
    box(ax, 3.55, 1.55, 1.05, 0.62, "联合输出", fc="white", ec=GRAY, fs=6.8)
    arrow(ax, (1.38, 2.20), (1.77, 1.95), color=GOLD, lw=0.8)
    arrow(ax, (1.38, 1.55), (1.77, 1.72), color=NAVY_L, lw=0.8)
    arrow(ax, (3.13, 1.88), (3.52, 1.88), color=NAVY, lw=0.8)
    note(ax, 0.15, 0.95, "跨模态交互从第一层就开始", fs=6.6, color=GRAY)

    title(ax, 5.85, 2.90, "晚期融合（对比方案）", fs=7.8)
    box(ax, 5.85, 1.95, 1.15, 0.50, "视觉编码器", fc=GOLD_L, ec=GOLD, fs=6.6)
    box(ax, 5.85, 1.30, 1.15, 0.50, "文本编码器", fc=NAVY_XL, ec=NAVY_L, fs=6.6)
    box(ax, 7.30, 1.45, 1.10, 0.85, "各自打分\n再融合", fc=BG, ec=NAVY, fs=6.6)
    box(ax, 8.75, 1.55, 0.95, 0.62, "输出", fc="white", ec=GRAY, fs=6.8)
    arrow(ax, (7.03, 2.20), (7.27, 2.02), color=GOLD, lw=0.8)
    arrow(ax, (7.03, 1.55), (7.27, 1.72), color=NAVY_L, lw=0.8)
    arrow(ax, (8.43, 1.88), (8.72, 1.88), color=NAVY, lw=0.8)
    note(ax, 5.85, 0.95, "两模态几乎不交互，多用于检索类任务", fs=6.6, color=GRAY)

    note(ax, 0.15, 0.45, "读图顺序：图像 → patch → 编码 → 投影 → 与文本 token 拼接 → 同一个 LLM。",
         fs=7.0, color=GRAY)
    save(fig, "p18-multimodal")


# ---------------------------------------------------------------- 第 19 章

_TARGET = np.array([
    [0, 0, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 0],
    [1, 1, 0, 0, 1, 1],
    [1, 1, 0, 0, 1, 1],
    [0, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 0, 0],
])


def _frame(ax, x, y, s, rnd, w=0.95, lab=""):
    n = 6
    cell = w / n
    for r in range(n):
        for c in range(n):
            v = s * _TARGET[r, c] + (1 - s) * rnd[r, c]
            ax.add_patch(Rectangle((x + c * cell, y + (n - 1 - r) * cell), cell, cell,
                                   facecolor=NAVY, alpha=float(np.clip(v, 0.04, 0.95)) * 0.75,
                                   edgecolor=LGRAY, lw=0.2, zorder=4))
    ax.add_patch(Rectangle((x, y), w, w, facecolor="none", edgecolor=GRAY, lw=0.7, zorder=5))
    if lab:
        tag(ax, x + w / 2, y - 0.26, lab, 8.2, INK)


def f_p19_diffusion():
    """两种生成顺序：扩散并行去噪 vs 自回归逐 token。"""
    fig, ax = diagram(6.0, 3.95, xlim=(0, 10), ylim=(0.80, 7.05))
    rnd = np.random.default_rng(3).random((6, 6))

    title(ax, 0.15, 6.80, "扩散：从噪声开始，固定 T 步整图去噪", fs=9.2)
    note(ax, 0.15, 6.42, "每一步都是一次完整前向，步数预先固定", fs=8.2, color=NAVY)
    xs = [0.25, 1.85, 3.45, 5.05, 6.65]
    ss = [0.0, 0.30, 0.58, 0.82, 1.0]
    labs = ["$x_T$", "$x_{3T/4}$", "$x_{T/2}$", "$x_{T/4}$", "$x_0$"]
    for x, s, lb in zip(xs, ss, labs):
        _frame(ax, x, 5.05, s, rnd, lab=lb)
    for i in range(4):
        arrow(ax, (xs[i] + 0.98, 5.52), (xs[i + 1] - 0.03, 5.52), color=NAVY, lw=1.0)
    box(ax, 7.85, 5.05, 1.35, 0.95, "输出图像\n1024×1024", fc=BG, ec=NAVY, fs=8.2)
    arrow(ax, (7.64, 5.52), (7.82, 5.52), color=NAVY, lw=1.0)

    ax.plot([0.15, 9.85], [4.45, 4.45], color=LGRAY, lw=0.8, ls=(0, (3, 3)))

    title(ax, 0.15, 4.05, "自回归：从左到右，每个 token 一次前向", fs=9.2)
    n_tok = 8
    x0, w, gap = 0.25, 0.80, 0.16
    for i in range(n_tok):
        done = i < 5
        box(ax, x0 + i * (w + gap), 2.75, w, 0.58, f"$y_{i+1}$" if done else "",
            fc=NAVY_XL if done else "white", ec=NAVY_L if done else LGRAY,
            fs=8.2, rounded=0.03, lw=0.6)
        if not done:
            hatch(ax, x0 + i * (w + gap), 2.75, w, 0.58, color=LGRAY, z=3,
                  density="...", alpha=0.7)
    tag(ax, x0 + 5 * (w + gap) - 0.12, 2.52, "已生成", 8.2, NAVY, ha="right")
    tag(ax, x0 + 5 * (w + gap) + 0.02, 2.52, "待生成", 8.2, GRAY, ha="left")
    arrow(ax, (x0, 3.52), (x0 + 7 * (w + gap) + w, 3.52), color=NAVY, lw=0.9,
          style="-|>", shrink=0)

    note(ax, 0.15, 1.95, "第 $t$ 步只能依赖前 $t-1$ 个 token：长度可变，但必须串行；", fs=8.2)
    note(ax, 0.15, 1.60, "每步都要重读全部前缀（KV 缓存为此而生，见 p22-paged）。", fs=8.2,
         color=GRAY)
    note(ax, 0.15, 1.05, "对照：扩散的“顺序”是加噪步数，自回归的“顺序”是 token 位置。",
         fs=8.2, color=NAVY)
    save(fig, "p19-diffusion")
def f_p20_quant():
    """比特宽度与困惑度退化。"""
    fig, ax = canvas(6.0, 3.2)
    fig.subplots_adjust(left=0.115, right=0.975, top=0.86, bottom=0.235)
    labels = ["16", "8", "4", "3", "2"]
    vals = [0.10, 1.9, 1.2, 7.5, 42.0]
    cols = [NAVY_XL, NAVY_L, GOLD, RED, RED]
    x = np.arange(len(vals))
    bars = ax.bar(x, [v - 0.09 for v in vals], bottom=0.09, width=0.56,
                  color=cols, edgecolor="white", linewidth=0.8, zorder=3)
    for b, v in zip(bars, vals):
        txt = "基准" if v < 0.15 else f"+{v:g}%"
        ax.text(b.get_x() + b.get_width() / 2, v * 1.45 + 0.03, txt,
                ha="center", va="bottom", fontsize=8.5,
                color=INK if v < 10 else RED)

    ax.set_yscale("log")
    ax.set_ylim(0.09, 320)
    ax.set_xlim(-0.6, 4.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_xlabel("比特宽度（bit）", fontsize=8.5)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.set_ylabel("困惑度相对退化（%，对数轴）", fontsize=8.5)
    ax.set_yticks([0.1, 1, 10, 100])
    ax.set_yticklabels(["0.1", "1", "10", "100"])
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)

    ax.axhspan(10, 320, color=RED, alpha=0.05, lw=0, zorder=1)
    ax.annotate("4 bit：分组量化 + 逐层补偿" + chr(10) + "退化低于逐张量 INT8",
                xy=(2.32, 1.70), xytext=(1.72, 205), fontsize=8.2, color=GOLD,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.8,
                                connectionstyle="arc3,rad=-0.18"))
    ax.text(-0.55, 200, "RTN：直接四舍五入\n3 bit 以下崩坏", fontsize=8.2,
            color=GRAY, ha="left", va="top", linespacing=1.4)
    fig.text(0.5, 0.028, "16 bit 为 bf16 基准；8 bit 为逐张量 INT8（RTN）；"
             "4 bit 为分组 128 + GPTQ / AWQ；浅红区 >10% 视为不可用。",
             fontsize=8.2, color=GRAY, ha="center")
    save(fig, "p20-quant")


def f_p20_spec():
    """投机解码：草稿模型连提 4 个 token，目标模型一次验证。"""
    fig, ax = diagram(6.0, 3.2, xlim=(0, 10.6), ylim=(0.6, 6.6))

    # 逐 token 解码
    title(ax, 0.20, 6.35, "逐 token 解码", fs=9.0, color=GRAY)
    for i in range(4):
        box(ax, 0.30 + i * 1.62, 5.35, 1.50, 0.62, f"$y_{i+1}$", fc=LGRAY,
            ec=GRAY, fs=8.5, rounded=0.03)
    ax.add_patch(Rectangle((0.30, 5.12), 6.24, 0.13, facecolor=GRAY, alpha=0.35,
                           edgecolor="none", zorder=3))
    tag(ax, 0.30, 4.92, "目标模型跑 4 次：$4\\times t_{target}$", 8.2, GRAY, ha="left")

    # 投机解码
    title(ax, 0.20, 4.35, "投机解码", fs=9.0)
    for i in range(4):
        ok = i < 3
        box(ax, 0.30 + i * 0.56, 3.35, 0.52, 0.62, f"$\\gamma_{i+1}$",
            fc=GOLD_L if ok else "white", ec=GREEN if ok else RED,
            fs=8.2, rounded=0.02, lw=0.8)
    tag(ax, 0.30, 3.13, "草稿模型连续提 4 个", 8.2, GOLD, ha="left")

    box(ax, 1.62, 2.10, 1.72, 0.70, "目标模型\n验证 5 个位置", fc=NAVY, ec=NAVY,
        tc="white", fs=8.2, rounded=0.03)
    box(ax, 3.62, 2.10, 1.90, 0.70, "输出 4 个 token\n（3 接受 + 1 修正）", fc=NAVY_XL,
        ec=NAVY, fs=8.2, rounded=0.03)
    arrow(ax, (2.32, 3.32), (2.30, 2.84), color=NAVY, lw=0.9)
    arrow(ax, (3.38, 2.45), (3.58, 2.45), color=NAVY, lw=0.9)
    tag(ax, 2.62, 3.66, "第 4 个被拒，其后全丢", 8.2, RED, ha="left")

    ax.add_patch(Rectangle((0.30, 1.80), 1.10, 0.13, facecolor=GOLD, alpha=0.75,
                           edgecolor="none", zorder=3))
    ax.add_patch(Rectangle((1.40, 1.80), 1.50, 0.13, facecolor=NAVY, alpha=0.9,
                           edgecolor="none", zorder=3))
    tag(ax, 0.30, 1.60, "草稿 4 步", 8.2, GOLD, ha="left")
    tag(ax, 1.46, 1.60, "验证 1 次", 8.2, NAVY, ha="left")

    tag(ax, 6.10, 3.62, "≈ 2–3× 加速", 9.2, GREEN, ha="left")
    note(ax, 6.10, 3.24, "接受率越高越划算；\n每轮至少出 1 个 token。", fs=8.2, color=GRAY)

    note(ax, 0.20, 1.05, "第一处拒绝之后，剩余草稿全部作废，回到采样；",
         fs=8.2)
    note(ax, 0.20, 0.70, "草稿模型取目标模型的 1/10 大小，须同词表、同 tokenizer，"
         "分布越接近接受率越高。", fs=8.2, color=GRAY)
    save(fig, "p20-spec")
def f_p21_longctx():
    """有效利用率与长度扩展方法。"""
    setup()
    fig, axes = plt.subplots(1, 2, figsize=(6.0, 2.95),
                             gridspec_kw={"width_ratios": [0.95, 1.15]})
    fig.subplots_adjust(left=0.095, right=0.985, top=0.855, bottom=0.22, wspace=0.36)

    ax = axes[0]
    pos = np.linspace(0, 100, 400)
    acc = 90 - 34 * np.exp(-((pos - 50) / 26) ** 2)
    ax.axvspan(30, 70, color=RED, alpha=0.06, lw=0, zorder=1)
    ax.plot(pos, acc, color=NAVY, lw=1.5, zorder=4)
    ax.set_xlim(0, 100)
    ax.set_ylim(50, 108)
    ax.set_xlabel("关键信息的相对位置（%）", fontsize=8.2)
    ax.set_ylabel("召回准确率（%）", fontsize=8.2)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([50, 60, 70, 80, 90])
    ax.tick_params(labelsize=8.0)
    ax.set_axisbelow(True)
    ax.annotate("中段最易被忽略", xy=(50, 57.2), xytext=(50, 101),
                fontsize=8.2, color=RED, ha="center", va="top",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8,
                                connectionstyle="arc3,rad=0"))
    ax.text(2, 95, "开头", fontsize=8.2, color=GRAY)
    ax.text(98, 95, "结尾", fontsize=8.2, color=GRAY, ha="right")

    ax = axes[1]
    names = ["直接外推", "位置插值", "NTK/YaRN", "继续训练"]
    vals = [31, 58, 74, 89]
    cols = [RED, GOLD, NAVY_L, NAVY]
    bars = ax.bar(np.arange(4), vals, width=0.6, color=cols, edgecolor="white",
                  linewidth=0.8, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2.0, f"{v}", ha="center",
                va="bottom", fontsize=8.2, color=INK)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(names, fontsize=8.2)
    ax.set_ylim(0, 105)
    ax.set_ylabel("128K 检索准确率（%）", fontsize=8.2)
    ax.tick_params(labelsize=8.0)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)

    axes[0].set_title("同一上下文内，位置决定召回率", fontsize=8.8, pad=6)
    axes[1].set_title("把 8K 模型扩到 128K 的四条路线", fontsize=8.8, pad=6)
    save(fig, "p21-longctx")


def f_p22_paged():
    """逻辑 KV 块到物理页的映射，以及与连续分配的对比。"""
    fig, ax = diagram(6.0, 3.6, xlim=(0, 11), ylim=(0.28, 6.35))

    title(ax, 0.20, 6.12, "逻辑块 → 物理页：按需分配，可以共享", fs=9.0)

    rows = [("A · 块 0", "页 3", NAVY_XL, NAVY_L, ""),
            ("A · 块 1", "页 1", NAVY_XL, NAVY_L, ""),
            ("A · 块 2", "页 4", GOLD_L, GOLD, "公共前缀"),
            ("A · 块 3", "页 6", NAVY_XL, NAVY_L, ""),
            ("B · 块 0", "页 4", GOLD_L, GOLD, "复用 A 的页 4"),
            ("B · 块 1", "页 0", NAVY_XL, NAVY_L, ""),
            ("B · 块 2", "页 5", NAVY_XL, NAVY_L, "")]
    y0, step, hh = 5.58, 0.34, 0.28
    for i, (blk, page, fc, ec, extra) in enumerate(rows):
        y = y0 - i * step
        box(ax, 0.20, y, 1.25, hh, blk, fc=fc, ec=ec, fs=8.2, rounded=0.03, lw=0.6)
        arrow(ax, (1.49, y + hh / 2), (2.03, y + hh / 2), color=ec, lw=0.7, shrink=1)
        box(ax, 2.07, y, 0.82, hh, page, fc="white", ec=ec, fs=8.2, rounded=0.03, lw=0.6)
        if extra:
            note(ax, 2.98, y + hh / 2, extra, fs=8.2, color=GOLD)

    tag(ax, 4.30, 5.95, "GPU 显存中的物理页（页号与逻辑顺序无关）", 8.2, INK, ha="left")
    owners = ["B1", "A1", "空闲", "A0", "A/B", "B2", "A3", "空闲"]
    for i, own in enumerate(owners):
        x = 4.30 + i * 0.80
        if own == "A/B":
            fc, ec = GOLD, GOLD
        elif own == "空闲":
            fc, ec = LGRAY, GRAY
        else:
            fc, ec = (NAVY_XL if own[0] == "A" else GOLD_L), NAVY_L
        box(ax, x, 5.10, 0.72, 0.62, f"页{i}\n{own}", fc=fc, ec=ec,
            fs=8.2, rounded=0.03, lw=0.6)
        if own == "空闲":
            hatch(ax, x, 5.10, 0.72, 0.62, color=GRAY, z=4, density="////", alpha=0.4)
    tag(ax, 4.30, 4.86, "页 4 同时属于 A 与 B：公共前缀只算一次", 8.0, GOLD, ha="left")

    # 两种分配方式
    ax.plot([0.20, 10.85], [3.32, 3.32], color=LGRAY, lw=0.8, ls=(0, (3, 3)))
    title(ax, 0.20, 3.04, "连续分配：按最大长度预留，内部全是碎片", fs=8.2, color=GRAY)
    seq = [("A", 2.30, NAVY_XL), ("空闲", 1.10, LGRAY), ("B", 1.60, GOLD_L),
           ("空闲", 2.40, LGRAY), ("C", 1.20, LGRAY)]
    xx = 0.20
    for lab, wd, col in seq:
        ax.add_patch(Rectangle((xx, 2.38), wd, 0.42, facecolor=col,
                               edgecolor=GRAY if lab == "空闲" else NAVY_L, lw=0.6, zorder=3))
        if lab == "空闲":
            hatch(ax, xx, 2.38, wd, 0.42, color=GRAY, z=4, density="////", alpha=0.5)
        tag(ax, xx + wd / 2, 2.59, lab, 7.8, GRAY if lab == "空闲" else INK)
        xx += wd

    title(ax, 0.20, 2.02, "分页：按块填满，碎片小且可回收", fs=8.2, color=NAVY)
    xx = 0.20
    for lab, wd, col in [("A0", 0.70, NAVY_XL), ("A1", 0.70, NAVY_XL), ("B0", 0.70, GOLD_L),
                         ("A2", 0.70, GOLD), ("B1", 0.70, NAVY_XL), ("B2", 0.70, GOLD_L),
                         ("C0", 0.70, LGRAY)]:
        ax.add_patch(Rectangle((xx, 1.36), wd - 0.06, 0.42, facecolor=col,
                               edgecolor=NAVY_L, lw=0.6, zorder=3))
        tag(ax, xx + (wd - 0.06) / 2, 1.57, lab, 7.8, INK)
        xx += wd

    note(ax, 0.20, 0.85, "块大小固定（如 16 token/块），页号可以不连续；共享页让公共前缀只存一份。",
         fs=8.2, color=GRAY)
    note(ax, 0.20, 0.52, "连续分配按“最大可能长度”预留，长请求一来就装不下；", fs=8.2, color=GRAY)
    note(ax, 0.20, 0.24, "分页按实际块数分配，长短请求可以混跑，只剩最后一块有内部碎片。", fs=8.2, color=GRAY)
    save(fig, "p22-paged")
def f_p22_batching():
    """静态批处理 vs 连续批处理的时间线。"""
    fig, ax = diagram(6.6, 4.0, xlim=(0, 10.6), ylim=(0, 7.2))
    x0, sc = 0.85, 0.86                     # 时间轴：1 单位 = 0.86

    def bar(y, t0, t1, lab, fc, ec, h=0.42, tc=INK, fs=6.4):
        ax.add_patch(Rectangle((x0 + t0 * sc, y), (t1 - t0) * sc, h, facecolor=fc,
                               edgecolor=ec, lw=0.6, zorder=3))
        if lab:
            tag(ax, x0 + (t0 + t1) / 2 * sc, y + h / 2, lab, fs, tc)

    def slots(y_top, n=4):
        for i in range(n):
            yy = y_top - i * 0.60
            ax.add_patch(Rectangle((x0, yy), 10.4 * sc, 0.46, facecolor=BG,
                                   edgecolor="none", zorder=1))
            ax.text(x0 - 0.12, yy + 0.23, f"槽 {i}", fontsize=6.8, color=INK,
                    ha="right", va="center", zorder=6)

    # ---- 静态批处理
    title(ax, 0.20, 6.95, "静态批处理：整批同进同出，等最慢的那个", fs=7.8, color=GRAY)
    slots(6.10)
    st = [(0, 4.0, "A"), (0, 3.0, "B"), (0, 2.5, "C"), (0, 6.0, "D（最长）")]
    for i, (t0, t1, lab) in enumerate(st):
        yy = 6.10 - i * 0.60
        bar(yy, t0, t1, lab, NAVY_XL, NAVY_L)
        if t1 < 6.0:
            hatch(ax, x0 + t1 * sc, yy, (6.0 - t1) * sc, 0.46, color=GRAY, z=2,
                  density="....", alpha=0.55)
    st2 = [(6.0, 10.0, "E"), (6.0, 9.0, "F"), (6.0, 8.0, "G"), (6.0, 7.5, "H")]
    for i, (t0, t1, lab) in enumerate(st2):
        yy = 6.10 - i * 0.60
        bar(yy, t0, t1, lab, GOLD_L, GOLD)
        if t1 < 10.0:
            hatch(ax, x0 + t1 * sc, yy, (10.0 - t1) * sc, 0.46, color=GRAY, z=2,
                  density="....", alpha=0.55)
    tag(ax, x0 + 5.0 * sc, 3.72, "灰色点区 = 槽位空转：整批要等最慢的 D", 6.4, RED)

    # ---- 连续批处理
    title(ax, 0.20, 3.36, "连续批处理：谁先结束谁出队，空位立即被新请求填上", fs=7.8, color=NAVY)
    slots(2.70)
    ct = [
        [(0, 4.0, "A"), (4.0, 7.0, "E"), (7.0, 9.5, "I")],
        [(0, 3.0, "B"), (3.0, 6.0, "F"), (6.0, 8.0, "J")],
        [(0, 2.5, "C"), (2.5, 5.5, "G"), (5.5, 8.5, "K")],
        [(0, 6.0, "D"), (6.0, 9.0, "H")],
    ]
    for i, segs in enumerate(ct):
        yy = 2.70 - i * 0.60
        for t0, t1, lab in segs:
            bar(yy, t0, t1, lab, NAVY_XL, NAVY_L)
    tag(ax, x0 + 9.8 * sc, 0.74, "9.5 时刻已完成 11 个请求（静态为 8 个）", 6.4, NAVY, ha="right")

    # 时间轴
    ax.plot([x0, x0 + 10.4 * sc], [0.42, 0.42], color=GRAY, lw=0.7, zorder=4)
    for tt in range(0, 11, 2):
        ax.plot([x0 + tt * sc, x0 + tt * sc], [0.35, 0.42], color=GRAY, lw=0.7, zorder=4)
        ax.text(x0 + tt * sc, 0.23, str(tt), fontsize=6.6, color=GRAY,
                ha="center", va="top", zorder=6)
    tag(ax, x0 + 5.2 * sc, 0.02, "时间（每格 ≈ 一次解码步）", 6.6, GRAY)
    legend_swatch(ax, 0.20, 6.62, "同一批请求", fc=NAVY_XL, ec=NAVY_L)
    legend_swatch(ax, 2.55, 6.62, "后到请求", fc=GOLD_L, ec=GOLD)
    legend_swatch(ax, 4.90, 6.62, "槽位空闲", fc=BG, ec=GRAY, hatch_=True)
    save(fig, "p22-batching")


# ---------------------------------------------------------------- 第 23 章

def f_p23_cost():
    """不同上下文长度下的成本构成。"""
    fig, ax = canvas(6.0, 3.15)
    fig.subplots_adjust(left=0.115, right=0.975, top=0.80, bottom=0.155)
    ctx = ["1K", "8K", "32K", "128K"]
    prefill = np.array([1.0, 2.2, 4.5, 9.0])
    decode = np.array([1.2, 2.4, 4.8, 9.5])
    kv = np.array([0.9, 5.5, 22.0, 88.0])
    net = np.array([0.4, 0.9, 1.6, 3.0])
    x = np.arange(4)
    ax.bar(x, prefill, width=0.54, color=NAVY, label="prefill（预填充）",
           edgecolor="white", linewidth=0.8, zorder=3)
    ax.bar(x, decode, width=0.54, bottom=prefill, color=NAVY_L,
           label="decode（逐 token）", edgecolor="white", linewidth=0.8, zorder=3)
    ax.bar(x, kv, width=0.54, bottom=prefill + decode, color=GOLD,
           label="KV 缓存读写", edgecolor="white", linewidth=0.8, zorder=3)
    ax.bar(x, net, width=0.54, bottom=prefill + decode + kv, color=TEAL,
           label="网络 / 调度", edgecolor="white", linewidth=0.8, zorder=3)

    totals = prefill + decode + kv + net
    for xi, t in zip(x, totals):
        ax.text(xi, t + 2.5, f"{t:.0f}", ha="center", va="bottom", fontsize=8.5,
                color=INK)
    for xi, v, base in zip(x, kv, prefill + decode):
        if v > 12:
            ax.text(xi, base + v / 2, f"{v:.0f}", ha="center", va="center",
                    fontsize=8.5, color="white")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}" for c in ctx], fontsize=8.5)
    ax.set_xlabel("上下文长度", fontsize=8.5)
    ax.set_ylabel("相对成本（每 1K 输出 token）", fontsize=8.5)
    ax.set_ylim(0, 152)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.20), ncol=4,
              frameon=False, fontsize=8.2, handlelength=1.0, columnspacing=1.1,
              borderaxespad=0.0)

    ax.annotate("KV 缓存成为主项：" + chr(10) + "decode 每步都要读全量 KV", xy=(2.95, 84),
                xytext=(0.55, 136), fontsize=8.2, color=GOLD, ha="left",
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.8,
                                connectionstyle="arc3,rad=-0.22"))
    ax.text(0.30, 62, "64× 上下文\n→ 31× 成本", fontsize=8.2, color=GRAY,
            va="center", ha="left")
    save(fig, "p23-cost")
def f_p24_rag():
    """RAG 流水线与可优化环节。"""
    fig, ax = diagram(6.6, 3.8, xlim=(0, 10.2), ylim=(0, 6.2))

    title(ax, 0.15, 5.95, "离线索引", fs=7.8, color=GRAY)
    box(ax, 0.15, 4.95, 0.95, 0.62, "文档库", fc=BG, ec=GRAY, fs=6.8)
    box(ax, 1.35, 4.95, 0.90, 0.62, "切块", fc=GOLD_L, ec=GOLD, fs=6.8)
    box(ax, 2.55, 4.95, 1.00, 0.62, "向量化", fc=BG, ec=NAVY_L, fs=6.8)
    box(ax, 3.85, 4.95, 1.30, 0.62, "向量库", fc=NAVY_XL, ec=NAVY, fs=6.8)
    arrow(ax, (1.12, 5.26), (1.33, 5.26), color=GRAY, lw=0.8)
    arrow(ax, (2.27, 5.26), (2.53, 5.26), color=GRAY, lw=0.8)
    arrow(ax, (3.57, 5.26), (3.83, 5.26), color=GRAY, lw=0.8)
    tag(ax, 1.80, 4.76, "★ 粒度 / 重叠", 6.2, GOLD)

    title(ax, 0.15, 3.55, "在线查询", fs=7.8, color=NAVY)
    box(ax, 0.15, 2.55, 0.95, 0.62, "问题", fc=BG, ec=GRAY, fs=6.8)
    box(ax, 1.35, 2.55, 0.95, 0.62, "向量化", fc=BG, ec=NAVY_L, fs=6.8)
    box(ax, 3.85, 2.55, 1.30, 0.62, "检索 top-k", fc=GOLD_L, ec=GOLD, fs=6.6)
    box(ax, 5.50, 2.55, 1.20, 0.62, "重排 rerank", fc=GOLD_L, ec=GOLD, fs=6.6)
    box(ax, 7.00, 2.55, 1.35, 0.62, "拼上下文", fc=GOLD_L, ec=GOLD, fs=6.6)
    box(ax, 8.60, 2.55, 1.40, 0.62, "LLM 生成\n答案 + 引用", fc=NAVY, ec=NAVY,
        tc="white", fs=6.6)
    arrow(ax, (1.12, 2.86), (1.33, 2.86), color=NAVY, lw=0.8)
    arrow(ax, (2.32, 2.86), (3.83, 2.86), color=NAVY, lw=0.8)
    arrow(ax, (5.17, 2.86), (5.48, 2.86), color=NAVY, lw=0.8)
    arrow(ax, (6.72, 2.86), (6.98, 2.86), color=NAVY, lw=0.8)
    arrow(ax, (8.37, 2.86), (8.58, 2.86), color=NAVY, lw=0.8)
    # 向量库 -> 检索
    arrow(ax, (4.50, 4.93), (4.50, 3.19), color=NAVY, lw=0.9, style="-|>", shrink=2)
    tag(ax, 4.62, 4.05, "取候选", 6.2, NAVY, ha="left")

    for xx, lab in [(4.50, "★ 混合检索"), (6.10, "★ 交叉编码"), (7.68, "★ 压缩 / 引用")]:
        tag(ax, xx, 2.33, lab, 6.2, GOLD)

    box(ax, 0.15, 0.90, 9.85, 1.05,
        "★ 可优化环节：切块粒度与重叠、BM25 + 向量混合检索、交叉编码器重排、\n"
        "上下文压缩与引用对齐；每一步都要用“命中率 / 忠实度”回归测试验证效果。",
        fc="white", ec=LGRAY, fs=6.8)
    note(ax, 0.15, 0.45, "读图顺序：离线自上而下建库，在线自左向右查询；两条线在“向量库”处相接。",
         fs=6.7, color=GRAY)
    save(fig, "p24-rag")


# ---------------------------------------------------------------- 第 25 章

def f_p25_agent():
    """长程任务的智能体结构：规划、执行、验证、回退。"""
    fig, ax = diagram(6.6, 3.9, xlim=(0, 10.2), ylim=(0, 6.5))

    box(ax, 0.25, 5.62, 1.15, 0.52, "用户目标", fc=BG, ec=GRAY, fs=6.8)
    box(ax, 1.62, 5.30, 2.00, 0.92, "规划器\n拆解子任务与依赖", fc=NAVY_XL, ec=NAVY,
        fs=6.8, lw=0.9)
    box(ax, 4.05, 5.30, 1.58, 0.92, "任务队列\nDAG / 待办", fc=BG, ec=NAVY_L, fs=6.8)
    box(ax, 4.05, 3.68, 1.58, 0.90, "执行器\n按步产出", fc=NAVY_XL, ec=NAVY, fs=6.8, lw=0.9)
    box(ax, 6.20, 3.68, 2.85, 0.90, "工具 / 环境\n检索 · 代码执行 · API", fc=BG,
        ec=NAVY_L, fs=6.8)
    box(ax, 6.20, 2.15, 2.85, 0.85, "验证器\n测试 / 规则 / 模型评分", fc=BG, ec=RED,
        fs=6.8, lw=0.9)
    box(ax, 6.20, 0.85, 2.85, 0.75, "汇总答案（带引用与不确定度）", fc=NAVY,
        ec=NAVY, tc="white", fs=6.8)
    box(ax, 0.25, 3.62, 1.55, 0.95, "记忆\n短期轨迹\n长期经验", fc=GOLD_L, ec=GOLD,
        fs=6.6)

    arrow(ax, (1.42, 5.88), (1.60, 5.82), color=NAVY, lw=0.9)
    arrow(ax, (3.64, 5.76), (4.03, 5.76), color=NAVY, lw=0.9)
    arrow(ax, (4.84, 5.28), (4.84, 4.61), color=NAVY, lw=0.9)
    tag(ax, 4.96, 4.95, "取子任务", 6.2, NAVY, ha="left")
    arrow(ax, (5.65, 4.36), (6.18, 4.36), color=NAVY, lw=0.9)
    tag(ax, 5.90, 4.52, "① 调用", 6.2, NAVY)
    arrow(ax, (6.18, 3.90), (5.65, 3.90), color=GRAY, lw=0.9)
    tag(ax, 5.90, 3.74, "② 观察", 6.2, GRAY)
    arrow(ax, (5.62, 3.70), (6.72, 3.05), color=NAVY, lw=0.9)
    tag(ax, 5.66, 3.18, "③ 产出", 6.2, NAVY, ha="right")
    arrow(ax, (7.62, 2.13), (7.62, 1.63), color=GREEN, lw=1.0)
    tag(ax, 7.74, 1.89, "通过", 6.4, GREEN, ha="left")

    arrow(ax, (6.18, 2.57), (5.12, 2.57), color=RED, lw=0.9, ls=(0, (3, 2)))
    tag(ax, 5.65, 2.72, "不通过", 6.2, RED)
    box(ax, 2.20, 2.20, 2.88, 0.72, "回退：重试 / 重规划 / 请人工", fc="white",
        ec=RED, fs=6.6, lw=0.8)
    arrow(ax, (2.62, 2.94), (2.62, 5.28), color=RED, lw=0.9, ls=(0, (3, 2)))
    tag(ax, 2.72, 4.20, "重规划", 6.2, RED, ha="left")
    arrow(ax, (4.62, 2.94), (4.62, 3.66), color=RED, lw=0.9, ls=(0, (3, 2)))
    tag(ax, 4.72, 3.30, "重试", 6.2, RED, ha="left")

    arrow(ax, (1.02, 4.59), (1.58, 5.28), color=GOLD, lw=0.8, style="<|-|>")
    tag(ax, 1.04, 4.86, "读写", 6.2, GOLD, ha="left")

    note(ax, 0.25, 1.98, "长程任务的失败大多不在单步，而在错误累积；", fs=6.7, color=GRAY)
    note(ax, 0.25, 1.74, "验证器把“早停 + 回退”写成结构。", fs=6.7, color=GRAY)
    note(ax, 0.25, 1.28, "读图顺序：目标 → 规划 → 队列 → 执行 →", fs=6.6, color=GRAY)
    note(ax, 0.25, 1.04, "验证 → 汇总；虚线为失败回退路径。", fs=6.6, color=GRAY)
    save(fig, "p25-agent")


FIGURES = [
    ("p10-parallel", f_p10_parallel),
    ("p10-pipeline", f_p10_pipeline),
    ("p10-memory", f_p10_memory),
    ("p11-sft", f_p11_sft),
    ("p12-rlhf", f_p12_rlhf),
    ("p12-ppo", f_p12_ppo),
    ("p13-dpo", f_p13_dpo),
    ("p14-grpo", f_p14_grpo),
    ("p14-length", f_p14_length),
    ("p16-testtime", f_p16_testtime),
    ("p17-tools", f_p17_tools),
    ("p18-multimodal", f_p18_multimodal),
    ("p19-diffusion", f_p19_diffusion),
    ("p20-quant", f_p20_quant),
    ("p20-spec", f_p20_spec),
    ("p21-longctx", f_p21_longctx),
    ("p22-paged", f_p22_paged),
    ("p22-batching", f_p22_batching),
    ("p23-cost", f_p23_cost),
    ("p24-rag", f_p24_rag),
    ("p25-agent", f_p25_agent),
]


def main(argv: list[str]) -> None:
    want = set(argv[1:])
    todo = [f for f in FIGURES if not want or f[0] in want]
    missing = want - {f[0] for f in FIGURES}
    if missing:
        print("未知图名：", ", ".join(sorted(missing)))
    for name, fn in todo:
        fn()
        assert (FIGDIR / f"{name}.pdf").exists(), name
    print(f"完成 {len(todo)} 张")


if __name__ == "__main__":
    main(sys.argv)

