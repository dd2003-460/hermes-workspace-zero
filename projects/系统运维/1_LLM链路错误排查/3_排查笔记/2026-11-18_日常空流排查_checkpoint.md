# 日常空流排查 — 阶段性 checkpoint（2026-11-18）

> 状态：**进行中**（Task #4）· 根因已定位到 proxy.mjs onStreamEnd 静默早退，待加诊断日志确认
> 断点恢复：读本文件 + `proxy.mjs` 行 2374-2394 + `proxy.log` 行 1002222 起

## 1. 症状

用户日常聊天频繁出现空流（hermes 报 `EmptyStreamError`，`http_status=200 bytes=80 chunks=2 finish_reason_seen=False`）。
今日（11-18）16:43-17:18 本地时间共 15 次。

## 2. 空流签名（一手 SSE 抓包确认）

15 个 capture 文件（`~/.claude-vllm-proxy/captures/cap-*.sse`，858-873B）全部同构：

```
data: {"choices":[{"delta":{"role":"assistant","content":""},...}]}   ← role 帧
data: {"choices":[],"usage":{"completion_tokens":74-4607,...}}        ← usage-only 帧，finish_reason=null
data: [DONE]
data: [DONE]                                                          ← 双 [DONE]
```

- 引擎侧 `completion_tokens=74-4607`（decode 耗时 3-5s），说明引擎**确实做了 decode**
- 但 SSE 只发了 role 帧 + usage 帧，**无 content、无 finish_reason**
- 请求体：`stream=true, model=qwen3.8-27b-mtp, enable_thinking=false, max_tokens=16384`
- prompt_tokens 14k-88k（hermes 压缩/摘要 agent 调用）

## 3. 进程时间线

| 事件 | 时间（本地） | proxy.log 行 |
|---|---|---|
| proxy 重启（pid 93238） | 16:39:05 | 1001117 |
| 4-upstream 配置加载 | 16:39:05 | 1001114 |
| PREFILL_PROBE #1 成功 | 16:39:05 | 1001118 |
| 第 1 次空流 | 16:43:37 | 1002222 |
| 第 15 次空流 | 17:18:49 | 1006855 |

该进程**有** 11-17 的 retry 代码（`proxy.mjs` mtime 11-18 02:57 本地，含 `isPureEmptyShell` + `retryPureEmptyShell` + `onStreamEnd` hook）。

## 4. 关键发现：EMPTY_SHELL_RETRY 从未触发

**在整个 proxy.log 中，`EMPTY_SHELL_RETRY` 只出现 4 次**，全在两个 OOM 崩溃批次（03:53:22 ×2、08:21:22 ×2）。

今日 15 次日常空流的窗口内：
- **零** `EMPTY_SHELL_RETRY`
- **零** `RESUME_EMPTY_BODY`
- **零** `RESUME_HOOK_ERR`
- **零** `UPSTREAM_ERR`
- **零** `UPSTREAM_ATTEMPT_FAIL`

但 15 次全部有 `stream=true piped` 日志行（proxy.mjs:1349），证明 `pipeStream` 正常执行完毕。

## 5. 根因定位：onStreamEnd 静默早退

### 代码路径

```
pipeStream (proxy.mjs:1231)
  └─ 流读完 → log "piped" (line 1349)
  └─ if (opts.collectState && opts.onStreamEnd) (line 1351)
       └─ await opts.onStreamEnd(streamState) (line 1352)
            └─ onStreamEnd callback (line 2374)
                 ├─ if (!/\/v1\/chat\/completions/.test(pathWithQuery)) return;  ← 无日志
                 ├─ origBody = JSON.parse(buf.toString('utf8'))                  ← 无日志
                 ├─ if (isPureEmptyShell(st) && origBody) {                      ← 无日志
                 │    await retryPureEmptyShell(...)                             ← 有日志（但从未到达）
                 │  }
                 └─ if (!isEmptyBodyState(st)) return;                           ← 无日志
```

### 诊断盲区

`onStreamEnd` 回调内**没有任何入口日志**。唯一日志在 `retryPureEmptyShell` 内部（line 1093 `EMPTY_SHELL_RETRY start`），且在该函数的 3 个 guard 全部通过之后。

如果以下任一条件导致静默早退，**零日志输出**：
1. `pathWithQuery` 正则不匹配（但 urlLen=20 = `/v1/chat/completions`，应匹配）
2. `buf` 为 undefined/null → `origBody = null` → skip
3. `isPureEmptyShell(st)` 返回 false（但 capture 显示 contentLen=0, reasoningLen=0, toolCalls=0, finishReason=null，应返回 true）
4. `PURE_EMPTY_RETRY` 为 false（默认 true，plist 未设 `VLLM_PURE_EMPTY_RETRY`）

