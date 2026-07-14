# 03-任务分解（Iteration 8）— 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型

> 所属规格：`loop/1-loop/03-任务分解.md`
> 迭代编号：8
> 输入：`loop/1-loop/01-任务澄清-Iteration8.md` + `loop/1-loop/02-目标澄清-Iteration8.md`
> 输出：本文件 + DAG 拓扑排序 + 并行方案

---

## 核心科学问题

在 Iteration 6 严格证明三角 OLC Michelson-like 变量手征 ORF = 0、Iteration 7 验证多星座混合网络 |Gamma^V| ~ 1.0 的基础上，Iteration 8 回答一个更基本的问题：**单个三角形 OLC 星座能否通过非共面构型本身实现可探测的 Gamma^V？**

**关键物理洞察**：单平面探测器 R^V = 0 源于镜面反射对称性。打破镜面反射对称性的方法有：
1. **多星座方案** (Iteration 7)：不同轨道位置的空间分离导致 3D 网络效应
2. **单三角非共面方案** (Iteration 8)：单个三角形的三卫星不在同一平面内

本迭代专注方案 2。目标是建立 |Gamma^V| 与非共面几何参数的定量关系。

---

## 子任务分解

### M1: 代码 Fork + 非共面构型基础框架
**优先级**: P0（阻塞所有后续任务）
**依赖**: 无（直接承接 Iteration 6/7 代码）

**输入**:
- `scripts/10-olc-chiral-orf-triangular.py` — fork 源：Michelson 变量 + 单臂链路响应
- `scripts/11-multi-constellation-chiral-orf.py` — fork 源：E 变量 CW sum + 归一化
- `scripts/test_crosscorr_symmetry.py` — 对称性验证框架参考

**输出**:
- `scripts/12-noncoplanar-triangular-chiral-orf.py` — 主计算脚本
  - `build_noncoplanar_triangle(theta_inc, delta_h, side_ratios)` — 构建非共面三角形构型
  - `coplanarity_measure(sat_positions)` — 标量三重积非共面度量
  - `compute_e_variable_chiral_orf(f, sat_positions, L)` — E 变量 (CW sum) chiral ORF
  - `compute_michelson_chiral_orf(f, sat_positions, L)` — Michelson chiral ORF（预期 = 0）
  - `compute_single_arm_pair_chiral_orf(f, arm1, arm2)` — 单臂非共面链路对（对标已知结果 K3）
  - 参数扫描引擎：theta_inc x delta_h/L x side_ratio

**关键技术决策**:
- 非共面构型构造：先构建等边三角形在 xy 平面，绕 X 轴旋转 theta_inc，沿法线方向附加高度差 delta_h
- 非共面度量：coplanarity = |(r2-r1) . ((r3-r1) x n_ref)| / (|r2-r1| * |r3-r1| * |n_ref|)
- E 变量天线：R_E+ = sum_{CW} F_+ * T, R_Ex = sum_{CW} F_x * T，norm_V = 1.0
- Michelson 变量复用 Iteration 6 的往返对称性验证

**验收标准**:
- Fork 脚本可独立执行，不修改源文件
- 共面极限 (theta_inc=0, delta_h=0, side_ratio=1.0) 下 E 变量 Gamma^V < 1e-10
- Michelson 变量共面 Gamma^V < 1e-10
- 单臂非共面链路对在 30 mHz 达到 |Gamma^V| ~ 0.041（对标 K3）

---

### M2: 共面零检验 + 单臂链路对基准
**优先级**: P0（最快回归验证）
**依赖**: M1

**输入**:
- M1 产出的 `scripts/12-noncoplanar-triangular-chiral-orf.py`

**输出**:
- 共面 E 变量 Gamma^V < 1e-10 验证结果
- 共面 Michelson Gamma^V < 1e-10 验证结果
- 单臂非共面链路对 Gamma^V(f) 曲线，与已知结果 K3 对标（0-0.5 mHz 偏差 < 20%）

**关键技术**:
- 共面等边三角形：theta_inc=0, delta_h=0, side_ratio=1.0
- 验证网格 ntheta=32, nphi=64
- 频率覆盖 1 mHz 到 100 Hz，log-spaced，至少 20 个点

**验收标准**:
- P1 通过：共面 E 变量 Gamma^V < 1e-10
- P7 通过：共面 Michelson Gamma^V < 1e-8
- 单臂链路对高频 |Gamma^V| > 1.0（对标 P5）

---

### M3: 非共面参数扫描 P0+P1（theta_inc x delta_h/L）
**优先级**: P0（核心计算任务）
**依赖**: M2（回归通过）

**输入**:
- M2 验证通过的代码框架

**输出**:
- 至少 12-21 种非共面构型的 Gamma^V(f) 数值表
- 初步趋势：|Gamma^V| 随 theta_inc 和 delta_h/L 的变化

