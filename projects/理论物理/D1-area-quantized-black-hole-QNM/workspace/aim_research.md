# Dehghan-Safari AIM 方法研究：Teukolsky QNM 计算前置分析

**Date**: 2026-06-27
**Purpose**: Dehghan-Safari AIM 的核心思想、步骤及其在 Teukolsky 方程上的适配分析

---

## 1. 参考文献

|R#| 文献 | 内容 |
|---|------|------|
| [R1] | Tikver & Yavuz, Phys. Lett. A 343, 280 (2005) | AIM 原始论文（二阶 ODE） |
| [R2] | Cho et al., CQG 27, 155004 (2010), arXiv:0912.2740 | AIM on black hole QNMs（Schwarzschild, SdS, SAdS） |
| [R3] | Cho et al., CQG 28, 235008 (2011), arXiv:1111.5024 | **AIM 综述**：Schwarzschild, RN, Kerr 统一框架 + 数值改进版 |
| [R4] | Dehghan, Safari & Alimohammadi, JCAP 04 (2011) 010 | 项目引用的 Dehghan-Safari AIM 原始文献 |
| [R5] | Dey, Phys. Lett. A 373, 4248 (2009) | Another AIM-QNM paper |

**说明**: [R4] 是唯一未在 arXiv 上找到的文献。[R2] 和 [R3] 为 Cho-Dehghan-Safari 团队的工作，可能包含 [R4] 的相同或更早结果。R3 是该方法的最佳综合参考。

---

## 2. AIM 核心思想

### 2.1 原始 AIM (Tikver & Yavuz)

AIM 用于求解二阶齐次线性 ODE:
```
y''(x) = lambda_0(x) * y'(x) + mu_0(x) * y(x)
```

**关键观察**: 如果 y 可以消去，即 y 及其任意阶导数之间存在线性关系，则有递推关系：
```
y^(n+2)(x) = lambda_n(x) * y^(n+1)(x) + mu_n(x) * y^(n)(x)
```

其中系数的递推：
```
lambda_{n+1}(x) = lambda_n'(x) + lambda_n(x)^2 - mu_n(x)
mu_{n+1}(x)     = mu_n'(x) + lambda_n(x) * mu_n(x)
```

**核心条件**: 当 n -> infinity 时，lambda_n 和 mu_n 的行为趋于某种比例关系，导致判别式：
```
delta_n(x) = lambda_n(x) * mu_{n-1}(x) - lambda_{n-1}(x) * mu_n(x) = 0
```

当 delta_n(x) = 0 在某点成立时，递推在第 n 步收敛，从而确定本征值。

**Tikver-Yavuz 改进**（2005）: 使用比值：
```
r_n(x) = mu_n(x) / lambda_n(x) = mu_{n-1}(x) / lambda_{n-1}(x)
```

即判别式用 ratio 形式:
```
mu_n(x)/lambda_n(x) - mu_{n-1}(x)/lambda_{n-1}(x) = 0
```

### 2.2 AIM 本征值条件

对于 QNM 问题：
1. 从视界（r* -> -infinity）积分得到theta_horizon(omega)
2. 从无穷远（r* -> +infinity）积分得到theta_infinity(omega)
3. QNM 条件:
   ```
   theta_horizon(omega) = theta_infinity(omega)
   ```
   即:
   ```
   D(omega) = |theta_horizon - theta_infinity| = 0
   ```

**注意**: AIM 迭代可以同时在两个端点积分，这是 AIM 相对于 shooting method 的效率优势。

---

## 3. 标准 AIM vs 改进版 AIM (Cho et al. R3)

### 3.1 标准 AIM 的问题

1. **收敛速度依赖系数大小**: 当 lambda_0, mu_0 很小或发散时，递推可能不收敛。
2. **数值稳定性**: 标准 AIM 在大 N 时容易出现浮点溢出/下溢。

### 3.2 改进版 AIM (arXiv:1111.5024 [R3])

Cho et al. 提出的改进包括：

1. **Gauge 变换消除奇异行为**: 通过选择适当的 factor function，消除方程在视界和无穷远的渐近行为。
   ```
   psi(r) = f(r) * y(r)
   ```
   其中 f(r) 编码已知的边界行为。

2. **变量变换**: 将径向变量变换为有限区间上的变量，使收敛更好。

3. **数值规范化的全局策略**: 当 |lambda_n| 和 |mu_n| 超过阈值时，将变量全局缩放。

---

## 4. 项目中的 Dehghan-Safari 规范变换

