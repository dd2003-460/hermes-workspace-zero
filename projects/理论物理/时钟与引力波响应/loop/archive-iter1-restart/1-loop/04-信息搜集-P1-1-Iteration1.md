# 信息搜集 — P1-1 手征引力波物理基础 (Iteration 1)

> 阶段：1-loop/04（信息搜集）
> 按规格文件：`/Users/a1-6/Desktop/workspace/loop/1-loop/04-信息搜集.md` 执行
> 输入：`loop/1-loop/03-任务分解-P1-1-Iteration1.md`（5 个子任务）
> 输出：本文件（工具清单 + 新颖性评估 N0-N3）
> 状态：completed
> 创建时间：2026-07-07T18:30+0800

---

## Subtask 1: 验证圆极化基的归一化

### 可用工具

| 工具 | 可用性 | 说明 |
|------|--------|------|
| JCAP 原文 PDF (`raw/JCAP2025_Chiral.pdf`) | **可用** | 1.4 MB，包含 eq. 2.3-2.4 原始定义 |
| JCAP 原文文本 (`raw/JCAP2025_Chiral.txt`) | **可用** | 60 KB，可程序化搜索公式位置 |
| 已有笔记 (`note/P1-1-chiral-physics.md`) | **可用** | §1.2 已有圆极化基定义和物理直觉 |
| Python (numpy/scipy) | **可用** | numpy 2.4.4, scipy 1.17.1 — 可用于代数验证计算 |
| Seto PRL 97, 151101 (2006) | **需要获取** | JCAP 的 key reference，引用列表 [33] 中列出，原文未本地存档 |

### 背景知识评估

**充足**。笔记 §1.2 已经给出了：
- 圆极化基张量定义 (eq. 2.3)
- 圆极化光应变定义 (eq. 2.4)
- 物理直觉（测试粒子圆周运动图像）

Subtask 1 仅需要纯代数验证 $|h_R|^2 + |h_L|^2 = |h_+|^2 + |h_\times|^2$ 和交叉项为零。这是 undergraduate 级别的线性代数，背景知识完全充足。

**不确定项**（笔记 §8.1）：关于 $\sqrt{2}$ 归一化因子是否确保功率守恒的疑问 —— 这正是 Subtask 1 要回答的。

### 查重结果

- 已有笔记 §1.2 中包含了圆极化基的定义，但未做显式代数验证
- 已有代码 `scripts/09-olc-chiral-orf.py` 和 `scripts/11-multi-constellation-chiral-orf.py` 使用了圆极化基（包含 `h_R`/`h_L`），但验证逻辑不在代码中
- 记忆 16 (`memory/16-orlando-nonzeroRV-mirror-plane.md`) 讨论了 R^R(k) vs R^L(k) 的对称性，间接涉及圆极化基的使用
- **无重复实现**。纯代数验证在现有代码和笔记中均不存在

### 新颖性评估：N0

纯代数验证，不涉及任何创新。只是将已知定义代入并验证恒等式。

---

## Subtask 2: Gamma^V 宇称奇性的严格张量推导

### 可用工具

| 工具 | 可用性 | 说明 |
|------|--------|------|
| JCAP 原文 PDF (`raw/JCAP2025_Chiral.pdf`) | **可用** | eq. 2.10 给出 Gamma^V 的完整表达式 |
| JCAP 原文文本 (`raw/JCAP2025_Chiral.txt`) | **可用** | 行 280-290 附近有 Gamma^V 的定义，Appendix B.2 (行 ~1400+) 有详细推导 |
| 已有笔记 (`note/P1-1-chiral-physics.md`) | **可用** | §5.3 有镜面对称性的直觉论证，但非严格证明 |
| Python (numpy/scipy) | **可用** | 可用于数值验证：构造具体的 z+ 和 x+ 张量，计算 e^+e^x - e^x e^+ 在宇称变换下的行为 |
| 记忆 16 (`memory/16-orlando-nonzeroRV-mirror-plane.md`) | **可用** | 包含 R^V(k) 宇称奇性的详细讨论和镜面对称性论证 |
| 已有代码 (`scripts/debug_rv_zero.py`) | **可用** | 36 行，可能包含 R^V = 0 的数值验证 |
| Orlando arXiv:2011.07059 PDF (`note/Orlando-2021-arXiv2011.07059.pdf`) | **可用** | 验证 Orlando 的 R^V 计算与 JCAP 公式的一致性 |

### 背景知识评估

