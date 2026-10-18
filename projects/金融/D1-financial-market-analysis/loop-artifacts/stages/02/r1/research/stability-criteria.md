# 稳定性判据：时间窗口数与通过阈值

# origin: ai
任务：阶段02 资料搜集 —— 交易信号稳定性判据（独立时间窗口划分 / 跨窗口一致性阈值 / 公开验证实践）
实际观察时间：2026-10-17（Asia/Shanghai）。所有 arXiv 引用均经 export.arxiv.org API 实际抓取（HTTP 200，feed 日期 2026-10-16）。
工具状态：web_search 不可用（`DeepSeek search has no API key for "DEEPSEEK_API_KEY"`，2次）；Wikipedia/wikiwand/mlfinlab/deprado.com/AMS 全部不可达（见 §4 失败记录）。

---

## 1. 独立时间窗口如何划分

### C1 Walk-forward（滚动OOS）是时间序列模型验证的标准做法；expanding window 为最常见默认，fixed-length rolling window 为稳健性对照；OOS 测试段互不重叠且严格按时间顺序
- 来源1：arXiv:2601.08896（Malla et al., NEPSE XGBoost），2026-01-13，https://arxiv.org/abs/2601.08896
  - 观察：摘要明写 "walk forward validation under both expanding and fixed-length rolling window schemes"；两种方案都跑，expanding 20-lags 最优（RMSE 0.013450、方向准确率 65.15%），窗口经 time-series CV 选定。
- 来源2：arXiv:2608.24786（Wysocki, SPXW 0DTE 波动率风险溢价），2026-08-25，https://arxiv.org/abs/2608.24786
  - 观察：4 个 walk-forward 窗口覆盖 2021–2024 + 一个严格 hold-out 的 2025 out-of-time（OOT）切片；WF 窗口与 OOT 分离。
- 来源3：arXiv:2512.15720（Singha, SPY 订单流熵），2025-12-02，https://arxiv.org/abs/2512.15720
  - 观察：明写 "Walk-forward validation across five non-overlapping test periods"（5 个互不重叠测试段）。
- 不确定性：三个来源覆盖股票/期权市场，非加密；方法学描述可直接迁移，具体参数（步长、重叠）各家自定。

### C2 窗口粒度：公开多年期研究中"年度 OOS 窗口"是主流（5–15 年样本用 3–9 个窗口）；月级窗口在已获取的公开文献中零出现，且按多重检验逻辑会显著加重 deflation
- 来源1：arXiv:2602.00080（Sheppert, "The GT-Score"，JRFM 19(1) 60, 2026），DOI 10.3390/jrfm19010060，https://arxiv.org/abs/2602.00080
  - 观察：15 年样本（2010–2024, 50 只 S&P 500）用 "nine sequential time splits"（≈年度级窗口）。
- 来源2：arXiv:2605.04004（Mesfin, MNQ 日内动量系统性证伪研究），pub 2026-05-05 / v3 2026-09-15，https://arxiv.org/abs/2605.04004
  - 观察：5 年样本（2021–2025, 947 交易日, 5-min）用 3 个测试年（2023/2024/2025）+ expanding window。
- 来源3：arXiv:2608.24786（见 C1）——4 个年度窗口 + 1 个 OOT 年。
- 不确定性："月级窗口有害"无直接文献支持，是归纳（3 个独立来源均为年度级）+ 多重检验推断（窗口越多，PBO/DSR deflation 越重，见 C8）。此条标**未解决**（无直接反证/正证文献）。

### C3 理论边界：训练充分性 / 测试覆盖 / 时间因果性存在守恒律——窗口数不能无限制增加
- 来源1：arXiv:2609.29530（Jiayu Li, "The Impossible Trinity of Time-Series Validation"），2026-09-02，https://arxiv.org/abs/2609.29530
  - 观察：证明 α+β≤1+Λ 与 α+min{β,δ/T}≤1（α=各折最小训练占比，β=测试覆盖占比，Λ=测试点"未来"训练数据占比，δ=测试点到最近未来训练点距离）；β-mixing 下泄漏偏置上界 2Mβ_mix(δ)；原话 "expanding walk-forward is exactly the Pareto frontier of causal validation, k-fold cross-validation buys the most future data, and purged k-fold with an embargo pays in distance instead"。纯噪声上：shuffled 5-fold 报告 IC +0.32，contiguous 5-fold（等量未来数据）报告 +0.004——k-fold 本身产生虚假信号。
- 来源2（经验佐证）：arXiv:1910.05555（Sebastian & Gebbie），2019-10-12，https://arxiv.org/abs/1910.05555
  - 观察：明写 "results are inconsistent when training windows are varied, the Sharpe ratio is seen to be inflated"——训练窗口长度本身是敏感超参数，需显式报告与验证。
