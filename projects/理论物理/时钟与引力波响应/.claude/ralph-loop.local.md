---
project: D1-grav-waves (时钟与引力波响应)
iteration: 8 (IN PROGRESS — P0+P2 complete, P1 reviewed/analyzed, paper v15 compiled)
iteration: 3 (COMPLETE)
iteration: 5 (COMPLETE — 2-loop all 6 stages done)
iteration: 7 (COMPLETE — 2-loop all 6 stages done)
iteration: 6 (1-loop COMPLETE, 2-loop/01 paper update COMPLETE)
iteration: 6 (2-loop ALL 6 stages done)
loop_phase: idle
Iteration 7 status: 1-loop + 2-loop ALL 6 STAGES COMPLETE (conf=0.82)
Iteration 8 status: P0 = χ_orb resolved (memory/15), P2 = paper v14 compiled (49 pages, 0 errors)
next_round: P1 = 三角形 3 卫星 OLC 手征 ORF 物理分析 + 深度非共面构型 (sub-brain critique pending review)
started_at: "2026-07-01"
last_completed_at: "2026-07-06"
last_action: P0 = Orlando deep analysis + memory/15; P2 = paper v14 with new subsection 3.5.6 + arXiv v14 package
last_outcome: 36x discrepancy resolved. Paper v14 (49 pages) includes new subsection 3.5.6 "手征 ORF 的归一化约定与 Orlando (2021) 的比较" citing Orlando JCAP 2022 arXiv:2011.07059. arXiv v14 submission package at paper/teX-submit/arXiv-submission-v14.zip (531KB).
last_insight: χ_orb ≈ 0.17 for maximally chiral signal is a "regression to the mean" effect: R^I is ~10× stronger than R^V → Ω^I is much better constrained → best-fit χ = Ω^V/Ω^I < true χ = 1. Three normalizations: (1) our norm_V (E-variable CW sum, =1.0 by construction), (2) Orlando's raw R^V/R^I (~0.06-0.12), (3) Orlando's χ_orb Fisher best-fit (0.17).

# RALPH Loop 本地状态 — D1-grav-waves

## 当前阶段
`1-loop/06-决策` (Iteration 5 完成) → 下一轮进入 2-loop

## 已完成阶段

### 1-loop（规划 Iteration 3）— 全部完成
| 阶段 | 本地文件 | 状态 | 核心产出 |
|------|----------|------|---------|
| 01-任务澄清 | loop/1-loop/01-任务澄清.md | ✅ | 混合网络分析任务定义 |
| 02-目标澄清 | loop/1-loop/02-目标澄清.md | ✅ | 阶段目标 + 判定标准 |
| 03-任务分解 | loop/1-loop/03-任务分解.md | ✅ | M1-M6 子任务 + DAG |
| 04-信息搜集 | loop/1-loop/04-信息搜集.md | ✅ | 信息源 + 工具 + 洞察 |
| 05-完备核验 | loop/1-loop/05-完备核验.md | ✅ | Gap分析 + 置信度表 (target 0.80) |
| 06-决策 | loop/1-loop/06-决策.md | ✅ | enter_2loop + 核心科学结论 |

### 1-loop（规划 Iteration 5：手征 ORF 求解器验证）— 全部完成
| 阶段 | 本地文件 | 状态 | 核心产出 |
|------|----------|------|---------|
| 01-任务澄清 | loop/1-loop/01-任务澄清.md | ✅ | 方向A：填补7.2.2节手征空白 |
| 02-目标澄清 | loop/1-loop/02-目标澄清.md | ✅ | 8项判定标准，3项硬约束 |
| 03-任务分解 | loop/1-loop/03-任务分解.md | ✅ | M1-M5 DAG，P0=M1(测试)+M3(扫描) |
| 04-信息搜集 | loop/1-loop/04-信息搜集.md | ✅ | 7个信息源，理论覆盖充分 |
| 05-完备核验 | loop/1-loop/05-完备核验.md | ✅ | Gap分析 + 置信度 0.71 |
| 06-决策 | loop/1-loop/06-决策-Iteration5.md | ✅ | enter_2loop + P0=补充断言 |

