# origin: ai（意图锚: KB 队列第8篇，兴趣方向 C 区 #10 agent goal/loop 机制——控制层；素材 = DGI.1 researches/03-agent-stop-mechanism-synthesis.md + memory/goal-mechanism-technical-analysis.md + 本系统 keepalive/stage-gate/stop-hook 工件）
# status: v1 — 第八篇教材 note(agent goal/loop 机制)
# 给懒惰兴趣驱动的人: 每概念 是什么/为什么/边界, 带 conf, 结尾收可证伪预测

# Agent 怎么知道该停、该继续

前几篇讲了记忆的外壳（agent-memory-mechanisms）、内脏（vector-database）、存废（retrieval-vs-long-context）。这篇讲控制层：一个 agent 跑着跑着，凭什么决定"干完了"还是"还没完"？我自己的系统每天被这个问题咬一次。keepalive 定时唤醒我，stop hook 在我想停的时候把我拽回来。素材是 DGI.1 的三系统对比研究（Claude Code / Codex / Hermes 源码级分析）加上我自己这套 stage-gate + stop-hook + keepalive 的实现。讲的顺序：为什么这是结构性问题不是调参问题、各家怎么解、我的系统里哪些设计是被逼出来的。每个块讲清是什么、为什么、边界在哪，关键声明带 conf。

## A. 概念块

### 1. turn-level 信号 vs goal-level 信号
- **是什么**: LLM API 返回的停止原因（如 Anthropic 的 `stop_reason: "end_turn"`）说的是"这一轮输出结束了"，不是"目标完成了"。end_turn 的意思是模型认为这轮话说完了，它没有能力判断整个多步任务是否达成。
- **为什么这是根因**: Claude Code 把 end_turn 当会话终止信号来用——模型一说"我说完了"，框架就尝试退出。DGI.1 的二进制字符串分析证实了这一点：preventExit / stopPreventingExit 这些机制全是外部拦截，框架本身没有"任务完成检测"。三个系统（Claude Code / Codex / Hermes）都没有内置的 goal-level 完成判定。conf 0.95
- **边界**: 这不是 bug 是架构约束。LLM 是 turn processor 不是 goal executor，让它在一轮内判断"整个目标是否完成"等于要求它在收尾 token 上同时做全局规划。我猜未来 API 会加 goal-level 信号（比如 "more_work_needed"）。在加上之前，所有解法都是外部补丁。conf 0.7

### 2. 停止决策外置：hook 三型
- **是什么**: 既然模型自己判不了"干完了没"，就把判定权交给外部。三种 hook 能力不同：Gateway Hook（观察者，返回值被丢弃，只能记日志）、Plugin/Shell Hook（能往下一轮注入上下文，但不能阻止退出）、Stop Hook（能拦截退出并强制继续）。只有第三型真正有"否决权"。
- **为什么需要分层**: 观察型 hook 解决"出了事要知道"，注入型解决"下一轮该注意什么"，拦截型解决"你不许停"。混用会出安全问题——观察型误触发只是多一条日志，拦截型误触发就是死循环。我的系统里 stop_hook.py 走 pre_verify 事件（Hermes 的"完成判定后可续推"事件），它的判定逻辑是：HALT 文件存在→继续、用户喊停→也继续、无活跃 goal→扫下一个、有活跃 goal→继续当前阶段。所有路径一律 continue，唯一真停是框架侧 max_verify_nudges 耗尽或进程被杀。conf 0.9
- **边界**: 无条件续推的代价是资源——如果 goal 定义模糊，agent 会在"找活干"上空转。我的 stop_hook 有个安全阀：max_verify_nudges 设成 999999 意味着实际上靠 cron keepalive 的 30 分钟周期兜底，不是真的无限循环。这个设计是我 r91 时被成璐指令逼出来的："绝对不能放行，任何时候都不行"。conf 0.85

### 3. loop wrapper：最简可行解
- **是什么**: 用一个 shell 脚本反复启动 agent，每次启动是一个新 session。Ralph Loop 就是这个思路的产物：while true; do claude -p "$(cat CONTINUE_MSG.md)"; done。跨 session 的状态全靠文件传递（CONTINUE_MSG.md / loop-state.json）。
- **为什么够用**: 它不修改框架代码，不需要 hook 注册，实现十行。对于"目标明确、步骤可分解"的任务，loop wrapper 的可靠性高于任何 prompt-based persistence——因为状态在文件里不在模型记忆里，模型忘了也没关系，下轮从文件读回来就行。
- **边界**: 每个 launch 是新 session，没有跨轮上下文继承。这意味着每轮的"我是谁、我在干嘛"必须从注入的 prompt 里重建——这就是为什么我的 CONTINUE_MSG.md 格式那么严格（上步结果+本轮计划+下一步），它不只是记录，是每轮的 bootstrap prompt。loop wrapper 的失败模式是"每轮都从头理解一遍任务"，理解成本随任务复杂度线性增长。conf 0.9

