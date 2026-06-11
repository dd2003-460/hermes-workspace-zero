# D3-1: 频率-动力学对偶理论

## 来源
转化自：
- raw/math_social_cross.md (1): 频率最优化理论（预先规划）
- raw/math_social_cross.md (18): 动态演化、动力学、泛函

## 核心猜想

**频率-动力学对偶定理（猜想）**：设决策者面对问题空间 $\mathcal{X}$，在时间窗口 $[0, T]$ 内以频率函数 $\omega: \mathcal{X} \to \mathbb{R}^+$ 探索。定义"预规划代价泛函"：

$$J[\omega] = \int_0^T \left(\alpha \cdot \text{search\_cost}(\omega(t)) + \beta \cdot (1-\text{quality}(\omega(t)))\right) dt$$

**猜想**：该变分问题的Euler-Lagrange方程等价于一个**具有记忆项的阻尼振荡系统**——这解释了为什么人类/Agent在探索时表现出"过冲-回调"行为。

## 物理直觉

**关键洞察**：你的"找刀/砍柴"直觉对应到一个经典物理问题——最优搜索路径。

**标准结果**：最优搜索的最小时间 $T^*$ 满足：
$$T^* \propto \frac{\sqrt{A}}{v}$$

其中 $A$ 为搜索区域面积，$v$ 为移动速度。

**你的扩展**：如果加上"磨刀成本"（工具切换成本）和"信息获取价值"，最优频率 $\omega^*$ 的演化方程是什么？

## 数学形式化

**Euler-Lagrange方程（猜想）**：
$$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\omega}}\right) - \frac{\partial \mathcal{L}}{\partial \omega} + \int_0^t \mu(t-\tau)\dot{\omega}(\tau)d\tau = 0$$

其中记忆核 $\mu(t)$ 编码"先验经验的衰减"。

**与已有连接**：
- 这解释了D9-18中"自适应粗细度"的数学本质
- 与Cahn-Hilliard方程有相同的记忆项结构

## 可验证性

1. **人类行为拟合**：用真实用户在StackOverflow/Arxiv上的行为数据拟合这个系统
2. **Agent模拟**：在虚拟环境中验证记忆项的存在必要性
3. **理论证明**：搜索速度-准确性权衡的数学下界

## 方法论创新点

这不是单纯的"探索-利用"框架——**加入记忆项是核心创新**。标准汤普森采样/epsilon-greedy没有记忆效应。

---
*Created: 2026-04-29 | Status: Conjecture — Requires behavioral data collection and fitting*
