# T17 阶段 03 覆盖证明（coverage_proof）

## G2 目标三要素 → DAG/证据映射

| G2 要素 | 承接方式 | 状态 |
|---|---|---|
| ①监控 runner 直到退出 | 02/02.5 字段已 confirmed 收口：EXITED @ 2026-11-04 00:19+0800，pgrep exit 1，官方聚合 locomo_results_20261104_001903.json 落盘（total_questions=610） | 既有证据引用，不重复建节点 |
| ②聚合各 cutoff 分数 + top_10 overall vs smoke01 baseline 对比表 + temporal ≥50% 判定 | 主体已由 02 字段 confirmed 收口：official top_10 overall 45.57% / temporal 38.41% vs smoke01 60.0%/0%（噪声 ±1.5pp），有效样本 conv2+3 73.22%/73.13%；final-report 已落盘 results/locomo/locomo-full01-final-report.md。02.5 指出的因果缺口（缺 matched before/after 对照）由 **N3** 补足 | 既有证据 + N3 增量 |
| ③更新 decomp loop-state 并 commit+push | **J** 节点承接：decomposition.md T17 条目更新 + 最终报告合并 + commit | J 节点 |

## 02.5 cross_validation action_items → DAG 节点

| action_item（perplexity + chatgpt 双 provider 共识） | 承接节点 |
|---|---|
| ①重跑前预定义 dirty-run 判据（排除标准应预定义，防 selection bias） | N1 |
| ②matched before/after 对照方案（补 "temporal 修复有效" 因果声明的证据缺口） | N3 |
| ③异源 judge 抽样复核（answerer/judge 同模型相关误差 caveat） | N4 |

## 完整性声明

- 无遗漏目标要素：G2 三要素与 02.5 三项 action_items 全部有承接（节点或既有 confirmed 证据）。
- 无未核验前提：DAG 所有步骤输入均来自 02/02.5 已核验字段（runner EXITED、官方聚合分数、脏数据根因 conv0 检索全空/conv4 生成全空、双 provider 交叉验证裁决）。
- 依赖完整且无循环：拓扑序 N1 → {N2, N4} → N3 → J（见 task-graph.json cycle_check）。
- user/agent 粒度：全部节点 owner=agent；唯一 user 触点（N2 server 健康确认）显式标为异步等待点，不构成同步阻塞，无执行顺序歧义。