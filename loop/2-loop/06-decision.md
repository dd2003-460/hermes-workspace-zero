# 06-decision（分叉决策）

**输入**：`confidence-report.md`（来自阶段 5）
**输出**：分叉决策（completed / completed_with_branches / needs_replan）

---

## 操作步骤

### Step 0：标注环节
输出开头声明：`[环节: decision]`

### Step 1：读取置信度报告
从 `confidence-report.md` 中提取：
- 总体置信度
- 判定（低/中/高）
- 遗留分支

### Step 2：应用分叉规则

#### 规则 A：completed
- **条件**：全部通过 + 置信度 > 0.6
- **动作**：标记完成，生成下一步

```markdown
# Decision
## 状态
completed

## 下一步
[下一个子任务或整体任务完成]

## 结论
**任务完成，置信度 > 0.6，标记 completed**
```

#### 规则 B：completed_with_branches
- **条件**：置信度 0.3-0.6
- **动作**：标记完成，生成遗留分支

```markdown
# Decision
## 状态
completed_with_branches

## 遗留分支
- [未验证的假设1]
- [未验证的假设2]

## 下一步
[处理遗留分支的计划]

## 结论
**任务完成但有遗留，置信度 0.3-0.6，需要进一步验证**
```

#### 规则 C：needs_replan
- **条件**：置信度 < 0.3 或任何核验未通过
- **动作**：回滚，回 1-loop

```markdown
# Decision
## 状态
needs_replan

## 回滚目标
[回滚到哪个备份点]

## 重新规划
[需要回到 1-loop 的哪个阶段]

## 结论
**任务失败，置信度 < 0.3 或核验未通过，需要回滚并重新规划**
```

### Step 3：写入 decision.md（2-loop 版本）
输出文件名：`decision-2loop.md`

---

## 输出文件

**必须存在**：`decision-2loop.md`

---

## 前置依赖

阶段 5 输出（`confidence-report.md`）

---

## 后置依赖

- completed → 下一个子任务或整体完成
- completed_with_branches → 需要进一步验证
- needs_replan → 回滚 + 回 1-loop

---

## 约束

- 不得跳过 verify 到 decision
- 必须按索引读
- 结果和证据优先
