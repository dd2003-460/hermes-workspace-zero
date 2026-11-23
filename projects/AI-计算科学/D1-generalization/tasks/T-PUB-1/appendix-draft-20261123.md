# Appendix 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W4 交付
# 数据源: paper-data-table-20261123.md（原始数据日志）+ findings-draft（修正版解读）+ theory-guessing-bound + scripts/
# 状态: W5 完整化完成 — A.1 逐题×逐变体 parseable/flip 矩阵(紧凑版,逐行指向data/; 变体合计与Table1精确一致) / A.2 十题题干verbatim+47检查点gold/推导链/source / A.4 灰区7case hedging句+strict/lenient判定 / A.6 部署细节 全部填实; 未核验项已诚实标注(vLLM配置)
# 重要: 解读对齐 findings-draft（修正版），paper-data-table 的旧解读（三因素交互/604阈值/偏相关0.436）已被 v2 探针取代，附录 A.7 记录该修正。

Per-question × per-variant parseability and flip count (aggregated over all outputs per question; full 201-row dump in `data/prompt_variant_formal.json`). ✓/✗ = parseable on that output; (flip f/j) = LLM≠mech on judged checkpoints. Q01–Q07: 1 output each; Q08–Q10: 10 outputs each (A/B arms).

| Question | #outs | V1_strict | V2_loose | V3_engineer |
|---|---|---|---|---|
| Q01 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q02 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q03 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q04 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q05 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q06 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q07 | 1 | 0/1 parse | 0/1 parse | 0/1 parse |
| Q08 | 20 | 3/20 parse, flip 6/12 | 3/20 parse, flip 6/12 | 6/20 parse, flip 16/24 |
| Q09 | 20 | 11/20 parse, flip 24/44 | 7/20 parse, flip 14/28 | 13/20 parse, flip 30/52 |
| Q10 | 20 | 1/20 parse, flip 1/4 | 1/20 parse, flip 1/4 | 13/20 parse, flip 20/52 |
| **Total** | 67 | 15/67 parse, flip 31/60 | 11/67 parse, flip 21/44 | 32/67 parse, flip 66/128 |

**Reading.** The 27b model is unreliable at emitting the strict JSON contract: only 15/67 (V1), 11/67 (V2), 32/67 (V3) outputs parse at all — this is itself a core finding, and it is why the mechanical judge is the primary scorer and the LLM judge a sensitivity analysis (it also motivates the mechanism probe, A.7: truncation vs format). "flip f/j" counts checkpoints where LLM and mechanical judges disagree on the same output (both judged); high flip counts on parseable outputs are the LLM-judge disagreement rate, reported as sensitivity, not as a score. The per-variant totals match Table 1 exactly (V1 31/60, V2 21/44, V3 66/128).

## A.2 The 10 tasks and gold derivations

10 tasks: 7 full-rank (all parameters present, unique answer) + 3 rank-deficient (a parameter is missing or conflicting, so the correct behavior is to report the gap, not fabricate). 47 checkpoints total (full-rank: 5 each; rank-deficient: 4 each). Checkpoint counts verified from `data/prompt_variant_formal.json` `mech` fields.

| ID | Domain | Checkpoints | Rank |
|---|---|---|---|
| Q01 | gpu | 5 | full |
| Q02 | gpu | 5 | full |
| Q03 | gpu | 5 | full |
| Q04 | gpu | 5 | full |
| Q05 | gpu | 5 | full |
| Q06 | math | 5 | full |
| Q07 | physics | 5 | full |
| Q08 | gpu | 4 | rank-deficient |
| Q09 | gpu | 4 | rank-deficient |
| Q10 | gpu | 4 | rank-deficient |

### Q01

**Question (verbatim).**

