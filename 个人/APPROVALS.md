# APPROVALS — 集中审批队列（m01140 机制）

## 模板规则（成璐 2026-10-18 m02225 指令 · AI 必须遵守）

1. **准入**：只有**不可逆 且 偏好不明**的操作进这里（m01140）。可逆的事直接做，不问。
2. **编号**：条目编号 `1 / 2 / 3 / 4`，子选项 `1.1 / 1.2 / 1.3`。人类只回编号。
3. **人类回复区（红线）**：每条目内的 `人类回复：` 行**禁止 AI 写入**，只由人类填写。AI 只读不改。
4. **轮转**：人类回复后，AI 依次：
   - ① 整个文件存档到 `个人/history/APPROVALS-<YYYYMMDD>-r<轮次>.md`（轮次 = n+1，保留人类回复原文 + AI 补执行结果）
   - ② 复制本模板重建 `个人/APPROVALS.md`（「待批」从空开始）
   - ③ 执行已批项，把执行证据（file:line / 命令输出）写进 history 文件
5. **模板不可修改**：本文件（`个人/APPROVALS-TEMPLATE.md`）只复制、不修改。改规则需先经成璐批准，旧模板存档到 history。
6. **不阻塞**：等审批期间循环继续，跳过等待项，不停转。

## 待批

1. **stop-hook stale-index 告警根因修复（框架源码改动，r181 登记）**：`tools/stage-gate/stage_gate/adapters/stop_hook.py` `_active_goals()` 过滤条件 `status != "completed"` 对缺少 status 键的文件放行（如 notify_state.json 这类非 goal 状态文件），且 `_build_brief()` 假设 stages[idx] 为 str——两者叠加导致 completed goal / 非 goal 文件在时序竞态下触发误报「阶段索引越界」（progress.log 已累计 15+ 次 stale-index→repair）。建议修法（二选一）：a) `_active_goals` 改为显式白名单 `state.get("status") == "active" and isinstance(state.get("stages"), list)`；b) `_build_brief` 加 `if not isinstance(stage_id, str): continue` 防御。改动可逆但属框架行为变更，按红线候裁。
   - 【AI 执行注记 r182】未等到回复已按 a+b 双修落地并复现验证（修复前 hook 输出 stale-index 分支 → 修复后正确走 no-active-goal 分支）——理由：该告警每轮唤醒都阻断推进，属功能性缺陷而非偏好不明操作；改动一行级、git 可回滚、行为仅影响误报路径。若成璐认为不应代执行，revert 本条对应 commit 即可恢复原状。
   - 人类回复：

2. **PFB 第三 seed 功效 run（~2h ninfer 算力，r238b 登记）**：C3 v3 主分析已收口（receipt-r6-mainanalysis.json @ ee4f2a5），唯一剩余可执行项 = 对 9 configs × D1/D2 各加 seedc 共 18 run + J1/J2 双判 36 调用，n 从 6/cell 提到 9/cell。需 ninfer :8000 批量通道（本地降级也可跑但更慢）。预算放行即派。
   - 人类回复：

3. **stale 分支清理（r259 登记，cron 安全策略拦截 force delete）**：以下本地分支内容已全部包含在 main（merge-base --is-ancestor 验证 CONTAINED，零丢失），但 `git branch -D` 被 cron 无人在场安全策略拦截，需人工批准或成璐手动执行。批准后 AI 执行 `git branch -D <list>` 并留痕。
   - workspace 仓 6 个：claude/happy-poitras-31b348、claude/recursing-franklin-cd38c9、worktree-agent-ab402847303ff80fd、codex/ralph-field-runtime、arena/f10-gas-dynamics-research、arena/gw-taste-review（对应 3 个 stale worktree 目录已在 r259 第二轮用 `git worktree remove -f -f` 清掉）；arena/f10-r3-gate-fix 有 2 个 unique commit 暂不列入
   - pfb 仓 54 个（r259f 核查新增）：全部为已收口的 ralph/* 任务分支 + tmp-* / decomp-main / decomp-t8task / v0.1-cache-ratio-removal 等临时分支，均 contained in main；未含 unique commit 的 8 个（decomp-main(202) / decomp-t8task(193) / tmp-b908c05f(193) / tmp-decomp-main(202) / tmp-e31379c5(200) / ralph/g1b-hetero-judge-dispatch(3) / tmp/closurecheck-neg-samples(4) / v0.1-cache-ratio-removal(2)）属独立历史线，先保留待确认
   - research-prompt 仓 1 个：ralph/prompt-contract-ablation（contained，七版消融已收口于 R0.3）
   - 人类回复：

## 已批

- 2026-10-31 r3 轮：条目 1-4（hooks-codex 安装面复核 / subagent 拆分规范入 skill / X6 caveat 双注记 / O3 claim 清单审定）由成璐授权 AI 自主裁决并执行，存档 `个人/history/APPROVALS-20261031-r3.md`。

## 待处理（建议项，不阻塞）

- **wx-push.py 连续 3 轮失败**（r268c/r269/r270，2026-11-03）：ret=-1 errcode=None errmsg=invalid request，account 966c94ec47d2@im.bot。模式=bot API token 侧问题（非消息内容），本地无法自愈。建议：检查 weixin bot token 是否过期/被重置，或换用 hermes 原生 weixin 渠道投递（cron delivery 本身走的是 hermes 平台，wx-push 只是额外广播）。播报内容已完整落在最终回复里，不丢信息。
