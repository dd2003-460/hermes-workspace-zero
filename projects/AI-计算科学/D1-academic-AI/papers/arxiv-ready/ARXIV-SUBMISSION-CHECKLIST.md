# arXiv Submission Checklist — D1-academic-AI Papers

## Prerequisites
- [ ] Login to https://submitt.arxiv.org with your arXiv account (成璐)
- [ ] If no account: create one at https://arxiv.org/signup (takes ~5 min)

## Submission Order (critical: DistCat FIRST)

### Batch 1: Citation anchor (submit first, wait ~1 day for acceptance)
1. **DistCat v5** — math.CT or math.RT
   - Package: `DISTCAT-arxiv-submission-v5.tar.gz` (802KB)
   - Pages: 20
   - Title: "Distance Derivation via 2-Categorical Framework"
   - Figure: 2 figures included

### Batch 2: Papers citing DistCat (can submit once DistCat is accepted)
2. **Chimera** — chao-dyn (chaos) or nlin.CD
   - Package: `chimera-stable-attractors-arxiv.tar.gz` (123KB)
   - Pages: 10

3. **S18-1** — cs.AI
   - Package: `S18-1-kolmogorov-router-arxiv.tar.gz` (480KB)
   - Pages: 13

4. **S17-1** — cs.CL or stat.ML
   - Package: `s17-1-arxiv-v1.tar.gz` (1.2MB)
   - Pages: 8

### Batch 3: Independent papers
5. **D30-2** — cs.LG
   - Package: `d30-2-ib-bound-arxiv-v1.tar.gz` (84KB)
   - Pages: 8
   - Title: "A Tighter Lower Bound on Chain-of-Thought Model Size via Information Bottleneck Analysis"

6. **D30** — cs.LG
   - Package: `d30-hierarchical-data-arxiv-v1.tar.gz` (90KB)
   - Pages: 6
   - Note: Companion paper to D30-2, references D30-2

7. **D29** — cs.LG
   - Package: `d29-scaling-understanding-arxiv-v1.tar.gz` (96KB)
   - Pages: 8
   - Title: "The Scaling-Understanding Incompatibility Theorem"

## Common Settings (all papers)
- Author: Cheng Lu
- Email: cheng.lu@example.com
- Affiliation: Independent Researcher
- Abstract: see each paper's .tex file `\begin{abstract}...\end{abstract}`

## Total Time Estimate
- ~5 minutes per paper (login + upload + submit + confirm)
- 7 papers × 5 min = ~35 minutes total (not counting arXiv review time)
- arXiv typically accepts within 1-3 business days for first submission

## After Submission
1. Replace `[D1-academic-AI/...]` cross-references with actual arXiv IDs
2. Update the arXiv versions of Chimera, S18-1, S17-1, D29 to cite the published arXiv IDs instead of "forthcoming"
3. Add arXiv links to all project documentation

## Paper Dependencies (for understanding why order matters)
- DistCat is cited by: Chimera, S18-1, S17-1, D29
- Chimera is cited by: S17-1
- S18-1 is cited by: S17-1
- D30-2 is cited by: D30, D29
- S17-1 is the LAST paper to submit (cites Chimera, S18-1, S12-1)
