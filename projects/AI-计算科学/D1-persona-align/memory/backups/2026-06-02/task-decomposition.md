# Task Decomposition — Health Check

## Subtask 1: 脚本编译检查
- 输入：scripts/ 下 20 个 .py 文件
- 输出：编译结果列表
- 验证：每个文件 `compile()` 成功，无 SyntaxError
- 回滚：无需回滚（只读检查）
- 置信度：0.99
- 依赖：null

## Subtask 2: 集成测试运行
- 输入：scripts/integration_test.py
- 输出：集成测试结果 (PASS/FAIL)
- 验证：结果为 "11 通过, 0 失败"
- 回滚：无需回滚（只读检查）
- 置信度：0.99
- 依赖：null

## Subtask 3: 评估基线检查
- 输入：eval_results/unified_report.json
- 输出：基线指标对比表
- 验证：prompt ≥ 0.90，平均分 ≥ 0.70，最小分 ≥ 0.65，所有维度 ≥ 0.40
- 回滚：无需回滚（只读检查）
- 置信度：0.99
- 依赖：null

## Subtask 4: 文件计数验证
- 输入：memory/、eval_results/、scripts/
- 输出：文件计数报告
- 验证：memory iteration files ≥ 158，eval results JSON 文件数匹配，活跃脚本 20 个
- 回滚：无需回滚（只读检查）
- 置信度：0.95
- 依赖：null

## Subtask 5: 文档索引一致性
- 输入：INDEX.md、memory/INDEX.md、CLAUDE.md
- 输出：索引一致性报告
- 验证：迭代号与实际 memory 文件最新编号一致
- 回滚：无需回滚（只读检查）
- 置信度：0.90
- 依赖：null

## Subtask 6: 健康检查报告
- 输入：Subtask 1-5 结果
- 输出：eval_results/health_check_report.json
- 验证：包含所有检查项的实际结果
- 回滚：删除报告即回滚
- 置信度：0.95
- 依赖：[1, 2, 3, 4, 5]

## DAG 依赖图
```
[1] 编译检查    ┐
[2] 集成测试    ├─ 无依赖，可并行
[3] 评估基线    │
[4] 文件计数    │
[5] 索引一致性  ┘
    ↓
[6] 健康报告    (依赖 1,2,3,4,5)
```

### 并行块
- Block A (完全并行): [1, 2, 3, 4, 5] — 各自独立，无输入依赖
- Block B: [6] — 依赖 [1,2,3,4,5]

### 理论最大并行加速比: 5x (Block A)
