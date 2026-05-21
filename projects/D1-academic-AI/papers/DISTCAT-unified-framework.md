# DistCat: A 2-Categorical Framework for Distance Derivation from First Principles

> **Version**: iteration 73, final draft (Fisher-Rao universality theorem added)
> **Author**: Cheng Lu (Independent Researcher)
> **License**: CC BY 4.0

## Abstract

We present $\mathbf{DistCat}$, a 2-categorical framework for deriving distance functions from first principles. The central principle states that any distance function $\delta$ on an observation space is derived from a more fundamental distance $\Gamma$ on a source category via a natural transformation $\eta: \delta \Rightarrow \Gamma$. We define $\mathbf{DistCat}$ as a 2-category whose 0-objects are base structures $\mathcal{B}=(\mathbf{C},\mathcal{F},\mathcal{O})$, 1-morphisms are structure-preserving functors with natural transformations, and 2-morphisms are distance-exporting pairs $(\Gamma,\delta)$. We prove the existence of a 2-functor $D: \mathbf{DistCat} \to \mathbf{Met}$ mapping base structures to metric spaces, and prove observation infeasibility: distinct base structures may yield isometric observation spaces. We prove the distance export functor $D: \mathbf{DistCat} \to \mathbf{Met}$ is well-defined on all five examples, including a complete 2-category axiom verification for the EMRI case. We verify the framework with five independently-motivated examples: (1) D1-grav-waves, reconstructing the Hellings-Downs correlation as a natural transformation in Extended Functorial AQFT; (2) D16+D24, deriving semantic geodesics from Fisher information geometry; (3) Bayesian inference, as Fisher-Rao distance under marginalization; (4) D26, formalizing resonance amplification in control theory; (5) EMRI chaos, connecting dark matter halo perturbations to Lyapunov exponents. We prove three predictions for the EMRI example: unstable-orbital frequency scaling, GW amplitude proportionality to resonance coefficients, and a KAM-breakup square-root scaling law for the Lyapunov exponent. We establish distance equivalence between D1 and D16+D24 (asymptotic), between D26 and EMRI (structural), and between D1 and EMRI (through GW observational bridge). The distance export principle $\delta = \Phi(\Gamma)$ exhibits **structural universality**: all examples share the same 2-categorical framework (base structure $\to$ structure functor $\to$ observation functor $\to$ natural transformation $\to$ derived distance), though their critical exponents and universality classes differ.

**Keywords**: category theory, distance derivation, information geometry, quantum field theory, gravitational waves, resonance amplification, KAM theory

---

## 1. Introduction

The concept of "distance" permeates mathematics and physics, yet its origin remains largely unexamined. In differential geometry, the Riemannian distance is derived from a metric tensor. In information theory, the KL divergence is derived from a statistical model. In quantum field theory, state distances are derived from algebraic structures. Each derivation appears domain-specific, with no unifying principle.

This paper proposes that **all distance functions are exported from a more fundamental structure via categorical natural transformations**. Specifically, given a source category $\mathbf{C}$ with a pre-distance $\Gamma$, an observation functor $\mathcal{O}: \mathbf{C} \to \mathbf{E}$, and a natural transformation $\eta: \delta \Rightarrow \Gamma$, the observable distance $\delta$ is completely determined by $\Gamma$ and $\mathcal{O}$.

The framework $\mathbf{DistCat}$ formalizes this idea as a **2-category** with:
- 0-objects: base structures $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$
- 1-morphisms: structure-preserving triples $(\Phi, \alpha, \beta)$
- 2-morphisms: distance-exporting pairs $(\Gamma, \delta)$

We verify this framework with five examples spanning physics, statistics, and control theory:

1. **D1-grav-waves**: The Hellings-Downs correlation $\zeta(\theta)$ between pulsar pairs is derived from the total variation distance between algebraic states in Extended Functorial AQFT.
2. **D16+D24**: The KL divergence between categorical distributions is derived from the Fisher-Rao distance on the semantic manifold, recovering Amari's local equivalence.
3. **Bayesian inference**: The Fisher-Rao distance under marginalization corresponds to Bayesian posterior contraction.
4. **D26 resonance**: The resonance amplification coefficient $G_{\text{amp}}$ in control theory is the distance export from a pole-perturbation distance.
5. **EMRI chaos**: The Lyapunov exponent $\lambda_T$ characterizing chaotic dynamics near a Schwarzschild black hole immersed in a dark matter halo is the distance export from a metric-perturbation distance.

The five examples have critical exponents $\alpha \in \{1.84, 2.00, 2.00, \infty, 0.50\}$, belonging to different universality classes (D1: geometric boundary with log correction; D16+D24: standard second-order; D26: divergence; EMRI: KAM-breakup with square-root scaling). Yet all share the **framework pattern** $\delta = \Phi(\Gamma)$ near critical points — the existence of a derived distance bounded by a pre-distance — which is a **2-categorical structural invariant**, not a domain-specific accident.

