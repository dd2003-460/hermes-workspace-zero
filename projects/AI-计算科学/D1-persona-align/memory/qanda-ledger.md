# 问题台账（qanda-ledger）

# origin: ai

> 建 2026-10-18（成璐 m02217：「这个异步可以保留历史吗（把已经回答到问题按事件和时间线放起来？）」）
> 纪律：成璐问的每个问题，回答当轮在此记一行——compress 不丢。
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
| 2026-10-19 | m01079 | 去网上调研蒸馏人说话风格的仓库和skill，测试在成璐上下文上的效果，GT数据量要大 | 进行中：已有调研(clearmode/Voice DNA/Humanizer-zh-academic/anti-ai-writing-style-skill)，正在扩大GT数据(271条语料263K字→多场景覆盖) | 进行中 |

- m01076(b)：KB「感兴趣-没学好/学好」分类，等成璐完整说
- P2 第一个数：30人30天≥40% 迁移实验，需要真实发布渠道（成璐的账号），v3 正式定稿的前置
| 2026-10-22 | m00001 | ①persona 目前有主要使用的方案吗（不同领域的回复/书写 SOP）②能否按三条线整理（1.模仿思考用 clonar 2.为我解答按知识库现状：熟悉域用我的术语/陌生域调研业内做法+不同粗细解释 3.和真人聊天待定）③之前验证过不好的（机械 prompt/不像的/AI 味/用力过猛的）全部归档 | ①有但散在项目里：总入口 persona.md（8 层）+ 公理层 persona-axioms.md（4-way 盲测=均值成璐）+ 语言层 author-voice SKILL（271 语料）+ OPRO-v8.1（盲测最像成璐 Y=34）+ 知识线 KB 教材格式（7 篇 note）②可以，已落 persona-sop.md 四条线（线 1 公理+clonar 补形式 / 线 2 KB 路由+L1 概括/L2 通俗/L3 术语子 note 粗细分层 / 线 3 待定等聊天语料 / 线 4 语言层横切）③已归档 tasks/archive/（8 个失败 prompt+失败原因表：排除词表≈无效/主动跳跃描述无效/逐句命令超调/角色未锚定/AI 自称） | 已答（已执行，persona-sop.md+archive/ 落盘） |
| 2026-10-19 | m00002(续) | 400 "At most 1 image(s) may be provided in one prompt" 怎么解决 | 根因：DSH 把连续 read_image 结果合入同一条 user 消息→一条 prompt 带 N 张 data:image 图→上游 8787 桥只允许 1 张→400。修复：~/.claude-vllm-proxy/proxy.mjs 注入 applyImageBudget（全局只留最早 1 张，其余换 text 占位）+ const→let 修 bug。launchd 监督，kill 即重启加载。验证：单元 6 case 全过 + 真实流量 IMG_BUDGET dropped=1/2 多次无回归。回滚点 fix-20261019/proxy.mjs.bak-20261019-165457。详见 projects/媒体/D1-ai-video-recreation/memory/fix-image-limit.md | 已答（修复落地+验证） |
