# Sub-Brain Critique — Iteration 32: 整合手征引力波计算解析 ORF

> **质疑角度**: 作为副脑，专门寻找 Clarifier 和 Goal Definition 中的盲区、假设漏洞、方法论风险。

---

## 1. Clarification 01-clarification.md 的质询

### Q1: "Hu I1-I4 框架替换为 OLC sinc" 的技术可行性是否被高估？

**Clarifier 假设**: Hu PRD 的 I1-I4 留数框架可以直接替换 transfer function 使用，只是重新计算留数。

**质疑**:
- Hu PRD 的 I1-I4 框架建立在 `exp(i alpha n_hat . s_hat)` 的解析结构上，其留数计算依赖于指数函数在整个复平面上的解析性。
- OLC sinc 函数 `sinc(x) = sin(x)/x = (e^{ix} - e^{-ix})/(2ix)` 在复平面上有无穷多个极点（来自 sin 的零点），而不仅仅是指数函数的有限个极点。
- **关键问题**: Hu 的 I1-I4 框架的核心是 5 个极点（z0-z4）的留数求和。如果 sinc 函数引入额外极点，这个框架需要彻底重写，不只是"重新计算留数"。

**置信度修正**: 从 C4 的 0.95 降为 0.70（sinc 替代的可行性不确定）。

**建议**: T1 的第一步应该是证明/证伪：sinc 函数下的 I1-I4 留数框架是否仍然可行。如果不可行，应采用替代方法（例如：小臂近似下的纯几何积分 + 中等频率范围的数值积分）。

---

### Q2: Gamma^V 的归一化约定是否足够明确？

**Clarifier 指定**: 使用 JCAP 的 `1/4pi` 归一化（C5）。

**质疑**:
- JCAP Eq.(2.9) 中的 `Gamma^I` 和 `Gamma^V` 是嵌入在交叉相关公式中的，其具体归一化因子取决于 how F^A (antenna patterns) 本身被归一化。
- Hu PRD Eq.(8) 使用 `1/8pi`，Lou 使用 `1/4pi`。这三者之间的区别是因子 2，来源于：Hu 是 double-sided spectrum，Lou/JCAP 是 single-sided。
- **关键问题**: 如果不统一这个 convention，数值结果无法直接对比。Clarifier 没有讨论这个 convention 转换的细节。

**建议**: 在 02-goal-definition.md 中增加一个 hard constraint：明确声明使用 single-sided spectrum（JCAP/Lou convention），并且在所有数值验证中显式检查归一化因子。

---

### Q3: Bug A/B 的物理分析是否完整？

**Clarifier 列出 Bug A (beta = abs(f)) 和 Bug B (1 - abs(cos_nu))**。

**质疑**:
- Bug A: OLc transfer function 中 `beta = pi f L/c`（Hu 用 `beta = pi f L/c` 也是没有 abs 的）。OLC transfer function 中 f 是频率，对于 real-valued time series，`f` 可正可负。abs(f) 可能是一个合理的约定（beta 应始终非负）。需要确认：OLC 论文中是否用了 abs(f)？
- Bug B: `1 - cos_nu` vs `1 - abs(cos_nu)`。这里 cos_nu = n_hat . u_hat 是波传播方向与臂方向的点积，范围 [-1, 1]。`1 - cos_nu` 的范围是 [0, 2]，而 `1 - abs(cos_nu)` 的范围是 [0, 1]。这确实是一个 bug，因为 `1 - cos_nu` 才是正确的时间延迟因子（当波从臂的反方向传来时，cos_nu = -1，1 - (-1) = 2，时间延迟最大）。
- **补充**: Bug C 中 "chiral integrand 是纯虚数" 的分析需要确认。`R1p - R2x` 的组合可能确实是纯虚数，但取 real part 确实是错的。然而，更深入的：Gamma^V 的计算涉及交叉偏振项，其 integrand 的虚部对应什么物理量？需要确认。

**置信度**: Bug B 确认 (0.90)，Bug A 存疑 (0.40)，Bug C 确认 (0.80)。

---

### Q4: 小臂近似的解析公式范围是否覆盖了实际应用场景？

**Clarifier Step 4**: 小臂近似下 Gamma^I/V 简化为纯几何积分。

