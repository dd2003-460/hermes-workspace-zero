# 400 "At most 1 image(s) may be provided in one prompt" 修复记录

**origin: ai** · 2026-10-19（更新 2026-10-21 闭环）

## 问题
旧会话（session-fc5fa159，qwen3.8-27b-w8a16 via 8787 上游）反复 400：
`{"message":"At most 1 image(s) may be provided in one prompt","type":"BadRequestError","code":400}`
10-21 复现：DSH 会话（session-fc5fa159 等 8 个 workspace--Users-a1-6-Desktop-workspace-- 会话）再次触发同一 400。

## 根因
1. 上游 vllm（100.112.53.47:8000）本身限制每条 prompt 只允许 1 张图（vllm 侧 limit，非 DSH 配置）
   - 直连复现证据（2026-10-21）：单图 200 正常 / 双图 400 `At most 1 image(s)`，key 有效
2. DSH 把连续多个 `read_image` 工具结果合入同一条 user 消息 → content 数组含 N 张 `data:image/png;base64` 图
3. 捕获包证据：`~/.claude-vllm-proxy/captures/cap-1792392620097.req.json` msg74 含 2 张 1282×725 图（t20/t60 抽帧，像素差 0.01%）
4. 4 个捕获包含 `IMG_BUDGET dropped=1`，时间 10-19 14:50:20/15:03:42/15:05:18/15:15:53——与旧会话 goal_round 重试节奏吻合
5. 10-21 复发触发点：DSH profile vllm baseURL 此前被改回直连 `http://100.112.53.47:8000/v1`，绕过了带 `applyImageBudget` 的本地 8787 代理，补丁对新流量失效。

## 修复
### 补丁层（10-19 已部署，本次确认仍生效）
`~/.claude-vllm-proxy/proxy.mjs` 注入 `applyImageBudget(buf)`：
- 通用透传路径（`/v1/responses`、`/v1/chat/completions`）：遍历 `messages[].content[]`，全局只留最早 1 张 `data:image` URI，其余换 `{type:"text",text:"[图片 #k 已省略：上游单请求仅允许 1 张图]"}`
- `/v1/messages` 路径（Anthropic 格式）：同款处理 `source.type==='base64'` 的 image 块
- 幂等、非法 JSON 安全透传
- 修 bug：`proxy.mjs:729` `const buf` → `let buf`（否则 `Assignment to constant variable`）

### 路由层（10-21 新增，防复发）
- `profiles/web/cordis.patch.yml:11` `baseURL` 由 `http://100.112.53.47:8000/v1` 改回 `http://127.0.0.1:8787/v1`（备份 `cordis.patch.yml.bak-20261021-203900`）
- `~/.claude-vllm-proxy/upstream.override` 由死节点 `http://10.20.33.188:8000` 修回 `http://100.112.53.47:8000`（备份 `upstream.override.bak-20261021-2025`）；代理逻辑：override 文件存在则整行优先，否则 env `VLLM_UPSTREAM`（plist 已设 100.112.53.47:8000）或默认 127.0.0.1:8000
- 生效方式：profile yml 声明式补丁，DSH 启动/新会话读取；已跑会话持旧 baseURL 不变（旧会话需重开）

## 验证
- 单元 6 case 全过（2图→1图/单图透传/跨消息第2张删/纯文本不动/幂等/非法JSON安全）
- 真实流量：`proxy.log` 多次 `IMG_BUDGET dropped=1/2/3/9 (kept 1 of N data-URI images)`，无回归
- **端到端闭环（2026-10-21 完成）**：
  - 直连 `http://100.112.53.47:8000/v1/chat/completions`（真实 vllm key）：单图 200，双图 400 `At most 1 image(s)`（稳定复现，key 有效）
  - 经 `http://127.0.0.1:8787/v1/chat/completions`（同一真实 key）：双图 200，代理日志 `IMG_BUDGET dropped=1 (kept 1)` + `CAPTURE cap-1792586051781` ✅
- 验证脚本：`/tmp/e2e-single.json`（1 图）、`/tmp/e2e-multi.json`（2 图，1×1 png data-URI，model=qwen3.8-27b-w8a16）
- **验证状态**：CLOSED — 修复前双图 400 → 修复后双图 200 对照实验完成

## 回滚点
- `~/.claude-vllm-proxy/fix-20261019/proxy.mjs.bak-20261019-165457`（原始 38059B）
- `workspace/tmp/fix-image-limit/proxy-REVERTED.mjs`（含补丁 40912B，供重放）
- 补丁脚本：`workspace/tmp/fix-image-limit/fix-images.mjs`（支持 `--check` / `--revert`）
- profile 备份：`profiles/web/cordis.patch.yml.bak-20261021-203900`（改回 100.112.53.47 用）
- override 备份：`~/.claude-vllm-proxy/upstream.override.bak-20261021-2025`（值 10.20.33.188:8000，不要回滚）

## 重启方式
代理由 launchd（`com.a16.claude-vllm-proxy`，KeepAlive+ThrottleInterval 5s）监督：**kill 监听进程即自动重启加载新代码**（~1-3s）。不要手动 nohup（会 EADDRINUSE）。

## 防复发检查清单
- [x] DSH profile vllm baseURL = `http://127.0.0.1:8787/v1`（走本地补丁代理）
- [x] `~/.claude-vllm-proxy/upstream.override` = `http://100.112.53.47:8000`（活节点）
- [x] 8787 监听进程存在（launchd 拉起）
- 若再复发：① 确认 baseURL 没被改回直连 ② 确认 override 没指死节点 ③ 抓一次 `~/.claude-vllm-proxy/captures/` 看是否仍有 N>1 图