### 4.1 规范变换公式

项目在 `d1-aim-solver-dehghan.py`、`d1-aim-dehghan-v2.py` 等文件中实现了名为 "Dehghan-Safari" 的规范变换：

**Gauge factor**:
```
F(r) = r^2 / (r - 2M)^2
```

**变换函数**:
```
psi = F^{i*omega} * x^{i*omega} * (1-x)^{i*omega} * u
```

其中 x = 1 - 2M/r，即 x = 0 对应视界 r = 2M，x = 1 对应无穷远 r -> infinity。

进一步分解（项目代码中称为 Dehghan gauge）:
```
G = F^{alpha} * x^{beta} * (1-x)^{gamma} * exp(h/(1-x))
```

其中项目的代码使用：
- alpha = -i*omega
- beta = i*omega  
- gamma = -i*omega（注意项目代码中的变量命名略有不同）

### 4.2 变换的目的

1. **消除视界处的奇异**: x^{-i*omega} 消除 x=0 处的行为
2. **消除无穷远处的奇异**: (1-x)^{i*omega} 消除 x=1 处的行为
3. **F^{i*omega} 消除 F 的余弦像行为**: 使方程系数的增长更快

4. **核心效果**: 经过规范变换后，AIM 系数 lambda_0 和 mu_0 变为**多项式系数的函数**且**|lambda_0| = O(omega) 量级 >> O(1)**，这使得 AIM 递推以双指数速度收敛。

### 4.3 Cho 的六因子 ansatz (d1-aim-dehghan-v1.py 对比)

代码同时实现了 Cho et al. 的六个因子 ansatz：
```
psi = F^{kappa/2} * x^{beta/2} * (1-x)^{gamma/2} * y
```
其中 kappa = 2i*omega, beta = 2i*omega, gamma = -2i*omega.

与 Dehghan 规范的主要区别：
- Cho 用 x 和 (1-x) 代替直接 x 幂次
- 指数系数因子不同

---

## 5. AIM 递推步骤（项目实现）

### 5.1 ODE 形式的映射

从 Regge-Wheeler 方程:
```
d^2psi/dr*^2 + (omega^2 - V_RW) * psi = 0
```

1. **变换变量到 x = 1 - 2M/r**
   - dr*/dx = r^2/(r-2M)^2 / (dr/dx)^{-1} 等链式法则
   - d^2psi/dx^2 + (Q/P) * dpsi/dx + (omega^2 - V)/P * psi = 0

