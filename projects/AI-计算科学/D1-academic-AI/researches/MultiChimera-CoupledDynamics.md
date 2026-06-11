# Multi-Chimera Coupled Dynamics: Coexistence, Competition, and I_C Topology

**日期**：2026-06-03
**阶段**：1-loop (executor design)
**状态**：实验设计草案（待验证）
**依赖**：D4-S18-r18 (多相凝聚), D4-S18-r20 (strict chimera), D4-S18-r22 (gradient-locking), D4-S18-r23 (diagnostic formalization), D4-S18-r25 (local coupling synchronization)

---

## 问题陈述

已有研究确认：在 Abrams-Strogatz 设置下（空间异质耦合 K(x) = K0(1+eps*cos(2px))），N>=500 可重现单 chimera 态。但核心开放问题是：

> **多个 chimera 态能否在同一个耦合振荡器系统中稳定共存？**

如果多个 chimera 可以共存，系统设计变量（域划分、耦合 DOF、I_C）如何影响共存/竞争相变？

这与 D4-S18-r18c 的最终结论形成张力：均匀耦合不产生 M>=2 多相态。但如果 **空间异质耦合** 被分段设计，能否诱导多 chimera 相？

---

## 核心假设

### 假设 1：域隔离 chimera (DC)
在圆形振子阵列上，用空间耦合函数 K(x) 制造两个独立的"chimera生产区"，如果域间耦合足够弱，两个 chimera 应能稳定共存。

### 假设 2：域间耦合 → 竞争相变
当域间耦合强度越过某个临界值，两种竞争模式出现：
- **One-wins**：一个 chimera 的同步区域吞噬另一个
- **Phase-slip coexistence**：两个 chimera 共存，但有持续的相位滑动 (phase slip)

### 假设 3：I_C 拓扑可表征多 chimera
I_C (拓扑不变量) 在单 chimera 下为 1 (b_0=1, b_1=1, chi=0, w_2=1)。在多 chimera 下，预期 I_C = M（M 个 chimera 区域），或更复杂的拓扑结构。

---

## 实验设计

### 实验 M1：分段域 chimera (Domain-Partitioned Chimera)

**目标**：验证多 chimera 共存的可能性

**系统设置**：
- N = 800 个振子，环形拓扑
- 位置：x_i = i/N, i = 0, ..., N-1
- **空间耦合函数 K(x)** 分为 4 个域：

```
域 A [0, 0.25):    K(x) = K0 * (1 + eps_A * cos(2px))
边界 [0.25, 0.35): K(x) = K_transition
域 B [0.35, 0.60): K(x) = K0 * (1 + eps_B * cos(2p(x - delta)))
边界 [0.60, 0.70): K(x) = K_transition
域 C [0.70, 1.0):  K(x) = K0 * (1 + eps_C * cos(2px))

其中:
K0  = 1.0 (全局耦合基准)
eps_A = eps_B = eps_C = 0.6 (域内异质耦合强度)
delta = 0.1 (域 B 的 chimera 中心偏移)
K_transition: 过渡区的耦合强度，作为调参旋钮
```

**控制参数**：K_transition 从 0.0 到 K0，步长 0.1

**预期相图**：

| K_transition | 预期现象 |
|------------|---------|
| 0.0 | 完美隔离，两个 chimera 独立演化 |
| 0.1-0.3 | 弱耦合共存，可能存在相位同步 |
| 0.4-0.6 | 竞争相变区域，一个 wins 或 phase slip |
| 0.7-1.0 | 强耦合融合，全局 chimera（统一同步域） |

**测量协议**：
1. 每个域的局部序参量 r_b(t) — 用 ChimeraDetector 分别检测每个域
2. 域间互相关：C_AB(tau) = <r_A(t) r_B(t+tau)> - <r_A><r_B>
3. Phase slip 计数：对每个域计算相位累积量，统计 integer winding events
4. I_C 拓扑：计算同步区域的 persistent homology，估计 b_1 (cycle count)

**失败条件**：如果 K_transition 在整个扫描范围内都只产生单 chimera 或全局同步，则假设 1 不成立，多 chimera 在耦合振子系统中不可行。

---

### 实验 M2：耦合 DOF 参数相图

**目标**：刻画 (K0, eps, delta) 三维空间中的共存/竞争边界

