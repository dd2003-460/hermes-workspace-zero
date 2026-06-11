# Iteration 237: ReportBench 维度同步 — EN checker + dashboard 扩展

## 目标
迭代 236 只在中国版 alignment_checker 中实现了 ReportBench 维度。本迭代将这两个维度同步到 EN checker 和 dashboard，确保三个工具一致。

## 执行动作

### persona_v3_alignment_checker_en.py 同步
1. 新增 `CITATION_RELEVANCE_KEYWORDS` (25 个英文关键词)
2. 新增 `FACTUAL_FAITHFULNESS_KEYWORDS` (30 个英文关键词)
3. 新增 `detect_citation_relevance()` 和 `detect_factual_faithfulness()` 函数
4. 更新 `compute_alignment_score()` 接受 citation_rel 和 fact_faul 参数
5. 更新 `print_report()` 显示 ReportBench 维度
6. 更新 `main()` 计算和输出 ReportBench 分数

### persona_v3_dashboard.py 同步
1. 新增 `CITATION_RELEVANCE_KEYWORDS` 和 `FACTUAL_FAITHFULNESS_KEYWORDS` (中英双语)
2. 新增 `detect_citation_relevance()` 和 `detect_factual_faithfulness()` 函数
3. 更新 `compute_alignment_score()` 接受 ReportBench 参数
4. 更新 `scan_file()` 计算和包含 ReportBench 分数到结果中

## 验证
- EN checker: idea-20 的 citation relevance 和 factual faithfulness 均为 0.0 (EN keywords 不匹配中文文本 — 正确行为)
- 三个工具现在一致支持 8 维度评估系统

## 影响
- persona-v3 评估工具一致性: 中文版 + EN 版 + dashboard 全部包含 ReportBench 维度
- EN checker 的英文关键词专为英文文本设计 (chinese text → 0 是预期行为)
- dashboard 扫描结果现在包含 citation_relevance 和 factual_faithfulness 字段
