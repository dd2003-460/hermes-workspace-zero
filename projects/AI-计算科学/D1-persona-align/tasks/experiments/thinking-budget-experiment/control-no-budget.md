# 8G 显存（RTX 4060）7B LLM LoRA 微调全流程 — 子任务分解

| # | 子任务 | 验证标准 | 工作量 |
|---|--------|----------|--------|
| 1 | 环境搭建：安装 CUDA + PyTorch + PEFT + Unsloth/QLoRA 栈，做推理冒烟测试（4bit 加载 7B 基座并生成一段文本） | 4bit 7B 模型在 8G 上成功加载并生成文本，峰值显存 < 8G，全程命令记录在案 | S |
| 2 | 数据集准备：选定目标任务（如领域 QA / 特定风格续写），清洗 1k–5k 条样本，转 alpaca/sharegpt JSONL，划分 train/val | 数据校验脚本通过（格式、去重、字段完整），train/val 划分固定且可复现 | S |
| 3 | QLoRA 微调：4bit 基座 + LoRA(r=16, target 全 attention+MLP)，开 gradient checkpointing，1–3 epochs 跑通 | 训练收敛（loss 明显下降无 NaN），全程无 OOM，最终 adapter 权重落盘可加载 | M |
| 4 | 评估：同一验证集上对比基座 vs 微调后模型（困惑度 / 任务准确率 + 抽样人工检查） | 微调后指标优于基座并记录到表格，评估脚本可一键重跑 | S |
| 5 | 合并与部署：LoRA 权重合并（或直接 4bit 起服务），用 vLLM/llama.cpp 在 8G 上部署，暴露 OpenAI 兼容 API | /v1/chat/completions 可正常请求，并发下延迟达标，显存占用 < 8G | M |
| 6 | 可复现 notebook：全流程整合为单一 notebook（固定 seed / 包版本 / 硬件假设），从零环境按序跑通 | 干净环境按 notebook 逐格重跑全部通过，关键输出（loss 曲线、评估分数）可复现 | M |

**总工作量估计 + 关键风险**：合计 ≈ 3S + 3M ≈ 6–8 周（含调试与迭代，3 个月内宽裕）。关键风险：① 8G 显存紧张——4bit 基座 + 激活峰值仍可能 OOM，需 gradient checkpointing + 小 batch + 短 context（~2k）兜底，最坏退回 7B 更小基座或换 4bit+CPU offload；② 数据质量不足 → 微调后指标不涨，需在子任务 2 预留换数据的返工余量；③ 环境版本漂移导致 notebook 不可复现，须在第 1 步就锁死 `requirements`/镜像并全程不改。
