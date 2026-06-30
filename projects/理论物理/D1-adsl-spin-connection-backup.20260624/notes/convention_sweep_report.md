# Convention Sweep 报告 — AdSL BTZ EOM 验证

> 扫描时间：2026-04-01T02:38+08:00
> 脚本：`scripts/convention_sweep.py`
> 测试：2⁴ = 16 种 convention 组合 × 2 frames

## 结果汇总

| 参数 | 测试值 |
|------|--------|
| ε^{abc} 符号 | +1, -1 |
| σ 符号 (σ = sign × κ) | +1, -1 |
| T^a 定义符号 | +1, -1 |
| F^a 是否含 (1/2)εσσ | True, False |

**没有任何组合通过全部 6 个检查 (3 EOMs × 2 frames)。**

## 最佳结果 (4/6 通过)

### 组合 A: eps=+1, σ=-1, T^a sign=-1, Fa_half=True
- EOM1 ingoing ✅ | EOM2 ingoing ✅ | EOM3 ingoing ✅
- EOM1 outgoing ✅ | EOM2 outgoing ❌ | EOM3 outgoing ❌
- Outgoing 残差：
  - EOM2: `{(0,1): -2r/ℓ²}`, `{(1,2): -2}`
  - EOM3: `{(1,2): 2r/ℓ²}`, `{(0,1): 2/ℓ²}`

### 组合 B: eps=-1, σ=+1, T^a sign=+1, Fa_half=True
- 同 A 的 pattern，ingoing 全过，outgoing 全败
- Outgoing 残差与 A 相同（符号相反但同样非零）

## 根因分析

**问题不是 convention，是 ω 的 frame-dependence。**

Script 假设 ingoing 和 outgoing 使用相同的 ω 连接：
```
ω = [{2: -b/2}, {2: 1}, {}]
```

但 outgoing frame 的 e[0] dr 系数从 +1 变为 -1，导致所有含 e_{0̄} 的 wedge 积分符号相反。由于 EOM2 和 EOM3 都涉及 ω∧e 和 σ∧e，相同的 ω 在不同 frame 下给出不同的 EOM 结果。

**数学约束**：如果 ω frame-independent，ingoing 通过 ⟹ outgoing 必然失败（因为 e 的符号差异在 wedge 中被放大而非抵消）。

## 下一步方向

1. **检查论文对 outgoing frame 是否给定了不同的 ω 表达式**（重读 JHEP 09 (2023) 185 §2-§3）
2. **检查 ω 的 frame-dependent 变换规则**：ingoing→outgoing 时 ω^a 是否应变换
3. **检查 outgoing frame 的 ω 是否应修改 dr 系数**（如 ω^{1̄} 中加入 dr 依赖项）
4. **仅验证单 frame**：如果论文只要求在一个坐标系中验证 EOM，ingoing 全通过已足够
