# 04-quality-check — P2-1 OLC Principles (Iteration 1)

- status: **FAIL**
- input: note/P2-1-olc-principles.md (379 lines)
- checked_at: 2026-07-08
- checklist:

  ## Completeness: FAIL

  The 1-loop/03 decomposition (`loop/1-loop/03-任务分解-P2-1-Iteration1.md`) specifies 11 subtasks (ST01-ST11) mapped to 13 acceptance criteria (AC1-AC13) and 8 hard constraints. Cross-referencing the actual document against these requirements:

  ### COVERED
  - **AC1** (signal model derivation, 5+ intermediate steps): PASS — Section 2.1 provides a complete 5-step chain from metric perturbation to frequency shift (Steps 1-5), each with explicit formula references.
  - **AC2** (transfer function (2-30)): PASS — Section 2.2 states the formula correctly and interprets all three factors.
  - **AC3** (response function (2-42)): PASS — Section 1.1 states the full response function with all terms identified.
  - **AC4** (SGWB four assumptions): PASS — Section 3.1 covers stationarity, Gaussianity, isotropy, and unpolarized, culminating in formula (2-39).
  - **AC5** (ORF definition and physical meaning): PASS — Section 3.2 derives from cross-correlation to the ORF integral with properties listed.
  - **AC6** (OLC ORF (3-1) and 6 geometric parameters): PASS — Sections 3.3-3.4 cover the full ORF expression, phase factors, and all 6 parameters.
  - **AC9** (physical intuition for key formulas): PASS — Every major formula has embedded physical interpretation (Sections 1.1, 1.2, 2.2, 2.3, 3.1, 3.2, 3.3, 3.5, 4.1, 5.2).
  - **AC10** (self-questioning): PASS — 5 self-questioning items found: "Self-questioning 1" (Section 2.3), "Self-questioning 2" (Section 3.5), and Questions A, B, C (Section 6/self-reflection).
  - **AC12** (5+ original citations): PASS — "Lou Chapter 2/3/5" with specific equation numbers cited throughout.

  ### PARTIALLY COVERED
  - **AC7** (OLC vs traditional detectors systematic comparison): Section 1.2 mentions qualitative advantages (direct frequency measurement, compact formation, quantum noise floor) and Section 4.3 references Lou Chapter 5 comparisons. However, the decomposition (ST07) requires a **systematic comparison table** covering detection principle, frequency band, arm length, and sensitivity source. The document has a parameter comparison table (Section 1.1) but it compares OLC vs LISA/Taiji/TianQin orbital parameters, NOT detection principles/bands/sensitivity sources as required by ST07.
  - **AC8** (OLC network typical geometric parameters): Partially covered in the parameter table at Section 1.1 and Section 3.4 (6 parameters). However, ST08 requires a **dedicated standalone section** (Section 8) covering: arm length parameters, baseline length parameters, typical configurations (coplanar, non-coplanar, PTA-like, isosceles trapezoid), detector count vs baseline count, and bidirectional link characteristics. The current document merges these into Sections 3-4 without a dedicated "OLC网络典型几何参数" section.
  - **AC13** (3+ intermediate derivation steps): PASS — signal model has 5 steps, ORF has 4+ steps.

  ### NOT COVERED
  - **AC11** (comparison with project existing work): Section 6.6 mentions `scripts/01-olc-orf-solver.py` only in passing ("The ORF solver script provides numerical confirmation..."), but this is NOT the required analysis. ST09 specifically demands:
    1. Verification that the code's OLC transfer function implementation matches formula (2-30)
    2. Verification that the ORF calculation framework matches formula (3-1)
    3. Cross-referencing with memory files (`memory/01-olc-orf-formulas.md`, `memory/02-lou-olc-transfer-function.md`, `memory/10-olc-triangular-chiral-orf-iteration6.md`, etc.)
    4. Explicit annotation of errors or outdated information
    The document has none of this analysis.
  - **ST03 gap** (OLC transfer function vs Hu PRD $T_{\text{one}}$): Section 5 "Consistency with Hu PRD Framework" mentions Hu PRD conceptually and displays $D_{ab}^{\text{OLC}}$ but does NOT:
    1. Display Hu PRD's $T_{\text{one}}(\beta, \hat{n}\cdot\hat{u})$ formula
    2. Show side-by-side comparison of the two formulas
    3. Derive the short-wave limit behavior for both
    4. Explain why OLC uses sinc while Hu PRD uses $[1-e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$

  ### Naming Discrepancy
  The decomposition specifies output as `note/P2-1-olc-principle.md` (singular "principle") but the actual file is `note/P2-1-olc-principles.md` (plural "principles"). This is a minor deviation.

  ## Formula Accuracy: PASS

  Key formulas verified against source materials:
  - **Transfer function (2-30)**: $\mathcal{T} = \frac{i2\pi f L}{c} \cdot \text{sinc}[\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})] \cdot \exp[-i\frac{\pi f L}{c}(1-\hat{u}\cdot\hat{n})]$ — correct per Lou thesis (raw/楼明智论文OLC.txt p720-728). Confirmed by solver code header (scripts/01-olc-orf-solver.py line 10-12) and memory file (memory/02-lou-olc-transfer-function.md line 14).
  - **Response function (2-42)**: Correctly written with polarization contraction, transfer function, and spatial phase factor. Matches source at raw/楼明智论文OLC.txt p819-826.
  - **ORF (3-1)**: Structure is correct. Phase factor $\alpha_{12} = \frac{2\pi f}{c}(\frac{L_1}{2}\hat{u}_1 - \frac{L_2}{2}\hat{u}_2 - \vec{x}_1 + \vec{x}_2)\cdot\hat{n}$ uses arm-center convention (valid per Lou). $\beta_{12} = \frac{\pi f}{c}(L_2-L_1)$ is correct.
  - **Hellings-Downs curve**: Standard formula correctly stated.
  - **Noise model**: QPN, PSN, AN formulas are consistent with Lou Chapter 5 (Eq. 5-11 through 5-16).
  - **$\Omega_{\text{GW}} = \frac{4\pi^2 f^3}{3H_0^2} S_h(f)$**: Correct standard definition.
  - **Minor concern**: $\Omega_n h^2 = \frac{4\pi^2 f^3}{3(H_0/h)^2 S_n(f)}$ — uses $S_n(f)$ (detector noise PSD) in denominator but does NOT clarify whether this is strain noise PSD or frequency-shift noise PSD. For OLC, the primary noise is in frequency shift (unitless), not strain ($1/\sqrt{\text{Hz}}$). This ambiguity would confuse readers attempting to perform the noise-to-ORF SNR calculation.
  - **Hu PRD formula representation**: In Section 5, the response tensor $D_{ab}^{\text{OLC}} = \frac{1}{2} u_a u_b \mathcal{T}_{\text{one}} e^{-i2\pi f \hat{n}\cdot\vec{x}/c}$ is stated. However, the Hu PRD $T_{\text{one}}$ formula is NOT displayed, making the consistency claim un-verifiable. Per memory/01-olc-orf-formulas.md, Hu PRD's actual $T_{\text{one}} = \frac{1+\hat{n}\cdot\hat{u}}{2}[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$, which is structurally different from OLC's sinc-based form.

  ## Derivation Chain: PASS

  Section 2.1 provides a 5-step chain from GW metric perturbation to frequency shift:
  1. GW metric perturbation $g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$ in TT gauge
  2. Null geodesic for light propagation → time-of-flight correction
  3. Frequency shift definition (core signal equation, Eq. 2-22)
  4. Time-of-flight integral correction (Eq. 2-23 through 2-26)
  5. Frequency-domain formulation → transfer function

  Each step states the physical starting point, the intermediate formula, and the relationship to the next step. The causal chain is preserved: metric perturbation → light travel time → phase shift → frequency shift → transfer function. Intermediate algebra (Fourier transform details, integral evaluation) is abbreviated, which is appropriate for a principles-level document.

  The ORF derivation (Section 3.2) also has a clear chain: cross-correlation definition → frequency domain → expectation signal → ORF emergence.

  ## Self-Questioning: PASS

  5 items identified, all high quality (asking "why" and "what if", not "what is"):
  - **Self-questioning 1** (Section 2.3): About directional dependence asymmetry ($\theta=0$ vs $\theta=\pi$) and whether the response asymmetry has a simple physical explanation. Strong question probing beyond the math.
  - **Self-questioning 2** (Section 3.5): About whether the non-trivial transformation's phase change affects optimal filter choice and whether ORF-modulus families can be searched for enhanced sensitivity. Genuine open research question.
  - **Question A** (Section 6): About fundamental difference between PTA "arm length" (parsecs to pulsars) and OLC arm length (millions of km between satellites), and its effect on sensitivity scaling. Deep conceptual question.
  - **Question B** (Section 6): About analytic upper bound on $|\Gamma_{12}|$ as function of separation distance. Good question for understanding ORF geometric limits.
  - **Question C** (Section 6): About when ORF phase has observable consequences beyond SGWB detection. Relevant to multi-detector network design.

  ## Physics Interpretation: PASS

  Every major section includes explicit physical interpretation:
  - Section 1.1: Physical picture (laser emission, propagation, atomic clock reception)
  - Section 1.2: OLC advantages over interferometers (direct frequency measurement, compact formation, quantum noise floor)
  - Section 2.2: Three-factor interpretation of transfer function (dipole response, finite-arm sinc, geometric phase)
  - Section 2.3: Origin story of sinc function — path integral over GW phase during light travel
  - Section 3.1: Physical meaning of SGWB assumptions (why they reduce to one function $S_h(f)$)
  - Section 3.2: ORF as "sky-averaged overlap" with clear properties
  - Section 3.3: Factor-by-factor decomposition of ORF
  - Section 3.5: Geometric meaning of non-trivial transformation
  - Section 4.1: Physical explanation of Hellings-Downs deviation (finite-arm sinc, phase factor, loss of common-mode correlation)
  - Section 5.2: ORF as inner product in function space
  - Section 6: Uncertainties and open questions with physical framing

  Interpretations consistently go beyond math to explain what formulas represent physically.

  ## Citations: FAIL

  - Citations to "Lou thesis" with equation numbers are good and traceable (e.g., "Lou Chapter 5, Eq. 5-11 through 5-16").
  - **Issue 1**: Hu PRD citation is incorrect. The document says "Hu PRD (arXiv:111.084065)". The correct arXiv identifier is **arXiv:2411.084065** (or the journal reference "Phys. Rev. D 111, 084065 (2025)"). The "111" in the document is the PRD volume number, not part of the arXiv identifier. This error makes the citation unsearchable.
  - **Issue 2**: Section 5.1 introduces Hu PRD response tensor notation $D_{ab}(\hat{n}, f)$ without any specific equation reference from the Hu PRD paper.
  - **Issue 3**: The entire Section 5 "Consistency with Hu PRD Framework" makes 5 consistency claims (Section 5.4 table) but NONE of them cite specific Hu PRD equation numbers, making all consistency claims unverifiable.
  - **Positive**: Noise model citations reference specific Lou thesis equation numbers.

