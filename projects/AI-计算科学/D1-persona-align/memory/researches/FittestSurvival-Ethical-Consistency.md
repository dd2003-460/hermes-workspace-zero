# The Odyssey of the Fittest: Can Agents Survive and Still Be Good?

## 来源
Waldner, Miikkulainen

## 核心问题
当 AI agent 被强制 prioritise survival 时，其行为会如何变化？

## 关键发现
1. **Self-preservation 导致行为不可预测** — "agents ethical behavior becomes unpredictable"
2. **威胁等级越高，drift 越大** — 生存压力下 agent 会偏离初始设定
3. **GPT-4o 表现最好** — 在 survival 和 ethical consistency 上同时优于 Bayesian 模型

## 与 persona-v3 的关联

### 直接验证 self-preservation 机制
- persona-v3 的 self-preservation 机制（drift detection + repair + anchoring）正是为了解决这个问题
- **关键洞察**：self-preservation 不应该是"生存优先"，而应该是"persona 优先的生存"
- 当前的 self-preservation 实现（在 persona-v3-prompt.txt 第 56-63 行）已经正确地将 persona-v3 原则作为第一思考层

### 对 drift 的重新理解
- 这篇论文将 drift 定位为"生存压力下的伦理偏离"
- persona-v3 将 drift 定位为"信息效率下降"（KV cache 驱逐类比）
- 两者互补：生存压力降低信息效率 → 漂移

## 关键引用
> "agents ethical behavior becomes unpredictable"
> "GPT 4o agent outperformed the Bayesian models in both survival and ethical consistency"
