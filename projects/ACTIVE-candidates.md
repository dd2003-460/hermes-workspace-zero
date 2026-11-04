## 新目标候选索引（成璐 2026-11-02 指示：不新建项目，find-goal 从下面选）

> 规则：find-goal SOP 扫到无可执行任务时，按此表优先级选方向，不再新开项目。条目完成或放弃后更新本行。

| # | 方向 | 锚点仓库（近期有活动） | 现状一句话 | 可立即做的动作 | 状态 |
|---|------|----------------------|-----------|--------------|------|
| 1 | 金融·正交信号源 | hermes-workspace-zero (D1-financial-market-analysis) | F6-F10-R4 四条负结果线闭环。**F10-R5 宏观调研已完成**（@ main 6304ab54, r8/ 共 7 文件 984 行）：13 条文献（≥10 独立来源）、6 数据源实测、3 个交互假设 H1-H3。**核心判决：H_macro 文献层面不成立**——日频方向被堵死（宏观 OOS 胜率 5.6% 最低档），宏观只在"波动/事件风险"有信号且不可套利。但 S5 (Shek 2026) 发现 funding 极值按**当日方向**分组有 +3.62pp gap（CI [2.60,4.67]），是 R2 漏掉的维度。**agent 建议：先做 H1（方向分组复现，不需要宏观数据），若也 FAIL 则 F10 收束为负结果报告** | r8 落盘 @ 6304ab54，待成璐拍板是否进 H1 回测 | **research-done · awaiting-decision** |
| 2 | 写作·动机社会 | from-motivation-to-society | Part I-V 全写完，等 P2 实验第一个数（30人30天≥40%信念迁移），solo 0美元方案已写好 | 起草 P2 实验招募文案 + 渠道对比（待你拍板渠道） | open·半阻塞(渠道) |
| 3 | 健康·MR L1 完成 | longevity-orthogonal-contribution | **阶段2 全部本地工作完成** (b7a9a83)：Step1✅ Step2✅ Step4 L1✅ (10 pair, Egger 为主) + verify_integrity C1-C24 PASS + 执行报告 + LDL→AD 管线伪影诊断(方向一致性69%)。BMI→CHD Egger OR=1.17, LDL→CHD OR=1.40, BMI→CKD OR=1.28 | blocked: 1000G v3 EUR ref (clumping, 所有源已死) + OpenGWAS token (Step3 condition-F)。本地 open-data 已穷尽 | blocked-on-credentials |
| 4 | 物理·ORF 收尾 | -orf | Stage 4 组件全完成，LaTeX 86→0（2026-11-02），arXiv tarball 已打好（2026-11-02） | arXiv 手动上传（需登录 arxiv.org/submission，不可自动绕过） | blocked-on-human |
| 5 | 视频复刻·batch-12 | d1-video-recreation | batch-12 E29-E32 全部完成（4/4 ✅，eccff00），已推 main | 无待办 — 等下一批规划 | done |
| 6 | 杂乱 idea 池 | conversation-raw-materials / D1-academic-AI raw ideas | 历史对话素材 + AI 研究猜想未消化 | 低优先级：定期蒸馏进对应领域项目，不单独立项 | backlog |

| 7 | 物理·BH 质量谱 + 实验框架 T8 | bh-mass-spectrum / decomp / pfb | **T8 C3v3 异源验证完成**（pfb @ 17f725c）：rubric v3.1 终版 J1 sha 7518ce5c，本地复放 κ=0.94 G2 35/36，arena 异源 κ=+0.31 G2 29/36（vs r270 ~0），arena 内部双判官 κ=0.70。arena-input rubric 副本已同步 r278（下轮复跑消除 code-fence 2 cell）。待成璐 sign-off 冻结 rubric | **awaiting-signoff** |

## #8 decomp · T17 泛化 bench（方法论跨域验证）

- **状态**：**首轮完成 + LoCoMo OD 诊断闭环**。3 域 × 2 run 全出分：总分均 15.5-16.5/18。四域全覆盖完成（r245F, decomp @ aeb12b1）。**LoCoMo conv4 rerun#2 完成**（entity guard：overall 82.0%@top_50，+16.8pp vs baseline 65.2%；OD 42.9% 达 ceiling）；**OD 诊断最终版**：5/8 失败题答案实体不在 LoCoMo 源文本中（数据集标注问题），OD 理论上限 ~43-50%，当前 42.9% 已接近实际可达上限。Prompt 改进 smoke test 无效。memory-benchmarks @ c5f8952。**T17 bench 收口**。
  - 核心发现：方法论的「拆什么」跨域迁移成功（C 项 6.0-7.0/8，关键概念自发识别）；「怎么拆得严」的形式纪律（SHARED 耦合记录、黑盒收口表）未自发内化（S2/S3 系统性丢分）→ 需显式注入 prompt。
  - 追加实验（r245A-r245B, decomp @ 066b113）：① injected-discipline 对照——纪律注入 S2/S3 拉满但总分不涨（挤占内容探索）；② 重复 run 噪声 ±1.5 ≥ 域间差 → **域排序不可信**；③ C4 judge 偏差确认（定性讨论被判死）。
  - 最终结论：概念迁移成功（C1-C3 稳）+ 形式纪律需显式注入（有轻微内容代价）+ 单 run 分数不能做域排序 + rubric v1 有已知偏差待修。**四域全覆盖完成**（r245F, decomp @ aeb12b1）：methodology 第 4 域 18/18×2 满分（纯逻辑域最强，不需外部事实）。四域汇总：ms 15.5 / infra 16.5 / rag 15.5 / methodology 18.0。方法论「拆什么」跨 4 个形状完全不同的问题全部成立。
- **Health paper draft 完成**（longevity @ 0377e74）：`papers/mr-methodology-draft.md` 18.6KB，methods+results(10-pair×3-method)+discussion+supplementary 完整。v3 数字经 Python 独立复现验证通过。v2 r12 诊断闭环（AF 列格式 bug，非数据丢失）。下一步需成璐确认目标期刊定格式。
- **测什么**：正交拆解+原子化方法论能否在形状完全不同的问题上长出同样可验算的树（硬件题候选是 GPU、叶子是物理量；模型选型题候选是 LLM、叶子是基准分/单价/许可证——根标量同构但树形不同）。
- **执行**：本地 ninfer :8787 (qwen3.8-27b) 直跑 agent 拆解 + 同族判官按 18 分制 rubric 打分（S1-S5 结构通用 + C1-C4 按域锚定 gold L1）。分数只作域间相对比较，不作绝对质量声明。
- **验收**：6 份树产出 + scores.json + 与 27B 硬件基准对比的泛化初步结论。
- **决策点**：无外部依赖，纯本地。完成后若三域均 ≥ 基准线 → 方法论泛化证据 +1。

**优先级建议**（P1 实际问题 > P2 完成度低优先）：#4 ORF 收尾（离产出最近，纯本地活）≈ #3 健康 dry-run（解锁整条 MR 链）> #5 视频（纯执行）> #1 金融（需调研先行）> #2 写作（等你拍板）。
