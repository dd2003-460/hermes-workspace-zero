# Multi-Chimera Coupled Dynamics: Review Report

**Reviewer**: Reviews agent
**Date**: 2026-06-03
**Source document**: researches/MultiChimera-CoupledDynamics.md (298 lines, 4 experiments)
**Phase**: reviewer

---

## Code Connection Audit

| Referenced Code | Document Claims Actual Location | Real Location | Can Be Imported? |
|----------------|--------------------------------|---------------|------------------|
| `chimera_detector.py` | `chimera_lab/` | `labs/simulations/chimera_detector.py` | YES (with path fix) |
| `chimera_diagnostic_v2.py` | `labs/simulations/` | `labs/simulations/chimera_diagnostic_v2.py` | YES |
| `experiment_chimera_spatial_coupling.py` | `labs/simulations/` | `labs/simulations/experiment_chimera_spatial_coupling.py` | YES |
| `detect_m_phase.py` | referenced in INDEX | `labs/simulations/detect_m_phase.py` | YES |

**Verdict**: Paths for chimera_detector.py are **INCORRECT**. The design references `chimera_lab/chimera_detector.py` which does not exist. All 3 other code references are correct.

---

## Experiment-by-Experiment Review

### M1: Domain-Partitioned Chimera (分段域 chimera)

**Connection to existing code**: PARTIAL PASS

- The design proposes modifying `experiment_chimera_spatial_coupling.py` to support multiple domains with different K(x) functions.
- **EXISTING**: `experiment_chimera_spatial_coupling.py` uses nearest-neighbor ring coupling (O(N) per step) with a SINGLE K(x) = K0*(1+eps*cos(2pi*x)). It has no multi-domain logic.
- **IMPLEMENTATION GAP**: The existing code only handles 10 spatial sectors for measurement. To support 3 distinct chimera domains, the spatial coupling function must be restructured from a single cosine to a piecewise definition. This is a significant code change, not an extension.
- **ChimeraDetector usage**: The design proposes using `ChimeraDetector` per domain (lines 167-175). The detector works on arbitrary phase arrays of any size. However, `ChimeraDetector.__init__` defaults to `n_windows=5` which assumes uniform windowing of an agent array. For domain slices of different sizes (e.g., N_A=200, N_B=200, N_C=400), n_windows must be manually adjusted per domain.
- **ChimeraDiagnosticV2 multi-domain support**: The design assumes ChimeraDiagnosticV2 can process domain slices independently. However, `ChimeraDiagnosticV2.compute_segment_sync()` partitions the FULL N agents into sectors. To use it for domain detection, the entire diagnostic class needs a `domain_mask` parameter.

**M1 Verdict**: NEEDS_REVISION (see recommendations below)

---

### M2: Coupled DOF Parameter Phase Diagram

**Connection to existing code**: PASS (with caveats)

- The design references ChimeraDetector for chimera scoring and ChimeraDiagnosticV2 for classification. Both are available.
- The parameter space (K0 x eps x delta x K_transition) requires 8,512 runs. This is purely an execution problem, not a code problem.
- **GAP**: There is no existing parameter scan infrastructure that supports multi-domain configurations. `scan_chimera_parameter_space/` and `scan_chimera_parameter_space.py` both operate on single-domain configurations.
- The design uses "quick scan" settings (T_transient=2000, T_measure=500) that are shorter than r23 recommendations (T>50000, see D4-S18-r23-p1 parameter constraints). This creates a risk of false positive chimera detection due to insufficient transient removal.

**M2 Verdict**: NEEDS_REVISION (parameter scan durations too short; no multi-domain scan infrastructure)

---

### M3: I_C Topology in Multi-Chimera Systems

**Connection to existing code**: FAIL

- The design proposes persistent homology (Vietoris-Rips complex) on the sync-rate field r(x,t).
- **NO EXISTING CODE** implements persistent homology computation anywhere in the project. The `detect_m_phase.py` uses k-means and density thresholding -- not topology.
- The information-theoretic approach (I_C ≈ H(spatial_r) - H(temporal_r)) uses basic numpy operations (histogram, entropy) which are feasible but have no existing wrapper.
- The mixed method (I_C_multi = b_1 + |H_1(velocity_field)) has no implementation skeleton.

**M3 Verdict**: FAIL -- requires writing new persistent homology code from scratch (or adding scipy/intervalt dependency). This is the most complex and least connected experiment.

---

### M4: Phase Slip Dynamics & Energy Landscape

**Connection to existing code**: FAIL

- The design proposes an effective Hamiltonian H and free energy estimation via F = -kT ln(Z).
- Kuramoto/chimera systems are DETERMINISTIC, not stochastic. The thermal fluctuation framework (kT, Z, free energy) is not a natural mapping. A proper Hamiltonian formulation would require the Lindbladian or the oscillator Lyapunov function, which is non-trivial.
- **NO existing code** in the project computes Hamiltonians, Lyapunov exponents, or free energy landscapes for chimera systems.
- The design assumes "thermal-like fluctuation" in the phase-slip region. In a deterministic oscillator system, this would be chaotic dynamics, not thermal noise. The interpretation needs careful grounding.

**M4 Verdict**: FAIL -- requires substantial new theoretical and computational work beyond what exists.

---

## UNIFIED-FRAMEWORK Theorem Consistency

### Theorem 3 (Multi-level Coupling Consistency)

