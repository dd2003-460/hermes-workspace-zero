# GW-BacQFT Taste Review

> **审查对象**: `projects/理论物理/D1-grav-waves/papers/2026-GW-BacQFT/GW-BacQFT-paper.tex` (514 行) 及 `.bib` (24 篇)
> **目标对标**: PRL / PRD / JCAP / JHEP (2023–2026 近 3 年 gr-qc / astro-ph / math-ph 已发表与预印本)
> **审查日期**: 2026-11-02 · **硬约束**: 不修改论文源码，仅输出审查建议；全部结论标注 `conf` 与 `arXiv ID`。

## 1. Taste 差距（对标 PRL/PRD/JCAP 写法）
| # | 位置(节/行) | 问题 | 对标论文怎么写 | 修复建议 | 严重度(H/M/L) |
|---|---|---|---|---|---|
| T1 | Abstract L35-38; §1 L60-73; §6 L384-386 | **AI 元叙事/跨学科空泛比附腔**：插入“Rate-distortion principle”“机器学习分类器/热噪声同构”等非物理口号，严重损害顶刊专业感 (conf=0.96) | Kehagias & Riotto (`arXiv:2401.10680`, JCAP 2024) 与 Grimm et al. (`arXiv:2404.05670`, JCAP 2025) 直奔对称性生成元、关联函数解析核与信噪比标度，零元叙事 | 删除 L35-38、L60-73、L384-386 三段元叙事；摘要缩至单段 ≤150 词，直接给出代数态可区分度与 $N_{\rm p}$ 标度 | **H** |
| T2 | §2 L81-202 vs §3 L252-302 | **“杀鸡用牛刀”框架脱节**：引入 extended TQFT 函子、Lurie 配边与 Tomita-Takesaki 模理论 (L162)，但证明全退回经典平面波积分与泊松计数 $\sigma_N^2\sim N_{\rm src}^{-1}$，未算模算子 $\Delta_\omega$ 或 Araki 相对熵 (conf=0.94) | Kudler-Flam et al. (`arXiv:2406.01669`, `arXiv:2309.15897`, PRD 2025) 在观测者世界线上实际构造引力穿戴 von Neumann 代数并算出相对熵/广义熵；不用无实质计算的范畴包装 | 二选一：(A) 用准自由高斯态 Araki 相对熵/Hellinger 距离实算世界线子代数可区分度；(B) 降调标题与扩展 TQFT 声明，改称局域协变场论算子语言重述 | **H** |
| T3 | §4.2 Eq.21 L341 vs Fig.3 L352 vs §6 L382 | **核心数值前后差两个数量级且指数混用**：SKAO ($N=200, N_{\rm src}=10^4$) 在 Eq.21 给 $\mathrm{SNR}_{\rm dis}\sim 140$，但 §6 L382 写 $\mathcal{O}(1\text{--}3)$；混用幅度 $\propto N_{\rm src}^{-1/2}$ 与方差 $\propto N_{\rm src}^{-1}$ (conf=0.98) | Lemke, Mitridate & Gersbach (`arXiv:2407.08705`, PRD 2025) 与 Sato-Polito & Kamionkowski (`arXiv:2305.05690`, PRD 2024) 严格区分 $C_\ell/C_0\propto N_{\rm src}^{-1}$ 与幅度 $\sqrt{C_\ell/C_0}$，数值前后完全闭合 | 统一定义幅度 $A_{\rm aniso}\equiv\sqrt{C_\ell/C_0}\propto N_{\rm src}^{-1/2}$ 与功率谱方差 $\sigma_N^2\propto N_{\rm src}^{-1}$；重算并对齐 §4.2、图 3 与 §6 的 SNR | **H** |
| T4 | Preamble L1-44; §2.4 L186-192 | **排版规范与文字重复**：用通用 `article` + `\tableofcontents` + 摘要内嵌 CC-BY 声明；L186-192 连续两句重复介绍 Kehagias & Riotto `arXiv:2401.10680` (conf=0.97) | PRL/PRD 用 `revtex4-2`（PRL 无目录、≤4500 词），JCAP/JHEP 用 `jcappub`/`jheppub` | 切换为 `revtex4-2` 或 `jheppub` 模板，移除摘要内 License 与目录，合并 L186-192 重复句 | **M** |

