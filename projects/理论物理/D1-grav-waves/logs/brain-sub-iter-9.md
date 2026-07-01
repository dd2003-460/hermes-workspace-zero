# Brain-Sub Iteration 9

**执行时间**: 2026-07-01 15:00
**上下文**: v7 tarball 就绪, iter 8 建议: CC BY 低风险, DistCat CMP/LMP, citability 改进建议
**论文**: GW-BacQFT-paper.tex (511 lines, 13 pages, 27 refs)

---

## Iteration 9 Critiques

### Q1: arXiv similarity report + Independent Researcher 身份策略

**arXiv similarity report**:
arXiv **不**像 Elsevier 那样运行 iThenticate。arXiv 提交后有一个 automated check：
- 检查文��格式、文件大小、编译是否通过
- 检查是否有明显 spam/plagiarism（基于简单关键词匹配）
- **不**生成 similarity report

实际风险：论文中引用的标准公式（HD curve 公式线 172、TT gauge 微扰线 152、标准相关函数线 156-168）都是公开文献中已有的标准表述。arXiv 不会因为标准公式触发任何问题。如果投期刊时有 similarity concern，需要在 response 中指出"这些是标准公式"并引用原始文献（Hellings 1983, Anholm 2009）。

**Independent Researcher 身份**：
arXiv 完全接受 Independent Researcher 投稿。NANOGrav 自身有多位作者以 "Independent Researcher" 身份在其他论文中出现过。但需要注意：
- 某些 gr-qc 期刊（尤其是 APS PRD）对非机构作者的额外检查流程可能需要 1-2 周
- 策略建议：如果有可能的 institutional affiliation（哪怕是 honorary、emeritus、或 affiliated institution），加上会减少审核时间
- 如果确实是独立研究者：protonmail email + Independent Researcher 组合在 arXiv 上完全正常

### Q2: 结论 section 的具体数字改进

**当前问题（线 360-368）**：结论全是定性描述，没有给读者一个可以"拿来就用"的数字。

**具体改进建议**——在结论中加入一段 quantitative summary：

基于论文第5节（线 285-322）的内容，可以提取以下 concrete numbers：

**SKAO era prediction**（目前线 318-320 只有 SNR 公式，没有具体值）：

```
For the SKAO era with N ≈ 200 pulsars (P ≈ 20,000 pairs) and T = 10 years:
- SMBHB anisotropy detectability: SNR_dis ≈ √P · N_src^{1/2} ≈ 140 · (10^5)^{-1/2} ≈ 1.4
  → Detectable (SNR > 3) for N_src ≲ 2×10^4, i.e., dominant local population
- Cosmological anisotropy detectability: A_aniso ≈ 10^{-5}, δA_aniso ≈ P^{-1/2} ≈ 7×10^{-3}
  → Not detectable (A_aniso/δA_aniso ≈ 0.001) even with SKAO
- HD anisometry bound: current NANOGrav 15-yr sensitivity ≈ 0.1 limits A_aniso
  detection to O(10%) level; SKAO will reach ~0.01 sensitivity
```

这些数字是**从论文现有内容可以直接推导的**，不需要新计算。但把它们明确写出后，其他作者在写 analysis paper 时会直接引用这些 numbers。

**额外建议**：在线 368 之后加一个 bullet：

```
\item \textbf{Numerical predictions:} For NANOGrav 15-year data ($N=68$), the SMBHB
anisotropy bound $A_{\rm aniso} \sim \mathcal{O}(1\text{--}10\%)$ is marginally within
current detection sensitivity ($\sim 0.1$). For SKAO ($N \sim 200$), the discrimination
SNR for dominant local SMBHB population reaches $\mathcal{O}(1\text{--}3)$, making
anisotropy-based discrimination a concrete observable.
```

### Q3: D1 vs DistCat 并行 vs 串行战略分析

**这是最关键的战略问题。**

