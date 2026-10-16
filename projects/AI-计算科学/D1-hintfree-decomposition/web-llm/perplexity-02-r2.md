origin: ai
service: Perplexity (perplexity.ai)
url: https://www.perplexity.ai/
time: 2026-09-26 15:26 (Asia/Shanghai)
ego-ref: taskSpace "02-r2-webllm" / page p2 (task.newPage) / composer @14
method: Ego Lite ego-browser 真实浏览器 — newPage + goto + fill @14 + press Enter + 等待流完成 + evaluate 提取
independently_supported: yes (29 来源, 独立于 ChatGPT 来源: Berkeley stat.berkeley, NIST csrc.nist SP 800-22 Rev.1a, UCL www0.cs.ucl.ac, CMU cmu, SHOP2 Nau jair, IJCAI Alford/Shivashankar/Roberts/Frank/Aha)

# 问题（同 stage-01 空缺 G1/G3/G4 研究）
方法论研究：把目标递归分解成互相正交、合覆盖因素，到原子。可验证权威来源+精确条件+不确定性，三点：(1) 正性(orthogonality)与合覆盖(completeness)标准数学框架与定义（partition disjoint+exhaustive / σ-代数 / 概率独立 P(A∩B)=P(A)P(B)）；(2) 判定"原子"/递归终止标准（well-founded relation / ranking measure μ(child)<μ(parent)）；(3) 仅方法+通用示例的分解能否对任意目标保持有结构(generality)——HTN / generalized planning 相关研究。每点: 来源(作者/年份/标准名)+条件+不确定性。

# 回答（关键内容，Ego 提取）

## 形式化
G→D{G_1,…,G_k}，子目标集合须满足: 正性(不重叠或共享关系显式建模)、完备性(实现父所需内容被覆盖)、终止性(无无限下降链)、保真性(子完成↔父完成有充分/必要/等价关系)。先区分: 集合"不相交"、概率"独立"、工程"互相正交" 三不同概念; 概率独立≠集合不相交。

## 1. 正交 + 合覆盖
- 集合 partition (最严格, 互斥且穷尽): 全集 U, 集合族 {C_i} i∈I 是 U 的 partition ⟺ ⋃_{i∈I}C_i=U (exhaustive: ∀x∈U ∃i∈I x∈C_i) ∧ i≠j⇒C_i∩C_j=∅ (disjoint)。来源: Berkeley 概率公理 (stat.berkeley) — 不相交事件 P(A∪B)=P(A)+P(B), 事件拆互斥穷尽区域。
- σ-代数: F⊆2^Ω 是 σ-代数 ⟺ Ω∈F, A∈F⇒A^c∈F, A_1,A_2,…∈F⇒⋃A_n∈F。在 (Ω,F,P): Ω 样本空间, F 可测事件, P 概率测度; 此处"完备"= 对补集/可数并封闭, 不自动意味着选子目标构成 partition。
- 概率独立: NIST 定义 P(A∩B)=P(A)P(B) (知道 A 不改变 B 概率), 列于 NIST SP 800-22 Rev.1a 术语体系 (csrc.nist)。事件族 {A_i} 相互独立需 ∀ 有限子集 J⊆I: P(⋂_{j∈J}A_j)=∏_{j∈J}P(A_j) — 比成对独立更强。
- 精确条件: "正交"=同一实例不能归两因素 → partition 条件 ∀i≠j C_i∩C_j=∅; "合覆盖"=任何有效实例≥1 因素 → ⋃C_i=U; 恰好一个 → ∀x∈U ∃!i x∈C_i。U 可 = "实现目标 G 相关状态/需求/约束/方案空间"。例: 完成可靠发布 → C1功能正确性,C2安全性,C3可运维性,C4合规性 (仅严格 MECE 若规定 U 并证明不重叠+覆盖)。
- 重要区分: 集合不相交 A∩B=∅(不重叠) / 概率独立 P(A∩B)=P(A)P(B)(否, 可同时发生) / 向量正交 ⟨x,y⟩=0(否除非另有结构)。概率独立事件可同时发生 → 不能用 P(A∩B)=P(A)P(B) 替代"互斥"。
- 不确定性: "完备"须相对明确 U 或 R(G), 无全集无法证明覆盖; "不相交"可能仅某抽象层级(概念层不重叠, 实现层共享资源); 许多工程因素=交叉约束不可划分 → 正交主维度+交叉约束模型 X_ij⊆R(G_i)×R(G_j), 而非假装 MECE。

## 2. 原子 + 递归终止
- 标准框架 = 良基关系 (well-founded relation) + 排名函数 (ranking function)。≺ 是 S 上的二元关系, 无无限下降链 s_0≻s_1≻s_2… → 良基。来源: UCL 程序终止理论 (www0.cs.ucl.ac) — 良基=不允许无限序列; 排名函数=映射到良序集。
- 递归: G_i≺G; 若良基 → 无无限递归 G_0≻G_1≻G_2…
- 实用证明 = 构造排名测度 μ:G→W (W 良序: ℕ, ℕ^k 字典序, 序数), 每递归分解 μ(G_i)<μ(G) → 终止充分条件。来源: CMU 程序验证课程 (cmu) — ranking function 把状态到有限下降结构, 每步严格下降。
- 精确原子: Atomic(G)⟺ApplicableDecomposition(G)=∅; 或更强 Atomic(G)⟺∃ 可执行原语动作 a 直接实现 G。
- 层次: 语法原子(规则库无适用分解) / 语义原子 / 原语原子。

