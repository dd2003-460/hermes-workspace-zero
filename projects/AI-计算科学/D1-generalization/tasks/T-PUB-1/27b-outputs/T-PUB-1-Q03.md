

### (a) Dense BF16 Tensor Throughput  
**Answer:** **989.5 TFLOPS**  
**Reason:** The datasheet specifies **1,979 TFLOPS with sparsity**. NVIDIA’s structured sparsity (2:4) typically doubles throughput compared to dense operations. Thus, dense throughput is **1,979 / 2 = 989.5 TFLOPS**.

---

### (b) Machine Ridge Point  
**Formula:**  
$$
\text{Ridge Point} = \frac{\text{Dense FLOPS}}{\text{HBM Bandwidth}}
$$  
**Calculation:**  
- Dense BF16 FLOPS = $989.5 \times 10^{12}$ FLOPS/s  
- HBM Bandwidth = $3.35 \times 10^{12}$ bytes/s  
$$
\text{Ridge Point} = \frac{989.5}{3.35} \approx 295.4 \, \text{FLOP/byte}
$$  
**Answer:** **295.4 FLOP/byte**

---

### (c) Arithmetic Intensity  
**FLOPs:**  
$$
\text{FLOPs} = 2 \times \text{params} \times \text{tokens} = 2 \times 32 \times 10^9 \times 8192 = 5.24288 \times 10^{14}
$$  
**Bytes Moved:**  
- **Weights (FP8):** $32 \times 10^9$ bytes  
- **KV Cache (FP8):**  
  - Per token: $64 \, \text{layers} \times 2 \, (K/V) \times 8 \, \text{heads} \times 128 \, \text{dim} \times 1 \, \text{byte} = 131,072$ bytes  
  - Total: $8192 \times 131,072 = 1.0737 \times 10^9$ bytes  
- **Total Bytes:** $32 \times 10^9 + 1.0737 \times 10^9 = 33.0737 \times 10^9$ bytes  
**Arithmetic Intensity:**  
$$
\frac{5.24288 \times 10^{14}}{33.0737 \times 10^9} \approx 15,850 \, \text{FLOP/byte}
$$  
**Answer:** **15,850 FLOP/byte**

---

### (d) Ratio of Arithmetic Intensity to Ridge Point  
$$
\frac{15,850}{295.4} \approx 53.7
$$  
**Answer:** **53.7**

---

### (e) Compute-Bound or Memory-Bound?  
**Answer:** **Compute**  
**Reason:** The arithmetic intensity (15,850 FLOP/byte) **exceeds** the ridge point (295.4 FLOP/byte), indicating the workload is **compute-bound**.