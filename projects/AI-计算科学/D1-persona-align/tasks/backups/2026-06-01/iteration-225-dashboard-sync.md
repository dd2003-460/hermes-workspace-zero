# Iteration 225: dashboard VERIFICATION_PATTERNS 同步

## 目标
完成四个评估工具验证模式统一 — dashboard 也需要同步 timeline consistency 改进。

## 执行动作

### persona_v3_dashboard.py 修改
- VERIFICATION_PATTERNS 29 → 31 条
- 新增:
  - `r"在什么条件下不成立"` — 边界条件追问
  - `r"当.*时.*不.*"` — 场景约束 (timeline consistency)

### 验证
- Dashboard 语法验证通过

## 影响
- 四个评估工具 (中文 checker, EN checker, gap_filler, dashboard) 的 VERIFICATION_PATTERNS 现在完全统一
- 符合迭代 215-217 建立的"四个工具统一评分逻辑"原则
