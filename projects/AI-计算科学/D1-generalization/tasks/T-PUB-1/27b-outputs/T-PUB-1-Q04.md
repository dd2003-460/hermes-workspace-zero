

### (a) H100 SXM Datasheet Specifications  
- **HBM Capacity per GPU**: 80 GB  
- **HBM Bandwidth per GPU**: 3.35 TB/s  
- **Source URL**: [NVIDIA H100 Datasheet](https://www.nvidia.com/en-us/data-center/h100/)  
- **Why Not NVL Numbers?**: The problem explicitly specifies **SXM5 form factor** (not H100 NVL). H100 NVL has different HBM capacity/bandwidth (e.g., 94 GB HBM3e for NVL), but SXM5 uses **80 GB HBM3** and **3.35 TB/s** as per the official datasheet.  

---

### (b) Weight Bytes per GPU  
- Total model parameters: 405B (405 × 10⁹)  
- FP8 precision: 1 byte/parameter  
- Total weight size: 405 × 10⁹ bytes  
- Tensor parallelism (TP=8): Sharded evenly across 8 GPUs  
- **Weight bytes per GPU**:  
  \[
  \frac{405 \times 10^9}{8} = 50.625 \times 10^9 \text{ bytes} = 50.625 \text{ GB}
  \]

---

### (c) KV-Pool Bytes per GPU  
- **Available memory per GPU**:  
  \[
  80 \text{ GB (HBM)} - 50.625 \text{ GB (weights)} - 5.5 \text{ GB (overhead)} = 23.875 \text{ GB}
  \]  
- **KV-pool bytes per GPU**:  
  \[
  23.875 \times 10^9 \text{ bytes} = 23.875 \text{ GB}
  \]

---

### (d) KV Bytes per Token (Per GPU, After Sharding)  
- **Per-layer KV size (unsharded)**:  
  - K and V: 2 tensors  
  - KV heads: 8  
  - Head dimension: 128  
  - FP8: 1 byte/element  
  \[
  2 \times 8 \times 128 \times 1 = 2048 \text{ bytes/layer/token}
  \]  
- **Sharded across 8 GPUs (TP=8)**:  
  \[
  \frac{2048}{8} = 256 \text{ bytes/layer/token/GPU}
  \]  
- **Total KV bytes per token (126 layers)**:  
  \[
  256 \times 126 = 32,256 \text{ bytes/token/GPU}
  \]

---

### (e) Largest Integer Batch at 16,384 Tokens/Sequence  
- **KV size per sequence (per GPU)**:  
  \[
  16,384 \text{ tokens} \times 32,256 \text{ bytes/token} = 528,482,304 \text{ bytes} \approx 528.48 \text{ MB}
  \]  
- **Max batch size**:  
  \[
  \left\lfloor \frac{23.875 \times 10^9 \text{ bytes}}{528,482,304 \text{ bytes/sequence}} \right\rfloor = \left\lfloor 45.17 \right\rfloor = 45
  \]  
- **Answer**: **45**

---

### (f) Does Batch 8 at 16,384 Tokens Fit?  
- **KV size for batch 8**:  
  \[
  8 \times 528.48 \text{ MB} = 4,227.84 \text{ MB} \approx 4.23 \text{ GB}
  \]  
- **Total memory per GPU**:  
  \[
  50.625 \text{ GB (weights)} + 4.23 \text{ GB (KV)} + 5.5 \text{ GB (overhead)} = 60.355 \text{ GB}
  \]  
- **HBM capacity**: 80 GB  
- **Conclusion**: **Yes**, batch 8 fits (60.355 GB < 80 GB).  

---

### Final Answers  
(a) **80 GB HBM, 3.35 TB/s** ([NVIDIA H100 Datasheet](https://www.nvidia.com/en-us/data-center/h100/)); SXM5 specified, not NVL.  
(b) **50.625 GB**  
(c) **23.875 GB**  
(d) **32,256 bytes**  
(e) **45**  
(f) **Yes**