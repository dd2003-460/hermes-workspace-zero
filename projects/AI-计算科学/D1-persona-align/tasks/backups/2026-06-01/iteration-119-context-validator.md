# Iteration 119: persona-v3 上下文验证器

**日期**: 2026-05-28
**任务**: 创建工具验证 persona-v3 prompt 在实际 Claude Code 会话中的效果

## 完成内容

### 新创建
- `scripts/validate_persona_in_context.py` — 上下文验证器

### 功能
1. **dry run 模式**（默认）：展示 benchmark 问题和验证计划
2. **API 模式**（`--run`）：对接 Anthropic API，对比三种策略：
   - no_prompt: 无特殊提示词
   - method_only: 80字符方法论提示词
   - persona_v3: 完整的 persona-v3 prompt

### Benchmark 问题
| ID | 问题 | 期望维度 |
|----|------|----------|
| math_gender_gap | 数学天赋男女差异 | 先验/投影/精度 |
| intelligence_definition | 什么是智能？ | 自我/投影/感知 |
| probability_dynamics | 概率=动力学信息抹除 | 精度/先验/自我 |

### 评估流程
1. 对每个 benchmark 用三种策略分别生成回答
2. 用 alignment_checker 评估 6 维度覆盖度
3. 对比哪种策略在期望维度上得分最高

## 状态
- dry run 通过
- API 验证需要设置 ANTHROPIC_API_KEY
