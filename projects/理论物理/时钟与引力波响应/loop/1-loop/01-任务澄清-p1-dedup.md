# P1 代码去重 — 1-loop/01 任务澄清

> **阶段**: 1-loop/01 任务澄清
> **项目**: D1-grav-waves
> **范围**: 1-loop 仅限，仅澄清和定义任务，不执行修改

---

## 0. 项目背景

该项目的 60+ 个 Python 脚本用于引力波/手写性 ORF（Overlap Reduction Function）研究，核心是 chiral ORF（Stokes V 极化相关）的计算。`src/core/` 中已有 19 个共享模块，但大量脚本仍自行定义重复函数。

**已有 core 模块**: `/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/src/core/`
- `constants.py` — 物理常数（c, G, h_bar, H_0, Mpc_in_m, AU_in_m）
- `transfer.py` — `olc_transfer_function(f, L, cos_nu)`
- `orf.py` — `compute_orf_standard(...)`
- `chiral.py` — `chiral_factor`, `compute_orf_chiral`, `compute_orf_chiral_compare`
- `geometry.py` — `arm_direction`, `build_constellation`, `make_triangle_constellation`, `link_direction`
- `antenna.py` — `antenna_patterns(n_theta, n_phi, u_theta, u_phi)`
- `sky.py` — `sky_grid`, `dOmega_element`, `sky_average`
- `noise.py` — `olc_noise_psn`, `olc_noise_qpn`, `interferometer_noise_psd`

当前覆盖率：66 个脚本中仅 7 个（10.6%）已导入 core 模块。

---

## 1. 脚本清单（按类型分类）

### 类型 A：正式论文脚本（需修改，导入 core）

| # | 文件名 | 核心导入 | 待提取函数 |
|---|--------|---------|-----------|
| A1 | `01-olc-orf-solver.py` | `constants.c`, `orf.compute_orf_standard` | 无 |
| A2 | `02-olc-noise-spectrum.py` | 未知 | 待确认 |
| A3 | `03-olc-snr-solver.py` | 未知 | 待确认 |
| A4 | `04-olc-3d-orf.py` | `transfer`, `antenna`, `orf` | 无 |
| A5 | `05-olc-detection-requirements.py` | `constants.c` | 无 |
| A6 | `06-olc-lisa-mixed-network.py` | 未知 | 待确认 |
| A7 | `06a-patched-mixed-network.py` | 未知 | 待确认 |
| A8 | `07-space-olc-snr.py` | 未知 | 待确认 |
| A9 | `08-space-olc-band-comparison.py` | 未知 | 待确认 |
| A10 | `09-olc-chiral-orf.py` | 无 | `olc_transfer_function` (行80), `compute_orf_chiral_compare` (行61), `arm_directions_3d` (行82), `orf_orient_avg_standard` (行108), `orf_orient_avg_chiral` (行119) |
| A11 | `10-olc-chiral-orf-triangular.py` | `constants.c`, `transfer.olc_transfer_function` | `olc_link_response_grid` (行41), `link_direction` (行112), `michelson_effective_response` (行125) |
| A12 | `11-multi-constellation-chiral-orf.py` | `constants.c`, `transfer.olc_transfer_function` | `antenna_pattern_e_variable` (行277, 探测器张量法), `antenna_pattern_e_variable_universal` (行452, CW link sum), `e_variable_response_grid` (行129), `compute_detector_tensor_e` (行225) |
| A13 | `12-noncoplanar-triangular-chiral-orf.py` | `constants.c`, `transfer.olc_transfer_function` | `olc_link_response_grid` (行49), `link_direction` (行214), `e_variable_response` (行250) |

**A 类共 13 个脚本**，其中 4 个已部分清理（A1, A4, A5, A11, A12），剩余 8 个需大量修改。

### 类型 B：调试/测试脚本（暂不修改，但需记录）

