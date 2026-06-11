# Eval 结果分析 — Iteration 2

**日期**: 2026-05-22
**类型**: 结果分析

## 最终结果

| 策略 | 平均分 | 平均长度 | 排名 |
|------|--------|----------|------|
| method_only | 87.62% | ~2720 字 | #1 |
| chenglu_persona | 86.35% | ~1454 字 | #2 (并列) |
| thinking_engine_v1 | 86.35% | ~1479 字 | #3 (并列) |

## 逐题对比

| 题目 | method_only | persona | v1 | 说明 |
|------|-------------|---------|-----|------|
| math_gender_gap | 92.06% | 92.06% | **100.00%** | v1 赢 |
| intelligence_definition | **100.00%** | 92.06% | 84.13% | method_only 赢 |
| agent_capability_test | **85.71%** | 79.37% | 71.43% | method_only 赢，v1 输 |
| probability_dynamics | 84.13% | 84.13% | **92.06%** | v1 赢 |
| unified_language | 76.19% | 84.13% | 84.13% | persona/v1 赢 |

**method_only 赢了 2 题，v1 赢了 2 题，persona 赢了 1 题**

## 深入分析

### 为什么 method_only 赢？
不是因为方法好，而是因为**评分机制偏爱长度**：
- method_only 平均 2720 字 vs v1/persona 约 1500 字
- 长回答更容易触发 block_structure、cross_domain、uncertainty 评分维度
- depth 评分是关键词密度（/3），长回答自然有更多关键词

### 为什么 thinking_engine_v1 没赢？
1. **5 阶段强制结构太僵化**: 不所有问题都需要 5 阶段分析
2. **字数约束导致回答短**: 回答短 → 评分维度触发少 → 分数低
3. **类型自动识别无效**: 不管识别成什么类型，输出格式都一样

### chenglu_persona 的意外表现
以 50% 的字数实现了和 v1 相同的分数。说明：
- persona 提示词在特定问题上有效（unified_language: 84.13% vs method_only 76.19%）
- 但整体平均不如 method_only — 缺少分析方法论

## 关键洞察

**"评分系统奖励长回答，而不是好回答"**

当前的 score_response() 评分机制对长度有系统性偏好：
1. length_reasonable: 300 字以下是 0 分
2. block_structure, question_ratio, cross_domain 都随长度增加
3. depth 是关键词密度，长回答自然有更多关键词
4. length_penalty 只在 >4000 字才扣分

**修正**: 需要重新设计评分系统，使长度不再是一个优势因素。

## 下一步

1. **修正评分系统**: 
   - 将 length_reasonable 从二元判断改为连续函数
   - 新增 efficiency 维度: score per character (深度 / 字数)
   - 增加长度惩罚: >2000 字开始扣分

2. **重新运行 eval**:
   - 修正评分后，chenglu_persona 可能会更高分（因为它的信息密度更高）
   - thinking_engine_v2 应该设计为中等长度（2000-2500 字），结构化但有密度

3. **思考引擎 v2 设计修正**:
   - 不强制 5 阶段输出
   - 保留 method_only 的方法论提示
   - 增加 persona 的跨域整合能力
   - 用评分效率驱动长度控制
