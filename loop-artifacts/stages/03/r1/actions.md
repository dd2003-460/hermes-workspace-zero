# T17 阶段 03 行动分解（actions.md）

依据：GOALS.md G2 + 02/02.5 已核验证据 + 02.5 cross_validation action_items。
结构化 DAG 见同目录 task-graph.json（供 ralph graph-apply 逐节点执行）。

## N1 预定义 dirty-run 判据
- owner: agent
- 输入: 官方聚合 locomo_results_20261104_001903.json；per-conv 重算结论（conv0 检索全空 152/152，conv4 生成全空 26/26）
- 动作: 写可机检判据脚本（retrieval.total_results==0 占比、generated_answer 空串占比、cutoff_results 缺失率），阈值先验固定（如单 conv 脏题占比 >30% 判 dirty），落盘 dirty_run_criteria.py + 对 full01 的判定输出
- 依赖: 无（可与 N4 并行起步）
- 预期产出: loop-artifacts/stages/03/r1/artifacts/dirty-run-criteria.md（判据+阈值+full01 判定结果）
- 验收方式: 脚本对 full01 复现 conv0/conv4 dirty、conv2/conv3 clean；阈值在重跑前冻结并记录 sha
- 并行: 是（与后续 N4 并行）
- 失败替代: 若判据无法区分（阈值敏感），退化为人工标注 conv 清单并记录理由，不阻塞 N2

## N2 干净重跑 conv0 + conv4
- owner: agent（user 异步等待点：server 8888 / vLLM 8787 健康确认，非阻塞主链）
- 输入: N1 判据；run-full.sh resume 机制；checkpoint 污染根因（smoke01 残留 checkpoint 被 --resume 误判 complete）
- 动作: 清理 conv0/conv4 残留 checkpoint 后仅重跑该两 conv（--conversations 0,4），监控至退出且文件数稳定
- 依赖: N1
- 预期产出: 新聚合 JSON（含 conv0/conv4 有效分数）+ 重跑日志
- 验收方式: 按 N1 判据全部 conv clean；新聚合 total_questions 不变（610）且 conv0/conv4 分数非零
- 并行: 否（依赖 N1；N4 可并行）
- 失败替代: vLLM 超时复发 → 降级本地 python 聚合现有产物出分并在报告标注 partial；停止条件：两次重启仍失败则标记未解决，不伪装完成

## N3 matched before/after 对照分析
- owner: agent
- 输入: N2 干净重跑聚合 + smoke01 baseline（各 cutoff overall 60.0%/temporal 0%）
- 动作: 同题（matched question id）前后对照：full01-dirty vs full01-clean vs smoke01，按 cutoff×category 出 Δ，重点 temporal top_10 ≥50% 达标判定
- 依赖: N1 + N2
- 预期产出: loop-artifacts/stages/03/r1/artifacts/matched-comparison.md（markdown 对照表 + 判定）
- 验收方式: 表格含三 run × 四 cutoff × overall/temporal；每格有分子/分母；判定注明噪声带 ±1.5pp
- 并行: 否（join 于 N1+N2）
- 失败替代: 题集不完全对齐时按交集计算并显式标注样本差，不补造数据

## N4 异源 judge 抽样复核
- owner: agent
- 输入: full01 逐题预测 JSON（predicted_locomo-vllm/*.json）；02.5 指出的 judge validity caveat（answerer/judge 同模型相关误差）
- 动作: 分层抽样（每 category × CORRECT/INCORRECT 各 n≥10），用异源 judge（不同模型）重判，统计一致率
- 依赖: N1（判据用于抽样分层）
- 预期产出: loop-artifacts/stages/03/r1/artifacts/judge-audit.md（一致率 + 分歧样例）
- 验收方式: 总一致率 ≥85% 视为 judge 可信；<85% 触发分数置信度降级声明
- 并行: 是（与 N2/N3 并行）
- 失败替代: 异源 judge 不可用 → 记录为未解决项，报告中明确 judge validity 风险不消除

## J 汇总收口
- owner: agent
- 输入: N3 对照表 + N4 审计 + final-report 既有内容
- 动作: 更新 decomposition.md T17 条目（状态/结论/产物路径）；合并最终对比表进 results/locomo/ 报告；commit + push
- 依赖: N3 + N4
- 预期产出: decomposition.md 更新 + commit hash + 最终报告路径
- 验收方式: decomp T17 条目含三 run 分数与判定；git log 可见 commit；ralph field-status 无 ready/pending/research 残留
- 并行: 否（终点 join）
- 失败替代: commit 冲突 → rebase 重试一次，仍失败则保留工作区改动并如实报告

## user 步骤说明
唯一 user 触点 = N2 中 server/vLLM 健康确认，为**异步等待点**（agent 可自行 pgrep/curl 探测，无需用户交互），不构成同步阻塞。