| 文件名 | 重复函数 |
|--------|---------|
| `_debug_v17_7p75_value.py` | `olc_transfer_function` (行33), `antenna_pattern_cw_sum` (行66) |
| `_debug_v17_7p75_value_v2.py` | `olc_transfer_function` (行20) |
| `_debug_v17_7p75_value_v3.py` | `olc_transfer_function` (行19) |
| `_debug_v17_7p75_value_v4.py` | —（无 olc_transfer_function） |
| `_debug_v17_hypotheses.py` | 待确认 |
| `_definitive_chiral_validation.py` | `olc_transfer_function` (行25), `antenna_pattern_cw_sum` (行47) |
| `_diag_chiral.py` | 待确认 |
| `_diag_comparison.py` | `olc_transfer_function` (行16), `antenna_pattern_cw_sum` (行32) |
| `_diag_freq_scan.py` | 待确认 |
| `_diag_link_evar.py` | 待确认 |
| `_diag_orlando_e.py` | 待确认 |
| `_diag_sky_max.py` | 待确认 |
| `_diag_taiji_tf.py` | 待确认 |
| `_scan_p23_comprehensive.py` | `olc_transfer_function` (行23) |
| `_scan_p23_fine_no_sp.py` | `olc_transfer_function` (行13) |
| `_scan_p23_fine.py` | `olc_transfer_function` (行17) |
| `_scan_single_sky_p23.py` | `olc_transfer_function` (行20) |
| `compute_chiral_orf_for_paper.py` | `olc_transfer_function` (行28), `antenna_pattern_e_variable` (行52) |
| `debug_gamma.py` ~ `debug_gamma9.py` | 待确认（9 个文件） |
| `debug_hd.py` | `antenna_patterns` (行10) |
| `debug_Minv.py` | 待确认 |
| `debug_rv_zero.py` | 待确认 |
| `diag_jcap_vs_num.py` | 待确认 |
| `explore-asymmetric-chiral.py` | `olc_transfer_function` (行17), `olc_link_response_grid` (行32), `link_direction` (行58), `compute_variable_on_sky` (行68) |
| `explore-non-michelson-chiral.py` | `olc_transfer_function` (行17), `olc_link_response_grid` (行32), `link_direction` (行58), `compute_variable_on_sky` (行68) |
| `nishizawa-xval.py` | `olc_transfer_function` (行38) |
| `p24_generate_plots.py` | `olc_transfer_function` (行34) |
| `test_non_michelson_chiral.py` | `olc_transfer_function` (行12), `olc_link_response_grid` (行26), `link_direction` (行48), `compute_variable_on_sky` (行57) |
| `test_non_michelson_deep.py` | 同 `test_non_michelson_chiral.py` |
| `validate_orlando_crosscorr.py` | `sky_grid` (行73) |
| `validate_orlando_response.py` | 待确认 |
| `verify-chiral-orf-analytical.py` | `olc_transfer_function` (行30) |
| `verify-helicity-flip-symmetry.py` | `olc_transfer_function` (行52), `antenna_pattern_e_variable_cw` (行104) |
| `verify_08_physics.py` | 待确认 |
| `verify_snr_v19.py` | 待确认 |
| `verify_snr_v21.py` | 待确认 |
| `chiral_orf_jcap_analytical.py` | 待确认 |

**B 类共约 37 个脚本**，均为调试/测试/探索性质，暂不修改。

### 类型 C：备份文件（不应触碰）

| 文件名 | 内容 |
|--------|------|
| `09-olc-chiral-orf-20260705-002945.py` | timestamped 备份：重复 `olc_transfer_function` (行39), `antenna_patterns` (行55), `compute_orf_standard` (行72), `compute_orf_chiral` (行123), `arm_directions_3d` (行192) |
| `09-olc-chiral-orf-20260705-054129.py` | timestamped 备份：同上述函数 |
| `09-olc-chiral-orf-20260705-055622.py` | timestamped 备份：同上述函数 |
| `11-multi-constellation-chiral-orf.py.bak` | 备份：`olc_transfer_function` (行40), `olc_link_response_grid` (行97), `link_direction` (行141) |
| `_diag_orlando_e.py.bak` | 备份 |

**C 类共 5 个文件**，不应修改或删除。

### 类型 D：已清理脚本（无需修改）

| # | 文件名 |
|---|--------|
| D1 | `01-olc-orf-solver.py` (导入 `constants.c`, `orf.compute_orf_standard`) |
| D2 | `04-olc-3d-orf.py` (导入 `transfer`, `antenna`, `orf`) |
| D3 | `05-olc-detection-requirements.py` (导入 `constants.c`) |
| D4 | `10-olc-chiral-orf-triangular.py` (导入 `constants.c`, `transfer.olc_transfer_function`) |
| D5 | `11-multi-constellation-chiral-orf.py` (导入 `constants.c`, `transfer.olc_transfer_function`) |
| D6 | `12-noncoplanar-triangular-chiral-orf.py` (导入 `constants.c`, `transfer.olc_transfer_function`) |