**基本充足，但有缺口**。笔记 §5.3 和记忆 16 已经建立了：
- 镜面对称性论证的物理直觉
- R^V(k) 在空间反演下变号的事实

但以下方面需要补充：
- **张量分量的变换律**：e^+_{ab}(k) 和 e^x_{ab}(k) 在 k -> -k 下的精确变换规则需要从头推导
- **LISA 构型的具体分析**：需要明确 LISA 的三个臂的几何结构来展示其镜面对称性
- **LISA-Taiji 交叉的具体计算**：两个探测器构型不同导致镜面对称性破缺的具体数学表述

**缺失知识点**：
1. 张量极化基在宇称变换下的精确变换律（需要从线性极化基的定义推导）
2. LISA 轨道构型的精确参数（倾角、航天器位置）—— 可用于数值验证

### 查重结果

- 已有笔记 §5.3 给出了镜像论证但**不是严格证明**
- 记忆 16 对 R^V 宇称奇性有深入讨论，但不涉及严格张量推导
- 已有代码 `scripts/debug_rv_zero.py` 可能有数值验证但未标注为推导
- JCAP Appendix B.2 包含 Gamma^V 的公式推导，是重要的参考资源
- Orlando paper 有 R^V 的数值计算但未涉及宇称奇性证明
- **严格张量推导在现有笔记中不存在**，是 Subtask 2 需要新增的内容

### 新颖性评估：N1

需要少量推导（张量分量的变换律），但基于 JCAP 和 Orlando 的已知结果。属于对已有理论的重新表述和严格化，不涉及新方法。

---

## Subtask 3: chi(f) 的频率依赖性与不同宇称破缺模型的频谱特征

### 可用工具

| 工具 | 可用性 | 说明 |
|------|--------|------|
| JCAP 原文 PDF/TXT | **可用** | §1 和 §4 简要列举了宇称破缺模型，但 chi(f) 频率依赖讨论有限 |
| JCAP 引用文献列表 | **可用** | 原文引用了 Alexander et al. 2006 (Leptogenesis), Satoh et al. 2008 (Chern-Simons), Cornwall 1997 (magnetic helicity), Callister et al. 2025 (propagation birefringence) |
| Seto PRL 97, 151101 (2006) | **需要获取** | 关于圆极化探测的前景分析，可能包含 chi 的频谱讨论 |
| Seto & Taruya 系列论文 (JCAP 2014, PRD 2015, PRD 2018, PRD 2019) | **需要获取** | 见 JCAP 引用 [29][34][37][46] |
| 已有笔记 (`note/P1-1-chiral-physics.md`) | **可用** | §4.1 列出了 3 种机制但**未讨论频率依赖性** |
| 已有笔记 (`note/手征-GW-ORF-文献调研2026.md`) | **可用** | 14 KB，可能包含文献调研信息 |
| Python (numpy/scipy) | **可用** | 可用于绘制 chi(f) 的预测曲线 |

### 背景知识评估

**不足，需要补充文献**。当前笔记 §4.1 仅列出了宇称破缺机制的名称和引用，但没有：
1. chi(f) 在各模型中的具体频率行为
2. 文献中对 chi(f) 频谱特征的分析
3. "手征光谱学"（通过频谱区分不同宇称破缺模型）概念的相关工作

**缺失知识点**：
1. Alexander-Peskin-Sheikh-Jabbari (2006) 中 chi(f) 的频率行为
2. Chern-Simons 引力中 chi(f) 的预测
3. 螺旋磁场湍流产生 GW 的手征频谱
4. 传播双折射中 chi(f) 的频率依赖
5. Seto 2006 和 Seto-Taruya 系列论文中对 chi 探测频率特性的分析

### 查重结果

- JCAP 原文本身对 chi(f) 频率依赖的讨论非常有限 —— 主要关注的是探测灵敏度而非频谱特征
- Seto 2006 (PRL) 是 JCAP 的主要引用，但原文未本地存档
- JCAP 引用 [28] Omiya-Seto 2024、[34] Seto-Taruya 2015、[37] Seto 2018、[46] Seto-Taruya 2015 都涉及圆极化/宇称分析，但原文未本地存档
- 已有笔记 `note/手征-GW-ORF-文献调研2026.md`（14 KB）可能包含部分文献调研结果，需要检查
- GitHub 上可能有 chiral GW 模拟代码（如 LISA 数据分析工具链），但需要进一步搜索
- **Subtask 3 的核心信息（chi(f) 频谱）在现有材料中基本缺失**

### 新颖性评估：N2

