# Task Card: Pricing & Cost Analysis — GPU Cost-Performance for 35B Inference

**Task ID**: 02-r1-pricing-analysis
**Parent Stage**: 02-r1 (GPU Cost-Performance Research)
**Priority**: P1 — foundational data for all downstream cost-performance calculations
**Estimated Effort**: 2-3 hours of research + 1 hour of analysis
**Required Skills**: Web research, data synthesis, financial modeling

---

## Objective

Build a comprehensive pricing and total-cost-of-ownership (TCO) model for consumer, prosumer, and datacenter GPUs repurposed for 35B-parameter LLM inference. Deliver a **ranked list of hardware options by cost-per-token-per-second ($/token/s)** with confidence intervals, including used market analysis and 3-year TCO.

---

## Research Dimensions

### Dimension 1: Current 2026 Pricing — New Hardware

Collect **current retail prices** from multiple sources (Newegg, Amazon, B&H, Apple Store, eBay new) for the following GPUs. For each item, record:

- **Product name and exact model**
- **Price in USD** (with tax/shipping if applicable)
- **Source URL and date** (must be verifiable)
- **Availability** (in stock, backorder, limited)

| Category | GPU Models |
|----------|-----------|
| Consumer | NVIDIA RTX 4090 (24GB), NVIDIA RTX 5090 (24GB), Mac Studio M4 Max (up to 128GB unified) |
| Prosumer | NVIDIA RTX 6000 Ada (48GB), Mac Studio Max M2/M3 (96GB unified) |
| Datacenter Repurposable | NVIDIA A100 80GB (used), NVIDIA H100 80GB (used) |

**Minimum 2 price sources per product.** If prices vary significantly, record the range and note the most representative price.

### Dimension 2: Cost-Performance Formula — $/token/s

Build a cost-performance model for **35B-parameter LLM inference** at various quantization levels. The formula must compute:

```
$/token/s = (Hardware Cost + 3-Year Power Cost) / (Total Tokens Generated Over 3 Years)
```

Where:

```
Total Tokens = (Tokens/sec at given quantization) × (hours/day used) × 365 × 3
```

**Required calculations for each GPU:**

1. **Quantization analysis**: Compute VRAM/HBM requirements for 35B models at:
   - FP16 (2 bytes/param = ~70GB + KV cache)
   - INT8 (1 byte/param = ~35GB + KV cache)
   - INT4 (0.5 bytes/param = ~17.5GB + KV cache)
   - Determine which quantization levels are feasible per GPU

2. **Inference throughput**: For feasible quantization levels, estimate tokens/sec using:
   - Published benchmarks (MLPerf, LLM inference benchmarks)
   - Memory bandwidth limits: max_tokens/sec ≈ memory_bandwidth_GB/s / bytes_per_token
   - For unified memory (Mac): account for CPU/GPU memory sharing overhead

3. **$/token/s computation**: Apply the TCO formula above for each feasible configuration

**Required input data for the formula:**
- GPU memory bandwidth (GB/s) — from manufacturer specs
- GPU compute throughput (TFLOPS) — from manufacturer specs
- Estimated tokens/sec at each quantization level
- Hours of operation per day (assume 8 hours/day baseline, provide sensitivity at 4h and 24h)
- Electricity rate (assume $0.12/kWh baseline, provide sensitivity at $0.08 and $0.20)

### Dimension 3: Used/Refurbished Market Analysis

Research the **secondary market** for datacenter GPUs:

1. **eBay**: Search for A100 40GB/80GB and H100 80GB listings. Record:
   - Current asking prices (last 30 days, not just current listings)
   - Sold/completed listings (actual transaction prices)
   - Price trend over the last 6-12 months
   - Seller ratings and warranty information

2. **Other used markets**: ServerMonkey, eBay Business, Greenbay, ITAD resellers
   - Compare pricing across platforms
   - Note any bulk pricing discounts

3. **Price trend analysis**:
   - Document whether prices are rising, falling, or stable
   - Identify driving factors (AI demand, supply chain, new product releases)
   - Project prices 6 months and 12 months forward with confidence ranges

**Deliverable**: A used-market price table with source URLs, transaction dates, and trend direction.

### Dimension 4: Power Cost Modeling

Compute **ongoing power costs** for each GPU over a 3-year ownership period:

```
3-Year Power Cost = TDP (watts) × electricity_rate ($/kWh) × hours/day × 365 × 3 / 1000
```

**Required data per GPU:**
- TDP (thermal design power) in watts — from manufacturer specs
- Real-world power draw during inference (if available from benchmarks; otherwise use TDP as upper bound)
- Idle power draw (for 16 hours/day if 8 hours active)
- Electricity rate sensitivity: compute at $0.08, $0.12, and $0.20 per kWh

