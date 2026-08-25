# 任务板

| ID | 任务(目标) | 状态 | 优先级 | 依赖 | 背景 |
|----|-----------|------|--------|------|------|
| T-kv-cache-hw | KV Cache 硬件优化：片上 SRAM 缓存 / 专用 KV 存储 / PagedAttention 硬件化 | pending | P1 | | KV cache 是 LLM 推理最大内存瓶颈，当前任务图未覆盖硬件级 KV cache 优化 |
| T-speculative-hw | 推测解码硬件加速：小模型加速器 + 快速验证单元设计空间探索 | pending | P2 | | 推测解码可提升 2-4x 吞吐量，需硬件支持，当前任务图未覆盖 |
| T-cxl-memory-hw | CXL 内存扩展硬件架构：CXL 3.0 用于 LLM 推理的内存池化与权重流式传输 | pending | P2 | | AMD MI300X / NVIDIA H200 已支持 CXL 3.0，当前任务图未覆盖 |
| T-verify-specs | 交叉验证 uncertain claims：H100/MI300X/H200 规格、HBM3e/4 带宽、Tensor Core 利用率 | pending | P1 | | 04.5 阶段 30 claims 中 23 条 uncertain，需权威来源验证 |
| T-gpu-research | GPU 调研：主流 GPU 硬件规格对比（H100/MI300X/H200/A100/RTX 5090/4090）、推理性能基准、价格/性价比分析、新兴架构（Groq、Cerebras、SambaNova） | pending | P1 | | 全局任务板新增：系统性 GPU 调研覆盖硬件选型、性能基准、成本分析 |
