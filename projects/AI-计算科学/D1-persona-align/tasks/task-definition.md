# Task Definition
## 一句话任务（不超过3行）
通过真实 Hermes 会话验证 persona-v3 在实际对话中的人格激发效果。

## 边界
- 范围：启动真实 Hermse 会话 → 收集输出 → 用评估工具链验证对齐度
- 边界：不修改 persona-v3 核心逻辑、不修改 chenglu personality 配置（除非发现 bug）

## 失败标准
- Hermes 服务不可用且无替代方案，或会话输出完全未体现 persona-v3 特征（所有维度 < 0.40）

## 硬约束
- 不能破坏现有 chenglu personality 部署
- 测试过程可回滚（备份 config.yaml）
- 评估使用现有统一评估管道

## 已有条件
- ~/.hermes/config.yaml — chenglu personality 已部署
- loop/hooks/pre-new-message-ralph.md — Hermes hook 文件
- persona-v3-prompt.txt — 完整 prompt
- unified_eval / alignment_checker / gap_filler_v2 — 评估工具链
- QQ gateway 已连接