**参数空间**：
- K0: [0.5, 1.5] x 0.1 步长
- eps: [0.3, 0.9] x 0.1 步长
- delta: [0.0, 0.3] x 0.05 步长
- K_transition: [0.0, K0] x 0.1 步长

**总参点数**：11 x 7 x 7 x 16 = 8,512（计算密集型）

**测量**：对每个参数组合，用快速扫描 (T_transient=2000, T_measure=500)：
1. chimera_score_A, chimera_score_B（每个域的 chimera 强度）
2. cross_correlation = <R_A R_B> - <R_A><R_B>
3. chimera_oscillation_frequency（FFT 分析同步率波动）
4. I_C estimate（persistent homology）

**数据分析**：
- 绘制 3D 相图切片（固定两个参数，扫描第三个）
- 标记三个相区：coexistence / one-wins / phase-slip
- 搜索可能的临界尺度 (critical exponents)

---

### 实验 M3：I_C (Chimera Information) 在多 chimera 系统中的度量

**目标**：建立 I_C 与 M（chimera 数量）的关系

**理论基础**（D1-r02）：
- I_C = chi_Euler + |w_2|
- 单 chimera：I_C = 1
- 多 chimera：预期 I_C = M 或更复杂

**度量方案**：

1. **序参量拓扑方法**：
   - 对同步率场 r(x,t) 构建 Vietoris-Rips 复形
   - 计算 persistent homology H_0（connected components）和 H_1（cycles）
   - b_1 的变化反映 chimera 边界形成的拓扑特征

2. **信息论方法**：
   - I_C ≈ H(spatial_r) — H(temporal_r) 其中 r 是同步率场
   - 高 H(spatial_r) 表示空间异质性（多 chimera 特征）
   - 低 H(temporal_r) 表示动力学稳定性

3. **混合方法**：
   ```
   I_C_multi = b_1(spatial_persistence) + |H_1(velocity_field)|
   
   验证: I_C(M chimera) >= M × I_C(1 chimera)
   ```

**输入**：实验 M1 和 M2 的同步率场数据

---

### 实验 M4：Phase Slip Dynamics 与能量景观

**目标**：理解 one-wins vs. coexistence 竞争的微观动力学

**方法**：
1. 在竞争边界参数处运行长时间模拟 (T > 100000)
2. 用有效 Hamiltonian 分析：
   ```
   H = -K0 * SUM_ij K(x_i,x_j) * cos(theta_i - theta_j) + potential(eps, delta)
   ```
3. 估计自由能 F = -kT ln(Z) 随序参量 M 的曲线
4. 寻找双势阱结构（对应 two-well potential for M=1 vs M=2）

**预期结果**：
- 在 coexistence 区域：双势阱均很深
- 在 one-wins 区域：一个阱远深
- 在 phase-slip 区域：两阱深度相近，存在 thermal-like fluctuation

---

## 与已有代码的接口

### chimera_detector.py (chimera_lab)

```python
from chimera_detector import ChimeraDetector, ChimeraPhase

detector = ChimeraDetector(n_windows=10, gamma=0.5)

# 在 M1 中使用，对每个域切片相位数据
phase_A = theta[0:N//4]  # 域 A 的相位
det_A = detector.detect(phase_A, history=history_A)
# 返回值包含：phase, strength, r_local, r_max, r_min, r_global

# 验证条件：det_A.phase == ChimeraPhase.PHASE_III_CHIMERA_STABLE
#           and det_B.phase == ChimeraPhase.PHASE_III_CHIMERA_STABLE
```

### chimera_diagnostic_v2.py (labs/simulations)

用于验证检测到的 chimera 是否是真的 chimera（而非 gradient-locking artifacts）：

```python
from chimera_diagnostic_v2 import ChimeraDiagnosticV2

diagnostic = ChimeraDiagnosticV2(n=200, dt=0.005, n_segments=4)
result = diagnostic.detect_chimera(theta, ...)

# result 包含:
#   phase: "chimera" | "gradient_locking" | "mixed"
#   mpi: 机制纯度指数
#   sci: 空间相干窗口不变量
#   tfd: 时间涨落诊断
#   confidence: 置信度

# 对多 chimera 系统：每个域独立运行诊断
```

### experiment_chimera_spatial_coupling.py (labs/simulations)