**D 类共 6 个脚本**，已部分导入 core。

### 类型 E：无关脚本（转换/验证辅助工具，无需修改）

- `convert_final.py`, `convert_markdown_to_latex.py`, `convert_to_latex.py`, `convert_to_latex2.py` — LaTeX 转换工具
- `final_heatmap.py`, `p24_generate_plots.py` — 出图脚本
- `space_olc_band_comparison.csv` — 数据文件（非 Python）

---

## 2. 需提取至 core 的函数

### 2.1 `olc_transfer_function` — 已完成（无需额外处理）

**现状**: `src/core/transfer.py` 已有实现，23 个脚本仍自行定义。

**核心版本** (`src/core/transfer.py`):
```python
def olc_transfer_function(f, L, cos_nu, eps=1e-15):
    # 使用 lazy _consts.c
```

**脚本版本差异**: 所有脚本版本与 core 版本在物理逻辑上完全一致（Lou Eq. 2-30），仅实现细节（如 eps 位置、scalar_in 处理）略有不同。

**结论**: 所有 B 类脚本只需添加 `from src.core.transfer import olc_transfer_function` 并删除本地定义。**不需要新的 core 函数**。

### 2.2 `olc_link_response_grid` — 需新增 core 函数

**发现**: 4 种不同签名，3 种实现变体。

| 版本 | 签名 | 脚本 |
|------|------|------|
| V1 | `olc_link_response_grid(tG, pG, arm_theta, arm_phi, L)` | 10, 12 |
| V2 | `olc_link_response_grid(f, tG, pG, arm_theta, arm_phi, L)` | explore-asymmetric, explore-non-michelson |
| V3 | `olc_link_response_grid(theta_u, phi_u, L, tG, pG)` | test_non_michelson_chiral, test_non_michelson_deep |

**实现一致性**: V1/V2/V3 的函数体在物理上等价（计算 `e_A^{ab} u_a u_b * T(f, L, cos_nu)`），仅参数顺序不同。

**建议**: 新增核心函数 `olc_link_response_grid(tG, pG, arm_theta, arm_phi, L)`，采用 V1 签名（无冗余 f 参数）。所有 B 类脚本使用此签名。

```python
# 新 core 函数签名（建议）
def olc_link_response_grid(tG, pG, arm_theta, arm_phi, L):
    """单条 OLC 单向链路在天空网格上的 GW 响应。
    
    Returns: (R_plus, R_cross) = e_A^{ab} u_a u_b * T(f, L, cos_nu)
    """
```

### 2.3 `arm_directions_3d` — 需新增 core 函数

**发现**: 4 个脚本（04, 09 系列 3 个备份）自行定义此函数。

| 签名 | 脚本 |
|------|------|
| `arm_directions_3d(arm_angle, dihedral, base_theta, base_phi)` | 04, 09 备份 |
| `arm_directions_3d(arm_angle, base_theta, base_phi, n=3)` | 09-olc-chiral-orf.py |

**关系**: `src/core/geometry.py` 已有 `arm_direction(arm_angle)` 和 `build_constellation(...)`。`arm_directions_3d` 是对 `arm_direction` 的批量调用，加上坐标旋转。

**建议**: 不单独提取，改用现有的 `arm_direction` + 旋转矩阵组合。如确有需要，新增 `arm_directions_3d` 到 `geometry.py`。

### 2.4 `link_direction` — 存在签名不兼容问题

**核心版本** (`src/core/geometry.py`):
```python
def link_direction(r_from, r_to):
    """返回 (unit_vector_3d, distance)"""
    # return direction, distance  # vector, not angles
```

**脚本版本** (10, 12, explore-asymmetric, explore-non-michelson, test_*):
```python
def link_direction(r_from, r_to):
    """返回 (theta, phi, distance)"""
    # returns spherical angles + distance
```

**结论**: 核心版本和脚本版本返回类型**完全不同**（矢量 vs 球坐标角度），二者不兼容。**不应强行合并**。

