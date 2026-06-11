# Ralph Loop Team — 持久化配置模板

## 下次如何重新创建团队

```bash
# 1. 确保实验功能已启用
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# 2. 在这个 conversation 中直接调用 TeamCreate:
# (Claude Code 会自动从 config.json 读取配置并恢复角色)

# 或者手动导入:
# 将下面的 config.json 保存到 ~/.claude/teams/ralph-loop-next/config.json
# 然后启动一个新的 Claude Code session，团队会自动加载
```

## 团队成员角色定义

| 角色 | 职责 | 负责阶段 |
|------|------|----------|
| planner | 任务澄清 + 目标定义 | 1-loop 01-02 |
| researcher | 任务分解 + 外部信息搜集 | 1-loop 03-04 |
| verifier | 完备核验 + go/no-go 决策 | 1-loop 05-06 |
| executor | 预检查 + 备份 + 执行 | 2-loop 01-03 |
| reviewer | 验证 + 置信度 + 分叉决策 | 2-loop 04-06 |

## 依赖关系

```
planner ──→ verifier ──→ executor ──→ reviewer
             ↑
researcher ──┘
```

## 查看成员工作

- 收件箱: `~/.claude/teams/ralph-loop-next/inboxes/{name}.json`
- 产出文件: `projects/D1-persona-align/tasks/` (planner/researcher) 和 `projects/D1-persona-align/backups/` (executor)
- 发消息: `@{name} 请汇报你的进度`

## 已产出的关键文件

- persona-v3-prompt.txt — 部署用的 prompt 模板 (iteration 268 增强)
- verify_prompt.py — prompt 专用验证脚本
- verification-report-prompt.json — 验证报告
- iteration-268 日志: memory/iteration-268-prompt-generation-complete.md
