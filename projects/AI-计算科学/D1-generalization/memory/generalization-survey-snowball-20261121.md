# 泛化/跨域方向滚雪球调研（2026-11-21）
# origin: ai
# 来源①：arXiv API 本轮实查（6 组查询 + 9 篇摘要/作者实拉）；来源②：本地 D1-generalization/memory/ 既有 7 篇。

## §0 一句话结论
我们做的三件事（跨域自发探针 / CodeARC 归纳容量 / 压缩-泛化）各自撞上了**活跃且有争议的文献线**，没有完全占位的撞车，但每条线都有可对话的组。理论物理背景在"压缩-泛化"和"动力系统"两条线上是**加分项不是减分项**——那两条线的核心方法本来就是物理的（AIT/MDL、dynamical systems）。

## §1 三条线 × 前沿（全部 arXiv API 本轮实查）

### 线 A：类比/跨域推理（我们：跨域自发探针 6/6）
这条线是**有争议的**，争议点正好是我们的实验设计：
- Webb, Holyoak, Lu — *Emergent analogical reasoning in LLMs*（Nature Human Behaviour 2023）+ 回复 2404.13070（2024-04）：主张 LLM 有涌现类比能力，用**反事实任务**（打乱字母表顺序）防记忆污染
- 2308.16118（2023-08）：反方 comment——GPT-3 在最简单的变体上失败，"zero-shot 是 extraordinary claim"
- 2406.13803 — *LLMs as Models for Analogical Reasoning*（Musker, Duchnowski, Millière, Pavlick，Cambridge）：核心问题="表层复述训练分布" vs "灵活的结构映射"——**和我们的"高频启发式复述 vs 真泛化"是同一个问题**
- 2503.03666（Opiełka/Rosenbusch/Stevenson，Nottingham）：内部表征层面——找到编码不变概念向量的 attention heads，但**抽象有边界**
- 2310.01714：analogical prompting（自发生成 exemplar 再解题）——"触发"侧的成熟方案

**前沿/缝隙**：争议焦点=**记忆污染的排除方法**。Webb 用反事实改写，我们用教科书 vs 新编场景对照——两套方法都没成为标准。"同构改写后能力保持"（Claude 回答里的点 4）在文献里只有 Webb 一家在做，没形成方法论。**我们的 n 扩上去 + 两套防污染方法对照，就是可发表的贡献。**

### 线 B：压缩 ↔ 泛化（我们：K^t 框架 + 27b 实证）
- 2309.10668 — *Language Modeling Is Compression*（Delétang, Ruoss, ..., **Hutter**, Veness；DeepMind + 苏黎世联邦理工）：LLM 是强压缩器，主张用压缩视角看预测。**这条线是 AIT/MDL 物理传统，理论物理背景直接对口**
- 2402.00861 — *Evaluating LLMs for Generalization via Data Compression*（2024-02）：**用无损压缩率测训练截止后的泛化**——压缩当泛化探针，和我们的方向同构，但测的是数据压缩不是规则归纳
- 2410.15280：NCD 与分类的 disconnect（压缩-泛化不总是一致——负面结果，做实验前必读）

**前沿/缝隙**：压缩测泛化目前只测"数据压缩率"，**没人测"规则归纳的压缩率"（我们 CodeARC 的隐式做法）**。2410.15280 的 disconnect 说明压缩≠泛化不总成立——我们的 edge 实验（探了边界但归纳不出）恰好是这种 disconnect 的一个行为实例。**"压缩率预测不了规则归纳容量"可以作为一个可检验命题提出来。**

### 线 C：动力系统/物理视角（我们：ODE 跨域 + 理论物理背景）
- 2606.25039 — *LLM-ACES*（Abhyankar, Li, Kabra, Ramakrishnan, Gel, **Chandan K. Reddy**，UT Austin，2026-06）：LLM 引导的**闭环动力系统发现**——物理组在做 LLM×动力系统
- 2611.21983（2026-11-16，很新）：*LLMs as Nonlinear Dynamical Systems: Three Clocks*——把 LLM 本身当动力系统
- 2502.15208：attractor cycles（把 LLM 生成当动力系统轨迹）

**前沿/缝隙**：这条线全是"把 LLM 当动力系统研究"，**没人做"LLM 自发把现实问题建模成动力系统"（我们的探针方向）**——方向相反，缝隙干净。

### 线 D（附）：知道自己不知道（我们：防御性语言=调研入口）
- 2310.17918 — *Knowing What LLMs DO NOT Know*（2023-10）：自检测方法（多表述采样看分歧）——和我们"logprob 探针只做排序不做触发"互补，可引用

## §2 和我们实验设计的直接命中（D 问"有什么命中我们刚刚讨论的设计"）

| 我们设计的点 | 文献命中 | 状态 |
|---|---|---|
| 防记忆污染（教科书 vs 新编） | Webb 反事实任务（2404.13070） | **同问题不同方法**，可对照 |
| "高频启发式复述 vs 真泛化" | 2406.13803 核心问题 | **同一问题**，Cambridge 组在推 |
| 能力 vs 触发分离 | 2310.01714 analogical prompting（触发侧） | 触发侧成熟，能力侧没人测 |
| 压缩↔泛化 | 2309.10668 + 2402.00861 | 数据压缩有，**规则归纳压缩没有** |
| 临界场景（必须用理论才行） | 未命中 | **缝隙，我们的独有设计** |

## §3 套磁名单（泛化线，按背景匹配度排序）

1. **Grégoire Delétang / Joel Veness**（DeepMind/苏黎世，2309.10668）— 压缩-泛化正主，AIT 物理传统，理论物理背景最对口
2. **Chandan K. Reddy 组**（UT Austin，2606.25039）— 物理×LLM 活跃组，动力系统方向
3. **Sam Musker / Ellie Pavlick**（Cambridge，2406.13803）— 类比推理"表层 vs 结构"争议线，我们的探针可直接对话
4. **Claire Stevenson 组**（Nottingham，2503.03666）— 类比内部表征，边界问题
5. pfb 线（process-depth-eval-survey §5）：ResearchRubrics / Dr.Credit / DEEPRUBRIC / FinRB II — 已列，不动

## §4 局限
- arXiv 查询词有限（6 组），非穷尽；Webb 的 Nature Human Behaviour 原文没拉（arXiv 只有回复版）
- 作者机构是从论文/常识推断的（Reddy=UT Austin、Pavlick=Cambridge、Stevenson=Nottingham），**发邮件前必须逐个去组主页核实**（来源③，未验证）
- 撞车判断 conf 0.6-0.7，同前几篇
