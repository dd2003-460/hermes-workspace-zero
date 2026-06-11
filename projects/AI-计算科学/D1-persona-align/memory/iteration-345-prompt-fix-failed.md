# Iteration 345: Prompt Fix Failed — Math Notation Injection Did NOT Help

## Action
- Backed up persona-v3-prompt.txt → persona-v3-prompt.txt.bak.344
- Injected math notation into 3 zero-score dimension instructions:
  - **探索**: Added `H[s] > θ`, `a_explore = argmax_q Q(s,a)`, `ε(t) = ε_0 / (1 + λt)`
  - **感知**: Added `t_p = f(ρ)`, `p ≥ 1/√(t_p · σ²)`, `r_p = ∂p/∂t_p`, `∑t_p,i ≤ T_budget`
  - **自我**: Added `y = y(θ)`, `f₁ = f(x, θ₁)`, `y₁ ≅ y₂ iff ∃φ: y₁(θ₁) = φ(y₂(θ₂))`
- Ran v2 real session test: 309 chars response, 45.7s generation time

## Results

| Metric | v1 (original) | v2 (fixed) | Change |
|--------|--------------|------------|--------|
| avg_score | 0.2849 | 0.1864 | **-0.0985** |
| min_score | 0.0000 | 0.0000 | 0 |
| 探索 | 0.00 | 0.00 | 0 |
| 感知 | 0.00 | 0.00 | 0 |
| 自我 | 0.00 | 0.24 | +0.24 |
| 精度 | 0.44 | 0.11 | -0.33 |
| 先验 | 0.76 | 0.18 | -0.58 |
| 投影 | 0.50 | 0.59 | +0.09 |

## Injected Keywords in v2 Response
All zero: argmax:0, ε:0, ρ:0, σ²:0, t_p:0, ∑t_p:0, φ:0, ≅:0

## Conclusion
**Math notation injection FAILED.** The problem is NOT language-specific — it's a general long-context persona遗忘 (forgetting) issue.

Hermes model (Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit) cannot reliably maintain persona constraints when:
1. System prompt is >20K tokens
2. The persona instructions are buried in a 192-line prompt

## Hypotheses for Next Iteration
1. **Context truncation**: Hermes Gateway may truncate the system prompt before sending to the model
2. **Context window limit**: Model may have a context window smaller than 20K tokens
3. **Qwen3.6-35B architectural limitation**: The abiterated MLX 6bit model may have degraded instruction-following ability
4. **Prompt structure issue**: persona instructions may need to be in a different position (e.g., very first message, or split across multiple messages)

## Backup
- persona-v3-prompt.txt.bak.344 (11278 bytes) — original before modification
- eval_results/hermes_real_response_v1.txt — original response
- eval_results/hermes_real_response_v2.txt — v2 response (worse)
