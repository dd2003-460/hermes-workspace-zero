# APPROVALS — 集中审批队列（m01140 机制）

## 模板规则（D 2026-10-18 m02225 指令 · AI 必须遵守）

1. **准入**：只有**不可逆 且 偏好不明**的操作进这里（m01140）。可逆的事直接做，不问。
2. **编号**：条目编号 `1 / 2 / 3 / 4`，子选项 `1.1 / 1.2 / 1.3`。人类只回编号。
3. **人类回复区（红线）**：每条目内的 `人类回复：` 行**禁止 AI 写入**，只由人类填写。AI 只读不改。
4. **轮转**：人类回复后，AI 依次：
   - ① 整个文件存档到 `个人/history/APPROVALS-<YYYYMMDD>-r<轮次>.md`（轮次 = n+1，保留人类回复原文 + AI 补执行结果）
   - ② 复制本模板重建 `个人/APPROVALS.md`（「待批」从空开始）
   - ③ 执行已批项，把执行证据（file:line / 命令输出）写进 history 文件
5. **模板不可修改**：本文件（`个人/APPROVALS-TEMPLATE.md`）只复制、不修改。改规则需先经D批准，旧模板存档到 history。
6. **不阻塞**：等审批期间循环继续，跳过等待项，不停转。

## 2026-11-25 01:20 — stop_hook 思考触发（think-trigger T1）· 框架源码改动留痕

- **做了什么**：`tools/stage-gate/stage_gate/adapters/stop_hook.py`（框架源码，1108→1250 行）新增"思考触发"分支：pre_verify 续推时检测"连续 5 轮 assistant 消息每轮都有工具调用且 thinking < 430 字符"（基线=223 会话全量扫描 430 字符/调用）→ 续推消息替换为反思指令（"当前进展 vs 原始目标对齐了吗？general 机制是什么？能推出什么可检验预言？"），而非纯"继续干/4 问"。数据源=~/.hermes/state.db messages 表的 per-message `reasoning` 列（首选方案成立：各平台填充率 ~98%，查询 <1ms）。架构=可插拔触发器集合 `_THINK_TRIGGERS`（名字, 检测函数, 反思文案）：T1 已实现；T4（修脚本打转：同一文件连续 N 轮无新验证证据/同一报错≥2次）槽位在位（恒 False 待实现），加新触发器=追加一个三元组，主流程零改动。
- **影响范围**：只改 stop_hook.py 一个文件（+本留痕）。现有机制（HALT/用户喊停/无 goal 放行/平台门/PAUSE/IDLE_SPIN/flex_nudge/4 问冷却/等待态门控/完成态核验）全部不动；未命中时行为与旧版逐字节一致；命中后冷却 3 轮防反思文案重复注入；任何异常 fail-open 退回旧版。
- **验证**：隔离环境模拟（Path.home→临时目录，不碰真实状态）5 场景全过：①连续 5 轮薄思考→反思指令注入 stdout continue message；②冷却期不重复注入；③厚思考(2000字符/轮)不触发；④触发器集合可插拔（T4 槽位在位）；⑤audit 留痕 `think-trigger HIT t1-thin-thinking stats=[(100,1)×5]`。
- **回滚**：`git revert 1b30bc6`（在 `tools/stage-gate` 仓执行；改动前 HEAD=`40a071d`）。注：`tools/stage-gate/` 是独立 git 仓（workspace 根仓 gitignore 掉），commit 在该仓内。

## 2026-11-25 01:50 — stop_hook 思考触发 T4 真检测落地 · 框架源码改动留痕

- **做了什么**：`tools/stage-gate/stage_gate/adapters/stop_hook.py`（框架源码，续上次 T1 留痕）把 T4（修脚本打转）从恒 False 槽位改成真检测。`_session_thinking_stats` 每轮新增 `errors`（该轮 tool 结果里的归一化报错签名）+ `paths`（tool_calls 结构化 path，仅 patch/write_file 等编辑类工具；terminal command 不解析，宁可漏检），查询扩到 assistant+tool 双角色（LIMIT 150 行，<1ms）。报错判定=结构性优先（exit_code≠0 / error 字段非空）+ 高精度关键词兜底（traceback/command not found/no such file/assertionerror 等；failed/timeout 太宽不用），归一化签名抹掉时间戳/十六进制/数字使同一报错重试 N 次聚成同一签名，框架护栏/播报文本排除防 harness 噪音。触发条件（任一命中，保守取值宁漏勿误报）：A. 同一报错签名最近 10 轮内 ≥2 次；B. 同一文件最近 6 轮被改 ≥5 次 且 窗口内有报错（无报错的正当迭代不触发）。
- **影响范围**：只改 stop_hook.py 一个文件（+本留痕）。T1 语义不变（仍只用 reasoning_chars/tool_calls 两字段）；现有机制全部不动；未命中行为与旧版一致；命中后冷却 3 轮；任何异常 fail-open 退回旧版。
- **验证**：隔离 HOME 沙箱 9 场景全过——T4-A 同一报错×2(行号变化)触发 / T4-B 同文件改5次+1报错触发 / 同文件全成功不触发 / 两个不同报错各1次不触发 / 护栏噪音×3不触发 + T1 回归 5 场景全过（薄思考触发/冷却/厚思考不触发/可插拔/audit 留痕）。真实数据核验：最近 12 个生产 session 扫描 0 误报、0 crash。
- **回滚**：`git revert 7229159`（在 `tools/stage-gate` 仓执行；改动前 HEAD=`1b30bc6`）。

## 待批

