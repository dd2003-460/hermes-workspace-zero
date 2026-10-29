# arena-outsource — 用 LMArena agent mode 外包调研/分解/复核工作

**origin: ai** · 2026-10-21 · 配套 AGENTS.md「研究优先 / 工具优先 / 问题与网络规则」

> 触发：需要联网调研（arXiv/GitHub/学术交叉验证）、大任务分解、或多模型交叉复核时，
> **优先外包给 LMArena 的 agent mode**（arena.ai/agent），而不是自己一步步抓。
> 前置：用户已在 ego-lite 浏览器中登录 arena（见 ego-browser skill）。

## 为什么是 arena
- **性价比**：免费，一个 agent 会话可跑多步任务（搜索+阅读+综合），替代 N 次 ego-browser 手动抓页
- **交叉验证天然**：LMArena 背后是多模型匿名对战/混合，同一 claim 可让多个模型各答一遍 = 02.5/04.5 交叉验证的免费通道
- **agent mode 可直接代干活**（AGENTS.md 站点清单标注"可选项最多"）：给它任务，它自己搜、自己读、自己汇总

## 通道：ego-browser（唯一，AGENTS.md 硬规则）

**故障处置**（2026-10-29 r32 补丁，成璐指令）：登录态几个月不失效，遇到"疑似掉线/401/重定向到登录页"**先检查工具和网络，别放弃、别直接找用户**：① `curl -I https://arena.ai` 确认网络通 ② ego-browser 重新 goto 目标页看是否只是会话页面过期 ③ 查 ego-lite 进程是否活着（`ps aux | grep -i ego`）④ 仍失败才记录具体报错找用户。把"要用户重新扫码"当第一反应是错的。

```bash
ego-browser nodejs <<'EOF'
const task = await taskSpace('arena-outsource-<stage>-<date>')   // 同任务复用同名 space
const p1 = task.page('p1')
await p1.goto('https://arena.ai/agent')
const s = await p1.snapshot()          // 定位输入框: @N ref / loc=css: / loc=role: / text=
// fill 任务 prompt → click 发送 → waitForFunction 等 agent 跑完 → snapshot 读结果
await task.finish({ keep: [] })        // 结束必须 finish，否则僵尸进程
EOF'
```

## 拆分优先（大调研题 · 2026-10-22 成璐 m00656 指令）

大题目 ≠ 一个 subagent 全包。标准流程：
1. **Lead 拆正交子领域**（3–7 个；每个子领域能独立成一句话问题）
2. **每个子领域 1 个 subagent**（任务卡自包含、背景 ≤10 行），并行 ≤3（subagent 上限）
3. subagent 按本 SOP 走 arena agent mode 调研 → 交付物先落盘
   3a. **arena 通道调研时，每个子领域拆成 2 个 subagent**（主调研 + 交叉验证），而非 1 个 subagent 做两件事——arena 失败率高，拆开后即使挂了一个，另一个还能落盘
   3b. **任务时长阈值**：≤15min 短任务（无需 checkpoint）/ 15–30min 中任务（需 checkpoint）/ >30min 长任务（应拆分）
4. Lead 汇总 → 交叉验证门禁 → 回写项目

为什么拆：短任务失败模式少、可断点恢复、可并行。本会话实证：3 个 20–90min 长任务挂 2 次 + 1 次 arena 回复未落页；子领域级短任务全部落盘。

## SOP（5 步）

0. **任务书 push 仓库**（2026-10-28 r26 补丁，成璐指令）：arena 会话绑定 GitHub 仓库时，任务书先 commit+push 到该仓 `tasks/<T-id>.md`，派发 prompt 只写「读 tasks/<T-id>.md 按其中步骤执行」——不贴 clone 命令、不在聊天里复制任务内容。prompt-first 类任务额外加一句「严格按仓库内 loop/prompt-first/ 的阶段 prompt 执行」（防 agent 用默认流程绕过修订规则）。仓库未绑定时才退回自包含任务卡。
1. **写任务卡**（给 arena 的 prompt，必须自包含；仅用于无仓库绑定的场景）：
   - 目标（一句话）+ 约束（语言/格式/长度）
   - 明确交付物格式（如「3 条来源+conf 的 JSON」「分解树 markdown」）
   - 要求标 conf，要求给来源 URL
