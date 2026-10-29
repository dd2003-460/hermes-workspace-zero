# 阶段 01 工件：目标分解（寿命正交贡献排序 · 阶段 2 MR 执行）

> 数据源：本目录 `fields.json`（唯一数据源，三字段已填齐：goal=confirmed 1.0 / known=confirmed 0.95 / unknown=research_required 0.8）。
> 规范：`loop/prompt-first/01-goal-decomposition.md`（递归分解到原子 + 正交 + 空缺清单）+ `00-common-review.md`（审阅标准）。
> 历史工件 `state.json`（status=unclarified）与 `tasks/` 4 组 json+md 为 field 路径的历史快照，保留只读、不删不改；本工件是 prompt-first 路径的阶段 01 收口工件。

## 1. 目标要交付什么

把寿命正交贡献排序研究推进到阶段 2 实际执行，产出：
1. `repo/data/derived/session_info.txt`（R 版本 + TwoSampleMR/MVMR 版本或 commit hash + 运行日期）；
2. 三道硬门禁证据：Step1 阳性对照 2/2（吸烟→肺癌、LDL→冠心病，β>0 且 p<0.05）；Step2 负对照（发色/左利手/初潮，按 valid_for）全部 |z|<1.96；Step3 双变量条件 F≥10（F08 按预注册用 ieu-a-835）；
3. L1 单变量 MR 结果表：覆盖内 暴露×结局 的 IVW 点估计 + 95%CI + p（每暴露引用 ≥3 独立来源），无 token 覆盖率写入 execution-log；
4. `repo` 内 `python3 scripts/verify_integrity.py` exit=0，且新 commit push 到 GitHub main 留痕。

若 ②③④ 任一门禁不过：按预注册停止，以 gate-fail 证据结案并诚实标注，不降级验收。

## 2. 分解树（正交拆到原子）

```
阶段2 MR 执行
├── F-环境（R + 两包 + 取数凭据策略）
│   ├── 环境锁定：R≥4.2 + TwoSampleMR + MVMR 版本/commit 落 session_info.txt
│   └── 凭据策略：无 OpenGWAS token（用户 2026-10-28 已决）→ 跑开放数据可覆盖子集，未覆盖暴露标 blocked 不补造
├── F-门禁（预注册三道硬门禁，顺序不许跳）
│   ├── 阳性对照 2/2（吸烟→肺癌、LDL→冠心病）
│   ├── 负对照（发色/左利手/初潮，按 valid_for）
│   └── 双变量条件 F≥10（含 ≥2 暴露共用 UKB 的 gencov=0 硬门禁，F08 换 ieu-a-835 规避）
├── F-主分析（L1 单变量 MR）
│   ├── 暴露×结局 配对集 = 免凭据覆盖表（空缺 U3 产出）
│   └── 每暴露 ≥3 独立来源引用
├── F-数据（摘要统计质量与裁决）
│   ├── 免凭据可得性：4 个 A 级暴露 id（空缺 U1/U6）
│   ├── GIANT 公开包下载路径（空缺 U2）
│   ├── LDL 样本量缓存 173,082 vs 论文 94,595 裁决（空缺 U5）
│   └── 主结局 ↔ 公开队列结局映射（空缺 U4）
├── F-完整性（verify_integrity.py C14 等全部校验 exit=0）
└── F-留痕（commit + push 到 GitHub main）
```

正交性说明：六因素各管一段互不重叠（环境 / 门禁 / 主分析 / 数据 / 完整性 / 留痕）；F-数据 是 F-门禁、F-主分析 的输入但不含它们的判定逻辑。

## 3. 三字段内容（引自 fields.json，原样保留语义）

### 【goal】（confirmed，conf 1.0）
把寿命正交贡献排序研究推进到阶段 2 实际执行：锁定 R≥4.2 + TwoSampleMR/MVMR 环境，按预注册计划（`repo/docs/20_方法/阶段2分析计划.md`）依次通过三道硬门禁（Step1 阳性对照 2/2、Step2 负对照全部不显著、Step3 条件 F≥10），产出可跑 A 级暴露的 L1 单变量 MR 点估计+95%CI，repo 内 verify_integrity.py exit=0 并 commit+push 到 GitHub main。全程走 1-loop 六阶段，整条链路默认外包 arena，只降通道不降流程。
- 范围：环境锁定 → 阳性对照 → 负对照 → 条件F → L1 单变量 MR（4 个可跑 A 级暴露）→ 完整性自检 → 提交推送
- 范围外：Step 5 L2 MVMR 主分析、东亚轨对照分析、F15 抑郁（nsnp=10000 截断版本轮 blocked）、阶段 1 重做

