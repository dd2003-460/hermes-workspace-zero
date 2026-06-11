# Iteration 236: ReportBench 维度实现 — citation relevance + factual faithfulness 加入 alignment_checker

## 目标
基于 iteration 233 的研究发现 (ReportBench)，将两个新评估维度 (citation relevance + factual faithfulness) 实际落地到对齐度检测工具中。

## 执行动作

### persona_v3_alignment_checker.py 扩展
1. **新增关键词列表:**
   - `CITATION_RELEVANCE_KEYWORDS` (22 个加权关键词，weight 2.0/1.0/0.5 三级)
   - `FACTUAL_FAITHFULNESS_KEYWORDS` (28 个加权关键词，weight 2.0/1.0/0.5 三级)

2. **新增评分函数:**
   - `compute_citation_relevance(text)` — 引用相关性评分
   - `compute_factual_faithfulness(text)` — 事实可信度评分

3. **更新 `compute_alignment_score()`:**
   - 权重从 50/10/20/20 改为 40/10/15/15/10/10
   - 加入 ReportBench 维度 (10% + 10%)

4. **更新 `format_report()`:**
   - 新增 "ReportBench 评估维度" 章节，显示维度 7-8

5. **更新 `main()`:**
   - 调用新评分函数，传递到 alignment_score 和 format_report
   - JSON 输出包含 citation_relevance 和 factual_faithfulness
   - `--show-sources` 显示 ReportBench 检测源

### 验证
- idea-20 评估: 总体 54.02/100 (从 67.81 下降，因权重重新分配)
- 引用相关性: 0.11 (低 — 文件缺少文献引用)
- 事实可信度: 0.00 (无 — 文件无可验证外部声明)

## 影响
- alignment_checker 从 6 维度扩展到 8 维度
- ReportBench 的 citation relevance + factual faithfulness 从研究论文落地为可执行的评估工具
- 新维度暴露了现有 idea 文件的两个系统性不足: 缺乏文献引用 + 缺乏可验证声明
- 加权评分系统保持不变 (三级权重 2.0/1.0/0.5)
