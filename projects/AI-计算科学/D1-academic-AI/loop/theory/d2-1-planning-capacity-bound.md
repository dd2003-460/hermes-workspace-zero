# D2-1: Agent规划容量下界 — 理论推导

## 1. 问题形式化

### 1.1 基本设定

**定义1（规划任务）**：一个规划任务 $t \in \mathcal{T}$ 由三元组 $(S_t, A, T_t)$ 定义：
- $S_t$：状态空间
- $A$：动作空间（全局共享）
- $T_t: S_t \times A \to S_t$：转移函数

**定义2（规划序列）**：对于任务 $t$ 和目标状态 $s^*_t$，一个长度为 $L$ 的规划序列是 $\pi = (a_1, a_2, \ldots, a_L)$ 其中 $a_i \in A$。

**定义3（规划成功）**：令 $s_0$ 为初始状态，$s_{i+1} = T_t(s_i, a_i)$。规划 $\pi$ 成功当且仅当 $d(s_L, s^*_t) < \epsilon$。

### 1.2 Agent模型

**定义4（规划Agent）**：一个规划Agent $A_\theta$ 由映射 $\phi_\theta: \mathcal{T} \times S_0 \to \Delta(A^L)$ 定义，其中 $\Delta$ 表示概率分布。

**关键假设（因果链）**：规划过程遵循以下马尔可夫结构：
$$\mathcal{T} \xrightarrow{\text{理解}} Z_{task} \xrightarrow{\text{规划}} Z_{plan} \xrightarrow{\text{执行}} (a_1, \ldots, a_L)$$

其中 $Z_{task}$ 是任务表征，$Z_{plan}$ 是规划内部状态。

---

## 2. 主要定理推导

### 定理1（规划容量下界）

**设定**：
- 任务空间 $\mathcal{T}$ 上的分布 $p(t)$
- 对于每个任务 $t$，成功规划的概率需求：$\mathbb{P}(\text{success}|t) \geq 1 - \delta$
- Agent的规划映射 $\phi_\theta$ 通过中间表示 $Z_{plan}$

**结论**：
$$|Z_{plan}| \geq I(Z_{task}; \mathcal{T}) + \Omega\left(\frac{H(\mathcal{T}|\text{success})}{L}\right)$$

其中 $|Z_{plan}|$ 表示规划内部状态的有效自由度。

**证明**：

**引理1（数据处理的因果约束）**：对于马尔可夫链 $\mathcal{T} \to Z_{task} \to Z_{plan} \to \hat{\pi}$，
$$I(\mathcal{T}; \hat{\pi}) \leq I(Z_{task}; \mathcal{T})$$

*证明*：由数据处理不等式直接可得。$\square$

**引理2（成功规划的必要性）**：若 $\mathbb{P}(\text{success}|t) \geq 1-\delta$，则
$$I(\mathcal{T}; \hat{\pi}) \geq H(\mathcal{T}) - H(\mathcal{T}|\text{success})$$

*证明思路*：成功意味着 $\hat{\pi}$ 必须编码足够的任务信息来区分不同任务的解决方案。形式化地：
$$H(\mathcal{T}) = H(\mathcal{T}|\text{success}) + I(\mathcal{T}; \mathbb{1}_{\text{success}})$$
当 $\delta$ 小时，$\mathbb{1}_{\text{success}} \approx f(\hat{\pi}, \mathcal{T})$，因此 $I(\mathcal{T}; \hat{\pi})$ 必须补偿信息损失。$\square$

**定理1证明**：结合引理1和2，
$$I(Z_{task}; \mathcal{T}) \geq I(\mathcal{T}; \hat{\pi}) \geq H(\mathcal{T}) - H(\mathcal{T}|\text{success})$$

对于 $Z_{plan}$，注意到规划序列长度 $L$ 限制了每步可传递的信息量：
$$I(Z_{plan}; \hat{\pi}) \leq L \cdot \log|A|$$

