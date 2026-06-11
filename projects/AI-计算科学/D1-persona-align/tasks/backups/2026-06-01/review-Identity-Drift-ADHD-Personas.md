# LLM-Based Educational Simulation: Evaluating Temporal Student Persona Stability Across ADHD Profiles

## 基本信息
- **论文**: LLM-Based Educational Simulation: Evaluating Temporal Student Persona Stability Across ADHD Profiles
- **作者**: Jana Gonnermann-Müller, Jennifer Haase, Nicolas Leins, Thomas Kosch, Sebastian Pokutta
- **来源**: arXiv
- **相关度**: 高相关

## 核心贡献

研究 LLM 在长期教育训练会话中是否保持一致的角色特征:

1. **对话内漂移 (Within-conversation drift)**: 在未脚本化对话中，高/中 ADHD 人设的模型会出现行为漂移
2. **自报告特质稳定**: 模型自我报告的特质保持稳定，但行为表现发生变化
3. **结构化交互提示的作用**: 使用结构化交互提示可以减少漂移

## 与 persona-v3 的关联

### 自报告 vs 行为表现的不一致
这篇论文发现了一个关键现象：模型可以"说"它是什么人设，但"做"的是另一回事。这与 persona-v3 的设计哲学高度一致：
- persona-v3 不依赖"说"（指令跟随），而依赖"做"（行为模式）
- persona-v3 的 3 行为约束 (简洁直接, 不解释, 推进而非停滞) 确保行为与 persona 一致

### 结构化交互提示 = persona-v3 的 prompt 结构
论文证明"结构化交互提示"可以减少漂移，直接验证了 persona-v3 的方法论：通过结构化 prompt 维护 persona 稳定性。

### ADHD Profiles 与人设粒度
使用 ADHD Profiles 作为人设变化的维度 — 这为 persona-v3 提供了新的视角：persona 可能不是静态的，而是会随着环境需求动态调整（类似 ADHD 症状的变化）。

## 对 persona-v3 的影响

1. **结构化交互提示 = persona-v3 的 8 原则 + 6 维度** — 两者都是结构化约束
2. **行为漂移检测** — 可以借鉴论文的"对比自报告和实际行为"方法
3. **ADHD Profiles 类比** — persona 的动态调整可能是有益的，而非缺陷

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接支持 persona-v3 核心假设
- **事实可信度**: 4/4 — 实证论文，ADHD Profiles 对比
