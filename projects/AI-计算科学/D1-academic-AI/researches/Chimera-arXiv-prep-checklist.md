# Chimera Paper arXiv Pre-Submission Checklist

**Date**: 2026-06-13
**Paper**: `chimera-stable-attractors/chimera.tex`
**Compiled PDF**: 20 pages, 356123 bytes, compiled 2026-06-13 01:51
**Previous readiness check**: `Chimera-Paper-ArXiv-Readiness-Check.md` (2026-06-07)
**Target venue**: Chaos (AIP) / arXiv

---

## 1. Compilation Status

| Check | Status | Details |
|-------|--------|---------|
| LaTeX compiles without error | PASS | Zero errors |
| Warnings | MINOR | Unused options `[amsfonts,amssymb]`; one overfull hbox (~12pt) at page 12 |
| Figure inclusion | PASS | All 4 figures loaded successfully |
| Bibliography compilation | PASS | All 27 entries resolved, cross-refs intact |
| `.aux` / `.out` clean | PASS | Output outline and bookmarks consistent |

**Assessment**: The PDF is technically clean. The minor warnings are cosmetic and non-blocking.

---

## 2. Title Assessment

**Current title**: "Chimera States as True Stable Attractors: Lifetime, Basin Geometry, and Mode Selection in Piecewise-Coupled Kuramoto Rings"

| Criterion | Status | Notes |
|-----------|--------|-------|
| Describes the contribution | PASS | Clearly states 3 contributions |
| Mentions key system | PASS | "Piecewise-Coupled Kuramoto Rings" |
| Not too long for Chaos | MINOR | 16 words. Chaos has no strict limit; PRL prefers shorter (12-15 words). For Chaos: acceptable. For PRL: consider shortening. |
| Not too long for arXiv | PASS | No character limit for arXiv title |

**Verdict**: Publication-ready for Chaos and arXiv.

---

## 3. Abstract Assessment

**Current abstract** (154 words, ~1080 characters):

> Chimera states---counterintuitive patterns in which identical coupled oscillators partially self-organize into coherent and incoherent regions---are typically presumed to be metastable. Here we challenge this view for a piecewise-coupled Kuramoto ring ($N = 1500$). Protocol A integration of 500,000 timesteps shows zero collapses and zero phase slips across three chimera seeds, with survival function $S(T) = 1.0$ and metastability classification H1 (coexisting attractor). A 300-run pilot scan across 100 grid points in $(\epsA, \epsB, K_0)$ reveals a domain coexistence (DC) rate of 73.7\%, with chimera produced at all tested parameters, indicating a large and parameter-invariant basin of attraction. We identify a mode-selection mechanism: the piecewise cosine coupling selects specific Fourier modes that stabilize chimera, consistent with recent work on delay-induced mode selection (Wu, 2026). Sector-level power spectral density shows no temporal modulation, confirming the chimera spatial pattern is frozen. Finally, we demonstrate that the domain-level order parameter ($r \approx 0.95$) is insufficient to detect chimera, establishing the necessity of sector-level resolution. Our results challenge the prevailing view of chimera metastability and provide a framework for understanding chimera stability in generalized coupling schemes.

| Criterion | Status | Notes |
|-----------|--------|-------|
| Length within arXiv limit | PASS | arXiv limit is generous; 154 words is reasonable |
| Length within Chaos limit | PASS | Chaos allows up to 250 words |
| Contains background | PASS | First sentence contextualizes chimera states |
| States the problem | PASS | "typically presumed to be metastable" |
| Describes methods | PASS | Protocol A, 300-run pilot, sector-level PSD |
| Reports key results | PASS | S(T)=1.0, DC rate=73.7%, zero slips, 6 contributions |
| States significance | PASS | Challenges metastability view, provides framework |
| Keywords | **BLOCKER** | Missing. Keywords are standard for arXiv and Chaos. Should list 4-6 terms. |
| Self-contained | PASS | No undefined acronyms; all abbreviations explained in text |

**Blocking issue**: Missing keywords. arXiv recommends them; Chaos journal requires them in the manuscript.

---

## 4. Author Information Assessment

