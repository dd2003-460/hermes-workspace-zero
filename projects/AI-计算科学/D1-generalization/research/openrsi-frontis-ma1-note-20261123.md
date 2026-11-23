# P4 精读 note · Frontis-MA1 / OpenRSI（2026-11-23）
# origin: ai · 来源：① 本轮实抓 arxiv.org/abs/2607.28568 + arxiv.org/html/2607.28568 + GitHub FrontisAI/OpenRSI + mushroom.cv 博客

## ⚠️ 勘误
我之前在 decomp 里记的 "Why Is RSI Hard to Verify?" arXiv 2607.13110 **全错**：
- 2607.13110 实为 "A Hybrid Mamba for Audio-Visual Navigation"（无关）
- 真实论文 = **Frontis-MA1: Training an AI4AI Model towards Recursive Self-Improvement in Machine Learning Engineering**
- 真实 arXiv = **2607.28568**（2026-07-30）
- 标题里没有 "Why Is RSI Hard to Verify" 这个说法，是我凭记忆编的（来源③ 未验证 → 本轮已升级成①）

## 基本信息
- 标题：Frontis-MA1: Training an AI4AI Model towards Recursive Self-Improvement in MLE
- arXiv：2607.28568 · 2026-07-30 · 0 citations（新）
- 作者：Junlin Yang, Che Jiang（leaders）；Kaiyan Zhang（correspondence）；Horizon Research + Frontis.AI + Tsinghua
- 开源：github.com/FrontisAI/OpenRSI（327★，CC BY-NC 4.0）；权重 35B+30B（BF16+GGUF）+ OpenMLE-Tasks + SFT Traces + 全栈代码
- 底座：Qwen3.6-35B-A3B（主）/ Qwen3-30B-A3B-Thinking-2507（companion）

## 核心问题（他们怎么定义"RSI 难"）
1. **行动空间不明确**："改进"可以是无数种操作，边界不清
2. **反馈信号难获取**：改进后好了多少，难量化
3. **训练-推理脱节**：模型训练的行为 ≠ 实际搜索中用到的行为

## 他们的答案（工程化）
把 MLE 任务设计成**可执行的验证环境** + **4 个原子算子作为唯一行动空间** + **用执行结果做反馈** + **训练和推理用同一套算子**。

**4 个原子算子**（= 行动空间全集）：
| 算子 | 作用 |
|------|------|
| Draft | 从头生成程序 |
| Improve | 基于执行反馈改进一个父程序 |
| Debug | 修复出错的程序 |
| Crossover | 重组两个父程序优点 |

**OpenMLE 全栈**：
- OpenMLE-Gym：5,758 个 quality-gated 可执行任务包 + Sandbox（分布式执行+自动评估）
- OpenMLE-ERL：execution-grounded SFT（26,259 例：17,245 完整 + 9,014 轨迹步）+ 在线 RL
- Frontis-MA1：后训练的元演化 agent
- OpenMLE-Evo / Evo-Max：长视野进化搜索（标准 / 异步多 GPU）

## 关键结果（MLE-Bench Lite，12h/task，单卡 RTX 4090 12GB cap）
| 配置 | Medal Avg |
|------|-----------|
| 基础模型（无搜索） | 39.39% |
| Frontis-MA1-35B + OpenMLE-Evo | 60.61%（+21.22pp 后训练增益） |
| **Frontis-MA1-35B + Evo-Max** | **71.21%** |
| GPT-5.5 + Codex（参考） | 68.18% |
| GPT-5.6 Sol / Kimi K3 2.8T（参考） | ~73% |

- 后训练增益（同框架 base→MA1）：+21.22pp
- 框架增益（同模型 无搜索→Evo-Max）：~+10pp
- **两个维度独立可测**（模型能力 vs 搜索框架，不互相掩盖）
- 30B companion 复现：34.85%→53.03%（Evo），66.67%（Evo-Max）
- **迁移测试（NatureBench Lite held-out）**：换模型 50%→70% Match-SOTA；换框架 20%→50%

## 机制层级（他们自己的定位）
- L1 Evolution：程序进化，改进算子冻结
- L2 Self-Evolution：经验回流搜索
- **L3 Meta-Evolution：改进算子本身被训练** ← Frontis-MA1 达到这层
- L4 RSI：完整自我改进闭环 ← **明确说没到，不声称一般性 RSI**

## 他们自认的 5 个 limitation（对我们最有价值的部分）
1. **更丰富的"改进改进器"目标**：目前只从执行结果学习（程序跑得好不好），**不捕捉"研究方向是否有前途/可泛化/鲁棒/值得投入"** → 系统更擅长优化 solution 而非判断哪个 idea 值得追。**这正是我们 formula-judge + 秩亏校准腿要填的洞。**
2. 进化搜索与通用 coding agent 割裂（外部 harness 限制了模型能自主发起的动作范围）
3. 只参与 AI 开发的一部分（改进外部 ML 工件），没到改进 LM 本身
4. 进化系统本身固定（没把进化系统当进化对象）
5. 经验利用浅（parent 选择只用 quality/progress/novelty 3 因子）

## 与我们 AGI 线的连接（碰撞研究结论）
1. **同一个赌注**：他们赌"可执行验证反馈 > LLM judge"，我们赌"机械公式验证器 > LLM judge"。方向一致，互相背书。
2. **行动空间对照**：他们 4 算子（Draft/Improve/Debug/Crossover）≈ 我们的 decomp 分解树 + 执行反馈闭环。结构同构。
3. **关键定位差异**：我们 27b+prompt+hook（**不改权重**）= L1/L2（经验回流），**不是 L3**（改进器不被训练）。这是诚实边界——我们没做后训练，所以到不了他们 L3。论文里必须说清这层，否则被审稿人抓"你凭什么比 35B 后训练模型"。
4. **limitation #1 = 我们的核心 claim**：他们明说执行分数不捕捉研究质量/泛化/方向价值——这正好是我们"信息充分性判定 + 秩亏校准"要解的。我们可以在论文里直接引用这条 limitation 作为 motivation。
5. **撞车风险**：他们在 MLE 域做了"可执行验证 + 进化搜索"，我们若只做到"可执行验证 + 单点判分"，novelty 会被压。差异化必须落在**校准腿（秩亏题测批判准确性）**——他们没做这个维度。

## 待核验 / follow-up
- [ ] 他们 4 算子的 prompt template 细节（在 appendix，本轮没抓全）
- [ ] MLE-Bench Lite 的 22 题具体构成（是否和我们 GPU 域题重叠）
- [ ] 是否有人在他们之后做了"执行反馈 + 校准/批判准确性"维度（撞车二次排查）
