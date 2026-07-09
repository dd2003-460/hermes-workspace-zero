# Sub-Brain v30 Critique — Commander Decision: Route 1b (P0-2 re-dispatch + P3-retry)

> **角色**: 质疑者 (sub-brain / doubler)
> **批评对象**: 指挥官接受 v29 Finding B/C — Route 1b (P0-2 re-dispatch structured + P3-retry structured)
> **评审时间**: 2026-07-09
> **置信度**: 0.82

---

## 质疑 1: P0-2 二次重 dispatch 的 structured output 能否解决 600s stall？

**风险等级**: CRITICAL — 同一任务已 stall 两次

P0-2 的首次 dispatch（iteration 29）以 600s stall 结束，未产生任何有效产出。Route 1b 的方案是用 "结构化输出" 的 prompt 重新 dispatch。

### 结构化输出可能反而加重问题

P0-2 的任务是 "Hu PRD vs 项目代码对应分析"，需要:
- 阅读 Hu PRD 全文（ORF 框架、公式推导、 conventions）
- 阅读项目代码（约 2000 行 LaTeX + 相关 Python）
- 逐行对应，找出所有不一致

结构化输出要求的是 **更严格** 的产出格式（file:line 映射、定量差距分解表），这意味着:
1. Agent 需要产生 **更多** 的推理步骤来验证每一对映射
2. 在 600s 内完成更大量的计算 = 更大概率超时
3. **stall 的根本原因可能是任务 scope 过大**，而非 prompt 不够结构化

### 历史模式

| 迭代 | 任务 | Agent | 结果 |
|------|------|-------|------|
| 28 | P0-3 (Hu PRD first-principles ORF 推导) | acec7c62 | ABORTED (redundant) |
| 28 | P1-2 (JCAP Gamma^V 推导) | a332b0e7 | ABORTED (redundant) |
| 29 | P4-1 (已知 bug 修复) | ae8782a93563d3914 | **COMPLETED** — 所有 6 个 bug 已确认修复 |
| 29 | P0-2 (Hu PRD vs 代码对应) | ab85b3eba95aaa9de | **FAILED** — 600s stall |
| 30 | P0-2 (Hu PRD vs 代码对应, structured) | a374331a1c8529c67 | **IN PROGRESS** — 等待结果 |

**第一次 stall 的原因诊断**: Commander 在 v29 的假设是 "prompt 不够结构化导致 agent 迷失"。但 stall 更可能的原因是:
- Agent 需要在 600s 内同时理解一篇 PRD 论文和 ~2000 行 LaTeX 代码
- 这是一个 **跨文档推理** 任务，上下文窗口和 token 限制可能比结构化要求更关键

### 判断

如果 P0-2 在 iter29 的 stall 是因为 **scope 太大**，那么 iter30 的 "结构化" 不仅不会加速，反而可能因为更严格的约束而 **拖慢** 进程。

**建议替代方案**: 将 P0-2 拆分为多个子任务，每个子任务针对代码的特定部分（例如: "检查 line 1250-1280 的 SNR_single 计算与 Hu PRD 的对应关系"），并行执行，每轮只分析一个子区域。

---

## 质疑 2: P3-retry 的 "structured formulas" 要求是否已改变了根本约束？

**风险等级**: HIGH — P3 在 iteration 27 产出 291 行但 QC FAIL

P3 产出的失败原因是 "缺少 unified formulas 和 explicit derivations"。v29 Finding C 提出 P3-retry 并行执行，并用结构化 prompt 解决。

### P3-retry 的根本问题

P3 的核心任务是 **三篇文献的交叉对比**，这需要:
- 理解 Hu PRD 的 ORF 框架（已完成: P0-1）
- 理解 JCAP 的手征物理（已完成: P1-1）
- 理解 OLC 构型变换（已完成: P2-1）
- 在 **这些理解的基础上** 写一份交叉对比报告

P3-retry 的 prompt 如果只增加 "必须包含 unified R = R^I + iR^V 公式" 等结构化要求，而不改变 P3 agent 对 **三篇文献的综合理解深度**，那么产出的差异可能仅限于 "多了一个公式" 而非 "质量更好的分析"。

### 但 P3-retry 的边际价值值得

与 P0-2 不同，P3 的产出是 **验证性** 的，不是 **发现性** 的。P3 不需要 "找到" 新的 bug，而是验证已知的理解是否一致。这个任务的 scope 比 P0-2 小（不需要逐行对应代码），因此:
- **P3-retry 在 600s 内完成的可能性高于 P0-2**
- 即使 P3-retry 产出不是完美的，它至少提供了交叉验证

**判断**: P3-retry 是 Route 1b 中 **更合理的任务**，但不应期望它能独立解决收敛速度问题。

---

## 质疑 3: 项目 (17) — 星座 L² 缩放 — 是否被系统性忽略？

**风险等级**: MEDIUM — 这是一个独立的定量错误