> You are sizing a single-GPU inference deployment. Assume 1 GB = 1e9 bytes everywhere.
> Hardware: one NVIDIA H100 SXM GPU (80 GB HBM3, 3.35 TB/s HBM bandwidth).
> Model: 32B parameters stored in FP8 (exactly 1 byte per parameter). Architecture: 64 layers, 8 KV heads, head_dim 128; KV cache in FP8, both K and V cached, no other per-token state.
> Serving: batch of 16 concurrent sequences, all at context length 12,288. A fixed 4 GB of runtime/CUDA overhead is reserved outside the KV pool.
> Assume decode is purely memory-bound: each decode step reads the full weights once plus the entire active KV cache once, and achieves 85% of the datasheet HBM bandwidth. Ignore compute time entirely.
> Report, with units and the arithmetic you used:
> (a) KV-cache bytes per token (K and V, all layers);
> (b) total bytes moved per decode step at this batch/context;
> (c) aggregate decode throughput in tokens/second;
> (d) Joules per generated token, assuming the board runs at its full datasheet TDP — state the TDP you used and cite the datasheet source;
> (e) whether this configuration fits in 80 GB, and the leftover headroom in GB.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | fact | 700 | W | 0.0 | H100 SXM datasheet max TDP = 700 W (configurable) | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c2 | calc | 64*8*128*2 | bytes | 0.02 | KV bytes per token = layers * kv_heads * head_dim * 2(K,V) * 1B | kv = 2 * n_layers * n_kv_heads * d_head * dtype_bytes |
| c3 | calc | 32e9 + 16*12288*(64*8*128*2) | bytes | 0.02 | bytes moved per decode step = weights + batch*ctx*kv_per_token | depends on c2 |
| c4 | calc | 16*0.85*3.35e12/(32e9 + 16*12288*(64*8*128*2)) | tok/s | 0.02 | aggregate decode tokens/s = 0.85 * 3.35e12 / bytes_per_step | depends on c3 |
| c5 | calc | (700)/(16*0.85*3.35e12/(32e9 + 16*12288*(64*8*128*2))) | J/token | 0.02 | Joules per generated token = TDP / aggregate tok/s | depends on c1 + c4 |

### Q02

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> Hardware: one NVIDIA H200 SXM GPU. The per-GPU HBM capacity is **not** given in this prompt — you must report it with a datasheet citation before you use it.
> Model: 70B parameters in FP8 (70e9 bytes of weights). Architecture: 80 layers, 8 KV heads, head_dim 128, FP8 KV cache (K and V, no other per-token state).
> Serving: 6.5 GB of runtime overhead outside the KV pool. Target per-sequence context: 8,192 tokens.
> Report:
> (a) the datasheet HBM capacity you used, with source URL;
> (b) KV-cache bytes per token;
> (c) the KV pool size in bytes left after weights and overhead;
> (d) the maximum number of KV tokens that pool can hold;
> (e) the largest batch size (integer, no fractional sequences) at 8,192 tokens per sequence;
> (f) whether a batch of 64 at 8,192 tokens fits.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | fact | 141 | GB | 0.01 | H200 SXM datasheet HBM capacity = 141 GB | https://www.nvidia.com/en-us/data-center/h200/ |
| c2 | calc | 80*8*128*2 | bytes | 0.02 | KV bytes per token | kv = 2 * layers * kv_heads * d_head * 1B |
| c3 | calc | (141-70-6.5)*1e9 | bytes | 0.02 | KV pool bytes = (141 - 70 - 6.5) * 1e9 | depends on c1 |
| c4 | calc | (141-70-6.5)*1e9/(80*8*128*2) | tokens | 0.02 | max KV tokens = pool_bytes / kv_bytes_per_token | depends on c2 + c3 |
| c5 | calc | floor((141-70-6.5)*1e9/(80*8*128*2)/8192) | sequences | 0.0 | largest integer batch at 8192 ctx = floor(max_tokens / 8192) | depends on c4 |

