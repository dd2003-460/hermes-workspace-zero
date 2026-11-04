# H1 Backtest Results — Funding Extreme × Same-Day Direction Grouping

**Run ID**: h1-backtest-v1  
**Date**: 2026-11-05  
**Design**: `f10-r5-h1-preregistration-draft.md` (pre-registered, frozen)  
**Code**: `h1_backtest.py` (same directory)

## Verdict: **FAIL**

H1 (negative funding extreme + same-day price direction grouping produces asymmetric returns) is **rejected** on OOS data. Both pre-registered conditions fail.

Per the preregistration protocol: **F10 closes as a negative result report.**

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total OOS events | 80 |
| G_up trades (direction = up) | 10 |
| G_down trades (direction = down) | 23 |
| Δgap (G_up − G_down) | **−2.38%** |
| 95% CI (block bootstrap) | [−4.92%, +1.03%] |
| Condition ① (CI excludes 0, G_up > G_down) | **FAIL** (CI includes 0; sign reversed) |
| Condition ② (8 gates for G_up) | **FAIL** (0/8 gates pass) |

The gap is **negative** — G_up performs *worse* than G_down, the opposite of the S5 hypothesis. However, the confidence interval includes zero, so even the reversal is not statistically significant.

---

## Per-Symbol Breakdown

### BTCUSDT
| Window | Events | G_up (n, mean ret) | G_down (n, mean ret) | Gap |
|--------|--------|--------------------|-----------------------|-----|
| 2020   | 1      | 0, N/A             | 1, +1.21%             | N/A |
| 2025   | 3      | 1, −0.51%          | 1, +0.37%             | −0.88pp |
| **Total** | **4** | **1**              | **2**                 | — |

BTC has very few negative funding extremes (only 4 across both windows). The 8h funding rate is capped near ±0.01% (±0.0001), making the p95 threshold hard to breach on the negative side.

### ETHUSDT
| Window | Events | G_up (n, mean ret) | G_down (n, mean ret) | Gap |
|--------|--------|--------------------|-----------------------|-----|
| 2020   | 1      | 0, N/A             | 1, +2.18%             | N/A |
| 2025   | 4      | 1, −4.11%          | 2, +3.82%             | −7.92pp |
| **Total** | **5** | **1**              | **3**                 | — |

ETH shows the largest negative gap (−7.9pp in 2025), but with n=1 in G_up this is a single-trade artifact, not a signal.

### SOLUSDT
| Window | Events | G_up (n, mean ret) | G_down (n, mean ret) | Gap |
|--------|--------|--------------------|-----------------------|-----|
| 2020   | 28     | 0, N/A             | 0, N/A               | N/A |
| 2025   | 43     | 8, −1.27%          | 18, +0.51%           | −1.79pp |
| **Total** | **71** | **8**              | **18**               | — |

SOL dominates the event count (71/80 = 89%) due to much wider funding variance (mean |rate| 1.39× BTC). All 28 events from 2020 failed trade execution (no 1h kline data cached for SOL 2020). The 2025 window shows G_up underperforming G_down by ~1.8pp.

---

## Gate Details (Condition ②)

| Gate | Requirement | Actual | Pass? |
|------|-------------|--------|-------|
| t ≥ 2.0 | t-statistic ≥ 2.0 | t = −1.55 | ✗ |
| n ≥ 30 | ≥ 30 G_up trades | n = 10 | ✗ |
| Net > 0 | Cumulative return positive | −14.81% | ✗ |
| Cross-window ≥ 3/4 | ≥ 3 of 4 windows positive | 0/3 | ✗ |
| Perm p < 0.001 | Permutation test p-value | p = 0.89 | ✗ |
| PSR > 0.95 | Probabilistic Sharpe Ratio | 0.000 | ✗ |
| BH-FDR | Benjamini-Hochberg rejection | Not rejected | ✗ |
| DSR > 0 | Deflated Sharpe Ratio | 0.000 | ✗ |

**0/8 gates passed.**

---

## Root Cause Analysis

### Why H1 fails