## 2. 方法严谨性
| # | 位置 | 问题 | 风险等级 | 修复建议 |
|---|---|---|---|---|
| M1 | `\thebibliography` L440-505 & `.bib` | **多处幻觉/张冠李戴文献（一票否决项）**：① `Isi:2024` 绑定 `arXiv:2401.04789`（实为有限群纯数学论文；真 NG15 各向异性为 Agazie et al. `arXiv:2306.16221`）；② `Mingolla:2023` 绑定 `arXiv:2301.07734`（实为等离子体原子物理）；③ `Gong:2021` 绑定 `arXiv:2105.10954`（实为核聚变 Lawson 判据综述）；④ `Phinney:2001` 写错为 `astro-ph/0110028`（真为 `astro-ph/0108028`）；⑤ `Ellis:2024`/`Tsang:2024` 期刊卷页未在 arXiv/CrossRef 查实（未验证，疑似幻觉） (conf=0.99) | **Critical (H)** | 立即删除全部幻觉引用条目，替换为经 arXiv 核实的真实文献（`arXiv:2306.16221`、`arXiv:2407.08705`、`arXiv:2305.05690`、`arXiv:1306.5394`、`astro-ph/0108028`），并补齐 `Kehagias:2024` 的 `arXiv:2401.10680` |
| M2 | §3.1 Theorem 3.1 Eq.(15) L244 | **总变差距离 $d_{\mathrm{TV}}$ 关于脉冲星对数 $P$ 的幂次写反**：Eq.(15) 写 $d_{\mathrm{TV}}\gtrsim c\cdot P^{-1/2}|\Delta\sigma_N^2|$，导致脉冲星对数 $P\to\infty$ 时两源类可区分度反而趋于 0；混淆了测量标准差 $\delta\zeta\sim P^{-1/2}$ 与分布距离 $d_{\mathrm{TV}}$ (conf=0.97) | **High** | 由 $P$ 对脉冲星高斯似然的 KL 散度 $D_{\mathrm{KL}}\propto P(\Delta\sigma_N^2/\sigma_{\rm noise}^2)^2$ 及 Pinsker/Le Cam 不等式重写为 $d_{\mathrm{TV}}\gtrsim \min\!\bigl(1,\,c\,P^{1/2}|\Delta\sigma_N^2|/\sigma_{\rm noise}^2\bigr)$ |
| M3 | §3.1-3.2 L256-302; §4.2 L336-346 | **遗漏 HD 曲线不可约宇宙方差（Allen Variance）并误读 Grimm 2025**：① 假设噪声随 $P^{-1/2}$ 无限趋零，忽略有限源干涉带来的不可约宇宙方差 $\sigma_{\rm cosmic}\propto N_f^{-1/2}$（Allen `arXiv:2205.05637`；Allen & Romano `arXiv:2407.10968`）；② L296 称 Grimm et al. (`arXiv:2404.05670`) 证实宇宙学各向异性 $\mathcal{O}(10^{-5})$，实则该文算的是天体物理源随大尺度结构（LSS）成团对 HD **方差**（非均值）的贡献 (conf=0.95) | **High** | 在误差预算中加入 $\sigma_{\rm total}^2 = \sigma_{\rm noise}^2/P + \sigma_{\rm pulsar}^2/P + \sigma_{\rm cosmic}^2/N_f$（引 `arXiv:2205.05637`, `arXiv:2508.21131`）；修正 L296 对 `arXiv:2404.05670` 的引述（LSS 成团不改变 HD 均值，仅贡献 HD 方差） |
| M4 | §2.1-2.2 Eq.(1)-(5) L91-125 | **类时世界线代数与洛伦兹配边定义不严谨**：4D 中类时曲线余维为 3，量子场点值算子奇异，必须沿世界线用测试函数涂抹（worldline smearing）；且洛伦兹配边连接的是类空 Cauchy 面而非两条类时曲线（Bunk, MacManus & Schenkel `arXiv:2308.01026`, `arXiv:2504.15759`） (conf=0.93) | **Medium-High** | 将 $F(w_i)$ 改写为沿世界线管状邻域/涂抹函数 $f_i\in C_0^\infty(w_i)$ 生成的 Weyl 子代数（参 `arXiv:2406.01669`），将“detector cobordism”改为因果钻石交集上的双局域态限制 |