**建议**:
- 保留核心 `link_direction` 不变（返回矢量，更通用）
- 脚本中使用的 "返回角度的 link_direction" 作为独立工具函数，可命名为 `link_angles` 或留在各脚本中

### 2.5 E-variable 天线方向图 — 存在 4 种不同实现

这是本次去重中最复杂的部分，因为 E-variable 本身有多种计算方法，且不同脚本采用了不同方法。

#### 模式 1：探测器张量法（detector tensor formalism）

- **脚本**: `11-multi-constellation-chiral-orf.py` (行277)
- **函数**: `antenna_pattern_e_variable(tG, pG, a1, a2, a3, n, L, det_type)`
- **原理**: 基于反对称探测器张量 `D_E^{ij} = (L/2) * (a1^i n^j - a1^j n^i + cyclic)`，投影到 GW 偏振
- **签名**: `(tG, pG, arm_vectors a1,a2,a3, normal n, L)`
- **返回值**: `(R_plus, R_cross)` 实数数组

#### 模式 2：CW link sum（顺时针链路求和）— "universal" 版本

- **脚本**: `11-multi-constellation-chiral-orf.py` (行452)
- **函数**: `antenna_pattern_e_variable_universal(tG, pG, satellite_positions, L, det_type)`
- **原理**: 对 3 条顺时针链路 (1→2, 2→3, 3→1) 求和 `F_+(link_k) * T(link_k)`
- **签名**: `(tG, pG, satellite_positions, L, det_type)`
- **返回值**: `(R_plus, R_cross)` 复数数组

#### 模式 3：CW link sum — 简化版（仅 OLC 转移函数）

- **脚本**: `12-noncoplanar-triangular-chiral-orf.py` (行250)
- **函数**: `e_variable_response(tG, pG, sat_positions, L)`
- **原理**: 同模式 2，但不支持 `det_type` 参数，硬编码使用 OLC transfer function
- **签名**: `(tG, pG, sat_positions, L)` — 比模式 2 少 1 个参数
- **返回值**: `(R_plus, R_cross)` 复数数组

#### 模式 4：CW link sum — paper 验证版

- **脚本**: `compute_chiral_orf_for_paper.py` (行52)
- **函数**: `antenna_pattern_e_variable(tG, pG, satellite_positions, L)`
- **原理**: 同模式 2/3，支持 OLC transfer function
- **签名**: `(tG, pG, satellite_positions, L)`
- **返回值**: `(R_plus, R_cross)` 复数数组

#### 模式 5：CW link sum + 双探测器类型（OLC vs Interferometer）

- **脚本**: `verify-helicity-flip-symmetry.py` (行104)
- **函数**: `antenna_pattern_e_variable_cw(tG, pG, satellite_positions, L, det_type)`
- **原理**: 同模式 2，但额外支持 `det_type='interferometer'`（使用 taiji_transfer_function）
- **签名**: `(tG, pG, satellite_positions, L, det_type)`
- **返回值**: `(R_plus, R_cross)` 复数数组

#### 模式 6：wrapper 版本（带 links_dict）

- **脚本**: `explore-asymmetric-chiral.py` (行68), `explore-non-michelson-chiral.py` (行68)
- **函数**: `compute_variable_on_sky(f, wdict, links_dict, tG, pG, L)`
- **原理**: 通过链接权重字典 `wdict` 构造任意线性组合（Michelson, E-like, T-like），每条链路使用 `olc_link_response_grid`
- **签名**: `(f, wdict, links_dict, tG, pG, L)`
- **用途**: 探索非 Michelson 组合的手征性

#### E-variable 推荐策略

```
新 core 函数（建议）:

def e_variable_response_cw(tG, pG, satellite_positions, L, det_type='olc'):
    """CW link sum E-variable antenna pattern.
    
    对应上述模式 2/3/5 的统一实现。
    - 对 3 条 CW 链路求和: R_E+ = sum F_+(link) * T(link)
    - det_type='olc' 使用 src.core.transfer.olc_transfer_function
    - det_type='interferometer' 使用 Michelson transfer function
    """

def e_variable_response_tensor(tG, pG, a1, a2, a3, normal, L, det_type='olc'):
    """Detector tensor formalism E-variable antenna pattern.
    
    对应上述模式 1 的实现。
    """

def compute_e_variable_orf(f, const1, const2, ...):
    """Cross-constellation chiral ORF with spatial phase factor."""
```

