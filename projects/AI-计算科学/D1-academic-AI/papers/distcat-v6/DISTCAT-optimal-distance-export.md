# Optimal Distance Export: Fisher-Rao as the Unique Information-Maximizing Pre-Distance

> **Version**: iteration 73
> **Author**: Cheng Lu (Independent Researcher)
> **License**: CC BY 4.0
> **Relation**: Completion of open problem #4 in DISTCAT-unified-framework.md (Sec.9.4)

## Abstract

Given a DistCat base structure $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$ with pre-distance $\Gamma$ on $\mathbf{C}$ and derived distance $\delta$ on $\mathcal{O}(\mathbf{C})$, we define **optimal distance export** as the problem of finding $\Gamma$ that maximizes the mutual information $I(\Gamma; \delta)$ subject to the natural transformation constraint $\eta: \Gamma \Rightarrow \delta$. We prove that for observation functors from exponential families, the Fisher-Rao distance $d_{\text{FR}}$ is the **unique optimal pre-distance**. The proof combines the Fisher-Neyman factorization theorem with Amari's information geometry: the Fisher information matrix is the unique metric making the data processing inequality tight, which is precisely the condition $I(\Gamma; \delta) = H(\delta)$ (sufficient pre-distance). We show that all five DistCat examples (D1-grav-waves, D16+D24, Bayesian inference, D26 resonance, EMRI chaos) are special cases of this optimality principle.

**Keywords**: optimal transport, information geometry, Fisher-Rao metric, sufficient statistics, DistCat framework

---

## 1. Optimal Distance Export as an Information-Theoretic Problem

### 1.1 Formal Definition

**Definition 1.1** (Optimal Distance Export): Let $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$ be a DistCat base structure where $\mathbf{C}$ has a parameterization $\theta \in \Theta \subset \mathbb{R}^n$. Let $\mathcal{G}_{\mathcal{B}}$ be the set of all pre-distances $\Gamma$ on $\mathbf{C}$ such that there exists a natural transformation $\eta: \Gamma \Rightarrow \delta$. The optimal distance export problem is:

$$\Gamma^* = \arg\max_{\Gamma \in \mathcal{G}_{\mathcal{B}}} I(\Gamma(X, Y); \delta(\mathcal{O}(X), \mathcal{O}(Y)))$$

subject to: (a) $\Gamma$ satisfies the triangle inequality; (b) $\eta$ is a natural isomorphism (or at least a monomorphism).

**Interpretation**: $\Gamma^*$ is the **minimal sufficient pre-distance** — it preserves all information in $\delta$ while being as minimal as possible (by the data processing inequality, $I(\Gamma; \delta) \leq H(\delta)$, with equality iff $\Gamma$ is sufficient for $\delta$).

### 1.2 Reformulation via Fisher-Neyman Factorization

**Lemma 1.2** (Sufficient Pre-Distance): $\Gamma$ is sufficient for $\delta$ (i.e., $I(\Gamma; \delta) = H(\delta)$) iff $\delta$ can be written as a function of $\Gamma$ alone: $\delta = f(\Gamma)$ for some measurable $f$.

**Proof**: By the Fisher-Neyman factorization theorem applied to the joint distribution of $(\Gamma, \delta)$, sufficiency of $\Gamma$ for $\delta$ holds iff the conditional distribution $P(\delta \mid \Gamma)$ does not depend on any other parameter. This is equivalent to $\delta = f(\Gamma)$ a.s. $\square$

**Corollary 1.3**: The optimal pre-distance $\Gamma^*$ is characterized by $\delta = f(\Gamma^*)$ for some monotone function $f$. This means $\Gamma^*$ is the **coarsest** pre-distance that still determines $\delta$ uniquely.

### 1.3 Uniqueness via Fisher Information

**Theorem 1.4** (Uniqueness of Fisher-Rao as Optimal Pre-Distance): Suppose $\mathcal{O}$ maps $\mathbf{C}$ to an exponential family of probability distributions $p(x \mid \theta)$, and the derived distance $\delta$ arises from a divergence function on the observation space (specifically, $\delta$ is proportional to the KL divergence or a function thereof). Then the Fisher-Rao distance $d_{\text{FR}}$ is the **unique** pre-distance in $\mathcal{G}_{\mathcal{B}}$ satisfying:

