# pfb-v3-benchmark-hardening — 分解

## 分解树

```
pfb-v3-benchmark-hardening
├── A. 统计严谨性（当前最大短板）
│   ├── A1. Bootstrap 95% CI for per-arm Total (n=15/arm, 10k resamples)
│   ├── A2. Paired delta test: S5-S0, S1-S0, S5-S1 (per-run paired, sign test or Wilcoxon)
│   └── A3. Per-metric CIs (M1-M6 individually, not just Total)
├── B. R-06 judge independence 闭环
│   ├── B1. Document why same-family judge is a limitation (qwen judging qwen outputs)
│   ├── B2. Quantify the risk: how would scores shift under a hetero-judge? [待核验]
│   └── B3. Mitigation: add "judge family" caveat to all reported numbers (already in §4 rule)
├── C. 最终汇总表（paper-ready）
│   ├── C1. Consolidate scores-v3.json + scores-v3-secondary.json into single table
│   ├── C2. Add CI columns, significance markers, caveats
│   └── C3. Write RESULTS-FINAL.md with full provenance (judge version, truncation method, weights)
└── D. 已知不可修项记录
    ├── D1. S8D prompt unrecoverable → mark as "non-reproducible arm" in results
    ├── D2. Arena channel dead → R-06 hetero-judge blocked, document as future work
    └── D3. n=15/arm → statistical power limited, note effect size thresholds
```

正交性自检：A(统计方法) ⊥ B(judge独立性) ⊥ C(呈现) ⊥ D(局限记录)。无重叠。

## 缺口清单

| 子项 | 缺什么 | 阻塞？ |
|------|--------|--------|
| A1-A3 | 无，纯计算 | 否 |
| B2 | 需要异族 judge 跑同一批 runs 才能量化偏移量 | 是（arena dead + no API key） |
| C1-C3 | 无，数据已有 | 否 |
| D1-D3 | 无，文档工作 | 否 |

[待核验] B2: 异族 judge (GPT-4o/Claude) 对同 45 runs 的 M1 分数偏移量是多少？当前无法本地验证，只能标注为 conf-0.2 的理论风险。

## 执行顺序

A1→A2→A3 (纯 Python, ~5min) → C1→C2→C3 (汇总+写文档, ~10min) → B1+B3 (文档, ~5min) → D1-D3 (文档, ~5min) → B2 标记为 blocked-on-external