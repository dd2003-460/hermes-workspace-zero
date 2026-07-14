# 03-任务分解（Iteration 6）— 三角 3 卫星 OLC 手征 ORF

**输入**：`02-目标澄清-Iteration6.md`
**输出**：本文件（子任务 DAG）
**前置**：Iteration 5 手征 ORF completed ✅

---

## 子任务 DAG

```
M1: fork + 读取基础代码
  ↓
M2: 构建三角卫星几何 + Michelson-like 变量天线方向图
  ↓
M3: 实现 chiral ORF 计算引擎（3 对 Michelson 变量交叉相关）
  ↓
M4: 跑等边三角形基准案例 + 共面零验证
  ↓
M5: 非对称构型扫描 + 频率依赖曲线
  ↓
M6: 收敛性验证 + LISA 对比 + 论文段落更新
```

---

## Subtask M1: Fork 基础代码 + 环境检查

- **输入**：`scripts/09-olc-chiral-orf.py`（已有单臂 chiral ORF 计算代码）
- **输出**：`scripts/10-olc-chiral-orf-triangular.py`（fork 副本）
- **验证**：`diff 09-olc-chiral-orf.py 10-olc-chiral-orf-triangular.py` 仅显示文件名差异
- **回滚**：删除 fork 文件，从 git 或原始文件重新 fork
- **置信度**：1.0
- **依赖**：null
- **关键操作**：
  1. `cp 09-olc-chiral-orf.py 10-olc-chiral-orf-triangular.py`
  2. 清理文件头注释（改为 Iteration 6）
  3. 保留所有函数签名不变（传递函数、天线方向图、手征因子）

---

## Subtask M2: 三角卫星几何 + Michelson-like 变量天线方向图

- **输入**：M1 fork 代码
- **输出**：
  1. 卫星位置函数 `satellite_positions(triangular_config)`
  2. 单向链路方向图函数 `olc_antenna_patterns(link_direction, GW_direction, polarization)`
  3. Michelson-like 变量等效天线方向图 `F_plus_M(VarX)`, `F_cross_M(VarX)`
- **验证**：
  - 等边三角形：三个卫星两两等距 d = 2.5 Gm
  - 链路方向图在 d→0 极限下与单臂 OLC 一致
  - Michelson-like 变量的天线方向图是两个路径的叠加（类似 LISA 的 X 变量）
- **回滚**：重置代码到 M1 状态
- **置信度**：0.6
- **依赖**：M1
- **理论参考**：
  - LISA Michelson: X = L12(t+L12) - L21(t+L21) （Odell & Sairt）
  - 3 个 Michelson-like 变量：X, Y, Z（对应三对卫星）
  - 每个 Michelson 变量的等效天线方向图是两条路径的相干叠加
- **风险**：OLC Michelson 的传递函数是两个路径传递函数的叠加，不是简单相加。需要正确实现：`T_M = T_path1 * exp_phase1 - T_path2 * exp_phase2`

---

## Subtask M3: 实现 Chiral ORF 计算引擎

- **输入**：M2（三角几何 + Michelson 天线方向图）
- **输出**：`gamma_chiral(f, config)` 函数，返回 Gamma^V
- **验证**：
  - 同一 Michelson 变量的自关联：Gamma^V(M_i, M_i) = 0（手征反对称性）
  - 与 LISA 三角已知结果交叉验证（d = 2.5 Gm 时 |Gamma^V| ~ 0.3）
- **回滚**：重置到 M2
- **置信度**：0.7
- **依赖**：M2
- **核心公式**：
  ```
  Gamma^V(f) = int d^2nhat/(4pi) * [F_+^M1 * F_x^M2 - F_x^M1 * F_+^M2]
               * T_M1 * T_M2^* * exp(-i*alpha*nhat.s)
  ```
  对 3 对 Michelson 变量 (X,Y), (Y,Z), (Z,X) 分别计算后合成星座 ORF
- **星座合成**：对 3 对变量取平均（或最优组合，需确认方法）

---

## Subtask M4: 等边三角形基准案例 + 共面零验证

- **输入**：M3 实现
- **输出**：
  1. 等边三角形的 |Gamma^V| 数值
  2. 共面构型零验证（对称共面时 |Gamma^V| < 1e-10）
- **验证**：
  - 判定标准 #1：共面零验证通过
  - 判定标准 #3：量级在 0.001-1.0 范围内
- **回滚**：无（M3 失败则重做 M3）
- **置信度**：0.8
- **依赖**：M3
- **测试构型**：
  - 等边三角形（d = 2.5 Gm），三种空间取向
  - 退化构型（三个卫星共线），|Gamma^V| 应接近零
  - d→0 极限下应与双臂 OLC 参考点一致

---

## Subtask M5: 非对称构型扫描 + 频率依赖曲线

- **输入**：M4 基准案例
- **输出**：
  1. 至少 5 种构型的 |Gamma^V| 表（等边、等腰、直角、退化、非对称）
  2. |Gamma^V(f)| 频率依赖曲线（1 mHz - 100 Hz）
  3. 与 LISA 三角构型对比图
