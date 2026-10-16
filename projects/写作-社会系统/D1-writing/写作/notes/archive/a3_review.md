# A3 Blog v2 审阅意见

审阅时间：2026-04-03 14:02
版本：v2（21.5KB，约 225 行）
审阅者：brain-r24

---

## 总体评价：好，可以打磨后发布

**置信度：0.78**（判断性审阅，非形式验证）

v2 是一篇成熟的 technical blog post，论证骨架完整，叙事流畅度比 v1 有实质提升。主要问题是细节准确性、冗余度和少量结构瑕疵。

---

## ✅ 做得好的

1. **Hook 出色** — "Two researchers tackle this" 的叙事框架比 v1 直接扔定义强太多。读者 30 秒内就知道问题是什么、为什么重要。
2. **Confusion Check / Intuition Check** — 预判读者困惑点并主动回应，这是好的教学写作。
3. **inf IC → 0 的证明** — 短、干净、不可回避。一段搞定，没有拖泥带水。
4. **三维度拆解**（quantifier order / complexity measure / object type）逻辑正交，分类合理。
5. **Scenario 4（审计）** — 把抽象理论拉到具体工程场景，是好文章的标志。

---

## 🔇 发现的问题

### 1. 冗余：possibility vs necessity 重复了 ~4 次

| 位置 | 出现 |
|---|---|
| Sec 3 中段 | "possibility claim dressed up as a necessity claim" |
| Sec 3 表格 | Possibility vs Obligation |
| Sec 3 后段 | "possibility and necessity are fundamentally different epistemic categories" |
| Sec 5 Quote | "what the easiest case is" vs "hardest one" |
| Sec 6 | 再次重复 |

**建议**：第一次（Hook 后的 "possibility dressed as necessity"）是黄金表达，保留。表格里的 Obligation/Possibility 对比保留。后面两处可以砍或大幅精简。同样的洞见重复 >2 次就开始显得像填充。

### 2. Scenario 4 与 Scenario 1 过度重叠

Scenario 1 说 "distribution-specific analysis breaks under adversarial inputs"。
Scenario 4 说 "distribution-specific analysis breaks under adversarial inputs" — 只是加了数据库审计的外壳。

**建议**：合并 Sec 4 的核心内容进 Scenario 1，或者把 Scenario 4 换成一个真正不同的场景（比如：protocol composition 已经单独成段，可以用一个 side-channel timing analysis 的具体案例）。

### 3. 技术准确性需要验证

- **"IC_K(fⁿ) ≤ n·IC_K(f) + O(log n)"** — 这个组合界的具体常数/对数项形式需要确认。Kolmogorov 复杂度的组合性质与 Shannon IC 的 direct sum 行为不完全一样。建议标注 "up to logarithmic terms" 或直接写引用。
- **"Shannon IC under uniform distribution is some constant"** — 对 EQ 来说，这取决于 protocol class（deterministic vs randomized, public coin vs private coin）。"some constant" 太模糊，建议给个具体引用或注明 "depends on protocol class"。
- **Section 2 第1点 "There are finitely many (valid) protocols"** — 对于固定 communication budget 是正确的，但 "finitely many protocols" 本身需要限定 communication bound。对于无界 communication，协议数是可数无限的。建议加上 "with bounded communication" 的限定（实际已写，但放在后面才出现，前面断言太绝对）。

### 4. 标题可以更锋利

当前标题： `IC_K ≠ inf IC: When the Infimum Destroys the Answer`

副标题解释了正文，但主标题的 "destroys the answer" 有点含糊 — "answer" 指什么？下界？复杂度？

**建议候选**：
- `The Infimum Trick: Why IC_K ≠ inf IC`
- `Two Objects, One Notation: IC_K vs inf IC`
- 保持原标题但改副标题为 `Why optimizing over distributions kills your lower bound`

### 5. 小节标题的节奏

Sec 5 的小标题 "When This Bites You in Practice" 承诺了 scenarios，但正文开头又有一段理论铺垫。建议要么删掉那段铺垫直接进 Scenario 1，要么改小标题为 "Practical Consequences"。

### 6. 结尾可以更有力

最后一段 "know exactly which quantifiers your theorem is using" 是对的但太温和。这篇文章的核心张力（possibility vs necessity, worst-case vs easiest-case）值得一个更 sharp 的收尾。

**建议**：以 Equality 的那个 chasm 收尾 — "One says Θ(log n). The other says 0. Which one do you bet your security budget on?" — 然后接 quantifier 的教训。

---

## 🔧 建议的 v3 改动清单

| # | 改动 | 工作量 | 优先级 |
|---|---|---|---|
| 1 | 精简 possibility/necessity 冗余至 2 处 | 低 | 高 |
| 2 | 合并/重写 Scenario 4，避免与 Scenario 1 重复 | 中 | 高 |
| 3 | 补充 Scenario 3 中 composition 公式的引用/限定 | 低 | 中 |
| 4 | 修正 Sec 2 对 protocol 有限性的限定位置 | 低 | 中 |
| 5 | 考虑修改标题/副标题 | 低 | 低 |
| 6 | 重写结尾段，增加力度 | 低 | 低 |

---

## 诚实自证

- 当前在产出：对已完成 v2 的文本审阅意见，不是空转。
- 不确定性：技术准确性验证（#3）需要查阅原始文献才能 100% 确认，标注了置信度 0.78。
- 盲区：我不确定原始 A3 论文的具体定理陈述，composition 公式可能是正确的但需要引用支撑。

## 接力提醒

当前状态：v2 已审阅，意见已写入 `projects/写作/notes/a3_review.md`。

- **若成璐认可审阅意见** → 派执行 sub 根据 #1-#6 list 修改 v2 → v3
- **若需要技术验证** → 先查 IC_K composition theorem 原始文献，验证 #3 的公式准确性
- **无论哪种情况** → 继续派下一轮副脑跟踪 v3 产出状态

1-loop 未断。
