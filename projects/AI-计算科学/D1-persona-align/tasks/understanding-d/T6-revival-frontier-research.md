# origin: ai
# T6 复活前沿调研任务书（understanding-d 4.1 → arena 外包）

【执行前必读】
1. 本任务必须走 1-loop：先读 sop/arena-loop-pipeline.md + loop/prompt-first/00..04.5
2. 每阶段产出落盘 loop-artifacts/stages/<N>/
3. 完成后 commit + push
4. 通道故障 → 报告 Lead 降级，不得静默跳过

[任务] 调研复活准备三方向的 SOTA 成熟方案（2024-2026），每方向交付"方法+来源+conf+对我们的适配建议"：
- Q1 记忆/人格持久化：agent memory 框架如何让长期 persona 不衰减/不漂移？（候选线索：mem0/Letta(Zep)/LangMem/Graphiti 时间知识图谱/consolidation 机制）
- Q2 思维操作的可执行编码：把"思考习惯"（如质疑-猜想-验证环、正交分解、置信度标注）编码成可执行检查/注入/judge 的成熟方法？（候选线索：Chain-of-Verification/self-consistency/process reward model/constitutional AI/reflection prompting）
- Q3 外部锚点网络：多模型共识/回归测试集/可执行真值作为外部校验源的长期维护方案？（候选线索：multi-model debate/LLM-as-judge 校准/eval regression suite 实践）

[背景]（最小必要）
我们在构建 D 的数字分身（数字永生准备）：persona map 六层（认知/内容/目标/taste/盲区/复活前沿）+ 11 条思考习惯（已提取，见同目录 thinking-patterns-v1.md）+ 61 条 idea 盘点（idea-inventory-v1.md）。现有基础设施：本地 27b vLLM（不改权重）+ Hermes agent hooks（prompt 注入层）+ git 版本化记忆。目标：找最小系统让加载 persona map 后的 agent 持续"像 D 一样思考"。不预设路径，调研决定。

[约束]
- 中文回答；每条结论标 conf(0-1)；给来源 URL（arXiv/GitHub/官方文档）；不确定的标"未验证"
- 只调研 2024-2026 的活跃方案（star 数/近期 commit 作活跃度证据）
- 每个方向至少 3 个独立来源交叉；矛盾点显式记录

[交付] 写入 projects/AI-计算科学/D1-persona-align/tasks/understanding-d/revival-frontier-research.md，格式：
```
## Q1 记忆/人格持久化
### SOTA 方法
| 方法 | 链接 | 一句话原理 | 对我们适配度(高/中/低+理由) | conf |
### 推荐组合（≤5 行）
## Q2 思维操作可执行编码
（同上）
## Q3 外部锚点网络
（同上）
## 横向结论（≤10 行：三方向的最小系统形态）
```

[长度] 核心 ≤50 行/方向；过程论证放附录
[回执] 完成后 push 到当前 checkout 分支；回执必须含 repo URL + branch + commit_sha
[指纹] 任务书 sha256(去指纹行) = d0fdaf81b4cf24d4；回执原样带回
[落盘约束] 文件不存在 = 任务未完成，Lead 不验收