| Criterion | Status | Details |
|-----------|--------|---------|
| Author names | **BLOCKER** | Currently "D1-Academic-AI Project" -- this is a project label, not actual author names. Real names are required for arXiv submission and Chaos submission. |
| Affiliations | **BLOCKER** | None provided. No institutional affiliation. |
| Corresponding author | **BLOCKER** | No email address or correspondence note. |
| Author order | **BLOCKER** | N/A with single "author" placeholder. |
| ORCID / author notes | MINOR | Not strictly required for arXiv but good practice. |
| Acknowledgments | PASS | Present, notes Ralph Loop autonomous framework |
| `\thanks{}` footnote | MINOR | "Ralph Loop Autonomous Research" is present but not sufficient as affiliation |

**Critical blockers**: arXiv requires real author names and at least one affiliation. Chaos requires author information with affiliations. The placeholder "D1-Academic-AI Project" will be rejected or require correction.

---

## 5. References Assessment

**Total entries in `.bib`**: 27
**Total `\cite{}` calls in `.tex`**: 22
**Uncited entries in `.bib`**: 2 (`ameli2025`, `smirnov2025` and `kuramoto1975`, `martens2015`, `rakshit2017`, `dos2018`, `banerjee2018`, `butzinski2023`, `eldering2021`, `lee2023`, `lee2019`, `grønborg2023`, `zhang2019`, `maistrenko2020`, `kundu2022`, `lee2021`) -- 15 uncited (the bib file has entries that are not cited)

Wait, let me recount. The bib file has these entries:
- Cited in tex: `abrams2004`, `kuramoto1975`, `strogatz2018`, `ashwin2024`, `wu2026`, `kumar2026`, `zdyrski2025`, `floriach2024`, `S12-1-2026`, `S17-1-2026`, `S18-1-2026` = 11 cited
- In bib but NOT cited: `smirnov2025`, `ameli2025`

Wait, the bib file also has entries not in the tex's thebibliography. Let me check more carefully.

The `.tex` file has thebibliography with 27 entries. The `.bib` file has 8 entries. These are two separate reference mechanisms.

| Criterion | Status | Details |
|-----------|--------|---------|
| Reference count in bibliography | WARN | 27 references. For Chaos: adequate (Chaos typically expects 20-50). For PRL: below typical 30-60 range. |
| Foundational references present | PASS | Abrams & Strogatz 2004, Kuramoto 1975 |
| Recent references included | PASS | Includes 2024-2026 papers |
| Intra-project references | WARN | 3 self-citations (S12, S17, S18). Acceptable for arXiv, but worth noting. |
| `floriach2024` incomplete | **ISSUE** | bib entry has `eprint = {2407.xxxx}` -- placeholder page numbers |
| `ameli2025` vague | MINOR | "et al.", no arXiv number, no journal info |
| `strogatz2018` title mismatch | **ISSUE** | Bib says year 2000, label says 2018. The actual citation is "From Kuramoto to Crawford" Physica D 143 (2000). Label should be `strogatz2000`. |
| All cited entries exist in bib | PASS | No broken citation keys |
| No duplicate references | PASS | No obvious duplicates |

**Issues to fix before submission**:
1. `floriach2024` eprint field has `2407.xxxx` -- needs actual page numbers/arXiv ID
2. `strogatz2018` citation key vs year mismatch (should be `strogatz2000`)
3. `ameli2025` lacks complete publication metadata
4. Consider adding more references from the 15 uncited entries if expanding

---

## 6. Figures Assessment

| Figure | File | Type | Status | Notes |
|--------|------|------|--------|-------|
| Fig 0 | `Fig0-ring-schematic.png` | PNG 788x585px | WARN | Generated 2026-06-09. README noted this should be manually drawn. Resolution is 788px -- adequate for digital, marginal for print (arXiv recommends 300+ DPI at print size). |
| Fig 1 | `Fig1-survival-function.pdf` | PDF vector | PASS | Data-driven, vector format. |
| Fig 2 | `Fig2-dc-rate-heatmap.pdf` | PDF vector | PASS | Data-driven, vector format. |
| Fig 3 | `Fig3-sector-psd.pdf` | PDF vector | PASS | Data-driven, vector format. |
| All figures have captions | PASS | All 4 have descriptive captions with labels |
| Figures referenced in text | PASS | All 4 referenced (Fig.~\ref{...}) |
| Figure numbering | PASS | Sequential Fig 0-3, but "Fig 0" is unconventional |
| Missing figure cross-refs in text | PASS | No orphaned figure references |

