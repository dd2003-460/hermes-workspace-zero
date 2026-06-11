# EMRI Paper I: Schwarzschild Limit ρ_s → 0 Derivation

**Date:** 2026-05-22  
**Origin:** ai (based on iter84 specification)  
**Status:** Draft 0  
**Target:** JCAP format

## 1. Introduction

This paper extends the Extended Functorial QFT framework for PTA gravitational wave observations to the extreme mass ratio inspiral (EMRI) regime. We study the Schwarzschild limit (ρ_s → 0) of the dark matter-modified EMRI waveform model, deriving 5 propositions that characterize the suppression of chaotic dynamics by dark matter halos.

## 2. Schwarzschild Limit Setup

### 2.1 Parameter Definition

Consider an EMRI system consisting of:
- Primary: Schwarzschild black hole of mass M
- Secondary: compact object of mass μ ≪ M
- Dark matter halo: density profile ρ_s with characteristic scale ρ_s → 0

The ratio ρ_s/ρ_0 parameterizes the DM halo contribution, where ρ_0 is the background density.

### 2.2 Modified Metric

The metric takes the form:

$$ds^2 = -f(r)dt^2 + f(r)^{-1}dr^2 + r^2(d\theta^2 + \sin^2\theta d\phi^2)$$

where:

$$f(r) = 1 - \frac{2GM}{c^2 r} - \frac{8\pi G}{3c^2}\rho_s r^2$$

The ρ_s → 0 limit recovers the standard Schwarzschild metric.

## 3. Propositions

### Proposition 1: Chaos Threshold

**Statement:** In the Schwarzschild limit ρ_s → 0, the Lyapunov exponent λ_L of the EMRI orbital dynamics satisfies:

$$\lambda_L(\rho_s) = \lambda_0 + O(\rho_s \ln \rho_s)$$

where λ_0 is the pure Schwarzschild Lyapunov exponent.

**Proof sketch:** The DM perturbation enters the geodesic equation as a force term F_DM ∝ ρ_s r. Using standard perturbation theory on the Poincaré map, the chaos threshold scales as stated. ∎

### Proposition 2: DM Suppression of Chaos

**Statement:** For ρ_s > 0, the chaotic region in phase space is suppressed relative to pure Schwarzschild:

$$\Delta\Phi_{\text{chaos}}(\rho_s) < \Delta\Phi_{\text{chaos}}(0)$$

where ΔΦ measures the measure of chaotic orbits in the initial condition space.

**Proof sketch:** The DM potential is attractive and smooth, regularizing the resonant overlap that drives chaos. The Melnikov method shows the splitting of separatrices is reduced by O(ρ_s). ∎

### Proposition 3: Waveform Phase Shift

**Statement:** The accumulated GW phase shift due to DM over N orbits is:

$$\Delta\Psi_{\text{DM}} = \kappa \cdot \frac{\rho_s}{\rho_0} \cdot N \cdot \left(\frac{r_s}{r}\right)^{\alpha}$$

where κ and α are model-dependent constants.

**Proof sketch:** Integration of the DM perturbation to the geodesic deviation equation yields a secular phase accumulation proportional to ρ_s. ∎

### Proposition 4: Detectability Bound

**Statement:** For PTA sensitivity S_PTA(f), the minimum detectable DM density is:

$$\rho_{s,\text{min}} \propto S_{\text{PTA}}^{1/(\alpha+1)}$$

**Proof sketch:** Signal-to-noise requires ΔΨ_DM > threshold. Substituting the phase shift scaling gives the detection bound. ∎

### Proposition 5: Universal Scaling

**Statement:** In the joint limit M → ∞, μ/M → 0, the scaled phase shift ΔΨ_DM · (ρ_0/ρ_s) converges to a universal function of the orbital invariants.

**Proof sketch:** Dimensional analysis of the perturbed geodesic equation shows all dependence on M, μ enters only through the orbital invariants (energy, angular momentum). ∎

## 4. Numerical Verification Plan

This section requires numerical integration of the perturbed geodesic equations. The implementation plan:

1. Set up initial conditions with varying (E, L, ρ_s)
2. Integrate using 8th-order Runge-Kutta
3. Compute Lyapunov exponents via Benettin's method
4. Compute GW phase accumulation via stationary phase approximation
5. Compare with analytical predictions from Propositions 1-5

**TODO:** Implement simulate_emri_chaos.py

## 5. Connection to JCAP Format

This work extends the Extended Functorial QFT framework from BAC-QFT PTA analysis to the EMRI regime. Key connections:

- The dark matter halo enters as a background field in the QFT picture
- The ρ_s → 0 limit corresponds to the decoupling limit
- The chaos suppression mechanism provides a new probe of DM distribution around SMBHs

## 6. References (TBD)

- NANOGrav 15-year results on GW background
- Black Hole Censuses and SMBH distribution
- Standard EMRI theory: Barack et al. (LISA science case)
- Dark matter near SMBH: standard DM spike models

---

*This is a draft 0 based on iter84 specifications. The 5 propositions need rigorous mathematical proof and numerical verification.*
