# origin: ai (2026-11-03 成璐指令"要不弄个故障索引")

# 故障索引 — 所有通道/工具/环境故障的单一登记处

## 规则

1. **任何故障结论写入前必须先查本文件**（防重复归因、防笼统结论复发）。
2. 每条必须写清【哪条链路 + 具体报错】。禁止"XX 通道不可用"这类无链路标识的笼统记录——stop_hook 会扫这种措辞并注入提醒。
3. 修复后不删除条目，改 status=已修复 + 补 root_cause。历史故障是未来排查的证据。
4. 新增条目追加到表格末尾，编号递增 F<n>。

## 两条独立浏览器链路（归因时必区分）

| 链路 | 是什么 | 登录态 | 用途 |
|---|---|---|---|
| ego-lite 持久会话 | WorkBuddy 维护的持久 profile，profile 目录一直活着 | deepseek/chatgpt/arena 等已登录，几个月不失效 | arena 外包唯一合法通道；网页 LLM 交叉验证 |
| ralph Playwright profile | ralph loop runner 自带的无头实例 | 无（每次新实例） | ralph 内部流程，与 arena 无关 |

一条链路故障 ≠ 另一条故障。跨链路归因 = 违规。

## 故障登记表

| 编号 | 日期 | 链路/组件 | 具体报错 | 根因 | 处置 | status |
|---|---|---|---|---|---|---|
| F1 | 2026-09-10 | ralph Playwright profile（非 ego-lite） | web-llm-check 3/3 provider 登录失败 | ralph 自带 Playwright 是无头新实例，无登录态；被误记为"web-llm 门禁不可用"并沉淀进 MEMORY.md，导致 2026-11-03 错误推断 arena 整体不可用 | 走 ego-browser（ego-lite）通道提交，有 11-01 金融项目 F6 成功先例；MEMORY.md 条目已修订；SKILL.md 加链路区分节；stop_hook 加笼统故障扫描 | 已修复（教训固化） |
| F2 | 2026-05-17 起 | Hermes cron | `NameError: tree_reduce is not defined` | Hermes 侧运行时问题，非工作区文件问题 | 待修（cron 全 paused 期间未阻塞主流程） | 未修复 |
| F3 | 2026-08-25 起 | 工作区整体 | 无产出（休眠） | 13 个 cron 全部 paused，无后台自主执行 | 2026-11-03 恢复活跃；PAUSE 机制已落地可手动控制 | 已修复 |

## 关联

- SOP 全文: `.claude/skills/arena-outsource/SKILL.md`「链路区分」节
- 自动拦截: `tools/stage-gate/stage_gate/adapters/stop_hook.py` VAGUE_FAILURE_PATTERNS（命中笼统措辞 → INBOX 注入归因提醒）
- 召回触发: `~/.hermes/agent-hooks/inject-rules.sh` memory-recall 路由（消息含"故障/报错/卡在哪"等词 → 强制先读本文件）