## 3. 背景覆盖
| # | 缺失主题 | 为什么重要 | 应引哪篇(arXiv ID) | 加在哪节 |
|---|---|---|---|---|
| B1 | **HD 关联函数的宇宙方差与脉冲星方差分解** | 决定 $P\to\infty$ 时 HD 测量的理论极限地板，也是 Fujimoto & Takahashi (`arXiv:2602.01108`) 三阶偏度计算的直接前提 (conf=0.98) | `arXiv:2205.05637` (Allen, PRD 2023); `arXiv:2407.10968` (Allen & Romano 2024); `arXiv:2508.21131` (Cosmic variance in PTA anisotropy 2025) | §2.4, §3.1, §4.2 |
| B2 | **NANOGrav 15yr 官方各向异性搜索与 SMBHB 检出率预测** | 替换文中虚构的 `Isi:2024`，提供真实的 NG15 各向异性上界（$<20\%$）及按频段分辨的 SMBHB 各向异性功率谱预测 (conf=0.98) | `arXiv:2306.16221` (NANOGrav 15yr Anisotropy, ApJL 2023); `arXiv:2305.05690` (Sato-Polito & Kamionkowski, PRD 2024); `arXiv:2407.08705` (Lemke et al., PRD 2025) | §1, §3.1, §4.1 |
| B3 | **PTA 各向异性重叠约化函数 (Anisotropic ORF) 多极展开** | 现有 PTA 社区处理 $\mathcal{P}(\hat{k}) = 1+\sum a_{\ell m}Y_{\ell m}$ 的标准工具，是检验 §2.3 命题 2.1 是否给出新物理预测的基准 (conf=0.95) | `arXiv:1306.5394` (Mingarelli et al., PRD 2013); `arXiv:2006.14570` (Ali-Haïmoud, Smith & Mingarelli, PRD 2020); `arXiv:2407.14460` (PTA sensitivity to anisotropies 2024) | §2.3, §5.1 |
| B4 | **全局双曲洛伦兹配边与函子型 AQFT 等价定理** | 直接解决 §5.2 L364“洛伦兹配边尚缺严格定义”的漏洞，用真正研究洛伦兹 AQFT 配边的数学物理文献替代泛泛的 `arXiv:2311.11026` (conf=0.96) | `arXiv:2308.01026` (Bunk, MacManus & Schenkel, Lett. Math. Phys. 2025); `arXiv:2504.15759` (BMS Equivalence Theorem 2025) | §2.1, §5.2 |
| B5 | **观测者世界线引力代数与动态视界/宇宙学广义熵** | 展示近 3 年 Hollands-Wald 学派如何在弯曲时空/宇宙学中将世界线局域代数转化为可计算的不变量 (conf=0.92) | `arXiv:2406.01669` (Kudler-Flam, Leutheusser & Satishchandran 2024); `arXiv:2309.15897` (PRD 2025); `arXiv:2402.00818` (Hollands, Wald & Zhang, PRD 2024) | §2.2, §3.1 |

## 4. 总体判断
- **是否达到目标期刊水平**：**否（需大修 Major Revision / 重写后重投）** (conf=0.96)。当前版本若直接投递 PRL/PRD/JCAP/JHEP，会因幻觉参考文献、定理 3.1 幂次符号反置、以及范畴论包装与初等散粒噪声计算脱节在初审或一审被拒。
- **最致命的 3 个问题（审稿人最可能拒稿的理由）**：
  1. **参考文献存在多处幻觉与张冠李戴（M1, conf=0.99）**：`Isi:2024` (`arXiv:2401.04789`)、`Mingolla:2023` (`arXiv:2301.07734`)、`Gong:2021` (`arXiv:2105.10954`) 等在 arXiv 上指向完全无关的数学/原子物理/核聚变论文，审稿人一查即直接拒稿。
  2. **数学形式体系与物理推导实质脱节 + 定理 3.1 $P^{-1/2}$ 方向写反（T2 & M2, conf=0.96）**：前半部分搭起 extended AQFT / Lurie 配边高塔却未做任何非平凡代数计算，后半部分核心判别不等式 Eq.(15) 随脉冲星对数 $P$ 的标度写反，且 §4.2 ($\mathrm{SNR}\sim 140$) 与 §6 ($\mathrm{SNR}\sim 1\text{--}3$) 数值自相矛盾。
  3. **遗漏 Allen (2023) 宇宙方差且误引 Grimm (2025)（M3 & B1, conf=0.95）**：忽略有限源干涉带来的不可约 HD 宇宙方差地板，并把 Grimm et al. (`arXiv:2404.05670`) 关于星系成团对 HD 方差的贡献误读为宇宙学背景 $10^{-5}$ 均值各向异性。
