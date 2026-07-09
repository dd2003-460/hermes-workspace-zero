# P2-1: OLC Detector Principles for Gravitational Wave Detection

## 1. OLC Detector Basics

### 1.1 What is an OLC Detector?

An Optical Lattice Clock (OLC) detector uses two satellites connected by a one-way laser link to detect gravitational waves (GWs) through frequency-shift measurements. Unlike laser interferometers that measure distance changes between test masses, OLC detectors measure the fractional frequency shift of laser light as it propagates between two atomic clocks.

**Physical picture**: A laser is emitted from spacecraft A, travels along direction $\hat{u}$ over arm length $L$ to spacecraft B where an atomic clock receives it. The measured quantity is the fractional frequency shift $y(f)$ — the relative change in laser frequency between emission and reception. GWs perturb spacetime along the light path, modulating this frequency shift in a characteristic way that encodes the GW signal.

The detector responds to a single polarization mode $A$ and GW propagation direction $\hat{n}$ through the response function (Lou Eq. 2-42):
$$R_A^{\text{OLC}}(f,\hat{n}) = \frac{1}{2} u^a u^b e^A_{ab}(\hat{n}) \mathcal{T}_{\text{one}}(\hat{u}\cdot\hat{n}, f) e^{-i 2\pi f \hat{n}\cdot\vec{x}/c}$$

where:
- $\hat{u}$ is the unit vector along the laser propagation direction
- $e^A_{ab}(\hat{n})$ are the polarization basis tensors ($+$ and $\times$)
- $\mathcal{T}_{\text{one}}$ is the one-way transfer function (Eq. 2-30)
- $\vec{x}$ is the position of the receiving spacecraft (laser endpoint)
- The exponential factor $e^{-i 2\pi f \hat{n}\cdot\vec{x}/c}$ accounts for the timing reference at the receiver

**Noise model** (Lou Chapter 5, Eq. 5-11 through 5-16): The total noise is dominated by three sources:
- **Quantum Projection Noise (QPN)**: $N_{\text{QPN}}(f) = \frac{2}{(2\pi\nu)^2 N T}$ — fundamental quantum limit from atomic state projection
- **Photon Shot Noise (PSN)**: $N_{\text{PSN}}(f) = \frac{2f^2\Delta L}{\nu^2[(2\pi f)^2 + \eta P_L \Delta L/(2\pi\hbar\nu)]}$ — photon counting statistics
- **Acceleration Noise (AN)**: $N_{\text{AN}}(f) = \frac{S_L}{c^2(2\pi f)^2}$ — residual acceleration of spacecraft

Typical parameters (Lou Eq. 5-15, 5-16): $\nu = 430$ THz, $N = 7 \times 10^6$ atoms, $T = 160$ s, $\eta = 0.5$, $\Delta L = 30$ mHz, $P_L = 3$ pW, $S_L = 9$ fm$^2$ s$^{-4}$ Hz$^{-1}$.

**Key parameter summary table** (from Lou thesis):

| Parameter | LISA | Taiji | TianQin | OLC (equal arm) |
|-----------|------|-------|---------|-----------------|
| Arm length L | 2.5 Gm | 3 Gm | 0.17 Gm | Variable (e.g. 0.1–3 Gm) |
| Formation radius r | 0.1–1.73 Gm | — | — | 0.089–1.53 Gm |
| Orbit eccentricity | 3.34e-4–5.8e-3 | — | — | 2.98e-4–5.2e-3 |

The OLC detector network has a smaller formation radius and lower eccentricity than LISA/Taiji for equivalent arm lengths, making it potentially more stable in terms of orbital dynamics.

### 1.2 Physical Interpretation

OLC detectors have fundamentally different advantages over laser interferometers:
1. **Direct frequency measurement** — No need for arm-length equalization via TDI (Time Delay Interferometry)
2. **Compact formation** — Smaller satellite spacing for equivalent arm lengths
3. **Different noise floor** — Quantum-limited rather than laser-frequency-noise-limited

For the same arm length, OLC network sensitivity outperforms LISA and Taiji in both low-frequency and high-frequency bands, while TianQin dominates above $10^{-4}$ Hz (Lou Chapter 5, Figures 5-3 through 5-8).

### 1.3 Systematic Comparison: OLC vs. Traditional GW Detectors

Beyond the parameter table in Section 1.1, a systematic comparison of detection principles, frequency bands, and sensitivity sources is essential for understanding the complementarity of OLC with existing GW observatories.

| Feature | PTA (NANOGrav/EPTA) | LISA | TianQin | OLC Network |
|---------|---------------------|------|---------|-------------|
| **Detection principle** | Pulse arrival time variation (integrated frequency shift) | Laser interferometry (arm-length change) | Laser interferometry (arm-length change) | Atomic clock frequency-shift measurement (direct) |
| **Observable** | Timing residual $z(t) = \int y(t) dt$ | Phase difference $\Delta\phi$ | Phase difference $\Delta\phi$ | Frequency shift $y(t) = \Delta\nu/\nu_0$ |
| **Frequency band** | $10^{-9}$ – $10^{-7}$ Hz | $10^{-4}$ – $0.1$ Hz | $10^{-4}$ – $1$ Hz | $10^{-3}$ – $10$ Hz (typical) |
| **Arm length** | Parsecs to kpc (pulsar distance) | 2.5 Gm | 0.17 Gm | Variable (0.1–3 Gm, satellite-to-satellite) |
| **Sensitivity source** | Millisecond pulsar timing stability | Laser frequency noise (dominant at low f), accelerometer noise | Short arm → better high-f response, but limited low-f | Atomic clock stability (QPN-limited), photon shot noise |
| **Detector/baseline count** | ~50–100 pulsars × 1 Earth (common vertex) | 3 spacecraft, 3 arms (triangular) | 3 spacecraft, 3 arms (triangular) | $N$ spacecraft, $N(N-1)$ one-way links; 4 spacecraft → 12 one-way links |
| **Orbit** | Pulsar + Earth (essentially fixed) | HEO (highly elliptical, 1 year orbit) | GEO (geostationary orbit) | Variable (circular, LEO/MEO/HEO) |
| **Noise floor** | Pulsar intrinsic timing noise | Laser frequency noise, shot noise, acceleration noise | Shot noise, acceleration noise | Quantum projection noise, photon shot noise, acceleration noise |
| **Key advantage** | Long integration time, huge arm length, low-frequency coverage | Large arm, wide frequency band, directional resolution | Compact size, GEO orbit (stable), good high-f sensitivity | Direct frequency measurement (no TDI), compact formation, quantum-limited noise |

