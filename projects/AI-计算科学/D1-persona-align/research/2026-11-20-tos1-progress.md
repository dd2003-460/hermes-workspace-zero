# T-OS-1 碰撞调研 · 进度与结论快照

> origin: ai（arena 结果落盘）
> 更新：2026-11-20 17:05
> 来源：arena 会话 01a1f80e（taskSpace arena-os1-dispatch-20261120），agent 自报，**报告全文未独立核验**（token 只读，commit 8607c54 在 arena/423a71ef 分支未 push）

## Q1-Q3 结论（agent 自报，Lead 已独立核验撞车对象）

- **Q1 判决：核心机制撞车，conf 0.97（agent 主观）**
  - 撞车对象：agent 自称 "ICAL"（2024）——**名字核验失败**：arXiv 搜 ICAL 全是中微子物理探测器（INO 实验），无 agent 系统。agent 实际读的两篇原文（Read 记录）：
    - **DROC** [arXiv:2311.10678，2023-11]：机器人操作，人类语言纠正→蒸馏知识库→文本+视觉相似度检索→新场景改善。四环节全命中，域=机器人。
    - **MemToolAgent** [arXiv:2606.07909，2026-06]：工具型 agent，反思式记忆提取用**环境+用户反馈**把错误执行蒸馏成 critique→检索按相似度分布选条数→**不改权重**。离本 idea 最近，2026 年。
  - 更早近邻（agent 自报，未独立核验）：HELPER（2023）、CIPHER 的 ICL-edit 基线、MemPrompt（2022，问答场景）
  - **未证实部分**："置信度 + 评价/CLI 双轨"完整增强组合是否已有先例（= 收窄主张候选差异点）
- 来源 29 条，7 系统机制拆解（ExpeL/Reflexion/Voyager/SEAL/Eureka/DGM/survey）
- 独立跨模型复核未完成（agent 环境限制，已写入报告）
- 交付物：`projects/AI-计算科学/D1-persona-align/research/2026-11-20-user-signal-iclagents-collision.md` + `search-log-os1.json`（在 arena 本地 commit 8607c54，未 push）
- **Lead 核验结论（11-20 17:20）**：撞车方向成立（DROC/MemToolAgent 摘要逐环节核对，arXiv API 直查），但 agent 的撞车对象命名错误（ICAL 不存在）。D 判断"就是 SFT 人类标注变成 prompt，不新"成立，且 MemToolAgent 连"不改权重"约束都做了。

## 对本地 idea 假设的影响

`2026-11-20-user-signal-iclagents.md` 的核心新颖性假设（"用户反馈信号→ICL+RAG 固化无先例，conf 0.4"）**被 Q1 结论否定**——撞车对象 ICAL 全环节命中。信号源层不新（D 11-20 判断"就是 SFT 人类标注变成 prompt，不新"与之一致）。

**转向：新颖性主张收窄到 Q4（harness 触发回路方向，D 点名感兴趣）**——用户反馈信号→固化成 harness 层稳定触发器→回路自进化。Q4 已派发（2026-11-20 17:00，同会话续推），任务书 @ 97a76614，sha 780cd400ddaca4a3。

## Q4 状态

- 派发：2026-11-20 17:00，agent 已开跑（读任务书+回执中）
- 三环节判据：①结晶判据 ②触发稳定性（确定性 vs LLM 自决）③回路自进化
- 必读：ACE (2510.04995 待核验) / COVE (2608.01234 待核验) / DGM 触发器层 / Voyager 后续
- 预计：~30 分钟（Q1-Q3 用了 24 分钟）

## 待办（Q4 回来后）

1. ~~提取报告全文核验 ICAL 撞车结论~~ **部分完成（11-20 17:20）**：撞车对象经 arXiv API 核验为 DROC (2311.10678) + MemToolAgent (2606.07909)，agent 自称的 "ICAL" 不存在（引用名错误）。报告全文仍在 arena 会话里（token 只读未 push），待 Q4 完成后一并提取落盘。
2. Q4 判决落盘 → 决定 idea 生死：Q4 也撞 → idea 收窄成工程实现（把 DROC/MemToolAgent 机制+触发回路搬进本地 27b+hook 体系，价值在落地不在新颖性）；Q4 缺环节 → 新颖性主张成立，进 goal-template
3. 报告全文落盘到 `projects/AI-计算科学/D1-persona-align/research/`（目前只在 arena 会话里）
