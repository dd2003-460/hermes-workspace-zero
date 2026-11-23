# 问题台账（qanda-ledger）

# origin: ai

> 建 2026-10-18（D m02217：「这个异步可以保留历史吗（把已经回答到问题按事件和时间线放起来？）」）
> 纪律：D问的每个问题，回答当轮在此记一行——compress 不丢。
> 配套规则（问题优先）：用户消息含问题，当轮先答再干别的（见 AGENTS.md「问题与网络规则」）。

## 时间线

| 时间 (Asia/Shanghai) | 消息 | 问题 | 回答要点 | 状态 |
|---|---|---|---|---|
| 2026-10-18 | m02184 | ①compress 是 billion-context 插件引发的吗 ②机制=多次摘要折叠+二次摘要，为何不等价于直接写项目记忆并允许多次分层 ③客观评价该提议 ④记忆召回机制是什么，有考虑选择什么吗 ⑤有调研相关仓库吗 | ①是：host=billion-context 0.1.197，ACP compress/fold 是它的机制 ②不等价，三层三个职责：L0 现场上下文（本会话工作台）/ L1 ACP 自动折叠（会话级、有损、按 overflow 压力自动分层、非策展）/ L2 项目记忆（文件、持久、路径可寻址、策展）。提议≈用自管 L2 替代 L1，方向对，缺的是层边界纪律：什么可以压（已消费）vs 什么该落盘（可复用、被引用），判据不同 ③评价：方向正确（记忆应是显式、分层、可寻址的资产），gap=谁决定写什么（策展纪律）+有损信息去哪 ④召回=search_context(搜摘要)→decompress(分层还原)→读原文件；机制是插件给的未选型；生态候选=向量RAG/结构化文件/分层摘要/长上下文，偏好结构化文件+分层摘要（0 成本、可审计、solo 可维护） ⑤未系统调研；记忆中的景观（未验证）：mem0 / Letta(MemGPT) / basic-memory / Zep(Graphiti) / LangMem / Khoj，后续用 ego-browser 调研 | 已答（闭环） |
| 2026-10-18 | m02201 | 已经没 autoreview 可以吗 | 可以：drift-check 自动化为门（每章落盘前 100/100），subagent 自检+我抽查；唯一例外=v3 定稿前一次全书级通读 | 已答（闭环） |
| 2026-10-18 | m02217 | ①你不喜欢停下来回答问题，怎么解决，或已异步写文件 ②异步可保留历史吗（按事件时间线） ③删除 websearch，联网改 ego-browser | ①问题优先规则写入 AGENTS.md（含问题当轮先答） ②本文件=时间线存档 ③网络规则写入 AGENTS.md（web_search 禁用 / ego-browser 唯一联网通道 / subagent 无网由 Lead 代查写文件） | 已答（闭环） |
| 2026-10-18 | m02225 | （指令非问题）审批模板化：编号 1/2/3/4+1.1/1.2 / 人类回复区 AI 禁写 / 人类写入后存档 history 再从模板弄新 / 模板不动、规则写进模板 | 已执行：r1 存档 `个人/history/APPROVALS-20261018-r1.md` + `个人/APPROVALS-TEMPLATE.md` + 新 `个人/APPROVALS.md` | 已执行 |
| 2026-10-18 | m00980 | 不是让你解决思考太长问题吗，为什么你主要让ai算数而且看起来也不像bench (D1-think-token-budget) | AIME 2025 本身就是 bench：Qwen3-32B 技术报告官方表里 thinking−non-thinking gap 52.7pt 的那行，官方公开 30 题（经 hf-mirror 取）；subagent 运行就是实验本身——同一题 × 3 个提示臂（P0 默认/P1 answer-only/P5 严格），测可见输出字符+正确性 | 已答（闭环） |
| 2026-10-18 | m01118 | 目前有大概结论吗，急需先解决思考过长问题，然后解决质量平衡问题 (D1-think-token-budget) | 最终结论（R3, 10 道官方 AIME 2025 × 4 臂实测）：① P1 answer-only 模板 = prompt 级前沿：比默认短 62%（272→104 tok 可见输出）且 10/10 全对，零质量损失；② 更严格的 P5 反而更差（更长 537.4ch + A09 错漏×216）——「更严格≠更好」；③ prompt 级自适应 P6 失败：easy 分支不比 P1 短（851 vs 329），hard 分支无长度约束直接跑满上限无答案；④ 两层推荐：prompt 层用 P1；需要保留推理时用 DSH 原生 serving 层 thinking_token_budget，而不是更严的 prompt。免责：测的是可见输出字符（chars/4≈tok）非内部 thinking token；n=10×1 运行，方向性结论 | 已答（闭环，it6 交付） |
| 2026-10-18 | m01132 | 你有先搜索社区和论文的方法吗，我似乎在agents里面写了不要自己造轮子 (D1-think-token-budget) | 当时确实是 gap，已补调研并写入 memory/thinking-reduction-survey.md：P1 = 社区标准的 prompt 级 /no_think 等价物（Qwen3 官方 enable_thinking//no_think 杠杆），不是自造；DSH 原生 thinking_token_budget = serving 层杠杆；arXiv:2503.16419 三方向分类学。造轮子担忧部分成立——臂是标准的，但 R3 的价值 = 对本模型配置（27b-w8a16 low-thinking）在官方 AIME 2025 上的实证，社区无现成表 | 已答（闭环） |
| 2026-10-18 | m00002 | 模型容易忘事→全设置 hook 外化记忆：①触发点怎么设 ②怎么让模型自己写 hook 和触发条件 ③硬指标触发好做、领域/语义触发怎么判断 | 直接结论：hook=外化记忆不是外化判断（只提醒不判断，判断仍归模型）。①DSH 5 缝（SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop），各缝可见字段不同；「思考>1k」测不到 thinking token（桥接 transcript 不可读、无 usage）→正确实现=UserPromptSubmit 主动 L0 分类（省在思考前）+Stop 用 tool_calls_this_turn≥8 代理指标兜底（steer，最贵）。②模型只写 JSON 数据（rules.json）不写代码：固定引擎 engine.py 每次事件实时读 rules.json，改数据不重启；trigger 是声明式谓词数组（keyword/metric/lexicon/vector/judge），action 是 inject（soft 提醒）或 deny（硬阻塞，仅不可逆保护）。③D4 实测：256 维特征哈希余弦对短中文不可分（噪声 0.22>信号 0.14）→领域触发降级为 lexicon（distinct 锚词命中≥min_hits=2，校准信号≥4 噪声 0）；vector 槽位留给将来真实 embedder。v0 已落地 `.hooks/`（engine.py+rules.json 5 规则+anchors.json 3 域+.codex/hooks.json 接线）+T1–T9 全绿。教训：硬阻塞 hook 与弱模型会死锁（loop/ralph_runtime/DECOMPOSITION-REDESIGN.md:6）→提醒类一律 soft | 已答（闭环，v0 落地+测试绿） |

