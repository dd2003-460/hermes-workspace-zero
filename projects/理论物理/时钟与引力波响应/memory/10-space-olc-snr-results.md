# Space OLC SNR 结果 — 公式确认与可探测性

> 创建时间: 2026-07-02
> 关键发现: 原始 SNR 公式正确，空间 OLC 可探测

---

## SNR 公式确认

### 两个候选公式

**Formula1 (原始代码)**:
```
dSNR²/df = 2·T_obs·Γ²·S_corr²(f)/S_y²(f)
```
其中 S_corr(f) = S_h · |T(f)|²，S_h = h_GW²/(4πf)，|T(f)|² ∝ (2πfL/c)²

**Formula2 (之前提议的"修正")**:
```
dSNR²/df = 2·T_obs·Γ²·S_corr²(f)/S_y(f)
```

### 维度分析

Formula1: S_corr² (Hz⁻²) / S_y² (Hz⁻²) = 无量纲
→ × T_obs (s) × ∫df (Hz) = 无量纲 ✓ SNR 无量纲，正确

Formula2: S_corr² (Hz⁻²) / S_y (Hz⁻¹) = Hz⁻¹
→ × T_obs (s) × ∫df (Hz) = Hz⁻¹ · s · Hz = 无量纲

两个公式维度上都"通过"，但物理含义不同。

### 数值验证

```
L=10m:   Formula1 SNR=3.91e-15, Formula2 SNR=1.11e-31
L=0.17Gm: Formula1 SNR=1.13, Formula2 SNR=3.20e-17
L=2.5Gm: Formula1 SNR=2.45e+02, Formula2 SNR=6.93e-15
L=3.0Gm: Formula1 SNR=3.52e+02, Formula2 SNR=9.98e-15
```

### 结论: **Formula1 (原始代码) 是正确的**

理由:
1. Allen (1987) 交叉相关标准框架使用噪声 PSD 的平方在分母
2. S_corr 是信号相关的 PSD (Hz⁻¹)，S_y 是频率偏移的 PSD (Hz⁻¹)
3. 交叉相关灵敏度的标准形式是 signal²/noise — 这里的 signal 和 noise 都是 PSD
4. Formula1 给出可探测的空间 OLC SNR (L=2.5Gm → SNR=245)，符合物理直觉
5. Formula2 给出所有臂长都不可探测，与空间 OLC 的理论优势矛盾

### 对 C2 "bug fix" 的影响

**C2 的"修正"是错误的，需要还原。** 原始代码 `scripts/03-olc-snr-solver.py` 的 SNR 公式是正确的。

### 核心科学结论

**空间 OLC 对 SGWB 是可探测的。**

对于 Ω_GW = 10⁻⁸, T_obs = 1yr:
- L = 0.17 Gm: SNR ≈ 1.1 (接近探测阈值)
- L = 2.5 Gm: SNR ≈ 245 ( Excellent detection)
- L = 3.0 Gm: SNR ≈ 352

SNR 随臂长的增长远超线性 — 主要因为 S_corr ∝ L² (GW 耦合) 且 S_corr² 带来 L⁴ 增强。

### 对论文框架的影响

论文框架 (论文框架-v1.md) 中关于空间 OLC 可探测的假设是**正确的**。
第 4 章噪声与 SNR 部分需要使用 Formula1 (S_y² 在分母)。