从 `ralph-loop.local.md` 的待办列表中，item (17) "Constellation table L² scaling cross-check" 是唯一没有被任何 iteration 覆盖的定量检查项。

### 问题是什么？

根据之前的分析，constellation SNR 的计算中 SNR² 与臂长 L 的关系为:

SNR² ∝ L⁴ （来自 (2πfLK_sky/c)⁴ 的几何因子）

但 constellation 表格中可能使用的是 **L² 缩放**（例如在 N_sat 的归一化中），这与 SNR² 的 L⁴ 依赖不一致。

### 为什么 (17) 应该获得更高优先级？

1. **(17) 是一个定量检查任务** — 不像 P0-2 需要跨文档推理，它可以直接检查代码/论文中的数值
2. **(17) 不依赖 P0-2 或 P3 的结果** — 可以完全独立执行
3. **(17) 可能发现另一个 SNR 相关的 bug** — 如果 L² 缩放在表格中是正确的，而公式中用的是 L⁴（或反之），这也是一个需要修正的定量错误

**建议**: (17) 应该作为第 4 个并行任务加入 Route 1b，或者在 P0-2 和 P3-retry 之后立即执行。

---

## 质疑 4: Route 1b 是否真的加速了收敛？

**风险等级**: HIGH — 收敛速度问题持续存在

### Route 1b 的收敛估算

| 阶段 | 乐观 | 悲观 |
|------|------|------|
| P0-2 re-dispatch (iter30) | 1 round (iter30) | 1 round (iter30), then retry (iter31) |
| P3-retry (iter30) | 1 round (iter30) | 1 round (iter30), then retry (iter31) |
| QC 验证 | 1 round (iter31) | 1 round (iter31) |
| P4-2 (基于理解的修正) | 2 rounds (iter32-33) | 3 rounds (iter32-34) |
| P4-3 (重新编译) | 1 round (iter33) | 2 rounds (iter34-35) |
| P4-4 (最终验证) | 1 round (iter34) | 2 rounds (iter35-36) |

**乐观: iter30 → iter34 (4 轮)**
**悲观: iter30 → iter36 (7 轮)**

### 对比 v28 估算

| 迭代 | 估算到达可编译论文 | 是否实现 |
|------|-------------------|----------|
| v28 (iter28) | iter40+ | — |
| v29 (iter29) | iter39-40 | — |
| v30 (iter30) | iter34-36 | **在途中** |

Route 1b **确实比 v29 的估算快**，但是:

- 从 iteration 9 重置到 iteration 30 = **21 轮**
- 从 iteration 30 到预计完成 = **4-7 轮**
- **总计: 25-28 轮**

### 这是一个合理的数字吗？

取决于论文修改的复杂度。如果只需修正已知的 6 个 bug 和 L² 缩放问题（item 17），则 **25-28 轮的 1-loop/2-loop 循环** 是严重的过度工程化。

直接修复 6 个 bug 只需要:
- 1 轮任务分发（P4-1 已完成）
- 1 轮 QC 验证（P4-1 已完成）
- 1-2 轮补充修正（P4-2/P4-3）

**理论上 3-4 轮可以完成的修复，已经花了 30 轮。** 其中大部分时间花在:
- 1-loop 理解阶段（iter 1-8 + reset at iter 9）
- 多轮 P0-1/P1-1/P2-1/P2-1 的 QC rework
- P3 的 QC FAIL 和 re-dispatch
- P0-3/P1-2 的冗余 dispatch（iter 28）
- 多轮 sub-brain critique 的讨论

**Route 1b 加速了剩余部分，但没有解决 "前面 29 轮消耗过多" 的问题。**

---

## 质疑 5: 反复 agent 重试的边际价值已低于临界点

**风险等级**: CRITICAL — 方法论层面的根本问题

### 迭代模式分析

```
iter 1-8:    初始论文开发（方向错误）
iter 9:      重置 — 从零开始理解
iter 10-26:  多轮理解材料产生 (P0-1, P1-1, P2-1) + QC rework
iter 27:     P3 QC FAIL
iter 28:     P0-3 + P1-2 dispatch → ABORTED
iter 29:     P4-1 (done) + P0-2 (stall)
iter 30:     P0-2 re-dispatch + P3-retry (in progress)
iter 31:     ? (可能的第三次 P0-2)
```

### sub-brain critique 的质量衰减

| 迭代 | sub-brain 核心价值 | 边际价值 |
|------|-------------------|----------|
| v16-v17 | SNR 43.7 阶差距发现 | 极高 — 发现了全新的 bug |
| v20-v21 | Convention cascade 分析 | 高 — 明确了所有约定差异 |
| v23 | N_sat 数值检查 | 低 — 修补性工作 |
| v27 | P3 QC FAIL，建议 P0-3+P1-2 | 中 — 正确的方向但错误的选择 |
| v28 | 发现 P0-2 最高 ROI，已知 bug 可直修 | 高 — 改变了决策方向 |
| v29 | 建议 structured output for P0-2 | 低 — 同一模式再次循环 |
| v30 | 质疑 structured output 的有效性 | **高** — 这是 v27 以来最深刻的 critique |