需要查阅至少 2 篇非 JCAP 原始文献（Alexander et al., Seto et al., Cornwall et al. 等），分析不同宇称破缺模型中 chi(f) 的频率行为。这涉及到跨文献的信息综合和理论分析，需要中等程度的创新——即将不同模型的预测统一到"手征光谱学"的框架下进行对比。

---

## Subtask 4: 手征 ORF (Gamma^V) 与通用 ORF (Hu PRD) 的形式对照

### 可用工具

| 工具 | 可用性 | 说明 |
|------|--------|------|
| Hu PRD 原文 PDF (`raw/PhysRevD.111.084065(1).pdf`) | **可用** | 816 KB，完整通用 ORF 框架 |
| Hu PRD 原文文本 (`raw/PhysRevD.111.084065(1).txt`) | **可用** | 72 KB，可程序化搜索 |
| JCAP 原文 PDF/TXT | **可用** | eq. 2.9-2.10 的 Gamma^I 和 Gamma^V 定义 |
| 已有笔记 (`note/P1-1-chiral-physics.md`) | **可用** | §7 对比分析薄弱（仅 4 行） |
| 已有笔记 (`note/OLC与手征引力波_对比分析报告.md`) | **可用** | 13 KB，可能包含 OLCO vs 手征 ORF 的对比 |
| 已有笔记 (`note/手征-GW-ORF-文献调研2026.md`) | **可用** | 可能包含 ORF 定义的对比信息 |
| Python 代码 (`scripts/01-olc-orf-solver.py`, `scripts/09-olc-chiral-orf.py`) | **可用** | 展示了 ORF 计算的代码实现，可用于反向推断公式 |
| 已有代码 (`scripts/11-multi-constellation-chiral-orf.py`) | **可用** | 40 KB，最完整的 chiral ORF 实现 |

### 背景知识评估

**基本充足但有缺口**。已知的关键发现：

**Hu PRD 不包含手征 ORF**：在 66 KB 的 Hu PRD 文本中搜索，"chiral" 出现 0 次，"parity" 出现 0 次，"helicity" 出现 0 次。Hu 的 ORF 公式仅处理宇称偶情况。

已有的理解：
- Hu 的通用 ORF 公式给出的是 $R_{ij}(\hat{k})$，是一个实数函数
- JCAP 将 ORF 分解为 $\Gamma^I$（宇称偶）和 $\Gamma^V$（宇称奇）两部分
- 复数形式 $R = R^I + i R^V$ 的对应关系在理论上可能成立

**缺失知识点**：
1. Hu PRD 中 ORF 定义的完整数学表述（需要从原文精读）
2. Hu 的探测器张量定义与 JCAP 的对比
3. OLC 探测器张量在 Hu 框架和 JCAP 框架中的具体代入结果
4. Hu PRD 中空间相位因子与 JCAP 的 exp(-ik.delta.x) 的统一性

### 查重结果

- 已有笔记 §7 仅有 4 行对比，远不够充分
- 已有笔记 `note/OLC与手征引力波_对比分析报告.md`（13 KB）可能包含部分对比，需要确认其内容
- 已有代码 `scripts/09-olc-chiral-orf.py` 中实现了 JCAP 风格的 Gamma^V 计算
- 记忆 15 和 16 涉及 chi_orb 和 R^V 的对比但不涉及 Hu PRD 的对照
- **Hu PRD vs JCAP 的显式公式对照在现有材料中不存在**，是 Subtask 4 需要新增的内容

### 新颖性评估：N2

需要同时精读 Hu PRD 和 JCAP 两篇文献的公式体系，进行显式对照。关键点在于回答"Hu 的通用框架能否包含手征 ORF"，这需要：
1. 理解 Hu 的 R_{ij} 定义与 JCAP 的 Gamma 定义是否等价
2. 分析 Hu 框架在宇称破缺介质中是否自然产生虚部
3. 对 OLC 探测器分别用 Hu 和 JCAP 公式代入计算并对比

这需要中等程度的理论分析创新，属于跨文献的框架统一尝试。

---

## Subtask 5: 整合验证与置信度评审

### 可用工具

| 工具 | 可用性 | 说明 |
|------|--------|------|
| Subtask 1-4 的输出 | **依赖 Subtask 1-4 完成** | 追加到 `note/P1-1-appendix-normalization.md` |
| P1-1 验收标准列表 | **可用** | 来自 `loop/1-loop/03-任务分解-P1-1-Iteration1.md`，10 项 AC |
| 已有笔记 (`note/P1-1-chiral-physics.md`) | **可用** | 包含对 10 项 AC 的已有覆盖评估 |
| P3 相关笔记规划 | **可用** | `tasks/task-decomposition-v2.md` 中 P3 的部分 |

