# Task Decomposition — Real Hermse Session Test

## Subtask 1: 环境检查与备份
- 输入：~/.hermes/config.yaml
- 输出：Hermes 服务状态报告 + config.yaml 备份
- 验证：Hermes Gateway 可达（curl 或 socket 检查），备份文件存在于 backups/
- 回滚：恢复 config.yaml 从备份
- 置信度：0.95
- 依赖：null

## Subtask 2: 启动真实会话
- 输入：Hermes Gateway（本地 HTTP API 或远程）
- 输出：一次包含用户输入和 AI 输出的完整会话
- 验证：获得非空 AI 响应文本，响应时间 < 30s
- 回滚：无需回滚（会话是一次性的）
- 置信度：0.80
- 依赖：[1]

## Subtask 3: 会话内容评估
- 输入：Subtask 2 的 AI 输出文本
- 输出：unified_eval.py 评估报告 + alignment_checker 维度覆盖报告
- 验证：prompt ≥ 0.90, 平均分 ≥ 0.70, 最低维度 ≥ 0.40
- 回滚：无需回滚（评估是只读的）
- 置信度：0.95
- 依赖：[2]

## Subtask 4: 结果记录与报告
- 输入：Subtask 3 评估结果
- 输出：memory/iteration-339-hermes-session.md 会话记录 + eval_results/hermes_test_report.json
- 验证：报告包含会话日志、评估指标、结论
- 回滚：删除记录文件
- 置信度：0.95
- 依赖：[3]

## DAG 依赖图
```
[1] 环境检查与备份
    ↓
[2] 启动真实会话
    ↓
[3] 会话内容评估
    ↓
[4] 结果记录与报告
```

### 并行块
- 无并行依赖（串行流程，每一步都依赖前一步的输出）

### 理论最大并行加速比: 1x (完全串行)
