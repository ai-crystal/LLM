#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 book/code/chNN/out/*.pdf 转成 book/images/NN/*.png。

书稿 Markdown 引用的是 PNG（GitHub 网页端可直接显示），
PDF 由各章绘图脚本生成，只作为中间产物，不进入仓库。

用法：python book/build/images.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "book" / "images"


def convert(pdf: Path, dst: Path, dpi: int = 220, max_width: int = 1500) -> None:
    doc = pymupdf.open(pdf)
    pix = doc[0].get_pixmap(dpi=dpi, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    if img.width > max_width:
        img = img.resize((max_width, int(img.height * max_width / img.width)), Image.LANCZOS)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=128)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, optimize=True)
    print(f"  {pdf.relative_to(ROOT)} -> {dst.relative_to(ROOT)} ({dst.stat().st_size // 1024} KB)")


def main() -> None:
    force = "--force" in sys.argv
    count = 0
    for ch_dir in sorted((ROOT / "book" / "code").glob("ch*")):
        out = ch_dir / "out"
        if not out.is_dir():
            continue
        n = ch_dir.name[2:]
        for pdf in sorted(out.glob("*.pdf")):
            short = re.sub(r"^p\d+-", "", pdf.stem)
            dst = IMAGES / n / f"{short}.png"
            if dst.exists() and not force:
                continue
            convert(pdf, dst)
            count += 1
    print(f"done: {count} images")


if __name__ == "__main__":
    main()
