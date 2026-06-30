# Branch D Report: dr sign investigation

> Date: 2026-04-01 09:37

## Key Finding

**e⁰ 的 dr 符号决定了 EOM2 是否通过。**

| Test | e⁰ dr | EOM1 | EOM2 | EOM3 |
|------|-------|------|------|------|
| Ingoing standard | +1 | ✅ | ❌ | ❌ |
| Ingoing dr=-1 | -1 | ✅ | **✅ ALL PASS** | ❌ (0,2) only |
| Outgoing standard | -1 | ✅ | **✅ ALL PASS** | ❌ (0,2) only |

当 e⁰ 使用 dr=-1 时，EOM2 在所有 frame 都通过。这意味着：
- 论文给的 ω 适用于 e⁰ 的 dr 系数为 -1 的 frame
- 但论文 ingoing EF 给的 e⁰ 写的是 +dr

## EOM3 Residual

无论哪个 frame、哪个 dr 符号，EOM3[0] 都有相同的 (0,2) 残差：
`r(ℓ²(M+b) - r²)/ℓ⁴`

这与 σ⁰_φ = (M+b-r²/ℓ²)/2 成正比。可能的修正：
- σ⁰ 的 dφ 系数需要调整（但会破坏 EOM2）
- σ¹ 需要非零 dv 项
- σ∧σ 项贡献未被正确处理

## Progress Score

| EOM | Status |
|-----|--------|
| EOM1 R^a=0 | ✅ ALL PASS (both frames) |
| EOM2 T+εσe=0 | ✅ ALL PASS (with dr=-1 fix) |
| EOM3 F+(1/2ℓ²)εee=0 | ❌ Single residual in (0,2) |

**从全部失败 → 仅剩一个残差。** 大幅进展。
