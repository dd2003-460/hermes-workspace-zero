# 01 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/01/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-10-28 19:28

## 概览

- 字段总数：**3**
- 待办（pending / research_required）：**1**
- 分组：primary_objective×1、baseline_knowledge×1、research_gaps×1

## 字段明细

### primary_objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal | stage2_mr_execution_longevity_orthogonal | confirmed | 1.00 | material | 否 |

### baseline_knowledge

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| known | established_repo_facts | confirmed | 0.95 | material | 否 |

### research_gaps

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| unknown | data_access_and_coverage_gaps | research_required | 0.80 | material | 否 |

## 证据与备注

### goal

把寿命正交贡献排序研究推进到阶段2实际执行：锁定 R>=4.2 + TwoSampleMR/MVMR 环境，按预注册计划（repo/docs/20_方法/阶段2分析计划.md）依次通过三道硬门禁（Step1 阳性对照2/2、Step2 负对照全部不显著、Step3 条件F>=10），产出可跑 A 级暴露的 L1 单变量 MR 点估计+95%CI，repo 内 verify_integrity.py exit=0 并 commit+push 到 GitHub main。全程走 1-loop 六阶段，整条链路默认外包 arena，只降通道不降流程。

证据：
- /Users/a1-6/Desktop/workspace/projects/健康长寿/D1-longevity-orthogonal/loop-state.json
- repo/docs/20_方法/阶段2分析计划.md

### known

2026-10-28 一手核实（repo 克隆 + 文件直读）：阶段1（IV 可得性实测）2026-10-21 并入 main 已完成；阶段2 从未运行（无 R 环境 + 无数据凭据），仓库目前不含任何本项目自算的因果估计（README 明示）。预注册稿已锁死停止规则/主结局/负对照阈值，改动必须记修订记录。可执行版 scripts/stage2_mr.R 从未运行，gate_fail 为硬门禁，首用先 --dry-run。阶段2 A 级暴露 5 个（stage2_config.R 自动生成）：F01 ukb-b-20261 / F03 ieu-b-38 / F04 ieu-a-300 / F08 ieu-b-40 / F15 ieu-a-1187(blocked)；F01/F03/F08 同含 UKB → MVMR 门禁触发，预注册「正确动作」= F08 换 ieu-a-835（Locke 2015 GIANT，无 UKB，F08 降 B 级）。主结局 7 个（含 ieu-a-7 / ebi-a-GCST005843 优先 006908 / ieu-a-1102 / ieu-a-966 / ieu-b-2 等）；负对照 3 个（发色/左利手/初潮，各有 valid_for 范围）。T2D ncontrol 用更正值 593,952（cache_crossvalidation.csv）。本机 R 未装（which R 空），brew 可用。

证据：
- repo/README.md
- repo/docs/20_方法/阶段2分析计划.md
- repo/data/derived/stage2_config.R
- repo/data/derived/cache_crossvalidation.csv
- repo/scripts/stage2_mr.R

### unknown

用户已决（2026-10-28 decision_log）：先无数据凭据跑可覆盖子集。由此产生以下待研究空缺（全部为阶段02 研究入口，未验证内容不伪装成默认值）：(1) 4 个 A 级暴露 id 全部挂在数据平台上，免凭据时能否取数；(2) 减重替代暴露 GIANT 官网公开包的可得性与合法下载路径；(3) 免凭据下可组的合法 暴露×结局 配对覆盖表（公开队列端点 × 开放暴露）；(4) 他汀代理暴露的样本量缓存值与论文发现阶段值不一致，开跑前须核对；(5) 预注册主结局与公开队列对应结局的映射关系；(6) TwoSampleMR 对公开队列端点的免凭据下载行为。任一覆盖缺口 ⇒ 对应暴露/结局标 blocked 记入 execution-log，不补造。
