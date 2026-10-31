# F8 IV skew prereg
# origin: human + ai
date: 2026-10-31 | PRE-REGISTERED

## Question
F7 closed: funding+basis same source. F8: option IV skew as entry signal.
Logic: skew spike = panic buying protection -> mean reversion bounce.

## Predictions (frozen)
- P1: corr(skew_change, next_day_ret) < -0.05
- P2: 5d avg ret after skew_z<=-1.5 > BTC buy-hold + 0.5%
- P3: must pass all 8 gates; partial = negative result

## Data
- Deribit API/S3 archive: DVOL, 25d skew, PCR (2019+)
- Fallback: CBOE BVIX daily

## Signal (frozen)
- S1: DVOL_z <= -1.5 -> long 5d
- S2: skew_chg_5d >= +2s -> long 3d
- S3: PCR >= 1.3 -> long 5d
- OR logic, 1x position, fixed-horizon exit

## Protocol (same as F6/F7)
- PIT: 00:00 UTC, t-1 data, t open fill
- Matrix: 3 sig x 3 thr x 5 win = 45 tests
- Gates: t>=2, >=30 trades, net>0, cross-win>=3/4, perm p<0.001 B=2000, PSR>0.95, BH-FDR@45, DSR>0
- Cost: 0.05% taker + 0.01%/0.02% slip
- Market: BTCUSDT, benchmark: buy-hold

## Fallback
- No Deribit data -> CBOE BVIX + funding skew proxy
- All FAIL -> timestamp route closed, go to macro or wrap-up report

## Checklist
1. Get Deribit history 2. Build run_f8.py 3. Backtest 4. Reconcile P1-P3
