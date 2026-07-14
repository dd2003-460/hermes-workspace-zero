# Task Decomposition — P1-1 JCAP 手征引力波物理 (Iteration 1: 深入推导与补充)

> 创建日期：2026-07-07
> 阶段：1-loop/03（任务分解）
> 按规格文件：`/Users/a1-6/Desktop/workspace/loop/1-loop/03-任务分解.md` 执行
> 输入：`loop/1-loop/02-目标澄清-手征物理-Iteration1.md`（验收标准）+ `note/P1-1-chiral-physics.md`（已有理解笔记）
> 输出：本文件（后续原子子任务 DAG）
> 状态：pending
> 回滚：删除本文件即可，不改动任何下游产出

---

## 现有产出评估

已有理解笔记 `note/P1-1-chiral-physics.md`（约 6KB, 213 行）已覆盖 P1-1 全部 10 项验收标准：

| 验收标准 | 状态 | 笔记覆盖位置 |
|----------|------|-------------|
| AC1: 通俗语言解释手征性 | ✅ 完整 | §1.1-1.3，含测试粒子圆周运动图像 |
| AC2: Stokes I/V 正确定义 | ✅ 完整 | §2.1-2.3, eq. 2.6 |
| AC3: chi 定义和物理含义 | ✅ 完整 | §3.1-3.3, 含取值范围和物理意义 |
| AC4: 至少 3 种宇称破坏模型 | ✅ 完整 | §4.1, 列了 3 种机制 |
| AC5: 平面探测器无法探测 Gamma^V | ✅ 完整 | §5.3, 镜面对称性论证 |
| AC6: 至少 5 处原文引用 | ✅ 超额完成 | 12+ 处引用 |
| AC7: 至少 3 处中间推导 | ✅ 满足 | §1.2, §2.2, §5.3 均有推导 |
| AC8: 每个关键公式的物理直觉 | ✅ 完整 | 每个公式旁有 >30 字解释 |
| AC9: 与项目已有工作对比 | ⚠️ 仅完成最低要求 | §7 仅 4 行讨论 |
| AC10: 至少 2 组自我问答 | ✅ 超额完成 | §9, 3 组 Q&A |

**结论**：P1-1 的基础理解任务已圆满完成。后续工作聚焦于 **深化推导严谨性**、**填补不确定之处**（笔记 §8 标记的 3 个未知项）、以及 **加强项目对比分析**。

---

## 子任务列表

## Subtask 1: 验证圆极化基的归一化
- **输入**：`note/P1-1-chiral-physics.md` §1.2 (eq. 2.3, 2.4)，JCAP 原文 eq. 2.3-2.4
- **输出**：补充笔记 `note/P1-1-appendix-normalization.md` 中 §1：
  - 明确验证 $|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_\times|^2$
  - 验证 $e^R_{ab} (e^R_{ab})^* = 1$ 以及交叉项为零
  - 推导出 $\langle S_R \rangle = \langle S_L \rangle = I(f)$ 在无手征条件下的等价性
- **验证**：
  - 写出完整验证过程：$(h_+ - i h_\times)(h_+^* + i h_\times^*)/2 + (h_+ + i h_\times)(h_+^* - i h_\times^*)/2 = |h_+|^2 + |h_\times|^2$
  - 至少包含 3 步代数推导
  - 归一化因子 $\sqrt{2}$ 不可约掉
- **回滚**：删除 `note/P1-1-appendix-normalization.md`
- **置信度**：0.95（纯代数验证，难度低）
- **依赖**：null（可独立进行，是纯数学验证）

---

## Subtask 2: Gamma^V 宇称奇性的严格张量推导
- **输入**：`note/P1-1-chiral-physics.md` §5.3, JCAP eq. 2.10, `note/P1-1-appendix-normalization.md`（Subtask 1 输出，如果已完成）
- **输出**：补充笔记 `note/P1-1-appendix-normalization.md` 中 §2：
  - 从 $e^+_{ab}(\hat{k}) e^\times_{cd}(\hat{k}) - e^\times_{ab}(\hat{k}) e^+_{cd}(\hat{k})$ 出发
  - 给出宇称变换 $\hat{k} \to -\hat{k}$ 下每个张量分量的变换律
  - 严格证明该组合在宇称变换下变号（宇称奇）
  - 用此论证解释：对具有镜面对称性的探测器网络，$\Gamma^V = 0$ 是必然结果（不仅是直觉，而是严格证明）
  - 讨论 LISA（单个三角）为何 $\Gamma^V = 0$，LISA-Taiji 为何 $\Gamma^V \neq 0$