### 背景知识评估

**充足**。Subtask 5 是评审性质的任务，不需要额外的文献阅读或推导。它依赖于 Subtask 1-4 的输出，对这些输出进行整合和验证。

### 查重结果

- 无重复，这是唯一的整合评审任务
- 已有笔记的验收标准评估（来自任务分解文件的表格）可直接作为 Subtask 5 的起点

### 新颖性评估：N0

纯评审任务，不涉及任何创新。

---

## 总体评估

### 工具就绪度：complete

| 资源类别 | 状态 | 说明 |
|----------|------|------|
| 原始 PDF 文献 | **全部可用** | JCAP PDF + Hu PRD PDF + 楼论文 PDF 均在 raw/ 目录 |
| 原始文本提取 | **全部可用** | 三个 PDF 均有 .txt 提取版本 (72 KB / 60 KB / 119 KB) |
| 已有理解笔记 | **部分可用** | P1-1-chiral-physics.md 完整；P0-1-hu-prd-understanding.md 尚未创建；P1-2/P1-3 笔记不存在 |
| 已有代码 | **全部可用** | 14 个 Python 脚本，包含 ORF 计算、噪声谱、SNR、chiral ORF、多星座分析 |
| 已有记忆 | **部分可用** | 记忆 15 和 16 有相关物理分析；多数记忆因 bug 前代码问题被标记为废弃 |
| 补充参考文献 | **需要获取** | Seto 2006 (PRL)、Alexander 2006、Satoh 2008、Cornwall 1997 等 5+ 篇引用未本地存档 |
| Python 科学计算栈 | **全部可用** | numpy 2.4.4, scipy 1.17.1, matplotlib 3.10.9 |

### 阻塞项

1. **Seto 2006 (PRL 97, 151101) 原文未本地存档**：这是 JCAP 最关键的引用文献，也是 Subtask 3 中 chi(f) 频谱分析的主要参考来源
2. **Hu PRD 不含手征内容**：这本身是重要发现（Subtask 4 的预期结果），但意味着 Subtask 4 的"Hu 框架包含手征"部分需要基于 Hu PRD 的通用公式进行反证分析
3. **P0-1 理解笔记尚未创建**：Subtask 4 需要 Hu PRD 的理解作为输入，但由于 Hu PRD 不涉及手征，Subtask 4 可以直接基于 Hu PRD 原文进行分析，不依赖 P0-1 笔记

### 新颖性评估：N1-N2 分布

| 子任务 | 新颖性 | 说明 |
|--------|--------|------|
| Subtask 1 | N0 | 纯代数验证 |
| Subtask 2 | N1 | 严格化已有直觉，少量张量推导 |
| Subtask 3 | N2 | 跨文献信息综合，手征光谱学框架 |
| Subtask 4 | N2 | 跨文献框架对照，Hu 是否包含手征的分析 |
| Subtask 5 | N0 | 纯评审任务 |

**整体新颖性**：N2（主要受 Subtask 3 和 4 拉动）。Subtask 1、2、5 属于巩固性/深化性工作，Subtask 3 和 4 涉及跨文献的综合分析，具有中等程度的新颖性。

### 并行度

- Group A（Subtask 1 + Subtask 2）：两个纯数学/张量推导，相互独立，可并行
- Group B（Subtask 3 + Subtask 4）：两个信息搜集+分析，相互独立，可并行
- Group C（Subtask 5）：必须等 Subtask 1-4 全部完成

最大并行度：4 个 agent 同时执行 Subtask 1-4。

---

## 信息搜集结论

P1-1 Iteration 1 的信息搜集工作表明：

1. **核心资源充足**：JCAP 原文 PDF+txt、Hu PRD 原文 PDF+txt、已有代码和笔记都已就位
2. **Subtask 1 和 2 可立即启动**：基于已有的 P1-1-chiral-physics.md 笔记和 JCAP 原文即可开始
3. **Subtask 3 需要额外文献获取**：Seto 2006、Alexander 2006 等关键引用需要 arXiv 获取
4. **Subtask 4 的关键发现已可预判**：Hu PRD 不含手征内容（chiral/parity/helicity 计数均为 0），这本身是对"Hu 框架是否包含手征"的直接回答 —— 答案是否定的
5. **Subtask 5 依赖明确**：仅依赖 Subtask 1-4 的产出，无外部依赖
