{
  "requirement": "通过真实 Hermes Gateway API 启动一次成璐人格会话，验证 persona-v3 在实际对话中是否被正确激发。",
  "background": "Hermes Gateway 运行在 127.0.0.1:8642，使用 OpenAI 兼容接口 /v1/chat/completions。之前测试 8080 端口是错误的。Gateway 健康检查返回 ok。",
  "existing_info": [
    "Hermes Gateway: 127.0.0.1:8642, /v1/chat/completions API",
    "~/.hermes/config.yaml — chenglu personality 已部署",
    "persona-v3-prompt.txt — 完整 prompt (11278 bytes, MATO DPA v2)",
    "评估工具链 — unified_eval / alignment_checker / gap_filler_v2",
    "backups/2026-06-02/hermes-session-test/config-backup.yaml — 已备份"
  ],
  "constraints": ["不能破坏现有部署", "API 调用需通过 persona-v3 prompt"],
  "priority": "planning"
}
