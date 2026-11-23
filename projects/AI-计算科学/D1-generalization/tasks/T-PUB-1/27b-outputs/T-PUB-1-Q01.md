

### (a) KV-cache bytes per token  
**Calculation:**  
- Per layer: K and V each have `8 KV heads × 128 head_dim = 1,024 elements`  
- Per layer (K + V): `2 × 1,024 = 2,048 elements`  
- Total layers: `64`  
- Bytes per token: `64 layers × 2,048 elements/layer × 1 byte/element = 131,072 bytes`  

**Answer:** `131,072 bytes/token` (or `128 KiB/token`).  

---

### (b) Total bytes moved per decode step  
**Calculation:**  
1. **Model weights:**  
   - `32B parameters × 1 byte/parameter = 32 × 10⁹ bytes`  
2. **KV cache:**  
   - Total tokens: `16 sequences × 12,288 tokens/sequence = 196,608 tokens`  
   - KV cache size: `196,608 tokens × 131,072 bytes/token = 25,769,803,776 bytes`  
3. **Total bytes:**  
   - `32 × 10⁹ + 25,769,803,776 = 57,769,803,776 bytes`  

**Answer:** `57.77 × 10⁹ bytes` (or `57.77 GB`).  

---

### (c) Aggregate decode throughput  
**Calculation:**  
1. **Effective HBM bandwidth:**  
   - `3.35 TB/s × 0.85 = 2.8475 × 10¹² bytes/s`  
2. **Time per decode step:**  
   - `57.77 × 10⁹ bytes / 2.8475 × 10¹² bytes/s = 0.02028 seconds`  
3. **Throughput:**  
   - `16 tokens/step / 0.02028 seconds/step = 788.9 tokens/s`  

**Answer:** `789 tokens/s` (rounded to 3 significant figures).  

---

### (d) Joules per generated token  
**TDP source:**  
- NVIDIA H100 SXM datasheet specifies **700 W** TDP for the SXM variant [NVIDIA H100 Datasheet, Section 2.1].  
**Calculation:**  
- Power = `700 W = 700 J/s`  
- Energy per token: `700 J/s / 788.9 tokens/s = 0.887 J/token`  

**Answer:** `0.887 J/token` (using **700 W TDP** from NVIDIA H100 SXM datasheet).  

---

### (e) Memory fit and headroom  
**Calculation:**  
1. **Total memory usage:**  
   - Weights: `32 GB`  
   - KV cache: `25.77 GB`  
   - Runtime overhead: `4 GB`  
   - **Total:** `32 + 25.77 + 4 = 61.77 GB`  
2. **Headroom:**  
   - `80 GB - 61.77 GB = 18.23 GB`  

**Answer:**  
- **Fits in 80 GB** (yes).  
- **Leftover headroom:** `18.23 GB`.  

---

### Summary of Results  
| Metric | Value |  
|--------|-------|  
| (a) KV-cache bytes/token | `131,072 bytes` |  
| (b) Bytes per decode step | `57.77 × 10⁹ bytes` |  
| (c) Decode throughput | `789 tokens/s` |  
| (d) Joules/token | `0.887 J/token` (TDP = 700 W) |  
| (e) Memory fit | **Yes**, with `18.23 GB` headroom |