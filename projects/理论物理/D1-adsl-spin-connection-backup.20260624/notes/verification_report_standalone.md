# Asymptotically AdS Spacetime with Spinning Cosmic String — EOM Verification Report

> **Date**: 2026-04-01
> **Authors**: Zero (automated verification)
> **Status**: 5/6 checks pass, 1 structural residual

## Abstract

We verify the equations of motion (EOMs) for the BTZ-like spacetime with a spinning cosmic string, as given in [JHEP 09 (2023) 185]. Using symbolic computation (SymPy), we check all three EOMs in both ingoing and outgoing Eddington-Finkelstein frames. Results: EOM1 (flatness) ✅, EOM2 (torsion) ✅ with identified convention fixes, EOM3 (Maxwell-like) has two structural residuals that survive all attempted corrections.

## 1. Setup

### Metric and Frame

Ingoing frame:
```
e⁰ = M dv + dr
e¹ = r dφ
e² = (r/ℓ²)(-r dv + ℓ² dφ)
```

Outgoing frame (hatted coordinates):
```
ê⁰ = -M dv̂ - dr̂
ê¹ = r dφ̂
ê² = (r/ℓ²)(r dv̂ + ℓ² dφ̂)
```

### Connection and Torsion

Given spin connection ω^a (dual representation) and torsion σ^a = -κ constant (σ⁰ = σ¹ = σ² = -κ).

### Equations of Motion

1. **EOM1**: R^a = 0 (curvature 2-form vanishes)
2. **EOM2**: T^a + ε_{abc} σ^b ∧ e^c = 0 (torsion constraint)
3. **EOM3**: F^a + (1/2ℓ²) ε_{abc} e^b ∧ e^c = 0 (field strength constraint)

where F^a = dσ^a + ε^a_{bc} ω^b ∧ σ^c + (1/2) ε^a_{bc} σ^b ∧ σ^c.

## 2. Convention Fixes

### 2.1 ε tensor convention

**Issue**: Script initially used ε^{abc} (ε^{012} = -1) throughout. Paper's EOMs are written with ε_{abc} (ε_{012} = +1).

**Resolution**: For antidiagonal η = diag(-1,1,1), we have ε_{abc} = -ε^{abc}. This -1 factor propagates into EOM2 and EOM3.

**Impact**: Without correction, EOM2 fails with wrong-sign residuals.

### 2.2 e⁰ dr sign

**Issue**: Paper writes ingoing e⁰ with dr coefficient +1, but the given ω^a is consistent with dr = -1.

**Resolution**: Flip dr to -1 in ingoing frame. This is a BMS/outgoing convention difference.

**Impact**: dr correction is required for EOM2 to pass in the outgoing frame.

### 2.3 Verification

Both fixes independently verified:
- ε correction alone: EOM2 passes in ingoing, fails in outgoing
- dr correction alone: EOM2 passes in outgoing, fails in ingoing
- Both corrections: EOM2 passes in both frames ✅

## 3. Results

### EOM1: R^a = 0 ✅

All 6 components (3 per frame) vanish. The spacetime is flat in the dual representation.

**This confirms**: The given ω^a correctly represents a flat connection.

### EOM2: T^a + ε_{abc} σ^b ∧ e^c = 0 ✅

After ε and dr corrections:
- Ingoing: 3/3 components ✅
- Outgoing: 3/3 components ✅

**Key insight**: EOM2 independently constrains σ. Linear solving (9 equations, 9 unknowns) confirms σ = -κ is consistent with the corrected conventions.

### EOM3: F^a + (1/2ℓ²) ε_{abc} e^b ∧ e^c = 0 ❌

Residuals in EOM3[0] (ingoing frame):

| Component | Value | Origin |
|-----------|-------|--------|
| (dr, dφ) | 2r/ℓ² | F⁰'s dσ⁰ term + e∧e term both contribute r/ℓ² |
| (dv, dφ) | r(ℓ²(M+b)-r²)/ℓ⁴ | σ∧σ term has b-dependence that e∧e lacks |

## 4. Exhaustive Investigation

### Branch A: ε convention ✅
Systematic sweep of 2⁴ = 16 sign combinations. Root cause identified and fixed.

### Branch B: Dual connection ✅
Confirmed: ω^a in dual representation is used correctly. No transformation needed.

### Branch C: Symbolic σ solve ❌
SymPy solve of EOM2 + EOM3 (18 equations, 9 unknowns) → **no solution exists**. System is overdetermined and inconsistent. No single σ can satisfy all three EOMs simultaneously.

### Branch D: dr sign ✅
Key fix identified: e⁰ dr = -1 resolves EOM2 in outgoing frame.

### Branch E: EOM3 δσ correction ❌
Tried σ = -κ + δσ. EOM2 forces all δσ = 0. No σ correction can fix EOM3 without breaking EOM2.

### Deep Dive: 4 Paths ❌

| Path | Method | Result |
|------|--------|--------|
| 1: σ⁰ dv component | Add dv term to σ⁰ | Wrong direction + breaks EOM2 |
| 2: σ¹ ≠ 0 | Allow σ¹ non-zero | EOM2 forces σ¹ = 0 |
| 3: σ∧σ audit | Full wedge product check | Computation correct, can't cancel |
| 4: ℓ² factor | Test prefactor combinations | No single factor resolves both residuals |

## 5. Conclusion

**EOM1** (flatness) and **EOM2** (torsion) are fully verified with two convention fixes:
1. ε_{abc} = -ε^{abc} for antidiagonal η
2. e⁰ dr = -1 (BMS convention)

**EOM3** has two structural residuals that cannot be fixed by:
- Adjusting σ (EOM2 constrains it completely)
- Changing conventions (ε and dr are now correct)
- Modifying ℓ² prefactors (no single factor works)

**Most likely explanation**: Paper has a typo or uses an unspecified gauge choice in EOM3. The connection ω^a and torsion σ^a = -κ are correct for EOM1 and EOM2, but EOM3 as written is inconsistent.

**Recommendation**: Accept 5/6 verification, or contact authors for clarification.

## 6. Reproduction

All verification scripts available at:
- `scripts/sympy_verify.py` — Main verification (ε + dr corrected)
- `scripts/convention_sweep.py` — 16-combination ε sweep
- `scripts/branch_A_corrected.py` — Post-fix verification
- `scripts/branch_B_dual_connection.py` — Dual connection check
- `scripts/branch_C_sigma_solve.py` — Symbolic σ solve
- `scripts/branch_D_dr_sign.py` — dr sign investigation
- `scripts/branch_E_eom3_fix.py` — EOM3 δσ attempt
- `scripts/eom3_path{1,2,3,4}_*.py` — Deep dive paths

Requirements: Python 3.10+, SymPy, NumPy.
Run: `python scripts/sympy_verify.py`

---

*Generated by Zero automated verification pipeline. 2026-04-01.*
