# M2: Multi-Chimera Parameter Phase Diagram — Stability Boundary Mapping

**Date**: 2026-06-03
**Phase**: Planner (M2 design)
**Preceded by**: M1 (Go/No-Go — double chimera CONFIRMED)
**Status**: Design Draft — Ready for review

---

## 1. Motivation

M1 confirmed that double chimera coexistence is possible under piecewise cosine coupling, with the following robust findings:

- Double chimera observed at **all** K_transition values [0.0, 0.8]
- Occurrence rate ~33% (1/3 of runs show double chimera; rest collapse to global sync)
- K_transition independence: outcome invariant across the entire scanned range
- r_A ~ 0.94-0.99, r_B ~ 0.95-0.97 (both domains show high-sync chimera)
- T_transient >= 50000 required for reliable detection

**The critical question M2 answers**: *Which combinations of (eps_A, eps_B, K0) produce double chimera, and where is the stability boundary?*

M1 held eps_A = eps_B = 0.6, K0 = 1.0 fixed — a single point in parameter space. M2 must map the full landscape to locate:
1. The **double-chimera basin** (where both domains sustain chimera)
2. The **single-chimera basin** (only one domain shows chimera)
3. The **double-sync basin** (both domains globally synchronized, no chimera)
4. The **asymmetric basin** (one chimera + one sync, the "one-wins" state)

---

## 2. Phase Classification Scheme

Each (eps_A, eps_B, K0) run is classified into one of four phases:

| Phase | Condition | Physical Interpretation |
|-------|-----------|------------------------|
| **DC** (Double Chimera) | chimera_A AND chimera_B | Both domains in Phase III (Abrams-Strogatz chimera) |
| **SC** (Single Chimera A) | chimera_A AND NOT chimera_B | Domain A chimera, B collapses to sync |
| **SC** (Single Chimera B) | NOT chimera_A AND chimera_B | Domain B chimera, A collapses to sync |
| **DS** (Double Sync) | NOT chimera_A AND NOT chimera_B | Both domains globally synchronized |
| **MS** (Mixed) | chimera_A AND chimera_B intermittently | Phase-slip or metastable regime |

**Chimera detection criteria** (per domain, identical to M1):

```
is_chimera = max(sector_syncs) > 0.8 AND min(sector_syncs) < 0.3
```

with `n_sectors = 8` per domain.

This aligns with the **UNIFIED-FRAMEWORK Theorem (Phase III criterion)**: chimera is a metastable state with r_max/r_min >= 3, distinguishing it from gradient locking (uniform sync) and complete desynchronization.

---

## 3. Parameter Scan Grid

### Fixed Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N (total oscillators) | 1500 | M1 baseline, per-domain >= 500 |
| domain_boundaries | [0.4, 0.5, 0.9] | M1 configuration |
| delta | 0.15 | M1 baseline (B domain offset) |
| K_transition | 0.3 | Fixed (M1 showed independence; pick mid-range) |
| T_transient | 50000 | r23 compliant |
| T_measure | 50000 | r23 compliant |
| dt | 0.02 | M1 standard |
| Runs per point | 3 (seeds 42, 43, 44) | M1 standard |

### Scanned Parameters

#### eps_A (Domain A heterogeneity)

| Step | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Count | 10 steps |

- eps_A < 0.3: coupling is nearly uniform in Domain A — M-T1 suggests chimera unlikely
- eps_A = 0.6: M1 baseline, confirmed chimera
- eps_A > 0.8: strong heterogeneity may induce desynchronization or global sync

#### eps_B (Domain B heterogeneity)

| Step | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Count | 10 steps |

Same range. Asymmetric (eps_A != eps_B) scans are important because M1 revealed inherent domain asymmetry.

#### K0 (Global coupling baseline)

| Step | 0.4 | 0.6 | 0.8 | 1.0 | 1.2 | 1.4 | 1.6 |
|------|-----|-----|-----|-----|-----|-----|-----|
| Count | 7 steps |

- K0 < 0.5: weak coupling — M-T2 suggests chimera requires sufficient coupling to sustain phase clusters
- K0 = 1.0: M1 baseline
- K0 > 1.4: strong coupling favors global synchronization over chimera (competition between sync and chimera stability)

### Total Grid Size

```
eps_A: 10 steps
eps_B: 10 steps
K0:    7 steps
Grid points: 10 × 10 × 7 = 700
```

