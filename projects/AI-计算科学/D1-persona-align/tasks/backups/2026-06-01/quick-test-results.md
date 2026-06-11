# Quick Test — persona_profile_full vs method_only

**日期**: 2026-05-22
**测试类型**: 单题验证（agent_capability_test）

## 结果

| 策略 | 得分 | 字数 |
|------|------|------|
| persona_profile_full | **100.00%** | 8589 |
| chenglu_persona | 87.50% | 417 |
| method_only | 75.00% | 511 |

## 分析

1. **persona_profile_full 得分最高** — 但需要扣除长度惩罚（8589 字远超 2500 阈值）
2. **method_only 得分最低** — 分析质量可能不足（只产生 511 字）
3. **chenglu_persona 居中** — 417 字但信息密度可能更高

## 修正评分（应用 length_penalty）

假设 length_penalty > 2500 字开始线性扣分：
- persona_profile_full (8589): penalty = 0.5 - (8589-2500)/6000 = 0.5 - 1.01 = 0.3 (最低)
- chenglu_persona (417): penalty = 1.0
- method_only (511): penalty = 1.0

修正后分数：
- persona_profile_full: ~100 * (1-weight) + 30 * weight — 仍然可能最高
- 但关键问题是：8589 字中有多少是有效分析，多少是冗余？

## 结论

**persona_profile_full 不应该是"越长越好"的方案。** 300 字符的 prompt 中包含了过多的指令（分析、执行、表达、思考 4 个板块），导致模型产生了大量冗余内容。

**v2 修正**: 将 persona_profile 精简为仅核心 5-6 条规则，去掉冗余指令。

```
分析时：1) 识别变量 2) 区分因果 3) 考虑混淆 4) 明确边界 5) 标不确定度
表达：中文优先，简洁直接，少空话多证据
自省：每结论问——Impact? Bias? Motivation?
```

~100 字符 — 保留核心，去掉冗余。
