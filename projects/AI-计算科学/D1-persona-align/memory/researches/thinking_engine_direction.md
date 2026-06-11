# 思考引擎 — 方向决策

**日期**: 2026-05-22
**版本**: iteration 4 决策

## 已有数据

### Iteration 1 — 偏差分析
- method_only 只有 80 字符 prompt
- 评分系统对长度有系统性偏好
- persona 无效是因为没有回答结构

### Iteration 2 — eval（原评分系统）
| 策略 | 平均分 | 平均长度 |
|------|--------|----------|
| method_only | 87.62% | ~2720 字 |
| chenglu_persona | 86.35% | ~1454 字 |
| thinking_engine_v1 | 86.35% | ~1479 字 |

- v1 的 5 阶段强制结构 **没有改进**

### Iteration 3 — v2 eval（修正评分系统，进行中）
- 修正：移除 block_structure 和 cross_domain（纯长度相关）
- 新增：density（信息密度）、conclusion_density（断言比例）
- 长度惩罚阈值从 4000 降到 2500

## 已验证的洞察

1. **简洁 prompt > 复杂 prompt**: method_only 的 80 字符击败 v1 的 900 字符
2. **persona 提示词不产生分析**: chenglu_persona 的平均深度分数和 method_only 一样都是 1.0 — 但这是 keyword density，不能说明内容质量
3. **长回答不等于好回答**: v1 平均 1479 字（vs 原版 2720 字）但分数只低 1.27%
4. **chenglu_persona 在某些问题上更好**: unified_language 上 persona 84.13% > method_only 76.19%

## 关键问题

**method_only 有效的原因是什么？**

反复检查 method_only prompt：
```
你是一个研究者。分析问题时必须：1) 识别问题的所有关键变量 2) 区分相关和因果 3) 考虑可能的混淆因素 4) 明确你的结论在什么条件下成立。用中文。
```

它做了什么让它有效？

1. **"分析问题时必须"** — 强制性指令，不协商
2. **"识别关键变量"** — 变量分解（分析的基础）
3. **"区分相关和因果"** — 方法论核心（这是成璐反复强调的）
4. **"考虑混淆因素"** — 边界意识
5. **"结论在什么条件下成立"** — 不确定性意识

**这 5 个点恰好对应成璐的方法论：变量分解、因果推断、边界追问、不确定性意识。**

## 决策

### 方案 A：接受 method_only 为最佳方案
- method_only 已经是当前最佳
- 不需要再迭代 "思维引擎"
- 将 method_only 的 prompt 整合到 AGENTS.md 作为系统级原则
- 成本：每次对话只需要 80 字符的 system prompt

### 方案 B：设计 method_only 的增强版（保留方法核心 + 增强特定能力）
- 保留 method_only 的 4 个方法点
- 增加"信息论视角"和"贝叶斯思维"（这些是 persona 的强项）
- 但不用 5 阶段强制结构
- 目标：method_only 的分析质量 + persona 的跨域整合

### 方案 C：等待 v2 修正评分系统后再决策
- v2 修正评分后，chenglu_persona 可能领先（因为信息密度高）
- 如果修正后结果不同 → 调整方向
- 如果结果相似 → 确认 method_only 方向正确

## 推荐：方案 A + C 并行
- **现在**：将 method_only 整合到系统级 prompt（AGENTS.md 中的 ralph-loop 约束）
- **等待**：v2 修正评分结果（约 1-2 小时）
- **如果不满意**：再迭代

## 整合方案（method_only → 系统级 prompt）

将 method_only 的 4 个方法点整合到 AGENTS.md 中，作为 ralph-loop 每次迭代的前置推理规则：

```
分析时必须执行：1) 识别关键变量 2) 区分因果和相关 3) 考虑混淆因素 4) 明确结论边界条件
```

这个 prompt 只有 80 字符，但覆盖了成璐方法论的核心：变量分解、因果推断、边界意识、不确定性。

不需要更复杂的"思维引擎"。
