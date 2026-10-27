#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计 Markdown 文件的中文字数（不含标点与空白）。"""
import re
import sys
from pathlib import Path

for arg in sys.argv[1:]:
    p = Path(arg)
    text = p.read_text(encoding="utf-8")
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    han = len(re.findall(r"[\u4e00-\u9fff]", body))
    print(f"{p.name}: {han} 汉字, {len(body)} 字符")
