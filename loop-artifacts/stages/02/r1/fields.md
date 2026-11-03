# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-11-03 17:24

## 概览

- 字段总数：**4**
- 待办（pending / research_required）：**4**
- 分组：research_findings×4

## 字段明细

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 研究未知因素：T17 runner 当前是否已退出 | runner 未退出（截至 2026-11-03T08:33Z 本机实测）；新鲜重查待补——本轮观察通道受 runtime 门禁限制，无法由 Commander 直接产生新 ps/log 证据（详见 rationale） | research_required |  |  |  |
| 研究未知因素：各 cutoff 的实际分数值 | 验证并记录：各 cutoff 的实际分数值 | research_required | 0.85 |  |  |
| 研究未知因素：对比表的呈现格式与落盘位置 | 对比表采用 markdown 表格（沿用既有对照表惯例），落盘到 tools/memory-benchmarks/results/locomo/ 下的诊断/报告 md 文件，并在 decomposition.md T17 条目同步结果 | research_required | 0.80 |  |  |
| 研究未知因素：decomposition.md 中 T17 条目的现状。 | 验证并记录：decomposition.md 中 T17 条目的现状。 | research_required | 0.90 |  |  |

## 证据与备注

### 研究未知因素：T17 runner 当前是否已退出

最近一次本机实测（observed_at 2026-11-03T16:33+08:00 = 08:33 UTC）：PID 45660（full01 --resume，STARTED 16:00:32）与 PID 53388（--evaluate-only --rejudge conv2,3，STARTED 16:31:28）均在运行，logs/locomo_20261103_160033.log 持续写入、无结束标记。本字段为纯本地工程状态调研，任务指令禁止 WebSearch/WebFetch，证据只能来自本机 ps/日志文件，无法以 HTTPS URL 形式满足 runtime 外部事实门禁（protocol.py _external_evidence_issues），按协议不伪造来源、保留 research_required + 空 evidence_refs。本轮阻塞点记录（2026-11-03 ~09:2x UTC）：Commander Bash 被 COMMANDER_BASH_SCOPE_FIELD 限定为受控 ralph 命令 + 只读 RALPH 工件，无法直接执行 ps/tail 产生新证据；Agent 派发被 FIELD_AGENT_NOT_NEEDED 拒绝（两个 deferred 字段非 ready，且无绑定路径）。因此「runner 是否已退出」的新鲜重查无法在本轮完成；需 supervisor 重新开放字段后由绑定 Agent 执行，或走 APPROVALS #4 裁决（4.3 人工放行路径下由人工检查 runner 退出后收口）。待补证据：一次新鲜的 ps -p 45660,53388 + 日志尾部观察结果。

### 研究未知因素：各 cutoff 的实际分数值

T17 即 tools/memory-benchmarks 子模块的 LoCoMo benchmark（stage 01 known 所称 memory-benchmarks 子模块在本机实际路径为 tools/memory-benchmarks，工作区根下无同名目录）。cutoff 维度 = top-k 检索深度 {top_10, top_20, top_50, top_200}。已确认三组历史分数（见 evidence_refs）。当前 full01 全量 run 尚无聚合结果文件落盘（results/locomo/ 下最新 results JSON 停留在 10/24 smoke；predicted_locomo-vllm/ 有 583 个逐题预测文件覆盖 conv0-3，说明 runner 仍在跑 conv4-9，未产出最终 metrics_by_cutoff）。本字段数值由逐题 cutoff_results 本地重算得出，与 diagnosis 报告的 0.488/0.755 交叉一致（差异源于 conv3 新增 q196-q197 两题及 13-15% 空答案噪声），本机证据链完整可复核；但 (a) runtime 外部事实门禁要求 HTTPS 来源，本地文件无法以 URL 形式满足，按 sibling 任务同款处理降为 research_required；(b) 这是 runner 未退出时的中途快照（predicted_locomo-vllm/ 仅覆盖 conv0-3，conv4-9 未跑完，无最终 metrics_by_cutoff 聚合文件），最终全量分数（含 conv4-9 及排除 conv0/1 的正式口径）需等 runner 退出后以官方聚合脚本复核。待补证据：runner 退出后的官方聚合结果文件（results/locomo/ 新 results JSON）。

