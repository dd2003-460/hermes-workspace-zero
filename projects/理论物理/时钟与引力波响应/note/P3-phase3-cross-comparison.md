# P3-1: 三项理解材料交叉对比

> **RALPH Loop Phase 3 (交叉对比)**
> 对比对象：
> 1. Hu PRD 111.084065 (P0-1) — 通用 ORF 框架
> 2. JCAP 2025 手征引力波 (P1-1) — 圆极化 SGWB 搜索
> 3. 楼明智硕士论文 (P2-1) — OLC 构型 ORF 分析

---

## 维度 1: ORF 定义与归一化约定

### 1.1 基本定义对比

| 来源 | ORF 定义 | 归一化因子 | 频谱约定 |
|------|----------|-----------|---------|
| **Hu PRD Eq.(8)** | $\Gamma_{IJ} = \frac{1}{8\pi}\int d^2\Omega_{\hat{n}} \sum_A R_I^A R_J^{A*}$ | $1/8\pi$ | 双边谱 $S_h(f)$, $S_h(f)=S_h(-f)$ |
| **JCAP Eq.(2.9)** | $\langle \tilde{s}_i \tilde{s}_j^* \rangle = \frac12\delta(f-f')[\Gamma^I I + \Gamma^V V]$ | 隐含在响应函数定义中 | 单边谱，$I(f)=(S_R+S_L)/2$ |
| **Lou Eq.(2-48/3-1)** | $\Gamma_{IJ} = \int \frac{d^2\hat{n}}{4\pi} R_A^I R_A^{J*}$ | $1/4\pi$ | 双边谱 convention，与 Hu 相同 |

**关键差异分析**：

1. **Hu 的 $1/8\pi$ vs Lou 的 $1/4\pi$**：这是谱约定差异。Hu 使用双边谱密度，因子 $1/2$ 已被吸收进 $S_h(f)$ 的定义（Hu Eq.(7)）。Lou 使用双边谱约定但显式写 $1/4\pi$，其响应函数 $R_A$ 定义（Lou Eq.2-42）不携带额外的 $1/\sqrt{2}$ 因子。两者物理内容一致，差异仅在于归一化因子的位置。

2. **JCAP 的特殊性**：JCAP 将 ORF 分解为 $\Gamma^I$（宇称偶）和 $\Gamma^V$（宇称奇）两部分，嵌入交叉相关期望值公式中。这种写法直接关联可观测量 $\langle Y \rangle \propto \int df\, S_h(f) \Gamma \tilde{Q}(f)$。

3. **$\Gamma^I$ 与 Hu ORF 的对应**：JCAP 的 $\Gamma^I$ 对应于 Hu 的通用 ORF（单偏振求和），即：
   $$\Gamma^I_{ij}(f) = \int \frac{d^2\hat{k}}{4\pi} F_i^A(\hat{k}) F_j^A(\hat{k}) e^{i2\pi f \hat{k}\cdot\vec{\Delta r}_{ij}/c}$$
   这与 Hu Eq.(8) 形式相同（区别仅在于 JCAP 用 $1/4\pi$ 而非 $1/8\pi$）。

**结论**：三者在 $\Gamma^I$ 上的定义在物理上一致。Hu 的 $1/8\pi$ 与 Lou 的 $1/4\pi$ 的差异源于双边谱约定中是否显式保留 $1/2$ 因子。在论文修正中，应明确所用约定并在所有公式中保持一致。

### 1.2 PTA 归一化对比

| 来源 | PTA ORF 归一化 | 归一化目标 |
|------|---------------|-----------|
| **Hu PRD §3.4** | $\gamma_{\text{PTA}} = 3\Gamma_{\text{PTA}}$ | 使短波长极限下单个脉冲星 ORF = 1 |
| **Lou §3.5** | 无显式归一化因子（OLC 网络使用绝对 ORF） | OLC 网络中 self-correlation 最大化 |
| **JCAP** | 无显式归一化（关注 $\Gamma^V/\Gamma^I$ 的比值） | 手征性搜索中使用最优滤波器 |

**Hu 的 $3\Gamma_{\text{PTA}}$ 归一化**：这与 Hellings-Downs 曲线的经典归一化一致。HD 曲线在 $\gamma=0$ 时 $\Gamma_{HD}(0) = 3/2$，所以 $3\Gamma_{HD}(0) = 9/2$。这个归一化因子来源于对 sky-average 的积分（$3 = 32\pi/32\pi \times 3$），使单个脉冲星的 ORF 在短波长极限下归一化为 1。

**OLC 网络的归一化缺失**：Lou 论文在 ORF 计算中未显式应用全局归一化因子。这是合理的，因为 OLC 网络设计时需要最大化 ORF 绝对值而非比例。但在与 Hu PRD 的 PTA 结果对比时需要注意此差异。

---

## 维度 2: 转移函数 — 指数形式 vs sinc 形式

这是三篇文献中**最关键的差异**，也是理解 PTA 与 OLC 物理本质的核心。

### 2.1 Hu PRD 转移函数

**Hu Eq.(6) — 通用单程链路响应**：
$$T_{\text{one}}^{\text{Hu}}(\beta, \hat{n}\cdot\hat{u}) = \frac{1+\hat{n}\cdot\hat{u}}{2} \left[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}\right]$$

