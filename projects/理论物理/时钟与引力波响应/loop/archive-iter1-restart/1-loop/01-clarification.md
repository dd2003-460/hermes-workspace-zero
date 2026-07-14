# 01-clarification — Iteration 32: 整合手征引力波计算解析 ORF

> **Clarifier Output**
> **Iteration**: 32
> **Goal**: 从 Hu PRD 通用框架 + JCAP 手征 ORF 公式出发，推导并实现适用于 OLC 网络的解析 Gamma^I(f) + i Gamma^V(f)
> **Prior Iterations**: 1-31. 所有已知 bug (P4-1 独立审计确认) 已修复。P0-1/P1-1/P2-1/P3 已完成理解材料。

---

## 1. 精确任务定义

### 核心物理问题

引力波随机背景的手征性（chirality）——即右旋(R)与左旋(L)圆极化强度不对称——是检验宇称破坏新物理的关键观测量。

JCAP 2025 (Eq.2.9) 将两个探测器 i,j 之间的交叉相关分解为：

$$\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle = \frac{1}{2}\delta(f-f')\left[\Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f)\right]$$

其中：
- **Gamma^I(f)**：宇称偶 ORF，正比于 Stokes I（总强度）
- **Gamma^V(f)**：宇称奇 ORF，正比于 Stokes V（手征不对称），即 $V = (S_R - S_L)/2$

**当前知识缺口**：

P3 交叉对比 (维度 5.1) 明确指出：Hu PRD 的 I1-I4 分解 + 留数定理框架是针对 PTA 指数转移函数 $T_{\text{one}}^{\text{Hu}}$ 推导的，而 OLC 使用 sinc 形式的转移函数 $\mathcal{T}_{\text{one}}^{\text{OLC}}$。虽然 P3 指出"Hu 框架可以自然地扩展以包含 Gamma^V——只需将偏振求和替换为 epsilon_AB 交叉项"，但**不存在显式的统一公式**——即：

1. 不存在 Hu I1-I4 框架 + OLC sinc 转移函数的统一解析推导
2. 不存在 Gamma^V 在 OLC sinc 转移函数下的显式表达式
3. 不存在小臂近似 ($kL \ll 1$) 下 Gamma^I 和 Gamma^V 的解析公式
4. 当前 script 11 使用数值积分方法，结果因多个物理 bug 而被标记废弃

### 任务边界条件

**包含在内**：
- 各向同性 SGWB 假设（sky average）
- 两个三角探测器网络的交叉相关
- + 和 x 线性极化 → R/L 圆极化基变换
- OLC 专用 sinc 转移函数 (Lou Eq.2-30)
- TDI E-variable 或 Michelson-like 变量
- 小臂近似 ($kL \ll 1$) 下的解析公式推导
- 数值验证（对比解析解与数值积分）

**排除在外**：
- 非各向同性 SGWB（需要 $l>0$ 球谐展开）
- 有方向的 SGWB 源
- 传播双折射效应
- 频率依赖的手征参数 chi(f)（假设 chi 为常数或仅讨论固定频率）
- 噪声谱和 SNR 计算
- 非三角构型（如四面体）

### 已知约束与不可协商硬约束

| # | 约束 | 来源 | 置信度 |
|---|------|------|--------|
| C1 | 单三角探测器（共面）：$\Gamma^V = 0$（镜面对称论证） | JCAP §1 + P1-1 §5 + P3 §4.2 | 0.95 |
| C2 | $\Gamma^V \neq 0$ 需要非共面网络：$(\hat{n}_1 \times \hat{n}_2) \cdot \hat{d} \neq 0$ | JCAP §2.1 Eq.(2.10) + P1-1 §5.3 | 0.95 |
| C3 | 双三角网络（LISA×Taiji，60°相对倾角）：Orlando 2021 给出 $|\Gamma^V|_{\max} \sim 0.3$ (从图读出) | arXiv:2011.07059 | 0.80 |
| C4 | OLC 使用 sinc 转移函数 (Lou Eq.2-30)，不能用 Hu 指数形式 | P2-1 + P3 §2 | 0.95 |
| C5 | JCAP 归一化：$\langle \tilde{s}_i \tilde{s}_j^* \rangle = \frac{1}{2}\delta(f-f')[\Gamma^I I + \Gamma^V V]$，隐含 $1/4\pi$ sky average | JCAP Eq.(2.9) | 0.95 |
| C6 | 小臂近似下 $kL \ll 1$，sinc 函数展开为 $1 - \frac{1}{6}(kL(1-\hat{n}\cdot\hat{u}))^2 + \cdots$ | P2-1 + P3 §2.4 | 0.90 |

### 失败判据

1. **Gamma^V = 0 for 共面网络**：数值测试中，两个相同 coplanar 三角探测器的 $\Gamma^V$ 必须 $< 10^{-6}$。如果 $> 10^{-6}$，说明代码/公式存在物理错误。
2. **非共面网络 Gamma^V 可探测**：LISA (i=60°) × Taiji (i=0°) 的 sky-max normalized $|\Gamma^V| \in [0.01, 1.5]$（覆盖 Orlando 范围及 convention 差异）。
3. **解析 vs 数值一致性**：小臂近似解析公式与数值积分结果的相对误差 $< 5\%$（在 $fL/c < 0.1$ 范围内）。
4. **$\Gamma^I$ 与现有代码一致性**：当 $\Gamma^V = 0$ 时，解析 $\Gamma^I$ 必须与 script 01 (已验证的 OLC ORF solver) 的结果在 $< 5\%$ 内一致。

### 具体技术路线建议（基于 P1-1 + P3）

**Step 1 — 修正现有代码的物理 bug**：

- **Bug A**（Line 46-47）：`beta = np.pi * np.abs(f) * L / c` 应为 `beta = np.pi * f * L / c`（去掉 abs，OLC transfer function 的 beta 定义与指数不同）
- **Bug B**（Line 47）：`one_minus = 1.0 - np.abs(cos_nu)` 应为 `1.0 - cos_nu`（去掉 abs，P3 §2.4 确认符号约定）
- **Bug C**（Line 534）：`gamma_V = np.real(...)` 应改为直接积分（chiral integrand 是纯虚数，取 real 会丢失信号）
- **Bug D**（Line 439 `antenna_pattern_e_variable_universal`）：CW link sum 方法在等边三角形上给出 $R_{E\times} \approx 0$，需改用 detector tensor 方法

**Step 2 — Hu I1-I4 + OLC sinc 的统一解析框架**：

在 Hu PRD Eq.(10) 的单程 ORF 积分中：

$$\Gamma_{ij}(f) = \frac{1}{8\pi}\int d^2\Omega_{\hat{n}} \sum_A R_I^A(\hat{n}) R_J^{A*}(\hat{n}) e^{i2\pi f \hat{n}\cdot\vec{\Delta r}_{ij}/c}$$

将 $R^A$ 中的 $T_{\text{one}}^{\text{Hu}}$ 替换为 $\mathcal{T}_{\text{one}}^{\text{OLC}}$：

$$\mathcal{T}_{\text{one}}^{\text{OLC}} = \frac{i2\pi fL}{c} \cdot \text{sinc}\left[\frac{\pi fL}{c}(1-\hat{n}\cdot\hat{u})\right] \cdot \exp\left[-i\frac{\pi fL}{c}(1-\hat{n}\cdot\hat{u})\right]$$

sinc 函数 $\text{sinc}(x) = \sin(x)/x$ 在复平面上有简单极点（在原点处可去），因此留数定理仍然适用，但极点结构不同于指数函数。

I1-I4 分解的核心是将被积函数写成 $g(\hat{n}) \cdot \exp(i\alpha \hat{n}\cdot\hat{s})$ 的形式，然后对 $\hat{n}$ 的五个极点 $z_0, \dots, z_4$ 做留数求和（Hu Eq.18-24）。

替换后的新 I1-I4 表达式：
- I1: $\int d^2\Omega \frac{e^{i\alpha \hat{n}\cdot\hat{s}}}{(1+\hat{n}\cdot\hat{u})(1+\hat{n}\cdot\hat{v})}$ — 需要新的留数计算（sinc 函数引入了额外的极点）
- I2, I3, I4: 类似修改

**Step 3 — Gamma^V 的显式表达式**：

JCAP Eq.(2.10) 给出：

$$\Gamma^V_{ij} \propto -i\int \frac{d^2\hat{k}}{4\pi} (e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd}) e^{-i2\pi f \hat{k}\cdot\vec{\Delta r}/c}$$

交叉偏振项可以重写为：

$$e^+_{ab}e^\times_{cd}-e^\times_{ab}e^+_{cd} = \epsilon^{AB} F^A_i F^B_j$$

其中 $\epsilon^{AB}$ 是 $2\times 2$ 反对称张量（$\epsilon^{+-1} = 1$, $\epsilon^{+-2} = -1$ 在 $\{+,\times\}$ 基下）。

因此 $\Gamma^V$ 可以表达为：

$$\Gamma^V_{ij}(f) = \frac{1}{4\pi}\int d^2\Omega_{\hat{n}} \left[F_i^+(\hat{n})F_j^\times(\hat{n}) - F_i^\times(\hat{n})F_j^+(\hat{n})\right] \mathcal{T}_i^{\text{OLC}} \mathcal{T}_j^{\text{OLC}} e^{i2\pi f \hat{n}\cdot\vec{\Delta r}_{ij}/c}$$

这将给出 I1-I4 形式的表达式，其中每个 $I_k$ 包含不同的天线模式乘积组合。

**Step 4 — 小臂近似**：

在小臂近似 $kL \ll 1$ 下：

$$\mathcal{T}_{\text{one}}^{\text{OLC}} \approx -\frac{4\pi^2 f^2 L^2}{c^2} (1-\hat{n}\cdot\hat{u}) + \mathcal{O}((kL)^4)$$

代入 ORF 积分，得到纯几何表达式：

$$\Gamma^I_{ij}(f) \approx \frac{4\pi^2 f^2 L_i^2 L_j^2}{c^4} \int \frac{d^2\Omega}{4\pi} (1-\hat{n}\cdot\hat{u}_i)(1-\hat{n}\cdot\hat{u}_j) \sum_A F_i^A F_j^A e^{i2\pi f \hat{n}\cdot\vec{\Delta r}_{ij}/c}$$

$$\Gamma^V_{ij}(f) \approx \frac{4\pi^2 f^2 L_i^2 L_j^2}{c^4} \int \frac{d^2\Omega}{4\pi} (1-\hat{n}\cdot\hat{u}_i)(1-\hat{n}\cdot\hat{u}_j) [F_i^+ F_j^\times - F_i^\times F_j^+] e^{i2\pi f \hat{n}\cdot\vec{\Delta r}_{ij}/c}$$

这些积分可以精确解析计算，因为它们只涉及 $\hat{n}$ 的多项式乘上指数函数。

---

## 2. 交付物清单

1. **解析公式笔记**：`note/P-chiral-orf-analytical.md` — 完整的 Hu I1-I4 + OLC sinc 统一推导，包括 Gamma^I 和 Gamma^V 的小臂近似解析公式
2. **验证脚本**：`scripts/verify-chiral-orf-analytical.py` — 数值验证脚本，对比解析解与数值积分
3. **测试基准**：
   - 共面网络 $\Gamma^V \approx 0$ 测试
   - LISA×Taiji 倾斜网络 $|\Gamma^V|_{\max}$ 基准测试
   - 小臂近似 vs 数值积分一致性测试

## 3. Agent 任务映射建议

此任务应分解为以下 Agent 子任务（按 DAG 顺序）：

1. **T1 — 解析推导**：在 Hu I1-I4 框架下，将 OLC sinc 转移函数代入，重新推导 Gamma^I 和 Gamma^V 的 I1-I4 表达式
2. **T2 — 小臂近似**：推导小臂近似下的简化解析公式（只涉及纯几何积分）
3. **T3 — 代码修正**：基于 T1+T2 的公式，修正 script 11 的物理 bug，或从头编写解析求解器
4. **T4 — 验证**：对比解析解与数值积分，运行共面和倾斜基准测试

## 4. 依赖关系与前置条件

- **前置**：P0-1 (Hu PRD 理解) ✓, P1-1 (JCAP 手征物理) ✓, P2-1 (OLC 原理) ✓, P3 (交叉对比) ✓
- **前置**：memory/13 (Orlando benchmark 数据) — 需要确认
- **前置**：validate_orlando_crosscorr.py — 已有验证基准
- **风险**：sinc 函数的留数计算可能比 Hu 的指数函数复杂（sinc 有无限多个极点），T1 需要验证 I1-I4 分解是否仍然可行