- confidence: 0.70
  - Reasoning: The document is well-structured with good physics interpretation and self-questioning. Formula accuracy is high. However, the missing ST03 (Hu PRD formula comparison), missing ST09 (project code comparison), incorrect arXiv citation, and missing dedicated sections (ST07 comparison table, ST08 geometry parameters) are significant gaps that reduce confidence. The formulas themselves are correct, so the physics content is reliable; it's the completeness and verification against external references that fails.

- required redo:
  1. **Add ST03 section** (transfer function comparison with Hu PRD): Insert a dedicated section comparing OLC transfer function (2-30) with Hu PRD $T_{\text{one}}(\beta, \hat{n}\cdot\hat{u}) = \frac{1+\hat{n}\cdot\hat{u}}{2}[1 - e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$. Display both formulas side-by-side. Explain that OLC measures frequency shift (time derivative of light travel time) while PTA measures pulse arrival time (direct integral). Derive short-wave limit behavior: OLC sinc form $\sim O(1/L)$ suppression vs Hu PRD exponential form. Clarify that the sinc zeros correspond to complete destructive interference of GW-modulated phases along the path.
  2. **Add ST09 section** (comparison with project existing work): Verify against `scripts/01-olc-orf-solver.py` — confirmed that the solver implements (2-30) correctly (lines 38-56: `prefac = 1j * 2.0 * np.pi * abs(f) * L / c`, `sinc_v = sin(sinc_arg) / sinc_arg`, `phase = exp(-1j * beta * one_minus)`). Verify against `memory/01-olc-orf-formulas.md` — Hu PRD $T_{\text{one}}$ formula is correctly extracted. Verify against `memory/02-lou-olc-transfer-function.md` — correctly identifies the sinc vs exponential distinction. Note any inconsistencies found.
  3. **Add ST07 comparison table**: Systematic comparison of OLC vs LISA/PTA/TianQin covering: detection principle, frequency band, arm length, and sensitivity source.
  4. **Add ST08 dedicated section**: "OLC网络典型几何参数" as a separate section covering arm length range, baseline length range, typical configurations, detector count vs baseline count, bidirectional link characteristics.
  5. **Fix Hu PRD citation**: Correct "arXiv:111.084065" to "arXiv:2411.084065" (or "Phys. Rev. D 111, 084065 (2025)").
  6. **Add specific Hu PRD equation references**: Section 5 should cite specific Hu PRD equation numbers (e.g., Hu PRD Eq. 9 for response function, Eq. 7 for $T_{\text{one}}$, Eq. 11 for ORF integral).
  7. **Clarify $\Omega_n h^2$ formula**: Specify whether $S_n(f)$ is strain noise PSD or frequency-shift noise PSD, as this affects the physical interpretation.
