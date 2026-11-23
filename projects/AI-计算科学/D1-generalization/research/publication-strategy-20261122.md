# 发表策略：从当前资产到顶会可见成果（2026-11-22）
# origin: ai · 触发：D 指令"查证后放仓库 + 具体计划（哪怕微小但可见的发表成果）"
# 查证来源：①本轮 web_extract 官方页面（NeurIPS/ICLR/ICML/PLOS），见 §1 逐条引用

## §1 已查证事实（全部 ① 来源，本轮工具输出）

| 事实 | 来源 | 备注 |
|---|---|---|
| NeurIPS 2026 双盲："All submissions must be anonymized…Papers violating this policy will be desk rejected" | neurips.cc/Conferences/2026/MainTrackHandbook（本轮抓取，缓存 neurips.cc-ff0837dd06.md L189） | 背书/挂名对投稿无效 |
| NeurIPS 2026 无版面费：CFP 全文无 page/publication fee；仅"至少一位作者须注册主会"（学生注册即可，Virtual Only 不够） | 同上（L342） | 会议=0 版面费，注册费仅中稿后 |
| NeurIPS 2026 截止：abstract 2026-05-04 / full 2026-05-06（已过） | neurips.cc/Conferences/2026/CallForPapers | 下届 NeurIPS 2027 约 2027-05 |
| **ICLR 2027 截止：abstract 2026-09-18 / paper 2026-09-25 AoE**；会期 2027-04-26~28；workshops 2027-04-29~30 | iclr.cc/Conferences/2027/Dates（本轮抓取） | **最近的主会窗口，距今约 12 周** |
| ICML 2027 截止：abstract 2027-01-14 / paper 2027-01-22 AoE；会期 2027-08-02~04 | icml.cc/Conferences/2027/Dates（本轮抓取） | 次选窗口 |
| 版面费（APC）只存在于期刊：PLOS 系 $1,088–$3,165/篇（plos.org/fees 本轮抓取）；Nat Comm 等 OA 期刊同量级 | plos.org/fees | 目标=会议→0 版面费 |
| TRUST(2611.10787) 已投 ICLR 2027 在审，同方向另有 3 篇 RSI 在审（含 "Why Is RSI Hard to Verify?"） | pfb git log 0faf8fa31（OpenReview 查询记录） | 赛道正在拥挤——客观验证器角度是差异化 |

**结论（对 D 三个猜测的裁定）**：
- 背书：顶会双盲，投稿不需要；需要的是 related work 定位 + 发表后传播
- 版面费：会议 0；只有走期刊才有 $1-5k
- social：不是发表门槛，是影响力放大器

## §2 我们的可发表资产（现状）

1. **formula_judge.py**（decomp/experiments/autoresearch-r1/run/）：机械公式验证器，SymPy 精确值+容差，verify/judge 双接口，reward-only 反馈串。H100 真实 run 5/5 判对（rel_err ≤0.00011）。
2. **2 题 × n=3 数据**：FP8 题 27b 3/3 全对；14x 误读题；consistency n=3 已做（可靠性行为 3/3 一致，内容 27% 方差）。
3. **judge 失败模式谱系**（jin-line-bench-judge-survey S4/S6）：self-preference / phantom / surface-compliance，及对策（outcome-blind / warrant-aware / 校准集）。
4. **理论钩子**：瞎猜概率→0（2000 次模拟 0 命中）；reward-only 自修复增量（A vs B）是可测新维度。

**核心 claim（一句话）**：LLM-as-judge 在 agent 可靠性评估上有三类系统性失败（self-preference/phantom/surface-compliance），**机械公式验证器**（预置检查点+符号精确值+reward-only 反馈）在同等题集上消除这三类失败，且使评估可复现、可统计检验。

**为什么这是顶会级而非工程报告**：① 对照实验（LLM-judge vs 机械 judge 的可靠性差异，同题同模型）② 量化指标（判分翻转率/一致率/显著性）③ 理论（瞎猜概率界 + reward-only 自修复测量）④ 可复现（spec 与题面分离，gold 预置，任何人可重跑）。

