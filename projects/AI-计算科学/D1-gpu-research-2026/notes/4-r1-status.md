origin: ai
time: 2026-09-27T04:15+08:00
stage: 04 / round: r2 / status: START

# cursor: 04/r1 DONE -> 04/r2 START

## 04/r1 done (pass)
- A7 first-hand price table (5 cards, >=2 disjoint src each).
- VRAM gate fit script-verified (INT4 15.81 / INT8 29.61 / BF16 57.22).
- cheapest feasible single-card per precision computed.

## 04/r2 scope
- A3 prefill tokens/s first-hand (vLLM/SGLang benchmark, 27B, per card).
- A4 decode tokens/s first-hand (bandwidth-bound).
- A5 quant ppl delta first-hand (lm-eval-harness, INT8/INT4 vs BF16).

## precise blocking
- G2 budget not given -> A10 rank stays three-scenario (conservative FP16 / baseline INT8 / aggressive INT4).
- config.json 401x3 -> sliding_window cross-checked only (not config-first-hand).
- first-hand throughput/ppl not yet fetched (04/r2 action).

## next concrete action (04/r2)
- WebSearch/WebFetch vLLM or SGLang benchmark for Gemma-3-27B prefill/decode tokens/s on 4090/5090/L40S/6000Ada/A100-40.
