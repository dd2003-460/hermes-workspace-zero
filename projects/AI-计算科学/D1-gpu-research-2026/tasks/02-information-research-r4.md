origin: ai
输入路径: tasks/01-goal-decomposition-r4.md (正交因素树 F1性能/F2成本→原子 + 空缺 G1-G6) + tasks/02-r1..r3 (已一手核验证据) + ralph web-llm 本轮(三 provider 未登录快速失败) + WebSearch 一手来源线索(G1 首队列量化)
观察时间: 2026-09-26T00:45+08:00 (Asia/Shanghai)

# 阶段 02 r4 工件：已一手证据重新映射 onto 01-r4 正交因素树 + G1 首队列一手补充

## 0. 本 r4 为何（对齐 01-r4 重构）
01-r4 重构正交因素树（第1层 性价比=F1性能/F2成本 正交+完整 → 递归到原子）+ 空缺 G1-G6。现有 02-r1..r3 围绕旧扁平 G1-G9。r4 把已一手核验证据（r1-r3）重新挂 onto 01-r4 因素树，标注覆盖/缺口，不重复搜集已一手。

## 1. web-llm 回执（本轮真实提交, 快速失败记录, 不循环重试）
- 命令: `ralph prompt-first web-llm . "27B 各量化格式显存占用+质量损失, 仅可复核来源线索" --context "阶段 02"`
- 回执: loop-artifacts/prompt-first/02-web-llm-cross-check.md (2026-09-25T19:36:42Z)
- 状态: ok:true, successful_provider_ids=[], failed=[perplexity-review, chatgpt-review, gemini-review]
- 完整失败原因: 三 provider 全部 "prompt box unavailable; login or UI changed / sign in manually" = 未登录/未配置快速失败。
- 处理: 按 02 prompt 步骤2 + 红线 → 记录完整失败原因后继续公开一手搜集, 不等待/不循环重试。本轮公开一手搜集替代 (WebSearch 一手来源线索)。

## 2. 已一手证据 onto 01-r4 因素树（r1-r3 一手✓, 不重复搜集）

### F1 性能 (性价比分子)
- **F1.1.1 prefill 速度 ← 算力 TFLOPS** [原子]
  - 一手✓ (r1): H100/H200/B200 一手页算力口径。
  - 一手✓ (r3): B300 算力口径 (GB300 NVL72 推算)。
  - 缺口: 各候选 27B prefill 实测 tokens/s → 属 03/04 (R)。
- **F1.1.2 decode 速度 ← 显存带宽** [原子]
  - 一手✓ (r3): MI350X/MI355X/B300 8TB/s; MI300X 5.3TB/s; H200 4.8TB/s; H100 3.35TB/s (rocm/nvidia 一手页原文+时间)。
  - 一手✓ (r3): B200 8TB/s (官方页口径)。
  - 缺口: 各候选 27B decode 实测 tokens/s → 属 03/04 (R)。
- **F1.2.1 精度/量化 ← 量化 bits** [原子] ← **本轮 G1 一手补充**
  - 一手来源线索 (WebSearch 2026-09-26, 聚合口径, 数值待一手): FP16→INT8 <0.5% ppl; FP16→INT4(AWQ/GPTQ) ~1-3% ppl; FP16→Q4_K_M ~2-5% ppl。
  - 一手来源线索 (论文): AWQ paper(2023) <1% ppl 4-bit; GPTQ paper(2022) ~1-2% ppl 4-bit; lm-evaluation-harness (EleutherAI) 标准 ppl 套件。
  - 一手✓ (r3): vLLM 0.30.0 支持 Blackwell CUDA≥12.8 (docs.vllm.ai 一手)。
  - 缺口: 各候选×各量化实测 ppl delta (一手需 lm-eval 跑) → 属 03/04 (R)。
- **F1.2.2 上下文能力 ← KV cache 显存** [原子]
  - 一手✓ (r1): 显存容量各候选 (H100 80GB/H200 141GB/B200 180GB/MI300X 192GB/MI350X 288GB)。
  - 缺口: KV cache 显存@seq/batch 公式核验 → 属 03 (D, 推导)。

### F2 成本 (性价比分母)
- **F2.1.1 单卡价格** [原子] ← **缺口 R (属 02 后续/04)**
  - 一手✗: 各候选单卡当前价格未一手核验 (r1-r3 仅规格, 价格属易变事实需近7天一手)。
  - 一手来源线索: 厂商 MSRP 页 + 独立评测/零售 (Amazon/Newegg) → 属 04 一手核验。
- **F2.1.2 卡数** [原子]
  - 一手✓ (r1): 显存容量 → 卡数=ceil(显存需求/单卡显存)。
  - 缺口: 显存需求=27B×bytes (G1 决定 bytes/param) → 属 03 (D)。
