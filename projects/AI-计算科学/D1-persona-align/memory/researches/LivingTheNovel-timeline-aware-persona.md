# Living the Novel: Timeline-Aware Conversational Agents from Novels

## 来源
Huang, Yan, Gong, Gao, Kang, Liu, Lu, Zheng

## 核心问题
Generic LLMs suffer from persona drift，无法在互动角色体验中保持角色一致性。

## 方案
Two-stage training method：
1. **Reinforcement fine-tuning** — 初步学习角色行为
2. **Timeline-aware constraints** — 时间线约束保证叙事逻辑一致性

## 关键发现
1. **timeline-aware constraints 是关键** — 角色行为必须与时间线上的已有行为一致
2. **two-stage training 效果显著** — 比单一 fine-tuning 更好保持 persona
3. **文学角色 → 交互体验** — 证明 persona 固化是可行的

## 与 persona-v3 的关联

### 相同理念
- timeline-aware constraints ≈ persona-v3 的 drift detection（都比较"过去行为"）
- 两个 stage ≈ persona-v3 的 pre-training + self-preservation online correction

### 互补点
1. **persona-v3 不需要 training** — 纯 prompt engineering，零成本
2. **但 persona-v3 可以借鉴 timeline-aware 思路** — 在 self-preservation 中检查时间线一致性
3. **future hybrid** — persona-v3 prompt + timeline consistency check 可作为 gap_filler 的增强

## 关键引用
> "generic LLMs suffer from persona drift, often failing to stay in character"
> "two-stage training method combining reinforcement fine-tuning with timeline-aware constraints"