**Additional considerations:**
- For Mac (Apple Silicon): include full system power, not just SoC TDP
- For datacenter GPUs in consumer rigs: account for PSU efficiency losses (~10-15%)
- Cooling costs in summer months (optional, note as sensitivity)

### Dimension 5: 3-Year Total Cost of Ownership

Combine all dimensions into a **3-year TCO comparison**:

```
3-Year TCO = Purchase Price + 3-Year Power Cost + Maintenance/Replacement Cost
```

**For each GPU, compute:**
1. Purchase price (new and used where applicable)
2. 3-year power cost (at baseline and sensitivity rates)
3. Maintenance cost (assume 2% of purchase price/year for consumer; 5% for datacenter)
4. Resale value at end of 3 years (estimate based on historical depreciation)
5. **Net TCO** = TCO - Resale Value

**Final ranking metric**: Net TCO per token/s of inference throughput

---

## Deliverables

### D1: Price Collection Table (CSV or Markdown)

| GPU | Category | New Price | Used Price | Price Source URLs | Memory | Bandwidth | TDP |
|-----|----------|-----------|------------|-------------------|--------|-----------|-----|

### D2: Cost-Performance Formula Output

| GPU | Quantization | Feasible? | Tokens/sec | $/token/s (8h/day) | $/token/s (24h/day) | Rank |
|-----|-------------|-----------|------------|---------------------|----------------------|------|

### D3: Used Market Analysis Report

- Price table with source URLs and transaction dates
- Trend analysis with driving factors
- Forward price projection with confidence ranges

### D4: Power Cost Summary

| GPU | TDP | 3-Year Power ($0.08) | 3-Year Power ($0.12) | 3-Year Power ($0.20) |
|-----|-----|----------------------|----------------------|----------------------|

### D5: 3-Year TCO Ranking

| Rank | GPU | Net TCO | Tokens/3yr | $/token/s | Confidence |
|------|-----|---------|------------|-----------|------------|

### D6: Executive Summary (1 page)

- Top 3 cost-effective options for 35B inference
- Key assumptions and their impact
- Confidence levels for each ranking
- Recommendations for different use cases (hobbyist, startup, production)

---

## Research Agent Instructions

1. **Start with price collection** — this is the foundation. Without accurate prices, all downstream calculations are meaningless. Use at least 2 sources per product.

2. **Validate feasibility before computing throughput** — if a GPU cannot fit a 35B model at any quantization level, mark it as "not feasible" and skip throughput calculations.

3. **For Mac (unified memory)**:
   - Account for ~10-15% memory overhead for system use
   - Memory bandwidth is significantly lower than discrete GPUs (e.g., M4 Max ~273 GB/s vs RTX 4090 ~508 GB/s)
   - But unified memory allows larger quantization levels that discrete GPUs cannot fit

4. **For used datacenter GPUs**:
   - Factor in potential risk (no warranty, unknown mining/compute history)
   - Consider that A100/H100 in datacenter rigs may require additional infrastructure (cooling, PCIe slot requirements)

5. **Confidence scoring**: For each ranking, assign:
   - **HIGH**: Prices verified from 2+ sources, throughput from published benchmarks
   - **MEDIUM**: Prices from 1 source, throughput estimated from specs
   - **LOW**: Prices from used market only, throughput extrapolated

6. **Sensitivity analysis**: Always provide results at multiple electricity rates and usage hours. The ranking may flip under different assumptions.

---

## Acceptance Criteria

- [ ] All prices have verifiable source URLs (not just "Newegg" without link)
- [ ] Cost-performance formula is explicitly stated and applied consistently across all GPUs
- [ ] Used market analysis includes at least 5 completed transaction records
- [ ] Power costs computed at 3 electricity rate scenarios
- [ ] 3-year TCO includes resale value estimation
- [ ] Final ranking includes confidence intervals (not just point estimates)
- [ ] Executive summary identifies which ranking is most robust to assumption changes

---

## Dependencies

- **Input from**: None (this is a foundational task)
- **Output to**: 02-r1-cost-performance-formula, 02-r1-gpu-pricing, 02-r1-power-thermal
- **Blocking**: None — can proceed in parallel with other 02-r1 tasks

---

## Notes

- This task card assumes a **35B-parameter model** as the target workload. Adjustments for other model sizes should be noted.
- The $/token/s metric is chosen because it directly maps to the economic value of inference hosting — the primary use case for repurposed GPUs.
- If real-time price data cannot be collected (e.g., retailer blocks), use the most recent available data and flag as lower confidence.