**Complementarity**: OLC and PTA share the same underlying physics (Doppler tracking via electromagnetic waves), but differ in baseline scale and observable. OLC and interferometers (LISA, TianQin) share similar arm lengths and space-borne architecture, but OLC's direct frequency measurement avoids the need for TDI and has a fundamentally different noise floor. This makes OLC particularly complementary for bridging the PTA–LISA frequency gap around $10^{-3}$ – $10^{-2}$ Hz.

---

## 2. Transfer Function Derivation

### 2.1 Signal Model: From Metric Perturbation to Frequency Shift

The derivation chain begins with the metric perturbation and ends with the transfer function in the frequency domain. Here is the complete sequence from Lou thesis Chapter 2:

**Step 1 — GW metric perturbation**: The spacetime metric is $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$ where $h_{\mu\nu}$ is the GW strain. In the transverse-traceless (TT) gauge, $h_{0\mu} = 0$ and $h_{ij}$ is purely spatial, trace-free, and transverse.

**Step 2 — Null geodesic for light propagation**: Light travels on null geodesics ($ds^2 = 0$). For a photon propagating along direction $\hat{u}$ from emitter at position $\vec{x}_e$ to receiver at position $\vec{x}_r = \vec{x}_e + L\hat{u}$, the coordinate time of flight is:
$$t_r - t_e = \frac{L}{c} + \delta t_{\text{GW}}$$

where $\delta t_{\text{GW}}$ is the GW-induced correction to the light travel time.

**Step 3 — Frequency shift definition**: The fractional frequency shift is defined as the ratio of the change in observed frequency to the emitted frequency. For the one-way link (Lou Eq. 2-22):
$$y(t_r) = \frac{\Delta \nu}{\nu_0} = \frac{1}{2} \frac{\hat{u}^a \hat{u}^b}{1 + \hat{u}\cdot\hat{n}} \left[ h_{ab}(t_r, \vec{x}_r) - h_{ab}(t_e, \vec{x}_e - L\hat{n}) \right]$$

This is the core signal equation. It says: the measured frequency shift is proportional to the difference of the metric perturbation $h_{ab}$ evaluated at (a) the reception event, and (b) the emission event "pulled back" along the GW propagation direction by the light-travel distance $L$.

**Step 4 — Time-of-flight correction** (Lou Eq. 2-23 through 2-26): The emission and reception times are not independent. The light travel time itself is modified by the GW:
$$t_e = t_r - \frac{L}{c} - \frac{1}{2c} \hat{u}^a \hat{u}^b \int_{t_r - L/c}^{t_r} h_{ab}(t, \vec{x}_e + \hat{u}(c t_r - c t)) dt$$

This integral correction must be accounted for when evaluating $h_{ab}$ at the emission event. The correction is essential for obtaining the correct transfer function — it introduces the frequency-dependent response that distinguishes the finite-arm response from the long-wavelength (Dipole) approximation.

**Step 5 — Frequency-domain formulation**: Taking the Fourier transform of Eq. (2-22) and carefully accounting for the time-of-flight correction yields the frequency shift as:
$$\tilde{y}(f) = \frac{1}{2} \hat{u}^a \hat{u}^b \tilde{h}_{ab}(f, \hat{n}) \mathcal{T}(\hat{u}\cdot\hat{n}, f) e^{-i2\pi f \hat{n}\cdot\vec{x}/c}$$

where the transfer function $\mathcal{T}$ encapsulates all the frequency dependence.

### 2.2 The Transfer Function (Lou Eq. 2-30)

The final result is the one-way transfer function:

$$\mathcal{T}(\hat{u}\cdot\hat{n}, f) = \frac{i 2\pi f L}{c} \cdot \text{sinc}\left[\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right] \cdot \exp\left[-i\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right]$$

**Physical interpretation of each factor**:

1. **Prefactor $\frac{i 2\pi f L}{c}$**: This is the dipole (long-wavelength) response. In the limit $f \to 0$ (or equivalently $L \to 0$ with $fL/c \ll 1$), the transfer function scales linearly with $f$, reflecting that the frequency shift is proportional to the time derivative of the metric perturbation. The factor $i$ indicates a phase shift of $\pi/2$ between the GW strain and the measured frequency shift.

2. **Sinc function $\text{sinc}\left[\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right]$**: This encodes the **finite arm-length effect**. The argument is $\frac{\pi f L}{c}(1 - \cos\theta)$ where $\theta$ is the angle between the laser direction and GW propagation direction.
   - When $1 - \hat{u}\cdot\hat{n} \approx 0$ (GW propagating parallel to laser, $\theta \approx 0$), the sinc is unity — no suppression.
   - The first zero occurs at $f = \frac{c}{2L(1-\hat{u}\cdot\hat{n})}$.
   - **Origin**: The sinc arises because different parts of the light path "see" different phases of the GW. The GW phase varies during the light travel time $L/c$, and the frequency shift is an integral over the path. This path-integral average produces the interference pattern captured by the sinc function.

3. **Phase factor $\exp\left[-i\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right]$**: This is a geometric phase accumulated along the light path. It represents the fact that the GW phase at reception differs from the GW phase at emission by an amount proportional to the path length projected along the GW propagation direction.

**Key dimensionless parameter**: The argument $y = \frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})$ determines the detector response. The characteristic frequency $f_c = \frac{c}{2\pi L}$ sets the scale where finite-arm effects become important. For LISA ($L = 2.5 \times 10^9$ m), $f_c \approx 20$ mHz; for an OLC with $L = 10^8$ m, $f_c \approx 500$ mHz.

### 2.3 Sinc Function and the GW Phase During Light Travel

The sinc function has a clear physical origin. Consider a plane GW with frequency $f_{\text{GW}}$ propagating along direction $\hat{n}$. A photon travels along $\hat{u}$ over distance $L$. Different points along the photon's path experience the GW at different times because the photon is moving. The GW phase at position $\vec{x}$ and time $t$ is $2\pi f_{\text{GW}}(t - \hat{n}\cdot\vec{x}/c)$.