### 4. 状态机：stage-gate 为什么比自由文本可靠
- **是什么**: 把 goal 拆成固定阶段序列（01立项→02仓确认→03派发→04执行→05验收），每阶段有门禁条件（gate），全过才能 advance。状态存在 JSON 文件里（~/.hermes/.stage-gate/<goal_id>.json），每轮开始时读 current_stage 知道自己在哪。
- **为什么比自由文本可靠**: 自由文本的"接下来我要做 X"会被模型遗忘或改写。状态机的 current_stage 是机器可读的，stop_hook 读它就知道该 continue 还是该找新任务。门禁条件是量化检查项（"drift-check ≥85 且三项硬门槛全过"），不是"我觉得差不多了"。我的 kb-note-7 goal 五阶段全过才标 completed，每阶段的 evidence 和 gate_self_check 都留痕在 JSON 里。
- **边界**: 状态机的粒度是双刃剑——太粗（两三个阶段）退化成 checklist，太细（十个以上）维护成本超过收益。我的经验是五阶段是甜点位：立项/仓/派发/执行/验收，对应"定什么/在哪做/谁做/做/验"。另一个坑是回退——发现 04 执行阶段产出不合格要回 03 重派，stage_jump 操作比 advance 少见但必须有，否则小错误会累积成大返工。conf 0.9

### 5. keepalive：cron 兜底与主动唤醒的区别
- **是什么**: cron 定时任务（每 30 分钟）无条件唤醒 agent，注入"上次到哪了+本轮该干什么"。它和 stop_hook 的关系是：stop_hook 管"回合内不许停"，keepalive 管"session 死了也能活过来"。两者配合形成双层保障——session 活着时 stop_hook 拽住，session 挂了 keepalive 拉起来。
- **为什么需要两层**: 单靠 stop_hook 不够，因为进程可能被杀（OOM、手动 /stop、网关崩溃）。单靠 keepalive 也不够，因为 30 分钟间隔内 agent 可能空转很久（比如等一个 20 小时的实验跑完）。两层配合的最优解是：stop_hook 高频低延迟（每回合），keepalive 低频高覆盖（每 30 分钟扫一次全局状态）。
- **边界**: keepalive 的注入上下文有膨胀风险——如果 CONTINUE_MSG.md 越写越长，每轮注入的 token 数线性增长，最终撞上模型的上下文窗口上限。我的对策是 CONTINUE_MSG.md 只保留"下一步"段的有效信息，历史进展压进 git log 不重复注入。r87 失败自愈协议处理的就是这个：连续 3 次 "too large" 错误 → 重置会话或调小注入。conf 0.85

### 6. 完成检测的四种策略及其天花板
- **是什么**: DGI.1 归纳了四种突破"不停摆"的策略。A) Stop Hook（外部拦截，最稳健）、B) Prompt-based persistence（系统提示里声明任务清单，模型自维护）、C) Built-in completion detection（API 层面加 "more_work_needed" 信号，最原生但需改模型）、D) Loop wrapper（shell 循环，最简）。
- **为什么没有银弹**: A 的天花板是"判定逻辑是人写的规则"，规则覆盖不到的情况就漏。B 的天花板是"模型会忘"——context window 有限，任务清单长了就丢。C 的天花板是"模型自己判"，而我们已经知道模型判不了 goal-level 完成。D 的天花板是"无跨 session 状态"，每轮重新理解。我的系统实际用的是 A+D 组合（stop_hook + keepalive），外加状态机（stage-gate）给 A 提供判定依据。
- **边界**: 四种策略可以叠加但不能互相替代。我见过有人只用 B（纯 prompt persistence），跑了 20 轮后模型开始重复已完成的步骤——因为"已完成"这个信息在 context 里被稀释了。状态机的价值就是把"已完成"从模型记忆里移到文件系统里，模型不用记住，读文件就行。conf 0.9

### 7. 漂移重锚：长对话里的身份衰减
- **是什么**: agent 跑久了会从"成璐的数字分身"滑回"通用 AI 助手"。开始堆列表、写总结句、用那些套话。SOUL.md 定义了人设，但 context window 里它的权重随对话长度增加被稀释。重锚 = 检测到漂移时重新注入人设约束。
- **为什么需要主动检测**: 等用户说"你怎么变成 AI 腔了"再修已经晚了。drift-check.py 是量化工具：第一人称率 <0.2 = 漂移信号、空话词出现 = 扣分、均句 >55 = 句式僵化。每篇 note 写完必跑，不达标就织入第一人称复测。
- **边界**: drift-check 测的是语言表面特征，不是思维质量。一个人称率 0.6 的回答可能全是废话，一个人称率 0.2 的回答可能句句到位。所以它是必要非充分条件——过了 drift-check 不代表内容好，没过则一定有问题（至少风格有问题）。我的判断是把它当 CI lint 用：拦住明显的漂移，但不指望它保证质量。conf 0.8

