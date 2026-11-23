

### (a) HBM Capacity with Source  
**141 GB** (141 × 10⁹ bytes)  
Source: [NVIDIA H200 SXM Datasheet](https://www.nvidia.com/en-us/data-center/h200/) (Section: "Memory", "141 GB HBM3e")  

---

### (b) KV-Cache Bytes per Token  
- **Layers**: 80  
- **KV Heads**: 8  
- **Head Dimension**: 128  
- **Precision**: FP8 (1 byte per element)  
- **K and V**: 2 tensors per token  

**Calculation**:  
\[
\text{Bytes/token} = 80 \times 8 \times 128 \times 2 \times 1 = 163{,}840 \text{ bytes}
\]  
**Answer**: **163,840 bytes/token**  

---

### (c) KV Pool Size in Bytes  
- **Total HBM**: 141 × 10⁹ bytes  
- **Weights (FP8)**: 70 × 10⁹ bytes  
- **Runtime Overhead**: 6.5 × 10⁹ bytes  

**Calculation**:  
\[
\text{KV Pool} = 141 \times 10^9 - 70 \times 10^9 - 6.5 \times 10^9 = 64.5 \times 10^9 \text{ bytes}
\]  
**Answer**: **64,500,000,000 bytes**  

---

### (d) Maximum KV Tokens in Pool  
\[
\text{Max Tokens} = \frac{64.5 \times 10^9}{163{,}840} \approx 393{,}664.0625
\]  
**Answer**: **393,664 tokens** (integer truncation)  

---

### (e) Largest Batch Size at 8,192 Tokens/Sequence  
\[
\text{Batch Size} = \left\lfloor \frac{393{,}664}{8{,}192} \right\rfloor = \left\lfloor 48.05 \right\rfloor = 48
\]  
**Answer**: **48**  

---

### (f) Does Batch 64 at 8,192 Tokens Fit?  
- **Required Tokens**: \(64 \times 8{,}192 = 524{,}288\)  
- **Available Tokens**: 393,664  
- **Comparison**: \(524{,}288 > 393{,}664\)  

**Answer**: **No** (exceeds KV pool capacity by 130,624 tokens)