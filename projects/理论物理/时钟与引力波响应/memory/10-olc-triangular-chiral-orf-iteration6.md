---
name: 10-olc-triangular-chiral-orf-iteration6
description: Iteration 6 triangular OLC chiral ORF results — all configurations give Gamma^V ≈ 0
metadata:
  type: project
---

# Iteration 6: Triangular 3-Satellite OLC Chiral ORF

## Result: Chiral ORF = Zero for ALL configurations

### Numerical Results

| Configuration | <Gamma^I> | |Gamma^V| | Pass? |
|--------------|-----------|----------|-------|
| Equilateral | -0.230 | 7.79e-20 | ❌ |
| Right triangle | -0.230 | 7.79e-20 | ❌ |
| Degenerate line | -0.230 | 7.79e-20 | ❌ |

Standard ORF is correctly nonzero (-0.23), confirming the code computes antenna patterns correctly.

### Frequency Scan (Non-Coplanar Single-Arm Pairs)

| f (mHz) | |Gamma^V| | <Gamma^I> |
|---------|----------|----------|
| 0.1 | 2.4e-14 | 0.50 |
| 0.3 | 5.7e-12 | 0.50 |
| 1.0 | 2.4e-9 | 0.50 |
| 3.0 | 5.7e-7 | 0.50 |
| 10.0 | 2.3e-4 | 0.51 |
| 30.0 | **0.041** | 0.54 |
| 100.0 | 1.07 | 0.47 |

**Key insight**: Single-arm non-coplanar OLC achieves |Gamma^V| > 1e-3 at f > 10 mHz, reaching ~0.04 at 30 mHz.

### Michelson-like Combination: EXACT ZERO at all frequencies

| f (mHz) | |Gamma^V| |
|---------|----------|
| 0.1 | 4.6e-22 |
| 0.3 | 1.8e-21 |
| 1.0 | 8.6e-21 |
| 3.0 | 1.1e-19 |
| 10.0 | 4.9e-18 |
| 30.0 | 6.2e-17 |
| 100.0 | 9.2e-16 |

**Why**: For any Michelson variable M = link(a) + link(b), the effective responses satisfy:
- R_+^M(a) = R_+^M(b) and R_×^M(a) = R_×^M(b)
- This makes the chiral factor identically zero

## Physical Conclusion

1. **Single-arm OLC**: negligible chiral sensitivity at f < 10 mHz. At f > 30 mHz, non-coplanar pairs achieve |Gamma^V| ~ 0.04.

2. **Michelson-like OLC**: zero chiral sensitivity at ALL frequencies due to the proportional relationship between R_+ and R_× responses.

3. **Triangular OLC constellation**: cannot detect chiral SGWB using Michelson-like variables. The claim "|Gamma^V| ~ 0.3" in the paper draft is **incorrect** and needs to be revised.

4. **The standard ORF works correctly**: <Gamma^I> = -0.23 for equilateral triangle (consistent with known PTA LISA results).

## Code Location

`scripts/10-olc-chiral-orf-triangular.py` — implements triangular OLC chiral ORF with Michelson-like variables.

## Related

- Iteration 5: single-arm OLC chiral ORF = 0 (09-olc-chiral-orf.py)
- This iteration: Michelson-like OLC chiral ORF = 0 (10-olc-chiral-orf-triangular.py)
- Both single-arm and Michelson-like OLC have zero chiral sensitivity
- Need to explore: different observable (not Michelson), multiple constellations, or different combination
