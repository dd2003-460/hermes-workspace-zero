# 网页 LLM 交叉验证查询清单（stage 02 r1）

目的：用 ≥2 个 LLM 网页服务验证 27B 固定任务硬件成本分解树中的 5 个关键 claim。
每个 claim 一条查询 + 期望可验证点。执行后逐条写回执 JSON 到 `loop-artifacts/stages/02/r1/web-llm/<id>.json`（kind: "ralph_web_llm_cross_check"）。

## Q1 — 27B Dense 4bit 单卡 decode 速度（决定 3090×2 / A100×1 分支）
Claim（待验）：27B dense Q4 权重 ~14GB，在 24GB 单卡（RTX 3090，936 GB/s）上单流 decode 约 60–90 tok/s（权重带宽瓶颈模型 v ≈ BW_eff / weight_bytes，BW_eff≈峰值×0.6-0.8）。
期望可验证点：a) 27B Q4 权重体积是否 ~14GB（±2GB）；b) 3090 或同带宽卡上 27B 4bit 单流 decode 实测区间。
查询文本：
「27B 参数 dense 模型量化到 4bit（AWQ/GPTQ Q4）后权重大约多少 GB？在 RTX 3090 24GB（显存带宽 936GB/s）上用 llama.cpp 或 vLLM 跑单流解码（batch=1），decode 速度大概多少 token/s？给出你的推理依据和实测数据（如果有）。」

## Q2 — 27B Q4 KV cache 每 token 字节数（决定 57.6K 缓存是否放得下）
Claim（待验）：27B（如 Qwen2.5-27B：64 层，GQA 8 KV 头，head_dim 128）Q8 KV 每 token ~0.25MB，64K token ~16GB；Q4 KV 一半 ~8GB。
期望可验证点：64K 上下文 Q4 权重的 KV cache 大小量级（GB 级），57.6K token KV 在 24GB 卡上的占用。
查询文本：
「Qwen2.5-27B（或同量级 27B GQA 模型）在 64K 上下文时，KV cache 占多少显存？假设 KV cache 用 8bit 和 4bit 两种精度，各约多少 GB？57600 token 的 KV 大约多少？给出计算过程。」

## Q3 — 90% 缓存命中下 prefill 实际计算量（决定 T_prefill 叶子）
Claim（待验）：固定前缀 57.6K 被 prefix cache 命中时，每次任务只需 prefill 新输入 ~5.76K token，prefill 时间 ≈ 5760 / (prefill tok/s)，与 64K 全量 prefill 差 10 倍。
期望可验证点：vLLM/llama.cpp prefix caching 的行为（命中的 token 是否跳过 attention 计算）、5.7K token prefill 在 3090 上的量级（秒级）。
查询文本：
「vLLM 的 prefix caching（自动前缀缓存）命中时，命中的 token 还会重新做 prefill 计算吗？如果一个 64K 上下文里 57.6K 命中缓存、只有 5.76K 是新 token，实际 prefill 计算量按多少 token 算？3090 上 prefill 5760 token 大概需要几秒（27B 4bit）？」

## Q4 — 2026 二手 3090 24GB 单卡价格区间（决定硬件小时成本叶子）
Claim（待验）：2026 年二手 RTX 3090 24GB 单卡 ≈ $800–1500（美区 eBAY），国区拆机卡 ≈ ¥4000–8000。
期望可验证点：美区 eBAY 2025 末–2026 的成交/挂牌价格区间。
查询文本：
「2026 年（或 2025 年底）二手 RTX 3090 24GB 在 eBAY 美区的典型成交价是多少美元？给我一个价格区间和依据（矿卡/非矿卡分开更好）。」

## Q5 — DGX-1 V100×8 整机二手价格区间（决定 #1 候选是否成立）
Claim（待验）：DGX-1（V100 32GB SXM2 ×8）二手整机 ≈ $3000–6000；或 8 张 V100 32GB 单卡 ≈ $1500–2500/张（美区）。
期望可验证点：整机或单卡的美元区间；整机功耗 ~2000W 是否属实。
查询文本：
「2026 年二手 NVIDIA DGX-1（8×V100 32GB SXM2 整机）大概多少钱美元？如果单独买 8 张 Tesla V100 32GB 卡（PCIe 或 SXM），单卡大概什么价？整机功耗大约多少瓦？给出依据。」

## 执行说明
- 站点任选 ≥2（ChatGPT / DeepSeek / GLM / Gemini / Perplexity / LMArena agent mode），必须 ≥2 个不同服务成功回答同一 claim 才算通过。
- 矛盾记录：不同 LLM 答案冲突时，记入 `two_leg_disagreements` 并补查。
- 纯 JS 聊天页不要用 WebFetch；走 ego-browser（已登录会话）。
- 回执最低字段：kind / responses[]（provider_id, endpoint_host, status, 回复要点）/ successful_provider_ids[] / observed_at(ISO8601+08:00)。
