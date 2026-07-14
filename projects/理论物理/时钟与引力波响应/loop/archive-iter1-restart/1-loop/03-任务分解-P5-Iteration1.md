# 03-任务分解-P5-Iteration1

> **Phase 5: 文献驱动的论文审查 (Literature-driven Paper Review)**
> 基于 02-目标澄清-P5-Iteration1.md + 两个 sub-brain critiques
> **分解时间**: 2026-07-08
> **前置条件**: Phase 4 Iter2 全部 7+ 修正已验证通过

---

## 1. Phase 5 核心问题修正

### 1.1 原始定位（来自 02 文件）
> "Phase 5 的核心问题是：在理解材料与 Phase 4 修正完成后，论文章节是否充分且正确地反映了对原始三篇文献的理解？这是一个回溯性验证阶段——不是去发现新的物理，而是审查已写内容是否忠实于已理解的知识。"

### 1.2 Sub-brain 修正后的定位

Phase 5 必须同时处理两类问题：
1. **结构性/数值性致命项**（来自两个 sub-brain critique）
2. **文献一致性审查**（来自原始 02 文件）

### 1.3 Phase 5 新范围

Phase 5 分为 **P0: 阻塞条件修复** + **P1: 文献审查**

P0 是 Phase 5 的前置子任务——如果 P0 不完成，P1 的审查没有意义（审查一个有数值错误的论文没有价值）。

---

## 2. 任务分解 (DAG)

```
P5_START
  |
  +-> SUB-5.0: [P0] SNR 独立验算 + 致命项修复  ← 阻塞 Phase 5 核心
  |    |
  |    +-> 5.0-A: 独立计算 SNR 公式数值（Python，使用正确 H_0 和 L）
  |    +-> 5.0-B: 对比论文 line 1253/1264 逐项值
  |    +-> 5.0-C: 修复论文 line 1260/1264/1268 的计算错误
  |    +-> 5.0-D: 修复 line 1282 (SNR_single = 1.3e-4 vs 5.1e-4)
  |    +-> 5.0-E: 修复 line 1290 (N_sat 计算，2.4万 vs 3.3万)
  |    +-> 5.0-F: 验证星座表 (line 1416-1418) 与 SNR_single 的关系
  |    +-> 5.0-G: 验证 H_0 计算 (line 1260: 1.4e-37 vs 2.29e-36)
  |
  +-> SUB-5.1: [P0] 代码-论文同步验证  ← 阻塞
  |    |
  |    +-> 5.1-A: 检查 03-olc-snr-solver.py 的 L_olc 值
  |    +-> 5.1-B: 检查 gamma_olc = -0.188 的来源
  |    +-> 5.1-C: 运行方位角扫描 (phi_g: 0 -> 2pi) 验证 chiral ORF 对称性
  |    +-> 5.1-D: 如代码有 bug，决定：修复代码 or 标记已知限制
  |
  +-> SUB-5.2: [P1] 补充 JCAP 2025 交叉分析理解  ← 有依赖关系
  |    |
  |    +-> 5.2-A: 访问 arXiv:2410.18916 (Chen-Liu-Zhang)
  |    +-> 5.2-B: 提取 JCAP eq. (2.2) 矩阵形式 (I/V Stokes 参数)
  |    +-> 5.2-C: 提取交叉相关统计量 Y 的期望值推导
  |    +-> 5.2-D: 提取 SNR 公式及其推导
  |    +-> 5.2-E: 输出 note/JCAP2025-cross-analysis-understanding.md
  |
  +-> SUB-5.3: [P1] 补充 Lou 硕士论文 OLC 构型分析理解  ← 有依赖关系
  |    |
  |    +-> 5.3-A: 定位 Lou 硕士论文文件路径
  |    +-> 5.3-B: 提取 OLC transfer function 的 sinc 推导
  |    +-> 5.3-C: 提取构型变换不变性论证
  |    +-> 5.3-D: 提取各 ORF 极小值的物理解释
  |    +-> 5.3-E: 输出 note/Lou-thesis-olc-configuration-understanding.md
  |
  +-> SUB-5.4: [P1] 论文-理解材料一致性审查  ← 依赖 5.2 和 5.3
  |    |
  |    +-> 5.4-A: 审查 Ch3.5 Gamma^V 证明 vs P1-1
  |    +-> 5.4-B: 审查 Ch4 SNR 公式 vs 5.2 (JCAP 理解)
  |    +-> 5.4-C: 审查 Ch2.3 transfer function vs P2-1 + 5.3 (Lou)
  |    +-> 5.4-D: 审查所有引用自洽性
  |    +-> 5.4-E: 审查参数数值 (arm length, T_obs, noise) 与原始文献一致
  |    +-> 5.4-F: 审查共面构型的 Gamma^V = 0 是否充分讨论
  |    +-> 5.4-G: 审查学术新颖性（与 Ganapathy 2026 和 Schaffrath 2025 对比）
  |
  +-> SUB-5.5: [P1] Gap 评估与 Phase 6 决策  ← 依赖 5.0-5.4
       |
       +-> 5.5-A: 综合 5.0-5.4 的验收结果
       +-> 5.5-B: 输出 loop/1-loop/05-完备核验-P5-Iteration1.md
       +-> 5.5-C: Phase 6 决策: completed / needs_replan / completed_with_branches
```

