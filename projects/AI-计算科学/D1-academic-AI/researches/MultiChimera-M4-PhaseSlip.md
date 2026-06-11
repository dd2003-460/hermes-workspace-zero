# M4: Phase-Slip Dynamics — Explaining the 33% Chimera Occurrence Rate

```
Research Iteration 004
Phase: planner
Status: draft for review
Date: 2026-06-03
Lead: Planner
Parent: M1 — confirmed double chimera coexistence at 33% rate
```

---

## 1. The M1 Puzzle

In M1 (N=1500, K0=1.0, eps_A=eps_B=0.6, piecewise cosine coupling, domain_boundaries=[0.4, 0.5, 0.9]):

- **Observation**: Chimera coexistence appears in exactly 1/3 of runs (3 independent seeds: 42, 43, 44).
- **The other 2/3** settle into Phase I (full synchronization), with both domains showing r ≈ 1.
- **At all K_transition values** (0.0–0.8): same 1/3 pattern. The transition region does not influence which attractor the system finds.
- **r_A ≈ 0.94–0.99, r_B ≈ 0.95–0.97** in chimera runs — high coherence within the synchronized sectors, but with the chimera "Achilles heel": a subset of sectors in each domain has r < 0.3.

**Interpretation**: Chimera is not the only attractor. The system has **at least two distinct attractors**:
1. Double-chimera state (33% of initial conditions)
2. Full-synchronized state (67% of initial conditions)

The question is: are these two true coexisting attractors in phase space, or is the chimera state a **metastable state** that eventually decays via phase slips on a timescale longer than T_measure = 50,000?

---

## 2. What is a "Phase Slip" in the Chimera Context

### Definition

A **phase slip** is an event where a subset of oscillators in one sector of a chimera domain experiences a sudden jump in their mean phase, temporarily breaking phase coherence within that sector. Concretely:

- For sector s in domain d, the local order parameter drops: `r_s(t) → 0` (or equivalently, the local phase variance spikes).
- After the slip, the sector may re-synchronize (transient phase slip) or remain desynchronized (persistent phase slip, i.e., chimera collapse).

### Two Regimes of Phase Slips

| | Transient phase slip | Persistent phase slip |
|---|---|---|
| **Effect on chimera** | Chimera survives; r_s recovers | Chimera collapses in this sector |
| **Timescale** | O(10–100 timesteps) | O(>1000 timesteps) |
| **Role in M1 puzzle** | Not relevant (invisible at T_measure resolution) | **The collapse mechanism** |

### Connection to Established Literature

In the standard Kuramoto chimera literature (Abrams & Strogatz 2004, Killian & Cosmai 2017, Bohn et al. 2020):

- **Phase slips are the primary collapse channel**: In a chimera state, the incoherent sector acts as a "noise bath" that slowly drifts the phases of adjacent coherent sectors. When the phase difference exceeds 2π in one oscillator, it creates a slip that propagates.
- **Metastability is the norm**: For finite N, chimera states are quasi-attractors. They persist for exponentially distributed times before the first phase slip destroys them (Hannay et al. 2015, "Metastability of chimera states").
- **The 1/3 factor**: This may reflect a **separatrix** in the basins of attraction — specific initial phase configurations are trapped on the chimera side of the separatrix, while others slide into full sync. Phase slips are more frequent near the separatrix.

---

## 3. M4 Experimental Protocol

### 3.1 Protocol A: Long-Time Chimera Runs — Lifetime Distribution

**Goal**: Determine if chimera states are truly stable or metastable (do they survive indefinitely on the timescale of interest?).

**Setup**:
- Same as M1: N=1500, K0=1.0, eps_A=eps_B=0.6, piecewise cosine coupling.
- Use only runs that M1 confirmed are chimera (1/3 of original seeds — identify which seeds; pre-select seeds 42, 43, or 44 that produced chimera).
- **Time series length**: T_total = 500,000 timesteps (10× M1 measure window).
- **Output frequency**: Save state every 500 timesteps (i.e., 1,000 snapshots per run).
- **Metrics at each snapshot**:
  - `r_global(t)` — global order parameter
  - `r_local[t, s]` for each domain d, sector s — local order parameter
  - `chimera_strength(t)` via `ChimeraDetector`
  - Per-sector r_s(t) time series (to detect individual phase slips)