**关键技术**:
- P0 网格：theta_inc = [0, 30, 60, 90] x delta_h/L = [0, 0.25, 0.5] → 12 种构型
- P1 网格：theta_inc = [0, 15, 30, 45, 60, 75, 90] x delta_h/L = [0, 0.25, 0.5] → 21 种构型
- side_ratio 固定为 1.0（等边）
- 每种构型计算 E 变量 Gamma^V + Gamma^I + 自相关
- 同构型 double-check：Michelson Gamma^V 也应接近零

**验收标准**:
- P2 初步：至少一种非共面构型的 Gamma^V > 1e-3 (f > 10 mHz)
- P7 初步：所有非共面构型 Michelson Gamma^V < 1e-8
- 至少扫描 theta_inc=30, 60, 90 三种非零倾角

---

### M4: 全参数扫描 P2+P3（加入 side_ratio）+ 深度非共面构型
**优先级**: P1（推荐完整，质量降级可交付）
**依赖**: M3（趋势确认）

**输入**:
- M3 的结果确认趋势后启动

**输出**:
- 42-168 种构型的完整 Gamma^V(f) 数值表
- 找到 |Gamma^V|_sky_max 最大的构型

**关键技术**:
- P2 扩展：P1 + side_ratio = [1.0, 1.2] → 42 种
- P3 完整：theta_inc(7) x delta_h/L(6) x side_ratio(4) → 168 种
- 记录每种构型的 coplanarity 度量和对应 |Gamma^V|
- 使用 1 mHz — 10 Hz 公共频段优先（如时间允许扩展到 100 Hz）

**验收标准**:
- P2 最终：确认非共面 Gamma^V > 1e-3 的频率区间
- P3：找到 |Gamma^V|_sky_max > 0.01 的构型
- P4：至少拥有足够的非共面度量数据点用于拟合

---

### M5: 几何-响应关系拟合 + 网格收敛验证
**优先级**: P0（分析型任务，必须在数值扫描后执行）
**依赖**: M3, M4

**输入**:
- M3+M4 产出的全部数值结果

**输出**:
- |Gamma^V| 与 coplanarity / theta_inc 的定量拟合（线性或二次）
- R^2 > 0.5 验证（P4 硬约束）
- ntheta=32→64, nphi=64→128 收敛验证（P6 硬约束）

**关键技术**:
- 拟合模型：|Gamma^V| = a * coplanarity + b * coplanarity^2
- 或在 theta_inc 上做二次拟合 |Gamma^V| = c * theta_inc + d * theta_inc^2
- 网格收敛：在 3 种典型构型（最大 Gamma^V、中等、接近零）上验证
- 收敛判定：ntheta=32→64 时 |Gamma^V| 变化 < 10%

**验收标准**:
- P4：拟合 R^2 > 0.5
- P6：网格收敛变化 < 10%
- 输出拟合参数 a, b, R^2 写入 memory 文件

---

### M6: 与多星座比较 + 结果总结 + 论文更新
**优先级**: P1（迭代收尾）
**依赖**: M2, M3, M4, M5

**输入**:
- M2: 共面零检验 + 单臂链路对基准
- M3+M4: 非共面参数扫描全结果
- M5: 几何-响应关系 + 收敛验证

**输出**:
- 可视化产出：
  - `figures/8-coplanar-zero-validation.png` — 共面 E 变量 Gamma^V < 1e-10
  - `figures/8-single-arm-k3-validation.png` — 单臂链路对对标 K3
  - `figures/8-gammaV_vs_coplanarity.png` — |Gamma^V| vs 非共面度量
  - `figures/8-gammaV_vs_inclination.png` — |Gamma^V| vs 倾斜角
  - `figures/8-frequency_comparison.png` — 所有构型频率依赖曲线对比
  - `figures/8-comparison_multiconstellation.png` — 单三角非共面 vs LISAxTaiji
- `ORF_data_8.csv` — 全部构型+频率的数值表
- `memory/17-noncoplanar-olc-chiral-orf-iteration8.md` — memory 文件
- 论文第 7 章更新草案：非共面构型章节

**验收标准**:
- 逐条对照 P1-P8 判定标准，明确通过/未通过
- 如未通过则说明原因和降级分析
- 回答Iteration 8 的原始物理问题：单三角非共面能否实现可探测 Gamma^V

---

## 并行执行方案

