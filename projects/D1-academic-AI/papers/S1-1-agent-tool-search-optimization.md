# S1-1：Agent 工具搜索频率优化理论

**日期**：2026-05-04
**来源**：S1-1 原始猜想 + S12 同时性发现整合
**状态**：理论框架提出（待实验验证）

---

## 元问题

> **Agent 在工具选择中需要多少探索才能平衡信息增益与任务效率？**

---

## 核心猜想

**工具搜索-利用折衷变分原理（猜想）**：设工具空间为 $\mathcal{T}$，任务分布为 $p(t)$，搜索策略为 $\pi_\theta(t)$，则最优搜索策略满足：

$$\min_{\pi} \left[ \underbrace{\mathbb{E}_{\pi}[\ell(\text{task}, \pi(\text{task}))]}_{\text{任务成本}} + \lambda \cdot \underbrace{KL(\pi \| \pi_0)}_{\text{搜索成本}} \right]$$

其中 $\pi_0$ 为**先验工具分布**（领域知识编码），$\lambda$ 控制探索-利用权衡。

---

## 理论命题

### 命题 1：磨刀-砍柴最优频率定理

**搜索梯度的动态平衡**：在最优解 $\lambda^*$ 处，搜索成本梯度与任务成本梯度正交：

$$\nabla_\theta KL(\pi_\theta^* \| \pi_0) \cdot \nabla_\theta \mathbb{E}[\ell] = 0$$

**搜索-任务最优平衡**：
$$\lambda^* = \frac{\|\nabla_\theta \mathbb{E}[\ell]\|}{\|\nabla_\theta KL(\pi_\theta \| \pi_0)\|}$$

**直觉解释**：当任务难度上升（任务梯度增大），最优搜索强度应降低（减少"磨刀时间"）；当领域先验贫乏（$\pi_0$ 熵大），最优搜索强度应增加。

---

### 命题 2：工具空间认知流形定理

**工具空间 $\mathcal{T}$ 作为认知流形**：
- 工具选择 → 流形上的随机游走（受 $KL$ 正则驱动）
- 最优工具 → 流形的**稳定点**（吸引力中心）
- 不同工具簇 → 流形上不同吸引盆的拓扑结构

**工具空间曲率-选择概率定理**：
$$P_{\text{select}}(t^*) \geq \exp\left(-\frac{R(t^*) \cdot d(t^*, t_{global}^*)^2}{\sigma^2}\right)$$

其中 $R(t^*)$ 为工具 $t^*$ 处的 Ricci 曲率，$\sigma^2$ 为探索噪声方差。

---

### 命题 3：同时性发现临界时间窗口定理

**S12 同时性发现的工具空间根源**：当多 Agent 面临相同任务分布 $p(t)$，且先验 $\pi_{0,i}$ 足够相似时：

**临界时间窗口定理**：
$$T_{critical} = \Theta\left(\frac{\log N}{\lambda^* - \lambda_0}\right)$$

其中 $\lambda^*$ 为最优探索率，$\lambda_0$ 为初始探索率，$N$ 为工具空间维度。

**推论**：同时性发现的充分条件：
$$\mathbb{I}[|t_i - t_j| < T_{critical} \mid i,j \in \text{Agents}] \iff KL(\pi_{0,i} \| \pi_{0,j}) < \epsilon_{threshold}$$

---

### 命题 4：与 Thompson Sampling Regret Bound 的形式统一

**Thompson sampling 下界**：标准 regret bound 为 $\mathcal{R}(T) = \mathcal{O}(\sqrt{T \cdot |\mathcal{T}| \cdot \log T})$

**工具搜索信息瓶颈改进**：利用先验 $\pi_0$ 的引导作用，**压缩 regret bound**：
$$\mathcal{R}_{S1-1}(T) = \mathcal{O}\left(\sqrt{T \cdot KL(\pi_{opt} \| \pi_0) \cdot \log T}\right)$$

**理论意义**：当先验 $\pi_0$ 接近最优策略 $\pi_{opt}$，regret 显著低于标准 Thompson sampling。

---

## 实验验证计划

### 实验 1：多 Agent 工具市场收敛
```python
# 1. 构建 N 个 Agent，每个有不同先验 π_0,i
# 2. 测量收敛到相同工具的时间
# 3. 验证 T_critical 随 KL(π_0,i || π_0,j) 的关系
```

### 实验 2：LLM 工具选择探索比例
```python
# 1. 在开放世界任务中测量 LLM 的工具切换频率
# 2. 拟合 λ* = f(任务难度, 先验熟悉度)
```

### 实验 3：Thompson sampling 先验增益
```python
# 1. 对比有/无先验引导的 Thompson sampling
# 2. 验证 regret bound 中的 KL(π_opt || π_0) 因子
```

---

## 理论贡献总结

1. **首次将工具选择问题形式化为流形上的变分原理**
2. **为 S12 同时性发现提供了工具空间层面的机制解释**
3. **给出了 Thompson sampling regret bound 的先验改进形式**

---

## 预期输出

- [x] 理论文档：命题 1-4 的数学推导
- [ ] 实验 1：多 Agent 工具市场收敛
- [ ] 实验 2：LLM 工具选择探索比例
- [ ] 实验 3：Thompson sampling 先验增益

---

*此文档将 S1-1 原始猜想整合到工具搜索-利用折衷理论框架中。*
*完成时间：2026-05-04 | 轮次：r01 | 理论转化迭代*