2. **ego-browser 提交**（上面代码块）；agent mode 下等它跑完（waitForFunction 检测输出稳定，超 5min 算超时）
3. **snapshot 读取结果** → 存到项目 `loop-artifacts/stages/<stage>/arena-outsource/<task>.md`
4. **交叉验证门禁**（02.5/04.5）：同一 claim 至少 2 个独立回答（同一 arena 会话内让不同对战轮次各答一遍，或 arena + 另一站点），矛盾点记录 + 进一步核实；回执 JSON 满足 AGENTS.md「回执与门禁」最低字段（`kind: "ralph_web_llm_cross_check"` / `responses[]` / `successful_provider_ids[]` ≥2 / `observed_at` 带时区）
5. **落盘**：结论写入项目 `tasks/decomposition.md` 或 `memory/`，标 `# origin: ai` + conf + 来源
   5a. **汇总报告分层**（2026-10-22 S4 补丁）：核心发现 ≤20 行（结论+关键数字+决策）+ 附录（完整数据，引用源文件路径）。Lead 汇总时先写核心，附录只写"详见 <路径>"。实测 S4 汇总读了 S2+S3 共 153 行，报告只用 ~40 行核心，其余 110 行是过程论证，对下游无用。
   5b. **loop-state change_log 轮转**（2026-10-22 S4 补丁）：保留最近 5 条详细记录，更早的压缩为一行摘要（`2026-10-21 r15-r19: 公轴 v2→v2.1 迭代`）。新 agent 只关心"当前状态 + 最近 3 轮"，历史细节在 memory/ 按需查。
   5c. **APPROVALS 分区**（2026-10-22 S4 补丁）：待批/已批严格分区，已批只保留"条目号+日期+一句话结论"，细节移到 `个人/history/APPROVALS-<YYYYMMDD>.md`。新 agent 扫 APPROVALS 时只看待批区。

## 任务卡模板

```
[任务] <一句话目标，具体到"回答 X 问题"，不开放式>
[背景] <最小必要上下文，≤10 行>
[约束] 中文回答；每条结论标 conf(0-1)；给来源 URL；不确定的标"未验证"
[交付] <markdown 表格 / JSON schema，给具体模板>
[长度] ≤50 行（核心发现+关键数字+决策，过程论证放附录）
[正交性自检]（可选）本子领域与其他子领域的输入/输出/时间轴重叠度（<30% / 30-50% / >50%）
[落盘约束] 文件不存在=任务未完成，Lead 不验收
```

**任务卡 prompt 优化 3 原则**（2026-10-22 S5 prompt 级补丁）：
1. **交付格式模板化**：[交付] 字段必须给具体模板（markdown 表格/JSON schema），不开放式。实测 S2/S3 给了 markdown 模板，subagent 直接按模板写，格式合规率高。
2. **输出长度限制**：[长度] 字段限制"≤50 行"，避免 subagent 写长篇。实测 S2/S3 没限长度，写了 60/93 行，其中 ~110 行是过程论证（S4 汇总只用了 ~40 行）。
3. **问题具体化**：[任务] 字段必须具体到"回答 X 问题"，不开放式。"总结瓶颈"→"列出 arena 通道前 3 大失败模式+修复方案"。实测 S1 "读 5 个文件总结瓶颈"太开放，subagent 读了 4/5 后结束。

**背景最小化判据**（2026-10-22 S4 上下文管理补丁）：逐行问"删掉这行后 subagent 还能独立回答吗？能→删"。实测 S1 任务卡给了 5 个文件路径（~30 行），subagent 读了 4/5 后结束，背景过多分散注意力。正确做法：只给"回答问题必需的最小事实"，其余让 subagent 自己读文件（给路径不给内容）。

## 失败处理与降级（2026-10-22 实测补丁 · 本轮 4 次错误归纳）

