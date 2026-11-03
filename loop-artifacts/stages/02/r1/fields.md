# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-11-04 02:19

## 概览

- 字段总数：**4**
- 待办（pending / research_required）：**4**
- 分组：research_findings×4

## 字段明细

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 研究未知因素：T17 runner 当前是否已退出 | EXITED — runner 已退出（第五轮观测 2026-11-04 00:19 +08:00，PID 37261 pgrep 无匹配），predicted_locomo-vllm/*.json = 620 ≥ 604 稳定达标；官方聚合产物 tools/memory-benchmarks/results/locomo/locomo_results_20261104_001903.json（4.76MB，含 metadata/metrics_by_cutoff/evaluations）已落盘——完成信号三项全部满足。本字段为纯本地工程状态调研（任务指令禁止 WebSearch/WebFetch），按 sibling 惯例保留 research_required + 空 evidence_refs，不伪造 HTTPS 来源 | research_required |  |  |  |
| 研究未知因素：各 cutoff 的实际分数值 | EXITED — runner 已退出（第五轮观测 2026-11-04 00:19 +08:00），官方聚合产物 locomo_results_20261104_001903.json 已落盘；final full01 各 cutoff overall/temporal 分数待本轮由绑定 Agent 从该文件读出并刷新 | research_required |  |  |  |
| 研究未知因素：对比表的呈现格式与落盘位置 | 对比表采用 markdown 表格（沿用既有对照表惯例），落盘到 tools/memory-benchmarks/results/locomo/ 下的诊断/报告 md 文件，并在 decomposition.md T17 条目同步结果 | research_required | 0.80 |  |  |
| 研究未知因素：decomposition.md 中 T17 条目的现状。 | 验证并记录：decomposition.md 中 T17 条目的现状。 | research_required | 0.90 |  |  |

## 证据与备注

### 研究未知因素：T17 runner 当前是否已退出

Commander 状态刷新（observed_at 2026-11-04T00:25+08:00），依据绑定 Agent ae621eb0a66708989 第五轮本机实测（field-apply ok=true, added=1 已持久化至 tasks/02-r1-field-T17-runner-194b873314.json）：(1) pgrep -f 'benchmarks.locomo.run' 无匹配，exit code 1 → PID 37261 已退出；(2) ls results/locomo/predicted_locomo-vllm/*.json | wc -l = 620 ≥ 604 阈值且稳定（较上一轮 618 +2，最新 conv4_q25/q24 mtime ≈ 2026-11-04 00:19 +08:00，conv4_q23 23:51、conv4_q22 23:38）；(3) 今日新聚合产物 locomo_results_20261104_001903.json（mtime 2026-11-04 00:19 +08:00，4.76MB）已出现，python3 json.load 验证含 metrics_by_cutoff 键。退出时间窗口在 23:50~00:19 之间（无精确记录）。五轮轨迹：23:11 615 → 23:19 615(+0) → 23:32 616(+1) → 23:50 618(+2, RUNNING) → 00:19(+08:00) 620(+2, EXITED + aggregate landed)。logs/locomo_20261103_225713.log 尾部仍停留在 22:57:14 ingestion 行（conv0..4 chunks 419/369/663/629/680），无 'All conversations completed'/'Evaluation finished' 标记——该 log 在逐题生成阶段未写入，不影响退出判定。注：最终官方聚合 total_questions=610（conv0:152/conv1:81/conv2:152/conv3:199/conv4:26），与磁盘 620 文件数差 10 属正常（部分逐题文件未被计入聚合或存在重判覆盖），以官方聚合 JSON 为准。描述性本机路径（非伪造 URL）：tools/memory-benchmarks/results/locomo/locomo_results_20261104_001903.json、tools/memory-benchmarks/results/locomo/predicted_locomo-vllm/、tools/memory-benchmarks/logs/locomo_20261103_225713.log。

### 研究未知因素：各 cutoff 的实际分数值

状态刷新（observed_at 2026-11-04T00:25+08:00，Commander 记录）：runner PID 37261 已确认退出（pgrep 无匹配），predicted_locomo-vllm/*.json = 620 ≥ 604 稳定达标，今日新聚合产物 tools/memory-benchmarks/results/locomo/locomo_results_20261104_001903.json（4.76MB，含 metadata/metrics_by_cutoff/evaluations）已出现——目标完成信号三项全部满足。本字段数值需以该官方聚合文件为准重读：(1) metrics_by_cutoff 各 cutoff（top_10/top_20/top_50/top_200）overall accuracy 分子/分母；(2) temporal 子集 accuracy（若聚合 JSON 缺细分，用 predicted_locomo-vllm/*.json 620 个逐题文件本地重算补全并注明口径）；(3) vs smoke01 baseline（top_10/20/50/200 均 60.0%、temporal 0/2=0%，噪声 ±1.5pp）判定 temporal 修复是否达标 ≥50%。前一轮中途快照（2026-11-03T16:45+08:00，仅 conv0-3 共 583 题）参考值：overall top_10 0.485/top_20 0.489/top_50 0.494/top_200 0.491（conv0/conv1 污染拉低），有效样本 conv2+3 top_10 0.749、temporal top_10 51/67=0.761。说明性路径（非伪造 URL）：tools/memory-benchmarks/results/locomo/locomo_results_20261104_001903.json、tools/memory-benchmarks/results/locomo/predicted_locomo-vllm/、tools/memory-benchmarks/results/locomo/locomo-full01-diagnosis.md、locomo-smoke-report.md + locomo_results_20261021_044003.json、locomo-temporal-fix-verified.md + locomo_results_20261024_160459.json。按既有惯例：纯本地工程状态，外部事实门禁要求 HTTPS 来源，本机文件证据不伪造 URL，evidence_refs 保留空数组。

### 研究未知因素：对比表的呈现格式与落盘位置

本地工程惯例调研已完成，结论如下（待主 Agent 以本机文件复核后转 confirmed/inferred）：(1) 格式——沿用 markdown 表格，模板见 tools/memory-benchmarks/results/locomo/locomo-full01-diagnosis.md L15-21『对照表（temporal 修复验证）』：列 run|样本|temporal top_10|备注，含 smoke01/smoke-temporal-quick/full01 conv2+3 三行；(2) 落盘——tools/memory-benchmarks/results/locomo/ 目录（既有惯例：带时间戳 *_results_*.json + 诊断 md 如 locomo-full01-diagnosis.md、locomo-smoke-report.md、temporal-analysis.md），新对比表建议新建 locomo-cutoff-scores.md 或追加进 diagnosis md 对照表节；(3) 同步——projects/AI-计算科学/D1-persona-align/tasks/decomposition.md L83 T17 条目状态列 + loop-state（阶段 01 goal 要求）。disposition 暂记 research_required 的原因：runtime field-apply 对 role=research_findings 且 disposition∈{confirmed,inferred,assumed_default} 的字段硬性要求 evidence_refs 含具体 HTTPS 页面 URL（protocol.py _is_specific_source_url），不接受本机文件路径作为可复核来源；本字段为纯本地工程惯例调研、无外部事实成分，按协议不伪造 URL，故保留 research_required + 空 evidence_refs，上述本机证据路径与行号摘要在此 rationale 内供主 Agent 直接复核。

### 研究未知因素：decomposition.md 中 T17 条目的现状。

外部事实校验器要求 HTTPS 来源，本任务明确为本地文件调研且禁止 WebSearch/WebFetch，故不伪造外部引用，按协议存为 research_required + 空 evidence_refs。本地调研结论（可人工复核）：projects/AI-计算科学/D1-persona-align/tasks/decomposition.md 第83行 T17 条目为『公理层3决策生成(subagent 521f8207)』，类型实验、不可并行、上游依赖 T16，状态列标注 done(3034字, 3决策, 4公理全应用)，即已执行完成且结果摘要落盘；下游 T18（第84行，依赖 T17）同样 done，链路已收口，无未勾选标记。关于『跑完出分/聚合 cutoff 分数/对比表』的既有计划文字：decomposition.md 全文 grep cutoff|聚合|对比表|出分 零命中，该文件不含此类计划描述；若存在应位于 memory/ 或 loop 阶段文档等其他位置，不在本条目内。待补证据：如需通过 field-apply 的 HTTPS 校验，需将上述本地发现另行发布到可访问 URL 或由主 Agent 豁免外部来源要求。
