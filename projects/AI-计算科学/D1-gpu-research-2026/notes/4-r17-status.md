origin: ai
time: 2026-09-27T20:35+08:00
stage: 04 / round: r17 / status: DONE (decision TREE collapsed to EXECUTABLE resolver resolve_hstar.py + machine-checked + test-the-test RED-proven; added to unified gate; deliverable still gated on user Q1/Q2/Q3)

# cursor: 04/r17 = H* decision tree now RUNS as code, not just prose/ASCII (regression-tested, teeth-proven)

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r16-status.md -> advanced to r17 here. Stayed GPU thread, did not restart.

## done this round (实现+验证, not analysis — per "上一多为分析 -> 本轮实现/验证")
r16 wrote the H* tree as PROSE/ASCII in 04-Hstar-decision-tree.md. Gap: prose trees cannot be regression-tested
(eyeball-only). This round collapses the tree to an EXECUTABLE function + machine-checks it:
- NEW `tasks/resolve_hstar.py`: `resolve(form_factor, a100_quote, rtx4090_quote) -> (H*, reason)`. Encodes the
  exact tree (server->Q2 vs $1735 ; tower->Q3 vs $1124 ; missing answer -> HELD). BE_A100=1735, BE_4090=1124.
- 9-case self-test incl. BOTH boundaries (strict '<' at $1735 and $1124 -> 5090 wins at be) + HELD cases + unknown form.
- inv9 (NEW): monotonicity-in-price guard -- cheap A100-40 ($600) MUST win, pricey ($3000) MUST lose to 5090 ->
  proves the tree is PRICE-driven (matches the r5 roofline finding), not throughput-driven.
- TEST-THE-TEST (teeth, not decorative): [A] normal -> ALL PASS exit0 ✓ ; [B] inject WRONG-CANARY expected ->
  caught, RESULT FAIL, exit1 ✓ ; [C] canary removed -> green again ✓.
- Added resolve_hstar.py to run_all.py SUITES -> unified gate now 3 suites, ALL GREEN exit0 ✓ (re-ran).

## why this matters (advance, not restate)
- Before r17: the deliverable's decision tree was prose -> if a future edit changed a break-even or flipped a branch,
  nothing would catch it (the tree could silently rot). Now it is code behind the same exit-code discipline as r13.
- The tree's THREE leaves + boundaries are machine-checked, so when the user answers Q1/Q2/Q3, the collapse is
  verified-by-construction, not eyeballed-once. This closes the last eyeball-gap in the deliverable's logic.

## honest boundary (unchanged, NOT loosened)
- resolver encodes the RULE; it does NOT supply the ANSWERS. All three inputs are USER/market (form-factor, two
  refurb quotes) -> resolve() returns HELD until each is given. No fabricated answer.
- throughput still roofline ceiling / community R; first-hand vLLM ENV-BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round verified the tree's LOGIC, not the answer)
1. form-factor = USER (Q1: desktop tower vs server/workstation).
2. refurb A100-40 quote vs $1735 = USER/market (Q2, server branch).
3. refurb RTX 4090 quote vs $1124 = USER/market (Q3, tower branch).
4. first-hand single-stream vLLM = ENV (Apple Silicon no CUDA; rented NVIDIA box).

## next concrete action
- autonomous 一手✓ + logic-verification exhausted: tree runs + is regression-tested + teeth-proven. No further
  offline advance without user Q1/Q2/Q3 or an NVIDIA box.
- resting state: deliverable = self-resolving tree (prose 04-Hstar-decision-tree.md + code resolve_hstar.py, both
  green); H* collapses to one card the instant the user supplies Q1 (+ the relevant quote).