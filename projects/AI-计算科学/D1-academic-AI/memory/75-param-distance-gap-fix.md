---
name: Iteration 75 — parameter distance gap fix
description: EMRI η connects δ to d_param, not directly to Γ; equivalence established via Prop 4.8
type: reference
---

## iteration 75 结果

### 核心修复

**问题**: 副脑审查 (iteration 74) 指出 Definition 4.5 中 η: δ ⇒ Γ 的连接是"错的"——Lemma 4.6 证明的是 δ ≤ C·(Δρ_s + Δr_s)，即参数空间距离 d_param，不是 L² 度规扰动距离 Γ。δ ≤ C·Γ 只是在 Dehnen 度规线性于 ρ_s 这个"巧合"下成立的。

### 修复方案

1. **Definition 4.5 重写**: η: δ ⇒ d_param 其中 d_param(X₁,X₂) = Δρ_s + Δr_s
2. **新增 Proposition 4.8** (参数-度规等价):
   - c·d_param ≤ Γ ≤ C·d_param 对于 Dehnen 族在紧区域 U 上成立
   - 上界: 度规扰动 h_ij 线性于 (ρ_s, r_s)，L² 范数控制
   - 下界: ∂h_tt/∂ρ_s 在 U 上非零，L² 下界成立
3. **新增 Corollary 4.9**: d_param 继承 pseudometric 结构
4. **更新 Proposition 4.7**: naturality square 改为 d_param
5. **更新 Theorem 5.2**: 明确 δ ≤ C·Γ 的推导链：η → d_param → (Prop 4.8) → Γ

### 修复后逻辑链
```
δ ≤ C·d_param (Definition 4.5 + Lemma 4.6, naturality)
d_param ≤ (1/c)·Γ (Proposition 4.8 lower bound)
∴ δ ≤ (C/c)·Γ (Theorem 5.2, derived)
```

### 未解决项
- 参数等价性是 Dehnen 族的特殊性质（线性参数化），不是一般范畴性质
- 对于一般非线性能量参数化，d_param 和 Γ 可能不等价

### 文件
- papers/DISTCAT-EMRI-2category-proof.md: version 75