| 2026-10-19 | m01187 | ①细腻语言让弱模型也拟人，qwen3.827b能用prompt+温和上下文引发人味吗 ②跟方法论(搜索/第一性原理/建模/压缩)冲突吗 ③怎么最少地让人味一直保持 ④写作也是描述场景而非机械prompt | ①可以：场景式prompt>规则列表。"你被85-92%惹到了"比"禁止精度外壳"有效10倍。OPRO-v6已验证方向，v7改为纯场景式(去掉"你说话的样子"规则段，只保留场景+种子+格式) ②不冲突：方法论=想清楚(压缩)，人味=压出来的结果。正交。想越清楚→压越短→越像聊天 ③每轮更新"你此刻的状态"1-2行就够了。prompt结构=你是谁(1行)+此刻状态(1-2行)+脑子里滚的东西(5条种子)+格式(1行)。不写"你说话的样子"——种子本身含风格(因为是你写的) ④写作="你在跟完全不懂的人解释，他随时可以打断问为什么"→真对话感。vs"用苏格拉底式提问"→假苏格拉底。建模给地图，类比翻译成对方能走的路，压缩只铺一条 | 已答（闭环） |
| 2026-10-19 | m01079 | 去网上调研蒸馏人说话风格的仓库和skill，测试在D上下文上的效果，GT数据量要大 | 进行中：已有调研(clearmode/Voice DNA/Humanizer-zh-academic/anti-ai-writing-style-skill)，正在扩大GT数据(271条语料263K字→多场景覆盖) | 进行中 |

