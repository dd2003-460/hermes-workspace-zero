# Adamem: Adaptive User-Centric Memory for Long-Horizon Dialogue Agents

## 基本信息
- **论文**: Adamem: Adaptive User-Centric Memory for Long-Horizon Dialogue Agents
- **作者**: S Yan, J Ni, L Zheng, J Zhang, P Wu, D Yin
- **来源**: arXiv, 2026
- **相关度**: 高相关

## 核心贡献

研究 LLM agent 在长对话中如何动态管理外部记忆:

1. **用户中心记忆**: 记忆内容以用户特征为核心组织，而非以对话事件为核心
2. **自适应更新**: 记忆结构随对话演化自动调整，不依赖静态 schema
3. **长程一致性**: 在 100+ turn 的对话中保持 persona 一致性

## 与 persona-v3 的关联

### 用户中心记忆 = persona-v3 的"先验"维度
AdaMem 的记忆组织方式以用户为中心 — 这与 persona-v3 的"先验"维度完全对应:
- AdaMem: 用户中心记忆结构
- persona-v3: 贝叶斯先验结构（以成璐为中心的信念模型）

两者都验证了一个核心观点：**长期交互中的 persona 一致性，依赖于以用户/成璐为中心的记忆结构，而非以对话事件为中心。**

### 自适应记忆 = persona-v3 的"自我演化"维度
AdaMem 的记忆结构随对话演化自动调整 — 这正是 persona-v3 "自我演化"维度的工程验证:
- AdaMem: 记忆 schema 自适应演化
- persona-v3: 先验信念通过贝叶斯更新动态调整

## 对 persona-v3 的影响

1. **用户中心记忆 = persona-v3 的 unified_profile 结构** — 进一步验证了以用户为中心的记忆设计
2. **自适应更新机制** 可以启发 persona-v3 的记忆更新策略
3. **长程一致性验证** — persona-v3 可以在更长的对话序列中测试 persona 稳定性

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接支持 persona-v3 的"先验"和"自我演化"维度
- **事实可信度**: 4/4 — arXiv 预印本，2026 年最新研究