As the photon travels from $s=0$ to $s=L$ (where $\vec{x}(s) = \vec{x}_e + s\hat{u}$), the GW phase it "sees" varies. The integrated effect — which determines the frequency shift — produces the sinc function through constructive and destructive interference. When the GW wavelength is much larger than $L$ (low frequency), all points along the path see nearly the same GW phase, and the sinc is close to 1 (maximum response). When the GW wavelength is comparable to or smaller than $L$, the contributions from different parts of the path partially cancel, producing the sinc suppression.

**Self-questioning 1**: The transfer function depends on $\hat{u}\cdot\hat{n} = \cos\theta$. For a given arm length, the response is maximized when $\cos\theta \to 1$ (GW propagating along the laser) and suppressed when $\cos\theta \to -1$ (anti-parallel). But the $1-\cos\theta$ factor also determines the **direction of the first zero**. Is this directional dependence physically intuitive? In particular, when $\theta = 0$, the sinc argument vanishes and the transfer function approaches $\frac{i2\pi f L}{c}$ — this is the dipole response. When $\theta = \pi$, the argument doubles, making the sinc suppress earlier in frequency. Does this asymmetry have a simple physical explanation?

---

### 2.4 Measurement Convention: Frequency Shift vs. Timing Residual

The distinction between OLC and PTA transfer functions also reflects a deeper difference in **measurement convention** — what physical quantity is directly measured by the detector:

- **PTA (pulse arrival time)**: Measures the integrated phase of pulsar radio waves. The observable is the *timing residual* $z(t) = \int^t y(t') dt'$, i.e., the integral of frequency shift over the observation time. This corresponds to Hu PRD's $T_{\text{one}}^{\text{Hu}}$ in Eq. (6).

- **OLC (frequency shift)**: Measures the fractional frequency shift directly via atomic clock comparison. The observable is $y(t) = \Delta\nu/\nu_0$, which is the *time derivative* of timing residual. This corresponds to the OLC transfer function $\mathcal{T}_{\text{one}}^{\text{OLC}}$ in Eq. (2-30).

The mathematical relation between the two conventions is:
$$\mathcal{T}_{\text{one}}^{\text{OLC}} \approx i 2\pi f \cdot \frac{1}{1+\hat{u}\cdot\hat{n}} \cdot T_{\text{one}}^{\text{Hu}} \quad \text{(up to phase conventions)}$$

The factor $1/(1+\hat{u}\cdot\hat{n})$ arises because the timing residual depends on the Doppler integral along the full light path, while the OLC measures the instantaneous derivative. The $i2\pi f$ factor is the Fourier-space representation of the time derivative.

**Physical consequence**: Because the OLC measures the derivative, its transfer function naturally contains the $i2\pi f L/c$ prefactor. The sinc function emerges from the path-integral of the GW phase over the finite light travel time, which is the Fourier transform of the rectangular "integration window" along the light path. In contrast, the PTA timing residual does not have this sinc structure — its exponential form reflects the cumulative phase integral over a much longer baseline.

---

## 3. ORF for OLC Networks

### 3.1 SGWB Idealized Assumptions

To define the ORF, we first need the statistical description of the Stochastic Gravitational Wave Background. Lou thesis (Eq. 2-31 through 2-39) introduces four idealized assumptions:

**(1) Stationarity**: The GW background is statistically stationary — its statistical properties are invariant under time translation. This means frequency components are uncorrelated:
$$\langle \tilde{h}_A(f, \hat{n}) \tilde{h}_{A'}^*(f', \hat{n}') \rangle \propto \delta(f - f')$$

**(2) Gaussianity**: The amplitude distribution is Gaussian. By Wick's theorem, all higher-order correlations reduce to products of two-point correlations.

**(3) Isotropy**: The GW background is the same in all sky directions. Points in different directions are uncorrelated:
$$\langle \tilde{h}_A(f, \hat{n}) \tilde{h}_{A'}^*(f', \hat{n}') \rangle \propto \delta^2(\hat{n}, \hat{n}')$$

**(4) Unpolarized**: Different polarization modes are uncorrelated:
$$\langle \tilde{h}_A(f, \hat{n}) \tilde{h}_{A'}^*(f', \hat{n}') \rangle \propto \delta(A, A')$$

**Combined result** (Lou Eq. 2-39):
$$\langle \tilde{h}_A(f, \hat{\Omega}) \tilde{h}_{A'}^*(f', \hat{\Omega}') \rangle = \frac{1}{2} \delta(f - f') \delta^2(\hat{\Omega}, \hat{\Omega}') \frac{4\pi}{4\pi} \delta_{AA'} S_h(f)$$

where $S_h(f)$ is the single-frequency-sideband power spectral density, satisfying $S_h(f) = S_h(-f)$ (the factor of 1/2 comes from this symmetry).

**Physical meaning**: Under these assumptions, the entire SGWB is characterized by a single function $S_h(f)$ — one number per frequency. All directional and polarizational correlations are fixed by symmetry. The detector's ability to detect this background depends entirely on its **geometric sensitivity**, encoded in the ORF.

### 3.2 Cross-Correlation Analysis and the ORF Definition

The signal from detector $I$ is (Lou Eq. 2-41):
$$s(t) = \sum_{A=+,\times} \int_{-\infty}^{\infty} df \int d^2\hat{n} \, R_A(f, \hat{n}) \tilde{h}_A(f, \hat{n}) e^{i 2\pi f t}$$

The cross-correlation estimator between two detectors (Lou Eq. 2-44):
$$Y = \int_{-T/2}^{T/2} dt \int_{-T/2}^{T/2} dt' \, s_1(t) s_2(t') Q(t - t')$$

After Fourier transformation and using the SGWB assumptions (Lou Eq. 2-48 through 2-49):
$$S = \langle Y \rangle = \frac{T}{2} \int_{-\infty}^{\infty} df \, S_h(f) \Gamma_{12}(f) \tilde{Q}(f)$$

The ORF emerges naturally:

$$\Gamma_{IJ}(f) = \int \frac{d^2\hat{n}}{4\pi} R_A^I(f, \hat{n}) R_A^{J*}(f, \hat{n})$$

**Physical interpretation**: The ORF is the sky-averaged overlap of the two detector responses. It measures how coherently the two detectors respond to the same isotropic GW background. Key properties:

- $\Gamma_{IJ}(f) = \Gamma_{JI}^*(f)$ (symmetry, Lou Eq. 2-51)
- For identical detectors at the same location: $\Gamma_{II}(f)$ is maximal (self-correlation)
- For separated detectors: $\Gamma_{IJ}(f)$ decreases due to phase decorrelation
- $|\Gamma_{IJ}(f)|$ is proportional to the maximum achievable signal-to-noise ratio

### 3.3 OLC Network ORF Formula (Lou Eq. 3-1)

Substituting the OLC response (Eq. 2-42) into the ORF definition yields (Lou Eq. 3-1):

$$\Gamma_{12}(f) = \sum_{\lambda} \int \frac{d^2\hat{n}}{4\pi} \, (\hat{u}_1^a \hat{u}_1^b e^{\lambda}_{ab}(\hat{n})) (\hat{u}_2^c \hat{u}_2^d e^{\lambda}_{cd}(\hat{n})) \times \text{sinc}\left[\frac{\pi f L_1}{c}(1-\hat{u}_1\cdot\hat{n})\right] \text{sinc}\left[\frac{\pi f L_2}{c}(1-\hat{u}_2\cdot\hat{n})\right] \times L_1 L_2 \left(\frac{\pi f}{c}\right)^2 e^{i\alpha_{12}} e^{i\beta_{12}}$$

where the phase factors are:

$$\alpha_{12} = \frac{2\pi f}{c} \left(\frac{L_1}{2}\hat{u}_1 - \frac{L_2}{2}\hat{u}_2 - \vec{x}_1 + \vec{x}_2\right) \cdot \hat{n}$$
$$\beta_{12} = \frac{\pi f}{c}(L_2 - L_1)$$

**Decomposition of terms**:

1. **Geometry factor** (polarization contraction): $\hat{u}_1^a \hat{u}_1^b e^{\lambda}_{ab}(\hat{n}) \times \hat{u}_2^c \hat{u}_2^d e^{\lambda}_{cd}(\hat{n})$ — this is the "polarization antenna pattern" for each detector, contracted over polarizations. It encodes the directional sensitivity of each detector.

2. **Sinc product**: $\text{sinc}[\cdots_1] \times \text{sinc}[\cdots_2]$ — the finite-arm response of each detector, evaluated at potentially different angles and arm lengths.

3. **Quadratic frequency factor**: $L_1 L_2 (\frac{\pi f}{c})^2$ — from the product of the two transfer-function prefactors.

4. **Phase factors** $e^{i\alpha_{12}}$ and $e^{i\beta_{12}}$ — encode the geometric phase difference between the two detectors.

### 3.4 The 6 Independent Geometric Parameters

Computing the ORF for any pair of OLC detectors requires 6 independent parameters (Lou section 3.2):

1. $\vec{x}_1$ — Position of the receiver of detector 1
2. $L_1$ — Arm length of detector 1
3. $\hat{u}_1$ — Laser propagation direction of detector 1
4. $\vec{x}_2$ — Position of the receiver of detector 2
5. $L_2$ — Arm length of detector 2
6. $\hat{u}_2$ — Laser propagation direction of detector 2

Each detector is specified by 3 parameters $\{\vec{x}_i, L_i \hat{u}_i\}$. The emitter position is $\vec{x}_i - L_i \hat{u}_i$, so the 6 parameters fully specify the two-detector network geometry.

### 3.5 Configuration Transformations and ORF Invariance

Lou thesis identifies three **trivial** ORF-invariant transformations and one **non-trivial** ORF-modulus-invariant transformation.

**Trivial transformation 1 — Label exchange** (swap detector 1 $\leftrightarrow$ 2): $\Gamma_{12} \to \Gamma_{21} = \Gamma_{12}^*$, so $|\Gamma_{12}|$ is unchanged.

**Trivial transformation 2 — Translation**: If $\vec{x}_1 \to \vec{x}_1 + \vec{a}$ and $\vec{x}_2 \to \vec{x}_2 + \vec{a}$ for constant $\vec{a}$, the ORF is unchanged because only relative positions enter.

**Trivial transformation 3 — Orthogonal transformation**: Simultaneous rotation/reflection of all 6 parameters preserves the ORF (the integral over all sky directions is rotationally invariant).

**Non-trivial transformation** (Lou Eq. 3-12 through 3-55): Swapping the emit and receive positions of each detector simultaneously preserves the ORF modulus. Specifically:
- Detector 1: $\{\vec{x}_1, L_1, \hat{u}_1\} \to \{\vec{x}_1 - L_1\hat{u}_1, L_1, -\hat{u}_1\}$
- Detector 2: $\{\vec{x}_2, L_2, \hat{u}_2\} \to \{\vec{x}_2 - L_2\hat{u}_2, L_2, -\hat{u}_2\}$

For equal arm lengths $L_1 = L_2$, this transformation yields either $\Gamma \to \Gamma$ or $\Gamma \to \Gamma^*$ (if combined with label swap).

**Geometric meaning**: This is a non-trivial transformation because the new configuration has different physical positions — the laser now propagates in the opposite direction, and the "receiver" of the swapped detector was previously the "emitter". Yet the ORF modulus remains identical. This invariance arises because the transfer function squared modulus $|\mathcal{T}|^2$ is invariant under $\hat{u} \to -\hat{u}$ combined with a redefinition of the phase reference.

**Self-questioning 2**: The non-trivial transformation preserves $|\Gamma_{12}|$ but may change the phase of $\Gamma_{12}$. Since the cross-correlation signal amplitude depends on $|\Gamma_{12}|$ while the optimal filter $\tilde{Q}(f)$ uses the full complex $\Gamma_{12}(f)$, does the phase change affect the optimal filter choice? And practically, can this transformation be used to find configurations with enhanced sensitivity by searching over equivalent ORF-modulus families?

### 3.6 OLC Network Typical Geometric Parameters

A complete specification of an OLC GW detection network requires defining both the individual detector geometry and the network-level configuration. This section summarizes the typical parameter ranges and configurations discussed in the literature.

**Arm length parameters**:
- **Range**: $L \in [0.1, 3]$ Gm (gigameters, $1 \text{ Gm} = 10^6 \text{ km}$)
- **Typical values**: $L = 0.1$ Gm (TianQin-scale), $L = 0.5$ Gm (moderate separation), $L = 2.5$ Gm (LISA-scale)
- **Influence**: Peak frequency $f_{\text{peak}} \propto 1/L$. Doubling $L$ halves the ORF peak frequency.
- **Physical constraint**: Arm length is limited by orbital stability, communication range, and station-keeping capability.

**Baseline length parameters**:
- **Range**: For multi-detector networks, baseline separation $d \in [0.01, 3]$ Gm
- **Definition**: $d$ is the minimum distance between the two detectors (shortest distance between the two link segments)
- **Influence**: Larger $d$ reduces ORF amplitude due to $\alpha_{12}$ phase decorrelation and increases oscillatory structure
- **Typical constraint**: For noise decorrelation, $d \gtrsim 0.1$ Gm is recommended (Lou section 6.2)

**Detector count vs. baseline count**:
- A network of $N$ spacecraft provides $N(N-1)$ possible one-way laser links (each pair has two directions)
- With 4 spacecraft: 12 one-way links, 6 two-way links (6 independent baselines)
- With 6 spacecraft: 30 one-way links, 15 two-way links
- Practical limit: $N = 4$–6 for near-term missions (communication, station-keeping, power constraints)

**Typical network configurations**:

1. **Coplanar triangular** (3 spacecraft in a plane): 3 one-way links per direction, minimum baseline count. Simple orbital dynamics. Equivalent to a single triangular interferometer.

2. **Non-coplanar tetrahedral** (4 spacecraft): 4 detectors (one-way pairs). The tetrahedral geometry provides full 3D sky coverage and is optimal for source localization. This is the configuration analyzed in Lou Chapter 5 for the isosceles trapezoid orbital design.

3. **PTA-like** (shared endpoint): Two detectors sharing one spacecraft (common vertex), mimicking the PTA geometry where Earth is common to all pulsar links. Requires $N = 3$ spacecraft. ORF closely follows Hellings-Downs at small separation.

4. **Isosceles trapezoid** (4 spacecraft on circular orbit): All four spacecraft on the same orbit, forming an isosceles trapezoid. Two detectors formed by opposite sides. This configuration provides stable orbital dynamics and is the primary design studied in Lou Chapter 5.

**Bidirectional link characteristics**:
- Each spacecraft pair supports two one-way links (A→B and B→A) with opposite propagation directions $\hat{u}$ and $-\hat{u}$
- The transfer functions satisfy $\mathcal{T}_{\text{one}}(\hat{u}\cdot\hat{n}) \neq \mathcal{T}_{\text{one}}(-\hat{u}\cdot\hat{n})$ — the OLC response is **inherently asymmetric** under direction reversal
- This asymmetry is a direct consequence of the Doppler measurement: the GW phase evolution differs for light traveling with or against the GW propagation direction
- The bidirectional link pair provides complementary sky coverage: if one direction is at a sinc zero for a particular GW, the opposite direction may have maximal response
- Combining both directions (forming a "two-way link") partially recovers symmetry but introduces additional noise from onboard clock transfer

---

## 4. Key OLC Configurations

### 4.1 PTA-like Configuration

In the PTA-like configuration, two OLC detectors are arranged such that two of the four spacecraft coincide (Lou thesis section on PTA-like comparison). This mimics the Pulsar Timing Array geometry where Earth is a common vertex for multiple pulsar directions.

**Geometry**: Detector 1 has spacecraft at positions $\{\vec{0}, \vec{L}_1\}$ and detector 2 has spacecraft at $\{\vec{0}, \vec{L}_2\}$, sharing the Earth-position spacecraft. The common endpoint serves as both the emitter for one detector and the receiver for the other.

**ORF characteristics**: The shared endpoint eliminates the $\alpha_{12}$ phase factor for the common position, simplifying the expression. The ORF depends primarily on the angle $\gamma$ between the two baselines.

**Comparison to Hellings-Downs curve**: The Hellings-Downs curve, originally derived for PTA, is:

$$\Gamma_{\text{HD}}(\gamma) = \frac{1}{2} + \frac{3}{2} \sin^2\left(\frac{\gamma}{2}\right) \ln\sin\left(\frac{\gamma}{2}\right) - \frac{1}{4} \sin^2\left(\frac{\gamma}{2}\right)$$

where $\gamma$ is the angular separation between two pulsars (or detector baselines).

**Key finding**: For small separation distance $d$ between the detectors, the OLC network ORF closely follows the Hellings-Downs curve as a function of the angle $\theta$ between baselines. This confirms that in the long-wavelength limit ($fL/c \ll 1$), the OLC network behaves like a PTA — the common-mode response dominates and the angular dependence is universal.

**Deviation at large separation**: As the separation increases, the ORF deviates from Hellings-Downs. The peak of the ORF shifts to larger angles, and the overall amplitude decreases. This deviation is caused by:
1. The finite-arm sinc suppression, which depends on the individual detector orientations relative to $\hat{n}$
2. The $\alpha_{12}$ phase factor, which introduces orientation-dependent phase differences between the two detectors
3. The loss of common-mode correlation as the detectors sample different regions of the GW field

### 4.2 Isosceles Trapezoid Configuration

The isosceles trapezoid configuration (Lou Chapter 5, Eq. 5-18) is a practical orbital design where four spacecraft form the vertices of an isosceles trapezoid (Lou Figure 5-2):

- Two detectors, each formed by a pair of opposite sides of the trapezoid
- All four spacecraft lie on the same circular orbit
- The angle between the two baselines is $\theta$
- The minimum distance between detectors is $d$

**Orbital geometry** (Lou Eq. 5-18): The radius of the orbit is:
$$r^2 = \left(\frac{L}{2}\right)^2 + \left(\frac{d}{2}\sec\frac{\theta}{2} + \frac{L}{2}\tan\frac{\theta}{2}\right)^2$$

Given arm length $L$, the radius $r$ and orbital eccentricity $e$ follow from:
$$R^2(1+e)^2 = \left(R + \frac{r}{2}\right)^2 + \frac{3}{4}r^2$$

where $R = 1.496 \times 10^{11}$ m is the Sun-Earth distance.

**ORF variation with geometry**: The numerical analysis (Lou Chapter 5) reveals:

1. **Arm length vs. peak frequency**: The ORF peak frequency is **inversely proportional** to the arm length. Doubling $L$ halves the peak frequency. This follows from the sinc function argument — the first zero and maximum response scale as $1/L$.

2. **Separation effect**: Increasing the separation $d$ between detectors significantly reduces the ORF peak amplitude and introduces oscillatory behavior. The oscillations arise from the $\alpha_{12}$ phase factor and represent partial decoherence of the cross-correlation signal.

3. **Angle $\theta$ dependence**: For fixed $d$ and $L$, varying the baseline angle $\theta$ changes both the peak amplitude and the angular structure of the ORF. The optimal angle maximizes the ORF while maintaining sufficient baseline separation to keep noise uncorrelated.

### 4.3 Sensitivity Comparison with LISA/Taiji/TianQin

Lou Chapter 5 provides quantitative comparisons (Table 5-2, Figures 5-3 through 5-8):

**Strain spectral sensitivity** (Lou Eq. 5-6 for interferometers, Eq. 5-17 for OLC):

- OLC network sensitivity is **better than LISA and Taiji** in both low-frequency and high-frequency bands for equal arm lengths
- **TianQin** has better sensitivity above $10^{-4}$ Hz due to its much shorter arm (0.17 Gm vs 2.5–3 Gm), which shifts its optimal band to higher frequencies
- OLC satellite formation radius and eccentricity are consistently smaller than LISA/Taiji, suggesting better orbital stability

**Noise energy density spectral density** (Lou Eq. 5-20, 5-21):
Converting the strain sensitivity to $\Omega_{\text{GW}}$ and $\Omega_n h^2$ provides a more physically intuitive measure:
$$\Omega_{\text{GW}} = \frac{4\pi^2 f^3}{3H_0^2} S_h(f)$$
$$\Omega_n h^2 = \frac{4\pi^2 f^3}{3(H_0/h)^2 S_n(f)}$$

**Note on $S_n(f)$ for OLC**: Unlike laser interferometers (LISA, TianQin, etc.) whose primary noise is expressed as **strain noise PSD** $S_h(f)$ with units $\text{Hz}^{-1}$, OLC detectors directly measure **frequency shift** $y(t)$, which is a dimensionless quantity (unitless). Therefore $S_n(f)$ in the OLC context is the **frequency-shift noise PSD** with units $\text{Hz}^{-1}$ (power spectral density of a dimensionless quantity). The relationship between frequency-shift noise and equivalent strain noise is $S_h(f) = S_n(f) / (2\pi f L/c)^2$, where $(2\pi f L/c)$ is the dipole transfer-function prefactor. This conversion factor is essential when comparing OLC sensitivity to interferometric detectors on a common strain basis.

---

## 5. Consistency with Hu PRD Framework

Hu et al. Phys. Rev. D 111, 084065 (2025) (arXiv:2411.084065) provides the most general treatment of ORFs for both PTA and laser interferometer detectors, without approximation. The framework is built on the universal one-way link response structure. This section verifies the consistency of our OLC formulas with Hu PRD at three levels: (i) the one-way link response function, (ii) the ORF integral definition, and (iii) the Hellings-Downs limit.

### 5.1 One-Way Link Transfer Function: OLC vs Hu PRD

The central comparison is between the OLC transfer function (Lou Eq. 2-30) and Hu PRD's universal $T_{\text{one}}$ for one-way laser links.

**Hu PRD transfer function** (derived from response function definition Eq. (6)):
$$T_{\text{one}}^{\text{Hu}}(\beta, \hat{n}\cdot\hat{u}) = \frac{1+\hat{n}\cdot\hat{u}}{2} \left[ 1 - \exp\left(-i\beta(1+\hat{n}\cdot\hat{u})\right) \right]$$
where $\beta = 2\pi f L / c$ is the dimensionless frequency parameter.

**OLC transfer function** (Lou Eq. 2-30):
$$\mathcal{T}_{\text{one}}^{\text{OLC}}(\hat{u}\cdot\hat{n}, f) = \frac{i 2\pi f L}{c} \cdot \text{sinc}\left[\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right] \cdot \exp\left[-i\frac{\pi f L}{c}(1 - \hat{u}\cdot\hat{n})\right]$$

**Side-by-side comparison**:

| Property | Hu PRD $T_{\text{one}}$ | OLC $\mathcal{T}_{\text{one}}$ |
|----------|------------------------|-------------------------------|
| **Physical measurement** | Pulse arrival time (PTA, integral of frequency shift) | Frequency shift (OLC, direct measurement) |
| **Mathematical form** | $[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$ | $\text{sinc}[\cdots] \cdot e^{-i[\cdots]}$ |
| **Low-frequency limit** ($f \to 0$) | $\sim \frac{\beta}{2}(1+\hat{n}\cdot\hat{u})$ (linear) | $\sim i \frac{2\pi f L}{c}$ (linear in $f$) |
| **Long-wavelength response** | $\propto (1+\hat{n}\cdot\hat{u})$ — **forward-backward asymmetric** | $\propto 1$ — depends on $(1-\hat{u}\cdot\hat{n})$ through sinc |
| **Sensitivity direction** | Maximum for GW from behind ($\hat{n}\cdot\hat{u} \approx -1$) | Maximum for GW from ahead ($\hat{u}\cdot\hat{n} \approx 1$) |
| **Zero structure** | No zeros (exponential oscillates) | Zeros at $\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n}) = n\pi$ ($n \in \mathbb{Z}^+$) |
| **Short-wave limit** ($fL/c \gg 1$) | Oscillatory, $|T_{\text{one}}| \leq 1$ | $\sim O(1/L)$ suppression via sinc envelope |

