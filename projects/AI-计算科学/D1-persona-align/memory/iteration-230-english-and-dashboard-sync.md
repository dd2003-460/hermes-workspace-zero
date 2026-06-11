# Iteration 230: EN checker + dashboard 加权关键词同步

## 目标
将 weighted keyword matching 同步到所有三个评估工具 (中文 checker → EN checker → dashboard)。

## 执行动作

### 同步
1. persona_v3_alignment_checker_en.py — DIMENSION_KEYWORDS 改为 (keyword, weight) 元组, detect_dimensions 改为 weighted sum
2. persona_v3_dashboard.py — 同上, 加权匹配替换 flat matching

### 验证
- EN checker: 语法验证通过 (persona-v3-prompt.txt 中文文件评分低, 正常)
- Dashboard: detect_dimensions 逻辑验证通过, 返回加权分数

### 权重设计
- 2.0x: 核心术语 (dimension name, fundamental concept)
- 1.0-1.5x: 相关术语 (technical terms, synonyms)
- 0.5x: 表达变体 (alternative phrasings, less direct)

## 影响
- 三个评估工具统一使用加权关键词匹配
- 符合"四个工具统一评分逻辑"的维护原则
- 从 flat keyword matching 到 category-based retrieval 的闭环完成
