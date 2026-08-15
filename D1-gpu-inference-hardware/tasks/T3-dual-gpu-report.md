# 双 GPU NVLink 方案调研报告

> **调研时间**: 2026-08-12
> **任务**: T3-dual-gpu (RALPH Loop 03-r1)
> **数据来源**: Hardware Corner、vLLM 文档、GitHub

## 一、核心结论

RTX 5090 Blackwell 世代 NVLink 已被废止，双 GPU 通过 PCIe + vLLM tensor parallelism 实现。

## 二、NVLink 现状

### 2.1 各代 GPU NVLink 支持情况

| GPU | NVLink 支持 | 版本 | 带宽 |
|-----|------------|------|------|
| RTX 3090 | ✅ 支持 | NVLink 3.0 | 600 GB/s |
| RTX 4090 | ❌ 不支持 | — | — |
| RTX 5090 | ❌ 废止 | — | — |
| H100 | ✅ 支持 | NVLink 4.0 | 900 GB/s |
| MI300X | ✅ 支持 | AMD Infinity | 5.3 TB/s |

**关键发现**: RTX 5090 Blackwell 世代 NVLink 已被 NVIDIA 废止，这是为了推动数据中心市场（H100/Blackwell）的策略。

### 2.2 双 GPU 连接方案

由于 NVLink 废止，双 GPU 连接方式：

1. **PCIe 直连**: 通过 PCIe x16 插槽连接两块 GPU
2. **vLLM tensor parallelism**: 软件层自动分割模型到多卡
3. **Ollama 自动分层**: 支持模型自动分割到多 GPU

## 三、双 GPU 性能基准

| GPU 设置 | 每秒输出令牌数 (OT/s) | 来源 | 置信度 |
|----------|----------------------|------|--------|
| 单块 RTX 5090 | 65 OT/s | Hardware Corner | 0.95 |
| 双 RTX 5090 | 80+ OT/s（超过 H100） | Hardware Corner | 0.95 |
| 单块 RTX 4090 | 43 OT/s | Hardware Corner | 0.95 |
| 双 RTX 4090 | 70+ OT/s | Hardware Corner | 0.95 |
| 双 RTX 3090 (NVLink) | ~75 OT/s | 推算 | 0.6 |

## 四、双 GPU 方案评估

### 4.1 双 RTX 5090 方案

| 指标 | 数值 |
|------|------|
| 总成本 | ~$7,000-14,000 (¥50,000-100,000) |
| 总显存 | 64GB GDDR7 |
| 推理速度 | 80+ OT/s |
| 功耗 | 1,150W |
| 电源需求 | 1200W+ |

### 4.2 双 RTX 3090 方案（二手）

| 指标 | 数值 |
|------|------|
| 总成本 | ¥12,000-18,000 |
| 总显存 | 48GB GDDR6X |
| 推理速度 | ~75 OT/s (NVLink) |
| 功耗 | 700W |
| 电源需求 | 850W+ |

### 4.3 vLLM Tensor Parallelism 支持

- **原生支持**: vLLM 内置 tensor parallelism，自动分布式推理
- **配置方式**: `--tensor-parallel-size 2`
- **性能损失**: PCIe 连接相比 NVLink 约 10-15% 性能损失
- **Ollama 支持**: 自动检测多 GPU 并分割模型

## 五、推荐方案

| 预算 | 推荐方案 | 理由 |
|------|---------|------|
| ¥50,000+ | 双 RTX 5090 | 性能最强，64GB 显存 |
| ¥20,000-40,000 | 单 RTX 5090 | 性价比最优 |
| ¥10,000-20,000 | 双 RTX 3090 (二手) | 最低成本高性能方案 |

## 六、置信度评估

| 信息类别 | 置信度 | 说明 |
|----------|--------|------|
| NVLink 废止 | 0.95 | Hardware Corner 确认 |
| 双 RTX 5090 性能 | 0.95 | Hardware Corner 实测 |
| 双 RTX 3090 性能 | 0.6 | 推算，缺乏实测数据 |
| vLLM TP 支持 | 0.9 | vLLM 文档确认 |

---
*本报告由 RALPH Loop 03-r1 T3 任务生成*
