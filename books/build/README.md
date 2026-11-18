# 构建说明

书稿是 Markdown，PDF 由 Pandoc + XeLaTeX 生成。工程按册组织，`books/v1-intro` … `books/v8-*` 同构，每册独立成书、共用一套构建脚本。

## 依赖

| 工具 | 用途 | 默认查找位置 |
|---|---|---|
| Python 3 | 运行脚本 | PATH、`%LOCALAPPDATA%\Programs\Python\Python312` |
| Pandoc 3.x | Markdown → LaTeX | PATH、`E:\tools\pandoc-3.12.1` |
| TinyTeX / TeX Live | XeLaTeX 编译 | PATH、`E:\tools\TinyTeX\bin\windows` |

换机器时改 `books/build/build.py` 顶部的 `EXTRA_PATH`。

## 生成 PDF

```bat
build.bat                 全部册
build.bat v2-basics       只构建基础篇
build.bat check           只体检，不排版
build.bat figures         重画全部插图
build.bat figures 03      只重画第 3 章插图
```

等价于：

```bat
python books/build/build.py
python books/build/build.py --book v2-basics
python books/build/build.py --check
python books/build/build.py --book v2-basics --no-opt   (跳过图片压缩)
```

输出在 `output/<pdf>`，文件名取自该册 `book.json` 的 `pdf` 字段，所以四册不会互相覆盖。PDF 超过 20 MB 时脚本会自动把插图压成 JPEG 再排一次；字体子集化由 XeLaTeX 默认完成，书签来自 `hyperref`。

每本先体检再排版：`structure.json` 里的文件是否都在、图片是否存在、图片所在目录是否与章号一致、代码围栏是否配对、标题里有没有会打断编译的字符、各册输出文件名是否重复。任何一项不过就停下，不带着错往下排。

## 新增一册

1. 建目录 `books/v5-xxx/`，放入 `book.json`、`structure.json`、`front/preface.md`、`chapters/`、`images/`。
2. `book.json` 至少要写 `title`、`subtitle`、`author`、`year`、`pdf`，`toc_sections` 控制目录是否列到节。
3. 跑 `python books/build/make_site.py` 生成该册的 `README.md`、`_sidebar.md` 和根侧栏。
4. `build.bat v5-xxx` 出 PDF，把新册写进根 `README.md` 的表格。

## 目录约定

```text
llm-book/
├── index.html              站点入口，全系列共用
├── _sidebar.md             系列导航（由 make_site.py 生成）
├── _coverpage.md           封面页
├── README.md               首页：各册简介、在线阅读、PDF 下载
├── build.bat               总入口
├── build-<册名>.bat        单册入口
├── books/
│   ├── build/              构建、体检、站点生成，全系列共用
│   ├── code/               插图脚本 figs_v1.py、figs_v2.py 与 figstyle.py
│   ├── appendix/           全系列共用的附录
│   └── <册名>/
│       ├── book.json       书名、副标题、作者、输出文件名
│       ├── structure.json  该册的正文顺序（唯一来源）
│       ├── README.md       该册首页
│       ├── _sidebar.md     该册侧栏
│       ├── front/          前言、后记
│       ├── chapters/       ch01.md …
│       └── images/         插图，按章分子目录；封面 cover.jpg、封底 backcover.jpg
└── output/                 各册 PDF
```

- 一份正文只存一处，站点侧栏只放链接，不复制 Markdown。
- 章节顺序以 `structure.json` 为准，不看文件名排序。
- 插图按章分目录（`images/03/` 对应 `chapters/ch03.md`），构建前的体检会核对这一点。
- 写作笔记、旧稿、下载的论文放 `_private/`（已在 `.gitignore` 里）。

## 插图

```bat
python books/code/figs_v1.py         全部重画第一卷
python books/code/figs_v2.py 03 07   只画第二卷的第 3、7 章
```

脚本直接输出到 `books/<册名>/images/NN/xxx.png`，也就是书稿里引用的文件。样式统一放在 `books/code/figstyle.py`。

## 站点

根目录是 docsify 站点：`index.html`、`_sidebar.md`、`_coverpage.md`、`README.md`、`.nojekyll`。
根侧栏只做系列导航，每册目录下各有自己的 `_sidebar.md`，docsify 会就近取用。

GitHub Pages 选 `main` 分支的 `/ (root)`。新增或调整章节后跑一次 `make_site.py`，侧栏与各册首页的目录会跟着 `structure.json` 更新。
