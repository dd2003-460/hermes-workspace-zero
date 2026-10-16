origin: ai
time: 2026-09-28T03:40+08:00
stage: 04 / round: r30 / status: DONE (IMPLEMENTATION: attack the GATE STRUCTURE itself -- the roofline's feasibility gate has ONLY ever checked CAPACITY (bytes<=VRAM: inv8/14/18/19). It NEVER checked COMPATIBILITY -- whether the chosen quant KERNEL actually RUNS on the card's compute capability. A card can FIT the model in VRAM yet be UNRUNNABLE if the GPTQ/AWQ CUDA kernel isn't compiled for its arch. DEPLOYABLE = VRAM_fit AND kernel_ready -> VRAM-fit is NECESSARY-not-SUFFICIENT -> the roofline's sole-gate assumption could recommend an UNRUNNABLE card. Encoded the compat gate into roofline_verify.py (inv21) AND the deliverable tree resolve_hstar.py.)

# cursor: 04/r30 = the roofline conflated CAPACITY with DEPLOYABILITY -- added the COMPATIBILITY gate (kernel runs on the card's arch), teeth-proven, encoded into the deliverable tree

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r29-status.md -> advanced to r30 here. Stayed GPU thread, did not restart.
- guardrail satisfied: r29 was IMPLEMENTATION (workload axis); r30 attacks a NEW KIND of assumption (gate STRUCTURE, not arithmetic).

## the genuine NEW-KIND-of-attack this round (first attack on the GATE, not the ARITHMETIC)
- inv11..inv20 all bounded BYTES / BANDWIDTH / PHASE -- i.e. the roofline's ARITHMETIC (bw/bytes, the ratio, the
  ceiling's validity). None ever questioned the GATE itself. The roofline's feasibility test is literally
  `bytes <= VRAM` -- a CAPACITY check. But deployability ALSO needs the quant KERNEL to RUN on the card's compute
  capability (CC). These are DIFFERENT gates. VRAM-fit does NOT imply deployable.
- RTX 5090 = Blackwell sm_100 = the NEWEST arch (一手✓ arch mapping). Quant-kernel support LAGS new arches:
  sm_100 GPTQ INT4 reported partial / recompile-needed (社区R web-search); AWQ / INT8 / FP8 reported supported.
  So the form-factor DEFAULT candidate (5090) is precisely the card whose newest arch has the LEAST-mature kernel
  support -- the roofline never looked there.

## done this round (implementation + verification)
### roofline_verify.py -- inv21 (the roofline-side proof)
- CC map {RTX_5090:sm_100, A100-40:sm_80, RTX_4090:sm_89, L40S:sm_89} (一手✓ arch).
- vram_fit21(card,prec) = the roofline's OWN capacity gate (weights + real FP16 KV + overhead <= VRAM).
- kernel_ready(card,prec) = honest 社区R risk flag: sm_100 GPTQ INT4 -> False; everything else -> True.
- deployable = vram_fit21 AND kernel_ready.
- inv21(1): exhibit a (card,prec) that PASSES the roofline's VRAM gate yet is UNRUNNABLE -> [('RTX_5090','INT4')]
  (fits 13.5<=32GB but kernel reported lagging) -> VRAM-fit does NOT imply deployable -> COMPATIBILITY is a
  SEPARATE load-bearing gate.
- inv21(2): COMPAT does NOT move the roofline arithmetic or the break-even (it PRUNES candidates, adds NO bytes/bw
  term) -> be=$1735 unchanged -> roofline arithmetic & be are COMPAT-INVARIANT; compat only shrinks the feasible SET.
- inv21 teeth: assume-all-kernels-ready (kernel_ready_bad=always True) -> fits-but-unrunnable witness VANISHES ([])
  -> the compat flag is LOAD-BEARING (removing it HIDES the 5090 sm_100 GPTQ risk the roofline never checked).
### resolve_hstar.py -- the deliverable-tree compat guard
- COMPAT_UNREADY = {("RTX 5090","INT4")}; parse_card_quant() splits a leaf into (card,quant); loop every resolved
  leaf, fail if any is unrunnable. Normal: every leaf DEPLOYABLE (5090 leaf emits INT8 which sm_100 supports).

