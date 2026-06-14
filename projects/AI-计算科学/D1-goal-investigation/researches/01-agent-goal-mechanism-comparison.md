# Agent Goal 运行原理对比：Claude Code vs Codex vs Hermes

> 调研时间: 2026-06-12 (Iteration 27)
> 来源: 源码分析 + 文档研究 + 二进制字符串提取

---

## 1. 三者停止条件对比

### Claude Code

| 条件 | 行为 | 是否可被覆盖 |
|------|------|-------------|
| Stop Hook exit 0 | 允许退出 | 否（hook 控制） |
| 状态文件被删除 | 允许退出 | 是（手动删除） |
| Completion Promise 匹配 | 允许退出 | 是（匹配字符串） |
| Max iterations 达到 | 允许退出 | 是（改 max_iterations） |
| Session ID 不匹配 | 允许退出 | 否（自动） |
| 状态文件损坏 | 允许退出 | 否（自动清理） |
| Ctrl+C / SIGTERM | 强制退出 | 否 |
| Hook 执行失败 | 退出 + error | 否 |

**核心发现**: Claude Code 的退出由 **Stop Hook 控制**。如果 hook 决定 block → 注入 prompt → 继续；如果 hook 允许退出（exit 0）→ session 结束。

### Codex (OpenAI)

| 条件 | 行为 | 是否可被覆盖 |
|------|------|-------------|
| 用户发出新指令 | 继续执行 | 是（用户控制） |
| 用户发出停止指令 | 退出 | 是（用户控制） |
| 任务完成 | 等待用户验证 | 否（无自主完成检测） |

**核心发现**: Codex 没有自主完成检测。终止完全由用户控制。

### Hermes

| 系统 | 退出行为 | 注入能力 |
|------|----------|----------|
| Gateway Hook | 无控制能力 | 无（observer） |
| Plugin Hook (pre_llm_call) | 可注入 context | 有（但不能阻止退出） |
| Shell Hook (pre_llm_call) | 可注入 context | 有（但不能阻止退出） |

**核心发现**: Hermes Gateway Hook 是纯 observer，Plugin/Shell Hook 可注入但不能控制 session 生命周期。

---

## 1.5 Claude Code 的 API 层停止机制（核心发现）

**用户指出**: "你明明有 goal，而且你没完成就停下来了，这是为什么？"

### Claude Code 的真实停止路径

```
用户给 Claude Code 一个 goal/prompt
       ↓
Claude Code 调用 Anthropic API (messages endpoint)
       ↓
API 返回 response，包含 stop_reason:
  - "end_turn"     → 模型认为它完成了当前 turn
  - "tool_use"     → 模型调用了工具，等待结果
  - "max_tokens"   → 达到 max_tokens 限制
  - "stop_sequence" → 匹配了 stop sequence
       ↓
Claude Code 根据 stop_reason 决定:
  - tool_use → 执行工具 → 把结果喂回 API → 继续
  - end_turn → 尝试退出 session → Stop hook 触发
  - max_tokens → 可能继续（有剩余 tokens）或退出
       ↓
Stop hook 拦截退出:
  - hook 输出 {"decision":"block", ...} → 注入 prompt → 继续
  - hook 输出 {"decision":"continue"} 或 exit 0 → session 结束
```

### 为什么"有 goal 但不完成就停"

**根因: `stop_reason: "end_turn"` ≠ "goal 完成"**

`stop_reason: "end_turn"` 是 API 层面的信号，意思是"模型完成了这一轮的输出"。它**不代表**:
1. 用户的 goal 完成了
2. 任务完成了
3. 甚至不一定是模型自己认为的任务完成了

**具体机制**:
1. Claude Code 调用 Anthropic API 时，API 会返回 `stop_reason`
2. 当 `stop_reason` 从 `tool_use` 变为 `end_turn`（即模型开始输出文本而不是调用工具），Claude Code 认为"没有更多工具需要调用"
3. 此时 Claude Code 尝试退出 session
4. 如果没有外部 hook 阻止（Ralph Loop），session 结束
5. **即使 goal 未完成**

### 为什么模型会输出 `end_turn`

模型输出 `end_turn` 的条件:
1. 模型认为当前输入已经处理完毕（输出了回复 + 所有工具调用）
2. **模型可能错误地判断"我已经回答完了"** — 尤其是当 goal 复杂、需要多轮协作时
3. **max_tokens 限制** — 如果单轮 max_tokens 较小，模型可能被截断

