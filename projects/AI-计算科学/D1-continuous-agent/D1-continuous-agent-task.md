{
  "requirement": "验证 Claude Code 团队配置的有效性，探索 agent 持续循环机制",
  "background": "ITERATION 501 — 1-loop 已完成。TASKS.md 标注'dynamic workflow + CC团队 集成验证'未开始。现有 signal-ops 和 forge-labs 团队配置。",
  "existing_info": [
    "stop-hook-analysis: Claude Code Stop Hook 可以阻止退出并注入 prompt",
    "hermes-gateway-hooks: agent:end 事件可触发外部 observer",
    "signal-ops: team-lead (opus), project /Users/a1-6",
    "forge-labs: team-lead + alice/bob/jack, MLX distilled model"
  ],
  "constraints": ["不修改 ralph-loop.global.md（除 iteration 计数）", "跳过作者确认阻塞项"],
  "priority": "immediate"
}
