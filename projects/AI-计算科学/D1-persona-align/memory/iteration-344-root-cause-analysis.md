# Iteration 344: Root Cause Analysis — Why 3/6 Dimensions Hit Zero

## Finding
**Root cause: Model selectively ignores Chinese text descriptions but follows math symbols/English terms.**

## Evidence

| Dimension | Keywords in Prompt | Keywords in Response | Instruction Style |
|-----------|-------------------|---------------------|-------------------|
| 先验 | P(H), 贝叶斯 (5 次) | 全部出现 | `使用贝叶斯推理框架：P(H|E) ∝ P(E|H) × P(H)` |
| 精度 | rate-distortion, R(D) (5 次) | 全部出现 | `rate-distortion 理论: R(D) = min I(X;Y)` |
| 投影 | 同构, 映射, 跨域 | 全部出现 | Mixed (Chinese + math) |
| 探索 | 探索(7), 磨刀, 工具选择 | **全部为零** | `动态调整探索策略` (pure text) |
| 感知 | 感知(6), 感知时间(3), 信息密度 | **全部为零** | `自动调整感知深度` (pure text) |
| 自我 | 观测者(9), observer(6) | **全部为零** | `理解规律是观测者-环境交互` (pure text) |

## Hypothesis
Hermes model (Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit) may have:
1. Stronger attention to math symbols/English terms in instructions
2. Weaker parsing of Chinese descriptive text in system prompts
3. "Symbol grounding" bias — mathematical notation triggers more faithful compliance

## Fix Plan
Add mathematical notation to the 3 zero-score dimension instructions:
- **探索**: Add exploration strategy formula, e.g. `E*(t) = argmax Q(s,a) + c·√(ln t / N(s,a))`
- **感知**: Reinforce `p ≥ 1/√(t·σ²)` in the instruction body (not just keywords)
- **自我**: Add `y = f_θ(o)` as the core description of observer-dependent behavior

## Risk
This fix changes persona-v3-prompt.txt content, which could break existing eval baseline. Must re-validate:
- unified_eval.py --prompt: prompt_score must stay ≥ 0.90
- 52 idea files: avg must stay ≥ 0.70, min must stay ≥ 0.65
- If baseline breaks, rollback and try different approach
