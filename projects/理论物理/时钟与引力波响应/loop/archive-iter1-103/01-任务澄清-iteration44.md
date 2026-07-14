# 01-任务澄清 — Iteration 44

**状态**: pending
**输入**: ralph-loop.local.md (iter 43 completed), sub-brain v42 critique (07-sub-brain-iteration42.md), user status message
**时间**: 2026-07-10

---

## 背景

Iteration 43 完成了 sub-brain v42 的 A/C/D 三项修复（§3.4.3 物理表述、PDF 编译、标题风格）。

用户状态消息提到 "P0-1已QC PASS; P1-1 re-exec刚完成需QC; P2-1 QC FAIL需修复7项"。

**文件核实结果**：

| 文件 | 修改时间 | 与用户状态的关系 |
|------|---------|-----------------|
| note/P1-1-chiral-physics.md | 2026-07-08 13:56 | **无更新** — 无 re-exec 产出 |
| note/P2-1-olc-principles.md | 2026-07-08 01:54 | **无更新** — 无 re-exec 产出 |
| loop/2-loop/04-quality-check-P2-1-Iteration1.md | 2026-07-08 | P2-1 Iter1 QC FAIL（7项需修复），但已在 Iter2 修复并通过 |
| loop/2-loop/04-quality-check-P2-1-Iteration2.md | 2026-07-08 | **P2-1 Iter2 QC 已 PASS** |
| loop/2-loop/03-fix-report-P2-1-Iteration2.md | 2026-07-08 | P2-1 7项修复已全部完成 |

**关键发现**: 用户的 "P2-1 QC FAIL需修复7项" 指的是 **P2-1 Iteration 1** 的 QC 结果，该 7 项修复已在 **P2-1 Iteration 2** 完成并通过 QC。P2-1 当前状态为 **QC PASS**。

用户的 "P1-1 re-exec刚完成需QC" — 但 note/P1-1-chiral-physics.md 自 7月8日以来未更新，**不存在新的 re-exec 产出**。P1-1 当前状态为 **无更新，维持 Iter1 产出**。

**结论**: 用户状态消息描述的是旧的 P1/P2 迭代历史（约 iter1-8 阶段），不是当前的 fresh 产出。当前实际状态：

- P0-1, P1-1, P2-1 理解材料: **已完成且通过 QC**（iter1-8 阶段）
- P-chiral-orf-analytical: **已完成**（iter35）
- 论文 §3.4.3 + §3.5.4 插入: **已完成**（iter42-43）
- PDF: **已编译**（iter43，52页）
- 主论文: **无已知未修复错误**

---

## 本轮聚焦目标

loop_phase 当前为 `completed_2loop`，iteration 43 已完成。Iteration 44 应进入新的 1-loop 周期。

基于 sub-brain v42 的质疑 6（iter29 到 iter42 收敛效率极低）和本轮核实结果（P1-1/P2-1 无新的 re-exec 产出），**本轮应做收敛决策而非继续执行无目标的 re-exec**：

**Primary**: 评估当前论文完成度，决定是否继续 1-loop/2-loop 或进入提交准备阶段
**Secondary**: 修复 sub-brain v42 质疑 4（§3.5.4 缺少 P^V 宇称奇性证明）— 这是一个真正的、可执行的 Gap

---

## 关键任务列表（不超过 4 项）

1. **收敛评估**: 基于已有 QC PASS 状态（P0-1/P1-1/P2-1 QC + iter42-43 QC-5 PDF 编译），评估论文是否可进入下一里程碑（arXiv 提交或终稿）
2. **P^V 宇称奇性证明**: 在 §3.5.4 中补充 $P^V = (\hat{u}_1 \times \hat{u}_2) \cdot \hat{n}$ 的代数论证 — 这是 sub-brain v42 质疑 4 明确指出的物理深度 Gap
3. **Sub-brain v42 质疑 6 响应**: 确认 iter29 以来 14+ 轮的边际价值，决定是否继续 2-loop 或收敛
4. **创建 sub-brain v43 质询**: 按规则 8 派发下一轮质疑

---

## 前置材料清单（可直接使用）

| 文件 | 用途 |
|------|------|
| `note/P0-1-hu-prd-understanding.md` | 理解材料 P0-1（Hu PRD） |
| `note/P1-1-chiral-physics.md` | 理解材料 P1-1（手征物理） |
| `note/P2-1-olc-principles.md` | 理解材料 P2-1（OLC 原理） |
| `note/P-chiral-orf-analytical.md` | 手征 ORF 解析框架（iter35 产出） |
| `note/P3-phase3-cross-comparison.md` | 三文献交叉对比 |
| `main-paper.tex` | 主论文，§3.4.3 + §3.5.4 已插入（iter42-43） |
| `main-paper.pdf` | 编译版 PDF（iter43 编译，52页） |
| `loop/2-loop/04-qc.md` | iter42/43 QC 报告（QC-1 到 QC-5 全部 PASS） |
| `loop/2-loop/07-sub-brain-iteration42.md` | sub-brain v42 完整质疑 |
| `loop/1-loop/05-verifier-report-iteration41.md` | verifer 报告（conf 0.94） |

---

## 收敛标准

完成 iteration 44 后，应达成以下之一：

- [ ] **收敛决策已做出**: 输出明确的 "继续 2-loop" 或 "进入提交准备" 决策，并附理由
- [ ] **§3.5.4 补充 P^V 证明**: 如决定继续修正，P^V 宇称奇性代数论证已插入 §3.5.4
- [ ] **Sub-brain v43 已派发**: 按规则 8，下一轮质疑已生成

---

## 风险与盲点

1. **用户状态与实际状态脱节**: 用户的 "P1-1 re-exec需QC; P2-1 QC FAIL" 是 iter1-8 的历史状态，不是当前状态。需明确告知，避免基于过时信息继续无用 re-exec。

2. **sub-brain v42 质疑 4 的物理深度问题**: §3.5.4 缺少 $P^V$ 宇称奇性的证明，这是一个真正需要修补的 Gap。P-chiral-orf-analytical.md Sec 4.3 和 appendix B 已有完整证明，可直接引用。

3. **收敛效率**: sub-brain v42 质疑 6 指出 iter29 到 iter42 消耗 13+ 轮但净进度极小。本轮必须做出收敛决策，避免继续低效循环。

4. **规则 3 约束**: 当前 loop_phase 为 `completed_2loop`，按 AGENTS.md 和 CLAUDE.md 约束，必须先完成 1-loop 全部 6 阶段才能进入下一轮。Clarifier 输出仅定义任务范围，不替代完整流程。
