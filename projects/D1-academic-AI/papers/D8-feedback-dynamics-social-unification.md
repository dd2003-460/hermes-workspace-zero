# D8：正负反馈社会的分化-统一动力学

> **原始想法**：「压力（正反馈）导致的不稳定分化（噪声放大），引力（负反馈）导致稳定演化，迁移到社会各种分化和统一？」（raw.md #46）

---

## 0. 核心洞见

**分化（不同化/多样/破裂）**与**统一（凝聚/共识/同质化）**的社会动力学，对应于正/负反馈环路的相变行为。

**D8 断言**：社会系统中的分化-统一转变，本质上是**信号增益 $G$ 穿越临界值 $G_c = 1$ 时的系统稳态突变**。

---

## 1. 理论框架

### 1.1 反馈环路的基本动力学

**定义 D8-1（反馈算子）**：设系统状态 $x \in \mathbb{R}^n$ 演化服从：
$$\dot{x} = Ax + f_{\text{feedback}}(x) + \xi(t)$$

其中 $f_{\text{feedback}}(x) = \begin{cases} +G \cdot h(x) & \text{positive feedback} \\ -G \cdot h(x) & \text{negative feedback} \end{cases}$

**定义 D8-2（反馈符号）**：
- **正反馈**：$G > 0$ → **信号放大** → 可能导致**分化**
- **负反馈**：$G < 0$ → **信号抑制** → 可能导致**统一**

---

### 1.2 社会统一定义

**社会统一定理（SocUni-T1）**：
对于任何社会子群体，其**分化指数**：
$$\mathcal{D}[t] = \frac{1}{N} \sum_{i,j} \text{Var}(\theta_i - \theta_j | t)$$

满足演化方程：
$$\frac{d\mathcal{D}}{dt} = (G_+ - G_-) \cdot \mathcal{D} - \gamma \cdot \mathcal{D} + \sigma^2$$

其中：
- $G_+$：正反馈增益（信息扩散/偏见放大/回声室效应）
- $G_-$：负反馈增益（纠正/验证/共识形成）
- $\gamma$：自然耗散系数
- $\sigma^2$：外部噪声强度

---

## 2. 五个理论命题

### 命题 D8-1：社会分化临界增益定理

**形式化表述**：
存在临界增益比 $\rho_c = G_c^+/G_c^-$，使得：
$$\rho = \frac{G_+}{G_-} \begin{cases} > \rho_c & \implies \mathcal{D}[t] \to \infty \quad \text{（社会化分化）} \\ < \rho_c & \implies \mathcal{D}[t] \to \mathcal{D}^* < \infty \quad \text{（社会统一）} \end{cases}$$

**临界值计算**（在均衡态线性化）：
$$\rho_c = 1 + \frac{\gamma}{\lambda_{\max}(A_{\text{diff}})}$$

其中 $A_{\text{diff}}$ 为差分算子最大特征值。

---

### 命题 D8-2：正反馈相变 → 二级相变类比

**形式化表述**：
定义**社会序参量** $m = 1 - \mathcal{D}/\mathcal{D}_{\max}$，在 $\rho \to \rho_c$ 处：
$$m \sim |\rho - \rho_c|^{\beta}, \quad \chi_{\mathcal{D}} \sim |\rho - \rho_c|^{-\gamma_{\text{soc}}}$$

**临界指数预测**（平均场）：
- $\beta = \frac{1}{2}$（序参量平方根行为）
- $\gamma_{\text{soc}} = 1$（发散指数）

---

### 命题 D8-3：负反馈统一速率由耗散控制

**形式化表述**：
在统一区域（$\rho < \rho_c$），统一速率：
$$-\frac{d\mathcal{D}}{dt} \geq (\rho_c - \rho) \cdot \mathcal{D} - \sigma^2$$

**推论 D8-3a**：统一存在**最小充分噪声阈值**：
$$\sigma^2_{\min} = (\rho_c - \rho) \cdot \mathcal{D}_{\max}$$

低于此阈值，统一无法达到完美态（$\mathcal{D} = 0$）。

---

### 命题 D8-4：临界 slowing down（临界减慢）

**形式化表述**：
当系统接近 $\rho_c^-$ 时（从统一侧趋近），恢复时间：
$$\tau_{\text{relax}} = \frac{1}{\rho_c - \rho} \to \infty \quad \text{as } \rho \to \rho_c^-$$

**社会含义**：社会系统在被推过临界点产生分化后，即使**回调增益至统一区**，恢复速度也会极慢。

---

### 命题 D8-5：反馈不对称的不可逆性

**形式化表述**：
设 $\tau_h$ 为滞后时间（hysteresis loop），则：
$$\Delta \rho_{\text{hysteresis}} = \rho_{\text{divergence onset}} - \rho_{\text{convergence recovery}} > 0$$

**推论**：分化比统一更容易发生（$G_+^{\text{onset}} < G_-^{\text{recovery}}$），且**一旦分化，逆转需更强负反馈**。

---

## 3. 四组实验验证协议

### 协议 D8-A：回声室分化相变