### 【known】（confirmed，conf 0.95；2026-10-28 一手核实）
- 阶段 1（IV 可得性实测）2026-10-21 并入 main 已完成；阶段 2 从未运行，仓库不含任何本项目自算的因果估计（README 明示）。
- 预注册稿已锁死停止规则/主结局/负对照阈值，改动必须记修订记录（禁静默修改）。
- 可执行版 `scripts/stage2_mr.R`（450 行）从未运行，gate_fail 为硬门禁（条件 F 不达标→stop()），首用先 `--dry-run`。
- 阶段 2 A 级暴露 5 个（stage2_config.R 自动生成）：F01 ukb-b-20261 / F03 ieu-b-38 / F04 ieu-a-300 / F08 ieu-b-40 / F15 ieu-a-1187(blocked)；F01/F03/F08 同含 UKB → MVMR 门禁触发，预注册正确动作 = F08 换 ieu-a-835（Locke 2015 GIANT，无 UKB，F08 降 B 级）。
- 主结局 7 个（含 ieu-a-7 / ebi-a-GCST005843 优先 006908 / ieu-a-1102 / ieu-a-966 / ieu-b-2 等）；负对照 3 个（发色/左利手/初潮，各有 valid_for 范围）。
- T2D ncontrol 用更正值 593,952（cache_crossvalidation.csv，缓存 1,178 系误取巴基斯坦裔病例数）。
- 本机 R 4.6.1 已装，brew 可用；TwoSampleMR 自 2024-05 起取数需 OPENGWAS_JWT。

### 【unknown】（research_required，conf 0.8）
用户已决（2026-10-28 decision_log）：先无数据凭据跑可覆盖子集。由此产生以下待研究空缺（全部为阶段 02 研究入口，未验证内容不伪装成默认值）：
1. 4 个 A 级暴露 id 全部挂在数据平台上，免凭据时能否取数；
2. 减重替代暴露 GIANT 官网公开包的可得性与合法下载路径；
3. 免凭据下可组的合法 暴露×结局 配对覆盖表（公开队列端点 × 开放暴露）；
4. 他汀代理暴露的样本量缓存值与论文发现阶段值不一致，开跑前须核对；
5. 预注册主结局与公开队列对应结局的映射关系；
6. TwoSampleMR 对公开队列端点的免凭据下载行为。
任一覆盖缺口 ⇒ 对应暴露/结局标 blocked 记入 execution-log，不补造。

## 4. 正交性核对（known 与 unknown 无词语重叠，逐项）

| 核对项 | known 覆盖 | unknown 覆盖 | 重叠判定 |
|---|---|---|---|
| 暴露 id 可得性 | 列出 5 个 A 级暴露 id 与 UKB 构成（静态事实） | 这些 id 免凭据时能否实际取数（动态行为，未验证） | 无重叠：已知的是「id 是什么」，空缺是「取不取得到」 |
| 结局 id | 列出 7 主结局 + 3 负对照及其 valid_for | 主结局 ↔ 公开队列结局的映射（未验证） | 无重叠：已知的是「预注册选了哪些」，空缺是「公开端点对应的 id 是哪个」 |
| GIANT 暴露 | F08 换 ieu-a-835 的决策与理由（已锁死） | ieu-a-835 对应公开包能否免凭据下载（未验证） | 无重叠：决策已知，可得性未知 |
| 样本量 | T2D ncontrol=593,952 已更正 | LDL ieu-a-300 缓存 173,082 vs 94,595 未裁决 | 无重叠：一更正一待定，对象不同 |
| 凭据 | 用户 2026-10-28 决策「先无 token 跑可覆盖子集」 | 免凭据行为的具体边界（哪些端点/行为，未验证） | 无重叠：决策已知，边界未知 |

结论：known/unknown 无词语重叠；无 pending 字段（3 字段 disposition = confirmed/confirmed/research_required）。

## 5. 空缺清单（= 阶段 02 输入，research_queue 6 项）