**注意**: 模式 1（探测器张量法）与模式 2/3/5（CW link sum）在物理上等价（都描述同一个 TDI E variable），但实现路径不同。模式 2 是已验证正确的版本（"detector tensor approach gives ~1e-5; the correct CW sum gives ~1e-3"）。建议以 CW link sum 为主要实现。

### 2.6 `antenna_patterns` — 已在 core 中

`src/core/antenna.py` 已有 `antenna_patterns(n_theta, n_phi, u_theta, u_phi)`。4 个脚本仍自行定义（3 个 timestamped 备份 + 1 个 debug_hd.py）。删除即可。

### 2.7 `compute_orf_standard` 和 `compute_orf_chiral` — 已在 core 中

`src/core/orf.py` 和 `src/core/chiral.py` 已有实现。仅有 3 个 timestamped 备份自行定义。删除即可。

### 2.8 `antenna_pattern_cw_sum`（调试版本）

- `09-olc-chiral-orf.py` 无此函数
- `_debug_v17_7p75_value.py` 行66: `antenna_pattern_cw_sum_flexible`
- `_definitive_chiral_validation.py` 行47: `antenna_pattern_cw_sum`
- `_diag_comparison.py` 行32: `antenna_pattern_cw_sum`

这些都是调试脚本，不需要提取到 core。当 core 的 `e_variable_response_cw` 建成后，调试脚本可以切换过来。

### 2.9 `compute_orf_chiral_compare` — 脚本私有

`09-olc-chiral-orf.py` 行61 有自己的 `compute_orf_chiral_compare` 实现。`src/core/chiral.py` 已有 `compute_orf_chiral_compare`。只需改为 import。

### 2.10 `sky_grid` override

`validate_orlando_crosscorr.py` 行73 有自定义 `sky_grid(Ntheta, Nphi)`。`src/core/sky.py` 已有 `sky_grid(ntheta=60, nphi=120)`。签名不同（参数名和默认值），但不影响使用。

---

## 3. 修改优先级

### P0 — 紧急：正式脚本中删除重复的 `olc_transfer_function`

| 文件 | 行号 |
|------|------|
| `09-olc-chiral-orf.py` | ~80 |
| `compute_chiral_orf_for_paper.py` | 28 |
| `explore-asymmetric-chiral.py` | 17 |
| `explore-non-michelson-chiral.py` | 17 |
| `nishizawa-xval.py` | 38 |
| `p24_generate_plots.py` | 34 |
| `test_non_michelson_chiral.py` | 12 |
| `test_non_michelson_deep.py` | 12 |
| `verify-chiral-orf-analytical.py` | 30 |
| `verify-helicity-flip-symmetry.py` | 52 |

操作：删除本地定义，改为 `from src.core.transfer import olc_transfer_function`

### P1 — 高优先级：正式脚本中的其他重复函数

| 文件 | 函数 | 操作 |
|------|------|------|
| `09-olc-chiral-orf.py` | `compute_orf_chiral_compare`, `orf_orient_avg_standard`, `orf_orient_avg_chiral` | 从 `src/core/chiral.py` import |
| `09-olc-chiral-orf.py` | `arm_directions_3d` | 考虑改为 `geometry.arm_direction` 组合 |
| `10-olc-chiral-orf-triangular.py` | `olc_link_response_grid`, `link_direction`, `michelson_effective_response` | 新增 core 函数 + 修改调用 |
| `12-noncoplanar-triangular-chiral-orf.py` | `olc_link_response_grid`, `link_direction`, `e_variable_response` | 同上 + 统一 E-variable 接口 |
| `explore-asymmetric-chiral.py` | `olc_link_response_grid`, `link_direction`, `compute_variable_on_sky` | 新增 core 函数 |
| `explore-non-michelson-chiral.py` | 同 explore-asymmetric | 同上 |
| `test_non_michelson_chiral.py` | 同 explore-asymmetric | 同上 |
| `test_non_michelson_deep.py` | 同 explore-asymmetric | 同上 |