因此要传递足够的任务信息：
$$|Z_{plan}| \geq I(Z_{task}; \mathcal{T}) + \frac{H(\mathcal{T}|\text{success}) - L\log|A|}{L}$$

整理得证。$\square$

---

### 定理2（临界规模相变）

**设定**：
- Agent参数空间维度 $d = |\theta|$
- 有效表征容量 $|Z_{plan}| \leq c \cdot d^\alpha$（$\alpha \in [0.5, 1]$ 为效率指数）
- 任务复杂度参数 $\kappa(t) = I(Z_{task}; t)$

**结论**：存在临界规模 $d_c$ 使得
$$\mathbb{P}(\text{generalization}) = \begin{cases} 
o(1) & d < d_c - \omega(d^{-\beta}) \\
1 - o(1) & d > d_c + \omega(d^{-\beta})
\end{cases}$$

其中 $d_c = \frac{I_{plan}^*}{c}$，$I_{plan}^* = \sup_t \kappa(t)$。

**证明思路**：

1. **下界（不足则失败）**：当 $d < d_c$ 时，$|Z_{plan}| \leq c \cdot d^\alpha < I_{plan}^*$，由定理1无法覆盖最坏情况任务。

2. **上界（足够则成功）**：当 $d > d_c$ 时，利用集中不等式——高维参数空间中随机初始化的Agent以高概率覆盖大部分任务流形。

3. **相变sharpness**：由Talagrand集中不等式，高维随机过程的偏差以 $e^{-c \cdot d}$ 衰减，导致相变宽度 $\sim d^{-\beta}$。$\square$

---

## 3. 与Grokking的联系

### 命题1（规划Grokking机制）

**陈述**：设 $L_{train}$ 为训练损失，$L_{test}$ 为测试损失。当 $d \approx d_c$ 时，存在延迟泛化现象：
$$L_{train} \to L^* \text{（早）} \quad \text{但} \quad L_{test} \to L^* \text{（晚，当 } d > d_c\text{）}$$

**机制解释**：
- **阶段I（$d < d_c$）**：Agent学习记忆训练样本的"捷径"——统计拟合而非真正规划
- **阶段II（$d > d_c$）**：容量足够支持真正的规划表征 $Z_{plan}$，泛化突然发生

**数学结构**：这与自注意力网络的相变行为一致——当 $d$ 超过某个阈值，注意力机制从"最近邻检索"切换到"泛化推理"。

---

## 4. 可计算量与实证预测

### 4.1 规划信息估计

**定义5（可观测规划互信息）**：通过行为数据估计
$$\hat{I}_{plan} = \sup_{f,g} \text{MI}(f(\text{task}), g(\pi))$$

其中 $f, g$ 为可观测函数的选择空间。

**猜想1（下界可达性）**：存在最优函数对 $(f^*, g^*)$ 使得
$$\hat{I}_{plan}(f^*, g^*) \geq (1 - \epsilon) I_{plan}^*$$

### 4.2 实证预测清单

| 预测 | 方向 | 可检验方式 |
|------|------|------------|
| P1 | 规划成功率 vs 模型规模 | 阶梯函数，非S形 |
| P2 | $d_c$ vs 任务空间维度 | $d_c \propto \dim(\mathcal{T})^{1/\alpha}$ |
| P3 | Grokking延迟 $\tau$ vs 容量缺口 | $\tau \sim (d_c - d)^{-\gamma}$ |
| P4 | 中间层表征的任务区分度 | 线性探针准确率在 $d_c$ 处跃迁 |

---

## 5. 开放问题

1. **$\alpha$ 的界**：对于Transformer架构，$\alpha \leq 1$ 是否严格成立？
2. **任务结构的影响**：若 $\mathcal{T}$ 具有流形结构（而非离散集合），下界如何修正？
3. **元规划容量**：Agent能否通过训练增加 $c$（表征效率）？
4. **$\delta_{margin}$ 的普适性**：10%冗余是否跨领域成立？

---
*推导完成: 2026-04-30 | Status: Theorem sketch — needs rigorous proof verification*
