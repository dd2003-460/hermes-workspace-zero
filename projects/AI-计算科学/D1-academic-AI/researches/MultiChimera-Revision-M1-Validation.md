# Multi-Chimera M1 Validation: Go/No-Go Experiment

**Revision**: 1 (post-reviewer-2 feedback)
**Status**: PENDING RE-APPROVAL (reviewer-2)
**Date**: 2026-06-03
**Scope**: M1 ONLY (single experiment)
**Goal**: Go/no-go decision on multi-chimera existence

---

## Problem Statement

D4-S18-r18c conclusively showed that uniform coupling cannot sustain M>=2 chimera phases. The remaining hypothesis is that **spatially heterogeneous (piecewise) coupling** can induce coexistence of multiple chimera domains.

> **M1 Objective**: Verify that two distinct chimera domains can coexist under piecewise spatial coupling K(x).

**Failure condition**: If no (K_transition, N) combination produces 2 chimera domains simultaneously, the entire multi-chimera program collapses.

---

## System Configuration

### Oscillator Array

- **N = 1500** oscillators on a ring (x_i = i/N, i = 0, ..., N-1)
- Per-domain size: N/2 = 750 > D20 threshold (N/3 >= 500 for stable chimera)
- Total N >= 1500 ensures sufficient density per domain for chimera formation

### Piecewise Spatial Coupling K(x) — 2-Domain Design

The coupling function is divided into 4 zones (2 chimera domains + 2 transition zones):

```
Domain A   [0.00, 0.40): K(x) = K0 * (1 + eps_A * cos(2*pi*x))
Transition [0.40, 0.50): K(x) = K_transition (flat, mediating domain)
Domain B   [0.50, 0.90): K(x) = K0 * (1 + eps_B * cos(2*pi*(x - delta)))
Transition [0.90, 1.00): K(x) = K_transition (flat, mediating domain)
```

Parameters:
- K0 = 1.0 (global coupling baseline)
- eps_A = eps_B = 0.6 (intra-domain heterogeneity)
- delta = 0.15 (Domain B chimera center offset)
- K_transition scanned: [0.0, 0.8] step 0.1 (8 values)

### Domain Count

Reduced from 3 domains to **2 domains** to maximize per-domain size and isolate the existence question. The 3-domain design used 267 agents per domain (N=800), which the reviewer flagged as marginal. With 2 domains at N=1500, each domain has 750 agents.

---

## Parameter Scan Protocol

### Transient and Measurement Times

- **T_transient = 50000** time units (per r23 recommendation for reliable convergence)
- **T_measure = 50000** time units (per r23 recommendation)
- Runs: 3 independent seeds per (K_transition, domain_coupling) configuration

Rationale from r23: Too-short transients (<5000) produce false-positive chimera detection because the system has not yet reached its asymptotic attractor. T_transient >= 50000 is required.

### Coupling Modes Tested

1. **Separate couplings** (primary): Each domain has its own K(x) shape
2. **Identical couplings** (control): Both domains have K(x) = K0*(1+eps*cos(2pi*x))
3. **Uniform coupling** (baseline): K(x) = K0 globally, should yield only single chimera

### Failed State (M1 FAIL)

If ALL K_transition values from 0.0 to 0.8 produce fewer than 2 simultaneous chimera domains (Phase III), then multi-chimera coexistence is ruled out and the program halts.

---

## Measurement Protocol

### 1. Local Order Parameter per Domain (Primary)

Each domain is split into sub-sectors to detect chimera state:

```python
for domain in [domain_A_indices, domain_B_indices]:
    domain_slice = theta[domain]
    n_sectors = 8  # local sub-sectors within domain
    sector_syncs = []
    for s in range(n_sectors):
        sector = domain_slice[s * len(domain) // n_sectors : (s+1) * len(domain) // n_sectors]
        sync = abs(mean(exp(1j * sector)))
        sector_syncs.append(sync)
    # Chimera detected if max(syncs) > 0.8 and min(syncs) < 0.3
    is_chimera = max(sector_syncs) > 0.8 and min(sector_syncs) < 0.3
```

