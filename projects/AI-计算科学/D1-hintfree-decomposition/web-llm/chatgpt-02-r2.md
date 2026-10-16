origin: ai
service: ChatGPT (chatgpt.com)
url: https://chatgpt.com/
time: 2026-09-26 (Asia/Shanghai)
ego-ref: taskSpace "02-r2-webllm" / page p1 / composer @83
method: Ego Lite ego-browser 真实浏览器 — fill @83 + press Enter + 等待流完成 + evaluate 提取
independently_supported: yes (回答引用多个独立权威来源: Harvard 概率教材、Encyclopedia of Mathematics、MIT OCW 6.042、Erol/Nau/Hendler 1993、Georgievski & Aiello、Srivastava 2022)

# 问题（stage-01 空缺 G1/G3/G4 研究）

我在研究"目标递归分解"方法论（把目标拆成互相正交、合覆盖因素，递归到原子）。缺三个可验证判标准，请给出权威来源线索、精确条件、不确定性/边界，不要只结论：
(1) 正独立性/正性(orthogonality)与合覆盖(completeness)如何操作化测试——标准数学/决策分析框架（概率独立事件、σ-代数、partition disjoint+exhaustive）？定义与来源。
(2) 因素如何判定"原子"（不能再分解）——标准终止条件（well-founded relation / 递归终止 / 单位元素）？
(3) 一套"仅方法+通用示例"分解提示能否对任意目标结构保持有结构逐层分解(generality)——相关研究（decomposition / problem reduction / HTN generality）？
每点给出：可验证权威来源（作者/年份/链接或标准名）、精确条件、不确定性。

# 回答（关键内容，Ego 提取）

## 1. 正交 + 合覆盖
- 最严格 = finite partition: Disjointness F_i∩F_j=∅ (i≠j) + Exhaustiveness ∪F_i=Ω。来源: Harvard 概率教材（finite partition = pairwise disjoint + union 全空间；有限 σ-algebra 的 atoms 形成 partition）。→ 可验证判据: ∀i≠j 交集空 ∧ union=Ω。
- 边界1: 很多"目标因素"（提高收入/降低成本/提高资产利用率）不是 mutually exclusive events → partition 太强。
- 弱版本 = set cover / exhaustive coverage: 只 Ω⊆∪F_i，允许 F_i∩F_j≠∅。
- 若"正交"指 statistical independence: P(A∩B)=P(A)P(B) 或 P(A|B)=P(A) (P(B)>0)。来源: Encyclopedia of Mathematics。n 事件 mutual independence 需所有有限子集乘积条件，两两独立≠mutual independence（Encyclopedia 明确）。
- 建议定义: Orthogonality criterion = 一个因素不能承担另一因素的判定责任 + 无定义重复覆盖。Level1 严格 F_i∩F_j=∅; Level2 功能正交 DecisionRole(F_i)∩DecisionRole(F_j)=∅（Level2 是方法论定义，非标准数学）。
- 不确定性: 先须规定 ontology（因素=事件/状态集合/变量/评价维度/子目标？），否则"正交"无唯一数学测试。相关≠不能作为两因素；不要把 orthogonal=statistically independent 作为公理。

## 2. 原子 + 停止
- 核心 = well-founded relation + decreasing measure: 关系 < 无无限下降链 → well-founded。每次分解"往下走"且不能无限。
- ranking/measure: 每目标 x 有 μ(x)∈W（W well-founded, 如 ℕ）；真分解 x→x_i 要求 μ(x_i)<μ(x) → 递归不能无限。来源: MIT OCW 6.042/Algorithms（非负整数 measure 严格下降 → 终止）。
- 严格原子: Atomic(x)⟺¬D(x)（不存在满足 decomposition rules 的合法进一步分解）。
- 关键区别: "不可分解"≠"应该停止"（"提高生活质量"可无限分）。→ Atomic(x;R,C) 相对给定 rules R 与 granularity C。
- 程序验证 termination condition 直接借鉴: Decompose(x){ if Atomic(x) return x; children=Split(x); require Coverage, Orthogonality, μ(child)<μ(x); return Decompose(children);} 三 proof obligation: 不漏→不重→不无限。
- 另一含义: 代数/格论 atom = 最小非零元素（偏序: 不存在 0<x<a）。接近但≠绝对不可分解。
- 建议: 用 "relative atomicity under a specified decomposition relation"，不声称 universally accepted definition。
- 不确定性: 选择 measure（复杂度/抽象/信息量/规模）可能非天然全序；termination 可严格证明，"何时足够原子" domain-dependent。

## 3. generality
- 谨慎结论: 有研究 formalize generalized plans/hierarchical decomposition，但**没有已证明的"通用分解提示"对任意目标保持正确层级**。
- HTN (Hierarchical Task Network): Task→Subtasks→Primitive Tasks; compound task 递归 via decomposition method。来源: Georgievski & Aiello HTN overview (arXiv) — expressiveness/domain authoring/competence/performance/applicability; HTN 核心特征=依赖丰富 domain knowledge。
- Erol, Nau & Hendler 1993 "General Framework for HTN Planning" (ResearchGate) — 形式化 decomposition methods, 研究 soundness/completeness。
- 关键: "general" 两含义 — (a) 一个 decomposition rule 解决所有领域（假）; (b) 一个形式主义表达很多 domain 的 decomposition systems（真）。
- 更接近问题 = Generalized Planning: Srivastava 2022 "Hierarchical Decomposition and Analysis for Generalized Planning" (arXiv) — generalized plans 适用一类 problems; termination/goal reachability/scope/utility/hierarchical termination arguments。
- generality 可测试: 定义问题族 P + procedure D; 问 ∀P∈P, D(P) 满足 Termination/Soundness/Completeness/Goal reachability/Structural validity。General(D,P)=|{P:D 满足}|/|P|（empirical metric, 非 HTN 标准定义）。Scope(D)={P: D sound+terminating on P}。
- 通用示例不能证明 generality: 有限测试集 ≠ ∀x D(x) valid。区分 Demonstrated (∀x∈T Valid) / Formal (∀x∈P Valid) / Universal (∀x, 需先定义"所有目标"domain)。
- 合成框架: G→D{G_i} 每分解三/四 gate: A Coverage/Orthogonality (∪G_i⊇G, 可选 ∩=∅); B Progress/Termination (∃ well-founded μ, μ(G_i)<μ(G)); C Atomicity (Atomic(G)⟺∄G'[G→D G']); D Generality (∀P∈P: Termination∧Coverage∧Validity; 若仅实验 → Pr[Valid(D,P)]≥1−ε = empirical generalization)。

## 权威来源地图
| 问题 | 成熟理论 | 核心判据 | 来源 |
| 正交+合覆盖 | Partition / probability independence | disjoint+exhaustive; P(A∩B)=P(A)P(B) | Harvard Probability; Encyclopedia of Mathematics |
| 原子+停止 | Well-founded relation / termination | μ(child)<μ(parent), μ well-founded | MIT 6.042/Algorithms |
| 层级递归 | HTN planning | compound→methods→primitive | Erol,Nau&Hendler 1993; Georgievski&Aiello |
| generality | Generalized Planning | scope/utility/termination | Srivastava 2022 |
