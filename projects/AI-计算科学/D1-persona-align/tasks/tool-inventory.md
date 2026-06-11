# Tool Inventory — Real Hermse Session Test

## Subtask 1: 环境检查与备份
- 可用工具：`curl`/`wget` (Hermes API 可达性检查), Python `shutil.copy2` (备份)
- 工具可用性：complete
- 背景知识：充足 — 需要知道 Hermes Gateway 的 API 端点（默认 localhost:8080 或配置中定义）
- 查重结果：无需开源方案
- 新颖性：N0

## Subtask 2: 启动真实会话
- 可用工具：Hermes Gateway HTTP API（POST /chat 或类似端点）, `curl`, Python `requests`
- 工具可用性：partial — 需要确认 Hermes Gateway 当前是否运行，API 端点和请求格式
- 背景知识：不足 — 需要确认 Hermes API 文档（`~/.hermes/config.yaml` 中的 gateway 配置）
- 查重结果：现有 `sync_personality.py` 使用 Hermes API，可参考
- 新颖性：N1（需要少量调整）

## Subtask 3: 会话内容评估
- 可用工具：`scripts/unified_eval.py --prompt <text>`, `scripts/persona_v3_alignment_checker.py`, `scripts/persona_v3_gap_filler_v2.py`
- 工具可用性：complete — 所有评估脚本已验证
- 背景知识：充足
- 查重结果：无需开源方案
- 新颖性：N0

## Subtask 4: 结果记录与报告
- 可用工具：Python `json.dump()`, Markdown `Write` 工具
- 工具可用性：complete
- 背景知识：充足
- 查重结果：无需开源方案
- 新颖性：N0

## 总体评估
- 工具就绪度：partial — 主要阻塞点为 Subtask 2 中 Hermes Gateway 的可达性和 API 格式
- 阻塞项：Hermes Gateway 服务状态未知，需要检查
- 新颖性评估：N1 — 主要创新点在于将已有评估工具应用于真实会话场景
