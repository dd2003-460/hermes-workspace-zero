# LLM-assisted Review 流水线 — 浏览器渲染 + Claude 视觉分析

## 概述

通过浏览器渲染文档并截图，然后让 Claude 视觉模型直接审查输出质量。形成"产出 → 渲染 → 截图 → 审查 → 反馈"的闭环。

## 架构

```
┌──────────────┐
│  产出文档     │  Markdown / HTML / LaTeX
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  编译/渲染    │  pandoc / latexmk / 直接打开HTML
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  浏览器渲染   │  Playwright (headless Chromium)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  截图         │  PNG 全页截图
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Claude 视觉   │  Sonnet 4.5 分析截图
│  审查         │  排版/公式/图表/整体质量
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  审查报告     │  具体问题和改进建议
└──────────────┘
```

## 工具

### browser-review.js

路径: `tools/browser-review.js`

三个子命令:

```bash
# 渲染文档为截图
node tools/browser-review.js render input.html output.png

# Claude 分析截图
node tools/browser-review.js analyze output.png "[CLAUDE_API_KEY]"

# 完整流水线
node tools/browser-review.js pipeline input.html "[CLAUDE_API_KEY]"
```

### 环境要求

- Playwright + Chromium (已安装并验证)
- Node.js 18+
- Anthropic API Key (可选，用于视觉分析)

## 应用场景

### 1. LaTeX 文档审查

```bash
# 编译 LaTeX
pdflatex manuscript.tex
bibtex manuscript.aux
pdflatex manuscript.tex
pdflatex manuscript.tex

# HTML 转换 (可选)
pandoc manuscript.pdf -t html -o manuscript.html

# 截图审查
node tools/browser-review.js pipeline manuscript.html "[API_KEY]"
```

### 2. arXiv 提交前检查

```bash
# 检查最终排版效果
node tools/browser-review.js render final-paper.html paper-review.png

# Claude 审查
node tools/browser-review.js analyze paper-review.png "[API_KEY]"
```

### 3. 在线文档审查

```bash
# 打开远程 URL
node -e "
const { renderToFile } = require('./tools/browser-review.js');
renderToFile('https://arxiv.org/abs/2026.xxxxx', 'arxiv-paper-review.png');
"
```

## 审查标准

Claude 应该按以下维度审查:

| 维度 | 检查项 |
|------|--------|
| 排版 | 边距、行距、段落间距、段落对齐 |
| 公式 | LaTeX 渲染是否正确、公式编号、跨页断裂 |
| 图表 | 清晰度、标注可读性、与正文引用对应 |
| 表格 | 表格线、文字换行、跨页处理 |
| 整体 | 视觉层次、一致性、专业度 |

## Ralph Loop 集成

### 集成到 2-loop 执行层

```
2-loop 验证阶段:
  |
  +-- 产出草稿 → LaTeX/HTML/PDF
  |
  +-- [新] 浏览器渲染 + Claude 视觉审查
  |    自动检查排版质量
  |
  +-- 根据审查反馈修改
  |
  +-- 2-loop 置信度评估 (含视觉质量评分)
```

### 自动化审查 (可选)

设置定时审查:

```bash
# 监控特定目录，有新文档时自动审查
watch -n 3600 'node tools/browser-review.js pipeline /path/to/docs/*.html "[API_KEY]"'
```

## 与 T11 配合

T11 (arXiv 搜索) + T10 (浏览器审查) 形成完整管线:

```
T11: 搜索相关论文 → 下载/获取 PDF
T10: 渲染论文 → Claude 视觉审查 → 提取好/坏的设计模式
```

这样可以自动分析 arXiv 上的优秀论文排版，提取样式参考。

## 故障处理

| 问题 | 解决方案 |
|------|----------|
| Playwright 超时 | 增加 --delay 参数 |
| 公式渲染慢 | 增加延迟或使用 MathJax 静态渲染 |
| API Key 无效 | 检查 ANTHROPIC_API_KEY 环境变量 |
| PDF 截图质量差 | 使用 PDF.js 转换为高分辨率 SVG |
