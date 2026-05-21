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

## 待验证的关键问题

1. **`agent:end` 回调能否注入新 prompt？**
   - Claude Code Stop Hook 通过 stdout 输出 `{decision:"block"}` 实现
   - Hermes Gateway Hook 的注册机制不同，需要发现注入新 prompt 的方法
   - 可能需要注册到 JSON-RPC 的请求/响应流中

2. **`agent:begin` 是否存在？**
   - 只知道 `agent:end`，如果还有 `agent:begin`，可以构建完整的 agent 生命周期追踪
   - 这意味着可以知道"agent 什么时候开始跑一轮"

3. **hook 注册的生命周期**
   - hook 注册后是持久化的还是 session 级别的？
   - 是否支持跨会话恢复（类似 Claude Code 的 state 文件机制）

4. **如何实际触发 hook**
   - 目前只找到了注册函数，没有成功运行验证
   - 需要实际触发 agent:end 并观察回调

---

## 对连续 agent 的意义

如果 `agent:end` hook 能注入新 prompt，那么：
- **Hermes 自己的 loop 机制就通了**：不需要 bash loop wrapper
- 可以实现比 bash loop 更优雅的循环：同会话、无启动开销、无进程隔离问题
- 与 Claude Code Stop Hook 的架构差异在于：
  - Claude Code: 拦截退出 → 阻止退出 → 注入 → 继续
  - Hermes: 完成推理 → 拦截 → 注入 → 继续（agent 本来就在跑）

**这是 Hermes 连续 agent 的最优路径，需要优先验证。**

---

*下一步：尝试实际调用 `register_gateway_hook` 并用 `agent:end` 事件验证回调能否触发。*
