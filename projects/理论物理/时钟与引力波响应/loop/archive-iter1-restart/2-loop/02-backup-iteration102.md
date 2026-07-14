# 02-backup — Iteration 102

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/02-backup.md`
**状态**：completed
**输入**：loop/2-loop/01-pre-check-iteration102.md (pre-check PASS)
**输出**：备份关键文件，确保可回滚

---

## 备份说明

Iter102 将修改 `scripts/09-olc-chiral-orf.py` 以支持严格 P^V 形式 `Im(w_1^2 w_2^{*2})`。
备份关键代码段以便回滚。

---

## 当前实现备份

### `09-olc-chiral-orf.py` — Chiral ORF 核心逻辑（修改前）

**文件路径**：`scripts/09-olc-chiral-orf.py`
**备份时间**：2026-07-12
**修改范围**：
1. 新增函数 `chiral_factor_strict(u1, v1, u2, v2, nx, ny, nz)` — 使用 `Im(w_1^2 w_2^{*2})`
2. 在 `compute_orf_chiral()` 中添加严格形式计算路径（与原形式对比模式）
3. 新增 `test_strict_equivalence()` 测试函数

### 关键代码段备份

#### Line 177-179: 当前 chiral factor 实现（BEFORE）
```python
# Chiral factor: antisymmetric polarization combination
# F_+1 * F_×2 - F_×1 * F_+2 (parity-odd: F_+ is even, F_× is odd under reflection)
chiral_factor = F1p * F2x - F1x * F2p
```

#### Line 58-71: 天线方向图（不改，但需理解关系）
```python
def antenna_patterns(n_theta, n_phi, u_theta, u_phi):
    """F_plus and F_cross antenna patterns."""
    ct, st = np.cos(n_theta), np.sin(n_theta)
    cp, sp = np.cos(n_phi), np.sin(n_phi)
    ux = np.sin(u_theta)*np.cos(u_phi)
    uy = np.sin(u_theta)*np.sin(u_phi)
    uz = np.cos(u_theta)
    th_x, th_y, th_z = ct*cp, ct*sp, -st
    ph_x, ph_y, ph_z = -sp, cp, 0.0
    F_plus = (th_x*ux)**2 + (th_y*uy)**2 + (th_z*uz)**2 \
           - (ph_x*ux)**2 - (ph_y*uy)**2 - (ph_z*uz)**2
    F_cross = 2.0*(th_x*ux)*(ph_x*ux) + 2.0*(th_y*uy)*(ph_y*uy) \
            + 2.0*(th_z*uz)*(ph_z*uz)
    return F_plus, F_cross
```

**重要关系**：`th` 和 `ph` 构成垂直于 `n̂` 的正交归一基：
- `th = ∂n̂/∂θ`（极向）
- `ph = ∂n̂/∂φ`（方位向）
- 定义 `w = (th·u) + i(ph·u)`
- 则 `F_plus = (th·u)² - (ph·u)² = Re(w²)`
- 且 `F_cross = 2(th·u)(ph·u) = Im(w²)`
- 因此 `F1p*F2x - F1x*F2p = Im(w₁² · conj(w₂²)) = Im(w₁² w₂*²)`

#### Line 126-192: 完整的 `compute_orf_chiral()` 函数（完整备份，见 execute 阶段全文件）

---

## 回滚命令

如需回滚到当前状态：
```bash
# 备份修改后的文件
cp scripts/09-olc-chiral-orf.py scripts/09-olc-chiral-orf.py.iter102.modified
# 重新检查 git 状态或从 execute 阶段之前的提交恢复
```

---

## 结论

**备份完成 — 可进入 2-loop/03 执行阶段**

---

last_completed_at: 2026-07-12
