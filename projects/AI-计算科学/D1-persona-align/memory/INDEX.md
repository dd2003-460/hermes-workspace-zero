# Memory Index

D1-persona-align memory files. 52 persona-v3 analyses (Tier 1+2) + 188 iteration logs (4-430) + framework + external research synthesis.

All 52 idea files enhanced with persona-v3 dimension coverage (iteration 197).
Persona-v3-prompt.txt updated with self-preservation mechanism (iteration 200, inspired by SPASM/ContextEcho).
Hermes chenglu personality同步更新 (iteration 201).

Two quality tiers:
- **Tier 1** (手工撰写, ~21 files): 200-230 lines, complete insight extraction
- **Tier 2** (脚本批量生成, ~31 files): 60-200+ lines, enhanced with persona-v3 dimensions

---

## Tier 1: Hand-Written Analyses (Complete)

### Adaptive Precision (自适应精度)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 20 | [idea-20-adaptive-token-information-density.md](idea-20-adaptive-token-information-density.md) | 206L | 自适应 token 块，KV cache 驱逐，分层 RAG |
| 44 | [idea-44-compression-loss-cost.md](idea-44-compression-loss-cost.md) | 218L | Rate-distortion R(D) 作为压缩代价 |
| 46 | [idea-46-probability-perception-time-interference.md](idea-46-probability-perception-time-interference.md) | 221L | 感知时间干扰下的概率判断，Drift Diffusion Model |
| 41 | [idea-41-marketized-ai-rate-distortion.md](idea-41-marketized-ai-rate-distortion.md) | 227L | 市场化 AI = 有损压缩，H(Y) ≤ H_capacity 约束 |

### Adaptive Exploration (自适应探索)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 38 | [idea-38-tool-selection-optimization-frequency.md](idea-38-tool-selection-optimization-frequency.md) | 212L | 磨刀理论：工具选择的最优频率 |

### Adaptive Perception (自适应感知)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 46 | [idea-46-probability-perception-time-interference.md](idea-46-probability-perception-time-interference.md) | 221L | R_max = H/t_p 感知速率上限 |

### Adaptive Prior (自适应先验)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 97 | [idea-97-biological-neural-network-pretraining-cognition.md](idea-97-biological-neural-network-pretraining-cognition.md) | 218L | θ_bio = 进化预训练网络，"非欧几何"问题 |

### Adaptive Self (自适应自我)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 102 | [idea-102-self-centered-law-derivation.md](idea-102-self-centered-law-derivation.md) | 214L | 观测者依赖的规律，I(θ;y) 作为采样密度 |

### Adaptive Projection (自适应投影)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 89 | [idea-89-orthogonal-dimensions-association.md](idea-89-orthogonal-dimensions-association.md) | 205L | 联想发生在低维投影中，跨域类比 = 最优投影选择 |

### Social Dynamics (社会动力学)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 26 | [idea-26-feedback-dynamics-social-polarization.md](idea-26-feedback-dynamics-social-polarization.md) | 203L | 社会分化/统一作为 SDE，Landau 相变 |
| 11 | [idea-11-love-concrete-hate-system.md](idea-11-love-concrete-hate-system.md) | 203L | 抽象作为信息压缩，"恨制度>恨个体"信息密度 |
| 42 | [idea-42-memetic-love-dynamics.md](idea-42-memetic-love-dynamics.md) | 205L | 爱情动力学 dA/dt = αM(t) + βI(t) - γA(t) |

### Cognitive Foundations (认知基础)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 72-75 | [idea-72-75-intelligence-phase-transition.md](idea-72-75-intelligence-phase-transition.md) | ~200L | 智能相变，信息+选择压力→智能 |
| 55 | [idea-55-information-unification-language-math-distance.md](idea-55-information-unification-language-math-distance.md) | ~200L | 信息论统一语言、数学、距离 |

### Information Theory (信息论基础)

