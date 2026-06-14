# arXiv Submission Guide for D1-academic-AI Papers

## Submission Status

| Paper | Title | Target | Package | Status |
|-------|-------|--------|---------|--------|
| DistCat v5 | Distance Derivation via 2-Categorical Framework | arXiv (math.CT) | DISTCAT-arxiv-submission-v5.tar.gz | READY |
| Chimera | Chimera States as True Stable Attractors | Chaos / PR-E | chimera-stable-attractors-arxiv.tar.gz | READY |
| S18-1 | Kolmogorov Complexity Router for Dynamic Tool Selection | arXiv (cs.AI) | S18-1-kolmogorov-router-arxiv.tar.gz | READY |
| S17-1 | Semantic Space Geometry: Negative Curvature from Word Vector Embeddings | arXiv (cs.CL) | s17-1-arxiv-v1.tar.gz | READY |
| D30-2 | Tighter CoT Model Size Lower Bound via IB (proof improved, 8 pages) | arXiv (cs.LG) | d30-2-ib-bound-arxiv-v1.tar.gz | READY |
| D30 | Hierarchical Training Data and CoT Bounds (companion paper, references D30-2) | arXiv (cs.LG) | d30-hierarchical-data-arxiv-v1.tar.gz | READY |
| D29 | Scaling-Understanding Incompatibility Theorem (8 pages) | arXiv (cs.LG) | d29-scaling-understanding-arxiv-v1.tar.gz | READY |

## How to Submit

1. Go to https://submitt.arxiv.org
2. Login with your arXiv account (or create one)
3. Click "New Submission"
4. Upload the tar.gz package for each paper
5. Select the appropriate category (see below)
6. Submit each paper individually

## Recommended Categories

- **DistCat**: math.CT (Category Theory) or math.RT
- **Chimera**: chao-dyn (chaos/nlin.CD) or phys.rev.e
- **S18-1**: cs.AI (Artificial Intelligence)
- **S17-1**: cs.CL (Computation and Language) or stat.ML
- **D30-2**: cs.LG (Machine Learning) or stat.ML
- **D30**: cs.LG (Machine Learning) or cs.AI
- **D29**: cs.LG (Machine Learning) or stat.ML

## Common arXiv Requirements

- PDF must be compiled from LaTeX source included in package
- All figures must be included
- Author name: Cheng Lu
- Corresponding email: cheng.lu@example.com (update if needed)
- Abstract: see each paper's .tex file
- No external dependencies beyond standard TeX Live packages

## Package Locations

All packages are at:
`/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-academic-AI/papers/arxiv-ready/`

## Notes

- DistCat v5: 20 pages, LaTeX source + 2 figures. Most important paper — submit first.
- Chimera: 10 pages, compiled clean on 2nd pass (citation resolved).
- S18-1: 13 pages, 5 figures, cosmetic hyperref warning only.
- S17-1: 8 pages, 3 figures, font warnings (cosmetic).
- D30-2: 8 pages, 0 figures, rigorous 4-step proof (Fano inequality + chain rule). Theoretical paper on CoT model size.
- D29: 8 pages, 0 figures. Theoretical paper on scaling-understanding incompatibility.

## Post-Submission

After submission, update the paper references across all papers:
- Replace `[D1-academic-AI/...]` with actual arXiv IDs
- Update cross-references in Chimera, S18-1, and other papers
