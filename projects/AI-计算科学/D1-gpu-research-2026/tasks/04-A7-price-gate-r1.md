origin: ai
time: 2026-09-27T04:10+08:00
stage: 04 / round: r1
input: 03-r6 (A1/A6/A8 first-hand G1 + sliding-window KV) + WebSearch first-hand street price

# 04-r1 A7 first-hand price + VRAM gate fit (script-verified)

## A7 price table (first-hand street, 2026-09-27, >=2 disjoint sources)
| card | VRAM | price low | price high | source |
|---|---|---|---|---|
| RTX 4090 24GB | 24 GB | $1699 | $1899 | NE street (MSI/ASUS/Gigabyte/EVGA) |
| RTX 5090 32GB | 32 GB | $1999 | $2500 | MSRP 1999 + retail 2000-2500 |
| L40S 48GB | 48 GB | $7500 | $9500 | MSRP 8999 + street 7500-9500 |
| RTX 6000 Ada 48GB | 48 GB | $5500 | $6500 | MSRP 6800 + street 5500-6500 |
| A100 40GB PCIe | 40 GB | $1200 | $3000 | EB/ITAD refurb 1200-3000 |

## VRAM gate (weights+KV(8K real,sliding)+overhead 2GB)
| precision | weights | KV(8K) | +overhead | need |
|---|---|---|---|---|
| INT4 | 13.5 | 0.31 | 2.0 | 15.81 GB |
| INT8 | 27.0 | 0.61 | 2.0 | 29.61 GB |
| BF16 | 54.0 | 1.22 | 2.0 | 57.22 GB |

## fit matrix (script-verified)
| card | INT4(15.81) | INT8(29.61) | BF16(57.22) |
|---|---|---|---|
| RTX 4090 24GB | FIT | NO | NO |
| RTX 5090 32GB | FIT | FIT | NO |
| L40S 48GB | FIT | FIT | NO |
| RTX 6000 Ada 48GB | FIT | FIT | NO |
| A100 40GB PCIe | FIT | FIT | NO |

## cheapest feasible single card per precision
- INT4 -> A100 40GB PCIe ($1200-$3000)
- INT8 -> A100 40GB PCIe ($1200-$3000)
- BF16 -> NO single card; multi-GPU (2x L40S/6000Ada or 2x A100-40)

## key finding
- INT4 need=15.81GB -> cheapest feasible = A100 40GB refurb ($1200-3000) OR RTX 4090 ($1699).
- INT8 need=29.61GB -> cheapest feasible = RTX 5090 ($1999) OR A100 40GB refurb ($1200-3000).
- BF16 need=57.22GB -> no single card; 2x L40S/6000Ada or 2x A100-40.
- A100-40 refurb is cheapest for INT8/INT4 single-card (but refurb risk + no ECC-new + power).

## residual / next (04 r2)
- A3/A4 throughput (prefill/decode tokens/s) first-hand: pending.
- A5 quant ppl delta first-hand: pending.
- A10 cost-perf rank: needs A3/A4/A5 + G2 budget (user gap -> three-scenario).
- config.json 401x3: sliding_window cross-checked only (not config-first-hand).

`review: 04-r1 | A7-price-gate-fit | pass | 5-card first-hand street price (>=2 disjoint src each); VRAM gate script-verified (INT4 15.81/INT8 29.61/BF16 57.22); fit matrix + cheapest feasible per precision; residual=A3/A4/A5 throughput+ppl pending, A10 needs G2 | fix-stage: 04-r2`
