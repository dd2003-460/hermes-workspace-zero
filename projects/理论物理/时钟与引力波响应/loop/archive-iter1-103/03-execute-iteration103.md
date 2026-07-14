# 03-execute — Iteration 103

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/03-execute.md`
**状态**：completed
**输入**：loop/2-loop/02-backup-iteration103.md (backup ready)
**输出**：Iter103 执行结果

---

## 执行内容

**Bug 修复**: `1.0 - np.abs(cos_nu)` → `1.0 - cos_nu`

### 修复的文件 (15 files)

| # | 文件 | 行号 | 状态 |
|---|------|------|------|
| 1 | `scripts/09-olc-chiral-orf.py` | 44 | FIXED |
| 2 | `scripts/04-olc-3d-orf.py` | 34 | FIXED |
| 3 | `scripts/10-olc-chiral-orf-triangular.py` | 42 | FIXED |
| 4 | `scripts/11-multi-constellation-chiral-orf.py` | 44 | FIXED |
| 5 | `scripts/12-noncoplanar-triangular-chiral-orf.py` | 42 | FIXED |
| 6 | `scripts/explore-non-michelson-chiral.py` | 22 | FIXED |
| 7 | `scripts/test_non_michelson_chiral.py` | 20 | FIXED |
| 8 | `scripts/test_non_michelson_deep.py` | 20 | FIXED |
| 9 | `scripts/verify-helicity-flip-symmetry.py` | 58 | FIXED |
| 10 | `scripts/nishizawa-xval.py` | 41 | FIXED |
| 11 | `scripts/chiral_orf_jcap_analytical.py` | 333 | FIXED |
| 12 | `scripts/explore-asymmetric-chiral.py` | 16 | FIXED |
| 13 | `scripts/debug_rv_zero.py` | 80,159,195 | FIXED |
| 14 | `scripts/validate_orlando_chiral.py` | 34 | FIXED |
| 15 | `scripts/validate_orlando_response.py` | 49 | FIXED |

### 对比测试脚本 (新建)

`scripts/test_abs_vs_linear_cos_nu.py` — 对比 `|cos_nu|` vs `cos_nu` 的数值差异

---

## 执行结果

### 对比测试结果 (test_abs_vs_linear_cos_nu.py)

| 指标 | `|cos_nu|` 版本 | `cos_nu` 版本 | 相对误差 |
|------|-----------------|---------------|----------|
| chiral ORF (low f) | 1.85e-05 | ~0 | **96-99%** |
| sky-avg $\langle |T_1|^2 |T_2|^2 \rangle$ | 1.0468 | 1.0 | **4.68%** |
| at cos_nu=-1.0, |T| | 0.552 | 0.538 | **2.4%** |
| at cos_nu=-1.0, phase | -1.568 | -1.047 | **30 deg** |

### 核心脚本测试

| 测试 | 09-olc-chiral-orf | 11-multi-constellation | helicity-flip |
|------|-------------------|------------------------|---------------|
| T1: 天空网格收敛 | PASS | N/A | N/A |
| T2: 多频率一致性 | PASS | N/A | N/A |
| T3: Coplanarity $\Gamma^V=0$ | PASS | PASS (self-correlation) | PASS (Taiji*Taiji) |
| T4: Non-coplanar $\Gamma^V \neq 0$ | N/A | PASS (OLC x Taiji: -2.68e-04) | PASS (LISA*Taiji: -7.75e-03) |
| T5: $\text{Im}(w_1^2 w_2^{*2})$ 等价 | PASS (diff<3e-16) | N/A | N/A |
| T6: Reflection symmetry | N/A | N/A | PASS (max dev: 0) |

### 关键物理发现

1. **Coplanar 构型**: $\Gamma^V = 0$ (修复后), 之前非零是因为 `|cos_nu|` bug 破坏了反射对称性
2. **Non-coplanar 构型**: $\Gamma^V \neq 0$ 仍然成立, 数值合理 (Orlando benchmark: 1.34e-05)
3. **Self-correlation vs cross-correlation**: OLC 自相关 (2-arm) 共面, 所以 $\Gamma^V=0$; OLC x Taiji (cross) 非共面, 所以 $\Gamma^V \neq 0$

---

last_completed_at: 2026-07-12