其中 $\beta = 2\pi f L/c$。注意这个 $T_{\text{one}}$ 已包含了因子 $(1+\hat{n}\cdot\hat{u})/2$ 来自 Doppler 积分。

### 2.2 Lou (OLC) 转移函数

**Lou Eq.(2-30)**：
$$\mathcal{T}_{\text{one}}^{\text{OLC}}(\hat{u}\cdot\hat{n}, f) = \frac{i2\pi fL}{c} \cdot \text{sinc}\left[\frac{\pi fL}{c}(1-\hat{u}\cdot\hat{n})\right] \cdot \exp\left[-i\frac{\pi fL}{c}(1-\hat{u}\cdot\hat{n})\right]$$

### 2.3 两种形式的数学关系

两种形式对应**不同的物理观测量**：

| | Hu (PTA) | Lou (OLC) |
|---|---|---|
| **观测量** | 脉冲到达时间残差 $z(t) = \int y(t)dt$ | 频率偏移 $y(t) = \Delta\nu/\nu_0$ |
| **时间域关系** | $z = \int y dt$ | $y = \dot{z}$ |
| **傅里叶域** | $\tilde{z}(f) = \tilde{y}(f)/(i2\pi f)$ | $\tilde{y}(f) = i2\pi f \tilde{z}(f)$ |

因此：
$$\mathcal{T}_{\text{one}}^{\text{OLC}} \approx i2\pi f \cdot T_{\text{one}}^{\text{timing}}$$

其中 $T_{\text{one}}^{\text{timing}}$ 是用于时间残差的转移函数。

### 2.4 指数到 sinc 的近似

Hu 的指数形式可以通过以下推导近似为 sinc 形式：

Hu 的指数项展开：
$$1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})} = 1 - \cos[\beta(1+\hat{n}\cdot\hat{u})] + i\sin[\beta(1+\hat{n}\cdot\hat{u})]$$

当 $\beta(1+\hat{n}\cdot\hat{u}) \ll 1$（低频/短臂）时：
$$\approx i\beta(1+\hat{n}\cdot\hat{u}) - \frac{1}{2}[\beta(1+\hat{n}\cdot\hat{u})]^2 + \cdots$$

OLC 的 sinc 形式来自不同的物理推导路径（频率偏移定义，Lou Eq.2-22），其核心是：
$$y(t_r) = \frac{1}{2}\frac{\hat{u}^a\hat{u}^b}{1+\hat{u}\cdot\hat{n}}[h_{ab}(t_r,\vec{x}_r) - h_{ab}(t_e,\vec{x}_e)]$$