- **修复工作量估计**：**天级（约 3–5 天）** (conf=0.90)——其中清洗幻觉文献、删 AI 元叙事、修正 Eq.(15) 标度与统一 SNR 数值需 **1 天**；引入世界线涂抹准自由高斯态相对熵/KL 散度计算并纳入 Allen 宇宙方差重绘 Fig.2/Fig.3 需 **2–4 天**。

## 附录：对标论文清单
1. `arXiv:2306.16221` (Agazie et al. [NANOGrav], ApJL 956, L3, 2023) — NANOGrav 15yr 官方各向异性搜索真身，揭露文中 `Isi:2024` (`arXiv:2401.04789`) 为幻觉引用并提供真实上界 (conf=0.99)。
2. `arXiv:2404.05670` (Grimm, Pijnenburg, Cusin & Bonvin, JCAP 03, 011, 2025) — 证明大尺度星系成团不改变 HD 均值仅增加 HD 方差，直接暴露本文 §3.2 L296 对其结论的误读 (conf=0.98)。
3. `arXiv:2602.01108` (Fujimoto & Takahashi, PRD accepted, 2026) — 在 Allen (2023) 框架上推导混叠噪声区 HD 三阶偏度，核实了本文 §4.1 第三点引用真实有效，但凸显本文缺失 Allen (2023) 基础 (conf=0.98)。
4. `arXiv:2401.10680` (Kehagias & Riotto, JCAP 06, 059, 2024) — 用天球共形/洛伦兹对称性简洁导出 HD 曲线与三点关联，确立顶刊用对称性重导 HD 的行文 taste 标杆 (conf=0.97)。
5. `arXiv:2205.05637` (Allen, PRD 107, 043018, 2023) & `arXiv:2407.10968` (Allen & Romano, 2024) — 确立 HD 曲线的 pulsar variance 与不可约 cosmic variance 分解，证伪本文 $P\to\infty$ 误差无限趋零假设 (conf=0.98)。
6. `arXiv:2407.08705` (Lemke, Mitridate & Gersbach, PRD 111, 063068, 2025) & `arXiv:2305.05690` (Sato-Polito & Kamionkowski, PRD 109, 123544, 2024) — 给出 SMBHB 频域各向异性与 NG15/IPTA 检出概率（$2\%\text{--}28\%$），校准本文 §4.2 过度乐观的 $\mathrm{SNR}\sim 140$ (conf=0.96)。
7. `arXiv:2308.01026` & `arXiv:2504.15759` (Bunk, MacManus & Schenkel, Lett. Math. Phys. 2025 / 2025) — 严格建立全局双曲洛伦兹配边伪范畴/伪运算元与 AQFT 的等价定理，指出本文把两条类时世界线当配边的定义缺陷 (conf=0.96)。
8. `arXiv:2406.01669` & `arXiv:2309.15897` (Kudler-Flam, Leutheusser & Satishchandran, 2024 / PRD 2025) & `arXiv:2402.00818` (Hollands, Wald & Zhang, PRD 2024) — 示范如何在观测者世界线和动态时空中严格构造引力算子代数与相对熵 (conf=0.94)。
9. `arXiv:1306.5394` (Mingarelli et al., PRD 2013) & `arXiv:2407.14460` (2024) — 确立各向异性重叠约化函数 (ORF) 的球谐多极展开标准，用于替除文中虚构的 `Mingolla:2023` (`arXiv:2301.07734`) (conf=0.97)。