---

## 3. 阻塞条件 (Blocking Conditions)

来自两个 sub-brain critiques，汇总并更新状态：

| # | 条件 | 状态 | 来源 |
|---|------|------|------|
| **B1** | SNR 4.4.2 vs 4.6.2 数值鸿沟（44 阶数量级差异） | **未解决** — sub-brain 已独立验证 | sub-brain a8fb3011 / a97399fd |
| **B2** | 代码-论文同步（03-olc-snr-solver.py 仍用 L_olc=10.0） | **未解决** | sub-brain a8fb3011 |
| **B3** | 方位角对称性检验（phi_g 扫描验证 Gamma^V 共面=0） | **未解决** | sub-brain a8fb3011 |
| **B4** | H_0 计算错误（1.4e-37 vs 2.29e-36） | **未解决** — 独立验证确认 | sub-brain a97399fd |
| **B5** | SNR_single 值不一致（1.3e-4 vs 5.1e-4） | **未解决** — line 1268 vs 1282 | sub-brain a97399fd |
| B6 | JCAP 2025 和 Lou 论文的理解文件缺失 | 已在 5.2/5.3 中计划补充 | 02 文件 |
| B7 | 手征分析（Gamma^V=0 对所有计算构型）占论文 300 行但贡献可能为零 | 已在 5.4-G 中计划审查 | sub-brain a97399fd |

**必须全部解决 B1-B5 后才能进行 5.4。**

---

## 4. 子任务分配

### SUB-5.0: SNR 独立验算 + 致命项修复 (P0 — 阻塞)
- **目标**: 独立计算 SNR，确认 44 阶差异，修复论文计算
- **关键文件**: `paper/main-paper.tex` (line 1253-1418), `scripts/03-olc-snr-solver.py`
- **验收**:
  - [ ] 独立 Python 计算确认 product = 3.264e-52, sqrt = 1.807e-26
  - [ ] paper main-paper.tex line 1260: H_0 计算修正 (1.4e-37 -> 2.29e-36)
  - [ ] paper main-paper.tex line 1264: 乘积计算修正
  - [ ] paper main-paper.tex line 1268: SNR_single 值修正
  - [ ] paper main-paper.tex line 1282: 4.4.3 中 SNR_single 值修正 (1.3e-4 -> 修正后值)
  - [ ] paper main-paper.tex line 1290: N_sat 计算修正 (2.4万 -> 正确值)
  - [ ] paper main-paper.tex line 1300-1303: 表格数值修正
  - [ ] paper main-paper.tex line 1416-1418: 星座表数值修正
- **置信度评估**: 0.50 — 因为数值体系全面崩盘，需要重新校准整个 SNR 段落

### SUB-5.1: 代码-论文同步 (P0 — 阻塞)
- **目标**: 验证并同步代码与论文的数值一致性
- **关键文件**: `scripts/03-olc-snr-solver.py`, `scripts/10-olc-chiral-orf-triangular.py`, `scripts/11-multi-constellation-chiral-orf.py`
- **验收**:
  - [ ] 确认 gamma_olc = -0.188 的来源（硬编码 vs 计算）
  - [ ] phi_g 扫描测试（0 -> 2pi）验证 chiral ORF 对称性
  - [ ] 共面构型 Gamma^V 是否确实为零
  - [ ] 如代码有 bug，决定是否修复并更新
- **置信度评估**: 0.60 — phi_g 扫描是直接可验证的，但 gamma_olc 来源可能需要追溯到更底层

### SUB-5.2: JCAP 2025 交叉分析理解 (P1)
- **目标**: 补充 JCAP arXiv:2410.18916 交叉分析理解
- **关键文件**: arXiv:2410.18916 (Chen-Liu-Zhang, JCAP 05(2025)050)
- **产出**: `note/JCAP2025-cross-analysis-understanding.md`
- **验收**:
  - [ ] 完整推导交叉相关统计量 Y 的期望值和方差
  - [ ] SNR 公式与论文 Ch4（修正后）一致
  - [ ] 与 P1-1 手征部分衔接
  - [ ] 关键公式引用 JCAP 原文 page + equation number
- **置信度评估**: 0.70 — arXiv 论文可访问，但 P1-1 可能存在概念混淆（Kato & Soda vs JCAP）

### SUB-5.3: Lou 硕士论文 OLC 构型理解 (P1)
- **目标**: 补充 Lou 硕士论文 OLC 构型 ORF 分析理解
- **关键文件**: 需定位 Lou 论文文件
- **产出**: `note/Lou-thesis-olc-configuration-understanding.md`
- **验收**:
  - [ ] OLC transfer function 的 sinc 形式推导
  - [ ] 构型变换不变性论证
  - [ ] 各 ORF 极小值的物理解释
- **置信度评估**: 0.55 — Lou 论文未在 memory 中记录具体引用信息

