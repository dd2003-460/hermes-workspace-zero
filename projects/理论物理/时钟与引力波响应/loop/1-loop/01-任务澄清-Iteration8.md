# 1-loop/01-任务澄清 — Iteration 8

## 任务标题

**三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型**

**One-Sentence Definition:**
系统性地探索单三角形 OLC 星座在"深度非共面构型"下的手征重叠约化函数 (ORF) Gamma^V(f)，量化其对引力波圆极化的灵敏度，并与多星座交叉相关结果建立比较基线。

---

## 1. 物理动机

### 1.1 已确立的物理结论 (Iterations 5-7)

1. **镜面反射对称性导致 R^V = 0** (Iteration 6 严格证明):
   对于任意处于同一平面的单探测器，在镜面反射操作下 R^R(k̂) = R^L(reflected k̂)，结合 R^R(k̂) = R^L(-k̂) 的左右手征对称性，推出 R^V(k̂) = -R^V(reflected k̂) AND R^V(k̂) = R^V(reflected k̂) → R^V = 0 对所有天空方向严格成立。

2. **Michelson 似然变量具有精确零手征响应**:
   M = Link(a→b→a) - Link(b→a→b) 将两个相反单向链路组合为往返可观测量。在 F_A(u) = F_A(-u) (偶函数对称性) 下，M 的手征响应精确为零，对所有几何构型成立（包括非等边三角形）。已在 Iteration 6 中通过数值验证。

3. **E 变量 (CW sum) 打破镜面对称**:
   E = (X - 2Y + Z)/sqrt(6) 使用不对称的三链路组合，打破 M 变量中的链路线性对称性，允许非零 R^V。

4. **多星座交叉相关实现 |Gamma^V| ~ 1.0** (Iteration 7):
   LISA × Taiji 交叉相关的天空最大化归一化手征响应 sky-max norm_V = 1.00。OFC(30) × Taiji(0) 达到 0.99。这归因于不同轨道位置 (~60° 分离) 破坏镜面平面对称性的网络效应。

5. **chi_orb = 0.17 已解析为归一化约定不匹配** (memory/15):
   Orlando 的 chi_orb ~ 0.17 是对最大手征信号 (chi_true = 1) 的 Fisher 最佳拟合值，不是响应函数比 R^V/R^I。"均值回归"效应：R^I 比 R^V 强 ~10 倍 → Omega^I 约束远好于 Omega^V → 最佳拟合 chi = Omega^V/Omega^I < true chi = 1。

### 1.2 Iteration 8 要回答的物理问题

核心问题：**一个单三角形 OLC 星座（无需多星座交叉相关）能否通过"深度非共面构型"实现可探测的手征 ORF？**

子问题分解：

- **Q1:** 在真实的太阳轨道运动中，OLC 三卫星的三角形是否会因为轨道相位差异而自然呈现"非共面"构型？这些非共面性是否会积累到足以破坏手征对称性？
- **Q2:** 如果人工构造深度非共面构型（如倾斜三角形平面、不等臂三角形、三卫星不在同一平面内），Gamma^V 的最大可达值是多少？
- **Q3:** 深度非共面构型的手征响应与多星座交叉相关的手征响应在物理起源上是否相同？（两者都通过破坏镜面平面对称性获得 R^V ≠ 0）
- **Q4:** 在高频极限下（f >> c/L），OLC 传递函数的频率依赖相位因子是否会破坏 F_A(u) = F_A(-u) 对称性，从而在单臂水平产生非零手征响应？

### 1.3 为什么这个问题重要

- 如果单三角形 OLC 即可实现可探测的 Gamma^V，将极大简化探测方案的系统设计需求
- 确认手征响应的"纯几何"起源（对称性破缺是唯一必要条件），为未来探测方案提供设计指导原则
- 为后续灵敏度分析和 SNR 计算奠定基础

---

## 2. 已知与未知

### 已知