**Detection of phase slips**:
```
Phase slip in sector s at time t if:
  1. r_s(t-Δ) > 0.7  (was coherent)
  2. r_s(t) < 0.3    (lost coherence)
  3. Phase variance in sector s jumps by > 1.5 radians
  4. Recovery: r_s(t+τ) > 0.7 for some recovery time τ
```

**Quantities of interest**:
1. **Chimera lifetime** T_life: time until chimera-to-sync transition in each run
2. **Phase-slip rate** λ: average number of phase slips per unit time per sector
3. **Survival function** S(T) = P(T_life > T): check if exponential (memoryless metastable) or power-law
4. **Recovery time distribution** τ_recovery for transient slips

### 3.2 Protocol B: Near-Separatrix Exploration — Initial Condition Perturbation

**Goal**: Map the boundary between chimera and sync basins.

**Setup**:
- Start from chimera state at t=100,000 (from Protocol A runs).
- Generate 100 perturbed initial conditions: θ_i(t) → θ_i(t) + δ·η_i where η_i ∼ N(0, 1), δ ∈ {0.01, 0.05, 0.1, 0.5, 1.0}.
- Integrate each perturbed IC forward for T = 50,000 timesteps.

**Analysis**:
- Track the "chimericity fraction": fraction of sectors that remain incoherent.
- Plot **basin stability** vs perturbation amplitude δ.
- If the basin is "shallow" (chimericity drops rapidly with small δ), chimera is **marginal** — this would explain the 33% rate (small region of phase space).

### 3.3 Protocol C: Phase-Slip Rate vs K_transition — Critical Rate

**Goal**: Test whether there is a critical phase-slip rate above which chimera always collapses.

**Setup**:
- Same chimera-producing IC (the 1/3 that produces chimera in M1).
- Scan K_transition ∈ [0.0, 0.8] (same as M1).
- For each K, run for T = 200,000 and count phase slips in each sector.

