# 01 — Claude Code Stop Hook 机制完整分析

**日期**: 2026-05-13
**状态**: 初始分析完成
**参考**: Claude Code ralph-loop 插件 + bash ralph-loop skill + hookify 模式

---

## 关键纠正

之前说"hook 都是观察者模式，无法注入新 prompt"是**错的**。Claude Code 确实有**决策型 hook**（decision hook），可以阻止 agent 退出并注入新 prompt。

---

## 方案 A：Claude Code 原生 Stop Hook

### 机制

Claude Code 提供 `Stop` 事件钩子，当 agent 尝试退出时触发。`Stop` 钩子通过 `command` 类型执行 shell 脚本，脚本的 stdin 接收 JSON 上下文，stdout 输出 JSON 决策。

**决策输出格式**:
```json
{
  "decision": "block",
  "reason": "<prompt_text>",
  "systemMessage": "🔄 Ralph iteration N"
}
```

- `decision: "block"` — 阻止 agent 退出
- `reason` — 注入到下一轮的 prompt
- `systemMessage` — 本轮系统消息

### 入口文件

```
plugins/ralph-loop/hooks/hooks.json:
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh\""
      }]
    }]
  }
}
```

### 核心逻辑（stop-hook.sh 流程）

```bash
# 1. 读取 stdin JSON（Claude Code 注入的会话上下文）
HOOK_INPUT=$(cat)
# 格式: {"session_id": "...", "transcript_path": "..."}

# 2. 检查 state 文件确认 loop 是否活跃
#    文件: .claude/ralph-loop.local.md
#    字段: iteration, max_iterations, completion_promise, session_id

# 3. 解析 transcript（JSONL 格式），提取最近 assistant 文本
LAST_LINES=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -n 100)
LAST_OUTPUT=$(echo "$LAST_LINES" | jq -rs '
  map(.message.content[]? | select(.type == "text") | .text) | last // ""
')

# 4. 检查是否出现 <promise>xxx</promise>（完成条件）
PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s')

# 5. 如果完成 → 退出，让 agent 正常关闭
if [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
  rm "$RALPH_STATE_FILE"
  exit 0
fi

# 6. 如果未完成 → 更新 iteration++，注入 prompt
NEXT_ITERATION=$((ITERATION + 1))
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$RALPH_STATE_FILE")

# 更新状态文件
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" ...

# 输出决策 JSON（输出到 stdout）
jq -n \
  --arg prompt "$PROMPT_TEXT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

# exit 0 表示 hook 执行成功
```

### 特点

- **在同进程内**：hook 脚本和 agent 共享生命周期
- **实时拦截**：agent 说"退出"的那一刻被 hook 拦截
- **状态持久化**：state 文件（markdown frontmatter 格式）跨 turn 保存
- **完成条件灵活**：支持 `completion_promise` 或 `max_iterations` 双机制
- **多 session 隔离**：通过 `session_id` 字段避免其他 session 干扰

---

## 方案 B：外部 Bash 循环

### 入口文件

```
skills/autonomous-ai-agents/ralph-loop/scripts/ralph
```

### 核心逻辑

```bash
# 每次迭代调用：
hermes chat -Q --accept-hooks --source ralph-loop --continue "ralph-session-$$" -q "$loop_prompt"

# 检查输出文件中是否出现 completion_promise
grep -Fq "<promise>$completion_promise</promise>" "$output_file"
```

### 特点

- **每次独立进程**：启动 → 运行 → 退出，完全隔离
- **依赖 `--continue`**：Hermes CLI 的会话恢复机制
- **结果在输出文件**：grep 检查输出，不是解析 transcript
- **session 隔离自然**：PID-based session name（`ralph-session-$$`）

---

## 两套方案对比

| 维度 | Stop Hook (A) | Bash Loop (B) |
|------|---------------|---------------|
| **进程模型** | 同进程内拦截 | 每次独立进程 |
| **结果检查** | 解析 transcript JSONL | grep 输出文件 |
| **状态文件** | `.claude/ralph-loop.local.md`（markdown frontmatter） | `.ralph/state.json`（JSON） |
| **依赖 agent 能力** | 需要 agent 暴露 hook API | 只需要 CLI 输入 |
| **跨 agent 通用性** | Claude Code 专属 | Hermes 通用（只要 CLI 支持 --continue） |
| **启动开销** | 无（同进程） | 每次进程启动（Python 解释器 + 模块加载） |
| **失败影响** | hook 异常可能卡住 agent | 进程异常不影响循环 |
| **完成检测** | 实时（在退出前） | 延迟（等待进程结束） |

---

## Hermes 移植可行性

### 障碍

1. **Hermes 没有 hook 机制**：Hermes 是 CLI 工具，不是持续运行的进程。它的 `--continue` 标志是会话恢复，不是 hook。
2. **没有 `Stop` 事件**：Hermes 没有暴露类似 Claude Code 的事件系统。
3. **CLI 模型**：`hermes chat -q "..." --continue session` 是一次性进程。

### 可行路径

#### 路径 1：保持现有 bash loop（方案 B）
- 已在 `scripts/ralph` 中实现
- 之前测试失败是因为 CLI 语法错误，已找到正确用法
- **推荐作为 Hermes 上的默认方案**

#### 路径 2：Claude Code 包装层
- Claude Code 调用 Hermes 子进程
- Claude Code 的 Stop Hook 负责循环控制
- 优点：利用 Claude Code 原生 hook
- 缺点：需要 Claude Code 运行

#### 路径 3：Hermes CLI 扩展
- 给 Hermes 添加 `--loop` 模式，变成持续进程
- 类似 Claude Code 的进程模型
- 工作量最大，但最彻底
- 需要修改 Hermes 源码

### 置信度评估

| 路径 | 置信度 | 理由 |
|------|--------|------|
| 路径 1 | 高 | 已有代码，只需修 CLI 调用 |
| 路径 2 | 中 | 可行但引入额外依赖 |
| 路径 3 | 低 | 需要深入理解 Hermes 架构 |

---

## 关键发现

1. **Claude Code 的 stop hook 是决策型**：不只是"观察者"，可以输出 `{"decision":"block"}` 阻止退出并注入新 prompt
2. **ralph-loop 同时实现了两套方案**：stop hook（在 Claude Code 内）和 bash loop（独立进程），不是只有其中一种
3. **状态文件格式是关键**：Claude Code 用 markdown frontmatter（可读性好），bash loop 用 JSON（解析可靠）
4. **transcript 解析是难点**：JSONL 格式，需要正确提取 assistant 文本块（text/tool_use/thinking 三种 content type）
5. **Hook 超时限制**：hook 脚本应在 < 60s 内完成（来自 hook-linter.sh 的最佳实践）

---

## 错误和纠正

- **R1**: 说"所有 hook 都是观察者模式" → **纠正**: Claude Code Stop hook 是决策型，可以阻断和注入
- **R2**: 说"ralph-loop 只用 bash 循环" → **纠正**: 同时有 stop hook 和 bash loop 两套
- **R3**: 说"Hermes 没有 --continue 机制" → **纠正**: `hermes chat --continue session` 确实存在，只是 CLI 参数语法需要注意
- **R4** (2026-05-25 迭代 95): 说"Hermes 没有 hook 机制" → **部分纠正**: Hermes 有 `agent:end` 事件系统，但它是观察者型而非决策型（详见 02-hermes-gateway-hooks.md 的完整验证）

---

*持续更新中。Hermes Gateway Hook 验证见 02-hermes-gateway-hooks.md（观察者型，不能注入）。Claude Code Stop Hook 仍是连续 agent 的最优方案。*
