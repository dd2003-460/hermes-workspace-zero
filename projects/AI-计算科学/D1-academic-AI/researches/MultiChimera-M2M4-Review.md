# Review: M2 + M4 Joint Design Review

**Date**: 2026-06-03
**Reviewer**: M2 + M4 joint review
**Status**: M2 NEEDS_REVISION (minor), M4 PASS

---

## M2: Multi-Chimera Parameter Phase Diagram

### Verdict: NEEDS_REVISION

### PASS items

1. **Scientific rationale**: Excellent motivation. Mapping the (eps_A, eps_B, K0) 3D phase diagram to locate stability boundaries is the natural next step after M1's single-point confirmation. The five-phase classification (DC, SC-A, SC-B, DS, MS) is physically well-motivated.

2. **Grid design**: 10x10x7 = 700 grid points is well-scoped. The pilot-to-full progression plan is prudent — validates parameter ranges before committing to full scan. The asymmetric epsilon scanning correctly captures domain asymmetry observed in M1.

3. **Detection consistency**: Phase classification criterion (max_sync > 0.8 AND min_sync < 0.3, n_sectors=8) is identical to M1, ensuring continuity. Reference to unified framework theorems is appropriate.

4. **Implementation plan**: Creating a new driver script (`multi_chimera_m2_phase_diagram.py`) that calls the existing `run_chimera_experiment` is minimal and correct. No modifications to core simulation code needed.

5. **Visualization plan**: Phase diagrams, contour plots, and boundary extraction (f_DC = 0.5) are standard and well-scoped.

### Issues requiring revision

#### Issue 1 (REVISION): Pilot T_transient = 20K is too short

**Priority: HIGH**

M1 critical finding: the "fast mode false negative" bug. With T_transient=30K + T_measure=3K, Domain B showed r_B = 0.566 (chimera-indistinguishable from gradient locking) and all 3 runs produced 0/3 double chimera by primary detection. Only with T_transient=50K did chimera become reliably detectable.

M2 pilot uses T_transient=20K and T_measure=20K. **This is worse than the fast mode that produced false negatives.** At 20K transient, the pilot could:

- Miss chimera in boundary-region parameter points where chimera requires longer transient to emerge
- Incorrectly classify a grid point as "double-sync" when it would become "chimera" with 50K
- **Distort the pilot phase diagram**, potentially moving boundary estimates outward (overestimating DS region)

The pilot produces results that will be **consumed by both M2 (grid refinement) and M4 (boundary identification for phase-slip study)**. Incorrect boundaries at pilot stage propagate to both downstream experiments.

**Fix**: Set pilot T_transient >= 50K, T_measure >= 30K. This doubles pilot wall time from ~1 hour to ~2 hours, still within budget. A 50K transient for 300 pilot runs is ~20K seconds (~5.6 hours). Acceptable trade-off.

#### Issue 2 (INFORMATIONAL): Timing estimates are overstated by ~3x

The designs cite 50-100 μs/step (M2) and 50 μs/step (M4). Actual benchmark: **21.3 μs/step** for N=1500 vectorized nearest-neighbor ring coupling.

Implications:
- **M2**: Estimated 5-6 hours should be ~1.5-2 hours (simulation only). 300 pilot runs should be ~5-6 hours total, not 1-2 hours.
- **M4**: Protocol A 500K steps should be ~11 seconds per chimera seed, not ~37 seconds.
- **M4**: Protocol B 500 runs × 50K steps should be ~21 minutes, not ~31 minutes.

This is favorable — actual cost is lower than estimated. But ensure that I/O, ChimeraDetector calls per snapshot (M4), and post-processing are factored in separately.

#### Issue 3 (MINOR): Full-scan transient time should match M1

Full scan specifies T_transient=50K, T_measure=50K, which is M1-consistent. Good. But the grid specification at eps_A=0.1 and eps_B=0.1 (very weak coupling) may produce different transient requirements than the M1 point. Monitor this if pilot boundaries at low-eps corners behave unexpectedly.

#### Issue 4 (MINOR): Mixed/Slip classification is vague