```
阶段一（独立任务）:
  M1 (Fork + 框架)  ──> M2 (回归验证) ────────────────┐
  纯编码，无并行                                      │
                                                       │
阶段二（依赖 M1）:                                     │
  M2 (共面零检验 + 链路对基准) ──┐                      │
  P0，阻塞性验证                  │  M2 完成后立即启动   │
                                │                      │
阶段三（依赖 M2）:              │                      │
  M3 (P0+P1 参数扫描) ──────────┤  M3 是核心计算       │
  P0，最长任务                   │  M4 可延后但推荐      │
                                │                      │
阶段三.b（可选，依赖 M3）:       │                      │
  M4 (P2+P3 全参数扫描) ─────────┤  与 M3 串行，M3      │
  P1，质量降级可跳过              │    趋势确认后启动      │
                                │                      │
阶段四（依赖 M3+M4）:            │                      │
  M5 (拟合 + 收敛) ──────────────┤                      │
  P0，分析型任务                  │                      │
                                │                      │
阶段五（收尾，依赖 M2+M3+M4+M5）:│                      │
  M6 (可视化 + 总结 + 更新) ─────┘                      │
  P1，收尾                                               │
```

### DAG 依赖图

```
    M1 (Fork)
     |
     v
    M2 (Zero-test + K3 benchmark)
     |
     v
    M3 (P0+P1 scan: theta_inc x delta_h)
     |
     v (optional, depends on M3 results)
    M4 (P2+P3 scan: + side_ratio)
     |
     v
    M5 (Fit + convergence)
     |
     v
    M6 (Summary + plots + paper update)
```

### 并行机会

| 并行组 | 任务 | 说明 |
|--------|------|------|
| P1 | M1 | 无并行（阻塞所有后续） |
| P2 | M2 | M2 内部可并行：共面零检验 + 单臂链路对可同时进行 |
| P3 | M3 | 参数扫描内部天然可并行（各构型独立），但实现中作为单脚本批量处理 |
| P4 | M4 | 可选，与 M3 串行 |
| P5 | M5, M6 | 串行（M5 是 M6 的输入） |

### 最优并行策略

1. M1 完成后立即启动 M2
2. M2 内部：共面零检验和单臂链路对并行执行
3. M2 通过后立即启动 M3
4. M3 趋势确认后再决定 M4（P1 可选）
5. M3+M4 完成后启动 M5
6. M5 完成后启动 M6 收尾

---

## 计算资源估算

| 任务 | 计算量 | 预估时间 |
|------|--------|---------|
| M1 (Fork) | 纯编码，复用 10+11 | 1.5 小时 |
| M2 (零检验+基准) | 3 种构型 x 20 频率 x 32x64 网格 | 15 分钟 |
| M3 (P0+P1 扫描) | 12-21 构型 x 20 频率 | 30-60 分钟 |
| M4 (P2+P3 扫描) | 42-168 构型 x 20 频率 | 2-8 小时 |
| M5 (拟合+收敛) | 3 网格 x 3 构型 + 回归拟合 | 20 分钟 |
| M6 (总结+可视化) | 6 图 + CSV + memory + 论文 | 2 小时 |
| **总计（串行，无 M4）** | | ~4.5 小时 |
| **总计（串行，含 M4）** | | ~8 小时 |

---

## 验收判定矩阵

| # | 判定标准 | 对应任务 | 通过条件 |
|---|---------|---------|---------|
| P1 | 共面 E 变量零检验 | M2 | Gamma^V < 1e-10 (硬约束) |
| P2 | 非共面 E 变量非零检验 | M3, M4 | Gamma^V > 1e-3 at f>10mHz (硬约束) |
| P3 | 可探测极值 | M4 | |Gamma^V|_sky_max > 0.01 (硬约束) |
| P4 | 几何-响应关系 | M5 | 拟合 R^2 > 0.5 (硬约束) |
| P5 | 高频极限 | M2 | 单臂链路对 |Gamma^V| > 1.0 at f>>c/L (硬约束) |
| P6 | 网格收敛 | M5 | ntheta=32->64 变化 < 10% (硬约束) |
| P7 | Michelson 零检验 | M2, M3 | 任意非共面 Michelson Gamma^V < 1e-8 (硬约束) |
| P8 | 频率扫描覆盖 | M2, M3, M4 | 1 mHz-100 Hz, log-spaced, >= 20 点 (硬约束) |

---

## 风险分级与缓解

| 风险 | 级别 | 缓解措施 | 触发条件 |
|------|------|---------|---------|
| R1: 非共面单三角 Gamma^V 最大 < 1e-3 | **HIGH** | 降级为单臂链路对分析（M2 已覆盖），报告上限而非零结果 | 全参数扫描后最大 |Gamma^V| < 1e-3 |
| R2: E 变量三臂求和恢复对称性导致 Gamma^V = 0 | **HIGH** | 检查各臂贡献相对符号，尝试不对称权重组合 E' = aX+bY+cZ | M3 中所有倾角 Gamma^V < 1e-8 |
| R3: 参数空间 168 构型计算量过大 | **MEDIUM** | 优先 P0+P1（12-21 构型），M4 标记为可跳过 | M3 耗时 < 1h 则启动 M4 |
| R4: theta_inc=0 和 180 镜面对称冗余 | **LOW** | 扫描前验证对称性，限制 theta_inc 到 [0, 90] | 无 |
| R5: 非共面构型"参考方向"定义歧义 | **LOW** | 明确定义：参考平面 = xy 平面，倾斜绕 X 轴 | M1 实现时固化 |

