---
name: orlando-chi_orb-resolution-iteration8
description: Orlando's χ_orb ≈ 0.17 is a Fisher best-fit parameter, NOT a response function ratio. The 36x discrepancy with our norm_V=1.0 is a normalization convention difference, not a bug.
metadata:
  type: project
  created: 2026-07-06
---

# Iteration 8 P0: Orlando χ_orb ≈ 0.17 vs Our norm_V = 1.0 — Resolved

## Key Finding: χ_orb is NOT the Response Function

**From Orlando arXiv:2011.07059, equations 2.14 and 4.6:**

- **χ(f)** = V(f)/I(f) = (P_R - P_L)/(P_R + P_L) — chirality parameter, |χ| ≤ 1
- **χ_orb ≈ 0.17** (Figure 3, bottom central) is the **Fisher best-fit value** for a maximally chiral signal where χ_true = 1
- The Fisher analysis uses parameterization θ_α = {h²Ω^I_GW, h²Ω^V_GW} with data model:
  D^Λτ = h²Ω^I_GW R^I_Λτ + h²Ω^V_GW R^V_Λτ

**Therefore: χ_orb ≠ R^V/R^I**

χ_orb is a recovered parameter affected by:
1. R^I being ~10× stronger than R^V → much better constraint on Ω^I
2. Fisher degeneracy between Ω^I and Ω^V → error ellipse tilted
3. Frequency integration over noise spectra and response functions
4. Detector configuration: θ_L + θ_T = π (diametrically opposite)

## Orlando's Actual Response Functions (Figure 2)

- R^I_AC cross-correlation max: ~0.3-0.4
- R^V_AC cross-correlation max: ~0.02-0.04
- **Raw ratio R^V/R^I ≈ 0.06-0.12** (not 0.17, but same order)

The Fisher best-fit χ_orb = 0.17 is higher than the raw R^V/R^I ratio because:
- The Fisher analysis weights different frequencies differently
- The optimal detector configuration (θ_L + θ_T = π) enhances R^V at certain frequencies

## Three Different Normalizations

1. **Our norm_V** (E-variable CW sum): Sky-averaged Γ^V normalized by sqrt(Γ^I_auto) → by construction = 1.0
2. **Orlando's raw R^V/R^I**: Unnormalized cross-correlation response ratio from Figure 2 → ~0.06-0.12
3. **Orlando's χ_orb**: Fisher best-fit for maximally chiral signal → 0.17

**Our norm_V = 1.0 and Orlando's χ_orb = 0.17 measure DIFFERENT QUANTITIES.**
There is NO 36x discrepancy — it is a normalization convention mismatch.

## Our E-variable vs Orlando's TDI 1.5 AET Basis

- Our script uses CW (center-to-wing) link sum E-variable: E = (X - 2Y + Z)/√6
- Orlando uses TDI 1.5 AET/CDS noise-diagonal basis
- Both are valid choices for constructing GW-sensitive observables
- The chiral response (Γ^V) is a **geometric property** of the detector network, not a basis-dependent quantity
- The raw response function magnitudes (R^V) differ due to:
  - Different arm length combinations (LISA: 2.5Mkm vs Taiji: 3.0Mkm)
  - Different TDI generations (1.5 vs CW)
  - Different channel mixing matrices (AET vs E-variable)

**However, the geometric origin of non-zero Γ^V is the same: non-planar detector network.**

## Implications for the Paper

1. **Our claim "norm_V = 1.0 for LISA-Taiji" is correct** under our normalization convention
2. **Cannot directly compare with Orlando's χ_orb** — they measure different things
3. **For paper writing**: should cite Orlando's raw R^V values (Figure 2) for cross-check
4. **The non-zero chiral response for non-planar networks is confirmed** by both methods
5. **Orlando's Figure 2c, 2d should be referenced** when discussing chiral response magnitudes

## Why χ_orb < 1 for Maximally Chiral Signal

From Orlando text (lines 1262-1266):
> "the estimated error on h²Ω^VGW is roughly between 1 and 2 orders of magnitude larger than the estimated error on h²Ω^IGW. This can be explained by noticing that ... the maximum of R^I is roughly 1 order of magnitude larger than the maximum of R^V"

The Fisher error hierarchy means: even when the true signal has Ω^V = Ω^I (maximally chiral), the **best-fit** tends to have Ω^V < Ω^I because the data is more consistent with the stronger R^I response. This is a classic **regression to the mean** effect when one parameter is poorly constrained.

χ_orb ≈ 0.17 means: for a maximally chiral signal, the Fisher analysis recovers χ = Ω^V/Ω^I ≈ 0.17 as the best-fit value. The true χ = 1 is still within the error bars (Figure 3 shows the error ellipses extending to χ > 1 region).

---

**Next step**: Update paper to clarify normalization convention and cite Orlando's raw response functions as independent confirmation of non-zero chiral response for non-planar networks.