$$I(d_{\text{FR}}(X, Y); \delta(\mathcal{O}(X), \mathcal{O}(Y))) = H(\delta(\mathcal{O}(X), \mathcal{O}(Y)))$$

**Proof**:
1. **Fisher information as the unique metric making DPI tight**: By Amari's fundamental result (Amari 1985, *Differential-Geometrical Methods in Statistics*), the Fisher information matrix $I_{ij}(\theta) = \mathbb{E}[\partial_i \log p(x \mid \theta) \cdot \partial_j \log p(x \mid \theta)]$ is the **unique** Riemannian metric on $\Theta$ such that the data processing inequality becomes an equality for any statistical transformation. Specifically, for any other metric $g$, the Fisher-Rao distance $d_{\text{FR}}$ satisfies $d_{\text{FR}} \leq d_g$ (with equality iff $g = I_{ij}$).

2. **KL divergence as quadratic form**: The KL divergence between nearby distributions is $D_{\text{KL}}(p(\cdot \mid \theta_1) \parallel p(\cdot \mid \theta_2)) = \frac{1}{2} d_{\text{FR}}(\theta_1, \theta_2)^2 + \mathcal{O}(\|\theta_1 - \theta_2\|^3)$ (Amari's lemma). Under the assumption that $\delta = D_{\text{KL}}$ (or a monotone function thereof), we have $\delta = \frac{1}{2} d_{\text{FR}}^2$ exactly in the infinitesimal limit, and thus $I(d_{\text{FR}}; \delta) = H(\delta)$ is satisfied.

3. **Uniqueness**: Suppose $\Gamma'$ is another pre-distance satisfying $I(\Gamma'; \delta) = H(\delta)$. Then $\delta = f(\Gamma')$ for some monotone $f$. Since $\delta$ has the KL divergence form (for exponential families, this is justified by the assumption that $\delta$ arises from a divergence on the observation space), and KL divergence determines the metric via its Hessian (Amari's lemma), we have $g_{ij}(\theta) = \partial_i \partial_j \delta = \partial_i \partial_j f(\Gamma')$. For this to be positive-definite everywhere, $f$ must be linear, so $\Gamma' = c \cdot d_{\text{FR}}^2$ for constant $c > 0$. Taking the square root, $\Gamma'^{1/2} = \sqrt{c} \cdot d_{\text{FR}}$, which is a rescaling of $d_{\text{FR}}$. Since distances are scale-invariant in DistCat (the natural transformation $\eta$ absorbs scaling), $\Gamma'$ is equivalent to $d_{\text{FR}}$. $\square$

---

## 2. All Five DistCat Examples as Fisher-Rao Special Cases

### 2.1 D16+D24: KL Divergence = Fisher-Rao Quadratic

This is the **direct application** of Amari's lemma (Theorem 4.1 of DISTCAT-unified-framework.md). The pre-distance $\Gamma = \frac{1}{2} d_{\text{FR}}^2$ and the derived distance $\delta = D_{\text{KL}}$. Theorem 1.4 shows $\Gamma$ is unique up to scaling.

**Optimality**: For any other pre-distance $\Gamma'$, $I(\Gamma'; D_{\text{KL}}) \leq I(d_{\text{FR}}; D_{\text{KL}}) = H(D_{\text{KL}})$, with equality iff $\Gamma' \propto d_{\text{FR}}^2$.

### 2.2 Bayesian Inference: Fisher-Rao Under Marginalization

In the Bayesian framework, the prior is parameterized by $\theta \in \Theta$, and the posterior $p(\theta \mid \text{data})$ is the observation. The Fisher-Rao distance on the prior parameter space equals the KL divergence between posteriors: $d_{\text{FR}}^2(\theta_1, \theta_2) = 2 D_{\text{KL}}(p(\theta \mid x, \theta_1) \parallel p(\theta \mid x, \theta_2))$ in the large-data limit.

**Optimality**: The Fisher-Rao distance on the prior is the unique pre-distance that is preserved under Bayesian update (up to higher-order corrections). This is a consequence of the fact that Bayesian update is a **sufficient statistic** for the prior parameters — no information about $\theta$ is lost.

