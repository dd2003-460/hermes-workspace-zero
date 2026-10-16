origin: ai
输入路径:
- /Users/a1-6/Desktop/workspace/projects/D1-hintfree-decomposition/tasks/01-goal-decomposition-r1.md（空缺 G1-G5）
- /Users/a1-6/Desktop/workspace/projects/D1-hintfree-decomposition/web-llm/chatgpt-02-r2.md（Ego Lite 真实浏览器）
- /Users/a1-6/Desktop/workspace/projects/D1-hintfree-decomposition/web-llm/perplexity-02-r2.md（Ego Lite 真实浏览器）
观察时间: 2026-09-26 15:31 (Asia/Shanghai)

# 02 信息研究 r1 — 仅研究 01 空缺 G1/G3/G4（+G2 入口）

> 按 main-8.7-loop 阶段 02 角色：研究 01 阶段空缺，不执行、不改分解。
> 两独立 Ego Lite 网页 LLM 回执已落盘（chatgpt + perplexity），硬门满足。
> 注入零领域答案；全部结论挂权威来源 + 标注不确定性。

## 硬门确认（两真实 Ego Lite 回执）

| 服务 | 方法 | 独立来源 | 文件 |
| ChatGPT | ego-browser p1 fill @83+Enter+evaluate | Harvard 概率教材、Encyclopedia of Mathematics、MIT OCW 6.042、Erol/Nau/Hendler 1993、Georgievski & Aiello、Srivastava 2022 | web-llm/chatgpt-02-r2.md |
| Perplexity | ego-browser p2 newPage+fill @14+Enter+evaluate | Berkeley stat.berkeley、NIST SP 800-22 Rev.1a、UCL、CMU、SHOP2(Nau)、IJCAI(Alford/Shivashankar/Roberts/Frank/Aha) | web-llm/perplexity-02-r2.md |

两服务来源集合**完全 disjoint**（ChatGPT: Harvard/MIT/Encyclopedia/HTN-1993/Srivastava；Perplexity: Berkeley/NIST/UCL/CMU/SHOP2/IJCAI）→ 独立支持成立。

## G3 操作化正交 / 合覆盖测试（合成两独立来源）

两服务独立给出同一三层判据，来源不同 → 交叉确认：

- **合覆盖 (exhaustive)**: ⋃_{i} C_i = U（U = 实现目标 G 相关状态/需求/约束/方案空间）。
- **正性 (disjoint)**: ∀ i≠j, C_i ∩ C_j = ∅。
- 两者同时 = **finite partition**（Harvard 教材 / Berkeley 概率公理独立确认）。
- 弱版本 = **set cover**（仅 ⋃C_i ⊇ U，允许交集）— 两服务独立指出"目标因素"（如 提高收入/降低成本）不是 mutually exclusive events → partition 太强，须允许 cover。
- **关键区分**（两服务独立一致）: 集合不相交 A∩B=∅（不重叠）≠ 概率独立 P(A∩B)=P(A)P(B)（可同时发生，NIST SP 800-22 定义）≠ 向量正交 ⟨x,y⟩=0。→ 方法论"正交"应 = 集合交集空（互斥），**不**用概率独立作为公理。
- **可操作判定**（Perplexity 独立给出 8 步协议）: 定义宇宙 U/R(G)/S → 子目标可判定 Done(G_i,s) → 覆盖 R(G)⊆⋃R(G_i) → 正性 R(G_i)∩R(G_j)=∅（若不能证明则显式交叉约束 X_ij⊆R(G_i)×R(G_j)，不假装 MECE）→ 保真 ⋀Done(G_i,s)⇒Done(G,s)。

→ G3 空缺**部分闭合**: 操作化测试 = partition 判据（严格）/ cover 判据（弱）+ 8 步协议。剩余不确定性: 须先规定 ontology（因素=事件/状态/变量/维度/子目标？），否则"正交"无唯一测试（两服务独立一致）。

## G4 原子判定标准（合成两独立来源）

- **核心 = well-founded relation + ranking measure μ**: 关系 ≺ 无无限下降链 → 良基（UCL 独立定义）；每真分解 μ(G_i)<μ(G)，μ 值域良序（ℕ/字典序/序数）→ 递归终止（MIT OCW 6.042 + CMU 独立确认）。
- **严格原子**: Atomic(G) ⟺ ¬D(G) / Atomic(G) ⟺ ApplicableDecomposition(G)=∅（不存在满足 decomposition rules 的合法进一步分解）。
- **关键区别**（两服务独立一致）: "不可分解" ≠ "应该停止"（"提高生活质量"可无限分）→ 原子须**相对**给定 rules R 与 granularity C: Atomic(x;R,C)。
- 程序验证三 proof obligation: Coverage（不漏）+ Orthogonality（不重）+ μ(child)<μ(parent)（不无限）。
- 另一含义: 格论/布尔代数 atom = 最小非零元素（偏序 不存在 0<x<a）— 接近但 ≠ 绝对不可分解。