---

## 与 Iteration 6/7 的衔接

| Iteration | 结果 | Iteration 8 使用 |
|-----------|------|-----------------|
| Iter 6 | Michelson Gamma^V = 0 严格证明 + 单臂链路对 | M1 fork + M2 验证 |
| Iter 7 | E 变量 CW sum + norm_V = 1.0 | M1 fork + 归一化约定复用 |
| Iter 7 | LISA x Taiji |Gamma^V|_max = 1.0 | M6 比较基准 |

---

## 副脑质疑的验证路径

来自 01/02 文件的副脑质疑将在迭代中逐一验证：

| 质疑号 | 内容 | 验证任务 |
|--------|------|---------|
| #1 | 单三角非共面与多星座物理起源是否相同？ | M6（比较图确认二者都通过破缺镜面反射对称性获得 R^V） |
| #2 | 三臂 CW sum 贡献抵消怎么办？ | M3（验证 E 变量非零；如为零则转 M2 单臂链路对） |
| #3 | 深度非共面是否"物理可执行"？ | M3-M4（报告人工构造的数值结果，明确标注非轨道真实构型） |

---

## 产出文件清单

| 文件 | 类型 | 状态 |
|------|------|------|
| `scripts/12-noncoplanar-triangular-chiral-orf.py` | 主计算脚本 | 待创建 |
| `figures/8-coplanar-zero-validation.png` | 共面零检验图 | 待生成 |
| `figures/8-single-arm-k3-validation.png` | 单臂链路对标 | 待生成 |
| `figures/8-gammaV_vs_coplanarity.png` | 非共面度量曲线 | 待生成 |
| `figures/8-gammaV_vs_inclination.png` | 倾斜角曲线 | 待生成 |
| `figures/8-frequency_comparison.png` | 频率依赖对比 | 待生成 |
| `figures/8-comparison_multiconstellation.png` | 单三角 vs 多星座 | 待生成 |
| `ORF_data_8.csv` | 数值表 | 待生成 |
| `memory/17-noncoplanar-olc-chiral-orf-iteration8.md` | 记忆文件 | 待创建 |
| `loop/2-loop/` 执行目录 | 执行产出 | 待创建 |

---

## 任务依赖关系总览

```
M1 (Fork)              P0, 阻塞所有
│
├─ M2 (Zero-test)      P0, 依赖 M1 — 共面零检验 + 单臂链路对基准
│   ├─ P1 验证         共面 E 变量 Gamma^V < 1e-10
│   ├─ P5 验证         单臂链路对高频 |Gamma^V| > 1.0
│   └─ P7 初步验证     Michelson Gamma^V < 1e-8
│
├─ M3 (Core Scan)      P0, 依赖 M2 — P0+P1 非共面参数扫描
│   ├─ P2 初步验证     至少一种构型 Gamma^V > 1e-3
│   └─ P7 初步验证     所有构型 Michelson Gamma^V < 1e-8
│
├─ M4 (Full Scan)      P1, 依赖 M3 — P2+P3 全参数扫描（可跳过）
│   └─ P3 验证         |Gamma^V|_sky_max > 0.01
│
├─ M5 (Analysis)       P0, 依赖 M3+M4 — 拟合 + 收敛
│   └─ P4 验证         拟合 R^2 > 0.5
│   └─ P6 验证         网格收敛 < 10%
│
└─ M6 (Summary)        P1, 依赖 M2+M3+M4+M5 — 可视化 + 总结
    └─ M6 验证         P8 频率覆盖 + 逐条对照 P1-P8
                       + 比较图 + memory + 论文更新

DAG 拓扑排序: M1 -> M2 -> M3 -> [M4] -> M5 -> M6
并行策略: M2 内部可并行（零检验+链路对），M3 内部参数扫描可并行
```

---

last_completed_at: pending

---

*此任务分解基于 Iteration 6/7 的代码基础（scripts 10+11）、已确立的物理结论（单平面 R^V=0，单臂非共面 |Gamma^V|>0.041 at 30mHz），以及 Iteration 7 的多星座基线数据（|Gamma^V|_max = 1.0）。核心假设是：单三角形非共面构型通过破坏镜面反射对称性可获得非零 Gamma^V，其幅度与 coplanarity 度量正相关。*
