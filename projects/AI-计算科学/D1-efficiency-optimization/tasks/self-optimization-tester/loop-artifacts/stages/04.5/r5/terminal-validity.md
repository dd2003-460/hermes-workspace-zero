# R5.4 终态效度对照（run4 · n=1 定性首测）

> origin: ai · 2026-10-29 · Lead 独立复验（非执行者自评）
> 判定标准事先写死于 task-brief.md；本表为 Lead 侧独立重跑结果。

## 终态成败（oracle 口径）

| 项 | 值 | 证据 |
|---|---|---|
| check-run4.sh 退出码 | **0**（4/4 PASS：6.75 / 9.00 / 0.60 / 缺列 rc=1） | 2026-10-29 Lead 独立重跑，本次会话 |
| check-run4.sh sha256 | `bc286895baf9ced667c2f16f1716ad324a380398098a687d1bc45403f2dbc15c` | 与预登记 `check-run4.sha256` **一致**（求解者未改判定脚本）✓ |
| 终态判定 | **PASS**（一次性通过，无修改重跑记录） | loop-state.json iterations=1 + result.txt SUM=16.50 |

## 过程分 vs 终态成败

| 口径 | 分数 | 来源 |
|---|---|---|
| M1-M6 加权（Lead provisional） | 94.84 | run4/scoring-r5.json（caveat: 自估偏高风险，r4 实测偏差 +11.39） |
| M8 first-pass rate | 100（4/4 用例首次通过） | scoring-r5.json gates.M8_first_pass |
| 终态成败 | PASS（二值） | 上表 oracle 重跑 |

## 结论（n=1，仅定性，conf 0.6）

1. **方向一致**：过程分高（94.84）↔ 终态 PASS，无"高分低能"反例。
2. **M8 与 M3 共线判断（回应 run5 任务书问题）**：run4 中 M8=100 且 M3=100，单点无法算 r；但机制上 M8（验证点一次通过率）是 M3（断点完整率）的子集维度——断点完整 ≠ 一次通过（可完整执行但迭代 3 次才过）。建议 M8 保留为独立指标观察 n≥3 后再定权重，不并入 M3。
3. **局限**：n=1 定性；单一任务类型（CSV 求和）；Lead 既是流程设计者又是复验者（角色冲突已标注，r4 教训：自估系统性偏高，待 R5.1 双打分器校正）。
4. **下一步**：R5.1 第二打分器回执落盘后，用独立分替换 provisional 分重算本表；run5（arena 通道）补第二个终态数据点。

## 锚点

- check-run4.sh sha256 钉死：`bc286895baf9ced667c2f16f1716ad324a380398098a687d1bc45403f2dbc15c`（复验一致）
- 复跑命令：`bash run4/check-run4.sh` → EXIT=0
- 时间：2026-10-29T16:52:54+08:00