The design correctly identifies tension: multi-chimera systems are inherently "inconsistent" (different chimera regions have independent dynamics). The proposed revision (allowing R_m != R_{m'} as a new emergent behavior) is reasonable.

**Assessment**: The design points out a real gap in the theorem but does not propose a specific, testable modification. The revision formula is more of an observation than a formal claim.

**Score**: 6/10 (identification is good, formalization is weak)

### Theorem 4 (Emergent Autonomy = Symmetry Breaking Rate)

The design proposes A_multi = d/dt sum_m H(R_m), which generalizes the single-chimera A = -d/dt H(phi). This is a valid generalization.

**Assessment**: However, H(R_m) is the entropy of the sync-rate distribution in domain m, which is not the same symmetry as the global symmetry breaking in Theorem 4. The connection to "symmetry breaking" is tenuous for domain-partitioned systems.

**Score**: 5/10 (plausible but loosely justified)

---

## Cross-Cutting Issues

### 1. R18c Direct Contradiction

The design relies on the hypothesis that multi-chimera (M>=2) can coexist. However, **D4-S18-r18c concluded** that in uniform coupling, M>=2 intermediate states DO NOT EXIST. The M1 design correctly shifts to *spatially heterogeneous* coupling as the proposed pathway, which is consistent with r18c's correction #2 ("multi-phase condensation requires non-uniform coupling"). However, the design should explicitly cite that it is testing the **only remaining hypothesis** for multi-chimera existence after r18c's elimination of the uniform coupling path.

### 2. The chimera_detector API mismatch

The design calls `detector.detect(phase_A, history=history_A)` and expects the result to contain `det_A.phase == ChimeraPhase.PHASE_III_CHIMERA_STABLE`. This is correct -- `detect()` returns a dict with `phase` key. However, the `history` parameter is `np.ndarray [T, 2]`, not an instance attribute. The design's intent is correct but the history management across multiple domains (each needing its own history buffer) is non-trivial.

### 3. N=800 vs N=500

The design proposes N=800 for M1. r20 confirmed N>=500 is the threshold for stable chimera. For 3 domains, the effective system size per domain is N/3 ~ 267. Since chimera formation depends on LOCAL density of oscillators, and the chimera exists within each domain (not globally), N=800 (267 per domain) may be marginal. The design should validate N>=400 per domain (total N>=1200) for M1.

### 4. Phase slip measurement (M1/M4)

The design proposes counting "integer winding events" of phase accumulation. This requires integrating d(theta)/dt for each domain and counting topological crossings. No existing code does this. The approach is theoretically valid but needs a new `phase_winding_counter.py` module.

---

## Recommendations

1. **For M1 (priority 1)**:
   - Fix the import path to `chimera_detector.py` (use `labs/simulations/`)
   - Extend `experiment_chimera_spatial_coupling.py` with a `domain_coupling` parameter that overrides the single K(x) with a piecewise definition
   - Add domain-aware history tracking to ChimeraDetector (or use separate detector instances per domain)
   - Start with N=1000 (333 per domain) for initial verification

2. **For M2 (priority 2)**:
   - Increase T_transient to at least 5000 (per r23 guidelines)
   - Build a scan driver that handles the multi-domain parameter set. Consider using `scan_chimera_parameter_space.py` as a base but adding domain-aware coupling

3. **For M3 (priority 3)**:
   - Use `scipy.spatial.Delaunay` + `ripser` library for persistent homology, OR simplify to a proxy metric (e.g., count of connected components in the sync-rate thresholded field)
   - Information-theoretic approach is lower cost and should be implemented as a backup/alternative to persistent homology

4. **For M4 (priority 4)**:
   - Abandon the free energy/thermal analogy. Instead, compute Lyapunov exponents or use a Poincare section approach for the phase-slip dynamics
   - Consider replacing M4 with a "phase slip = sign change of dR/dt in each domain" count, which requires no new theory

5. **Theoretical**:
   - Explicitly cite D4-S18-r18c as the eliminator of uniform-coupling multi-chimera
   - Frame M1 as the "smoking gun" test of the non-uniform coupling hypothesis
   - Theorem 3 and Theorem 4 connections should be treated as "motivational" rather than "verification targets"

---

## Summary Scoring

| Experiment | Code Connected | Measurements Feasible | Theory Consistent | Verdict |
|-----------|---------------|----------------------|-------------------|---------|
| M1 | PARTIAL (path fix needed) | YES | PARTIAL (theorem 3 gap) | NEEDS_REVISION |
| M2 | PARTIAL (scan infra missing) | YES (with higher T) | NO | NEEDS_REVISION |
| M3 | NO (no persistent homology) | NO (needs new code) | PARTIAL | FAIL |
| M4 | NO (no Hamiltonian code) | NO (thermal analogy flawed) | WEAK | FAIL |

### Overall Verdict: NEEDS_REVISION

### Confidence Score: 0.75

The design correctly identifies a meaningful scientific question (multi-chimera coexistence) and connects it to established code (ChimeraDetector, ChimeraDiagnosticV2, spatial coupling experiment). The main issues are:

- Code paths are wrong in 1 of 3 references
- Experiments M3 and M4 are disconnected from existing code and require significant new implementation
- M1/M2 are feasible but require careful implementation (domain partitioning, extended transient times)
- Theorem 3 and Theorem 4 connections are motivational, not operational

### Suggested Revision Path

Run M1 with minimal scope (2 domains, N=600, K_transition=[0, 0.5]) before committing to the full 4-experiment design. If M1 fails to produce multi-chimera coexistence, the theoretical foundation collapses and M2-M4 become moot. This is a "go/no-go" experiment.

### If REVISION ACCEPTED:

1. Executor agent should modify `experiment_chimera_spatial_coupling.py` to support 2-domain partitioning
2. Use separate `ChimeraDetector` instances (n_windows=4 per domain, not 10 globally)
3. Confirm or refute M1 before proceeding to parameter scans
4. M3 and M4 should be demoted to "phase 3" status with simplified implementations

---

*Review complete. Document written to researches/MultiChimera-Review.md*
