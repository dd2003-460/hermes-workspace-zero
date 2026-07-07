# 1-loop/04 信息搜集 — P2-1: 楼明智 OLC 探测器论文理解

> 阶段: 1-loop/04 (Gatherer / 信息搜集)
> 来源任务: 1-loop/03-任务分解-P2-1-Iteration1.md (11 个子任务)
> 完成时间: 2026-07-07
> 状态: completed

---

## 总览：子任务依赖图

```
ST01(ST02,ST03) → ST04 → ST05 → ST06 → ST07 → ST09 → ST08
                                         ↓
                                      ST10 → ST11
```

**关键路径**: ST02→ST04→ST05→ST06→ST09→ST10→ST11 (最长依赖链，7步)

---

## 子任务逐项工具与背景评估

### ST01: 从楼明智论文提取 OLC 工作原理描述

| 项目 | 评估 |
|------|------|
| **所需工具** | 文本搜索 + 人工理解 |
| **可用工具** | ✅ `raw/楼明智论文OLC.txt` (2663行, 118KB) — 完整论文文本<br>✅ `raw/楼明智论文OLC.pdf` (5.5MB) — PDF原文<br>✅ `note/workspace-019f3b66/lou_full.txt` — 另一版本提取<br>✅ `note/workspace-019f3b66/lou_text.txt` — 另一版本提取<br>✅ `note/OLC引力波科普.md` — 已有助教级理解文档<br>✅ `note/用原子钟"听"引力波.md` — 科普级理解文档 |
| **背景知识是否足够** | ✅ **足够**。项目已积累大量 OLC 背景知识：<br>- `OLC引力波科普.md` 和 `用原子钟"听"引力波.md` 已将 OLC 原理转化为通俗语言<br>- `OLC与手征引力波_对比分析报告.md` 第0节明确列出两篇底稿论文的对比<br>- 项目已完成 OLC ORF 的数值计算验证，对 OLC 框架有深入理解 |
| **重复检查** | ⚠️ `note/OLC引力波科普.md` 和 `note/用原子钟"听"引力波.md` 已包含 OLC 工作原理的通俗描述，但它们是面向非专业人士的，**不是针对楼明 Thesis 原文的技术性提取**。ST01 需要的是**精确引用楼 Thesis 原文**的描述。两者互补，非重复。 |
| **新颖性** | **N0** — 纯文本提取任务，无新方法论 |
| **阻塞项** | 无 |

**操作路径**:
```bash
grep -n "时钟\|频率\|光钟\|原子钟\|引力波\|相移\|相位\|传播时间" raw/楼明智论文OLC.txt | head -50
```

---

### ST02: 从楼明 Thesis 提取 Transfer Function (公式 2-30)

| 项目 | 评估 |
|------|------|
| **所需工具** | 公式定位 + 数学表达式提取 |
| **可用工具** | ✅ `raw/楼明智论文OLC.txt` — 含公式行号索引 (第668-987行)<br>✅ `memory/02-lou-olc-transfer-function.md` — 已有 transfer function 提取<br>✅ `scripts/01-olc-orf-solver.py` 中 `olc_transfer_function()` — 项目已实现的版本 |
| **背景知识是否足够** | ✅ **足够**。memory 文件 02 已提取并确认 transfer function 的准确性。项目代码 `olc_transfer_function(f, L, cos_nu)` 已实现 Lou Eq. 2-30 的 sinc 形式：$\mathcal{T} = \frac{i2\pi fL}{c} \text{sinc}[\frac{\pi fL}{c}(1-\hat{u}\cdot\hat{n})] e^{-i\frac{\pi fL}{c}(1-\hat{u}\cdot\hat{n})}$ |
| **重复检查** | ✅ **不重复**。memory/02 已提取，但 ST02 要求重新从原文验证并记录符号约定。memory 文件可能是从 PDF 提取的文本格式，需要与原文对齐。 |
| **新颖性** | **N0** — 公式提取任务，已有参考 |
| **阻塞项** | 无 |

**操作路径**:
```bash
# 从 raw 文件定位公式 2-30 附近的文本
sed -n '668,987p' raw/楼明智论文OLC.txt
# 对比 memory 文件中的公式提取
cat memory/02-lou-olc-transfer-function.md
```

