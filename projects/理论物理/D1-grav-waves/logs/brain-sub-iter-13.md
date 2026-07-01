# Brain-Sub Iteration 13 Report -- Final Pre-Submission Audit

## Risks

| Risk | Level | Details |
|------|-------|---------|
| 3 uncited bibitems in bibliography | MEDIUM | `\bibitem{Lemke:2024}`, `\bibitem{Schenkel:2023}`, `\bibitem{Benini:2019}` are defined in the thebibliography but never referenced via `\cite{...}` anywhere in the text. These are residual entries with no citation anchor. Either they need a \cite added to the paper body, or they should be removed from the bibliography. |
| Line 61 overfull hbox (~6.5pt) | LOW | Single line exceeding margin by 6.5pt in "Precision-aware methodology" paragraph. Minor cosmetic issue. |
| Underfull hboxes in bibliography | LOW | 3 instances in long bibliography titles. Standard LaTeX behavior with titles longer than a line. No editorial concern. |
| Compile: label rerun warning | INFO | Normal LaTeX behavior. Labels stabilize after second run (already happened). |

## Verification Results

- **Citation-to-bibitem matching**: 24 unique cite keys (across 18 \cite commands) all have matching \bibitem definitions. 0 unresolved citations. 0 unmatched bibitems (excluding the 3 uncited ones above).
- **pdflatex compile**: Clean. No errors. No undefined references. 15-page PDF produced successfully (1,200,208 bytes).
- **Tarball integrity**: v12 contains 5 files (GW-BacQFT-paper.tex, GW-BacQFT-paper.pdf, Fig1-3.png). MD5 of tex in tarball (`4c03e4131851f2ca78a403fc7873d927`) matches working copy exactly.
- **Previous fixes verified**: Fujimoto:2026 OK (iter 12), Raidal 2017 year OK (iter 12), (infty,n) structural fix (iter 10), skewness/PBH caveats (iter 11) -- all present in current text.

## Recommendation

**Not yet ready for final submission.** One actionable issue needs resolution before v13:

**Remove or cite the 3 dangling bibliography entries** (Lemke:2024, Schenkel:2023, Benini:2019). If these papers are not actually used in the text, they should be deleted to avoid reviewer confusion about whether they are relevant. If they should be cited, add the appropriate `\cite{...}` references to the manuscript body.

This is a straightforward fix (either 3 `\bibitem` deletions or 3 `\cite` additions).

## Next Dispatch: Brain-Sub Iteration 14
- Remove Lemke:2024, Schenkel:2023, Benini:2019 from bibliography
- Rebuild v13 tarball
- Confirm ready for arXiv upload