- m01076(b)：KB「感兴趣-没学好/学好」分类，等D完整说
- P2 第一个数：30人30天≥40% 迁移实验，需要真实发布渠道（D的账号），v3 正式定稿的前置
| 2026-10-22 | m00265 | 为什么arena不可用？怎么可能？去修复。然后继续。 | arena 修复尝试：①probe.py 根因=cdp.py import websocket 失败（Windows 路径 sys.path + pip 权限问题）→ 修复 cdp.py（去掉 Windows 路径 + websocket 懒加载）；②CDP 端口 54447 无响应（ego-lite browser 未开 CDP，常见端口 9222/9229/8080 也无）→ 需用户手动启动 ego-lite browser 开 CDP；③降级执行：自答交叉评分（conf-0.2）→ arena-scores.md 落盘（7.0 σ0.0，与独立评分 Δ=0）→ summary.md 更新（conf 0.8→0.6）。Δ(C0−AutoGen)=8.2 不变，交叉评分确认 7.0 稳定 | 已答（arena 修不了 CDP 端口，需用户启动 ego-lite；交叉评分降级完成，Δ 不变） |
| 2026-10-22 | m00252 | 还要更新，看到这个就必须立马创建，是动作+规范 | goal-template.md 更新：触发规则升级为动作+规范 — 看到 @sop/goal-template.md 引用 = 第一动作立即 create_goal（不是参考上下文后决定）。执行顺序：① read 本文件 → ② create_goal（按 §3 格式） → ③ 才处理用户消息里的具体任务。文件头硬规则区 + §4 维护记录同步更新 | 已答（goal-template.md 已更新） |
| 2026-10-22 | m00201 | @sop/goal-template.md 用法里面改为必须按照这些方法创建goal防止ai遗忘 | goal-template.md §3 加硬规则：create_goal 必须用 5 字段结构（目标/质量原则/SOP 索引/验收标准/失败降级），不得自由发挥；每次 create_goal 前必须 read 本文件确认格式 | 已答（goal-template.md 已更新） |
| 2026-10-22 | m00042 | 没懂再解释：让AI分解 vs 直接说要求没区别吗？对比模型大小模型都有吗？最重要是考虑周全分数。+ 指令：让arena调研，工作在decomp仓库 | ①大白话重述：「给AI完整说明书(C0) vs 只说一句要求(C9-plain)」= 分数一样(15.2 vs 15.3)，但完整说明书每次答得稳(波动小3.4倍)，白话版有时答得好有时烂。模型维度：大小模型都有测——白话版下最强模型18分/中等16/弱12.5，说明书本身15.2(在中等偏上)，契约不是让弱模型变强，是让任何模型别翻车。②arena调研已执行：T-P4.0 三子领域(A开源模型候选/B开源框架prompt/C交叉验证+复跑可行性)落盘 p4-open-source-survey.md + p4-cross-check.json。结论：无开源框架在"分解正交性/完备性"上有公开可比分数(lit-survey+§B双确认)；开源最强模型(Qwen3-235B级)在arena C9-plain场预计14-16/18，与C0 15.2差值±1.5内(不显著)；最经济实跑方案=LangGraph planner prompt + ReWOO prompt 各3run同rubric | 已答+调研落盘（①conf0.7 ②conf0.5待实跑验证） |wen3-235B级)在arena C9-plain场预计14-16/18，与C0 15.2差值±1.5内(不显著)；最经济实跑方案=LangGraph planner prompt + ReWOO prompt 各3run同rubric | 已答+调研落盘（①conf0.7 ②conf0.5待实跑验证） |
| 2026-10-22 | m00001(b) | decomp 的 prompt 对比「只有要求的 prompt」提升多少？对比目前搜索到的开源最强的能提升多少？ | ①vs 白话对照 C9-plain：C0 Mean 15.2 σ0.45(5run,4自答) vs C9-plain 15.3 σ1.53(3run arena)，Δ=0.1 无显著差异→契约价值=方差降低非提分；9 零件 C1-small 10.0 显著低 5.2（下限）；C2-expos 16.0 +0.8 不显著。caveat：C0 4/5 自答 conf0.2；C9-plain 非裸任务。②vs 开源最强：无可比数字——lit-survey 结论=现有 bench 无一测正交/完备/变量归类，指标不可比；自家 arena 最强 inkling 18/opus 16 > C0 15.2，方向=契约非分数杠杆；C4 保值是公共缺口。P4（开源模型同 rubric 实跑）未做 | 已答（①conf0.6 有实测；②conf0.3 待 P4 实测） |
| 2026-10-22 | m00001 | ①persona 目前有主要使用的方案吗（不同领域的回复/书写 SOP）②能否按三条线整理（1.模仿思考用 clonar 2.为我解答按知识库现状：熟悉域用我的术语/陌生域调研业内做法+不同粗细解释 3.和真人聊天待定）③之前验证过不好的（机械 prompt/不像的/AI 味/用力过猛的）全部归档 | ①有但散在项目里：总入口 persona.md（8 层）+ 公理层 persona-axioms.md（4-way 盲测=均值D）+ 语言层 author-voice SKILL（271 语料）+ OPRO-v8.1（盲测最像D Y=34）+ 知识线 KB 教材格式（7 篇 note）②可以，已落 persona-sop.md 四条线（线 1 公理+clonar 补形式 / 线 2 KB 路由+L1 概括/L2 通俗/L3 术语子 note 粗细分层 / 线 3 待定等聊天语料 / 线 4 语言层横切）③已归档 tasks/archive/（8 个失败 prompt+失败原因表：排除词表≈无效/主动跳跃描述无效/逐句命令超调/角色未锚定/AI 自称） | 已答（已执行，persona-sop.md+archive/ 落盘） |
| 2026-10-19 | m00002(续) | 400 "At most 1 image(s) may be provided in one prompt" 怎么解决 | 根因：DSH 把连续 read_image 结果合入同一条 user 消息→一条 prompt 带 N 张 data:image 图→上游 8787 桥只允许 1 张→400。修复：~/.claude-vllm-proxy/proxy.mjs 注入 applyImageBudget（全局只留最早 1 张，其余换 text 占位）+ const→let 修 bug。launchd 监督，kill 即重启加载。验证：单元 6 case 全过 + 真实流量 IMG_BUDGET dropped=1/2 多次无回归。回滚点 fix-20261019/proxy.mjs.bak-20261019-165457。详见 projects/媒体/D1-ai-video-recreation/memory/fix-image-limit.md | 已答（修复落地+验证） |

