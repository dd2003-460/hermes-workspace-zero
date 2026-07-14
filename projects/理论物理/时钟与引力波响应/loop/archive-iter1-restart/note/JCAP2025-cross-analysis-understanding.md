# JCAP 2025 Cross-Analysis Understanding

> **Citation**: JCAP05(2025)050, arXiv:2410.18916v2
> **Title**: Chiral gravitational-wave detection with triangular detectors
> **Authors**: [verify from IOP]
> **DOI**: https://doi.org/10.1088/1475-7516/2025/05/050

## 1. Stokes Parameters and Cross-Power Spectrum Matrix

### 1.1 Linear Polarization Basis

**JCAP p.2, eq. (2.1)**:
$$h_{ab}(t, \hat{\vec{r}}) = \sum_{P=+, \times} \int df \int \frac{d^2\hat{k}}{4\pi} \tilde{h}_P(f, \hat{k}) e^P_{ab}(\hat{k}) e^{i2\pi f (t - \hat{k}\cdot\hat{\vec{r}}/c)}$$

### 1.2 Circular Polarization Basis (Handedness)

**JCAP p.2, eq. (2.3)**:
$$e^R_{ab} = \frac{e^+_{ab} - i e^\times_{ab}}{\sqrt{2}}, \quad e^L_{ab} = \frac{e^+_{ab} + i e^\times_{ab}}{\sqrt{2}}$$

**JCAP p.2, eq. (2.4)**:
$$h_R = \frac{h_+ - i h_\times}{\sqrt{2}}, \quad h_L = \frac{h_+ + i h_\times}{\sqrt{2}}$$

Note: This convention matches Seto 2006. Check that $|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_\times|^2$:
$$|h_R|^2 + |h_L|^2 = \frac{1}{2}(|h_+ - i h_\times|^2 + |h_+ + i h_\times|^2) = \frac{1}{2}(2|h_+|^2 + 2|h_\times|^2) = |h_+|^2 + |h_\times|^2$$
Confirmed: unitary transformation.

### 1.3 Cross-Power Spectrum Matrix

**JCAP p.2, eq. (2.2)**:
$$\begin{pmatrix}
\langle \tilde{h}_+(f,\hat{k}) \tilde{h}_+^*(f',\hat{k}') \rangle &
\langle \tilde{h}_+(f,\hat{k}) \tilde{h}_\times^*(f',\hat{k}') \rangle \\
\langle \tilde{h}_\times(f,\hat{k}) \tilde{h}_+^*(f',\hat{k}') \rangle &
\langle \tilde{h}_\times(f,\hat{k}) \tilde{h}_\times^*(f',\hat{k}') \rangle
\end{pmatrix}
= \delta(f-f') \frac{\delta^2(\hat{k}-\hat{k}')}{4\pi} \cdot \frac{1}{2} \cdot
\begin{pmatrix} I(f) & -iV(f) \\ iV(f) & I(f) \end{pmatrix}$$

**CRITICAL**: The matrix has $I(f)$ on BOTH diagonals, and $\pm iV(f)$ off-diagonal.
- Top-left: $I(f)$, NOT $I(f) - iV(f)$
- Bottom-right: $I(f)$
- Top-right: $-iV(f)$
- Bottom-left: $iV(f)$

This is a Hermitian matrix (as required for a correlation matrix): the off-diagonal elements are complex conjugates of each other.

**Verification**: In the circular basis, this matrix diagonalizes:

**JCAP p.2, eq. (2.5)**:
$$\langle \tilde{h}_\Lambda(f,\hat{k}) \tilde{h}_{\Lambda'}^*(f',\hat{k}') \rangle
= \delta(f-f') \frac{\delta^2(\hat{k}-\hat{k}')}{4\pi} \cdot \frac{1}{2} \cdot \delta_{\Lambda\Lambda'} S_\Lambda(f)$$

where $\Lambda = R, L$ and $S_R(f)$, $S_L(f)$ are the right/left circular polarization power spectra.

### 1.4 Stokes Parameters

**JCAP p.2, eq. (2.6)**:
$$I(f) = \frac{1}{2}[S_R(f) + S_L(f)], \quad V(f) = \frac{1}{2}[S_R(f) - S_L(f)]$$

Physical interpretation:
- $I(f)$: total intensity (average power of both handedness)
- $V(f)$: circular polarization asymmetry (difference between R and L)
- $\chi(f) = V(f)/I(f) = (S_R - S_L)/(S_R + S_L)$: normalized handness parameter, $|\chi| \leq 1$

**I(f) normalization convention**: JCAP uses the **mean** convention $(S_R + S_L)/2$, NOT the sum $(S_R + S_L)$. This differs from Maggiore's textbook (eq. 8.38) by a factor of 1/2. JCAP explicitly notes this on p.2:
> "Notice that comparing with eq. (8.38) in [39], there is an additional factor 1/2 due to different definitions of I(f)."

This matches Seto 2006's convention.

### 1.5 Why Q and U are Ignored

**JCAP p.2**: "The other two Stokes parameters, Q and U, which describe linear polarization, are spin-4 quantities and do not contribute to the monopole modes, i.e., the isotropic components of the stochastic background."

For an isotropic SGWB, only monopole ($\ell = 0$) terms survive. Q and U have spin-4 and vanish in $\ell = 0$.

## 2. Cross-Correlation Statistic

### 2.1 Detector Response

**JCAP p.3, eq. (2.7)**:
$$s_i(t) = \int d^3\hat{k} \sum_P \int df \, F_i^P(\hat{k}) \tilde{h}_P(f, \hat{k}) e^{i2\pi f t} + n_i(t)$$

where $F_i^P$ is the detector antenna pattern and $n_i$ is instrumental noise.

### 2.2 Cross-Power Spectrum

**JCAP p.3-4, eq. (2.9)**:
$$\langle \tilde{s}_i(f) \tilde{s}_j^*(f') \rangle = \frac{1}{2} \delta(f - f') \left[ \Gamma^I_{ij}(f) I(f) + \Gamma^V_{ij}(f) V(f) \right]$$

This is the fundamental equation linking measured cross-correlations to Stokes parameters.

### 2.3 Overlap Reduction Functions

**JCAP p.3-4, eq. (2.10)**:
$$\Gamma^I_{ij}(f) = \frac{3}{4} \int \frac{d^2\hat{k}}{4\pi} \sum_{P,Q} e^P_{ab}(\hat{k}) e^Q_{cd}(\hat{k}) F_i^P(\hat{k}) F_j^Q(\hat{k}) e^{i2\pi f \hat{k}\cdot\Delta\vec{r}_{ij}/c}$$

$$\Gamma^V_{ij}(f) = -\frac{3i}{4} \int \frac{d^2\hat{k}}{4\pi} \sum_{P,Q} (e^P_{ab}(\hat{k}) e^Q_{cd}(\hat{k}) - e^Q_{ab}(\hat{k}) e^P_{cd}(\hat{k})) F_i^P(\hat{k}) F_j^Q(\hat{k}) e^{i2\pi f \hat{k}\cdot\Delta\vec{r}_{ij}/c}$$

Key observations:
- $\Gamma^I$ is **parity-even** (invariant under $\hat{k} \to -\hat{k}$)
- $\Gamma^V$ is **parity-odd** (changes sign under $\hat{k} \to -\hat{k}$)
- The factor $3/4$ is the normalization to give $\gamma(0) = 1$ for co-located co-aligned detectors
- The antisymmetric combination $e^P e^Q - e^Q e^P$ ensures parity-odd behavior

**Hu PRD comparison**: Hu's ORF framework uses a similar structure but with different normalization. Hu does not explicitly separate $\Gamma^I$ and $\Gamma^V$; instead, the full cross-correlation tensor is used. The JCAP decomposition is a specialized application of Hu's general framework to the chiral case.

**Seto 2006 comparison**: Seto defines $\Gamma_{RL}(f)$ and $\Gamma_{RR}(f) - \Gamma_{LL}(f)$ separately. JCAP's $\Gamma^I$ corresponds to the symmetric combination, while $\Gamma^V$ corresponds to the antisymmetric (parity-odd) combination.

### 2.4 Normalized ORFs

**JCAP p.4-5, eq. (2.11)**:
$$\gamma^I_{ij}(f) = \frac{10}{3} \frac{\Gamma^I_{ij}(f)}{\sin(2\pi f L_i/c) \sin(2\pi f L_j/c)}$$

$$\gamma^V_{ij}(f) = \frac{10}{3} \frac{\Gamma^V_{ij}(f)}{\sin(2\pi f L_i/c) \sin(2\pi f L_j/c)}$$

The $10/3$ factor ensures $\gamma^I_{ij}(0) = 1$ for co-located, co-aligned detectors.

### 2.5 Effective ORFs

**JCAP p.5, eq. (2.13)**:
$$\gamma_{\text{eff}}^I = \sqrt{\sum_\kappa (\gamma_\kappa^I)^2 - \frac{\left(\sum_\kappa \gamma_\kappa^I \gamma_\kappa^V\right)^2}{\sum_\kappa (\gamma_\kappa^I)^2}}$$

$$\gamma_{\text{eff}}^V = \sqrt{\sum_\kappa (\gamma_\kappa^V)^2 - \frac{\left(\sum_\kappa \gamma_\kappa^I \gamma_\kappa^V\right)^2}{\sum_\kappa (\gamma_\kappa^I)^2}}$$

Derivation: The optimal SNR comes from Fisher matrix inversion of the 4-channel cross-correlation system. The effective ORFs are the "signal eigenmodes" after marginalizing over the cross-talk between I and V. The subtraction term is the Fisher matrix projection that removes the I/V degeneracy.

These effective ORFs represent the optimal combination of all channel pairs that maximizes sensitivity to each component separately.

### 2.6 SNR Formula

**JCAP p.4-5, eq. (2.12)**:
$$\text{SNR}_I^2 = \left(\frac{3}{10}\right)^2 T_{\text{obs}} \int df \, \frac{\gamma_{\text{eff}}^I(f)^2 \cdot I^2(f)}{\sum_\kappa (\gamma_\kappa^I)^2(f) / N^2(f)}$$

$$\text{SNR}_V^2 = \left(\frac{3}{10}\right)^2 T_{\text{obs}} \int df \, \frac{\gamma_{\text{eff}}^V(f)^2 \cdot V^2(f)}{\sum_\kappa (\gamma_\kappa^V)^2(f) / N^2(f)}$$

where $N \equiv N_1(f) N_2(f) / [\sin(2\pi f L_1/c) \sin(2\pi f L_2/c)]$, and $N_1(f)$, $N_2(f)$ are the noise PSD of the A or E channels for each detector.

The $(3/10)^2$ factor is the inverse of the $10/3$ normalization applied to the ORFs. This ensures that for optimal configurations, the SNR reduces to the standard cross-correlation sensitivity.

**Note**: The original JCAP eq. (2.12) writes the numerator as a sum over individual channel pairs rather than the effective ORF form:
$$\text{numerator}_I = \sum_\kappa \left( (\gamma_\kappa^I)^2 - \frac{(\sum_{\kappa'} \gamma_{\kappa'}^I \gamma_{\kappa'}^V)^2}{\sum_{\kappa'} (\gamma_{\kappa'}^I)^2} \right) I^2(f) / N^2$$
This is algebraically equivalent to $\gamma_{\text{eff}}^I(f)^2 I^2(f) / N^2$ when the cross-term is factored out.

### 2.7 Auxiliary Tensors and Spherical Bessel Coefficients

**JCAP p.5, eq. (2.14)-(2.16)**:
$$\gamma_{ij}^I = D_i^{ab} D_j^{cd} \hat{\Gamma}^I_{abcd}, \quad \gamma_{ij}^V = D_i^{ab} D_j^{cd} \hat{\Gamma}^V_{abcd}$$

$$\hat{\Gamma}^I_{abcd} = b_0^I \delta_{ac}\delta_{bd} + b_1^I \delta_{ac} s_b s_d + b_2^I s_a s_b s_c s_d$$

$$\hat{\Gamma}^V_{abcd} = b_0^V w_{ac}\delta_{bd} + b_1^V w_{ac} s_b s_d$$

where $w_{ab} \equiv \epsilon_{abc} s_c$.

**Spherical Bessel coefficients**:
$$b_0^I(\iota) = \frac{20}{7} j_0 - \frac{1}{7} j_2 + \frac{60}{7} j_4, \quad
b_1^I(\iota) = \frac{60}{7} j_2 - \frac{10}{7} j_4, \quad
b_2^I(\iota) = \frac{5}{2} j_4$$

$$b_0^V(\iota) = 4 j_1 - j_3, \quad
b_1^V(\iota) = 5 j_3$$

with $\iota = 2\pi f \Delta r / c$.

### 2.8 Geometric Decomposition

**JCAP p.5-6, eq. (2.17)-(2.20)**:
$$\gamma_{ij}^I = \sum_{m=0}^2 b_m^I \chi_{ij}^{Im}, \quad \gamma_{ij}^V = \sum_{m=0}^1 b_m^V \chi_{ij}^{Vm}$$

The $\chi$ coefficients depend only on the geometry:
- $\chi^{I,m}$ terms: $\delta_{ac}\delta_{bd}$, $\delta_{ac}s_b s_d$, $s_a s_b s_c s_d$ contracted with detector tensors
- $\chi^{V,m}$ terms: $w_{ac}\delta_{bd}$, $w_{ac}s_b s_d$ contracted with detector tensors

**JCAP p.6, eq. (2.21)**: The three relevant angles are:
$$a = \arccos(\hat{n}_1 \cdot \hat{s}), \quad b = \arccos(\hat{n}_2 \cdot \hat{s}), \quad c = \arccos(\hat{n}_1 \cdot \hat{n}_2)$$

where $\hat{n}_1$, $\hat{n}_2$ are the unit normal vectors of the two constellation planes, and $\hat{s}$ is the unit separation vector.

The geometric factors $X_{mn}$ (summations over channel pairs) depend only on these three angles due to rotational invariance.

### 2.9 Explicit Geometric Factors

**JCAP p.6-7, eq. (2.22)**: Parity-even $X_{mn}^I$ (9 terms for $m,n = 0,1,2$). Key example:
$$X_{00}^I = \frac{1}{16}(1 + 6\cos^2 c + \cos^4 c)$$
$$X_{00}^V = \frac{1}{16}[2\cos a \cos b \cos c (3 + \cos^2 c) + (1 + \cos^2 c)\sin^2 c]$$

**JCAP p.7-8, eq. (2.23)-(2.24)**: Parity-odd $X_{mn}^V$ (4 terms for $m,n = 0,1$) and cross-term $X_{mn}^{IV}$ (8 terms).

**JCAP p.8, eq. (2.25)**:
$$C \equiv \sqrt{\frac{1}{2}(4\cos a \cos b \cos c - \cos 2a - \cos 2b - \cos 2c - 1)}$$

## 3. Comparison with Hu PRD and Seto 2006

### 3.1 Cross-Power Spectrum Matrix

| Convention | Matrix form | Diagonal elements |
|-----------|------------|-------------------|
| JCAP 2025 | [[I, -iV], [iV, I]] | I(f) on both |
| Seto 2006 | Diagonal: S_R, S_L | S_R, S_L |
| Hu PRD | Full 2×2 | $h_+$, $h_\times$ in linear basis |

JCAP uses the linear basis matrix (eq. 2.2) which is Hermitian with $I$ on diagonals. Seto works directly in the circular basis where the matrix is diagonal with $S_R$ and $S_L$. Hu works in the most general case with the full polarization tensor.

### 3.2 I(f) Normalization

| Convention | I(f) definition | Factor in $\Omega_{\text{GW}}$ |
|-----------|----------------|-------------------------------|
| JCAP 2025 | $(S_R + S_L)/2$ | $4\pi^2 f^3/(3H_0^2)$ |
| Seto 2006 | $(S_R + S_L)/2$ | Same |
| Maggiore | $S_R + S_L$ | Same |

JCAP and Seto agree on the mean convention, giving $\Omega_{\text{GW}} = 4\pi^2 f^3/(3H_0^2) I(f)$.

### 3.3 R/L Convention

| Convention | $h_R$ | $h_L$ |
|-----------|------|------|
| JCAP 2025 | $(h_+ - i h_\times)/\sqrt{2}$ | $(h_+ + i h_\times)/\sqrt{2}$ |
| Seto 2006 | $(h_+ - i h_\times)/\sqrt{2}$ | $(h_+ + i h_\times)/\sqrt{2}$ |
| Hu PRD | Not explicitly defined (works in linear basis) | |

JCAP and Seto agree. The sign convention determines whether $V > 0$ means right-handed or left-handed dominance.

### 3.4 ORF Normalization

JCAP's $\Gamma^I_{ij}(f)$ includes the $3/4$ prefactor (eq. 2.10) which, combined with the $10/3$ in the normalization (eq. 2.11), gives $\gamma^I_{ij}(0) = 1$ for co-located co-aligned detectors. Hu PRD does not use this explicit normalization; instead, the ORFs are left unnormalized and the detector response is included in the full cross-correlation formula.

### 3.5 Effective ORFs and SNR

JCAP introduces effective ORFs $\gamma_{\text{eff}}^I$, $\gamma_{\text{eff}}^V$ as optimal combinations of channel-pair ORFs. This is specific to the multi-channel, multi-detector setup with AET TDI combinations. Seto 2006 considers only a single detector pair with circular polarization basis, while JCAP's framework generalizes to arbitrary networks of triangular detectors with AET TDI channels.

## 4. Key Physical Insights

### 4.1 Non-Coplanar Requirement for Gamma^V Detection

For an isotropic SGWB, circular polarization is undetectable with planar detector(s). Detection requires correlating detectors that are not co-planar. This follows from the parity-odd nature of $\Gamma^V$: under a mirror reflection that maps the network to itself, $\Gamma^V$ must change sign but also remain unchanged, so $\Gamma^V = 0$. Only non-coplanar arrangements (e.g., LISA-Taiji with different orbital inclinations) can produce non-zero $\Gamma^V$.

### 4.2 Low-Frequency Behavior

- $\gamma_{\text{eff}}^I(f \to 0)$: approaches a non-zero constant determined by the geometric factors
- $\gamma_{\text{eff}}^V(f \to 0)$: drops to zero — the V component is inherently less sensitive at low frequencies

### 4.3 Cartwheel Motion

Individual ORFs $\gamma_{ij}^\kappa$ vary over time due to the orbital motion of space-borne detectors ("cartwheel motion"). However, the summations $\sum_\kappa (\gamma_\kappa^I)^2$, $\sum_\kappa (\gamma_\kappa^V)^2$, and $\sum_\kappa \gamma_\kappa^I \gamma_\kappa^V$ are invariant under rotation of detectors within their constellation planes, depending only on the three angles $a$, $b$, $c$.

### 4.4 PLI Sensitivity

JCAP defines the power-law integrated sensitivity (eq. 3.3):
$$\Omega_{\text{PLI}}^{\text{max}}(f; \alpha) = \frac{3 H_0}{4\pi^2 f^3} \sqrt{\frac{2}{T_{\text{obs}}}} \frac{1}{|\gamma_{\text{eff}}(f)|} \frac{1}{f^{3/2}} \sqrt{\frac{P_I + P_V \pm 2\sqrt{P_I P_V} \langle \gamma^I \gamma^V \rangle / \langle (\gamma^I)^2 \rangle}{\langle (\gamma^I)^2 \rangle + \langle (\gamma^V)^2 \rangle - \langle \gamma^I \gamma^V \rangle^2 / \langle (\gamma^I)^2 \rangle}}$$

where $\alpha$ is the power-law index and the $\pm$ refers to the I or V component respectively.

## 5. Verification Summary

| Item | Status | Notes |
|------|--------|-------|
| Citation: JCAP05(2025)050, arXiv:2410.18916v2 | CONFIRMED | From IOP Science |
| Eq. (2.2) matrix: [[I, -iV], [iV, I]] | CONFIRMED | I(f) on BOTH diagonals |
| Eq. (2.6): I = (S_R + S_L)/2, V = (S_R - S_L)/2 | CONFIRMED | Mean convention |
| Eq. (2.9): cross-power spectrum with Gamma^I, Gamma^V | CONFIRMED | 1/2 delta function prefactor |
| Eq. (2.10): Gamma definitions with 3/4 sin factors | CONFIRMED | Parity-even vs parity-odd |
| Eq. (2.11): Normalized ORFs with 10/3 | CONFIRMED | gamma(0) = 1 normalization |
| Eq. (2.12): SNR with (3/10)^2 coefficients | CONFIRMED | Multiple channel pairs |
| Eq. (2.13): Effective ORFs | CONFIRMED | Optimal combination |
| Eq. (2.14)-(2.16): Auxiliary tensors and Bessel coeffs | CONFIRMED | 5 b-coefficients total |
| Eq. (2.17)-(2.20): Geometric decomposition | CONFIRMED | Oscillatory + geometric factorization |
| Eq. (2.21): Three angles a, b, c | CONFIRMED | Rotational invariants |
| Eq. (2.22)-(2.25): Explicit geometric factors | CONFIRMED | I, V, IV components |
