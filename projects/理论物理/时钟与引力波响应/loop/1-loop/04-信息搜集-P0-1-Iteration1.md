# Tool Inventory — P0-1 Hu PRD 111.084065 理解

**所属规格**: `/Users/a1-6/Desktop/workspace/loop/1-loop/04-信息搜集.md`
**对应目标**: P0-1（来自 `tasks/task-decomposition-v2.md`）
**输入**: `loop/1-loop/03-任务分解-P0-1-Iteration1.md`（8 个原子子任务 ST1-ST8）
**状态**: in_progress

---

## Subtask ST1: Hu PRD 第 1 章理解 — ORF 物理直觉与通用框架动机

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — Hu PRD 全文文本（主要信息源）
  2. `raw/PhysRevD.111.084065(1).pdf` — Hu PRD PDF（辅助查看公式排版）
  3. `note/workspace-019f3b66-7691-7c5d-9acc-9ae6c6db9031/physrevd_text.txt` — 另一版本 Hu PRD 文本（73KB，已提取）
  4. `note/手征引力波ORF精确计算_研究路线图.md` — 包含 Hu PRD 第 1 章动机概述（"PRD 论文发明了一套万能钥匙..."）
  5. `note/OLC与手征引力波_对比分析报告.md` — 包含 Hu PRD 公式定位表（`| PRD | ... 万能钥匙 |`）

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt | 可用（2023 行，72KB） |
  | Hu PRD pdf | 可用（815KB） |
  | 路线图笔记 | 可用（含相关概述） |
  | 对比分析报告 | 可用 |

- **背景知识**: 充足
  - 已有 ORF 物理直觉理解（从 `memory/03-olc-orf-results-summary.md` 可知项目已掌握 ORF 作为几何因子的基本概念）
  - 已有 Tomassini 小天线近似的基本了解（通过 Hu PRD 第 1 章的引用）
  - 缺失: Tomassini (2007) 原文 PDF 不可用，但 Hu PRD 第 1 章已详细阐述了 Tomassini 近似及其局限，不影响 ST1 的完成

- **查重结果**: `note/手征引力波ORF精确计算_研究路线图.md` 第 1 节（环节A）已包含 ORF 物理直觉概述。但 ST1 需要以 Hu PRD 原文为第一手信息源逐章梳理，路线图笔记是基于理解的二手摘要，不能作为产出替代。产出是纯原创理解笔记，不存在重复实现问题。

- **新颖性**: **N1**（需要少量调整或组合 — 主要是对原文第 1 章的解读和通俗化解释，不涉及公式推导）

---

## Subtask ST2: 通用单向链路 ORF 推导 — 天空积分分解 + I1 留数计算

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — 第 2 章（General Formulation），包含 Eq.(6)-(24)、Eq.(16) 五个极点、Eq.(18) I1 结果
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本可用于检查公式排版
  3. `note/workspace-019f3b66-7691-7c5d-9acc-9ae6c6db9031/physrevd_text.txt` — 替代文本
  4. `note/手征引力波ORF精确计算_研究路线图.md` — 包含详细的留数定理推导路线（Step 3-4 节），包括极点位置、围道选择、复指数积分函数 Ei 等
  5. `scripts/01-olc-orf-solver.py` — 实现单向链路响应函数（Eq.6 中的 transfer function），代码中有注释 `One-way link transfer function for OLC (Lou Eq. 2-30)`

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（第 2 章） | 可用（文本中包含 Eq.(6), (8), (10)-(24) 等全部关键公式引用） |
  | Hu PRD pdf | 可用 |
  | 路线图推导笔记 | 可用（含留数定理推导详细路线） |
  | 01-olc-orf-solver.py | 可用（单向链路实现，可作代码对比） |
  | Tomassini 原文 | 不可用（需要时可通过 arXiv 获取） |

- **背景知识**: 基本充足，但有不足
  - 充足部分: 引力波与探测器响应的基本物理（GR 微扰理论）、天空积分的基本概念
  - 不足部分:
    - **复平面留数定理的详细计算**: 需要仔细跟踪 Hu PRD 中 z0-z4 五个极点的围道选择和留数计算，特别是 Ei 函数（复指数积分）的引入过程。路线图笔记虽有大框架，但缺中间步骤细节
    - **复指数积分函数 Ei**: 项目中没有现成的关于 Ei 函数的笔记。需要理解为什么天空积分中频率相关的指数项会导致 Ei 函数（留数计算的自然结果）

