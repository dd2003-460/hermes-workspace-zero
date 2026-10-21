# think-split 最小方案（2026-10-19，think-translate）

## 根因
vLLM 未开 `--reasoning-parser` → Qwen3 thinking 以 `<think>...</think>` 标签文本混在 `delta.content` 里。
DSH openai-completions 解析器只认 `delta.reasoning_content`/`reasoning`/`reasoning_text` 字段才建 thinking 块
（`/tmp/dsh-llm-index.js` line 362168 `OPENAI_COMPLETIONS_REASONING_FIELDS`）→ 无 thinking 块 → 前端无法折叠，孤立 `</think>` 当正文显示。

## 改动（仅 /Users/a1-6/.claude-vllm-proxy/proxy.mjs）
1. 新增模块（`// ---------- HTTP 服务 ----------` 之前，约 line 370-550）：
   - `THINK_OPEN/THINK_CLOSE` 常量；`makeThinkSplitter({contentHook, reasoningHook})` 增量状态机：
     in_think 时 content→reasoning 分片，out 时透传；支持孤立 `</think>` 自动补开；
     标签跨 chunk 截断用 `prefixOverlap` hold 末尾字节。
   - `prepareChatCompletionsFrame(frame)`：解析 `chat.completion.chunk` 帧，清空 `delta.content`，
     返回 `{needsSplit, pushContent, baseFrame}`（tool_calls/role/usage 帧不动）。
   - `frameWithContent/baseFrame,s` / `frameWithReasoning(baseFrame,s)`：回调构造新 SSE 帧。
   - 翻译 hook：`THINK_TRANSLATE_CMD` 环境变量 → 常驻翻译子进程，stdin JSONL 请求 `{"id","part"}` / stdout `id:out` 行响应（10s 超时兜底原样回传）。默认未设置 = 纯转换，不翻译。
2. `pipeStream` 帧循环加 `opts.frameHook(frame)`：非 null 返回写 res+tee（tee 保留原始字节）；null = 抑制原帧。
3. HTTP 路由：`/v1/chat/completions` 的 SSE 分支创建 splitter，frameHook 里 `split.push(content)`，
   回调直接 `res.write` 新帧；流结束 `split.flush()` + drain 翻译队列（≤30s guard）后放行 `[DONE]`。
   `/v1/messages`（Anthropic 格式）与其他路径零改动。

## 效果
- DSH 收到 `delta.reasoning_content` → 建 thinking 块（signature=reasoning_content）→ **可折叠**。
- DSH 下一轮 convertMessages 把 thinking 写回 assistant 消息的 `reasoning_content` 字段回传（vLLM 忽略未知字段，无害，保持上下文完整）。
- 正文不再混 `</think>` 等标签残留。

## 回滚
`launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.a16.claude-vllm-proxy.plist`
`cp ~/.claude-vllm-proxy/proxy.mjs.bak-$(date +%Y%m%d) ~/.claude-vllm-proxy/proxy.mjs && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.a16.claude-vllm-proxy.plist`
（部署前先备份 `proxy.mjs.bak-<date>`。无翻译层时改动纯增量，删掉 think-split 模块 + frameHook 即还原。）

## 验证记录（2026-10-19）
- 单测：状态机 7 组语义 + 26 个标签跨 chunk 边界 case 全过（THINK_OPEN 7 字符/THINK_CLOSE 8 字符修正后）。
- 端到端：mock vLLM（8788，标签拆在 chunk 边界）→ 改后 proxy（PROXY_PORT=8799）→ curl：
  content 帧 `Let me ` + `2.`，reasoning 帧 ` think: 1+1=2. Then` + ` the answer is `，[DONE] 正常 → **PASS**。
  DSH 解析器对 `delta.reasoning_content` 会建 thinking 块（signature=reasoning_content）→ 前端可折叠。
- 已部署：launchd kickstart，pid 25833，8787 health ok，日志正常（18:27:55 CAPTURE 正常）。

## 待决
翻译层本地实现（见 /tmp/think-translation-plan.md）；远程 vLLM 若重启可加 `--reasoning-parser qwen3` 根治（不改 proxy 也行，但 proxy 层已覆盖）。