### 2. ChimeraDetector per Domain (Secondary Validation)

**Key fix from reviewer**: Create SEPARATE ChimeraDetector instances per domain, each configured with appropriate n_windows.

```python
# Domain-specific detector initialization
# n_windows must match the local sector count within each domain
detector_A = ChimeraDetector(n_windows=8, gamma=0.5)
detector_B = ChimeraDetector(n_windows=8, gamma=0.5)

# Each detector processes only its domain's phase slice
phase_A = theta[domain_A_indices]
phase_B = theta[domain_B_indices]

det_A = detector_A.detect(phase_A)  # Returns dict with 'phase' key
det_B = detector_B.detect(phase_B)

# Multi-chimera confirmed if:
# det_A['phase'] == ChimeraPhase.PHASE_III_CHIMERA_STABLE AND
# det_B['phase'] == ChimeraPhase.PHASE_III_CHIMERA_STABLE
```

Note: n_windows=8 for each domain is appropriate because domain_A contains ~750 agents and we subdivide into 8 local sectors. The default n_windows=5 is too few to capture the local structure.

### 3. ChimeraDiagnosticV2 per Domain (Tertiary Verification)

**Key fix from reviewer**: ChimeraDiagnosticV2.compute_segment_sync() uses self.n and divides the full circle into sectors. To apply it to a domain, we need a domain_mask parameter or a dedicated diagnostic instance per domain.

Two approaches, prioritized:

**Approach A (preferred)**: Add domain_mask parameter to ChimeraDiagnosticV2.compute_segment_sync()
```python
def compute_segment_sync(self, theta, domain_mask=None):
    if domain_mask is None:
        domain_mask = slice(None)
    # Only use angles and positions where domain_mask is True
    theta_subset = theta[domain_mask]
    # Recompute angles from subset position indices, not full circle
```

**Approach B**: Instantiate a second ChimeraDiagnosticV2 with n=len(domain), offset positions
```python
diag_A = ChimeraDiagnosticV2(n=len(domain_A_indices), dt=0.005)
diag_B = ChimeraDiagnosticV2(n=len(domain_B_indices), dt=0.005)
diag_A.compute_segment_sync(theta, domain_mask=domain_A_mask)
```

Approach A is cleaner and should be implemented in chimera_diagnostic_v2.py.

### 4. Inter-Domain Measures

- Cross-correlation: C_AB(tau) = <R_A(t) R_B(t+tau)> - <R_A><R_B> for tau in [-T, T]
- Relative order parameter drift: |R_A(t) - R_B(t)| over time
- Synchronization transition indicator: if one domain's chimera "wins" (R_A -> 1, R_B < 0.5 or vice versa)

---

## Modified Files

### File 1: experiment_chimera_spatial_coupling.py (labs/simulations/)

The file at `labs/simulations/experiment_chimera_spatial_coupling.py` is the primary implementation target. Changes needed:

1. **Add domain_coupling parameter** to `run_chimera_experiment()`
   - When enabled, replaces the single `k_spatial[i]` with a piecewise K(x) function
   - Parameters: domain_boundaries=[0.4, 0.5, 0.9], domain_eps=[0.6, 0.6], delta=0.15, K_transition value
   - The piecewise function must produce 2 distinct chimera-friendly zones

2. **Increase T_transient** from 5000 to 50000

3. **Add dual-domain output**:
   - Compute and output per-domain chimera_score separately
   - Compute cross-domain correlation
   - Return boolean array: was_chimera_per_domain (1500 entries)

### File 2: chimera_detector.py (labs/simulations/)

Path fix from `chimera_lab/chimera_detector.py` to `labs/simulations/chimera_detector.py`.

No code changes needed in ChimeraDetector itself, but callers MUST:
- Create separate instances per domain (not reuse a single instance)
- Set n_windows to match the domain's internal sector count
- Pass domain-specific phase_slice (not the full theta array)

