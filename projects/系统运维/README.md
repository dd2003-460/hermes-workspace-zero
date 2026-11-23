# 系统运维

> 本 workspace 自身运行链路的运维：LLM 上游（vllm → 8787 proxy → hermes/workbuddy/dsh）、hook、监控。
> 创建：2026-11-18，起因 = 四渠道同时报"stream 空 / 用户已取消 / 无 final reason"。

## 主要功能

本地 LLM 服务链路的故障排查与事件记录。链路拓扑：

```
vllm 10.20.33.188:8000 (qwen3.8-27b-mtp, tp4, 16G)
  │  （备选 8010 relay / 100.112.53.47:8000/8010 tailscale，常 DOWN）
  ▼
claude-vllm-proxy :8787  (~/.claude-vllm-proxy/proxy.mjs, 健康探测 15s, 多上游 failover)
  ├── hermes gateway  (~/.hermes/, 渠道: qqbot / weixin / api_server:8642)
  ├── WorkBuddy.app   (~/.workbuddy/, --model=custom-local:qwen3.8-27b-mtp)
  └── DSH desktop     (harness profiles baseURL → 8787/v1, bridge 60111)
```

## 接口

- 输入：用户报障（渠道名 + 症状）
- 输出：根因定位 + 修复动作 + 事件台账条目
- 对外：无（纯运维文档 + 排查脚本）

## 调用说明

1. 报障 → 先查 `1_LLM链路错误排查/1.1_症状-根因映射/README.md` 按症状对根因
2. 按 `1.2_排查手册/README.md` 的分层流程取证（proxy.log → errors.log → 上游）
3. 定位后在 `2_事件台账/` 记一条（日期/症状/根因/动作/证据行号）
4. 详细 SOP 已挂 `sop/SOP-INDEX.md` §6（`sop/llm-chain-troubleshooting.md`）
