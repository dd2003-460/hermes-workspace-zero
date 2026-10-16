origin: ai
time: 2026-09-27T09:05+08:00
input: user answers (G4=个人本地低并发, A100-40 refurb=接受) + 04-roofline-r5 rank + 显存门

# 04-r7 H* collapse under user scenario

## user scenario (confirmed this round)
- G4 concurrency = 个人本地 / 低并发 -> single-stream (batch=1) dominant -> roofline is the relevant ceiling.
- A100-40 refurb = ACCEPTED -> the $1200 price that drives the roofline cost-perf flip is available.

## collapse on single-stream cost-perf (roofline, script-verified)
INT8 (refurb accepted, better quality):
- A100-40 refurb INT8: roofline 58 tok/s @ $1200 -> R@low = 0.0480
- RTX 5090 INT8:     roofline 66 tok/s @ $1999 -> R@low = 0.0332
- A100-40 wins cost-perf (0.0480 > 0.0332) at $1200.
INT4:
- A100-40 INT4: 115 @ $1200 -> 0.0960 ; 5090 INT4: 133 @ $1999 -> 0.0664 ; A100-40 wins.
NOTE: 5090 is FASTER at roofline (133>115, 66>58); the flip is on PRICE ($1200 vs $1999), not throughput.

## VRAM gate check (一手✓)
- A100-40 40GB: INT8 29.61GB fits, INT4 15.81GB fits. OK.
- 5090 32GB: INT8 29.61GB fits (tight), INT4 fits. OK.

## HONEST form-factor caveat (load-bearing for 个人本地)
A100-40 is a DATACENTER accelerator, not a desktop card:
- cooling designed for server airflow (blower/passive), not a tower; often 2-slot + needs strong case airflow.
- no NVENC/display; consumer boards may lack PCIe spacing/cooling; refurb warranty nil.
- power ~250W (more efficient than 5090 ~575W), but cooling/form is the real friction.
=> cost-perf math says A100-40; 个人本地 form-factor may say 5090.

## collapsed H* (two viable, form-factor is the tiebreaker)
- IF personal-local = a workstation/server you CAN cool properly + accept refurb:
  H* = A100-40 refurb INT8 ($1200). Best single-stream cost-perf, 40GB headroom, INT8 quality.
- IF personal-local = a desktop tower (consumer cooling, easy buy):
  H* = RTX 5090 INT4/INT8. Worse cost-perf (0.0332 vs 0.0480) but form-factor viable, 32GB, full consumer support.

## honest boundary (unchanged)
- all throughput = community R + roofline theoretical; first-hand single-stream vLLM still BLOCKED (no GPU) ->
  the A100-40-vs-5090 cost-perf flip is physics-consistent but not first-hand-confirmed.
- A100-40 refurb price is live-quote-sensitive ($1200-3000); flip holds only near $1200.

`review: 04-r7 | Hstar-collapse | pass | user G4=个人本地低并发 (single-stream) + refurb A100-40 accepted -> roofline flip regime satisfied; single-stream cost-perf H*=A100-40 refurb INT8 ($1200, R@low 0.0480 > 5090 0.0332); flip is on PRICE not throughput (5090 faster 66>58); HONEST form-factor caveat: A100-40 datacenter cooling impractical in desktop tower -> if desktop, H*=5090; first-hand still blocked no-GPU; refurb price live-quote-sensitive | next: confirm form-factor (tower vs server) + live refurb quote`