The "MS (Mixed)" phase for "chimera_A AND chimera_B intermittently" needs an operational definition. Intermittency on what timescale? Over the 50K measure window, can you actually observe chimera-to-sync transitions? At 21.3 μs/step, measuring the full 50K transient+measure = 1.1 seconds wall time. The output JSON does not include per-timestep local r_s(t), only final domain classification. This means **M2 cannot detect "intermittent chimera" or phase slips** — it only sees the end state.

If MS is important for boundary mapping, the output format should include at least a time-series of domain r_A(t) and r_B(t) over the measure window (50,000 values stored as float32 per domain per run). Otherwise, the MS class should be removed or redefined as a post-hoc flag.

---

## M4: Phase-Slip Dynamics

### Verdict: PASS (with notes)

### Strengths

1. **Question is well-defined**: Resolving whether chimera is a coexisting attractor (H1) vs metastable (H2) vs intermittent (H3) is the central theoretical question. Protocol A's direct discrimination of H1 vs H2 via survival function S(T) is the cleanest experimental design I can imagine for this question.

2. **Dual-criterion phase-slip detection**: The algorithm requiring BOTH (a) r_s drop from >0.7 to <0.3 AND (b) phase variance spike is correct. A coherence drop alone could be a slow gradual decay (real physical process), but adding the variance spike criterion eliminates false positives. Good.

3. **4-protocol structure is independent**: Protocols A (lifetime), B (basin), C (slip rate vs K), D (PSD) answer distinct questions with complementary methods. No waste.

4. **Collapse window = 10,000 timesteps**: This correctly distinguishes transient phase slips (resolve in <10K steps) from genuine collapse. The ratio of collapse window (10K) to total simulation length (500K) is reasonable (2% dead-time near each endpoint).

5. **Phase-slip tracker architecture**: The `PhaseSlipTracker` is a clean extension of the existing ChimeraDetector. It correctly handles per-sector history tracking and recovery detection.

6. **Literature grounding**: Hannay et al. 2015 (exponential lifetime scaling with N) and Killian & Cosmai 2017 (front dynamics) are precisely the right references for this problem.

### Notes for implementation

#### Note 1: Phase-slip tracker signature mismatch

In the design spec (Section 4), `PhaseSlipTracker.__init__` does not accept a `_domain_id` parameter, but `detect_slips` references `self._domain_id` at line 171 (`'domain': self._domain_id`). This is a simple fix — add `domain_id: int = -1` to the constructor. The tracker will be instantiated once per domain, so domain_id is needed for output attribution.

#### Note 2: Phase variance computation is not trivial

The `detect_slips` signature takes `sector_phase_vars` as an argument. Computing phase variance requires access to per-oscillator theta within each sector, not just the pre-aggregated r_s values. The PhaseSlipAnalyzer must receive theta snapshots (not just order parameters) or compute sector variance internally.

This does not change the protocol — the output format (saving state every 500 steps) already preserves theta. But the implementation must compute `sigma_phase = Var(theta_i)` within each sector for each PhaseSlipTracker invocation.

#### Note 3: Snapshot frequency vs slip detection frequency

The spec says "tracker is invoked every 10 timesteps during Protocol A/C" but state is saved every 500 timesteps. If detection is between snapshots, the transient slip events between 500-step intervals would be missed.

Recommendation: Either (a) compute r_s(t) at every 10 steps using the full theta vector (cheap — just a np.exp(1j*theta) mean per sector), or (b) invoke PhaseSlipTracker on every snapshot window, accepting lower temporal resolution (500 steps vs 10 steps).

