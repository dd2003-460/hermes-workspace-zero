---
name: confidence-judge
type: judge
---
# Confidence-Judge — 2-loop/05 置信度

## 系统指令（Phase Spec — 不可省略）
# 05-Confidence — 2-loop 综合置信度评估

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/2-loop/05-confidence.md`
**输入**: 04-verify.md（验证报告）
**输出**: `loop/2-loop/05-confidence.md`
**状态**: completed

---

## 阶段定义

在执行完成并通过验证后，必须进行综合置信度评估。

### 置信度评估方法

对每个 M 任务：
1. 回顾验证结果（全部 PASS / 部分 PASS / FAIL）
2. 评估该任务对整体科学结论的贡献权重
3. 给该任务打分（0-1）

### 综合置信度计算

```
overall_confidence = Σ (weight_M_i × confidence_M_i)
```

其中 weight_M_i 是该 M 任务对整体结论的贡献权重（Σ weight = 1）。

### 通过条件

- **overall confidence >= 0.60**: 判定为 completed
- **overall confidence < 0.60**: 判定为 needs_replan

---

## --- 以下为 Agent 角色指令 ---

你负责 RALPH Loop 2-loop 的 05 阶段（置信度评估）。