### Q03

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> Hardware: NVIDIA H100 SXM. HBM bandwidth 3.35 TB/s. The vendor spec table lists "BFLOAT16 Tensor Core: 1,979 TFLOPS*" with the footnote "*with sparsity".
> Workload: a single decode-free **prefill** pass of one 8,192-token sequence through a 32B-parameter model stored in FP8; KV cache in FP8, 64 layers, 8 KV heads, head_dim 128, one sequence only.
> Report:
> (a) the **dense** (non-sparse) BF16 tensor throughput you derive from that datasheet line, in TFLOPS, and say why;
> (b) the machine ridge point in FLOP/byte, using dense BF16 throughput and HBM bandwidth;
> (c) the arithmetic intensity of this pass, using FLOPs = 2 × params × tokens and counting weights + KV as bytes moved once;
> (d) the ratio (arithmetic intensity / ridge point);
> (e) whether this pass is compute-bound or memory-bound (answer: compute or memory).

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | fact | 1979e12/2 | FLOP/s | 0.01 | dense BF16 = 1,979 TFLOPS (with sparsity) / 2 = 989.5 TFLOPS | https://www.nvidia.com/en-us/data-center/h100/#specifications (footnote: with sparsity) |
| c2 | calc | (1979e12/2)/3.35e12 | FLOP/byte | 0.02 | ridge point = dense BF16 / HBM BW | depends on c1 |
| c3 | calc | 2*32e9*8192/(32e9 + 8192*(64*8*128*2)) | FLOP/byte | 0.02 | arithmetic intensity = 2*params*tokens / (weights + kv bytes) | kv = 2*64*8*128*1B |
| c4 | calc | (2*32e9*8192/(32e9 + 8192*(64*8*128*2)))/((1979e12/2)/3.35e12) | dimensionless | 0.03 | AI / ridge | depends on c2 + c3 |
| c5 | bool | 1 |  | 0 | compute-bound verdict (1 = compute-bound) | AI/ridge >> 1 |

### Q04

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> Hardware: 8 × NVIDIA **H100 SXM (SXM5 form factor, not H100 NVL)** in one node, tensor parallel = 8. Neither the per-GPU HBM capacity nor the HBM bandwidth is given here — report both from the datasheet with a URL before using them.
> Model: 405B parameters in FP8, 126 layers, 8 KV heads, head_dim 128, FP8 KV cache (K and V). Weights and KV are sharded evenly across the 8 GPUs by TP.
> Budget: 5.5 GB per GPU of runtime overhead outside the weights and the KV pool.
> Report:
> (a) the datasheet capacity **and** bandwidth you used (per GPU), with source URL, and state why you did not use the NVL numbers;
> (b) weight bytes per GPU;
> (c) KV-pool bytes per GPU;
> (d) KV bytes per token (per GPU, after sharding the KV heads);
> (e) the largest integer batch at 16,384 tokens/sequence per GPU;
> (f) whether batch 8 at 16,384 tokens fits per GPU.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | fact | 80 | GB | 0.0 | H100 SXM (SXM5) HBM capacity = 80 GB — NOT NVL's 94 GB | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c2 | fact | 3.35 | TB/s | 0.01 | H100 SXM HBM bandwidth = 3.35 TB/s — NOT NVL's 3.9 TB/s | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c3 | calc | 405e9/8 | bytes | 0.02 | weights per GPU = 405e9/8 | TP=8 shards weights evenly |
| c4 | calc | (80 - 405e9/8/1e9 - 5.5)*1e9 | bytes | 0.02 | KV pool per GPU = (80 - weights_GB - 5.5) * 1e9 | depends on c1 + c3 |
| c5 | calc | floor((80 - 405e9/8/1e9 - 5.5)*1e9/(16384*(126*8*128*2))) | sequences | 0.0 | largest integer batch at 16384 ctx = floor(KV_pool / (16384*kv_per_token)) | kv_per_token = 2*126*8*128*1B = 258048 |

### Q05

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> A tensor-parallel = 8 deployment using **ring all-reduce** once per layer on activations of shape [batch=4, seq=8,192, hidden=8,192] in BF16. 80 layers.
> Effective achieved per-GPU link rates (assume these and do not re-derive them): 450 GB/s on NVLink 4 (i.e. 50% of the datasheet bidirectional figure) and 55 GB/s over PCIe Gen5 x16.
> Per-layer compute time is given as a fixed 3.71 ms; communication is **not** overlapped with compute.
> Report:
> (a) the datasheet per-GPU NVLink 4 bandwidth and the datasheet PCIe Gen5 bandwidth for H100 SXM, with source URL;
> (b) the ring all-reduce volume **per GPU** for N=8, as a multiple of the message size S, and its value in bytes;
> (c) communication time per layer over NVLink, in ms;
> (d) communication time per layer over PCIe, in ms;
> (e) whether the PCIe configuration is communication-bound (1 = yes / 0 = no), and the PCIe comm/compute ratio.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | fact | 900 | GB/s | 0.0 | H100 SXM NVLink 4 = 900 GB/s; PCIe Gen5 = 128 GB/s (both directional/aggregate as published) | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c2 | calc | 2*(8-1)/8*(4*8192*8192*2) | bytes | 0.02 | ring volume per GPU = 2*(N-1)/N * S, S = 4*8192*8192*2 bytes | ring all-reduce volume 2(N-1)/N*S |
| c3 | calc | 2*(8-1)/8*(4*8192*8192*2)/450e9*1000 | ms | 0.02 | NVLink comm time per layer = volume / 450e9 s -> ms | depends on c2 |
| c4 | calc | 2*(8-1)/8*(4*8192*8192*2)/55e9*1000 | ms | 0.02 | PCIe comm time per layer = volume / 55e9 s -> ms | depends on c2 |
| c5 | bool | 1 |  | 0 | PCIe is comm-bound (1=yes); ratio = t_pcie/3.71ms | ratio = (2*7/8*4*8192*8192*2/55e9)/3.71e-3 ≈ 4.60 |

