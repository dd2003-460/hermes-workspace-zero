# SOP：LLM 链路错误排查（vllm → 8787 proxy → hermes/WorkBuddy/DSH）

> 创建：2026-11-18 · 起因：四渠道同抖事件（qqbot 不回复 / workbuddy 用户已取消 / 微信·QQ stream 空 / dsh 无 final reason）
> 配套 project：`projects/系统运维/1_LLM链路错误排查/`（症状映射表 + 排查手册 + 事件台账）

## 何时用

任何客户端（hermes 渠道 / WorkBuddy / DSH / Claude Code）出现：不回复、stream 空、无 finish_reason、工作到一半"用户已取消"、500/502。

## 第一原则

**8787 是唯一出口**。hermes 所有 provider、WorkBuddy custom-local、DSH harness 全指 `http://127.0.0.1:8787/v1`。
多渠道**同时**报障 → 先怀疑 8787 上游（vllm），不要按渠道分别排查。

## 流程（4 层，从上到下，先排除便宜的）

1. **渠道层**：`~/.hermes/gateway_state.json` platform=connected？`channel_directory.json` 有会话？
2. **proxy 层**：`curl -s http://127.0.0.1:8787/v1/models` 通？proxy.log 最近 `HEALTH` 行 `active=` 有值？
3. **上游层（最常见根因）**：
   - `grep 'UPSTREAM_ERR' ~/.claude-vllm-proxy/proxy.log | tail`（500=EngineCore 崩 / 502=relay 拒连）
   - `grep 'stream_diag' ~/.hermes/logs/errors.log | tail`（空流签名：`http_status=200 bytes≈80 chunks=2 finish_reason_seen=False`）
   - `python3 ~/vllm-monitoring/pull-remote-logs.py --once` + `tail freeze-verdict.jsonl`（磁盘冻结=UNREACHABLE）
4. **客户端层**：客户端会话日志末条真错误（WorkBuddy jsonl 末条 `providerData.error`；"cancelled" 常是流被 500 打断的表象，不是用户真取消）。

## 根因 → 动作

| 根因 | 动作 |
|---|---|
| vllm EngineCore 500 / 空流（OOM 边缘） | 服务器重启 vllm；长期降 `--gpu-memory-utilization` / 限 `max_num_seqs`。前兆：VRAM 单调逼近上限（如 15.4G/16G）+ KV cache 占比低 + 大请求（>400KB body）触发 |
| relay 8010 502 | 自愈（proxy 15s failover）；反复出现查服务器 ninfer-relay watchdog |
| 磁盘冻结 | freeze-verdict 持续 UNREACHABLE → 服务器重启 |
| 渠道掉线 | 重启 hermes gateway（会短暂断 QQ） |

## 纪律

- proxy.log 百万行级：grep 必带 `tail`/`-c`，不整读。
- 定位后**必须**在 `projects/系统运维/1_LLM链路错误排查/2_事件台账/README.md` 记一条（日期/症状/根因/动作/证据行号）。
- 别把表象当根因：workbuddy "用户已取消" ≠ 用户取消；dsh "无 final reason" ≠ dsh 的 bug。