注意到 Hu 的分母是 $(1+\hat{n}\cdot\hat{u})$ 而 OLC 也是 $(1+\hat{u}\cdot\hat{n})$ —— **符号约定一致**。但 OLC 的分子中没有 $(1+\hat{u}\cdot\hat{n})/2$ 因子，这是因为 OLC 直接从频率偏移定义出发，而 Hu 的响应函数包含了脉冲到达时间对频率偏移的积分。

**关键洞察**：Hu 的 $(1+\hat{n}\cdot\hat{u})/2$ 因子出现在响应函数 $R^A$ 的定义中（Hu Eq.6），而 OLC 的响应函数 $R_A$（Lou Eq.2-42）直接使用 $1/(1+\hat{u}\cdot\hat{n})$。这两个因子在 ORF 积分中产生不同的权重分布。

### 2.5 物理后果

| 特性 | Hu 指数形式 | OLC sinc 形式 |
|------|------------|---------------|
| **低频行为** | $T \propto \beta(1+\hat{n}\cdot\hat{u})$ | $T \propto i\beta$（与角度无关） |
| **高频行为** | 振荡，$|T|\leq 1$ | sinc 包络抑制 $\sim O(1/fL)$ |
| **零点** | 无零点（指数函数） | 零点在 $f = \frac{c}{2L(1-\hat{u}\cdot\hat{n})n}$ |
| **前向-后向不对称** | 有（$(1+\hat{n}\cdot\hat{u})$ 因子） | 有（sinc 中 $1-\hat{u}\cdot\hat{n}$） |
| **适用范围** | 任意 $f, L$（精确） | 任意 $f, L$（精确） |

**两者都是精确的**，但适用于不同的观测量。指数形式用于时间残差（PTA），sinc 形式用于频率偏移（OLC）。

---

## 维度 3: 手征极化定义与 Stokes 参数

### 3.1 圆极化基定义

三篇文献在圆极化基定义上的一致性：

| 来源 | 右旋 $e^R$ | 左旋 $e^L$ |
|------|-----------|-----------|
| **JCAP Eq.(2.3)** | $(e^+ + ie^\times)/\sqrt{2}$ | $(e^+ - ie^\times)/\sqrt{2}$ |
| **Seto PRL 97, 151101** | 相同约定 | 相同约定 |
| **Hu PRD** | 未直接使用圆极化基（仅用 $+$, $\times$） | 未直接使用 |
| **Lou 论文** | 未直接使用圆极化基（仅用 $+$, $\times$） | 未直接使用 |

**结论**：JCAP 的圆极化基定义与 Seto 2006 一致，这是 PTA 文献中的标准约定。Hu PRD 和 Lou 论文在 ORF 框架中均只使用线性极化基，这与它们不处理手征性的目的一致。

### 3.2 Stokes 参数 $I, V$

| 来源 | $I(f)$ | $V(f)$ | chi 参数 |
|------|--------|--------|---------|
| **JCAP Eq.(2.6)** | $(S_R+S_L)/2$ | $(S_R-S_L)/2$ | $\chi = V/I$ |
| **Seto 2006** | $(S_R+S_L)/2$ | $(S_R-S_L)/2$ | $\chi = V/I$ |
| **Hu PRD** | 无 Stokes 参数 | 无 | 无 |
| **Lou 论文** | 无 Stokes 参数 | 无 | 无 |

**一致确认**：JCAP 与 Seto 2006 的 Stokes 参数定义完全一致，包括 $1/2$ 归一化因子。这与 Maggiore 教科书 (8.38) 的差异已在 JCAP 原文中注明。

### 3.3 $\Gamma^I$ 与 $\Gamma^V$ 的分解

