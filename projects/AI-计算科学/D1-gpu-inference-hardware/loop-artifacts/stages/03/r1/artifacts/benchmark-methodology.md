# LLM Benchmark Methodology

> **Version 1** (2026-08-18)
>
> Produced by T02 — Unified LLM Benchmark Methodology Documentation.
>
> **Context**: Stage 02.5 cross-validation revealed that LLM benchmark numbers for the same GPU can vary 10-70x depending on measurement methodology. This document defines the standardized comparison framework for all subsequent T02-T07 branches of the DAG.

---

## Why This Matters

Stage 02.5 cross-validation (02.5-r1) found the following discrepancies for otherwise comparable claims about the same hardware:

| GPU | Claim A (sources [1], [2]) | Claim B (source [3]) | Ratio |
|---|---|---|---|
| H100 | 250-300 tok/s (13B-70B FP16, real-world conditions) | 21,800 tok/s (Llama 2 70B, TensorRT-LLM FP8, optimal batch) | **~70x** |
| H200 | N/A (new product) | 31,700 tok/s (Llama 2 70B, TensorRT-LLM FP8, optimal batch) | N/A |
| A100 | 130 tok/s (13B-70B FP16, real-world conditions) | 1,200-1,500 tok/s (Llama-7B FP16, synthetic conditions) | **~10x** |
| RTX 4090 | 120-140 tok/s (13B-70B FP16, real-world conditions) | ~1,000+ tok/s (Llama-7B FP16, synthetic conditions) | **~10x** |
| RTX 5090 | 5,841 tok/s (Qwen2.5-Coder-7B Q4_K_M) | N/A | Single data point |
| Cerebras | 750 tok/s (GPT-5.6 Sol Ultrafast, official page) | 1,800-3,000 tok/s (peak claims) | **~2-4x** |

**Conclusion from 02.5**: LLM benchmark numbers are meaningless without full methodology disclosure. This document standardizes how all comparisons are performed and reported.

---

## Methodology

### Framework

All GPU models in this study are compared using a consistent set of measurement conditions. Each benchmark is reported with the **full parameter context**, never as a single scalar. The comparison framework has three layers:

1. **Standardized test matrix**: A defined set of model/quantization/context-size combinations.
2. **Measured metrics**: Each combination is evaluated on 4 core metrics.
3. **Methodology tags**: Every reported number includes tags identifying which framework, batch configuration, and measurement methodology produced it.

This "full context + standard matrix + tagging" approach means any two numbers from any sources can be directly compared or flagged as incomparable.

### Standard Test Matrix

Every GPU model is benchmarked against the following 5-cell test matrix. Each cell has a defined prompt length, generation length, batch size, and expected workflow (prefill-heavy, decode-heavy, or balanced).

| Cell ID | Model | Quantization | Prompt Len | Generation Len | Batch Size |
|---------|-------|-------------|------------|----------------|------------|
| S-7B | Llama 3.1 8B | FP16 (baseline) | 256 tokens | 256 tokens | 1 (latency), 128 (throughput) |
| S-13B | Llama 3.1 8B | FP16 (baseline) | 256 tokens | 256 tokens | 1 (latency), 64 (throughput) |
| B-8B | Llama 3.1 8B | FP8 / INT8 / INT4 | 256 tokens | 256 tokens | 1 (latency), 256 (throughput) |
| B-70B | Llama 3.1 70B | FP16 / FP8 | 256 tokens | 256 tokens | 1 (latency), 16 (throughput) |
| L-7B | Llama 3.1 8B | FP16 (baseline) | 2048 tokens | 2048 tokens | 1 (latency), 8 (throughput) |

Key decisions for the test matrix:
- **Prompt length 256**: This is the common real-world user prompt length. At 256 input tokens, prefill and decode are roughly equal in total compute — this tests balanced workload.
- **Prompt length 2048**: Tests long-context and long-generation scenarios where decode dominates. Pre-fill accounts for ~10% of total latency. This isolates pure decode performance.
- **Batch size 1**: Measures p50 latency (what individual users experience).
- **Large batch sizes**: Measures aggregate system throughput (what the datacenter cares about).

### Measurement Protocol

All measurements use the same hardware configuration and software baseline unless noted:

**Hardware**: Each GPU is tested on its standard form factor (SXM4/SXM5 or PCIe), with the highest-speed interconnect available for multi-GPU configs (NVLink Gen4 for A100/H100, PCIe for consumer GPUs).

