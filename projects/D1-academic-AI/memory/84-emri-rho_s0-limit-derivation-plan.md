---
name: EMRI rho_s→0 limit derivation plan (iteration 83)
description: Subbrain 分析 EMRI Paper I JCAP 需要的 rho_s→0 极限解析推导方案
type: reference
---

## EMRI Paper I ρ_s→0 极限推导计划

### ρ_s→0 的物理含义
ρ_s 是 Dehnen 暗物质晕的核心密度。ρ_s→0 时暗物质晕消失，恢复纯 Schwarzschild 度规:
f(r) = 1 - 2M/r

### ρ_s→0 预期行为
- 同宿轨道在 Schwarzschild 中持续存在 (Perlick 1990, Cardoso et al.)
- λ_T 不趋于 0 (Schwarzschild λ_T ~ 3.5e-3, 最大值; DM 抑制混沌, 移除它恢复最大混沌)
- κ → κ_schw = 1/(4M)

### 需要的数学工具
1. **隐函数定理**: V_eff'(r_circ; ρ_s, r_s, L) = 0 → r_circ(ρ_s) 在 ρ_s=0 处 C1 光滑
2. **Melnikov 方法**: DM 项作为 Schwarzschild 测地线流的小扰动
3. **Peyrard-Auckly 变分表征**: KAM 阈值附近的平方根标度

### 具体推导计划 (3-5 页附录 A)
a) 证明 r_circ(ρ_s) = r_circ^(0) + ρ_s r_circ^(1) + O(ρ_s²)
b) 同宿轨道退化: r_hom(ρ_s) → r_hom^Schw
c) λ_T 展开: 线性化庞加莱映射, 特征值展开
d) 严格界限: MSS 不等式 λ_T² < κ²

### 已有 vs 缺失
- **已有** (2511.03657v1): 数值 Schwarzschild λ_T (Table 3), MSS 界限数值验证
- **缺失**: λ_T(ρ_s) 的解析展开, 同宿轨道持续性的严格证明, Melnikov 计算

### JCAP 提交建议
添加附录 "A. Schwarzschild limit (ρ_s → 0)"，使用隐函数定理+Melnikov 分析，3-5 页可满足 JCAP 分析严谨性要求。

### 实际完成（iteration 84）
- 创建 EMRI-AppendixA-Schwarzschild-limit.md（完整附录，含 5 个命题）
- 命题 A.1: 圆轨道半径解析性 (隐函数定理)
- 命题 A.2: 不稳定/同调轨道半径解析性
- 命题 A.3: 同调轨道持续性 (Melnikov 方法)
- 命题 A.4: Lyapunov 指数渐近展开
- 命题 A.5: SST 混沌界极限验证
- 核心结论：Schwarzschild 混沌是"温和"的 (λ_T << κ)，DM 抑制混沌