- **F2.2.1 功耗 / F2.2.2 散热 / F2.2.3 维护** [原子]
  - 一手✓ (r3): MI350X 1000W air / MI355X 1400W liquid / MI350P 600W PCIe (rocm 一手原文)。
  - 缺口: NVIDIA 各候选 TDP 一手 + 散热形态 → 属 04 (R)。

### 显存门 (硬约束, 横层)
- 一手✓ (r1): 显存容量各候选。
- 一手✓ (本轮 G1 补充): 量化显存占用 FP16≈54GB (一手推导 27e9×2bytes✓) / INT8≈27GB / INT4/AWQ/GPTQ≈14-16GB / Q4_K_M≈16GB / Q8_0≈27GB (WebSearch 一手来源线索, 数值待一手)。
- 缺口: 显存需求=27B×bytes (G1 决定 bytes/param) → 属 03 (D)。

## 3. 候选集合 onto 因素树 (r2 一手✓)
- 一手✓ (r2): 候选集合 = {H100,H200,B200,B300,GB200,GB300} ∪ {MI300X,MI325X,MI350X,MI355X} ∪ {Groq LPU, Cerebras WSE}; 各成员一手页命中型号/规格; 两独立 LLM 一致。
- 一手✓ (r2): 形态分层边界 (GB200/GB300=rack 36Grace+72GPU 不能单GPU替代; Groq/Cerebras=专用推理系统非通用GPU)。
- 缺口: 各成员"某地区/云/规模即时库存" (商务确认未做) → 属 04 (R)。

## 4. 覆盖/缺口表 (01-r4 因素 → 一手状态 → 缺口 → 后续阶段)
| 因素/原子 | 一手状态 | 缺口 | 后续阶段 |
|---|---|---|---|
| F1.1.1 prefill 算力 | 一手✓ 规格 | 实测 tokens/s | 03/04 |
| F1.1.2 decode 带宽 | 一手✓ 规格 | 实测 tokens/s | 03/04 |
| F1.2.1 量化质量 | 一手线索 (论文/聚合) | 各候选×量化实测 ppl | 03/04 |
| F1.2.2 上下文 KV | 一手✓ 显存容量 | KV@seq/batch 公式 | 03 |
| F2.1.1 单卡价格 | 一手✗ | 各候选当前价格近7天 | 04 |
| F2.1.2 卡数 | 一手✓ 显存→卡数 | 显存需求 (G1) | 03 |
| F2.2.1 功耗 | 一手✓ AMD TDP | NVIDIA TDP | 04 |
| F2.2.2 散热 | 一手✓ AMD 形态 | NVIDIA 散热 | 04 |
| 显存门 | 一手✓ 容量+量化占用 | 显存需求 (G1) | 03 |
| 候选集合 | 一手✓ 成员+形态 | 即时库存 | 04 |

## 5. 未解决空缺 (不伪装已知)
- G1 量化精度偏好: 未给 → 显存需求 bytes/param 未定 → 候选集合边界未定 (属用户决策)。
- G2 预算上限: 未给 → 性价比排序无预算 (属用户决策)。
- G3 部署形态: 未给 → 卡数/候选集合 (属用户决策)。
- G4 并发/SLO: 未给 → 速度需求 (属用户决策)。
- G5 采购时点: 未给 → 价格时点 (属用户决策)。
- G6 上下文长度: 未给 → KV 显存 (属用户决策)。
- 一手数值缺口 (R): 各候选单卡价格、实测 tokens/s、各量化实测 ppl、NVIDIA TDP → 属 04 一手核验。

## 6. 一手来源线索引用 (本轮公开一手, 数值待一手核验)
- WebSearch 1 (2026-09-26): 量化显存占用表 + ppl delta; 一手来源线索=lm-evaluation-harness/AWQ paper(2023)/GPTQ paper(2022)/llama.cpp GitHub。
- WebSearch 2 (2026-09-26): GGUF 显存占用 + ppl (WikiText-2/C4); 一手来源线索=llama.cpp GitHub/TheBloke GGUF repos/Reddit r/LocalLLaMA。
- 两 WebSearch 一致 (显存数值一致、质量损失一致) → ≥2 独立来源线索✓; 数值属聚合口径 → 待一手核验 (R)。

## Reviewer 判定
`review: 02-r4 | align-01r4-orthogonal-tree | pass | 已一手证据(r1-r3)重新映射 onto 01-r4 正交因素树(F1性能/F2成本→原子)标注覆盖/缺口; web-llm 三 provider 未登录快速失败完整记录不循环重试; G1 首队列一手补充(量化显存占用+质量损失, 一手来源线索=lm-eval/AWQ/GPTQ paper, 数值待一手标注R); 覆盖表因素→一手状态→缺口→后续阶段; 未解决空缺G1-G6不伪装已知+一手数值缺口R属04; 两WebSearch一致≥2独立来源线索 | 修复阶段: 无(本维度通过; 一手数值属04)`