# pfb-n-expansion-r4 — 分解

## 分解树

```
pfb-n-expansion-r4
├── A. 新 runs 生成 (45 = 3 arms × 5 questions × 3 new reps r4-r6)
│   ├── A1. 确认 ablation_harness.py 支持 rep 参数化 (r4, r5, r6)
│   ├── A2. 确认 S0/S1/S5 prompt 文件存在且正确
│   ├── A3. 批量执行: 每 arm 串行 5q×3rep, 3 arms 可并行 (GPU 单卡 → 实际串行)
│   └── A4. 监控: wall_s per run, token count, 失败重试
├── B. 评分 (45 new runs → scores-v3-r4.json)
│   ├── B1. 用 score.py v3 (smart truncation) 评分
│   ├── B2. 合并: scores-v3.json (45 old) + scores-v3-r4.json (45 new) → scores-v3-full.json (90)
│   └── B3. 验证: 新旧 runs 分数分布一致 (无 systematic shift)
├── C. 统计重算 (n=30/arm)
│   ├── C1. Bootstrap CI recompute (should be ~√2 narrower)
│   ├── C2. Paired sign test at n=30 pairs
│   ├── C3. Per-metric CIs
│   └── C4. 更新 RESULTS-FINAL.md (n=30 version)
└── D. 质量检查
    ├── D1. 新 runs 的 output_text 非空且 >500 chars (排除失败 run)
    ├── D2. M1 分数与旧 runs 同量级 (sanity check)
    └── D3. 如果某 arm 新 runs 分数异常偏移 >0.2 → 调查原因
```

正交性：A(生成) ⊥ B(评分) ⊥ C(统计) ⊥ D(质检)。流水线顺序 A→B→C→D。

## 缺口清单

| 子项 | 缺什么 | 阻塞？ |
|------|--------|--------|
| A1 | 需确认 harness 是否硬编码 rep=1..3 [待核验] | 可能 |
| A2 | prompt 文件已确认存在 (S0/S1/S5 × Q1-Q5) | 否 |
| A3 | GPU 时间: 45 runs × ~60s/run ≈ 45min (单线程) | 否 |
| B1-B3 | 无，score.py 已就绪 | 否 |
| C1-C4 | 无，纯计算 | 否 |
| D1-D3 | 无 | 否 |

[待核验] A1: ablation_harness.py 的 run_single() 是否接受任意 rep 编号，还是硬编码 1-3？需要读代码确认。

## 预估时间
- A: ~50min (45 runs serial, ~60s each + overhead)
- B: ~8min (45 × 2 judge calls × ~5s, 4 workers)
- C+D: ~5min
- Total: ~1h