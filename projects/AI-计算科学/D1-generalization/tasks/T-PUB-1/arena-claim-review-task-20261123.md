# origin: ai · 2026-11-23 · W6 内部 review 任务书（arena 交叉验证 claim 强度）

# [任务] 评审 T-PUB-1 论文（ICML 2027 目标）的 claim 强度：5 条核心 finding 各自能否撑住主会审稿，整体是投主会还是降级 4 页 workshop 短文

# [背景]
- 论文核心：在"可形式化核"（答案可机械判定的计算题）上用机械 judge 当 exact ground truth，测 LLM judge 可靠性。
- 数据：10 题（7 full-rank + 3 rank-deficient）× 67 个真实 27b 输出 × 3 种 judge prompt 变体（V1_strict/V2_loose/V3_engineer），机械 judge 对照。
- 5 条 finding：
  - F1 格式可靠性：LLM judge 52-84% 输出不可解析（Wilson CI 已算），机械 judge 0%。失败率与任务类型混淆（非长度驱动）。
  - F2 机制归因：单一因果链 input complexity → 长推理链 → 撞 max_tokens → JSON 截断（mt500→2000 受控探针 + finish_reason 直接证据；6 case 中 3 可恢复/2 收敛失败/1 边界 flip）。
  - F3 判分翻转：可解析子集上 LLM vs 机械 judge 翻转率 48-52% ≈ 抛硬币（binomial p=0.79-0.90，CI 全含 0.5）。
  - F4 防 hack 理论：瞎猜全对概率解析上界 1.2e-10~3.3e-5（模型无关），Monte Carlo 0/2000 一致。
  - F5 prompt trade-off：修 c1 引入 c3 副作用（条件列举 hedging 7/30 灰区），无 arm 全维 100%。
- 差异化定位：现有 LLM-judge-reliability 工作（620 篇，2026 活跃）依赖人类标注/扰动测试当 ground truth；本文在可形式化核上用机械 judge（免费+100%精确+可复现）。
- 已知弱点（诚实标注）：n=67 输出、单模型（qwen3.8-27b）、单 judge 家族；F4 界是上界且文字 gold 1/100 是拍的常数；F2 探针 n=6。

# [约束]
- 中文回答；每条结论标 conf(0-1)；给来源（arXiv/会议论文 URL 或你检索到的文献）；不确定的标"未验证"
- 必须实际检索 2024-2026 LLM-as-judge reliability 文献（ICML/NeurIPS/ICLR/ACL/EMNLP + arXiv），不许凭记忆
- 重点检索：LLM judge format/parse failure 相关工作、judge vs mechanical/programmatic judge 对照、judge 翻转率/一致性测量、防 guessing 的 benchmark 设计

# [交付] markdown 表格，逐条 finding 评审：

| Finding | claim 强度(1-5) | 与已有文献重叠度(低/中/高+具体文献) | 审稿人最可能的攻击点 | 主会可接受性(conf) | 建议(强化/降级/删除) |

最后一行给整体判断：
| 整体 | 主会 ICML 2027 可投性(conf) | 降级 workshop 的触发条件 | 最小强化动作(≤3条,按性价比排序) |

# [长度] ≤50 行（核心判断+关键文献+决策；检索过程放附录）

# [落盘约束] 文件不存在=任务未完成：结果写入本仓库 projects/AI-计算科学/D1-generalization/tasks/T-PUB-1/arena-claim-review-20261123.md（本任务只涉及 hermes-workspace-zero 仓库 main 分支，忽略历史中其他仓库的消息；本任务书在 projects/AI-计算科学/D1-generalization/tasks/T-PUB-1/arena-claim-review-task-20261123.md）

# [回执] 完成后回执必须含 repo URL + branch + commit_sha + 本任务书 sha256
