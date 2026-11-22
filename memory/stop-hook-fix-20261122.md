# stop_hook 连续行动修复（2026-11-22，D："stophook 本来可以，但是问题太多了，怎么办"）

## 根因（有硬证据）

`~/.hermes/.stage-gate/HALT` 是**全局单文件**停止门，无会话归属、无过期。
今早 03:23 config-sync cron（AGENT 型，每小时起一个 LLM 会话）跑完想停，
stop_hook 因"有全局活跃 goal (research-agi-budget)"一直让它 continue，
它写 HALT 强行停自己（HALT 文件内容自述）——副作用：主会话自动续推
从 03:23 到 23:35 全被"HALT 存在→放行停止"压死（progress.log 25 条误杀）。

同时：stop_hook 注释里假设的"keepalive cron 每 5 分钟唤醒"实际**不存在**
（cron 列表里只有 config-sync + t53b-snapshot），唤醒半边是死的。

"问题太多" = ①HALT 无 TTL，瞬时会话能永久压死主会话 ②纯 bash 任务
（config-sync）不该跑 agent 会话 ③唤醒机制缺失。

## 修复三件套（全可逆，未碰 SM/batch/watchdog）

1. **HALT 加 6h TTL**（stop_hook.py，commit 0067f95 @ tools/stage-gate repo）：
   mtime > 6h 视为 stale，忽略并 audit 留痕（halt-stale），不阻断续推。
   手动写 HALT 想停通常几分钟内消费，6h 余量不影响真停语义。
   备份：stop_hook.py.bak-20261122-halt-ttl。
   测试：新鲜 HALT→stop ✓ / 8h 旧 HALT→continue ✓ / 无 HALT+活跃 goal→continue ✓
2. **LAST_ACTIVE 心跳**（stop_hook.py main() 开头）：任何 hook 触发刷新
   `~/.hermes/.stage-gate/LAST_ACTIVE` 时间戳。
3. **keepalive-wake.sh**（~/.hermes/scripts/，cron 03f4afb0ea3b，每 10min，
   no_agent，deliver 本 QQ 会话）：三条件全满足才输出唤醒消息
   （空闲>10min + 有活跃 goal + 距上次唤醒>30min），否则静默（watchdog 模式）。
   测试 5 分支全过（含全角逗号变量名 bug 修复：$active→${active}）。
   config-sync 同步转 no_agent（cron b650a2d69bf8，script=hermes-config-sync.sh
   wrapper→workspace 真身，单一来源），不再起 agent 会话写 HALT。

## 连续性架构（修复后）

- 会话内：stop_hook pre_verify continue（有活跃 goal 就不停）
- 会话死后：keepalive-wake cron 10min 检查，空闲+有 goal→投递唤醒消息
- 真停：HALT（6h 内有效）/ 用户喊停 / 无活跃 goal
- 失效模式：gateway 挂（heartbeat 可查）/ 无 goal（设计如此，不刷屏）

## 诚实边界

唤醒消息是"外部 user 消息"身份注入，主会话收到后靠 goal 状态机 +
plan-layered 的"唤醒后第一动作"续接。这解决了"什么时候醒来"，
但醒来后干得对不对仍靠规划质量。