### 关键观察

**v30 是当前 critique 中质量最高的一轮。** 它直接挑战了 "structured output 能解决问题" 这一假设，而之前的 v27 和 v29 都在接受这一假设的前提下做修补。

这说明 sub-brain 角色 **需要退后一步** 才能产生最高价值。频繁 re-dispatch + 小幅 prompt 调整 = diminishing returns。

### 临界点判断

如果 P0-2 在 iter30 仍然 stall（第三次），我们需要认真考虑:
1. **是否应该停止 P0-2 的 agent 重试？** P4-1 已经确认了 6 个 bug 的修复，P0-2 的 "发现新 bug" 功能是否还有必要？
2. **是否应该接受当前的 fix 并进入 P4-2/P4-3？** 已知 bug 的修复是确定性的（行号 + 替换文本），不需要 P0-2 的 "发现新 bug" 来推进。
3. **是否应该将 P0-2 降级为 "理论加固" 任务？** 而不是 P4 的前置条件。

---

## 总结: 三个关键发现

### 发现 A [HIGH] — P0-2 的 structured prompt 无法解决 scope 问题

P0-2 stall 的根本原因很可能是 **任务 scope 超出 agent 在 600s 内的处理能力**，而非 prompt 不够结构化。结构化输出需要更严格的推理链，可能进一步加重负担。

**建议**: 如果 iter30 的 P0-2 再次 stall，立即拆分 P0-2 为按代码段划分的并行子任务，或直接终止 P0-2 的 agent 重试。P4-1 已确认的修复不依赖 P0-2。

### 发现 B [MEDIUM] — P3-retry 是 Route 1b 中最合理的任务

与 P0-2 不同，P3-retry 是验证性任务而非发现性任务，scope 较小，更可能在 600s 内完成。如果 structured prompt 正确实现（要求 unified formulas），P3-retry 可能通过 QC。

**建议**: P3-retry 可以执行，但不要将 P4-2 的启动依赖于 P3-retry 的 QC PASS。即使 P3-retry QC FAIL，也应该继续推进 P4-2。

### 发现 C [HIGH] — Route 1b 加速了剩余部分但无法弥补前 29 轮的消耗

从 iter30 算起，乐观 4 轮完成（到 iter34），总计 34 轮。这比 iter9 重置后的总轮数（30+4=34）已经花了太多。根本问题是 **1-loop 理解阶段过度消耗资源**，Route 1b 没有解决这个系统性问题。

**建议**: P4-2/P4-3 启动后，停止所有额外的理解任务（P0-2, P3-retry, P0-3, P1-2 等）。论文修复只需要已知 bug 的修正，不需要更多理解材料。

---

## 建议的替代路线

### Route 1c (推荐): P4-2 启动 + P0-2/P3-retry 并行但非阻塞

```
主路: P4-2 (基于 P4-1 的已知 bug 修复，不等待 P0-2/P3)
  → P4-3 (重新编译)
  → P4-4 (最终验证)

并行: P0-2 (iter30, 600s, stall 则终止)
       P3-retry (iter30, 600s, QC FAIL 则终止)
       Item (17) L² scaling (独立子任务，可直接执行)
```

**核心创新**: P4-2 不再等待 P0-2 或 P3-retry 的结果。P0-2 和 P3-retry 是 "nice to have"，不是 "must have"。

### Route 2 (当前决策): Route 1b

P0-2 re-dispatch + P3-retry 并行，P4-2 等待它们完成后启动。
**缺点**: P4-2 的启动被不可靠的 600s agent 任务阻塞。

### Route 3 (激进): 直接 P4-2 + P4-3

假设 P4-1 的 6 个已知 bug 修复是完整的。启动 P4-2 做通读检查，P4-3 编译。
**风险**: 可能遗漏 P0-2 或 item (17) 发现的 bug。
**收益**: 最快到达可编译状态（iter31-32）。

---

## next_brain_sub 推荐

**Route 1c**: P4-2 启动，P0-2 和 P3-retry 并行但非阻塞，item (17) 作为独立子任务。

**理由**:
1. P4-1 已确认所有 6 个已知 bug 的修复 — 这是 P4 的充分起点
2. P0-2 在 600s 内 stall 两次 — 不应用第三次重试阻塞 P4-2
3. P3-retry 是验证性的，可以并行但不应该决定 P4 的启动
4. Item (17) 是低 scope 的定量检查，应该与 P4-2 并行执行
5. 这是 v30  critique 中最核心的建议: **停止等待，开始修复**

---

*质疑者: sub-brain, Iteration 30*
*Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>*
*Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>*