### Runs and Total Trajectories

```
700 grid points × 3 runs = 2,100 trajectories
```

---

## 4. Expected Phase Structure

Based on established chimera theory (Abrams-Strogatz 2004, Bera et al. 2015, Jafari et al. 2018) and M1 results, we predict:

### Region 1: Double-Chimera Basin (Low-to-Moderate K0, Moderate eps)

| Region | eps_A | eps_B | K0 | Rationale |
|--------|-------|-------|-----|-----------|
| DC-core | 0.4-0.8 | 0.4-0.8 | 0.8-1.2 | M1 baseline neighborhood; chimera most stable |
| DC-edge | 0.3-0.9 | 0.3-0.9 | 0.6-1.4 | Transition region; intermittent chimera |

In this region, we expect to find a connected DC basin centered around the M1 point (eps=0.6, K0=1.0). The basin boundary marks the **stability boundary** — the critical transition from DC to DS or DC to single-chimera.

### Region 2: Single-Chimera Asymmetric Band

| Region | eps_A | eps_B | K0 | Rationale |
|--------|-------|-------|-----|-----------|
| SC_a-edge | 0.0-0.3 | 0.5-0.8 | 0.8-1.2 | Domain A too uniform for chimera |
| SC_b-edge | 0.5-0.8 | 0.0-0.3 | 0.8-1.2 | Domain B too uniform for chimera |

When one domain has low eps (< 0.3), it behaves like a nearly-uniformly-coupled ring. Per D4-S18-r18c, uniform coupling cannot sustain chimera. Only the domain with sufficient heterogeneity forms chimera.

### Region 3: Double-Sync Plateau

| Region | eps_A | eps_B | K0 | Rationale |
|--------|-------|-------|-----|-----------|
| DS-strong | any | any | 1.4-1.6 | Strong coupling overwhelms chimera |
| DS-weak | 0.0-0.2 | 0.0-0.2 | 0.4-0.8 | Too little heterogeneity |

### Region 4: Mixed/Phase-Slip (Interfacial Region)

The boundary between DC and DS regions is expected to show:
- Intermittent chimera (runs switch between DC and DS)
- Phase slips near domain boundaries
- Correlation peaks at specific tau in C_AB(tau)

This corresponds to the **M-T3 phase-slip criticality**: the slip rate should diverge near the stability boundary with a critical exponent beta.

---

## 5. Computational Cost Estimate

### Per-Trajectory Cost

```
T_transient + T_measure = 100,000 time steps
Per step: N=1500 oscillators, nearest-neighbor ring coupling (2 shifts + 1 dot per step)
FLOP per step: ~2 × N = 3,000 (vectorized NumPy)
FLOP per trajectory: 3,000 × 100,000 = 3 × 10^8
```

Total for all trajectories:
```
2,100 trajectories × 3 × 10^8 FLOP = 6.3 × 10^11 FLOP
```

### Wall-Clock Estimate (CPU single core)

Python/NumPy with vectorized nearest-neighbor ring coupling runs at approximately 50-100 microseconds per time step for N=1500:

```
Per trajectory: 100,000 × 75e-6 = 7.5 seconds
Total: 2,100 × 7.5 = 15,750 seconds = ~4.4 hours
```

**With 3 runs per point, including I/O overhead: estimate 5-6 hours on a single modern CPU core.**

### GPU / Parallel Estimate

The scan is embarrassingly parallel (no inter-run dependencies). With N cores:
```
Total wall time: ~5.4 hours / N
```

### HPC Budget

For a modest cluster with 32-64 nodes (24 cores each):
```
Full scan: ~5.4 hours / 768 cores = < 1 minute of wall-clock (with parallelism)
I/O overhead dominates; realistic estimate: 10-30 minutes on 768 cores
```

---

## 6. Fast Prototyping Mode

Before running the full 2,100-run scan, we should validate with a rapid pilot to check parameter range choices and refine grid spacing near the expected DC basin boundary.

### Pilot Mode Parameters