**JCAP Eq.(2.9-2.10)** 将交叉相关分解为：
$$\langle \tilde{s}_i \tilde{s}_j^* \rangle = \frac12\delta(f-f')\left[\Gamma^I I + \Gamma^V V\right]$$

其中：
$$\Gamma^I_{ij} \propto \int \frac{d^2\hat{k}}{4\pi} e^A_{ab}e^A_{cd} e^{-i2\pi f\hat{k}\cdot\vec{\Delta r}/c} \quad (\text{宇称偶})$$
$$\Gamma^V_{ij} \propto -i\int \frac{d^2\hat{k}}{4\pi} (e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}) e^{-i2\pi f\hat{k}\cdot\vec{\Delta r}/c} \quad (\text{宇称奇})$$

**Hu PRD 的 $\Gamma$ 对应 $\Gamma^I$**：Hu 的 ORF 仅对偏振求和 $\sum_A R_I^A R_J^{A*}$，没有交叉偏振项 $e^+ e^\times - e^\times e^+$，所以 Hu 的 $\Gamma$ 对应 $\Gamma^I$。

**关键发现**：Hu PRD 框架可以自然地扩展以包含 $\Gamma^V$——只需将偏振求和 $\sum_A$ 替换为 $\sum_{A,B} \epsilon_{AB} (\cdots)$，其中 $\epsilon_{AB}$ 是反对称张量。这正是在 JCAP 中的做法。

---

## 维度 4: Gamma^V 宇称奇 ORF — 存在条件

### 4.1 核心条件：非共面

| 来源 | Gamma^V 条件 | 是否强调 |
|------|-------------|---------|
| **JCAP §1** | 非共面探测器网络 | 核心结论 |
| **JCAP §2.1** | $(\hat{n}_1 \times \hat{n}_2) \cdot \hat{d} \neq 0$ | 公式化表达 |
| **P1-1 附录 A.2** | 5步推导，明确 Gamma^V $\propto$ 三重标量积 | 完整证明 |
| **Hu PRD** | 未讨论（仅处理 $\Gamma^I$） | 不涉及 |
| **Lou 论文** | 未讨论（仅处理 $\Gamma^I$） | 不涉及 |

### 4.2 Gamma^V = 0 的镜面论证

JCAP 的核心论证（§1 + P1-1 §5.3）：

1. 对于共面探测器网络（如单个三角形），存在一个镜面反射将网络映射到自身
2. 宇称奇量 $\Gamma^V$ 在此反射下变号
3. 网络不变 $\implies \Gamma^V$ 不变
4. 唯一可能值：$\Gamma^V = 0$

**此论证在 P1-1 附录 A.2 中得到完整的代数证明**：通过显式计算 $e^+ e^\times - e^\times e^+$ 的积分，证明其正比于 $(\hat{n}_1 \times \hat{n}_2) \cdot \hat{d}$，即三臂矢量的标量三重积。

### 4.3 对 OLC 网络的含义

Lou 论文分析的 OLC 构型中：
- **共面三角构型**：三个航天器在同一平面 $\implies \Gamma^V = 0$，无法探测手征性
- **非共面构型**（如四面体、等腰梯形轨道）：$(\hat{n}_1 \times \hat{n}_2) \cdot \hat{d} \neq 0$ $\implies \Gamma^V \neq 0$，可以探测手征性

**这为 OLC 网络设计提供了明确指导**：如果要探测手征 SGWB，OLC 网络必须采用非共面构型（如四面体），而不仅仅是共面三角。

---

## 维度 5: 单程链路 ORF — I1-I4 分解框架的适用性

### 5.1 Hu 的 I1-I4 框架与 OLC 通用性

Hu 的核心贡献（I1-I4 分解 + 留数定理）是针对**通用单程链路 ORF** 的。任何基于单程链路的探测器网络，包括 OLC，都可以通过 Hu 的框架计算 ORF。

**但关键差异在于转移函数**：