---

### ST03: 从 Hu PRD 论文提取通用 ORF 定义

| 项目 | 评估 |
|------|------|
| **所需工具** | 公式定位 + 数学表达式提取 |
| **可用工具** | ✅ `raw/PhysRevD.111.084065(1).txt` (72KB) — 完整论文文本<br>✅ `raw/PhysRevD.111.084065(1).pdf` (816KB) — PDF原文<br>✅ `memory/01-olc-orf-formulas.md` — Hu PRD 公式提取<br>✅ `note/workspace-019f3b66/physrevd_text.txt` — 另一版本提取 |
| **背景知识是否足够** | ✅ **足够**。memory/01 已提取 Hu PRD 中的 ORF 定义。对比分析报告第1节也明确写出了强度 ORF 和手征 ORF 的标准定义：
$$\Gamma^I_{IJ}(f) = \frac{3}{4}\int\frac{d^2\hat n}{4\pi}\sum_{A=+,\times} R_I^A(\hat n) R_J^{A*}(\hat n) e^{-i2\pi f \hat n\cdot\Delta\vec r/c}$$ |
| **重复检查** | ⚠️ memory/01 标注为"保留参考，可能部分正确"。需要重新从原文验证，特别是公式编号和符号约定。 |
| **新颖性** | **N0** — 已有提取，需重新验证 |
| **阻塞项** | 无 |

---

### ST04: 对比 OLC Transfer Function 与 PTA T_one

| 项目 | 评估 |
|------|------|
| **所需工具** | 数学表达式对比 + 符号对照 |
| **可用工具** | ✅ `memory/02-lou-olc-transfer-function.md` — Lou TF 提取<br>✅ `memory/01-olc-orf-formulas.md` — Hu PRD T_one 提取（如包含）<br>✅ `raw/PhysRevD.111.084065(1).txt` — 含 T_one = $(1+\hat{n}\cdot\hat{u})/2 \times [1-e^{-i\beta(1+\hat{n}\cdot\hat{u})}]$ |
| **背景知识是否足够** | ✅ **足够**。对比分析报告第1节已讨论了 PTA 与 OLC 的差异：PTA 使用双端响应 $F_L+F_R$，而 OLC 是单向链路 $F_L$。TF 在 ORF 中的角色差异已明确。 |
| **重复检查** | ✅ **不重复**。已有对比分析，但 ST04 要求对单个 TF 公式进行逐项对比。这是更细致的分析层次。 |
| **新颖性** | **N0** — 已有对比基础，需更细致 |
| **阻塞项** | 无 |

---

### ST05: 确认 OLC 中的 ORF 定义（2-31 或附近）是否与 Hu PRD 标准一致

| 项目 | 评估 |
|------|------|
| **所需工具** | 公式定位 + 数学表达式对比 |
| **可用工具** | ✅ `raw/楼明智论文OLC.txt` — ORF 定义行号索引<br>✅ `raw/PhysRevD.111.084065(1).txt` — Hu PRD ORF 定义<br>✅ `memory/01-olc-orf-formulas.md` 和 `memory/02-lou-olc-transfer-function.md` — 已提取公式 |
| **背景知识是否足够** | ✅ **足够**。根据已有记忆，楼 Thesis 的 ORF 定义应与 Hu PRD 一致，因为楼 Thescis 在文献综述部分引用了类似框架。需要精确验证公式编号和符号约定。 |
| **重复检查** | 否。ST04 比较的是 TF（transfer function），ST05 比较的是 ORF（overlap reduction function）定义。两者不同。 |
| **新颖性** | **N0** — 纯验证任务 |
| **阻塞项** | 需要先完成 ST01-ST03 的提取 |

---

### ST06: 理解楼 Thesis ORF (3-1) 的具体形式 — 6个几何参数

