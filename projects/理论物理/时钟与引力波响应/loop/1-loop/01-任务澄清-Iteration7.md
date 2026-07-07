# 01-任务澄清（Iteration 7）— 多星座手征 ORF 计算

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/01-任务澄清.md`
> 迭代编号：7
> 优先级：P0（承接 Iteration 6 completed，填补手征 SGWB 探测的核心空白）
> 触发条件：loop_phase = idle，Iteration 6 已全部完成

---

## 一句话任务

突破单一三角 OLC 星座 Michelson-like 变量的手征 ORF = 0 限制，计算**多星座混合网络**（OLC triangle + LISA/Taiji）的交叉相关手征 ORF，验证不同星座间能否获得非零 Gamma^V。

---

## 任务描述

### 核心问题

Iteration 6 严格证明了：

1. **三角 OLC Michelson-like 变量：Gamma^V = 0（所有构型，所有频率）**
2. **物理原因**：F_A(u) = F_A(-u)（偶函数对称性），导致 Michelson 变量的两个臂响应相等 R_+^M(a) = R_+^M(b)，chiral factor (R_+1 * R_x2 - R_x1 * R_+2) 严格为零
3. **替代方案已验证但受限**：单臂非共面 OLC 对 |Gamma^V| > 1e-3（f > 10 mHz），但牺牲了 Michelson-like 的噪声抑制

### Iteration 6 后新发现：非对称权重打破零结果

**验证实验**（Iteration 7 启动时执行）：测试非 Michelson 线性组合

| 组合 | Gamma^V | 物理含义 |
|------|---------|---------|
| (M_X, M_Y) — 标准 Michelson | ~0 | 对称权重 (1,1) |
| (M_E, M_X) — E-like vs M_X | ~0 | Michelson 间权重不等 |
| (M_T, M_X) — T-like vs M_X | ~0 | Michelson 间权重不等 |
| (M_X_{2:1}, M_Y) — 内部权重 (2,1) | ~0 | 内部权重不等但同号 |
| **(M_X_{1:-1}, M_Y)** | **7.8e-03** | **内部权重 (1,-1)，符号相反** |

**物理机制**：(1,-1) = link(a→b) - link(b→a)，依赖 **sign(cos_nu)** 打破镜像对称。

**代价**：失去噪声抵消能力。单一星座内仅当权重内部符号相反时才打破零结果。多星座网络仍是最有前景的路径。

论文草稿声称三角 OLC 可达 |Gamma^V| ~ 0.3（与 PTA、LISA-Taiji 相当），但此声称基于 **LISA-Taiji 双网络的外推**，而非实际计算。

### 突破路径：多星座混合网络

**关键洞察**：对称性破缺的条件是打破 F_A(u) = F_A(-u) 的条件。

单一星座内，Michelson 变量 M = link(a->b->a) - link(b->a->b) 天然具有臂响应对称性。但**不同星座之间的交叉相关**不再需要满足这种对称性：

- OLC triangle (S1,S2,S3) 与 Taiji triangle (T1,T2,T3) 有不同的空间位置、轨道倾角、臂长
- OLC 与 LISA 可能有不同的测量物理量（OLC = 频率偏移，LISA = 应变差）
- 不同星座的 Michelson 变量 X_OLC 与 X_Taiji 的交叉相关：R_+^X_OLC(a) 不一定等于 R_+^X_Taiji(b)

**为什么有效**：交叉相关涉及两个不同探测器的天线方向图和传递函数的乘积，不再是同一探测器的自关联，对称性条件 F_A(u) = F_A(-u) 不再导致 chiral factor 为零。

### 候选星座组合

| 组合 | 类型 | 可测量 | 物理一致性 |
|------|------|--------|-----------|
| OLC triangle x Taiji triangle | 三角 x 三角 | 频率偏移 x 频率偏移 | 高 — 相同可测量 |
| OLC triangle x LISA triangle | 三角 x 三角 | 频率偏移 x 应变 | 中 — 不同可测量，需统一归一化 |
| Taiji triangle x LISA triangle | 三角 x 三角 | 应变 x 应变 | 高 — 已有文献基准 (Orlando 2021) |
| OLC triangle x OLC triangle (不同构型) | 三角 x 三角 | 频率偏移 x 频率偏移 | 高 — 两个独立 OLC 星座 |

**P0 优先级**：OLC triangle x Taiji triangle（相同可测量类型，Taiji 是中国空间引力波探测计划，与本项目的物理背景一致）

### 理论基础

本项目的理论基础已经成熟：

1. **Iter. 6 的 chiral ORF 计算引擎**（`scripts/10-olc-chiral-orf-triangular.py`）实现了三角星座 Michelson 变量的 chiral ORF 计算
2. **Iter. 5/6 的 chiral ORF 求解器**（`scripts/09-olc-chiral-orf.py`）实现了两探测器对的交叉相关 chiral ORF 计算
3. **Iter. 3 的混合网络代码**（`scripts/06a-patched-mixed-network.py`）已修复了 OLC+LISA 的 4 个物理 bug，包含 SNR 框架
4. **JCAP 2025 Chen-Liu-Zhang**（JCAP 05, 050 (2025), arXiv:2410.18916）提供了双三角网络的 chiral ORF 计算方法（长波近似框架）
5. **Orlando et al. 2021 JCAP**（JCAP 069, 2021）LISA-Taiji 网络的手征 ORF 计算是验证基准

### 文献对标

| 文献 | 星座 | Gamma^V_max | 方法 |
|------|------|------------|------|
| Orlando et al. 2021 | LISA x Taiji (60 deg inclination) | ~0.3 | 标准 ORF formalism |
| Chen-Liu-Zhang JCAP 2025 | dual-triangle | 未明确 | 长波近似 |
| Kato & Soda 2016 | PTA (many pulsars) | ~0.3 | 广义 ORF |
| **OLC triangle (Iter. 6)** | OLC self | **0** | Michelson-like |
| **Iteration 7 目标** | **OLC x Taiji / LISA** | **待测定** | **混合网络** |

---

## 科学问题

### SQ1: 混合星座 chiral ORF 是否非零？

**问题陈述**：不同星座之间的交叉相关能否突破单一星座的对称性限制，产生可观测的 Gamma^V？

**预期结果**：是。不同星座的空间位置、轨道倾角、臂长差异破坏了 F_A(u) = F_A(-u) 的对称性条件。

**物理机制**：
- OLC triangle 的 Michelson 变量 M_OLC = link(1->2->1) - link(2->1->2)
- Taiji triangle 的 Michelson 变量 M_Taiji = link(T1->T2->T1) - link(T2->T1->T2)
- 交叉相关中：R_+^M_OLC 和 R_+^M_Taiji 是**不同探测器**的响应，无对称性约束
- chiral factor: R_+^M_OLC * R_x^M_Taiji - R_x^M_OLC * R_+^M_Taiji 一般非零

### SQ2: 网络灵敏度对比

**问题陈述**：混合网络（OLC + Taiji/LISA）的 chiral SNR 相比单一星座是否有显著提升？

**关注点**：
- 单一星座（OLC）Gamma^V = 0，chiral SNR = 0
- 混合网络 Gamma^V 非零，chiral SNR > 0
- 提升因子 = (chiral SNR_mixed) / (chiral SNR_OLC alone) = 无穷大（从 0 到有值）

### SQ3: JCAP 2025 framework 适用性

**问题陈述**：Chen-Liu-Zhang 的双三角网络框架（长波近似）能否直接用于 OLC 频率范围（mHz - Hz）？

**答案**：不能完全直接套用。OLC 的工作频段覆盖了长波近似失效的区域。需要使用本项目 Iteration 6 建立的**全频段精确 ORF 计算框架**（数值天区积分），而非长波近似公式。

---

## 目标

### 期望产出（Iteration 7 完成标志）

1. **混合星座 chiral ORF 数值表**：对 OLC x Taiji、OLC x LISA、Taiji x LISA 三种组合给出 Gamma^V(f)
2. **频率依赖曲线**：在 0.1 mHz - 10 Hz 范围内绘制 Gamma^V(f)
3. **单一星座 vs 混合网络对比**：可视化展示混合网络的优势
4. **物理解释**：说明非零 chiral ORF 的几何来源

### 理论目标

1. **确认突破**：验证混合星座确实能产生非零 chiral ORF
2. **量化优势**：给出混合网络的 chiral ORF 量级，与 PTA/LISA-Taiji 对比
3. **指导任务设计**：为未来空间时钟星座网络的 chiral 探测能力提供定量约束

---

## 判定标准

### 必须满足（Pass/Fail）

| # | 判定标准 | 通过条件 |
|---|---------|---------|
| 1 | **混合星座非零检验** | OLC x Taiji 的 |Gamma^V| > 1e-3（至少在某些频率） |
| 2 | **自关联零** | OLC x OLC（同星座自关联）的 |Gamma^V| < 1e-10（确认与 Iter. 6 一致） |
| 3 | **频率平坦性** | |Gamma^V(f)| 在公共频段内变化 < 1 个量级（归一化后） |
| 4 | **归一化自洽** | 标准 ORF Gamma^I 量级在 0.01 - 1.0 范围内（确认代码正确） |
| 5 | **收敛性** | ntheta=32->64 时，|Gamma^V| 变化 < 10% |
| 6 | **Orlando 基准** | Taiji x LISA 组合的 |Gamma^V| 在 f -> 0 极限下与 Orlando et al. 2021 的 LISA-Taiji 结果一致（~0.3） |

### 失败标准

- 所有混合星座组合的 |Gamma^V| < 1e-3：chiral 灵敏度仍然不可观测（需要 4+ 卫星星座或完全不同的可观测构造）
- |Gamma^V| 发散或 > 1.0：数值错误或公式错误

### 理想达到（Best case）

| # | 目标 | 说明 |
|---|-----|------|
| A | |Gamma^V|_max >= 0.05 | 达到有意义的手征灵敏度 |
| B | 不同构型有明显差异 | 展示几何参数对 chiral ORF 的影响 |
| C | 给出最优星座参数 | 为未来任务设计提供指导 |

---

## 硬约束

### 不可妥协的条件

1. **复用已有代码框架**
   - 在 `scripts/10-olc-chiral-orf-triangular.py` 的基础上扩展，不修改原文件
   - 使用 `scripts/09-olc-chiral-orf.py` 中的 chiral ORF 求解器作为 double-check
   - 使用 `scripts/06a-patched-mixed-network.py` 中的 detector 参数（噪声模型、灵敏度）

2. **与 Iteration 6 方法论一致**
   - 天区数值积分（不用留数定理，保持数值积分方法）
   - 网格：ntheta >= 32, nphi >= 64
   - 积分权重：sin(theta) * (pi/ntheta) * (2*pi/nphi)
   - 归一化：sqrt(auto1 * auto2)

3. **Michelson 变量构建一致**
   - 每个 Michelson 变量 = 两条反向单向链路的相干叠加
   - 有效天线方向图 = 两条链路天线方向图的叠加（包含传递函数）

4. **代码 fork 原则**
   - 新建 `scripts/11-multi-constellation-chiral-orf.py`（fork 自 Iter. 6 代码）
   - 不修改任何已有脚本

5. **探测器参数定义**
   - OLC triangle: 臂长 L_OLC = 0.17 - 3 Gm（空间 OLC 参数）
   - Taiji triangle: 臂长 L_Taiji = 2.5 Gm（Taiji 设计参数）
   - LISA triangle: 臂长 L_LISA = 2.5 Gm
   - 不同星座的相对位置：假设在同一日心轨道上（最小复杂度）

### 理论基础约束

6. **不同可观测量的处理**
   - OLC x OLC/Taiji（相同可测量）：直接使用 chiral ORF 公式
   - OLC x LISA（不同可测量）：需要将频率偏移灵敏度转换为等效应变灵敏度，或使用通用的 cross-correlation framework
   - 建议：优先实现相同可测量类型（OLC x Taiji），不同可测量类型作为扩展

7. **相对几何**
   - 不同星座的相对取向：需要参数化（相对倾角、相对相位、相对距离）
   - 推荐从最简单情况开始：两个星座在同一轨道平面、固定相对相位
   - 参考 Orlando et al. 2021：通过轨道倾角变化来扫描 chiral ORF

---

## 输入/输出

### 输入

| 输入 | 来源 | 说明 |
|------|------|------|
| OLC 传递函数 | `scripts/10-olc-chiral-orf-triangular.py` | fork 使用 |
| Michelson 变量天线方向图 | `scripts/10-olc-chiral-orf-triangular.py` | 扩展为多星座 |
| 双探测器 chiral ORF 求解器 | `scripts/09-olc-chiral-orf.py` | 交叉验证 |
| Detector 参数 | `scripts/06a-patched-mixed-network.py` | 噪声、灵敏度 |
| 手征 ORF 理论 | Hu PRD + Kato & Soda 2016 + Orlando 2021 | 公式参考 |
| JCAP 2025 框架 | Chen-Liu-Zhang JCAP 05, 050 (2025) | 多星座框架参考 |

### 输出

| 输出 | 说明 |
|------|------|
| `scripts/11-multi-constellation-chiral-orf.py` | 主计算脚本 |
| 混合星座 chiral ORF 数值表 | Gamma^V 对 OLCxTaiji, OLCxLISA, Taiji x LISA |
| 频率依赖曲线 | |Gamma^V(f)| 在公共频段的行为 |
| 单一星座 vs 混合网络对比图 | 可视化混合网络的优势 |
| 更新 memory 文件 | 记录 Iteration 7 的发现和结论 |
| 更新论文段落 | 在 draft 中替换外推性陈述为实际计算结果 |

---

## 风险与依赖

### 风险

| 风险 | 严重性 | 缓解措施 |
|------|--------|---------|
| 混合星座 Gamma^V 仍接近零 | **HIGH** | 如果不同星座间对称性仍未被打破，探索 4+ 卫星构型或完全不同的观测组合 |
| 不同可观测量的交叉相关定义不明确 | **HIGH** | 优先实现相同可测量类型；对不同可测量类型使用通用 cross-correlation framework |
| JCAP framework 不直接适用于 OLC | **MEDIUM** | Chen-Liu-Zhang 使用长波近似，OLC 需要全频段精确方法 — 使用本项目 Iter. 6 框架替代 |
| 数值计算量大（多星座+多构型） | 中 | 控制网格密度，使用向量化 numpy 运算，必要时降低 n_orient |
| 星座间相对几何参数化复杂 | 中 | 从最简单几何（同一轨道平面、固定相位）开始，逐步增加复杂度 |

### 依赖

1. **Iteration 6 代码**：三角 OLC 的 Michelson 变量构建 + chiral ORF 计算引擎已验证正确
2. **Iteration 5/6 chiral ORF 求解器**：双探测器交叉相关框架已验证
3. **Iteration 3 混合网络代码**：已修复 4 个物理 bug 的 SNR 框架
4. **Orlando et al. 2021 基准**：LISA-Taiji 的 chiral ORF ~0.3，用于验证代码正确性
5. **Chen-Liu-Zhang JCAP 2025**：双三角框架参考（但在长波近似下）

### 前置依赖

- Iteration 6 1-loop + 2-loop completed ✅
- 三角 OLC chiral ORF = 0 的对称性证明已完成 ✅
- 混合网络 SNR 框架（06a-patched-mixed-network.py）已修复 ✅

---

## 方法论说明

### 为什么使用交叉相关而非自关联

单一星座的自关联 chiral ORF = 0 是因为：
- Michelson 变量 M_i = link(a) + link(b) 的响应 R^M_i = R_a + R_b
- 当计算 M_i x M_j 的 chiral ORF 时，R_a 和 R_b 的对称性导致 chiral factor = 0

混合星座的交叉相关涉及：
- M_OLC 的响应 R_OLC 与 M_Taiji 的响应 R_Taiji
- R_OLC 和 R_Taiji 来自不同探测器的不同几何
- 没有 R_OLC(a) = R_OLC(b) 的对称性约束
- chiral factor = R_OLC+ * R_Taiji_x - R_OLC_x * R_Taiji+ 一般非零

### 与 Orlando 2021 LISA-Taiji 的关系

Orlando et al. 2021 的核心发现是：
- LISA 和 Taiji 两个三角星座之间存在非零 chiral ORF
- 轨道倾角 60 度时 |Gamma^V|_max ~ 0.3
- 轨道倾角 0 度（共面）时 |Gamma^V| = 0

**本 Iteration 7 的差异化**：
- 不仅验证 LISA-Taiji，还探索 OLC-Taiji、OLC-LISA
- 使用全频段精确计算（非长波近似）
- 探索 OLC 独特频段（0.1-10 Hz，LISA 灵敏度较低的区间）

---

## 任务总结

| 项目 | 内容 |
|------|------|
| **核心问题** | 不同星座的交叉相关能否突破单一星座 chiral ORF = 0 的限制？ |
| **突破口** | 不同星座打破 F_A(u) = F_A(-u) 对称性 |
| **预期量级** | |Gamma^V|_max ~ 0.01 - 0.3（对标 LISA-Taiji） |
| **失败信号** | |Gamma^V|_max < 1e-3（需要 4+ 星座或其他方案） |
| **关键创新** | 首次在 OLC 框架下计算多星座混合网络的手征 ORF |
| **工作量估计** | 1-2 天（编码 + 运行 + 分析） |
| **文件产出** | `scripts/11-multi-constellation-chiral-orf.py` + memory + paper update |

---

## 副脑质疑

**质疑#1（CRITICAL）**：如果同一星座内 Michelson 变量的对称性导致 Gamma^V = 0，那么不同星座间的对称性能否真正被打破？两个三角星座（OLC 和 Taiji）的 Michelson 变量仍然各自具有 R_a + R_b 的结构，chiral factor = (R_OLC_a+ + R_OLC_b+) * (R_Taiji_x) - (R_OLC_x) * (R_Taiji_a+ + R_Taiji_b+) 是否可能仍然为零？需要仔细分析。

**质疑#2（HIGH）**：Orlando et al. 2021 的 LISA-Taiji 非零 chiral ORF 的关键因素是**60 度轨道倾角**。如果 OLC 和 Taiji 在同一轨道平面（0 度倾角），chiral ORF 是否仍然非零？还是仅由轨道倾角驱动？

**质疑#3（MEDIUM）**：OLC 的频率偏移测量与 LISA 的应变测量之间如何定义交叉相关？两种可观测量的量纲不同，直接相乘的物理意义不明确。是否需要先转换为统一的应变等效形式？

**质疑#4（MEDIUM）**：如果多星座交叉相关确实给出非零 chiral ORF，这个效应的大小是否足以实际探测到？需要同时进行 chiral SNR 计算，评估在典型 Omega_GW 模型下需要多长的观测时间才能达到可探测性。

---

last_updated: 2026-07-05
next_brain_sub: 进入 02-目标澄清阶段