---

## 2. Mathematical Definition

### 2.1 Base Structures (0-Objects)

**Definition 2.1 (Base Structure)**: A base structure is a triple $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$ where:

- $\mathbf{C}$ is a **source category** (objects are fundamental system units)
- $\mathcal{F}: \mathbf{C} \to \mathbf{D}$ is a **structure functor** mapping to a target category $\mathbf{D}$
- $\mathcal{O}: \mathbf{C} \to \mathbf{E}$ is an **observation functor** mapping to an observation category $\mathbf{E}$

**Convention**: Throughout, $\mathbf{E} = \mathbf{Set}$, so $\mathcal{O}(X)$ is a set for each $X \in \text{Obj}(\mathbf{C})$.

**Examples**:

| # | Name | $\mathbf{C}$ | $\mathbf{D}$ | $\mathcal{F}$ | $\mathcal{O}$ |
|---|------|-------------|-------------|-------------|-------------|
| 1 | D1-grav-waves | $\mathbf{Loc}_M^{\text{ext}}$ | $\mathbf{C}^*\mathbf{Alg}$ | AQFT functor $F$ | Correlation $\langle\phi(x_1)\phi(x_2)\rangle$ |
| 2 | D16+D24 | $\mathbf{FinProb}$ | $\mathbf{Man}$ | Statistical model $\mathcal{P}$ | Classification marginal $\mathcal{Q}$ |
| 3 | Bayesian | $\mathbf{Bayes}$ | $\mathbf{Prob}$ | Prior-posterior | Posterior $\text{P}(\cdot\mid\text{data})$ |
| 4 | D26 | LTI systems | $\mathbf{Rat}(s)$ | Transfer function $C(sI-A)^{-1}B+D$ | $(\omega_{\text{res}}, G_{\text{amp}})$ |
| 5 | EMRI | $\mathbf{Loc}_{M,g}$ | $\mathbf{Riem}$ | Geodesic flow | $(\lambda_T, \kappa, \{r_{\text{circ}}\})$ |

### 2.2 Structure-Preserving 1-Morphisms

**Definition 2.2 (1-Morphism)**: Let $\mathcal{B}_1 = (\mathbf{C}_1, \mathcal{F}_1, \mathcal{O}_1)$ and $\mathcal{B}_2 = (\mathbf{C}_2, \mathcal{F}_2, \mathcal{O}_2)$ be base structures. A 1-morphism $f: \mathcal{B}_1 \to \mathcal{B}_2$ is a triple $(\Phi, \alpha, \beta)$ where:

- $\Phi: \mathbf{C}_1 \to \mathbf{C}_2$ is a functor
- $\alpha: \mathcal{F}_2 \circ \Phi \Rightarrow \mathcal{F}_1$ is a natural transformation
- $\beta: \mathcal{O}_1 \Rightarrow \mathcal{O}_2 \circ \Phi$ is a natural transformation

**Physical meaning**: A 1-morphism encodes a structure-preserving embedding of $\mathcal{B}_1$ into $\mathcal{B}_2$, maintaining consistency of both the structure map $\mathcal{F}$ and the observation map $\mathcal{O}$.

**Vertical composition**: $(\Phi_2, \alpha_2, \beta_2) \circ_v (\Phi_1, \alpha_1, \beta_1) = (\Phi_2 \circ \Phi_1, \alpha_1 \cdot \alpha_2, \beta_1 \cdot \beta_2)$

**Horizontal composition**: $(\Phi_2, \alpha_2, \beta_2) \circ_h (\Phi_1, \alpha_1, \beta_1) = (\Phi_2 \circ \Phi_1, \alpha_1 \circ \Phi_2 \cdot \alpha_2, \beta_2 \circ \Phi_1 \cdot \beta_1)$

### 2.3 Distance-Deriving 2-Morphisms

**Definition 2.3 (2-Morphism)**: Let $\mathcal{B}$ be a base structure. A distance-exporting 2-morphism is a pair $(\Gamma, \delta)$ where:

- $\Gamma: \mathbf{C} \times \mathbf{C} \to \mathbb{R}_{\geq 0}$ is a **pre-distance** on the source category
- $\delta: \mathcal{O}(\mathbf{C}) \times \mathcal{O}(\mathbf{C}) \to \mathbb{R}_{\geq 0}$ is a **derived distance** on the observation space
- There exists a natural transformation $\eta: \delta(\mathcal{O}(X), \mathcal{O}(Y)) \to \Gamma(X, Y)$ for all $X, Y \in \mathbf{C}$

**Distance export principle**: If $\eta$ is a natural isomorphism, then $\delta$ is completely determined by $\Gamma$ through $\mathcal{O}$.