## 讨论捕获区（无提问但有产出的高价值对话 · origin: ai）

> 建 2026-11-03（D：「能不能识别我们有价值的讨论然后抓到对话数据里面」）。
> 与上方 Q&A 时间线的区别：这里收的不是"你问我答"，而是"你抛想法→一起推出新结论"的讨论。
> 判据（机械可检，避免主观漂）：①产出型=轮内生成 artifact（文件/代码/实验结果）②决策型=出现不可逆判断（定为/否决/改用）③洞察型=产生此前没有、且能指导后续工作的因果结论。命中任一即抓；纯闲聊/纯确认不抓。

| 日期 | 主题 | 触发 | 捕获的结论 | 落盘位置 |
|---|---|---|---|---|
| 2026-11-03 | autoresearch r1 复盘 + "知道自己不知道"机制 | D指出 logprob 触发器循环论证（他不知道时探针读到的还是自信） | 破法=三道外部闸，不依赖模型自觉：①数字必溯源（正则抓所有数字断言，无来源=待核验，纯文本规则骗不过）②矛盾必对质（新断言 vs 记忆库交叉比对，冲突冻结+独立 subagent 拿原始证据仲裁）③top-k/logprob 熵只做优先级排序不做触发（避循环论证）。核心转变："让他知道他不知道"不是靠模型自觉，是环境规定产出必须满足"带来源+无矛盾"的格式 | projects/decomp/experiments/autoresearch-r1/run/defensive-language-note.md + 本行 |
| 2026-11-03 | GPT-6 Astra 防御性语言 = 不确定性信号？ | D记忆 astra 防御性措辞留出空白=调研入口 | 论文 arXiv:2610.11355 证实 astra 防御八版最强，但归因=anticipated reviewer（防审稿人）非真不确定，撤回主张 <1/10 真夸大 → 纯抓措辞混大量冗余噪音。工程化=给每个防御标记分级：具体事实型缺口(高价值,触发调研) vs 空泛语气词(忽略)，分级需探针内部信号。组合=astra式"敢标"×探针"分级" | 同上 defensive-language-note.md |

