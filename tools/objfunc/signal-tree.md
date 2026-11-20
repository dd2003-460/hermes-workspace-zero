# 信号树（D 反馈 → 领域/情况/方法）

> 派生物：数据源 `signal-tree-tiered.json`，本文件由 gen-signal-tree-md.py 自动生成。
> 标记：✓已落地 ◐部分 ◑待固化 ⬜缺口 · tier: G全局 D领域 P项目
> 用法：VSCode 大纲视图折叠导航，或 <details> 折叠。只展开你关心的线路。

## D1 工作区结构与索引  `27信号 · 2缺口`

<details>
<summary>D1 工作区结构与索引（点开看情况）</summary>

### ✓ S1.1 项目分类与命名  `P·已落地·6信号`
方法：按agents分类原则, 命名=最小项目名-父-二级父递增, 学术小项目归对应领域下; 指令跟随=按项目分类规范+loop流程走
落点：`sop/project-tidy + AGENTS.md 分类原则`

### ◑ S1.2 工作区路径与持久  `D·待固化·11信号`
方法：持久用workspace(非zero), 时间到分秒, 查文件最新mtime
落点：`sop/project-tidy (workspace路径规范)`

### ✓ S1.3 索引与持久化规则  `G·已落地·6信号`
方法：分类规则+索引规则+任务状态写入/更新/持久化, 每层有索引, 外层memory只索引; 每个cron/小项目有自己的状态和记忆
落点：`AGENTS.md 项目分类原则节`

### ✓ S1.4 简洁与复用  `G·已落地·4信号`
方法：软连接冗长违背简洁最小原则; 能引用/复制就不生成; prompt本身就是global内容不必临时文件; 大导出文件含主题子节点对话
落点：`rules/execution-discipline (压缩律)`

### ⬜ S1.5 归档与清理  `D·缺口·0信号`
缺口：归档标准(什么进archive/什么删)无信号, 待D定义
落点：`sop/project-tidy (归档标准)`

### ⬜ S1.6 备份与回滚  `D·缺口·0信号`
缺口：备份策略无信号(只见过事故后手动备份), 待D定义
落点：`sop/project-tidy (备份策略)`

</details>

## D2 循环与流程  `12信号 · 2缺口`

<details>
<summary>D2 循环与流程（点开看情况）</summary>

### ✓ S2.1 1-loop分解流程  `D·已落地·4信号`
方法：先分解规划再获取信息; 标准分解流程自动分解; 无限制默认全面搜索; ralph loop简单=hook+阶段指针
落点：`loop/prompt-first/ (1-loop)`

### ✓ S2.2 2-loop与代码规范  `D·已落地·2信号`
方法：用subagent读2loop原则执行; 2loop规范=代码规范
落点：`loop/archived-20261016/2-loop/`

### ✓ S2.3 副脑派发与互提醒  `D·已落地·4信号`
方法：派发副脑互相提醒质询; 两agent一session持久对话共同规划1loop找盲点
落点：`sop/arena-loop-pipeline + ralph-team-setup`

### ✓ S2.4 全局prompt与goal内容  `D·已落地·2信号`
方法：ralph-loop.global.md当每次启动prompt或改系统提示; 拿ralphglobal作goal内容; goal不必另一agent接受, 做项目时留完整过程文档
落点：`ralph-loop.global.md`

### ⬜ S2.5 循环终止与收口  `G·缺口·0信号`
缺口：什么时候算做完(收口判据)无信号, 待D定义
落点：`rules/ (收口判据, 新)`

### ⬜ S2.6 多goal并行调度  `G·缺口·0信号`
缺口：多goal优先级仲裁无信号(只见过串行), 待D定义
落点：`rules/ (多goal仲裁, 新)`

</details>

## D3 钩子与触发  `15信号 · 1缺口`

<details>
<summary>D3 钩子与触发（点开看情况）</summary>

### ✓ S3.1 stop hook实现  `D·已落地·8信号`
方法：模仿cc stop用endhook; 收停止信号重新注入prompt; 不用重启(禁言即可)
落点：`~/.hermes/hooks/stop_hook.py`

### ✓ S3.2 触发与原则注入  `D·已落地·7信号`
方法：cron投递(非轮询)+桥接hook注入+固定session不新开; process.wait返回可做触发点; 行动/计划时注入对应原则; agents直接录入系统提示
落点：`~/.hermes/agent-hooks/routing.json + hooks`

### ⬜ S3.3 触发失败恢复  `D·缺口·0信号`
缺口：hook没触发时怎么发现(自检机制)无信号, 待D定义
落点：`hooks 自检机制 (新)`

</details>

## D4 上下文与压缩  `4信号 · 1缺口`

<details>
<summary>D4 上下文与压缩（点开看情况）</summary>

### ◐ S4.1 截断与压缩  `P·部分·2信号`
方法：自动压缩机制, 上下文压缩要自由
落点：`hermes 配置 (压缩参数)`

### ⬜ S4.2 上下文重复  `G·缺口·2信号`
方法：看自己上下文, 找重复的机理
落点：`rules/ (重复检测, 新)`

### ◐ S4.3 压缩后状态恢复  `G·部分·0信号`
缺口：压缩后第一件事做什么无信号(播报规则提过补发摘要, 但恢复协议未定义), 待D定义
落点：`rules/chat.md (压缩恢复协议)`

</details>

## D5 工具与浏览器  `6信号 · 1缺口`

<details>
<summary>D5 工具与浏览器（点开看情况）</summary>

### ✓ S5.1 ego lite默认  `D·已落地·5信号`
方法：只用ego lite(免登录), 删其他浏览器工具或设默认; 看自己工作区不必走ekko
落点：`skill ego-browser + arena规则(浏览器分工表)`