1. **回复落页校验**：提交后先 waitForFunction 等新输出出现；**三档超时**：30s 无新 DOM 节点 → 判定"没跑"，re-snapshot 重新定位输入框+发送按钮，重试 1 次；1min 有输出但无新输出 → 判定"跑慢"，继续等到 3min；3min 无新输出 → 判定"超时"，**直接进降级阶梯第 2 级**（不再 re-snapshot 第二次）。"提交成功"≠"回复已落"（实测：decomp 提交成功但回复未落页，页面疑似 outage，subagent 空等 20min+）。
2. **降级阶梯**（逐级降，每级记录原因）：arena agent mode → arena 普通 Battle → ego-browser 直抓目标页 → 自答。自答时 conf −0.2，文件头标「arena 不可用 <日期> <原因>（降级自整理）」。
3. **恢复协议（幂等）**：subagent 开工先检查交付文件是否已存在且完整 → 完整则跳验证；中断后从最近完成步骤续跑，任务卡必须可重入（不依赖内存态）。
4. **交叉验证降级**：第二站点不可用（页面漂移/未登录）→ 用 arXiv 摘要/官方文档直核替代，回执记「交叉验证降级：<站点>不可用，改 <来源>」（实测先例：persona 调研 ChatGPT 漂移 → arXiv 2509.14543/2509.24930 直核）。
5. **长任务 checkpoint**：预计 >15min 的任务，先写交付文件「开始」行 + 更新 loop-state，再开工；中途挂掉 Lead 也能从磁盘看出进度（实测：persona RESEARCH.md 87min 后才落盘，期间无任何中间痕迹，只靠 .bak-v0 推断）。
6. **格式校验**（理论推演，待实测）：任务卡加"[格式校验] 交付物必须是 <markdown 表格/JSON>，否则重写"；Lead 收到后先 grep 关键字段确认格式合规。
7. **登录态检查**（理论推演，待实测）：提交前 snapshot 确认"退出"按钮存在（=已登录）；若会话被重置 → 从第 1 步重新开始。
8. **串行提交**（理论推演，待实测）：同一 taskSpace 内多任务串行提交，不并发；等回复落页再提交下一个。
9. **落盘硬约束**（高优，本会话实证 #4）：任务卡加"文件不存在=任务未完成，Lead 不验收"；Lead 收到完成通知后先 `ls` 确认文件存在+行数>0（实测：memory-hooks researcher 结束未写文件）。

## 边界
- arena 是**执行层**外包，决策仍在本会话（conf 低/矛盾 → 自己用 ego-browser 补查）
- **链路硬规则（2026-10-22 成璐 m00201 批准）**：① arena 外包 = 必须首选通道（默认走 arena，不自己 AI 琢磨）；② loop 6 阶段（01→04.5）无论 arena 执行还是回退本地自答都全程必需——回退降级的是执行通道，不是流程。本 skill 的 5 步是**提交机制**；调研/核验/执行类任务的链路总控见 `sop/arena-loop-pipeline.md`（唯一 SOP 入口，含仓库映射/降级/断点门禁）。
- subagent 无网络（AGENTS.md 硬规则）：需要在线信息时由 Lead（本会话）走本 skill 代查并写文件，subagent 读文件
- 匿名 Battle 评测（非 agent mode）有专门工具：`projects/decomp/arena_capture/`（Edge+CDP 驱动，先读其 SKILL.md）——与本 skill 正交：那里是「评测模型」，这里是「外包任务」
- web_search 仍禁用（付费）；纯 JS 聊天页 WebFetch 仍禁用

## 仓库绑定门禁（2026-10-29 r79 补丁 · 成璐指令）

**教训**：r64-r69 复用旧 arena 会话派发 rubric-v3/deepresearch 任务，该会话历史里混着 market-alpha 的 T3 任务消息，用户误判"所有工作都在 market 下面"。实际产出全在 prompt-first-bench（已逐条核验 remote/分支），但**派发前没有验证绑定**，是流程缺口不是结果错误。

