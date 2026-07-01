# Brain-Sub Iteration 11

**执行时间**: 2026-07-01
**上下文**: v10 tarball 就绪, iter 10 遗留问题: Section 1-2 bridge, PBH degeneracy, skewness "iff" claim
**论文**: GW-BacQFT-paper.tex (520 lines, 14 pages PDF, 1.2 MB, 27 refs inline thebibliography)

---

## Iteration 11 Critiques

### Q1: PBH Source Degeneracy — Can the Paper Distinguish PBH from SMBHB?

**风险等级**: MEDIUM

**现状**: 搜索整个 .tex 文件，`pbh`、`primordial black hole`、`dark matter.*GW` 等关键词均无匹配。论文完全未提及 PBH GWB。

**三分法的缺口**: 论文 (第 204-208 行) 列出的源类只有：
1. **SMBHBs**: discrete, LSS-tracing, O(1-10%) anisotropy
2. **Cosmological backgrounds**: effectively continuous, O(10^-5) anisotropy
3. **Cosmic strings**: line-like, "potential anisotropy patterns"

PBH 是一个重要的第三候选者。它们形成离散源（与 SMBHB 类似），同时它们构成暗物质（其各向异性也追踪大尺度结构，振幅可达 O(1-10%) 与 SMBHB 类似）。

**能否仅凭谱指数区分?**
- SMBHB: spectral index gamma ~ 2/3 (gas dynamical friction 主导的演化)
- PBH (暗物质形成 GWB): 在辐射主导时期形成，谱形通常是 gamma ~ -2/3 或 ~0 (取决于形成机制)
- 但论文的谱指数精度为 Dgamma ~ 0.3 (第 47 行)，这正是当前精度局限性的核心论据

**空间各向异性模式**: PBH 和 SMBHB 都追踪 LSS，各向异性模式可能难以仅凭形态学区分。关键差异可能在于空间相关函数中的非高斯成分（PBH 是更稀疏的源）和各向异性的红移依赖性。

**应在 Discussion 中添加什么?**
The following paragraph should be added to Section 6.2 (Limitations), after the existing bullet points:

> \item \textbf{Source-class degeneracies:} Our framework distinguishes SMBHB GWBs from cosmological backgrounds, but additional degeneracies must be considered. Primordial black holes (PBHs) forming dark matter would produce a GWB with Poisson shot noise anisotropy (Raidal et al.\ 2020; Soni et al.\ 2019) that scales as $\mathcal{O}(N_{\rm src}^{-1/2})$, potentially comparable to the SMBHB signal. Both trace the large-scale structure, and their anisotropy patterns may not be distinguishable from SMBHB anisotropy alone. Discrimination would require combining multiple observables: spectral index (SMBHBs produce $\gamma \approx 2/3$, while PBH GWBs may have different spectral indices), anisotropy amplitude at different sky scales, and higher-order statistics. We leave a systematic treatment of multi-source degeneracies to future work.

The paper would also benefit from citing:
- Raidal et al. 2020: ``Primordial black hole as dark matter,'' (review)
- Soni et al. 2019: ``Gravitational waves from primordial black hole dark matter''

These would need to be added to the thebibliography.

---

### Q2: Skewness "If and Only If" Claim

**风险等级**: MEDIUM

**现状**: 第 305-307 行:

```latex
Building on Fujimoto \& Takahashi \cite{Fujimoto:2026} and Mingolla et al.\ \cite{Mingolla:2023}, our framework predicts that the skewness of the HD correlation is non-zero only for discrete sources:
\begin{equation}
\langle\langle \zeta^3 \rangle\rangle \neq 0 \quad \text{if and only if sources are discrete (Poisson)}
\end{equation}
```

**"Only if" 问题的具体分析**:

"Fujimoto:2026" 引用的论文是关于 HD 曲线的 skewness，但即使它的条件是"仅对离散源非零"，它也是针对特定模型假设。论文本身声称的是更强的说法。

具体反例:

1. **Cosmic string loops** (第 47 行列为"cosmological sources"): 单个 string loops 是离散源，它们会产生 discreteness skewness。因此"non-zero skewness $\Rightarrow$ SMBHB"是不成立的。

2. **Phase transition bubbles**: 单个气泡是离散事件，在适当的极限下可能产生非高斯 skewness。