| 项目 | 评估 |
|------|------|
| **所需工具** | 代数推导 + 几何参数理解 |
| **可用工具** | ✅ `raw/楼明智论文OLC.txt` — 含公式行号索引（第668-987行）<br>✅ `scripts/01-olc-orf-solver.py` — `compute_orf_two_arm()` 实现<br>✅ `scripts/01-olc-orf-solver.py` — `antenna_patterns()` 函数 |
| **背景知识是否足够** | ⚠️ **部分足够**。项目代码已实现 ORF 计算，但需要确认实现的是 Lou 论文中 Eq. 3-1 的具体形式（含6个几何参数：两个时钟的方位角、天顶角以及相对方位角）。对比分析报告第6节讨论了 ORF 计算的几何基础，但需要更细致的逐参数对照。 |
| **重复检查** | ✅ 否。ST06 要求逐项理解6个几何参数在公式中的具体角色，这是计算实现级别的理解。 |
| **新颖性** | **N1** — 需要将抽象公式转化为可计算形式，涉及符号约定转换 |
| **阻塞项** | 需要 ST03 (ORF 定义) 已完成 |

**操作路径**:
```bash
# 定位 Lou Thesis ORF 公式 (3-1)
grep -n "3-1\|ORF\|重叠响应\|重叠函数" raw/楼明智论文OLC.txt
# 查看项目实现
grep -n "compute_orf\|antenna\|baseline\|n_s" scripts/01-olc-orf-solver.py
```

---

### ST07: 确认楼 Thesis ORF 对 SGWB 4 个假设的依赖

| 项目 | 评估 |
|------|------|
| **所需工具** | 文本搜索 + 物理理解 |
| **可用工具** | ✅ `raw/楼明智论文OLC.txt` — 论文全文<br>✅ `memory/02-lou-olc-transfer-function.md` — TF 提取（可能含假设说明）<br>✅ `note/手征-GW-ORF-文献调研2026.md` — 文献调研中涉及 SGWB 假设 |
| **背景知识是否足够** | ✅ **足够**。SGWB 的 4 个假设（平稳性 Stationarity、高斯性 Gaussianity、各向同性 Isotropy、非偏振 Non-polarization）是标准引力波背景理论内容。项目调研报告中已涉及相关讨论。需要定位楼 Thesis 中明确引用这些假设的段落。 |
| **重复检查** | 否。ST07 要求定位楼 Thesis 中具体的引用位置，这是 ST01-ST06 理解之后的验证步骤。 |
| **新颖性** | **N0** — 纯定位和确认任务 |
| **阻塞项** | 需要 ST05 已确认 ORF 定义 |

---

### ST08: 对比 OLC ORF 与标准 PTA/LISA 的 ORF

| 项目 | 评估 |
|------|------|
| **所需工具** | 公式对比 + 参数空间对比 |
| **可用工具** | ✅ `raw/PhysRevD.111.084065(1).txt` — Hu PRD 含 PTA 和干涉仪 ORF<br>✅ `scripts/01-olc-orf-solver.py` — OLC ORF 实现（可生成对比数据）<br>✅ `memory/01-olc-orf-formulas.md` — Hu PRD 公式提取<br>✅ `note/OLC与手征引力波_对比分析报告.md` — 已有框架对比 |
| **背景知识是否足够** | ✅ **足够**。对比分析报告已明确讨论了 PRD (Hu) 框架的适用范围（PTA + 激光干涉仪），OLC 是其中的一种特例。项目代码 `compute_orf_two_arm()` 实现的是通用双臂 ORF，可以生成 OLC 的数值结果并与 PTA/LISA 对比。 |
| **重复检查** | ✅ **部分重复**。对比分析报告第0-1节已有框架级对比。ST08 要求对 ORF 的**具体形式**进行对比（即 OLC 的 ORF 公式 vs PTA 的 ORF 公式 vs LISA 的 ORF 公式）。这是公式级对比，比框架级对比更深入。 |
| **新颖性** | **N1** — 需要生成数值对比数据并发现差异来源 |
| **阻塞项** | 需要 ST06 (ORF 3-1 理解) 已完成 |

---

### ST09: 用项目代码验证 OLC Transfer Function 和 ORF 公式

