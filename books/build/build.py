#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建《大模型技术全景》系列中某一册的 PDF。

用法：
    python books/build/build.py --book books/v1-intro
    python books/build/build.py --book v1-intro
    python books/build/build.py                  # 构建全部册
    python books/build/build.py --book v2-basics --check   # 只体检，不排版
    python books/build/build.py --book v2-basics --no-opt  # 跳过图片压缩
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
BUILDDIR = BOOKS / "build"
TEMPLATE = BUILDDIR / "template" / "book.tex"
WORKROOT = BUILDDIR / "work"

EXTRA_PATH = [
    Path(r"E:\tools\TinyTeX\bin\windows"),
    Path(r"E:\tools\pandoc-3.12.1"),
    Path(r"C:\Windows\System32"),
]

# 一册必备的东西
REQUIRED_FIELDS = ("title", "subtitle", "author", "year", "pdf")


def find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for d in EXTRA_PATH:
        for suffix in (".exe", ".bat", ""):
            p = d / (name + suffix)
            if p.exists():
                return str(p)
    return None


def run(cmd, cwd: Path, quiet: bool = False) -> None:
    print("  >", " ".join(str(c) for c in cmd))
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(p) for p in EXTRA_PATH] + [env.get("PATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(cmd, cwd=str(cwd), env=env,
                          stdout=subprocess.PIPE if quiet else None,
                          stderr=subprocess.STDOUT if quiet else None,
                          text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        if quiet and proc.stdout:
            print("\n".join(proc.stdout.splitlines()[-40:]))
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(map(str, cmd))}")


# ---------------------------------------------------------------- 体检

def check_book(book: Path) -> list[str]:
    """返回问题列表；空列表表示这一册可以排版。"""
    problems: list[str] = []
    meta_path = book / "book.json"
    order_path = book / "structure.json"

    if not meta_path.exists():
        return [f"{book.name}: 缺 book.json"]
    if not order_path.exists():
        return [f"{book.name}: 缺 structure.json"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{book.name}/book.json 不是合法 JSON: {e}"]
    for f in REQUIRED_FIELDS:
        if not meta.get(f):
            problems.append(f"{book.name}/book.json 缺字段 {f}")
    if meta.get("pdf") and not meta["pdf"].endswith(".pdf"):
        problems.append(f"{book.name}/book.json 的 pdf 字段应以 .pdf 结尾")

    try:
        order = json.loads(order_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return problems + [f"{book.name}/structure.json 不是合法 JSON: {e}"]

    entries = []
    for key in ("front", "chapters", "appendix"):
        entries += list(order.get(key, []))
    if not order.get("chapters"):
        problems.append(f"{book.name}/structure.json 没有任何章节")

    images_dir = book / "images"
    referenced: set[Path] = set()
    for rel in entries:
        p = (book / rel)
        if not p.exists():
            problems.append(f"{book.name}: structure.json 里的 {rel} 不存在")
            continue
        text = p.read_text(encoding="utf-8")
        # 代码围栏配对与嵌套检查
        fences = re.findall(r"^\s*(```+|~~~+)", text, flags=re.M)
        if len(fences) % 2:
            problems.append(f"{book.name}/{rel}: 代码围栏数量为奇数，格式会错乱")
        # 标题里的危险字符
        for line in text.splitlines():
            if re.match(r"^#{1,6}\s", line) and re.search(r"[\u0000-\u001f\\\\]", line):
                problems.append(f"{book.name}/{rel}: 标题含反斜杠或控制字符 {line[:40]}")
        # 图片引用：路径必须存在，且 images/NN 与章号一致
        chap = re.match(r"chapters/ch(\d+)\.md$", rel)
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
            src = m.group(1).split()[0]
            if src.startswith(("http://", "https://")):
                continue
            target = (p.parent / src).resolve()
            img_root = images_dir.resolve()
            if not target.exists():
                problems.append(f"{book.name}/{rel}: 图片不存在 {src}")
                continue
            referenced.add(target)
            try:
                inside = target.relative_to(img_root)
            except ValueError:
                problems.append(f"{book.name}/{rel}: 图片不在 images/ 下 {src}")
                continue
            if chap:
                num = chap.group(1)
                if inside.parts and inside.parts[0].isdigit() and inside.parts[0] != num:
                    problems.append(
                        f"{book.name}/{rel}: 图片放在 images/{inside.parts[0]}/，"
                        f"与章号 {num} 不一致")

    if images_dir.exists():
        for png in images_dir.rglob("*.png"):
            if png.resolve() not in referenced and png.parent.name.isdigit():
                problems.append(f"{book.name}: 图片未被引用 {png.relative_to(book)}")
    return problems


def check_all(books: list[Path]) -> None:
    problems: list[str] = []
    seen: dict[str, str] = {}
    for book in books:
        problems += check_book(book)
        meta_path = book / "book.json"
        if meta_path.exists():
            pdf = json.loads(meta_path.read_text(encoding="utf-8")).get("pdf", "")
            if pdf in seen:
                problems.append(f"输出文件名重复：{book.name} 与 {seen[pdf]} 都是 {pdf}")
            seen[pdf] = book.name
    if problems:
        print("体检未通过：")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print(f"体检通过（{len(books)} 册）")


# ---------------------------------------------------------------- 排版

def part_to_latex(md: str) -> str:
    lines = md.split("\n")
    m = re.match(r"#\s*第(.+?)部[　 ]+(.*)", lines[0].strip())
    if not m:
        return md
    num, title = m.group(1), m.group(2).strip()
    body = "\n".join(lines[1:]).strip()
    return ("```{=latex}\n\\partpage{%s}{%s}\n```\n\n"
            "::: {.partintro}\n%s\n:::\n" % (num, title, body))


def assemble(order: dict, book: Path, images: Path) -> str:
    """正文部分（章节 + 附录）；前言等前置页由 front.tex 单独生成。"""
    parts = []
    for key in ("chapters", "appendix"):
        for rel in order.get(key, []):
            p = book / rel
            if not p.exists():
                raise SystemExit(f"structure.json 里的 {rel} 不存在")
            text = p.read_text(encoding="utf-8")
            if p.parent.name == "front" and p.name.startswith("part"):
                text = part_to_latex(text)
            parts.append(text)
    body = "\n\n".join(parts)
    body = body.replace("](../images/", "](%s/" % images.as_posix())
    return body


def fragment(src: Path, out: Path, title: str, pandoc: str) -> None:
    run([pandoc, str(src), "-f", "markdown+tex_math_dollars",
         "-t", "latex", "-o", str(out)], ROOT, quiet=True)
    head = ("\\chapter*{%s}\n\\addcontentsline{toc}{chapter}{%s}\n"
            "\\markboth{%s}{}\n\\thispagestyle{plain}\n" % (title, title, title))
    out.write_text(head + out.read_text(encoding="utf-8"), encoding="utf-8")


def build_once(pandoc: str, xelatex: str, body: str, images: Path, meta: dict,
               work: Path, tag: str) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    (work / "body.md").write_text(body, encoding="utf-8")
    tex = work / f"book{tag}.tex"
    tpl_text = TEMPLATE.read_text(encoding="utf-8")
    repl = {
        "@@IMAGES@@": images.as_posix(),
        "@@TITLE@@": meta.get("title", "大模型技术全景"),
        "@@SERIES@@": meta.get("series", "大模型技术全景"),
        "@@VOLUME@@": meta.get("volume", ""),
        "@@SUBTITLE@@": meta.get("subtitle", ""),
        "@@AUTHOR@@": meta.get("author", ""),
        "@@YEAR@@": str(meta.get("year", "")),
        "@@TOCDEPTH@@": "1" if meta.get("toc_sections") else "0",
    }
    for k, v in repl.items():
        tpl_text = tpl_text.replace(k, v)
    tpl = work / f"template{tag}.tex"
    tpl.write_text(tpl_text, encoding="utf-8")
    run([pandoc, str(work / "body.md"), "-f", "markdown+tex_math_dollars+pipe_tables+fenced_divs",
         "--top-level-division=part", "--number-sections",
         "--lua-filter", str(BUILDDIR / "boxes.lua"),
         "--template", str(tpl), "-o", str(tex)], ROOT, quiet=True)
    for _ in (1, 2):
        run([xelatex, "-interaction=nonstopmode", "-halt-on-error", tex.name], work)
    return work / f"book{tag}.pdf"


def build_book(book: Path, pandoc: str, xelatex: str, optimize: bool = True) -> None:
    name = book.name
    meta = json.loads((book / "book.json").read_text(encoding="utf-8"))
    order = json.loads((book / "structure.json").read_text(encoding="utf-8"))
    images = book / "images"
    output = ROOT / "output" / meta["pdf"]
    work = WORKROOT / name
    tag = "-" + name

    print(f"== {name}")
    body = assemble(order, book, images)
    print("[1/4] assemble markdown")
    work.mkdir(parents=True, exist_ok=True)
    front_parts = []
    for rel in order.get("front", []):
        p = book / rel
        if not p.exists():
            raise SystemExit(f"structure.json 里的 {rel} 不存在")
        text = p.read_text(encoding="utf-8")
        text = text.replace("](../images/", "](%s/" % images.as_posix())
        front_parts.append(text)
    if front_parts:
        front_md = work / "front.md"
        front_md.write_text("\n\n".join(front_parts), encoding="utf-8")
        fragment(front_md, work / "front.tex", "前言", pandoc)
    else:
        (work / "front.tex").write_text("", encoding="utf-8")
    afterword = book / "front" / "afterword.md"
    if afterword.exists():
        fragment(afterword, work / "afterword.tex", "后记", pandoc)
    else:
        (work / "afterword.tex").write_text("", encoding="utf-8")

    print("[2/4] pandoc -> LaTeX")
    pdf = build_once(pandoc, xelatex, body, images, meta, work, tag)

    print("[3/4] xelatex done, check size")
    size_mb = pdf.stat().st_size / 1024 / 1024
    if optimize and size_mb > 20:
        print(f"  PDF is {size_mb:.1f} MB, recompressing figures to JPEG ...")
        from PIL import Image
        jpg_dir = work / "img_jpg"
        jpg_dir.mkdir(exist_ok=True)
        body2 = body
        for png in sorted(images.rglob("*.png")):
            rel = png.relative_to(images)
            dst = jpg_dir / rel.with_suffix(".jpg")
            dst.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(png).convert("RGB")
            if im.width > 1200:
                im = im.resize((1200, int(im.height * 1200 / im.width)), Image.LANCZOS)
            im.save(dst, quality=82, optimize=True)
            body2 = body2.replace(png.as_posix(), dst.as_posix())
        pdf = build_once(pandoc, xelatex, body2, images, meta, work, tag + "c")
        size_mb = pdf.stat().st_size / 1024 / 1024

    output.parent.mkdir(exist_ok=True)
    shutil.copyfile(pdf, output)
    print(f"[4/4] done: {output.relative_to(ROOT)} ({size_mb:.1f} MB)")


def all_books() -> list[Path]:
    """books/ 下所有带 book.json 的册目录，按名字排序。"""
    return sorted(p for p in BOOKS.iterdir()
                  if p.is_dir() and (p / "book.json").exists())


def resolve(name: str) -> Path:
    p = Path(name)
    if p.exists():
        return p.resolve()
    cand = BOOKS / name
    if cand.exists():
        return cand
    raise SystemExit(f"找不到册：{name}（可用：{', '.join(b.name for b in all_books())}）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", help="册目录名，例如 v1-intro；不传则处理全部")
    ap.add_argument("--check", action="store_true", help="只体检，不排版")
    ap.add_argument("--no-opt", action="store_true", help="跳过超大 PDF 的图片压缩")
    args = ap.parse_args()

    books = [resolve(args.book)] if args.book else all_books()
    if not books:
        raise SystemExit("books/ 下没有带 book.json 的册")

    check_all(books)
    if args.check:
        return

    pandoc = find_tool("pandoc")
    xelatex = find_tool("xelatex")
    if not pandoc or not xelatex:
        raise SystemExit("pandoc or xelatex not found. Check EXTRA_PATH in books/build/build.py.")

    for book in books:
        build_book(book, pandoc, xelatex, optimize=not args.no_opt)


if __name__ == "__main__":
    main()