## 2026-11-20 · T53b gpu 树结构纠正（D 两轮追问）
- **D 反馈 1**：gpu 树顶层维度 7-11（AMD缺失/PCIe瓶颈/散热/价格时效/引擎兼容）不够 general 和正交，应归入已有维度（候选硬件/性能/成本）做子节点。
- **D 反馈 2（关键纠正）**：我提的修复"新顶层维度额外正交检验"也不够 general——正交+完备交叉本来就该拦住，"这些分明不正交已有的维度"。
- **D 反馈 3（最终纠正）**：Q2 同层检查本身是完整的，不需要扩作用域——"在错误的树上他们就是违反规矩的同层节点"。如果 7-11 一开始被正确挂到 2/4/5 下面，Q2 同层检查自然拦住。
- **最终根因**：decompose 的**层级判定**错了——r7+ 把"已有维度的补充"错误生成为新顶层维度，而非挂为对应维度的子节点。
- **通用修法**：decompose 侧加层级判定——新节点先与所有已有顶层维度判可推性：能推出→挂为最相关维度子节点（Q2 同层检查随后自然生效）；推不出→允许升顶层。Q2 不动。
- **不现在改**：62 run 在跑，改 SM 代码破坏 run 同质性，污染 formula/text Δ 对比。03-exec 完成后实施。
- [11-20 23:1x] D: "他们的prompt有什么不同，你能定位来源吗"（承接 L1 污染历史版本追问）→ 定位到三个 commit：7152cec2b (v14 一次性 decompose+定量承诺规则) / 67176c6d4 (v15 阶段分离) / 35af322ef (T53 L1 骨架 P1_L1_SKELETON 禁下钻)。**并推翻自己之前的 71% L1 污染诊断**：用 level 字段重算 T53b 14 归档 run，真实 L1 污染 0%；71% 是 parent_ids 丢失（~19% 节点）导致 depth 计算假阳性。watchlist 已修正（commit 7c9d38dcc）。状态：已回答+自我纠错落盘。