- **查重结果**: `note/手征引力波ORF精确计算_研究路线图.md` 包含大量与 ST2 相关的推导路线，但：
  - 路线图是针对 JCAP 手征 ORF（Gamma^V）的推导框架，对 Hu PRD（Gamma^I）的推导只有框架性概述
  - ST2 的产出是针对 Hu PRD 原文的逐公式理解，不是路线图笔记的简单复制
  - 路线图中 Step 3（变量代换与留数定理）提到 "PRD论文式16 给出的 z0,...,z4 公式对 xi_I 和 xi_V 应该是通用的"——这正是 ST2 需要验证的内容

- **新颖性**: **N1**（对原文公式的解读和通俗化，路线图中已有类似推导但需要完全基于 Hu PRD 原文重新推导）

---

## Subtask ST3: PTA ORF 推导 — 完整表达式与 Hellings-Downs 曲线恢复

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — 第 3 章（PTA ORF），包含 Eq.(26) 完整表达式、Eq.(27) HD 曲线
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本
  3. `note/手征引力波ORF精确计算_研究路线图.md` — 第 2.3 节包含 HD 曲线的背景说明（"短波近似"）
  4. `memory/03-olc-orf-results-summary.md` — 包含 HD 曲线与 ORF 平坦性的讨论
  5. `scripts/debug_hd.py` — 专门验证 HD 曲线的调试脚本
  6. `scripts/validate_hd.py` — HD 曲线验证脚本
  7. Tomassini (2007) 原始文献: **不可用**（但 HD 曲线本身是 Hellings & Downs 1983 的经典结果，物理内容已知）

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（第 3 章） | 可用 |
  | Hu PRD pdf | 可用 |
  | 路线图笔记 | 可用 |
  | debug_hd.py | 可用（但为旧代码，基于 bug 前版本） |
  | validate_hd.py | 可用（但为旧代码，基于 bug 前版本） |
  | memory/03（HD 与 ORF 平坦性） | 可用 |
  | Tomassini 原文 | 不可用 |

- **背景知识**: 充足
  - Hellings-Downs 曲线是 PTA 领域的标准结果，项目记忆中已有相关讨论
  - Hu PRD 第 3 章是通用公式的最直接特例（PTA 的单向链路），推导逻辑清晰
  - 路线图笔记中已包含 "PRD 论文把这套精确解应用回 PTA 情形（令 alpha=0），严格证明它退化为经典的 Hellings-Downs 曲线加上脉冲星项修正"

- **查重结果**: 
  - `memory/03-olc-orf-results-summary.md` 讨论了 OLC ORF 在 d=0 时的平坦性及其与 HD 曲线的关系，但这是 OLC 特定结论
  - ST3 的产出是针对 Hu PRD 原文第 3 章的系统理解（从 Eq.26 到 Eq.27 的退化过程、脉冲星项物理含义等），与现有笔记不重复
  - `debug_hd.py` 和 `validate_hd.py` 是代码实现，不是理解性笔记

- **新颖性**: **N0**（PTA/ORF 是引力波数据分析中的标准主题，HD 曲线是已知经典结果。ST3 主要是原文复述和通用公式的特例推导，无需创新）

---

## Subtask ST4: GbLI ORF — 两向链路表示及其与单向链路的关系

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — 第 4 章前半部分（GbLI），包含 Eq.(33)-(35)
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本
  3. `note/手征引力波ORF精确计算_研究路线图.md` — 包含 GbLI 框架说明
  4. `scripts/01-olc-orf-solver.py` — 有单向链路实现，可作为对比基础
  5. `note/OLC引力波科普.md` — 包含科普级别的两向链路物理描述
  6. Tomassini (2007) 原文: **不可用**（小天线近似 T_two ≈ 2iβ 的来源）

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（第 4 章前半） | 可用 |
  | Hu PRD pdf | 可用 |
  | 路线图笔记 | 可用 |
  | 01-olc-orf-solver.py | 可用（单向链路部分） |
  | OLC科普笔记 | 可用（科普级物理描述） |
  | Tomassini 原文 | 不可用 |

- **背景知识**: 基本充足
  - 激光干涉仪基本原理是已知知识（LIGO/LISA 常识）
  - 两向链路 vs 单向链路的区别在 Hu PRD 中有详细阐述
  - 不足: Tomassini (2007) 的"小天线近似"推导不可用。但 Hu PRD 中已有对近似与精确方法的对比讨论（grep 发现 `raw/PhysRevD.111.084065(1).txt` 第 1207 行 "based on small antenna approximation can be used to"）

