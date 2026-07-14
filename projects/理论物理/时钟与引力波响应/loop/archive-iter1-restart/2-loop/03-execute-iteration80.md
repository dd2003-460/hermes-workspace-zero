# 2-loop/03-execute (Iteration 80) — Helicity Flip Symmetry Verification Script

**状态**: completed
**完成时间**: 2026-07-11

## 执行内容

实现 `scripts/verify-helicity-flip-symmetry.py`，验证手征 ORF 的螺旋翻转对称性：

### 关键修复

1. **T3 修复**: 从 LISA×Taiji (tilted) 改为 Taiji×Taiji (coplanar)
   - 原因: 倾斜探测器破坏反射对称性 (θ,φ)→(θ,2π-φ)
   - 解析证明见 note/P-chiral-orf-analytical.md §4.3

2. **T4 修复**: 移除 sign flip 检查
   - 原因: 非共面构型不满足反射对称性
   - 仅保留 |Γ^V| > 1e-10 阈值检查

### 测试结果

```
Test 1: coplanar Taiji*Taiji Gamma^V ~ 0       | 0.0 < 1e-10  ✅ PASS
Test 2: reflection symmetry P^V + P^V(ref) ~ 0  | max_dev = 0      ✅ PASS
Test 3: spatial phase preserves helicity flip   | max_dev < 0.02   ✅ PASS
Test 4: non-coplanar LISA*Taiji Gamma^V != 0    | |Γ^V| = 7.75e-3 ✅ PASS
```

总耗时: ~34ms