| # | 优先级 | 空缺 | 研究路径（目标源 + 搜索词 + 备用） | 阻塞影响 |
|---|---|---|---|---|
| U1 | P1 | GIANT 官网（Locke 2015 BMI，ieu-a-835）免凭据公开下载路径与数据格式 | GIANT 官网；搜索词 "GIANT consortium BMI gwas download" / "Locke 2015 body mass index genetic analysis s3 data"；备用：FinnGen BMI 替代 | 阻塞 F08 减重暴露可跑判定 |
| U2 | P1 | FinnGen R13 公开端点免凭据摘要统计下载（含 I9_IHD 等主结局映射） | FinnGen 官网 R13 公开 SS；搜索词 "FinnGen R13 summary statistics download" / "FinnGen I9_IHD cases 88476"；备用：UKB 开放部分/BBJ | 阻塞主结局映射与 L1 配对 |
| U3 | P1 | Biobank Japan 公开端点免凭据下载（bbj-a-107 等） | BBJ 官网公开 SS；搜索词 "Biobank Japan summary statistics download public" / "Biobank Japan R10 gwas download"；备用：跳过 BBJ 标 blocked | 阻塞多队列独立来源 |
| U4 | P2 | TwoSampleMR 对 FinnGen/BBJ 端点的免凭据 get_sumstats 行为 | 文档 + 小规模实测（1 个 pair）；搜索词 "TwoSampleMR get_sumstats FinnGen token" / "TwoSampleMR biobank japan data_id"；备用：curl 直下 CSV | 阻塞取数管线选型 |
| U5 | P2 | ieu-a-300（Willer 2013 LDL）样本量 173,082 vs 94,595 差异核实 | 论文/GWAS Catalog（PMID 24097068 / GCST002220）；搜索词 "Willer 2013 lipid gwas sample size 94595 discovery" / "GCST002220 sample size"；备用：token 核验（若有） | 阻塞 F04 他汀暴露 A 级开跑裁决 |
| U6 | P3 | 免凭据覆盖表汇总：可组 暴露×结局 合法 MR 对清单 + 每对独立来源 ≥3 核验 | U1-U5 结果汇合；搜索词 "Mendelian randomization open summary statistics BMI cardiovascular" / "FinnGen coronary artery disease I2D CAD gwas" | 阻塞 L1 配对集冻结（F-主分析 输入） |

## 6. 缺失条件阻塞的后继判断

- U1/U2/U3 → 决定「可跑 A 级暴露」到底是 4 个还是更少（影响门禁 ③ 与 L1 范围）；
- U4 → 决定取数管线（TwoSampleMR 免凭据 vs curl 直下 CSV）；
- U5 → 决定 F04 能否保持 A 级开跑（预注册要求开跑前裁决）；
- U6 → 冻结 L1 暴露×结局 配对集，之后不得漂移（候选集冻结原则）。

## 7. 下一阶段（02）第一批行动

按 U1→U2→U3（P1 可得性三连）→ U4（管线实测 1 pair）→ U5（样本量裁决）→ U6（覆盖表汇总）顺序执行；每项产出来源 + 观察时间 + 不确定性；缺口项标 blocked 不补造。

<!-- stage-review 回执块由独立 Reviewer 按 00-common-review 标准追加于本工件末尾；DONE 标记仅在 verdict=pass 且 reviewed_before_done=true 后写入。 -->

<!-- stage-review
verdict: pass
repair_stage: none
reviewed_before_done: true
artifact_sha256: e7c5938c2092fb4db8f32526e369ff5ca93d1cede01c7be8e5a370d9aad9c474
reviewer: 独立 subagent（d898700e-d14d-4a4a-9b19-d479851edad9），按 00-common-review 通用标准 + 01 阶段质检标准独立复核，非作者自审
依据: ①第 2 节 6 因素分解树（环境/门禁/主分析/数据/完整性/留痕）正交且合盖第 1 节全部 4 项交付物+gate-fail 结案路径；②第 3 节三字段忠实转写 fields.json（goal 1.0/known 0.95/unknown 0.8）无失真；③U1–U6 与 research_queue 6 项一一对应（unknown(1) 暴露端点取数合理拆为 U2 FinnGen+U3 BBJ 并汇入 U6 覆盖表）；④空缺表每条含目标源+搜索词+备用路径，阶段 02 可按 U1→U6 直接开工；⑤未验证内容未伪装成已验证（【known】抽查无越界断言，具体对象均在空缺表内标待研究）；⑥第 4 节 known/unknown 正交核对 5 行判定均成立
非阻塞观察（记录在案，不触发 revise）: ①【known】转写 T2D ncontrol 时省略"缓存 1,178 系误取巴基斯坦裔病例数"说明（细节省略不影响判断）；②unknown(1) 暴露端点取数核验未单列，由 U2/U3 具体化+U6 汇合承担（有 blocked 兜底）
-->

<!-- stage: done -->