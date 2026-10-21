# 8G 显存（RTX 4060）7B LLM LoRA 微调全流程 — 子任务清单（思考预算版）

| # | 子任务 | 验证标准 | 工作量 |
|---|--------|----------|--------|
| 1 | 环境与基线：装 CUDA + PyTorch + transformers + PEFT + bitsandbytes，4bit 量化加载 7B 基座做推理冒烟，并跑一次基座评估留作对照 | `load_in_4bit=True` 加载成功且生成 1 段连贯文本；`torch.cuda.max_memory_allocated()` < 7.5G；基座在验证集上的指标已记录到 `baseline.json` | S |
| 2 | 数据：选定 1 个具体任务，收集并清洗 2k–5k 条样本，统一为 alpaca 格式 JSONL，固定 seed 划分 90/10 train/val，写校验脚本 | 校验脚本断言通过（字段齐全、无重复、长度分布正常）；`python check_data.py` 退出码 0；train/val 划分可用 seed 一键复现 | S |
| 3 | 训练：QLoRA（r=16, α=32, 全 attention 层 + down_proj），gradient checkpointing，batch=1 + 梯度累积 16，max_seq_len=2048，训 2 epochs | 训练全程无 OOM 且无 NaN；val loss 相对基线下降 >5%；最终 LoRA adapter 文件落盘（<200MB）可被 `from_pretrained` 重新加载 | M |
| 4 | 评估 + 合并：同一验证集上基座 vs 微调后对比，达标后 `merge_and_unload` 导出全量权重并转 GGUF 4bit | 对比表格中微调模型目标指标严格优于基座；导出 `model.gguf` 可被 llama.cpp 正常加载 | M |
| 5 | 部署 + 可复现交付：llama.cpp（或 vLLM 4bit）起服务暴露 `/v1/chat/completions`，把 1–4 步整合为单一 notebook（锁 `requirements.txt` + seed + 硬件假设） | 干净机器按 notebook 逐格重跑至服务可用，`curl` 请求返回正常补全且响应 <10s/token；全程显存峰值 < 8G | M |

**总工作量估计 + 关键风险**：2S + 3M ≈ 5–8 周有效工作量，3 个月窗口内留有 ~50% 调试缓冲。关键风险：① 8G 是硬边界——训练期激活峰值最易 OOM，兜底链为减 batch/缩短 seq_len/开 offload，仍不行则降基座到 1.5–3B 而非加卡；② 数据量小 + 2 epoch 可能过拟合或学不动，子任务 4 的"严格优于基座"是硬门禁，不达标回子任务 2 换/扩数据；③ 可复现性靠版本锁定，子任务 1 锁死后中间步骤禁止升包，否则 notebook 重跑即失效。