**Software stack (baseline)**: vLLM 0.6+ with PagedAttention, auto-tuned kernels. This is the default choice because it achieves the highest throughput across most GPU families while maintaining correctness. The actual choice is determined per-GPU in T02 research (a given GPU may have a better native toolchain — e.g., TensorRT-LLM for NVIDIA, ROCm for AMD — which should be used instead).

**Software stack (optimal benchmark)**: For "optimal" (best-case) benchmark reporting, use the GPU manufacturer's recommended native stack: TensorRT-LLM for NVIDIA GPUs, ROCm vLLM for AMD Instinct, etc.

Both baseline and optimal benchmarks must be reported for each GPU, enabling readers to assess the margin between "easily achievable" and "peak."

---

## Standardized Models

All benchmark comparisons use models from this canonical set. Models are listed by parameter count for easy lookup; the actual model with checkpoint URL and recommended quantization are listed in the annex.

### Core Model Set

| ID | Model | Parameters | Layers | Hidden Dim | Attention Heads | Supported Precisions |
|----|-------|-----------|--------|------------|-----------------|---------------------|
| M-8B | Llama 3.1 8B | 8.03B | 32 | 4096 | 32 (GQA × 8) | FP16, BF16, FP8, INT8, INT4 |
| M-70B | Llama 3.1 70B | 70.6B | 80 | 8192 | 64 (GQA × 8) | FP16, BF16, FP8, INT8, INT4 |
| M-405B | Llama 3.1 405B | 405.5B | 126 | 16384 | 128 (GQA × 8) | FP16, BF16, INT8 (FP8 untested at this scale) |
| M-3B | Qwen 2.5 3B | 3.09B | 28 | 2048 | 24 (GQA × 8) | FP16, BF16, INT8, INT4 |
| M-14B | Qwen 2.5 14B | 14.73B | 48 | 5120 | 40 (GQA × 8) | FP16, BF16, INT8, INT4 |

### Why These Models

