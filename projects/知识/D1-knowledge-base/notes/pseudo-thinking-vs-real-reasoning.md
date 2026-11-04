# origin: ai（意图锚: KB 队列第9篇，兴趣方向 C 区 #8『伪 thinking / 推理时计算』——成璐 S3 场景亲自质疑点。素材 = 02.5 六调研字段已核验证据：Wei 2022 CoT 规模涌现 / In-The-Wild post-hoc rationalization 率 / Introspective Faithfulness flip-pair / Setlur TTS VB>VF / Agarwal 7B-235B TTS 系统研究。）
# status: v1 — 第九篇教材 note(伪 thinking vs 真推理)
# 给懒惰兴趣驱动的人: 每概念 是什么/为什么/边界, 带 conf, 结尾收可证伪预测

# 模型说它在思考，怎么知道它没在表演

前八篇讲了 agent 的记忆、检索、控制层。这篇换一个更底层的疑点：一个模型输出一段"推理过程"，我怎么知道这段过程真的参与了答案的产生，而不是答案先生成完、再补一段流畅的论证？这个问题我在 S3 场景里亲自问过——本地 27b 开着 thinking 跑任务，那些 thinking token 到底是在算还是在演？我觉得这问题问得值，因为它直接决定我 autoresearch 系统里"读什么"的设计。这篇把 2022 到 2026 的实证研究串起来，回答三件事：CoT 什么时候真有用、伪 thinking 长什么样且怎么检测、推理时加计算在小模型上划不划算。每个块讲清是什么、为什么、边界在哪，关键声明带 conf。

## A. 概念块

### 1. CoT 与 scratchpad：中间步骤的两张皮
- **是什么**: chain-of-thought prompting 是让模型在答最终答案前先写中间步骤；scratchpad 是更早的说法（Brown et al. 2020 用 "GPT-3 can perform complex arithmetic by writing intermediate steps on a scratchpad"）。两者机制假设相同：把多步问题拆成中间步骤，为难题分配额外解码计算。区别只是时代标签——2022 年前叫 scratchpad，之后叫 CoT。我翻回原文确认过，这两个词指的就是同一件事。后来社区分着用纯粹是习惯。
- **为什么有效（以及只在多大以上有效）**: Wei et al. NeurIPS 2022 的关键发现是规模涌现：<100B 的模型上 CoT 没有正收益。小模型生成的中间步骤流畅但不合逻辑，反而低于 standard prompting。PaLM 540B + 8 exemplar 才在 GSM8K 拿到 58.1%。也就是说 CoT 不是"提示技巧"，是能力阈值现象——模型先有做对的能力，CoT 才把它释放出来。conf 0.9
- **边界**: 长度也有最优区间。Thinking-Optimal Scaling (2025, OpenReview) 报告过度拉长 CoT 会在某些域伤害性能（overthinking）。所以"多写点推理"不是单调收益，存在拐点。这个拐点位置目前只有大模型上的粗测量，小模型上没人认真测过——这是本篇后面 TTS 拐点的伏笔。conf 0.8

### 2. 伪 thinking 判据线 A：post-hoc rationalization（事后合理化）
- **是什么**: 同题换成正反问法，模型系统性给出 Yes/Yes 或 No/No，但两边都配流畅论证——说明论证是为预设答案服务的，不是推导出来的。In The Wild Not Always Faithful (2025, arXiv 2503.08679) 在真实 prompt 上实测生产模型：GPT-4o-mini 13%、Haiku 3.5 7%、Gemini 2.5 Flash 2.17%、ChatGPT-4o 0.49%、DeepSeek R1 0.37%、Gemini 2.5 Pro 0.14%、Sonnet 3.7 thinking 0.04%。thinking 模型普遍更低，但没有一家是零。我把这张表抄下来过。最扎眼的是 GPT-4o-mini 的 13%，小一号的生产模型伪 thinking 率能高一个数量级。
- **为什么这条判据可用**: 它是行为测试不需要读模型内部：flip-pair 一致率（正反问法答案是否被论证方向绑架）+ 删掉中间步骤后答案不变率（步骤冗余度）两个可操作指标就能量化"论证对决策的真实贡献"。比任何单一模型自评都可复核。conf 0.85
- **边界**: 该文献还记录了 unfaithful illogical shortcuts——模型用微妙不合逻辑的推理让投机答案显得像严格证明。这种 case 单靠 flip-pair 抓不全，需要配合数学一致性检查。另外 13% 是 GPT-4o-mini 在特定题型下的数字，跨模型外推要谨慎。conf 0.75