| Parameter | Full Mode | Pilot Mode |
|-----------|-----------|------------|
| eps_A steps | 10 (0.1-1.0) | 5 (0.3, 0.5, 0.6, 0.7, 0.9) |
| eps_B steps | 10 (0.1-1.0) | 5 (0.3, 0.5, 0.6, 0.7, 0.9) |
| K0 steps | 7 (0.4-1.6) | 4 (0.8, 1.0, 1.2, 1.4) |
| Grid points | 700 | 100 |
| Runs per point | 3 | 3 |
| Total runs | 2,100 | 300 |
| T_transient | 50,000 | 20,000 |
| T_measure | 50,000 | 20,000 |
| Est. wall time | 5-6 hours | 1-2 hours |

The pilot scan retains M1-proven parameter ranges and eliminates low-eps corners (eps < 0.3) where chimera is known to be unlikely. It provides sufficient resolution to:
1. Validate that the DC basin is centered near (eps=0.6, K0=1.0)
2. Identify approximate stability boundaries
3. Determine if K0 < 0.8 or K0 > 1.4 needs finer resolution

### Progression Plan

1. **Run pilot mode** (300 runs, 1-2 hours)
2. **Plot preliminary phase diagram** — eps_A vs eps_B heatmap at K0=1.0
3. **Refine grid** — denser sampling near boundary regions identified in pilot
4. **Run full mode** on refined grid
5. **Post-process** — fit phase boundaries, compute transition order parameters

---

## 7. Output Format

For each grid point, the output records:

```json
{
  "params": {"eps_A": 0.6, "eps_B": 0.6, "K0": 1.0, "K_transition": 0.3},
  "grid_position": [5, 6, 4],
  "runs": [
    {
      "seed": 42,
      "phase": "DC",
      "chimera_A": true, "chimera_B": true,
      "r_A_sector_syncs": [0.12, 0.94, 0.15, 0.88, 0.10, 0.91, 0.18, 0.85],
      "r_B_sector_syncs": [0.14, 0.96, 0.11, 0.93, 0.13, 0.97, 0.09, 0.95],
      "global_sync": 0.87,
      "sync_score_A": 0.82,
      "sync_score_B": 0.86,
      "cross_corr_peak": 0.15
    },
    ...
  ],
  "summary": {
    "dc_fraction": 0.33,
    "sc_a_fraction": 0.33,
    "sc_b_fraction": 0.00,
    "ds_fraction": 0.33,
    "mean_r_A": 0.95,
    "mean_r_B": 0.96,
    "phase": "DC"
  }
}
```

### Visualization

1. **Phase diagram heatmaps** — eps_A vs eps_B colored by dominant phase at each K0 slice
2. **Contour plot** — double-chimera fraction f_DC as a continuous field in (eps_A, eps_B, K0) space
3. **Stability boundary extraction** — isolate surface f_DC = 0.5 (boundary between chimera-sustaining and chimera-failing regions)
4. **Cross-domain correlation** — mean C_AB(tau) peak vs. f_DC for each phase region

---

## 8. Connection to UNIFIED-FRAMEWORK

### Theorem: Layered Coupling Consistency (Theorem 3)

The theorem requires:
$$\frac{1}{M}\sum_{m=1}^{M} [R_m(t) - \bar{R}(t)]^2 \leq \epsilon(t) \to 0$$

For M=2 double chimera, R_A and R_B evolve independently, so this condition is violated. M2 tests whether this **deviation from consistency is bounded**:

```
Delta_R_squared = mean((r_A(t) - r_B(t))^2)  for t in [T_transient, T_transient+T_measure]
```

In the DC region, Delta_R should be moderate (chimera is asymmetric by nature). In the DS region, Delta_R -> 0. The **transition** from moderate to vanishing Delta_R defines a consistency-breaking boundary.

### Theorem: Emergent Autonomy = Symmetry Breaking Rate (Theorem 4)

For multi-chimera systems:
```
A_multi = d/dt [H(R_A) + H(R_B)]
```

where H is the entropy of the local order parameter distribution across time windows. The DC region should show higher A_multi than DS (more symmetry broken = more autonomy).

### Abrams-Strogatz Phase III Criterion

Per the UNIFIED-FRAMEWORK synthesis of Abrams-Strogatz (2004):
- Phase I: complete synchronization (all sector sync > 0.95)
- Phase II: partial synchronization (0.5 < max_sync < 0.95, no min_sync < 0.3)
- Phase III: chimera (max_sync > 0.8, min_sync < 0.3)
- Phase IV: locked/gradient locking (spatially monotonic sync)

The sector-based detection criterion (max > 0.8, min < 0.3) is a direct implementation of the Phase III diagnostic.

---