**验证 D8-1 和 D8-2**：
1. 构建 Agent-Based Model：Agent 持有观点 $\theta_i \in [-1, 1]$
2. 正反馈规则：$\theta_i \leftarrow \theta_i + G_+ \cdot (\theta_j - \theta_i) \cdot \mathbb{I}(|\theta_i - \theta_j| < \delta)$（同质性吸引）
3. 负反馈规则：$\theta_i \leftarrow \theta_i - G_- \cdot (\theta_j - \theta_i) \cdot \mathbb{I}(|\theta_i - \theta_j| > \Delta)$（极端观点修正）
4. 扫描 $(G_+, G_-)$ 平面，绘制分化相图

**预期**：清晰的两相边界在 $\rho = \rho_c$ 处。

---

### 协议 D8-B：舆论极化临界减速

**验证 D8-4**：
1. 在统一区运行模拟，施加脉冲扰动 $\theta_i(t_0) \leftarrow \theta_i(t_0) + \epsilon$
2. 测量恢复时间 $\tau$ 随 $\rho_c - \rho$ 的变化
3. 验证：$\tau \propto (\rho_c - \rho)^{-1}$

---

### 协议 D8-C：反馈滞后环测量

**验证 D8-5**：
1. 从低 $\rho$（统一）开始，**缓慢增加** $\rho$ 至远高于 $\rho_c$
2. 记录分化 onset $\rho_{\uparrow}$
3. **缓慢减少** $\rho$ 至低于 $\rho_c$
4. 记录收敛恢复 $\rho_{\downarrow}$
5. 验证：$\rho_{\uparrow} > \rho_{\downarrow}$

---

### 协议 D8-D：最小统一噪声阈值

**验证 D8-3a**：
1. 固定 $\rho < \rho_c$，变化 $\sigma^2$
2. 测量最终分化指数 $\mathcal{D}^*$
3. 验证存在 $\sigma^2_{\min}$ 使得 $\mathcal{D}^* \to 0$

---

## 4. 与其他框架的关联

### 4.1 D9 框架关联

**D9-V 社会推论**：社会拓扑保真度 $\Phi_{\text{soc}}$ 由负反馈强度决定：
$$\Phi_{\text{soc}} = 1 - \frac{\mathcal{D}[\infty]}{\mathcal{D}_{\max}}$$

**D9 五条件社会扩展**：增加 $\mathcal{C}_{\text{feedback}}$（反馈平衡条件）：
$$\mathcal{C}_{\text{feedback}} \equiv \frac{G_-}{G_+ + G_-} > \rho_c^{-1}$$

---

### 4.2 S18 动力学关联

**社会 S18-泛函**：
$$\mathcal{F}_{\text{soc}}[\theta] = \underbrace{\sum_{i,j} K_{ij} |\theta_i - \theta_j|^2}_{\text{负反馈凝聚}} - \underbrace{G_+ \sum_{i,j} J_{ij} (\theta_i - \theta_j)^2 \mathbb{I}(|\theta_i - \theta_j| < \delta)}_{\text{正反馈分化}}$$

**社会均衡**：$\frac{\delta \mathcal{F}_{\text{soc}}}{\delta \theta_i} = 0 \iff \text{稳定社会态}$

---

### 4.3 历史周期率解释

**D8-历史周期率模型**：
- 王朝建立 → 强负反馈（建制完善，社会统一）
- 时间推移 → 正反馈累积（土地兼并、利益固化）
- $\rho \to \rho_c^+$ → **系统性崩溃**（分化）
- 王朝重建 → 回到强负反馈态
- 周期 $T_{\text{dynasty}} \approx \frac{1}{\lambda} \log\left(\frac{\rho_c - \rho_0}{\rho - \rho_c}\right)$

---

## 5. 理论界限

### 5.1 主要可证伪声明

1. **D8-1 证伪**：不存在社会系统的 $\rho_c$ 临界点
2. **D8-4 证伪**：社会恢复时间不随 $\rho \to \rho_c^-$ 发散
3. **D8-5 证伪**：分化-统一转变不可逆（无滞后环）

### 5.2 理论局限

1. 忽略**社会行动者主体性**（非被动动力学）
2. 未建模**空间异质性**（不同地理区域差异）
3. 反馈符号 $+/-$ 在实际社会中可能是**时间依赖**的

---

## 6. 最终定理陈述

### 社会分化-统一统一定理

**设**社会系统由 Agent 集合构成，个体观点演化受正/负反馈驱动：
$$\dot{\theta}_i = -G_- \sum_j w_{ij}(\theta_i - \theta_j) + G_+ \sum_k v_{ik}(\theta_i - \theta_k) \mathbb{I}(|\theta_i - \theta_k| < \delta) + \xi_i(t)$$

**则**：
$$\boxed{\frac{d\mathcal{D}}{dt} = (G_+ - G_-)\mathcal{D} - \gamma \mathcal{D} + \sigma^2 = 0 \iff \rho = \frac{G_+}{G_-} = \rho_c}$$

**即**：社会分化-统一转变等价于增益比穿越临界值 $G_c = 1$ 的一级相变。

---

*D8 理论文档完成。正负反馈动力学提供了理解社会分化与统一转变的统一理论框架，连接统计物理相变、控制理论与社会动力学。*
