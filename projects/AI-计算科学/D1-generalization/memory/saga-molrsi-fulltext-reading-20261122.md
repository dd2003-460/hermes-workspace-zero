# SAGA + MoLRSI 全文精读笔记（2026-11-22）
# origin: ai
# 来源：ego-browser 抓 arXiv HTML 全文（SAGA 286K 字符 / MoLRSI 219K 字符），~/.hermes/cache/scratch/{saga_full.txt, molrsi_full.txt}
# 触发：D 追问"完整读过吗/树分解训练还是ICL/继承还是不同道路/反馈持久化=RL还是ICL/模型规模/泛化还是特化"

## SAGA (2512.21782, 2025-12) 关键事实
- **无树分解**：全文 "tree" 唯一命中=参考文献（AI-Scientist-v2 agentic tree search）。核心是 4 模块循环：Planner（分解目标→可计算 objectives）/ Implementer（web 调研+Docker 内实现 scoring function）/ Optimizer（内层优化循环，默认 LLM-based 进化算法）/ Analyzer（分析+终止决策）
- **纯 prompting，零训练**：所有模块都是 LLM agent
- **backbone（S1 原文）**：Planner/Analyzer=gpt-5-2025-08-07；Implementer/Selector=Claude Code + claude-sonnet-4-5-2025-0929；Optimizer=任务特定（可不同 LLM 或无 LLM）
- **三档自动化**：co-pilot（人审所有目标）/ semi-pilot（人只在 analyzer 阶段介入）/ autopilot（全自动）
- **domain-agnostic 设计**：S1.7 给了 4 步适配新问题的流程（写 charter→实例化 Optimizer→...）

## MoLRSI (2610.39714, 2026-10) 关键事实
- **核心机制=experience-guided MCTS + 三类持久记忆**：
  - solution memory（workflows + performance）
  - refinement memory（modifications + effects）
  - execution memory（execution strategies + verified repairs）
- **"树"=MCTS 搜索树**：forest of executable workflows，每节点=一个 workflow 配置，父→子=修改版。是搜索算法，不是训练方法
- **执行反馈持久化 ≠ RL**：backbone 全程零权重更新（Claude Sonnet 5 via Anthropic API）。"self-improvement"=搜索策略 π_t→π_{t+1}，由记忆内容引导 MCTS selection rules 实现。比 ICL 多跨任务持久记忆层，比 RL 少梯度/策略网络层
- **backbone**：Claude Sonnet 5；baseline Codex=GPT-5.5；对照 Claude Science=Claude Opus 5
- **结果**：抗生素 hit rate 15.9% vs 专家 workflow 8.7%（同训练数据同筛选库）；peptide-MHC 8 个实验验证 hits vs Claude Science 0 hits

## 对套磁定位的修正（重要）
- 两人整条线**隐含假设 backbone=最强 frontier API 模型**，SAGA→MoLRSI 没有任何小模型消融
- 研究定位=frontier 大模型的特化能力研究（分子发现），**不是泛化研究、不是小模型能力边界研究**
- 我的 A/B 证据（27b+读全文工具→引用行为质变）戳的是他们研究线的**盲区维度**：agent 系统框架迁移到小模型时可靠性边界在哪
- 套磁姿态从"我在你的问题上做增量"修正为"你的框架在 frontier-only 假设下成立，我有关于小模型侧的证据，你们没测过这个维度"

## fragility 论文 (2609.17804, 2026-09) 全文精读
- **模型**：主=Llama-3.3-70B-Instruct (80 layers)，replication=Qwen-2.5-14B + Gemma-2-9B（App F 泛化）——**open-weight 模型，不是 frontier API**
- **方法**：三独立方法交叉验证 4 阶段边界（residual cosine 层间动态 / per-category linear probes / cross-prompt activation patching）→ 收敛到同一 4 阶段分解
- **因果验证**：Operation Planning 由一组 attention heads 实现，双向验证（amplify anti-wrong-plan 子集→恢复精度；ablate→正常题也崩，H+ 子集 ablate 伤害是 H- 的 7-8 倍）
- **定位**：NoOp fragility=计算脆弱（模型属性，head-localizable），与信息获取脆弱正交
- **对套磁的意义**：Gomes 这条线用 open-weight 模型做机制研究（和 Jin 的 frontier-API 特化线是两种范式）；我的 A/B（信息获取脆弱，工具可修）是她 4 阶段框架没覆盖的正交轴

## 待办
- [x] 两封草稿按新定位重写（Jin=frontier-only 盲区角度 v4；Gomes=正交维度+框架扩展 v4）
- [x] fragility 论文全文精读（74K 字符，ego-browser 抓全文）
