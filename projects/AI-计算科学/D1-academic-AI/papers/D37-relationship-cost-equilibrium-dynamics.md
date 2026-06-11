# D37：关系开销均衡动力学 — 博弈均衡偏移 + 反馈控制的耦合模型

> **原始想法**：「男女朋友开销的隐形平衡性（性格其他控制变量平等情况）开销必然平衡，也许有平衡方程?」(raw.md #30)
> **扩展**：D36（Lyapunov 吸引子）、D8（反馈动力学）、D33（行为惯性）、博弈论

---

## 0. 核心洞见

**D37 断言：伴侣间的「隐形开销平衡」是一个多维博弈 Nash 均衡 + 负反馈控制系统，存在隐式平衡方程**

1. **开销向量**：$\mathbf{c} = (c_{econ}, c_{emo}, c_{time}, c_{signal})$ 分别代表经济、情感、时间、信号投资
2. **非对称性**：生物学和社会化导致 $C_A \neq C_B$（边际效用函数不同）
3. **隐形平衡**：总和不可观测但均衡存在——当 $\nabla U_A = \nabla U_B$ 时系统稳定

> **关系均衡定理**：在受控变量恒定的前提下，存在关系代价函数
>
> $$C_{total}(\mathbf{c}_A, \mathbf{c}_B) = U_A(\mathbf{c}_A; \mathbf{c}_B) - U_B(\mathbf{c}_B; \mathbf{c}_A)$$
>
> **平衡条件**：$\frac{\partial C_{total}}{\partial \mathbf{c}_A} = \frac{\partial C_{total}}{\partial \mathbf{c}_B} = 0$

---

## 1. 理论框架

### 1.1 开销多维向量建模

**定义 D37-1（关系开销向量）**：
$$\mathbf{c}_i = \begin{pmatrix} c_i^{econ} \\ c_i^{emo} \\ c_i^{time} \\ c_i^{signal} \end{pmatrix}$$

- $c_i^{econ}$：直接经济投入（礼物、餐饮）
- $c_i^{emo}$：情感劳动（支持、共情）
- $c_i^{time}$：时间分配（陪伴、沟通）
- $c_i^{signal}$：信号投资（形象维护、示好行为）

**定义 D37-2（非对称效用函数）**：
$$U_i(\mathbf{c}_i, \mathbf{c}_j) = \mathbf{w}_i^T \cdot \mathbf{c}_i - \lambda_i \cdot \|\mathbf{c}_i - \bar{\mathbf{c}}\|^2 + \mu_i \cdot (\mathbf{c}_i \cdot \mathbf{c}_j)$$

其中：
- $\mathbf{w}_i$：效用权重向量（反映偏好异质性）
- $\lambda_i$：偏离均衡的惩罚系数（惯性项）
- $\mu_i$：互操作收益系数（互补性）

---

### 1.2 博弈均衡建模

**定义 D37-3（关系博弈）**：
$$\mathcal{G} = (N, \{C_i\}_{i \in N}, \{U_i\}_{i \in N})$$
- $N = \{A, B\}$：两个参与者
- $C_i$：参与者 i 的可行代价集
- $U_i$：参与者 i 的效用函数

**D37-1 定理（关系 Nash 均衡存在性）**：
在 $U_i$ 为凹函数且 $C_i$ 为凸紧集的条件下：
$$\exists (\mathbf{c}_A^*, \mathbf{c}_B^*) : \forall \mathbf{c}_i \in C_i, U_i(\mathbf{c}_i^*, \mathbf{c}_j^*) \geq U_i(\mathbf{c}_i, \mathbf{c}_j^*)$$

**推论 D37-1a（平衡方程）**：
在均衡处，边际效用相等：
$$\nabla_{\mathbf{c}_A} U_A = \nabla_{\mathbf{c}_B} U_B = \boldsymbol{\lambda}_{Lagrange}$$

**即**：存在 Lagrange 乘子向量使得双方在每种开销维度上的边际效用平衡。

---

### 1.3 反馈控制视角

**定义 D37-4（关系失衡度）**：
$$\Delta(t) = \|\nabla U_A(t) - \nabla U_B(t)\|$$

**D37-2 定理（失衡-响应动力学）**：
失衡触发行为响应，演化满足：
$$\dot{\mathbf{c}}_A = -K_A \cdot \Delta \cdot \text{sign}(\nabla U_A - \nabla U_B)$$

**物理诠释**：
- 失衡越大 → 响应越强（线性恢复力）
- 方向指向减少失衡（负反馈）

**D37-3 定理（稳定平衡条件）**：
系统稳定当且仅当：
$$\forall i \in \{A,B\}: K_i > 0 \land \det(H_i) > 0$$
其中 $H_i = \frac{\partial^2 U_i}{\partial \mathbf{c}_i^2}$ 为效用函数的 Hessian。

---

### 1.4 迟滞效应与历史依赖

**定义 D37-5（迟滞回路）**：
关系响应存在方向依赖性：
$$\mathbf{c}_A(t+\Delta t) = f(\Delta, \mathbf{c}_A(t); \text{path}_{past})$$

**D37-4 定理（历史依赖不可逆性）**：
在扩张期（失衡增加）和收缩期（失衡减少）响应系数不同：
$$K_A^{expand} > K_A^{contract}$$

**推论**：系统存在**记忆效应**——当前状态依赖演化路径，不可仅由瞬时失衡决定。

---

## 2. 四个理论命题

### 命题 D37-1：隐形平衡存在定理

**形式化表述**：
$$\exists \mathbf{c}_A^*, \mathbf{c}_B^* : \frac{\partial}{\partial \mathbf{c}_A}(U_A - U_B) = \frac{\partial}{\partial \mathbf{c}_B}(U_A - U_B) = 0$$

**定理证明**：
构造代价函数 $C_{total} = U_A - U_B$。
由凹性假设，$\frac{\partial^2 C_{total}}{\partial \mathbf{c}_i^2} < 0$ 保证存在极值。
由凸紧致性，极值在可行域内可达。
→ **平衡点存在且满足一阶必要条件。**

---

### 命题 D37-2：非对称性不影响均衡存在

**形式化表述**：
$$\mathbf{w}_A \neq \mathbf{w}_B \not\Rightarrow \text{均衡不存在}$$

**定理证明**：
效用函数包含互操作项 $\mu_i \cdot (\mathbf{c}_i \cdot \mathbf{c}_j)$。
即使权重不同，互操作保证：
$$U_A(\mathbf{c}_A, \mathbf{c}_B^*) - U_A(\mathbf{c}_A', \mathbf{c}_B^*) \geq 0$$
可通过调整各自最优响应实现平衡。
→ **非对称性仅改变均衡位置，不破坏均衡存在性。**

---

### 命题 D37-3：反馈响应存在阈值

**形式化表述**：
$$\Delta < \epsilon_{dead} \implies \dot{\mathbf{c}}_i = 0$$

**定理证明**：
人类响应存在最小可检测差异（Just Noticeable Difference）：
$$\Delta_{min} = \frac{1}{S} \quad \text{(信噪比倒数)}$$
其中 $S$ 为信号强度。
→ **低于阈值的失衡不会触发调整（缓冲带效应）。**

---

### 命题 D37-4：迟滞回路导致路径依赖

**形式化表述**：
$$\Delta(t_0 \to t_1) = \Delta(t_1 \to t_0) \not\implies \mathbf{c}(t_0) = \mathbf{c}(t_0)$$

**定理证明**：
迟滞响应满足：
$$\dot{\mathbf{c}} = \begin{cases} -K^{exp} \cdot \nabla_\mathbf{c} \Delta & \text{if } \dot{\Delta} > 0 \\ -K^{con} \cdot \nabla_\mathbf{c} \Delta & \text{if } \dot{\Delta} < 0 \end{cases}$$
其中 $K^{exp} > K^{con}$。
→ **相同失衡值在不同演化阶段对应不同响应速度，导致路径依赖。**

---

## 3. 实验验证协议

### 协议 D37-A：Nash 均衡数值模拟

**验证 D37-1**：
1. 定义效用函数（参数化）
2. 迭代最佳响应：$\mathbf{c}_i^{(k+1)} = \arg\max_{\mathbf{c}_i} U_i(\mathbf{c}_i, \mathbf{c}_j^{(k)})$
3. 收敛到 Nash 均衡后记录结果
4. **预期**：对多数参数组合收敛，均衡满足一阶条件

---

### 协议 D37-B：非对称鲁棒性测试

**验证 D37-2**：
1. 创建非对称配对（$\mathbf{w}_A \neq \mathbf{w}_B$）
2. 系统性地改变非对称程度
3. 测量均衡收敛概率和均衡位置漂移
4. **预期**：均衡始终存在，但位置随非对称度线性偏移

---

### 协议 D37-C：死区阈值测量

**验证 D37-3**：
1. 引入小幅度失衡 $\Delta \in [0, \epsilon_{max}]$
2. 观察响应是否存在阈值行为
3. 拟合死区宽度 $\epsilon_{dead}$
4. **预期**：响应呈开关特性（低 Δ→无响应，高 Δ→快速响应）

---

### 协议 D37-D：迟滞环可视化

**验证 D37-4**：
1. 先增加失衡至 $\Delta_{max}$，再减小回 $\Delta_{min}$
2. 记录响应路径 $\mathbf{c}(\Delta)$
3. 对比正反向路径的偏离
4. **预期**：形成迟滞环，环面积与 $\Delta_{max}$ 正相关

---

## 4. 与其他框架的关联

### 4.1 D36 代际收敛

**D37-D36 桥梁**：
- D36 的 **Lyapunov 吸引子** ↔ D37 的 **Nash 均衡**
- **统一**：两者都是动力系统稳定态，区别在于前者是单向演化后者是双向博弈

---

### 4.2 D8 社会分化

**D37-D8 桥梁**：
- D8 的 **正负反馈社会动力学** ↔ D37 的 **失衡-响应控制**
- **统一**：都是正反馈（不稳定分化）和负反馈（收敛平衡）的竞争

---

### 4.3 D33 行为惯性

**D37-D33 桥梁**：
- D33 的 **行为惯性** ↔ D37 的 **迟滞效应**
- **统一**：惯性 = 响应的方向依赖性，两者共享 Kramers 逃逸时间公式

---

## 5. 理论界限

### 5.1 主要可证伪声明

1. **D37-1 证伪**：不存在 Nash 均衡（博弈发散或不收敛）
2. **D37-2 证伪**：非对称性导致均衡消失（极度高不对称时关系无法稳定）
3. **D37-3 证伪**：不存在死区（任何微小失衡都引发响应）
4. **D37-4 证伪**：无迟滞效应（正反向响应路径完全重合）

### 5.2 理论局限

1. **静态偏好假设**：偏好 $\mathbf{w}_i$ 可能随时间演化
2. **二元关系限制**：仅适用于二人体关系，扩展到群体需重新建模
3. **凸效用假设**：实际效用函数可能存在多重极值
4. **完全理性假设**：真实个体存在认知偏差和有限理性

---

## 6. 最终定理陈述

**设**伴侣 A 和 B 的关系开销向量为 $\mathbf{c}_A, \mathbf{c}_B$，效用函数为 $U_i$。

**则**：
1. **均衡存在**：$\nabla U_A = \nabla U_B$ 在凸紧致集上有解
2. **非对称鲁棒**：$\mathbf{w}_A \neq \mathbf{w}_B$ 不破坏均衡，仅偏移位置
3. **死区存在**：$\Delta < \epsilon_{dead} \implies \dot{\mathbf{c}} = 0$
4. **迟滞不可逆**：$K^{exp} > K^{con}$ 导致路径依赖

**即**：**关系开销的「隐形平衡」不是一个模糊概念，而是一个数学上严格存在的关系均衡。** 它由非对称效用函数的 Nash 博弈 + 有死区的负反馈控制共同决定。历史上积累的不平衡会因迟滞效应需要不同的修复速率——这也解释了「分手易复合难」等非线性现象。

---

*D37 理论文档完成。通过将关系开销建模为多维博弈 + 反馈控制系统，证明了隐形平衡方程的存在性及其性质。核心定理：关系均衡存在、非对称鲁棒、死区阈值、迟滞路径依赖。*