- **验证**：
  - 判定标准 #2：至少一种非对称构型 |Gamma^V| > 1e-3
  - 判定标准 #4：自关联为零
- **回滚**：无
- **置信度**：0.7
- **依赖**：M4
- **扫描参数**：
  - 构型参数：卫星间距比 a:d（改变一边长度）
  - 频率点：1 mHz, 3 mHz, 10 mHz, 30 mHz, 100 mHz, 300 mHz, 1 Hz, 3 Hz, 10 Hz, 30 Hz, 100 Hz
- **LISA 对比**：使用相同卫星间距（d = 2.5 Gm），对比 OLC Michelson 与 LISA 激光干涉的 |Gamma^V|

---

## Subtask M6: 收敛性验证 + LISA 对比 + 论文更新

- **输入**：M5 结果
- **输出**：
  1. 网格收敛性报告（ntheta=32→64，变化 < 10%）
  2. 论文草稿段落更新（替换推测性陈述为实际数据）
  3. memory 文件写入（Iteration 6 结论）
- **验证**：
  - 判定标准 #5：网格收敛
  - 判定标准 #6：参考点对比
- **回滚**：无
- **置信度**：0.8
- **依赖**：M5
- **产出文件**：
  - `memory/10-olc-triangular-chiral-orf-iteration6.md`
  - 更新 `chiral-olc-paper-draft.md` 相关段落
  - 更新 `loop/1-loop/06-决策-Iteration6.md`（进入 2-loop）

---

## 依赖图

```
M1 (fork)
  │
  ├─→ M2 (geometry + Michelson patterns)
  │     │
  │     └─→ M3 (chiral ORF engine)
  │           │
  │           ├─→ M4 (equilateral + coplanar zero)
  │           │     │
  │           │     └─→ M5 (asymmetric scan + frequency curves)
  │           │           │
  │           │           └─→ M6 (convergence + paper update)
  │           └─→ M5
  └─→ M5 (can parallelize after M3)
```

**关键路径**：M1 → M2 → M3 → M4 → M5 → M6
**并行机会**：M4 和 M5 可以在 M3 完成后并行（但 M5 依赖 M4 基准验证）

---

## 风险与缓解

| 风险 | 严重性 | 缓解 |
|------|--------|------|
| Michelson-like 变量天线方向图的 OLC 实现不确定 | **HIGH** | 参考 LISA 的 Michelson 构造方法，从频率偏移第一性原理推导；如果 d→0 极限不收敛到已知双臂结果则回滚 |
| 单三角星座 |Gamma^V| 仍接近零 | **HIGH** — 这是可能失败的场景。如果 |Gamma^V|_max < 1e-3，则在后续迭代中探索双星座（OLC+OLC）方案 |
| 星座合成方法不明确 | 中 | 3 对 Michelson 变量的合成需要确认：平均？最优加权？参考 LISA 的 TDI 组合方式 |
| 数值计算量大 | 低 | 控制网格密度，Python + numpy 矩阵运算应在可接受时间内 |

---

## 完成标准

所有 6 个判定标准通过（见 02-目标澄清-Iteration6.md）：
1. ✅ 共面零验证 |Gamma^V| < 1e-10
2. ✅ 非零检验 |Gamma^V| > 1e-3
3. ✅ 量级检查 0.001 <= |Gamma^V|_max <= 1.0
4. ✅ 自关联零
5. ✅ 网格收敛 < 10%
6. ✅ 参考点对比

**完成信号**：迭代产出可验证的结果文件（数值表 + 曲线 + 论文更新）

---

## 副脑质疑（由主脑在 1-loop/06 后派发）

**质疑#1（CRITICAL）**：OLC 的频率偏移观测量是标量，没有 LISA 那样的干涉仪相位差结构。Michelson-like 变量的构造是否真的能产生手征灵敏度？还是我们错误地将 LISA 的干涉仪物理套用到了 OLC 上？

**质疑#2（HIGH）**：3 个 Michelson-like 变量的星座合成方法没有理论依据。LISA 使用 TDI (Time-Delay Interferometry) 构造无时钟噪声组合，OLC 是否有对应的 TDI？如果没有，直接平均 3 个 Michelson 变量的 ORF 是否合理？

**质疑#3（MEDIUM）**：等边三角形的对称性可能天然抑制手征 ORF。是否需要刻意选择非对称构型？如果等边三角形的 |Gamma^V| < 非对称构型，论文中关于"等边三角形可达 |Gamma^V| ~ 0.3"的声称是否成立？

**质疑#4（MEDIUM）**：论文声称 |Gamma^V| ~ 0.3 是基于 PTA 或 LISA-Taiji 双网络的外推，而非实际计算。单三角 OLC 星座与 LISA 单三角在手征灵敏度上有哪些本质差异？

---

last_updated: 2026-07-05
