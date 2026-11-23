# 2 事件台账

每次定位到根因后记一条。格式：`## YYYY-MM-DD 症状摘要` + 根因 / 动作 / 证据。

---

## 2026-11-18 四渠道同抖（qqbot 不回复 / workbuddy 用户已取消 / 微信·QQ stream 空 / dsh 无 final reason）

**根因**：vllm 上游 10.20.33.188:8000 不稳定 ——
1. 间歇空 SSE 流：200 但 bytes≈80 / chunks=2 / 无 finish_reason（hermes 侧当日 1526× EmptyStreamError，全在 8787）
2. EngineCore 崩溃 500：03:53:22 ×4、08:21:22 ×4（proxy.log `UPSTREAM_ERR status=500 ... EngineCore encountered an issue`；08:21 批次前有 bodyBytes=498,027 / msgs=102/224 的大请求）

诱因：GPU OOM 边缘（用户当日已诊断：VRAM 15.4G/16G 单调增长、KV cache 仅 24%）。

**症状映射**：
- qqbot/weixin 不回复 = 空流 ×3 重试全败（qqbot 间歇正常：16:13:51 成功发 147 字 → 非渠道问题）
- workbuddy "用户已取消" = 流中 500 → finalState=cancelled（会话 jsonl 末条 `providerData.error.code=500 isRetryable=false`）
- dsh 无 final reason = 同上空流/500（harness baseURL 指 8787）

**动作**：
- [x] 建立本 project + SOP（`sop/llm-chain-troubleshooting.md`，挂 SOP-INDEX §6）
- [x] 移除陈旧 HALT 文件 `~/.hermes/.stage-gate/HALT`（11-17 21:20 遗留，导致 stop_hook 全天放行停止、自动续推失效）
- [ ] 服务器侧：重启 vllm 或降 gpu-memory-utilization / 限 max_num_seqs（需 ssh server，用户操作）
- [ ] 清空 `~/.claude-vllm-proxy/upstream.override` 残留（死文件，防误导）

**证据**：
- `~/.hermes/logs/errors.log`：`stream_diag: Stream exhausted on attempt 3/3 ... http_status=200 bytes=80 chunks=2 finish_reason_seen=False`
- `~/.claude-vllm-proxy/proxy.log` L998160-998180（08:21 崩溃批次）
- `~/.workbuddy/projects/Users-a1-6-WorkBuddy-2026-10-18-21-08-21/94341de7-43d3-4fdc-979a-20fb384f6900.jsonl` 末条
- `~/.hermes/.stage-gate/progress.log`：11-18 全天 `stop HALT 文件存在→放行停止`

---

## 2026-11-18 日常空流根因定位 + 修复（MTP 引擎 reader.read() 挂起）

**根因**：vLLM MTP 引擎（qwen3.8-27b-mtp, vllm-1.5.3-tp4）在发送 role 帧 + [DONE]×2 后，HTTP 连接不关闭 —— proxy 侧 `reader.read()` 永远不返回 `{done: true}`，while 循环卡死。客户端（hermes/workbuddy）只收到 role 帧，报 "empty stream" / "chunks=0, bytes=0"。

**与 OOM 崩溃的区别**：OOM 崩溃是引擎 500 错误（EngineCore crash），本问题是引擎 200 但连接挂起。两者独立。

**症状**：
- 296B SSE（role + [DONE]×2，无 usage、无 finish_reason、无 tool_calls）
- 修复前每 30-60s 出现一次
- 仅 qwen3.8-27b-mtp 模型（MTP 解码特异性）
- workbuddy 早停 = 同一根因（workbuddy SSE parser 只计 content chunks，role 帧不算 → "chunks=0, bytes=0"）

**修复**（proxy.mjs pipeStream while 循环）：
- 收到 [DONE] 帧后（`doneReceived=true`），用 `Promise.race([reader.read(), timeout(5s)])` 限制等待
- 超时后强制结束流：写出 pendingDone、`res.end()`、触发 `onStreamEnd`（让 retry 机制介入）
- 日志：`PIPE_STREAM_DONE_TIMEOUT` + `PIPE_STREAM_FORCED_END`（长期监控）
- **注意**：`reader.cancel()` 和 `ac.abort()` 均无法解除挂起的 `reader.read()`，只有 Promise.race（放弃挂起的 promise 并 break 出循环）有效

**确认有效**：
- 部署前：296B 空流每 30-60s 一个
- 部署后（18:53 本地）：5 分钟内零新 296B 文件
- 19:04:48 出现 1 个 296B（引擎返回空但正常关闭连接，非挂起），542ms 完成，onStreamEnd 正常触发

**附带清理**：
- 移除诊断日志：PIPE_STREAM_START / READ_CHUNK / READ_DONE / LOOP_DONE / DONE_DETECTED
- ON_STREAM_END 改为仅 pure=true 时输出（此前每请求都打，~1100 条/小时）
- Tailscale 100.112.53.47 双通路持续 DOWN，从 upstream.list 注释掉（减少无效 health check）

**证据**：
- 15 个 296B SSE capture：`~/.claude-vllm-proxy/captures/cap-1794991417519.sse` 等
- 诊断日志对比：所有 296B 有 PIPE_STREAM_START 但无 PIPE_STREAM_READ_DONE
- 修复后 proxy.log：零 PIPE_STREAM_DONE_TIMEOUT（无新挂起）
- checkpoint：`3_排查笔记/2026-11-18_日常空流排查_checkpoint.md`

**待办**：
- [ ] 服务器侧：确认 vLLM MTP 引擎 bug（需 ssh server 查 vllm 日志）
- [ ] 加 truncated tool_call 流的重试路径（toolCalls>0, 无 FR, 无 usage）
