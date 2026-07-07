# 03-任务分解（Iteration 7）— 多星座手征 ORF 计算

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md`
> 迭代编号：7
> 输入：`loop/1-loop/01-任务澄清-Iteration7.md` + `loop/1-loop/02-目标澄清-Iteration7.md`
> 输出：本文件 + DAG 拓扑排序 + 并行方案

---

## 核心科学问题

Iteration 6 严格证明了：三角 OLC Michelson-like 变量的手征 ORF 恒为零（对称性恒等式）。本迭代的目标是**通过多星座混合网络突破这一限制**，验证不同星座之间的交叉相关能否产生非零 Gamma^V。

**关键物理洞察**：同一星座内 Michelson 变量 M = link_a + link_b 的 R_a = R_b 对称性源于 F_A(u) = F_A(-u) 偶函数性质。不同星座之间的交叉相关涉及两个不同探测器的响应，不存在 R_a = R_b 的对称性约束。

---

## 子任务分解

### M1: 代码 Fork + 多星座基础框架
**优先级**: P0（阻塞所有后续任务）
**依赖**: 无（直接承接 Iteration 6 代码）

**输入**:
- `scripts/10-olc-chiral-orf-triangular.py` — fork 源文件
- `scripts/09-olc-chiral-orf.py` — 双探测器求解器，用作 double-check
- `scripts/06a-patched-mixed-network.py` — detector 参数参考

**输出**:
- `scripts/11-multi-constellation-chiral-orf.py` — 主计算脚本
  - 从 `10-olc-chiral-orf-triangular.py` fork
  - 新增 `Constellation` 类，封装星座的臂长、卫星位置、link 方向
  - 新增 `compute_cross_orf()` 函数，支持两不同星座的交叉相关
  - 保留原有的 `compute_triangular_orf_standard/chiral()` 作为单星座计算引擎
  - 复用 `olc_transfer_function()`、`olc_link_response_grid()`、`michelson_effective_response()` 等基础设施

**关键技术决策**:
- 使用参数化星座几何（臂长 L、轨道倾角 i、相对相位 phi_rel）
- 不同星座间通过旋转矩阵参数化相对取向
- 交叉相关计算中，每个星座贡献自己的 Michelson 有效响应，但积分时考虑星座间相对位置导致的相位延迟（传递函数中的相对相位因子 e^{-i alpha n_s}）

**验收标准**:
- Fork 脚本可以独立执行，不修改源文件
- 单星座回归测试通过（OLC x OLC = 零结果）
- Taiji x LISA（相同参数 L=2.5 Gm）在低频率下与 Orlando 2021 结果对标

---

### M2: Taiji x LISA 基准验证（对标 Orlando 2021）
**优先级**: P0（必须最先验证的基准）
**依赖**: M1

**输入**:
- M1 产出的 `scripts/11-multi-constellation-chiral-orf.py`（含 cross ORF 函数）
- Orlando et al. 2021 JCAP 数值结果（60 deg 倾角下 |Gamma^V| ~ 0.3）

**输出**:
- Taiji x LISA 的 |Gamma^V(f)| 在 0.1 mHz - 1 Hz 范围内的数值表
- 验证报告：与 Orlando 2021 偏差 < 50%（容差基于近似方法差异）

**关键技术**:
- Taiji triangle: 臂长 2.5 Gm，在黄道面内
- LISA triangle: 臂长 2.5 Gm，倾角 60 度（相对于黄道面）
- 两星座中心在同一日心轨道上，角距离设为 0（最小复杂度）
- 扫描相对倾角 delta_i = 0°, 30°, 60°

**验收标准**:
- 60 度倾角下 |Gamma^V|_max 在 0.05 - 0.5 范围内
- 0 度倾角（共面）下 |Gamma^V| < 1e-3（共面导致对称性恢复）
- 与 Orlando 2021 结果偏差 < 50%

---

### M3: OLC x Taiji 混合网络 chiral ORF（P0 核心任务）
**优先级**: P0（核心科学目标）
**依赖**: M1

**输入**:
- M1 产出的多星座脚本
- M2 验证通过的代码框架

**输出**:
- OLC triangle x Taiji triangle 的 |Gamma^V(f)| 在 0.1 mHz - 10 Hz 范围内的数值表
- 不同相对倾角下的 Gamma^V 比较

**关键技术**:
- OLC: 臂长 L_OLC = 0.17 Gm（紧凑构型）或 3 Gm（扩展构型），两组参数均需扫描
- Taiji: 臂长 L_Taiji = 2.5 Gm
- 两星座在同一轨道平面（delta_i = 0 基准），后续扫描 30°、60°
- 传递函数频率范围覆盖 mHz 到 Hz
- **相同可测量类型**（频率偏移 x 频率偏移），无需量纲转换

**验收标准**:
- |Gamma^V| 至少在某些频率 > 1e-3（通过检验）
- 或 |Gamma^V| < 1e-3（失败信号，需要探索其他方案）
- 标准 ORF Gamma^I 量级在 0.01 - 1.0（确认代码正确）

---

### M4: OLC x LISA 混合网络（不同可测量处理）
**优先级**: P1（扩展任务，质量降级可交付）
**依赖**: M1

**输入**:
- M1 产出的多星座脚本

**输出**:
- OLC triangle x LISA triangle 的 |Gamma^V(f)| 数值表
- 频率偏移 -> 等效应变转换的归一化处理

**关键技术**:
- **不同可测量**：OLC 测量频率偏移 S_y(f)，LISA 测量应变差 S_h(f)
- OLC 等效应变灵敏度：S_h_OLC(f) = 2*pi*f * S_y_OLC(f)
- 交叉相关归一化因子需统一量纲
- 此任务存在理论不确定性，如转换存在困难可延后

**可妥协**:
- 如果不同可测量转换存在不确定性，可先只输出 OLC x Taiji 和 Taiji x LISA，OLC x LISA 延后处理

---

### M5: 频率扫描 + 参数化研究
**优先级**: P0（必须完成）
**依赖**: M2, M3

**输入**:
- M2 和 M3 的计算结果

**输出**:
- |Gamma^V(f)| 频率依赖曲线（0.1 mHz - 10 Hz，semilog plot）
- 相对倾角扫描图（delta_i = 0°, 30°, 60° 对比）
- 星座间角距离扫描（delta_alpha = 0°, 60°, 120°）

**关键技术**:
- 控制网格密度：ntheta=32, nphi=64 起步，验证收敛性后提升至 64/128
- 频率对数采样：11-21 个点覆盖 0.1 mHz - 10 Hz
- 每次计算耗时估算：~10-30 秒/频率点（向量化 numpy）

**验收标准**:
- 频率曲线连续、无数值振荡异常
- 收敛性验证：ntheta=32->64 时 |Gamma^V| 变化 < 10%

---

### M6: 结果总结 + 论文更新
**优先级**: P1（迭代收尾）
**依赖**: M2, M3, M5

**输入**:
- M2: Taiji x LISA 基准验证结果
- M3: OLC x Taiji 核心结果
- M5: 频率扫描 + 参数化研究

**输出**:
- Iteration 7 结果汇总表（|Gamma^V| 数值、频率行为、与文献对标）
- 更新论文草稿：§3.5（手征 ORF 理论 + 多星座结果）和 §7.2.2（未来方向）
- 更新 memory 文件：`memory/12-iteration7-multi-constellation-chiral-orf.md`

**验收标准**:
- 数值结果与 02-目标澄清.md 中判定标准逐条对照
- 通过判定标准 1-5（硬约束）或明确说明未通过原因

---

## 并行执行方案

```
阶段一（独立任务，可并行）:
  M1 (Fork) ──┬──> M2 (Taiji×LISA 基准) ──┐
              │                              │
              └──> M4 (OLC×LISA 扩展) ───────┤  可并行开始
                                              │
