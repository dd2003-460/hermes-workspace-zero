# Brain-Sub Iteration 8

**执行时间**: 2026-07-01 14:30
**上下文**: v7 tarball 就绪, 2-loop complete, ready_for_submission
**论文**: GW-BacQFT-paper.tex (511 lines, 13 pages, 27 refs)

---

## Iteration 8 Critiques

### Q1: CC BY 4.0 冲突的实际解决方案

**问题**: 论文摘要中声明了 CC BY 4.0，但大多数 gr-qc 期刊（PRL, PRD, JCAP）要求投稿时版权归出版社。这是否构成真正冲突？

**回答**: 实际冲突程度比 B4 担心的低。arXiv 预印本用 CC BY 4.0 是当前标准做法——NANOGrav 15-year 数据论文 (Agazie:2023) 本身就是在 arXiv 上以 CC BY 4.0 发布的。arXiv 投稿不需要作者选择 license（arXiv 只做技术性检查），license 声明是作者自述。

**实际操作**：arXiv 作者通常怎么做？
- 绝大多数 gr-qc 作者在 arXiv 上放 CC BY 4.0，因为这是 NSF/DOE 资助者的 open access 要求
- 期刊投稿时，出版社要求的是**投稿后**的版本版权，不是 arXiv 预印本的版权
- 大多数出版社（APS, IOP, Springer）明确允许作者将 arXiv 预印本留在 arXiv 上（即使正式版本是 copyrighted）
- **唯一需要注意的**：如果作者打算投 Elsevier 的期刊（如 Nuclear Physics B），他们的政策更严格；但本文目标分类是 gr-qc（APS PRD 或 IOP JCAP），这两家对 arXiv 预印本都很友好

**结论**：CC BY 4.0 不会阻塞投稿。但如果用户想完全避免任何潜在问题，可以在提交 arXiv 之前把摘要中的 license 声明去掉，改为仅在正文末尾保留。这是零风险做法。

### Q2: DistCat 的具体数学内容规划

**问题**: math.CT 分类论文需要什么深度？

**回答**：基于论文现有内容的分析：

论文已经在下面这些点上有数学基础：
- 线 69-73: `F: Loc_M^{ext} → C*Alg^{(\infty, n)}` 的 functor 定义 — 这是 extended functorial QFT 的核心
- 线 93: 关联函数作为 natural transformation `ι_{12}` — 这是 natural transformation 的具体实现
- 线 134: Tomita-Takesaki modular theory 提及 — 这是 AQFT 的深层数学

DistCat 论文的**最低可行深度**：
1. **Lurie 的 cobordism hypothesis** — 论文用了 cobordism 语言（detector cobordism, 线 88），但没有形式化。DistCat 需要把 detector cobordism 嵌入到 cobordism hypothesis 的框架中
2. **Schenkel 2023 的 Lorentzian bordism** — 论文引用了它（线 353），但只是作为 limitation。DistCat 应该正面回答：Lorentzian bordism 的 AQFT 如何支持 PTA 场景的具体计算？
3. **AQFT 中的 state space 几何** — 论文用 total variation distance 做 discrimination（定理 1），但 TV distance 在 infinite-dimensional C*-algebras 上的计算缺少 rigor。DistCat 可以聚焦在 quasifree states 的 special case 上

**推荐深度**：不要试图 build 一个完整的 math.CT 论文。聚焦在一个具体命题：把 HD correlation 的 functorial derivation 扩展到**定量**的 anisotropy 预测。这需要在数学上：
- 定义 `Loc_M^{ext}` 中 detector worldline subobjects 的 precise category
- 给出 `C*Alg^{(\infty, n)}` 中 total variation distance 的 C*-algebraic definition
- 证明 discrimination bound 在 C*-algebra 语言中的精确形式

**这不是一个纯数学论文**。它的贡献在于展示 category theory 语言如何让物理计算更精确。target journal 应该是 `Communications in Mathematical Physics` 或 `Letters in Mathematical Physics`，不是 pure math journals。

### Q3: D1-grav-waves 在 gr-qc 社区的 citability

**问题**: 是否有可以改进的地方来提高引用率？

**基于实际论文内容的分析**：