## 9. Link to M3 (I_C Topology) and M4 (Phase-Slip Dynamics)

### M3 (I_C Topology) — Uses M2 output

The steady-state phase fields theta_final(x) from M2 provide direct input to:
- Persistent homology computation on the sync-rate field r(x)
- I_C estimation per grid point
- Verification of M-T2: I_C = M in DC region

The pilot mode already generates phase data suitable for this analysis.

### M4 (Phase-Slip Dynamics) — Informed by M2 boundary

The boundary between DC and DS regions is where phase slips are most likely. M2 identifies the parameter coordinates for M4's phase-slip study. The intermittent chimera region in M2 (where f_DC ~ 0.33, i.e. DC appears in 1/3 of runs) is a natural target for M4's long-time simulation (>100,000 time units).

---

## 10. Expected Discoveries and Risks

### Potential Discoveries

1. **DC basin boundary shape**: The stability boundary in (eps_A, eps_B, K0) space may reveal whether the boundary is a sphere (isotropic to perturbations), an ellipsoid (preferred direction of perturbation), or has fractal features (critical behavior).

2. **Asymmetric chimera stability**: If one domain requires significantly higher eps than the other to sustain chimera, this would imply asymmetry in chimera robustness — possibly related to domain size difference.

3. **K0 as master variable**: If the DC basin extends across all eps values but collapses above a critical K0, this identifies K0 as the primary control parameter.

4. **Critical scaling**: Near the DC-DS boundary, f_DC may follow power-law scaling f_DC ~ |p - p_c|^beta, connecting to M-T3 critical exponents.

### Risks and Mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| DC basin is much smaller than expected (isolated point) | Low | Pilot mode confirms extent; if too small, abandon M2 with clear characterization |
| All runs produce global sync (DC never observed) | Low (M1 already confirmed) | If pilot shows this, triple check T_transient and sector detection |
| K0 stability boundary is very sharp, pilot misses it | Medium | Use pilot to bound region; full mode increases K0 resolution if needed |
| Computational budget insufficient for full scan | Medium | Parallelize across cluster; fast pilot mode reduces risk |
| Domain asymmetry masks true phase structure | Low | Output per-domain results separately; inspect both domains' chimera frequency independently |

---

## 11. Summary

M2 maps the 3D parameter space (eps_A, eps_B, K0) at fixed K_transition=0.3 to locate the stability boundary of double chimera coexistence.

**Core deliverables**:
1. Phase diagram classifying 700 grid points into DC/SC/DS/MS phases
2. Extraction of stability boundary surface f_DC = 0.5
3. Confirmation or refutation of K0 as master control parameter
4. Dataset for M3 (I_C topology analysis) and M4 (phase-slip boundary parameters)

**Total computational cost**: 2,100 trajectories, ~5-6 hours single-core, ~30 min on 768-core cluster
**Fast prototyping**: 300 pilot trajectories, ~1-2 hours single-core

---

## 12. Implementation Plan

### File Modifications

The existing `experiment_chimera_spatial_coupling.py` already supports the piecewise coupling and per-domain detection needed for M2. Only a new driver script is required:

**New file**: `labs/simulations/multi_chimera_m2_phase_diagram.py`

```
Function: run_phase_diagram(eps_a_range, eps_b_range, k0_range, ...)
  - Iterates over all grid points
  - Calls run_chimera_experiment for each (eps_a, eps_b, k0)
  - Aggregates results and classifies phases
  - Outputs:
    1. JSON file with per-run data
    2. Phase diagram heatmap (matplotlib)
    3. Summary statistics
```

No changes to the core simulation or detection code are needed — M1 already exercised the full pipeline.

### Suggested parallel execution

```python
import concurrent.futures
from itertools import product

eps_a_grid = np.arange(0.1, 1.1, 0.1)
eps_b_grid = np.arange(0.1, 1.1, 0.1)
k0_grid = np.arange(0.4, 1.7, 0.2)

grid = list(product(eps_a_grid, eps_b_grid, k0_grid))
# 700 grid points

with concurrent.futures.ProcessPoolExecutor(max_workers=768) as executor:
    futures = [executor.submit(run_single_point, *params, run_id) for params in grid for run_id in range(3)]
    for f in futures:
        result = f.result()
        aggregate(result)
```

---

*Design completed: 2026-06-03*
*Ready for review by researcher(s) before 2-loop execution*