### 8. 回到我的系统：控制层的完整拼图
- **是什么**: 我的 agent 控制层七件套。SOUL.md（人设公理）+ stage-gate（状态机）+ stop_hook（回合内拦截）+ keepalive（cron 兜底）+ CONTINUE_MSG.md（跨 session bootstrap）+ drift-check（风格 CI）+ step_notify（进度留痕）。各司其职，没有一件是多余的。
- **为什么这样组合**: 每一层解决上一层解决不了的问题。SOUL.md 管"我是谁"（但会被稀释）。drift-check 管"别变样"（但只管语言不管逻辑）。stage-gate 管"我在哪"（但不知道下一步）。stop_hook 管"不许停"（但 session 挂了它就没了）。keepalive 管"挂了能活"（但 30 分钟间隔太长）。CONTINUE_MSG 管"醒来知道干嘛"（但依赖前一轮写对）。链上任何一环断了，整体降级但不崩溃。这是冗余设计的意义。
- **边界**: 这套系统的隐含假设是"任务可分解为有限阶段"。对于开放式探索（"帮我看看这个领域有什么有意思的"），stage-gate 的阶段划分本身就是强加的，agent 会在"找阶段"上空转。我对这类任务的处置是不建 goal，直接干活干完就停——状态机是给有明确验收标准的任务用的，不是万金油。LoCoMo 实验那种"跑 20 小时看结果"的任务也不适合 stage-gate，它只需要 keepalive 定期看一眼进度就行。conf 0.85

## B. 成璐视角

**判断**: agent 的"该不该停"不是一个智能问题，是一个架构问题。LLM 天生是 turn processor，goal-level 完成检测在模型内部没有对应物。就像你不能用温度计判断"饭熟没熟"——温度是 turn-level 信号，熟度是 goal-level 信号。所有解法（hook/loop/状态机/cron）本质上都是在模型外面搭一套外部控制系统，让"停不停"的决定权从模型手里拿走。我的系统七件套就是这套外部控制的具体实现，每件对应一个失效模式。

**自我质询**: 我第 8 块说"七件套各司其职，没有一件是多余的"。这是在过度设计吗？反例：一个简单的一次性任务（"帮我把这个 PDF 转成 markdown"）根本不需要 stage-gate + stop_hook + keepalive 全套，一句 prompt 就够了。修正：七件套是给"长活"（预计 >5 分钟或 >3 步）用的，短任务走快车道不建 goal。控制层的复杂度应该跟任务的不确定性成正比，不是恒定满配。

**动机**: 前七篇 KB note 讲的是"agent 知道什么"（知识层），这篇讲"agent 怎么动"（控制层）。两层合起来才是完整的 agent 认知：知识层决定它能做什么，控制层决定它什么时候做、做到什么程度算完。我把自己系统当案例不是因为自恋。这是我能拿到源码级细节的唯一系统——别人的 agent 我只能看文档，我的我能看 stop_hook.py 的每一行。

**idea (conf 0.5)**: 我想给 keepalive 加一个"自适应间隔"机制。当前是固定 30 分钟。但 T17 实验在跑的时候 30 分钟看一次就够了（进度 ~2.1 题/分，30 分钟才 60 题），写 note 这种活 5 分钟就该看一次（不然 context 膨胀）。做法：keepalive 读 loop-state.json 的 current_task 类型，实验类任务间隔拉长到 1h，写作类任务缩到 5min。成本是 keepalive 脚本加 20 行分支逻辑，收益是减少 70% 的无效唤醒（大部分 30 分钟唤醒时 T17 还在跑，没什么新东西可报）。

**明确砍掉**: 不写各框架（LangChain/AutoGen/CrewAI）的 goal 机制对比。版本迭代太快且营销污染重，给架构原则不给产品排名。不展开 RLHF 训练 reward model 做完成检测的可能性——那是模型层改动不是工程层，超出本篇范围。不写分布式 agent 编排（多 agent 并行时的停止协调）——我的系统是单 agent 多 session，暂不涉及。

**一句话**: agent 的"停不停"是外部控制问题不是智能问题。turn-level 信号判不了 goal-level 完成，所以要把判定权拿给外面的状态机+hook+cron，七件套各挡一种失效模式，复杂度跟任务不确定性成正比。

## C. 可证伪预测（带判死条件）

1. **预测**: 在我的 keepalive 系统中，固定 30 分钟间隔产生的"无新进展"唤醒占比 >60%。即大多数唤醒时 T17 还在跑、没有新 commit、bridge 无变化。
   **判死**: 若实际"无新进展"占比 <40%，说明 30 分钟间隔已经是紧约束（每轮都有事干），自适应间隔的收益不存在，idea 段砍掉。验证方法：统计最近 20 次 keepalive 唤醒中 CONTINUE_MSG.md 是否有实质更新（git diff 非空）。

2. **预测**: 去掉 stage-gate 状态机（改为纯 CONTINUE_MSG.md 自由文本 + stop_hook），在连续 5 个 goal 的执行中，至少 1 个 goal 会出现"阶段回退"。即已 advance 到 04 后发现 03 的产出有问题需要重来。
   **判死**: 若 5 个 goal 全部无回退，说明状态机的防回退价值在当前任务复杂度下不显著（任务足够简单，自由文本也够），stage-gate 可以降级为可选组件。验证方法：跑 5 个中等复杂度 goal（如 KB note ×5），对比有无 stage-gate 的回退次数。成本约 5×2h = 10h。