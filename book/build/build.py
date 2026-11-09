#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建《大模型技术全景》系列中某一卷的 PDF。

用法：
    python book/build/build.py --vol v1-intro
    python book/build/build.py            # 旧的单卷合订本
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
BOOK = ROOT / "book"
WORK = BOOK / "build" / "work"
TEMPLATE = BOOK / "build" / "template" / "book.tex"

EXTRA_PATH = [
    Path(r"E:\tools\TinyTeX\bin\windows"),
    Path(r"E:\tools\pandoc-3.12.1"),
    Path(r"C:\Windows\System32"),
]


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


def part_to_latex(md: str) -> str:
    lines = md.split("\n")
    m = re.match(r"#\s*第(.+?)部[　 ]+(.*)", lines[0].strip())
    if not m:
        return md
    num, title = m.group(1), m.group(2).strip()
    body = "\n".join(lines[1:]).strip()
    return ("```{=latex}\n\\partpage{%s}{%s}\n```\n\n"
            "::: {.partintro}\n%s\n:::\n" % (num, title, body))


def assemble(manifest: Path, base: Path, images: Path) -> str:
    parts = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = base / line
        if not p.exists():
            raise SystemExit(f"manifest entry missing: {p}")
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


def build_once(pandoc: str, xelatex: str, body: str, images: Path, meta: dict, tag: str) -> Path:
    (WORK / "body.md").write_text(body, encoding="utf-8")
    tex = WORK / f"book{tag}.tex"
    tpl_text = TEMPLATE.read_text(encoding="utf-8")
    repl = {
        "@@IMAGES@@": images.as_posix(),
        "@@TITLE@@": meta.get("title", "大模型技术全景"),
        "@@SERIES@@": meta.get("series", "大模型技术全景"),
        "@@VOLUME@@": meta.get("volume", "大模型技术全景"),
        "@@SUBTITLE@@": meta.get("subtitle", "从 Transformer 到智能体时代的架构、训练与推理"),
    }
    for k, v in repl.items():
        tpl_text = tpl_text.replace(k, v)
    tpl = WORK / f"template{tag}.tex"
    tpl.write_text(tpl_text, encoding="utf-8")
    run([pandoc, str(WORK / "body.md"), "-f", "markdown+tex_math_dollars+pipe_tables+fenced_divs",
         "--top-level-division=part", "--number-sections",
         "--lua-filter", str(BOOK / "build" / "boxes.lua"),
         "--template", str(tpl), "-o", str(tex)], ROOT, quiet=True)
    for _ in (1, 2):
        run([xelatex, "-interaction=nonstopmode", "-halt-on-error", tex.name], WORK)
    return WORK / f"book{tag}.pdf"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", help="卷目录名，例如 v1-intro")
    args = ap.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    pandoc = find_tool("pandoc")
    xelatex = find_tool("xelatex")
    if not pandoc or not xelatex:
        raise SystemExit("pandoc or xelatex not found. Check EXTRA_PATH in book/build/build.py.")

    if args.vol:
        vol = BOOK / args.vol
        meta = json.loads((vol / "meta.json").read_text(encoding="utf-8"))
        manifest = vol / "manifest.txt"
        base = vol
        images = vol / "images"
        output = ROOT / "output" / meta.get("output", f"{args.vol}.pdf")
        front = vol / "front.md"
        afterword = vol / "afterword.md"
        tag = "-" + args.vol
    else:
        meta = {}
        manifest = BOOK / "build" / "manifest.txt"
        base = BOOK
        images = BOOK / "images"
        output = ROOT / "output" / "llm-book.pdf"
        front = BOOK / "front" / "preface.md"
        afterword = BOOK / "front" / "afterword.md"
        tag = ""

    body = assemble(manifest, base, images)
    print("[1/4] assemble markdown")
    fragment(front, WORK / "front.tex", "前言", pandoc)
    if afterword.exists():
        fragment(afterword, WORK / "afterword.tex", "后记", pandoc)
    else:
        (WORK / "afterword.tex").write_text("", encoding="utf-8")

    print("[2/4] pandoc -> LaTeX")
    pdf = build_once(pandoc, xelatex, body, images, meta, tag)

    print("[3/4] xelatex done, check size")
    size_mb = pdf.stat().st_size / 1024 / 1024
    if size_mb > 20:
        print(f"  PDF is {size_mb:.1f} MB, recompressing figures to JPEG ...")
        from PIL import Image
        jpg_dir = WORK / "img_jpg"
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
        pdf = build_once(pandoc, xelatex, body2, images, meta, tag + "c")
        size_mb = pdf.stat().st_size / 1024 / 1024

    output.parent.mkdir(exist_ok=True)
    shutil.copyfile(pdf, output)
    print(f"[4/4] done: {output} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