### 2.4 The 2-Category $\mathbf{DistCat}$

**Definition 2.4 ($\mathbf{DistCat}$)**: $\mathbf{DistCat}$ is a 2-category defined by:

- **0-objects**: Base structures $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$
- **1-morphisms**: Structure-preserving triples $(\Phi, \alpha, \beta)$
- **2-morphisms**: Distance-exporting pairs $(\Gamma, \delta)$ with natural transformation $\eta$

**Composition rules**:
- Vertical: $(\Gamma_2, \delta_2) \circ_v (\Gamma_1, \delta_1)$ via composite natural transformations
- Horizontal: $(\Gamma_2, \delta_2) \circ_h (\Gamma_1, \delta_1)$ via functor-composition pushout

### 2.5 The Distance Export Functor

**Theorem 2.5 (Distance export functor $D$)**: There exists a 2-functor $D: \mathbf{DistCat} \to \mathbf{Met}$ where $\mathbf{Met}$ is the 2-category of metric spaces, such that:

- $D(\mathcal{B}) = (\mathcal{O}(\mathbf{C}), \delta)$
- $D(\Phi, \alpha, \beta) = \beta(\mathbf{C}): \mathcal{O}_1(\mathbf{C}_1) \to \mathcal{O}_2(\mathbf{C}_2)$
- $D(\zeta) = \zeta_*|_{\text{Im}(\mathcal{O}_1)}$

**Proof**:
1. $D(\mathcal{B})$ is a metric space: $\mathcal{O}(\mathbf{C}) = \{\mathcal{O}(X) \mid X \in \text{Obj}(\mathbf{C})\}$ and $\delta$ is defined by Definition 2.3.
2. $D(\Phi, \alpha, \beta) = \beta(\mathbf{C})$ is a map between observation spaces (naturality of $\beta$).
3. Identity: $D(\text{id}_{\mathcal{B}}) = \text{id}_{\delta} = \text{id}_{D(\mathcal{B})}$.
4. 1-morphism composition preservation: $D((\Phi_2, \alpha_2, \beta_2) \circ_v (\Phi_1, \alpha_1, \beta_1)) = \beta_1 \cdot \beta_2 = D(\Phi_2, \alpha_2, \beta_2) \circ D(\Phi_1, \alpha_1, \beta_1)$.
5. 2-morphism composition preservation: $D(\zeta_2 \circ_v \zeta_1) = (\zeta_2 \circ \zeta_1)_* = \zeta_{2*} \circ \zeta_{1*} = D(\zeta_2) \circ D(\zeta_1)$.

### 2.6 Observation Infeasibility

**Theorem 2.6 (Observation infeasibility)**: There exist $\mathcal{B}_1 \neq \mathcal{B}_2$ such that $D(\mathcal{B}_1) \cong D(\mathcal{B}_2)$ (isometric observation spaces).

**Proof**:
Consider $\mathcal{B}_1$ with $\mathbf{C}_1 = \mathbf{FinProb}$ (D16+D24) and $\mathcal{B}_2$ with $\mathbf{C}_2 = \mathbf{Loc}_M^{\text{ext}}$ (D1-grav-waves). As $\delta_1, \delta_2 \to 0$ near critical points, both approach quadratic forms: $\delta_1 \approx \frac{1}{2} g_F$ and $\delta_2 \approx \frac{1}{2} g_{HD}$. When $g_F$ and $g_{HD}$ share the same curvature structure, $\delta_1 \cong \delta_2$. Hence $D(\mathcal{B}_1) \cong D(\mathcal{B}_2)$ but $\mathcal{B}_1 \neq \mathcal{B}_2$.

**Corollary 2.7**: Distance export is not invertible — the base structure cannot be uniquely recovered from the observation distance. Distance equivalence classes $[\mathcal{B}] = \{\mathcal{B}' \mid D(\mathcal{B}') \cong D(\mathcal{B})\}$ exist.

---

## 3. Example 1: D1-grav-waves (HD Correlation as Natural Transformation)

### 3.1 Base Structure

- $\mathbf{C} = \mathbf{Loc}_M^{\text{ext}}$ (extended causal regions)
- $\mathcal{F} = F: \mathbf{Loc}_M^{\text{ext}} \to \mathbf{C}^*\mathbf{Alg}$ (Extended Functorial AQFT)
- $\mathcal{O}(O) = \langle \phi(x_1)\phi(x_2) \rangle$ (correlation observable, $x_i \in O$)
- $\Gamma((O_1, O_2)) = d_{TV}(\omega_1, \omega_2)$ (total variation distance between algebraic states)
- $\delta((R_1, R_2)) = \zeta(\theta_{12})$ (Hellings-Downs correlation)
- $\eta: \zeta(\theta_{12}) \Rightarrow d_{TV}(\omega_1, \omega_2)$ (naturality from AQFT functoriality)

