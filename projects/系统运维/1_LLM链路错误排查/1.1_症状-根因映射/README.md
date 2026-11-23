# 1.1 症状 → 根因映射

> 更新：2026-11-18（四渠道同根因事件后建立）

## 核心结论（2026-11-18 事件）

**四个症状同一条根因链**：vllm 上游（10.20.33.188:8000）不稳定 —— 间歇返回空 SSE 流（200 但只有 2 个 chunk、无 finish_reason）+ EngineCore 崩溃（500）。8787 proxy 只是透传，客户端各自把同一故障显示成不同症状。

| 症状（渠道侧） | 客户端显示 | 链路根因 | 证据位置 |
|---|---|---|---|
| hermes qqbot 不回复 | 无回复（间歇性，不是 100% 死） | EmptyStreamError：vllm 200 空流，hermes 重试 3 次全空 → 放弃 | `~/.hermes/logs/errors.log` `stream_diag: Stream exhausted ... http_status=200 bytes=80 chunks=2 finish_reason_seen=False` |
| hermes weixin 不回复 | 同上 | 同上（同一条 8787 链路） | 同上 |
| hermes 显示 "stream 返回空" | `Provider returned an empty stream with no finish_reason` | 同上 | `~/.hermes/logs/errors.log`（当日 1526 次） |
| WorkBuddy 工作到一半"用户已取消" | finalState=cancelled | vllm EngineCore 500 打断流中请求；workbuddy 把流中断记成 cancelled | `~/.workbuddy/logs/daemon.log` `pool:state-change ... finalState:"cancelled"` + 会话 jsonl 末条 `providerData.error={"code":500,"message":"EngineCore encountered an issue..."}` |
| DSH 结束没有 final reason | 无 finish_reason | 同上空流/500（DSH harness baseURL 也指 8787） | `~/.claude-vllm-proxy/proxy.log` `UPSTREAM_ERR status=500 ... EngineCore` |
| （伴生）hermes 上下文压缩失败 | `Context compression LLM returned empty content ... paused for 30 seconds` | 同一空流，压缩调用也走 8787 | `~/.hermes/logs/errors.log` |

## 分层判据（先判哪一层坏了）

1. **客户端层**（渠道没连上 / 配置错）：`~/.hermes/gateway_state.json` 各 platform state ≠ connected，或 channel_directory 里没有该会话。
   - 2026-11-18 事件中 gateway_state 全 connected、qqbot 16:13 还成功发过 147 字回复 → **排除渠道层**。
2. **proxy 层**（8787 挂了 / 上游全挂）：`~/.claude-vllm-proxy/proxy.log` 连续 `HEALTH ... -> active=NONE`，或 8787 端口不通。
   - 事件中 HEALTH 行 active 始终有值、curl 8787 能出 "OK"+finish_reason=stop → **排除 proxy 层**。
3. **上游 vllm 层**（本事件根因）：
   - 空流签名：`http_status=200 bytes≈80 chunks=2 finish_reason_seen=False`
   - 崩溃签名：`UPSTREAM_ERR status=500 ... "EngineCore encountered an issue"`
   - 诱因（用户当日已诊断）：GPU OOM 边缘，VRAM 15.4G/16G 单调增长，KV cache 仅 24%；大请求（bodyBytes≈498KB, msgs=102/224）触发 EngineCore 崩溃。

## 已知次生问题

| 问题 | 状态 | 说明 |
|---|---|---|
| `upstream.override` 残留（内容 `http://100.112.53.47:8010`） | 无害但误导 | proxy.mjs 只在**没有** `upstream.list` 时才读 override；现在 list 存在，override 是死文件。HEALTH 显示 100.112.53.47 两端口常 DOWN，若哪天 list 被删，failover 会打到死上游。建议清空或删除该文件。 |
| 8010 relay 偶发 502 Connection refused | 自愈 | relay 挂了 proxy 15s 内切回 8000；服务器侧 `ninfer-relay` watchdog 会重启（remote-logs 见 `KEEPALIVE restarted relay`） |
| 服务器磁盘冻结 | 监控中 | `~/vllm-monitoring/remote-logs/freeze-verdict.jsonl`，2026-11-15 有 UNREACHABLE 段，11-18 16:28 已 OK |
