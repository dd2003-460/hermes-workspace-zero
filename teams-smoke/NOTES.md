# Agent Teams AI — 本机指挥备忘（2026-11-15）

## API（localhost:3456）
- 读：GET /api/teams、GET /api/teams/:name
- 写：POST /api/teams（建队，body: teamName/displayName/description/cwd/providerId/model/members[]）
- 启动：POST /api/teams/:name/launch（body: cwd + prompt=派给 lead 的指令 + skipPermissions）
- 停止：POST /api/teams/:name/stop
- 无 delete 端点 → rm -rf ~/.claude/teams/<name>/

## 坑
1. launch 的模型校验：模型名必须在 app 运行时 catalog 里（兼容端点 /v1/models 探测）。
   8000 端口的 MLX server 挂了 → catalog 空 → 任何模型都报 "not launchable"。
   可用端点：127.0.0.1:8787 → qwen3.8-27b-mtp（vLLM，262k 上下文）。
2. 建队后模型写死在 ~/.claude/teams/<name>/team.meta.json + members.meta.json，
   launch 前可直接改这两个文件换模型。
3. 成员 bootstrap 有 queryGuard：lead 在跑时成员提交会被拒（retryable），等 lead 空闲后自动重试。

## 现有队
- core：team-lead + reviewer + logic-reviewer + method-reviewer，模型 qwen3.8-27b-mtp
  链路验证通过（2026-11-15 21:07）：lead 建文件 → reviewer 核验 → 结论追加，全链路 ~1 分钟。
- forge-labs：旧队（MLX Qwen3.6-35B），8000 挂了起不来，可删。

## 护栏
- loop-guard.py 阈值已放宽：软 60min/200 次、硬 120min/500 次（原 10min/20 次）。
  备份：~/.hermes/agent-hooks/loop-guard.py.bak-20261115-guard、~/.hermes/config.yaml.bak-20261115-guard

## stophook 主动停止门（2026-11-15 21:10 改）
- 原 r91 语义「HALT 也 continue / 用户喊停也 continue」→ 机械重复根因，已废
- 新语义：HALT 文件（~/.hermes/.stage-gate/HALT）= 真停开关；用户喊停 = 放行停止
- 无停止信号 + 有未完成工作/无活跃 goal → 仍自动续推（ralph 语义不变）
- 备份：stop_hook.py.bak-20261115-r91（改前原文件）
- config.yaml pre_verify 已恢复（stop_hook + pre-verify-ralph + pre-verify-lead-ralph）
- 行为测试通过：HALT→stop、喊停→stop、无信号+有活→continue

## 模型切换（2026-11-15 21:15）
- 原计划：MLX Qwen3.6-35B @ 127.0.0.1:8000
- 实际：vLLM qwen3.8-27b-mtp @ 127.0.0.1:8787
- 原因：8000 端口无进程监听（MLX 服务挂了），8787 是唯一活着的模型端点
- core 队全员（lead + 3 reviewer）已切到 27b-mtp，smoke test 通过
- 27b-mtp 是 NVFP4 量化（root=/models/Qwen3.8-27B-NVFP4），max_model_len=262144