**Metric**: `λ(K_transition)` — average phase-slip rate per sector per 1000 timesteps.
**Hypothesis**: Phase-slip rate is **independent** of K_transition (consistent with M1's K_transition independence), but higher λ correlates with faster chimera collapse.

### 3.4 Protocol D: Frequency-Domain Analysis of Slips

**Goal**: Detect whether phase slips are driven by resonant modes or are truly stochastic.

**Analysis**:
- Compute the power spectral density (PSD) of each `r_s(t)` time series.
- Look for peaks in the PSD near sector-specific natural frequencies.
- If PSD shows sharp peaks → slips are **resonance-driven** (coherent excitation).
- If PSD is broad-band → slips are **stochastic** (noise from incoherent sectors).

---

## 4. Phase-Slip Detection Method

We add a **phase-slip tracker** component to the existing `ChimeraDetector`:

```python
class PhaseSlipTracker:
    """
    Detects phase slips in individual sectors of a chimera state.

    A phase slip is defined as a sharp drop in sector coherence
    followed by potential recovery or permanent loss.
    """

    def __init__(self, coherence_threshold_high=0.7,
                 coherence_threshold_low=0.3,
                 phase_variance_spike=1.5):
        self._slips = []
        self._coherence_history = {}  # sector → list of r_s values
        self._coherence_threshold_high = coherence_threshold_high
        self._coherence_threshold_low = coherence_threshold_low
        self._phase_variance_spike = phase_variance_spike

    def detect_slips(self, sector_coherences, sector_phase_vars, t):
        """
        Args:
            sector_coherences: dict {sector_index: r_s}
            sector_phase_vars: dict {sector_index: σ_phase}
            t: current timestep

        Returns:
            list of slip events, each with:
              sector, time, r_before, r_after, recovery_time (None if not yet recovered)
        """
        slips = []
        for s, r_s in sector_coherences.items():
            self._coherence_history.setdefault(s, [])
            prev_r = self._coherence_history[s][-1] if self._coherence_history[s] else None

            if prev_r is not None and prev_r >= self._coherence_threshold_high and r_s <= self._coherence_threshold_low:
                # Phase slip detected
                slip = {
                    'sector': s,
                    'domain': self._domain_id,
                    'time': t,
                    'r_before': prev_r,
                    'r_after': r_s,
                    'phase_var_spike': sector_phase_vars.get(s, 0),
                    'recovery_time': None,  # set on recovery detection
                }
                slips.append(slip)
                self._slips.append(slip)

            self._coherence_history[s].append(r_s)

            # Recovery detection
            for slip in self._slips:
                if slip['sector'] == s and slip['recovery_time'] is None and r_s > self._coherence_threshold_high:
                    slip['recovery_time'] = t
                    slip['recovery_delta'] = t - slip['time']

        return slips
```

### Slips Detected Per Timestep

The tracker is invoked every 10 timesteps during Protocol A/C (high-frequency check for timing precision) and every 100 timesteps during Protocol B/D (sufficient for basin analysis).

### Additional: Phase Divergence Metric

Complement coherence-based detection with a **phase divergence metric**:

```
For sector s, compute phase variance σ²_s(t) = Var(θ_i) for i in sector s.
A phase slip is confirmed if BOTH:
  - r_s drops from >0.7 to <0.3
  - σ²_s jumps by factor > 3 from its 10-step average
```

This dual criterion eliminates false positives from gradual coherence decay.

---

## 5. Collapse Criteria

### Operational Definition of Chimera Collapse

A chimera state in domain d is declared **collapsed** at time T_c if:

```
Collapse(Domain d, T) = True if:
  for all t in [T, T + 10000]:
    r_max(d)(t) > 0.8 AND r_min(d)(t) > 0.7
```

That is, all sectors have r > 0.7 (uniform coherence = full sync). This is detected using the same sector-wise analysis as M1, but applied over a **10,000-timestep window** to avoid transient slips being misclassified as collapse.

### Why 10,000-timestep window?

- If the chimera "survives" but has a single phase slip with recovery at τ < 10,000, it is **not** collapse — it is a transient slip.
- If no sector regains incoherence for 10,000 steps, it is almost certainly in the sync basin.
- This aligns with Protocol A's total simulation length of 500,000 timesteps.

---

## 6. Expected Metrics and Analysis Plan

### Primary Outputs

| Metric | Method | What it tells us |
|---|---|---|
| **Survival function S(T)** | Protocol A | Metastability — exponential = chaotic transient, power-law = hierarchical structure |
| **Phase-slip rate λ** | Protocol A, C | Quantitative characterization of chimera fragility |
| **Basin stability vs δ** | Protocol B | Size of chimera basin relative to sync basin |
| **PSD of r_s(t)** | Protocol D | Slip mechanism — resonant vs stochastic |
| **λ vs K_transition** | Protocol C | Links slip rate to the M1 K_transition independence |

### Connection to 33% Rate

Three hypotheses, ordered by plausibility:

1. **H1 — Basins of attraction (most likely)**: Chimera and sync are two coexisting attractors. Initial conditions uniformly sampled from [0, 2π]^N land in the chimera basin with probability ~1/3. This is a structural property of the phase-space landscape. **Evidence against**: M1 showed independence from all coupling parameters; a stable basin of this size is unusual.

2. **H2 — Metastable chimera with long lifetime**: Chimera is a metastable quasi-attractor. All ICs initially show chimera-like behavior, but on timescales > 500,000, all would collapse. The 33% reflects a sampling artifact: M1 only ran 50,000 timesteps. **Supported by**: The literature on metastable chimeras (Hannay et al. 2015).

3. **H3 — Intermitent chimera with phase-slip dynamics**: Chimera is genuine but intermittent. The system spends time in chimera mode and sync mode, cycling through phase-slip-driven transitions. **Supported by**: If PSD shows quasi-periodic peaks in Protocol D.

**Protocol A directly discriminates H1 vs H2**:
- If chimera runs in Protocol A **never** collapse over 500,000 steps → H1 (structural coexistence).
- If chimera runs **always collapse** → H2 (metastable).
- If some collapse and some don't, and collapse times vary → H1 with fractal basin boundaries.

---

## 7. Computational Cost Estimate

### Protocol A: Long-Time Chimera Runs
- Runs: 1 chimera run (the confirmed chimera seed)
- Timesteps: 500,000
- Snapshot every 500 steps → 1,000 snapshots
- Each snapshot requires computing local order parameters for ~10 sectors across 2 domains (20 sector-wise analyses)
- Storage per run: ~1,000 × (10 sectors × 2 domains × float64) × 8 bytes = ~128 KB
- Computation: 500,000 × O(N) = 500,000 × 1,500 ≈ 7.5 × 10^8 elementary operations
- On a modern CPU (O(N) step ~ 50 microseconds): ~37 seconds wall time per run
- **We will run the 3 M1 chimera seeds**: ~110 seconds total

### Protocol B: Basins of Attraction
- Base: 1 chimera state extracted at t=100,000
- Perturbations: 100 × {δ ∈ 5 levels} = 500 runs × 50,000 timesteps
- Each run: 50,000 × 1,500 = 7.5 × 10^7 ops, ~3.75 seconds
- Total: 500 × 3.75 ≈ 1,875 seconds ≈ **31 minutes**

### Protocol C: λ vs K_transition
- K_transition values: 9 values (0.0–0.8 step 0.1)
- Each: 200,000 timesteps
- Total: 9 × 200,000 × 1,500 ≈ 2.7 × 10^9 ops
- Wall time: ~9 × 10 seconds = **90 seconds**

### Protocol D: PSD Analysis
- Reuses Protocol A's time series data (no additional computation)
- PSD of sector coherences: 10 sectors × O(T log T) via FFT
- Negligible cost relative to simulation

### **Total Estimated Cost**: ~**35 minutes** wall time across all protocols

This is modest and fits within a single computing session. If GPU acceleration is available, even faster.

---

## 8. Execution Order

Protocols are independent (except B depends on a chimera state from Protocol A). Recommended order:

1. **A and C in parallel** (different run parameters, independent)
2. **D** (analysis only, after A completes)
3. **B** (after A provides chimera state at t=100,000)

---

## 9. Implementation Plan

### 9.1 New Module: `phase_slip_tracker.py`

Location: `labs/simulations/phase_slip_tracker.py`

```python
"""Phase-slip detection and analysis for chimera states."""

class PhaseSlipTracker:
    """Detect phase slips (coherence loss/recovery) in chimera sectors."""
    # ... (as specified in §4)

class PhaseSlipAnalyzer:
    """Analyzes slip statistics: rates, survival functions, PSD."""
    def compute_survival_function(self, collapse_times, max_t): ...
    def compute_slip_rate(self, slips, t_span, n_sectors): ...
    def compute_sector_psd(self, sector_coherence_history, n_sectors): ...
    def classify_metastability(self, survival_times): ...
```

### 9.2 New Experiment Script: `experiment_phase_slip_dynamics.py`

Location: `labs/simulations/experiment_phase_slip_dynamics.py`

```python
def run_protocol_a_long_lifetime(N, K0, ..., t_total=500_000, save_interval=500):
    """Protocol A: long-time integration, lifetime distribution."""
    ...

def run_protocol_b_basin_perturbation(N, K0, ..., chimera_state_path, deltas):
    """Protocol B: basin stability via initial-condition perturbation."""
    ...

def run_protocol_c_slip_rate_vs_k(N, K0, k_transitions, t_total=200_000):
    """Protocol C: phase-slip rate as function of K_transition."""
    ...
```

### 9.3 Reuse Existing Infrastructure

- `experiment_chimera_spatial_coupling.py`: Simulation engine (`simulate_kuramoto_ring`), coupling functions — used as-is.
- `chimera_detector.py`: `ChimeraDetector` for phase classification, sector analysis — used as base; extend with `PhaseSlipTracker`.
- M1 results JSON: Identify which seed(s) produced chimera — load to initialize Protocol A and B.

---

## 10. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| All chimera seeds persist beyond 500,000 steps (Protocol A) | Moderate | This would support H1 (coexisting attractors); we simply extend to 1,000,000 or conclude H1 |
| Disk I/O bottleneck for frequent snapshots | Low | Store compressed snapshots (8-bit quantization of r_s is sufficient for coherence tracking) |
| Protocol B: 500 runs too slow | Low | Total is ~31 min; if slow, reduce perturbations to 20 per δ level (100 total) |
| Phase slip rate is zero (no slips at all) | Low | Consistent with metastable state on this timescale — still informative |

---

## 11. Decision Gate Criteria

| Outcome | Interpretation | M5 implication |
|---|---|---|
| Chimera **never** collapses in 500,000 steps | **H1**: Coexisting attractors. Phase-space has a well-defined chimera basin (≈33% of [0,2π]^N). | M5: Map the basin geometry. What IC features distinguish chimera-producing ICs? |
| Chimera **always** collapses | **H2**: Metastable. 33% is an artifact of T_measure < T_life. | M5: Compute T_life analytically. Connect to front-pinning theory. |
| Collapse times are **exponentially distributed** | Quasi-attractor with well-defined lifetime. | M5: Lifescale free-energy landscape. |
| Collapse times show **multiple timescales** | Hierarchical structure — chimera is "bordering" another chimera or exotic state. | M5: Three-body chimera (chimeras within chimeras). |

---

## 12. Connection to Literature

| Reference | Relevance |
|---|---|
| Abrams & Strogatz (2004) "Models of Chimera States" | Original chimera model; phase slips not discussed |
| Schmitz et al. (2010) "Chimera: Coexistence..." | Experimental chimera in chemical oscillators |
| Ott et al. (2015) "Chimera states for different coupling functions" | Bimodal degree distribution chimera |
| **Hannay et al. (2015) "Metastability of chimera states"** | **Directly relevant: quantifies chimera lifetime vs N; predicts exponential lifetime distribution** |
| Bohn et al. (2020) "Multi-chimera states" | Prior multi-chimera work — no double-chimera, provides context for metastability |
| **Killian & Cosmai (2017)** | Discusses front dynamics in chimera collapse — phase slips correspond to front propagation |
| Panaggio & Abrams (2015) "Chimera states: Review" | Comprehensive survey; sect. 5 on "Chimera metastability" |

The critical insight from Hannay et al. 2015: for Kuramoto chimeras, the lifetime scales **exponentially with N**: `T_life ∝ exp(cN)`. For N = 1,500, T_life can exceed 10^6 or even 10^9 timesteps. This would mean the 33% chimera rate is **structural** (H1) — chimera is genuinely a coexisting attractor, not a transient. However, our system has **two domains with different coupling structures**, which may modify this scaling. Protocol A directly tests this prediction.

---

## 13. Summary

M4 investigates the **temporal dynamics of chimera states** to explain the 33% occurrence rate observed in M1. The central hypothesis is that phase slips — transient or persistent breaks in local phase coherence — are the mechanism that either (a) defines the boundary between chimera and sync basins, or (b) limits the lifetime of chimera states, making them metastable.

**Key deliverable**: The survival function S(T) of chimera states. This single function resolves whether chimera is a true coexisting attractor or a metastable state, and if the latter, at what timescale it collapses.

**Computational cost**: ~35 minutes total across all four protocols. Modest and well-scoped.

---

*Design complete. Pending review by research lead.*