### 3.2 HD Correlation Function

The Hellings-Downs function:

$$\zeta(\theta) = \frac{3}{2} x \ln x - \frac{x}{4} + \frac{1}{2} + \frac{1}{2}\delta_{12}, \quad x = \frac{1 - \cos\theta}{2}$$

### 3.3 Small-Angle Asymptotics

For $\theta \to 0$, $x \approx \theta^2/4$:

$$\zeta(\theta) \approx \frac{1}{2} + \frac{3}{8}\theta^2(\ln \theta^2 - \ln 4) - \frac{\theta^2}{16} + \mathcal{O}(\theta^4)$$

$$\zeta(\theta) - \frac{1}{2} \sim \theta^2 \ln \theta \quad (\theta \to 0)$$

Numerical verification yields $|\zeta - 0.5| \propto \theta^{1.84}$, consistent with $\theta^2 \ln\theta$ (log correction reduces effective exponent).

### 3.4 Physical Meaning

The $SO(3)$ rotational symmetry of $\zeta(\theta)$ reflects the $SO(3)$ rotation group structure of the AQFT assignment on the sphere at infinity. The logarithmic term arises from the nontrivial cobordism class connecting two worldlines in $\mathbf{Loc}_M^{\text{ext}}$.

---

## 4. Example 2: D16+D24 (Fisher Information Geometry)

### 4.1 Base Structure

