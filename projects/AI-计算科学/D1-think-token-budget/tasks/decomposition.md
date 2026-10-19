# tasks/decomposition.md — D1-think-token-budget
# origin: ai

规划纪律(m02353)：派 subagent 前必须更新本文件；派发只执行任务表内条目。

## 分解树

目标：减少 qwen3.8-27b-w8a16 (low-thinking) 的无效思考 token，不损质量。

```
R1 基线 (done)      — 3 提示臂 × ZebraLogic 子集
R2 复测 (done)      — 稳定复测
R3 前沿映射 (done)  — P0/P1/P5 × 10 AIME 2025 → P1 = prompt 级前沿
  ├─ 数据/评分      done (tasks/scorer_r3.py, results/round3/scores.csv)
  ├─ P6 自适应臂    done (4 臂: A03✓/A16✓(scorer artifact)/A09✗超时/A27✗超时)
  ├─ findings 文档  → T1
  └─ loop-state it6 → T2
收尾
  ├─ T1: round3-findings.md 终稿 (P6 + P0 A27 + 最终前沿表 + 两层建议)
  ├─ T2: loop-state.json it6
  ├─ T3: 副脑质询 (subagent, 后台) — 挑战最终结论
  └─ T4: 用户最终答复 (m01118) + qanda-ledger 记账
```

## 正交性核对

- T1 (文档) 与 T3 (副脑) 独立可并行；T3 的产出可在 T1 定稿前并入或作脚注。
- T2 依赖 T1 的数据一致性；T4 依赖 T1。

## 空缺清单

- 未见社区对 qwen3.8-27b-w8a16 low-thinking 配置在 AIME 2025 上的 token 效率公开表（已搜, conf 中）→ R3 的实证价值即在此。
- P6 hard 分支的失败模式是「跑满输出上限」，不是推理错误 → 自适应提示需要 serving 层预算兜底（两层建议的依据）。

## 任务表

| ID | 条目 | 状态 | 备注 |
|----|------|------|------|
| T1 | round3-findings.md 终稿 | done | 155行, P6+P0 A27+前沿表+两层建议, memory/round3-findings.md |
| T2 | loop-state it7 | in_progress | 依赖 T1(done) |
| T3 | 副脑质询 subagent | pending | 后台派发, 不阻塞 T4 |
| T4 | 用户答复 + 台账 | pending | 依赖 T1 |