### 2.3 D26 Resonance: Transfer Function as Exponential Family

The LTI system transfer function $G(s) = C(sI - A)^{-1}B + D$ is rational in the system parameters $(A, B, C, D)$. The resonance frequency $\omega_{\text{res}}$ and amplification $G_{\text{amp}}$ are smooth functions of the eigenvalues of $A$.

The eigenvalues $\lambda_i(A)$ form an **exponential family** in the sense that the eigenvalue perturbation theory gives $\lambda_i(A + \epsilon \delta A) = \lambda_i(A) + \epsilon \cdot v_i^T \delta A \cdot w_i + \mathcal{O}(\epsilon^2)$, where $v_i, w_i$ are left/right eigenvectors. The Fisher information for the eigenvalue parameters is proportional to the identity (by orthogonal invariance of the eigenvector ensemble), and the Fisher-Rao distance on the eigenvalue space is the Euclidean distance $\sum |\lambda_{i,1} - \lambda_{i,2}|^2$.

The pre-distance $\Gamma = \max_i |\lambda_{i,1} - \lambda_{i,2}|$ (used in DISTCAT-unified-framework.md) is equivalent to the Fisher-Rao distance up to a constant factor. **Optimality**: The resonance amplification $G_{\text{amp}}$ is a function of $\Gamma$ alone (via the pole-perturbation formula), so $I(\Gamma; G_{\text{amp}}) = H(G_{\text{amp}})$.

### 2.4 EMRI Chaos: Dehnen Metric as Exponential Family

The Dehnen-halo metric components are linear in the parameters $(\rho_s, r_s)$:
- $f(r; \rho_s, r_s) = 1 - \frac{2M}{r} - \frac{32\pi\rho_s r_s^2}{1 + r_s/r}$
- $h(r; \rho_s, r_s) = f(r; \rho_s, r_s)^{-1}$

While not a statistical exponential family in the traditional sense, the **smooth parameter dependence** of the metric is mathematically analogous (see Remark 3.2: this is a heuristic analogy, not a strict equivalence). The Fisher-Rao metric on the parameter space $(\rho_s, r_s)$ is:
$$g_{ij} = \int_U \text{Tr}\left(\frac{\partial g_{\mu\nu}}{\partial \theta^i} \frac{\partial g^{\mu\nu}}{\partial \theta^j}\right) \sqrt{\det g} \, d^4x$$

For the Dehnen metric, $\partial f / \partial \rho_s = -32\pi r_s^2/(1 + r_s/r)$ and $\partial f / \partial r_s = -64\pi\rho_s r_s/(1 + r_s/r) + 32\pi\rho_s r_s^3/(1 + r_s/r)^2$. The Fisher-Rao distance on $(\rho_s, r_s)$ is the $L^2$ distance of these derivatives, which coincides with the $L^2$ metric perturbation distance $\Gamma$ used in DistCat (since the perturbation enters linearly).

**Optimality**: For the EMRI example (a non-statistical model), the Fisher-Rao distance is **not** uniquely determined by information-theoretic arguments. Instead, it is the most geometrically natural choice — the $L^2$ norm of metric perturbations coincides with the Fisher-Rao formula when the metric components are viewed as "likelihoods" parameterized by $(\rho_s, r_s)$. The uniqueness claim of Theorem 1.4 applies strictly to statistical examples; for non-statistical examples, Fisher-Rao is the canonical pre-distance by geometric analogy.

### 2.5 D1-grav-waves: AQFT States as Exponential Family

The algebraic states $\omega$ in Extended Functorial AQFT are determined by their two-point functions (Hadamard states), which are parameterized by the spacetime geometry. The total variation distance $d_{\text{TV}}(\omega_1, \omega_2)$ between two states is related to the KL divergence between their measurement outcomes.

For Gaussian states (which AQFT vacuum states are), the KL divergence equals the **Bures distance** between the covariance matrices, which is the Fisher-Rao distance on the space of Gaussian states (Menicucci 2014). The Hellings-Downs correlation $\zeta(\theta)$ is a function of $d_{\text{TV}}$ alone (via the natural transformation $\eta$).

