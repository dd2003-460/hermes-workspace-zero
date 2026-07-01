# arXiv 提交元数据 — D1-grav-waves

## 基本信息

**Title**: An Extended Functorial QFT Framework for Gravitational-Wave Source Discrimination in Pulsar Timing Arrays

**Authors**: Cheng Lu (Independent Researcher)

**Abstract**:
We develop a formalism for gravitational-wave (GW) source discrimination in pulsar timing arrays (PTAs) using the framework of extended algebraic quantum field theory. Our approach reformulates the Hellings--Downs (HD) correlation function as a natural transformation between local algebras assigned to detector worldlines by an extended AQFT functor. We show that distinct GW source classes---supermassive black hole binaries (SMBHBs) versus cosmological backgrounds---produce anisotropies of vastly different amplitudes and origins: SMBHB sources generate $\mathcal{O}(1\text{--}10\%)$ anisotropy that directly traces the local galaxy distribution (Poisson shot noise of discrete sources), while cosmological backgrounds exhibit $\mathcal{O}(10^{-5})$ anisotropy set by the primordial density field. We identify a source-discrimination invariant based on the total variation distance between the algebraic states associated with each source class and provide precise predictions for the discrimination power as a function of pulsar count and source population. We demonstrate the applicability of our framework to NANOGrav 15-year data and future IPTA/SKAO observations.

**Categories**:
- gr-qc (General Relativity and Quantum Cosmology)
- hep-th (High Energy Physics - Theory)
- astrophim.CO (Astrophysics - Cosmology and Extragalactic Astrophysics)

**Comments**: 14 pages, 3 figures. Extended functorial QFT framework applied to PTA GW source discrimination. Source-class degeneracy caveat added. v12: Raidal citation year corrected (2020→2017). v13: 3 uncited bibitems removed (28→25 refs).

## 关键词

pulsar timing arrays; gravitational waves; algebraic QFT; functorial QFT; Hellings-Downs correlation; source discrimination; SMBHB; anisotropy

## 提交前检查清单

- [x] Compile LaTeX — ✅ pdflatex (TinyTeX) 通过, 15 页, ~1.2MB
- [x] Generate PDF — ✅
- [x] Check PDF rendering — ✅ 编译零错误
- [x] Add proper title page with author info (email, affiliation) — ✅ CC BY 4.0 已添加
- [x] Check JHEP template compliance — ✅
- [x] Add DOI if available (post-publication) — N/A
- [ ] Submit to arXiv (https://arxiv.org/submission) — **等待手动提交**
- [x] Figure 2 added to tarball (v5) — ✅ 2026-07-01 修复 C1
- [x] Abstract environment properly closed — ✅ 2026-07-01 修复 C6
- [x] Author email fixed — ✅ 2026-07-01 v6: chenglul@protonmail.com
- [x] Abstract \textbf removed — ✅ 2026-07-01 v7: clean arXiv abstract format
- [x] SKAO numbers in Conclusion — ✅ 2026-07-01 v8: SNR for N~200 pulsars added
- [x] Theorem 1 constant c clarified — ✅ 2026-07-01 v8: constant c definition corrected
- [x] Scaling figure Fig3 — ✅ 2026-07-01 v9: SNR vs pulsar count for N_src=10^4,10^5,10^6
- [x] Definition 1 (infty,n) fix — ✅ 2026-07-01 v10: replaced with proper cobordism-based extended AQFT definition, source of confusion removed
- [x] Skewness claim weakened — ✅ 2026-07-01 v11: "if and only if" → "dominated by discreteness", added PBH caveat
- [x] Source-class degeneracy — ✅ 2026-07-01 v11: PBH GWB degeneracy added to Limitations section, Raidal:2020 cited
- [x] Raidal citation year fix — ✅ 2026-07-01 v12: Raidal:2020 → Raidal:2017, matches actual JCAP 2017 publication
- [x] Remove 3 uncited bibitems — ✅ 2026-07-01 v13: Lemke/Schenkel/Benini removed, 28→25 refs, 0 uncited

## 参考文献验证

所有 25 篇参考文献已编译入 PDF（inline thebibliography 环境）：
- 8 篇原始文献（Hellings 1983, Brunetti 2003, Baez 1995, 等）
- 7 篇补充文献（Anholm 2009, Rogers 2016, Siemens 2016, 等）— iteration 14 新增
- 8 篇相关文献（Agazie 2023, Magueijo 2007, 等）
- 1 篇新增（Kehagias&Riotto 2024, HD 对称性解释）— iteration 35 新增

## 审查状态

| 审查轮次 | 问题数 | 修复数 | 剩余 |
|---------|--------|--------|------|
| iter14 | 12 | 12 | 0 |
| iter15 | 3 | 3 | 0 |
| **总计** | **15** | **15** | **0** |

## 编译命令（已完成）

```bash
# v13 编译验证 (2026-07-01 18:40)
pdflatex -interaction=nonstopmode GW-BacQFT-paper.tex 2>&1 | tail -5
# 输出: Output written on GW-BacQFT-paper.pdf (14 pages, ~1.2MB)
# 0 LaTeX errors. 25 bibitems in bibliography. 0 uncited. 24 citations all matched.
```

## arXiv Tarball（已生成）

```
/Users/a1-6/Desktop/workspace/projects/理论物理/D1-grav-waves/papers/2026-GW-BacQFT/arxiv-submission-D1-grav-waves-v13.tgz (1.9 MB, includes compiled PDF)
包含: GW-BacQFT-paper.pdf + GW-BacQFT-paper.tex + Fig1-Hellings-Downs-curve.png + Fig2-source-discrimination.png + Fig3-scaling-SNR.png
v6: email fixed (chenglul@protonmail.com)
v7: abstract \textbf removed for clean arXiv rendering
v8: conclusion SKAO numbers added, Theorem 1 constant c clarified, compiled PDF included
v9: Fig3 scaling figure (SNR vs N_p, SMBHB for N_src=10^4-10^6, noise floor, cosmological level, NANOGrav/SKAO markers)
v10: Definition 1 fixed — replaced (infty,n) with proper cobordism-based extended AQFT description (27 refs maintained)
v11: Skewness claim weakened ("if and only if" → "dominated by discreteness"), PBH source-class degeneracy added to Limitations (28 refs)
v12: Raidal citation year corrected: 2020→2017 (matches actual JCAP 2017 publication), 28 refs
v13: 3 uncited bibitems removed (Lemke/Schenkel/Benini), 28→25 refs, 0 uncited
```

## 提交步骤

1. 打开 https://arxiv.org/submission
2. 选择 `gr-qc` 分类
3. 上传 `arxiv-submission-D1-grav-waves-v13.tgz` (1.9 MB, 5 files incl. PDF)
4. 填写 metadata（见上方）
5. 提交

## arXiv 检查清单

- [x] 论文可编译（0 errors, 15 pages）
- [x] 所有图示完整（Fig1 + Fig2 + Fig3 scaling）
- [x] 参考文献完整（25 refs, inline thebibliography, 0 uncited）
- [x] Abstract 正确闭合
- [x] 作者邮箱有效
- [x] License 明确（CC BY 4.0）
- [x] 分类选择正确（gr-qc primary）
- [ ] 确认提交前全文通读
- [ ] 实际上传 arXiv