- **验证**：
  - 推导中至少包含 5 个中间步骤
  - 明确写出镜面对称操作 M 满足 $M \mathcal{N} = \mathcal{N}$ 时 $\Gamma^V = -\Gamma^V \implies \Gamma^V = 0$
  - 对 LISA 和 LISA-Taiji 给出具体构型对比
- **回滚**：追加内容可回退，主文件不变
- **置信度**：0.85（需要张量计算，正确性依赖仔细推导）
- **依赖**：null（与 Subtask 1 可并行）

---

## Subtask 3: chi(f) 的频率依赖性与不同宇称破缺模型的频谱特征
- **输入**：`note/P1-1-chiral-physics.md` §3.3（不确定性 #3），JCAP 原文中 chi(f) 的频域表述，以及各宇称破缺模型的原始文献（Alexander et al. 2006, Satoh et al. 2008, Cornwall 1997, Callister et al. 2025）
- **输出**：补充笔记 `note/P1-1-appendix-normalization.md` 中 §3：
  - 分析 chi(f) 在不同模型中的频率行为：
    - Leptogenesis/Chern-Simons：预期 chi ≈ 常数（与频率无关的手征增强）
    - 螺旋磁场：chi(f) 可能有幂律形式 $f^\alpha$
    - 传播双折射：chi(f) 随传播距离和频率指数增长
  - 这些频谱特征是否可用于区分不同宇称破缺模型（"手征光谱学"概念）
  - 与 LISA 频带（mHz 量级）的对应关系
- **验证**：
  - 至少引用 2 篇原始文献（不限于 JCAP）中关于 chi(f) 频率依赖的论述
  - 明确区分"产生时的手征性"（早期宇宙过程）和"传播中的手征性增长"（宇宙学演化）
  - 指出这些频谱特征对探测器设计的意义
- **回滚**：追加内容可回退
- **置信度**：0.75（需要查阅额外原始文献，JCAP 本身对此讨论有限）
- **依赖**：null（可独立进行，信息搜集为主）

---

## Subtask 4: 手征 ORF (Gamma^V) 与通用 ORF (Hu PRD) 的形式对照
- **输入**：`note/P1-1-chiral-physics.md` §7（薄弱的项目对比分析），`note/P0-1-hu-prd-understanding.md`（如果已存在，否则引用 Hu PRD 原文），JCAP eq. 2.9-2.10
- **输出**：补充笔记 `note/P1-1-appendix-normalization.md` 中 §4：
  - Hu PRD 中的 ORF 定义（$R_{ij}(\hat{k})$）与 JCAP 中的 $\Gamma^I_{ij}$, $\Gamma^V_{ij}$ 的对应关系
  - 是否可以将 $\Gamma^I + i\Gamma^V$ 写成复数 ORF 的形式 $R_{ij} = R^I_{ij} + i R^V_{ij}$？
  - Hu 的通用框架是否能自然包含手征 ORF？（即 Hu 的公式在宇称破缺介质中是否自动产生虚部）
  - 对 OLC 探测器的具体影响：OLC 的探测器张量代入 JCAP 的 $\Gamma^V$ 公式会得到什么结果？
- **验证**：
  - 写出至少 2 个公式的显式对照（Hu 公式 vs JCAP 公式）
  - 对"Hu 框架是否包含手征"给出明确结论（是/否/部分），并给出理由
  - 至少 3 处原文引用（JCAP + Hu PRD）
- **回滚**：追加内容可回退
- **置信度**：0.70（需要同时理解 Hu PRD 和 JCAP 的公式体系，交叉难度较高）
- **依赖**：null（如果 P0-1 笔记已完成则依赖 P0-1 完成，否则作为独立任务需要自行查阅 Hu PRD）

---

## Subtask 5: 整合验证与置信度评审
- **输入**：Subtask 1-4 的输出（`note/P1-1-appendix-normalization.md` 的 §1-4 内容，以及任何额外产出）
- **输出**：`note/P1-1-appendix-normalization.md` 中 §5 + 最终评审报告：
  - §5：将所有补充内容整合为连贯的附录章节
  - 最终评审：对照 P1-1 的 10 项验收标准，逐条标注"已满足"并说明满足程度
  - 置信度总结：对整个 P1-1 理解任务的最终置信度评分
  - 列出仍存的未决问题（如果有）
  - 为 P3（三文献交叉对比）提供具体建议：哪些 P1-1 的结论可以直接用于 P3 的分析