- 含义：对 5–6 年样本，窗口越多 → 单窗口训练段越短 → 估计越不稳；这是窗口数的硬约束。

---

## 2. "稳定"的通过阈值如何设定

### C4 跨窗口方向一致性是公开的显式通过判据（不是软性参考）
- 来源1：arXiv:2605.04004（Mesfin，见 C2）
  - 观察：5 条显式判据之一为 "consistent direction across test years (2023, 2024, 2025)"；14 个信号族中 3 个因此失败（ORB long T=0.88、VVG reversal T=1.26 均 year-inconsistent；gap continuation short T=1.46 另加 min-folds 不满足）。
- 来源2：arXiv:2602.00080（GT-Score，见 C2）
  - 观察：目标函数四项之一即 "consistency"（performance + statistical significance + consistency + downside risk 复合）。
- 来源3（间接）：arXiv:2605.17724（Mesfin, MNQ LSTM vs GBM），2026-05-18，https://arxiv.org/abs/2605.17724
  - 观察：944 天、3 个 OOS 期，无显著优势（50.00–50.89% vs 基线 51.8%）；原话 "Feature importance instability across walk-forward folds suggests noise fitting"——跨折不稳定性被当作噪声拟合红旗。
- 不确定性：一致性判据的"强度"（方向一致 vs 幅度相近 vs 统计量落在同区间）各研究自定，无统一标准。

### C5 统计通过阈值的公开具体取值（可直接参照的严格集合）
- 来源1：arXiv:2605.04004（Mesfin）——原文五条判据：
  1. "T-statistic >= 2.0 on out-of-sample net returns"
  2. ">= 30 trades per out-of-sample fold"
  3. "positive net returns after instrument-appropriate friction"
  4. "consistent direction across test years (2023, 2024, 2025)"
  5. "permutation p < 0.001 where applicable"
  - 结果：14 族全部未过（该研究是证伪研究，但判据本身是完整公开模板）。阳性对照：RTH Confluence OOS T=3.11（净 +11.82 pts, N=196）；London B T=4.30（+4.09 pts, N=247, p=0.000025）。
- 来源2：arXiv:2608.24786（Wysocki）——通过案例的数值带：OOT 年化 Sharpe 4.31–5.76（7 种 sizing）、PSR 0.964、max DD −2.28%；WF 窗口 Sharpe 区间 1.90–3.11。PSR≈0.96 可视为"正 Sharpe 概率"的严格门槛参考。
- 来源3：arXiv:2209.05559（Gort et al., DRL 加密货币交易），pub 2022-09-12 / v6 2023-01-31，https://arxiv.org/abs/2209.05559
  - 观察：把 backtest overfitting 检测做成假设检验——估计过拟合概率、拒绝过拟合 agent；10 种加密、测试段 2022-05-01→06-27（含两次崩盘）；低过拟合 agent 跑赢高过拟合/等权/S&P DBM。与本项目（加密）场景最近的公开实践。
- 不确定性：无普适标准；上述为已获取文献中最严格的显式集合，且来自证伪研究（天然偏严）。阈值最终值属阶段03设计决策。

### C6 Sharpe / 胜率 / MDD 的跨窗口一致性阈值
- **直接公开来源未找到"MDD 跨窗口一致性阈值"的标准值——记录为未解决。**
- 最接近的公开实践（3 个独立来源）：
  - arXiv:2602.00080（GT-Score）：downside risk 作为复合目标项（Sortino/MDD 族指标进入总分）。
  - arXiv:2608.23808（"MinervaScore", Santoni/Jouanne/Scullin, q-fin.ST），pub 2026-08-24 / v2 2026-08-26，https://arxiv.org/abs/2608.23808：五门之一为 "regime-stability diagnostic"（市场状态稳定性诊断）；DSR + PBO + Superior Predictive Ability + Minimum Track Record Length 各映射为通过阈值的 signed margin → 0–100 分；"Robustness Seal" 要求 score ≥80 且五门全过；在 359,062 条生产回测记录上校准，合成数据 AUROC 0.989。
  - arXiv:2605.04004（Mesfin）："consistent direction across test years" 是跨窗口一致性的离散实现。
- 含义：跨窗口一致性在公开实践中多以"复合评分项"或"离散方向一致"出现，而非单一 MDD 比值阈值。

### C7 阈值校准的两个警告（防"过了门槛就稳了"的误读）
- 来源1：arXiv:2608.23808（MinervaScore）——预注册真实数据检验：Spearman 0.013、单侧置换 p=0.40，即该稳健度评分**与未来表现无显著正向关系**；它是事后过拟合过滤器，不是前瞻预测器。
- 来源2：arXiv:2610.07701（Zheng, "On the Boundary of Admission Gates"），2026-10-06，https://arxiv.org/abs/2610.07701
  - 观察：admission gates（采用前的统计门槛）在弱信号区消灭假发现，但把采用率压到 1–7%，对强信号无增益；原话 "criteria computed on absolute rather than excess returns silently reject every candidate, including true signals"——门槛用绝对收益（而非超额）计算会系统性误杀。
  - 不确定性：2026-10-06 发布，距观察时间 11 天，略超 7 天窗口（标**未解决**：其结论是否经同行评议未核验）。

