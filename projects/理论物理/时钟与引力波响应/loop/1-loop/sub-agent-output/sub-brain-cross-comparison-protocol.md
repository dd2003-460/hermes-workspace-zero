# Cross-Comparison Protocol: Three-Source Convergence Check

**Epistemological question**: Are these sources independently correct, or just "consistent but wrong"?

## Comparison Table

| # | Critical Item | SUB-5.0 (Calc) | SUB-5.1 (Code) | SUB-5.2 (JCAP) | Verdict |
|---|--------------|---------------|---------------|---------------|---------|
| 1 | SNR formula | $2T\!\int\!\gamma^2 S_{corr}^2/S_N^2$ | Code line 12 same | $(3/10)^2 T\!\int\!\gamma_{eff}^2 I^2/\sum\gamma^2/N^2$ [eq.2.12] | **DISAGREE**: code has no $(3/10)^2$ or $\gamma_{eff}$ |
| 2 | $H_0$ factor | Paper $(1.4e{-37})^2$, correct $(7.223e{-37})^2$ | Code `H_0^2/2\pi^2` (line 30) — missing 3 | Confirms $\Omega_{GW}=4\pi^2 f^3/3H_0^2 I(f)$ [sec 3.2] | **AGREE**: factor 3 missing everywhere |
| 3 | ORF norm $1/8\pi$ vs $1/4\pi$ | Not addressed | Not addressed | Hu: $1/8\pi$ [P3]; Lou: $1/4\pi$ [P3]; JCAP: $1/4\pi$ | **AGREE**: $1/4\pi$ correct for Lou; Hu absorbs 1/2 |
| 4 | $\Gamma^V=0$ planar equilateral triangle | Not addressed | `test_coplanar_zero()` line 280: $<1e{-10}$ | Mirror symmetry argument [JCAP §1 + P3 §4.2] | **AGREE**: solid result |
| 5 | $L_{olc}$: 10m vs Gm | Not addressed | Code line 45: `L_olc=10.0`, paper says Gm | P3 §2 assumes space-based arm length | **AGREE**: 10m gives TF $10^8$ too small |
| 6 | $\gamma_{olc}=-0.188$ | Used for SNR calc (line 1264) | HARDCODED line 46, source unknown | No code-level equivalent | **DISAGREE**: blind spot in all sources |
| 7 | $SNR_{single}=1.3e{-4}$ (paper) | Corrected: $9.227e{-26}$ (21 orders) | Code uses $L_{olc}=10$, does not verify | JCAP: $\gamma_{eff}$, not single-detector | **AGREE**: paper's 21-order overestimation is real |

## Disagreement Analysis

- **Item 1**: Code implements Allen (1987) directly; JCAP adds $\gamma_{eff}$ from Fisher matrix inversion of multi-channel cross-correlations. Code is foundational — not wrong, just single-channel lower bound, not comparable to JCAP's optimal SNR.
- **Item 6**: None of the three sources can independently verify $-0.188$. If planar equilateral $\implies \gamma_{olc}=0$, the entire SUB-5.0 SNR chain collapses. **This is the weakest link** — a single unverifiable constant corrupts all downstream conclusions.

## Breaking the Closed Loop: Independent Verification

### Primary: Derive $\Gamma^I$ from Hu PRD Eq.(8) for Planar Equilateral Triangle

For $fL/c \ll 1$, $T_{olc} \approx 2\pi f L/c$ is angle-independent:
$$\Gamma^I \approx \frac{1}{8\pi}(2\pi f L/c)^2 \int d^2\Omega_{\hat{n}} \sum_A |F^A(\hat{n})|^2$$

The angular integral is a **pure geometric constant**. Uses only Hu's first-principles formula + OLC's sinc TF + triangle geometry. No code, no JCAP, no SUB-5.0.

**Expected**: $\gamma(0)$ should match Hellings-Downs $\approx 0.53$. Paper claims $K_{sky}=0.53$ (line 604) — mismatch means $K_{sky}$ is also wrong.

Since $y(t) \propto \dot{h}(t)$, $S_{corr}(f) = (2\pi f)^2 \langle|T_{gw}|^2\rangle S_h(f)/f^2 \propto f^{-1}$ at low frequency.
**Code assumes $S_{corr} \propto f^{-3}$** (line 12). This shifts SNR by another order of magnitude.

### Execution Order
1. Independent Hu+OLC ORF spherical integral (no dependencies)
2. First-principles $S_{corr}$ frequency dependence
3. Compare all three sources to the independent results
4. If agree: confidence rises; if disagree: identify epistemic gap
