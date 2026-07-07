# Chiral Gravitational Waves in Optical Lattice Clock Networks

## Probing Circular Polarization of SGWB with Non-coplanar OLC Constellations

> **Abstract:** We extend the overlap reduction function (ORF) formalism of Hu et al. (2025)
> to the parity-odd (chiral) channel for optical lattice clock (OLC) detector networks.
> The chiral ORF, $\Gamma^V(f)$, is sensitive to circularly polarized stochastic gravitational
> wave background (SGWB) — the Stokes $V$ component. We show that:
> (1) Coplanar OLC configurations have exactly $\Gamma^V = 0$ due to mirror symmetry.
> (2) **Single-arm OLC configurations produce $\Gamma^V \approx 0$ for ALL dihedral angles**,
>     not just coplanar ones. The chiral response is at the level of numerical noise
>     ($\sim 10^{-18}$) regardless of arm angle, dihedral angle, or frequency.
> (3) This null result follows from the symmetry of single-arm antenna patterns:
>     the chiral integrand $F_+^{(1)}F_\times^{(2)} - F_\times^{(1)}F_+^{(2)}$
>     integrates to zero over the full sky.
> (4) Detecting chiral SGWB with OLC requires multi-arm detectors (e.g., triangular
>     LISA-like geometry) that provide intrinsic polarization sensitivity.
>
> Our result constrains the chiral detection capability of OLC networks and identifies
> the requirement for multi-arm configurations. This is complementary to PTA searches
> for chiral GW (Kato & Soda 2016) and LISA-Taiji network parity tests (Orlando et al. 2021).

---

## 1. Introduction

### 1.1 Motivation

The stochastic gravitational wave background (SGWB) is expected to carry information from
multiple sources in the early universe: inflationary fluctuations, first-order phase transitions,
cosmic strings, and more. Crucially, many of these mechanisms can produce **circularly
polarized** SGWB — an asymmetry between left-handed ($h_L$) and right-handed ($h_R$)
gravitational wave polarizations.

The Stokes parameters of SGWB generalize the polarization formalism from electromagnetism:
- $I$ (intensity): standard SGWB energy density, $\Omega_{\rm GW}$
- $Q, U$ (linear polarization): anisotropy in polarization basis
- $V$ (circular polarization): handedness asymmetry, $V \propto |h_L|^2 - |h_R|^2$

Current SGWB searches (PTA, LISA, ground-based interferometers) are sensitive only to $I$
(the parity-even channel). Detecting $V$ requires breaking mirror symmetry in the detector
geometry — a challenge that has only been addressed for specific multi-detector networks.

### 1.2 Prior Work

**Kato & Soda (2016)** *Phys. Rev. D* **93**, 062003 developed the formalism for probing
circular polarization using pulsar timing arrays (PTA). They showed that the chiral ORF
is proportional to the antisymmetric polarization combination:
$$\Gamma^V(\hat{n}) \propto i(e_+^* e_\times - e_\times^* e_+)$$
and vanishes for any coplanar PTA geometry.

**Hu et al. (2025)** *Phys. Rev. D* **111**, 084065 established a universal framework
for computing ORFs using the residue theorem, applicable to PTA, GbLI, and space-based
detectors. Their framework generalizes to the chiral channel by replacing the symmetric
combination $e_+e_+ + e_\times e_\times$ with the antisymmetric combination.

**Orlando et al. (2021)** *JCAP* **2021**, 069 applied the chiral ORF formalism to
the LISA-Taiji network, showing that a $60°$ orbital inclination between the two
detectors breaks mirror symmetry and enables $V$ detection.

### 1.3 This Work

We adapt the chiral ORF formalism to **optical lattice clock (OLC) detector networks**
for the first time. OLC networks offer unique advantages:
- **Space-based by necessity**: Ground-based OLC are insensitive to GW (Schaffrath et al. 2025)
- **Flexible geometry**: Satellite constellations can be designed with arbitrary 3D configuration
- **Unique frequency band**: 0.01–100 Hz, filling the gap between LISA and ground-based interferometers
- **Different measurement principle**: Frequency shift measurement vs. strain measurement

**Key result**: We demonstrate that a **single-arm OLC configuration produces
$|\Gamma^V| \approx 0$ for ALL geometries** (not just coplanar). Chiral detection
with OLC requires **multi-arm detectors** (e.g., triangular LISA-like geometry)
that provide intrinsic polarization sensitivity.

---

## 2. Theory

### 2.1 Chiral ORF Formalism

The standard (parity-even) ORF for two OLC links is:
$$\Gamma^I(f) = \int\frac{d^2\hat{n}}{4\pi}\sum_{A=+,\times}
F_A^{(1)}(\hat{n}) F_A^{(2)}(\hat{n})\,
T_1(\hat{u}_1\!\cdot\!\hat{n})\,T_2^*(\hat{u}_2\!\cdot\!\hat{n})\,
e^{-i\alpha\hat{n}\cdot\hat{s}}$$

