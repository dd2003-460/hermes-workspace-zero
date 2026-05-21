# continue — Agent 自动循环机制

**状态**: ✅ 已实现 (2026-05-13)
**功能**: agent 完成后自动注入下一轮 prompt，持续迭代

## 实现概要

### 架构

```
用户消息 → agent 运行 → agent:end hook → 写入信号文件
→ gateway 读取信号 → 注入 _pending_messages → 下一轮 agent
→ 循环直到：完成关键词 / 达到 max_iterations / 用户手动中断
```

### 文件结构

```
~/.hermes/
├── hooks/
│   └── continue/
│       ├── HOOK.yaml          # 注册 agent:end 事件
│       └── handler.py         # 信号注入处理函数
├── continue-signals/          # 信号文件存储（动态创建）
│   └── signal-{hash}.txt      # 会话信号文件
└── config.yaml                # 配置项（可选）

projects/
└── continue/                  # 项目文档
    ├── INDEX.md
    └── memory/
```

## 使用方法

### 1. 启用 continue

在 `~/.hermes/config.yaml` 中添加：

```yaml
continue_config:
  enabled: true                    # 是否启用
  max_iterations: 10               # 最大迭代次数
  completion_keywords:             # 完成关键词（命中则停止）
    - "COMPLETE"
    - "DONE"
    - "任务已完成"
    - "全部完成"
  next_prompt_template: "继续。检查当前进展并推进下一步。"
```

### 2. 控制 agent 行为

Agent 需要明确完成标志。在 prompt 中要求：

```
请逐步完成任务。每轮完成后：
- 如果任务未完成，回复当前进展并等待下一步
- 如果任务完成，回复 "COMPLETE: [总结]" 终止循环
```

或者在 transcript 中注入 `<promise>` 标签（类似 Claude Code 的 stop hook）。

## 核心逻辑

### Hook Handler (handler.py)

1. 从 context 读取 response、transcript_path、session_key
2. 检查完成关键词 → 命中则不写信号文件（停止）
3. 检查 max_iterations → 达到则停止
4. 条件不满足 → 写入 `~/.hermes/continue-signals/signal-{hash}.txt`

### Gateway (run.py)

1. 在 10702 行检查信号文件
2. 读取信号内容 → 注入 `pending`
3. 利用现有 pending message 处理链路递归运行下一轮
4. 递归限制：`_MAX_INTERRUPT_DEPTH`

## 验证测试

```bash
# 手动创建信号文件测试
python3 << 'EOF'
import hashlib
from pathlib import Path

session_key = "weixin:test"
sig_hash = hashlib.md5(session_key.encode()).hexdigest()[:12]
sig_path = Path.home() / ".hermes" / "continue-signals" / f"signal-{sig_hash}.txt"
sig_path.parent.mkdir(parents=True, exist_ok=True)
sig_path.write_text("1234567890:继续分析。")
print(f"Created: {sig_path}")
EOF

# 重启 gateway 后观察日志：
# [INFO] Continue signal detected for session weixin:test — injecting next turn.
```

## 注意事项

1. **信号文件路径**：基于 session_key 的 md5 hash，确保不同会话隔离
2. **非致命错误**：信号文件读取失败不中断主流程
3. **递归限制**：防止无限循环，默认 `_MAX_INTERRUPT_DEPTH` 可配置
4. **用户消息优先**：用户发送新消息会清空 pending queue

## 与 Claude Code 对比

| 维度 | Claude Code | Hermes |
|------|-------------|--------|
| 机制 | 同进程 stdout JSON | 信号文件 IPC |
| 完成检测 | transcript 中的 `<promise>` | response 关键词 + 迭代计数 |
| 递归 | 无限制（同进程） | `_MAX_INTERRUPT_DEPTH` |
| 进程 | 同进程 | 跨进程（hook 子进程） |

---

*2026-05-13 实现完成*