硬规则：
1. **每次派发前必验绑定**：ego-browser 打开目标会话 → snapshot 读 "Coding session repository and branch" 区块 → 确认仓库名 + 分支与任务书所在仓一致，不一致就停（新开会话选对仓库，不复用错绑定的会话）。
2. **长会话历史污染**：一个 agent 会话跑过多项目任务后，对话历史会串（旧项目的仓库名/路径出现在上下文里），模型可能按旧上下文行动。跨项目任务必须开新会话，或派发时显式声明「本任务只涉及 <repo> 仓库，忽略历史中其他仓库的消息」。
3. **回执带仓库指纹**：arena 执行类任务的回执 JSON 必须含 `repo`（remote URL）+ `branch` + `commit_sha`，Lead 落盘前用 `git ls-remote` 核对 sha 存在——回执没指纹 = 未验证，不通过门禁。

## 会话复用纪律（2026-10-29 r80 补丁 · 成璐指令）

**原则：一个仓库 = 一个 arena 会话，长期复用，不乱开新窗口。**

1. **同仓库任务一律复用已有会话**：派发前先看该仓库是否已有活跃 agent 会话（ego-browser 打开 arena.ai/agent 列表核对），有就直接在那个会话里发下一条消息，不开新会话。
2. **跨仓库才开新会话**：目标仓库和现有会话绑定的仓库不一致时，才为新仓库开新会话（按 §3.1 映射表选仓库直连）。
3. **历史污染靠显式声明解决，不靠换会话**：同一仓库的长会话历史串了旧上下文 → 派发 prompt 开头加一句「本任务只涉及 <repo>/<branch>，忽略历史中其他仓库的消息」，不换会话。
4. **会话台账**：`sop/arena-loop-pipeline.md` §3.1 映射表旁维护「仓库 → 当前会话 ID/URL」对照，每次开新会话后更新；派发前先查台账。

## 会话固定仓库（2026-10-29 r81 补丁 · 成璐指令）

**每个 arena 会话从创建起就固定绑定一个仓库，永不混用。**

1. **开新会话时选仓库**：按 §3.1 映射表选好目标仓库再建会话；建完立刻把「会话 ID → 仓库」写进 `sop/arena-loop-pipeline.md` §3.1 会话台账。
2. **派发前查台账**：要派任务 → 先查该仓库在台账里绑定的会话 → 直接在那个会话发。找不到才开新会话（选对仓库 + 登记台账）。
3. **禁止跨仓库复用同一会话**：一个会话只服务一个仓库。旧会话历史里混过其他仓库消息的（如 pfb 会话里的 market-alpha T3），视为"脏会话"——继续用可以，但每次派发 prompt 必须开头声明「本任务只涉及 <repo>/<branch>，忽略历史中其他仓库的消息」。
4. **为什么之前会连错**：r64-r69 复用了 deepresearch 调研建的会话，那个会话早期跑过 market-alpha 的 T3 任务，agent 上下文被旧仓库消息污染，我派发时没验绑定、没加声明，属于流程执行缺失，不是 arena 机制问题。现在门禁补上了：查台账 → 验绑定 → 显式声明，三步缺一不可。

## 行动 hook（2026-10-29 r83 · 成璐指令）

**派发 arena 任务前，Lead 必须在当轮先执行以下动作（不是靠自觉读文档）：**

```bash
# 1. 查会话台账（仓库 → 会话 ID 对照）
grep -A5 '会话台账' sop/arena-loop-pipeline.md | head -15
# 2. 确认目标仓库远端可达 + 任务书分支存在
git ls-remote https://github.com/dd2003-460/<repo>.git 'refs/heads/<branch>'
```

两条命令的输出都要在派发前的同一轮里跑过。台账里没有该仓库的会话 → 开新会话选对仓库并登记台账；有 → 打开该会话 snapshot 验 "repository and branch" 区块再发。跳过这两步直接派发 = 流程违规。

## 派发前检查清单（硬门禁 · 每轮派发必过）

**触发条件**：本轮要往 arena 发任务消息时，先逐条过以下清单，全部通过才许点发送。任何一条不过 = 停，先修再发。

