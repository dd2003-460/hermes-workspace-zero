# 02 — Hermes Gateway Hooks 系统发现（agent:end 事件钩子）

**日期**: 2026-05-13
**来源**: 通过 `hermestool` (hermes-tools v0.118.0) 逆向发现的 Hermes 内置 hooks 系统
**参考**: Claude Code 01-stop-hook-analysis.md 作为对照

---

## 核心发现

Hermes 内置了一个 **Gateway Hooks 系统**，在 agent 运行时通过 WebSocket JSON-RPC 暴露事件。这证明我之前的判断（"Hermes 没有 hook 机制"）是**错的**。

### Gateway Hooks 的触发时机

**`agent:end`** — agent 完成一轮推理并发送响应后触发。

这是**最关键的发现**：agent 在发送完响应后、进入等待状态前，会发出 `agent:end` 事件。这意味着：
- 外部 observer 可以在 agent 完成后、用户回复前截取
- 可以做结果检查、循环控制、自动注入新 prompt

这与 Claude Code 的 Stop Hook 机制类似但**更灵活**——不是拦截退出，而是拦截"完成推理后"的间隙。

### 如何注册 hook

通过 `hermestool` 的 `register_gateway_hook` 注册。这是一个标准的 `json` 消息，发送到 Hermes 的 JSON-RPC 接口。

**置信度**: 中 — 找到了注册函数和事件名，但没有实际运行验证回调是否正确触发

---

## 与 Claude Code 机制对比

|| 维度 | Hermes Gateway Hook | Claude Code Stop Hook |
|------|----------|-----------|
| **事件类型** | `agent:end`, `agent:begin` | `Stop` (单一事件) |
| **触发时机** | agent 完成推理后 | agent 尝试退出时 |
| **注入能力** | 未知（注册回调后如何注入需验证） | 通过 `{decision: "block", reason: "..."}` 直接注入 |
| **注册方式** | `json` 消息注册到 Hermes gateway | Shell 脚本通过 stdin/stdout 通信 |
| **同一进程** | 外部 WebSocket observer，非同进程 | 同进程内 |
| **通用性** | Hermes 专属 | Claude Code 专属 |

**关键差距**: Claude Code 的 Stop Hook 能**阻断退出并注入新内容**（决策型）。Hermes 的 `agent:end` 目前只知道**可以监听**，不知道能否注入新 prompt。这是必须验证的点。

---

## 与 D1-stop-hook-analysis 的错误纠正

| 之前的说法 | 新发现 | 纠正 |
|------|------|------|
| "Hermes 没有 hook 机制" | `agent:end` + `register_gateway_hook` 存在 | **错了**。Hermes 有事件系统，只是通过 WebSocket 暴露 |
| "Hermes 只有 --continue 调用模式" | 有注册 gateway hook 的函数 | **错了**。可以外部观察 agent 生命周期 |
| "Hermes 没有 agent:complete 事件" | `agent:end` 本质就是 agent complete 事件 | **错了。时机不同：agent:end 在响应完成后，不是退出时** |

---

## 机制验证（2026-05-25 迭代 95 补充）

**实际验证结果**：`register_gateway_hook` 不存在于 Hermes 源码中。原笔记的发现是基于对 `hermestool` API 的误读。

`agent:end` 在 `run.py` 中被 emit 的代码（实际阅读）：
```python
await self.hooks.emit("agent:end", {
    **hook_ctx,
    "response": (response or "")[:500],
})
```

钩子注册机制在 `hooks.py`：handlers 从 `~/.hermes/hooks/` 目录发现，每个 hook 目录包含 `HOOK.yaml`（元数据）+ `handler.py`（`async def handle(event_type, context)`）。

**关键区别**：
- `hooks.emit()` 是 **单向广播**：数据从 agent → handler，handler 无返回值
- Claude Code Stop Hook 是 **双向决策**：handler 输出 `{decision:"block", reason:"..."}` 可以控制 agent

所以 Hermes Gateway Hook 是**观察者模式**，不是决策者模式。

---

## 与 Claude Code Stop Hook 的架构对比（已验证）

| 维度 | Hermes Gateway Hook | Claude Code Stop Hook |
|------|----------|-----------|
| **事件类型** | `agent:end`, `agent:start`, `agent:step` | `Stop` (单一事件) |
| **触发时机** | agent 完成推理后 | agent 尝试退出时 |
| **方向** | **观察者型**：agent → handler (单向) | **决策型**：handler → agent (双向) |
| **注入能力** | 不能注入新 prompt | 通过 `{decision:"block", reason:"..."}` 注入 |
| **阻断能力** | 不能阻断执行 | `decision:"block"` 阻止退出 |
| **注册方式** | `~/.hermes/hooks/*/` (HOOK.yaml + handler.py) | Shell 脚本通过 stdin/stdout 通信 |
| **handler 返回值** | 忽略，错误被 catch | 解析 JSON 决策 |

---

## Hermes 连续 agent 的可行路径（更新）

### 路径 1：bash loop wrapper（推荐）
- 已在 `scripts/ralph` 中实现
- 每次独立进程，`hermes chat --continue session` 恢复会话
- 优点：独立于 Hermes 内部机制
- 缺点：每次进程启动开销

### 路径 2：外部 WebSocket observer + 新 session
- 监听 `agent:end` → 获取 response 和 session 信息
- 检测到完成 → 发送新消息触发新一轮
- **可行但需要额外平台**（QQ/Telegram 等 messaging platform）
- 需要 QQ/Telegram 消息发送权限（当前 QQ Bot token 报错）

### 路径 3：Hermes CLI 扩展
- 给 Hermes 添加 `--loop` 模式
- **工作量最大，不推荐**

---

## 仍然有用的发现

1. **`agent:step` 事件**：tool-calling 循环的每一步都触发，可以用来做推理过程监控（但无法注入）
2. **`session:start` / `session:end`**：可以感知会话生命周期
3. **hook 处理器支持 async**：可以在 `~/.hermes/hooks/` 中添加 handler，实现 agent 完成后自动执行操作（如记录日志、触发外部 API）

---

## 错误纠正

| 之前的说法 | 验证结果 | 纠正 |
|------|------|------|
| "`register_gateway_hook` 存在" | 不存在于源码中 | **错了**。hook 系统是 `~/.hermes/hooks/` 目录发现模式 |
| "agent:end 可能可以注入" | emit 是单向广播 | **错了**。不能注入，是观察者模式 |
| "这是最优路径" | 架构不支持 | **错了**。bash loop wrapper 仍是 Hermes 上的可行方案 |

---

## 对 ralph-loop 的启示

当前 ralph-loop 使用 Claude Code Stop Hook（决策型），这是**比 Hermes Gateway Hook 更好的方案**：
- 在同进程内拦截
- 可以控制退出行为
- 已经稳定工作

Hermes Gateway Hook 可以作为**增强**：在 `~/.hermes/hooks/` 中添加 handler，利用 `agent:step` 做推理过程监控，或 `agent:end` 触发外部通知（如发送 QQ 消息 "AI 已完成一轮"）。但这不改变循环控制机制。

---

*验证完成。agent:end hook 存在但不能注入新 prompt，Hermes 连续 agent 的最优路径仍是 bash loop wrapper。Claude Code Stop Hook 方案优于 Hermes Gateway Hook。*