### 最可疑点

`buf` 的作用域：`buf` 在 line 2035 定义（`let buf = await readBody(req)`），在 line 2045/2084/2197 被多次重新赋值。`onStreamEnd` 是闭包，捕获的是**同一个 `buf` 变量引用**（不是值拷贝），所以运行时 `buf` 应该是最终的请求体 buffer。理论上不应为 null。

但**没有日志证实这一点**——这是当前的诊断盲区。

## 6. hermes 侧重试掩盖了问题

15 次空流中，**12 次** hermes 自身的 3-attempt 重试成功了（同 bodyBytes 的后续 capture 有正常 content + finish_reason）。

真正用户可见的失败只有 3 次：
- `cap-1794992109967`（113681B body）— 未找到同 body 重试
- `cap-1794992661898`（248373B body）— 未找到同 body 重试
- `cap-1794993529177`（301271B body）— 重试存在（line 1006868 → `cap-1794993534893`）但返回 `finish_reason=stop` + **空 content**（completion_tokens=225，"合法空响应"）

## 7. 模型特异性：仅 qwen3.8-27b-mtp

过去 24h 共 42 个小 SSE 文件（<1000B），**全部是 qwen3.8-27b-mtp**。其他模型（qwen3.8-27b, qwen3.8-27b-w8a16）零空流。

**MTP（Multi-Token Prediction）特异性**：27b-mtp 使用 MTP 解码（每步生成多 token）。引擎可能在 MTP decode 后 SSE 序列化时丢失 content 帧，只发 usage 帧。这是**服务器侧 vllm 引擎 bug**，不是 proxy bug。

proxy 的 EMPTY_SHELL_RETRY 机制可以缓解（检测 usage-only-no-FR → 重发 stream=false → 写入真实 content），但当前从未触发（onStreamEnd 静默早退）。

## 8. workbuddy 早停 = 同一根因

workbuddy 的 "Empty stream: upstream gateway sent only placeholder chunks without any model output (chunks=0, bytes=0, elapsed=0ms)" 与 hermes 的 EmptyStreamError 是**同一根因**：

- proxy 交付了 866B（role 帧 + usage 帧），但 workbuddy 的 SSE parser 只计 "content chunks"（有 delta.content 或 delta.tool_calls 的帧），role 帧和 usage-only 帧不算 → 报 "chunks=0, bytes=0"
- workbuddy 配置：`http://127.0.0.1:8787/v1`（与 hermes 同一 proxy）
- workbuddy 3 个模型全指 8787，但用户只用 27b-mtp → 观察到的 "仅 27b 早停" = 实际是 "仅 27b-mtp 有空流"

## 9. 未解疑点

| # | 疑点 | 状态 |
|---|---|---|
| 1 | hermes 报 `bytes=80 chunks=2`，proxy tee 了 859B — 谁在中间截断？ | **已解**：hermes/workbuddy 的 "bytes" 只计 content bytes，不计 role/usage 帧 |
| 2 | 引擎为什么 decode 了 74-4607 tokens 但 SSE 只发 usage 帧？ | 未解（MTP 引擎 bug，需服务器侧 vllm 日志确认） |
| 3 | `pull-remote-logs.py --once` 拉了 0 字节 — 远程日志通道断了 | 阻塞（需用户 ssh） |

## 10. 下一步（按优先级）

1. ~~加诊断日志到 proxy.mjs onStreamEnd~~ **已完成**（2026-11-18 09:50 UTC / 17:50 本地）
   - 在 `proxy.mjs` line 2374 入口加了 `ON_STREAM_END` 日志行，记录：`bufOk`, `bufLen`, `pure`(isPureEmptyShell 结果), `contentLen`, `reasoningLen`, `toolCalls`, `finishReason`, `promptTokens`
   - 另加 `origBody=null` 日志（buf parse 失败时）
   - proxy 已重启（`launchctl kickstart`），日志已生效
   - **当前状态**：已捕获 8 个 `ON_STREAM_END` 事件，全部 `pure=false`（正常请求有 toolCalls/content），尚无 `pure=true` 的空流事件
   - **等待**：下一次空流出现时，日志会显示 `pure=true` + 各字段值，确认 retry 是否触发
