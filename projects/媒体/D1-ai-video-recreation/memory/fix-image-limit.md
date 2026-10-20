# 400 "At most 1 image(s) may be provided in one prompt" 修复记录

**origin: ai** · 2026-10-19

## 问题
旧会话（session-fc5fa159，qwen3.8-27b-w8a16 via 8787 上游）反复 400：
`{"message":"At most 1 image(s) may be provided in one prompt","type":"BadRequestError","code":400}`

## 根因
1. 上游 8787（`~/.workbuddy/binaries/node` 桥接，launchd 监督 ppid=1）只允许一条 prompt 带 1 张图
2. DSH 把连续多个 `read_image` 工具结果合入同一条 user 消息 → content 数组含 N 张 `data:image/png;base64` 图
3. 捕获包证据：`~/.claude-vllm-proxy/captures/cap-1792392620097.req.json` msg74 含 2 张 1282×725 图（t20/t60 抽帧，像素差 0.01%）
4. 4 个捕获包含 `IMG_BUDGET dropped=1`，时间 10-19 14:50:20/15:03:42/15:05:18/15:15:53——与旧会话 goal_round 重试节奏吻合

## 修复
`~/.claude-vllm-proxy/proxy.mjs` 注入 `applyImageBudget(buf)`：
- 通用透传路径（`/v1/responses`、`/v1/chat/completions`）：遍历 `messages[].content[]`，全局只留最早 1 张 `data:image` URI，其余换 `{type:"text",text:"[图片 #k 已省略：上游单请求仅允许 1 张图]"}`
- `/v1/messages` 路径（Anthropic 格式）：同款处理 `source.type==='base64'` 的 image 块
- 幂等、非法 JSON 安全透传
- 修 bug：`proxy.mjs:729` `const buf` → `let buf`（否则 `Assignment to constant variable`）

## 验证
- 单元 6 case 全过（2图→1图/单图透传/跨消息第2张删/纯文本不动/幂等/非法JSON安全）
- 真实流量：`proxy.log` 多次 `IMG_BUDGET dropped=1/2/3/9 (kept 1 of N data-URI images)`，无回归
- **401 阻塞端到端直连复现**（8787 对无真实 token 的请求 401），缺一次「修复前 400 → 修复后 200」的对照实验
- 间接证据链完整：补丁加载（kill 重启后新 PID）+ 真实流量经去重 + 无回归
- **验证脚本**：`workspace/tmp/fix-image-limit/e2e.py`（kill 监听者→等 launchd 重启→单图基线+双图复现+日志判定）
- **验证状态**：NEEDS CHECK — 需真实客户端（DSH 自身）触发一次双图场景做对照

## 回滚点
- `~/.claude-vllm-proxy/fix-20261019/proxy.mjs.bak-20261019-165457`（原始 38059B）
- `workspace/tmp/fix-image-limit/proxy-REVERTED.mjs`（含补丁 40912B，供重放）
- 补丁脚本：`workspace/tmp/fix-image-limit/fix-images.mjs`（支持 `--check` / `--revert`）

## 重启方式
代理由 launchd 监督：**kill 监听进程即自动重启加载新代码**（~1-3s）。不要手动 nohup（会 EADDRINUSE）。