### 这解释了 Claude Code 的行为

| 行为 | 原因 |
|------|------|
| "没完成就停" | API 返回 `stop_reason: end_turn`，Claude Code 认为 turn 结束了 |
| "问用户是否继续" | Claude Code 在 turn 结束时没有更多 tool_use，所以停下来 |
| "你让我自己改 prompt" | Claude Code 无法自主延长 turn — 它只能等用户发新消息 |
| "多轮后遗忘" | 上下文窗口满了，旧内容被压缩/总结 |

### 对比: Ralph Loop 如何解决

Ralph Loop 的 stop hook 在 Claude Code 尝试退出时介入:
1. 拦截 exit 尝试
2. 注入相同的 prompt（让 Claude Code 看到自己之前的输出）
3. Claude Code 在下次 turn 中看到之前的上下文，继续工作
4. 直到 `completion_promise` 被满足，hook 才放行

**结论**: Claude Code 的"非完成即停止"不是 bug，是 **API 设计的必然结果**。`stop_reason` 是 turn-level 的信号，不是 goal-level 的信号。

---

## 2. "非完成即停止"的共同根因

### 根因 1: LLM 是 Turn Processor，不是 Goal Executor

所有三个系统都基于同一模型:
- LLM 处理一个 **turn**（接收 prompt → 输出 response）
- 每个 turn 是 **self-contained** 的
- LLM 本身不知道"我还没完成任务"
- 跨 turn 状态通过外部文件/memory 传递

### 根因 2: 没有内置的 Completion Detection

| Agent | Completion Detection | 如何判断"done" |
|-------|---------------------|---------------|
| Claude Code | 无 | Hook 检查 completion promise 字符串 |
| Codex | 无 | 用户判断 |
| Hermes | 无 | 发送完 response → 结束 |

### 根因 3: 退出条件由外部决定

- Claude Code: Stop Hook 文件状态
- Codex: 用户指令
- Hermes: 无（自动结束）

**三者都没有内置的 task completion detection**。

---

## 3. 突破方案对比

### 方案 A: Stop Hook（Claude Code）

**原理**: 在 session 退出时拦截，注入新 prompt

**优点**: 
- 可以在退出时阻止
- 不修改核心代码

**缺点**:
- 需要外部脚本
- 状态管理复杂
- 容易出错（文件损坏、session_id 不匹配等）

### 方案 B: Prompt-based Task Persistence

**原理**: 在 system prompt 中声明任务列表，LLM 自行维护状态

**优点**:
- 不需要 hook
- 完全基于 prompt

**缺点**:
- 依赖 LLM 的 self-awareness
- 可能遗忘任务（上下文窗口限制）

### 方案 C: 内置 Completion Detection

**原理**: LLM 层面支持 "I have more work to do" 信号

**优点**:
- 最原生
- 最可靠

**缺点**:
- 需要 LLM + framework 同时修改

### 方案 D: Loop Wrapper

**原理**: Shell 脚本循环启动 Claude Code

**优点**: 简单可靠

**缺点**: 无法跨会话持久化，每次启动都是新 session

---

## 4. Ralph Loop 的方案与局限

Ralph Loop 利用了 Claude Code 的 Stop Hook 实现无限循环。

**核心机制**:
```
1. Stop hook 检查状态文件存在性
2. 检查 session_id 匹配
3. 检查 completion promise
4. 检查 max iterations
5. 全部通过后 → block + 注入 prompt
```

**局限**:
1. 单一 prompt（不能动态调整）
2. 无优先级/子目标
3. 状态文件管理复杂
4. session_id 隔离导致跨会话不连续
5. `<promise>` 是字符串匹配，不是语义理解

**改进方向**:
- 多任务队列（task queue）
- 优先级系统
- 语义级 completion detection（不是字符串匹配）
- 跨会话状态继承

---

## 5. 关键文件路径

| 系统 | 路径 |
|------|------|
| Claude Code Stop Hook | `~/.claude/plugins/.../ralph-loop/hooks/stop-hook.sh` |
| Claude Code Settings | `~/.claude/settings.json` |
| Hermes Gateway Hooks | `~/.hermes/hermes-agent/gateway/hooks.py` |
| Hermes Plugin Hooks | `~/.hermes/hermes-agent/agent/plugin_hooks.py` |
| Hermes Shell Hooks | `~/.hermes/hermes-agent/agent/shell_hooks.py` |
