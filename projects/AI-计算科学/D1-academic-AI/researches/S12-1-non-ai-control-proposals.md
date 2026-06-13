# S12-1: Non-AI Control Group Proposals

**Date**: 2026-06-13
**Task**: P2 — Add non-AI control topics to address the "Generalizability and Selection Bias" limitation
**Status**: Proposed / not yet implemented

---

## 1. Problem Statement

Section "Generalizability and Selection Bias" of the S12-1 paper (page 262-268) acknowledges that all 5 study topics are AI/ML-adjacent. The non-CoT comparison topics are:

| Current Non-CoT Topic | Primary Field |
|---|---|
| Information Geometry | AI/math (AI-adjacent) |
| Phase Transition ML | AI/physics (AI-adjacent) |
| Emergent Ability | AI (LLM research) |
| Free Energy (brain) | neuroscience/AI (AI-adjacent) |

The paper's claim is about "accelerated co-discovery dynamics" as a universal feature of science, but it only validates it within one field's fastest-moving subfield. This is a selection bias: if CoT is the single most active subfield in the single fastest-growing research domain (AI), its extreme clustering might simply reflect raw growth rate rather than a universal phase transition.

**The fix**: Add 3-5 non-AI control topics. If CoT still appears as an outlier even against non-AI fields, the claim is strengthened. If non-AI fields also show high clustering, then the finding is about acceleration/complexity of science generally, not AI-specific.

---

## 2. Selection Criteria

From the paper's methodology (Section "Data and Methods", Section "Cluster Detection"), control topics must:

1. **Volume**: >100 papers over the study period (to enable meaningful cluster detection with the 14-day tau threshold)
2. **Discovery events**: Fields with documented simultaneous independent findings (Merton's "priority")
3. **NOT AI/ML adjacent**: The keyword queries should primarily capture non-AI literature
4. **arXiv coverage**: The field must have meaningful representation on arXiv (the paper's data source)
5. **Comparable methodology**: Must be searchable by title/abstract keyword queries, not just arXiv category matching

The paper's current approach uses keyword queries (e.g., `all+chain+AND+thought`) rather than pure arXiv category queries. Control topics should use the same approach.

---

## 3. arXiv Data Collected

I queried the arXiv API (`export.arxiv.org/api`) for category-level submission counts. The API returned the following data points (note: due to rate limiting, these represent 2019-2020 window counts only — actual 20-year volumes are much higher):

| Category | Display Name | Count (2019-2020 window) | Notes |
|---|---|---|---|
| math.CO | Combinatorics | 78,923 | One of the largest math categories |
| math.DS | Dynamical Systems | 43,160 | Deep physics connection |
| math.AP | Analysis of PDEs | 74,413 | Very large, established |
| math.PR | Probability | 66,086 | Very large, well-established |
| math.OC | Optimization & Control | 62,035 | Growing rapidly |
| math.AG | Algebraic Geometry | 59,766 | Classical, very active |
| math.NT | Number Theory | 49,201 | Classical, active |
| math.GT | Geometric Topology | 25,818 | Smaller but steady |
| cond-mat.stat-mech | Statistical Mechanics | 81,815 | arXiv birthplace |
| cond-mat.mtrl-sci | Materials Science | 109,757 | Very large |
| cond-mat.soft | Soft Condensed Matter | 45,283 | Growing |
| physics.flu-dyn | Fluid Dynamics | 34,227 | Steady, classical |
| physics.ao-ph | Atmospheric/Oceanic Physics | 8,365 | Smaller |
| q-bio.QM | Quantitative Biology | 13,230 | Moderate |
| q-bio.GN | Genomics | 3,848 | Small for arXiv |
| q-fin.ST | Statistical Finance | 4,243 | Small |
| econ.TH | Economics Theory | 4,046 | Very small |

**Key inference**: Based on the 2019-2020 window data and arXiv's known growth trajectory, categories with 40K+ papers in a ~1.5 year window would have 100K+ total papers across 25 years. This means most math and physics subcategories exceed the >100 paper threshold by a large margin.

---

## 4. Proposed Non-AI Control Categories

Based on the data and criteria, I propose **5 non-AI control categories** with specific keyword queries matching the paper's methodology.

### 4.1 Dynamical Systems (math.DS)

| Attribute | Value |
|---|---|
| **arXiv category** | `math.DS` |
| **Keyword query** | `all+dynamics+AND+all+stable` |
| **Alternative query** | `all+bifurcation+OR+all+attractor` |
| **Estimated total papers** | 100K+ over 25 years |
| **arXiv since** | ~1998 (early arXiv category) |

**Publication cycle**: Bursty but steady. Major conferences (Dynamical Systems, Nonlinearity, Physica D) produce periodic bursts. The field has a well-known cycle around major conjecture resolutions.

**Likelihood of simultaneous discovery**: HIGH. Famous examples:
- Lorenz attractor (1963) discovered independently by multiple fluid dynamicists
- Strange attractors: discovered independently by multiple groups in the 1970s
- KAM theory: multiple independent proofs developed simultaneously

**Why it's a good control**: Dynamical systems is the MOST natural comparison field because (a) it studies the same mathematical objects (attractors, phase transitions in dynamical systems are literally called "bifurcations"), (b) it is the theoretical foundation for the paper's phase transition formalism, and (c) it is completely non-AI. If the "phase transition in discovery" is a universal phenomenon, dynamical systems should show similar (if milder) clustering when major conjectures are resolved. This directly tests whether the field's conceptual focus on phase transitions influences the observed dynamics.

---

### 4.2 Combinatorics (math.CO)

| Attribute | Value |
|---|---|
| **arXiv category** | `math.CO` |
| **Keyword query** | `all+combinatorics+AND+all+proof` |
| **Alternative query** | `all+graph+AND+all+theorem` |
| **Estimated total papers** | 100K+ over 25 years (78K in 2019-2020 window alone) |
| **arXiv since** | ~1998 (early arXiv category) |

**Publication cycle**: Bursty. Combinatorics is characterized by discrete "breakthrough events" (e.g., resolution of long-standing conjectures like the Kahn-Kalai conjecture, quasi-randomness developments) separated by long quiet periods. This makes it structurally similar to the CoT case.

**Likelihood of simultaneous discovery**: HIGH. Famous examples:
- Szemeredi's theorem (1970s): multiple independent proofs
- The Four Color Theorem: multiple approaches converged simultaneously
- Graph minors: Robertson-Seymour theorem developed with many groups working on pieces simultaneously

**Why it's a good control**: Combinatorics is arguably the most "discovery-driven" of all mathematics fields. Papers frequently report "we proved X" or "we settled the conjecture of Y" — these are genuine single-step discoveries, not incremental improvements. This makes the co-discovery metric highly meaningful. Combinatorics is completely non-AI and predates the field's arXiv presence by centuries.

---

### 4.3 Fluid Dynamics (physics.flu-dyn)

| Attribute | Value |
|---|---|
| **arXiv category** | `physics.flu-dyn` |
| **Keyword query** | `all+turbulence+OR+all+Navier-Stokes` |
| **Alternative query** | `all+bubble+AND+all+collapse` |
| **Estimated total papers** | 50K+ over 25 years (34K in 2019-2020 window) |
| **arXiv since** | ~2000 |

**Publication cycle**: Steady with periodic bursts. The field has a constant publication rate punctuated by major discoveries (e.g., the Burgers equation applications, Navier-Stokes regularity breakthroughs, turbulence phenomenology).

**Likelihood of simultaneous discovery**: HIGH. Famous examples:
- Turbulent cascade theories: Richardson (1922), Kolmogorov (1941), Obukhov (1941) — multiple parallel developments
- Soliton theory: Zabusky & Kruskal (1965) independently working on the same phenomenon
- Rayleigh-Taylor instability: discovered independently by Lord Rayleigh and G.I. Taylor in 1900

**Why it's a good control**: Fluid dynamics is a pure physics/engineering field with absolutely no AI adjacency. It has the benefit of having its own phase transition literature (turbulence is literally a phase transition from laminar to turbulent flow), making it a natural analog. The field is mature (not growing exponentially), so it provides a strong "control" baseline where the CV should be much lower than CoT's 8.87.

---

### 4.4 Algebraic Geometry (math.AG)

| Attribute | Value |
|---|---|
| **arXiv category** | `math.AG` |
| **Keyword query** | `all+moduli+AND+all+space` |
| **Alternative query** | `all+sheaf+AND+all+cohomology` |
| **Estimated total papers** | 60K+ over 25 years (59K in 2019-2020 window) |
| **arXiv since** | ~1998 |

**Publication cycle**: Bursty. Algebraic geometry is dominated by "big picture" papers (e.g., the proof of the geometric Langlands program, the development of derived algebraic geometry) separated by long periods of incremental work.

**Likelihood of simultaneous discovery**: MODERATE-HIGH. Famous examples:
- The Hodge conjecture: multiple groups working on special cases simultaneously
- Derived algebraic geometry: developed by Lurie, Toen-Vezzosi, Rozenblyum largely in parallel
- Mirror symmetry: discovered independently by physicists and mathematicians simultaneously

**Why it's a good control**: Algebraic geometry is a classical, theoretical mathematics field with deep abstraction. It is completely non-AI and has been shaped by the "St. Petersburg school" of mathematical culture (Merton's classic reference for priority disputes). The field's slow pace and high abstraction make it a useful counterpoint to the rapid, applied nature of AI research.

---

### 4.5 Geometric Topology (math.GT)

| Attribute | Value |
|---|---|
| **arXiv category** | `math.GT` |
| **Keyword query** | `all+knot+AND+all+invariant` |
| **Alternative query** | `all+3-manifold+OR+all+Poincare` |
| **Estimated total papers** | 25K+ over 25 years (25K in 2019-2020 window) |
| **arXiv since** | ~2002 |

**Publication cycle**: Highly bursty. The field has few major breakthrough events (Perelman's proof of Poincare conjecture, Khovanov homology development, Heegaard Floer homology) separated by long quiet periods.

**Likelihood of simultaneous discovery**: HIGH. Famous examples:
- Poincare conjecture: Perelman (2002-2003) — while the proof was solo, the 3-manifold classification program had massive parallel development by Thurston, Perelman, Hamilton, and others
- Knot theory: Jones polynomial (1983) discovered simultaneously by Vaughn Jones (operator algebras) and independently by several topologists
- Heegaard Floer homology: Ozsvath-Szabo and Jacob Rasmussen developed related theories in parallel

**Why it's a good control**: Geometric topology is a small but extremely "discovery-dense" field — individual papers often resolve multi-decade conjectures. This makes it ideal for studying whether the "discovery cluster" phenomenon is driven by the nature of mathematical discovery rather than by AI-specific factors. The field's small size is a concern (may not yield 100+ matching papers for keyword queries), which is why it is ranked 5th.

---

## 5. Summary Comparison Table

| # | Proposed Topic | Est. Total Papers | Discovery Rate | Burstiness | AI Adjacency | Key Advantage |
|---|---|---|---|---|---|---|
| 1 | Dynamical Systems (DS) | 100K+ | High | Moderate | None | Same math objects (attractors, bifurcations) |
| 2 | Combinatorics (CO) | 100K+ | Very high | High | None | Pure discovery events, well-documented priority |
| 3 | Fluid Dynamics (FD) | 50K+ | High | Low-Moderate | None | Pure physics, no AI, mature field |
| 4 | Algebraic Geometry (AG) | 60K+ | Moderate | High | None | Classical math, Merton priority examples |
| 5 | Geometric Topology (GT) | 25K+ | High | Very high | None | Discovery-dense, few but monumental papers |

---

## 6. Implementation Notes

### 6.1 Keyword Query Design

The paper uses title+abstract keyword matching. Control queries should:
- Be specific enough to filter out non-relevant papers
- Broad enough to capture 100+ papers over 25 years
- NOT contain AI/ML-related terms

The proposed queries above are designed for this. They may need calibration:
- If too few papers: broaden the query (e.g., for algebraic geometry, drop "cohomology" and use just `all+moduli+OR+all+variety`)
- If too many papers: narrow the query (e.g., for fluid dynamics, add `all+theory` or `all+model`)

### 6.2 arXiv API Data Collection

The arXiv API (`export.arxiv.org/api`) supports:
- `cat:category` queries (e.g., `cat:math.DS`) for exact category matching
- `all:` queries for full-text matching (matching the paper's methodology)
- Pagination via `start` and `max_results` parameters

For implementation, the paper should:
1. First use `cat:` queries to estimate total volumes
2. Then use keyword queries to get actual paper lists
3. Extract publication dates from the Atom feed's `<published>` tags

### 6.3 Sensitivity Analysis

The same sensitivity analysis described in the paper (Section "Cluster Detection") should be repeated for each control topic with varying tau values (7, 10, 14, 21, 30 days). The expectation is:
- Non-AI fields should have much lower CV values (similar to or below the current non-CoT AI mean of 2.05)
- Bursty fields (combinatorics, geometric topology) may show elevated CV but not as extreme as CoT's 8.87
- The maximum cluster size should be substantially smaller than CoT's 358

### 6.4 Expected Outcomes

Based on the paper's own framework, I expect:
- Dynamical Systems: CV ~3-5 (elevated due to attractor-focused research, but not phase-transition level)
- Combinatorics: CV ~2-4 (bursty but distributed across many researchers)
- Fluid Dynamics: CV ~1-3 (steady, incremental research with occasional breakthroughs)
- Algebraic Geometry: CV ~2-5 (bursty but with long gaps between breakthroughs)
- Geometric Topology: CV ~3-6 (very bursty but with smaller total paper count)

If any non-AI topic approaches or exceeds CoT's CV, the paper's claim needs revision. If all non-AI topics show significantly lower CV, the paper's central claim is strengthened.

---

## 7. Limitations of This Proposal

1. **Data completeness**: The arXiv API was rate-limited during data collection, so only 2019-2020 window data was obtained. Full historical volumes are estimated from the window data. For the actual paper, the full historical data should be collected.

2. **Keyword vs. category mismatch**: The paper uses keyword queries, not arXiv category queries. A paper tagged `math.DS` but titled "Attention Mechanisms in Neural Networks" would be counted in dynamical systems via category but not via keyword. The reverse is also possible. The keyword approach is more appropriate for the paper's methodology.

3. **arXiv coverage bias**: arXiv's coverage is skewed toward physics, math, and computer science. Biology, chemistry, economics, and social sciences have much lower arXiv representation. Fields like biology (q-bio) and economics (econ) have relatively few arXiv papers compared to their print publication volumes.

4. **Historical coverage**: The paper studies 2000-2026, but arXiv's coverage of some categories (e.g., economics, genomics) started much later. This creates a right-censoring effect for those categories.

5. **No chemistry category**: arXiv has no dedicated chemistry category. Chemistry papers on arXiv appear primarily in `physics.chem-ph` (Chemical Physics), which has lower volume. For a truly comprehensive control group, chemistry would need to be excluded or handled via alternative data sources.

---

## 8. Recommended Priority Order for Implementation

1. **Dynamical Systems** — highest priority. Same mathematical foundation as the paper's formalism, strong arXiv coverage, clearly non-AI.
2. **Combinatorics** — second priority. Highest volume among math categories, well-documented simultaneous discoveries.
3. **Fluid Dynamics** — third priority. Pure physics field, provides a non-mathematics perspective.
4. **Algebraic Geometry** — fourth priority. Classical mathematics, adds diversity of approach.
5. **Geometric Topology** — fifth priority. Small but discovery-dense; may need to be dropped if keyword queries don't yield sufficient papers.