**优势**：
- NANOGrav 15-year 数据是 hot topic（2023 年 Discovery paper 已被引 ~200 次）
- HD anisotropy 是当前 PTA 分析的前沿（Grimm:2025, Isi:2024 都是最近的论文）
- SMBHB vs cosmological 的 anisotropy 幅度差异（1-10% vs 10^{-5}）是一个清晰、可检验的 prediction

**需要改进的地方**：

1. **结论 section（线 360-368）缺少 concrete numbers 用于 SKAO**。论文提到 "SKAO era (N ~ 200 pulsars)" 但没有给出可检验的具体 prediction。gr-qc 社区的引用往往来自**其他作者用到你的 number**。建议在结论中加入：
   - SKAO 时期对 SMBHB anisotropy 的 detection SNR 数值
   - HD anisometry bound 的具体公式（线 287-292 只有 O(·) 符号）

2. **缺乏与现有 PTA 分析 software 的连接**。NANOGrav 用 Tempo/TempoNest，IPTA 用 enterprise framework。如果论文提到 "我们的 anisotropy parameter 可以直接嵌入到 enterprise 的 Bayesian inference 中"，会大幅增加实用性。

3. **引言中 too much category theory jargon**。gr-qc 领域的读者可能不熟悉 AQFT/cobordism。建议在引言前两段中更清楚地陈述**物理结果**，而不是 functor 定义。category theory 应该是工具，不是卖���。

4. **缺少一个 summary figure**。论文只有两个 figure：Hellings-Downs 曲线和 source discrimination 概念图。增加一个 figure 显示 SMBHB vs cosmological anisotropy 幅度随频率/ pulsar count 的 scaling，会极大增加 citability——其他论文的 "compare to our result" 场景会引用这个 scaling。

### Q4: 你的盲区在哪里？

**我的盲区**：

1. **arXiv 的 similarity report**。我不确定 arXiv 投稿后是否自动生成 similarity report（与 iThenticate 对比）。如果生成，CC BY 4.0 声明和标准 PTA review article 中的通用表述是否可能触发 false positive？这是一个实际的提交风险。

2. **作者身份认定**。"Independent Researcher" 在学术系统中可能遇到问题——某些期刊对 independent author 的审核更严格。是否有 affiliation 可以补充？即使是非挂名的 institutional affiliation（比如 "Self-funded" 或某个 online institution）。

3. **bib 条目完整性**。27 条参考文献中，Baez:1995, Lurie:2009, Phinney:2001 都是 arXiv preprints（没有正式 published journal）。这不影响 arXiv 提交，但在 peer review 中可能被问到：是否有正式出版的版本可以引用？

4. **理论声明的数学 rigor**。定理 1 中的 TV distance bound（线 222）的 `c` 常数是含糊的。物理审稿人可能不介意（QFT 论文中常数不精确很常见），但如果投更数学的 journal，这是致命的。需要事先确定 target journal 的数学严格度期望。

5. **DistCat 和 D1 的时间规划**。DistCat 是单独的数学论文，意味着作者要同时推进两个写作项目。我的盲区是：作者的时间和精力是否足够并行推进？还是应该等 D1 发表后再启动 DistCat？这是一个战略决策，不是技术问题。

---

## Iteration 8 总结

| 项 | 风险等级 | 可行动项 |
|----|----------|----------|
| CC BY 4.0 | 低 | 可选：移除摘要中 license 行，放正文末尾 |
| DistCat 深度 | 信息 | 聚焦 AQFT + cobordism 的定量化，target CMP/LMP |
| Citability 改进 | 中 | 结论中加具体 numbers；加一个 scaling figure |
| arXiv similarity | 未知 | 需要调研 arXiv 的 similarity report 政策 |
| Independent Researcher | 低 | 可接受，但可能有额外审核 |
| 定理 1 的常数 c | 中 | 定义 c 的物理含义或在正文中给 bound |

**盲区**：战略层面——D1 和 DistCat 是否应该并行？作者精力有限，并行的风险值得评估。

---

**dispatch next_brain_sub iteration 9**：

迭代 9 方向：
1. arXiv similarity report 风险分析 + Independent Researcher 策略
2. 结论 section 的具体数字改进方案（SKAO prediction）
3. D1 vs DistCat 的并行 vs 串行战略分析
4. 你的盲区在哪里？