→ G4 空缺**部分闭合**: 原子判定 = relative atomicity under specified decomposition relation + well-founded measure。剩余不确定性: 选择 measure（复杂度/抽象/信息量/规模）可能非天然全序；"何时足够原子" domain-dependent（两服务独立一致）。

## G1 generality 证据（合成两独立来源，谨慎结论）

- **两服务独立一致结论**: 有研究 formalize generalized plans/hierarchical decomposition，但**没有已证明的"通用分解提示"对任意目标保持正确层级**。
- 框架: HTN（Erol/Nau/Hendler 1993 + Georgievski & Aiello + SHOP2 Nau）— compound task 递归 via decomposition method → primitive task; HTN 核心特征 = 依赖丰富 domain knowledge。
- **两含义区分**（两服务独立一致）: "general" = (a) 一个 decomposition rule 解决所有领域（假）; (b) 一个形式主义表达很多 domain 的 decomposition systems（真）。
- 更接近问题 = **Generalized Planning**（Srivastava 2022 + IJCAI Alford et al.）— generalized plans 适用一类 problems; termination/goal reachability/scope/utility。
- **generality 可测试**（两服务独立一致）: 定义问题族 P + procedure D; 问 ∀P∈P, D(P) 满足 Termination/Soundness/Completeness/Goal reachability/Structural validity。General(D,P)=|{P:D 满足}|/|P|（empirical metric, 非标准定义）。Scope(D)={P: D sound+terminating}。
- **通用示例不能证明 generality**（两服务独立一致）: 有限测试集 ≠ ∀x D(x) valid。区分 Demonstrated(∀x∈T Valid) / Formal(∀x∈P Valid) / Universal(∀x, 需先定义"所有目标"domain)。
- 不可判定边界（Perplexity 独立）: HTN 限制复杂度 PSPACE-complete~EXPSPACE-complete, 一般半可判定 → 不应承诺普适自动分解。

→ G1 空缺**部分闭合**: generality 证据 = HTN/Generalized Planning 框架 + 可测试 metric General(D,P) + 不可判定边界。剩余: 仅有限数学示例（3-5）= Demonstrated 而非 Formal/Universal → 须另 2 结构不同目标 probe（→ P2, 下一阶段）。

## G2 subagent run 入口（部分）

- 01 工件本身 = 一次 executor run 用 prompt+00-task → 真实逐层分解（已满足完成条件第 2 项静态）。
- 剩余: fresh run 对照 F2.3 判定 + 另 2 结构不同目标 probe generality（P1/P2）→ 下一阶段执行。

## 六必答（工件必须回答）

1. 目标交付: hint-free 通用分解 prompt 让任意目标→有结构逐层分解。
2. 受哪些因素: F1 交付(文本) / F2 验证(行为)（01 已拆）。
3. 已确定条件: 正性/合覆盖 = partition/cover 判据（G3 闭合）; 原子 = relative atomicity+well-founded μ（G4 闭合）; generality 框架 = HTN/Generalized Planning（G1 框架闭合）。
4. 仍缺失: ontology 规定（正交唯一测试前提）; measure 选择（原子全序）; 另 2 结构不同目标 generality 证据（G1 仅有限示例）; fresh run 判定（G2）。
5. 缺失阻塞: ontology→G3 正性判定; measure→G4 停止; 另目标→G1 Formal/Universal claim; fresh run→F2.3 全部。
6. 下一阶段优先: P2（另 2 结构不同目标 probe generality, →G1）; P1（fresh run 对照 F2.3, →G2）; 写操作化测试正交/覆盖/原子（→G3/G4 落地）。

## 不确定性登记（红线: 未验证标注）

- 所有权威来源 = 网页 LLM 自引用（ChatGPT/Perplexity 给出作者/年份/标准名），**未一手核验原文** → 标"待一手核验"。
- generality 仅有限示例 → Demonstrated, 不 Formal/Universal。
- 正性/原子须相对 ontology/measure → 不绝对。

review: 02-r1 | gap-research | pass | 仅研究 01 空缺 G1/G3/G4(+G2 入口); 两独立 Ego Lite 回执(来源 disjoint)交叉确认 partition/cover+well-founded μ+HTN/Generalized Planning; 六必答答; 未一手核验+仅有限示例标注 | 修复阶段: none