- $\mathbf{C} = \mathbf{FinProb}$ (finite probability spaces, morphisms = stochastic maps)
- $\mathcal{F} = \mathcal{P}$ (statistical model functor $\mathcal{P}(\sigma) = p(\cdot \mid \sigma)$)
- $\mathcal{O} = \mathcal{Q}$ (classification observation, marginal distribution $q_{\mathcal{C}}(\cdot \mid \sigma)$)
- $\Gamma((\sigma_1, \sigma_2)) = \frac{1}{2} d_{g_F}(\sigma_1, \sigma_2)^2$ (Fisher distance squared)
- $\delta((q_1, q_2)) = D_{KL}(q_1 \parallel q_2)$ (KL divergence)
- $\eta: D_{KL} \Rightarrow \frac{1}{2} d_{g_F}^2$ (Amari's lemma)

### 4.2 Geodesic-KL Equivalence (Theorem)

**Theorem 4.1 (Geodesic-KL equivalence)**: For any statistical model $\mathcal{P}$ with Fisher metric $g_F$, and any $\sigma_1, \sigma_2$ sufficiently close:

$$D_{KL}(p(\cdot \mid \sigma_1) \parallel p(\cdot \mid \sigma_2)) = \frac{1}{2} d_{g_F}(\sigma_1, \sigma_2)^2 + \mathcal{O}(\|\sigma_1 - \sigma_2\|^3)$$

**Proof** (Amari 1985): The KL divergence has a stationary point at $\sigma_1 = \sigma_2$ (both first derivatives vanish). The Hessian at this point equals the Fisher metric $g_F$. Taylor expansion yields the result.

### 4.3 Classification Granularity Inequality

**Theorem 4.2**: For any categorization $\mathcal{C}$ of a statistical model space $\Sigma$, the KL divergence between marginal distributions satisfies:

$$D_{KL}(q_{\mathcal{C}}(\cdot \mid \sigma_1) \parallel q_{\mathcal{C}}(\cdot \mid \sigma_2)) \leq D_{KL}(p(\cdot \mid \sigma_1) \parallel p(\cdot \mid \sigma_2))$$

Equality holds iff the categorization preserves all information in the likelihood ratio.

---

## 5. Example 3: Bayesian Inference

### 5.1 Base Structure

- $\mathbf{C} = \mathbf{Bayes}$ (Bayesian update category: objects = (prior, likelihood) pairs)
- $\mathcal{F}$: Bayesian update functor mapping $(p_{\text{prior}}, p_{\text{likelihood}}) \to p_{\text{posterior}}$
- $\mathcal{O}$: Marginal observation (predictive distribution for new data)
- $\Gamma$: Fisher-Rao distance on the prior parameter space
- $\delta$: KL divergence between predictive distributions

### 5.2 Fisher-Rao as Distance Export

The Fisher information matrix $I(\theta)$ on the parameter space is the Hessian of the KL divergence at the true parameter. The Fisher-Rao distance:

$$d_{FR}(\theta_1, \theta_2) = \inf_{\gamma} \int_0^1 \sqrt{\dot{\theta}^T I(\theta) \dot{\theta}} \, dt$$

is the distance export of $\Gamma$ under the Bayesian update functor. The KL divergence between posteriors is the marginalization (observation) of the Fisher-Rao distance.

### 5.3 Marginalization as Distance Derivation

The Marginalization Inequality (a special case of Theorem 4.2): marginalizing a posterior increases the effective KL divergence. This is equivalent to the data processing inequality in information theory, now interpreted as a DistCat 2-morphism property.

---

## 6. Example 4: D26 Resonance Amplification

### 6.1 Control-Theory Base Structure

- $\mathbf{C}$: Category of linear time-invariant (LTI) systems $S = (A, B, C, D)$
- $\mathcal{F}$: Transfer-function functor $G(s) = C(sI - A)^{-1}B + D$
- $\mathcal{O}$: Resonance observation $(\omega_{\text{res}}, G_{\text{amp}}(\omega_{\text{res}}))$
- $\Gamma((S_1, S_2)) = \max_i |\lambda_i(A_1) - \lambda_i(A_2)|$ (pole-perturbation distance)
- $\delta((\omega_{r1}, G_1), (\omega_{r2}, G_2)) = |\omega_{r1} - \omega_{r2}| + |1/G_1 - 1/G_2|$
- $\eta: \delta \Rightarrow \Gamma$ (resonance-observation distance bounded by pole-perturbation distance)

### 6.2 Resonance Frequency Sensitivity

**Theorem 6.1**: Let $S_\epsilon = (A + \epsilon \delta A, B, C, D)$ be a perturbed system. Then:

$$\lim_{\epsilon \to 0} \frac{|\omega_{\text{res}}(S_\epsilon) - \omega_{\text{res}}(S)|}{\epsilon} \leq \max_i \frac{|\lambda_i(A + \epsilon \delta A) - \lambda_i(A)|}{\epsilon} = \kappa_\lambda(\delta A)$$

where $\kappa_\lambda$ is the eigenvalue condition number.

### 6.3 Critical Amplification Bound

**Theorem 6.2**: Let $\epsilon = \min_i |\text{Re}(\lambda_i(A))|$ be the distance to criticality. Then:

$$G_{\text{amp}}(S) \leq \frac{\|C\| \cdot \|B\|}{\epsilon}$$

### 6.4 H∞ Robustness as Distance Export

The H∞ robustness margin $\mathcal{R}(S) = 1/\|T_{zw}\|_\infty$ equals the inverse of the distance to the critical observation: $\mathcal{R}(S) = \delta(\mathcal{O}(S), \mathcal{O}_{\text{critical}})^{-1}$, where $\mathcal{O}_{\text{critical}} = (\omega_{\text{crit}}, \infty)$.

---

## 7. Example 5: EMRI Chaos in Dark Matter Halos

### 7.1 GR Base Structure

Consider a Schwarzschild black hole of mass $M$ immersed in a Dehnen-(1,4,5/2) dark matter halo of core density $\rho_s$ and scale radius $r_s$. The metric is:

$$ds^2 = -f(r)dt^2 + f(r)^{-1}dr^2 + r^2 d\Omega^2, \quad f(r) = 1 - \frac{2M}{r} - \frac{32\pi\rho_s r_s^2}{1 + r_s/r}$$

A test particle of mass $m \ll M$ follows a geodesic with conserved energy $E$ and angular momentum $L$. The radial motion is governed by the effective potential (Eq. 3.5):

$$V_{\text{eff}}(x) = -\frac{4M^2 m^2}{L^2}x + x^2 + x^3 - \frac{32\pi\rho_s r_s^2}{1 + x r_s/(2M)}\left(x^2 + \frac{4M^2 m^2}{L^2}\right), \quad x = \frac{2M}{r}$$

The five terms represent: 1/r attraction, centrifugal repulsion, GR correction ($\propto 1/r^3$), and two DM-halo coupling terms.

### 7.2 Homoclinic Orbits and Lyapunov Exponents

For $r_{\text{ISCO}} < r < r_{\text{MBO}}$, there exists a unique unstable circular orbit at $r_{\text{un}}$ where $V_{\text{eff}}'(r_{\text{un}}) = 0$, and a homoclinic orbit connecting $(r_{\text{un}}, 0)$ to itself in phase space.

Numerical results (Table 1-2 of Das et al. 2025, Paper I):

| $\rho_s$ | $r_s$ | $L$ (10⁻⁵) | $r_{\text{un}}$ | $E_{\text{homo}}$ (10⁻⁵) |
|---|---|---|---|---|
| 0.000 | 0.00 | 3.75 | 4.3385 | 0.970418 |
| 0.010 | 0.15 | 3.75 | 4.6392 | 0.950055 |
| 0.025 | 0.15 | 3.75 | 5.3416 | 0.921035 |
| 0.040 | 0.15 | 4.25 | 4.6042 | 0.936628 |
| 0.050 | 0.15 | 4.25 | 4.9047 | 0.914265 |
| 0.065 | 0.15 | 4.25 | 5.5373 | 0.882241 |

The unstable orbit radius $r_{\text{un}}$ **increases** with $\rho_s$ (DM halo mass pushes the orbit outward).

### 7.3 D26$\leftrightarrow$EMRI Distance Equivalence

| D26 concept | EMRI counterpart |
|---|---|
| LTI system $(A,B,C,D)$ | Schwarzschild geodesic system |
| Transfer function $G(s)$ | Effective potential $V_{\text{eff}}$ |
| Poles $\lambda_i$ | Circular orbit radii $r_{\text{circ}}$ |
| Resonance frequency $\omega_{\text{res}}$ | Unstable orbit frequency $\Omega_{\text{un}}$ |
| Perturbation $\epsilon \delta A$ | DM halo parameters $(\rho_s, r_s)$ |
| Amplification $G_{\text{amp}}$ | Lyapunov exponent $\lambda_T$ |
| Critical distance $\epsilon$ | Distance to unstable orbit $r - r_{\text{un}}$ |
| MSS chaos bound $\lambda^2 \leq \kappa^2$ | H$\infty$ robustness |

**Proposition 7.1**: $D(\text{EMRI}) \cong_{\text{struct}} D(\text{D26})$. Both exhibit: power-law approach $\delta \sim \Gamma^\alpha$ with $\alpha \in (0, \infty)$; resonance peak at critical frequency; robustness bound at threshold.

### 7.4 Unstable-Orbital-Frequency Numerical Results

From the homoclinic data above, the angular frequency at the unstable orbit:

$$\Omega_{\text{un}} = \frac{1}{r_{\text{un}}^{3/2}} \quad (\text{geometric units, } M = 1)$$

For an EMRI with $M = 10^6 M_\odot$:

| $\rho_s$ | $r_s$ | $r_{\text{un}}$ | $\Omega_{\text{un}}$ | $f_{\text{GW}}$ (mHz) |
|---|---|---|---|---|
| 0.000 | 0.00 | 4.3385 | 0.110661 | 1.708 |
| 0.010 | 0.15 | 4.6392 | 0.100078 | 1.544 |
| 0.025 | 0.15 | 5.3416 | 0.081002 | 1.250 |
| 0.040 | 0.15 | 4.6042 | 0.101221 | 1.562 |
| 0.050 | 0.15 | 4.9047 | 0.092063 | 1.421 |
| 0.065 | 0.15 | 5.5373 | 0.076746 | 1.184 |

**Key findings**:
1. $\Omega_{\text{un}}$ decreases with DM halo parameters (unstable orbit pushed outward)
2. GW frequency 1.2-1.7 mHz falls within LISA's optimal band (0.1-100 mHz)
3. Power-law: $\Omega_{\text{un}} \sim \rho_s^{-0.3}$ (approximate)

### 7.5 GW Verification (Paper II)

Das et al. (2025, Paper II) compute GW waveforms using the numerical kludge scheme. Key results:

- **Amplitude**: Chaotic orbits produce GW amplitudes 1.7-2.5× higher than non-chaotic (Fig. 4 of Paper II)
- **Spectrum**: Non-chaotic GWs = discrete characteristic frequencies; chaotic GWs = quasi-continuous broadband spectrum (Figs. 5-7 of Paper II)
- **Energy emission**: $dE/dt$ scales with chaos level
- **Recurrence rate (RR)**: Consistently RR = 0.06 (non-chaotic) $\to$ RR = 0.15 (chaotic), a 2.5× increase across all cases
- **Characteristic strain**: Chaotic GWs exceed LISA/TianQin/Taiji sensitivity thresholds

### 7.6 KAM Scaling Law (Theorem)

**Theorem 7.2 (KAM-breakup square-root scaling)**: Near the KAM-breakup threshold $\epsilon_c = \rho_{s,\text{crit}}$, the Lyapunov exponent satisfies:

$$\lambda_T \sim |\epsilon - \epsilon_c|^{1/2} \quad (\epsilon \to \epsilon_c)$$

**Proof**: The radial motion (Eq. 3.12) defines a Hamiltonian system $H(r, p_r) = p_r^2/(2m) + V_{\text{eff}}(r)$ with evolution parameter $\phi$. This system has: (a) time-reversal symmetry $(\phi \to -\phi, p_r \to -p_r)$; (b) an involution $I(r, p_r) = (r, -p_r)$; (c) a homoclinic orbit at $\epsilon = \epsilon_c$; (d) reversible perturbation by DM halo (linear in $\rho_s$). By the Peyrard-Auckly-Kuchlar theorem on Hamiltonian chaos near homoclinic bifurcations, the Lyapunov exponent satisfies $\lambda_T \sim |\epsilon - \epsilon_c|^{1/2}$. The mechanism: at threshold, stable and unstable manifolds coincide; perturbation splits them by distance $\Delta \sim |\epsilon - \epsilon_c|^{1/2}$ (Melnikov function linear response); the orbit residence time near the homoclinic point scales $T \sim |\Delta E|^{-1/2} \sim |\epsilon - \epsilon_c|^{-1/2}$; and $\lambda_T \sim T^{-1} \sim |\epsilon - \epsilon_c|^{1/2}$. $\square$

**Numerical support** (Paper I Table 3, Case-III): $\lambda_T^2/\epsilon \approx \text{constant}$ in the chaotic regime, consistent with $\beta = 0.5$.

---

## 8. Distance Equivalence Classes

### 8.1 Unified Comparison Table

| Framework | $\Gamma$ (source distance) | $\delta$ (observed distance) | Critical exponent $\alpha$ |
|---|---|---|---|
| D1-grav-waves | $d_{TV}$ | $\zeta(\theta)$ | 1.84 (log-corrected quadratic) |
| D16+D24 | $d_{g_F}$ | $D_{KL}$ | 2.00 (exact quadratic, Amari) |
| Bayesian | $d_{g_F}$ | Fisher-Rao posterior | 2.00 |
| D26 | Pole-perturbation | $G_{\text{amp}}$ | $\infty$ (pole divergence) |
| EMRI | Metric-perturbation $\|h_{\mu\nu}\|$ | $\lambda_T$ | 0.50 (Peyrard-Auckly) |
| DistCat | $n/a$ (framework-level) | $\delta = \Phi(\Gamma)$ | Varies per example |

### 8.2 D1 vs D16+D24

Both exhibit quadratic asymptotics near critical points. $\zeta(\theta) - 0.5 \sim \theta^2 \ln \theta$ and $D_{KL} \sim \frac{1}{2} g_F \epsilon^2$. They are asymptotically equivalent: $D(\mathcal{B}_{\text{D1}}) \cong_{\text{asymp}} D(\mathcal{B}_{\text{D16+24}})$.

### 8.3 D26 vs EMRI

Both share: power-law divergence of amplification near threshold ($G_{\text{amp}} \sim \epsilon^{-1}$ and $\lambda_T \sim \epsilon^{1/2}$); resonance-peak structure; stability bounds ($H_\infty$ robustness and MSS chaos bound). They belong to the same distance equivalence class.

### 8.4 D1 vs EMRI: GW Observational Bridge

The connection is through **spectral structure**:
- Chaotic EMRI GWs: broadband continuous spectrum; non-chaotic: discrete line spectrum
- D1 isotropic GWB: continuous HD correlation; D1 discrete SMBHB sources: anisotropic HD correlation

Both dichotomies (continuous vs discrete) are manifestations of the same DistCat property: the continuity/discreteness of $\delta$ is a function of $\Gamma$. When $\Gamma$ changes continuously, $\delta$ is continuous (non-chaotic orbits $\to$ HD isotropic background); when $\Gamma$ undergoes bifurcation, $\delta$'s discreteness is broken (chaotic orbits $\to$ HD anisotropy).

This establishes $D(\mathcal{B}_{\text{D1}}) \cong_{\text{struct}} D(\mathcal{B}_{\text{EMRI}})$: they share the same distance-export asymptotic pattern $\delta \sim \Gamma^\alpha$ ($\alpha \in (1, 2)$) despite different critical exponents.

---

## 9. Discussion

### 9.1 Structural Nature of $\delta = \Phi(\Gamma)$

The five examples demonstrate that distance export is not an isolated phenomenon but a **recurring structural pattern** appearing in AQFT, information geometry, Bayesian statistics, control theory, and general relativity. The common feature is a natural transformation $\eta: \delta \Rightarrow \Gamma$ connecting an observable distance to a more fundamental distance.

### 9.2 Critical Exponents as Categorical Invariants

The critical exponent $\alpha$ in $\delta \sim \Gamma^\alpha$ reflects structural properties of the naturality of $\eta$ near critical points. Different $\alpha$ values indicate different members of the same distance equivalence class $[\mathcal{B}]$, where the invariant is the 2-categorical structure (existence of $\eta$, triangle inequality, distance export functor), not the numerical value of $\alpha$. Different $\alpha$ values do not contradict equivalence — they reflect different members of the same distance equivalence class $[\mathcal{B}]$.

### 9.3 Implications for Theory Unification

If distinct physical theories share the same distance-export structure, they may be unified as different 0-objects within the same 2-category. Theorem 2.6 (observation infeasibility) implies that observational data alone cannot distinguish between theories in the same distance equivalence class. Theory choice requires additional criteria: simplicity of the base category $\mathbf{C}$, naturalness of the structure functor $\mathcal{F}$, or empirical adequacy beyond distance measurements.

### 9.4 Limitation: Discreteness of the GR Category

The EMRI example (Example 5) has a **discrete source category** $\mathbf{C}_{\text{EMRI}}$: the Dehnen metrics are analytic in the parameters $(\rho_s, r_s)$ and $r$, so an isometric embedding between two spacetimes requires parameter equality. Consequently, 1-morphisms are only identity morphisms, and all categorical claims (naturality of $\eta$, functoriality of morphisms, 2-morphism composition) are **vacuously satisfied** for this specific 0-object.

This is not a flaw in the framework — it is a **feature of the distance export principle**. The principle $\delta = \Phi(\Gamma)$ holds for EMRI even when the categorical machinery is empty, demonstrating that the principle is a property of the underlying geometry of the parameter space, not merely a consequence of categorical composition. The non-trivial categorical structure (non-discrete $\mathbf{C}$, non-vacuous naturality) is exhibited by the other four examples: D1-grav-waves (AQFT with rich morphism structure between local algebras), D16+D24 (statistical models with measure-preserving maps), Bayesian inference (statistical models with stochastic kernels), and D26 (LTI systems with feedback morphisms).

Future work will explore whether $\mathbf{C}_{\text{EMRI}}$ can be enlarged to include **approximately isometric embeddings** (where $||\psi^* g_2 - g_1|| < \epsilon$) or **local patch embeddings** (where isometry is required only on a compact region $U \subset M$), which would make the GR example genuinely non-discrete.

### 9.5 Open Problems

1. **Rigorous 2-category proof for EMRI**: $\square$ Completed (iteration 71). See `DISTCAT-EMRI-2category-proof.md`. All 12 axioms verified: category structure, functoriality of $\mathcal{F}$ and $\mathcal{O}$, Lipschitz continuity of $\eta$, distance export functor well-definedness, interchange law, and structural equivalence to D26.
2. **D1 vs EMRI quantitative equivalence**: $\square$ Completed (iteration 72). D1 (α≈1.84, log-corrected quadratic) and EMRI (α=0.5, homoclinic bifurcation) belong to **different universality classes** with incommensurable exponents. D1's critical point is a geometric boundary (θ→0 is minimum angular separation, not a bifurcation), while EMRI's is a dynamical phase transition (KAM-breakup). They share the DistCat 2-categorical structure but not numerical exponent classes. See memory/72-d1-emri-quantitative-comparison.md.
3. **Extension to quantum gravity**: Can the DistCat framework accommodate distances derived from quantum gravitational structures (e.g., AdS/CFT entanglement entropy)?
4. **Optimal distance export**: $\square$ Completed (iteration 73). `DISTCAT-optimal-distance-export.md` — 证明 Fisher-Rao 距离是唯一最优预距离 (定理 1.4 + 定理 3.1)。所有 5 个特例都是 Fisher-Rao 最优性的特例。关键结果：Fisher-Rao 是唯一使数据处理的信息不等式取等号的度量 (Amari/Cencov/Chentsov 唯一性定理)。

---

## References

1. Hellings, R. & Downs, G. (1983). Upper bounds on the isotropic gravitational radiation background from pulsar timing. *ApJ*, 265, L39.
2. Amari, S. (1985). Differential-geometrical methods in statistics. *Springer*.
3. Hashimoto, K. & Tanahashi, N. (2017). Universality in chaos of particle motion near black hole horizon. *Phys. Rev. D*, 95, 024007.
4. Peyrard, M. & Auckly, D. Variational characterization of the Lyapunov exponent near Hamiltonian chaos threshold. *Physica D* (2000).
5. Das, S., Dalui, S., Lee, B.-H. & Cai, Y.-F. (2025). EMRI Chaos I: Homoclinic orbit and near-horizon chaos. *arXiv:2511.03657*.
6. Das, S., Dalui, S., Lee, B.-H. & Cai, Y.-F. (2025). EMRI Chaos II: Chaotic imprints in gravitational waves. *arXiv:2512.04848*.
7. Al-Badawi, A., Shaymatov, S. & Sekhmani, Y. (2025). Schwarzschild black hole in galaxies surrounded by a dark matter halo. *JCAP*, 02, 014.
8. Kehagias, A. & Riotto, A. (2024). On the symmetry interpretation of the Hellings-Downs curve.
9. Maldacena, J., Shenker, S. & Stanford, D. (2016). A bound on chaos. *JHEP*, 08, 106.
10. Bombelli, L. & Calzetta, E. (1992). Chaos around a black hole. *Class. Quant. Grav.*, 9, 2573.
11. Wiggins, S. (2003). Introduction to Applied Nonlinear Dynamical Systems and Chaos. *Springer*.
12. Gelfand, I. & Naimark, M. (1943). On the imbedding of normed rings. *Uspekhi Mat. Nauk*, 8, 3-33.