### File 3: chimera_diagnostic_v2.py (labs/simulations/)

Add optional `domain_mask` parameter to:
- `ChimeraDiagnosticV2.compute_segment_sync(theta, domain_mask=None)`
- `ChimeraDiagnosticV2.compute_sci(theta, domain_mask=None)`
- `ChimeraDiagnosticV2.__init__()`: store domain position offsets if needed

### File 4: new M1 driver script

Create `labs/simulations/multi_chimera_m1_validation.py`:
- Iterates over K_transition scan
- Calls modified experiment function
- Aggregates chimera_count_per_domain results
- Generates phase diagram (K_transition vs chimera_state)
- Plots final convergence data for each configuration

---

## Expected Outcomes Table

| K_transition | If M1 = TRUE (coexistence possible) | If M1 = FALSE (coexistence impossible) |
|-------------|-------------------------------------|----------------------------------------|
| 0.0 | 2 chimera domains, clear domain boundary | 1 chimera dominates or global sync |
| 0.1-0.3 | 2 chimera domains, weak coupling | 1 chimera dominates or global sync |
| 0.4-0.6 | Possible "one-wins" OR phase slip coexistence | Uniform/global chimera only |
| 0.7-0.8 | May merge into global chimera at high K_transition | Uniform/global chimera |

The "go/no-go" decision is binary:
- **GO**: At least one K_transition value (preferably K_transition < 0.5) produces 2 simultaneous chimera domains
- **NO-GO**: No K_transition value produces 2 simultaneous chimera domains

---

## Timeline (If Approved)

| Milestone | Duration | Deliverable |
|-----------|----------|-------------|
| Code modifications | 2 days | Modified experiment + driver |
| First scan (K_transition 0.0, 0.1, 0.2) | 1 day | Preliminary results |
| Full scan (8 K_transition values, 3 runs each) | 3 days | Complete phase diagram |
| Analysis + M1 verdict | 1 day | Go/no-go report |

Total: approximately 1 week if the experiment is feasible.

---

## Reviewer-2 Re-review Checklist

1. [ ] Fixed import path: `chimera_detector.py` -> `labs/simulations/`
2. [ ] Reduced to 2-domain design (not 3), N=1500 total (750 per domain)
3. [ ] Separate ChimeraDetector instances per domain with domain-appropriate n_windows
4. [ ] Added domain_mask requirement to ChimeraDiagnosticV2.compute_segment_sync()
5. [ ] Increased T_transient from 5000 to 50000 (r23 compliant)
6. [ ] K_transition scan range reduced to [0.0, 0.8] (8 steps, not 10)
7. [ ] M1 is clearly a go/no-go with defined failure condition
8. [ ] M2-M4 are explicitly deferred (Phase 2+), not simultaneous
9. [ ] D4-S18-r18c explicitly cited as the motivation for spatial heterogeneity

---

## Reviewer Feedback Response Summary

### Issue 1: chimera_detector.py path
**Fixed**: All references changed from `chimera_lab/` to `labs/simulations/`.

### Issue 2: Separate ChimeraDetector per domain
**Fixed**: Each domain gets its own ChimeraDetector instance with n_windows=8 (matching local sector count).

### Issue 3: Domain-aware history tracking
**Fixed**: History is maintained per-domain via the history parameter passed to each detector.detect() call, not as an instance attribute.

### Issue 4: n_windows defaults to 5
**Fixed**: Explicitly set n_windows=8 per domain. Documented that this must match the local sub-sector count.

### Issue 5: ChimeraDiagnosticV2.compute_segment_sync() uses full N
**Fixed**: Added requirement for domain_mask parameter. Provided two implementation approaches (parameter addition vs. separate instance).

### Issue 6: N=800 vs N>=1500
**Fixed**: N increased from 800 to 1500, giving 750 per domain. Exceeds the D20 threshold (N/3 >= 500).

---

*Revision 1 complete. Pending reviewer-2 re-approval before implementation begins.*
*Revision date: 2026-06-03*