### 2-loop（执行 Iteration 5 手征 ORF）— all completed
| 阶段 | 本地文件 | 状态 |
|------|----------|------|
| 01-pre-check | loop/2-loop/01-pre-check.md | ✅ completed |
| 02-backup | loop/2-loop/02-backup.md | ✅ completed (MD5: a57e18ff) |
| 03-execute | loop/2-loop/03-execute.md | ✅ completed — test assertions + code bugs + paper fixed |
| 04-verify | loop/2-loop/04-verify.md | ✅ completed — all 8 checks PASS (conf=1.0) |
| 05-confidence | loop/2-loop/05-confidence.md | ✅ completed (conf=0.88) |
| 06-decision | loop/2-loop/06-decision.md | ✅ completed — decision: completed |
| 07-review | loop/2-loop/07-review-correction.md | ✅ sub-brain critique completed (conf=0.55) |

### 1-loop（规划 Iteration 7：多星座手征 ORF）— 全部完成
| 阶段 | 本地文件 | 状态 | 核心产出 |
|------|----------|------|---------|
| 01-任务澄清 | loop/1-loop/01-任务澄清-Iteration7.md | ✅ | Fork multi-constellation script task |
| 02-目标澄清 | loop/1-loop/02-目标澄清-Iteration7.md | ✅ | Benchmark criteria + acceptance range |
| 03-任务分解 | loop/1-loop/03-任务分解-Iteration7.md | ✅ | M1-M6 DAG |
| 04-信息搜集 | loop/1-loop/04-信息搜集-Iteration7.md | ✅ | JCAP + Orlando literature |
| 05-完备核验 | loop/1-loop/05-完备核验-Iteration7.md | ✅ | Gap analysis + conf=0.82 |
| 06-决策 | loop/1-loop/06-决策-Iteration7.md | ✅ | enter_2loop |

### 2-loop（执行 Iteration 7：多星座手征 ORF）— 全部完成
| 阶段 | 本地文件 | 状态 |
|------|----------|------|
| 01-pre-check | loop/2-loop/01-pre-check-Iteration7.md | ✅ environment check |
| 02-backup | loop/2-loop/02-backup-Iteration7.md | ✅ backup done |
| 03-execute | loop/2-loop/03-execute-Iteration7.md | ✅ script + full analysis + figures |
| 04-verify | loop/2-loop/04-verify-Iteration7.md | ✅ 9/9 checks PASS |
| 05-confidence | loop/2-loop/05-confidence-Iteration7.md | ✅ conf=0.82 |
| 06-decision | loop/2-loop/06-decision-Iteration7.md | ✅ completed |

## 2-loop M 任务清单（来自 1-loop/06）

| # | 任务 | 优先级 | 预期产出 |
|---|------|--------|---------|
| M1 | 修复 06-olc-lisa-mixed-network.py 的物理错误 | P0 | 06a-patched-mixed-network.py |
| M2 | 添加空间 OLC 模型到混合网络对比 | P1 | 三条臂长曲线叠加图 |
| M3 | 独立求和 vs 交叉相关对比分析 | P1 | 分析报告 + 对比图 |
| M4 | 观测时间扫描和检测阈值 | P2 | 阈值等高线图 + CSV |
| M5 | 验证脚本 | P1 | verify_mixed_network.py |
| M6 | 结果总结和 memory 写入 | P3 | memory/09-olc-mixed-network-iteration3.md |

## 已知问题

- ~~`scripts/06-olc-lisa-mixed-network.py` 有 4 个严重物理错误 (C1-C4)，需要完全重写~~ → **M1 已完成修复**
- `07-space-olc-snr.py` 部分有效，噪声模型需完善
- 已有 2-loop (08-stage) 已完成，可复用 `verify_08_physics.py`

## 最终产出汇总

### 科学产出
- 9 个 memory 文件（理论推导和结论）+ 10-space-olc-snr-results (SNR 公式确认)
- 10 个 Python 脚本（含验证脚本）
- 12 个 loop 阶段文件
- **空间 OLC 可探测性确认**: Formula1 (S_y² 分母) 正确，L=2.5Gm → SNR=245
- **C2 "bug fix" 确认为错误，需还原**
- 论文框架 v1 (7 章 + 附录)

### 基础设施
- CLAUDE.md — RALPH Loop 规则注入
- start-ralph-loop.sh — 启动检查脚本
- .claude/agents/ — 12 个 Agent 定义文件
- .claude/ralph-loop.local.md — 项目状态

## 从哪开始
1. 读取 `.claude/ralph-loop.local.md` 获知当前阶段
2. 读取 `loop/1-loop/03-任务分解.md` 追溯 M 任务清单
3. 启动 2-loop/01-pre-check → 环境检查
