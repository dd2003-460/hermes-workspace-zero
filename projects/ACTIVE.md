# ACTIVE — 活跃项目面板

**自动生成**: 2026-11-06 16:20 — 由 scripts/aggregate-active.sh 聚合

## 焦点项目

| 项目 | 相对路径 | 阶段 | 迭代 | 状态 | 当前任务 |
|------|----------|------|------|------|----------|
| D1-longevity-orthogonal | `健康长寿/D1-longevity-orthogonal/` | 04 | 1 | active | T5 硬阻塞: FinnGen R13 无 allele 列 + 1000G FTP 404 → strand harmonisation 无法完成。管道代码已就绪 (v2, palindrome-safe + IVW/Egger/WMed |
| D1-efficiency-optimization | `AI-计算科学/D1-efficiency-optimization/` | 01-goal-decomposition | 1 | in_progress | R6+R7+candidate#4 完成 (2026-11-05): R6 阶段门控加载 M1=78.1≥70 PASS (规则负载 -67.6%); R7 SOP 压缩 6826→2698 tok (-60.5%), 54/54 hard |
| quant-capital-flow | `金融/quant-capital-flow/` | unknown | 1 | in_progress | toy model v15 联合优化完成（十五连败确认框架不够），转其他研究方向 |
| d1-video-recreation | `媒体/D1-ai-video-recreation/` | batch-13-closed | 13 | done | 无待办 — batch-13 收官，等下一批规划（需成璐定 E37+ 主题或确认新季方向） |
| bh-mass-spectrum | `理论物理/bh-mass-spectrum/` | active | 3 | active | 任务 A (P0-1/P0-2) v2 数据质量修复完成 @ 6ab6336。三个 bug 已修：(1) 种子 BH 污染 — m_bh>=1e-7 排除 ~339 Msun 标记；(2) 占据率 NaN — 分母改为全晕群体；(3) LO |
| D2-efficient-propagation-book | `写作-社会系统/D2-efficient-propagation-book/` | init | r1 | active | L1-L6 全15章完成. v3 定稿前通读完成. 2026-11-05: FULL-BOOK.html/md 合订本(e47eb801); P2 招募文案+问卷v1 落盘(09c4f76b)待发群; r292 渠道选择已登记 APPROV ⚠️ v3 正式定稿待 P2 实验第一个数（渠道待成璐拍板 r292; 招募文案+问卷已就绪） |
| D1-think-token-budget | `AI-计算科学/D1-think-token-budget/` | implementation | 10 | complete | T1-T4 全完成: R3 前沿映射交付 (P1=prompt 级前沿, 414.5ch/104tok 2.63x 短于 P0); 下一步候选: serving层 thinking_token_budget 实测… |
| D1-persona-align | `AI-计算科学/D1-persona-align/` |  |  | active | goal-fb61fede r11 完成 S5 prompt 级优化: SKILL.md 修订 1 处(任务卡模板+3 原则, 88 行). prompt-optimization-r1.md 落盘(3 优化点+完成度评估). goal 完 |
| D1-knowledge-base | `知识/D1-knowledge-base/` | kb-note-8-done | r3 | active | KB 13 notes 全收口 (2026-11-05): 第9篇 pseudo-thinking-vs-real-reasoning 已收口(2026-11-04); INDEX.md 补了 2 个缺失条目(pseudo-thinking |
| D1-financial-market-analysis | `金融/D1-financial-market-analysis/` | exploration | r1 | exploration | F10-R5 + H1 全闭环 (2026-11-05): H_macro 文献层面不成立; H1 OOS FAIL (Δgap=−2.38%, 8 gates 全挂); SOL 排除敏感性检验确认机制本身不成立 (BTC+ETH only |

---

*此文件由脚本自动生成，不要手动编辑。修改请通过各项目 loop-state.json。*

## 新目标候选索引（成璐 2026-11-02 指示：不新建项目，find-goal 从下面选）

> 规则：find-goal SOP 扫到无可执行任务时，按此表优先级选方向，不再新开项目。条目完成或放弃后更新本行。

| # | 方向 | 锚点仓库（近期有活动） | 现状一句话 | 可立即做的动作 | 状态 |
|---|------|----------------------|-----------|--------------|------|
| 1 | 金融·正交信号源 | hermes-workspace-zero (D1-financial-market-analysis) | F6-F10 全闭环。**F10-R5 宏观调研**（@ main 6304ab54）：H_macro 文献层面不成立。**H1 OOS 回测 FAIL**（2026-11-05, r8/）：Δgap=−2.38% CI[−4.92,+1.03]，G_up 跑输 G_down，8 gates 全挂。S5 方向分组效应 OOS 不复现。**F10 收口为负面结果报告** | r8/h1-backtest-report.md (含 SOL 排除敏感性检验) + results.json + h1_backtest.py @ a2859d18 | **done · negative result** | · BTC+ETH 敏感性检验确认 FAIL 稳健
| 2 | 写作·动机社会 | D2-efficient-propagation-book | Part I-V 全写完。P2 实验材料就绪（招募文案+前后测问卷+数据表）。**r292 自批渠道 E**（微信私域 A + 即刻/小红书 B）。等成璐发群即启动 30 人前测 | 成璐发群 → 收满 30 人 → 发前测链接+ch1 → 30 天后后测 | open·等成璐发群 |
| 3 | 健康·MR L1 完成 | longevity-orthogonal-contribution | **阶段2 全部本地工作完成** (b7a9a83)：Step1✅ Step2✅ Step4 L1✅ (10 pair, Egger 为主) + verify_integrity C1-C24 PASS + 执行报告 + LDL→AD 管线伪影诊断(方向一致性69%)。BMI→CHD Egger OR=1.17, LDL→CHD OR=1.40, BMI→CKD OR=1.28 | blocked: 1000G v3 EUR ref (clumping, 所有源已死) + OpenGWAS token (Step3 condition-F)。本地 open-data 已穷尽 | blocked-on-credentials |
| 4 | 物理·ORF 收尾 | -orf | Stage 4 组件全完成，LaTeX 86→0（2026-11-02），arXiv tarball 已打好（2026-11-02） | arXiv 手动上传（需登录 arxiv.org/submission，不可自动绕过） | blocked-on-human |
| 5 | 视频复刻·batch-12 | d1-video-recreation | batch-12 E29-E32 全部完成（4/4 ✅，eccff00），已推 main | 无待办 — 等下一批规划 | done |
| 6 | 杂乱 idea 池 | conversation-raw-materials / D1-academic-AI raw ideas | 历史对话素材 + AI 研究猜想未消化 | 低优先级：定期蒸馏进对应领域项目，不单独立项 | backlog |

| 7 | 物理·BH 质量谱 + 实验框架 T8 | bh-mass-spectrum / decomp / pfb | **T38 fullloop hetero-judge + rubric v3.2 replay 全部闭环**（2026-11-06, pfb @ 8037303）：v3.2 fence-skip 修复确认有效（§6-A 两围栏 cell J1 0→1.0），κ 0.606→0.559，J1 pass 0.654→0.886；窄结论成立（围栏 bug 修好），"整体质量提升"不可归因于 rubric（同模型双角色 leniency drift）。T36 Q2-Q5 扩展完成（H2 CONFIRMED, H1 INCONCLUSIVE）。论文已更新含 cross-question 证据。WorkBuddy MR 触发源待停否 | DRAFT-rubric-v3.2.md (FINAL) @ 8037303 | **done · all arena rounds closed** |

| 8 | pfb · stage-ablation 收口 | prompt-first-bench | **T17 最终报告落盘** @ 2c51b36 + **T36 异族评委 Q2-Q5 扩展完成**（e4c6842）：H2 CONFIRMED（S1→S2 最大增益跨题稳健），H1 INCONCLUSIVE（Q1 -0.187 未系统性复现），H3 CONFIRMED（S2→S3 ≤0）。Cross-question curve: S0=0.445→S2=0.500 peak。核心发现不变：judge-dependence 是论文核心证据 | T17-stage-ablation-final-report.md + runs/hetero-judge-q2q5-summary.json | **done · T36 integrated** |

## #8 decomp · T17 泛化 bench（方法论跨域验证）

- **状态**：**首轮完成 + LoCoMo OD 诊断闭环**。3 域 × 2 run 全出分：总分均 15.5-16.5/18。四域全覆盖完成（r245F, decomp @ aeb12b1）。**LoCoMo conv4 rerun#2 完成**（entity guard：overall 82.0%@top_50，+10.7pp vs baseline 71.3% (rerun#1)；OD 42.9% 达 ceiling）；**OD 诊断最终版**：5/8 失败题答案实体不在 LoCoMo 源文本中（数据集标注问题），OD 理论上限 ~43-50%，当前 42.9% 已接近实际可达上限。Prompt 改进 smoke test 无效。memory-benchmarks @ 55f7a77。**T17 bench 收口**。
  - 核心发现：方法论的「拆什么」跨域迁移成功（C 项 6.0-7.0/8，关键概念自发识别）；「怎么拆得严」的形式纪律（SHARED 耦合记录、黑盒收口表）未自发内化（S2/S3 系统性丢分）→ 需显式注入 prompt。
  - 追加实验（r245A-r245B, decomp @ 066b113）：① injected-discipline 对照——纪律注入 S2/S3 拉满但总分不涨（挤占内容探索）；② 重复 run 噪声 ±1.5 ≥ 域间差 → **域排序不可信**；③ C4 judge 偏差确认（定性讨论被判死）。
  - 最终结论：概念迁移成功（C1-C3 稳）+ 形式纪律需显式注入（有轻微内容代价）+ 单 run 分数不能做域排序 + rubric v1 有已知偏差待修。**四域全覆盖完成**（r245F, decomp @ aeb12b1）：methodology 第 4 域 18/18×2 满分（纯逻辑域最强，不需外部事实）。四域汇总：ms 15.5 / infra 16.5 / rag 15.5 / methodology 18.0。方法论「拆什么」跨 4 个形状完全不同的问题全部成立。
- **Health paper draft 完成**（longevity @ 0377e74）：`papers/mr-methodology-draft.md` 18.6KB，methods+results(10-pair×3-method)+discussion+supplementary 完整。v3 数字经 Python 独立复现验证通过。v2 r12 诊断闭环（AF 列格式 bug，非数据丢失）。下一步需成璐确认目标期刊定格式。
- **测什么**：正交拆解+原子化方法论能否在形状完全不同的问题上长出同样可验算的树（硬件题候选是 GPU、叶子是物理量；模型选型题候选是 LLM、叶子是基准分/单价/许可证——根标量同构但树形不同）。
- **执行**：本地 ninfer :8787 (qwen3.8-27b) 直跑 agent 拆解 + 同族判官按 18 分制 rubric 打分（S1-S5 结构通用 + C1-C4 按域锚定 gold L1）。分数只作域间相对比较，不作绝对质量声明。
- **验收**：6 份树产出 + scores.json + 与 27B 硬件基准对比的泛化初步结论。
- **决策点**：无外部依赖，纯本地。完成后若三域均 ≥ 基准线 → 方法论泛化证据 +1。

**优先级建议**（P1 实际问题 > P2 完成度低优先）：#4 ORF 收尾（离产出最近，纯本地活）≈ #3 健康 dry-run（解锁整条 MR 链）> #5 视频（纯执行）> #1 金融（需调研先行）> #2 写作（等你拍板）。

## 研究 Prompt 消融实验（research-prompt）

- **状态**：✅ CLOSED（2026-11-06, @ 2450b6d）
- **最终结果**：8 变体 × n=9 对称样本。R0.3 定版（简洁性原则）。统一判官协议下 R0.3 mean=14.00 σ=2.24 stall=22%，R0.7 mean=13.29 σ=3.45 stall=22%（Δ=-0.71 within noise，不可区分）。
- **关键修正**：原"18/20 σ=0"是宽松判官+n=3 运气产物；真实分布含 22% 硬停 + 成功 run 内部 11-16 分波动。
- **结论**：prompt 层无已证实改进路径。突破需更强执行模型（70B+/API 级）。
- **文件**：`projects/research-prompt/bench/runs/ablation-L1/SUMMARY.md` + `prompt-result/R0.7/N9-FINAL-COMPARISON.md`
