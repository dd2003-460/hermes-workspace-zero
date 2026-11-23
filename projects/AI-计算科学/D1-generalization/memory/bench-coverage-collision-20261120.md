# 对标调研结论：C/D bench 维度是否空白（2026-11-20）
# origin: ai
# 方法：collision-research 四象限 + arXiv 真实 ID 验证（abs 页，来源①）。
# 核心问题：规则压缩泛化（C）+ bug 猜测-验证（D）的维度，在已有 bench 里是否空白？

## 结论：C 和 D 都撞车了，"新 bench" 基本不成立
- **C（规则抽象/压缩/泛化）→ 🔴 撞 CodeARC + BabyTheorist**
- **D（bug 猜测-验证）→ 🔴 撞 SWE-bench 系 + CodeARC 的 interactive oracle**
- 唯一可能留缝的维度：**"规则长度压缩率"作为显式指标**（区别于 CompAct-Bench 的上下文压缩）——🟡 部分空白，但太薄，撑不起独立 bench。

## 撞车证据（真实 arXiv ID，abs 页验证）
| 论文 | ID | 日期 | 做什么 | 撞谁 |
|---|---|---|---|---|
| CodeARC | 2503.23145 | 2025-03 | inductive program synthesis：从 I/O 例归纳函数、**泛化到未见输入**、1114 函数、**interactive differential testing oracle**（查隐藏函数→合成候选→按反馈迭代修正）、18 模型 o3-mini 才 52.7% | **C + D 双撞**：C 的"从例归纳+未见例泛化"，D 的"猜测-验证闭环"（oracle 反馈迭代） |
| BabyTheorist | 2611.08177 | 2026-11-05 | observational theory learning：从纯观察归纳可复用理论、泛化到新情境、curriculum + continual train-test | C 的"归纳理论+泛化" |
| CompAct-Bench | 2611.25673 | 2026-11-19 | working-context compaction：压缩 agent 工作上下文、看下游任务完成度、controlled retention ratios | "压缩"维度——但是**上下文压缩**，不是我们的"规则长度压缩" |
| SWE-bench 系 | [来源③，未本轮验证 abs] | 2023- | bug 修复 pass/fail（给 issue+repo→修对） | D 的"修对"，但不显式测"先猜 bug 再修" |

## 逐维度判定
1. **从例子归纳 + 未见例泛化（C 核心）**：🔴 CodeARC 已做（1114 函数、held-out 泛化、interactive）。我们 C 的 12 例→规则→10 未见例，是 CodeARC 的迷你版。
2. **猜测-验证闭环（D 核心）**：🔴 CodeARC 的 differential testing oracle 就是这个闭环（合成→跑 oracle→按反馈修正）。SWE-bench 系测修对不测先猜，但 CodeARC 补上了"先猜"。
3. **规则长度压缩率（C 的"压缩"）**：🟡 唯一留缝。CompAct-Bench 测的是上下文压缩（token 保留率），不是"从 N 例压出的规则多短"。但单靠这一维度太薄。
4. **矛盾例鲁棒性**：[待核验] 未单独查，CodeARC/BabyTheorist 的 curriculum 可能已覆盖难度梯度。

## 对 D 问题"能否当新对标 bench"的回答
**不能当"新维度 bench"**——CodeARC 已经是"从例归纳+泛化+interactive 猜测-验证"的成熟 bench，我们 C+D 是它的低配复刻。
**能当"对标/复现目标"**——反过来用：把 CodeARC 的 1114 函数拿来当标准尺子，测**本地 27b + 不同 prompt 格式**在这个标准任务上的表现。这才是 pfb 该走的路（对标已有 bench，不是造新 bench）。

## 下一步建议（产投比）
1. **放弃"造新 bench"**（撞车，性价比低）
2. **改走"对标 CodeARC"**：拉它的 1114 函数（开源？待核验 repo），本地 27b 跑，测 prompt 格式差异是否在 CodeARC 这种难度下显现（CodeARC o3-mini 才 52.7%，27b 大概率更低 → 有区分度空间）
3. C 的"规则长度压缩率"留作**次要分析维度**，不单独立 bench

## 搜索日志
- arXiv search: "program synthesis from input output examples"（75 命中，CodeARC #9）
- arXiv search: "LLM root cause analysis bug"（37 命中，SWE-bench 系）
- arXiv search: "rule learning generalization few shot"（112 命中，BabyTheorist #2）
- arXiv search: "SWE-bench benchmark software engineering issue"（首条 CompAct-Bench）
- 真实 ID 验证：2503.23145 / 2611.08177 / 2611.25673（abs 页，来源①）
- 手搓 ID 教训：本轮先猜 2503.21978/2511.03970 全错（撞 Leibniz 代数/室内重建），改从搜索页抓真实 ID 才对——印证 skill"手搓 ID 必幻觉"。
