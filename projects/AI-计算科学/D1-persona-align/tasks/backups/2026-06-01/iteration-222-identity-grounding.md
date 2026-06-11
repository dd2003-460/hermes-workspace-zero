# Iteration 222: persona-v3 identity grounding 改进

## 目标
根据 ID-RAG 研究验证的 identity grounding 方向, 增强 self-preservation 机制。

## 执行动作

### persona-v3-prompt.txt 修改
- self-preservation 从 4 条扩展到 5 条
- 新增 **"身份图谱 (Identity Grounding, ID-RAG)"**:
  - 维护结构化 persona 属性清单 (核心信念、方法论偏好、表达风格)
  - 在关键决策点主动查询而非依赖衰减上下文
  - 输出前检查是否与之前表达的信念冲突

### 验证
- persona-v3-prompt.txt baseline 评分: 63.08 (与迭代 204 的 63.8 一致)
- 所有维度正常计分, 无回归

## 影响
- self-preservation 现在包含: 检测 → 修复 → 锚定 → **身份图谱** → 记忆传递
- 5 条机制完全对应 ID-RAG 建议: drift grounding, re-grounding, belief consistency check
- 评分工具不受影响
