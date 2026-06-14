# Agent Goal 运行原理对比

> 调研时间: 2026-06-12
> 来源: 源码分析 + 文档研究 + 二进制字符串提取

---

## 1. Claude Code 的 Stop Hook 机制

### 1.1 退出条件

Claude Code 是 **turn-based**（非 time-based）:
- 一个 turn = 接收 prompt → 工具调用 → 输出
- Claude 完成 turn 且没有更多动作时，尝试退出 session
- Hooks 在退出时触发

### 1.2 Stop Hook 架构

**配置路径**: `/Users/a1-6/.claude/settings.json`
```json
"hooks": {
  "Stop": [{
    "hooks": [{
      "type": "command",
      "command": "npx claude-code-monitor hook Stop"
    }]
  }]
}
```

**Ralph Loop Stop Hook**: `/Users/a1-6/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/hooks/stop-hook.sh`

关键逻辑:
1. 检查状态文件是否存在（不存在则 exit 0 = 允许退出）
2. 检查 session_id 匹配（不匹配则 exit 0）
3. 检查状态文件数值字段有效性（损坏则 exit 0）
4. 检查 completion promise（匹配则 exit 0 = 允许退出）
5. 检查 max_iterations（达到则 exit 0）
6. 否则输出 `{"decision": "block", "reason": prompt}` → 阻止退出

### 1.3 "非完成即停止"的根因

Claude Code 的退出由 **外部 hook 控制**，而非内部任务完成检测:
- **没有内置的 task completion detection**
- **退出条件是文件状态**（state file 存在性、有效性），而非任务完成度
- Ralph Loop 通过在退出时注入相同 prompt 来阻止退出
- 当 Ralph Loop 状态异常/被删除/max_iterations 达到 → Claude Code 正常退出

### 1.4 二进制字符串发现

从 Claude Code 二进制中提取的关键字符串:
- `preventExit` / `stopPreventingExit` — hook 的阻止退出机制
- `executeStopHooks`, `tengu_pre_stop_hooks_cancelled`, `SessionEnd`
- `hook_error_during_execution` — hook 失败时 session 终止
- `asyncRewake` (exit code 2) — hook 后台运行并在错误时唤醒模型
- `[loop-tick] Stop hook block discarded (turn is yielding to a cron)` — cron 任务可以干扰 hook blocking

---

## 2. OpenAI Codex 的 Goal 机制

### 2.1 终止条件

Codex 的终止是 **externally driven**（外部驱动）:
- 用户验证输出（lint + 测试）
- 用户发送后续指令
- 用户手动干预（commit/revert）

**没有公开的自主完成检测机制**。

### 2.2 "非完成即停止"的根因

Codex 不会"在未完成时停止"——它等待用户指令。问题是:
- **缺乏自主判断"done"的能力**
- **用户必须作为 goal satisfaction checker**
- 每次进展都需要用户 prompt 推进

### 2.3 与 Claude Code 的对比

| 维度 | Claude Code | Codex |
|------|------------|-------|
| 终止驱动 | Hook 控制 | 用户驱动 |
| 自主完成检测 | 无（需外部 hook） | 无 |
| 中断后恢复 | 需要重新 prompt | 需要重新 prompt |
| "done"判断 | Hook + promise | 用户判断 |

---

## 3. Hermes Gateway Hook 机制

### 3.1 Hook 系统架构

Hermes 有三个 Hook 系统:

| 系统 | 注册方式 | 注入能力 |
|------|----------|----------|
| Gateway Hooks | `HOOK.yaml` + `handler.py` | **无** (observer) |
| Plugin Hooks | `ctx.register_hook()` | **有** (pre_llm_call 返回 context) |
| Shell Hooks | `config.yaml` 指向脚本 | **有** (pre_llm_call 可注入) |

### 3.2 为什么 Gateway Hook 是 observer