### SUB-5.4: 论文-理解材料一致性审查 (P1)
- **目标**: 逐项检查论文 vs 理解材料
- **前置条件**: 5.0 (致命项修复) 完成 + 5.2 (JCAP 理解) 完成 + 5.3 (Lou 理解) 完成
- **验收**:
  - [ ] AC1-AC10 (来自 02 文件的验收标准表)
  - [ ] 特别审查：4.4.2 与 4.6.2 的 SNR 数值现在一致
  - [ ] 特别审查：chiral ORF 数值是否在 azimuth bug 修复后重新计算
- **置信度评估**: 0.65 — 如果理解材料本身有错，审查可能"一致但错误"（sub-brain 的闭环验证问题）

### SUB-5.5: Gap 评估与 Phase 6 决策 (P1)
- **目标**: 基于 5.0-5.4 的产出，判断论文状态和下一步
- **验收**:
  - [ ] 输出 05-完备核验-P5-Iteration1.md
  - [ ] Gap 评估置信度 >= 0.80
  - [ ] Phase 6 决策有明确依据
- **置信度评估**: 0.60 — 依赖 5.0-5.4 的结果，不确定性传递

---

## 5. Sub-brain 建议的替代方案整合

Sub-brain a97399fd 提出了三个替代方案，本分解已整合：

| Sub-brain 方案 | 整合位置 | 说明 |
|----------------|---------|------|
| **A: 独立推导** | SUB-5.0 | 独立 Python 验算本身就是"反证法"——从第一性原理推导，不假设理解材料正确 |
| **B: 致命项审查** | SUB-5.0 + SUB-5.1 | 聚焦 B1-B5，跳过形式问题 |
| **C: 读者视角审查** | SUB-5.4 | 5.4-G 审查学术新颖性，5.4-D/E 审查推导链路的可追踪性 |

---

## 6. 执行顺序与并行性

```
[5.0] SNR 独立验算       [5.1] 代码同步验证     [5.2] JCAP 理解         [5.3] Lou 理解
  |                         |                     |                     |
  |                         |                     |                     |
  +---+---------------------+---------------------+---------------------+
      |                                                     |
      v                                                     v
  [5.4] 论文-理解一致性审查  <-------------------------------+
      |
      v
  [5.5] Gap 评估 + Phase 6 决策
```

- **5.0, 5.1, 5.2, 5.3 可并行启动**（P0 阻塞项独立于 P1 理解补充）
- **5.4 依赖 5.0 + 5.2 + 5.3**（必须致命项修复完毕 + 补充理解完成）
- **5.5 依赖 5.4**

---

## 7. 执行策略

### 7.1 推荐的 Agent 分配

| 子任务 | Agent 类型 | 调度方式 |
|--------|-----------|---------|
| SUB-5.0 | executor (代码执行) | Agent tool, background |
| SUB-5.1 | executor (代码执行) | Agent tool, background |
| SUB-5.2 | gatherer (文献搜索+理解) | Agent tool, background |
| SUB-5.3 | gatherer (文献搜索+理解) | Agent tool, background |
| SUB-5.4 | verifier (审查) | 待 5.0/5.2/5.3 完成后调度 |
| SUB-5.5 | decision-maker (决策) | 待 5.4 完成后调度 |

### 7.2 执行优先级

1. **第一优先级**: SUB-5.0 (SNR 独立验算 + 致命项修复) — 阻塞全部后续
2. **第二优先级**: SUB-5.1 (代码同步) + SUB-5.2 (JCAP) + SUB-5.3 (Lou) 并行
3. **第三优先级**: SUB-5.4 (一致性审查) — 依赖 1+2
4. **第四优先级**: SUB-5.5 (决策) — 依赖 3

### 7.3 关于"闭环验证"问题的处理

Sub-brain 提出的核心认识论危机——"AI 生成的理解材料审查 AI 生成的论文 = 闭环验证"——在 SUB-5.0 中得到部分缓解：

- SUB-5.0 使用**独立 Python 验算**（反证法）替代"理解材料 vs 论文"对比
- 数值错误的修复不依赖理解材料，而是依赖第一性原理的计算
- SUB-5.4 的审查仍然有闭环风险，但只在数值体系已被独立验证的基础上进行

**关键区分**: SUB-5.0 是"独立验证"，SUB-5.4 是"一致性审查"。前者产生客观正确结果，后者只判断文本一致性。

---

## 8. 置信度总评估

| 阶段 | 置信度 | 说明 |
|------|--------|------|
| SUB-5.0 | 0.50 | SNR 数值体系全面崩盘，修正工作量不确定 |
| SUB-5.1 | 0.60 | 代码修改范围可预估，但 azimuth bug 影响范围不确定 |
| SUB-5.2 | 0.70 | arXiv:2410.18916 可访问，但概念理解风险 |
| SUB-5.3 | 0.55 | Lou 论文定位不确定，理解深度不确定 |
| SUB-5.4 | 0.65 | 闭环验证问题未完全解决 |
| SUB-5.5 | 0.60 | 取决于前置任务结果 |
| **Phase 5 总置信度** | **~0.55** | 不高于初始评估，因为独立验证确认了更严重的数值问题 |

---

*Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>*