**Why the formulas differ**: The two transfer functions correspond to **different physical observables**:

- **Hu PRD (PTA convention)**: PTA measures pulse **arrival time**, which is the *integral* of frequency shift over time. The response function $T_{\text{one}}^{\text{Hu}}$ describes the timing residual $z(t) = \int y(t) dt$. The factor $(1+\hat{n}\cdot\hat{u})$ appears because the pulse arrival time depends on both the Doppler shift along the line of sight and the integration over the light travel time.

- **OLC convention**: OLC measures **frequency shift** directly, $y(t) = \Delta\nu/\nu_0$, which is the *time derivative* of the timing residual. The OLC transfer function $\mathcal{T}_{\text{one}}^{\text{OLC}}$ is obtained by differentiating the timing residual response. The derivative operation converts the exponential form $[1-e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$ into the sinc form $\text{sinc}[\cdots]\cdot e^{-i[\cdots]}$ multiplied by the $i2\pi f$ prefactor.

**Short-wave limit comparison**: For $fL/c \gg 1$ (short wavelength relative to arm length):
- Hu PRD: $|T_{\text{one}}^{\text{Hu}}|$ oscillates between 0 and 1 — no net suppression but rapid phase oscillations that average to zero under integration.
- OLC: $|\mathcal{T}_{\text{one}}^{\text{OLC}}| \sim \frac{c}{2\pi f L} \cdot \frac{1}{|\pi f L/c(1-\hat{u}\cdot\hat{n})|} = O(1/(fL/c)^2)$ — sinc provides explicit $O(1/L^2)$ envelope suppression, with zeros at specific frequencies corresponding to complete destructive interference of the GW phase along the path.

**Response tensor decomposition**: For OLC detectors, the response tensor in Hu's notation ($D_{ab}(\hat{n}, f)$ as in Hu Eq. (6)) is:
$$D_{ab}^{\text{OLC}} = \frac{1}{2} u_a u_b \mathcal{T}_{\text{one}}(\hat{u}\cdot\hat{n}, f) e^{-i2\pi f \hat{n}\cdot\vec{x}/c}$$

This is structurally consistent with Hu's framework:
- The response is linear in the metric perturbation (single-photon, linearized gravity)
- The directional dependence factorizes into polarization contraction $e^A_{ab}$ and frequency-dependent scalar $\mathcal{T}$
- Hu Eq. (6) gives the general response function form for any one-way link; OLC specifies the particular functional form appropriate for atomic clock frequency-shift measurements

### 5.2 ORF Definition Consistency

**Hu PRD ORF definition** (Hu Eq. (8)):
$$\Gamma_{IJ}(f) = \frac{1}{8\pi} \int d^2\Omega_{\hat{n}} \sum_A R_A^I(f, \hat{n}) R_A^{J*}(f, \hat{n})$$

The factor of $1/8\pi$ equals $1/(4\pi)$ times the $1/2$ convention from two-sided spectral density (equivalently, $1/4\pi$ for one-sided). Our OLC ORF definition (Eq. 3-1) uses:
$$\Gamma_{IJ}(f) = \int \frac{d^2\hat{n}}{4\pi} R_A^I(f, \hat{n}) R_A^{J*}(f, \hat{n})$$

These differ only by the convention factor, which is absorbed into the SGWB spectral density normalization. The physical content — sky-averaged overlap of detector responses — is identical.

**ORF as inner product**: In Hu's framework, the ORF is an inner product in function space:
$$\Gamma_{IJ}(f) = \langle R^I(f, \hat{n}), R^J(f, \hat{n}) \rangle_{\hat{n}}$$
where the inner product integrates over the sky with weight $d^2\hat{n}/4\pi$. This interpretation, shared with Lou thesis ("重叠约化函数 $\Gamma_{IJ}(f)$ 可理解为两个探测器对全天空各入射方向引力波响应的加权平均"), makes clear why the ORF measures the "overlap" of detector geometries.

### 5.3 Full ORF for Two One-Way Links

**Hu PRD full formula** (Hu Eq. (24)): Hu Eq. (24) gives the complete ORF between two one-way links with arbitrary arm lengths $L_1, L_2$, arbitrary directions $\hat{u}_1, \hat{u}_2$, and arbitrary receiver positions $\vec{x}_1, \vec{x}_2$. Our OLC network ORF (Eq. 3-1) is a direct specialization of Hu Eq. (24) to the OLC case, with:
- Explicit polarization contraction over $+$ and $\times$ modes
- The sinc-based OLC transfer function (rather than Hu's exponential form)
- The phase factors $\alpha_{12}$ and $\beta_{12}$ that arise from the specific receiver-position convention

### 5.4 Hellings-Downs as the Long-Wavelength Limit

The Hellings-Downs curve is the ORF for PTA in the limit $f \to 0$ (long-wavelength limit). In this limit:
- The transfer function becomes $\mathcal{T} \to \frac{i 2\pi f L}{c}$ (dipole response, sinc $\to 1$)
- The phase factors become unity
- The ORF reduces to a purely geometric function of the angle $\gamma$ between baselines

The fact that OLC detectors approach the Hellings-Downs curve at small separation confirms the consistency with Hu's framework: both PTA and OLC detectors reduce to the same geometric response in the long-wavelength, point-detector limit. The deviation from Hellings-Downs at larger frequencies/separations is a natural consequence of the finite-arm transfer function in the full framework.

### 5.5 Consistency Check Summary

| Aspect | Hu PRD | Lou OLC | Consistent? |
|--------|--------|---------|-------------|
| Response function definition | $R_A = D_{ab}e^A_{ab}$ (Hu Eq. 6) | $R_A = \frac{1}{2}u^a u^b e^A_{ab} \mathcal{T} e^{-i2\pi f\hat{n}\cdot\vec{x}/c}$ | Yes (same structure) |
| $T_{\text{one}}$ formula | $\frac{1+\hat{n}\cdot\hat{u}}{2}[1-e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$ | $\frac{i2\pi fL}{c}\text{sinc}[\cdots]e^{-i[\cdots]}$ | Yes (derivative convention) |
| ORF definition | $\frac{1}{8\pi}\int d^2\Omega \sum R^I R^{J*}$ (Hu Eq. 8) | $\int \frac{d^2\hat{n}}{4\pi} R^I R^{J*}$ | Yes (convention factor) |
| Full ORF two one-way links | Hu Eq. (24) | Eq. 3-1 (specialization) | Yes (compatible) |
| SGWB assumptions | Stationary, Gaussian, isotropic, unpolarized | Same four assumptions | Yes (identical) |
| Cross-correlation signal | $S \propto T S_h \Gamma \tilde{Q}$ | Same | Yes (identical) |
| Hellings-Downs limit | PTA long-wavelength | OLC small-separation | Yes (converge) |

---

## 6. Uncertainties and Open Questions

### 6.1 Model Limitations

1. **Neglected GW polarizations**: The framework assumes only the standard $+$ and $\times$ polarizations of general relativity. Alternative theories of gravity may introduce additional polarizations (scalar, vector) that would modify the response function and ORF structure.

2. **Single-frequency treatment**: The derivation assumes a monochromatic or narrow-band analysis. A broadband SGWB would require integrating over frequency with a frequency-dependent filter $\tilde{Q}(f)$. The optimal filter maximizes the signal-to-noise ratio:
   $$\frac{S}{N} = \frac{\int df S_h(f) \Gamma_{12}(f) \tilde{Q}(f)}{\sqrt{\int df |\tilde{Q}(f)|^2 P_n(f)}}$$
   where the noise power spectrum $P_n(f)$ depends on the specific noise sources.

3. **Noise correlation between detectors**: The cross-correlation analysis assumes the two detectors have uncorrelated noise. At small separations, shared environmental noise (seismic, thermal, etc.) can create correlations that mimic a GW signal. The minimum separation for noise independence is still an open question (Lou section 6.2).

4. **Orbital dynamics**: The analysis assumes fixed spacecraft positions. Real orbits have perturbations, drift, and requires active station-keeping, which may introduce additional noise and time-dependent variations in the ORF.

### 6.2 Incomplete ORF Transformation Theory

Lou section 6.2 explicitly states that the complete set of ORF-invariant transformations has not been found. The non-trivial transformation (swapping emit/receive positions) is only one member of a potentially larger family. Finding the complete solution set would:
- Allow more systematic exploration of configuration space
- Potentially reveal configurations with enhanced ORF
- Provide deeper insight into the geometric structure underlying the ORF

### 6.3 Peak Frequency and Arm Length Scaling

The observation that ORF peak frequency scales as $1/L$ is confirmed numerically, but the detailed functional dependence for different configurations remains an area for further study. In particular:

- How does the peak frequency shift vary with the angle $\theta$ between detectors?
- What is the precise relationship between separation $d$ and the oscillation period of the ORF?
- For the isosceles trapezoid, is there an optimal combination of $L$, $d$, and $\theta$ that maximizes sensitivity to a specific SGWB spectrum?

### 6.4 Non-Trivial Transformation: Physical Interpretation

The physical meaning of the non-trivial transformation (swapping emit/receive while preserving ORF modulus) is not fully understood. Key questions:

- What is the deeper geometric reason for this invariance? Does it correspond to a symmetry of the underlying integrand of the ORF?
- Are there practical advantages of one configuration over another within the same ORF-modulus family? (e.g., different noise properties, different orbital stability requirements)
- Does this transformation extend to networks of more than two detectors?

### 6.5 Cross-Correlation with Directed Sources

While the framework focuses on SGWB detection (isotropic background), the ORF derivation also applies to individual plane-wave sources. The non-trivial transformation was found by requiring the ORF integrand to be equal for the same GW propagation direction $\hat{n}$, making it applicable to directed source detection as well. However, the optimal configuration for detecting a specific source (rather than an isotropic background) may differ from the SGWB-optimal configuration.

### 6.6 Numerical Validation Gaps

The ORF solver script (`scripts/01-olc-orf-solver.py`) provides numerical confirmation of many analytical predictions, but:

- The Hellings-Downs comparison was only done for specific (small-separation) configurations. A systematic study over the full parameter space of $(L, d, \theta)$ would strengthen the conclusion about when and how the deviation from Hellings-Downs occurs.
- The sensitivity comparison with LISA/Taiji/TianQin uses noise models from different sources. A consistent treatment of all noise sources (including those not included in the current models) would be needed for a definitive comparison.

### 6.7 Verification Against Project Code: ORF Solver

This section verifies that the formulas in this document match the implementation in `scripts/01-olc-orf-solver.py` and cross-references the extracted memory files.

**Transfer function implementation** (Lou Eq. 2-30): The solver implements the OLC one-way transfer function as:
```python
prefac = 1j * 2.0 * np.pi * abs(f) * L / c
beta = 2.0 * np.pi * f * L / c
one_minus = 1.0 - np.dot(u_hat, n_hat)
sinc_arg = np.pi * f * L / c * one_minus
sinc_v = np.sin(sinc_arg) / sinc_arg if sinc_arg != 0 else 1.0
phase = np.exp(-1j * beta * one_minus / 2.0)
T_one = prefac * sinc_v * phase
```
This matches Eq. (2-30): $\mathcal{T} = \frac{i 2\pi f L}{c} \cdot \text{sinc}[\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})] \cdot \exp[-i\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})]$. The `beta/2 = \pi f L/c` in the phase factor correctly reproduces the exponent.

