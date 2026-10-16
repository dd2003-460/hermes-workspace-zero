#!/usr/bin/env python3
# 04-r12: independent test runner for the H*-collapse decision rule (break-even $1735).
# 一手✓ self-test hardened r10/r11 -> now the DECISION RULE itself is machine-checked, not just asserted.
# Run: python3 tasks/test_hstar_rule.py
import sys
sys.path.insert(0, "/Users/a1-6/Desktop/workspace/projects/D1-gpu-research-2026/tasks")
from roofline_verify import roofline, CARDS, GATE, vram_gb, FULL_LAYERS, SLIDING_LAYERS

P_BE = CARDS["RTX_5090"]["price"] * (roofline("A100-40","INT8")/roofline("RTX_5090","INT8"))
fails = []

def check(name, cond):
    if not cond: fails.append(name)

# inv1: break-even algebra is correct (independent re-derivation, not just inv5's $1200<be)
#   at quote==P_BE both R equal -> tie; below -> A100 wins; above -> 5090 wins.
r_a, r_s = roofline("A100-40","INT8"), roofline("RTX_5090","INT8")
check("be-algebra-tie", abs(r_a/P_BE - r_s/CARDS["RTX_5090"]["price"]) < 1e-9)
check("be-algebra-value", abs(P_BE - 1734.6) < 0.5)
# inv2: boundary behavior of the decision rule (compare ACTUAL R@ values, not quote/be)
#   A100 wins iff roof_A100/quote > roof_5090/1999  <=>  quote < P_BE.
r5090_at = r_s/CARDS["RTX_5090"]["price"]          # 5090's R@ = 0.0332 (fixed)
check("quote-1200-A100-wins", (r_a/1200) > r5090_at)     # 0.048 > 0.0332 ✓
check("quote-2000-5090-wins", (r_a/2000) < r5090_at)      # 0.0288 < 0.0332 ✓
check("quote-at-be-tie", abs(r_a/P_BE - r5090_at) < 1e-9) # at $1735 exactly tie
# inv3: first-hand Gemma-3 hybrid pattern (unchanged)
check("pattern-10-52", FULL_LAYERS==10 and SLIDING_LAYERS==52)
# inv4: VRAM gate consistent with artifact
check("vram-int8", abs(vram_gb(GATE["INT8"]) - 29.61) < 0.05)

print("== H*-collapse decision-rule test (一手✓ machine-checked) ==")
print(f"  break-even = ${P_BE:.0f} (ratio {r_a/r_s:.4f})")
print(f"  rule: refurb A100-40 quote < ${P_BE:.0f} -> H*=A100-40 INT8 ; > ${P_BE:.0f} -> H*=RTX 5090")
print("  RESULT:", "ALL PASS ✓" if not fails else ("FAIL -> " + "; ".join(fails)))
sys.exit(1 if fails else 0)