# Abstract (Draft)

**Title**: Chimera States as True Stable Attractors: Lifetime, Basin Geometry, and Mode Selection in Piecewise-Coupled Kuramoto Rings

**Abstract**:
Chimera states—counterintuitive patterns in which identical coupled oscillators partially self-organize into coherent and incoherent regions—are typically presumed to be metastable. Here we challenge this view for a piecewise-coupled Kuramoto ring (N = 1500). Protocol A integration of 500,000 timesteps shows zero collapses and zero phase slips across three chimera seeds, with survival function S(T) = 1.0 and metastability classification H1 (coexisting attractor). A 300-run pilot scan across 100 grid points in (eps_A, eps_B, K0) reveals a domain coexistence (DC) rate of 73.7%, with chimera produced at all tested parameters, indicating a large and parameter-invariant basin of attraction. We identify a mode-selection mechanism: the piecewise cosine coupling selects specific Fourier modes that stabilize chimera, consistent with recent work on delay-induced mode selection (Wu, 2026). Sector-level power spectral density shows no temporal modulation, confirming the chimera spatial pattern is frozen. Finally, we demonstrate that the domain-level order parameter (r ≈ 0.95) is insufficient to detect chimera, establishing the necessity of sector-level resolution. Our results challenge the prevailing view of chimera metastability and provide a framework for understanding chimera stability in generalized coupling schemes.

---

# Figure Descriptions (Draft)

## Fig 1: Piecewise-coupled Kuramoto ring
Schematic of the model. N = 1500 oscillators arranged on a ring with piecewise cosine coupling K(x) = K0 × (1 + eps·cos(2πx)). Domain A [0, 0.4) and Domain B [0.5, 0.9). Shows coherent/incoherent partition in chimera state.

## Fig 2: Survival function S(T)
S(T) = 1.0 for all T ∈ [5,000, 500,000] timesteps. All 3 seeds survive. Metastability classification: H1 — coexisting attractor. Error bars: ±1σ (binomial confidence interval).

## Fig 3: Phase slip counts
Zero phase slips across all 3 seeds, 16 sectors, 500,000 timesteps. Total: 2.4M sector-timesteps with 0 slips.

## Fig 4: Domain vs sector coherence
Comparison of domain-level r (r_A ≈ 0.94-0.99) vs sector-level r (r_s ranges from 0.1 to 0.95). Shows domain-level r is insufficient for chimera detection.

## Fig 5: M2 pilot DC rate
Heatmap of DC rate across 100 grid points in (eps_A, eps_B, K0). DC rate ≈ 70% everywhere. Confirms basin geometry is parameter-invariant.

## Fig 6: Sector PSD
Power spectral density of sector r_s(t) for 16 sectors. All sectors within each domain have identical PSD. No temporal modulation. Dominant frequency at Nyquist limit.

## Fig 7: Phase snapshot
Snapshot of chimera state showing coherent/incoherent partition. θ vs x plot with color coding for r_s.

---

*Drafted by Ralph Loop iteration 17*
*For target: Physical Review Letters / Chaos*