阶段二（依赖 M1）:                              │
  M3 (OLC×Taiji) ─────────────────────────────┤  M2+M3 可并行
                                              │
阶段三（依赖 M2+M3+M5）:                        │
  M5 (频率扫描+参数化) ─────────────────────────┤
                                              │
阶段四（收尾）:                                 │
  M6 (总结+论文更新) ───────────────────────────┘
```

### DAG 依赖图

```
    M1 (Fork)
    /   \   \
   v     v   v
  M2    M3   M4
   \    /
    \  /
     v
     M5
     |
     v
     M6
```

### 并行机会

| 并行组 | 任务 | 说明 |
|--------|------|------|
| P1 | M1 | 无并行（阻塞所有后续） |
| P2 | M2, M3, M4 | **M2 和 M3 可并行** — 各自调用 M1 的 cross ORF 函数 |
| P3 | M5 | 依赖 M2, M3 的结果，必须串行 |
| P4 | M6 | 依赖 M2, M3, M5，必须串行 |

### 最优并行策略

1. **M1 完成后**，同时启动 M2 和 M3（两个独立的计算任务）
2. M4 可与 M2/M3 并行，但因优先级 P1 可延后
3. M5 等待 M2 和 M3 完成后启动（需要两个基准结果来指导扫描参数）
4. M6 收尾

---

## 计算资源估算

| 任务 | 计算量 | 预估时间 |
|------|--------|---------|
| M1 (Fork) | 纯编码 | 0.5 小时 |
| M2 (基准验证) | 3 倾角 x 21 频率 = 63 次积分 | 30 分钟 |
| M3 (核心计算) | 2 OLC 臂长 x 3 倾角 x 21 频率 = 126 次积分 | 1-2 小时 |
| M4 (扩展) | 2 OLC 臂长 x 3 倾角 x 21 频率 = 126 次积分 | 1-2 小时 |
| M5 (扫描) | 包含在上述计算中 | 已计入 |
| M6 (总结) | 图表生成 + 文档更新 | 1 小时 |
| **总计（串行）** | | **~5 小时** |
| **总计（M2+M3 并行）** | | **~3 小时** |

---

## 验收判定矩阵

| # | 判定标准 | 对应任务 | 通过条件 |
|---|---------|---------|---------|
| 1 | 混合星座非零检验 | M3 | OLC x Taiji 的 |Gamma^V| > 1e-3（至少在某些频率） |
| 2 | 自关联零检验 | M1 | OLC x OLC 的 |Gamma^V| < 1e-10（回归测试） |
| 3 | Taiji x LISA 基准 | M2 | Taiji x LISA 的 |Gamma^V|_max 在 0.05 - 0.5 范围内 |
| 4 | 标准 ORF 自洽 | M2, M3 | 所有组合的 Gamma^I 量级在 0.01 - 1.0 |
| 5 | 网格收敛 | M5 | ntheta=32->64 时 |Gamma^V| 变化 < 10% |
| 6 | 频率平坦性 | M5 | |Gamma^V(f)| 在公共频段内变化 < 1 个量级 |
| 7 | 几何参数扫描 | M5 | 至少扫描 3 组相对倾角（0°, 30°, 60°） |
| 8 | 可视化完整性 | M6 | 频率依赖曲线 + 星座对比图 + 参数扫描图 |

---

## 风险分级与缓解

| 风险 | 级别 | 缓解措施 | 触发条件 |
|------|------|---------|---------|
| OLC x Taiji 的 |Gamma^V| 仍接近零 (< 1e-3) | **HIGH** | 切换至 4+ 卫星构型或非 Michelson 观测组合（如 M_X_{1:-1} 权重） |
| Taiji x LISA 基准验证失败 | **HIGH** | 检查 Michelson 变量定义、传递函数形式、倾角参数化 | |Gamma^V|_max 与 Orlando 2021 偏差 > 50% |
| OLC x LISA 不同可测量归一化不明确 | **MEDIUM** | 延后 M4，优先 OLC x Taiji | 量纲转换存在理论争议 |
| 数值计算量大 | **MEDIUM** | M2+M3 并行，网格从 ntheta=32 起步 | 单次计算 > 60 秒 |
| OLC 传递函数在高频数值振荡 | **MEDIUM** | 检查 sinc 函数的 epsilon 截断 | 高频段出现非物理振荡 |

---

## 迭代 7 时间线（最优并行策略）

| 时间 | 阶段 | 任务 | 状态 |
|------|------|------|------|
| H+0.5 | M1 | Fork 代码，验证单星座回归 | 完成 |
| H+1.0 | M2 | Taiji x LISA 基准（第一批倾角） | in-progress |
| H+1.0 | M3 | OLC x Taiji 核心计算（第一批参数） | in-progress |
| H+1.5 | M2 | Taiji x LISA 基准（扫描完成） | 完成 |
| H+3.0 | M3 | OLC x Taiji 核心计算（扫描完成） | 完成 |
| H+3.5 | M5 | 频率扫描 + 参数化研究 + 收敛验证 | 完成 |
| H+4.0 | M4 | OLC x LISA 扩展（如时间允许） | 可跳过 |
| H+4.5 | M6 | 结果总结 + 论文更新 + memory 更新 | 完成 |

**总时间**: 约 4.5 小时（并行策略）或 5 小时（串行策略）

---

## 与 Orlando 2021 的衔接

**Orlando et al. 2021 JCAP 的关键参数**（来自论文和 iter 6 memory）:
- LISA: L = 2.5 Gm, 倾角 i_LISA = 60 deg
- Taiji: L = 2.5 Gm, 倾角 i_Taiji = 0 deg（黄道面内）
- 轨道倾角差: 60 deg
- |Gamma^V|_max ~ 0.3（在低频极限 f -> 0）
- 共面构型 (0 deg) 时 |Gamma^V| -> 0

**本迭代对标**:
- 使用完全相同的 LISA 和 Taiji 参数
- 计算 |Gamma^V(f)| 在 f < 10 mHz 的极限值
- 偏差 < 50% 即可接受（近似方法差异 + 数值积分网格差异）

---

## 副脑质疑的验证路径

来自 01-任务澄清的副脑质疑将在迭代中逐一验证：

| 质疑号 | 内容 | 验证任务 |
|--------|------|---------|
| #1 | 双 Michelson 对称性能否被打破？ | M3（OLC x Taiji 非零检验）直接回答 |
| #2 | 0 度倾角时是否为零？ | M5（倾角扫描 0°, 30°, 60°）验证趋势 |
| #3 | 不同可测量交叉相关物理意义 | M4（如执行）处理量纲转换 |
| #4 | 非零 chiral ORF 是否可探测？ | 本迭代给出 |Gamma^V| 值，SNR 计算留给后续迭代 |

---

## 产出文件清单

| 文件 | 类型 | 状态 |
|------|------|------|
| `scripts/11-multi-constellation-chiral-orf.py` | 主计算脚本 | 待创建 |
| `figures/11-multi-const-benchmark.png` | Taiji x LISA 基准图 | 待生成 |
| `figures/11-multi-const-olc-taiji.png` | OLC x Taiji 核心结果 | 待生成 |
| `figures/11-multi-const-frequency.png` | 频率依赖曲线 | 待生成 |
| `figures/11-multi-const-angle-scan.png` | 倾角扫描图 | 待生成 |
| `figures/11-multi-const-comparison.png` | 单一星座 vs 混合网络对比 | 待生成 |
| `memory/12-iteration7-multi-constellation-chiral-orf.md` | 记忆文件 | 待创建 |
| `loop/2-loop/` 执行目录 | 执行产出 | 待创建 |

---

## 任务依赖关系总览

```
M1 (Fork)           P0, 阻塞所有
├─ M2 (Benchmark)   P0, 依赖 M1 — Taiji x LISA 对标 Orlando 2021
│   └─ M6 (Summary) P1, 依赖 M2 — 总结中必须包含基准验证结果
├─ M3 (Core)        P0, 依赖 M1 — OLC x Taiji 核心计算
│   └─ M6 (Summary) P1, 依赖 M3 — 总结中必须包含核心结果
├─ M4 (Extend)      P1, 依赖 M1 — OLC x LISA 扩展（可跳过）
│   └─ M6 (Summary) P1, 依赖 M4（如执行）
└─ M5 (Scan)        P0, 依赖 M2+M3 — 频率扫描 + 参数化研究
    └─ M6 (Summary) P1, 依赖 M5 — 总结中必须包含扫描结果

DAG 拓扑排序: M1 -> [M2, M3, M4] -> M5 -> M6
并行策略: M2 + M3 + M4 可同时启动
```

---

last_completed_at: pending

---

*此任务分解基于 Iteration 6 的代码基础（`10-olc-chiral-orf-triangular.py`）、Orlando 2021 文献基准、以及 Iteration 6 证明的对称性恒等式。核心假设是：不同星座间的交叉相关不再受同一星座内 F_A(u) = F_A(-u) 对称性的约束。*