| # | File | Quality | Core Insight |
|---|------|---------|-------------|
| 7 | [idea-07-cot-redundancy-information-theory.md](idea-07-cot-redundancy-information-theory.md) | 85L | CoT 模型大小理论下限，30-60% 冗余 |
| 23 | [idea-23-probability-information-erasure-dynamics.md](idea-23-probability-information-erasure-dynamics.md) | 95L | 概率作为 K-mixing 下的相空间测度 |
| 21 | [idea-21-channel-capacity-water-flow.md](idea-21-channel-capacity-water-flow.md) | 212L | "大管子小管子"类比，分层编码，Fountain code |
| 33 | [idea-33-complexity-simplicity-which-is-stupid.md](idea-33-complexity-simplicity-which-is-stupid.md) | 206L | "笨" = 信息效率低于随机基线 |
| 15 | [idea-15-复杂和简单讨论...md](idea-15-复杂和简单讨论-把复杂事物简单化与把简单事物复杂化-哪个是头.md) | 165L | 复杂vs简单的信息效率权衡 |

---

## Tier 2: Auto-Generated Drafts (Needs Refinement)

Covered by batch script (generate_analyses.py). Quality range: 60-80 lines.

| # | File | Raw.md Content | Priority |
|---|------|---------------|----------|
| 1 | [idea-01-ai训练数据是否是层级化的...md](idea-01-ai训练数据是否是层级化的-粗到细-rag外挂呢-以及内部检.md) | AI训练数据层级化, RAG | HIGH |
| 2 | [idea-02-ai强cot的模型大小理论下限...md](idea-02-ai强cot的模型大小理论下限-留存冗余.md) | CoT冗余 | HIGH (similar to idea 7) |
| 3 | [idea-03-耦合定义为双射以外自由度...md](idea-03-耦合定义为双射以外自由度-解耦和最小步更新测试循环-任何项目.md) | 耦合/解耦 | MEDIUM |
| 4 | [idea-04-如果让你当agent...md](idea-04-如果让你当agent-例如coding和启动本地clicod.md) | 自主agent计划 | MEDIUM |
| 8 | [idea-08-小说idea-ai视角下的诞生...md](idea-08-小说idea-ai视角下的诞生与进化-主要从长记忆开始因为有.md) | AI诞生与进化, 长记忆 | MEDIUM |
| 9 | [idea-09-安全-长期守则-硬编码...md](idea-09-安全-长期守则-硬编码不被压缩和遗忘.md) | 安全规则硬编码 | HIGH |
| 10 | [idea-10-老师说小的就是乳...md](idea-10-老师说小的就是乳-例如乳猪乳鸽-小明说我家住乳房-ulu说小.md) | 语义演化, 大小隐喻 | LOW |
| 12 | [idea-12-男女朋友开销的隐形平衡...md](idea-12-男女朋友开销的隐形平衡性性格其他控制变量平等情况开销必然.md) | 关系成本均衡 | MEDIUM |
| 13 | [idea-13-人行为的惯性...md](idea-13-人行为的惯性即使行为矛盾-理性在什么情况会质询矛盾行为.md) | 行为惯性, 理性质询 | HIGH |
| 14 | [idea-14-我继承了我父母...md](idea-14-我继承了我父母之前对食品健康的看法-未来会趋于一致吗-机.md) | 遗传vs信息灌注 | MEDIUM |
| 16 | [idea-16-每个人在交往之初...md](idea-16-每个人在交往之初都会展现好甚至不存在的好-虽然有利于初期-但.md) | 交往初期展现好 | LOW |
| 17 | [idea-17-反注入prompt...md](idea-17-反注入prompt只阅读遵循标准格式语言-遇到泄露和不正当.md) | 反注入prompt | HIGH |
| 18 | [idea-18-不同选择压-基因编码.md](idea-18-不同选择压-基因编码.md) | 选择压与基因编码 | HIGH |
| 19 | [idea-19-群体特征数据获取...md](idea-19-群体特征数据获取-网络提纯结构.md) | 群体特征, 网络提纯 | MEDIUM |
| 22 | [idea-22-身边统计学...md](idea-22-身边统计学-模因的代表-推算网络范围.md) | 身边统计学偏差 | HIGH |
| 24 | [idea-24-模因催生的爱情动力学.md](idea-24-模因催生的爱情动力学.md) | 模因爱情 (duplicate of idea 42?) | LOW |
| 25 | [idea-25-如果ai是市场化的...md](idea-25-如果ai是市场化的-为了适应大部分人的认知和负荷.md) | 市场化AI精度 (duplicate of idea 41?) | LOW |
| 27 | [idea-27-社会舆论信用制度...md](idea-27-社会舆论信用制度-不管男女-发表客观-温和-定量也是客观.md) | 信用制度 | MEDIUM |
| 28 | [idea-28-链在一起-三维太空-星球.md](idea-28-链在一起-三维太空-星球.md) | 空间链, 星球 | LOW |
| 29 | [idea-29-负反馈和正反馈-历史周期率.md](idea-29-负反馈和正反馈-历史周期率.md) | 正负反馈, 历史周期率 | HIGH |
| 30 | [idea-30-自证预言-正反馈-社会学动力.md](idea-30-自证预言-正反馈-社会学动力而不只是数学描述.md) | 自证预言 | HIGH |
| 31 | [idea-31-信息理论与优化-频率匹配-几何视角.md](idea-31-信息理论与优化-频率匹配-几何视角-.md) | 信息理论几何视角 | MEDIUM |
| 32 | [idea-32-同调群的几何直观.md](idea-32-同调群的几何直观.md) | 同调群几何 | LOW |
| 34 | [idea-34-算法效率-信息论.md](idea-34-算法效率-信息论-.md) | 算法效率, 信息论 | HIGH |
| 35 | [idea-35-t^t^2003=2003.md](idea-35-t^t^2003=2003-求解-设t20032003.md) | 迭代幂运算求解 | LOW |
| 36 | [idea-36-正逆-结构信息损失...md](idea-36-正逆-结构信息损失-解码编码-信息视角.md) | 正逆信息损失不对称 | MEDIUM |
| 37 | [idea-37-线性代数和高数统一...md](idea-37-线性代数和高数统一-前传-内积-范数-度量.md) | 线代与高数统一 | LOW |
| 39 | [idea-39-生物神经网络和ai神经网络映射...md](idea-39-生物神经网络和ai神经网络映射-仿生应用.md) | 生物NN与AI NN映射 | HIGH |
| 40 | [idea-40-信息因子贡献-媒体操纵...md](idea-40-信息因子贡献-媒体操纵-技术指标太短期且滞后-根据源头信息-.md) | 信息因子与市场 | MEDIUM |
| 43 | [idea-43-泥地-高速路-中间河流...md](idea-43-泥地-高速路-中间河流-类比自然语言-专业语言-科普桥梁.md) | 语言类比, 科普桥梁 | MEDIUM |