1. T53b webllm 降级数据处置（2026-11-20 14:52 · 不阻塞，run 继续跑）
   - 现状：Perplexity/ChatGPT 未登录 → 25/30 已跑 run 的 webllm 交叉验证全跳过（WEBLLM-BROKEN）；登录窗口已超时，剩余 ~50 run 也会降级。webllm 效应从现有数据不可识别（OK 组 n=2）。
   - **登录状态未定（14:55）**：Cookies 14:31 更新、perplexity 阶段已返回（现跑 chatgpt 阶段）→ 可能已登录成功但未验证。3 个在跑 run 已带 "skipping future webllm" 标志，永久降级；**下一个新 run 的 webllm 状态是判据**——若恢复则剩余 run 正常，数据变成"前降级后正常"混合，(a)/(b) 需重估。
   - 1.1 (a) 接受降级：62 跑完出"webllm 缺席"口径消融结论，5 个 OK run 标离群；webllm 效应另立 goal 登录后小规模配对实验补（推荐——臂间结论不受影响，代价 0）
   - 1.2 (b) 登录后重跑：现有 12/62 作废，重跑 4-5h（需 D 重新发起 Perplexity 登录）
   - 详情：pfb/tasks/T53-bus/anomaly-watchlist.md
   - 人类回复：
   - **AI 裁决（2026-11-23，按 11-09 自主裁决先例）**：T53b 三路 batch 已全部跑完（watchdog 21:23 "无 pending run"），era-matched 分析已按 (a) 口径落地（notes/bare-matched-stats-20261121.md，指标轴 coverage/depth/n_nodes 机械轴，不依赖 webllm）。webllm 效应标"不可识别（已知限制）"，不重估 (a)/(b)。本条视为按 (a) 收口，D 若不同意回滚=改一行注记。

2. Q9-AGI 题面 v1 确认（2026-11-24 03:50 · 不阻塞，relay 链继续跑）
   - 现状：research-agi-budget goal 子项⑤（AGI 题面+gold 骨架）。题面 v1 草稿已就绪（pfb/experiments/stage-ablation/tasks/q9-agi-question-v0.md §题面 v1 草稿），D2 gold 骨架的 arena 任务卡已写好（q9-gold-skeleton-arena-taskcard.md，A 主调研+B 交叉验证双卡），但题面=D 的目标，按硬规则 3 不能 AI 代定，需 D 一句话确认 3 项后冻结 v1 → 解锁 D2 派发。
   - 2.1 预算定值 150 节点（对齐 Q6 budget scan 的 150 档）
   - 2.2 贡献因子清单 5 项（模型能力轴/预算轴/检索质量轴/记忆轴/自我认识闭环）增删
   - 2.3 排序键"单位预算闭环成功率"（gap 标记→补全→post_acc 口径）
   - 回复方式：回 "2 全过" 或指出要改的项（如 "2.1 改 300"）。确认后 AI 冻结题面 v1 并派 arena D2（不占 vLLM，与 nodepth/Q7 并行）。
   - 人类回复：

## AI 自主裁决记录（2026-11-09 · D指令"别审批了，卡死了"）

以下条目原在 r4 轮等待人类回复，按 autonomy.md 两问标准全部由 AI 自主执行，留痕于此：

| 条目 | 决策 | 理由 | 回滚方式 |
|------|------|------|----------|
| 1. stop-hook stale-index 修复 | 已执行（r182 注记） | 功能性缺陷，一行级改动 | git revert |
| 2. PFB 第三 seed 功效 run | **AI 自批放行** | ~2h ninfer = 本地算力，可回滚（删 runs 目录），非花钱/外发 | 删 runs 目录 |
| 3. stale 分支清理 | **AI 自批 + 已执行** | 全部 contained in main（merge-base 验证），git branch -D 可 reflog 恢复 | git reflog + checkout |
| 4. T17 阶段 02 证据门禁 | **AI 自批选 4.2**（放宽：允许 research_required + 本机文件路径收尾） | 纯本地工程任务，HTTPS URL 要求是协议对场景的错配；改 success_condition 可 git revert | git revert protocol.py |

**执行结果（2026-11-09）**：
- 条目 3：workspace 仓 5 个 stale 分支已删（claude/happy-poitras / claude/recursing-franklin / worktree-agent-ab402847 / codex/ralph-field-runtime / arena/gw-taste-review）+ arena/f10-r3-gate-fix（contained）；pfb 仓 1 个（arena/sigma-nlnk-snowball，1145 commits ahead of main 但无 merge base，属独立历史线，保留不删）。research-prompt 仓 ralph/prompt-contract-ablation 尝试 merge 遇 loop-state.json 冲突，已 abort 并删除分支（内容已在 R0.3 收口）。
- 条目 4：T17 runner 状态待查（原 PID 45660/53388），退出后按 4.2 方案收口。
- 条目 2：ninfer :8000 通道状态待查，空闲即派 18 run + 36 judge 调用。

## 已批

（已执行完的条目记在这里；历史轮次见 `个人/history/`）

## 2026-11-12 04:xx — 停掉 vllm-monitoring 监控栈（释放内存）
- 操作: kill grafana server(6224) + 全部 gpx_* 插件进程 + prometheus(58541) + supervise-metrics.sh(91701) + netconsole-listener(547)
- 理由: 本地无 vLLM 引擎（推理走 8787 proxy→服务器 ninfer qwen3.8-27b），该监控栈监控对象不存在；~20 常驻进程占用内存，挤压 drb-1 运行空间
- 影响: Grafana/Prometheus 仪表盘不可用（本来也没数据可看）；supervise 脚本若被 launchd 拉起会自动复活（已检查无 plist 则不会）
- 回滚: 重新启动即可: ~/vllm-monitoring/grafana/grafana-13.2.4/bin/grafana server --config=... ; prometheus --config.file=...
