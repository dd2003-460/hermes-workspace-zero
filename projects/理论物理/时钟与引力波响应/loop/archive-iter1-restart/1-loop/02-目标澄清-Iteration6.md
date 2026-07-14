# 02-目标澄清（Iteration 6）— 三角 3 卫星 OLC 手征 ORF

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/1-loop/02-目标澄清.md`
**状态**：completed
**输入**：loop/1-loop/01-任务澄清-Iteration6.md
**输出**：本文件 + acceptance-criteria.md

---

## 阶段目标

为三角 3 卫星 OLC 星座（6 个单向链路，3 个 Michelson-like 变量）计算手征 ORF（chiral ORF, Gamma^V），验证论文草稿中"triangular OLC can achieve |Gamma^V| ~ 0.3"的声称是否成立。

**核心问题**：三角 OLC 与 LISA 三角构型在手征检测方面有何异同？OLC 的标量频率偏移观测量是否仍然能实现手征灵敏度？

---

## 期望结果

### 必须产出（Iteration 6 完成标志）

1. **手征 ORF 数值表**：对至少 5 种构型（等边三角形、等腰、直角、退化、非对称）给出 |Gamma^V| 值
2. **频率依赖曲线**：在 1 mHz — 100 Hz 范围内绘制 |Gamma^V(f)|
3. **与 LISA 对比**：在相同卫星构型下，对比 OLC 与 LISA 三角构型的 |Gamma^V|
4. **收敛性验证**：证明积分结果收敛（至少 2 档网格密度）

### 理论目标

1. **验证或修正论文声明**：确认三角形 OLC 的手征灵敏度是否可达 ~0.3
2. **确定 OLC 手征检测的最低要求**：什么样的三角构型才能实现有意义的 chiral 探测
3. **量化 OLC vs LISA**：在相同几何构型下，OLC 手征灵敏度相比 LISA 的比率

---

## 判定标准

### 必须满足（Pass/Fail）

| # | 判定标准 | 通过条件 |
|---|---------|---------|
| 1 | **共面零验证** | 对称共面三角构型 |Gamma^V| < 1e-10 |
| 2 | **非零检验** | 至少有一种非对称构型满足 |Gamma^V| > 1e-3 |
| 3 | **量级检查** | |Gamma^V|_max 在合理范围内：0.001 <= |Gamma^V|_max <= 1.0 |
| 4 | **自关联零** | 同一 Michelson 变量的手征 ORF = 0 |
| 5 | **网格收敛** | ntheta=32→64 时，|Gamma^V| 变化 < 10% |
| 6 | **参考点对比** | d→0 简化极限下，与双臂 OLC 结果一致 |

### 失败标准

- |Gamma^V|_max < 1e-3：三角 OLC 也不具备手征灵敏度（需要更大规模星座或改进组合方式）
- |Gamma^V| 发散或 > 1.0：数值错误或公式错误
- 共面构型 |Gamma^V| > 1e-6：代码存在系统性偏差

---

## 硬约束

1. **传递函数**：必须使用 OLC 特定传递函数（Lou 硕士论文公式 2-30）
2. **天线方向图**：必须与 Iteration 5 代码完全一致
3. **手征因子**：必须使用 F_+1*F_x2 - F_x1*F_+2
4. **代码 fork 原则**：fork `09-olc-chiral-orf.py` → `10-olc-chiral-orf-triangular.py`
5. **天空积分**：ntheta >= 32, nphi >= 64，权重 sin(theta)*(pi/ntheta)*(2*pi/nphi)
6. **归一化**：sqrt(auto1 * auto2)

---

## 完成时间
last_completed_at: 2026-07-05
