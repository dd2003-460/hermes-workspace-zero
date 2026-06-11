# Iteration 223: alignment_checker 验证模式增强 — timeline consistency + 边界追问

## 目标
根据 LivingTheNovel (timeline-aware constraints) 和 persona-v3 输出要求 #4 (边界追问), 增强 verification patterns。

## 执行动作

### persona_v3_alignment_checker.py 修改
- VERIFICATION_PATTERNS 从 15 条增至 17 条
- 新增:
  - `r"在什么条件下不成立"` — 边界条件追问 (对应输出要求 #4)
  - `r"当.*时.*不.*"` — 场景约束 (timeline consistency)

### 验证
- baseline 评分: 63.08 → 63.47 (+0.39)
- 提升来源: "在什么条件下不成立?" 在 persona-v3-prompt.txt 中被正确匹配

## 影响
- verification 权重 20% 的 scoring 更精准
- timeline consistency 约束现在可被量化检测
- 不影响 gap_filler / dashboard / sync_personality
