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

## 待批

1. T53b webllm 降级数据处置（2026-11-20 14:52 · 不阻塞，run 继续跑）
   - 现状：Perplexity/ChatGPT 未登录 → 25/30 已跑 run 的 webllm 交叉验证全跳过（WEBLLM-BROKEN）；登录窗口已超时，剩余 ~50 run 也会降级。webllm 效应从现有数据不可识别（OK 组 n=2）。
   - **登录状态未定（14:55）**：Cookies 14:31 更新、perplexity 阶段已返回（现跑 chatgpt 阶段）→ 可能已登录成功但未验证。3 个在跑 run 已带 "skipping future webllm" 标志，永久降级；**下一个新 run 的 webllm 状态是判据**——若恢复则剩余 run 正常，数据变成"前降级后正常"混合，(a)/(b) 需重估。
   - 1.1 (a) 接受降级：62 跑完出"webllm 缺席"口径消融结论，5 个 OK run 标离群；webllm 效应另立 goal 登录后小规模配对实验补（推荐——臂间结论不受影响，代价 0）
   - 1.2 (b) 登录后重跑：现有 12/62 作废，重跑 4-5h（需 D 重新发起 Perplexity 登录）
   - 详情：pfb/tasks/T53-bus/anomaly-watchlist.md
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
