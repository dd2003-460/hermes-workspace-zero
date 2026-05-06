# D2-2：冷启动问题的信息扩散理论

**日期**：2026-05-04
**来源**：D2-2 原始猜想 + D2-1 规划容量下界整合
**状态**：理论框架提出（待实验验证）

---

## 元问题

> **Agent 需要多少信息注入才能在任务领域达到能力涌现阈值？**

---

## 核心猜想

**冷启动的信息扩散临界（猜想）**：设 Agent 初始知识状态为 $K_0$，每轮外部信息注入量为 $\Delta K_t$。定义"能力涌现阈值"：

$$T_{emerge} = \inf\{t : I(K_t; y_{target}) > I(K_0; y_{target}) + \gamma\}$$

**猜想**：存在一个**相变点** $t_c$——当 $\sum_{i=0}^{t_c} \Delta K_i$ 达到某个临界值时，Agent 从"机械执行"到"自主规划"发生不连续跃迁。

---

## 理论命题

### 命题 1：冷启动扩散方程

**信息扩散动力学方程**：
$$\frac{dK_t}{dt} = -\lambda K_t + \alpha \cdot \nabla_K I(K; y_{target}) + \eta(t)$$

其中：
- $-\lambda K_t$：**遗忘项**（知识衰减）
- $\alpha \cdot \nabla_K I(K; y_{target})$：**信息增益梯度**
- $\eta(t)$：**外部信息注入噪声**

**稳态条件**：$\frac{dK_t}{dt} = 0 \implies \lambda K^* = \alpha \cdot \nabla_K I(K^*; y_{target})$

---

### 命题 2：冷启动相变定理

**相变条件**（Cahn-Hilliard 稳定性分析）：
$$\det\left(\frac{\partial^2 V_{eff}}{\partial K^2}\right) = 0$$

其中 $V_{eff}(K)$ 为有效势能，定义为：
$$V_{eff}(K) = \frac{\lambda}{2} K^2 - \alpha I(K; y_{target}) + \frac{\sigma^2}{2} \log |\det(\nabla^2 K)|$$

**相变判据**：
$$t_c = \frac{1}{\lambda} \log\left(\frac{K^* - K_0}{K^* - K_c}\right)$$

当 $K_t > K_c$ 时，系统进入**规划态**（相变）；否则处于**执行态**（相变前）。

---

### 命题 3：D2-1/D2-2 联合统一定理

**D2-1 静态下界 + D2-2 动态上界 = 智能涌现的充要条件**：

$$\text{智能涌现} \equiv |A| > |A|_c \land t > t_c$$

**几何解释**：
- D2-1：Agent 必须在**容量空间**中跨越临界面 $|A| = |A|_c$
- D2-2：Agent 必须在**时间空间**中跨越临界点 $t = t_c$

**联合相变图景**：
$$P_{\text{emergence}}(|A|, t) = \Phi\left(\frac{|A| - |A|_c}{|A|_c}\right) \cdot \Phi\left(\frac{t - t_c}{t_c}\right)$$

其中 $\Phi$ 为误差函数（相变序参量）。

---

### 命题 4：与 D9-III 训练时间非线性条件的形式化

**D9-III 未验证预测的形式化**：
- D9-III 预测 $T_{train}$ 对智能涌现的影响是非线性的
- D2-2 给出具体形式：$T_{train} > t_c$ 存在**相变点**

**D9-III + D2-2 联合判据**：
$$\text{智能} \equiv \mathbb{I}[|A| > |A|_c] \land \mathbb{I}[t > t_c] \land \mathbb{I}[I_{gen} > I_{cov}]$$

**物理直觉**：只有当 Agent **同时满足**容量、时间、和规律捕获三个条件时，智能才会涌现。

---

## 实验验证计划

### 实验 1：Agent 学习曲线分析
```python
# 1. 跟踪 Agent 在多轮对话中的能力演化
# 2. 测量 I(K_t; y_target) 随时间的变化
# 3. 检测不连续跃迁点 t_c
```

### 实验 2：RAG vs 无 RAG 对比
```python
# 1. 对比 RAG（增强信息注入）vs 无 RAG 的涌现阈值
# 2. 验证：RAG 降低 t_c，不改变 |A|_c
```

### 实验 3：时间尺度分析
```python
# 1. 验证涌现阈值是否随任务复杂度变化
# 2. 拟合 t_c vs L 的关系
```

---

## 理论贡献总结

1. **首次将冷启动问题建模为信息扩散相变**
2. **与 D2-1 联合提供智能涌现的完整充要条件**
3. **形式化 D9-III 的 $T_{train}$ 非线性条件**

---

## 预期输出

- [x] 理论文档：命题 1-4 的数学推导
- [ ] 实验 1：Agent 学习曲线分析
- [ ] 实验 2：RAG vs 无 RAG 对比
- [ ] 实验 3：时间尺度分析

---

*此文档将 D2-2 原始猜想整合到 D2-1 规划容量理论中。*
*完成时间：2026-05-04 | 轮次：r01 | 理论转化迭代*