## §3 两轨计划

### 轨 A（主）：~~ICLR 2027 主会~~ → **ICML 2027 主会（2027-01-22 截止，2026-11-23 修正：ICLR 2027 截止 2026-09-25 已过，最近主会窗口 = ICML 2027）**

| 周 | 任务 | 产出 | 依赖 |
|---|---|---|---|
| W1-2 | 题集扩到 n≥10：每题 3-5 机械检查点（calc/fact/bool），含 2-3 道"秩亏"题（缺关键事实，测正确报缺口 vs 幻觉） | spec-*.json ×10 + 题面 | 无（可外包 arena 出题+Lead 核 gold） |
| W3 | baseline 对比实验：LLM-judge（27b 判 27b 输出）vs 公式 judge，同题同输出 | 判分翻转率/一致率表 | W1-2 |
| W4 | consistency + 显著性：每题 n≥3，跨 run 一致率；judge 结论的 bootstrap CI | 统计报告 | W3 |
| W5 | 校准腿：秩亏题上测"正确报缺口率"（满秩类比，见 metacognition-rsi-survey §C） | 校准维度数据 | W1-2 |
| W6 | reward-only 自修复：A（one-shot）vs B（二元反馈 ≤5 轮），rounds_to_pass 分布 | 自修复增量数据 | W1-2 |
| W7 | 交叉核验：关键数字 ≥2 独立 LLM（ego-browser）+ arena 对抗核验 | 核验回执 | W3-W6 |
| W8-10 | 成文（9 页 + 附录）：intro（judge 可靠性问题）→ 方法（三层架构）→ 实验 → 理论 → related work（TRUST/RuHarness/Phantom/Agent-as-a-Judge） | 初稿 | W7 |
| W11 | 内审：按 NeurIPS checklist 自查 + 双盲合规（匿名化代码/链接） | 修订稿 | W10 |
| W12 | 9/18 abstract → 9/25 提交 | OpenReview 提交 | W11 |

**风险**：12 周偏紧。缓解：W1-6 的每个实验块独立可交付——任何一块完成即有 arXiv 预印本素材（预印本不违反双盲，Handbook L252 明确允许）。

### 轨 B（保底，微小但可见）：workshop / 预印本，4-6 周

- **最小可见成果 = 4 页 workshop 短文**："Mechanical Verifiers as Objective Judges for Agent Reliability"：10 题 × 2 judge 的翻转率对比 + 瞎猜概率界 + 1 个 reward-only 自修复案例。
- 目标：ICLR 2027 workshop（2027-04-29~30；**论文提交 suggested deadline 2027-02-01**（2026-11-23 ego-browser 实查 iclr.cc/Conferences/2027/CallForWorkshops），录用通知须 2027-02-26 前；workshop 组织者录用名单 2026-11-29 公布 → 届时确认目标 workshop + 各自 CFP 页数限制）+ arXiv 预印本先行。
- 成本：W1-3 做完即可投，不需要等 W4-6 全量。
- 可见性：arXiv + workshop 报告 + 与 Jin 线/SAGA 线的 outreach（cold-email-design 已有 SOP）形成引用链。

### 不做
- 不投期刊（APC $1-5k + 周期长，性价比低）
- 不上 12 指标全套可靠性 profile（n 不够，先做 judge 对比这一条主线）
- 不做"AGI 定义"position paper（无可证伪内容，评审不买账）

## §4 立即可执行（本周）

1. [ ] 题集扩 10 题：外包 arena 出题（任务卡见 tasks/decomp-publish-20261122.md），Lead 核 gold
2. [ ] LLM-judge vs 公式 judge 对比脚本（复用 formula_judge.py + 27b judge prompt）
3. [ ] 秩亏题设计 2-3 道（校准腿最小集）
4. [ ] arXiv 预印本占位：W1-3 完成后即投（date-stamp）

## §5 arXiv 背书政策（2026-11-22 查证，① ego-browser 实抓 info.arxiv.org/help/endorsement.html）

