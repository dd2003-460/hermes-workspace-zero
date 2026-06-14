arXiv Submission Package
========================
Title: Chimera States as True Stable Attractors: Lifetime, Basin Geometry,
       and Mode Selection in Piecewise-Coupled Kuramoto Rings
Author: Cheng Lu (Algorithm Research Group)
Target: Physical Review E / Chaos
Source Project: D1-academic-AI (Ralph Loop Research)

Contents:
  chimera.tex          - Main LaTeX source (XeLaTeX, 12pt article class)
  Fig1-ring-schematic.png - Ring schematic figure
  Fig2-survival-function.pdf - Survival function
  Fig3-dc-rate-heatmap.pdf - DC rate heatmap
  Fig4-sector-psd.pdf  - Sector-level power spectral density

Compilation:
  xelatex chimera.tex

References:
  - Kuramoto (1976, 1984) - Original coupled oscillator model
  - Abbot et al. (2014) - Chimera states in nature
  - Cencenas et al. (2022) - Metastability of chimera states
  - DistCat framework (forthcoming) - 2-categorical distance derivation

Notes:
  - Uses standard LaTeX packages: graphicx, bm, hyperref, booktabs, amsmath
  - The refname package is not needed; Chinese section names in abstract
    use \textrm{} inline (see .tex for details)
  - 10 pages, 3 figures, 1 schematic