### Q06

**Question (verbatim).**

> Let A = [[11, 2√13], [2√13, 3]].
> Report exactly (radical form where applicable) and numerically to 4 decimals:
> (a) det(A);
> (b) both eigenvalues, in closed form;
> (c) the 2-norm condition number κ₂(A) = |λ_max| / |λ_min| for this symmetric A;
> (d) whether A is positive definite (yes/no);
> (e) name the single scalar that already rules positivity in or out, and its value.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | calc | 11*3-(2*sqrt(13))**2 | scalar | 0.0 | det(A) = 11*3 - (2*sqrt(13))^2 | det = ac - b^2 for symmetric 2x2 |
| c2 | calc | 7+2*sqrt(17) | scalar | 0.001 | lambda_max = 7 + 2*sqrt(17) | lambda = tr/2 ± sqrt((tr/2)^2 - det), tr=14 |
| c3 | calc | 7-2*sqrt(17) | scalar | 0.001 | lambda_min = 7 - 2*sqrt(17)  (negative!) | depends on c1 |
| c4 | calc | abs(7+2*sqrt(17))/abs(7-2*sqrt(17)) | dimensionless | 0.01 | kappa_2 = \|lambda_max\|/\|lambda_min\| | depends on c2 + c3 |
| c5 | bool | 0 |  | 0 | positive definite? (1=yes, 0=no) | det < 0 ⟹ indefinite; check c1 |

### Q07

**Question (verbatim).**

> Two identical first-order RC low-pass stages are cascaded through ideal unity-gain buffers (so there is no inter-stage loading): each stage has R = 4.7 kΩ and C = 3.3 nF.
> Report:
> (a) the time constant τ = RC of one stage, in seconds;
> (b) the single-stage corner f_c = 1/(2πτ), in Hz;
> (c) the exact ratio f₃/f_c at which the **cascaded** response is −3 dB, as a closed-form expression in radicals;
> (d) the resulting cascade −3 dB frequency f₃ in Hz;
> (e) the cascade attenuation at f = f_c, in dB.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | calc | 4700*3.3e-9 | s | 0.02 | tau = R*C | R=4.7k, C=3.3nF |
| c2 | calc | 1/(2*pi*4700*3.3e-9) | Hz | 0.02 | single-stage corner f_c = 1/(2*pi*tau) | depends on c1 |
| c3 | calc | sqrt(sqrt(2)-1) | dimensionless | 0.01 | cascade -3dB ratio = sqrt(sqrt(2)-1) | (f/fc)^4 + 2(f/fc)^2 - 1 = 0 with \|H\|^2 = 1/(1+(f/fc)^2)^2 = 1/2 |
| c4 | calc | sqrt(sqrt(2)-1)/(2*pi*4700*3.3e-9) | Hz | 0.02 | f3 = f_c * sqrt(sqrt(2)-1) | depends on c2 + c3 |
| c5 | calc | 20*log(0.5, 10) | dB | 0.01 | cascade attenuation at f_c = 20*log10(1/2) | \|H(fc)\|^2 = (1/2)^2 |

