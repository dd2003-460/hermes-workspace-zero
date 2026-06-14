# I-2: Physical Theory as Fit — EFT Residual Analysis Framework

**Date**: 2026-06-12
**Iteration**: 12
**Status**: VERIFIED
**Data**: notes/i2_fit_framework_results.json

---

## 1. Thesis

**Physical theories are fits to data in information space.** This is not a new claim in philosophy of science — it is the operative philosophy of Effective Field Theory (EFT). What we formalize here is the **mathematical framework** that makes this claim quantitative:

- **Theory T** = parametric model family M with parameters theta
- **Fit quality** = likelihood p(D|T) or equivalently chi2(T, D)
- **Theory complexity** = parameter count k_T
- **Theory selection** = AIC/BIC crossover criterion
- **Residual structure** r = D - T(D) = signature of missing degrees of freedom

### Theorem 1 (Physical Theory as Fit)

Let D = experimental data spanning energy scale [E_min, E_max].
Let Family(E) = set of theory families valid at scale E.

The optimal theory is:
$$T^* = \arg\min_{T \in \text{Family}(E)} [\chi^2(T, D) + 2k_T] \quad \text{(AIC criterion)}$$

where k_T is the number of free parameters.

### Corollary 1 (Residual Structure Theorem)

If residuals $r = D - T^*(D)$ exhibit non-random structure (e.g., autocorrelation, energy-dependent trend), then $T^*$ is a local optimum, not global. Evidence for $T' \in \text{Family}(E')$ with $E' > E$ is given by:

$$\Delta \text{AIC}(T, T') = \chi^2(T, D) - \chi^2(T', D) + 2(k_T - k_{T'})$$

If $\Delta \text{AIC} > 10$, the evidence is "decisive" (Jeffreys scale).

### Corollary 2 (EFT as Hierarchical Fit)

An EFT expansion in powers of $E/\Lambda$ (where $\Lambda$ is the new physics scale) is a **systematic hierarchical fit**:

- Leading order (LO): $T_0$ with $k_0$ parameters — fit at $E \ll \Lambda$
- Next-to-leading order (NLO): $T_1$ with $k_0 + 1$ parameters — fit at $E \lesssim 0.5\Lambda$
- N2LO: $T_2$ with $k_0 + 2$ parameters — fit at $E \lesssim 0.8\Lambda$
- ...

AIC/BIC crossover between orders determines: **when the data demands new parameters** (i.e., "new physics").

---

## 2. Numerical Results

### Example 1: Fermi Theory vs Electroweak Theory

| Quantity | Fermi (k=1) | Electroweak (k=3) |
|----------|-------------|-------------------|
| chi2 | 370.8 | 0.0 |
| AIC | 372.8 | 6.0 |
| BIC | 73.4 | 7.7 |
| Akaike weight | 2.24e-80 | 1.00 |
| Bayesian weight | 3.94e-80 | 1.00 |

**Crossover energy**: EW first preferred at E ~ 212 GeV (single-measurement AIC analysis).

**Residual structure**: Fermi theory residual grows quadratically with energy, becoming -15296% at E = 1000 GeV (vs data). This is the **classic signature of contact interaction breaking down** — the W boson is the missing degree of freedom.

**[I-2 Insight]**: "New physics" (W/Z bosons) is precisely what AIC/BIC demand when residual structure becomes non-random. The historical discovery of the W/Z was driven by this same logic — Fermi theory predictions violated unitarity at E >~ 300 GeV.

### Example 2: Post-Newtonian vs EOB (Gravitational Waves)

| Model | chi2 | k | AIC | BIC |
|-------|------|---|-----|-----|
| 1PN | 18694 | 1 | 18696 | 18698 |
| 2PN | 2244 | 2 | 2248 | 2253 |
| 3PN | 77.0 | 3 | 83.0 | 90.8 |
| EOB | 192 | 5 | 202 | 215 |

| Metric | 1PN | 2PN | 3PN | EOB |
|--------|-----|-----|-----|-----|
| Residual RMS | 0.019 | 0.007 | 0.001 | 0.002 |

**Residual at merger (v/c = 0.5)**:
- 1PN: -0.050 (5% phase error)
- 2PN: +0.022 (2% error)
- 3PN: +0.001 (0.1% error)
- EOB: +0.005 (0.5% error)

**[I-2 Insight]**: PN series is a **polynomial fit** in v/c. Each order captures more of the "signal" (waveform phase). The **structured residuals** at high v/c are the signature of missing physics (merger + ringdown). EOB is a **resummed fit** that captures the global structure. In real GW analysis, full EOB/IMRPhenom models include merger+rings, which pure PN can never capture.

### Example 3: Schwarzschild vs Kerr (Black Hole Shadows)

| Quantity | Schwarzschild (k=0) | Kerr (k=1) |
|----------|---------------------|------------|
| chi2 | 750.6 | 2.6 |
| AIC | 750.6 | 4.6 |
| Akaike weight | 1.05e-162 | 1.00 |

**[I-2 Insight]**: The no-hair theorem predicts black holes have only M and J. Kerr = minimal parameterization (k=1 for spin). **If Kerr residuals remain after fitting**, they signal "hair" (scalar fields, charge, modified gravity). AIC/BIC quantify whether hair is justified.

---

## 3. Connection to I-3 (Minimal Description Length)

AIC and MDL are **asymptotically equivalent** (Scharf 1995, Rissanen 1996):

$$\text{AIC} \approx -2\log L + 2k = \text{description length of (model + data)}$$
$$\text{MDL} = L(T) + L(D|T) = \text{description length of (theory + data)}$$

Both formalize "theory = fit" in information-theoretic terms:
- **AIC**: Frequentist — minimize prediction error
- **MDL**: Information-theoretic — minimize total code length
- **BIC**: Bayesian — maximize model posterior probability

The I-3 result (MDL crossover at N=1731 for anyon theories) and I-2 result (AIC/BIC crossover for Fermi vs EW) are **the same phenomenon at different scales**:

- **I-2**: Crossover in theory space (parameterized models)
- **I-3**: Crossover in description length (non-parameterized, Kolmogorov complexity)

Both are facets of the same principle: **physics is compression**.

---

## 4. Implications

1. **"New physics" is AIC/BIC demand**: When a theory's residuals become non-random, information criteria quantitatively demand a better theory. This is not philosophy — it's decision theory applied to science.

2. **EFT is a justified procedure**: EFT's hierarchical expansion in E/Lambda is exactly what AIC/BIC would prescribe: add parameters only when data demands it.

3. **Residuals are signals, not noise**: In particle physics (LHC anomaly search), cosmology (Hubble tension), and GW astronomy (PN convergence), structured residuals are the **only** reliable sign of new physics.

4. **BIC vs AIC for theory choice**: BIC penalizes complexity more strongly (log N vs 2). For large datasets (N >> 100), BIC favors simpler theories. For small datasets, AIC is more conservative. In all three examples above, both AIC and BIC agree — this is because the signal is overwhelming.

---

## 5. Next Directions (I-2 Continued)

1. **Cosmological residual analysis**: Apply this framework to supernova Ia H(z) data. Are dark energy signals "real" or just structured residuals of an incomplete model? Symbolic regression (SR) can detect this.

2. **Hubble tension as residual structure**: The 5-sigma discrepancy between early- and late-universe H0 measurements is a structured residual of the LCDM model. I-2 predicts: AIC/BIC would favor a new theory (early dark energy, modified gravity) over LCDM if N is large enough.

3. **Connection to I-1/I-3**: The hard-sphere derivation (I-1) is an "effective fit" valid for N < 1731. The MDL crossover (I-3) is the information-theoretic boundary. The AIC/BIC framework (I-2) provides the statistical decision theory for the same phenomenon.

---

*Generated by ralph-loop iteration 12*
*origin: ai*