### ⬜ S5.2 ccconnect稳定性  `P·缺口·1信号`
方法：dinotty可能也需要, session找不到
落点：`ccconnect 配置`

### ✓ S5.3 工具选型标准  `G·已落地·0信号`
缺口：选工具的标准(免费/成熟/登录态)散落在规则里未成情况, 待D定义
落点：`AGENTS.md 工具优先红线`

</details>

## D6 模型与推理  `7信号 · 3缺口`

<details>
<summary>D6 模型与推理（点开看情况）</summary>

### ✓ S6.1 provider与模型  `P·已落地·2信号`
方法：不改模型, provider=本地omlx(非lmstudio)
落点：`MEMORY.md (8787/omlx)`

### ⬜ S6.2 推理激活  `P·缺口·1信号`
方法：不给答案激活完整推理, 把激活作为目标
落点：`D1-academic-AI (推理激活实验)`

### ⬜ S6.3 小模型与微调  `P·缺口·4信号`
方法：试小模型微调; 核心推理+工具调用不需大量参数存知识; 微调不带工程知识只考获取信息+推理; 控制变量(模型大小)最大化单位成本token效率
落点：`D1-gpu + pfb (小模型方向)`

### ⬜ S6.4 模型切换与降级  `P·缺口·0信号`
缺口：什么时候换模型/降级无信号, 待D定义
落点：`rules/ (模型切换判据, 新)`

</details>

## D7 目标与持续  `11信号 · 0缺口`

<details>
<summary>D7 目标与持续（点开看情况）</summary>

### ✓ S7.1 goal粒度  `D·已落地·4信号`
方法：/goal太大让AI拆小goal评估完成; goal能持续工作; 直接用/goal命令; 更高轮次=hermes goal轮次
落点：`stage-gate + /goal`

### ◐ S7.2 稳定性  `D·部分·6信号`
方法：gateway重启崩溃; bypass权限可找setup.sh; 能用工具; 团队启动不稳; 默认全给工具且稳定
落点：`rules/safety + 故障索引`

### ✓ S7.3 自主工作  `G·已落地·1信号`
方法：总是中断没有自主工作=违背自主第一, 跳过阻塞做可执行工作
落点：`rules/autonomy.md`

### ✓ S7.4 目标发现  `G·已落地·0信号`
缺口：无明确指令时怎么找goal有USER.md规则但未成树节点, 待D定义
落点：`rules/goal-discovery.md + USER.md`

</details>

## D8 研究与idea  `8信号 · 0缺口`

<details>
<summary>D8 研究与idea（点开看情况）</summary>

### ✓ S8.1 物理研究方向  `P·已落地·3信号`
方法：扭结相互作用生成粒子/场(难); pauli不相容→拓扑缺陷→任意子交换负号; 黑洞视界2+1例子
落点：`D1-academic-AI memory/ (7猜想)`

### ✓ S8.2 研究方式  `D·已落地·5信号`
方法：task与claude区分+装数据分析skill+预测社会经济趋势; 换方向看其他论文找空白; projects/ai下持续研究; gpu调研就是gpu调研(非黑洞); gpu调研测ralph runtime找问题优化
落点：`sop/collision-research + arena-outsource`

### ✓ S8.3 碰撞调研标准  `D·已落地·0信号`
缺口：新颖性判据(撞车/缺环节)散落在T-OS-1里未成通用情况, 待D定义
落点：`sop/collision-research-sop.md`

</details>

## D9 沟通与偏好  `10信号 · 0缺口`

<details>
<summary>D9 沟通与偏好（点开看情况）</summary>

### ✓ S9.1 说人话与可读  `G·已落地·2信号`
方法：加形象解释+站我角度提前解答疑问; 说人话: 谁做的/背景/结果含义
落点：`rules/chat-tone.md`

### ◐ S9.2 审美与有趣  `G·部分·4信号`
方法：跳过没意义工作考虑有趣工作(遵循我喜好); 有趣=对齐我喜好+直观+参考我原始idea+避免通用ai风格; 物理约束广场景像≠规律驱动; 培养taste sop(信息理论/互信息/残差分析视角)
落点：`rules/ (taste SOP, 新) + 科学家标准taste锚`

### ✓ S9.3 预期回答  `G·已落地·2信号`
方法：判断问题+完整考虑变量+拆解任务+反复追问到边界; 问题太trivial关键是经典复杂问题
落点：`rules/execution-discipline (追问到底)`

### ✓ S9.4 学习方式  `G·已落地·2信号`
方法：从整体框架了解; 你教我怎么用然后我发给你
落点：`rules/chat.md`

### ✓ S9.5 汇报密度  `G·已落地·0信号`
缺口：播报频率标准在chat规则里(每实质步骤一条), 但未成树节点, 待D定义
落点：`rules/chat.md (播报纪律)`

</details>

## D10 验证与质量  `12信号 · 1缺口`

<details>
<summary>D10 验证与质量（点开看情况）</summary>

### ✓ S10.1 验证  `D·已落地·6信号`
方法：我一般问为什么(这些像ai输出); 确定在跑+清记录避免干扰; 用网页llm; 验证用skill完型; 为什么没arena测试部分
落点：`sop/verification-sop + arena核验规则`

### ✓ S10.2 边界与机械  `D·已落地·6信号`
方法：避免ai一意孤行/曲解意思; 换关键词搜+multy search; 截图team名; arena仓库可连接让它只针对子模块调研; 能跑要说清能跑边界; 日志跨度大改逐节点
落点：`sop/arena-loop-pipeline (门禁)`

### ⬜ S10.3 核验深度  `G·缺口·0信号`
缺口：核验到什么程度算够(信汇报/信git/独立复算)无统一信号, 待D定义
落点：`rules/ (核验深度标准, 新)`

</details>