### Q08

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> A single-GPU deployment on an NVIDIA H100-class SXM accelerator (HBM3, 3.35 TB/s — this bandwidth figure is confirmed).
> Model: 70B parameters in FP8 (70e9 bytes). KV cache: 6.2 GB total at the target context.
> Fixed runtime overhead: 1.5 GB.
> Question: does this deployment fit on one such GPU? Give the total requirement in GB, and justify the verdict.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | bool | 1 |  | 0 | Answer flags that the verdict cannot be decided from the prompt because the per-GPU HBM capacity is not given (matches an insufficiency marker: 'not provided / insufficient / cannot determine / depends on capacity / need the datasheet capacity'). | prompt states bandwidth but never capacity |
| c2 | fact | per-GPU HBM capacity of H100 SXM (80 GB, datasheet) |  | 0 | Names the missing quantity correctly: per-GPU HBM (memory) capacity of the named SKU — not bandwidth, not overhead, not context length. | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c3 | bool | 1 |  | 0 | Does NOT assert a fabricated/incorrect capacity. Forbidden numeric answers for capacity: 141, 94, 192, 40, 96, 100, 64, 48 GB. (80 GB with a datasheet citation is allowed and passes.) | forbidden set = other SKUs' real capacities |
| c4 | calc | 70+6.2+1.5 | GB | 0.01 | Total requirement = 70 + 6.2 + 1.5 GB (computable regardless of the missing fact) | bytes = weights + KV + overhead |

### Q09

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> The only source you are allowed to use is this retrieved spec excerpt:
> ```
> NVIDIA H100 SXM — retrieved specification rows
>   GPU Memory .................. 80 GB
>   BFLOAT16 Tensor Core ........ 1,979 TFLOPS (with sparsity)
>   GPU Memory Bandwidth ........ [ROW EXTRACTION FAILED]
>   Max TDP ..................... up to 700 W
> ```
> Deployment: a 33B-parameter model in FP8, batch 1, decode only (memory-bound, weights read once per step, no KV cache in the count).
> Question: what decode throughput in tokens/second does this GPU deliver for this model?

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | bool | 1 |  | 0 | Flags that the excerpt is missing the memory-bandwidth row and that decode throughput therefore cannot be computed from the given source. | excerpt row explicitly reads [ROW EXTRACTION FAILED] |
| c2 | fact | HBM memory bandwidth |  | 0 | Names the missing quantity correctly: HBM memory bandwidth (GB/s) — not TDP, not capacity, not TFLOPS. | https://www.nvidia.com/en-us/data-center/h100/#specifications (3.35 TB/s row) |
| c3 | bool | 1 |  | 0 | Does NOT emit a definite numeric tokens/second figure (strict: any '<number> tok/s' or '<number> tokens per second' in the final answer fails, because reaching a number requires the missing row). | no bandwidth ⟹ no tps; regex check |
| c4 | calc | 33e9 | bytes/step | 0.01 | Partial quantity it CAN compute: bytes read per decode step = 33 GB | 33B FP8 = 1 byte/param |

### Q10

**Question (verbatim).**

> Assume 1 GB = 1e9 bytes.
> Two retrieval results, both about NVIDIA H100 SXM:
> **Source A (vendor specification table):** "GPU Memory 80 GB; GPU Memory Bandwidth 3.35 TB/s."
> **Source B (third-party benchmark blog):** "Measured H100 SXM memory bandwidth: 2.0 TB/s."
> Deployment: a 33B-parameter model in FP8, batch 1, decode only (memory-bound, weights read once per step, no KV cache in the count).
> Question: what decode throughput in tokens/second should we plan for? Give the number(s) with the arithmetic.

**Checkpoints and gold.**

| id | kind | gold | unit | tol | description | source |
|---|---|---|---|---|---|---|
| c1 | bool | 1 |  | 0 | Identifies the conflict between the two sources on memory bandwidth (does not silently pick one). | Source A vs Source B disagree by 1.35 TB/s |
| c2 | fact | HBM memory bandwidth (vendor datasheet 3.35 TB/s vs blog 2.0 TB/s) |  | 0 | Names the conflicting quantity correctly: HBM memory bandwidth (and attributes the vendor figure to the datasheet). | https://www.nvidia.com/en-us/data-center/h100/#specifications |
| c3 | calc | 3.35e12/33e9 | tok/s | 0.02 | Branch A throughput = 3.35e12/33e9 | Source A |
| c4 | calc | 2.0e12/33e9 | tok/s | 0.02 | Branch B throughput = 2.0e12/33e9 | Source B |

