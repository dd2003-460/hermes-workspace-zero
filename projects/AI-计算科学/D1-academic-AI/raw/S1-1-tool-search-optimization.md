# S1-1: 工具搜索频率优化猜想

## 来源
转化自：
- raw/social/math_social_cross.md (1): 频率最优化理论（磨刀/砍柴比喻）

## 核心猜想

**工具搜索-探索折衷变分原理（猜想）**：设工具空间为 $\mathcal{T}$，任务分布为 $p(t)$，搜索策略为 $\pi_\theta(t)$，则最优搜索策略满足：

$$\min_{\pi} \left[ \underbrace{\mathbb{E}_{\pi}[\ell(\text{task}, \pi(\text{task}))]}_{\text{任务成本}} + \lambda \cdot \underbrace{KL(\pi \| \pi_0)}_{\text{搜索成本}} \right]$$

其中 $\pi_0$ 为**先验工具分布**（领域知识编码），$\lambda$ 控制探索-利用权衡。

## 物理直觉

| 原始比喻 | 数学结构 |
|----------|----------|
| 磨刀（探索） | 搜索未使用工具分布 |
| 砍柴（利用） | 对已知最优工具的收敛 |
| 磨刀太久效率低 | $\lambda \downarrow$ 过犹不及 |
| 找不到新刀 | $\pi_0$ 支持集过小 |

**最优频率**：当 $\lambda^* = \arg\min$ 时，**搜索梯度** $\nabla_\theta KL(\pi_\theta \| \pi_0)$ 与**任务梯度** $\nabla_\theta \mathbb{E}[\ell]$ 达到平衡。

## 与 S12 的关联

**同时性发现的根源**：当多人面临相同任务分布 $p(t)$，且各自先验 $\pi_{0,i}$ 足够相似时：
- 存在**临界时间窗口** $T_{critical}$
- 在该窗口内，不同 agent 倾向于收敛到**相同最优工具**
- 这就是"S12 同时性发现"——它源于**工具空间的全局最优结构**

## 可验证性

1. **Agent 搜索模拟**：构建多 Agent 工具市场，测量收敛到最优工具的时间分布
2. **搜索行为分析**：LLM 在开放-world 任务中工具选择的探索比例
3. **理论证明路径**：使用**Thompson sampling 的 regret 界**推导最优探索率

## 与定理 10 的关联

工具空间 $\mathcal{T}$ 可视为**认知流形**：
- 工具选择 → 流形上的随机游走
- 最优工具 → 流形的"吸引子"（稳定点）
- 不同工具集合 → 流形上不同吸引 basin 的拓扑

---
*Created: 2026-04-30 | Status: Conjecture — Testable via multi-agent simulation*
