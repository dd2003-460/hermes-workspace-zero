# APPROVALS r3 轮存档（2026-10-31）

> 轮转规则：成璐 2026-10-31 指令「你自己决定 approve 里面的事情」→ AI 自主裁决全部待批条目，人类回复区由 AI 代为记录裁决依据。

## 条目 1 — hooks-codex 未生效 → **裁决 1.1（install_bundle）**

**执行结果（2026-10-31 复核）**：
- `profiles/web/package.json` deps 已含 `@deepseek-ai/dsh-hooks-codex 0.2.0-rc.2`（deps 从 13 增至 19，安装面已补齐——10-20 定位的根因已消除）。
- `.generations/live/deepseek-ai+dsh-hooks-codex+0.2.0-rc.2+asar-bundled` 存在；harness.log 10-29 04:40 重启后仅剩一条 compatibility warning（peerDeps 版本未含 dsh 0.2.1-rc.2），**无 "declares no dsh.bundle" 启动失败、无 activation failure**。
- **验证判据未完全达成**：`.hooks/state/` 仍只有 10-29 00:03 的两个 test*.jsonl，无真实 session ledger（s18-*.jsonl）。
- **残留风险**：compatibility warning 意味着 peer 依赖版本不匹配（插件要 0.2.0-rc.2 系 harness peers，宿主是 0.2.1-rc.2），加载可能静默降级。需要一次 DSH Desktop 干净重启 + 开新会话观察 `.hooks/state/` 是否出现真实 ledger。重启 DSH 属外部 app 操作，不在本轮自动执行范围，登记为后续动作。
- 结论：**1.1 已实质完成（安装面修复），端到端验证 pending 重启**。

## 条目 2 — subagent 细粒度拆分规范写入位置 → **裁决 2.1（只写 arena-outsource skill）**

**执行证据**：
- `.claude/skills/arena-outsource/SKILL.md` 「失败处理与降级」节追加第 10 条「细粒度拆分规范」（1 subagent 领 1 子领域走 arena / 短任务多并行 / 拆分判据 / 失败隔离），并诚实标注缓存收益未验证（acp_cache 实测 provider 不回报 cache tokens）。
- commit：workspace main @ 82badede（r59），已 push。
- 未动 AGENTS.md（红线文件）、未建 sop/arena-researcher.md（2.3 不做，skill 层够用）。

## 条目 3 — r4 冻结分 run1_M2=100 依赖错配输入 "49 行" → **裁决 3.3（caveat 注记 + reason 修正都做）**

**执行证据**：
- `pfb/bench/self-opt-tester/r4/adjudication-step2.json`：inputs 字段追加 caveat（run1 实测 24 行三源一致，原 49 为笔误，分值不受影响）；run1_M2.reason 改为 "24 行 ≤200 行满分（原理由文本误引 49，见 inputs caveat）"。**final=100 与 final_scores_applied 全部未动**（分数冻结纪律）。
- `pfb/bench/self-opt-tester/r5/packet-audit-r4-v1.md` X6 节追加状态更新（批准 3.3 + 双注记说明）。
- commit：pfb main @ 510c124（r45），已 push。

## 条目 4 — O3 原子 claim 清单 31 条措辞人工审定 → **裁决 4.2（认可 runner 起草版）**

**执行证据**：
- `pfb/bench/rubric-v3/o3-claim-list.md` 头部追加审定状态行（认可起草版为正式判据件，无人工逐条批注；§5.1 S2 限定语约束继续适用）。
- 依据：已过 assert-o3-claim-list.py 结构自检（31/31 覆盖、零 gold 专有数值泄漏）+ 三源校准（gold-tree 本体 + prior-estimates reason + hit-matrix h=1 evidence）。
- commit：同 pfb r45，已 push。

## 后续动作（非本轮）
- [ ] DSH Desktop 干净重启后验证 `.hooks/state/` 出现真实 session ledger（条目 1 收尾）
- [ ] 若重启后仍无 ledger：查 compatibility warning 是否导致静默降级（peer 0.2.0 vs 宿主 0.2.1）
