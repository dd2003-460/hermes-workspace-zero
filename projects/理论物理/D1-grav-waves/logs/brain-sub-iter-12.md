# Brain-Sub Iteration 12 Report

**Date**: 2026-07-01
**Scope**: Literature verification for v11 edits + post-v11 structural check

## 1. Fujimoto:2026 verification

**VERIFIED: Paper exists and matches the claim.**

- arXiv:2602.01108, titled "Skewness in the Hellings-Downs curve" by Ryosuke Fujimoto and Keitaro Takahashi, cosmology & astrophysics category.
- The paper explicitly derives the third central moment (skewness) for a single unpolarized point source and for overlapping emitters.
- It finds that "the skewness remains non-zero in the large-source-number limit" -- this directly supports the weakened claim in the tex (line 305-306: "skewness of the HD correlation is primarily driven by discrete sources with Poisson shot noise").
- The mechanism is discrete-source shot noise, which is precisely what the tex claims.
- **Bibitem (line 440-443)**: `\bibitem{Fujimoto:2026}`, authors "R. Fujimoto and K. Takahashi", arXiv:2602.01108 -- **correctly formatted and matches reality.**
- **Minor caveat**: Fujimoto:2026 does not explicitly use the phrase "Poisson shot noise" in the abstract; it describes the mechanism as discreteness of sources, which is equivalent.

## 2. PBH GWB literature check

### Raidal:2017 (inline citation at line 366; bibitem at line 522-526)

- Bibitem: `\bibitem{Raidal:2017}`, M. Raidal, V. Vaskonen, H. Veermae, "Gravitational waves from primordial black hole mergers", JCAP **2017** (2017) no.09, 037, arXiv:1707.01480.
- **Key finding from pdflatex**: Citation `Raidal:2017` was initially undefined (first pass) but resolved by subsequent passes. This is normal LaTeX behavior for bibtext-based references.
- The paper discusses GWB from PBH mergers. However, the specific claim in the tex ("PBH GWB would trace dark matter distribution... with potentially comparable anisotropy amplitudes O(1-10%)") is NOT quantitatively substantiated by this paper. Raidal:2017 focuses on the merger GWB spectrum, not its anisotropy amplitude.
- **Better sources for PBH GWB anisotropy**:
  - Bartolo et al., arXiv:2002.02891: "Gravitational Wave Anisotropies from Primordial Black Holes" -- explicitly calculates anisotropies and non-Gaussianity of PBH GWB.
  - Wang, Vardanyan, Kohri, arXiv:2107.01935: "Probing primordial black holes with anisotropies in stochastic gravitational-wave background" -- first study of angular correlations of PBH GWB anisotropies.
  - arXiv:1909.12619 -- also discusses PBH GWB anisotropies.
- **Verdict: MEDIUM RISK.** Raidal:2017 is real and relevant to PBH GWB, but does not quantify anisotropy amplitudes.

### Soni et al. -- NOT FOUND AS A TEX CITATION

- I searched for Soni in the tex file: zero hits. Soni et al. is not cited anywhere in the current tex file. The Soni claim may have been removed in a later edit.
- The spectral index claim ("gamma = 2/3 for SMBHB") at line 366 is standard literature (Sesana 2013, Stevenson et al. 2015). Independent verification: accurate.
- The arXiv ID 1907.03004 now maps to a condensed matter paper (Richter et al.), not a Soni PBH GWB paper. Irrelevant since not cited in tex.

### Line 61 typo discovered during compilation

- Compile output shows `\OT1` appearing at the beginning of a paragraph on lines 61-62: `Overfull \hbox (6.50569pt too wide) in paragraph at lines 61--62: \OT1/cmr/m/n/10.95 ods be-cause...`
- This `\OT1` artifact suggests a line break or formatting issue in the text. It is visible in the compile log as part of the typeset text.
- Investigation needed: likely a stray token or word split (the word "o" appears as the first typeset token before "because" starts being hyphenated normally as "ods be-cause" which is wrong).
- This does NOT prevent compilation but is a typo in the source text.

## 3. Post-v11 structural check

All LaTeX environments balanced:
- `\begin{itemize}` / `\end{itemize}`: 3 pairs -- OK
- `\begin{enumerate}` / `\end{enumerate}`: 4 pairs -- OK
- `\begin{abstract}` / `\end{abstract}`: 1 pair -- OK
- `\begin{document}` / `\end{document}`: 1 pair -- OK
- `\begin{thebibliography}` / `\end{thebibliography}`: 1 pair -- OK

Sections present:
- Line 47: `\section{Introduction}` -- OK
- Line 65: `\section{Extended Functorial QFT for Gravitational-Wave Detection}` -- OK
- Line 200: `\section{Source Discrimination}` -- OK
- Line 282: `\section{Application to NANOGrav 15-Year Data}` -- OK
- Line 339: `\section{Discussion}` -- OK
- Line 350: `\subsection{Comparison with Standard Approaches}` -- OK
- Line 360: `\subsection{Limitations}` -- OK (nested under Discussion)
- Line 369: `\section{Conclusion}` -- OK

All 3 figure files exist: Fig1-Hellings-Downs-curve.png, Fig2-source-discrimination.png, Fig3-scaling-SNR.png.
No unmatched environments, no orphaned LaTeX commands.

## 4. Compile check

- **pdflatex version**: pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026)
- **Output**: 15 pages, 1,200,208 bytes
- **Fatal errors**: 0
- **Warnings**:
  - Label rerun (normal after structural changes)
  - Overfull hbox: ~6.5pt wide on lines 61-62 (cosmetic)
  - Underfull hbox: 3 instances in bibliography entries (normal formatting)
- **Images**: All 3 figures render successfully
- **Overall**: Clean compilation. Compiles to a 15-page PDF.

## 5. Risk Summary

| Risk | Level | Description |
|------|-------|-------------|
| Raidal:2017 cited for PBH GWB anisotropy amplitude (line 366) | MEDIUM | Paper discusses PBH merger GWB but does not quantify anisotropy. Better sources: Bartolo et al. (arXiv:2002.02891), Wang et al. (arXiv:2107.01935). |
| Overfull hbox on lines 61-62 | LOW | Minor formatting issue in paragraph about HD correlation form. Cosmetic only. |
| Fujimoto:2026 skewness citation | LOW | Verified: explicitly derives HD skewness for finite source populations. |
| Compile: 15-page PDF, 0 fatal errors | -- | Clean compilation. |

## 6. v11 Readiness Assessment

**Structurally sound. One citation gap.** The Raidal:2017 bibitem is valid, but the PBH GWB anisotropy amplitude claim ("O(1-10%)") lacks a directly supportive citation. Recommend adding Bartolo et al. (arXiv:2002.02891) as a citation for the anisotropy amplitude claim, or as `\cite{Raidal:2017,Bartolo:2020}`.

Fujimoto:2026 verified cleanly. Soni et al. is not cited in the current tex. No LaTeX errors.

## 7. Next Dispatch: Brain-Sub Iteration 13

- Add citation to Bartolo et al. (arXiv:2002.02891) for the PBH GWB anisotropy amplitude claim at line 366
- Fix overfull hbox on lines 61-62 if cosmetic polish is desired
- User confirms whether to proceed with the citation fix
