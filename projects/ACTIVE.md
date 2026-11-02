# ACTIVE — 活跃项目面板

**自动生成**: 2026-11-03 04:16 — 由 scripts/aggregate-active.sh 聚合

## 焦点项目

| 项目 | 相对路径 | 阶段 | 迭代 | 状态 | 当前任务 |
|------|----------|------|------|------|----------|
| D1-longevity-orthogonal | `健康长寿/D1-longevity-orthogonal/` | 04 | 1 | active | T5 硬阻塞: FinnGen R13 无 allele 列 + 1000G FTP 404 → strand harmonisation 无法完成。管道代码已就绪 (v2, palindrome-safe + IVW/Egger/WMed |
| D1-efficiency-optimization | `AI-计算科学/D1-efficiency-optimization/` | 01-goal-decomposition | 1 | active | R5 run5 完成 (M8 新指标题, 防复读): receipt.md + m8-proposal.md + scoring-r5.json (weighted 84.75) @ r5/run5/; bench.md n=4 mean  |
| quant-capital-flow | `金融/quant-capital-flow/` | unknown | 1 | in_progress | toy model v15 联合优化完成（十五连败确认框架不够），转其他研究方向 |
| bh-mass-spectrum | `理论物理/bh-mass-spectrum/` | active | 3 | active | 任务 A (P0-1/P0-2) v2 数据质量修复完成 @ 6ab6336。三个 bug 已修：(1) 种子 BH 污染 — m_bh>=1e-7 排除 ~339 Msun 标记；(2) 占据率 NaN — 分母改为全晕群体；(3) LO |
| D2-efficient-propagation-book | `写作-社会系统/D2-efficient-propagation-book/` | init | r1 | active | L1-L6 全15章第一稿完成(第1-15章全100/100, 我全审过). v3 定稿前全书通读完成(6处交叉引用修复+ch12回指补, notes落盘). 提前做文档完成(commit 9c0c00cf: p2-experiment-p ⚠️ v3 正式定稿待 P2 实验第一个数（30 人 30 天 ≥40% 信念迁移, solo 0 美元设计已在 ch14+p2-experiment-plan.md; 渠道待成璐拍板） |
| D1-think-token-budget | `AI-计算科学/D1-think-token-budget/` | implementation | 10 | complete | T1-T4 全完成: R3 前沿映射交付 (P1=prompt 级前沿, 414.5ch/104tok 2.63x 短于 P0); 下一步候选: serving层 thinking_token_budget 实测… |
| D1-persona-align | `AI-计算科学/D1-persona-align/` |  |  | active | goal-fb61fede r11 完成 S5 prompt 级优化: SKILL.md 修订 1 处(任务卡模板+3 原则, 88 行). prompt-optimization-r1.md 落盘(3 优化点+完成度评估). goal 完 |
| D1-knowledge-base | `知识/D1-knowledge-base/` | kb-note-5-gpu | r1 | active | KB.1 第5篇教材note notes/gpu-inference-hardware.md(Lead直写, 素材=author-voice-mining corpus四篇GPU/推理对话档案: 本地GPU选型流程2018行/AI硬件推理性 |
| D1-financial-market-analysis | `金融/D1-financial-market-analysis/` | exploration | r1 | exploration | F7 多信号组合完成 (05 r3): funding+basis 三市场 FAIL — |ρ|≥0.3 信息冗余无增量; SOL bull×T1×B10×2021 t=3.27/p=0.0025 记录为 post-hoc 不升级; 下一步 |

---

*此文件由脚本自动生成，不要手动编辑。修改请通过各项目 loop-state.json。*

## 新目标候选索引（成璐 2026-11-02 指示：不新建项目，find-goal 从下面选）

> 规则：find-goal SOP 扫到无可执行任务时，按此表优先级选方向，不再新开项目。条目完成或放弃后更新本行。

| # | 方向 | 锚点仓库（近期有活动） | 现状一句话 | 可立即做的动作 | 状态 |
|---|------|----------------------|-----------|--------------|------|
| 1 | 金融·正交信号源 | hermes-workspace-zero (D1-financial-market-analysis) | F7 三市场组合 FAIL（信息冗余），F10 agent-game-model 在探索阶段 | 外包 arena 调研链上资金流/期权 skew 数据可得性 → 定 F8 实验设计 | open |
| 2 | 写作·动机社会 | from-motivation-to-society | Part I-V 全写完，等 P2 实验第一个数（30人30天≥40%信念迁移），solo 0美元方案已写好 | 起草 P2 实验招募文案 + 渠道对比（待你拍板渠道） | open·半阻塞(渠道) |
| 3 | 健康·MR L1 完成 | longevity-orthogonal-contribution | **阶段2 全部本地工作完成** (b7a9a83)：Step1✅ Step2✅ Step4 L1✅ (10 pair, Egger 为主) + verify_integrity C1-C24 PASS + 执行报告 + LDL→AD 管线伪影诊断(方向一致性69%)。BMI→CHD Egger OR=1.17, LDL→CHD OR=1.40, BMI→CKD OR=1.28 | blocked: 1000G v3 EUR ref (clumping, 所有源已死) + OpenGWAS token (Step3 condition-F)。本地 open-data 已穷尽 | blocked-on-credentials |
| 4 | 物理·ORF 收尾 | -orf | Stage 4 组件全完成，LaTeX 86→0（2026-11-02），arXiv tarball 已打好（2026-11-02） | arXiv 手动上传（需登录 arxiv.org/submission，不可自动绕过） | blocked-on-human |
| 5 | 视频复刻·batch-12 | d1-video-recreation | batch-12 E29-E32 全部完成（4/4 ✅，eccff00），已推 main | 无待办 — 等下一批规划 | done |
| 6 | 杂乱 idea 池 | conversation-raw-materials / D1-academic-AI raw ideas | 历史对话素材 + AI 研究猜想未消化 | 低优先级：定期蒸馏进对应领域项目，不单独立项 | backlog |

| 7 | 物理·BH 质量谱 + 实验框架 T8 | bh-mass-spectrum / decomp / pfb | BH 任务C 完成（e2d419b）；T21-RR 调研完成 @ 2482280；**T8 Part C 两轮对抗核验均 FAIL×2+partial×4** → **T8 Part C 探索性收口完成**（decomp @ 1cd3e74，m01140 自主执行可回滚：freeze 段三域负效应方向稳健，确认性实验等异源 judge+M8-fixed+口径冻结+预算四条件；报告副本已同步 pfb @ e92a0e4）；**rubric v2 全量重放完成 overall_pass=False**（AC1 0.661<0.85，J2 恒高分分不开配置，J1 parse 失败 7run）→ **v3 对账+脚本完成**（r246: 根因=工件条目编号不统一致双判官自造 id 不对齐 + J1-v2 来源判据一刀切过严；v3=id 锚定注入+J1 来源三级化；**全量重放完成 r247**：AC1=0.979✅ AC2✅ AC3✅ **AC4 FAIL**（B-2del-eo 满分→与 A-full 无区分度，根因=evidence 段被假设性标记污染非 rubric 错）→ **r248 修正**：v3.1 重放暴露真瓶颈不是同族判官天花板而是 **J2-lenient 的 B-1/B-2 边界模糊**（有数字无来源的方案级主张被 J2 误判 pass → AC3 FAIL）。J1 三级判据是对的。下一步：修 J2 或确认工件分布代表性。pfb @ 0dcb46f）；v2 MR 触发源查明=WorkBuddy App | **r249e 闭环**：B-2a 3步流程修复 J2 leniency → AC3 恢复（B-none J2=0.000）；AC4 确认为消融配置 design limitation（B-2del-eo 的 U/Q 研究计划条目使均值反超 A-full，非 rubric bug）。v3-final: AC1✅ AC2✅ AC3✅ AC4❌(design)。pfb @ a42fbf1。剩余：异源 judge（Fleiss κ + T8 Part C confirmatory）+ WorkBuddy 会话停否 | partial-awaiting-decision |

## #8 decomp · T17 泛化 bench（方法论跨域验证）

- **状态**：**首轮完成**（r245t-r245z，decomp @ 114ffa7）。3 域 × 2 run 全出分：总分均 15.5-16.5/18。
  - 核心发现：方法论的「拆什么」跨域迁移成功（C 项 6.0-7.0/8，关键概念自发识别）；「怎么拆得严」的形式纪律（SHARED 耦合记录、黑盒收口表）未自发内化（S2/S3 系统性丢分）→ 需显式注入 prompt。
  - 追加实验（r245A-r245B, decomp @ 066b113）：① injected-discipline 对照——纪律注入 S2/S3 拉满但总分不涨（挤占内容探索）；② 重复 run 噪声 ±1.5 ≥ 域间差 → **域排序不可信**；③ C4 judge 偏差确认（定性讨论被判死）。
  - 最终结论：概念迁移成功（C1-C3 稳）+ 形式纪律需显式注入（有轻微内容代价）+ 单 run 分数不能做域排序 + rubric v1 有已知偏差待修。**四域全覆盖完成**（r245F, decomp @ aeb12b1）：methodology 第 4 域 18/18×2 满分（纯逻辑域最强，不需外部事实）。四域汇总：ms 15.5 / infra 16.5 / rag 15.5 / methodology 18.0。方法论「拆什么」跨 4 个形状完全不同的问题全部成立。
- **Health paper draft 完成**（longevity @ 0377e74）：`papers/mr-methodology-draft.md` 18.6KB，methods+results(10-pair×3-method)+discussion+supplementary 完整。v3 数字经 Python 独立复现验证通过。v2 r12 诊断闭环（AF 列格式 bug，非数据丢失）。下一步需成璐确认目标期刊定格式。
- **测什么**：正交拆解+原子化方法论能否在形状完全不同的问题上长出同样可验算的树（硬件题候选是 GPU、叶子是物理量；模型选型题候选是 LLM、叶子是基准分/单价/许可证——根标量同构但树形不同）。
- **执行**：本地 ninfer :8787 (qwen3.8-27b) 直跑 agent 拆解 + 同族判官按 18 分制 rubric 打分（S1-S5 结构通用 + C1-C4 按域锚定 gold L1）。分数只作域间相对比较，不作绝对质量声明。
- **验收**：6 份树产出 + scores.json + 与 27B 硬件基准对比的泛化初步结论。
- **决策点**：无外部依赖，纯本地。完成后若三域均 ≥ 基准线 → 方法论泛化证据 +1。

**优先级建议**（P1 实际问题 > P2 完成度低优先）：#4 ORF 收尾（离产出最近，纯本地活）≈ #3 健康 dry-run（解锁整条 MR 链）> #5 视频（纯执行）> #1 金融（需调研先行）> #2 写作（等你拍板）。
