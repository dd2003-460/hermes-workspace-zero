# D1-academic-AI/ — 学术研究项目索引

**创建**：2026-05-03（CLAUDE.md 原则重构）
**最后更新**：2026-05-13（iteration 94，DistCat arXiv v3 tarball 验证通过 11/11 checklist，D40 arXiv-ready v2，BayesFrame JCR 论文 iteration 94 参考文献修复，权限配置修复 bypassPermissions + 通配符 Read/Write/Edit/Bash(*)）

## 理论体系

| 理论编号 | 名称 | 路径 |
|----------|------|------|
| D30 | [详见 theories/INDEX.md] | theories/ |
| D40 | AI 精度-可访问性权衡 | papers/D40-ai-market-precision-tradeoff-paper-draft.md |
| D52 | Van der Pol 非线性振荡重构 | theories/chimera-dynamics/ |
| D44 | Tautology 理论 | theories/ |
| ... | [详见 theories/INDEX.md] | theories/ |

## 实验与框架

| 内容 | 路径 |
|------|------|
| Chimera 检测与循环使用 | chimera_lab/ |
| WKB 曲率熵 | wkb_curvature_entropy.py |
| Bayesian 感知推理框架 (iteration 134+, 6 模块 491 行, 27 导出) | bayesian-frame/ |
| BayesFrame JCR 论文 (iteration 94, 9p/857K, |sin(4θ)| 为核心发现) | bayesian-frame/JCR-paper-PLOS.tex |
| D40 实验代码与数据 | chimera_lab/d40-precision-tradeoff-simulation.py, chimera_lab/d40-results.json |

## 文档

| 内容 | 路径 |
|------|------|
| 统一框架（定理 1-10） | UNIFIED-FRAMEWORK.md |
| 跨理论综合分析 | papers/cross-theory-synthesis.md |
| D16+D24 联合推导：语义距离统一理论 | papers/D16-D24-joint-framework.md |
| D16+D24 + D1-grav-waves 方法论对比 | papers/D16-D24-D1-comparison.md |
| **$\mathbf{DistCat}$ 统一框架**（2-范畴距离导出） | papers/DISTCAT-framework.md |
| bayesian-frame 纳入 $\mathbf{DistCat}$ | papers/DISTCAT-bayesian-integration.md |
| D26 共振距离导出 | papers/DISTCAT-D26-resonance.md |
| **EMRI 混沌 + D26 共振映射**（9 个命题+3 预测+Paper II 验证） | papers/EMRI-D26-resonance-mapping.md |
| **DistCat 统一框架**（9 节~30KB，5 个特例整合，定理 1-10） | papers/DISTCAT-unified-framework.md |
| **DistCat 2-范畴严格证明**（12 项公理验证，EMRI 作为 0-object） | papers/DISTCAT-EMRI-2category-proof.md |
| **D1 vs EMRI 定量等价**（不同普适类分析，指数不可通约） | memory/72-d1-emri-quantitative-comparison.md |
| **最优距离导出**（Fisher-Rao universality theorem，5 个特例统一） | papers/DISTCAT-optimal-distance-export.md |
| **参数距离修复**（Iteration 75：η → d_param，Prop 4.8 d_param ≡ Γ） | memory/75-param-distance-gap-fix.md |
| **第四轮副脑审查修复**（Iteration 76：Prop 4.8 紧域，Prop 4.7 commutative inequality，Thm 5.2 fixed r_s） | memory/76-subbrain-review-round4-fix.md |
| **深层范畴问题：C_EMRI 离散性**（Iteration 77/78：Round 5 审查发现 vacuity，需决定 reformulate） | memory/77-subbrain-review-round5-analysis.md |
| **深层范畴问题续**（Iteration 78：C_EMRI 离散性证明，三条出路评估） | memory/78-deep-categorical-discreteness.md |
| **Round 7/8 审查修复汇总** | memory/79-distcat-final-limitation-fix.md + memory/80-round7-fix.md + memory/81-round8-verify-fix.md |
| **arXiv 工具链策略** | memory/82-arxiv-tooling-strategy.md |
| **最终提交状态** | memory/final-submission-status.md |
| arXiv 提交包 (LaTeX + supp PDFs) | arxiv-ready/DISTCAT-arxiv-submission-v3.tar.gz (867K) |
| BibTeX | DISTCAT-references.bib (12 refs) |
| 探索记录 | memory/ |
| 任务状态 | tasks/D1-academic-AI-tasks.md |
| 单循环状态 | tasks/single_loop_state.json |

---

*按 CLAUDE.md 红线 0 原则：INDEX.md 只描述下一层有哪些项目*
