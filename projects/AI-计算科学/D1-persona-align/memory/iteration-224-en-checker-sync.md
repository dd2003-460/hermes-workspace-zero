# Iteration 224: 英文版 alignment_checker verification patterns 同步

## 目标
根据"评估工具本身应该是 persona-v3 迭代的一部分"原则, 同步英文版 checker 的 VERIFICATION_PATTERNS 增强。

## 执行动作

### persona_v3_alignment_checker_en.py 修改
- VERIFICATION_PATTERNS 29 → 31 条
- 新增:
  - `r"under what condition.*not.*"` — 边界条件追问 (英文版)
  - `r"when.*not.*"` — 场景约束 / timeline consistency (英文版)

### 验证
- English checker 语法验证通过

## 影响
- 两个对齐检测工具的验证模式完全一致
- 符合"四个工具统一评分逻辑"的维护原则