## 3. generality
- 结论: 不能无条件下保证。"方法+通用示例"=可迁移分解启发式, 但保证对任意目标结构上一般性需明确: 目标空间、状态/动作语言、分解规则表达能力、方法是否允许参数化/分支/递归/组合、"泛化"=可表达/可求解/可证明正确/跨实例性能稳定。
- HTN 对应: 复合任务 C=待分解目标, 方法 m=分解规则, 原语任务 O=可执行动作, 方法前置条件=何时适用, 方法子任务网络=如何递归展开。来源: Nau 等 SHOP2 论文 (jair) — HTN 通过方法把任务递归分解到可直接执行原语; 复合任务多方法 → 搜索空间。标准化 HTN: m=(h,χ,N) h=方法头(复合任务), χ=适用条件, N=子任务网络; 若 h 复合→选满足 m 替换 h 成 N; 若原语→调用动作算子。
- 四性质区分: 表达一般性(能表示某类目标/解, 需表达能力/表示定理) / 求解一般性(总能找到解, 需完备+终止) / 正确性(方案实现目标, soundness/保真) / 跨实例泛化(未见实例有效, 需归纳偏差/分布假设/经验验证)。仅一套方法+通用例子最多支持"经验迁移性", 不能推出前三严格性质, 更不能 ∀ 目标保证。
- HTN 限制: Alford, Shivashankar, Roberts, Frank, Aha IJCAI 论文 — HTN/HGN/GTN 表达能力; 标准 HTN 核心操作=方法把任务递归分解到原语动作序列; 不同层级规划语义保解翻译; 标准 HTN 一般情况半可判定性 (ijcai)。→ 某些层级规划可翻译保解集; 方法体系强表达; 但强表达≠每目标自动可解判断; 一般 HTN 可解性可能半可判定。
- SHOP2 (Nau jair): HTN 方法通常领域特定"标准操作程序", 规划器领域无关; 方法库领域知识提高效率, 能力来自方法设计, 不是通用规划器自动获得。
- 两解释: A 方法=模板(目标→{资源,动作,约束,验证}) 可迁移但仅结构相似, 不保证完整覆盖(=元方法/分析框架); B 方法=领域完备 HTN 方法库(每复合目标有方法, 每状态正确前置, 每方法网络可达原语) → 对声明领域证明 目标完成⟺∃合法原语计划, 仅声明领域/目标语言成立, 不是 ∀ 目标。
- 可验证泛化条件: ∃ 目标类 G、方法抽象 M、原语动作语言 A 使 ∀G∈G ∃ finite derivation G⇒*A_1,…,A_n ∧ Execute(A_1,…,A_n,s)⊨G; 完备性 ∀π Execute(π,s)⊨G⇒∃ HTN derivation 等价 plan; 终止 ∃ well-founded μ G_i∈D(G)⇒μ(G_i)<μ(G); 方法正合覆盖 ⋃_{m∈M}Dom(m)⊇G_target, 互斥时 m≠m'⇒Dom(m)∩Dom(m')=∅。但 HTN 方法域重叠通常有意(多可行方案) → 更合理条件 = ∀G∈G_target Dom(m_1)∪…∪Dom(m_k) 覆盖 G, 允多方法适用=搜索分支。
- 不确定性: "任意目标"=任意自然语言目标 → 通常无明确语义, 无法定义完备性; 强目标空间(任意计算/递归/无限状态) → 可能不可判定, 不应承诺普适自动分解; HTN 高表达↔高复杂度/不可判定 (已有研究 HTN 限制复杂度 PSPACE-complete 到 EXPSPACE-complete, 一般半可判定, ijcai); "训练示例结构相似"≠未见目标形式化泛化证明, 需目标类定义/分布假设/保真映射/外部验证; 方法重叠→非确定性/搜索爆炸/重复分解, 覆盖性与互斥性分开处理。
- 可操作判定协议: 1 定义宇宙(U,R(G),S); 2 子目标语义(每 G_i 可判定 Done(G_i,s)); 3 覆盖 R(G)⊆⋃R(G_i); 4 正性(互斥证明 R(G_i)∩R(G_j)=∅, 否则显式交叉约束); 5 保真 ⋀Done(G_i,s)⇒Done(G,s); 6 终止(良基 μ, G_i∈D(G)⇒μ(G_i)<μ(G)); 7 原子(最小排名目标→原语动作/判定器/证明); 8 泛化范围(一实例/有限领域/形式化目标类/任意目标)。
- 最重要结论: "正交+合覆盖"=分解质量, "良基+排名"=递归终止, "HTN/广义规划"=方法表达与求解, 三者不能互相替代。声称仅方法+通用示例 ∀ 目标一般性至少需: 目标语言、方法覆盖定理、保真证明、终止证明、表达/不可判定边界限定。

## 来源 (29)
Berkeley stat.berkeley (概率公理/不相交事件); NIST csrc.nist SP 800-22 Rev.1a (独立定义); UCL www0.cs.ucl.ac (良基/排名); CMU cmu (ranking function); SHOP2 Nau jair (HTN 递归/领域特定方法); IJCAI Alford/Shivashankar/Roberts/Frank/Aha (HTN/HGN/GTN 表达/半可判定/复杂度 PSPACE~EXPSPACE-complete)。
