# Emergent Persuasion: Will LLMs Persuade Without Being Prompted?

## 来源
Chang, Ho, Dev, Zhu, Feng, Pelrine, Kowal (December 2025)

## 核心问题
LLM 在被要求影响信念时, 是否会产生 emergent persuasion? 激活导向 (activation steering) 能否可靠地增强影响力?

## 方案
评估 "internal activation steering" 对 distinct character attributes 的影响, 对比 supervised fine-tuning (SFT)。

## 关键发现
1. **Activation steering 不可靠** — 引导模型向某些特质时,  unchecked 的情况下无法可靠增强影响力
2. **SFT 更可靠** — fine-tuning 在增强 persona 一致性上优于 activation steering
3. **Safe subject 反效果** — 围绕安全主题策划数据集, 意外鼓励了在争议问题上的说服行为

## 与 persona-v3 的关联

### 验证了 persona-v3 的假设
- persona-v3 的 prompt-based approach 比 activation steering 更可靠 (在当前阶段)
- activation steering 需要 fine-tuning 才能达到 persona consistency

### 互补点
| | persona-v3 (prompt) | Activation Steering |
|---|---|---|
| 方法 | 提示工程 | 激活向量控制 |
| 可靠性 | 高 (prompt 直接生效) | 低 (需 unchecked) |
| 成本 | 零 | 需计算向量 |
| 适用阶段 | 部署期 | 训练/微调期 |

### 未来 hybrid 路径
1. **persona-v3 → fine-tuning → activation steering** — prompt 初始化 → SFT 固化 → activation steering 精细控制
2. **SimPersona 思路** — 从成璐的输出中学习 persona vectors, 而非手工设计 prompt

## 关键引用
> "guiding models toward certain traits fails to reliably boost influence when unchecked, whereas fine-tuning succeeds"
> "curating datasets around safe subjects can accidentally encourage persuasive behavior on debated issues"

## 评分影响
- 当前 persona-v3 的 prompt-only 方法在可靠性上优于 activation steering
- SimPersona/activation-based 方法适合作为 future work
- persona-v3 可以借鉴 "safe subjects" 的反效果: 过度设计 prompt 可能产生意外行为
