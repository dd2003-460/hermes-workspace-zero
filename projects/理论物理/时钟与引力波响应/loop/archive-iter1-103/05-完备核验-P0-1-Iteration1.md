# Completeness Verification — P0-1 Hu PRD

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/1-loop/05-完备核验.md`
**对应目标**: P0-1（Hu PRD 111.084065 理解）
**输入**:
- `loop/1-loop/02-目标澄清-P0-1-Iteration1.md`（11 条验收标准）
- `loop/1-loop/03-任务分解-P0-1-Iteration1.md`（8 个原子子任务 ST1-ST8）
- `loop/1-loop/04-信息搜集-P0-1-Iteration1.md`（工具清单、阻塞项、新颖性评估）
**状态**: completed
**核验时间**: 2026-07-07T18:50+0800

---

## 验收标准就绪评估

| AC编号 | 状态 | 说明 |
|--------|------|------|
| AC1 ORF 物理直觉解释 | **满足** | ST1 专门负责 ORF 物理直觉，含通俗语言解释、几何因子定义、前人近似局限。ST8 负责整合一致性检查。 |
| AC2 单向链路分解 + 留数定理 | **满足** | ST2 覆盖 Eq.(6)-(24) 全部关键公式，含复平面极点 z0-z4 和 I1 的 Ei 函数结果。ST6 补充参数代换规则。 |
| AC3 PTA ORF 完整表达式 + HD 曲线恢复 | **满足** | ST3 覆盖 Eq.(26)（完整 PTA ORF）和 Eq.(27)（HD 曲线），含退化过程、脉冲星项物理含义。 |
| AC4 GbLI ORF 两向链路表示 | **满足** | ST4 覆盖 Eq.(33)-(35)，含应变归一化因子和额外归一化因子解释。 |
| AC5 SbLI TDI 通道 ORF | **满足** | ST5 覆盖 Eq.(38)-(40)，含 TDI 通道物理含义和轨道运动相位说明。 |
| AC6 >=5 处原文公式引用 | **满足** | 所有 ST（ST2/3/4/5/6/7）都包含明确的公式引用目标。ST8 汇总确认 13+ 引用。 |
| AC7 >=3 处中间推导步骤 | **满足** | ST2（留数围道选择）、ST3（HD 退化）、ST4（两向链路展开）、ST6（参数代换规则）共 4 处推导步骤，超过 3 处要求。 |
| AC8 每个关键公式附带物理直觉 | **满足** | 所有 ST（ST1-ST7）均要求在公式旁附 >=30 字物理直觉解释。ST8 负责一致性检查。 |
| AC9 Tomassini 对比分析 | **满足** | ST7 覆盖对比分析，含小天线近似数学形式、渐近行为验证、误差量级分析。唯一阻塞项（Tomassini 原文不可用）已有明确缓解措施。 |
| AC10 >=2 组自我问答 | **满足** | AC 文件中已提供 3 组示例 Q&A。ST8 负责整合并确认至少 2 组。 |
| AC11 关键方程通俗解释 | **满足** | 与 AC8 重叠，ST1/2/3/4/5/6 均有物理直觉解释要求，AC 文件提供 5 个示例解释。 |

**总结**: 11 条验收标准在规划层面全部具备充分覆盖，无遗漏。

---

## Gap Analysis

### Hu PRD 章节结构核实

Hu PRD 实际结构：
- Section I: INTRODUCTION（行 17）
- Section II: CORRELATION ANALYSIS OF SGWB — 通用公式推导（行 140）
- Section III: OVERLAP REDUCTION FUNCTION — PTA（行 283）
- Section IV: OVERLAP REDUCTION FUNCTION — 激光干涉仪（行 798）
- Section V: CONCLUDING REMARKS + TABLE I 数值比较（行 1227）

**Gap 1**: 规划要求"覆盖 5 章内容"，但 Hu PRD 实际是 5 **节**而非章。AC 文件的硬约束中"必须覆盖 5 章内容"的表述不准确。
- **严重度**: 低
- **缓解措施**: 不影响实质内容覆盖。5 节内容均被 ST1-ST8 覆盖。术语修正即可。

**Gap 2**: Section V（Concluding Remarks + TABLE I 数值比较）没有对应的显式子任务。TABLE I 包含 PTA/GbLI/SbLI 三种探测器在不同方法下的计算时间和精度比较，这是一个有价值的数值参考。
- **严重度**: 低
- **缓解措施**: TABLE I 的内容可通过 ST2/ST3/ST4/ST5 的理解笔记自然覆盖（因为这些子任务在分析公式时必然会涉及数值结果）。ST8 的整合阶段也可以加入对 TABLE I 的总结。

**Gap 3**: Tomassini (2007) 原文不可用，是 ST7 的唯一阻塞项。
- **严重度**: 中
- **缓解措施**: Hu PRD 第 1 章和第 4 章已包含对 Tomassini 近似的充分描述。建议进入 2-loop 前通过 arXiv 获取（arXiv:gr-qc/0702019 / Phys. Rev. D 76, 083009）。如无法获取，ST7 可在不使用原文的情况下完成基础对比。

---

## 工程可行性评估

| 维度 | 状态 | 说明 |
|------|------|------|
| 理论完整性 | **complete** | 8 个子任务覆盖所有 5 节内容和 11 条验收标准，DAG 依赖图合理 |
| 工程可行性 | **complete** | Hu PRD txt（2023 行，72KB）完整可用，PDF 辅助可用 |
| 工具就绪度 | **partial** | 主要工具就绪，Tomassini 原文是阻塞项（有缓解措施） |
| 方向正确性 | **complete** | 规划完全对齐验收标准，11/11 覆盖 |
| 可回滚性 | **complete** | 每个 ST 均有明确的回滚方案（详见任务分解文件各 ST 的"回滚"条目） |

---

## 高影响项

```json
[
  {
    "dimension": "工具就绪度",
    "status": "partial",
    "impact": "medium",
    "action": "在 1-loop/06 决策阶段，建议补充获取 Tomassini (2007) 原文。如无法获取，ST7 可基于 Hu PRD 中的描述完成对比，但验证精度会略低。"
  },
  {
    "dimension": "理论完整性",
    "status": "complete",
    "impact": "low",
    "action": "Section V（TABLE I 数值比较）无显式子任务，但可通过 ST8 整合阶段补充。"
  }
]
```

---

## 置信度评估

### 总体置信度: **0.75**

### 关键假设
1. **8 个子任务的质量取决于 2-loop 执行阶段executor 的输出质量**。规划本身是完备的，但 1-loop 阶段无法验证执行输出。
2. **Hu PRD txt 文件内容完整且公式编号准确**。经核实，txt 文件包含全部 5 个 Section、2023 行、18+ 处公式引用。
3. **路线图笔记中的留数推导框架足够指导 ST2 的执行**。路线图是针对 JCAP 手征 ORF 的推导框架，但对 Hu PRD 的留数定理推导只有框架性概述，ST2 执行时需要完全基于 Hu PRD 原文重新推导。
4. **T**DI 通道的物理含义可以在不使用 LISA TDI 手册的情况下从 Hu PRD 原文中充分理解。存在一定风险，但 Hu PRD 第 4 章后半部分有较详细阐述。

### 风险项
1. **中等风险**: ST2（复平面留数定理计算）是数学复杂度最高的子任务，执行中可能出现理解偏差。路线图笔记提供的框架不完整，需要 executor 仔细跟踪原文推导。
2. **中等风险**: ST5（SbLI TDI 通道）需要额外的 LISA TDI 背景知识，项目缺乏专门笔记。
3. **低风险**: Tomassini 原文不可用影响 ST7 的对比精度。
4. **低风险**: 理解笔记的最终质量取决于 executor 的阅读深度和表达能力，无自动化的质量检查机制（在 2-loop/04 阶段有质量验证，但标准是验证脚本而非理解深度）。

### 进入 2-loop 的准备度: **needs-more-work**

### 理由
- **规划完备性充分**：8 个子任务的分解是细致的，验收标准 11/11 覆盖，DAG 依赖关系合理，回滚方案完整。
- **但存在两项改进建议**：
  1. ST2 的留数定理计算复杂度较高，建议在执行前（2-loop/01 pre-check 阶段）验证 Hu PRD txt 中 Eq.(16) 的极点表达式和 Eq.(18) 的 Ei 函数结果是否可读/可解析解析。
  2. ST7 的 Tomassini 对比建议先通过 arXiv 获取原文，或在 ST7 中明确标注哪些对比是基于 Hu PRD 二手描述而非 Tomassini 原文。
- **不阻塞进入 2-loop**：两项改进均可在 2-loop 执行阶段同步完成，不需要在 1-loop 阶段额外投入。

---

## 建议

1. **建议进入 2-loop，但有前置条件**：
   - [ ] 在 2-loop/01 pre-check 阶段确认 Hu PRD txt 文件中关键公式（Eq.(16)、(18)、(26)、(27)、(33)-(35)、(38)-(40)）可被正确识别和引用。
   - [ ] 在 2-loop/01 pre-check 阶段尝试通过 arXiv 获取 Tomassini (2007) 原文。如果失败，ST7 使用 Hu PRD 二手描述，但在笔记中标注。

2. **2-loop/03 executor 执行策略建议**：
   - 按照 DAG 顺序执行：第 1 轮 ST1+ST2（并行），第 2 轮 ST3+ST6（并行），第 3 轮 ST4，第 4 轮 ST5+ST7（并行），第 5 轮 ST8（整合）。
   - 每个 ST 执行完成后，应通过编辑任务分解文件更新其状态为 completed，方便 1-loop 阶段追踪。

3. **关于"5 章"的术语修正**：
   - Hu PRD 实际是 5 **sections**（节），不是 5 chapters。建议在后续文件中统一使用"节"的表述，避免与物理学论文中的 chapter 概念混淆。

---

## 5 维度评分汇总

| 维度 | 评分 |
|------|------|
| theoretical_integrity | complete |
| engineering_feasibility | complete |
| tool_readiness | partial |
| direction_correctness | complete |
| revertibility | complete |

---

**核验结论**: P0-1 的任务分解和信息搜集已完成，规划覆盖 11/11 验收标准，DAG 依赖合理，回滚方案完整。工具就绪度为 partial（Tomassini 原文阻塞项），置信度 0.75。建议以条件满足方式进入 2-loop 执行阶段。
