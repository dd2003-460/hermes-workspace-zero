# D1-grav-waves 项目团队

## 团队成员

| 编号 | 角色 | Agent ID | 职责 | 状态 |
|------|------|----------|------|------|
| 01 | 任务澄清师 | Agent 01 | 解析任务目标、边界条件、可验证标准 | 未启用 |
| 06 | 决策制定者 | Agent 06 | 基于各角色输入做阶段决策 | 未启用 |
| 07 | 预检查员 | Agent 07 | 执行 pre-check：编译、tarball 校验、依赖检查 | ✅ 本轮已用 |
| 08 | 执行员 | Agent 08 | 修复缺陷、重新打包、更新文档 | 待启用 |
| 09 | 验证员 | Agent 09 | 独立验证执行结果 | 待启用 |
| 10 | 副脑 | Brain-sub | 持续质询，发现盲区 | ✅ iteration 5 已派发 |

## 交互页面

每个 agent 的工作产出记录在：
- Agent 产出：`projects/理论物理/D1-grav-waves/logs/agent-{id}-iter-{n}.md`
- 副脑产出：`projects/理论物理/D1-grav-waves/logs/brain-sub-iter-{n}.md`
- 决策记录：`projects/理论物理/D1-grav-waves/loop/{loop-stage}/06-decision.md`

## 通信协议

1. **派发任务**：通过 Brain-sub 机制分发到对应 Agent
2. **结果收集**：Agent 完成后写入 logs/ 目录
3. **状态汇总**：ralph-loop.local.md 记录最新状态
4. **监控**：tmux sessions（待配置）

## Tmux 监控

需要配置 tmux session 管理，每个 agent 跑在独立 window：
```bash
tmux new-session -d -s d1-grav-waves
tmux new-window -t d1-grav-waves -n agent-01
tmux new-window -t d1-grav-waves -n agent-07
tmux new-window -t d1-grav-waves -n agent-08
tmux new-window -t d1-grav-waves -n brain-sub
tmux select-window -t d1-grav-waves -n monitor  # 主窗口用于查看各 agent 输出
```

状态：未配置
