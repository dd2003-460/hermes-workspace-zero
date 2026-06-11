# Iteration 235: 迭代追问机制 — persona-v3 prompt 结构增强

## 目标
基于 iteration 234 的研究结论，实现三条改进路径中的 #2 — 迭代追问结构化。当前 persona-v3 只有"追问边界：对每个结论追问 '在什么条件下不成立?'" 的文字要求，缺少结构化的 gap detection + follow-up + self-answer 机制。

## 执行动作

### persona-v3-prompt.txt 修改
- 在"输出要求"和"自我保全机制"之间插入新的"迭代追问机制"章节
- 包含三个步骤:
  1. **Gap Detection**: 识别 1-3 个缺口（证据/边界/视角/深度）
  2. **Follow-up Question**: 针对最显著缺口生成具体追问
  3. **Self-Answer**: 对每个追问给出初步回答 + 置信度标注
- 提供完整示例输出

### 同步更新评估工具
- `persona_v3_alignment_checker.py`: 添加 4 个新 VERIFICATION_PATTERNS (迭代追问, Gap:, Q?:, A?:, 置信度)
- `persona_v3_alignment_checker_en.py`: 添加 4 个新 VERIFICATION_PATTERNS (gap, follow.up, self.answer, confidence)
- `persona_v3_dashboard.py`: 添加 4 个新 VERIFICATION_PATTERNS (同上)

## 影响
- persona-v3 正式从"混合模式（分层指令 + 迭代追问 + 自验证）"中验证了"迭代追问"这一步骤
- 新增 12 个 VERIFICATION_PATTERNS（每个 checker 4 个）
- 评估工具现在可以检测输出是否包含结构化迭代追问