1. **Sample size collapse**: The primary hypothesis requires G_up (negative funding extreme + prior day was UP). This intersection is rare:
   - Negative funding extremes are already uncommon (especially for BTC/ETH where rates cluster near zero)
   - Requiring the prior day to be UP further halves the sample
   - Result: only 10 G_up trades pooled, far below the n≥30 gate

2. **SOL dominance distorts the pooled estimate**: SOL contributes 89% of all events. Its funding dynamics (much wider variance, more frequent negatives) are structurally different from BTC/ETH. Pooling them together is not a fair test of a unified mechanism.

3. **The S5 finding may be dataset-specific**: S5 (Shek 2026) found a +3.62pp gap using 274 events over a longer sample. Our OOS windows (2020 + 2025) capture different market regimes. The 2025 SOL events cluster around Oct 11–13 (a specific volatility episode), which may drive the results rather than a generalizable pattern.

4. **Direction conditioning doesn't help**: The core claim of H1 is that knowing the prior day's direction lets you filter funding extreme signals. In practice, the direction group that "should" benefit (G_up: enter long after a down day following negative funding) actually underperforms. This suggests the mean-reversion logic behind S5's finding does not hold out-of-sample.

### Data limitations

- **BTC/ETH 2020**: Only 1 event each. Insufficient for any meaningful inference.
- **SOL 2020**: 28 events found but 0 trades executed (no 1h kline data). These events are lost.
- **OI condition**: 2020 window uses funding-alone degradation (Bybit OI starts 2022). This means 2020 events lack the OI confirmation that R2 requires, potentially including false positives.
- **2025 SOL clustering**: 10 of 43 SOL events fall within 3 days (Oct 11–13), creating an effective sample size much smaller than 43.

---

## Implications for F10

Per the preregistration: **"If H1 FAIL → F10 closes as candidate D negative result report."**

This means:
- The daily-frequency direction prediction track (F10) is closed
- The negative result itself is publishable: "We attempted to replicate S5's direction-grouping effect out-of-sample and failed, suggesting the original finding was either regime-specific or subject to selection bias"
- The macro regime hypothesis (H_macro) was already rejected at literature level (F10-R5 survey)
- Both F10 sub-hypotheses now have definitive negative verdicts

### What this does NOT rule out
- S5's finding might still hold in its original sample (in-sample)
- A different conditioning variable (not same-day direction) might work
- Higher-frequency data (intra-day funding, order book features) might capture the signal better
- The effect might exist only in specific market regimes (high volatility, specific funding distributions)

---

## Reproducibility

```bash
cd /Users/a1-6/Desktop/workspace
python3 projects/金融/D1-financial-market-analysis/loop-artifacts/stages/05/r8/h1_backtest.py
```

Data sources:
- Binance spot API (daily + 1h klines): `r8/cache/{SYM}_kline_{1d,1h}_{year}.csv`
- Binance futures API (funding rates): `r8/cache/{SYM}_funding_{year}.csv`
- Bybit OI cache: `r6/cache/bybit_oi/{SYM}_oi_1d.csv`
- Local BTC 2020 data: `projects/金融/quant-capital-flow/tasks/stage03/toy-model/data/`

Random seeds: bootstrap=42, permutation=42

---

## Appendix: Event Timeline (SOL 2025 Top Events)

| Date | Funding Rate | Direction | Group |
|------|-------------|-----------|-------|
| 2025-10-11 08:00 | −0.3028% | — | — |
| 2025-10-11 16:00 | −0.2039% | — | — |
| 2025-10-12 00:00 | −0.1587% | — | — |
| 2025-10-12 08:00 | −0.1250% | — | — |
| 2025-10-12 16:00 | −0.1234% | — | — |
| 2025-01-20 08:00 | −0.0712% | — | — |
| 2025-10-13 08:00 | −0.0607% | — | — |
| 2025-10-13 00:00 | −0.0572% | — | — |
| 2025-02-04 08:00 | −0.0558% | — | — |
| 2025-03-30 16:00 | −0.0401% | — | — |

(Only top 10 shown; full event list in `h1-backtest-results.json`)