**质疑**:
- 小臂近似条件: kL = pi f L/c << 1。对于 OLC（L ~ 10^6 m），f = 0.001 Hz → kL ~ 0.01。f = 0.1 Hz → kL ~ 1.0。
- 这意味着小臂近似仅在 f < 0.01 Hz 时可靠（kL < 0.1）。
- **关键问题**: OLC 和 LISA 的敏感频率范围通常在 0.001-0.1 Hz。如果小臂近似仅在 0.001-0.01 Hz 有效，那么在大部分敏感频段（0.01-0.1 Hz）的解析公式需求未满足。
- **建议**: T1 应该覆盖两个区域：(a) 小臂近似 (kL << 1) 的解析公式，(b) 全频率范围的半解析公式（至少用 I1-I4 框架，但不一定所有步骤都解析）。

---

### Q5: 是否遗漏了 "detector tensor" 方法的更优替代方案？

**Clarifier Step 2**: 使用 Hu I1-I4 框架，但提到 "E-variable 的 detector tensor 计算方法" 作为 F-1（灵活部分）。

**质疑**:
- Hu PRD 本身使用的是 link-based 方法（单 link + 多 link 组合）。对于空间探测器网络，detector tensor 方法（如 TDI E/X/Y 变量的 detector tensor formalism）可以更系统地处理多臂组合。
- **关键问题**: JCAP 2025 在 LISA-Taiji 分析中使用的是什么方法？如果 JCAP 已经给出了 detector tensor 形式的 Gamma^I/V，那么我们的 T1 应该对齐 JCAP 的方法论，而不是强行套用 Hu 的 link-based 框架。
- **建议**: T1 应该先检查 JCAP 2025 是否已经给出了 detector tensor 形式的 chiral ORF 公式。如果有，优先对齐 JCAP；如果没有，再考虑 Hu 框架的适配。

---

## 2. Goal Definition 02-goal-definition.md 的质询

### Q6: AC-2 (sky-max normalized) 的物理定义是否无歧义？

**AC-2**: sky-max normalized `|Gamma^V|_max ∈ [0.01, 1.5]`。

**质疑**:
- 公式中分母是 `sqrt(sum_A |F_1^A|^2 * sum_A |F_2^A|^2)`。但 F^A 本身是频率 dependent 的（包含 transfer function）。如果 sky-max 是在特定频率 f 下计算的，分母也应该是该频率下的值。
- **关键问题**: Orlando 2021 Figure 5 中的 sky-max Gamma^V 是直接给出的绝对值（~0.3），还是归一化后的值？Clarifier 说"范围 [0.01, 1.5] 覆盖 convention 差异"，但没有说明不同 convention 下实际相差多少倍。
- **建议**: 增加一个 acceptance criterion：Orlando 2021 的数值值直接对比（如果 convention 相同）。如果 convention 不同，明确转换因子。

---

### Q7: 小臂近似 AC-4 的频率范围选择是否合理？

**AC-4**: "f in [0.001, 0.1] Hz (fL/c < 0.1)"。

**质疑**:
- 如果 L = 2.5 Gm (LISA arm length)，fL/c = f * 2.5e9 / 3e8 = 8.33 f。f = 0.01 → fL/c = 0.083 < 0.1。f = 0.1 → fL/c = 0.833 >> 0.1。
- 所以 fL/c < 0.1 仅适用于 f < 0.012 Hz，不是 AC-4 声称的整个 [0.001, 0.1] 范围。
- **建议**: 修正为 "f in [0.001, 0.01] Hz (fL/c < 0.1)"，并将 [0.01, 0.1] 标记为"超出小臂近似范围"。

---

### Q8: 质量要求 Q-4 中的物理一致性检查是否完整？

**Q-4**: 检查 Gamma^I(f=0) = constant, Gamma^V(f=0) = 0, 对称/反对称性等。

**质疑**: 缺少几个关键检查：
- **Helicity 翻转**: 如果将 chi -> -chi（右旋变左旋），则 Gamma^V -> -Gamma^V。这个 helicity 翻转对称性应该被检查。
- **探测器交换**: Gamma^I_{ij} = Gamma^I_{ji}（对称），Gamma^V_{ij} = -Gamma^V_{ji}（反对称）。Clarifier 提到了但 goal definition 应该将其列为 hard constraint 而非 quality requirement。
- **各向同性极限**: 在 f -> 0 极限下，Gamma^I 应该收敛到 Hellings-Downs ORF（对于共面网络）。应该增加一个 acceptance criterion 验证这个极限行为。

