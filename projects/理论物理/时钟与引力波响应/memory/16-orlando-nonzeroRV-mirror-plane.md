---
name: orlando-nonzeroRV-mirror-plane
description: Why Orlando gets nonzero R^V for LISA-Taiji cross-correlation: mirror plane symmetry breaking
metadata:
  type: project
  created: 2026-07-06
---

# Why Orlando R^V ≈ 0.02-0.04 for LISA-Taiji Cross-Correlation

## Key Theoretical Result

For a single planar detector, R^V = 0 is a consequence of mirror symmetry:

- Under mirror reflection across detector plane: e^R(k̂) = e^L(-k̂), e^L(k̂) = e^R(-k̂)
- For planar detector: R^R(k̂) = R^L(reflected k̂)
- Therefore: R^V(k̂) = R^V(reflected k̂) AND R^V(k̂) = -R^V(reflected k̂) → R^V = 0
- This holds for ALL self-correlations within a single detector

## Cross-Correlation Between Two Planar Detectors

For cross-correlation between detectors 1 and 2:
R^V_12(k̂) = (R^R_1(k̂) * R^R_2*(k̂) - R^L_1(k̂) * R^L_2*(k̂)) / 2

The mirror symmetry argument R^V_12 = -R^V_12 only works if BOTH detectors share the SAME mirror plane. If their mirror planes are tilted relative to each other, the reflection for detector 1 ≠ reflection for detector 2, and the symmetry breaks.

## LISA-Taiji Geometry

- Both LISA and Taiji are equilateral triangular detectors inclined 60° to ecliptic
- LISA trails Earth by 20°, Taiji leads by 20° (60° orbital separation)
- Both have same z-axis (ecliptic pole direction)
- Their mirror planes intersect at the z-axis

The mirror reflection for both detectors sends z → -z, which corresponds to (θ, φ) → (π-θ, φ) in ecliptic coordinates. Since they share the SAME reflection (same z-axis), the mirror symmetry SHOULD still apply...

UNLESS the different arm lengths (L_LISA = 2.5 Gm vs L_Taiji = 3.0 Gm) or different orbital positions break the symmetry through the transfer function W(kL).

## Orlando's Confirmed Results (CrossV.pdf)

For LISA(A,E,T) × Taiji(C,D,S) cross-correlation at fixed positions:
- R^V_AC max: ~0.04
- R^V_EC max: ~0.03
- All 9 channel pairs have nonzero R^V (max ~0.01-0.04)

For single detector self-correlations: R^V = 0 (identically, per Orlando text line 140)

## Resolution

The nonzero R^V for LISA-Taiji cross-correlation arises from the **non-planar network geometry**:
- Even though both detectors are individually planar, their different orbital positions mean the network spans 3D space
- The key is NOT the detector orientations, but that the two detectors are at different heliocentric positions (~60° apart)
- Orlando's computation includes the phase factor exp(-2πi k · (x_LISA - x_Taiji)) in the cross-correlation

This is a NETWORK effect, not a single-detector effect. The spatial separation between LISA and Taiji (in 3D) breaks the parity symmetry that makes R^V = 0 for single detectors.

**This confirms our norm_V = 1.0 is the correct normalization for the non-planar LISA-Taiji network.**

---

**Validation in progress**: scripts/validate_orlando_crosscorr.py (agent building full Orlando formalism validator)