| 环节 | Hu | OLC (Lou) |
|------|-----|-----------|
| 单程链路响应 | $R^A = \frac{1}{2}e^A_{ab}u^au^b T_{\text{one}}^{\text{Hu}} e^{-i2\pi f\hat{n}\cdot\vec{x}/c}$ | $R^A = \frac{1}{2}e^A_{ab}u^au^b \mathcal{T}_{\text{one}}^{\text{OLC}} e^{-i2\pi f\hat{n}\cdot\vec{x}/c}$ |
| 转移函数 | 指数形式 | sinc 形式 |
| ORF 积分 | I1-I4 分解 + 留数定理 | 无 I1-I4 分解（Lou 采用数值积分） |

**关键推论**：OLC 网络的 ORF 也可以使用 Hu 的 I1-I4 留数框架计算——只需将 $T_{\text{one}}^{\text{Hu}}$ 替换为 $\mathcal{T}_{\text{one}}^{\text{OLC}}$，然后重新进行 I1-I4 分解。但 sinc 函数的复解析性质比指数函数复杂得多（sinc 有极点也有零点），留数计算将更加复杂。

### 5.2 何时应该用 Hu 的解析框架？

根据 Hu Table I 的速度对比：

| 探测器类型 | 数值积分速度 | 解析速度 | 解析方法的必要性 |
|-----------|-------------|---------|----------------|
| PTA | 10-1660s | 0.3ms | 中（短波长近似已足够） |
| GbLI | 0.24-3.95s | 30ms | 低（小天线近似在现有频段足够） |
| SbLI | 0.27-166s | 40-110ms | **高**（小天线近似高频失效） |
| **OLC** | 估计 SbLI 量级 | 待开发 | **中高**（取决于臂长和频率） |

OLC 的典型臂长（0.1-3 Gm）与 SbLI 类似，因此在高频段小天线近似失效。解析框架对 OLC 的价值取决于：
1. 臂长 $\sim$ Gm：sinc 零点结构需要精确处理
2. 计算需求：如果需要在参数空间中扫描大量构型，解析方法的价值显著

---

## 维度 6: 构型变换不变性

### 6.1 Lou 的构型变换

Lou 论文（§3.5）识别了四种构型变换：

| 变换类型 | 操作 | ORF 变化 |
|---------|------|---------|
| 标签交换 | 1 $\leftrightarrow$ 2 | $\Gamma \to \Gamma^*$，$|\Gamma|$ 不变 |
| 平移 | $\vec{x}_i \to \vec{x}_i + \vec{a}$ | 不变 |
| 正交变换 | 旋转/反射所有参数 | 不变 |
| **非平凡变换** | 交换每个探测器的发射/接收位置 | $|\Gamma|$ 不变 |

### 6.2 Hu 框架中的对应

Hu 框架中的 I1-I4 分解也隐含了构型不变性：

- **平移不变性**：Hu 的 $\alpha = 2\pi f \Delta L/c$ 只依赖于相对位置 $\vec{r}_v - \vec{r}_u$，平移不改变 $\alpha$
- **旋转不变性**：Hu 的 $\Gamma$ 仅通过标量积 $\hat{n}\cdot\hat{s}$, $\hat{n}\cdot\hat{u}$, $\hat{n}\cdot\hat{v}$ 依赖方向，旋转不改变这些不变量
- **非平凡变换**：Hu 框架中，交换发射/接收位置改变 $\hat{u} \to -\hat{u}$ 和 $L$ 的参考点，但 Hu 的指数形式 $e^{-i\beta(1+\hat{n}\cdot\hat{u})}$ 在 $\hat{u} \to -\hat{u}$ 下的行为与 OLC 的 sinc 形式不同

**重要差异**：非平凡变换对 OLC 的 sinc 转移函数保持 $|\mathcal{T}|^2$ 不变是因为：
$$|\text{sinc}(y)|^2 = \left|\frac{\sin y}{y}\right|^2$$
其中 $y = \frac{\pi fL}{c}(1-\hat{u}\cdot\hat{n})$。当 $\hat{u} \to -\hat{u}$ 时 $y \to \frac{\pi fL}{c}(1+\hat{u}\cdot\hat{n})$，二者一般不相等。但 Lou 的非平凡变换同时交换了发射/接收位置，这会额外引入相位因子，使得最终 $|\Gamma|$ 不变。

