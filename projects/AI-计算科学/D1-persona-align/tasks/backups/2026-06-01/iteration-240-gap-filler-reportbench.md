# Iteration 240: gap_filler ReportBench 维度补全 — 引用相关性 + 事实可信度

## 目标
将 gap_filler 扩展到可以检测和建议 ReportBench 维度的补全内容。此前 gap_filler 只能建议 6 个自适应维度的补全，现在扩展到包括引用相关性和事实可信度。

## 执行动作

### persona_v3_gap_filler.py 扩展

1. **DIMENSION_KEYWORDS 扩展**: 新增 `引用相关性` 和 `事实可信度` 两个维度关键词列表 (各 16 个关键词)

2. **GAP_FILL_TEMPLATES 扩展**: 新增两个模板:
   - `引用相关性`: "#### 文献引用支撑" — 包含实证研究引用、理论框架引用、meta-analysis 证据
   - `事实可信度`: "#### 可验证声明与数据来源" — 包含定量声明、交叉验证、可重复性

3. **SUGGESTION_HEADINGS 扩展**: 新增 3 个标题 (跨域同构分析、文献引用支撑、可验证声明与数据来源) — 防止这些建议区块被错误提取为源上下文

## 验证

对 idea-20 运行 gap_filler --json:
```
dimension: 自适应探索 [0.27]
dimension: 引用相关性 [0.14]
dimension: 事实可信度 [0.00]
Total suggestions: 3
```

gap_filler 正确检测到了 ReportBench 维度为缺失并生成补全建议。

## 影响

- gap_filler 从 6 维度补全扩展到 8 维度补全
- ReportBench 维度现在是闭环的: 检测 (alignment_checker) → 建议 (gap_filler) → 补全 (--apply) → 再评估 (alignment_checker)
- 建议的模板设计为填充式 (citation_1, data_source_1 等占位符)，需要用户补全具体引用
- SUGGESTION_HEADINGS 扩展防止了建议区块在 --file 模式下被错误提取为源上下文
