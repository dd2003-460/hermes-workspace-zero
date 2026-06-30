# Branch A Report: ε convention correction

> Date: 2026-04-01 09:30
> Script: `scripts/branch_A_corrected.py`

## Finding

脚本用 ε^{abc}（ε^{012}=-1），但论文 EOM 用 ε_{abc}（ε_{012}=+1）。
对于反角 η = antidiag(1,1,0;1,0,0;0,0,1)：**ε_{abc} = -ε^{abc}**（差负号）。

## Results (corrected ε_{abc})

| EOM | Ingoing | Outgoing |
|-----|---------|----------|
| EOM1 R^a=0 | ✅ PASS | ✅ PASS |
| EOM2 T^a+ε_{abc}σ^b∧e^c=0 | ❌ {(0,1): -2r/ℓ², (1,2): -2} | ✅ PASS |
| EOM3 F^a+(1/2ℓ²)ε_{abc}e^b∧e^c=0 | ❌ {(1,2): 2r/ℓ², (0,2): r(M+b-r²/ℓ²)/ℓ²} | ❌ {(0,2): r(M+b-r²/ℓ²)/ℓ⁴} |

## Key Progress

- **EOM2 outgoing 全部通过** ✅ ← 这是重大进展！原来用错 ε 符号导致出射 frame 全部失败。
- EOM2 ingoing 仍失败，但模式不同了（不再是所有组合都 fail）
- EOM3 两个 frame 都还剩一个共同残差 (0,2): r(M+b-r²/ℓ²)/ℓ⁴

## Analysis

EOM3 的 (0,2) 残差 = r(ℓ²(M+b) - r²)/ℓ⁴。这与 κ⁰ 的 dφ 系数 (r²/ℓ² - M - b)/2 有关。如果 σ ≠ -κ 而是某个修正版本，这个残差可能被消除。

EOM2 ingoing 的残差 -2r/ℓ² in (dv,dr) 和 -2 in (dr,dφ) 提示可能存在标架/度规的符号约定差异（ingoing vs outgoing 的 dr 符号）。

## Next

- Branch B: 双对偶联络变换
- 如果 Branch B 不能解释剩余残差 → 可能需要修正 σ ≠ -κ 的假设