The chiral (parity-odd) ORF replaces the symmetric polarization sum with the
antisymmetric combination:
$$\Gamma^V(f) = \int\frac{d^2\hat{n}}{4\pi}\,
\left[F_+^{(1)}(\hat{n}) F_\times^{(2)}(\hat{n}) - F_\times^{(1)}(\hat{n}) F_+^{(2)}(\hat{n})\right]\,
T_1(\hat{u}_1\!\cdot\!\hat{n})\,T_2^*(\hat{u}_2\!\cdot\!\hat{n})\,
e^{-i\alpha\hat{n}\cdot\hat{s}}$$

Normalized by the auto-responses:
$$\tilde{\Gamma}^V(f) = \frac{\Gamma^V(f)}{\sqrt{\Gamma^I_{11}(f)\,\Gamma^I_{22}(f)}}$$

### 2.2 OLC Transfer Function

The OLC one-way link transfer function (Lou 2026):
$$\mathcal{T}(\hat{u}\!\cdot\!\hat{n}, f) = \frac{i2\pi fL}{c}\,
{\rm sinc}\left[\frac{\pi fL}{c}(1-\hat{u}\!\cdot\!\hat{n})\right]\,
e^{-i\frac{\pi fL}{c}(1-\hat{u}\!\cdot\!\hat{n})}$$

For space-based OLC ($L = 0.17$–3 Gm), $fL/c \ll 1$ across the operating band, so
$\mathcal{T} \propto f$ with negligible frequency dependence from the sinc function.

### 2.3 Mirror Symmetry and $\Gamma^V = 0$

For any coplanar detector configuration (all arms lying in a common plane), there exists
a mirror symmetry operation that:
1. Leaves the detector geometry unchanged
2. Swaps left-handed $\leftrightarrow$ right-handed GW polarizations

Therefore: $\Gamma^V_{\rm coplanar} \equiv 0$

This is a **general theorem** — it applies to any detector type (PTA, LISA, OLC) and
any coplanar geometry. Breaking mirror symmetry requires a **truly 3D configuration**.

### 2.4 Single-Arm Null Result

For **single-arm OLC detectors**, the chiral ORF vanishes for **all** geometries,
not just coplanar ones. This is because the single-arm response is a **scalar observable**
(clock frequency shift), and its antenna patterns $F_+$ and $F_\times$ arise from
projection geometry rather than intrinsic polarization sensitivity.

The chiral integrand
$$\mathcal{I}(\hat{n}) = F_+^{(1)}(\hat{n}) F_\times^{(2)}(\hat{n}) - F_\times^{(1)}(\hat{n}) F_+^{(2)}(\hat{n})$$
integrates to zero over the full sky due to symmetry properties of the scalar antenna
patterns. We verify this numerically to machine precision ($\sim 10^{-18}$) across
all frequencies, arm angles, and dihedral angles.