**D 的担心（"arXiv 要领域专家背书，我只是理论物理硕士"）不成立，政策原文裁定如下**：

| 政策点 | 原文/含义 | 对我们的影响 |
|---|---|---|
| 触发条件 | "endorsed before submitting their first paper **or a new category**" | 背书是**按 category** 的，不是按领域身份。cs.AI 背书一次后该 category 内所有后续论文免背书 |
| 背书人门槛 | "authored a certain number of papers within the endorsement domain…any active scientist who has been working in their field for a few years should be able to endorse" | 背书人只需是**该 category 的活跃 arXiv 作者**（近 3 月-5 年间的论文计数），不需要是大牛 |
| 背书性质 | "**The endorsement process is not peer review.** You do not expect you to read the paper in detail, or verify that the work is correct, but you should check that the paper is appropriate for the subject area" | 背书 = 确认"这人属于该领域科学社区"，**不是质量背书**。官方明确不要求背书人验证正确性 |
| 找谁 | "best for you to find an endorser who **you know personally** and is knowledgeable in the subject area" | 优先熟人；其次每篇 arXiv 摘要页底部有 "Which authors of this paper are endorsers?" 链接，可找领域内活跃作者（官方明确：不要群发、不要重复骚扰同一人） |
| 加速通道 | 机构邮箱 + 认领自己参与过的论文 → 可能直接获背书 | 有机构邮箱的话流程更快 |

**操作路径（按性价比排序，2026-11-22 修正：D 确认无 cs 类背书人，arXiv 当前发不了）**：
1. **关键修正：arXiv 不在关键路径上**。ICLR 2027 投稿走 OpenReview，不要求预印本。"微小但可见成果"= ICLR workshop 4 页短文（4-6 周可投），arXiv 只是加分项
2. **背书触发机制**：endorsement request 邮件（含 6 位码）在**开始一次提交时**才由系统生成。序列：D 登录 arXiv → 开始 pfb 论文提交（cs.CL）→ 收到背书请求邮件 → 6 位码附给 Jin/Gomes → 解锁 cs 类 → 提交
3. **一次背书覆盖两篇**：pfb 论文（cs.CL/cs.AI/cs.LG）+ 新 formula-judge 论文（cs.AI）同属 cs 类，解锁一次全通
4. **背书人选 = 已有套磁邮件复用**：Jin（Northeastern）/ Gomes（Cornell）草稿已就绪（tasks/emails/，待 D 确认发送），各加 2 行背书请求附块（arXiv 政策允许附论文副本；背书人只需填 6 位码，30 秒动作）
5. **背景**：D 有 4 篇物理/数学论文待上传（gr-qc×2/math.CT/q-bio.NC，见 memory/arxiv_submission_status.md）→ arXiv 账号已存在，物理类背书已有（[待核验]），但 cs 类是新 category 需新背书
6. 理论物理背景不是障碍：背书看"提交者属于该领域社区"，跨领域（物理→ML）在 arXiv 极常见

**结论**：背书不是学术门槛（官方明确非 peer review、不验证正确性），是一个流程动作，且与既有 outreach 计划完全复用。当前真实状态：无 cs 类背书人 → arXiv 暂不可发，但 ICLR 投稿不依赖 arXiv，研究排期不受影响。真正的门槛仍是 §3 的实验规模（n≥10 + baseline + 显著性）。

## §6 待核验
- [ ] ICLR 2027 workshop 论文截止日期（各 workshop CFP 预计 2027-01 发布）
- [ ] "Why Is RSI Hard to Verify?" 全文（与 judge 客观性直接相关，需精读定位 delta）
- [ ] NeurIPS 2027 CFP 是否延续双盲（预计延续，2026-09 后确认）
- [x] pfb 待上传论文的 arXiv category：cs.CL (primary) / cs.AI / cs.LG（pfb/experiments/stage-ablation/arxiv-submission.md）→ 与 formula-judge 论文（cs.AI）同背书域
- [ ] D 的 arXiv 账号物理类背书状态（gr-qc 等 4 篇待上传 → 账号存在，物理类背书大概率已有，未登录核验）