关键代码 (`gateway/hooks.py` emit 方法):
```python
async def emit(self, event_type, context):
    for fn in handlers:
        result = fn(event_type, context)
        # result 被丢弃，无返回值收集
```

**设计意图**: Gateway Hooks 用于日志、告警、webhook — 不是控制。

### 3.3 Plugin/Shell Hook 是 injectable

Plugin Hooks 的 `pre_llm_call` 返回 context 并注入到 user message:
```python
_pre_results = _invoke_hook("pre_llm_call", ...)
for r in _pre_results:
    if isinstance(r, dict) and r.get("context"):
        _ctx_parts.append(str(r["context"]))
```

Shell Hooks 同理。但它们只能在 **当前 turn 内** 注入上下文，**不能阻止 session 结束**。

### 3.4 "非完成即停止"的根因

Hermes 的 Gateway Hook: **根本不是为控制设计的**，是纯粹的 observer。
Hermes 的 Plugin/Shell Hook: 可以注入上下文但不能控制 session 生命周期。

---

## 4. 三者共同根因分析

### 4.1 共同模式

| Agent | "停止"机制 | 未完成时的行为 |
|-------|-----------|---------------|
| Claude Code | Stop hook 允许退出 | 如果 hook 允许 → 退出 |
| Codex | 用户 prompt | 等待用户指令 → 闲置 |
| Hermes Gateway | 无控制能力 | 发送完 response → 结束 |

**三者都没有内置的 task completion detection**。停止/继续的逻辑完全依赖外部机制。

### 4.2 根因: LLM 是 "turn processor" 而非 "goal executor"

所有三个系统都基于同一模型:
- LLM 处理一个 turn（接收 prompt → 输出 response）
- 没有"未完成任务"的概念
- 每个 turn 是 **self-contained** 的
- 跨 turn 的状态必须通过 **外部文件/memory** 传递

**核心问题**: LLM 本身不知道"我还没完成任务"。当它输出 response 时，它完成了当前的 turn。外部系统决定是否继续。

### 4.3 突破方案

#### 方案 A: Stop Hook（Claude Code 方案）
- 优点: 可以在退出时拦截，注入新 prompt
- 缺点: 需要外部脚本，状态管理复杂，容易出错

#### 方案 B: Loop Wrapper（Shell 脚本循环）
- 优点: 简单可靠，不依赖系统 hooks
- 缺点: 无法跨会话持久化

#### 方案 C: 内置 Completion Detection
- 需要 LLM 层面支持 "I have more work to do" 信号
- 当前没有这样的机制

#### 方案 D: Prompt-based Task Persistence
- 在 system prompt 中声明任务列表和当前状态
- LLM 在每次 turn 开始时检查任务状态
- 优点: 不需要 hook，完全基于 prompt
- 缺点: 依赖 LLM 的 self-awareness

---

## 5. 与 Ralph Loop 的关系

Ralph Loop 利用了 Claude Code 的 Stop Hook 机制实现无限循环。
它的核心发现是: **"阻止退出 = 阻止完成任务判断"**

当前的 Ralph Loop 方案:
- 通过 stop hook 阻止退出
- 注入相同的 prompt → LLM 看到之前输出 → 继续工作
- 状态持久化到文件

改进方向:
- 当前 Ralph Loop 是**单一 prompt 固定注入**
- 理想系统应该允许多任务、优先级、子目标
- 当前的 `<promise>` 是字符串匹配，不是语义判断

---

## 6. 关键文件路径

| 组件 | 路径 |
|------|------|
| Claude Code Stop Hook | `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/hooks/stop-hook.sh` |
| Claude Code Settings | `~/.claude/settings.json` |
| Claude Code Binary | `/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe` |
| Hermes Gateway Hooks | `~/.hermes/hermes-agent/gateway/hooks.py` |
| Hermes Plugin Hooks | `~/.hermes/hermes-agent/agent/plugin_hooks.py` |
| Hermes Shell Hooks | `~/.hermes/hermes-agent/agent/shell_hooks.py` |
