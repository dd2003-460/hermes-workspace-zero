# Persona Profile — 成璐画像 → System Prompt 转换

**来源**: D1-memory/memory/profile/unified_profile.json v3.1
**日期**: 2026-05-22
**迭代**: 7
**类型**: 决策 + 实现

## 核心决策

**persona_align 的最终方向：method_only 的 4 条分析框架 + unified_profile 中的决策倾向和表达风格。**

method_only 的 80 字符覆盖了成璐的**分析方式**（变量分解、因果推断、混淆控制、边界追问），但 missing：

1. **决策倾向** — "对齐优先于效率"、"安全边界内默认自主"、"完成≠质量达标"
2. **表达风格** — "简洁直接"、"少空话多证据"、"非必要不英文"
3. **自省机制** — "Impact? Bias? Motivation?" 三要素
4. **研究品味** — "框架式"、"数学深度"、"跨学科整合"

## 转换方案：method_only → full_personhood_prompt（v2 精简版）

**v2 精简版（~100 字符）** — 2026-05-22 快速测试后优化：

```
分析：1)识别变量 2)区分因果 3)考虑混淆 4)明确边界 5)标不确定度
表达：中文优先，简洁直接，少空话多证据
自省：每结论问——Impact? Bias? Motivation?
决策：对齐>效率，边界内自主，对标世界顶尖
```

**~100 字符** — 去掉了"思考"板块（贝叶斯/溯因/三层拆解是方法论文档中的，不需要每次分析都重复）。

**v1 测试问题**：v1 (213 字符) 导致模型输出 8589 字 — 指令过多产生冗余。v2 应控制在合理字数。

## 验证计划

等 v2 eval 完成后，加入此策略作为第 5 个对比项：
- method_only (80 chars)
- chenglu_persona (200 chars)
- thinking_engine_v1 (900 chars)
- **persona_profile_full (~300 chars)**

## 为什么这个方向正确

eval 反复证明：method_only > persona。但 persona 在 unified_language 问题上更好（84.13% vs 76.19%）。

 persona_profile_full 的设计是：method_only 的 4 条分析 + persona 的决策倾向 + persona 的表达风格 + persona 的思维模式。

**不添加任何身份标签（"你是成璐"），只添加方法论和行为约束。**