3. **Domain walls**: 虽然通常被归为"cosmological"，但 wall 网络产生的 GW 分布可能有独特的 non-Gaussian 特征。

4. **Cosmological large-scale structure projection**: 即使 GWB 本身是连续的，LSS 投影（通过 SWS effect）在非线性尺度上也可能引入 modest 的非高斯性，尽管这种效应通常很小。

**应该弱化到什么程度?**

建议修改为:

```latex
\item \textbf{Higher-order correlation functions:} Building on Fujimoto \& Takahashi \cite{Fujimoto:2026} and Mingolla et al.\ \cite{Mingolla:2023}, our framework predicts that the skewness of the HD correlation is dominated by the discreteness of the source population. For a Poisson distribution of discrete sources, the skewness is non-zero and scales with the source density. Its sign and magnitude encode the source clustering properties. Non-HD correlation patterns (e.g., monopole, dipole) also provide complementary discrimination channels \cite{Mingolla:2023}.
```

关键修改:
- "non-zero only for" 替换为 "dominated by the discreteness"
- 添加 "For a Poisson distribution" 的限定
- 弱化 to a descriptive statement 而非 proof-level claim

这实际上改变了 claim 的级别——从理论预测 (predicts that) 到框架性观察 (framework predicts that... is dominated by...)。但由于这是在 Discussion/predictions 语境下，这是可以接受的。

**关于 AQFT 框架能否证明这个命题**: 在当前形式下，不能。skewness 是一个统计性质的论断，而 AQFT 框架提供的是代数结构的差异性论断。要将 skewness 纳入 AQFT 框架，需要定义一个 skewness operator 或 higher-point correlation functor，这在论文中没有做。论文引用了 Fujimoto 来做这个 statement 的背书，这是正确的做法，但论文不应暗示这是 AQFT framework 自身的结果。

---

### Q3: Structural Quality Check — Post-v10

#### 3a: Definition 1 与其余部分的术语一致性

**已修复项**: (infty,n)-categories 的 problematic 用法已从 v10 移除。Definition 1 (第 69-75 行) 现在使用 cobordism-based 的描述而不是具体 (infty,n) category。

**Check list**:

- "extended AQFT" 出现在第 33, 51, 59, 63, 70 行 — 这是定义后的合理术语使用
- "extended TQFT" 出现在第 51, 70 行 — 引用 Baez 和 Lurie 是正确的
- "cobordism" 出现在第 54, 70, 74, 86, 89, 96, 125, 361 行 — 从 Definition 1 到 "Detector Cobordism" 的术语链路是连贯的
- Section 2 标题 "Extended Functorial QFT for Gravitational-Wave Detection" — 与定义后的术语一致
- Section 6.2 (Limitations) 第 361 行承认 "Lorentzian cobordism" 尚在发展 — 这是一个好的诚信声明

**结论**: 在 v10 修复 (infty,n) 之后，术语链路是 self-consistent 的。

#### 3b: Section 1 到 Section 2 的过渡问题（iter 10 遗留）

**仍然存在，但没有恶化。**

第 45-49 行 (Introduction) 的四个 bullet points 承诺了物理结果，但第 51-57 行的 transition paragraph 没有填补从物理承诺到抽象框架的鸿沟。然而:

1. 第 59 行的 ``Precision-aware methodology`` 段落提供了一个 "why category theory?" 的动机 — 这不是完美的物理直觉 bridge，但至少回应了 "为什么要用这个框架" 的问题
2. 第 61 行的 ``Bayesian prior`` 段落进一步为抽象框架提供了物理动机
3. 与 iter 10 描述的原始情况相比（完全没有过渡），这两个 methodology 段落是一个显著的改进

**但仍然是潜在的风险点**: gr-qc 读者在 Section 2 开头遇到 "Extended AQFT" 定义时，可能需要回看前面的段落来理解动机。这不是灾难性的，但也不是最好的读者导航。

**如果要做最后一个 quick fix**，可以在 Definition 1 之前（第 63 行之后）添加一个过渡句：

```latex
While the full machinery of extended AQFT may seem abstract, the physical justification is direct: the Hellings--Downs correlation itself depends on the choice of quantum state in the gravitational-wave field, and the algebraic framework makes this dependence precise. The 'extended' aspect — assigning algebras to lower-dimensional submanifolds such as detector worldlines — is motivated by the fact that pulsar timing measures the field directly along worldlines rather than in bulk spatial regions.
```

