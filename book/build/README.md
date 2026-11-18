# 构建说明

书稿是 Markdown，PDF 由 Pandoc + XeLaTeX 生成。工程按卷组织，`book/v1-intro` … `book/v8-multimodal` 同构，每卷独立成书。

## 依赖

| 工具 | 用途 | 默认查找位置 |
|---|---|---|
| Python 3 | 运行脚本 | PATH、`%LOCALAPPDATA%\Programs\Python\Python312` |
| Pandoc 3.x | Markdown → LaTeX | PATH、`E:\tools\pandoc-3.12.1` |
| TinyTeX / TeX Live | XeLaTeX 编译 | PATH、`E:\tools\TinyTeX\bin\windows` |

换机器时改 `book/build/build.py` 顶部的 `EXTRA_PATH`。

## 生成 PDF

```bat
python book\build\build.py --vol v2-basics   :: 只构建一卷
python book\build\build.py                   :: 构建 book\ 下全部已成稿的卷
build.bat                                     :: 同上（全部卷）
build-v2-basics.bat                           :: 单卷快捷方式
```

输出到 `output/<卷名>.pdf`，例如 `output/v2-basics.pdf`。脚本会检查体积，超过 20 MB 时自动把插图转成压缩 JPEG 再编译一次。

新增一卷只要建 `book/vN-xxx/`，放入 `meta.json`、`manifest.txt`、`front.md`、`chapters/`、`images/`，`build.py` 会自动发现它。

## 重画插图

整卷的插图脚本在 `book/code/figs_vN.py`（单文件，`main` 里按编号分发）：

```bat
python book\code\figs_v2.py        :: 全部重画
python book\code\figs_v2.py 03 07  :: 只画指定编号
```

脚本直接输出到 `book/vN-xxx/images/NN/xxx.png`，也就是书稿里引用的文件，不需要中间格式转换。

## 目录约定

- `book/vN-xxx/chapters/chNN.md`：正文，图片用 `../images/NN/xxx.png`
- `book/vN-xxx/front.md`：该卷前言
- `book/vN-xxx/manifest.txt`：卷内正文顺序
- `book/vN-xxx/meta.json`：书名、副标题、输出文件名
- `book/vN-xxx/images/`：插图 PNG（含 `cover/`）
- `book/code/figs_vN.py`：该卷插图代码，共用 `figstyle.py`
- `book/appendix/`：各卷共用的附录（论文一览、术语表）
- `book/build/`：构建脚本与 LaTeX 模板
- `_private/`：写作笔记、旧单卷稿、下载的论文（不进仓库）

## 站点

根目录是 docsify 站点：`index.html`、`_sidebar.md`、`_coverpage.md`、`README.md`、`.nojekyll`。
GitHub Pages 选择 `main` 分支的 `/ (root)` 即可。侧栏与首页目录按卷分组，新增一卷时同步改 `_sidebar.md`。
