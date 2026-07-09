# Quality Check Report: P1-1 Chiral Physics (Iteration 1 — Re-review)

## Status

**FAIL**

---

## Executive Summary

This is a re-review after a previous QC flagged issues and a fix agent attempted to address them. The main improvement is that the appendix file `note/P1-1-appendix-normalization.md` now exists (121 lines, sections A.1-A.6). However, the content of this appendix does NOT satisfy any of the 5 required subtasks (Subtasks 1-5) specified in the task decomposition `loop/1-loop/03-任务分解-P1-1-Iteration1.md`. Additionally, the fix agent introduced new formula accuracy issues (invented chi_orb formula, dimensionally problematic S^V formula) and did not correct the citation errors in the main document.

---

## Checklist

| # | Check Item | Verdict | Details |
|---|-----------|---------|---------|
| 1 | **Completeness** | FAIL | Appendix exists but contains none of the 5 required subtask outputs |
| 2 | **Formula Accuracy** | FAIL (qualified) | Formulas in main doc partially correct; appendix contains invented and dimensionally problematic formulas |
| 3 | **Derivation Chain** | FAIL | Gamma^V tensor derivation (Subtask 2) entirely absent from appendix; 0 intermediate steps in main doc |
| 4 | **Self-Questioning** | PASS | 3 Q&A items in §9, exceeds minimum 2 |
| 5 | **Physics Interpretation** | PASS (qualified) | Main doc has good intuition in §1.2, §5.3; some formulas lack interpretation |
| 6 | **Citations** | FAIL | Section number errors uncorrected; appendix misattributes source material |

---

## Detailed Evaluation

### 1. Completeness — FAIL

**Appendix file exists but does not match Subtasks 1-5.**

The previous QC flagged the absence of the appendix file. This iteration's appendix `note/P1-1-appendix-normalization.md` (121 lines) exists but its content diverges significantly from what the task decomposition specified:

| Subtask | Required Content | Appendix Content | Match? |
|---------|-----------------|------------------|--------|
| **1. Circular basis normalization** | Algebraic verification of `|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_x|^2` and `e^R_{ab}(e^R_{ab})* = 1` | A.1 presents generic formula A.1 (not from source), A.2 gives S^V formula, but NO algebraic normalization verification | No |
| **2. Gamma^V parity-odd tensor derivation** | 5+ intermediate steps deriving the parity-odd ORF, strict proof of mirror symmetry leading to Gamma^V = 0 | A.6 defines generic `gamma_{ab}(f)` in eq. A.6; eq. A.7 defines chiral ORFs in terms of `gamma^+` and `gamma^x`; NO Gamma^V derivation, NO 5+ intermediate steps | No |
| **3. chi(f) frequency dependence** | At least 2 non-JCAP references analyzing how chi varies with frequency and spectral shapes | No chi(f) spectral analysis anywhere in appendix; appendix does not analyze frequency dependence | No |
| **4. Hu PRD vs JCAP ORF comparison** | At least 2 formula comparisons between Hu PRD and JCAP frameworks, with clear conclusion | No comparison between Hu PRD and JCAP ORF formalisms in appendix | No |
| **5. Integration review** | 10-criteria checklist review, final confidence >= 0.85 | No criteria checklist, no confidence assessment | No |

**Subtask completion status:**

| Subtask | Status |
|---------|--------|
| 1. Circular basis normalization verification | **Not executed** |
| 2. Gamma^V parity-odd tensor derivation | **Not executed** |
| 3. chi(f) frequency dependence analysis | **Not executed** |
| 4. Hu PRD vs JCAP ORF comparison | **Not executed** |
| 5. Integration review with 10-criteria checklist | **Not executed** |

**Impact: Critical.** The appendix is the primary 2-loop output vehicle. Its content failing to match any required subtask means the 2-loop iteration has produced no valid deliverable.

---

### 2. Formula Accuracy — FAIL (qualified)

#### 2.1 Main Document — Partially Correct

