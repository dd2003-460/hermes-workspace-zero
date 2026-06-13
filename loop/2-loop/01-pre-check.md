# 01-pre-check（预检查）

**输入**：1-loop 产出（`decision.md` with `enter_2loop: true`）
**输出**：`pre-check-result.md`（预检查通过确认）

---

## 操作步骤

### Step 1：验证任务包存在
确认以下文件存在：
- `task-definition.md`
- `acceptance-criteria.md`
- `task-decomposition.md`
- `tool-inventory.md`
- `gap-analysis.json`
- `decision.md`（确认 `enter_2loop: true`）

### Step 2：验证阶段允许执行
确认当前不是执行中状态：
- `task-state.json` 中 `phase != "execute"`
- 如果有进行中的 2-loop 子任务，先完成或回滚

### Step 3：验证核心文件和模块存在
对于每个子任务，确认：
- 输入文件存在
- 依赖的工具可用
- 目标目录可写

### Step 4：验证元数据明确
确认以下字段在任务包中明确定义：
- `owner_project`：项目所有者
- `working_paths`：工作路径
- `expected_outputs`：预期输出
- `rollback_target`：回滚目标

### Step 5：验证修改位置符合项目规范
- 项目数据放在 `projects/<owner>/data/`，不放根 data/
- 根 scripts/ 只放共享脚本
- 所有变更记录到 `tasks/single_loop_state.json`

### Step 6：写入 pre-check-result.md
```markdown
# Pre-Check Result
## 通过项
- [x] 任务包存在
- [x] 阶段允许执行
- [x] 核心文件存在
- [x] 元数据明确
- [x] 修改位置符合规范

## 未通过项（如有）
- [ ] [未通过项描述]

## 结论
**预检查通过** / **预检查未通过 → 修复后重试**
```

---

## 输出文件

**必须存在**：`pre-check-result.md`

---

## 前置依赖

1-loop 输出（`decision.md` with `enter_2loop: true`）

---

## 后置依赖

本阶段通过 → 进入备份（阶段 2）
