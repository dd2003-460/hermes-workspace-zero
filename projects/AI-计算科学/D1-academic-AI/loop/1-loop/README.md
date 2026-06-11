# 1-loop — Planning / 任务规划层

**原则**：任务要求→目标澄清→分解→信息搜集→核验→决策。不是"完成任务"，而是"让任务可以被正确执行"。

## 流程架构

```
输入 → [1.1-任务澄清] → [1.2-目标澄清] → [1.3-任务分解]
                                              ↓
                              [1.4-信息搜集] ← [继续1-loop]
                              [1.5-完备核验]
                                          ↓
                                  [1.6-决策] → enter_2loop | continue_1loop
```

## 阶段一览

| 步骤 | 文件 | 输入 | 输出 |
|------|------|------|------|
| 1.1 | `1-clarify-task.md` | 原始任务 | `task-definition.md` |
| 1.2 | `1.2-clarify-goal.md` | 任务定义 | `acceptance-criteria.md` |
| 1.3 | `1.3-decompose.md` | 验收标准 | `task-decomposition.md` |
| 1.4 | `1.4-information-gather.md` | 子任务DAG | `tool-inventory.md` |
| 1.5 | `1.5-verify.md` | 工具+子任务 | `gap-analysis.json` |
| 1.6 | `1.6-decide.md` | gap分析 | `decision.md` |

## 退出 1-loop
1-loop 的进入/退出标准：`1-EXIT-TO-2LOOP.md`

## 标准 I/O
- 输入格式：`1.1-input-schema.json`
- 状态格式：`task-state.schema.json`

## 读取顺序
1. `1-EXIT-TO-2LOOP.md`（判断当前是否需要规划）
2. `1.1-input-schema.json`（理解输入格式）
3. 按阶段顺序：1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6
4. `task-state.schema.json`（状态读写）

## 副脑永续
副脑每轮必出现。目标：质疑主脑，找缺口，不停止原则传递。
