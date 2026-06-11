{
  "decision": "enter_2loop",
  "reason": "核验结论：\n- task-definition.md：存在，真实 Hermse 会话测试定义清晰\n- acceptance-criteria.md：存在，6条验收标准（5硬1可妥协）\n- task-decomposition.md：存在，DAG串行 4 步，每步含输入→输出→验证→回滚\n- tool-inventory.md：存在，评估工具就绪，Hermes Gateway 为唯一阻塞点\n- gap-analysis.json：存在，0高影响未解决项，高风险项有明确缓解方案\n- 副脑：如 Hermes Gateway 不可用，需立即切换到模拟会话方案",
  "next_action": "执行 2-loop 流程 — pre-check → backup → execute → verify → confidence → decision",
  "enter_2loop": true,
  "average_confidence": 0.90,
  "subtasks": [
    {"id": 1, "name": "环境检查与备份", "status": "pending"},
    {"id": 2, "name": "启动真实会话", "status": "pending"},
    {"id": 3, "name": "会话内容评估", "status": "pending"},
    {"id": 4, "name": "结果记录与报告", "status": "pending"}
  ]
}