| 项目 | 评估 |
|------|------|
| **所需工具** | 代码分析 + 数值验证 |
| **可用工具** | ✅ `scripts/01-olc-orf-solver.py` (~556行) — 核心实现<br>✅ `scripts/_diag_*.py` — 7个诊断脚本 (chiral, freq_scan, link_evar, orlando_e, sky_max, taiji_tf)<br>✅ `scripts/validate_orlando_crosscorr.py`, `validate_orlando_response.py`, `validate_orlando_chiral.py` — 3个验证脚本<br>✅ `scripts/debug_rv_zero.py`, `scripts/test_crosscorr_symmetry.py` — 调试脚本<br>✅ `memory/10-olc-triangular-chiral-orf-iteration6.md` — **⚠️ 废弃** (含bug前代码结果)<br>✅ `memory/15-orlando-chi_orb-resolution-iteration8.md` — 有效 (χ_orb vs norm_V 归一化分析)<br>✅ `memory/16-orlando-nonzeroRV-mirror-plane.md` — 有效 (镜面对称性分析) |
| **背景知识是否足够** | ⚠️ **部分足够**。项目代码 `olc_transfer_function()` 使用 `|cos_nu|`（绝对值），这在之前迭代中被识别为天线方向图 bug。需要确认：<br>1. Bug 是否已修复（`|cos_nu|` vs `cos_nu`）<br>2. 验证测试是否仍然通过<br>3. 自相关 (self-correlation) 和低频极限 (low-freq limit) 验证 |
| **重复检查** | ✅ **部分重复**。之前迭代（5-16）已完成多次验证。`memory/10` 标记为废弃，`memory/15` 和 `memory/16` 仍有效。需要区分哪些验证仍然适用。 |
| **新颖性** | **N1** — 对比任务，需要识别差异和改进空间 |
| **阻塞项** | 需要 ST02 (TF 精确公式) 和 ST06 (ORF 精确公式) 已完成 |

**操作路径**:
```bash
# 检查项目代码中的 TF 实现
grep -n "cos_nu\|transfer_function\|sinc" scripts/01-olc-orf-solver.py
# 检查已知 bug
grep -n "abs\|absolute\|\|cos_nu\|" scripts/01-olc-orf-solver.py
# 运行现有验证测试
python scripts/01-olc-orf-solver.py
```

---

### ST10: 用物理直觉检验 OLC ORF 的关键极限情况

| 项目 | 评估 |
|------|------|
| **所需工具** | 物理推导 + 数值验证 |
| **可用工具** | ✅ `scripts/01-olc-orf-solver.py` — 含 self-correlation 和低频极限验证<br>✅ `scripts/_diag_freq_scan.py` — 频率扫描<br>✅ `memory/10-olc-triangular-chiral-orf-iteration6.md` — **⚠️ 废弃** (但结论中 R^I = -0.23 可信)<br>✅ `memory/15-orlando-chi_orb-resolution-iteration8.md` — 归一化分析<br>✅ `memory/16-orlando-nonzeroRV-mirror-plane.md` — 镜面对称性分析<br>✅ `note/手征-GW-ORF-文献调研2026.md` — 文献调研中的物理直觉讨论 |
| **背景知识是否足够** | ✅ **足够**。已知极限情况：<br>1. **低频极限** $f \to 0$: ORF 应趋近于常数<br>2. **自相关** (self-correlation): 探测器与自身的相关应给出归一化值<br>3. **Michelson-like 变量**: 对单臂 Michelson 组合，chiral ORF = 0 (镜面对称性)<br>4. **星等臂长相等**: 三角形等边构型有特殊对称性 |
| **重复检查** | ✅ 部分重复。之前迭代已验证了 Michelson-like 变量的零 chiral 响应和三角形构型的标准 ORF。ST10 要求系统性覆盖所有关键极限情况。 |
| **新颖性** | **N0** — 标准验证步骤，但需要整合所有之前的发现 |
| **阻塞项** | 需要 ST09 (代码验证) 已完成 |

**自我质询问题（建议）**:
- [ ] OLC ORF 在 $f \to 0$ 时的极限值是多少？是否与 PTA 低频极限一致？
- [ ] 楼 Thesis 中是否讨论了 ORF 对几何参数的灵敏度？
- [ ] "构型变换不变性" (楼 Thesis 标题) 的物理含义是什么？数学上如何证明？
- [ ] 如果两个 OLC 探测器的时钟间距不同，ORF 会如何变化？

---

### ST11: 组装完整的 P2-1 理解文档

