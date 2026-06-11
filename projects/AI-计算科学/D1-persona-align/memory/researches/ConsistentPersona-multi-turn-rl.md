# Consistently Simulating Human Personas with Multi-Turn Reinforcement Learning

## 来源
Abdulhai, Cheng, Clay, Althoff, Levine, Jaques

## 核心问题
Off-the-shelf LLMs 在 extended conversations 中经常 drift from assigned personas，特别是在教育或治疗场景中需要保持一致性。

## 方案
使用 reinforcement learning tuned with consistency metrics 来显著减少 contradictory outputs。

## 关键发现
1. **RL 可以学习 persona consistency** — 不是靠 prompt engineering，而是靠 reward signal 训练
2. **multi-turn consistency metric** — 跨轮数评估一致性，不是单轮评分
3. **off-the-shelf LLMs 固有 drift** — 即使是 strong prompt 也无法在长对话中保持

## 与 persona-v3 的关联

### 验证了 persona-v3 的核心假设
- persona-v3 假设"对齐不是记住规则，是内化价值函数" — 这与 RL 方法 converge
- self-preservation 机制是 prompt-level 的 consistency metric 实现

### 差异与互补
| | persona-v3 | ConsistentPersona |
|---|---|---|
| 方法 | Prompt engineering | RL training |
| 漂移预防 | self-preservation | RL consistency reward |
| 适用范围 | 任意 LLM | 需要 fine-tuning |
| 成本 | 零 | 训练成本 |

### 对 persona-v3 的启示
1. **可验证性** — 可以用 ConsistentPersona 的 multi-turn consistency metric 来验证 self-preservation 的效果
2. **hybrid 路径** — persona-v3 作为 pre-training 的初始化，再经 RL 微调可能效果最优
3. **future work** — 将 persona-v3 的维度覆盖率作为 RL reward 的一个 component

## 关键引用
> "off-the-shelf LLMs often drift from their assigned personas during extended conversations"
> "reinforcement learning tuned with consistency metrics significantly reduces contradictory outputs"