| # | 内容 | 来源 |
|---|------|------|
| K1 | 单平面探测器的 R^V = 0 是镜面反射对称性的严格推论 | memory/16 |
| K2 | Michelson 似然变量对任何单三角星座的 Gamma^V = 0（数值验证通过） | Iteration 6, scripts/10-olc-chiral-orf-triangular.py |
| K3 | 单臂非共面链路对实现 |Gamma^V| > 1e-3 (f > 10 mHz)，在 30 mHz 达到 ~0.041，在 100 mHz 达到 ~1.07 | Iteration 6 结果, Iteration 6 memory 文件 |
| K4 | 多星座交叉相关 |Gamma^V|_max ~ 1.0，归因于 3D 空间分离破坏镜面对称性 | Iteration 7, scripts/11-multi-constellation-chiral-orf.py |
| K5 | E 变量 (CW sum) 的响应: R_E+ = sum_CW F_+, R_Ex = sum_CW F_x | Iteration 7, antenna_pattern_e_variable_universal |
| K6 | Gamma^V 是纯几何量（归一化后与频率无关，但归一化因子有频率依赖） | Iteration 7 |
| K7 | 三个归一化约定已区分：(1) norm_V = 1.0 (E变量CW求和), (2) R^V/R^I (~0.06-0.12), (3) chi_orb = 0.17 (Fisher最佳拟合) | memory/15 |
| K8 | 多星座交叉相关的非零 R^V 来源于网络效应的相位因子 exp(-2pi i k · (x_1 - x_2)) | memory/16 |

### 未知

| # | 内容 | 说明 |
|---|------|------|
| U1 | 深度非共面单三角 OLC 的 Gamma^V 最大值 | 需要系统搜索非共面参数空间 |
| U2 | 非共面程度（dihedral angle / 偏离平面的距离）与 Gamma^V 的定量关系 | 需要参数化扫描 |
| U3 | 真实轨道运动导致的自然非共面性及其对手征响应的影响 | 需要轨道动力学计算 |
| U4 | 高频极限下传递函数相位因子对 F_A(u) = F_A(-u) 对称性的破坏程度 | 需要详细分析 |
| U5 | 最优的非共面构型参数（哪些自由度最有效地增加手征响应） | 需要优化搜索 |

---

## 3. 迭代目标

### 目标 1: 深度非共面构型的 Gamma^V 参数化研究

构造一系列非共面三角形构型，扫描以下参数：

- **倾斜角 (inclination angle)**: 三角形平面相对于参考平面的倾斜角度 (0-90°)
- **卫星高度差 (height differential)**: 三卫星在垂直于三角形平面方向的高度差
- **不等臂比 (side ratio)**: 三条边的长度比
- **三卫星非共面度 (coplanarity measure)**: 用标量三重积 (r2-r1) · ((r3-r1) × n_ref) 量化

对于每个构型，计算：
- 使用 Michelson 似然变量的 Gamma^V (预期接近 0)
- 使用 E 变量 (CW sum) 的 Gamma^V
- 单臂非共面链路对的 Gamma^V

### 目标 2: 手征响应与构型几何量的定量关系

建立 |Gamma^V| 与以下几何量之间的定量关系：

- 镜面对称性破缺度量: M = |(r2-r1) × (r3-r1)| / |r2-r1|/|r3-r1| · |sin(theta)| (theta 为理想共面时的夹角)
- 归一化手征响应对几何参数的依赖

### 目标 3: 多星座结果与单三角非共面结果的比较

将深度非共面单三角 OLC 的手征响应与多星座交叉相关结果进行直接比较，确认物理起源的一致性。

---

## 4. 通过/失败判定标准

### 核心通过标准

| # | 标准 | 定量要求 |
|---|------|----------|
| P1 | 共面三角形 E 变量 Gamma^V < 1e-10 | 严格验证镜面对称性 |
| P2 | 非共面三角形 E 变量 Gamma^V > 1e-3 (在 f > 10 mHz) | 验证非共面性导致手征响应 |
| P3 | 找到至少一种构型使得 |Gamma^V|_sky_max > 0.01 | 与多星座结果的比较基准 |
| P4 | 建立 |Gamma^V| 与构型几何参数（倾斜角/非共面度）的定量关系 | 至少线性/二次拟合 |
| P5 | 高频极限 (f >> c/L) 下，单臂非共面链路对的 |Gamma^V| > 1.0 | 与 Iteration 6 结果比较 |

### 硬约束

