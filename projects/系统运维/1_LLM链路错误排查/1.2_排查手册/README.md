# 1.2 排查手册（分层取证）

> 更新：2026-11-18

## 关键日志路径

| 层 | 路径 | 看什么 |
|---|---|---|
| hermes 渠道 | `~/.hermes/logs/gateway.log` | 入站消息、`[QQBot] Sending response`（渠道是否真发出过回复） |
| hermes 错误 | `~/.hermes/logs/errors.log` | `stream_diag`（空流签名）、`API call failed after 3 retries`、compression 失败 |
| hermes 运行 | `~/.hermes/logs/agent.log` | `response ready: platform=...` |
| hermes 状态 | `~/.hermes/gateway_state.json` | 各 platform state / needs_attention |
| proxy | `~/.claude-vllm-proxy/proxy.log` | `HEALTH`（active 上游）、`UPSTREAM_ERR`（500/502）、`EMPTY_SHELL_RETRY` |
| proxy 看门 | `~/.claude-vllm-proxy/proxy-watchdog.log` | 8787 进程存活（每 2min code=200） |
| WorkBuddy | `~/.workbuddy/logs/daemon.log` | `finalState:"cancelled"`、sidecar spawn 参数 |
| WorkBuddy 会话 | `~/.workbuddy/projects/<proj>/<uuid>.jsonl` | 末条 assistant 的 `providerData.error`（真错误码在这） |
| DSH | `~/Library/Application Support/dsh-desktop/harness/`（profiles + 会话日志 zstd） | baseURL 指向；bridge 60111 日志。既有 SOP：`~/.claude-vllm-proxy/DSH_BRIDGE_SOP.md` |
| 上游服务器 | `~/vllm-monitoring/remote-logs/`（`python3 pull-remote-logs.py --once` 增量拉） | watchdog / relay / freeze-verdict |

## 排查流程（按层从上到下，先排除便宜的）

```
症状：某客户端"没回复/取消/无 final reason"
│
├─ 1. 渠道层：gateway_state.json 该 platform connected? channel_directory 有该会话?
│     └─ 否 → 渠道连接问题（重启 gateway / 重新授权）
│
├─ 2. proxy 层：curl -s http://127.0.0.1:8787/v1/models 通?
│     proxy.log 最近 HEALTH 行 active= 有值?
│     └─ 不通/active=NONE → 8787 或全部上游挂（查 watchdog log / upstream.list）
│
├─ 3. 上游层（最常见根因）：
│     grep 'UPSTREAM_ERR' proxy.log | tail      # 500=EngineCore 崩, 502=relay 拒连
│     grep 'EMPTY_SHELL_RETRY' proxy.log | tail # 空流重试轨迹
│     grep 'stream_diag' ~/.hermes/logs/errors.log | tail  # 空流签名 bytes/chunks/finish_reason
│     └─ 有 → vllm 侧问题：
│         a. 拉服务器日志 python3 ~/vllm-monitoring/pull-remote-logs.py --once
│         b. 查 freeze-verdict.jsonl 末尾（磁盘冻结=UNREACHABLE）
│         c. 大请求（>400KB body）+ VRAM 高位 → OOM 边缘，见 §修复动作
│
└─ 4. 客户端层：客户端自己的会话日志末条错误
      WorkBuddy: 会话 jsonl 末条 providerData.error（"cancelled" 常是流被 500 打断的表象）
      DSH: harness 会话日志（zstd）+ bridge 日志
```

## 常用命令

```bash
# 8787 端到端冒烟（应返回 OK + finish_reason=stop）
curl -s http://127.0.0.1:8787/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.8-27b-mtp","messages":[{"role":"user","content":"说OK"}],"max_tokens":8}'

# 上游直连健康
curl -s -o /dev/null -w '%{http_code}\n' http://10.20.33.188:8000/v1/models

# 当日空流/崩溃计数
grep -c 'stream_diag' ~/.hermes/logs/errors.log
grep -c 'UPSTREAM_ERR status=500' ~/.claude-vllm-proxy/proxy.log

# 拉服务器侧日志
python3 ~/vllm-monitoring/pull-remote-logs.py --once
tail -5 ~/vllm-monitoring/remote-logs/freeze-verdict.jsonl
```

## 修复动作（按根因）

| 根因 | 动作 | 权限 |
|---|---|---|
| vllm EngineCore 崩（500） | 服务器侧重启 vllm；长期=降 `--gpu-memory-utilization` / 限 `max_num_seqs`，避开 OOM 边缘（VRAM 15.4G/16G 单调增长是前兆） | 需服务器（ssh server） |
| 空流（200 无 finish_reason） | 多为同一 OOM 边缘的轻症状；同上。proxy 已有 EMPTY_SHELL_RETRY（4 次跨上游）兜底，但上游全空时只能失败 | 需服务器 |
| relay 8010 拒连 | 自愈（15s failover）；反复出现查服务器 `ninfer-relay` watchdog | 自愈 |
| 磁盘冻结 | freeze-verdict 持续 UNREACHABLE → 服务器重启 | 需服务器 |
| `upstream.override` 残留 | 清空/删除（有 upstream.list 时它是死文件，但会误导排查） | 本机 |
| hermes 渠道掉线 | `~/.hermes` gateway 重启（注意会短暂断 QQ） | 本机 |

## 注意

- proxy.log 很大（百万行级），grep 时带 `tail`/`-c` 限量，别整文件读进上下文。
- 8787 是**唯一出口**：hermes 所有 provider、WorkBuddy custom-local、DSH harness 全指它。8787 一抖全渠道同抖 —— 多渠道同时报障时优先怀疑 8787 上游，而不是各渠道分别坏。