### 3. 伪 thinking 判据线 B：introspective faithfulness（内省忠实度）
- **是什么**: Introspective Faithfulness (2026, arXiv 2605.27773) 做了 200 题 × 8 模型 × 4 条件的实验：flip pairs 保留 96% same-answer 相似度（cosine 0.784 vs 0.817，d=0.34；ROUGE-L d=0.45）。表面推理文本对最终决策几乎不敏感。真正的自我知识信号在 self-rated confidence 层：obscure facts 条件下 p<0.001、r=0.134，model-specific（GPT-4o 是唯一可靠耦合的模型，Δ=-0.132）。native-reasoning 模型的 internal thinking tokens 比 user-facing CoT 决策敏感性更高（Wilcoxon p=0.033）。我读这篇时最意外的就是那个 96%——论证文本几乎不随决策变。跟我直觉相反。
- **为什么这条最重要**: 它直接回答了"读什么"的问题——读逻辑论证是错的，confidence 表达才是真自我知识所在。我猜这就是为什么我设计 logprob 探针时坚持"只排序不触发"：触发要靠行为信号，而行为信号在 confidence 层不在论证层，探针只做优先级排序正好避开循环论证。conf 0.85
- **边界**: r=0.134 是弱信号，且 model-specific——不能假设所有模型都有可用的 confidence 通道。对不开 thinking 的模型，user-facing CoT 的决策敏感性更低，判据效力打折。conf 0.7

### 4. test-time compute scaling 在小模型上的拐点
- **是什么**: test-time scaling（TTS）指用更多推理时间/采样换准确率。Setlur et al. (2025, arXiv 2502.12118) 在 3B/8B/32B 上验证了 TTS 扩展需要验证信号渐优（VB > VF，verification-based 优于 verification-free），否则多花的时间只是在放大错误。Agarwal et al. (2025, arXiv 2512.02008) 扫了 7B-235B 共 8 个模型：没有单一 TTS 策略普适占优。小模型 + 高级推理算法（如 Lemma-7B + tree search）可以 Pareto 胜过更大模型（ICLR 2025 proceedings 第三源印证）。
- **为什么关心拐点**: 大模型上的 TTS 曲线（更多采样 → 更高准确率）能否外推到 7B-27B？Wei 2022 已经暗示小模型连 CoT 本身都不受益，那么 TTS 拐点在小模型上大概率显著左移甚至不存在正收益区。我翻了一圈没找到公开数据直接回答"27B 本地模型的 TTS 拐点在哪"——这是本地实验能填的空，也是我觉得这篇最值钱的落点。conf 0.8
- **边界**: "无普适策略"意味着结论高度依赖任务分布。数学题上的 TTS 曲线和开放问答上的不可混用。小模型 Pareto 胜大模型的 case 也集中在结构化推理任务，泛化性存疑。conf 0.7

### 5. verify/自校验在小模型上是正收益还是错误放大器
- **是什么**: 自校验（self-verification / self-consistency 变体）让小模型检查自己的答案。Setlur 的证据是 verification 是 TTS 收益的前提（VB>VF）。没有可靠验证信号的模型，加 verify 步骤等于加噪声。Lemma-7B + tree search 超过 34B MATH 分数（ICLR 2025）说明"小模型 + 好的搜索结构"路线成立，但那是算法侧补偿，不是模型自校验。
- **为什么风险不对称**: 大模型自校验通常正收益（能力强到能发现自己的错）；小模型可能负收益——它发现自己错误的概率低于它把对的改成错的概率。错误放大风险在小模型上更高，因为"判断自己错了"本身需要高于平均水平的元认知能力。我倾向认为 27b 落在这个负收益区，但这是猜想不是证据，C 段预测 2 就是来验证它的。conf 0.75
- **边界**: 目前缺"同一小模型开/关 self-verify 的 matched 对照"公开数据。现有证据都是跨模型或跨方法比较，因果链不完整。本地 27b 可以做这个对照实验。conf 0.7

### 6. 习惯刻入权重 vs prompt：推理行为的来源分层
- **是什么**: 成璐 S3 质疑的第二半：模型的"推理习惯"（比如爱写冗长论证、爱用特定解题模板）是权重里的还是 prompt 诱导的？现有证据支持分层。CoT 的行为模式（写不写步骤）主要由 prompt 触发——Wei 2022 的 standard vs CoT prompting 对照就是纯 prompt 效应。但步骤的质量（合不合逻辑）由权重决定，小模型写得出流畅但错误的步骤，这就是权重天花板。thinking 模型的 internal reasoning 则是第三种来源——训练目标直接优化了推理过程（R1 系），prompt 只能开关不能改风格。
- **为什么这个分层重要**: 它决定了干预手段的选择空间。想改变"写不写步骤"→改 prompt 就行；想改变"步骤质量"→只能换模型或 fine-tune；想改变"internal thinking 风格"→当前无法外部干预，只能选模型。我设计 autoresearch 系统时就是按这个分层下注的："防御性语言=调研入口"赌的是第一层（prompt 可达），logprob 探针赌的是第二层（权重可读）。如果分层错了，整个系统的读取面就选错了。conf 0.8
- **边界**: 三层分界不干净——长上下文里的 few-shot 示例能部分覆盖第二层（in-context learning 改变步骤质量），RLHF 后的模型 prompt 敏感度也变了。分界是经验性的不是原理性的。conf 0.65