| # | 约束 | 说明 |
|---|------|------|
| H1 | 必须复用现有脚本框架 | 基于 scripts/10-olc-chiral-orf-triangular.py 和 scripts/11-multi-constellation-chiral-orf.py |
| H2 | 所有计算必须包含 sky-averaged 和 sky-maximized 两种平均 | 与 Iteration 7 保持一致的归一化 |
| H3 | 非共面构型的几何参数必须在 [0, pi] 或合理物理范围内 | 不包括数值奇点 |
| H4 | 频率扫描范围: 1 mHz 到 100 Hz (与既有工作一致) | log-spaced, >= 20 个点 |

---

## 5. 输入与输出

### 输入

| # | 来源 | 内容 |
|---|------|------|
| I1 | scripts/10-olc-chiral-orf-triangular.py | 三角形 OLC 手征 ORF 计算框架 (Iteration 6) |
| I2 | scripts/11-multi-constellation-chiral-orf.py | 多星座交叉相关框架 + 归一化约定 (Iteration 7) |
| I3 | memory/16-orlando-nonzeroRV-mirror-plane.md | 镜面反射对称性与 R^V = 0 的证明 |
| I4 | memory/15-orlando-chi_orb-resolution-iteration8.md | chi_orb 归一化约定解析 |
| I5 | Iteration 6 memory 文件 | 单臂非共面链路对的已知结果 |
| I6 | Iteration 7 决策文件 | 多星座结果的基线数据 |

### 输出

| # | 内容 | 格式 |
|---|------|------|
| O1 | 非共面参数扫描的数值结果 | CSV 数据文件 + Python 脚本 |
| O2 | 手征响应与几何参数的拟合关系 | 分析结果写入 memory 文件 |
| O3 | 频率依赖性分析 | 图文件 (PNG) |
| O4 | 与多星座结果的比较分析 | memory 文件 |
| O5 | loop 阶段文件 (01-06) | 标准格式 |
| O6 | 2-loop 执行产物（如 enter_2loop 决策后） | 标准格式 |

---

## 6. 风险评估与依赖

### 风险

| # | 风险 | 严重度 | 缓解措施 |
|---|------|--------|----------|
| R1 | 自然轨道运动导致的非共面性可能过小，Gamma^V 接近数值噪声 | 中 | 人工构造深度非共面构型作为验证；同时研究轨道动力学效应 |
| R2 | 如果单三角非共面构型的 Gamma^V 最大值远小于 1e-3，可能无实际探测价值 | 中 | 重点分析高频区 (f > 30 mHz)，因为单臂非共面链路对在此区域已显示 |Gamma^V| > 0.041 |
| R3 | 传递函数 F_A(u) = F_A(-u) 的对称性在非共面构型下可能仍然保持 | 低 | E 变量 (CW sum) 不使用 F_A(u) = F_A(-u) 对称性；单臂非共面链路对独立计算 |
| R4 | 计算复杂度：参数空间扫描可能导致大量数值积分 | 低 | 使用自适应网格 + 并行计算；优先扫描关键参数区域 |

### 依赖

| # | 依赖 | 状态 |
|---|------|------|
| D1 | Iteration 6 和 7 的理论框架 | 已完成 |
| D2 | 现有脚本框架 (10-olc-chiral-orf-triangular.py, 11-multi-constellation-chiral-orf.py) | 可用 |
| D3 | 归一化约定的统一理解 | memory/15 已解决 |
| D4 | Orlando 2021 (arXiv:2011.07059) 作为基准参考 | 已阅读 |

---

## 7. 关键参考文献

| # | 引用 | 关键内容 |
|---|------|----------|
| R1 | Orlando 2021 (arXiv:2011.07059) | LISA-Taiji 交叉相关手征 ORF 计算，R^V = 0 的理论声明 |
| R2 | Hu & Wolff (2002) | 手征引力波检测基础理论 |
| R3 | Kato & Soda (2016) | 手征 ORF 形式体系 |
| R4 | Allen & Romano (1987) | 交叉相关 ORF 基础理论 |
| R5 | Lou 硕士论文 | OLC 传递函数 (Eq. 2-30) |
| R6 | memory/16-orlando-nonzeroRV-mirror-plane.md | 镜面对称性破缺的物理分析 |
| R7 | memory/15-orlando-chi_orb-resolution-iteration8.md | chi_orb 归一化约定解析 |
| R8 | Iteration 7 memory/14 | 多星座交叉相关结果基线 |