**Issue**: "Fig 0" is unconventional. Standard practice is Fig 1, Fig 2, etc. The "0" designation suggests it is supplementary or preliminary. For publication, consider renumbering to Fig 1 (shifting others) or moving to Supplementary.

---

## 7. Manuscript Structure Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Abstract present | PASS | |
| Introduction with motivation | PASS | Good opening, clear problem statement |
| Model section | PASS | Well-defined equations (1)-(4) |
| Methods/Protocols described | PASS | Protocol A, phase slip detection, RK4 scheme |
| Results with data | PASS | Protocol A results, basin geometry, PSD |
| Discussion | PASS | Comparison, limitations, future work |
| Conclusion | PASS | Summarizes 5 key results |
| Acknowledgments | PASS | |
| References | WARN | 27 entries, see Section 5 |
| No tables | PASS | Not required for this paper |
| Equations numbered | PASS | All display equations numbered |
| Cross-references work | PASS | All `\ref{}` resolve correctly |

---

## 8. arXiv-Specific Requirements

### 8.1 Required Information

| Requirement | Status | Details |
|-------------|--------|---------|
| Author names | **BLOCKER** | "D1-Academic-AI Project" is not a valid author name |
| Author affiliation(s) | **BLOCKER** | Missing |
| Email (for corresponding author) | **BLOCKER** | Missing |
| arXiv category | WARN | Paper targets `chao-dyn` or `nlin.AO`. These are valid categories. Need to select during submission. |
| Abstract | PASS | Present and adequate |
| Comments/notes | MINOR | No "Comments:" field. arXiv allows optional notes (e.g., "Submitted to Chaos"). |
| DOI | MINOR | No DOI yet (expected -- arXiv assigns arXiv:XXXX.XXXXX after submission) |

### 8.2 Formatting

| Requirement | Status | Notes |
|-------------|--------|-------|
| Single PDF submission | PASS | `chimera.pdf` is a single file |
| PDF embedded fonts | PASS | Standard Computer Modern fonts |
| PDF searchability | PASS | Text-based PDF, not scanned images |
| No external dependencies | PASS | All figures embedded in PDF |
| File size | PASS | 356 KB (well under arXiv limits of ~50MB) |
| `\documentclass` compatibility | WARN | Uses `article` class, not Chaos-specific `aipacp` class. For arXiv this is fine. For Chaos journal submission, would need to switch. |

### 8.3 Optional but Recommended

| Recommendation | Status | Notes |
|----------------|--------|-------|
| Keywords | **BLOCKER** | arXiv recommends; Chaos requires |
| PACS/MSC codes | MINOR | arXiv doesn't require PACS codes (deprecated). The `chao-dyn` or `nlin.AO` category codes suffice. |
| License | MINOR | arXiv uses non-exclusive license by default. For Chaos, copyright assignment happens at acceptance. |
| Supplementary materials | WARN | No supplementary files. The paper mentions M2 full scan (700 grid points) as future work -- if data files exist, they could be supplementary. |
| Data availability statement | WARN | Not included. Increasingly expected even for computational papers. |

---

## 9. Chaos Journal-Specific Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Journal template | **BLOCKER** | Uses `article` class. Chaos requires `aipacp` or `CHAOS2` class. |
| Manuscript length | PASS | 20 pages single-column is within Chaos limits (typically up to 25 pages) |
| Figure quality | WARN | Fig 0 is PNG at 788px; rest are PDF vector. Chaos prefers TIFF/EPS/PDF. |
| Color figures | PASS | Color figures allowed |
| Online supplementary | MINOR | Can be added via AIP portal |
| Cover letter | MINOR | Required for Chaos submission (separate from arXiv) |
| Suggested reviewers | MINOR | Required for Chaos submission |
| Copyright form | MINOR | Post-acceptance |

---

## 10. Blockers Summary

The following items MUST be resolved before arXiv submission:

| # | Blocker | Severity | Estimated Fix |
|---|---------|----------|---------------|
| B1 | **Author names are placeholder** "D1-Academic-AI Project" | **P0 - BLOCKING** | Replace with actual author names. arXiv will not accept "D1-Academic-AI Project" as a legitimate author. |
| B2 | **No author affiliation** | **P0 - BLOCKING** | Must include at least one affiliation (institutional or "Independent Research"). |
| B3 | **No corresponding author email** | **P0 - BLOCKING** | Required for arXiv submission and Chaos submission. |
| B4 | **Missing keywords** | **P0 - BLOCKING** | Required by Chaos; recommended by arXiv. |
| B5 | `strogatz2018` citation key/year mismatch | **P1 - SHOULD FIX** | Change to `strogatz2000` (the paper was published in 2000). |
| B6 | `floriach2024` has `2407.xxxx` placeholder | **P1 - SHOULD FIX** | Needs real arXiv number and/or page numbers. |

---

## 11. Recommended Actions (Priority Order)

### P0 - Must fix before ANY submission:
1. **Replace author line** with real author names and affiliations.
   ```latex
   \author{Author Name\affiliation{Affiliation}\email{email@example.com}}
   ```
2. **Add keywords**:
   ```latex
   \keywords{chimera states, Kuramoto model, stable attractors, basin of attraction,
   phase synchronization, mode selection, piecewise coupling}
   ```
3. **Add PACS/MSC codes** (arXiv doesn't require but Chaos may request):
   ```
   05.45.Xt, 02.50.Ch, 05.45.Gg
   ```

### P1 - Should fix before Chaos journal submission:
4. **Switch to Chaos document class** (`\documentclass[aipacp]{aip-cp}` or equivalent).
5. **Fix figure numbering** -- rename Fig 0 to Fig 1 or move to Supplementary.
6. **Fix citation errors** (B5, B6).
7. **Add data availability statement** (increasingly expected).
8. **Fix overfull hbox** on page 12 (split long sentence).

### P2 - Nice to have for arXiv:
9. Consider expanding references from the 15 uncited entries in the bib file.
10. Add Supplementary Material if M2 pilot data files exist.
11. Add comments field for arXiv: `arXiv:26XX.XXXXX [chaos-dyn]`

---

## 12. arXiv Submission Command (after fixes)

When all P0 blockers are resolved, submission can proceed:

```bash
# arXiv submission (requires author confirmation)
curl -F "submission_type=arXiv" \
     -F "file=@chimera.pdf" \
     -F "title=..." \
     -F "authors=..." \
     -F "categories=chaos-dyn" \
     "https://arxiv.org/submit"
```

Previous issue: HTTP 422 (Unprocessable Entity) -- likely SSL MITM interception. May need to use the web interface at `submit.arxiv.org` instead of CLI.

---

## 13. Comparison with Previous Readiness Check (2026-06-07)

| Item | Previous Assessment | Current Assessment | Change |
|------|--------------------|--------------------|--------|
| Length | PRL may need compression, Chaos OK | No change | -- |
| Abstract quality | Missing keywords | Missing keywords | No change |
| References | 8 cited, need 30-60 | 11 cited, 27 in bib file | Slightly worse (more uncited entries exist) |
| Figure quality | 2 of 4 need work | Same (Fig 0 still PNG, others OK) | No change |
| Author info | Missing | Confirmed missing -- now BLOCKER | Escalated to P0 |
| PACS codes | Missing | Confirmed missing | No change |
| LaTeX errors | Zero | Zero | No change |

---

## 14. Final Verdict

**Current state: NOT READY for arXiv submission**

The paper is well-structured with sound methodology and compelling results. However, **5 P0 blockers** must be resolved:

1. Real author names (not "D1-Academic-AI Project")
2. Author affiliations
3. Corresponding author email
4. Keywords
5. Citation errors (strogatz2018, floriach2024)

After resolving these 5 items, the paper would be **arXiv-ready**. For Chaos journal submission, items in P1 (document class, figure numbering, overfull hbox) also need attention.

**Estimated effort to reach arXiv-ready state**: 30-45 minutes (primarily author information and keywords).

**Estimated effort to reach Chaos-ready state**: 2-4 hours (document class, figures, additional references, title length optimization for PRL if targeting PRL instead).
