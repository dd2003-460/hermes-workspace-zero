# T17 阶段 03 结构化 DAG（task_graph）

graph_id: 03-r1-t17-scoring-closeout · stage 03 r1 · 无循环（拓扑序 N1 → {N2, N4} → N3 → J）

```
N1 ──→ N2 ──┐
 │         ├──→ N3 ──┐
 └──→ N4 ────────────┴──→ J
        └──────────────→ J
```

## 节点定义

| id | title | owner | depends_on | writes | 验收方式 | 失败替代 |
|---|---|---|---|---|---|---|
| N1 | 预定义 dirty-run 判据（重跑前冻结阈值） | agent | — | artifacts/dirty-run-criteria.md | 判据脚本对 full01 复现 conv0/conv4 dirty、conv2/conv3 clean；阈值冻结并记录 sha | 阈值敏感时退化为人工标注 conv 清单并记录理由，不阻塞 N2 |
| N2 | 干净重跑 conv0 + conv4（清理残留 checkpoint） | agent | N1 | artifacts/clean-rerun-log.md | 按 N1 判据全部 conv clean；新聚合 total_questions=610 且 conv0/conv4 分数非零 | vLLM 超时复发 → 降级本地 python 聚合现有产物出分并标注 partial；两次重启仍失败则标记未解决 |
| N3 | matched before/after 对照分析（补 02.5 因果缺口） | agent | N1, N2 | artifacts/matched-comparison.md | 三 run × 四 cutoff × overall/temporal 对照表，每格含分子/分母，判定注明噪声带 ±1.5pp 与 temporal ≥50% 达标线 | 题集不对齐时按交集计算并显式标注样本差，不补造数据 |
| N4 | 异源 judge 抽样复核（judge validity caveat） | agent | N1 | artifacts/judge-audit.md | 分层抽样（每 category × CORRECT/INCORRECT 各 n≥10）异源重判，一致率 ≥85% 可信；<85% 触发置信度降级声明 | 异源 judge 不可用 → 记录为未解决项，明确风险不消除 |
| J | 汇总收口：decomposition.md T17 更新 + 最终报告 + commit | agent | N3, N4 | artifacts/closeout-summary.md | decomp T17 条目含三 run 分数与判定；git log 可见 commit；field-status 无残留 | commit 冲突 → rebase 重试一次，仍失败保留工作区改动并如实报告 |

## 边（edges）

N1→N2, N1→N3, N2→N3, N1→N4, N3→J, N4→J

## 并行组

- [N2, N4]：N1 完成后可并行执行

## user 触点说明

唯一 user 触点 = N2 中 server 8888 / vLLM 8787 健康确认，为**异步等待点**（agent 可自行 pgrep/curl 探测），不构成同步阻塞。全部节点 owner=agent，无 user/agent 混排歧义。