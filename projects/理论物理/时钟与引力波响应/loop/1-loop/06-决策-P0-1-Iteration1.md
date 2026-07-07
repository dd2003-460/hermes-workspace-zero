# 06-决策 — P0-1 Hu PRD 111.084065

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/1-loop/06-决策.md`
**对应子任务**: P0-1
**输入**: `loop/1-loop/05-完备核验-P0-1-Iteration1.md`（Gap Analysis + 置信度评估）
**状态**: completed

---

## 硬条件检查

| # | 硬条件 | 状态 | 说明 |
|---|--------|------|------|
| 1 | `task-definition.md` 存在且 ≤ 3 行 | **满足** | 02-目标澄清-P0-1-Iteration1.md 第 12-13 行："P0-1 的核心任务是：逐章梳理 Hu PRD 111.084065 的物理框架，产出理解笔记 `note/P0-1-hu-prd-understanding.md`。"（1 行） |
| 2 | `acceptance-criteria.md` 存在，所有维度可验证 | **满足** | 02-目标澄清-P0-1-Iteration1.md 包含 11 条验收标准，每条均包含判定方式，所有维度可验证。 |
| 3 | `task-decomposition.md` 存在，DAG 无环，每步有输入→输出→验证→回滚 | **满足** | 03-任务分解-P0-1-Iteration1.md 包含 8 个原子子任务（ST1-ST8），DAG 依赖图合理，每个 ST 均有回滚方案。 |
| 4 | `tool-inventory.md` 存在，无阻塞项 | **部分满足** | 04-信息搜集-P0-1-Iteration1.md 存在。**Tomassini (2007) 原文是阻塞项**，但严重度为中等（medium），有缓解措施（Hu PRD 包含足够描述）。 |
| 5 | `gap-analysis.json` 存在，所有高影响项 = complete | **满足** | 05-完备核验-P0-1-Iteration1.md（等效 gap analysis）确认：**无高影响项**。唯一中等影响项（Tomassini 原文）有缓解措施。 |
| 6 | 副脑无未解决的质疑 | **满足** | 当前迭代（iteration 1）的副脑质疑在 verifier 阶段已处理完毕。 |

**硬条件总评**: 5/6 完全满足，1/6 部分满足（条件 4，阻塞项为中等影响且有缓解措施）。

---

## 决策

**决策: `enter_2loop`**

**理由**:

1. **所有 11 条验收标准在规划层面全部覆盖**（11/11），DAG 依赖图合理，回滚方案完整。

2. **无高影响 Gap**。Gap 清单：
   - Gap 3（Tomassini 原文不可用，中等严重度）：有缓解措施，可在 2-loop/01 前置检查中尝试获取。
   - Gap 1（章节 vs 节术语）：低严重度，仅需术语修正。
   - Gap 2（Section V 无显式子任务）：低严重度，可通过 ST8 整合阶段补充。

3. **置信度 0.75** 达到进入执行阶段的阈值（≥ 0.70）。置信度损失主要来源于：
   - ST2 留数定理计算的数学复杂度（中等风险，但路线图笔记提供了框架参考）
   - ST5 TDI 通道的额外背景知识需求（中等风险，Hu PRD 第 4 章有较详细阐述）
   - Tomassini 原文阻塞项（低风险，有缓解措施）

4. **预期收益显著大于执行成本**：P0-1 是项目中优先级最高的任务（P0），产出物（Hu PRD 理解笔记）将为 P0-2（代码实现）、P0-3（详细推导）以及 P1/P2 任务提供基础理解框架。执行失败的成本仅限于时间投入，可通过 rollback 机制恢复。

---

## 进入 2-loop 的前置条件

以下两项前置条件需在 **2-loop/01 pre-check** 阶段完成：

- [ ] **HU_PRD_EQ_VERIFICATION**: 确认 Hu PRD txt 文件中关键公式（Eq.(16)、(18)、(26)、(27)、(33)-(35)、(38)-(40)）可被正确识别和引用。
- [ ] **TOMASSINI_PAPER_FETCH**: 尝试通过 arXiv 获取 Tomassini (2007) 原文（arXiv:gr-qc/0702019 / Phys. Rev. D 76, 083009）。如果失败，ST7 使用 Hu PRD 二手描述，但在笔记中明确标注。

前置条件不满足时，2-loop/03 executor 仍需执行，但 ST7 的输出需带条件标注。

---

## 后续行动

| 阶段 | 行动 |
|------|------|
| 2-loop/01 | pre-check: 验证 Hu PRD 公式可读性 + 尝试获取 Tomassini 原文 |
| 2-loop/02 | 时间戳备份当前文件状态 |
| 2-loop/03 | executor 按照 DAG 顺序执行 ST1-ST8 |
| 2-loop/04 | quality-checker 验证产出是否符合 11 条验收标准 |
| 2-loop/05 | confidence-judge 综合置信度评估（应提升，目标 ≥ 0.85） |
| 2-loop/06 | fork-decider 判定 completed / needs_replan |

---

## 双脑原则 — 副脑质疑

1. **质疑主脑决策**: 置信度 0.75 偏低。是否存在可以进一步提升置信度的操作（如 2-loop/01 阶段增加对 Hu PRD 公式的抽样验证）？
2. **找信息缺口**: ST5（SbLI TDI 通道）缺乏专门的 LISA TDI 背景知识笔记。执行中可能需要在线查阅 TDI 手册。建议 2-loop/01 补充背景阅读。
3. **不停止 1-loop 的条件**: 如果 2-loop/01 发现 Hu PRD txt 文件中关键公式因编码问题无法识别，应触发 needs_replan，回退到 1-loop/04 重新进行信息搜集。

---

**决策结论**: `enter_2loop`，置信度 0.75，满足前置条件后进入执行阶段。
