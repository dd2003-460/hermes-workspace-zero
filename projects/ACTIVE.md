# ACTIVE — 活跃项目面板

**自动生成**: 2026-11-02 17:35 — 由 scripts/aggregate-active.sh 聚合

## 焦点项目

| 项目 | 相对路径 | 阶段 | 迭代 | 状态 | 当前任务 |
|------|----------|------|------|------|----------|
| D1-longevity-orthogonal | `健康长寿/D1-longevity-orthogonal/` | 04 | 1 | running | T5 硬阻塞: FinnGen R13 无 allele 列 + 1000G FTP 404 → strand harmonisation 无法完成。管道代码已就绪 (v2, palindrome-safe + IVW/Egger/WMed |
| D1-efficiency-optimization | `AI-计算科学/D1-efficiency-optimization/` | 01-goal-decomposition | 1 | active | R5 run5 完成 (M8 新指标题, 防复读): receipt.md + m8-proposal.md + scoring-r5.json (weighted 84.75) @ r5/run5/; bench.md n=4 mean  |
| quant-capital-flow | `金融/quant-capital-flow/` | unknown | 1 | in_progress | toy model v15 联合优化完成（十五连败确认框架不够），转其他研究方向 |
| bh-mass-spectrum | `理论物理/bh-mass-spectrum/` | active | 2 | active | P1-5 PISN 间隙正式图完成 (fig4: none/S15/S17 BHMF + GWTC-4.0 观测间隙带叠加) @ ae2c4008; GWTC-4.0 观测数字表落盘 literature/notes/。下一步候选：任务 A |
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
| 4 | 物理·ORF 收尾 | -orf | Stage 4 组件全完成，LaTeX 86→0（2026-11-02），arXiv tarball 已打好（2026-11-02） | arXiv 手动上传（同 GW-BacQFT） | open→upload |
| 5 | 视频复刻·batch-12 | d1-video-recreation | batch-12 E29-E32 全部完成（4/4 ✅，eccff00），已推 main | 无待办 — 等下一批规划 | done |
| 6 | 杂乱 idea 池 | conversation-raw-materials / D1-academic-AI raw ideas | 历史对话素材 + AI 研究猜想未消化 | 低优先级：定期蒸馏进对应领域项目，不单独立项 | backlog |

**优先级建议**（P1 实际问题 > P2 完成度低优先）：#4 ORF 收尾（离产出最近，纯本地活）≈ #3 健康 dry-run（解锁整条 MR 链）> #5 视频（纯执行）> #1 金融（需调研先行）> #2 写作（等你拍板）。