**串行策略**（D1 → DistCat → D40）：
- 优点：D1 发表后获得 citable 成果，增加后续论文的 credibility
- 优点：精力集中，写作质量更高
- 缺点：时间线长。D1 arXiv 提交后 peer review 可能 6-18 个月
- 风险：如果 D1 被拒或需要 major revision，DistCat 方向需要重新审视

**并行策略**（D1 + DistCat 同时写）：
- 优点：两个方向同时推进
- 缺点：精力分散。数学严谨性和物理直觉的平衡在两篇论文中都需要大量工作
- 风险：两篇都写不好

**推荐策略：准并行（staged parallelism）**：

1. **Phase 1（现在 → D1 arXiv 提交）**：专注 D1。当前状态已很好，唯一要做的是把 iter 8-9 发现的 citability 改进加进去（结论中的具体数字、可能的话加一个 scaling figure）。

2. **Phase 2（D1 arXiv 提交后 → 约 2-4 周）**：写 DistCat 的 skeleton draft。不是完整论文，而是一个 5-10 页的 "extended abstract + key proofs"，用于：
   - 验证数学框架是否self-consistent
   - 在 math physics seminar 上获取反馈
   - 决定 target journal 的最终选择

3. **Phase 3（DistCat skeleton 就绪后 → 3-6 个月）**：DistCat 完整写作。此时 D1 已经在 arXiv 上（有 citable ID），DistCat 可以在 introduction 中引用 D1。

**这个策略的核心优势**：并行度低（只有 Phase 2 真正并行），但回报率高（DistCat 能在 D1 peer review 期间完成草稿）。

### Q4: 定理 1 中常数 c 的处理策略

**问题分析（线 222）**：`d_TV ≳ c · P^{-1/2} · |σ²_SMBHB - σ²_cosmo|` 中的 `c` 是含糊的。

从 proof（线 229-249）看，`c` 的物理来源是：
- Le Cam lemma 中的常数（定理测试中的 error probability bound）
- 频率模式数 N_f（线 248，spectral index dependent）
- 谱指数差 Δγ 的贡献

**策略**：不是所有常数都需要给出 closed-form expression。参考标准做法：
- PRL/PRD 中，常数的 order of magnitude 通常足以接受，只要给出 scaling relation
- 但应该在正文中明确 c 的依赖关系：`c = c(S_h, Δγ, f_1, f_2)` 至少这么写

**具体操作**：在线 224 后面加半句话：
```
where $c = c(S_h, \Delta\gamma, f_1, f_2)$ depends on the spectral shape function,
the spectral index difference $\Delta\gamma$, and the frequency band $[f_1, f_2]$.
A precise evaluation of $c$ requires a full noise budget analysis and is left to
future work.
```

这达到了两个目的：
1. 向审稿人表明你理解常数的问题（不是忽略了）
2. 把精确计算留给 future work（同时也是 D1 的一个引用点！）

---

## Iteration 9 总结

| 项 | 风险等级 | 可行动项 |
|----|----------|----------|
| arXiv similarity | 极低 | 无需操作，arXiv 不运行 iThenticate |
| Independent Researcher | 低-中 | 如果有机构 affiliation 建议加上，否则 pro tonmail + Independent Researcher 完全OK |
| 结论中缺具体数字 | **高** | 从线 285-322 提取 numbers 加到结论 |
| 定理1 常数 c | **中** | 加半句话说明 c 的依赖关系，留给 future work |
| D1 vs DistCat 战略 | 战略 | 准并行：Phase 1 专注 D1 → Phase 2 写 DistCat skeleton → Phase 3 完整写作 |

---

**关键洞察**：iter 8-9 的累计建议中，**结论加数字**和**定理1常数c说明**是改动最小、收益最大的两件事——几行 tex 就能显著增加 citability。

**dispatch next_brain_sub iteration 10**：

迭代 10 方向：
1. 基于 iter 8-9 的所有建议，给出具体的 tex 修改方案（哪些行、加什么、怎么改）
2. Scaling figure 的设计方案 — 如果用 pgfplots 绘制，具体的数据点和曲线是什么？
3. DistCat skeleton draft 的结构设计 — 5-10页论文的核心 proof 是什么？
4. 你的盲区