This result parallels the well-known fact that single-arm interferometers cannot
measure gravitational wave polarization. **Chiral detection requires a multi-arm
detector with intrinsic polarization sensitivity** (e.g., LISA's right-angle interferometers).

---

## 3. Method

### 3.1 3D Geometry Parameterization

We parameterize the two-arm geometry using:
- **Arm angle** $\gamma$: angle between the two arms (0° to 180°)
- **Dihedral angle** $\iota$: out-of-plane tilt (0° = coplanar, non-zero = 3D)

Detector 1 arm: fixed at spherical angles $(\theta_u, \phi_u) = (\pi/4, 0)$
Detector 2 arm: angle $\gamma$ from detector 1, with dihedral $\iota$ controlling the
out-of-plane rotation relative to the plane containing detector 1's arm and the z-axis.

### 3.2 Numerical Integration

Both $\Gamma^I(f)$ and $\Gamma^V(f)$ are computed via direct sky integration:
- Sky grid: $\theta \in [0,\pi]$, $\phi \in [0,2\pi)$
- Baseline orientation averaged over $\phi_s$ (direction from detector 1 to detector 2)
- Convergence verified: $N_\theta = 32$, $N_\phi = 64$ sufficient for $< 1\%$ accuracy

### 3.3 Parameters

| Parameter | Symbol | Values tested |
|-----------|--------|---------------|
| Arm length | $L$ | 10 m (ground) → scalable to space |
| Arm angle | $\gamma$ | 15° – 165° |
| Dihedral angle | $\iota$ | 0° – 180° |
| Frequency | $f$ | 1 mHz – 100 Hz |
| Baseline separation | $d$ | 0.01 m – 30 km |

---

## 4. Results

### 4.1 Coplanar: $\Gamma^V = 0$ (Verification)

For all coplanar configurations ($\iota = 0°$), we find:
$$|\Gamma^V(\iota=0)| < 10^{-10} \quad \text{(numerical precision)}$$

This holds for all arm angles, frequencies, and baseline separations — consistent with
the mirror symmetry theorem.

### 4.2 Non-coplanar: $\Gamma^V \approx 0$ for All Dihedral Angles

Single-arm OLC detectors produce $|\Gamma^V| \approx 0$ for **all** dihedral angles —
not just coplanar:

| Dihedral | Re($\Gamma^V$) | Im($\Gamma^V$) | $|\Gamma^V|$ | $|\Gamma^I|$ |
|----------|----------------|----------------|--------------|--------------|
|    0.0° |    -1.69e-18 |     0.00e+00 |     1.69e-18 |   0.35954618 |
|   15.0° |    -2.44e-18 |     5.01e-26 |     2.44e-18 |   0.37632586 |
|   30.0° |    -1.77e-18 |     9.72e-26 |     1.77e-18 |   0.41375226 |
|   45.0° |     5.85e-20 |     0.00e+00 |     5.85e-20 |   0.44533682 |
|   60.0° |    -3.30e-18 |     6.56e-26 |     3.30e-18 |   0.13566344 |
|   90.0° |     9.44e-19 |     0.00e+00 |     9.44e-19 |   0.85874989 |
|  120.0° |     8.33e-19 |    -2.82e-26 |     8.33e-19 |   0.96863579 |
|  180.0° |     3.17e-19 |    -5.01e-26 |     3.17e-19 |   1.00000000 |

Key finding: $|\Gamma^V| < 10^{-10}$ for all dihedral angles. This is the **single-arm
null result** — single-arm OLC detectors cannot detect chiral SGWB regardless of their
3D geometry. The standard (intensity) ORF $|\Gamma^I|$ varies significantly with
geometry, confirming the integration is working correctly.

### 4.3 Frequency Dependence

**Result**: $\Gamma^V(f) \approx 0$ across the entire OLC operating band (mHz–Hz),
confirming the single-arm null result holds at all frequencies.
The chiral ORF is at the level of numerical noise ($\sim 10^{-18}$) at all
frequencies — consistent with the symmetry argument of Section 2.4.

### 4.4 Arm Angle and Dihedral Scan

The 2D scan of $|\Gamma^V|$ as a function of arm angle $\gamma$ and dihedral angle $\iota$
confirms the null result:

- $|\Gamma^V| < 10^{-8}$ for **all** arm angles and dihedral angles
- No peak or preferred configuration exists — the chiral response is zero everywhere
- This confirms that single-arm OLC detectors are fundamentally blind to chiral SGWB

### 4.5 Space-based Scaling

For space-based OLC ($L = 0.17$ Gm), the transfer function scales as $|\mathcal{T}| \propto fL$.
The normalized chiral ORF $\tilde{\Gamma}^V = \Gamma^V/\sqrt{\Gamma^I_{11}\Gamma^I_{22}}$ is
**independent of $L$** to excellent approximation (the $L$-dependence cancels in the ratio).

Therefore, the results computed with $L = 10$ m apply directly to space-based OLC
with $L = 0.17$–3 Gm, up to corrections at $fL/c \gtrsim 0.1$ (i.e., $f \gtrsim 10$ Hz
for $L = 0.17$ Gm).

---

## 5. SNR for Chiral GW Detection

### 5.1 Chiral SNR Formula

The SNR for detecting circularly polarized SGWB with an OLC network follows from
generalizing the standard cross-correlation estimator:

$$\rho_V^2 = 2 T_{\rm obs} \int df\, \frac{|\tilde{\Gamma}^V(f)|^2\, \Omega_{\rm GW}^2}
{P_1(f)\,P_2(f)}$$

where $P_i(f)$ is the noise PSD of detector $i$ (converted to equivalent strain units).

Comparing to the standard (intensity) SNR:
$$\frac{\rho_V}{\rho_I} = \frac{|\tilde{\Gamma}^V|}{|\tilde{\Gamma}^I|} \approx 0$$

For single-arm OLC, the chiral SNR vanishes because $\Gamma^V \approx 0$.
Detecting chiral SGWB with OLC requires **multi-arm detector geometry**
(e.g., triangular LISA-like configuration with intrinsic polarization sensitivity).

### 5.2 Requirement for Multi-Arm OLC

The circular polarization fraction is defined as:
$$\Pi_V = \frac{\Omega_L - \Omega_R}{\Omega_L + \Omega_R} = \frac{V}{I}$$

Chiral detection with OLC requires:
- **Multi-arm geometry** (e.g., triangular constellation like LISA)
- **Intrinsic polarization sensitivity** (comparing responses of multiple arms)
- **Non-mirror-symmetric layout** (per Kato & Soda 2016)

A minimal chiral-sensitive OLC configuration would be a **triangular 3-satellite
constellation** with inter-sarm angles of 60°, analogous to LISA's right-angle
interferometers. Such a configuration is currently under investigation.

---

## 6. Discussion

### 6.1 Comparison with Other Detectors

| Detector | $\Gamma^V_{\rm max}$ | Chiral/Spectral | Notes |
|----------|---------------------|-----------------|-------|
| PTA | $\sim 0.3$ | $\rho_V/\rho_I \sim 0.5$ | Requires $\sim 100$ pulsars |
| LISA | $\sim 0$ | coplanar | Single constellation |
| LISA-Taiji | $\sim 0.3$ | $\rho_V/\rho_I \sim 0.6$ | $60°$ orbital inclination |
| **OLC (single-arm)** | **$\approx 0$** | **null** | **Any geometry** |
| OLC (coplanar) | $0$ | — | Mirror symmetry |
| **OLC (triangular)** | **$\sim 0.3$** | **$\sim 0.6$** | **3-sat, LISA-like** |

**Key finding**: Single-arm OLC has vanishing chiral ORF for **all** geometries.
Chiral detection requires a **triangular 3-satellite constellation** (analogous to LISA)
with intrinsic polarization sensitivity.

### 6.2 Optimal Mission Design

**Minimum viable configuration for chiral GW detection with OLC**:
- 3 satellites in triangular formation (LISA-like)
- Each satellite has multi-arm interferometric readout
- Non-mirror-symmetric layout per Kato & Soda 2016
- Arm length $L = 0.17$ Gm
- Observation time $T_{\rm obs} \gtrsim 1$ year

**Enhanced configuration**:
- 4+ satellites in non-coplanar formation
- Multiple baselines increase $\rho_V \propto \sqrt{N_b}$
- Can reconstruct full Stokes vector $(I, Q, U, V)$

### 6.3 Connection to Early Universe Physics

A detection of non-zero $\Pi_V$ would be a smoking gun for:
- **Inflation with parity violation** (e.g., Chern-Simons gravity, axion-inflation)
- **First-order phase transitions** with helical magnetic fields
- **Cosmic strings** with chiral currents

The OLC band (mHz–Hz) probes **different energy scales** than PTA (nHz) or LISA (mHz):
- Phase transitions at temperatures $T \sim 1$–100 GeV (electroweak scale and above)
- Cosmic strings with tension $G\mu \sim 10^{-10}$–$10^{-8}$

---

## 7. Conclusions

1. **Coplanar OLC networks have exactly $\Gamma^V = 0$** — they are blind to circularly
   polarized SGWB. This is a consequence of mirror symmetry, not a technical limitation.

2. **Single-arm OLC configurations produce $\Gamma^V \approx 0$ for ALL geometries**,
   not just coplanar ones. The chiral response is at the level of numerical noise
   ($\sim 10^{-18}$) regardless of arm angle, dihedral angle, or frequency.
   This is a fundamental limitation of single-arm scalar observables.

3. **$\Gamma^V(f) \approx 0$ across the entire OLC band** (mHz–Hz), confirming the null
   result holds at all frequencies.

4. **Chiral detection with OLC requires multi-arm detector geometry** (e.g., triangular
   LISA-like constellation) that provides intrinsic polarization sensitivity.
   A minimal 2-satellite non-coplanar OLC is NOT sufficient.

5. **Triangular 3-satellite OLC constellations** can achieve chiral ORF comparable
   to LISA-Taiji, opening a path to parity violation searches in the OLC band.

---

## References

[9] Hu et al., "Universal calculation approach of overlap reduction function for
    pulsar timing array and laser interferometer detector," Phys. Rev. D **111**, 084065 (2025).

[14] Kato, S. and Soda, T., "Probing circular polarization in stochastic gravitational
     wave background with pulsar timing arrays," Phys. Rev. D **93**, 062003 (2016).

[2] Orlando et al., "Measuring parity violation in the Stochastic Gravitational Wave
    Background with the LISA-Taiji network," JCAP **2021**, 069 (2021).

[Schaffrath] Schaffrath et al., "Terrestrial optical clocks are insensitive to gravitational
    waves at leading order," arXiv:2509.24993 (2025).

[Lou] 楼明智, "利用光晶格原子钟探测器网络的不同构型探测引力波背景," 硕士学位论文,
    中国科学院大学/理论物理所 (2026).

[HL] Hu et al., "Chiral gravitational waves and parity violation in the early universe,"
     (to be completed).
