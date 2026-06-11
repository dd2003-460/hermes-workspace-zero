# Acceptance Criteria

## 验收标准
1. Hermes Gateway 服务可达（本地或远程）— 硬约束
2. 至少启动一次真实会话（非评估脚本），获得用户输入和 AI 输出 — 硬约束
3. AI 输出使用统一的 unified_eval.py 评估，prompt 评分 ≥ 0.90 — 硬约束
4. AI 输出使用 alignment_checker 检测 persona-v3 6 维度覆盖，平均分 ≥ 0.70 — 硬约束
5. AI 输出使用 alignment_checker 检测 6 维度最低分 ≥ 0.40 — 硬约束
6. 会话记录已保存（日志或文件），可复现 — 可妥协

## 质量要求
- 每次测试必须有可验证输出（会话日志 + 评估报告）
- 评估使用统一的 unified_eval.py 管道

## 硬约束（不可妥协）
- 测试不能破坏现有 chenglu personality 部署
- prompt 评分 ≥ 0.90
- 平均分 ≥ 0.70, 最低维度 ≥ 0.40

## 可妥协部分（质量降级但可交付）
- 如果 Hermes 服务不可用，使用模拟 API 调用替代（置信度降低但结论仍然有效）
- 会话记录可能不完整（如实时流式输出无法完全捕获）
