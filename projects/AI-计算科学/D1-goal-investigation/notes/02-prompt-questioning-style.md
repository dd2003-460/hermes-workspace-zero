# Prompt 激发 AI 提问风格 — 研究笔记

> 调研时间: 2026-06-12 (Iteration 27)
> 来源: 知识检索 + 论文研究 + Agent 调研

---

## 1. 核心问题

如何让 AI 从 "answer mode"（被动回答）切换到 "question mode"（主动提问）？
并且如何 **稳定** 地维持这种模式，而非仅一次性的提问？

---

## 2. 已知技术

### 2.1 Self-Ask Prompting（Google DeepMind）

**原理**: 通过链式提问（chain of questions）让 AI 自己拆解问题。

**关键 prompt 模式**:
```
Q: Which country does the capital of the city where Neil Armstrong was born belong to?
A: The relevant question is: In which city was Neil Armstrong born?
Let me think, Neil Armstrong was born in Wapakoneta, Ohio.
The next question is: Which country is Wapakoneta, Ohio in?
Let me think, Wapakoneta, Ohio is in the United States.
The final answer is: United States
```

**适用场景**: 复杂问题的逐步拆解
**局限**: 只在 LLM 自身的问题拆解中起作用，不激发对上下文的质询

### 2.2 Tree of Thoughts（Yao et al. 2023）

**原理**: 扩展 Chain of Thought，让 LLM 在多个思考分支上并行探索。

**关键机制**:
1. 生成多个 "thoughts"（思考步骤）
2. 每个 thought 被评分
3. 搜索算法（BFS/DFS）选择最优路径

**prompt 示例**:
```
Consider possible next steps in your reasoning:
Thought 1: ...
Thought 2: ...
Thought 3: ...
```

**与提问风格的关系**: ToT 需要 LLM 生成多个可能的路径，本质上是在"提问"而非"回答"。

### 2.3 Graph of Thoughts（Sakaguchi et al. 2023）

**原理**: 更灵活的结构，允许 thoughts 之间的任意连接。

**关键机制**: 支持 backtracking（回溯）和 merging（合并），意味着 LLM 可以"质疑"之前的思考并修正。

---

## 3. System Prompt 设计模式

### 3.1 "Answer-Mode" vs "Question-Mode" Prompt

**Answer-Mode（默认）**:
```
You are a helpful assistant. Answer the user's questions.
```
→ LLM 专注于回答，不主动提问。

**Question-Mode（改写后）**:
```
You are a research partner. Your job is to identify gaps, ask critical questions,
and challenge assumptions. Before providing an answer, first ask:
1. What is the underlying assumption?
2. What evidence supports/contradicts this?
3. What alternatives exist?
Only after exploring these questions should you provide your analysis.
```
→ LLM 专注于质询，回答是次要的。

### 3.2 稳定提问的关键技术

| 技术 | 描述 | 效果 |
|------|------|------|
| **Role 约束** | 指定 AI 为"质询者"而非"助手" | 改变默认行为模式 |
| **Few-shot 示例** | 提供提问风格的示例 | 稳定输出风格 |
| **结构化输出** | 要求 AI 先列出问题，再给出分析 | 强制提问步骤 |
| **循环指令** | "每轮结束时提出至少 3 个新问题" | 持续性 |
| **负向约束** | "不要直接回答，先质疑前提" | 抑制默认回答行为 |
| **置信度驱动** | "只在置信度<0.8 时提问" | 只在不确定时提问 |

### 3.3 经过验证的 Prompt 模板

#### 模板 A: 质询者模式（用于理论研究）
```
You are a critical research partner. For every response:
1. First identify the underlying assumptions in the previous statement
2. Ask 2-3 probing questions about each assumption
3. Only then provide your analysis

Format:
> Assumptions: [list assumptions]
> Questions: [2-3 probing questions]
> Analysis: [your response]
```

#### 模板 B: 反向 Socratic 模式（用于探索新概念）
```
When presented with a concept or claim:
1. Ask "Why must this be true?" (至少一层)
2. Ask "What would make this false?"
3. Ask "What alternative explains the same phenomenon?"

Never accept a claim without first exploring alternatives.
```

#### 模板 C: 持续提问循环（用于多轮迭代）
```
At the END of each response, you MUST:
1. State 3 questions that your analysis raised but did not answer
2. State 1 assumption that you think may need re-examination
3. State 1 direction that you believe is worth exploring

This ensures the questioning continues across turns.
```

#### 模板 D: 置信度 + 提问（用于研究探索）
```
For each claim you make, rate your confidence (0-1):
- If confidence < 0.8: You MUST also state what would increase your confidence
- If confidence < 0.6: You MUST propose a specific experiment or analysis to test it
- If confidence >= 0.8: You may skip the questioning step
```

### 3.4 稳定性分析

**为什么 AI 容易回到 answer mode**:
1. **训练数据偏差**: LLM 在训练中以"回答问题"为主要模式
2. **RLHF 偏差**: RLHF 偏好直接回答，不喜欢过多质疑
3. **用户期望**: 用户通常期望答案，不期望问题

**稳定提问的障碍**:
- 即使 prompt 要求提问，LLM 仍然会不自觉地回答
- 多轮迭代后，提问质量下降（模式退化）
- 没有外部反馈循环，LLM 不知道哪些问题是有价值的

---

## 4. 与 Ralph Loop 的关系

Ralph Loop 的核心机制（注入相同 prompt）天然适合持续提问:
- 每次循环注入相同的 prompt → LLM 持续面对相同的提问约束
- 但如果 prompt 本身是 answer-mode 的，循环只会产生更多 answer

**Ralph Loop 中提问模式的设计建议**:
1. 在 global.md 的 `prompt` 字段中包含提问约束
2. 每轮结束要求 LLM 提出新问题
3. 将 LLM 提出的问题纳入下一轮的 prompt

---

## 5. 实验设计建议

### 实验 1: 不同 Prompt 策略的提问率对比

**方法**: 同一 task，不同 system prompt

| Group | Prompt 类型 | 预期提问率 |
|-------|------------|-----------|
| A | 默认（helpful assistant） | 0% |
| B | 质询者角色 | 20-40% |
| C | Few-shot 示例 | 40-60% |
| D | 结构化输出（先问后答） | 60-80% |
| E | C + 负向约束 | 70-90% |

**测量指标**: 每轮响应中问题的数量 / 分析长度

### 实验 2: 多轮稳定性

**方法**: 50 轮 Ralph Loop，记录每轮的提问率

**预期**: 前 10 轮高提问率，之后逐渐退化（除非有持续约束）

---

## 6. 参考资料

1. Self-Ask: https://arxiv.org/abs/2210.03350
2. Tree of Thoughts: https://arxiv.org/abs/2305.10601
3. Graph of Thoughts: https://arxiv.org/abs/2308.09688
4. Constitutional AI: https://arxiv.org/abs/2212.08073
5. Claude Code stop hook: `~/.claude/plugins/.../ralph-loop/hooks/stop-hook.sh`