- **验证**：
  - 10 项验收标准全部标注为"已满足"或"部分满足（原因）"
  - 最终置信度 ≥ 0.85（P1-1 核心理解应达到高置信度）
  - 评审报告中至少 3 条具体建议用于后续 P3
- **回滚**：此任务是评审性质，无副作用
- **置信度**：0.90（评审任务，难度低但需要全面覆盖）
- **依赖**：Subtask 1, Subtask 2, Subtask 3, Subtask 4（全部完成后方可执行）

---

## DAG 依赖图

```
Subtask 1: 验证圆极化基归一化         Subtask 2: Gamma^V 严格推导        Subtask 3: chi(f) 频谱特征      Subtask 4: Hu vs JCAP 对照
        │                                     │                                  │                                 │
        └──────────────┬──────────────────────┴──────────────────┬─────────────────┴────────────────────────┘
                       │                                        │
                       ▼                                        ▼
              ┌─────────────────────────────────────────────────────────┐
              │                                                         │
              ▼                                                         ▼
      可并行执行的基础推导                                      可并行执行的背景研究
      （Subtask 1 和 2 相互独立，可并行）                          （Subtask 3 和 4 相互独立，可并行）
                                                                        │
                                                                        ▼
                                                              ┌─────────────────────┐
                                                              │                     │
                                                              ▼                     ▼
                                                        Subtask 5:              （无额外任务）
                                                        整合验证与
                                                        置信度评审
                                                              │
                                                              ▼
                                                        P1-1 完成
                                                      (置信度评审通过)
```

**文本描述**：

| 子任务 | 依赖 | 可并行组 |
|--------|------|---------|
| Subtask 1 (归一化验证) | null | Group A（第一批并行） |
| Subtask 2 (Gamma^V 推导) | null | Group A（第一批并行） |
| Subtask 3 (chi 频谱) | null | Group B（第一批并行） |
| Subtask 4 (Hu vs JCAP) | null | Group B（第一批并行） |
| Subtask 5 (整合评审) | Subtask 1, 2, 3, 4 | Group C（最后执行） |

- **Group A**: Subtask 1 + Subtask 2 可同时执行（都是纯数学/张量推导）
- **Group B**: Subtask 3 + Subtask 4 可同时执行（都是信息搜集 + 分析）
- **Group C**: Subtask 5 必须等 Group A 和 B 全部完成
- **总并行度**：最高可达 4 个 agent 并行执行（Subtask 1-4 各一个）
- **串行瓶颈**：Subtask 5 是唯一串行末端

---

## 产出文件结构

所有补充内容追加到单一文件，保持组织简洁：

```
note/P1-1-chiral-physics.md        ← 主笔记（已完成，不修改）
note/P1-1-appendix-normalization.md ← 新增附录文件（Subtask 1-5 的产出）
  ├─ §1: 圆极化基归一化验证         (Subtask 1)
  ├─ §2: Gamma^V 宇称奇性严格推导   (Subtask 2)
  ├─ §3: chi(f) 频率依赖性分析      (Subtask 3)
  ├─ §4: Hu PRD vs JCAP ORF 对照   (Subtask 4)
  └─ §5: 整合验证与置信度评审       (Subtask 5)
```

---

## 质量标准

每个子任务完成后需满足对应质量标准（详见各子任务的"验证"字段）。

**整体质量标准**：
- [ ] Subtask 1-2: 所有代数推导至少 3 步，无可约简错误
- [ ] Subtask 3: 引用至少 2 篇非 JCAP 原始文献
- [ ] Subtask 4: 明确回答"Hu 框架是否包含手征 ORF"
- [ ] Subtask 5: 10 项验收标准全部标注，最终置信度 ≥ 0.85
- [ ] 所有 LaTeX 公式正确编译（无语法错误）

---

## 与全局任务架构的关系

本分解对应 `tasks/task-decomposition-v2.md` 中 P1 部分：

- 当前分解：P1-1 的后续深化工作（P1-1 base 已完成）
- P1-2 (chiral ORF)：在手征物理基础扎实后可启动 — 建议 P1-1 append §2 和 §4 完成后即启动
- P1-3 (数值结果)：依赖 P1-1 和 P1-2 的理论基础
- P3 (交叉对比)：Subtask 5 将提供直接建议

---

## 迭代历史

- **Iteration 1 (本文件)**: 基于 P1-1 base note 已完成的事实，分解后续深化工作。聚焦于推导严谨性、不确定项填补、以及跨文献对照。