## B. 成璐视角

**判断**: "伪 thinking"不是一个 bug，是一个测量面。模型输出的推理文本天然对决策低敏感（flip-pair 96% 保留）。所以"读论证判断它是否在真思考"这条路从根上就走不通——就像第 8 篇说的 turn-level 信号判不了 goal-level 完成，这里的论证文本是 turn-level 信号，决策贡献是 goal-level 量。正确的测量面是 confidence 层和行为一致性（flip-pair 一致率、删步骤不变率），不是文本内容。我的 logprob 探针定位（只排序不触发）正好落在这个测量面上，我觉得这个设计现在有了文献支撑。

**自我质询**: 我前面说"读 confidence 不读论证"，但 confidence 本身也是模型生成的文本，不也可能被 prompt 操纵吗？反例：让模型"自信一点"会抬高 self-rated confidence，而实际正确率不变。修正：confidence 的信号价值来自它的 model-specific 耦合结构（哪类问题上 confidence 变化预测正确率变化），不是它的绝对值。单看数值会被操纵。看跨题型的校准曲线才有信息量。所以判据应该是校准曲线 + flip-pair 的组合，不是单一 confidence 读数。

**动机**: 这篇接住我在 S3 场景的两个未闭合质疑（伪 thinking 怎么检测、习惯在权重还是 prompt），同时给本地 27b 实验指了三个可做的空：TTS 拐点位置、self-verify matched 对照、logprob 探针 vs confidence 校准曲线的对照。前八篇建了框架，这篇把"推理时计算"这块补上，C 区 #8 闭合。我要的教材感在这里兑现——不是罗列论文，是让我下次开 thinking 跑任务时知道该盯哪个信号。

**idea (conf 0.5)**: 给本地 27b 做一个"伪 thinking 指数"：对同一批 50 题分别跑 (a) 正常 CoT (b) 删掉中间步骤只留首尾 (c) 正反问法 flip-pair，统计答案不变率和论证相似度，得到一个 0-1 的"论证对决策贡献度"。如果 27b 的指数显著高于生产模型（比如 >0.5），说明小模型的 CoT 更多是表演性的，那我 autoresearch 系统里"读 thinking 内容做缺口标记"的设计就该砍掉，只保留 logprob 探针。成本约 50×3 次推理 ≈ 2h（8787 端口现成）。

**明确砍掉**: 不展开各厂商 thinking 模型（R1/o1/Claude thinking）的内部机制对比——闭源细节不可考，营销污染重。不写 RLHF/DPO 如何塑造推理风格的训练侧分析——那是训练机制篇（第一篇）的地盘，这里只接边不重复。不讨论 interpretability（circuit analysis/probing）路线——需要白盒访问，本地 27b 虽开源但 circuit 级分析超出本 note 范围，留给专门调研。

**一句话**: 推理文本对决策低敏感是结构性事实（flip-pair 96% 保留）。伪 thinking 的检测要读 confidence 校准和行为一致性，不读论证内容。小模型上 CoT/TTS 的收益拐点未知，本地 27b 是填这个空的唯一低成本实验台。我觉得这篇最该记住的就是前半句——下次有人拿"看它的 reasoning trace"当验证手段，直接引用 flip-pair 数据怼回去。

## C. 可证伪预测（带判死条件）

1. **预测**: 本地 qwen3.8-27b 的"伪 thinking 指数"（定义见 B 段 idea）>0.5，即其 CoT 论证对最终决策的贡献度低于生产模型中位数（~0.3-0.5 区间，按 post-hoc rationalization 率 0.04%-13% 反推）。我押它落在这个表演区。
   **判死**: 若实测指数 <0.3，说明 27b 的 CoT 论证与决策耦合度不低于生产模型，"小模型 CoT 更多是表演"的猜想不成立，autoresearch 系统保留"读 thinking 内容做缺口标记"的设计。验证方法：50 题 × (正常 CoT / 删步骤 / flip-pair) 三条件对照，统计答案不变率与论证 cosine 相似度。成本 ~2h @ :8787。

2. **预测**: 本地 27b 上 self-verify（让模型检查自己答案后再输出）的净收益 ≤0，即在 matched 对照下开 verify 的正确率不高于关 verify（错误放大 ≥ 纠错收益）。
   **判死**: 若开 verify 组正确率比关 verify 组高 ≥3pp（噪声带 ±1.5pp 之外），说明 27b 的元认知能力足以支撑自校验正收益，"小模型 verify 是错误放大器"的边界判断需修正为"取决于具体任务分布"。验证方法：同 50 题集开/关 self-verify 两组，judge 用异源模型避免同模型相关误差。成本 ~4h。我要的是这个对照跑完能直接回答"27b 该不该开 verify"，而不是再出一篇模糊结论。