**新增 core 函数（需创建）**:
1. `src/core/transfer.py` 中新增 `olc_link_response_grid(tG, pG, arm_theta, arm_phi, L)`
2. `src/core/e_variable.py` 中新增 `e_variable_response_cw(tG, pG, satellite_positions, L, det_type='olc')`
3. `src/core/e_variable.py` 中新增 `e_variable_response_tensor(tG, pG, a1, a2, a3, normal, L)`
4. `src/core/e_variable.py` 中新增 `compute_e_variable_orf(...)`（跨星座相关）

### P2 — 中优先级：调试脚本的清理

所有 B 类脚本中的 `olc_transfer_function` 定义可统一删除并 import core。`antenna_patterns` 和 `compute_orf_standard/chiral` 备份同理。

| 文件 | 函数 |
|------|------|
| `_debug_v17_7p75_value.py` 等 5 个 debug 脚本 | `olc_transfer_function` |
| `_scan_p23_*.py` 等 4 个 scan 脚本 | `olc_transfer_function` |
| `_diag_*.py` 等 7 个 diag 脚本 | 待确认具体函数 |
| `debug_hd.py` | `antenna_patterns` |
| `verify-helicity-flip-symmetry.py` | `antenna_pattern_e_variable_cw`（需要新的 core 函数） |

### P3 — 低优先级：timestamped 备份和 .bak 文件

所有 C 类文件（5 个）不需要修改。

---

## 4. E-variable 实现差异详细对比

| 维度 | 模式1: 探测器张量 | 模式2: CW link sum (universal) | 模式3: CW link sum (简化) | 模式4: CW link sum (paper) | 模式5: CW link sum (双类型) | 模式6: wrapper |
|------|-------------------|-------------------------------|-------------------------|--------------------------|--------------------------|---------------|
| 脚本 | 11-multi-constellation | 11-multi-constellation | 12-noncoplanar | compute_chiral_orf_for_paper | verify-helicity-flip | explore-*/test_* |
| 签名 | `(tG,pG,a1,a2,a3,n,L)` | `(tG,pG,pos,L,det_type)` | `(tG,pG,pos,L)` | `(tG,pG,pos,L)` | `(tG,pG,pos,L,det_type)` | `(f,wdict,links,tG,pG,L)` |
| 输入 | 臂矢量+法向量 | 卫星位置 | 卫星位置 | 卫星位置 | 卫星位置 | 权重字典+链路字典 |
| 输出 | 实数 (R_plus,R_cross) | 复数 | 复数 | 复数 | 复数 | 复数 |
| det_type | 无 | 有 | 无 | 无 | 有 | N/A (仅 OLC) |
| 支持空间相位 | 否 | 否 | 否 | 是 | 是 | 否 |
| 支持交叉相关 | 否 | 是 (compute_cross_e_variable_orf) | 否 | 是 (compute_cross_e_variable_orf) | 否 | 否 |
| 空间相位因子 | — | — | — | exp(-2πi·f/c·k̂·Δx) | exp(-2πi·f/c·k̂·Δx) | — |
| 天空积分 | — | — | — | 内置 in compute_cross_e_variable_orf | 内置 | — |

**关键发现**:
1. 模式 2、3、4 本质上是同一算法（CW link sum），仅参数化程度不同
2. 模式 6 是独特的泛化方法，允许任意线性组合（不限于 E variable）
3. 只有模式 4 和 5 的实现包含了空间相位因子和跨星座 ORF 计算
4. 模式 1（探测器张量法）与模式 2/3/4 物理等价但实现路径不同

**建议**: 以模式 2（`antenna_pattern_e_variable_universal`）为蓝本创建 core 函数，融合模式 4 的空间相位因子和 ORF 计算，形成统一的 `src/core/e_variable.py`。

---

## 5. 总结：1-loop 任务的 2-loop 输入

本阶段输出为 2-loop 执行层提供以下输入：

1. **需修改的脚本清单**（A 类 13 个，其中 5 个需大规模修改）
2. **需新增的 core 函数**（3 个：`olc_link_response_grid`, `e_variable_response_cw`, `compute_e_variable_orf`）
3. **修改优先级**（P0/P1/P2/P3 四档）
4. **E-variable 统一方案**（以 CW link sum 模式 2 为蓝本）
5. **已知不兼容项**（`link_direction` 返回类型差异，不强行合并）

2-loop executor 应基于此文档编写 `02-任务分解.md`，详细规划每个脚本的具体修改步骤。