Since phase slips are described as O(10-100 timesteps long (Section 2.2), 500-step resolution would miss most slips. **Go with option (a): compute r_s per 10 steps and run tracker, but only store results (not raw theta) at every 500 steps.**

#### Note 4: Protocol C with K_transition scan is low value

M1 already demonstrated K_transition independence across [0.0, 0.8] — identical 1/3 chimera rate at all values. Protocol C's hypothesis ("phase-slip rate is independent of K_transition") is already confirmed. Protocol C costs ~90 seconds (negligible) but adds limited insight.

Recommendation: Merge Protocol C's runs into additional Protocol A runs at key boundary parameters (from M2 pilot) instead. If the team wants to preserve Protocol C for archival completeness, keep it.

#### Note 5: Sampling resolution for Protocol D (PSD)

Protocol D computes PSD of r_s(t) over 500K timesteps. The Nyquist frequency for this series (dt=0.02) is f_Nyquist = 1/(2*0.02) = 25 Hz. Phase slips on timescales of O(10-100 steps) correspond to frequencies of 50-500 Hz — above Nyquist.

If PSD reveals peaks, they would correspond to slow modulations (O(>200 steps)). Fast phase slips (10-100 steps) would appear only as broadband noise. This is physically correct — PSD analysis is designed to find periodic drivers, not fast stochastic events. The spec is correct in interpretation.

Just flag this for the implementor: **PSD will detect resonance-driven dynamics (slow, coherent excitations) but not fast stochastic slips.** If the protocol aims to detect the dominant mechanism, this resolution is fine.

---

## Overlap Analysis: M2 vs M4

### Independence: HIGH

M2 and M4 address fundamentally different questions:

| | M2 | M4 |
|---|---|---|
| **Question** | "Where does chimera exist?" | "Why 33%?" |
| **Method** | 2D+3D parameter grid scan | Long-time simulation + perturbations |
| **Output** | Phase boundaries | Lifetime distribution, basin structure |
| **Timescale** | 100K steps (end-state snapshot) | 200K-500K steps (full dynamics) |
| **Phase-slip info** | None (end-state only) | Central measurement |

They are **not** independent only in that M2 identifies boundary parameters used by M4 (the M2→M4 connection in Section 9). But this is a proper handoff, not overlap — M4 benefits from M2 results.

### No duplication of experiments detected.

---

## Revised Cost Summary (with actual benchmark)

Benchmark: **21.3 μs/step** for N=1500 nearest-neighbor vectorized simulation.

### M2 costs
| Component | Estimate (design) | Actual |
|---|---|---|
| Pilot (300 runs × 100K) | 1-2 hours | 5-6 hours with T_transient >= 50K |
| Full scan (2,100 runs × 100K) | 5-6 hours | 1.5-2 hours |
| **Total** | **5-6 hours** | **7-8 hours** (mostly from pilot) |

The pilot dominates wall time once T_transient is corrected. This is still a single-session computation.

### M4 costs
| Component | Estimate (design) | Actual |
|---|---|---|
| Protocol A (3 × 500K) | ~110 seconds | ~32 seconds |
| Protocol B (500 × 50K) | ~31 minutes | ~21 minutes |
| Protocol C (9 × 200K) | ~90 seconds | ~21 seconds |
| **Total** | **~35 minutes** | **~24 minutes** |

M4 cost estimates are inflated by ~5x but still very manageable.

---

## Action Items for Executor

### M2:
1. Set pilot T_transient = 50,000, T_measure = 30,000 (not 20K)
2. Add per-timestep r_A(t), r_B(t) arrays to output for each grid point (enables MS classification)
3. Factor actual benchmark (21.3 μs/step) into scheduling — expect pilot to dominate wall time

### M4:
4. Fix `PhaseSlipTracker.__init__` to accept `domain_id` parameter
5. Compute r_s per 10 steps for slip tracking (not just per 500-step snapshots)
6. Consider merging Protocol C runs into additional Protocol A boundary runs
7. Compute phase variance `Var(θ_i)` within each sector inside PhaseSlipTracker (not as external input)

---

## Go/No-Go Verdict

- **M2: NEEDS_REVISION** — Fix pilot T_transient (Issue 1 is the blocker). Items 2-4 are nice-to-have and can be addressed during implementation without halting.
- **M4: PASS** — Protocol design is physically sound, cost estimates conservative, implementation plan is complete. Notes 1-5 are implementation notes, not blockers.

**Overall: Both experiments can proceed to execution after M2 pilot T_transient fix.**
