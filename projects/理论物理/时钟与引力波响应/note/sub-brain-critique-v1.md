# Sub-Brain Critique — Paper Writing v1

> 创建时间: 2026-07-02
> 来源: Sub-Brain Agent (RALPH Loop 副脑)
> 类型: 质询 — 找盲区，问"为什么"

---

## Critique 1: SNR 尺度律 — 从 L=10m 到 L=2.5Gm 的推演

**问题**: SNR ∝ L² 还是 SNR ∝ L⁴？从 L=10m 到 L=2.5Gm 的尺度推演是否自洽？

**分析**:
- S_corr(f) = S_h · |T|²，而 |T|² ∝ (fL/c)² → **S_corr ∝ L²**
- dSNR²/df ∝ S_corr²/S_y² ∝ L⁴ → **SNR² ∝ L⁴ → SNR ∝ L²**

从 L = 10m 到 L = 2.5Gm (2.5×10⁸ m)，臂长增加因子 = 2.5×10⁸：
- SNR 增加因子 = (2.5×10⁸)² = 6.25×10¹⁶
- L=10m 的 SNR = 3.91×10⁻¹⁵ × 6.25×10¹⁶ = 244

这与 script 计算的 SNR = 245 **完全一致**。（微小的差异来自 S_y 在 L 不同时略有变化，以及数值积分的精度。）

**严重性**: 低 — 推演自洽。但**论文中关于 scaling 的描述有误**：
- memory/07-olc-detection-requirements.md 写 "SNR ∝ L²" — 正确（但解释模糊）
- memory/10-space-olc-snr-results.md 写 "S_corr ∝ L² (GW 耦合) 且 S_corr² 带来 L⁴ 增强" — 正确
- 论文第4.4节写 "SNR² ∝ L⁴" 和 "臂长增加 ~10⁸ 倍，SNR 放大超过 10³³ 倍" — **10³³ 是 SNR² 的放大，不是 SNR**

**建议**: 修正论文第4.4节中关于 SNR 放大因子的描述：
> "SNR 放大因子 = (2.5×10⁸)² = 6.25×10¹⁶（SNR ∝ L²）。"

---

## Critique 2: 比较脚本中 Formula2 为什么给出不可探测的 SNR

**问题**: Formula2 使用 S_y（非平方）在分母，给出 L=2.5Gm 时 SNR=7×10⁻¹⁵。为什么与 Formula1 相差 30 个数量级？

**分析**: 
- Formula1: dSNR²/df ∝ S_corr²/S_y² → S_corr²/S_y² 是无量纲的
- Formula2: dSNR²/df ∝ S_corr²/S_y → S_corr²/S_y 的量纲是 Hz⁻¹

虽然 Dimensional Analysis 上两者都可以给出无量纲的 SNR²（因为 ∫df 消去了 Hz⁻¹），但 **Formula2 的物理基础不牢**：
- Allen (1987) 的标准交叉相关公式中，分母是噪声 PSD 的乘积（即 S_y²）
- Formula2 对应的是 S_y^{1/2}，这在物理上对应什么？没有明确的文献支持

**严重性**: 低 — Formula1 的物理基础更坚实，且有 Allen (1987) 的支持。

---

## Critique 3: Gravitational Redshift 效应对空间 OLC 的影响

**问题**: 论文完全忽略了 Gravitational Redshift (GR) 效应对空间 OLC GW 探测的影响。Schatt 等人（2022, PRL 129, 161301）证明，对于基于原子能级跃迁的时钟，最主要的 GW 耦合机制是 **GR 效应**（引力红移），而非 direct Doppler 效应。

**分析**:
- GR 效应给出的 GW 响应为 Δf/f ≈ h · (f_gw/c) · L · sin²(θ/2)
- 与 direct Doppler 相比，GR 效应在某些几何构型下可能占主导
- Schatt 的论文指出，对于 clock-based 探测器，GR 效应在所有频率下都是主要的