## teeth-proven (all three, EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: normal EXIT=0; compat-decorative canary (sed kernel_ready->always True) -> inv21(1) fires
  FAIL -> EXIT=1 ✓; full gate run_all.py EXIT=0.
- resolve_hstar.py: normal EXIT=0.
- **[B] TREE GUARD TEETH (the defect FIXED this round):** the FIRST canary attempt copied resolve_hstar.py to
  `/tmp/rs_canary.py` -> raised `ModuleNotFoundError: No module named 'roofline_verify'` because resolve_hstar's
  `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` resolves to `/tmp`, so the EXIT=1 came from the
  WRONG cause (import error, not the guard) -> a FALSE teeth-prove. FIXED: ran the canary INSIDE tasks/
  (`cp resolve_hstar.py ./_rs_canary.py`, sed the server 5090 leaf INT8->INT4) so the import resolves -> the inv21
  guard fires RED for the RIGHT reason: `inv21: tree emits an UNRUNNABLE (card,quant) [('server','RTX 5090 INT4'),
  ...] -> compat gate violated` -> EXIT=1 ✓ (captured directly, no pipe). Restored -> [A] normal EXIT=0, [C]
  run_all.py EXIT=0.

## why this matters (advance, not restate)
- This is the FIRST attack on the GATE STRUCTURE, a dimension the roofline NEVER modeled. Prior rounds proved the
  roofline's NUMBER ($1735) robust to bytes/bw/phase/precision. r30 proves the roofline's GATE ("feasible = fits")
  is INCOMPLETE: fitting is necessary-not-sufficient. The H* decision's VALUE is unchanged (be COMPAT-INVARIANT,
  inv21(2)), but the FEASIBLE SET narrows -- and the deliverable tree must now REFUSE to emit an unrunnable
  (card,quant). Concretely: if the user's answer were "5090 + INT4", the roofline would have approved it (fits
  13.5<=32GB); the compat gate now blocks it (sm_100 GPTQ INT4 unready) and the tree routes the 5090 leaf to INT8
  (which sm_100 supports) instead.

## honest boundary (NOT loosened)
- kernel_ready is a 社区R RISK FLAG (web-search reports), NOT a 一手✓ first-hand compile test -- ENV-BLOCKED (no
  CUDA/vLLM on Apple Silicon). The first-hand single-stream vLLM run QUINTELY settles it (inv21 joins inv13 eta /
  inv19 KV dtype / inv20 prefill-decode ratio / the bw confirmation).
- the unready set is a BINARY known-risk snapshot; real kernel maturity is a continuum -> the tree refuses the KNOWN
  unready pair; a future sm_100 GPTQ-INT4 build would clear it (needs the first-hand run).

## precise blocking (deliverable advances ONLY on these; this round made the gate compatibility-aware)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- now QUINTELY
   load-bearing: settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), AND the sm_100 kernel-ready
   status (inv21).

## next concrete action
- premise chain complete through the PHASE boundary AND the GATE STRUCTURE, both ENCODED in the deliverable tree:
  regime (inv10) + traffic (inv11/15) + cache (inv16) + sparsity (inv17) + quant-meta (inv18) + KV-precision
  (inv19) + PHASE-domain (inv20) + GATE-structure/COMPAT (inv21) + eta (inv13) + constants (inv8/14) + cross-file
  (inv12) + tree (r17/inv9). Every remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted --
  HOLD awaiting user/market/hardware.

## r30 housekeeping DONE
- FIXED the broken teeth-prove of the resolve_hstar.py inv21 compat guard (was a FALSE teeth-prove: canary in
  /tmp raised ModuleNotFoundError -> EXIT=1 for the wrong reason). Now teeth-proven INSIDE tasks/ -> guard fires
  RED for the right reason -> EXIT=1; restored green; run_all EXIT=0.
- persisted r30 cursor; advanced INDEX.md cursor pointer r28->r30 + added the inv21 entry; updated durable memory
  with inv21 (COMPATIBILITY gate).