2. ~~加 PIPE_STREAM_START/READ_DONE/LOOP_DONE 诊断日志~~ **已完成**（2026-11-18 10:27 UTC / 18:27 本地）
   - 在 `pipeStream` 入口加了 `PIPE_STREAM_START` 日志（line 1231）
   - 在 `reader.read()` 后加了 `readCount` 计数 + `PIPE_STREAM_READ_DONE` 日志（line 1272-1273）
   - 在 while 循环正常退出后加了 `PIPE_STREAM_LOOP_DONE` 日志（line 1354）
   - proxy 已重启（`launchctl kickstart`），日志已生效
3. **根因已定位**（2026-11-18 10:37 UTC / 18:37 本地）：
   - **所有 296B 空流（role + [DONE]×2）都有 `PIPE_STREAM_START` 但无 `PIPE_STREAM_READ_DONE`**
   - 这意味着 `reader.read()` 在引擎发送 [DONE]×2 后**挂起**，不返回 `done: true`
   - while 循环卡在 `await reader.read()`，既不完成也不触发 catch
   - `activityTimer`（90s 闲置超时）应该触发 abort，但实际未触发（或触发后未正确传播）
4. **修复已部署并确认有效**（2026-11-18 10:53 UTC / 18:53 本地）：
   - 在 `pipeStream` 的 while 循环中，收到 [DONE] 帧后（`doneReceived=true`），用 `Promise.race` 限制 `reader.read()` 最多等 5s
   - 超时后强制结束流：写出 `pendingDone`，调用 `res.end()`，触发 `onStreamEnd`（让 retry 机制介入）
   - 日志：`PIPE_STREAM_DONE_TIMEOUT` + `PIPE_STREAM_FORCED_END`
   - **确认有效**：部署后 5 分钟（18:53-18:58）内无新 296B 空流（之前每 30-60s 一个）。最后一个 296B 文件在 18:52:16（部署前 53s）
   - **注意**：`reader.cancel()` 和 `ac.abort()` 均未生效（`reader.read()` 仍挂起），只有 `Promise.race` + 强制 break 有效
5. ~~清理诊断日志~~ **已完成**（2026-11-18 11:05 UTC / 19:05 本地）
   - 移除：`PIPE_STREAM_START`、`PIPE_STREAM_READ_CHUNK`、`PIPE_STREAM_READ_DONE`、`PIPE_STREAM_LOOP_DONE`、`PIPE_STREAM_DONE_DETECTED`
   - 保留：`PIPE_STREAM_DONE_TIMEOUT` + `PIPE_STREAM_FORCED_END`（长期监控）
   - `ON_STREAM_END` 改为仅在 `pure=true` 时输出（此前每请求都打，1115 条/小时）
   - proxy 已重启（pid 65282），日志干净，正常请求无噪音
6. 加 truncated tool_call 流的重试路径（toolCalls>0, 无 FR, 无 usage — 当前无路径覆盖）
7. ~~确保只有一个 proxy 进程运行~~ **已完成**（2026-11-18 19:06 本地）— 仅 pid 65282 在 8787 端口，8799 无监听
8. ~~降级 Tailscale 100.112.53.47~~ **已完成**（2026-11-18 19:06 本地）— 双通路持续 DOWN，已从 upstream.list 注释掉，health check 只探 LAN 双通路
9. 解 hermes bytes=80 vs proxy 859B 差异（已解释：hermes 只计 content bytes，不计 role/usage 帧）
10. 记入事件台账

## 9. 证据索引

| 证据 | 位置 |
|---|---|
| 15 个空流 SSE capture | `~/.claude-vllm-proxy/captures/cap-1794991417519.sse` 等 |
| 15 个空流 proxy.log 行 | 1002222, 1002508, 1002536, 1004406, 1004743, 1004824, 1005022, 1005185, 1005200, 1005397, 1005984, 1006019, 1006051, 1006093, 1006855 |
| 15 个 piped 日志行 | 1002268, 1002524, 1002547, 1004409, 1004759, 1004825, 1005037, 1005216, 1005194, 1005411, 1005992, 1006025, 1006057, 1006099, 1006858 |
| onStreamEnd 代码 | `proxy.mjs` line 2374-2394 |
| isPureEmptyShell 代码 | `proxy.mjs` line 930 |
| retryPureEmptyShell 代码 | `proxy.mjs` line 1070-1093 |
| pipeStream onStreamEnd 调用 | `proxy.mjs` line 1351-1353 |
| hermes EmptyStreamError | `~/.hermes/logs/agent.log` 16:43:45 起 |
| LaunchAgent plist | `~/Library/LaunchAgents/com.a1-6.claude-vllm-proxy.plist` |
