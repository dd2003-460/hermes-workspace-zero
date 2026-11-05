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

| 7 | 物理·BH 质量谱 + 实验框架 T8 | bh-mass-spectrum / decomp / pfb | **T8 rubric v3.1 FINAL sign-off**（r289 AI 自主执行 @ a843890）：DRAFT→FINAL，J1 sha 7518ce5c / J2 sha b229dcc9 冻结。证据链：κ=0.94 同源 + κ=+0.31 异源 + G2 35/36。r269 baseline 已标「旧 rubric 参考值」。下一步：arena 复跑消除 code-fence 2 cell（可选） | DRAFT-rubric-v3.1-s01-fix.md (FINAL) @ a843890 | **done · rubric frozen** |

| 8 | pfb · stage-ablation 收口 | prompt-first-bench | **T17 最终报告落盘** @ 2c51b36：gate-fixed 全量 90-run 重评分 + cross-judge 对比。核心发现：judge-dependence 是论文核心证据（同族 H1 CONFIRMED +0.129，异族 REFUTED -0.187）。Per-question H1 全正（Q1-Q5）。下一步：Arena 授权拉 per-dim JSONL + 扩展异族评委到 Q2-Q5 | T17-stage-ablation-final-report.md @ 2c51b36 | **done · awaiting-arena-auth** |

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
