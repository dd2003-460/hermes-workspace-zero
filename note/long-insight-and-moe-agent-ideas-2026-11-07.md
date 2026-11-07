# Note: 长程洞察可分解性 + MoE/Agent 等价性——两个 idea 的关系与开放问题

> origin: human（成璐 2026-11-07 的两个 idea，AI 补结构与文献锚点）
> 日期: 2026-11-07 · 状态: idea 收录 note，调研进行中（T-PR-07 / T-PR-08）
> 关联: paradigm-routing/tasks/T-PR-07-long-insight-decomposability.md, T-PR-08-moe-agent-equivalence.md
>        note/compression-unified-view-2026-11-07.md（压缩统一观，本 note 的上游框架）

## 成璐的原话（意图锚点）

**Idea A（长程洞察可分解性）**：
> "我看到顶级模型的出色洞察和表现，但是也许可以理解为一个长步长的迁移或者联系。但是这种肯定（有可能?）也可以被分解成更原子的步骤和联想。那么这会超过模型注意力的 ctx 范围吗，有下界要求吗，有什么不可分解的长步骤吗？或者至少某种 dense 的 net 在搜索上效率更高（更有概率跳出局部?）"

**Idea B（MoE vs 正交小 Agent 等价性）**：
> "庞大的 MoE 可以由一些大部分正交的小 agent 模拟吗，他们的纠缠、激活，有什么数学等价性吗，在什么层次等价性没有证明？"

## 两个 idea 的共同内核

两者都在问同一个问题的两面：**一个复杂系统的"涌现行为"能不能被拆解为原子组件的组合，拆到什么粒度会失效？**

- Idea A 从推理侧切入：一条 insight 是原子事件还是可分解链？分解链的长度有没有下界（ctx 窗口）？有没有本质不可分解的步骤？
- Idea B 从架构侧切入：一个巨型 MoE 的行为能不能被 N 个正交小 agent 复现？"纠缠"（组件间耦合）在哪个层面消失、哪个层面不可消除？

如果 Idea A 的答案是"存在不可分解的长步骤"，那 Idea B 的等价性就有天花板——正交小 agent 组合不出那个不可分解步骤对应的计算。反过来，如果 Idea B 证明了 L0-L1 层等价成立，那 Idea A 的"原子步骤"就有了操作化定义：等价性开始失效的那个粒度就是原子性的边界。

## Idea A 的结构化（四子问题 → T-PR-07）✅ 已完成

T-PR-07 产出：`research/long-insight-decomposability-survey.md`（394行，19外部来源其中10读原文，commit 79f3cc7）。

**核心结论（已核验，conf 来自 arena 报告）**：

1. **分解单位是依赖图上的 k 跳链，k 跳要 k 步，不多不少。** BAPO 模型（2602.02909, ICML '26）证明了 token 下界：全局聚合类 Ω(n) 步不可压缩；指针追踪类 Θ(链长)。→ "洞察要多少步"取决于它是链式还是全局约束式，不取决于"跳得多远"。
2. **"执行可分解"已证，"发现可分解"没有正面证据且有反面证据。** 蒸馏线（2210.11416：770M T5 打赢 few-shot 540B PaLM）证明给定步骤后小模型能走；AInstein（2510.05432）显示严格复现已发表解法 <19%，失败模式 = 跨域类比迁移。
3. **瓶颈不在"切不切得开"，在"切开后谁来验每一步"。** SCORE（2407.13692：refiner 可迁移、verifier 不可迁移）+ PlanningBench（2605.20873：Avg-pass 90% 但 All-pass 58%）+ LLM Monkeys（2407.21787：覆盖率 >95% 但 selector plateau）三条独立证据链收敛到同一处。
4. **ctx 不是主因。** 串行 CoT 自己造中间状态，窗口大小不影响可达性；并行 attend 路线才受窗口限制。且没有任何文献给出 W→D 的定量关系（负结果 N2）。
5. **dense net 搜索优势有条件：** 需要回溯的图搜索上是的（ProsQA +19.5pp / 1/3 token），串行算术上不是（GSM8K −8.8pp）。"跳不出局部最优"的主因是选择器而非搜索器。

**对成璐三个担忧的直接回应**（arena §10）：
- "超出 ctx？" → 不是主要原因，真正卡住的是"用不用得上自己刚写下的东西"
- "有下界？" → 有，两层：结构层（问题结构决定，硬的）+ 模型层（模型能力决定，软的）
- "dense 更高效？" → 条件性成立，且瓶颈在选择器

## Idea B 的结构化（五层等价性 → T-PR-08）✅ 已完成

T-PR-08 产出：`research/moe-agent-equivalence-survey.md`（284行，commit 129420b，已 merge main @ e843b68）。

**核心结论（已核验）**：

1. **"等价"在容量层面是废话，在结构层面是真的，在训练层面是假的。** 万能逼近定理使两边在函数类上完全一样（都是万能逼近器），所以问"能不能模拟"必须先排除容量层面。真正的结构同构：2505.24205 Thm 5.2——深度-2L、每层 E 专家的 MoE 可逼近 E^L 个分片的复合稀疏函数，**E^L 正好等于 MoA 的 L 层 × M agent 能枚举的组合数**。而且不需要正交性前提。

