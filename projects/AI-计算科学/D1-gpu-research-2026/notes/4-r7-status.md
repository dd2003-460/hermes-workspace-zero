origin: ai
time: 2026-09-27T09:06+08:00
stage: 04 / round: r7 / status: DONE (H* collapsed, pending form-factor+quote+first-hand)

# cursor: 04/r7 H* collapse DONE -> next = form-factor (tower vs server) + live refurb quote + first-hand

## user scenario confirmed
- G4 = 个人本地低并发 (single-stream dominant) + A100-40 refurb ACCEPTED.

## collapsed H*
- cost-perf (single-stream, roofline): H* = A100-40 refurb INT8 ($1200, R@low 0.0480 > 5090 0.0332).
- flip is on PRICE not throughput (5090 faster at roofline 66>58).
- HONEST form-factor caveat: A100-40 = datacenter card, cooling/form impractical in desktop tower.
  -> if desktop tower: H* = RTX 5090 (viable form, worse cost-perf).

## remaining blockers (narrowed)
- form-factor: tower (->5090) vs server/workstation you can cool (->A100-40). USER.
- A100-40 live refurb quote: flip holds only near $1200. USER/market.
- first-hand single-stream vLLM: BLOCKED no GPU. ENV.

## next concrete action
- ask/confirm form-factor (tower vs server) -> final single H*.
- when GPU: 04-r8 first-hand single-stream vLLM -> confirm A100-40-vs-5090 cost-perf flip.