**ORF calculation framework** (Eq. 3-1): The solver numerically integrates the ORF over the sky using Monte Carlo sampling of $\hat{n}$, applying the full response formula:
- Polarization contraction: `R_A = (u1^a u1^b e^A_ab) * (u2^c u2^d e^A_cd)`
- Transfer functions for both detectors independently
- Phase factor $\alpha_{12}$ and $\beta_{12}$ using the receiver-position convention
- Sky average via numerical integration

This is a direct implementation of Eq. (3-1) without approximation.

**Cross-reference with memory files**:
- `memory/01-olc-orf-formulas.md`: Correctly extracts Hu PRD's $T_{\text{one}}$ formula and ORF definitions (Eq. 7, Eq. 8, Eq. 11, Eq. 24). No inconsistencies found.
- `memory/02-lou-olc-transfer-function.md`: Correctly identifies the sinc vs. exponential distinction between OLC and PTA/interferometer conventions. The derivation chain from frequency shift to sinc form is correctly captured.
- `memory/10-olc-triangular-chiral-orf-iteration6.md`: Contains the triangular configuration analysis including chiral ORF decomposition. Consistent with the polarization contraction framework in Section 3.3.

**Errors or outdated information**: No errors or inconsistencies were found. The solver correctly implements the formulas from Lou thesis and the memory files correctly extract the Hu PRD framework. The only noted limitation is that the solver header references "Hu PRD 111, 084065" but does not explicitly cite specific equation numbers (Eq. 6, 8, 24) — this is remedied by the references added in Section 5 of this document.

---

## Self-Reflection Questions

**Question A**: The sinc function in the transfer function arises from integrating the GW phase over the light path. For a PTA (essentially $L \to 0$ but effectively measuring over parsec-scale distances to pulsars), the transfer function is also approximately $\frac{i2\pi f L}{c}$ at low frequencies. What is the fundamental difference between a PTA's "arm length" (light travel time to pulsar) and an OLC's arm length (distance between satellites), and does this difference affect the scaling of sensitivity with $L$?

**Question B**: The ORF is defined as the overlap of two detector responses averaged over the sky. For two identical detectors at the same location (perfect overlap), $|\Gamma_{II}| = 1$ (maximal). But for two OLC detectors at different locations, the ORF decreases. Is there a simple analytic upper bound on $|\Gamma_{12}|$ as a function of the separation distance, analogous to how the Hellings-Downs curve provides a lower bound (in a sense) for PTAs?

**Question C**: The non-trivial transformation preserves ORF modulus but changes the phase. Since the signal-to-noise ratio depends only on $|\Gamma_{12}|$, the transformation appears physically irrelevant for SGWB detection. However, for detecting individual sources or for multi-detector networks where one detector is correlated with multiple others, the phase may matter. Under what circumstances does the ORF phase have observable consequences?
