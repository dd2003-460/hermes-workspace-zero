# Review: TextBO — Bayesian Optimization in Language Space

**Paper**: TextBO: Bayesian Optimization in Language Space for Eval-Efficient Self-Improving AI
**Authors**: Enoch Hyunwook Kang, Hema Yoganarasimhan (Anthropic)
**Approach**: Extends Bayesian Optimization to language domain for evaluation-efficient self-improvement.

## Key Insights

1. **Language-space BO**: Optimizes prompts/text directly using Bayesian Optimization, not gradient descent. Each iteration proposes a new text configuration and evaluates it against a target metric.

2. **Persona-induced preference distribution**: Uses "persona-induced preference distribution" to guide the optimization. This is directly relevant to persona-v3 — instead of keyword injection, use BO to find optimal prompt texts.

3. **Eval-efficient**: Optimizes with minimal evaluation calls, critical when evaluations are expensive.

4. **Connection to MATO**: MATO uses adjustable multipliers during generation. TextBO uses BO to find the optimal prompt configuration. Together: MATO optimizes at generation time, TextBO optimizes at prompt design time.

## Connection to persona-v3

1. **Alternative to keyword injection**: Instead of manually adding keywords, TextBO would automatically find which text modifications improve persona alignment.

2. **Test-time optimization synergy**: 
   - MATO: dynamic multipliers during generation → optimization at inference time
   - TextBO: BO over prompt text → optimization at prompt design time
   - Together: optimized prompt + optimized multipliers

3. **Gradient-free**: No gradients needed — just text modifications + evaluation score. Compatible with our unified_eval.py as the evaluation oracle.

## Action Items

1. Implement TextBO with persona-v3 evaluation as the objective function
2. Find optimal prompt modifications that improve avg score > 0.7318
3. Compare keyword injection vs TextBO-optimized prompt
