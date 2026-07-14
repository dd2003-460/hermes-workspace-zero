**最后更新**: 2026-07-14（D1-grav-waves RALPH Restart — P2-3/P2-4/P3 全部完成，51页PDF编译通过）

---

## ✅ 已完成

### 全局基础设施
- loop/1loop.md + loop/2loop.md — 精简版规划/执行循环（替代旧 6 阶段结构）
- loop/1-loop-prompts/ + loop/2-loop-prompts/ — 步骤化 AI prompt（4+1 prompt）
- ralph-loop.global.md — 已更新引用精简版路径
- CLAUDE.md — 全局 AGENTS.md（含成璐数字分身原则）
- CLAUDE.md — 项目级 grav-waves CLAUDE.md

### D1-grav-waves 历史（iter1-103 已归档）
- loop/archive-iter1-103/ — 所有1-loop/2-loop本地产出
- paper-archive/main-paper-v17.tex — 最终论文版本（含|cos_nu| bug warning）
- memory/ + note/ — 保留所有探索记录和P0-P5理解笔记

---

## 🔴 当前 Focus — D1-grav-waves RALPH Restart

### P0: 清理与重置
| 任务 | 状态 | 说明 |
|------|------|------|
| P0-1: 归档 loop/1-loop/2-loop | ✅ 完成 | → archive-iter1-103/ |
| P0-2: 归档 paper v17 | ✅ 完成 | → paper-archive/ |
| P0-3: 重置 ralph-loop.local.md | ✅ 完成 | iteration=1, loop_phase=idle |
| P0-4: 更新 TASKS.md | ✅ 完成 | — |

### P0.5: RALPH Restart — 1-loop 完成
| 任务 | 状态 | 说明 |
|------|------|------|
| 02-目标澄清 (restart) | ✅ 完成 | 4 目标: O1-04 |
| 03-任务分解 (restart) | ✅ 完成 | P1-P4, 依赖图 |
| 04-信息搜集 (restart) | ✅ 完成 | 完整代码库存扫描 |
| 05-综合收敛 | ✅ 完成 | confidence 0.90, 进入 2-loop |
| 06-决策 | ✅ 完成 | ENTER 2-LOOP |

### P1: 代码去重与模块化合并
| 任务 | 状态 | 说明 |
|------|------|------|
| P1-1: 创建 core/ 共享模块 | ⏳ 待开始 | olc_transfer_function, antenna_patterns, compute_orf_two_arm |
| P1-2: 修改 script 09/04/10/12 import | ⏳ 待开始 | 从 core/ 导入 |
| P1-3: 统一 E-variable 实现 | ⏳ 待开始 | script 11/10/12 三个版本合并 |

### P2: Chiral ORF 数值修正
| 任务 | 状态 | 说明 |
|------|------|------|
| P2-0: 偏振基底替换对复变函数解法的影响分析 | ✅ 完成 | 关键中间要求，写入 loop/2-loop/ |
| P2-1: 重新计算所有 chiral ORF 数值 | ✅ 完成 | 2-loop/01-预检已完成，脚本运行通过 |
| P2-2: 解决 v17 LISA×Taiji 500x 差异 | ✅ 完成 | v17 之谜已破解：-7.75e-3 是单天区值(θ≈28°, φ≈89-90°) |
| P2-3: 精确单天区匹配验证 | ✅ 完成 | θ=36.51°, φ=82.58°, 0.02% gap accepted |
| P2-4: 生成正确的结果表格和图表 | ✅ 完成 | 5 figures + 3 LaTeX tables generated |

### P3: 论文 v18 更新
| 任务 | 状态 | 说明 |
|------|------|------|
| P3-1: 基于修正数值更新 paper main tex | ✅ 完成 | Section 3.5.6 数值精度提升至 6 位以上，新增结论 (7) |
| P3-2: 更新理论基础章节 | ✅ 完成 | 7.2.2 手征引力波探测已更新，引用精确匹配结果 |
| P3-3: 添加 bug 修正说明 | ✅ 完成 | 已在文中保留 |
| P3-4: 编译验证 | ✅ 完成 | xelatex 51页，无错误 |

### P4: 验证测试加固
| 任务 | 状态 | 说明 |
|------|------|------|
| P4-1: coplanar Γ^V = 0 测试 | ✅ 已验证 | iter103 完成 |
| P4-2: helicity flip 对称性测试 | ✅ 已验证 | iter80/103 完成 |
| P4-3: P^V 严格形式等价性测试 | ✅ 已验证 | iter102 完成 |
| P4-4: Nishizawa 2009 交叉验证 | ✅ 已解决 | Nishizawa 非手征参考文献；Omiya-Seto (2107.12001) 已完成跨验证 (0.95 置信度，7/7 通过) |

---

## 🆕 新项目 — 流程分解（loop-prompt-engineering）

### D1-loop-prompt-engineering：1-loop/2-loop 阶段精确指令化
| 任务 | 状态 | 说明 |
|------|------|------|
| 精简版 1loop/2loop 单文档 | ✅ 完成 | loop/1loop.md + loop/2loop.md |
| 步骤化 prompt（4+1） | ✅ 完成 | loop/1-loop-prompts/ (信息搜集/分解/执行/验证) + loop/2-loop-prompts/ (预检) |
| ralph-loop.global.md 更新 | ✅ 完成 | 引用路径已更新 |
| grav-waves CLAUDE.md 更新 | ✅ 完成 | 引用精简版结构 |

---

## 阻塞项
- MITM SSL 拦截 — 影响 arXiv 提交
- 作者确认 — 影响论文提交

---

## 项目任务索引

| 项目 | 任务文件 | 当前状态 |
|------|----------|----------|
| D1-loop-prompt-engineering | tasks/TASKS.md | ⏳ 新建 — 1-loop/2-loop 阶段精确指令化 |
| D1-grav-waves | tasks/TASKS.md | 🟡 RALPH iter13 reset，待新任务 |
| D1-persona-align | tasks/TASKS.md | T1-T47 完成 |
| D1-academic-AI | — | DistCat + Chimera + EMRI 就绪 |
| D1-academic (BayesFrame) | — | JCR 论文 arXiv 就绪 |
| D1-anyon-hawking | — | arXiv-ready |
| D1-aging-economics | — | Phase 0-7 完成 |
| D1-goal-investigation | — | Agent 行为研究中 |
| adsl-spin-connection | — | Phase 2 完成，待推进 BTZ pole-skipping |

---

*任务状态以各项目 tasks/ 目录为准。全局 TASKS.md 只保留高层摘要。*