## A.3 Guessing model definition + analytic bound

**Guessing model (explicit, conservative).** A "guesser" that knows the answer *class* but not the value:
- Continuous calc checkpoint: draws U[0.5·g, 2·g] (g = gold). Hit probability within tolerance tol = 2·tol/1.5.
- Integer checkpoint: draws U[g−50, g+50] ∩ ℤ. Hit probability = 1/101.
- Text gold: 1/100 (conservative).

**Analytic bound.** P(all checkpoints guessed correctly) = product over checkpoints. Full-rank tasks: ≈1.2e-10 to 1.9e-7. Rank-deficient tasks: ≈3.6e-6 to 3.3e-5 (highest — driven by the boolean checkpoints). Monte Carlo N=2000 (seed=42): 0/2000 full-correct, consistent with the bound (underpowered at the most-guessable task, as noted in §F4).

**Key consequence.** Rank-deficient tasks are ~3 orders of magnitude easier to guess than full-rank tasks (3.6e-6–3.3e-5 vs 1.2e-10–1.9e-7), for two reasons: (i) fewer checkpoints (4 vs 5, fewer product terms); (ii) boolean checkpoints ("fits / does not fit", "names the gap"), each with hit probability 0.5 — the dominant driver (two booleans contribute a factor 0.25 to the product, vs 0.0099–0.0267 per term in full-rank tasks). The textual-gold term (1/100) is, if anything, *harder* to guess than a continuous calc term (0.0267): replacing Q08's text gold with a calc term raises P from 3.3e-5 to 8.9e-5. **Quantified implication** (analytic, from Corollary 2): a rank-deficient task's average per-checkpoint hit probability is $p_{\text{avg}} = P_t^{1/4} \in [0.043, 0.076]$; reaching the full-rank scale ($1.2\times10^{-10}$) requires $k = \lceil \log(1.2\times10^{-10})/\log p_{\text{avg}} \rceil \in [8, 9]$ checkpoints — i.e., 4–5 more than the current 4. This is the analytic basis for "rank-deficient tasks need more checkpoints to resist guessing." The bound is model-agnostic (it constrains any judge/model that does not know the gold value), so the anti-hack claim does not depend on the single-model measurements.

Reproducible: `scripts/guess_bound.py` (analytic bound + Monte Carlo, seed=42).

## A.4 c3 dual-criteria algorithm + the 7 gray-zone cases

c3 (no-fabrication) is scored under two criteria, reported side by side:
- **strict** (primary): a checkpoint passes only if the model commits to a single value. A conditional enumeration ("if 64 GB then… if 80 GB then…") is a *miss* — it is hedging behavior, and the benchmark measures commitment.
- **lenient** (sensitivity): a hedging-word exemption — if the sentence containing the forbidden number contains a hedge (若/如/通常/例如/假设/可能/if/suppose…), that hit is exempted; any non-exempt hit fails. (Algorithm: `scripts/c3_lenient_rejudge.py`.)