**严重性**: **高** — 如果 GR 效应是主要的 GW 耦合机制，那么：
1. 论文的响应公式可能不完整
2. GR 效应的频率依赖性与 Doppler 效应不同（不依赖于 f，只依赖于方向）
3. 这可能改变 ORF 的计算结果

**建议**: 增加一节讨论 GR 效应与 Doppler 效应的相对贡献。参考文献：
- Y. Yu et al., "Gravitational redshift and gravitational-wave detectors", Phys. Rev. D 106, L111501 (2022)
- N. Schaffrath et al., "Fundamental limits of quantum sensors for gravitational wave detection", PRX Quantum 3, 040333 (2022)

---

## Critique 4: Ganapathy 2026 的协同观测框架引用

**问题**: 论文中引用 Ganapathy et al. (2026, arXiv:2606.01516) 作为协同观测的"金标准"，但具体引用他们的什么结果？arXiv ID 是否足以确定论文内容？

**分析**:
- arXiv:2606.01516 是 2026 年 6 月上传的新论文
- 论文的标题、作者列表、摘要都需要确认
- 如果这篇论文还没有经过 peer review，引用时需要注明 "preprint"

**严重性**: 低 — 在学术论文中引用 preprint 是常见的，但需要注明。建议添加 "(preprint)" 标记。

---

## Critique 5: 混合网络独立求和的物理基础

**问题**: 论文提出 ρ²_mixed = ρ²_OLC + ρ²_LISA，理由是"不同探测器测量不同物理量"。但 OLC 的频率偏移和 LISA 的应变本质上都是无量纲的 h 的测量。交叉相关项是否可以定义？

**分析**:
- OLC 测量的 Δf/f ∝ h · (2πfL/c) — 与 f 线性相关
- LISA 测量的 h — 直接测量应变
- 两者对同一 GW 信号的响应不同，但**物理量本质上是相关的**（都正比于 h）
- 因此，**混合网络的交叉相关项在理论上是可以定义的**，只是需要统一的响应函数

**严重性**: 中 — 保守估计（忽略交叉相关）是合理的，但应该说明：
> "在保守估计下，我们忽略 OLC 与 LISA 之间的交叉相关项，仅通过独立求和合并 SNR。更精确的处理需要建立统一的响应函数框架。"

**建议**: 在论文第5.2节增加一段说明，承认更精确的处理是可能的，但在当前框架下选择保守估计。

---

## Critique 6: 论文完整性检查

**问题**: 论文框架 (论文框架-v1.md) 和实际撰写 (论文-第*-*.md) 之间有哪些差异？

**分析**:
1. **框架第3章** 提到了"机构信息修正" — **已包含**在论文第3章
2. **框架第4章** 提到 "C2 bug 修正" — **已在 SNR 公式中体现**
3. **框架第5章** 提到 Ganapathy 2026 — **已包含**
4. **框架第6章** 的 Taiji/TianQin 参数 — **论文中仅列了名字，没有具体数值**
5. **附录D** 的脚本说明 — **已包含**
6. **英文标题和摘要** — **尚未撰写**

**严重性**: 中 — 英文标题和摘要是 arXiv 提交必需的。Taiji/TianQin 的具体参数应该补充。

**建议**: 
1. 撰写英文标题和摘要
2. 补充 Taiji/TianQin 的具体数值

---

## 总结

| 编号 | 问题 | 严重性 | 建议 |
|------|------|--------|------|
| 1 | SNR 尺度律描述有误 | 低 | 修正第4.4节 |
| 2 | Formula2 物理基础薄弱 | 低 | 已在论文中正确排除 |
| 3 | GR 效应被忽略 | **高** | 增加讨论或引用 |
| 4 | Ganapathy preprint 引用 | 低 | 标注 "preprint" |
| 5 | 混合网络交叉相关省略 | 中 | 说明这是保守估计 |
| 6 | 英文摘要缺失 | 中 | 补写英文标题+摘要 |
