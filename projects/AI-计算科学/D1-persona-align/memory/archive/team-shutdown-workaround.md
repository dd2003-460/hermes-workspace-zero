# Team 功能 Shutdown Bug 与绕过方法

## 问题

使用 `TeamCreate` 创建的团队成员 (in-process backend) 无法通过 `shutdown_request` 正常退出。`TeamDelete` 会报错：
> Cannot cleanup team with N active member(s): Use requestShutdown to gracefully terminate teammates first.

即使所有成员的 inbox 中 shutdown_request 都已标记为 "read: true"。

## 原因

in-process 后端的 agent 在接收 shutdown_request 后不会自动终止进程。它们可能仍在等待 mailbox 消息或处于 idle 状态。

## 绕过方法

1. **不要使用 TeamDelete** — 留下残留的 team 目录和 inbox 文件无害
2. **下次使用 TeamCreate 时** — 使用不同的 team_name，旧的会自动过期
3. **手动清理** — 如果团队不再需要：
   ```bash
   rm -rf ~/.claude/teams/<team-name>/
   rm -rf ~/.claude/tasks/<team-name>/
   ```

## 结论

Team 功能在单次 session 内有效：
- ✅ 可以 spawn 多个成员
- ✅ 可以通过 mailbox 分发任务
- ✅ 成员产出文件正确
- ❌ 无法优雅 shutdown
- ❌ 无法在同一个 session 中重新创建同名团队

这是 Claude Code 的已知限制，非我们实现的问题。
