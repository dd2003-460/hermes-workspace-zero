# SUB-5.4: Paper Consistency Review Report

## Checklist: Does the Paper Contain the Wrong Value?

| Finding | Paper Contains Wrong Value? |
|---------|---------------------------|
| H_0 factor error | **YES** |
| SNR numerical value | **YES** |
| L_olc mismatch | **NO** (paper is correct; code has the issue) |
| gamma_olc hardcoded | **NO** (paper uses \Gamma=0.5, not hardcoded gamma=-0.188; but paper does not discuss sky-averaging derivation) |
| Gamma^V=0 | **YES** (not addressed despite being physically critical) |
| S_corr frequency dependence | **YES** |

---

## Detailed Findings

### 1. H_0 Factor Error

**Status: ERROR IN PAPER**

The paper at **line 1227** states $H_0 = 2.18 \times 10^{-18}$ Hz (Planck 2018). This individual value is correct.

However, at **line 1260**, the paper computes:

$$(3H_0^2/2\pi^2)^2 \approx (1.4 \times 10^{-37})^2 \approx 2.0 \times 10^{-74} \text{ Hz}^4$$

**The correct value is: $(7.223 \times 10^{-37})^2 \approx 5.217 \times 10^{-73}$ Hz$^4$.**

- Paper's intermediate value: $1.4 \times 10^{-37}$ (should be $7.223 \times 10^{-37}$)
- Paper is **5.2x too small** on the intermediate value
- Paper's squared value $2.0 \times 10^{-74}$ is **26.6x too small** (should be $5.217 \times 10^{-73}$)
- Line: **1260**

### 2. SNR Numerical Value

**Status: ERROR IN PAPER**

The paper at **line 1264-1266** multiplies:

$${\rm SNR}_{\rm single}^2 \approx 6.4 \times 10^7 \times 0.25 \times 10^{-16} \times 2.0 \times 10^{-74} \times 5.1 \times 2 \times 10^{30}$$

- Paper's claimed result: $1.7 \times 10^{-8}$ (line 1266)
- Actual product of the paper's own numbers: $6.4 \times 0.25 \times 10^{-16} \times 2.0 \times 10^{-74} \times 5.1 \times 2 \times 10^{30} \times 10^7 = 3.264 \times 10^{-52}$
- **Gap: ~43.7 orders of magnitude**
- Paper claims SNR$_{\rm single} = 1.3 \times 10^{-4}$ at **line 1268**, but the correct SNR$_{\rm single}$ from paper's formula (with correct arithmetic) would be $\sim \sqrt{3.264 \times 10^{-52}} \approx 1.8 \times 10^{-26}$
- Even with the corrected $(3H_0^2/2\pi^2)^2$, the correct SNR$_{\rm single}$ would be $\sim 9.2 \times 10^{-26}$
- Lines: **1264, 1266, 1268**

### 3. L_olc Mismatch

**Status: PAPER IS CORRECT; CODE HAS THE ISSUE**

The paper correctly uses space-based arm lengths throughout:
- **Line 444**: $L = 0.17$-3 Gm (space-based)
- **Line 790**: $L = 1.7 \times 10^8$ m
- **Line 1230**: $L = 1.7 \times 10^8$ m (0.17 Gm)
- **Line 1116**: $L = 1.7 \times 10^8$ m (0.17 Gm)

The paper correctly identifies and corrects the ground-based $L = 10$ m assumption at **lines 442-444**. The code (03-olc-snr-solver.py) has the hardcoded $L\_olc = 10.0$ issue, but the paper itself does not contain this error.

### 4. gamma_olc Hardcoded

**Status: NOT DIRECTLY HARDCODED IN PAPER, BUT UNJUSTIFIED**

The paper uses $\Gamma = 0.5$ at **line 1230** in the parameter table. This is the ORF parameter (intensity overlap reduction function).

- The paper references "第3章计算结果" (calculated in Chapter 3) as the source
- The paper does NOT document HOW this value was derived
- The paper uses $K_{\rm sky} \approx 0.53$ at **lines 604, 1111** (sky-averaged response factor), which is a different but related quantity
- There is no discussion of sky-averaging procedure, azimuthal integration, or constellations geometry in the SNR section
- The code uses a hardcoded $\gamma\_olc = -0.188$ which is physically different (un-normalized ORF for 60-degree arm angle)
- Lines: **1230** (value given without derivation)

### 5. Gamma^V = 0 for Planar Configurations

**Status: NOT ADDRESSED (CRITICAL GAP)**