| 项目 | 评估 |
|------|------|
| **所需工具** | 文本编辑 + 文档编排 |
| **可用工具** | ✅ `note/OLC引力波科普.md` — 可作为参考模板<br>✅ `note/用原子钟"听"引力波.md` — 可作为参考模板<br>✅ `note/OLC与手征引力波_对比分析报告.md` — 可作为参考模板<br>✅ 编辑工具 (Write/Edit) |
| **背景知识是否足够** | ✅ **足够**。项目已有多个高质量理解文档作为模板和参考。 |
| **重复检查** | 否。ST11 是汇编步骤，产出新的综合文档。 |
| **新颖性** | **N0** — 纯文档组装任务 |
| **阻塞项** | 需要 ST01-ST10 全部完成 |

---

## 总体评估

### 工具就绪度

| 类别 | 数量 | 就绪度 | 说明 |
|------|------|--------|------|
| 原始文献 (raw/) | 6 文件 (3论文 × 2格式) | ✅ 完全就绪 | TXT + PDF 双格式 |
| 提取文本 (note/workspace-019f3b66/) | 4 文件 | ✅ 完全就绪 | 补充访问途径 |
| 项目代码 (scripts/) | 25+ 文件 | ✅ 完全就绪 | 含核心计算 + 验证 + 调试 |
| 诊断脚本 (scripts/_diag_*.py) | 7 文件 | ✅ 完全就绪 | 频率扫描、sky_max 等 |
| 记忆文件 (memory/) | 18 文件 | ⚠️ 部分有效 | 10废弃, 15/16有效, 01/02需验证 |
| 已有理解文档 (note/) | 4 文件 | ✅ 完全就绪 | 科普级 + 对比分析 + 调研报告 |
| 工作区脚本 (workspace-*) | 1 文件 | ⚠️ 需验证 | 需检查是否包含 P2-1 相关内容 |

### 阻塞项汇总

| 阻塞项 | 影响子任务 | 严重度 |
|--------|-----------|--------|
| ST01-ST03 需先完成提取，ST05/ST06/ST08/ST09 依赖它们 | ST05, ST06, ST08, ST09 | **高** |
| memory/01 标记为"保留参考，可能部分正确" | ST05, ST06, ST08 | **中** |
| 项目代码 `olc_transfer_function` 使用 `|cos_nu|` (已知bug) | ST09 验证任务 | **中** |
| memory/10 废弃结果中的 R^I = -0.23 仍可信 | ST09, ST10 | **低** (有替代证据) |

### 新颖性分布

| 新颖度 | 子任务 | 占比 |
|--------|--------|------|
| **N0** (纯提取/验证/组装) | ST01, ST02, ST03, ST04, ST05, ST07, ST10, ST11 | 8/11 (73%) |
| **N1** (对比分析/公式转换) | ST06, ST08, ST09 | 3/11 (27%) |
| **N2** (深度推导/新发现) | 无 | 0/11 (0%) |
| **N3** (全新问题) | 无 | 0/11 (0%) |

### 建议执行顺序

```
第1批 (并行): ST01, ST02, ST03, ST04  # 纯提取，无依赖
第2批: ST05, ST07  # 验证任务，依赖第1批
第3批: ST06  # ORF 几何参数分析，依赖 ST03+ST05
第4批: ST08, ST09  # 对比+代码验证，依赖第2/3批
第5批: ST10  # 极限检验，依赖 ST09
第6批: ST11  # 最终组装，依赖全部
```

预计总耗时: 第1批 15min, 第2批 10min, 第3批 20min, 第4批 30min, 第5批 10min, 第6批 15min ≈ **100分钟**（纯理解阶段，不含执行）

---

## 与 P0-1 和 P1-1 信息搜集的协同

- **P0-1 (Hu PRD)** 和 **P2-1 (OLC)** 共享同一份 raw 文献。P0-1 对 Hu PRD 的提取结果可直接用于 P2-1 的 ST03/ST05/ST08。
- **P1-1 (手征物理)** 的结果可用于 P2-1 的 ST08 (对比) 和 ST10 (极限检验)。
- **代码复用**: `scripts/01-olc-orf-solver.py` 同时服务于 P0-1 (Hu PRD 验证) 和 P2-1 (OLC 验证)。

---

*本文件由 gatherer (信息搜集 Agent) 生成，进入 1-loop/05 verifier 阶段。*