**Formula 1: eq. 2.3 circular basis tensors**
- Note: `e^R = (e^+ + i e^x)/sqrt(2)`, `e^L = (e^+ - i e^x)/sqrt(2)`
- JCAP (eq. 2.3): Identical
- **Verdict: Correct**

**Formula 2: eq. 2.4 light strain**
- Note: `h_R = (h_+ - i h_x)/sqrt(2)`, `h_L = (h_+ + i h_x)/sqrt(2)`
- JCAP (eq. 2.4): Identical
- **Verdict: Correct** (note: JCAP defines these separately, the note's combined citation is imprecise)

**Formula 3: eq. 2.6 Stokes parameters**
- Note: `I(f) = (S_R + S_L)/2`, `V(f) = (S_R - S_L)/2`
- JCAP (eq. 2.6): Identical
- **Verdict: Correct**

**Formula 4: eq. 3.3 energy density**
- Note: `Omega_I(f) = (4*pi^2/3H_0^2) f^3 I(f)`, `Omega_V(f) = (4*pi^2/3H_0^2) f^3 V(f)`
- JCAP (eq. 3.3 in §3.2): Numerically identical
- **Verdict: Numerically correct but citation location wrong** (see §6 below)

**Formula 5: eq. 2.9 cross-correlation**
- Note: `<s_i(f) s_j^*(f')> = (1/2) delta(f-f') [Gamma^I_ij(f) I(f) + Gamma^V_ij(f) V(f)]`
- JCAP (eq. 2.9): Identical
- **Verdict: Correct**

**Formula 6: eq. 2.10 Gamma^V parity-odd ORF**
- Note: `Gamma^V_ij(f) propto -i int d^2k/4pi (e^+ e^x - e^x e^+) e^(-i2pi f k.Delta r/c)`
- JCAP (eq. 2.10): The full expression includes:
  - `(3/4)` prefactor
  - `sin(2pi f L_i/c) sin(2pi f L_j/c)` detector-specific terms
  - Both Gamma^I and Gamma^V in one equation
- **Verdict: The proportional relationship is correct, but omitting the prefactor and detector terms makes the formula incomplete.**

#### 2.2 Appendix — New Issues Found

**Formula A.4 (S^V definition):**
```
S^V = h_R^2 - h_L^2
```
- **Problem**: For power spectral density (PSD) based definitions, S^V should be defined in terms of ensemble-averaged squared amplitudes, not raw amplitudes. The notation `h_R^2` is ambiguous — does it mean `|h_R|^2`? Even so, S^V is defined as `(S_R - S_L)/2` in JCAP eq. 2.6, where `S_R = <h_R h_R^*>` is a PSD. The appendix's formula A.4 conflates field amplitudes with PSDs.
- **Verdict: Dimensionally problematic.**

**Formula A.8 (chi_orb):**
```
chi_orb(f) = Im[gamma_{ab}(f)] / Re[gamma_{ab}(f)]
```
- **Problem**: The appendix (A.3) attributes `chi_orb` to JCAP 2025, but a thorough review of the JCAP paper found **no such parameter**. The symbol `chi_orb` appears nowhere in JCAP's text or equations. The definition `Im[gamma]/Re[gamma]` is the fix agent's own invention, likely inspired by the chiral ORF structure in eq. A.7 (`gamma^{R/L} = (gamma^+ +- i gamma^x)/2`), but this is not an established quantity in either source paper.
- **Verdict: Invented formula, misattributed to source.**

**Formula A.6 (generic ORF):**
```
gamma_{ab}(f, Omega) = (1/2) sum_{A,+x} F_a^A(Omega) F_b^A(Omega) e^{i 2pi f Omega.(x_a - x_b)/c}
```
- **Problem**: This does not match either Hu PRD or JCAP precisely. Hu PRD defines ORF with `(1/8pi) int d^2n` and uses link response functions `R_A^{one}`. JCAP uses detector tensor `D_{ab}` and auxiliary tensors `Gamma^{I/V}_{abcd}` (eqs. 2.14-2.15). The formula A.6 is a simplified hybrid not matching either source exactly.
- **Verdict: Simplified hybrid, not faithful to either source.**

---

### 3. Derivation Chain — FAIL

**Subtask 2 (Gamma^V parity-odd tensor derivation) is entirely missing from the appendix.**

The main document (§5.3) provides the following on Gamma^V:

> "括号内的组合 e^+ e^x - e^x e^+ 是宇称奇的——它在空间反换下变号。"

This is a **claim** without derivation. The required 5+ intermediate steps are:
1. Write `e^+_{ab}` and `e^x_{ab}` in explicit form using orthonormal basis `{e_th, e_ph}`
2. State parity transformation P: `k -> -k` under which `e_th -> -e_th`, `e_ph -> e_ph`
3. Derive `e^+ -> e^+` (parity-even) and `e^x -> -e^x` (parity-odd)
4. Prove `e^+_{ab} e^x_{cd} - e^x_{ab} e^+_cd -> -(e^+_{ab} e^x_{cd} - e^x_{ab} e^+_cd)`
5. Argue that for mirror-symmetric detector network M, Gamma^V = -Gamma^V implies Gamma^V = 0

**None of these steps appear anywhere in the main document or the appendix.**

Subtask 1 (normalization algebraic verification) is also absent — no verification of `|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_x|^2` or `e^R_{ab}(e^R_{ab})* = 1`.

Subtask 5 (10-criteria integration checklist) is absent — no checklist, no confidence assessment.

---

### 4. Self-Questioning — PASS

Section §9 contains 3 Q&A items:

| Question | Answer Quality |
|----------|---------------|
| Q1: chi=1 physical meaning | Good answer connecting to extreme chiral generation mechanisms and new physics |
| Q2: Why Q/U have no monopole contribution | Correct spin-harmonics explanation (s=4, l=0) |
| Q3: Why planar triangular detector has Gamma^V=0 | Correct mirror symmetry argument |

3 Q&A items exceed the minimum requirement of 2. Quality is acceptable.

---

### 5. Physics Interpretation — PASS (qualified)

The main document provides notably good physical intuition compared to what the previous QC flagged:

| Formula | Has Physical Intuition? | Evaluation |
|---------|----------------------|------------|
| eq. 2.3 circular basis (radians) | Yes (§1.2) | Test particle circular motion intuition |
| eq. 2.6 I/V definitions | Yes (table in §2.3) | Physical meaning table with V=0, V>0, V<0 cases |
| eq. 3.3 chi(f) definition | Yes (§3.3, §2.3) | "Angular momentum helicity per unit energy" interpretation |
| Chi parameter parity breaking (§4) | Yes (§4) | Three mechanisms explained physically |
| eq. 2.9 cross-correlation | Yes (§5.2) | Signal extraction from noise explained |
| Gamma^V parity-odd (eq. 2.10) | Yes (§5.3) | Three intuitive explanations (mirror, triple product, observable) |
| Omega_GW energy density (eq. 3.3) | Partially (§6) | Note about Maggiore normalization difference |

The document now covers approximately 80% of key formulas with physical interpretation. This is a significant improvement over the previous QC's "40%" assessment.

**Residual concern**: Stokes matrix (eq. 2.2) still has no direct physical interpretation — only the matrix elements are listed.

---

### 6. Citations — FAIL

| Note Citation | Actual Location | Issue |
|---------------|----------------|-------|
| JCAP §3.1, eq. 3.3 | **JCAP §3.2, eq. 3.3** | Section number error **uncorrected** (§3.1 covers LISA-Taiji network configurations; §3.2 covers power-law integrated sensitivity and energy density) |
| eq. 2.4 covers both tensors and strains | eq. 2.3 is tensors, eq. 2.4 is strains | Two formulas merged in citation (pre-existing issue, not corrected) |
| eq. 2.10 describes only Gamma^V | eq. 2.10 contains both Gamma^I and Gamma^V | Incomplete citation (pre-existing) |
| A.6 attributes chi_orb to JCAP | chi_orb does not exist in JCAP | **New misattribution by fix agent** |
| A.6 attributes S^I complete framework to Hu PRD | Hu PRD uses one-way link ORFs, not Stokes parameters | **Misattribution by fix agent** |

---

## Key Issues

1. **Appendix content does not match Subtasks 1-5.** The file exists but none of the five required subtask outputs are present. This is the same core failure as the previous QC, manifested differently — the previous QC found the file missing; this QC finds it present but empty of the required content.

2. **New formula accuracy problems introduced by the fix agent.** The appendix contains formula A.8 (chi_orb) which is invented and not found in either source paper, and formula A.4 (S^V = h_R^2 - h_L^2) which is dimensionally problematic.

3. **Citation errors uncorrected.** The section number error (§3.1 vs §3.2), formula merging (eq. 2.3/2.4), and incomplete citation (eq. 2.10) all persist.

4. **Derivation chain still absent.** No 5+ step derivation of Gamma^V, no normalization verification, no integration checklist.

5. **Appendix references are partially inaccurate.** The fix agent's reference section (A.6) misattributes Stokes parameter frameworks to Hu PRD and invents chi_orb content for JCAP.

---

## Confidence

**Confidence in main document output: 0.50**

| Factor | Score Change |
|--------|-------------|
| Formulas 1-5 numerically correct | +0.20 |
| Good physics interpretation (~80% of formulas) | +0.15 |
| Self-questioning meets requirements (3 Q&A) | +0.05 |
| Appendix exists but lacks required subtasks | -0.20 |
| Appendix introduces invented formulas (A.8, A.4) | -0.10 |
| Citation errors uncorrected | -0.05 |
| No derivation chain (0 intermediate steps for Gamma^V) | -0.10 |
| **Net** | **0.50** |

---

## Required Redo

1. **Execute Subtasks 1-5 properly.** The appendix must contain:
   - **Subtask 1**: Explicit algebraic steps verifying `|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_x|^2` and `e^R_{ab}(e^R_{ab})* = 1`, starting from eqs. 2.3-2.4 of JCAP.
   - **Subtask 2**: Complete 5+ step derivation of Gamma^V starting from the tensor decomposition in JCAP eqs. 2.14-2.15, including parity transformation analysis of e^+ and e^x, and mirror symmetry argument for planar detectors.
   - **Subtask 3**: chi(f) frequency dependence analysis with at least 2 non-JCAP references (e.g., Seto PRL 2006, Hu PRD, Alexander et al. 2006).
   - **Subtask 4**: Explicit formula-by-formula comparison of ORF frameworks between Hu PRD (eqs. 8-10, one-way link formalism) and JCAP (eqs. 2.9-2.10, Stokes parameter decomposition), with at least 2 specific formula comparisons and a clear conclusion on compatibility.
   - **Subtask 5**: 10-criteria acceptance checklist (AC1-AC10), each item evaluated with evidence, final confidence >= 0.85.

2. **Remove invented content from the appendix.** Delete chi_orb formula A.8 and its section A.3 unless it can be grounded in a real source. Correct A.4 to use proper PSD notation: `S^V = (S_R - S_L)/2` per JCAP eq. 2.6. Correct A.6 to match either Hu PRD's or JCAP's ORF definition exactly.

3. **Correct citation errors in the main document.** Change `JCAP §3.1, eq. 3.3` to `JCAP §3.2, eq. 3.3`. Separate the citation of eqs. 2.3 and 2.4. Note that eq. 2.10 contains both Gamma^I and Gamma^V.

4. **Add physical interpretation for Stokes matrix (eq. 2.2).** The matrix structure `[[I-iV], [iV, I]]` in the circular basis should have a physical explanation — it encodes that off-diagonal terms represent coherent cross-correlations between + and x polarizations, and their imaginary part is precisely the parity-odd component V.

---

## Next Steps

- Return to 2-loop/02 (backup) -> 2-loop/03 (redo Subtasks 1-5 with correct content)
- The next QC pass must verify that the appendix content directly implements all 5 subtasks as specified in `loop/1-loop/03-任务分解-P1-1-Iteration1.md`
- Subtask 5's final confidence assessment must reach >= 0.85

---

*Quality check performed by Commander agent*
*Date: 2026-07-08*
*This is a re-review (Iteration 1) following a previous QC cycle*