这个修改的置信度：**中低** — 它是一个建议而不是必须的。

#### 3c: 文献格式一致性

**风险等级**: LOW

27 个 bibitems 格式检查:

- 所有条目统一使用 `LastName:Year` 格式作为 citation key
- 作者姓名格式: `Initials. Surname` (consistent across all entries)
- 标题使用 ``quoted format`` — consistent
- 期刊名称使用 \textit{} — consistent
- 卷号使用 \textbf{} — consistent (all entries with volumes: Math. Phys., Phys. Rev., JCAP, etc.)
- 年份后紧跟 — consistent
- arXiv IDs present for modern entries — consistent
- Pre-2000 arXiv entries correctly use old format (astro-ph/xx, math/xx) where applicable

唯一的小不一致:
- Phinney:2001 (第 389-392 行) 是纯 arXiv，没有正式发表信息。这在 gr-qc 论文中很常见，但在引用标准上略微不统一（其他多数有 journal reference）。对于 gr-qc 来说这是可以接受的。

**结论**: 27 references 的格式是一致的 gr-qc 风格，没有 arXiv  Veterinarians 会标记的问题。

---

### Q4: arXiv Submission Readiness — Post-v10 Final Assessment

#### 积极因素

- **编译**: 0 errors, 14 pages, 1.2 MB PDF
- **tarball**: arxiv-submission-D1-grav-waves-v10.tgz (1.9 MB with tar overhead), 含 tex + 3 图 + PDF
- **许可证**: CC BY 4.0 — 完全合规
- **分类**: gr-qc (primary) + hep-th + astro-ph.CO — 合理
- **元数据**: 标题/作者/摘要/关键词一致
- **参考文献**: 27 inline thebibliography, all properly formatted
- **图表**: 3 figures in correct format (PDF/PNG)
- **Abstract**: 包含 license statement, keywords — 完整

#### arXiv Veterinarians 可能标记的问题

| 潜在问题 | 严重性 | 可能性 |
|----------|--------|--------|
| "Independent Researcher" 作者归属 | LOW | 可能收到验证邮件，但这是 arXiv 允许的 |
| 未使用 .bib file | LOW | gr-qc 中 inline thebibliography 完全可接受 |
| Citation format 非 BibTeX | LOW | 与 journal 格式一致 |
| 无 institutional affiliation | LOW | 可能要求 email 验证，但不是 rejection 理由 |
| CC BY 4.0 声明 | INFO | 这是作者的选择，不是问题 |
| 公式密度较高 | INFO | gr-qc 论文中是常态 |

**总结**: 没有 HIGH 风险或会导致 "send to author" 的问题。

#### arXiv 可能会触发 "sent to author" 的低风险检查

- 未使用 arXiv 的默认 class (IEEEtrans, APS, amsart)。论文使用 article class。这不是问题，但不标准。gr-qc 常用 article + revtex4-2 或 apsrev4-2，但 article class 完全可以。
- 唯一的潜在问题是 --article class 没有 `\thanks` 对 institutional affiliation。作者需要确认邮件验证是 chenglu@protonmail.com。

#### Final Quick Wins? (before submission)

1. **[MEDIUM]** Add PBH degeneracy paragraph to Limitations (约 5-7 行)
2. **[MEDIUM]** Soften skewness "if and only if" to "dominated by discreteness"
3. **[LOW]** Add transitional paragraph between Section 1 and Section 2 (2-3 行)
4. **[LOW]** Add Raidal et al. and Soni et al. references if adding PBH discussion

These are ALL quick to implement (15-20 minutes total editing) and would significantly improve the paper's defensibility against reviewer comments.

However, if the goal is **fast submission**, items 1 and 2 are worth doing because they address reviewer arguments that are highly likely (PBH degeneracy is a standard astrophysics concern, skewness "iff" is a logic flaw). Item 3 is optional.

---

## Iteration 11 Summary Table