---

## Uncovered Ideas (No Domain Context)

| # | Raw.md Content |
|---|---------------|
| 5 | https://www.zhihu.com/pin/2009229624433980351 |
| 6 | https://www.zhihu.com/pin/2001010421000341000 |

---

## Cross-Cutting Themes

1. **Rate-Distortion Duality**: ideas 20, 44, 46, 41, 15 — 所有自适应精度选择都可以看作 rate-distortion 问题的不同实例
2. **Low-Dimensional Projection**: ideas 89, 55 — 跨域联想和统一都需要选择正确的低维投影
3. **Observer Dependence**: ideas 102, 97, 25 — 规律和认知路径都依赖于观测者的参数控制能力和受众约束
4. **Social Phase Transitions**: ideas 26, 11, 42, 29, 30 — 社会现象可以用反馈动力学和相变统一描述
5. **Information Efficiency**: ideas 33, 15, 34 — "聪明"的信息论定义是最大化信息效率
6. **Adaptive Communication**: ideas 41, 25, 43 — 从专业到大众的精度损失是系统性问题

## Iteration Logs

- iteration-166-external-research-batch6.md — arXiv batch 6 (LATTE, RGoT, PPAI, TAME)
- iteration-167-gap-filler-scan-performance-fix.md — 消除 100+ subprocess fork
- iteration-168-gap-filler-context-aware-templates.md — context-aware template
- iteration-169-external-research-batch7.md — batch 7 (UniSteer, Teaching Values, ActTraitBench)
- iteration-170-external-research-batch8.md — batch 8 (SimPersona, activation patching)
- iteration-171-gap-filler-extraction-robustness.md — 跳过元数据/引用/代码块
- iteration-172-full-pipeline-verification.md — 52/52 端到端验证
- iteration-173-index-cleanup.md — memory/INDEX.md 更新
- iteration-174-alignment-checker-real-file-verification.md — alignment_checker 真实文件验证
- iteration-175-workspace-tasks-sync.md — workspace TASKS.md 同步
- iteration-176-external-research-batch9.md — persona drift (ContextEcho/SPASM)
- iteration-177-alignment-checker-drift-detection.md — drift 检测 (--baseline)
- iteration-178-full-drift-scan.md — 52 文件全量 drift scan
- iteration-179-research-batch-11.md — 低相关, 跳过添加
- iteration-181-english-checker-drift-detection.md — 英文版 drift 检测
- iteration-182-gap-filler-apply-test.md — --apply 端到端测试
- iteration-184-persona-dashboard.md — 全局对齐度仪表盘 (53 文件扫描 + JSON/HTML + drift)
- iteration-186-gap-filler-apply-fix.md — --apply 行为约束 KeyError + 累积写入修复
- iteration-187-gap-filler-behavioral-fix.md — behavioral suggestion 去负面词
- iteration-189-gap-filler-validate.md — --validate 自一致性检查 + --scan 零 fork
- iteration-190-dashboard-top-filter.md — --top 参数 JSON 过滤
- iteration-193-dashboard-v3-baseline.md — persona-v3-prompt.txt 基线漂移检测
- iteration-194-gap-filler-priority-apply.md — 优先级 #1 文件增强 (38.7→68.99)
- iteration-196-batch-enhance.md — persona_v3_batch_enhance.py 批量工具
- iteration-197-batch-persist-enhance.md — 批量持久化增强全部 52 个 idea 文件
- iteration-200-research-synthesis.md — 外部研究综述 + persona-v3 prompt self-preservation
- iteration-201-hermes-chenglu-update.md — Hermes chenglu personality 同步更新 self-preservation
- iteration-202-sync-personality.md — sync_personality.py 同步脚本 (含 sp_section 行索引修复)
- iteration-203-project-audit.md — 项目审计 + 评估报告更新
- iteration-204-pipeline-end-to-end-test.md — 端到端管道验证 (2.1 → 63.8)
- iteration-205-research-paper-summaries.md — 6 篇外部论文独立总结文件 (PDD/SimPersona/ContextEcho/SPASM/UniSteer/ActTraitBench)
- iteration-206-synthesis-update.md — 研究综述同步 (54→60+ 篇计数 + 独立文件索引)
- iteration-207-index-fix.md — 入口索引修复 (INDEX.md + TASKS.md 滞后信息)
- iteration-208-dashboard-fix.md — dashboard Python 3.14 glob 兼容性修复
- iteration-209-pipeline-verification.md — 全管道健康验证 (53/53 通过, Python 3.14 兼容)
- iteration-210-prompt-research-extraction.md — 从迭代日志提取 Prompt 推理相关论文
- iteration-211-paper-coverage-audit.md — 论文覆盖度审计 (9/25 高相关论文有独立文件)
- iteration-212-batch-paper-extraction.md — 批量创建 7 篇缺失极高相关论文摘要
- iteration-213-batch-high-relevance-extraction.md — 批量创建 11 篇高相关论文摘要
- iteration-214-structure-audit.md — 项目结构审计 + Dashboard 基线 (AGENTS.md 合规)
- iteration-215-alignment-checker-bugfix.md — alignment_checker 维度评分过于宽松修复
- iteration-216-verification.md — alignment_checker 修复验证 (CLI + gap_filler + dashboard 全部通过)
- iteration-217-maintenance-and-verification.md — 维护迭代: 四个工具统一评分逻辑 + persona-v3-prompt.txt 审计
- iteration-218-project-cleanup.md — 项目清理: 删除 __pycache__/ iterations/, 新增 .gitignore
- iteration-219-index-maintenance.md — 索引和评估报告维护 (INDEX.md + 评估报告滞后信息修复)
- iteration-221-research-supplement.md — arXiv 搜索补充 8 篇 persona drift 论文
- iteration-222-identity-grounding.md — persona-v3 self-preservation 扩展: 身份图谱 grounding
- iteration-223-verification-patterns.md — alignment_checker verification patterns 增强 (timeline consistency)
- iteration-224-en-checker-sync.md — 英文版 checker VERIFICATION_PATTERNS 同步
- iteration-225-dashboard-sync.md — dashboard VERIFICATION_PATTERNS 同步, 四个工具验证模式完全统一
- iteration-226-gap-filler-context-filter.md — gap_filler 上下文提取模板残留过滤
- iteration-227-gap-filler-boundary-fix.md — gap_filler #### 标题边界检测 + 元数据过滤 (上下文全部来自源内容)
- iteration-228-synthiusmem-update.md — Synthius-Mem 研究更新: 6 认知域分解 + CategoryRAG
- iteration-229-weighted-keywords.md — alignment_checker 加权关键词 (flat matching → category-based retrieval)
- iteration-230-english-and-dashboard-sync.md — EN checker + dashboard 加权关键词同步, 三个工具统一
- iteration-231-end-to-end-verification.md — 端到端验证: gap_filler 质量 + alignment_checker 加权评分
- iteration-235-iterative-questioning.md — 迭代追问机制: gap detection + follow-up + self-answer (混合模式实现)
- iteration-236-reportbench-dimensions.md — ReportBench 维度实现: citation relevance + factual faithfulness (8 维度评估系统)
- iteration-237-reportbench-sync.md — ReportBench 维度同步: EN checker + dashboard (三个工具一致)
- iteration-238-reportbench-validation.md — ReportBench 维度批量验证: 跨文件一致性确认 (质量信号非噪声)
- iteration-239-fewshot-injection.md — 少样本示例注入: persona-v3 深度推理示例 (混合模式实现)
- iteration-240-gap-filler-reportbench.md — gap_filler ReportBench 维度补全 (检测→建议→补全→再评估 闭环)
- iteration-241-e2e-pipeline-test.md — 端到端测试: 评估→建议→apply→再评估 (引用相关性 +120%, 事实可信度 +∞)
- iteration-242-auto-cite.md — gap_filler --auto-cite: 自动搜索 arXiv 文献填充引用占位符
- iteration-243-auto-cite-mapping.md — --auto-cite 映射表扩展 (2→30 个 topic, 全测试通过)
- 新研究: EmergentPersuasion-activation-steering.md — activation steering vs SFT for persona
- 新研究: ReportBench-research-agent-evaluation.md — 研究 agent 评估 (citation relevance + factual faithfulness)
- 新研究: PromptStructure-deep-reasoning-elicitation.md — Prompt 结构对深度推理激发的影响

## Coverage

- Total ideas in raw.md: 55
- Covered: 52/55 (95%)
- Tier 1 (complete): ~21 files
- Tier 2 (draft): ~31 files, ALL enhanced with persona-v3 dimensions (iteration 197)
- **迭代日志: 188 个** (iteration-4 到 iteration-430)
- Uncovered: 2 (知乎链接) + 1 (无domain context)
- **研究论文独立总结: 42 个** (researches/*.md, 含 SPASM/ContextEcho/PDD/SimPersona/ID-RAG/ConsistentPersona 等)
- **Python 脚本: 23 个** (scripts/, 全部 Python 3.14 兼容)
- **外部研究综述: 68+ 篇** (researches/persona-research-synthesis.md, iteration 221 新增 8 篇)
