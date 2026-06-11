# Amulet: ReAlingment During Test Time for Personalized Preference Adaptation of LLMs

## 基本信息
- **论文**: Amulet: ReAlingment During Test Time for Personalized Preference Adaptation of LLMs
- **作者**: Zhaowei Zhang, Fengshuo Bai, Qizhi Chen, Chengdong Ma, Mingzhi Wang, Haoran Sun, Zilong Zheng, Yaodong Yang
- **来源**: arXiv
- **相关度**: 极高相关

## 核心贡献

解决"静态训练目标"与"动态用户需求"的不对齐:

1. **在线学习解码**: 将 token 解码视为在线学习问题，由轻量用户 prompt 指导
2. **Closed-form 解**: 为每个优化步骤推导闭式解，保持计算成本极低
3. **无参数更新**: 不需要更新模型参数，直接在推理时优化
4. **Training-free**: 通过用户提示直接实现偏好对齐

## 与 persona-v3 的关联

### Amulet = persona-v3 的"自适应先验"维度
Amulet 在测试时将 token 解码视为在线学习，persona-v3 通过贝叶斯先验更新实现自适应先验:
- Amulet: 在线学习 → 动态调整解码
- persona-v3: 贝叶斯更新 → 动态调整信念

两者都证明了一个核心观点：**模型在推理时的行为是可以动态调整的，不需要重新训练。**

### 对 persona-v3 的影响
1. **Amulet 验证了 persona-v3 的"自适应先验"** — 贝叶斯更新是数学化的在线学习
2. **可以从 Amulet 借鉴 "re-alignment" 机制** — 在长对话中周期性重新对齐 persona
3. **Amulet 的 "closed-form solution" 思路** 可以启发 persona-v3 的自适应维度调整策略

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接验证 persona-v3 核心方法论
- **事实可信度**: 4/4 — 实证论文，多数据集验证
