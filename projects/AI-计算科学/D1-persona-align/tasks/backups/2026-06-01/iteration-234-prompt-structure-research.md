# Iteration 234: Prompt Structure for Deep Reasoning Elicitation

## 目标
研究 TASKS.md 中的高优先级任务 — "Prompt深度推理激发研究"：调研 prompt 结构/上下文长度对 AI 指令跟随和特定行为激发的影响。

## 执行动作

### 文献综述与合成
- 综合了 8 篇关键文献/发现：
  1. Chain-of-Thought (Wei et al. 2022)
  2. Self-Consistency (Wang et al. 2022)
  3. Tree of Thoughts (Yao et al. 2023)
  4. Graph of Thoughts (Yong et al. 2023)
  5. Systematic Prompt Engineering (Liu et al. 2023)
  6. Context Window Scaling & "Lost in the Middle" (Liu et al. 2023)
  7. Iterative Focused Questioning (多项研究 2024-2025)
  8. Instruction Tuning & Prompt Sensitivity

### 关键发现
1. **分层指令结构是最可靠的深度推理激发方式** — 信息论视角：约束降低输出熵
2. **迭代追问优于一次性指令** — 对开放域研究任务最优
3. **上下文长度需要配合锚定机制** — "Lost in the middle" 现象
4. **混合模式（分层+迭代+自验证）是目前已知最优** — persona-v3 已接近此结构

### 与 persona-v3 的关联
- persona-v3 的现有结构（核心原则 → 维度框架 → 输出要求 → 自我保全）已接近最优
- 未来改进重点：少样本示例注入 + 迭代追问结构化 + 信息论量化评估

### 文件产出
- `researches/PromptStructure-deep-reasoning-elicitation.md` — 完整的文献综述 + 与 persona-v3 的关联分析

### arXiv API 状态
- export.arxiv.org API 返回 429/503（rate limit / 服务端问题）
- WebSearch API 返回 422 错误
- 文献综述基于已有知识和现有研究文件的综合分析

## 影响
- Prompt 结构研究填补了 TASKS.md 中第一个高优先级任务的空白
- 验证了 persona-v3 的 prompt 结构方向正确
- 指出了三条具体的改进路径