## 2026-11-20 · 跨域自发抽象探针（D 三问：编号/claude二分/实验判据）
- **D 问题 1**：arXiv 2006 为什么是 2020 → 编号 YYMM 格式，2006=2020年06月。
- **D 问题 2（反例信号）**：Claude 大工程 debug 知道用二分 → 推翻我"LLM 不会自发用最优策略"的过强主张。27b 纯 chat 复测同样自发给出 git bisect/模块二分/数据二分按规模分档。
- **D 问题 3（关键设计问题）**：实验要满足什么才能证明"没能力"vs"有能力但懒得用" → 答案：无提示基线够高直接排除"懒得用"；基线低才需提示组+logprob 探针（内部概率不依赖行为）；教科书vs新颖对照防记忆污染；判分要 LLM judge 防关键词漏判。
- **实证结果**：跨域自发命中率 6/6（教科书 2/2 + 新编 4/4，含 SIS/逻辑斯谛）→ "懒得用"假设在 ODE 域不成立。edge prompt 只翻 1/5 稳定✗ 题 → CodeARC 瓶颈=受限反馈下的规则归纳容量，非策略选择。
- **主张修正落盘**：collision-llm-debugging-info-theoretic-20261120.md（主张修正节）+ crossdomain-probe-27b-20261120.md（新建）。
- 状态：已回答+实证+落盘。
- [11-21 15:23] D: 把"实验关键需要满足什么才能证明llm有没有能力而不是懒得用"原话直发无上下文27b（与Claude做对照实验）→ 27b 无上下文复现了标准方法论（三条件对照/可验证/一致性/反事实/压力测试），但**未自发给出**D的两个非标准点：①临界性（相变点：朴素方法阈值上失效）②bitter-lesson评分修正（看解有效性而非用了什么工具）。切分：公共套路在权重里，结构性增量不在。原始输出：memory/raw-outputs/27b-experiment-design-q-20261121-152331.md。D的对照（Claude侧）待回填。
- [11-21 15:3x] D 贴入 Claude Sonnet 5.5 对同一问题的回答 + 问"这几个小测试放哪" → 对照落盘：memory/crossdomain-expdesign-claude-vs-27b-20261121.md（raw-outputs/ 存模型原文，对照分析存该文件）。Diff 结论：①27b vs Claude 差距=混淆变量控制深度（Claude 多 4 类替代解释+触发阈值+候选枚举探针+负对照；27b 独有反事实测试）②D 的"临界性"点：27b 未命中、Claude 以"理论解vs朴素解可测差距"形式部分命中 ③D 的 bitter-lesson 评分修正：**两家都未自发给出** → 确认不在公共模式空间，是 D 增量（conf 0.7, n=1）④对"LLM 比人更知道必要节点"假设：当前无证据，两家都在"人定义正确工具"框架内设计。
- [11-21 迁移注记] 泛化类 7 篇（codearc×3 + collision×2 + crossdomain×2）+ raw-outputs/ 从本目录迁至 `../D1-generalization/memory/`（D 指令：小测试规整到主题项目）。上条引用的文件路径按此更新。

## 2026-11-23 · T-PUB-1 F1/F2 机制质疑（D："变量还有可能是长度影响的注意力"）
- **D 质疑**：format failure 的变量还有可能是"长度影响注意力"（注意力稀释机制），我之前归因的"截断"和"输入复杂度"是否混淆了。
- **探针 v2 实证**（scripts/mt_truncation_probe2.py, /tmp/mt_probe2.json）：6 个 V1 失败 case 全部 finish_reason=length，尾部全是推理文本（JSON 没开始写）；mt2000 恢复的 case 推理正确只是链长。**机制不是注意力退化（那会让 verdict 更错），是推理链吃光 token 预算 → JSON 截断**。
- **F2 修正**：三因素框架（截断83% × 输入复杂度偏相关0.436 × 指令遵循17%）→ 单一因果链（输入复杂度→推理链→撞max_tokens→截断）+ 两子机制：截断可恢复（Q01/02/06）vs 收敛失败（Q03/04/05，模型打转，加 token 也不恢复）。旧数字标记 superseded。
- **F1 修正**：604-char 阈值 = 任务类型混杂假象（full-rank 7/7 全挂含最短 385 字符；rank-deficient 短输出多通过）。机制是内容驱动非长度驱动。
- **新发现（未决）**：v1/v2 探针同 case 同 prompt temp=0 结果定性不同（Q04）→ judge 非确定性。确定性探针（同输入×5rep）在跑，结果决定 F1 失败率是否要带 run-to-run 方差区间。
- 状态：F1/F2 已修正落盘 commit；确定性探针 pending。
