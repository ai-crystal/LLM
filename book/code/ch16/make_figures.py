# -*- coding: utf-8 -*-
"""第 16 章插图。

运行： python book/code/ch16/make_figures.py
输出： 本目录 out/ 下的 PDF，再由 book/build/images.py 转成 PNG。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "lib"))

import figures_d as fd

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def _save(fig, name: str) -> None:
    """把图写到本目录 out/，文件名保持原编号。"""
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.1)
    import matplotlib.pyplot as plt
    plt.close(fig)


fd.save = _save


if __name__ == "__main__":
    fd.f_p16_map()
    fd.f_p16_cost()
