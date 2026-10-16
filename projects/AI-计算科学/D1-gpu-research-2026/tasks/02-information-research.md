origin: ai
输入路径: tasks/01-goal-decomposition.md (空缺 G1-G8)
观察时间: 2026-09-25T02:25+08:00 (Asia/Shanghai)

# 阶段 02 工件：资料搜集与网页 LLM 询问

## 本轮核验空缺 ID 与主张
G1(H200显容量/带宽) G2(B200显/FP4) G3(近7天吞吐) G4(价格) G5(vLLM支持) G6(TDP) G7(近7天获取) G8(互联)

## 空缺 → 主张 → 权威证据 → 网页LLM回执 → 暂定结论/未解决

### G1 H200 显容量/带宽
- 主张: H200 = 141 GB HBM3e, 4.8 TB/s 显带宽。
- 权威证据: NVIDIA H200 产品页(WebFetch 返回 141GB/4.8TB/s, 1.4× H100 带宽); vLLM docs 间接确认 H200 支持。
- 网页LLM: Perplexity(2026-09-25, 一手 nvidia 页日期2026-08-27) + ChatGPT(2026-09-25, 官方页+HGX架构文档) 一致。
- 暂定结论: 已验证(≥2独立: 官方页+两LLM一致)。

### G2 B200 显容量/FP4
- 主张: B200 SXM 单卡显存口径争议; 官方 HGX B200 系统 1.4TB total(8卡); DGX B200 1440GB=8×180GB/卡; FP4 144 PFLOPS sparse/72 dense(8卡)。
- 权威证据: NVIDIA B200 官方页(WebFetch: 1.4TB total, NVLink 1.8TB/s, FP4 144/72 PFLOPS, "HGX B200/B300 shipping now")。
- 网页LLM: 两LLM 一致澄清 180GB/卡 vs 192GB(=GB200 superchip 口径), 警告混用。
- 暂定结论: 已验证口径澄清; 单卡"192GB"未证实(属 GB200 口径)。

### G3 近7天独立吞吐
- 主张: 近7天(09-18~09-25)独立 tokens/s 完整方法表。
- 证据: AIMultiple 多GPU benchmark 2026-09-21(摘要称 H200 比 H100 高约9-10%, 完整方法/tokens/s 未抓取); Metrum AI 2025-04-01(Llama4 Maverick vLLM 8GPU: B200 9870 vs H200 6694 output tok/s, 节点级)。
- 网页LLM: 两LLM 一致指出"8-GPU 整机≠单卡", 不能外推。
- 暂定结论: 未解决(近7天完整方法表未抓取; 仅摘要/旧节点级)。

### G4 当前价格
- 主张: 当前单卡/租赁价格。
- 证据: Nebius H200 $4.50/B200 $7.15 on-demand(2026-09-22动态spot); CoreWeave 8×B200 $68.80/h≈$8.60/GPU-h; Lambda B200 $6.69-6.99; Mercatus 指数 H200 avg $4.43/B200 avg $6.39(2026-09-13); AIMultiple 2026-09-22 H200 $2.09-13.78 离散。
- 网页LLM: 两LLM 一致强调价格随区域/形态/库存, 需时点。
- 暂定结论: 未解决(时间敏感, 多来源离散, 需采购时点快照)。

### G5 vLLM 支持
- 主张: vLLM 支持 H100/H200/B200/MI300X; 最新 0.30.0(2026-09-22); B200/GB200 需 CUDA≥12.8; Rubin preview CUDA13.4。
- 权威证据: vLLM docs WebFetch(CC≥7.5 含 H100/B200; ROCm MI300 gfx942/MI350)。
- 网页LLM: 两LLM 一致(0.30.0 2026-09-22)。
- 暂定结论: 已验证。

### G6 TDP/能效
- 主张: H200 SXM up to 700W。
- 证据: 仅 ChatGPT 官方页线索; 未独立 WebFetch 核验。
- 暂定结论: 未解决(单来源线索)。

### G7 近7天获取/新发布
- 主张: B200/B300 shipping now; Nebius 2026-10-01 价格上调(H200 $5.40/B200 $8.50)。
- 证据: 官方页"shipping now"; shattered.io 报道(2026-10-01 effective)。
- 暂定结论: 部分(发布状态官方; 库存/可订性未解决)。

### G8 互联
- 主张: B200 NVLink 5.0 1.8TB/s GPU-to-GPU, 14.4TB/s total(8卡); H200 NVLink 4.0 900GB/s。
- 权威证据: NVIDIA B200 官方页(1.8TB/s, 14.4TB/s)。
- 暂定结论: 已验证。

## 失败记录
- TechPowerUp h200/b200: 403 Forbidden ×2(替代尝试一次已耗尽)。
- nvidia.com/en-us/data-center/h200/: 404(路径变化, 内容仍通过其他官方页)。

## 网页LLM 回执引用
- web-llm/perplexity-r1.png + 会话 URL https://www.perplexity.ai/search/fb73cec7-0236-4005-be24-3789dafea6b7 (2026-09-25 02:18)
- web-llm/chatgpt-r1.png + 会话 URL https://chatgpt.com/c/6ab56a04-55dc-83ee-ba6d-3c319140fff6 (2026-09-25 02:2x)
两服务真实提交成功, 截图+URL+回答原文可见。