证据：
- 本机文件 tools/memory-benchmarks/results/locomo/predicted_locomo-vllm/conv*_q*.json（full01 run，583 题文件 conv0:152/conv1:81/conv2:152/conv3:198，每题含 cutoff_results{top_10,top_20,top_50,top_200}.{judgment,score}；observed_at 2026-11-03T16:45+08:00）— 本地重算：overall top_10 283/583=0.485 / top_20 285/583=0.489 / top_50 288/583=0.494 / top_200 286/583=0.491；按 conv(top_10)：conv0 0/152=0.000、conv1 21/81=0.259、conv2 118/152=0.776、conv3 144/198=0.727；有效样本 conv2+3 top_10 = 262/350=0.749；conv2+3 分 cutoff：top_10 temporal 51/67=0.761 / top_20 0.716 / top_50 0.716 / top_200 0.731
- tools/memory-benchmarks/results/locomo/locomo-full01-diagnosis.md — r280 中途诊断：full01 表面 top_10 overall 0.488(580题) 被 conv0/conv1 污染拉低，有效样本(conv2+3)真实水平 0.755、temporal 0.835；根因 conv0 检索全空(152/152 题 0 条记忆，smoke01 残留 checkpoint 被 --resume 误判 complete)、conv1 记忆残缺(仅 10 条 vs 应有 ~369)；待 runner 退出后收口动作尚未完成
- tools/memory-benchmarks/results/locomo/locomo-smoke-report.md + locomo_results_20261021_044003.json — smoke01(10/21, 5题)：top_10/20/50/200 均 60.0%，temporal 0/2=0%（修复前基线）
- tools/memory-benchmarks/results/locomo/locomo-temporal-fix-verified.md + locomo_results_20261024_160459.json — smoke-temporal-quick(10/24, 5题 temporal)：top_10 5/5=100%、top_20/50/200 各 4/5=80%（q6 在更高 cutoff 因 LLM 生成超时返回空答案，非检索错误）
- 本地检查方式说明：本字段为本地工程状态调研（任务指令明确禁止 WebSearch/WebFetch），证据为本机 tools/memory-benchmarks/results/locomo/ 下逐题预测 JSON 与诊断/报告 md；runtime 外部事实门禁要求 HTTPS 来源，本地文件证据无法以 URL 形式满足该格式，故按 sibling 任务同款处理降为 research_required

### 研究未知因素：对比表的呈现格式与落盘位置

本地工程惯例调研已完成，结论如下（待主 Agent 以本机文件复核后转 confirmed/inferred）：(1) 格式——沿用 markdown 表格，模板见 tools/memory-benchmarks/results/locomo/locomo-full01-diagnosis.md L15-21『对照表（temporal 修复验证）』：列 run|样本|temporal top_10|备注，含 smoke01/smoke-temporal-quick/full01 conv2+3 三行；(2) 落盘——tools/memory-benchmarks/results/locomo/ 目录（既有惯例：带时间戳 *_results_*.json + 诊断 md 如 locomo-full01-diagnosis.md、locomo-smoke-report.md、temporal-analysis.md），新对比表建议新建 locomo-cutoff-scores.md 或追加进 diagnosis md 对照表节；(3) 同步——projects/AI-计算科学/D1-persona-align/tasks/decomposition.md L83 T17 条目状态列 + loop-state（阶段 01 goal 要求）。disposition 暂记 research_required 的原因：runtime field-apply 对 role=research_findings 且 disposition∈{confirmed,inferred,assumed_default} 的字段硬性要求 evidence_refs 含具体 HTTPS 页面 URL（protocol.py _is_specific_source_url），不接受本机文件路径作为可复核来源；本字段为纯本地工程惯例调研、无外部事实成分，按协议不伪造 URL，故保留 research_required + 空 evidence_refs，上述本机证据路径与行号摘要在此 rationale 内供主 Agent 直接复核。

### 研究未知因素：decomposition.md 中 T17 条目的现状。

外部事实校验器要求 HTTPS 来源，本任务明确为本地文件调研且禁止 WebSearch/WebFetch，故不伪造外部引用，按协议存为 research_required + 空 evidence_refs。本地调研结论（可人工复核）：projects/AI-计算科学/D1-persona-align/tasks/decomposition.md 第83行 T17 条目为『公理层3决策生成(subagent 521f8207)』，类型实验、不可并行、上游依赖 T16，状态列标注 done(3034字, 3决策, 4公理全应用)，即已执行完成且结果摘要落盘；下游 T18（第84行，依赖 T17）同样 done，链路已收口，无未勾选标记。关于『跑完出分/聚合 cutoff 分数/对比表』的既有计划文字：decomposition.md 全文 grep cutoff|聚合|对比表|出分 零命中，该文件不含此类计划描述；若存在应位于 memory/ 或 loop 阶段文档等其他位置，不在本条目内。待补证据：如需通过 field-apply 的 HTTPS 校验，需将上述本地发现另行发布到可访问 URL 或由主 Agent 豁免外部来源要求。
