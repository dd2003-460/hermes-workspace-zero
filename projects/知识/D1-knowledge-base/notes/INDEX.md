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

## 排队(按 memory/interest-directions.md 的 C 区优先级)

1. ~~AI/ML 训练机制~~ → 已完成(第一篇)
2. ~~GPU 推理硬件~~ → 已完成(第五篇, 2026-10-20, 关联 DGH.1/DGR.1)
3. ~~agent 记忆与持续循环~~ → 已完成(第二篇, 关联 DM.1/CA.1)
4. ~~LLM persona 对齐~~ → 已完成(第四篇, 关联 DPA.1, 公理层)
5. ~~传播学 / 网络拓扑 / 传播效率~~ → 已完成(m01255, 2026-10-18, 第三四五篇, 供 D2 书底座)
6. (待补: C 区剩余兴趣方向, 见 memory/interest-directions.md)
