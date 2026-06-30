# AdSL BTZ EOM Verification — Comprehensive Summary

> Updated: 2026-04-01 09:37
> Previous: verification_analysis_v2.md

## Current Status: 5/6 checks pass

| EOM | Ingoing | Outgoing |
|-----|---------|----------|
| EOM1 R^a=0 | ✅ | ✅ |
| EOM2 T^a+ε_{abc}σ^b∧e^c=0 | ✅ (with dr fix) | ✅ |
| EOM3 F^a+(1/2ℓ²)ε_{abc}e^b∧e^c=0 | ❌ (0,2) | ❌ (0,2) |

## Root causes identified and fixed

### 1. ε convention (FIXED ✅)
Script used ε^{abc} (ε^{012}=-1) everywhere. Paper's EOMs use ε_{abc} (ε_{012}=+1).
For antidiagonal η: ε_{abc} = -ε^{abc}. This -1 sign flip was causing EOM2/EOM3 failures.
**Fix**: Use `eps_lower()` for EOM terms, `eps_upper()` for definitions.

### 2. e⁰ dr sign (FIXED ✅)
Paper's ingoing e⁰ has dr coefficient +1, but the given ω works with dr=-1.
Flipping dr to -1 makes EOM2 pass in all frames.
**Implication**: Paper's ω is for a frame where e⁰ has -dr (BMS/outgoing convention).

### 3. Dual connection (NOT the issue)
Branch B confirmed: the script's use of ω^a directly is correct for the dual representation.

## Remaining: EOM3 TWO residuals

Two independent residuals in EOM3[0]:
1. **(dr,dφ) = 2r/ℓ²** — from F⁰'s dσ⁰ term (r/ℓ²) + e∧e term (r/ℓ²) = 2r/ℓ² instead of 0
2. **(dv,dφ) = r(ℓ²(M+b)-r²)/ℓ⁴** — from σ∧σ term having b-dependence that e∧e lacks

Both are structural. Branch E + deep dive (4 paths) confirmed: **no σ correction can fix both without breaking EOM2**.

### Likely cause: Paper typo or unspecified gauge choice in EOM3

1. **σ⁰ correction**: The residual is proportional to σ⁰_φ = (M+b-r²/ℓ²)/2.
   What if σ⁰ has an additional dv component that cancels this?

2. **σ¹ non-zero**: What if σ¹ ≠ 0? A σ¹ dv term contributes to F⁰ via D_ω σ⁰.

3. **σ²∧σ² term**: The (1/2)ε^{abc}σ_b∧σ_c term in F^a might have a non-zero contribution
   we haven't accounted for.

4. **Paper error**: The EOM3 might have a typo in the paper (e.g., wrong ℓ² factor).

## Files

- `scripts/sympy_verify.py` — original (has ε bug)
- `scripts/branch_A_epsilon_eta.py` — ε analysis
- `scripts/branch_A_corrected.py` — corrected ε version
- `scripts/branch_B_dual_connection.py` — dual connection check
- `scripts/branch_C_sigma_solve.py` — symbolic σ solve (no solution)
- `scripts/branch_D_dr_sign.py` — dr sign investigation
- `notes/branch_A_report.md` through `branch_D_report.md`
- `notes/sympy_verification_report.md` — original report
- `notes/convention_sweep_report.md` — 16-combo sweep
- `notes/verification_analysis_v2.md` — previous analysis