| 项 | 风险等级 | v10 前状态 | v10 修复? | iter 11 建议 |
|----|----------|------------|-----------|--------------|
| PBH source degeneracy | **MEDIUM** | 未提及 | 无 | 添加 Limitations paragraph |
| Skewness "iff" claim | **MEDIUM** | 过强的逻辑断言 | 无 | 弱化到 "dominated by discreteness" |
| (infty,n) 不兼容 | **HIGH** | 原始 issue | YES | v10 已修复 |
| Sec 1-2 bridge | **MEDIUM** | 无过渡 | 部分 | 可加 2-3 行过渡句 |
| 参考文献格式 | LOW | — | — | 一致，无需修改 |
| 编译就绪 | LOW | — | — | 0 errors, ready |
| CC BY 4.0 | INFO | — | — | 合规 |
| tarball 完整性 | LOW | — | — | v10 完整 |

---

## Iteration 11 vs Iteration 10 新发现

1. **PBH 问题不是假设性的** — 论文完全没有任何提及，这在 gr-qc 审稿中是几乎必然会被问到的。Soni et al. (2019) 和 Raidal et al. (2020) 的相关文献是直接可用的。PBH GWB 不是 "esoteric"——它是暗物质研究的热点领域，与 PTA 直接相关。

2. **skewness claim 的逻辑问题比 iter 10 更严重** — iter 10 说 "if and only if is too strong"，迭代 11 发现这不仅是 over-statement，还是 **结构性的论证错误**：它将 cosmic string loops 和 phase transition bubbles（它们在论文的 Introduction 被归类为 "cosmological sources"）与 SMBHB 混为一个 "discrete" 类别，但 paper 的整个分析框架是基于 SMBHB vs cosmological 二分的。如果 skewness 也能由 "cosmological discrete sources" 产生，那么 skewness 就不是 SMBHB discriminator。

3. **Definition 1 的修复效果确认** — 通过搜索确认 v10 确实移除了具体的 (infty,n) 使用，现在的 "extended AQFT" 描述是通过 cobordism 概念表达的，与 Baez/Lurie 的 TQFT 框架兼容。这是正确的修复。

4. **arXiv 提交实际上几乎是 100% 就绪的** — 技术上没有任何问题。物理论据的两个 MEDIUM 问题（PBH、skewness）不太可能触发 "send to author"，但会在 peer review 中被质疑。论文的质量足以应付 gr-qc 审稿。

---

## Blind Spots / Uncertainties

1. **Fujimoto:2026 原文条件**: 我没有检查 Fujimoto \& Takahashi 2026 原文中 "skewness iff discrete sources" 的确切声明。可能是他们的条件比论文引用的更强或更弱。这是一个需要核实的关键点。

2. **PBH GWB 的谱指数**: 论文没有包含 PBH 的谱指数 prediction，因此 SKAO 数据的谱指数测量实际上可能区分 SMBHB (gamma ~ 2/3) 和 PBH (gamma ~ -2/3)。如果这个假设是正确的，PBH 退化问题比预期更容易解决。但我没有验证 PBH GW 谱指数的共识值。

3. **Cosmic string loops 作为 "discrete" 源的分类**: 在文献中，cosmic strings 通常不被归类为 "discrete Poisson sources" — 它们被视为一种 "continuous but structured" 的源。如果这个惯例成立，那么 "skewness iff discrete" 可能被接受为 "skewness iff point-like discrete sources"。但这需要澄清。

4. **arXiv 对 gr-qc 论文的具体格式偏好**: 我没有验证 arXiv 对 gr-qc 是否有特殊的 LaTeX class 要求。article class 应该可以，但需要确认。

---

## Next Dispatch: Brain-Sub Iteration 12

**推荐方向**:

1. **核实 Fujimoto:2026 原文的 skewness 条件** — arXiv:2602.01108。这是解决 skewness 问题的关键。

2. **核实 PBH GWB 谱指数和振幅** — Raidal et al. (2020) 和 Soni et al. (2019)。需要定量确认: (a) PBH GWB 谱指数 vs SMBHB, (b) PBH 各向异性振幅范围, (c) PBH 空间分布与 SMBHB 的可区分度。

3. **执行 iter 11 的 low-risk edits**: 强化 skewness claim + 添加 PBH 段落。这两个修改合计约 10 行 LaTeX，可以在 10 分钟内完成，将显著改善论文的审稿韧性。

4. **编译验证 v11** — 应用编辑后运行 pdflatex，确认 0 errors, 页面数不变。

5. **如果决定提交，更新 2-loop/06-decision.md** 为 v11 的 tarball metadata。