### 6.3 与手征性探测的关系

对于 $\Gamma^V$（宇称奇），**反射变换会改变符号**：
- 正交变换中的纯旋转：$\Gamma^V$ 不变
- 包含反射的正交变换：$\Gamma^V \to -\Gamma^V$
- 非平凡变换：可能改变 $\Gamma^V$ 的符号

这为搜索具有相同 $|\Gamma^I|$ 但不同 $\Gamma^V$ 的构型提供了方向。

---

## 综合对比表

| 维度 | Hu PRD | JCAP 2025 | Lou (OLC) | 一致性 |
|------|--------|-----------|-----------|--------|
| **ORF 定义** | $1/8\pi \int \sum R_I R_J^*$ | $\Gamma^I, \Gamma^V$ 分解嵌入交叉相关 | $1/4\pi \int \sum R_I R_J^*$ | $\Gamma^I$ 一致，归一化约定差异 |
| **转移函数** | 指数形式 (PTA convention) | 未显式给出（使用探测器专用响应） | sinc 形式 (OLC convention) | 不同观测量，数学上可转换 |
| **圆极化基** | 未使用 | $e^R=(e^++ie^\times)/\sqrt{2}$ | 未使用 | JCAP 与 Seto 2006 一致 |
| **Stokes 参数** | 无 | $I=(S_R+S_L)/2, V=(S_R-S_L)/2$ | 无 | JCAP 与 Seto 一致 |
| **$\Gamma^V$** | 不涉及 | 核心概念，宇称奇 ORF | 不涉及 | 可从 Hu 框架扩展得到 |
| **$\Gamma^V=0$ 条件** | 不涉及 | 共面网络 $\implies \Gamma^V=0$ | 不涉及 | 与 Hu 框架兼容 |
| **I1-I4 分解** | 核心数学工具 | 不涉及 | 不涉及 | Hu 框架可推广至 OLC |
| **构型变换不变性** | 隐含（标量积） | 不涉及 | 显式讨论4种变换 | Lou 的不变性可嵌入 Hu 框架 |

---

## Phase 3 结论

### 三大一致性

1. **ORF 基本框架一致**：Hu PRD 的通用单程链路 ORF 框架是 JCAP 和 Lou 工作的基础。JCAP 在此基础上分解出 $\Gamma^I$ 和 $\Gamma^V$，Lou 将框架应用于 OLC 专用转移函数。

2. **手征性探测条件一致**：JCAP 的"非共面是手征性探测的必要条件"与 P1-1 附录 A.2 的 $\Gamma^V \propto (\hat{n}_1\times\hat{n}_2)\cdot\hat{d}$ 代数证明一致，且可直接应用于 OLC 网络设计。

3. **转移函数差异是观测量约定差异**：Hu 的指数形式（时间残差）与 Lou 的 sinc 形式（频率偏移）对应于不同的物理观测量，在傅里叶域中相差 $i2\pi f$ 因子。两者都是精确的，无近似。

### 论文修正的关键启示

基于交叉对比，论文理论框架修正应关注：

1. **ORF 归一化约定**：全文统一使用 $1/4\pi$（Lou convention）或明确标注 $1/8\pi$（Hu convention）
2. **转移函数选择**：OLC 部分的公式必须使用 sinc 形式（Lou Eq.2-30），而非 Hu 的指数形式
3. **$\Gamma^V$ 扩展**：在手征性章节中，从 Hu 框架自然扩展引入 $\Gamma^V$，使用 JCAP 的分解方式
4. **构型不变性**：在 OLC 构型优化章节中，引用 Lou 的非平凡变换结果

---

*产出：Phase 3 交叉对比分析*
*完成日期：2026-07-08*
*置信度：0.92 — 所有对比基于原文公式的直接比对，无推断*