现有的单 chimera 实验代码是 M1 的基础框架，需要扩展为多域设置：
- 原始：单空间耦合 K(x) = K0*(1+eps*cos(2px))
- M1 扩展：分段的 K(x) 函数，每域有不同的中心位置和强度

---

## 理论命题汇总

### 命题 M-T1：多 chimera 共存域窗口

存在耦合阈值 K*_transition(N, K0, eps)，使得：
- K_transition < K*: M >= 2 chimera 相共存
- K_transition > K*: 退化为单 chimera 或全局同步

### 命题 M-T2：I_C 计数定理

在多 chimera 系统中，I_C 等于系统中稳定 chimera 区域的数量：
$$I_C = \sum_{m=1}^{M} I_C^{(m)} \approx M$$

这直接验证 I_C 作为 chimera 计数量的拓扑意义。

### 命题 M-T3：Phase Slip Rate 的临界标度

在 coexistence 与 one-wins 的边界附近，phase slip rate 满足：
$$\lambda_{slip} \sim |K_transition - K*_transition|^{beta}$$

其中 beta 是新的临界指数（不同于标准相变）。

---

## 与 UNIFIED-FRAMEWORK 的连接

### 定理 3：多层级耦合一致性

在多 chimera 系统中，每个 chimera 对应一个子系统层级。定理 3 要求：
$$\frac{1}{M} \sum_{m=1}^{M} [R_m(t) - \bar{R}(t)]^2 \leq epsilon(t) \to 0$$

这里的挑战是：**多 chimera 本身就是"不一致"的稳态**，因此定理 3 可能需要修正为存在多极小值：
$$\frac{1}{M} \sum_{m=1}^{M} [R_m(t) - \bar{R}(t)]^2 \leq epsilon(t) \quad \text{OR} \quad R_m \neq R_{m'}$$

即：要么所有 chimera 同步（高一致性），要么各自独立演化（允许的不一致 = 新的涌现行为）。

### 定理 4：涌现自主性 = 对称破缺速率

多个 chimera 共存对应更高的对称破缺（更多子域自组织）。自主性度量应为：
$$A_{multi} = \frac{d}{dt} \sum_{m=1}^{M} H(R_m)$$

这比单 chimera 的 A 更能体现系统的信息处理能力。

---

## 实施计划与优先级

### Phase 1（快速验证，1-2 周）
- 修改 `experiment_chimera_spatial_coupling.py` 为多域版本
- 运行实验 M1（3 个域，扫描 K_transition）
- 里程碑：确认或否定多 chimera 共存的可能性

### Phase 2（深度分析，2-4 周）
- 实现 ChimeraDiagnosticV2 的多域支持（输入处理 + 域分割）
- 运行实验 M2（参数相图）
- 将 persistent homology 计算接入 pipeline

### Phase 3（理论深化，4-6 周）
- I_C 的持久同调计算方法
- Phase slip dynamics 建模
- Hamiltonian/Free energy 分析

### Phase 4（论文准备，1-2 周）
- 数据整合，可视化
- 理论命题验证
- 撰写预印本章节

---

## 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| 多 chimera 在耦合振子中无法共存 | 30% | Phase 1 快速否定 |
| N 需要极大才能分辨多 chimera | 20% | 尝试 N=200, 400 的缩放测试 |
| Phase slip 时间尺度超出计算预算 | 25% | 改用序参量方法间接测量 |
| I_C 拓扑与 chimera 数量不对应 | 15% | 混合 I_C + 信息论方法 |
| 与 gradient-locking 混淆 | 10% | diagnostic v2 双阶段协议自动排除 |

---

## 验收标准

1. [ ] 至少在 (K_transition, N) 空间的某一区域观察到 2+ chimera 域同时为 Phase III
2. [ ] 绘制清晰的 (K_transition, K0) 相图，标记 coexistence / one-wins 边界
3. [ ] 给出 I_C(M chimera) 的数值估计，验证 I_C ~ M 的假设
4. [ ] Phase slip rate 的临界指数 beta 有可重复的测量值
5. [ ] chimera_detector.py + ChimeraDiagnosticV2 对多域系统的检测结果可解释

---

*设计完成：2026-06-03*
*此文档为多 chimera 共存的实验设计，后续需经过 1-loop 流程确认后再进入 2-loop 执行阶段*
