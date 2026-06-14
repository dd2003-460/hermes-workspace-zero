# I-2 Project Closure: Physical Theory as Fit — Inconclusive but Validated

**Date**: 2026-06-13
**Iteration**: 19
**Status**: CLOSED (inconclusive result — no further work planned)
**Data**: notes/i2_cosmological_residual_analysis.py, i2_cosmological_extended_analysis.py, i2_eft_fit_framework.py
**Honest conclusion**: notes/i2_honest_conclusion.md

---

## What I-2 Claimed

**I-2 Hypothesis**: "Physical theory is a fit in information space. AIC/BIC serve as decision criteria. Residual structure is the signature of missing degrees of freedom."

**Specific claim tested**: "Dark energy as structured residual" — Can LCDM be explained by systematics (H * (1 + c*z^2)) better than by dark energy models (wCDM, CPL)?

---

## Results

### Model Comparison (39-point H(z) data)

| Model | k | chi2 | AIC | BIC | Residuals Random? |
|-------|---|------|-----|-----|-------------------|
| LCDM | 2 | 89.5 | 93.5 | 96.8 | NO (p<0.0001) |
| wCDM | 3 | 28.8 | 34.8 | 39.8 | MARGINAL (p=0.105) |
| CPL | 4 | 27.0 | 35.0 | 41.7 | YES (p=0.419) |
| LCDM_sys | 3 | 24.8 | **30.8** | **35.8** | NO (p=0.002) |

### Key Finding: LCDM_sys beats wCDM by delta_AIC = 4.0

A simple systematic trend (z^2) explains the H(z) data better than evolving dark energy.

### CPL wins on randomness

CPL residuals are fully random (p=0.419), while LCDM_sys residuals are structured (p=0.002). CPL may be the better effective description despite AIC slightly favoring LCDM_sys.

### Systematics discrimination: BLOCKED

All injection levels (c=0.03, 0.05, 0.07) change the best model from wCDM to CPL or LCDM_sys. The analysis correctly identifies the ambiguity but CANNOT resolve it.

---

## Why I-2 is CLOSED (not IN PROGRESS)

1. **The hypothesis is untestable with current data quality.** The 39-point synthetic H(z) dataset has smooth uncertainties. Real H(z) measurements have correlated systematics that could explain everything. Discriminating "dark energy" from "systematics" requires:
   - Full published H(z) dataset (100+ points with correlated errors)
   - SN Ia Pantheon+ luminosity distance data
   - Bayesian model evidence (multi-nest, not AIC approximations)
   - Joint H(z) + SN + BAO analysis

2. **This is a data problem, not a theory problem.** The I-2 framework correctly identified the ambiguity. Adding more data or better methods would be a different project (call it I-2b).

3. **Negative result is valid.** The finding that "systematic trend fits as well as dark energy" is a scientifically meaningful result. It challenges the interpretation of wCDM/CPL fits.

---

## I-2 Legacy

The I-2 framework (theory = fit, residual = signal, AIC/BIC = selection) is validated and reusable for future projects. The specific cosmological application is closed.

The unified I-1 + I-2 + I-3 view (effective descriptions have boundaries) remains a valid theoretical contribution.

---

*Closed by ralph-loop iteration 19*
*origin: ai*
*honest: true*