---

## 8. 迭代计划概要

### 阶段预期

| 阶段 | 主要活动 | 预计产出 |
|------|----------|----------|
| 1-loop/01-05 | 任务澄清 + 目标澄清 + 任务分解 + 信息搜集 + 完备核验 | 6 个规划文件 |
| 1-loop/06-决策 | 评估进入 2-loop 的条件 | enter_2loop / needs_replan |
| 2-loop/01-06 | 执行 + 验证 + 置信度评估 + 分叉决策 | 数值结果 + memory 文件 |

### 前置条件

- Iteration 7 全部 1-loop + 2-loop 阶段已完成
- chi_orb 归一化约定解析完成 (memory/15)
- 现有脚本 10-olc-chiral-orf-triangular.py 和 11-multi-constellation-chiral-orf.py 可用
- 论文 v14 已编译 (P2 已完成)

### 置信度目标

初始置信度: 0.70 (基于 Iteration 6-7 的理论基础，但非共面构型的实际效果未知)
目标置信度: 0.80

---

## 9. 任务摘要表

| 项目 | 内容 |
|------|------|
| 任务 | 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型 |
| 物理动机 | 确认单三角 OLC 能否通过非共面构型实现可探测的手征响应 |
| 核心问题 | 非共面程度与 Gamma^V 的定量关系；单三角 vs 多星座手征响应的物理联系 |
| 通过标准 | P1-P5 (见第 4 节) |
| 硬约束 | H1-H4 (见第 4 节) |
| 输入 | I1-I6 (见第 5 节) |
| 输出 | O1-O6 (见第 5 节) |
| 关键风险 | R1 (轨道效应过小), R2 (Gamma^V < 1e-3) |
| 前置依赖 | D1-D4 (已完成) |
| 关键参考 | Orlando 2021, Iteration 6-7, memory/15, memory/16 |
| 初始置信度 | 0.70 |
| 目标置信度 | 0.80 |
| 预计工时 | 1-loop: ~4h, 2-loop: ~3h |

---

## 附录 A: 关键公式汇总

### A1. 手征重叠约化函数

```
Gamma^I = integral[dOmega / 4pi] [R_+1 * R_+2 + R_x1 * R_x2]
Gamma^V = integral[dOmega / 4pi] [R_+1 * R_x2 - R_x1 * R_+2]
```

### A2. E 变量天线模式 (CW sum)

```
R_E+ = sum_{CW links} F_+(link_k) * T(f, L, cos_nu)
R_Ex = sum_{CW links} F_x(link_k) * T(f, L, cos_nu)
```

### A3. Michelson 似然变量

```
M = Link(a→b→a) - Link(b→a→b)
R_A^M = R_A(link_a) + R_A(link_b)  (with F_A(u) = F_A(-u) → R_x^M = 0)
```

### A4. 归一化

```
norm_V = |Gamma^V| / sqrt(auto1 * auto2)
sky-max norm_V = max_over_sky[|R_+1*R_x2 - R_x1*R_+2| / sqrt(auto1*auto2)]
```

### A5. 非共面度量

```
coplanarity = |(r2-r1) · ((r3-r1) × n_ref)| / (|r2-r1| * |r3-r1| * |n_ref|)
其中 n_ref 是参考平面的法向量
```

---

## 附录 B: 与既有结果的对比

| 构型 | Gamma^V 量级 | 来源 |
|------|-------------|------|
| 单平面三角 OLC (Michelson) | = 0 (严格) | Iteration 6 |
| 单平面三角 OLC (E 变量) | < 1e-10 | 预期 (镜面反射对称性) |
| 单臂非共面链路对 | > 1e-3 at f>10mHz; ~0.041 at 30mHz | Iteration 6 |
| LISA × Taiji (交叉相关) | |Gamma^V|_max = 1.00 | Iteration 7 |
| OLC(30°) × Taiji(0°) (交叉相关) | |Gamma^V|_max = 0.99 | Iteration 7 |
| **单三角非共面 (本次迭代)** | **待确定** | **Iteration 8** |
