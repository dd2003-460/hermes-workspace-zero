# 04-信息搜集（Iteration 8）— 三角形 3 卫星 OLC 手征 ORF + 深度非共面构型

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/1-loop/`
**阶段**: 1-loop/04 — 信息搜集
**前置**: 01-任务澄清, 02-目标澄清, 03-任务分解
**输出**: 本文件 + enter_2loop 决策

---

## 1. 工具清单

以下表格列出 M1-M6 所有任务所需的工具/函数及其可用性状态。

| # | 工具/函数 | 来源脚本 | 用途 | 对应 M | 状态 |
|---|----------|---------|------|--------|------|
| T1 | `olc_transfer_function(f, L, cos_nu)` | scripts/10, line 33 | 单向链路传递函数 (Lou Eq. 2-30) | M1-M6 | ✅ 复用 |
| T2 | `triangle_sat_positions(equilateral, side_ratio)` | scripts/10, line 48 | 三角卫星位置生成，支持不等臂 | M1, M3 | ✅ 复用 |
| T3 | `link_direction(r_from, r_to)` | scripts/10, line 67 | 链路方向 (theta, phi, d_norm) | M1-M6 | ✅ 复用 |
| T4 | `olc_link_response_grid(f, L, sat_i, sat_j, ntheta, nphi)` | scripts/10, line 75 | 单臂链路响应 R_+, R_x, F_A(u) | M1-M4 | ✅ 复用 |
| T5 | `michelson_effective_response(tG, pG, link_a_*, link_b_*, L)` | scripts/10, line 152 | Michelson 有效响应 R_A^M = R_A(a) + R_A(b) | M2, M3 | ✅ 复用 |
| T6 | `compute_triangular_orf_chiral(f, m1_*, m2_*, L, ntheta, nphi)` | scripts/10, line 200 | Michelson 变量手征 ORF (Gamma^V = int[M1p*M2x - M1x*M2p]) | M2, M3 | ✅ 复用 |
| T7 | `test_coplanar_zero()` | scripts/10, line 500 | 共面等边三角形 Gamma^V < 1e-10 验证 | M2 | ✅ 复用 |
| T8 | `tri_orf_orient_avg(...)` | scripts/10, line 270 | 方位角平均 over phi_s | M2-M5 | ✅ 复用 |
| T9 | `antenna_pattern_e_variable_universal(tG, pG, sat_pos, L)` | scripts/11, line 260 | E 变量 CW sum: R_E+ = sum_CW F_+*T, R_Ex = sum_CW F_x*T | M1-M6 | ✅ 复用 |
| T10 | `compute_cross_e_variable_orf(f, const1, const2, ...)` | scripts/11, line 360 | 交叉相关 ORF: Gamma^I, Gamma^V (sky-averaged) | M2, M5 | ✅ 复用 |
| T11 | `compute_cross_e_variable_orf_sky_max(f, const1, const2, ...)` | scripts/11, line 420 | Sky-maximized norm_V = max|chiral_integrand|/sqrt(auto1*auto2) | M2, M5 | ✅ 复用 |
| T12 | `Constellation` class with `_apply_inclination()` | scripts/11, line 70 | 星座类，含 X 轴旋转实现倾斜 | M1, M3 | ✅ 复用 |
| T13 | `create_lisa()`, `create_taiji()`, `create_olc()` | scripts/11, line 53 | 工厂函数 | M2, M5 | ✅ 复用 |
| T14 | 天空网格 (ntheta=32/64, nphi=64/128) | scripts/10+11 | dOmega = sin(theta)*(pi/ntheta)*(2*pi/nphi) | M1-M6 | ✅ 复用 |
| T15 | 频率扫描基础设施 | scripts/10+11 | log-spaced f from 1mHz to 100Hz | M1-M6 | ✅ 复用 |
| T16 | `chiral_antenna(arm1, arm2)` | scripts/test_crosscorr_symmetry, line 52 | 手征天线模式 (GR, GL) | M2 | ✅ 复用 |
| T17 | `sky_avg_response(detector1_arms, detector2_arms)` | scripts/test_crosscorr_symmetry, line 65 | 交叉相关 R^I, R^V 快速验证 | M2 | ✅ 复用 |
| T18 | `sky_avg_response_with_phase(...)` | scripts/test_crosscorr_symmetry, line 149 | 含空间相位因子 exp(2pi i k·D) 的交叉相关 | M5 | ✅ 复用 |

### 缺失工具（需新建）

| # | 缺失工具 | 用途 | 对应 M | 复杂度 |
|---|---------|------|--------|--------|
| X1 | `build_noncoplanar_triangle(theta_inc, delta_h, side_ratios)` | 构建非共面三角形构型：绕 X 轴旋转 + 法线方向高度差 + 臂长比 | M1 | 低 |
| X2 | `coplanarity_measure(sat_positions)` | 标量三重积非共面度量 | M1 | 极低 |
| X3 | `single_arm_chiral_orf(arm1, arm2, f, ntheta, nphi)` | 单臂非共面链路对 Gamma^V 计算器 (K3 基准验证) | M2 | 低 |
| X4 | 参数扫描引擎 `scan_params(theta_inc_range, delta_h_range, side_ratio_range)` | 遍历参数空间，调用 X1+T10 或 T6 计算 | M3, M4 | 中 |
| X5 | 几何-响应拟合 `fit_geometry_response(coplanarity_values, gammaV_values)` | 线性/二次拟合 + R^2 评估 | M5 | 低 |
| X6 | `generate_6_figures(results, output_dir)` | 所有 6 张输出图表生成 | M6 | 中 |
| X7 | CSV 输出引擎 `write_results_csv(results, filename)` | 数据持久化 | M6 | 低 |
| X8 | **主脚本** `scripts/12-noncoplanar-triangular-chiral-orf.py` | 编排上述所有功能 | M1 | 高 |

---

## 2. 知识缺口

| # | 缺口 | 严重度 | 影响范围 | 缓解措施 |
|---|------|--------|---------|---------|
| KG1 | **K3 基准验证数据缺失**: 单臂非共面链路对 |Gamma^V|~0.041 (30mHz) 没有保存的结果文件 | MEDIUM | M2 阶段将直接通过 T4 (olc_link_response_grid) 重新计算并验证，不需要外部数据 |
| KG2 | 真实太阳轨道动力学导致的自然非共面性 — 需要轨道积分计算，本迭代未覆盖 | LOW | M4 (可降级跳过) | P1 优先级已排除，P0 仅使用人工构造 |
| KG3 | OLC 传递函数中 |cos_nu| 符号约定在非共面几何下的正确性 | MEDIUM | T1 使用 |cos_nu| 已在 script 10 中验证; 非共面下需检查 cos_nu = k_hat · u_link 的符号 |
| KG4 | JCAP 几何因子映射到 OLC 的适用性 (Iteration 6 置信度 0.70) | LOW | 本迭代不需要 JCAP 框架，直接数值积分 | 不阻塞 |
| KG5 | E 变量 CW sum 的三臂求和是否可能在非共面下恢复某种对称性 | HIGH (理论) | M3 核心风险 R2 | 先计算 theta_inc=90°, delta_h=0.5 最大非共面; 若 Gamma^V 仍接近零则回退到单臂链路对 |
| KG6 | 多星座交叉相关 vs 单三角非共面手征响应的物理起源一致性 | LOW (已有研究基础) | M5 比较分析 | memory/16 已阐明网络效应; 单三角非共面是否共享同一机制是待回答问题而非前置知识 |

**综合评估**: 知识缺口不阻塞进入 2-loop。KG1 通过 M2 重新计算解决；KG3 在实现中通过调试解决；KG5 是验证目标而非阻塞项。

---

## 3. 工具完备性评估

### 总体评估: **基本完备 (mostly complete)**

**已完成部分** (18/25 项，72%):
- 所有核心物理引擎 (T1-T18) 均已存在并经过 Iteration 6/7 验证
- OLC 传递函数 (T1) 在 scripts 10 和 11 中完全一致
- 单臂链路响应 (T4), Michelson ORF (T6), E 变量 CW sum (T9), 交叉相关 (T10), sky-max (T11) 全部可用
- 天空网格基础设施 (T14) 和频率扫描 (T15) 可直接复用
- 镜面对称性验证框架 (T16-T18) 在 test_crosscorr_symmetry.py 中
- memory/15 (归一化约定) 和 memory/16 (镜面对称性理论) 内容已完整吸收

**需新建部分** (7/25 项，28%):
- 所有缺失工具 (X1-X8) 均为**已有工具的编排和组合**，不涉及新物理公式
- X1 (build_noncoplanar_triangle) 是纯几何操作：rotate around X + add height differential + scale arms
- X4 (参数扫描引擎) 是简单的嵌套循环调用 T10/T6
- X8 (主脚本) 是已有模式的聚合

**与既有工作的一致性**:
- 脚本 10 的 `test_coplanar_zero()` 可直接作为 P1 (共面零检验) 的起点
- 脚本 11 的 `Constellation._apply_inclination()` 已有 X 轴旋转实现，X1 在此基础上扩展 delta_h 和 side_ratios
- 归一化约定 norm_V=1.0 (sky-max) 在脚本 11 T11 中已实现
- 共面等边三角形的 base_arms 在脚本 11 的 factory 函数中已定义

### 阻塞项

**无硬阻塞项**。所有物理计算引擎均可复用，缺失的是编排逻辑和参数扫描基础设施。这在 M1 阶段通过新建 `scripts/12-noncoplanar-triangular-chiral-orf.py` 即可解决。

---

## 4. 复用确认

### Iteration 6 代码 (scripts/10-olc-chiral-orf-triangular.py)

| 组件 | 复用方式 | 验证 |
|------|---------|------|
| OLC 传递函数 T(f,L,cos_nu) | 直接 import | ✅ 与 script 11 公式一致 |
| 三角形卫星位置生成 | 直接 import + 扩展 (添加 theta_inc/delta_h) | ✅ non-equilateral 已支持 |
| 单臂链路响应 | 直接 import | ✅ 包含 F_A(u) 频率依赖 |
| Michelson 有效响应 | 直接 import | ✅ R_A^M = R_A(a) + R_A(b) |
| Michelson 手征 ORF | 直接 import | ✅ Gamma^V = int[M1p*M2x - M1x*M2p] |
| 共面零检验 | 直接 import | ✅ test_coplanar_zero() |
| 方位角平均 | 直接 import | ✅ tri_orf_orient_avg |
| 天空网格+积分权重 | 直接 import | ✅ ntheta=32, nphi=64, sin(theta) 权重 |

### Iteration 7 代码 (scripts/11-multi-constellation-chiral-orf.py)

| 组件 | 复用方式 | 验证 |
|------|---------|------|
| E 变量 CW sum antenna pattern | 直接 import | ✅ cw_links = [(0,1),(1,2),(2,0)] |
| 交叉相关 ORF (sky-avg) | 直接 import | ✅ gamma_I, gamma_V |
| Sky-maximized norm_V | 直接 import | ✅ max over sky of chiral/auto |
| Constellation class | 直接 import + 扩展 | ✅ _apply_inclination 已有 |
| 工厂函数 (lisa/taiji/olc) | 直接 import | ✅ 可作为 baseline |
| 频率扫描基础设施 | 直接 import | ✅ log-spaced 1mHz-100Hz |

### Memory 文件

| 文件 | 内容 | 状态 |
|------|------|------|
| memory/15 | chi_orb=0.17 归一化约定解析：norm_V=1.0 正确，与 Orlando 不同量纲 | ✅ 已吸收 |
| memory/16 | 镜面对称性与 R^V=0 证明；多星座交叉相关的网络效应解释 | ✅ 已吸收 |
| memory/13 | Iteration 6 调查报告，JCAP 框架 | ✅ 参考使用 |

### 对称性验证框架

| 脚本 | 用途 | 状态 |
|------|------|------|
| test_crosscorr_symmetry.py | 快速验证旋转/倾斜下 R^V 行为 | ✅ 用于 M2 基准 |
| test_non_michelson_chiral.py | 非 Michelson 线性组合测试 | ✅ 参考使用 |

---

## 5. K3 基准验证计划

已知结果：单臂非共面链路对 |Gamma^V| > 0.041 (30 mHz)

验证方法（M2 阶段）：
```python
# 使用 T4 olc_link_response_grid 直接计算
arm1_dir = np.array([1, 0, 0])   # x 方向
arm2_dir = np.array([0, 0, 1])   # z 方向 (非共面)
R1 = olc_link_response_grid(f=0.03, L=2.5e9, *arm1_dir, ntheta=32, nphi=64)
R2 = olc_link_response_grid(f=0.03, L=2.5e9, *arm2_dir, ntheta=32, nphi=64)
# chiral_integrand = R1p*R2x - R1x*R2p
# Gamma^V = sum(chiral_integrand * dOmega) / (4*pi)
```

T4 (`olc_link_response_grid`) 已在脚本 10 中实现，输入 (f, L, theta, phi, d_norm) 返回 (R_+, R_x)，可直接用于单臂链路对计算。

---

## 6. 文献与理论基线

### 已确认的参考文献

| # | 引用 | 与本迭代关系 |
|---|------|-------------|
| R1 | Orlando 2021 (arXiv:2011.07059) | LISA-Taiji 交叉相关基准，hand. = 0.17 |
| R2 | Hu & Wolff (2002) | 手征 GW 检测基础 |
| R3 | Kato & Soda (2016) | 手征 ORF 形式体系 |
| R4 | Allen & Romano (1999) | 交叉相关 ORF 基础 |
| R5 | Lou 硕士论文 | OLC 传递函数 (Eq. 2-30) |

### 无需补充的文献

本迭代的核心物理已经由 Iterations 5-7 的严格证明和数值验证覆盖：
- 镜面对称性 → R^V=0 (memory/16 完整证明)
- Michelson 零手征响应 (scripts/10 验证通过)
- E 变量打破对称性 (scripts/11 实现)
- 多星座 |Gamma^V| ~ 1.0 (scripts/11 验证)

非共面构型的参数空间扫描属于**数值探索**而非理论推导，不需要新的文献。

---

## 7. 新颖性评估

**评估: N1 — 需要少量调整/组合**

理由：
1. **无新物理公式**: 所有计算基于已验证的 T1-T18，不涉及新数学结构
2. **核心创新是几何构造**: X1 (`build_noncoplanar_triangle`) 是纯几何变换，不涉及物理公式
3. **编排模式**: M1-M6 的执行流程完全基于已有脚本的调用链
4. **唯一不确定点**: E 变量 CW sum 在非共面下的 Gamma^V 行为 (KG5)，但这是**验证目标**而非**设计障碍**

**与 N2/N3 的区别**:
- N2 (需显著调整): 需要修改已有公式或推导新理论 — 不需要
- N3 (全新): 从头开始编写 — 不需要
- N1 (少量调整): fork + 组合已有引擎 — **本次任务**

---

## 8. enter_2loop 决策

### 前置条件检查

| # | 条件 | 状态 |
|---|------|------|
| 1 | 1-loop/01-03 文件已完成并审核 | ✅ |
| 2 | 核心物理引擎 (T1-T18) 全部可用 | ✅ |
| 3 | Memory/15, Memory/16 理论已吸收 | ✅ |
| 4 | 知识缺口不阻塞进入执行 (KG1-KG6) | ✅ |
| 5 | 无硬阻塞项 | ✅ |
| 6 | 新颖性评估为 N1 (可执行) | ✅ |
| 7 | 判定标准 P1-P8 明确可验证 | ✅ |

### 决策

```
enter_2loop: true
```

**理由**: 所有物理计算引擎均已验证可用，缺失的编排逻辑 (X1-X8) 属于已有工具的组装，不涉及新物理推导。参数空间扫描 (M3) 和比较分析 (M6) 是纯数值工作，2-loop 执行框架完全就绪。

**进入 2-loop 后第一个行动**: 在 `scripts/12-noncoplanar-triangular-chiral-orf.py` 中实现 X1 (build_noncoplanar_triangle) + X2 (coplanarity_measure)，然后立即执行 M2 (共面零检验 + K3 基准验证) 以确保新代码正确性。

### 进入 2-loop 的最低要求

1. 完成 M1 (script 12 fork) — 预期 <1 小时
2. M2 验证通过 — P1 (共面零检验) 和 K3 基准验证
3. 至少完成 P0 参数扫描 (12 种构型)
4. 其余 M3-M6 可在 2-loop 内逐步完成

### 降级方案

如果 2-loop 中 P0 扫描发现 E 变量 CW sum 的 Gamma^V 接近零 (KG5):
1. 回退到单臂链路对 Gamma^V (使用 T4)，跳过 E 变量
2. 将 M3 改为单臂链路对参数扫描
3. M5 和 M6 相应调整

此降级不阻塞 `enter_2loop: true`。

---

## 9. 置信度总结

| 维度 | 置信度 | 论据 |
|------|--------|------|
| 物理理论基础 | 0.95 | Iteration 6 严格证明 + memory/15/16 完整覆盖 |
| 核心代码可用性 | 0.95 | T1-T18 全部经过 Iteration 6/7 验证 |
| 新代码复杂度 | 0.85 | X1-X8 为已有引擎编排，无新物理 |
| K3 基准可验证 | 0.90 | T4 可直接用于单臂链路对计算 |
| 参数扫描可行性 | 0.90 | P0 仅需 12 种构型，每种 32x64 网格 ~2s |
| enter_2loop 准备度 | 0.90 | 无硬阻塞项，降级方案明确 |
| **综合置信度** | **0.90** | |

**达到进入 2-loop 的最低要求 (0.80)**。

---

## 10. 输出文件清单

| # | 文件 | 创建阶段 | 状态 |
|---|------|---------|------|
| O1 | `loop/1-loop/04-信息搜集-Iteration8.md` | 本阶段 | ✅ 创建中 |
| O2 | `scripts/12-noncoplanar-triangular-chiral-orf.py` | 2-loop/01 | ❌ 待创建 |
| O3 | `loop/2-loop/04-置信度评估-Iteration8.md` | 2-loop/04 | ❌ 待创建 |
| O4 | `memory/17-noncoplanar-olc-chiral-orf-iteration8.md` | 2-loop/06 | ❌ 待创建 |
| O5 | CSV 数据文件 | 2-loop/06 | ❌ 待创建 |
| O6 | 6 张 PNG 图表 | 2-loop/06 | ❌ 待创建 |

---

*信息搜集完成。确认 enter_2loop: true。*