The paper completely omits discussion of $\Gamma^V$ (parity-odd/chiral ORF). Specifically:

- No mention of chiral SGWB detection at all
- No mention of the requirement for non-coplanar detectors
- No discussion of parity-odd vs parity-even ORF components
- The JCAP paper (arXiv:2410.18916v2) establishes that for planar equilateral triangles, $\Gamma^V = 0$ exactly (parity symmetry)
- Lou's thesis also does not analyze $\Gamma^V$ (noted as future work at line 2498)
- The code correctly verifies $\Gamma^V < 10^{-10}$ for planar equilateral triangles, but this insight is not reflected in the paper
- The paper's SNR calculation assumes $\Gamma^2 = 0.25$ without explaining whether this refers to $\Gamma^I$ only (which is fine since the paper is not studying chiral detection), but the omission is significant for completeness

**If the paper claims detection capability for general SGWB (including chiral), it must address $\Gamma^V$.** If it restricts to non-chiral, it should state this explicitly.

Lines with no mention: entire paper (checked via grep for Gamma_V, Gamma^V, chiral, 手征, parity)

### 6. S_corr Frequency Dependence

**Status: ERROR IN PAPER**

At **line 1203**, the SNR formula is written as:

$${\rm SNR}_{\rm single}^2 \approx 2 T_{\rm obs} \cdot \Gamma^2 \cdot \Omega_{\rm GW}^2 \cdot \left( \frac{3H_0^2}{2\pi^2} \right)^2 \int_0^\infty df\, \frac{|\mathcal{T}(f)|^4}{P_N^2(f)}$$

This is correct in form — it has an integral over $f$. However, at **line 1261**, the frequency-dependent transfer function is replaced by a constant:

$$(2\pi L K_{\rm sky}/c)^4 \approx (1.5)^4 \approx 5.1$$

The paper computes this using $L = 1.7 \times 10^8$ m, but the factor $2\pi f L/c$ depends on frequency. The paper implicitly assumes a single frequency $f$ (unspecified) to evaluate this term, rather than carrying the full frequency integral.

- The integration range is stated as $10^{-4}$ to $10^3$ Hz at **line 1247**
- But the transfer function $(2\pi f L/c)^4$ varies by $10^{16}$ across this range
- The paper extracts the geometric factor $5.1$ from some unspecified frequency and multiplies it by the integral value $2 \times 10^{30}$ Hz$^{-1}$
- This is inconsistent: either carry the full frequency-dependent integrand, or explain why a single frequency approximation is valid
- Lines: **1203** (integral form), **1247** (integration range), **1261** (replacement by constant)

Additionally, at **line 1191**, the paper states $\Gamma$ is frequency-independent ("$\Gamma$ 与频率无关（第3章结论）"). This is a simplification — ORFs do have frequency dependence at high frequencies, though it is small in the short-wavelength limit. This should be stated as an approximation, not as a factual claim.

---

## Summary of Required Corrections

### Critical (must fix before publication):

1. **Line 1260**: Correct $(3H_0^2/2\pi^2)^2$ from $2.0 \times 10^{-74}$ to $5.2 \times 10^{-73}$. Recalculate SNR$_{\rm single}^2$ and SNR$_{\rm single}$ with correct arithmetic.
2. **Lines 1264-1266**: Fix the arithmetic error. The product $6.4 \times 0.25 \times 10^{-16} \times 2.0 \times 10^{-74} \times 5.1 \times 2 \times 10^{30} \times 10^7$ does not equal $1.7 \times 10^{-8}$.
3. **Lines 1282-1290**: Recalculate $N_b$ and $N_{\rm sat}$ using the corrected SNR$_{\rm single}$.
4. **Lines 1296-1302**: Update the entire table (N_sat values are wrong due to wrong SNR).

### Important (should fix):

5. **Lines 604, 1111, 1230**: Clarify the derivation of $\Gamma = 0.5$ and $K_{\rm sky} \approx 0.53$. Document the sky-averaging procedure.
6. **Lines 1203, 1261**: Either carry the full frequency-dependent transfer function through the integral, or explicitly justify the single-frequency approximation.
7. **Throughout**: Add discussion of $\Gamma^V = 0$ for planar configurations and its implications for chiral SGWB detection. State clearly whether the analysis covers only non-chiral SGWB.

### Low Priority:

8. **Line 1191**: Change "$\Gamma$ 与频率无关（第3章结论）" to note this is an approximation valid in the short-wavelength limit.