2. **规范变换 psi = g*y**
   - y'' + [2*(ln g)' + Q/P] * y' + [(ln g)'' + (ln g)'^2 + (Q/P)*(ln g)' + (omega^2-V)/P] * y = 0

3. **提取 AIM 系数**:
   ```
   lambda_0 = -[2*(ln g)' + Q/P]
   mu_0     = -[(ln g)'' + (ln g)'^2 + (Q/P)*(ln g)' + (omega^2-V)/P]
   ```

### 5.2 AIM 迭代

在两个评估点 xa 和 xb（通常 xa = 0.3, xb = 0.7）并行迭代：

```
lambda_{k+1} = lambda_k^2 + lambda_k' - mu_k
mu_{k+1}     = lambda_k * mu_k' - mu_k * lambda_k' + mu_k^2
```

其中 lambda_k' 和 mu_k' 通过有限差分计算。

### 5.3 收敛判断

方案 A（theta 比较）:
```
theta(xa) = lambda_{N-1}(xa) / lambda_N(xa)
theta(xb) = lambda_{N-1}(xb) / lambda_N(xb)
D(omega) = |theta(xa) - theta(xb)| = 0
```

方案 B（Wronskian）:
```
W_N = lambda_{N-1}(xa) * lambda_N(xb) - lambda_N(xa) * lambda_{N-1}(xb) = 0
```

方案 C（phase + ratio 组合，对 scaling 完全不变）:
```
phi_diff = |arg(theta_a) - arg(theta_b)|
ratio_dev = |abs(theta_a/theta_b) - 1|
D = phi_diff + ratio_dev
```

---

## 6. 与 4-term Frobenius 递归的关系

### 6.1 问题概述

项目 notes/teukolsky_rw_limit.md 确认了：
- Teukolsky(a=0) 的 Frobenius 递推是 **4-term**（非 3-term）
- 标准 Leaver 持续分数法仅适用于 3-term
- AIM 方法**不依赖于递推关系的项数**——AIM 在连续空间上做迭代，不受离散步数限制

### 6.2 核心洞察

**这是 AIM 相对于 Leaver CF 的关键优势**:
- Leaver CF: 需要从 3-term Frobenius 递推构建 3x3 三对角矩阵 -> 持续分数
- AIM: 直接从连续 ODE y'' = lambda*y' + mu*y 出发 -> 迭代不依赖离散递推的项数

因此 **AIM 天然适用于 Teukolsky 方程**。在 a=0 时，Teukolsky 方程在连续形式上仍是二阶 ODE，可以直接使用 AIM，不需要进行 Frobenius 级数展开。

### 6.3 对于 Teukolsky 方程的适配

#### 6.3.1 在 a=0 时

Teukolsky 方程（s = -2）在 a=0 时的径向方程：
```
Delta^2 * d/dr*(Delta^(-1) * dR/dr) + [K^2/Delta - 4isomega*r + A_lm] * R = 0
```

在 a=0 简化为:
```
r^2 * d/dr*(dR/dr) + [omega^2 * r^4 / (r-2M)^2 - 4(-2)*omega*r - l(l+1)] * R = 0
```

这是一个**连续二阶 ODE**，可以写成 AIM 标准形式：
```
R'' + P(r) * R' + Q(r) * R = 0
```

**不需要使用 Frobenius 级数**，直接用 AIM 迭代求解。

#### 6.3.2 规范变换

对于 Teukolsky 方程，需要构造合适的规范变换消除视界和无穷远的奇异行为。

视界处 (r = 2M): R ~ (r - 2M)^{-i*omega}（入射波条件）
无穷远处 (r -> infinity): R ~ e^{i*omega*r*}（出射波条件）

变换因子可以借鉴 RW 项目的 Dehghan gauge：
```
G = (r - 2M)^{alpha} * r^{beta} * exp(gamma * r*)
```

#### 6.3.3 需要处理的系数

Teukolsky a=0 的 ODE 系数 P(r) 和 Q(r) 包含：
- P(r) ~ 2/r（来自 Delta^2 的导数项）
- Q(r) ~ omega^2 * r^2/(r-2M)^2 + ...（来自势能项）

这些系数是有理函数（分母最多二次），与 RW 情况相同结构。

**关键点**: Teukolsky 的 P 和 Q 包含与 Regge-Wheeler **不同**的势能项（包含 spin-weight 效应），但函数结构相同——都是 r 的有理函数。

### 6.4 4-term 系数的实际影响

AIM 不受 4-term 递推的影响，因为：

1. **AIM 使用连续空间，不使用 Frobenius 展开**。 AIM 不构建 tridiagonal/四对角矩阵。

2. **但需要考虑的是**: 在 a=0 时，如果使用 Frobenius 展开的 AIM 变体（在某个点做级数展开后应用 AIM），则 4-term 递推意味着需要更复杂的递推关系。不过项目中使用的是标准的连续 AIM 方案，不涉及此问题。

---

## 7. 适配 Teukolsky (a=0, s=-2) 的具体步骤

### Step 1: 将 Teukolsky 方程写成 AIM 标准形式

从 Teukolsky radial ODE (a=0, s=-2) 提取 P(r) 和 Q(r)：
```
R'' + P(r) * R' + Q(r) * R = 0
```

对比 RW 项目的 `get_aim_coeffs` (d1-aim-solver-dehghan.py lines 46-153)，适配关键变化：

| | Regge-Wheeler | Teukolsky (a=0) |
|---|---|---|
| ODE 变量 | psi | R (Teukolsky variable) |
| 势 V(r) | (1-2M/r)[l(l+1)/r^2 - 6M/r^3] | omega^2*r^4/Delta^2 + spin terms + l(l+1) |
| dr*/dr | r^2/Delta | r^2/Delta（相同，因为 a=0） |
| 规范变换因子 | Dehghan 5-factor | 需要重构以适应 Teukolsky 边界条件 |

### Step 2: 确定 Teukolsky 的规范变换

Teukolsky 方程 s=-2 在 a=0 的渐近边界条件：
- 视界 r = 2M: R ~ (r-2M)^{i*omega*2M*...}
- 无穷远: R ~ e^{i*omega*r*} / r^3 (spin-weighted)

需要重新设计规范变换函数：
```
G_Teuk(r) = (r-2M)^{alpha} * r^{beta} * exp(gamma * r*)
```

参考 Leaver 的 Frobenius 指数：
- horizon: alpha_h = -2*omega*(M+r_+) + i*...
- infinity: alpha_in = i*omega*...

### Step 3: 验证 a=0 回归

在最关键的验证步骤中：
1. 在 a=0 应用 Teukolsky AIM 求解器
2. 得到的 omega 应与 RW AIM 求解器（已经验证）的结果相同
3. 这是 Ishibashi-Hoodge duality 的数值验证

### Step 4: 扩展至 a>0

1. 增加 Kerr 参数 a，Teukolsky 方程保持为二阶 ODE
2. a>0 时方程变为 Heun 型，但 AIM 不受 Frobenius 项数影响
3. 与 Berti 2009 参考值比较

---

## 8. Dehghan-Safari AIM 核心优势总结

### 相对于 Leaver CF

| 特征 | Leaver CF | AIM |
|---|---|---|
| 递推项数要求 | 仅 3-term | 不相关（连续空间） |
| 收敛性 | 有争议（理论上在 annulus 收敛） | 数值上稳定 |
| 适用方程 | Heun 方程 | 任意二阶线性 ODE |
| a>0 Teukolsky | 适用（3-term） | 适用 |
| a=0 Teukolsky | 不适用（4-term） | 适用 |

### 相对于 Shooting Method

| 特征 | Shooting Method | AIM |
|---|---|---|
| 计算开销 | 需从两端积分 + match | 两端同时迭代 |
| 对 N 的依赖 | 不依赖 | N~50-100 步 |
| 数值稳定性 | 对高频模式敏感 | 需处理 scaling |
| 并行化 | 两积分独立 | 两端独立迭代 |

---

## 9. 实施中的关键工程决策

### 9.1 Scaling 策略

项目发现的关键工程问题：
- **全局 scaling（推荐）**: xa 和 xb 用同一缩放因子，Wronskian 不变性保持
- **per-point scaling**: 可能导致 scaling-invariant 条件不再等价于 W=0
- **log-space**: 在 `d1-teukolsky-aim-solver-v4.py` 中实现了对复数的对数空间表示，从根本上避免溢出

### 9.2 评估点选择

项目的经验值（来自 d1-aim-nscan.py 的分析）:
- **Dehghan formulation**: xa = 0.35, xb = 0.65（远离视界和无穷远）
- **收敛窗口**: N = 4-6 是可靠的（在 N=7 时开始饱和，所有 omega 值的 D 都收敛到相近值）
- **原始 (no gauge) formulation**: 需要更大 N，收敛窗口更窄

### 9.3 指标选择

三种方案的性能排序（从项目经验）:
1. **Wronskian with global norm** (`d1-teukolsky-aim-solver-v5.py`): 简单可靠
2. **Phase + ratio** (`d1-aim-solver-dehghan.py`): scaling invariant，最 robust
3. **Pure theta difference** (`d1-aim-dehghan-v2.py`): 容易受 scaling 影响

---

## 10. Teukolsky a=0 的 4-term 系数具体形式

从 teukolsky_rw_limit.md 的分析，Teukolsky a=0 在视界处展开：

### Frobenius 递推结构

如果强行用 Frobenius 级数处理（AIM 不需要但需理解）:
```
A_n * c_{n-2} + B_n * c_{n-1} + C_n * c_n + D_n * c_{n+1} = 0
```

各系数的来源:
- **A_n**: 来自 Q(x) 的 1/x^2 项（例如 omega^2 * r^4/Delta^2）
- **B_n**: 来自 P(x) 的 1/x 项和 Q(x) 的 1/x 项
- **C_n**: 来自 Q(x) 的常数项
- **D_n**: 来自高阶展开项

具体系数需要在新代码中推导（不在本文范围内），但重点是：**AIM 不依赖此递推**。

---

## 11. 结论与建议

1. **AIM 天然适配 Teukolsky**: 不依赖 Frobenius 递推的项数，连续空间求解。
2. **Dehghan 规范变换**: 用 F(r) 和幂律因子编码边界行为，是加速收敛的关键。
3. **实施路径**:
   - 先复用 RW 项目的系数代码（已验证正确）
   - 将势 V_RW 替换为 Teukolsky 有效势（仅 Q(r) 不同）
   - 重新推导规范变换以适应 Teukolsky 边界条件
   - a=0 验证通过则扩展到 a>0
4. **最需要验证的点**: Dehghan gauge 在 Teukolsky 方程上的收敛窗口。可能需要不同于 RW 的 x_a, x_b 值和 N。

---

**End of Research**