2. **正交性假设实测是假的，而且"两头都不沾"。** Mixtral 专家间余弦相似度 0.2–0.4（与原始 FFN 反而 ~0.6），DeepSeekMoE 从零训练接近 0；最后一层突然跳到 >0.8。更狠的是 MoE-Lens（ICLR 2025 workshop）：单个 top-1 专家就能以余弦 0.95 逼近 6 专家集成，perplexity 只涨 ~5%。→ "大部分正交的小 agent"在工程现实里没有对应物。

3. **纠缠有两条可量化的形式化路径，都给出了"不可模拟"定理：**
   - 通信复杂度（2510.13903）：parity 类任务上多数投票式 agent 方案需要 2^Ω(N^c) 个 agent（超多项式），可加结构只要 O(log N) 深度——**某些任务用小 agent 群模拟大模型是指数亏的**
   - 量子类比：**不成立，且差距可精确写出**——MoE 路由是概率单纯形上的经典凸混合（密度矩阵对角），量子叠加的优势恰好是那个干涉项 2|A₁||A₂|cos(φ₁−φ₂)（2512.22296 把这一项单独隔离出来当优势来源）

4. **五层判定表**：L0 部分证明（结构性成立但严格形式不成立——MoA 原版聚合步是自由 LLM，不属于加权和函数类）；L1 弱经验支持；L2 **已反证**（2510.23671："misleading to think of MoEs as an aggregation of dense models"）；L3 仅 MoE 侧有泛化界（2604.09175 Thm 3.4），agent 侧为零；L4 完全空白。

5. **与 T-PR-07 的汇合点**：arena 建议用 T-PR-07 已建立的"覆盖率 vs 选择器"实验框架去测 2603.20324 的选择瓶颈阈值 s*——**长程洞察的瓶颈与 agent ensemble 的瓶颈是同一个东西：验证/选择。**

## 待验证（T-PR-09）

**P1: "最优性依赖任务结构" ≡ "NN 是否是目标的最简描述"？**
- MDL 视角：如果 ICL demo selection ≈ MDL 优化，那任务结构决定最优性自动成立。有没有人显式写过？
- Kolmogorov 视角：训练后权重是否编码了 K* 级压缩？ICL 侧有没有"context 中的 demo 构成 x 的最简条件描述"的结果？

**P2: "额外参数 = 万能拟合器"还是"压缩结构"？**
- 可测判据：N（参数量）vs K(data)（用 LZ76 近似）。N >> K(data) → memorization；N ≈ K(data) → compression。
- Scaling law 在什么 N/D 比值下从 memorization 切换到 compression？有相变证据吗？
- MoE 稀疏激活是否天然倾向 compression regime？

**P3: Bayesian/信息论范式是 ICL 高效性的结构性原因？**
- (a) ICL as Bayes：prior = parametric knowledge，context = likelihood evidence，输出 = posterior。在哪里精确成立、在哪里断裂？
- (b) 信息论界：I(y; context) 能否控制泛化误差？有人给过界吗？
- (c) PAC-Bayes 风格 ICL 泛化界存在吗？
- (d) 如果 ICL ≈ Bayes 更新，最优 demo selection 应该最大化 posterior 信息增益——这个准则有人试过吗？

## 与 compression-unified-view 的关系

compression-unified-view 建立了"训练=压缩，推理=选择性解压，CoT=外化解压"的统一框架。本 note 的三个 idea 是这个框架的三个推论方向：

- Idea A 问的是：解压过程（推理链）有没有不可压缩的原子单元？→ 对应 Kolmogorov 复杂度的操作化
- Idea B 问的是：压缩器（MoE 权重）能不能被分解为独立子压缩器的组合？→ 对应 MDL 中"描述长度可加性"的条件
- Idea C（T-PR-09）问的是：ICL 的高效性是否由 Bayesian/信息论结构保证？→ 对应"prior 质量决定 posterior 更新效率"

如果三者都得到肯定答案，那 compression-unified-view 需要加修正：**压缩/解压不是完全可分的，存在不可约简的纠缠项（Idea B L2 已反证支持此修正），且 ICL 的效率上界由 prior-posterior 距离决定（Idea C 待验证）**。

## 待办

- [x] T-PR-07 arena 产出 → `research/long-insight-decomposability-survey.md`（✅ commit 79f3cc7，已 merge main @ 3ac50cf）
- [x] T-PR-08 arena 产出 → `research/moe-agent-equivalence-survey.md`（✅ commit 129420b，已 merge main @ e843b68）
- [x] T-PR-09 arena 产出 → `research/icl-information-theory-framework.md`（✅ commit 239b9b8，merge main @ 822e0bd；判决：Bayesian/信息论支撑到"部分证明"级 conf 0.7——1/√(nT) 统计界 + 条件化 Bayes 最优性定理存在，但都没写成最简描述；互信息控制 ICL 泛化的直接结果穷尽检索未找到）
- [x] T-PR-10 arena 产出 → `research/model-capability-step-count-mechanisms.md`（✅ commit d94a73e；三机制排序 M3 校准 > M1 激活 > M2 联系，只有 M3 同时可计算+可干预+能翻译成步数）
- [x] T-PR-11 arena 产出 → `research/search-verify-contribution-function.md`（✅ commit f05753a+3a9bf1c；滚雪球核验完成：乘积型搜×校验贡献函数不存在——伪合成 2 + 单侧 4，且搜集质量连可计算定义都没有；§4.4 可直接引用的 pfb 定位段落已产出）
- [ ] 如果三篇 survey 结论指向"存在不可约简纠缠 + ICL 效率有信息论上界"，写进 compression-unified-view 作为修正条款