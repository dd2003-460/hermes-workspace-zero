# D40 arXiv Submission Metadata

## Title
The Precision-Accessibility Tradeoff in AI Markets: Why General and Expert Models Diverge as an Information-Theoretic Optimum

## Author
Cheng Lu (Independent Researcher)

## Subjects
cs.AI, cs.CY, stat.AP

## Abstract (English)

Large language models and other AI systems present an apparently paradoxical phenomenon: general-purpose models actively "downgrade" precision in their outputs to serve the majority of users—using more accessible language, simplified explanations, and fewer technical details. The traditional view understands this phenomenon as "information loss" or "compromise." This paper proposes an alternative theoretical framework: **the AI precision-accessibility tradeoff is not an engineering compromise, but an information-theoretic optimum under the constraint of user cognitive distribution.**

We establish a formal model defining user cognitive load capacity as $C \sim F_C(\mu_C, \sigma_C)$, system precision as $D$, and accessibility as $A(D) = P(C \geq C_{\text{threshold}}(D))$. Within this framework, we prove four core propositions: (1) precision degradation in general models is information selection, not information loss; (2) there exists an unattainable precision threshold under market constraints; (3) specialized markets require higher-quality precision output; (4) multi-precision routing strategies Pareto dominate any single-precision strategy.

Through four numerical experiments, we validate these propositions: monotonic decreasing accessibility (100%, R²=0.96), optimal precision for specialized markets $D^*_{\text{expert}} = 31.7$ significantly exceeding that for general markets $D^*_{\text{general}} = 17.0$ (gap of 14.6), flatter accessibility curves with greater user heterogeneity (log-log slope -0.97, consistent with $1/\sigma$ prediction), and 119.9% improvement of multi-precision routing over single strategies (p=2.9×10⁻¹³³).

Our theoretical framework provides a unified analytical tool for understanding the "basic" vs. "professional"分化 of AI products, and explains why different domains including medical AI, legal AI, and research AI all exhibit similar precision-tiering patterns.

## Keywords
AI precision; accessibility; cognitive load; specialization economics; multi-precision routing; information selection

## LaTeX File
D40-paper-converted.tex (628 lines)

## Supporting Files
- `chimera_lab/d40-precision-tradeoff-simulation.py` — experiment code
- `chimera_lab/d40-results.json` — experiment results
- `chimera_lab/Fig-D40-all-experiments.png` — experiment visualization figure

## arXiv Category
- Primary: cs.AI (Artificial Intelligence)
- Secondary: cs.CY (Computers and Society), stat.AP (Applications)

## Notes
- D40 has the highest Bayesian posterior (0.72) among 20 theories (D30-D53)
- All 4 experimental propositions pass validation
- 8/9 independent evidence sources directly support D40 predictions