---

## 3. 量化研究中的公开验证实践（多重检验校正与 CV 方法）

### C8 规范三件套：DSR（Deflated Sharpe Ratio）/ PBO（Probability of Backtest Overfitting）/ PSR（Probabilistic Sharpe Ratio），配套 CSCV（Combinatorially Symmetrical Cross-Validation）
- 可核验应用来源1：arXiv:2008.09481（da Costa & Gebbie, IEEE SSCI 2020, pp.1091–1099），2020-08-12，DOI 10.1109/SSCI47803.2020.9308232，https://arxiv.org/abs/2008.09481
  - 观察：明写 "rigorous assessment of backtest overfitting using both combinatorially symmetrical cross validation and probabilistic and deflated Sharpe ratios"（JSE 日频数据）。
- 可核验应用来源2：arXiv:2608.23808（MinervaScore，见 C6）——DSR + PBO 直接作为两道门。
- 可核验应用来源3：arXiv:2608.27734（Gençay, "What survives honest evaluation?"），2026-08-27，https://arxiv.org/abs/2608.27734
  - 观察：所有报告绩效按试验次数（trial count）deflate；453 只 point-in-time 美股 + 39-ETF 多资产；两个前沿 LLM 发现的策略（≤100 候选 × 5 次重复）**全部被拒**；"pre-registered hypotheses earn lower evidential bars than brute search"（预注册假设的证据门槛低于暴力搜索）；并给出"认证中等 edge 所需的样本量"量化。
- 分类学来源：arXiv:1905.05023（Koshiyama & Firoozye），2019-05-01，https://arxiv.org/abs/1905.05023——文献分类 "Data Snooping / Overestimated Performance / Cross-Validation Evaluation"；Covariance-Penalty Correction（按参数数+数据量降低风险指标）；1300+ 资产，TLS>OLS。
- **原始定义来源（未核验领域知识，待补URL）**：Bailey/Borwein/López de Prado《The Deflated Sharpe Ratio》《The Probability of Backtest Overfitting》（工作论文）与《Pseudo-Mathematics and Financial Charlatanism》（Notices AMS 61(5):678–687, 2014）；López de Prado《Advances in Financial Machine Learning》（Oxford, 2018）中 purged K-fold（含 embargo）与 CPCV 的定义——本环境 AMS 返回 403、deprado.com 不可达（见 §4），定义细节未经本次核验，仅按应用领域知识引用。

### C9 Purged K-fold（purging + embargo）与 CPCV：重叠标签时序的标准做法
- 来源1：arXiv:2407.17645（Nicolini et al., "Hopfield Networks for Asset Allocation"），2024-07-24，DOI 10.1145/3677052.3698605，https://arxiv.org/abs/2407.17645
  - 观察："extensive study based on combinatorial purged cross-validation over several datasets"；对 LSTM/Transformer 持平或更好，"faster training times and better stability"。
- 来源2：arXiv:1902.07855（Barnwal et al., 加密货币 stacking），2019-02-21，https://arxiv.org/abs/1902.07855
  - 观察：明写 "For Cross-validation, Purged Walk forward cross-validation has been used."（加密场景直接先例）。
- 来源3：arXiv:2609.29530（见 C3）——理论比较：purged k-fold with embargo "pays in distance instead"（用标签距离而非未来数据换因果干净）。
- 对本项目的含义（判断，非事实）：资金费率/OI 信号若标签为当日回报（非重叠），purging 不强制；若用多日前瞻标签（如预测未来 N 日），必须 purge + embargo。**未解决**：取决于阶段03的标签设计。

### C10 统计门槛防不住未来信息泄漏——结构性 point-in-time 是前提，不是可选项
- 来源1：arXiv:2608.27734（Gençay，见 C8）——原话 "a deliberately leaky oracle posting a Sharpe ratio of 35 survives Deflated Sharpe and probability-of-backtest-overfitting testing completely"：故意泄漏的 oracle（Sharpe 35）能完整通过 DSR 与 PBO 检验。
- 来源2：arXiv:2609.29530（见 C3）——守恒律中的 Λ 项即"测试点未来数据进入训练"的占比，定量刻画泄漏。
- 来源3：arXiv:2604.15531（Nikolopoulos, "Spurious Predictability in Financial Machine Learning"），2026-04-16，https://arxiv.org/abs/2604.15531
  - 观察：falsification audit——对零预测力合成参照类 + 微结构安慰剂做检验；selection inflation 度量 = 优化后 in-sample 与 disjoint walk-forward 的 "absolute magnitude gap"，按 effective multiplicity 校正。