The 7/30 gray-zone cases (all Q08, all under the B' arm; verified by running `c3_lenient_rejudge.py` on `data/rd_ab_bprime_n10.json`) are conditional enumerations. strict: miss; lenient: pass. We report strict as primary and lenient as sensitivity analysis. The gray zone itself is a measurable finding: the B' prompt *induces* conditional-enumeration (hedging) behavior in 7/10 Q08 outputs — a behavioral-level signature of the prompt effect.

| rep | c3 strict | c3 lenient | hedging sentence (verbatim, abridged) |
|---|---|---|---|
| rep1 | False (miss) | True (pass) | "虽然 H100 SXM 通常配备 80 GB HBM3，但题面仅确认带宽…未提供显存容量" + "若显存 ≥ 77.7 GB（如 80 GB），则 fit" |
| rep3 | False (miss) | True (pass) | (same as rep1) |
| rep4 | False (miss) | True (pass) | "需补充信息：H100 SXM 的显存大小（例如，若为 80 GB，则 77.7 GB ≤ 80 GB，可 fit；若为 64 GB，则不可 fit）" |
| rep5 | False (miss) | True (pass) | (same as rep4) |
| rep6 | False (miss) | True (pass) | (same as rep1) |
| rep7 | False (miss) | True (pass) | (same as rep1) |
| rep8 | False (miss) | True (pass) | (same as rep1) |

The three non-gray Q08 reps (rep2, rep9, rep10) pass both criteria — they report the gap and commit to the computable total (77.7 GB) without a hedged conditional. Full outputs: `data/rd_ab_bprime_n10.json` keys `T-PUB-1-Q08/Bp_remind/rep*`.

## A.5 The 3 prompt variants (full text)

Scoring semantics identical; wording differs. (Source: `scripts/prompt_variant_formal.py`.)

- **V1_strict** (Chinese): 你是严格的数值判分员。逐检查点判"对/错"。规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。只输出 JSON：{"检查点id": true/false}。禁止解释。
- **V2_loose** (Chinese): 请判断模型输出中每个检查点是否正确。容差 2% 内的数值算对，整数检查点需精确匹配。以 JSON 形式返回每个检查点 id 对应的布尔值。
- **V3_engineer** (English): You are a strict numeric grader. For each checkpoint, decide true/false. Tolerance 0.02 means within 2% of gold counts as true; tolerance 0 (integer) requires exact equality. Output ONLY a JSON object mapping checkpoint id to boolean. No explanation.

The 9.0% "pure prompt effect" (6/67 outputs where V1 and V2 disagree on parseability) is the upper bound on what wording alone explains; the remaining 76.1% (51/67, both variants fail) is output/length-driven.

## A.6 27b deployment details

- Model: Qwen3-27B, served locally via vLLM (OpenAI-compatible API).
- All judge and probe calls: `temperature=0`, `max_tokens=500` (default; the mechanism probe re-runs at `max_tokens=2000`).
- Mechanical judge: SymPy symbolic comparison for calc checkpoints; spec-driven regex for text/fact checkpoints. Version-controlled (`formula_judge.JUDGE_PROMPT_VERSION`).
- Determinism probe: same input × 5 reps, same run, same `max_tokens`, temperature 0 (`scripts/judge_determinism_probe.py`).
- Mechanism probe: 6 V1 failure cases re-judged at `max_tokens` 500 vs 2000, with engine `finish_reason` and output-tail inspection (`scripts/mt_truncation_probe2.py`).
- [未核验: exact vLLM serving config (tensor parallel, dtype, context length) — not recorded in the experiment scripts; the inference engine was not reconfigured for this study, so the model's standing deployment settings apply. Flagged rather than asserted.]

## A.7 Superseded claims (v1 → v2 correction, for transparency)

The mechanism attribution went through a correction, recorded here for reproducibility:

- **v1 probe** (recovered 5/6) reported "input complexity as an independent factor, partial r=0.436" and a "604-char threshold."
- **v2 probe** (6 V1 failure cases, mt500→2000, + determinism probe) supersedes this: the mechanism is a *single causal chain* — input complexity → longer reasoning chain → collision with max_tokens → JSON truncation. Input complexity is the *upstream driver* of reasoning-chain length, not an independent additive factor. The "604-char threshold" is a task-type confound (hard tasks have longer chains), not a length boundary.
- The Q04 discrepancy between v1 and v2 is explained: v1 sampled the "short JSON" mode, v2 sampled the "long chain" mode — a run-to-run flip at temperature 0 (instruction-following non-determinism), not a server-state artifact.
- **The Q05 discrepancy is the same phenomenon.** v1 reported Q05 mt2000 = recovered (True); v2 reports Q05 mt2000 = `finish_reason=length`, raw_len 3212, parseable False (convergence failure). Same input, same temperature 0, different probe runs → the judge sampled a short chain in v1 and a long (cycling) chain in v2. We therefore treat the v2 behavior classes (recoverable / borderline / convergence) as the primary attribution and v1's per-case recovery flags as superseded; the *rate* claim (5/6 recoverable in v1) is a single-run estimate, not a stable per-case label. Both v1 and v2 agree on the dominant mechanism: `finish_reason=length` on every mt500 failure case.

The raw v1 numbers remain in `paper-data-table-20261123.md` (data log); the corrected interpretation is in the main text (F2).