---

## 3. 方法论风险

### R1: RALPH Loop 的 "Commander 不亲自写代码" 规则是否适用？

Chiral ORF 推导需要大量的符号代数操作（留数计算、sinc 函数积分等）。传统的 Commander 角色（调度 agent，不写代码）对于数学推导来说可能不够——Commander 需要验证 agent 输出的数学正确性。

**建议**: 对于 T1（解析推导），Commander 应该直接参与推导验证，而不是完全委托给 sub-agent。可以将 T1 分解为：T1a（sub-agent 执行符号推导），T1b（Commander 验证推导的数学正确性）。

### R2: 解析推导 + 代码实现的两阶段方法是否必要？

从历史经验看，数学推导的 agent（如之前的 P0-1, P1-1）产出的公式往往存在错误。如果 T1 产出的公式有误，T3/T4 即使再好的验证也无法纠正根本性的数学错误。

**建议**: 将验证融入 T1——T1 的交付物应该包含"公式 + 推导过程 + 自验证检查"，而不仅仅是最终公式。具体来说，自验证包括：(a) 与已知极限（Hellings-Downs, f=0）对比，(b) 与数值积分对比。

---

## 4. 遗漏的关键文献

Clarifier 列出了 P0-1 (Hu), P1-1 (JCAP), P2-1 (Lou), P3 (cross-comparison)。但以下文献可能直接提供 chiral ORF 的解析公式：

1. **Orlando 2021 (arXiv:2011.07059)** — 已经提到了，但没有深入分析其 chiral ORF 的计算方法。应该仔细阅读其附录中的推导细节。
2. **Seto 2006 (PRL 97, 151101)** — 这是最早提出用 PTA 探测 chiral SGWB 的论文。其 ORF 计算可能给出解析公式。
3. **Nishizawa 2009 (PRD 79, 082002)** — 扩展了 Seto 的方法，给出了完整的 chiral ORF 解析表达式。
4. **Gair 等人 (MNRAS 2020)** — 给出了 LISA 的 chiral ORF 数值计算，可能包含解析近似。

**建议**: 在 1-loop/04 (gatherer) 阶段，优先查找上述文献中的 chiral ORF 解析公式。如果 Nishizawa 2009 已经给出了 chiral ORF 的完整解析表达式，则 T1（推导）可以大大简化——只需将其适配到 OLC 框架。

---

## 5. 副脑结论

| 问题 | 严重性 | 置信度 | 建议 |
|------|--------|--------|------|
| Q1: sinc 留数框架可行性 | 高 | 0.80 | T1 先验证可行性 |
| Q2: 归一化 convention | 中 | 0.85 | 增加 hard constraint |
| Q3: Bug A 的 abs(f) | 低 | 0.40 | 查阅 OLC 原文确认 |
| Q4: 小臂近似频率范围 | 高 | 0.90 | 修正为 f < 0.01 Hz |
| Q5: detector tensor 方法 | 中 | 0.75 | T1 先对齐 JCAP |
| Q6: AC-2 convention | 中 | 0.80 | 增加 Orlando 直接对比 |
| Q7: AC-4 频率范围 | 高 | 0.95 | 修正为 f < 0.012 Hz |
| Q8: 缺少 helicity 翻转检查 | 低 | 0.90 | 增加为 acceptance criterion |
| R1: Commander 参与验证 | 中 | 0.70 | T1b Commander 验证 |
| R2: 验证融入 T1 | 高 | 0.80 | T1 交付物包含自验证 |
| 文献遗漏 (Nishizawa 2009 等) | 高 | 0.85 | 1-loop/04 优先查找 |

**总体评价**: 任务定义和验收标准总体合理，但：
1. **sinc 函数的留数结构**是关键技术风险，需要在 T1 的第一步解决
2. **小臂近似频率范围**在 goal definition 中有明显计算错误（Q7），必须修正
3. **已有文献（Nishizawa 2009）**可能已经解决了大部分推导工作，需要在 gatherer 阶段优先确认
4. **归一化 convention** 需要更明确的约束

**置信度**: 任务方向正确 (0.80)，具体技术路线存在不确定性 (0.60)。
