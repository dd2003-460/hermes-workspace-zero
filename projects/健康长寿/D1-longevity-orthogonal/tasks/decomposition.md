# decomposition — 阶段2 MR 执行（2026-10-28）

> 规划纪律（m02353）：派 subagent 前必须先更新本文件；派发只执行任务表内条目。
> goal 全文 = `../loop-state.json` → goal_text（五字段）。

## 分解树

```
阶段2 MR 执行
├── 环境（可本地自决，无外部依赖）
│   └── R≥4.2 + TwoSampleMR(GitHub,记commit) + MVMR(GitHub) + MendelianRandomization + MRPRESSO
├── 数据（依赖 OpenGWAS token，用户阻塞项）
│   └── 摘要统计下载：4 暴露 + 7 结局 + 3 负对照结局 + 教育协变量 ieu-a-1001
└── 分析（依赖 环境+数据，按预注册顺序，不许跳步）
    ├── Step 0 环境锁定 → session_info.txt
    ├── Step 1 阳性对照 2/2（不过=管线问题，停）
    ├── Step 2 负对照（任一显著=残余混杂，停）
    ├── Step 3 条件 F（<10 停，不报点估计）
    └── Step 4 L1 单变量 MR（IVW + 敏感性）
→ 收尾：verify_integrity.py + commit + push
```

## 正交性核对

环境 / 数据 / 门禁(Step1-3) / 估计(Step4) / 留痕 五块互不重叠：门禁之间是硬序依赖（前不过后不跑），无并行重叠；数据获取与分析执行通道分离（下载=Python/R api，分析=TwoSampleMR）。

## 空缺清单（开跑前必须闭环或显式 blocked）

| 空缺 | 现状 | 处置 |
|------|------|------|
| OpenGWAS token | 未提供 | **已决（用户 2026-10-28）：先无 token 跑可覆盖子集**，token 到位后补齐全量 |
| 无 token 覆盖面（一手核对 2026-10-28） | 暴露侧 4 个 A 级 id 全在 OpenGWAS（ukb-b-20261 / ieu-b-38 / ieu-a-300 / ieu-b-40）= 全部要 token；唯一可开放替代 = BMI 走 GIANT 官网公开下载（ieu-a-835 同源 Locke 2015，未实证）；结局侧 FinnGen（I9_IHD 88,476 例等）与 BBJ（结直肠癌等）为公开端点。预注册的两个阳性对照暴露（ukb-b-20261、ieu-a-300）**都要 token** ⇒ 无 token 下 Step1 按预注册原设计跑不了 | T4 改为：先做覆盖表（哪些 暴露×结局 可无 token 组成合法 MR 对）→ 只跑覆盖内 pair（预期仅 BMI×FinnGen/BBJ 少数结局）→ 覆盖率与偏差记入 execution-log；Step1-3 门禁按预注册需 token 暴露，token 前以『open-data 管线验证』替代并记修订记录（不许静默改预注册） |
| F08 减重 UKB 重叠 | ieu-b-40 含 UKB，与 F01/F03 同含 UKB → MVMR 门禁触发 | 按预注册「正确动作」换 `ieu-a-835`（Locke 2015 GIANT，无 UKB，F08 降 B 级）；L1 轨不受门禁影响 |
| LDL ieu-a-300 样本量 | 缓存 173,082 vs 论文发现阶段 94,595 未证实 | 开跑前查论文正文或 token 核（阳性对照 2 用到） |
| 卒中 accession | ebi-a-GCST005843（跨祖先）vs ebi-a-GCST006908（欧洲亚组） | 预注册已定：优先 006908 |
| T2D ncontrol | 缓存 1,178 为误取 | 用 cache_crossvalidation.csv 更正值 593,952 |
| F15 抑郁 | nsnp=10,000 截断 | 本轮 blocked 不进主模型（config 已标 blocked=TRUE） |

## 任务表

| # | 任务 | 通道 | 依赖 | 状态 |
|---|------|------|------|------|
| T1 | 装 R≥4.2（brew install r）+ R 包（TwoSampleMR/MVMR from GitHub 记 commit + MendelianRandomization + MRPRESSO） | 本地 | 无 | **完成（2026-10-28）** 5/5 requireNamespace=TRUE：TwoSampleMR 0.7.13（MRCIEU/TwoSampleMR@`5e93ee7`）/ MVMR 0.4.9（WSpiller/MVMR@`f31bdf8`，步骤文件误写 MRCIEU/MVMR=404，以 repo 预注册引用为准）/ MendelianRandomization 0.10.0 / MRPRESSO 1.0 / ieugwasr 1.2.0；log=`tasks/t1b-r-env-finish.log`（macOS 无 setsid，改由 DSH job 承载） |
| T2 | OpenGWAS token | 用户输入 | 无 | **已决：先无 token**（用户 2026-10-28 选择），token 到位后补 T4 全量 |
| T3 | Step 0：环境锁定，session_info.txt 落盘 | 本地 | T1 | 未开始 |
| T4 | T4a 覆盖表（无 token 可组的合法 暴露×结局 pair，一手验证 GIANT/FinnGen/BBJ 开放下载）→ T4b 下载覆盖内摘要统计 → `stage2_mr.R --dry-run` | 本地 | T1 | 未开始 |
| T5 | Step 1 阳性对照 2/2 | 本地 R | T4 | 未开始 |
| T6 | Step 2 负对照（发色/左利手/初潮，按 valid_for） | 本地 R | T5 | 未开始 |
| T7 | Step 3 条件 F：先双变量（戒烟 + BMI ieu-a-835） | 本地 R | T6 | 未开始 |
| T8 | Step 4 L1 单变量 MR（4 暴露 × 结局，IVW+MR-Egger+加权中位数，每暴露 ≥3 独立来源引用） | 本地 R | T7 | 未开始 |
| T9 | verify_integrity.py exit=0 + audit 重跑 + commit + push main | 本地 | T8 | 未开始 |

> T5-T8 全部通过前不产生可写论文的点估计（预注册规则）。
> 下一 goal 候选：Step 5 L2 MVMR 主分析（含教育协变量入模）+ 东亚轨对照分析。