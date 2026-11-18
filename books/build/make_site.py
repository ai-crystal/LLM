#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从各册的 book.json / structure.json 生成站点导航。

生成物：
    books/<册名>/README.md    该册首页（简介 + 目录 + PDF 下载）
    books/<册名>/_sidebar.md  该册侧栏
    _sidebar.md               系列导航（各册入口 + 下载）

章标题取自每章正文的第一个标题，所以改标题后重跑一次即可，不需要在两处维护目录。

链接写法：
    _sidebar.md 只给 docsify 用，一律写站点绝对路径（/books/...）；
    各册 README.md 同时要在 GitHub 网页端可读，所以写同级相对路径。

用法：
    python books/build/make_site.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"


def first_heading(md: Path) -> str:
    """取正文第一个标题（优先二级，没有就用一级）。"""
    lines = md.read_text(encoding="utf-8").splitlines()
    for level in (2, 1):
        marker = "#" * level + " "
        for line in lines:
            if line.startswith(marker):
                return line[len(marker):].strip()
    return md.stem


def load(book: Path) -> tuple[dict, dict]:
    meta = json.loads((book / "book.json").read_text(encoding="utf-8"))
    order = json.loads((book / "structure.json").read_text(encoding="utf-8"))
    return meta, order


def books() -> list[Path]:
    return sorted(p for p in BOOKS.iterdir()
                  if p.is_dir() and (p / "book.json").exists())


def chapter_no(rel: str) -> str:
    m = re.search(r"ch(\d+)", rel)
    return str(int(m.group(1))) if m else ""


def write_book(book: Path) -> None:
    meta, order = load(book)
    name = book.name
    chaps = order.get("chapters", [])
    front = order.get("front", [])

    # ---------- 侧栏（docsify 专用，写站点绝对路径） ----------
    side = ["- [系列首页](/README.md)",
            f"- [本册首页](/books/{name}/README.md)",
            "",
            f"- **{meta['volume']}**"]
    for rel in front:
        side.append(f"  - [{first_heading(book / rel)}](/books/{name}/{rel})")
    for rel in chaps:
        side.append(f"  - [第{chapter_no(rel)}章 {first_heading(book / rel)}]"
                    f"(/books/{name}/{rel})")
    if order.get("appendix"):
        side += ["", "- **附录**"]
        for rel in order["appendix"]:
            side.append(f"  - [{first_heading(book / rel)}](/books/{name}/{rel})")
    side += ["", f"- [下载本册 PDF](/output/{meta['pdf']})"]
    (book / "_sidebar.md").write_text("\n".join(side) + "\n", encoding="utf-8")

    # ---------- 该册首页（GitHub 也能读，写同级相对路径） ----------
    rows = ["| 章 | 标题 |", "|---|---|"]
    for rel in chaps:
        rows.append(f"| {chapter_no(rel)} | "
                    f"[{first_heading(book / rel)}]({rel}) |")
    readme = (
        f"# {meta['volume']}：{meta['subtitle']}\n\n"
        f"> {meta['series']} · {meta['author']} · {meta['year']}\n\n"
        f"共 {len(chaps)} 章，[下载本册 PDF](../../output/{meta['pdf']})。\n\n"
        "## 目录\n\n"
        + "\n".join(rows) + "\n\n"
        "[返回系列首页](../../README.md)\n"
    )
    (book / "README.md").write_text(readme, encoding="utf-8")


def write_root_sidebar() -> None:
    lines = ["- [首页](/README.md)", "", "- **各册**"]
    for book in books():
        meta, _ = load(book)
        lines.append(f"  - [{meta['volume']}：{meta['subtitle']}]"
                     f"(/books/{book.name}/README.md)")
    lines += ["", "- **下载**"]
    for book in books():
        meta, _ = load(book)
        lines.append(f"  - [{meta['volume']} PDF](/output/{meta['pdf']})")
    (ROOT / "_sidebar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for book in books():
        write_book(book)
        print("site:", book.name)
    write_root_sidebar()
    print("site: _sidebar.md")


if __name__ == "__main__":
    main()
