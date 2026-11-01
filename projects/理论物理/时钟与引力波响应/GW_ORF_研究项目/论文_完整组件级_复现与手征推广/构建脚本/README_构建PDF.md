# Markdown 论文 → PDF 构建脚本

本目录的 `md2pdf.py` + `render_math.js` 把组件级论文
（`../论文_组件级完整解析解.md`，数学用标准 `$...$` / `$$...$$` LaTeX）
编译为 PDF。

- **显示公式**（`$$...$$`）用 Node + MathJax（mathjax-full）服务端渲染为 SVG，
  经 svglib 嵌入；支持 AMS 数学环境（aligned/cases 等），无需系统 LaTeX。
- **行内公式**（`$...$`）转为可读 Unicode 近似（正文阅读用）。
- **中文**用 reportlab 内置 Adobe CID 字体 STSong-Light，无需安装字体。

## 依赖
```bash
python3 -m venv .venv
.venv/bin/pip install reportlab svglib
cd <某个工作目录> && npm install marked mathjax-full
```

## 用法
当前脚本里把 Node 工作目录写死为 `/tmp/pdfbuild`（即 `npm install mathjax-full`
的目录）。构建前：
```bash
mkdir -p /tmp/pdfbuild && cp render_math.js /tmp/pdfbuild/
cd /tmp/pdfbuild && npm install mathjax-full   # 首次
.venv/bin/python md2pdf.py ../论文_组件级完整解析解.md ../论文_组件级完整解析解.pdf
```
超宽长公式会按页宽自动缩小；表格、代码块、标题、列表均支持。

## 与 paper.tex 的关系
`paper.tex`（revtex4-2，需系统 XeLaTeX + CJK 字体）是排版级正式稿；
本 Markdown/PDF 管线在没有 LaTeX 的环境下提供等价内容的可读 PDF。
