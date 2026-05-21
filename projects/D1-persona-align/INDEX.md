# D1-persona-align — AI人格对齐研究

**状态**: 复杂推理 eval 已完成，方法论提示 > persona 提示，LoRA 微调需验证推理能力是否受损
**创建**: 2026-05-18
**最近更新**: 2026-05-21 (Iteration 38: 复杂推理 eval — 测分析能力而非知识，4 种策略对比)

---

## 项目目标

### 顶层目标：自主人格研究体

不是"模仿语气"，而是创造一个**完整的人格自主体**：
- **自主提问**：能像成璐一样提出有深度、跨域、形式化的问题
- **自主研究**：能规划并执行调研任务，主动使用工具（搜索、浏览器、代码执行）
- **多路径探索**：遇到瓶颈时主动考虑替代方案，不依赖外部指令推进
- **风格一致**：语言、思维、行为三者对齐（不仅是表面文风）

### 核心工程问题：Token 效率最大化

固定模型大小的前提下，如何用最小成本获得最大人格对齐 + 分析能力？

子问题：
1. **prompt vs 微调的效率边界**：哪些能力用 prompt 即可实现，哪些必须微调？
2. **级联架构设计**：小模型判断+大模型推理？或者 prompt 增强小模型？
3. **最小有效样本量**：低于该阈值 → 能力骤降；高于该阈值 → 边际递减
4. **评估体系**：trivial 问题（"自由意志"）不能区分能力，需要用复杂问题

### 关键对齐特征（成璐）

**语言**：中文优先，简洁直接，少空话多证据

**思维**：
- 贝叶斯闭环：先验→证据→后验→新先验
- 信息论统一框架：语言/数学/物理/社会都是同一信息处理机制的不同信道
- 直觉是高维推理的压缩，追问"你说的意思是…？"而不是包装
- 概率是动力学下的信息抹除（不是 fundamental 的）

**行为**：
- 自主推进，不等指令
- 过程可见，做了就说做了
- 完整考虑各种方法，不依赖单一路径
- 完成是最低门槛，顶刊级质量才是标准

---

## 进度

| 任务 | 状态 | 产出 |
|------|------|------|
| T1: 开源项目搜索 | ✅ 完成 | T1-research-report.md (9 projects, 技术路线评估) |
| T2: 语言风格分析 | ✅ 完成 | persona-align-memory-t2-style-analysis.md (5 patterns + 6 metrics) |
| T3: Prompt injection | ✅ 完成 | T3-prompt-injection-scheme.md (hybrid injection, full system prompt) |
| T4: Prompt vs Fine-tuning 稳定性 | ✅ 完成 | T4-prompt-vs-fine-tuning-stability.md (级联架构 + 衰减曲线) |
| T5a: Prompt 最小样本量验证 | ✅ 完成 | T5a-prompt-sample-validation.md (评分工具 + 分层样本) |
| T5b: LoRA 最小样本量验证 | 📋 就绪 | 需要更多对话样本 |
| T5b: LoRA 最小样本量验证 | ✅ 完成 | T5b-lora-data-extraction.md (68 samples, prediction: 80-100) |
| T6: Hermes personality entry | ✅ 完成 | ~/.hermes/config.yaml chenglu personality |
| T6: Hermes personality entry | 📋 就绪 | — |
| **复杂推理 eval** (4 策略对比) | ✅ 完成 | `eval_complex_reasoning.py` — **method_only 最高 (74.66%)** |

---

## 复杂推理 Eval 结果 (2026-05-21)

**目的**：评估 AI 分析复杂问题的能力（推理 + 信息获取），而非知识问答。

**设计**：5 个经典复杂问题（男女数学天赋、智能定义、agent 能力、概率动力学、统一语言），每个用 4 个策略评估：

| 策略 | 平均分 | 说明 |
|------|--------|------|
| **method_only** | **74.66%** | 只给方法论提示（信息论+贝叶斯+边界追问），不给 persona |
| chenglu_persona | 70.52% | 成璐 persona 提示词 |
| persona + LoRA | 66.90% | persona 提示 + LoRA 微调（6-20 epochs） |
| baseline | 65.34% | 无特殊提示词 |

**关键发现**：
1. **方法论提示 > persona 提示**：给思维工具比给身份标签更有效
2. **LoRA 微调削弱了推理能力**：persona + LoRA 比 persona alone 低 3.6%，需要进一步验证
3. **问题难度差异大**：math_gender_gap 容易拿满分（100%），unified_language 几乎都在边缘（25-31%）
4. **评估核心**：测的是"分析能力"——能否识别问题边界、考虑多因素、区分因果相关、处理不确定性，而不是"答对与否"

详见：`eval_results/eval_complex_summary.json`

---

## 文件结构

```
D1-persona-align/
├── INDEX.md                  # 本文件
├── memory/                   # 探索记录（不可删除）
│   └── persona-align-memory-t2-style-analysis.md  # ✅ T2: 语言风格分析
├── raw/                      # 原始研究素材（论文、项目、data）
├── tasks/                    # 任务状态 (T1-T6, T1-4, T5a 完成)
│   ├── TASKS.md
│   ├── T1-research-report.md       # ✅ T1: 开源项目搜索 (9 projects)
│   ├── T3-prompt-injection-scheme.md  # ✅ T3: 三层架构 + 混合注入方案
│   ├── T4-prompt-vs-fine-tuning-stability.md  # ✅ T4: 级联架构 + 衰减曲线
│   └── T5a-prompt-sample-validation.md  # ✅ T5a: 评分工具 + 实验设计
└── researches/               # 研究报告
```

---

## 递归索引

见各子目录 `INDEX.md`。