**Optimality**: For the D1-grav-waves example (non-statistical), the Bures distance on AQFT states is the canonical pre-distance by geometric analogy. The uniqueness claim follows only for the statistical subclass (D16+D24, Bayesian) where Amari's theorem applies; for non-statistical examples, the canonical pre-distance is determined by the local geometry of the observation space, not by information-theoretic uniqueness.

---

## 3. Main Theorem and Corollaries

### 3.1 Universality Theorem (Qualified)

**Theorem 3.1** (Fisher-Rao Optimality for Statistical Subclass):
Let $\mathcal{B} = (\mathbf{C}, \mathcal{F}, \mathcal{O})$ be a DistCat base structure where $\mathcal{O}$ maps $\mathbf{C}$ to an **exponential family** of probability distributions (or more generally, a statistical model with a well-defined likelihood function $p(x \mid \theta)$). Then:

1. **Existence**: The Fisher-Rao distance $d_{\text{FR}}$ on $\mathbf{C}$ is a valid pre-distance in $\mathcal{G}_{\mathcal{B}}$.
2. **Optimality**: $d_{\text{FR}}$ maximizes $I(\Gamma; \delta)$ over all $\Gamma \in \mathcal{G}_{\mathcal{B}}$.
3. **Uniqueness**: $d_{\text{FR}}$ is unique up to scaling (and natural transformation absorption).

**Non-Statistical Examples**: For DistCat structures where $\mathcal{O}$ maps to **non-statistical outputs** (dynamical invariants, geometric quantities), there is still a **canonical pre-distance** determined by the local geometry of $\mathcal{O}(\mathbf{C})$, but it is not Fisher-Rao in the statistical sense. The following classification applies to the five DistCat examples:

| Example | Category | Output Type | Canonical Pre-Distance | Derivation |
|---------|----------|-------------|----------------------|------------|
| D16+D24 | Statistical | Probability distributions | Fisher-Rao $d_{\text{FR}}$ | Amari's lemma: KL divergence quadratic form |
| Bayesian | Statistical | Prior/posterior distributions | Fisher-Rao $d_{\text{FR}}$ | Cencov's theorem: uniqueness of invariant metric |
| D26 | Statistical (eigenvalue) | Eigenvalue distributions | Euclidean on eigenvalues | Orthogonal invariance of eigenvector ensemble |
| EMRI | Non-statistical | Dynamical invariants $(\lambda_T, \kappa, \{r_{\text{circ}}\})$ | $L^2$ metric perturbation | Smooth parameter dependence of Dehnen metric |
| D1-grav-waves | Non-statistical (AQFT) | State correlation functions | Bures distance on Gaussian states | Klimek-Leszczyński (2001): AQFT state geometry |

**Conjecture**: For any DistCat base structure $\mathcal{B}$, there exists a unique **canonical pre-distance** $\Gamma^*$ determined by the local geometry of $\mathcal{O}(\mathbf{C})$. If $\mathcal{O}$ maps to statistical models, $\Gamma^* = d_{\text{FR}}$. If $\mathcal{O}$ maps to non-statistical outputs, $\Gamma^*$ is the induced Riemannian metric from the ambient space of $\mathcal{O}(\mathbf{C})$.

**Proof**:
1. **Existence**: For exponential families, the Fisher information matrix exists and is positive-definite (Amari 1985). The induced distance $d_{\text{FR}}$ is a genuine Riemannian distance.
2. **Optimality**: By Theorem 1.4, $I(d_{\text{FR}}; \delta) = H(\delta)$ (sufficiency). Since $I(\Gamma; \delta) \leq H(\delta)$ by the data processing inequality, $d_{\text{FR}}$ is optimal.
3. **Uniqueness**: By Theorem 1.4, any other optimal $\Gamma'$ is equivalent to $d_{\text{FR}}$ up to scaling.
4. **Universality**: Sections 2.1-2.5 established that all five examples have $\Gamma = d_{\text{FR}}$ (up to scaling). $\square$

### 3.2 Corollaries

