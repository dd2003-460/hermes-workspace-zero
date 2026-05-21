# TASKS — D1-persona-align

## 任务状态

| ID | 任务 | 状态 | 优先级 |
|----|------|------|--------|
| T1 | 搜索开源人格对齐项目（PersonaTransfer、CharacterAI、LitGPT-persona等） | ✅ 完成 (report: T1-research-report.md) | P0 |
| T2 | 分析成璐的语言风格样本（raw.md + 历史对话） | ✅ 完成 (5 patterns + 6 metrics) | P0 |
| T3 | 设计prompt injection方案（ephemeral_system_prompt） | ✅ 完成 (hybrid injection + full system prompt) | P0 |
| T4 | 对比prompt激发vs微调的稳定性 | ✅ 完成 (级联架构推荐 + 衰减曲线) | P1 |
| T5a | Prompt最小样本量验证 | ✅ 完成 (scorer: 6 metrics, 3 scenarios) | P1 |
| T5b | LoRA最小样本量验证 | ✅ 完成 (104 samples > 80 predicted min) | P1 |
| T6 | 实现Hermes personality entry | ✅ 完成 (chenglu personality deployed) | P2 |
| T7 | Scorer calibration + synthetic data v5 | ✅ 完成 (scorer 100%/16%/80% discrimination) | P1 |
| T8 | Synthetic data v6 — question_ratio breakthrough | ✅ 完成 (q_ratio=0.1575 first 100% pass, English contamination found & fixed) | P1 |
| T9 | Anti-thinking prompt patch (v6.1) | ✅ 完成 (English leakage 660→0 chars, 101 clean samples) | P1 |
| T10 | v7 minimal prompt + large batch generation | ✅ 完成 (90% pass, 113 clean samples, exceeds T5b min) | P1 |
| T11 | LoRA fine-tuning pipeline end-to-end | ✅ 完成 (5 iters, loss decreasing, inference works) | P0 |

---

## T1: 搜索开源人格对齐项目

**目标**：找出所有相关的开源项目和技术方案

**验收标准**：
- 列出至少3个开源项目及其核心方法
- 分析每种方法的优缺点
- 给出对本项目的适用性评估

**参考资料**：
- GitHub搜索关键词：persona transfer, character AI, style transfer LLM
- 相关论文：人格迁移、few-shot personality imitation

**状态**: 待开始

---

## T2: 分析成璐的语言风格样本

**目标**：建立成璐的语言/思维/行为风格档案

**验收标准**：
- 从raw-human/raw.md和已有对话中提取特征
- 格式：语言特征（词汇偏好、句式特点）、思维特征（推理模式、分析框架）、行为特征（决策风格、沟通方式）
- 输出格式：结构化JSON或Markdown

**参考资料**：
- `projects/D1-academic-AI/raw/raw-human/raw.md`
- `AGENTS.md` 中的"约束与偏好"章节

**状态**: 待开始

---

## T3: 设计prompt injection方案

**目标**：设计将AGENTS.md注入Hermes system prompt的方案

**验收标准**：
- 研究Hermes的`ephemeral_system_prompt`机制
- 给出配置方案（config.yaml修改）
- 验证方案有效性（启动Hermes测试）

**参考资料**：
- `~/.hermes/config.yaml` 中的`personalities`配置
- `~/.hermes/hermes-webui/api/streaming.py` 中的system prompt注入逻辑

**状态**: ✅ 完成 (详见 T3-prompt-injection-scheme.md, hybrid injection recommended)

---

## T4: 对比prompt激发vs微调的稳定性

**目标**：通过实验对比两种方案的对齐稳定性

**验收标准**：
- prompt激发方案：测试不同上下文长度下的对齐保持率
- 微调方案：使用成璐样本微调，测试输出一致性
- 对比报告：两种方案的优劣势、适用场景

**参考资料**：
- 开源人格对齐项目的实验方法
- LitGPT的fine-tuning工具

**状态**: 待开始

---

## T5: 验证最小对齐样本量

**目标**：确定最少需要多少样本才能稳定激发目标人格

**验收标准**：
- 设计实验：从1条到N条样本，观察对齐保持率
- 找出临界点（低于该样本量对齐率骤降）
- 给出具体建议（最少需要多少条raw记录）

**参考资料**：
- Few-shot学习中的样本效率研究
- 人格迁移项目中的样本量讨论

**状态**: 完成 (split into T5a + T5b)

---

## T5a: Prompt最小样本量验证 (fidelity scorer)

**目标**：建立自动化工具验证persona对齐保真度

**完成内容**:
- 6-metric automated scorer: question_ratio, cross_domain, uncertainty, block_structure, metaphor_ratio, lexical_overlap
- Validated against 3 scenarios: raw.md baseline (100% PASS), formal text (8.33% FAIL), persona-style (83.3% PASS)
- Tool: `persona_fidelity_scorer.py`

**验收标准**:
- [x] Scorer correctly identifies persona style vs formal style
- [x] Scorer handles Qwen thinking process stripping
- [x] Score threshold established: >70% = acceptable persona alignment

**状态**: ✅ 完成

---

## T5b: LoRA最小样本量验证

**目标**：确定LoRA微调的最少样本量

**完成内容**:
- Extracted 50 persona thoughts from raw.md
- Generated 42 synthetic persona dialogues (Hermes API, batch + single-call)
- Total: 92 samples (exceeds T5b predicted minimum of 80)
- Dataset: `raw/lora_data/lora_trainset.jsonl`

**关键发现**:
- Synthetic data quality: 66.67% avg fidelity (above 50%, below 70% target)
- Core persona markers: cross_domain (93%), uncertainty (100%)
- Scorer issues: question_ratio extreme swings (0.06-0.79), block_structure artifact

**状态**: ✅ 完成

---

## T6: 实现Hermes personality entry

**目标**：在Hermes config中创建"成璐分身"personality

**验收标准**：
- 在`~/.hermes/config.yaml`中添加`chenglu` personality
- 包含AGENTS.md的核心约束和成璐的思维特征
- 测试Hermes使用该personality工作

**参考资料**：
- `~/.hermes/config.yaml` 中的`personalities`配置
- 已有的`helpful`、`concise`等personality示例

**状态**: 待开始
