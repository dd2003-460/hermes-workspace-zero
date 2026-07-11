# 06-决策（Iteration 8）— 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/06-决策.md`
> 迭代编号：8
> 输入：01-任务澄清 + 05-完备核验

---

## 决策结论: enter_2loop

**置信度: 0.75** (>= 0.70 门槛)

**决定: 进入 2-loop 执行阶段**

---

## 核心科学问题

一个单三角形 OLC 星座（无需多星座交叉相关）能否通过"深度非共面构型"实现可探测的手征 ORF Gamma^V(f)？

### 物理动机

Iteration 6 严格证明：共面单探测器的 R^V = 0 是镜面反射对称性的推论。
Iteration 7 验证：多星座交叉相关通过 3D 空间分离破坏该对称性，实现 |Gamma^V|_max ~ 1.0。

本迭代要回答的核心问题：**单三角非共面（几何效应）能否与多星座交叉相关（网络效应）一样实现可探测的手征响应？**

如果答案是肯定的，将极大简化探测方案的系统设计需求——不需要多星座、不需要空间分离，仅通过单星座的非共面构型即可实现手征灵敏度。

---

## 关键已知结果 (Iterations 6-7)

| 编号 | 内容 | 量级 | 来源 |
|------|------|------|------|
| K1 | 共面三角 Michelson Gamma^V = 0 | 严格零 | Iteration 6 |
| K2 | 共面三角 E 变量 Gamma^V = 0 | 预期 < 1e-10 | 镜面对称性 |
| K3 | 单臂非共面链路对 Gamma^V | ~0.041 at 30 mHz, ~1.07 at 100 mHz | Iteration 6 |
| K4 | LISA x Taiji 交叉相关 | |Gamma^V|_max = 1.00 | Iteration 7 |
| K5 | 归一化约定区分 | norm_V = 1.0 for E variable | memory/15 |

关键矛盾：K3 显示单臂非共面链路对可实现 |Gamma^V| > 0.041，但 E 变量是三臂 CW sum——三臂贡献可能相互抵消。这是本迭代要验证的核心不确定性。

---

## 判定标准总结 (P1-P8)

| # | 判定标准 | 通过条件 | 验证方式 |
|---|---------|---------|---------|
| P1 | 共面 E 变量 Gamma^V < 1e-10 | 验证镜面对称性 | M2 回归测试 |
| P2 | 非共面 E 变量 Gamma^V > 1e-3 (f > 10 mHz) | 验证非共面性导致手征响应 | M3 核心扫描 |
| P3 | |Gamma^V|_sky_max > 0.01 | 与多星座结果比较基准 | M4 全参数扫描 |
| P4 | |Gamma^V| 与几何参数定量关系 R^2 > 0.5 | 建立物理模型 | M5 拟合 |
| P5 | 高频极限 |Gamma^V| > 1.0 | 验证单臂链路对标 | M2 单臂测试 |
| P6 | 网格收敛 < 10% | ntheta=32->64 验证 | M5 收敛测试 |
| P7 | Michelson Gamma^V < 1e-8 (任意非共面) | 与 Iteration 6 一致 | M2, M3 |
| P8 | 频率扫描 1 mHz - 100 Hz log-spaced >= 20 点 | 覆盖完整频段 | M2-M4 实现 |

---

## Gap 分析结论

**无 blocking gap。**

7 个已识别 gap 中：
- G1（脚本 12 未创建）是迭代核心产出，不属于 gap
- G3（E 变量三臂抵消）有高严重度但已有缓解方案（降级为单臂链路对）
- 其余 5 个 gap 为低/中严重度，不阻塞进入 2-loop

---

## 风险与缓解

| 风险 | 严重度 | 触发条件 | 缓解措施 |
|------|--------|---------|---------|
| R1/R6: E 变量三臂 CW sum 抵消 | **高** | M3 中所有构型 |Gamma^V| < 1e-8 | 降级为单臂链路对分析（M2 已覆盖此路径） |
| R2: 单三角非共面 Gamma^V < 1e-3 | 中 | 所有非共面构型结果 | 聚焦高频区 (f > 30 mHz) |
| R7: 脚本 12 接口对齐 | 中 | M2 共面零检验失败 | 修复后重新验证 |
| R3/R4/R5 | 低 | — | 预置降级策略 |

---

## 2-loop 执行计划

### DAG 拓扑

```
M1 (Fork) -> M2 (Zero-test) -> M3 (Core scan) -> M5 (Fit+Convergence) -> M6 (Summary)
                                        -> M4 (Full scan, 并行/可选)
```

### M1 (P0): Fork 脚本 12 + 基础框架
- **来源**: fork 10 + 11
- **内容**: `scripts/12-noncoplanar-triangular-chiral-orf.py`
  - `build_noncoplanar_triangle(theta_inc, delta_h, side_ratios)`
  - `coplanarity_measure(sat_positions)`
  - `compute_e_variable_chiral_orf(f, sat_positions, L)`
  - `compute_michelson_chiral_orf(f, sat_positions, L)`
  - `compute_single_arm_pair_chiral_orf(f, arm1, arm2)`
- **验收**: 代码编译通过，基础函数返回合理值

### M2 (P0): 回归验证 + 零检验
- **任务**:
  - P1: 共面等边三角形 E 变量 Gamma^V < 1e-10
  - P7: 任意非共面三角形 Michelson Gamma^V < 1e-8
  - P5: 单臂非共面链路对标 K3（|Gamma^V| > 0.041 at 30 mHz）
- **验收**: 三项全部通过则 M2 通过；若 P1 失败则回 M1 修复接口