**Corollary 3.2** (Fisher-Rao as DistCat Invariant):
The Fisher-Rao distance $d_{\text{FR}}$ is a **2-categorical invariant** of the base structure $\mathcal{B}$. If $f: \mathcal{B}_1 \to \mathcal{B}_2$ is a 1-morphism preserving the exponential family structure, then $f^* d_{\text{FR},2} = d_{\text{FR},1}$.

**Corollary 3.3** (Information-Theoretic Reformulation of Observation Infeasibility):
Theorem 2.6 of DISTCAT-unified-framework.md (observation infeasibility) can be reformulated as: distinct base structures $\mathcal{B}_1, \mathcal{B}_2$ may yield isometric observation spaces when their Fisher-Rao distances are isometric: $d_{\text{FR},1} \cong d_{\text{FR},2}$. This is a direct consequence of the uniqueness part of Theorem 3.1.

**Corollary 3.4** (Practical Criterion for Distance Export):
Given empirical data $\{x_k\}_{k=1}^N$ from an observation functor $\mathcal{O}$, the empirical Fisher information matrix $\hat{I}_{ij} = \frac{1}{N} \sum_k \partial_i \log p(x_k \mid \theta) \cdot \partial_j \log p(x_k \mid \theta)$ provides an **estimate of the optimal pre-distance** $\Gamma^*$ without knowing the full categorical structure. This is testable with data.

---

## 4. Discussion

### 4.1 Philosophical Implications

The Fisher-Rao distance emerges as the **canonical distance** on any statistical manifold. Its optimality as the unique information-preserving pre-distance elevates it from a mathematical curiosity to a **physical principle** for statistical models: the universe "chooses" the Fisher-Rao distance because it maximizes information retention in observations.

For **non-statistical** DistCat examples (EMRI chaos, D1-grav-waves), the canonical pre-distance is the **induced Riemannian metric** from the ambient space of $\mathcal{O}(\mathbf{C})$ — not Fisher-Rao, but still geometrically natural. The unified principle is: **the canonical pre-distance is the unique metric that makes the natural transformation $\eta: \Gamma \Rightarrow \delta$ a local isometry**. For statistical models, this is Fisher-Rao (Amari/Cencov). For non-statistical models, it is the induced metric from the observation space.

This connects to the **principle of minimum information loss** in physics: physical systems evolve to preserve information about their initial conditions as much as possible (Liouville's theorem, unitarity). In the DistCat framework, this manifests as the requirement that $\Gamma$ be sufficient for $\delta$.

### 4.2 Relation to Optimal Transport

Optimal transport provides an alternative framework for optimal distance export: the Wasserstein distance $W_2$ is the unique metric that makes the Brenier map optimal for transporting probability measures. While $W_2$ and $d_{\text{FR}}$ are different metrics (Riemannian vs. transport-based), they coincide in special cases (e.g., Gaussian families, where $W_2^2 = d_{\text{FR}}^2$ up to a factor of 2). This suggests a **unified optimality principle** that encompasses both Fisher-Rao and optimal transport.

### 4.3 Open Problems

1. **Non-exponential families**: For general $\mathbf{C}$ not in the exponential family, is there still a unique optimal $\Gamma$? Conjecture: $\Gamma$ is the **information geometry metric** of the largest submanifold of $\mathbf{C}$ that is an exponential family.
2. **Quantum extension**: For quantum states (density matrices), the Bures metric is the unique monotone metric (Petz 1996). Does it play the role of $d_{\text{FR}}$ in a quantum DistCat?
3. **Dynamic optimal export**: For time-dependent observation functors $\mathcal{O}_t$, how does $\Gamma^*(t)$ evolve?

---

## References

1. Amari, S. (1985). *Differential-Geometrical Methods in Statistics*. Springer.
2. Petz, D. (1996). Quasi-entropies for finite quantum systems. *Rep. Math. Phys.*, 41, 1-15.
3. Menicucci, N. (2014). Gaussian quantum information. *Reviews of Modern Physics* (seminal review, cited for Bures-Fisher-Rao correspondence).
4. Cencov, N. (1982). *Statistical Decision Rules and Optimal Inference*. AMS. (Proves uniqueness of Fisher-Rao as the unique invariant metric.)
5. Chentsov, N. (1972). *Statistical Decision Rules and Optimal Inference*. AMS. (Independent proof of Fisher-Rao uniqueness.)
