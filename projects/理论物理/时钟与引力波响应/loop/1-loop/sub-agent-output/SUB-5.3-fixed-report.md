# Lou Thesis Extraction Report

## Chapter 3 (line 942+): OLC ORF Theory

**Transfer function sinc derivation (lines 963-975, eq. 3-1):** The full ORF expression for two OLC detectors is:

```
Gamma_12(f) = sum_λ ∫ d²n̂/4π [û₁^a û₁^b e^λ_ab(n̂)] [û₂^c û₂^d e^λ_cd(n̂)]
  × sinc[πfL₁/c (1 - û₁·n̂)] sinc[πfL₂/c (1 - û₂·n̂)]
  × L₁L₂ (πf/c)² exp(iα₁₂) exp(iβ₁₂)
```

with α₁₂ = 2πf/c (L₁/2 û₁ - L₂/2 û₂ - x₁ + x₂)·n̂, β₁₂ = πf/c (L₂ - L₁). The sinc factors come from the single-way link frequency-shift transfer function (derived in sec 2, eq. 2-30, line 948).

**Configuration transformation invariance (lines 1036-1602):**

- Trivial transformations that preserve |Γ|: (1) label swap (eq. 3-5), (2) global translation (eq. 3-6), (3) O(3) orthogonal rotation (eq. 3-8). All are coordinate changes that do not alter the physical configuration.
- **Non-trivial transformation (eqs. 3-43, 3-55):** x₃ = x₁ - L₁û₁, L₃û₃ = -L₁û₁; x₄ = x₂ - L₂û₂, L₄û₄ = -L₂û₂. This swaps the receive and transmit laser positions on each detector. When L₁ = L₂, the ORF is either identical or conjugated: Γ₁₂(f) = Γ₃₄(f) or Γ₁₂(f) = Γ₃₄*(f) (line 1602).

## Chapter 4 (line 1829+): ORF Configuration Comparison

**ORF types compared (lines 1856-1873):** Hellings-Downs curve (eq. 4-1), Gamma^I (intensity overlap reduction function, eq. 2-50). The thesis does not analyze Gamma^V (chiral/circular polarization ORF) — this is noted as future work in Ch. 6, line 2498.

**Detector configurations tested:**

- **PTA-like (classical): lines 1838-1941.** Two OLC detectors share two endpoint positions (their x₁ and x₂ coincide). Tunable: angle theta and arm length L. Fixed L=10¹⁰m, angles 0°-180° tested (lines 1888-1889).
- **Isosceles trapezoid: lines 1944-2074.** Four spacecraft form an isosceles trapezoid. Tested distances between detector centers: 0 m, 10⁸m, 3×10⁸m, 1×10⁹m, 3×10⁹m, 1×10¹⁰m, 3×10¹⁰m. Angles: 0°, 20°, and 0°-180° sweeps.

**ORF peak scaling (lines 1926-1941):** ORF peak frequency is inversely proportional to arm length (line 2065). At fixed angle, high-frequency limit value is independent of arm length and depends only on the angle (lines 1939-1941). As L increases, peak-valley features shift to lower frequency.

**Hellings-Downs breakdown (lines 2037-2074):**

- For isosceles trapezoid with 0 spacing (small separation): peak at ~10⁻² Hz follows HD angular dependence (lines 2031-2036).
- For large spacing (3×10¹⁰m = 3× arm length, lines 2039-2045): ORF peak decreases monotonically from 0° to 120°, then increases from 120° to 180° — **deviates from HD curve**. At high frequency, ORF absolute values are very small for all angles because separation >> wavelength.
- For non-PTA trapezoid config, the HD-related term does NOT always dominate in the high-frequency band (line 2036), unlike the PTA-like case where it does (line 1923).

## Chapter 5 (line 2075+): OLC Sensitivity Comparison

**Sensitivity calculations (lines 2084-2252):**

- Standard space laser interferometer noise (eqs. 5-3, 5-4): OMS noise + acceleration noise, dominated by laser frequency noise, removed via TDI to ~8 orders of magnitude (line 2109).
- OLC noise (eq. 5-11): N_total = N_QPN + N_PSN + N_AN (eqs. 5-12, 5-13, 5-14). Parameters: ν=430 THz, N=7×10⁶, T=160s, η=0.5, ΔL=30 mHz, P_L=3 pW, S_L=9 fm²s⁻⁴Hz⁻¹ (eq. 5-16).
- OLC strain sensitivity (eq. 5-17): h̃₁₂(f) = [(tau Δf) (Γ₁₂²/N²_total)]^(-1/4), with τ=1 year, Δf=f/10.

**Comparison with LISA/Taiji/TianQin (lines 2329-2396):**

- Table 5-1: LISA (L=2.5×10⁹m, A_OMS²=225 pm²/Hz, A_acc²=9 fm²/s⁴/Hz), Taiji (L=3×10⁹m, 64, 9), TianQin (L=1.7×10⁸m, 1, 1).
- Table 5-2: For equivalent arm lengths, OLC satellite formation radius is smaller than LISA/Taiji/TianQin, with correspondingly lower orbital eccentricity.
- **Result (lines 2385-2395):** OLC network sensitivity is superior to LISA/Taiji at low and high frequencies, while LISA/Taiji are better in the mid-frequency band. TianQin is superior to OLC above 10⁻⁴ Hz, but OLC wins at low frequencies. OLC sensitivity minimum is at 10⁻²-10⁻¹ Hz vs LISA's 10⁻³-10⁻² Hz, due to different noise model peak frequencies.
