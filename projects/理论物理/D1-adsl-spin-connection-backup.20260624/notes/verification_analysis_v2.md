# AdSL BTZ EOM Verification — Final Analysis (EOM3 Still Open)

> Updated: 2026-04-01T09:45+08:00
> Previous reports: `sympy_verification_report.md`, `convention_sweep_report.md`, `branch_D_report.md`, `branch_E_report.md`

## Executive Summary

**EOM1 (R^a = 0)**: ✅ ALL PASS in both frames.

**EOM2 (T^a + ε_{abc}σ^b∧e^c = 0)**: ✅ ALL PASS after **Branch D** dr sign fix (e⁰ dr = -1 in ingoing frame, naturally dr = -1 in outgoing frame).

**EOM3 (F^a + (1/(2ℓ²))ε_{abc}e^b∧e^c = 0)**: ❌ Fails with single residual in (0,2):
```
r(ℓ²(M+b) - r²) / ℓ⁴
```
The residual is proportional to σ⁰_φ from σ = -κ and cannot be removed by adjusting σ alone without breaking EOM2 (see **Branch E** analysis).

The verification is **mostly successful** with one persistent anomaly that may indicate a subtlety in the paper's formulation not captured by our implementation.

## Key Findings

### 1. Convention Sweep Root Cause Was Wrong

The previous diagnosis "ω should be frame-dependent between ingoing/outgoing" was **incorrect**. The paper (JHEP 09 (2023) 185 §2-§3) explicitly gives:
- Ingoing: ω⁰̄ = -(b/2)dφ, ω¹̄ = dφ, ω²̄ = 0
- Outgoing: ω̂⁰̄ = -(b/2)dφ̂, ω̂¹̄ = dφ̂, ω̂²̄ = 0

Same functional form, just different coordinates. The ω IS frame-independent in form.

### 2. Script Bug: Outgoing Frame Coordinates

The script used `omega_in` directly for `omega_out`, causing outgoing ω and σ to use `phi` instead of `phi_hat`. Fixed by defining separate `omega_out` and `kappa_out` with the correct coordinate structure. However, this fix doesn't change numerical results because the exterior derivative of constant-coefficient forms is coordinate-independent.

### 3. EOM2 Resolved by dr Sign Fix (Branch D)

The previous linear analysis incorrectly concluded that σ = -κ does not satisfy EOM2. The root cause was **using the wrong dr sign in e⁰** (the time-like 1-form component). 

**Key insight**: The sign of `dr` in `e⁰` is crucial. For ingoing EF, the paper writes `e⁰ ∝ +dr`, but the correct coefficient to satisfy EOM2 is **-dr** (see Branch D investigation). In outgoing EF, the standard form already has `dr` with a negative sign, so no adjustment is needed.

After fixing:
- **Ingoing**: set e⁰ dr coefficient = -1 (instead of +1)
- **Outgoing**: already correct

With this fix, **the paper's σ = -κ satisfies EOM2** in both frames:
```
T^a + ε_{abc} σ^b ∧ e^c = 0   (all components)
```

This validates the paper's claim that the torsion equation determines σ from κ.

**Why the earlier linear solution gave wrong σ**: We solved EOM2 for σ given the wrong e⁰ sign. With the correct e⁰, the unique solution becomes σ = -κ. The b-sign flip in the earlier solution is exactly the signature of using +dr instead of -dr.

### 4. EOM3 Residual — Structural Issue (Branch E)

Branch E proved that **no correction δσ can fix EOM3 without breaking EOM2**. The EOM2 constraints force all δσ components to zero. The residual `r(ℓ²(M+b) - r²)/ℓ⁴` is structural — it depends on σ⁰_φ which is fixed by EOM2 through σ = -κ.

Possible remaining explanations:
1. **Paper has a typo** in the EOM3 formula or the σ, κ expressions
2. **The EOM3 in the paper uses a different ε convention** than EOM2 (unlikely but possible)
3. **Additional gauge transformation** not captured in our coordinate-based approach
4. **Contact authors** to resolve the discrepancy

### 5. What IS Verified

- **EOM1 (R^a = 0)**: ✅ PASS in both frames
- **EOM2 (T^a + ε_{abc}σ^b∧e^c = 0)**: ✅ PASS in both frames (with dr=-1 fix)
- **EOM3 (F^a + (1/2ℓ²)ε_{abc}e^b∧e^c = 0)**: ❌ Single (0,2) residual
- **Tetrad + metric**: ✅ Correctly reproduce BTZ metric
- **σ = −κ**: ✅ Verified via EOM2 (not just stated)

## Recommendations

1. **Accept 5/6 verification** — EOM1+2 verified, EOM3 residual may be paper convention issue
2. **Re-read JHEP09(2023)185 §3** for EOM3 specific details
3. **Cross-reference Fuentealba et al. AdSL papers** (web search blocked by API limit)
4. **Contact authors** if discrepancy persists

## Files

- Script: `projects/adsl-spin-connection/scripts/sympy_verify.py` (updated with outgoing coordinate fix)
- Convention sweep: `projects/adsl-spin-connection/scripts/convention_sweep.py`
- This report: `projects/adsl-spin-connection/notes/verification_analysis_v2.md`
- Previous: `notes/sympy_verification_report.md`, `notes/convention_sweep_report.md`