- 含义：本项目 S1 的 "point-in-time（杜绝未来信息）" 是第一层（结构性设计），DSR/PBO 是第二层（统计校正）；Gençay 的证据表明第二层不能替代第一层。

---

## 4. 工具与来源失败记录（如实记录，失败不是证据）

| 工具/来源 | 目标 | 失败现象（原样） |
|---|---|---|
| web_search | 通用搜索 | `DeepSeek search has no API key for "DEEPSEEK_API_KEY"`（2 次调用均失败）→ 改用 arXiv export API |
| en.wikipedia.org / en.m.wikipedia.org | Walk-forward testing 定义 | `web fetch failed: TypeError: fetch failed` |
| wikiwand.com/en/articles/Walk-forward_testing | 同上（镜像） | "URL hostname ... resolves to a non-public IP address" |
| mlfinlab.readthedocs.io/en/latest/cv.html | mlfinlab CV 文档 | HTTP 404，页面正文 "This project is abandoned — Abandoned project 1.0 documentation"（mlfinlab 文档已从 Read the Docs 移除） |
| www.deprado.com | López de Prado 主页/论文 | `web fetch failed: TypeError: fetch failed` |
| www.ams.org/notices/201405/rtx140500678p.pdf | Notices AMS 2014 原文 | HTTP 403 bot 验证页 "Verifying your connection :: American Mathematical Society" |

说明：以上为工具/访问失败，不构成任何研究证据。本文所有引用均为经 arXiv export API 实际抓取（HTTP 200）的摘要级观察；未编造任何 URL。mlfinlab 弃用状态为易变事实，观察于 2026-10-17（<7 天，有效）。

---

## 对阶段03的建议输入（暂定结论+仍未解决的空缺，不写最终推荐）

**暂定结论（供阶段03设计参考，非最终推荐）：**
1. **窗口划分**：对 2020–2025（6 年，含 2020-21 牛 / 2022 熊 / 2023 震荡 / 2024-25 牛）样本，公开实践主流为 **3–5 个互不重叠的年度 OOS 窗口 + expanding window**（Mesfin：3 测试年；Wysocki：4 窗口 + 1 OOT 年；GT-Score：15 年 9 splits ≈ 年度级）。月级窗口在已获取文献中零出现，且窗口数受守恒律 α+β≤1+Λ 约束（窗口越多训练段越短）。2022 熊市窗口必须落入 OOS 段（方向一致性判据 C4 天然要求）。
2. **通过阈值**：无普适标准。已获取文献中最严格的显式集合 = 每窗口 OOS 净收益 T≥2.0 + 每窗口 ≥30 笔 + 扣费后净正 + 全部测试年方向一致 + permutation p<0.001（arXiv:2605.04004）；替代形态 = GT-Score 四项复合（performance + significance + consistency + downside risk）。PSR>0.95 可作"正 Sharpe 概率"严格门槛参考（arXiv:2608.24786）。
3. **验证栈分层**：第一层结构性 point-in-time（前提，统计门槛防不住泄漏，arXiv:2608.27734）→ 第二层 DSR/PBO/PSR 按试验次数 deflate（arXiv:2008.09481 / 2608.23808）→ 第三层（条件性）标签重叠时 CPCV/purged k-fold + embargo（arXiv:2407.17645 / 1902.07855）。
4. **阈值校准**：通过稳健度评分 ≠ 前瞻稳定（MinervaScore 真实数据 ρ=0.013）；门槛用绝对收益计算会系统性误杀真信号（arXiv:2610.07701）——建议阈值基于超额收益且预注册。

**仍未解决的空缺（阶段03需决策或补查）：**
1. DSR/PBO/PSR/CSCV 的原始定义 URL（Bailey et al. 论文 + AIFML 书）——**未核验领域知识（待补URL）**，本环境 AMS/deprado.com 不可达。
2. MDD 跨窗口一致性无公开标准值——需设计（候选：各窗口 MDD 之比上限 / MDD 符号与量级一致），建议与信号类型一并定。
3. 月级/季度级窗口无公开文献支持（现状=归纳+多重检验论证）；若坚持月级，多重检验校正需相应加强（fold 数↑ → deflation↑）。
4. CPCV 实现参考：mlfinlab 已弃用（2026-10-17 观察），需另找实现（未解决）。
5. 无 funding-rate/OI 信号专属的公开稳定性研究；最近邻证据为 DRL 加密过拟合拒绝检验（arXiv:2209.05559）与加密 purged WF（arXiv:1902.07855）。
6. arXiv:2610.07701（admission gates 采用率 1–7%）未过 7 天新鲜度窗（11 天）且未见同行评议——**未解决**，引用时保留不确定性。
