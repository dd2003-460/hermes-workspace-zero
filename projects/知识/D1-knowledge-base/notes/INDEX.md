# notes — 教材式笔记索引

**索引号**: [KB.1] 下层 · 格式见 `../README.md`(A 名词表 + B 成璐视角, drift-check 可验)

| 文件 | 领域 | 状态 | 一句话 |
|------|------|------|--------|
| `llm-training-mechanisms.md` | AI/ML 训练机制 | v1 完成(drift-check 85/100, 硬门槛全过) | LLM 训练 = 找复现语料统计结构的最短程序; persona 是补丁不是程序 |
| `agent-memory-mechanisms.md` | Agent 记忆与持续循环 | v1 完成(drift-check 100/100, 硬门槛全过) | agent 记忆 = 有限窗口对无限历史; solo 用 md 树 + 索引 + state 文件即最简可行解 |
| `propagation-studies-fundamentals.md` | 传播学 | v1 完成(硬门槛全过: 句级第一人称 0.435 / 句长 49.1 / 禁词 0) | 传播 = 信念在网络上按"成本/收益"迁移; 现有模型量"看到", 我量"信了" |
| `network-topology.md` | 网络拓扑 | v1 完成(硬门槛全过: 句级第一人称 0.266 / 句长 39.8 / 禁词 0) | 网络拓扑给"信念迁移流量"定天花板, 内容决定你顶不顶得到 |
| `propagation-efficiency.md` | 传播效率 | v1 完成(硬门槛全过: 句级第一人称 0.330 / 句长 38.2 / 禁词 0) | KPI=Δ信念/Δ成本, 解码成本=理解=压缩; 信息论焊进传播学的钉 |
| `llm-persona-alignment.md` | LLM persona 对齐 | v1 完成(drift-check 100/100, 1514 汉字) | persona 对齐 = 条件生成非权重修改; 公理编码 LENS+METHOD, voice 编码 VOICE |
| `gpu-inference-hardware.md` | GPU 推理硬件 | v1 完成(drift-check 100/100, 70 句/均句 51.8) | decode 是带宽瓶颈; TP 分片 KV 每卡 1/4; 组合比型号重要; 线性架构改内存公式 |
| `vector-database-cosine-similarity.md` | 向量检索与 agent 记忆基础设施 | v1 完成(drift-check 100/100, 109 句/均句 54.0) | embedding 把语义变几何; HNSW 小世界图索引; recall 地板 vs 延迟的交换; 结构化存储下关键词扫描优先, 非结构化语料才需向量层 |
| `retrieval-vs-long-context.md` | 检索 vs 长上下文（管道选型） | v1 完成(drift-check 100/100, 145 句/均句 42.6) | RAG 赌召回、长上下文赌定位衰减, 两个致命黑盒互为镜像; 选型第一变量是 doc_scale×问答量×更新频率三业务参数; 混合架构是唯一同时满足两条的解 |
| `agent-goal-loop-mechanisms.md` | Agent goal/loop 机制（控制层） | v1 完成(drift-check 100/100, 8 概念块) | agent 的"停不停"是外部控制问题不是智能问题; turn-level 信号判不了 goal-level 完成, 判定权拿给状态机+hook+cron 七件套, 复杂度跟任务不确定性成正比 |
| `pseudo-thinking-vs-real-reasoning.md` | 伪 thinking vs 真推理 | v1 完成(第九篇, 2026-11-04) | CoT 是规模涌现非因果链; post-hoc rationalization 率随模型增大反降; TTS 系统性偏差 VB>VF; 7B→235B 全区间验证 |
| `27b-local-hardware-costperf-2026-10.md` | 27B 本地部署硬件性价比 | v1 调研快照(2026-10-27) | Qwen3.8-27B Q4 decode 速度 vs 系统总价; 价格为 2026-10 时点, 采购前需复核 |

## 排队(按 memory/interest-directions.md 的 C 区优先级)

1. ~~AI/ML 训练机制~~ → 已完成(第一篇)
2. ~~GPU 推理硬件~~ → 已完成(第五篇, 2026-10-20, 关联 DGH.1/DGR.1)
3. ~~agent 记忆与持续循环~~ → 已完成(第二篇, 关联 DM.1/CA.1)
4. ~~LLM persona 对齐~~ → 已完成(第四篇, 关联 DPA.1, 公理层)
5. ~~传播学 / 网络拓扑 / 传播效率~~ → 已完成(m01255, 2026-10-18, 第三四五篇, 供 D2 书底座)
6. ~~AI/ML 训练机制 — 伪 thinking 子题~~ → 已完成(第九篇 pseudo-thinking-vs-real-reasoning, 2026-11-04)
7. (待补: C 区剩余兴趣方向, 见 memory/interest-directions.md) — 第7篇 retrieval-vs-long-context 已收口(2026-11-03, r278); 第8篇 agent-goal-loop-mechanisms 已收口(2026-11-03, r279), C 区 #10 控制层闭合; 第9篇 pseudo-thinking 已收口(2026-11-04)