- **查重结果**: 
  - 路线图笔记包含 GbLI 的框架说明
  - `OLC引力波科普.md` 有科普级描述但数学深度不足
  - ST4 产出（公式级理解笔记）与现有笔记不重复

- **新颖性**: **N1**（主要是 Hu PRD 第 4 章原文的理解和通俗化解释，公式结构已由 Hu 给出）

---

## Subtask ST5: SbLI ORF — TDI 通道展开与归一化

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — 第 4 章后半部分（SbLI/LISA），包含 Eq.(38)-(40)
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本
  3. `note/手征引力波ORF精确计算_研究路线图.md` — 包含 SbLI/手征 ORF 相关内容
  4. `scripts/06-olc-lisa-mixed-network.py` — LISA 混合网络实现
  5. `scripts/06a-patched-mixed-network.py` — LISA 混合网络补丁版本
  6. `note/论文-第1-2章.md`、`论文-第3-4章.md`、`论文-第5-7章.md` — 论文草稿中的 SbLI 相关内容

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（第 4 章后半） | 可用 |
  | Hu PRD pdf | 可用 |
  | 路线图笔记 | 可用 |
  | 06-olc-lisa-mixed-network.py | 可用 |
  | 06a-patched-mixed-network.py | 可用 |
  | 论文草稿 | 可用 |
  | LISA TDI 手册/文档 | 不可用（需外部获取） |

- **背景知识**: 基本充足但有不足
  - 充足: GbLI 基础（ST4 的输出）、LISA 三角构型常识
  - 不足:
    - **TDI（Time Delay Interferometry）** 的详细理论: LISA 的 TDI 通道（Michelson X/Y/Z, A/E/T）是 LISA 数据处理的核心技术。项目中有 `scripts/06-olc-lisa-mixed-network.py` 等代码涉及 LISA，但缺乏 TDI 理论的专门笔记
    - SbLI 的轨道运动引入的额外相位: Hu PRD 第 4 章后半部分有详细阐述

- **查重结果**:
  - 路线图笔记对 SbLI 有提及但深度有限
  - `scripts/06-olc-lisa-mixed-network.py` 等是代码而非理解性笔记
  - ST5 产出（基于 Hu PRD 原文的公式级理解）与现有笔记不重复

- **新颖性**: **N1**（主要是 Hu PRD 原文的理解，TDI 通道的物理含义需要额外的 LISA 知识背景）

---

## Subtask ST6: 参数代换规则 — I2, I3, I4 从 I1 导出

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — 第 2 章 Eq.(18) 到 Eq.(21)-(23)，参数代换规则
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本
  3. `note/手征引力波ORF精确计算_研究路线图.md` — Step 4 提到 "极点位置完全由 u_hat, v_hat 的方向决定"
  4. `note/workspace-019f3b66-7691-7c5d-9acc-9ae6c6db9031/physrevd_text.txt` — 替代文本

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（Eq.18-23） | 可用（文本中明确包含） |
  | Hu PRD pdf | 可用 |
  | 路线图笔记 | 可用（相关框架） |

- **背景知识**: 充足
  - 参数代换规则是纯数学操作，依赖 ST2 的 I1 结果
  - 几何含义（向量合成 alpha2 = |alpha*n_hat + beta*u_hat|）是已知的线代知识
  - Hu PRD 中该部分的推导是直接的公式代换，物理复杂度低

- **查重结果**: 无重复实现问题。这是 Hu PRD 中明确的数学步骤。

- **新颖性**: **N0**（纯公式代换操作，Hu PRD 已给出完整的代换规则，无需创新）

---

## Subtask ST7: Tomassini 小天线近似对比

- **可用工具**:
  1. `raw/PhysRevD.111.084065(1).txt` — Hu PRD 中讨论近似的段落（grep 发现第 1207 行包含 "small antenna approximation"）
  2. `raw/PhysRevD.111.084065(1).pdf` — PDF 版本
  3. `note/手征引力波ORF精确计算_研究路线图.md` — 第 2.2 节涉及近似讨论
  4. `memory/03-olc-orf-results-summary.md` — 包含 ORF 平坦性与小天线近似的相关讨论

