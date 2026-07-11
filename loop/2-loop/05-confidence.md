# 05-confidence（置信度检查）

**输入**：`verification-report.md`（来自阶段 4）
**输出**：置信度评估 + 是否继续执行

---

## Agent 使用规范

置信度检查阶段**必须通过 `confidence-judge` Agent 执行**。Commander 不自行评估置信度：

| 场景 | 使用 Agent | 原因 |
|------|-----------|------|
| 置信度综合评估 | `confidence-judge` Agent | Agent 基于验证报告独立评估置信度 |
| 遗留分支识别 | `fork-decider` Agent | Agent 识别需要进一步验证的分支 |

**强制要求**：
- 置信度评估必须通过 `confidence-judge` Agent
- 判定结果（低/中/高）必须由 Agent 给出
- Commander 只审核 Agent 的置信度评估，不做独立计算

---

## 操作步骤

### Step 0：标注环节
输出开头声明：`[环节: confidence]`

### Step 1：读取验证报告（Agent 执行）
**通过 Agent 执行**：`confidence-judge` Agent 从 `verification-report.md` 中提取：
- 总体置信度
- 未通过项

### Step 2：应用置信度门槛（Agent 执行）
**通过 Agent 应用**：`confidence-judge` Agent 应用置信度门槛：

| 评分 | 判定 | 动作 |
|------|------|------|
| < 0.6 | 低 | 不得 completed。标注不确定，生成遗留分支 |
| 0.6-0.8 | 中 | 标注不确定，记录未验证假设 |
| > 0.8 | 高 | 正常通过 |

### Step 3：处理未通过项（Agent 执行）
**通过 Agent 处理**：`fork-decider` Agent 如果任何交付物置信度 < 0.6：
- 标注不确定
- 生成遗留分支（需要进一步验证的假设）

### Step 4：写入 confidence-report.md（Agent 辅助整理）
**通过 Agent 辅助整理**：汇总 Agent 评估结果，写入 confidence-report.md。
```markdown
# Confidence Report
## 总体置信度
[加权平均值]

## 判定
- [低/中/高]

## 遗留分支（如有）
- [未验证的假设]

## 结论
**通过** / **需要进一步验证** / **需要回滚**
```

---

## 输出文件

**必须存在**：`confidence-report.md`

---

## 前置依赖

阶段 4 输出（`verification-report.md`）

---

## 后置依赖

本阶段通过 → 进入分叉决策（阶段 6）

---

## 约束

- 置信度必须通过统计工具计算，不靠感觉
- < 0.6 不得标记 completed
- 0.6-0.8 必须标注不确定