| # | 检查项 | 怎么验 | 不过怎么办 |
|---|--------|--------|-----------|
| 1 | 台账有该仓库的会话 | `grep -A5 '会话台账' sop/arena-loop-pipeline.md` | 没有 → 开新会话选对仓库，登记台账 |
| 2 | 目标分支远端存在 | `git ls-remote https://github.com/dd2003-460/<repo>.git refs/heads/<branch>` 返回 sha | 不存在 → 先 push 任务书分支 |
| 3 | 会话绑定正确 | ego-browser 打开会话，snapshot 找 "Coding session repository and branch" 区块，仓库名+分支与任务一致 | 不一致 → 停用该会话，按台账换或新建 |
| 4 | prompt 带仓库声明 | 派发文本开头含「本任务只涉及 <repo>/<branch>，忽略历史中其他仓库的消息」 | 补上再发 |
| 5 | 回执指纹要求已写进任务书 | 任务书末尾有「完成后回执必须含 repo URL + branch + commit_sha」 | 补进任务书再派 |

**为什么是清单不是文档**：r64-r69 连错仓库的根因是"知道规矩但派发时没执行"。清单把规矩变成逐条打勾的动作，跳过任何一条都算违规。


## 分支切换门禁（2026-10-29 r84 · 成璐指令）

**教训**：r79-r83 反复让 arena "checkout exp/rubric-v3-ablation"，它每次都拒绝——因为 arena 会话绑定的是自己的工作分支（如 arena/78602cd5-prompt-first-bench），agent 认为"分支不符就不执行"。根因：**任务书 push 到了 exp 分支，但 arena 会话 checkout 的是 arena 分支，两边对不上。**

硬规则：
1. **任务书必须 push 到 arena 会话当前 checkout 的分支**（通常是 `arena/<id>-<repo>`），不是另开一个 exp/research 分支。派发前用 `git ls-remote origin <arena-branch>` 确认任务书文件在该分支上。
2. **如果任务书在别的分支**：要么把任务书 merge/cherry-pick 到 arena 分支再派，要么让 arena 先 `git fetch && git checkout <task-branch>` 并明确告知"这是本任务要求的分支切换，不是违规"。
3. **回执指纹**：arena 完成后 push 到的分支 = 它当时 checkout 的分支。Lead 核验时用 `git ls-remote origin <那个分支>` 找新 commit，不是去 exp 分支找。

## 会话清理（2026-10-29 r85 · 成璐指令）

**原则：已完成任务的 arena 会话定期清理，只保留当前活跃的。**

1. **清理时机**：每完成一个项目阶段（如 rubric-v3 消融实验结束），把该阶段用完的旧会话删掉。
2. **怎么删**：ego-browser 打开 arena.ai/agent 列表 → 每个会话右侧 "More options" 按钮 → Delete。批量删时逐个点，不写脚本（arena 无批量删除 API）。
3. **保留规则**：台账里登记的"当前活跃会话"不删；同一仓库只留最新的一个。
4. **台账同步**：删完会话后更新 `sop/arena-loop-pipeline.md` §3.1 会话台账，把已删的标记为"已清理 <日期>"或移除。

## 分支切换门禁（2026-10-29 r84 · 成璐指令）

**教训**：r79-r83 反复让 arena "checkout exp/rubric-v3-ablation"，它每次都拒绝——因为 arena 会话绑定的是自己的工作分支（如 arena/78602cd5-prompt-first-bench），agent 认为"分支不符就不执行"。根因：**任务书 push 到了 exp 分支，但 arena 会话 checkout 的是 arena 分支，两边对不上。**

硬规则：
1. **任务书必须 push 到 arena 会话当前 checkout 的分支**（通常是 `arena/<id>-<repo>`），不是另开一个 exp/research 分支。派发前用 `git ls-remote origin <arena-branch>` 确认任务书文件在该分支上。
2. **如果任务书在别的分支**：要么把任务书 merge/cherry-pick 到 arena 分支再派，要么让 arena 先 `git fetch && git checkout <task-branch>` 并明确告知"这是本任务要求的分支切换，不是违规"。
3. **回执指纹**：arena 完成后 push 到的分支 = 它当时 checkout 的分支。Lead 核验时用 `git ls-remote origin <那个分支>` 找新 commit，不是去 exp 分支找。