- **工具可用性**:
  | 工具 | 状态 |
  |------|------|
  | Hu PRD txt（近似讨论） | 可用 |
  | Hu PRD pdf | 可用 |
  | 路线图笔记 | 可用 |
  | memory/03（ORF 平坦性） | 可用 |
  | **Tomassini (2007) 原文** | **不可用（阻塞项！）** |
  | Tomassini PDF (PhysRevD.76.083009) | 不可用，可从 arXiv 获取 |

- **背景知识**: 充足但有阻塞项
  - Hu PRD 中已包含对 Tomassini 近似的基本描述和对比
  - 但 ST7 要求对比 Tomassini (2007) 的核心结果，原文不可用是**阻塞项**
  - 替代方案: 通过 arXiv 搜索并获取 Tomassini (2007) 原文（Phys. Rev. D 76, 083009），或从 Hu PRD 的引用中推断 Tomassini 的核心结论

- **查重结果**: 
  - 路线图笔记中已有近似讨论，但深度有限
  - ST7 产出（详细的近似对比分析）与现有笔记不重复

- **新颖性**: **N0**（Tomassini 小天线近似是已知标准近似方法，Hu PRD 已给出完整的对比框架，ST7 主要是复述和验证）

---

## Subtask ST8: 综合整合 — 公式引用、物理直觉、自我问答汇总

- **可用工具**:
  1. ST1-ST7 的全部产出（理解笔记各节）
  2. `raw/PhysRevD.111.084065(1).txt` — 用于最终核对公式编号和内容
  3. `raw/PhysRevD.111.084065(1).pdf` — 用于公式排版核对

- **工具可用性**: 完全可用（依赖 ST1-ST7 的产出）

- **背景知识**: 充足（整合工作依赖前述子任务的成果）

- **查重结果**: 无。这是整合性质的子任务，产出是基于全部理解笔记的最终综合文档。

- **新颖性**: **N0**（纯整合工作）

---

## 总体评估

### 工具就绪度: **partial**

| 类别 | 可用性 | 说明 |
|------|--------|------|
| Hu PRD 原文（txt + pdf） | 可用 | 2023 行 txt，815KB pdf，覆盖全部 5 章 |
| Hu PRD 公式引用 | 可用 | 文本中包含 18 处 Eq./equation 引用，关键公式编号完整 |
| 替代文本 | 可用 | `workspace-019f3b66-7691-7c5d-9acc-9ae6c6db9031/physrevd_text.txt`（73KB） |
| 项目路线图笔记 | 可用 | `手征引力波ORF精确计算_研究路线图.md` 提供推导框架 |
| 项目对比分析报告 | 可用 | `OLC与手征引力波_对比分析报告.md` |
| 项目代码（ORF 实现） | 可用 | `scripts/01-olc-orf-solver.py` 等 |
| 项目记忆文件 | 可用 | memory/ 目录包含迭代 6-8 的 ORF 相关记录 |
| **Tomassini (2007) 原文** | **不可用（阻塞项）** | 关键对比文献，建议从 arXiv 获取 |
| LISA TDI 手册 | 不可用 | ST5 需要额外 TDI 知识，但 Hu PRD 有足够描述 |

### 阻塞项

1. **Tomassini (2007) 原文缺失** — 影响 ST7（Tomassini 小天线近似对比）。建议在进入 2-loop 前通过 arXiv 获取（Phys. Rev. D 76, 083009）。
   - 缓解措施: Hu PRD 第 1 章和第 4 章已包含对 Tomassini 近似的足够描述，ST7 可在不使用原文的情况下完成基础对比

### 新颖性评估: **N1**

理由:
- ST3 (N0) 和 ST6 (N0) 和 ST7 (N0) 和 ST8 (N0) 都是基于已知框架的理解工作
- ST5 (N1) 需要额外的 TDI 知识背景
- ST1 (N1), ST2 (N1), ST4 (N1) 需要对原文公式的解读和通俗化
- **整体评估 N1**: 8 个子任务中，3 个为 N0（纯公式代换和整合），4 个为 N1（原文解读和通俗化），1 个为 N1（需要额外背景知识）。不存在需要中等以上创新（N2/N3）的子任务，因为所有子任务的核心目标都是**理解已有文献**而非**发展新理论**。

### 结论

所有 8 个子任务均可执行，无明显阻塞项。唯一建议补充的资源是 Tomassini (2007) 原文（arXiv:gr-qc/0702019 或 Phys. Rev. D 76, 083009），但非必须。工具就绪度满足进入 2-loop 执行阶段的条件。