### M3 (P0): 核心参数扫描
- **参数空间**: theta_inc (7 点) x delta_h/L (6 点) = 42 构型
- **频率**: 1 mHz - 100 Hz, log-spaced, >= 20 点
- **验收**:
  - P2: 至少一种构型的 Gamma^V > 1e-3 (f > 10 mHz)
  - P8: 频率扫描覆盖确认
  - 如所有 42 构型 Gamma^V < 1e-8 -> 触发 R6 -> 降级单臂链路对

### M4 (P1): 全参数扫描（质量降级可跳过）
- **扩展参数**: M3 + side_ratio (4 点) = 168 构型
- **验收**:
  - P3: |Gamma^V|_sky_max > 0.01
  - P4: 找到最优构型，建立 |Gamma^V| vs coplanarity 关系
- **决策门**: M3 确认后决定是否执行（M4 时间 ~32 min）

### M5 (P0): 拟合 + 收敛性验证
- **任务**:
  - P6: ntheta=32->64 收敛验证 (< 10%)
  - P4: |Gamma^V| vs 几何参数回归拟合（R^2 > 0.5）
- **验收**: 收敛性通过，拟合优度达标

### M6 (P0): 总结 + 可视化
- **产出**:
  - `ORF_data_8.csv`：所有构型 + 频率的 Gamma^V, Gamma^I, auto 值
  - `gammaV_vs_coplanarity.png`
  - `gammaV_vs_inclination.png`
  - `gammaV_frequency_comparison.png`
  - `comparison_multiconstellation.png`
  - `memory/17-noncoplanar-olc-chiral-orf-iteration8.md`
- **验收**: 所有输出文件存在且格式正确

---

## 失败条件

如果以下任一条件触发，终止迭代并重新规划：

1. **M2 接口验证失败**: E 变量共面 Gamma^V > 1e-8，且修复后仍 > 1e-8 -> 说明实现框架有偏差，需重新审视天线模式接口
2. **M3 零结果**: 所有 42 构型 E 变量 Gamma^V < 1e-8 -> 降级为单臂链路对分析；如单臂链路对也不达标，迭代终止
3. **M3 非物理发散**: 数值计算出现不收敛或溢出
4. **M5 网格不收敛**: ntheta=32->64 变化 > 20% -> 需要重新审视天区积分实现

---

## 退出条件

- **成功**: P1-P8 全部通过，信心度提升至 >= 0.80
- **部分成功**: P1, P5, P7, P8 通过，P2/P3 部分通过，信心度 0.75-0.80 -> 更新 memory 文件，进入下一迭代继续
- **降级成功**: E 变量方案失败但单臂链路对成功，信心度 0.70-0.75 -> 更新 memory 文件，进入下一迭代继续
- **失败**: 所有尝试均失败 -> 终止迭代，重新规划

---

## 副脑关注重点

```
next_brain_sub: 进入 2-loop/01，按 DAG 优先级执行 M1 -> M2 -> M3 -> M5 -> M6

sub_brain_focus:
  1. M1 是 gating milestone：脚本 12 的 build_noncoplanar_triangle 实现是否正确
     验证方法：构建已知构型（共面等边三角形），检查卫星位置
  2. M2 是第一个 gate：共面零检验必须通过
     如果 E 变量共面 Gamma^V > 1e-8，说明天线模式或归一化有问题
     如果 E 变量共面 Gamma^V < 1e-10 但 Michelson > 1e-8，说明 Michelson 实现有问题
  3. M3 是核心发现阶段：重点关注 theta_inc 与 |Gamma^V| 的关系
     预期：theta_inc = 0 时 Gamma^V = 0，theta_inc > 0 时 Gamma^V 单调增加
  4. 如 E 变量三臂抵消，降级方案必须在 M3 中立即启动
  5. M6 中 memory 文件必须包含：物理结论 + 与多星座结果的对比分析
```

---

## ⚠️ Iteration 8 M1/M2 已完成 — 结果已改变方向

```
M1 fork ✅: scripts/12 (920 lines) created
M2 zero-test ✅ (发现了根本约束):

结论: 单三角所有链路方向必然共面 (3点共面 = 几何定理)
→ 反射对称 → Gamma^V = 0 for ANY two-variable cross-correlation
→ 独立 Agent 验证 4 个问题无 loopholes
→ memory/17 和 memory/18 完整记录 null theorem

M3/M4/M5/M6: 无需执行 (所有构型 Gamma^V = 0 由几何保证)

next_brain_sub: 评估 null result 后的重新规划方向
  - 选项 A: 聚焦多星座交叉相关 (Iteration 7 已验证可行)
  - 选项 B: 探索 4+ 卫星构型 (tetrahedral) 打破共面性
  - 选项 C: 更新 decision doc，结束本迭代
```

---

## 置信度总结

| 维度 | 置信度 | 论据 |
|------|--------|------|
| 理论基础完整性 | 0.85 | Iteration 6 严格证明 + Iteration 7 验证 + memory/15/16 |
| 工程可行性 | 0.75 | Fork 策略正确，但脚本 12 接口对齐未知 |
| 工具就绪度 | 0.70 | 基础工具就绪，脚本 12 是本次核心产出 |
| 方向正确性 | 0.90 | P1-P8 全部覆盖，验证方法明确 |
| 可回滚性 | 0.95 | 不修改已有代码，回滚方案完整 |
| 核心假设 (G3) | 0.55 | E 变量三臂 CW sum 抵消是唯一高严重度不确定 |
| **综合置信度** | **0.75** | **>= 0.70 门槛 -> enter_2loop** |

---

last_updated: 2026-07-10
decision: enter_2loop
next_brain_sub: dispatch 2-loop/01, M1 fork script 12