- **Llama 3.1 series**: Most widely deployed open-weight model family. Architectural features (GQA, rope scaling, modern block structure) are representative of 2024-2025 class models. Supports widest range of precisions including FP8.
- **Qwen 2.5 series**: Dominant non-Llama family in Chinese/Asian markets (per this project's China-market research task). Similar architecture makes fair GPU comparison possible.
- **8B class**: Fits in single consumer GPU (24GB), most common for edge/local inference.
- **70B class**: Requires multi-GPU (8×24GB or 2×80GB), represents the "datacenter GPU" workload.
- **405B class**: Requires multi-GPU with heavy parallelism, tests interconnect-bound scenarios.

### Quantization Levels

Quantization changes the problem from a throughput measurement to a combined bandwidth+compute measurement, and must be tracked separately for each level:

| Level | Storage (per parameter) | Impact on memory-bound inference |
|-------|------------------------|----------------------------------|
| FP16 / BF16 | 16 bits | Baseline. Hardware fully optimized for this precision on all GPU generations. |
| INT8 | 8 bits | 2x memory bandwidth reduction. Near-lossless for most workloads (<1% perplexity impact). Supported on all modern GPUs. |
| FP8 (E4M3) | 8 bits | NVIDIA H100+ hardware Tensor Core support. Same precision benefits as INT8. |
| INT4 | 4 bits | 4x memory bandwidth reduction. ~1-3% perplexity impact with quantization-aware training; up to 5-10% with post-training quantization. |
| INT2 | 2 bits | Emerging; significant perplexity impact. Primarily for very large models (70B+) on memory-constrained hardware. |

All benchmark numbers MUST include the quantization level in the methodology tag. **Benchmarking FP8 at peak performance while reporting INT4 or FP16 for other GPUs is not a fair comparison.**

### Emerging Architecture Models

For non-GPU architectures (Groq, Cerebras, SambaNova), model support differs due to proprietary constraints:

| ID | Model | GPU-supported quantization | Non-GPU platform constraints |
|----|-------|---------------------------|------------------------------|
| EA-GROQ | Llama 3 70B | N/A (integrated memory) | Groq uses LPUs with integrated SRAM — does not share common measurement framework |
| EA-CB | Llama 3 70B | N/A (wafer-scale) | Cerebras uses WSE-3 — does not share common measurement framework |
| EA-SN | Llama 3 8B | N/A (DataCore) | SambaNova uses DataScale architecture |

These can only be compared on **output tokens/s at batch=1** for a single standard model (8B FP16). Fine-grained per-metric comparison is not meaningful.

---

## Metrics

### 1. Tokens/Second — Decode (Output Throughput)

**Definition**: Number of output tokens produced per second during autoregressive generation, measured after the first token.

**Formula**:

```
decode_throughput = num_output_tokens / (time_last_token - time_first_token)
```

**Measurement protocol**:
- Use **warm-up period** of 10 generations before measurement to ensure GPU state is stabilized ( Tensor Core clock, memory state, etc.).
- Measure over at least 50 consecutive output tokens to reduce variance below 2%.
- Report the **mean decode throughput** with **95% confidence interval**.
- Use batch size 1 for the "per-user latency equivalent" number and the defined batch sizes for "system throughput."

**This is the metric to use when**: comparing hardware for real-world latency-sensitive services (chat, agent loops). The per-user experience depends almost entirely on decode throughput.

**Limitations**:
- Prefill time is ignored — at short prompt lengths this may dominate user-visible latency.
- Large batch sizes change memory access patterns. Compare batch sizes carefully.

### 2. Tokens/Second — Prefill (Input Processing)

**Definition**: Number of prompt tokens processed per second during the prefill phase (tokenizing + attending to the full context + generating first output token).

**Formula**:

```
prefill_throughput = num_prompt_tokens / (time_first_output_token - time_request_start)
```

**Measurement protocol**:
- Report at **fixed prompt lengths**: 256, 2048, 8192, 32768 tokens.
- Use **wall-clock time** from request submission to first output token appearance.
- Report mean over 10 runs with different random prompt content (to avoid worst-case attention patterns).
- **Always report the prompt length alongside the prefill throughput number.** Prefill throughput degrades with sequence length due to attention O(n²) complexity — a 2048-token prefill may be 20x slower per-token than a 256-token prefill.

**This is the metric to use when**: comparing GPU memory bandwidth for processing long documents, agent system prompts, or RAG-augmented inputs.

**Limitations**:
- Prefill throughput is largely a bandwidth + matrix multiplication problem — results vary heavily with kernel fusion, KV cache management, and sequence packing.
- Different inference frameworks (vLLM vs TGI vs vLLM with speculative decoding) can have significantly different prefill performance for the same hardware.

### 3. $ / Token (Cost Efficiency)

**Definition**: Dollar cost per output token, for both local hardware deployment and cloud API invocation.

**Formula (local)**:

```
$_per_output_token = GPU_hourly_cost / (decode_throughput * 3600)
```

**Formula (cloud API)**:
- Extract from the provider's published pricing per 1M tokens, divide by 1,000,000.

**Measurement protocol**:
- For **local hardware**, use **depreciated hardware cost per hour** (purchase price / total expected lifetime compute). Example: H100 SXM 80GB at $35,000 with a 3-year lifetime at 70% utilization:
  ```
  hourly_cost = $35,000 / (3 * 365 * 24 * 0.7) = $2.52/hr
  ```
- For **cloud APIs**, use the latest published on-demand price. API prices change rapidly and may differ between providers.
- **Include all overheads**: For cloud APIs, this is just the model provider price. For local deployment, this should be amortized hardware cost + electricity (0.10-0.15 USD/kWh typical datacenter rate).
- Always state the **effective decode throughput** used in the denominator — different batch sizes produce different cost per token.

**This is the metric to use when**: comparing cost-effectiveness of different GPU families for deployment planning. The most compelling metric for business decisions.

**Limitations**:
- Different prompt-to-response ratios invalidate cross-model comparisons (1B-token vs 70B-token models have different $/tok at same throughput).
- Electricity cost varies by datacenter location.
- Amortization assumptions (GPU lifetime, utilization) significantly affect the result.

### 4. ms/token (User-Visible Latency)

**Definition**: Milliseconds from each output token to the next, measured by end users.

**Measurement protocol**:
- This is simply **1000 / decode_throughput** for batch=1.
- Must distinguish from **TTFT (Time to First Token)**:
  - TTFT includes the prefill phase: prompt processing + first decode iteration.
  - Subsequent token latency = decode iterations only.
- For real user-experience measurements:
  - Report both TTFT and per-token latency separately.
  - For TTFT, report at **batch size 1** (real user sees one request at a time).

**Typical sensitivity**:
- For Llama 3 8B on H100 at batch=1: TTFT ~5-10ms (prefill at 256 tokens is negligible), subsequent tokens ~1-2 ms/tok (500-1000 tok/s).
- For Llama 3 70B on H100 at batch=1: TTFT ~20-50ms, subsequent tokens ~3-10 ms/tok (100-300 tok/s).
- These vary drastically depending on the serving framework.

**This is the metric to use when**: assessing UX quality — people perceive degradation when per-token latency exceeds ~100ms and interruption when TTFT exceeds ~500ms.

**Limitations**:
- User experience also depends on **jitter** (variance in token-by-token latency). A GPU with 5ms/token mean but 200ms spike is worse than one with 10ms/token steady.
- **Batch-induced latency**: concurrent requests increase per-request latency. Report latency curves (ms/token vs concurrent requests).

---

## Normalization Rules

### Rule 1: Always Report Methodology Tags

Every benchmark number MUST include a methodology tag string, formatted as follows:

```
{GPU}_{Model}_{Quant}_{PromptLen}_{GenLen}_{Batch}_{Framework}_{Optimal}
```

Examples:
- `H100_Llama3.1-8B_FP16_256_256_batch1_vLLM_optimal` — H100 running Llama 3.1 8B FP16, 256 prompt / 256 generation, batch=1, vLLM framework, using optimal (non-standard) kernel settings
- `RTX4090_Llama3.1-70B_FP8_256_256_batch16_TRT-LLM_baseline` — RTX 4090 running Llama 3.1 70B FP8, 256 prompt / 256 generation, batch=16, TensorRT-LLM framework, baseline settings
- `A100_Llama3.1-70B_FP16_2048_2048_batch1_vLLM_baseline` — A100 running Llama 3.1 70B FP16, 2048 prompt / 2048 generation, batch=1, vLLM framework

### Rule 2: Separate Prefill and Decode

Never report a single "throughput" number without specifying whether it measures prefill, decode, or an aggregate. If an aggregate is reported (e.g., total tokens / total time), the prompt length and generation length must be explicitly given.

**Correct**: "H100 Llama-8B FP16, prefill at 2048 prompt: 12,500 tok/s; decode at batch=64: 2,800 tok/s"

**Incorrect**: "H100 Llama-8B: 2,800 tok/s" (unspecified: prefill or decode? batch size? prompt length?)

### Rule 3: Same Precision Comparisons

When comparing GPU families, each must be benchmarked at the **same precision level**. H100's FP8 advantage is only meaningful when:
1. All GPUs being compared support FP8 Tensor Cores.
2. Model weights are quantized to FP8 with validated accuracy.
3. The prefill phase at FP8 is also measured (many tools still default to FP16/FP32 for KV cache and attention even when the matrix multiply uses FP8).

For GPUs that do not natively support FP8 (RTX 4090, A100, older AMD), compare at their native optimal precision (INT8 or FP16).

### Rule 4: Acknowledge Framework Differences

Different serving frameworks implement fundamentally different optimization levels for the same hardware. This list captures the major known sources of variance (based on cross-validation from stage 02.5):

| Framework | Typical Advantage | Typical Disadvantage | Notes |
|-----------|-------------------|---------------------|-------|
| vLLM (default) | Broad hardware support, PagedAttention, dynamic batching | Not all kernels auto-tuned for every GPU | Default choice for comparisons |
| TensorRT-LLM | Highest absolute throughput on NVIDIA GPUs | NVIDIA-only; compile time for kernel optimization | GPU-vendor-recommended "optimal" stack for NVIDIA |
| HuggingFace TGI (vLLM backend) | Production-ready, simple setup | Higher infrastructure overhead | Same as vLLM for core compute |
| Ollama (llama.cpp backend) | Extreme simplicity, GGUF support | Python overhead, less aggressive optimization | Popular for consumer/local inference |
| LM Studio | GUI-first local inference | Least performance-optimized | Used primarily for evaluation, not production |
| Speculative decoding (EAGLE, Medusa) | 2-5x decode speedup on CPU-assisted setups | Requires drafting model, complex deployment | Research-grade; affects benchmark comparability |
| DistAttention (distillation-accelerated) | Measured speedups reported by the Vidas Py team | Proprietary; accuracy verification needed | Emerging; needs independent verification |

If a source reports numbers without specifying which framework was used, the methodology tag must include `[framework=unknown]` and the result should be flagged as incomparable with framework-specific benchmarks.

### Rule 5: Acknowledge Tokenizer Variance

Different implementations of the same model may tokenize differently, producing different token counts for the same text. This can change per-token benchmark numbers by 5-20%.

**Primary sources of tokenizer variance**:
- **Chat template differences**: vLLM's default chat template for Llama 3.1 may produce different prompt token counts than Ollama's template. Since token-level benchmarks (tok/s) are measured per-token, different token counts shift the denominator.
- **Tokenizer version**: tokenizer revisions (even within the same repo) can tokenize differently.
- **Subword tokenization edge cases**: Different implementations may split the same text differently at edge cases (e.g., special Unicode, URLs, code blocks).

**Mitigation**: Report token counts for both the input prompt and the output text alongside throughput. Report: "tokens generated = N, total wall time = T, throughput = N/T." Also provide the raw input text and the tokenizer repo reference used.

### Rule 6: Consistent Context Length Reporting

**Attention is O(n²)**. Throughput varies inversely with sequence length for prefill, and linearly for decode (with KV cache). Always state the sequence length for the reported metric.

- **Prompt length**: Critical for prefill comparison. Always report the input prompt length.
- **Generation length**: For per-token latency (ms/token), generation length does not matter (stateless between tokens). For decode throughput, generation length can affect memory pressure when KV cache fills.
- **Total context length**: For very long sequences (>32K tokens), RoPE scaling and KV cache memory usage change. Note whether LongRoPE / rotary extension is active.

**Standard prompt lengths for prefill benchmarking**: 256, 1024, 2048, 8192 tokens. Benchmark at ALL four if possible, or at minimum at 256 and 2048.

---

## Known Limitations

### 1. FP8 Precision Gap

Only NVIDIA H100/H200 and AMD MI300X offer native FP8 Tensor/Core support. The RTX 4090, RTX 5090, and A100 do not support FP8 at the hardware level (they can run FP8-math via FP32 accumulators, but with different performance characteristics). This means:
- When H100 achieves 31,700 tok/s (FP8, TensorRT-LLM, optimal) vs 250-300 tok/s (FP16, realistic conditions), comparing FP8 results to FP16 results is not fair — they measure different computational precision.
- For multi-GPU comparisons, using the optimal precision for each GPU introduces "cherry picking" — compare at the lowest-common-denominator precision for apples-to-apples comparison.

### 2. Quantization Accuracy

INT4 and lower quantization levels introduce perplexity degradation that is model-dependent. Models designed with quantization-aware training (QAT) degrade less than post-training quantized (PTQ) models. Most benchmark sources do not disclose:
- Whether PTQ or QAT was used.
- Whether accuracy was validated (perplexity, MMLU, or downstream task performance).
- What specific quantization library was used (AWQ, GPTQ, bitsandbytes, llama.cpp's GGUF).

Without these details, two INT4 benchmarks for the same model may measure very different effective precisions.

### 3. Memory-Bound vs Compute-Bound Regimes

LLM inference moves from compute-bound to memory-bound as model size increases or precision decreases:
- **7B models on consumer GPUs**: Can be compute-bound with high quantization (INT4), or memory-bound with FP16.
- **70B models on single datacenter GPUs**: Almost always memory-bound regardless of precision.
- **Inter-GPU models**: Communication bandwidth (NVLink, PCIe) becomes the bottleneck for attention computation, adding a new complexity not captured in single-GPU benchmarks.

Comparing a compute-bound result (7B INT4 on RTX 4090) to a memory-bound result (70B FP8 on H100) does not reveal which hardware limits are real for deployment.

### 4. Temperature and Sampling Effects

The decode throughput measurement depends on the sampling temperature, top-p, and top-k settings used during generation:
- **Greedy decoding (temperature=0)**: Fastest possible decode throughput. No sampling overhead.
- **Standard decoding (temperature=1.0, top_p=0.9)**: Has minor sampling overhead (typically <1%).
- **High-temperature sampling**: Can increase throughput marginally by generating shorter outputs (e.g., higher randomness leads to earlier stopping tokens), but this is inconsistent.

Most public benchmarks use temperature=1.0 for realism. For consistent comparisons, use the same sampling parameters across all benchmarks.

### 5. Real-World vs Synthetic Workloads

Benchmark numbers change significantly when measured against real-world vs synthetic workloads:
- **Synthetic workloads**: Sequential "run 100 generations of 256 tokens each" measure maximum capabilities.
- **Real-world workloads**: Concurrent user requests with variable prompt lengths, variable output lengths, system prompt injection (RAG, tools), and batch-induced latency (queuing, scheduling).
- **Example**: H100 reported 21,800 tok/s at optimal batch for Llama 70B — but at realistic concurrent load with mixed prompt lengths, real throughput may be 5-10x lower.

### 6. GPU Utilization (Effective vs Theoretical)

GPU utilization in inference workloads is significantly lower than in training workloads, due to:
- Memory-bound execution (Tensor Cores idle waiting for memory)
- Streaming data and token generation sequentiality
- Low parallelism in attention vs matrix multiply
- Memory bandwidth as primary bottleneck (not compute)

**Report "compute utilization" alongside throughput** when possible. GPU utilization figures in benchmarks are frequently undisclosed and can range from 5% to 80% for inference workloads.

### 7. KV Cache Management

The KV cache is the single largest memory consumer in autoregressive inference:
- For Llama 3 8B at batch=128 with 4K context: KV cache uses approximately 8.4GB.
- For Llama 3 70B at batch=16 with 4K context: KV cache uses approximately 74GB.
- PagedAttention (vLLM) reduces fragmentation but does not reduce total memory usage.
- FlashAttention (during prefill) avoids KV cache matmul computation, reducing memory bandwidth pressure for long prompts.

KV cache size directly limits the maximum batch size — the throughput benchmarks at maximum batch size are constrained by KV cache, not by matrix compute.

### 8. Emerging and Proprietary Architecture Comparability

Non-GPU architectures (Groq LPU, Cerebras WSE-3, SambaNova DataScale) use fundamentally different designs:
- **Groq**: Synchronous design with 130K cores at 600MHz — no cache misses, deterministic latency. Comparing throughput vs NVIDIA GPU throughput is not meaningful because the compute/memory architecture is entirely different.
- **Cerebras**: Wafer-scale memory (912KB) and compute (800K cores) — "infinite" memory bandwidth from the GPU perspective. Throughput numbers may be higher or lower than GPU depending on model fit.
- **SambaNova**: Custom DataScale fabric with per-model hardware configuration.

These architectures should only be compared at the **system level**: $/output-token at a given latency percentile, rather than prefill/decode throughputs or $/month at the accelerator level.

---

## Annex: Source List and Verification Status

The following sources informed this document:

| # | Source | URL | Relevant Data | Verification |
|---|--------|-----|--------------|-------------|
| [1] | computeprices.com GPU guide | https://computeprices.com/blog/best-gpus-for-ai-inference-performance-vs-price | H100 250-300 tok/s (realistic), A100 130 tok/s, RTX 4090 120-140 tok/s, RTX 5090 5,841 tok/s | Partially confirmed by cross-validation |
| [2] | slyd.com inference GPU guide | https://slyd.com/guides/inference-gpu-guide | H200 31,700 tok/s (TensorRT-LLM FP8, optimal), H100 21,800 tok/s (TensorRT-LLM FP8, optimal) | Cross-validated: H200 numbers confirmed, H100 batch-level methodology documented |
| [3] | OpenRouter Speed Test | https://openrouter.ai/docs/speed-test | Framework comparison benchmark showing tokenizer, prefill, and decode variations across vLLM/TGI/Ollama | Framework differences documented in methodology section |
| [4] | Open LLM Leaderboard Speed | https://huggingface.co/spaces/open_llm_leaderboard/speed | Standard 2048-token prefill measurement with 2-token generation, comparing HF + vLLM, HF + TGI, Ollama | Methodology: 2048 prefill, standard tokenizer, consistent hardware configuration |
| [5] | LM Sys / Chatbot Arena Speed Test | https://lmsys.org/blog/2023-06-28-leaderboard/ | API provider speed comparison, TTFT measurement methodology | Measures per-provider latency at batch=1 using standard test prompts |
| [6] | NVIDIA H100 spec page | https://www.nvidia.com/en-us/data-center/h200/ | 1,979 TFLOPS dense FP16, 989 TFLOPS sparse FP16, 141GB HBM3e, 4.8 TB/s bandwidth | Confirmed by cross-validation |
| [7] | AMD MI300X spec page | https://www.amd.com/en/products/accelerated-processing-unit/instinct-mi300x.html | 192GB HBM3, 5.3 TB/s bandwidth, self-reported LLM benchmark 30-40+ tok/s 70B | Inference numbers unverified by independent third party |
| [8] | Groq LPU platform page | https://groq.com/platform | 1,000 tok/s/user per-user guarantee | Confirmed cross-validation |
| [9] | Cerebras GPT-5.6 | https://www.cerebras.ai/ | 750 tok/s (not peak 1800-3000 tok/s) | Confirmed lower than stage 02 peak claims |
| [10] | SpecBench (arXiv:2410.10527) | https://arxiv.org/abs/2410.10527 | TTFT and TPOT benchmarking methodology for speculative decoding | Documented for TTFT methodology reference |
