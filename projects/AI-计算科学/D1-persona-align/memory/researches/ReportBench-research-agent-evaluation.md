# ReportBench: Evaluating Deep Research Agents via Academic Survey Tasks

## 来源
Li, Zeng, Cheng, Jia, et al. (arXiv)

## 核心问题
如何评估 deep research agents 在学术调研任务中的输出质量? 传统 benchmark (如 MMLU, GSM8K) 不覆盖研究任务.

## 方案
系统化工具: 测量 citation relevance (引用相关性) 和 factual faithfulness (事实可信度). agent-based automated framework 验证未引用声明的外部来源.

## 关键发现
1. **citation relevance 评估** — agent 生成的引用必须与研究问题相关
2. **factual faithfulness 评估** — 声称必须可通过外部来源验证
3. **commercial research tools 仍有不足** — 缺乏 comprehensive depth 和 consistency

## 与 persona-v3 的关联

### 直接应用
1. **gap_filler 验证** — gap_filler 生成的补全建议是否符合 citation relevance? factual faithfulness?
2. **alignment_checker 扩展** — 当前 alignment_checker 只评估关键词覆盖, ReportBench 的思路可扩展:
   - 评估 persona-v3 分析中的引用相关性
   - 评估分析中的事实声明是否可验证
3. **research quality 评估** — persona-v3 生成的分析 (idea 分析文件) 可以被 ReportBench 评估

### 方法论借鉴
- ReportBench 的 "citation relevance + factual faithfulness" 是两个新的评估维度
- 可以添加到 alignment_checker 的 verification patterns 中
- 也可以作为 gap_filler 的补充建议质量评估

## 关键引用
> "proposes a systematic evaluation tool for measuring citation relevance and factual faithfulness in reports"
> "framework provides an agent-based automated framework to validate non-cited claims against external sources"
