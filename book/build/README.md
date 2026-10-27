# 构建说明

书稿是 Markdown，PDF 由 Pandoc + XeLaTeX 生成。

## 依赖

| 工具 | 用途 | 默认查找位置 |
|---|---|---|
| Python 3 | 运行脚本 | PATH、`%LOCALAPPDATA%\Programs\Python\Python312` |
| Pandoc 3.x | Markdown → LaTeX | PATH、`E:\tools\pandoc-3.12.1` |
| TinyTeX / TeX Live | XeLaTeX 编译 | PATH、`E:\tools\TinyTeX\bin\windows` |

换机器时改 `book/build/build.py` 顶部的 `EXTRA_PATH`。

## 生成 PDF

```bat
build.bat
```

等价于：

```bat
python book\build\build.py
```

输出 `output/llm-book.pdf`。脚本会检查体积，超过 20 MB 时自动把插图转成压缩 JPEG 再编译一次。

## 重画插图

每章的绘图脚本在 `book/code/chNN/make_figures.py`，运行后在该目录的 `out/` 下生成 PDF：

```bat
python book\code\ch16\make_figures.py
python book\build\images.py
```

`images.py` 把 `out/*.pdf` 转成 `book/images/NN/*.png`，也就是书稿里引用的文件。

## 目录约定

- `book/chapters/chNN.md`：正文，图片用 `../images/NN/xxx.png`
- `book/front/`：前言、部扉页、后记
- `book/appendix/`：附录
- `book/images/NN/`：插图 PNG
- `book/code/chNN/`：该章插图代码
- `book/build/`：构建脚本与 LaTeX 模板

## 站点

根目录是 docsify 站点：`index.html`、`_sidebar.md`、`_coverpage.md`、`README.md`、`.nojekyll`。
GitHub Pages 选择 `main` 分支的 `/ (root)` 即可。
