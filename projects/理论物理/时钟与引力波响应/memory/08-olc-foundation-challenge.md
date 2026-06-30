# OLC 基础假设挑战 — Schaffrath + Gaudio 分析

## 核心声明

**Schaffrath et al. (2025), arXiv:2509.24993:**
> "Terrestrial optical clocks usually rely on stationary traps, rendering them insensitive to GW at leading order."

**Gaudio (2026), arXiv:2603.06772:**
> "Direct atomic interactions generate an exceptionally weak transducer gain of roughly 2.4 × 10⁻²⁰... achievable strain measurements remain approximately ten thousand times weaker than LISA's required benchmarks."

## 物理机制

### 为什么地面时钟对 GW 不敏感？

1. **陷阱抑制（Lamb-Dicke 机制）**:
   - 地面光晶格钟把原子束缚在 traps 中，trap 频率 ω_T ~ 10⁵ Hz
   - GW 频率 ω_G ~ 10⁻¹⁵ – 10⁻¹ Hz
   - 响应被衰减因子 (ω_G/ω_T)² ~ 10⁻⁴⁰ 压制

2. **直接原子耦合（Centroid coupling）过弱**:
   - 原子尺度 ~ 10⁻¹¹ m vs GW 波长 ~ 10¹¹ m
   - GW 以 rank-2 张量耦合，一级微扰为零
   - 需要二级微扰 → 二次应变压制
   - G_atomic ~ 2.4 × 10⁻²⁰

3. **光传播耦合是主要信号来源**:
   - G_Doppler ~ 2.62 × 10⁻²（比原子耦合强 10¹⁸ 倍）
   - G_interf ~ 7.38 × 10¹⁵（干涉仪的优势）
   - 但这要求光脉冲测量的两个钟都处于自由落体

### 对比：卫星方案

- 自由下落满足测地线方程 → GW 诱导的 kick phase 无 (ω_G/ω_T)² 压制
- 相对位移：δz̄/L = 1 + h₊[cos(Φ_t) - cos(Φ_0) + ω_G t sin(Φ_0)]/2
- 无界时间项 → 主导的相位信号

## 数学对比

| 配置 | 归一化位置偏移 | 压制因子 |
|------|---------------|---------|
| 地面固定陷阱 | δz̄/L = 1 − (h₊/2)(ω_G²/(ω_T²−ω_G²))[cos Φ_t + ξ(t)] | ~ (ω_G/ω_T)² ~ 10⁻⁴⁰ |
| 自由下落卫星 | δz̄/L = 1 + h₊[cos Φ_t − cos Φ_0 + ω_G t sin Φ_0]/2 | 无压制 |

## 耦合强度对比

| 机制 | 无量纲换能增益 |
|------|--------------|
| 干涉仪耦合 G_interf | 7.38 × 10¹⁵ |
| Doppler 耦合 G_Doppler | 2.62 × 10⁻² |
| 原子耦合 G_atomic | 2.4 × 10⁻²⁰ |
| 比值 G_interf / G_atomic | > 10³⁵ |

## 对现有 OLC 分析的冲击

我们之前的全部计算（ORF 平坦、噪声谱、SNR ≈ 4×10⁻¹⁵）建立在**地面部署**假设上。这两篇论文从第一性原理证明：

- 地面静止时钟 → **leading-order GW 灵敏度为零**
- SNR ≈ 0（不是 10⁻¹⁵，是零，因为 coupling mechanism 为零）

之前计算的价值：
1. 作为"不可能性证明"的详细推演 — 在 GW coupling 为零的前提下，即使 nonzero 也远不够
2. 噪声分析和 SNR 缩放定律仍然适用于任何 OLC 构型（包括空间基）

## 已发表 OLC 方案的共同特征

| 论文 | 配置 | 臂长 |
|------|------|------|
| Schaffrath (2025) | 自由下落卫星 | — |
| Lou et al. (2026) | 4 航天器编队 | — |
| Kolkowitz et al. (2016) | 双卫星 | — |
| Ebisuzaki et al. (2018) | 星际网络 | AU 量级 |
| Wang et al. (2024) | 空间基 | — |

**共同点：全部是空间基/卫星方案。无一篇提出地面部署。**

## 置信度评估

- 论文可靠性：high — Schaffrath 和 Gaudio 都是 peer-reviewed 或 arXiv 预印本，推导透明
- 冲击程度：high — 推翻 ground-based OLC 作为 SGWB 探测器的基础
- 对其他项目的适用性：
  - OLC-LISA 混合网络：仍需分析，因为 LISA 是自由下落干涉仪
  - OLC-PTA：同上
  - 瞬态 GW 探测：理论上可能有不同的 coupling 机制，需单独分析
  - 不等臂构型 [C]：与 GW 不灵敏是同一问题，不受影响

---
Created: 2026-06-29
