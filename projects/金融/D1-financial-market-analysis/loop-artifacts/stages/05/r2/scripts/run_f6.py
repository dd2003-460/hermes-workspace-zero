#!/usr/bin/env python3
"""# origin: ai
F6 跨市场验证 — ETH/SOL funding-rate signal backtest (05 r2, pre-registered).

Protocol: t06-s2s3-preregistration.md §3 (frozen 2026-10-20) + S1 04r1 同构协议。
Deviation (recorded): B1 降级 — S2 美股数据源全断，S2→ETHUSDT、S3→SOLUSDT（Binance vision bulk）。
Data: local cache/ klines zips + funding/ zips (this dir), built by build_f6.py.
PIT: same as S1 04r1 — decision at day 00:00 UTC, signal uses latest settled funding
     with ts_norm <= t - 1_day; trade at day's open (taker).
Signals (pre-registered, directions frozen): T1 sign / T2 short-crowding / T3 long-crowding.
Matrix: 3 regime x 3 threshold x 5 window = 45 tests per market.
Regime calendar (frozen from S1 prereg, applied to both markets):
  bull 2020-21 & 2024-25; bear 2022; range 2023.
Criteria F1-F8: t>=2 (excess), >=30 trades, net excess > 0, cross-window direction
  consistency >=3/4, permutation p<0.001 (B=2000), PSR>0.95, BH-FDR alpha=0.05 on 45, DSR>0 @ N=45.
Costs: taker 0.05% + slippage 0.01% base / 0.02% stress per side (inherited from t05).
Outputs (this dir): f6_backtest_results.json, f6_trades_{SYM}.parquet
Idempotent: rebuilds everything from zips every run.
"""
import csv, glob, hashlib, json, os, re, zipfile
from datetime import datetime, timezone, timedelta
import datetime as dt
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
R2 = os.path.dirname(HERE)  # stages/05/r2 (cache/ funding/ live here, scripts/ is HERE)
SEED = 20261020
N_PERM = 2000
N_TRIALS = 45
ALPHA = 0.05
TAKER = 0.0005
SLIP_BASE = 0.0001
SLIP_STRESS = 0.0002
DAY_MS = 86400000
FUNDING_LAG_DAYS = 1
MARKETS = ["ETHUSDT", "SOLUSDT"]
WINDOWS = [2021, 2022, 2023, 2024, 2025]
REGIME_OF_YEAR = {2021: "bull", 2022: "bear", 2023: "range", 2024: "bull", 2025: "bull"}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def verify_checksums():
    """B1-B2: verify all zips against official CHECKSUM files."""
    report = {}
    for d in ("cache", "funding"):
        ok = bad = missing = 0
        for zpath in sorted(glob.glob(os.path.join(R2, d, "*.zip"))):
            cpath = zpath + ".CHECKSUM"
            if not os.path.exists(cpath):
                missing += 1
                continue
            line = open(cpath).read().strip()
            if line.startswith("MISSING"):
                missing += 1
                continue
            official = line.split()[0].strip().lower()
            actual = sha256(open(zpath, "rb").read())
            if actual == official:
                ok += 1
            else:
                bad += 1
                print(f"CHECKSUM MISMATCH: {zpath}")
        report[d] = {"ok": ok, "bad": bad, "checksum_missing": missing}
    return report


def first_monday_avail(ym_name):
    """Conservative availability: first Monday of following month + 1 day (same rule as S1)."""
    ym = re.search(r"(\d{4})-(\d{2})", ym_name).groups()
    y, m = int(ym[0]), int(ym[1])
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    d = datetime(ny, nm, 1, tzinfo=timezone.utc)
    first_monday = d + timedelta(days=(7 - d.weekday()) % 7 or 7)
    return (first_monday + timedelta(days=1)).timestamp() * 1000


def build_klines(sym):
    rows = []
    for zpath in sorted(glob.glob(os.path.join(R2, "cache", f"{sym}-1d-*.zip"))):
        with zipfile.ZipFile(zpath) as z:
            for n in z.namelist():
                if n.endswith(".csv"):
                    with z.open(n) as fh:
                        first = fh.readline()
                    if first.startswith(b"open_time"):
                        df = pd.read_csv(z.open(n))
                        df = df.rename(columns={"open_time": "openTime", "close_time": "closeTime"})
                    else:
                        df = pd.read_csv(z.open(n), header=None,
                                         names=["openTime", "open", "high", "low", "close", "volume",
                                                "closeTime", "qv", "trades", "tbb", "tbq", "ignore"])
                    rows.append(df[["openTime", "open", "high", "low", "close", "volume"]])
    kl = pd.concat(rows, ignore_index=True)
    kl["openTime"] = kl["openTime"].astype("int64")
    kl = kl.drop_duplicates(subset="openTime").sort_values("openTime").reset_index(drop=True)
    for c in ["open", "high", "low", "close", "volume"]:
        kl[c] = kl[c].astype("float64")
    assert kl["openTime"].min() > 1e12, "timestamp not in ms"
    return kl


def build_funding(sym):
    rows = []
    for zpath in sorted(glob.glob(os.path.join(R2, "funding", f"{sym}-fundingRate-*.zip"))):
        with zipfile.ZipFile(zpath) as z:
            for n in z.namelist():
                if n.endswith(".csv"):
                    df = pd.read_csv(z.open(n))
                    cols = {c.lower().strip(): c for c in df.columns}
                    # Binance vision bulk fundingRate schema (2020+): calc_time,funding_interval_hours,last_funding_rate
                    ts_col = cols.get("calc_time") or cols.get("funding_time") or list(df.columns)[0]
                    rate_col = cols.get("last_funding_rate") or cols.get("funding_rate") or list(df.columns)[-1]
                    sub = pd.DataFrame({
                        "ts_raw": df[ts_col].astype("int64"),
                        "rate": df[rate_col].astype(float),
                    })
                    # B1 magnitude check: 16-digit us -> ms
                    sub["ts_norm"] = np.where(sub["ts_raw"] > 1e15, sub["ts_raw"] // 1000, sub["ts_raw"])
                    # conservative availability: file-level lag (month-end + first monday + 1d)
                    sub["avail_ms"] = first_monday_avail(os.path.basename(zpath))
                    rows.append(sub)
    f = pd.concat(rows, ignore_index=True)
    f = f.sort_values("ts_norm").drop_duplicates(subset="ts_norm").reset_index(drop=True)
    return f[["ts_norm", "rate", "avail_ms"]]


def signal_side(threshold, rate):
    if rate is None or np.isnan(rate):
        return 0
    if threshold == "T1":
        return 1 if rate >= 0 else 0
    if threshold == "T2":
        return -1 if rate <= -1e-4 else 0
    if threshold == "T3":
        return -1 if rate >= 2e-4 else 0
    raise ValueError(threshold)


def run_strategy(f, kl, threshold, regime_filter, cost_per_side):
    days = kl[["openTime", "open", "close"]].values
    o = days[:, 1].astype(float)
    c = days[:, 2].astype(float)
    ts = days[:, 0].astype(np.int64)
    f_ts = f["ts_norm"].values.astype(np.int64)
    f_rate = f["rate"].values.astype(float)

    out = []
    prev_pos = 0
    for i in range(len(ts)):
        cutoff = ts[i] - DAY_MS * FUNDING_LAG_DAYS
        idx = np.searchsorted(f_ts, cutoff, side="right") - 1
        rate = float(f_rate[idx]) if idx >= 0 else np.nan
        pos = signal_side(threshold, rate)
        if regime_filter is not None and REGIME_OF_YEAR.get(pd.Timestamp(ts[i], unit="ms").year) != regime_filter:
            pos = 0
        ret_open_close = c[i] / o[i] - 1.0
        # strategy PnL: position held over [t, t+1), entry at open
        strat_ret = pos * ret_open_close
        # funding cashflow: long pays positive rate, short receives
        cf = -pos * rate
        # cost on position change
        turnover = abs(pos - prev_pos)
        cost = turnover * cost_per_side
        net = strat_ret + cf - cost
        out.append({"ts": int(ts[i]), "open": o[i], "close": c[i], "rate": rate,
                    "pos": pos, "ret_excess": net, "turnover": turnover,
                    "trade": 1 if pos != prev_pos else 0})
        prev_pos = pos
    return pd.DataFrame(out)


def perm_test(rets, n_perm=N_PERM, seed=SEED):
    obs = stats.tmean_onesample(rets)[0] if hasattr(stats, "tmean_onesample") else np.mean(rets)
    n = len(rets)
    t_obs = np.mean(rets) / (np.std(rets, ddof=1) / np.sqrt(n)) if np.std(rets, ddof=1) > 0 else 0.0
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=n)
        t_p = np.mean(rets * signs) / (np.std(rets * signs, ddof=1) / np.sqrt(n)) if np.std(rets * signs, ddof=1) > 0 else 0.0
        if abs(t_p) >= abs(t_obs):
            cnt += 1
    p = (1 + cnt) / (n_perm + 1)
    return t_obs, p


def psr(sr_annual, rets):
    n = len(rets)
    if n < 3 or np.std(rets) == 0:
        return 0.0
    m, s = np.mean(rets), np.std(rets, ddof=1)
    g = stats.skew(rets)
    k = stats.kurtosis(rets, fisher=False)
    denom = s * np.sqrt(1 - 0.5 * g * (m / s) + (k - 3) / 4 * (m / s) ** 2)
    if denom <= 0:
        return 0.0
    z = (m - sr_annual / np.sqrt(252) * (1 / np.sqrt(252))) / (denom / np.sqrt(n))
    return float(stats.norm.cdf(z))


def dsr(sr_annual, rets, n_trials):
    n = len(rets)
    if n < 3 or np.std(rets) == 0:
        return 0.0
    m, s = np.mean(rets), np.std(rets, ddof=1)
    g = stats.skew(rets)
    k = stats.kurtosis(rets, fisher=False)
    denom = s * np.sqrt(1 - 0.5 * g * (m / s) + (k - 3) / 4 * (m / s) ** 2)
    if denom <= 0:
        return 0.0
    z = (m - sr_annual / np.sqrt(252) * (1 / np.sqrt(252))) / (denom / np.sqrt(n))
    e_max = np.sqrt(2 * np.log(n_trials)) - (np.log(np.log(n_trials)) + np.log(4 * np.pi)) / (2 * np.sqrt(2 * np.log(n_trials)))
    return float(stats.norm.cdf(z - e_max))


def bh_fdr(pvals, alpha=ALPHA):
    n = len(pvals)
    order = np.argsort(pvals)
    rejected = set()
    for rank, idx in enumerate(order, start=1):
        if pvals[idx] <= alpha * rank / n:
            rejected.add(idx)
    return rejected


def main():
    cksum = verify_checksums()
    results = {"meta": {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "n_perm": N_PERM, "markets": MARKETS,
        "deviation_B1": "S2 US data sources dead (Yahoo/Stooq/ifzq); S2->ETHUSDT, S3->SOLUSDT per TASKS F6 candidate",
        "sol_listing": "SOLUSDT first bar 2020-09-14 (exchange listing); SOL windows 2021-2025 unaffected",
        "checksums": cksum,
    }, "per_market": {}}

    for sym in MARKETS:
        kl = build_klines(sym)
        f = build_funding(sym)
        per_window = {}
        matrix = []
        strats = {}
        for th in ["T1", "T2", "T3"]:
            for rf in ["bull", "bear", "range", None]:
                key = (th, rf)
                strats[key] = run_strategy(f, kl, th, rf, TAKER + SLIP_BASE)
        for year in WINDOWS:
            w = {}
            for th in ["T1", "T2", "T3"]:
                df = strats[(th, None)]
                yr = (df["ts"] // 1000).apply(lambda x: dt.datetime.fromtimestamp(x, tz=timezone.utc).year)
                sub = df[yr == year]
                if len(sub) < 30:
                    w[th] = {"status": "insufficient_data", "days": int(len(sub))}
                    continue
                rets = sub["ret_excess"].values
                t_stat, p_perm = perm_test(rets)
                trades = int(sub["trade"].sum())
                net = float(sub["ret_excess"].sum())
                ann = float(np.mean(rets) * 252)
                w[th] = {
                    "days": int(len(sub)), "trades": trades, "net_excess_sum": round(net, 6),
                    "annualized_excess": round(ann, 6), "t_stat": round(float(t_stat), 4),
                    "perm_p": round(float(p_perm), 6), "psr": round(psr(0.0, rets), 4),
                    "dsr": round(dsr(0.0, rets, N_TRIALS), 4),
                    "direction": "long-biased" if sub[sub["pos"] != 0]["pos"].mean() > 0 else "short-biased",
                }
            per_window[str(year)] = w
            # matrix cells
            for rf in ["bull", "bear", "range"]:
                for th in ["T1", "T2", "T3"]:
                    if REGIME_OF_YEAR[year] != rf:
                        matrix.append({"market": sym, "regime": rf, "threshold": th, "window": str(year),
                                       "status": "regime_mismatch_flat", "t": 0.0, "p": 1.0, "trades": 0,
                                       "net_excess_sum": 0.0})
                        continue
                    df = strats[(th, rf)]
                    yr = (df["ts"] // 1000).apply(lambda x: dt.datetime.fromtimestamp(x, tz=timezone.utc).year)
                    sub = df[yr == year]
                    if len(sub) < 30:
                        matrix.append({"market": sym, "regime": rf, "threshold": th, "window": str(year),
                                       "status": "insufficient_data", "t": 0.0, "p": 1.0, "trades": 0,
                                       "net_excess_sum": 0.0})
                        continue
                    rets = sub["ret_excess"].values
                    t_stat, p_perm = perm_test(rets)
                    matrix.append({"market": sym, "regime": rf, "threshold": th, "window": str(year),
                                   "status": "tested", "t": round(float(t_stat), 4), "p": round(float(p_perm), 6),
                                   "trades": int(sub["trade"].sum()), "net_excess_sum": round(float(sub["ret_excess"].sum()), 6)})
        # direction consistency per threshold family across 5 windows
        dir_consistency = {}
        for th in ["T1", "T2", "T3"]:
            dirs = [per_window[str(y)][th].get("direction") for y in WINDOWS
                    if isinstance(per_window[str(y)][th], dict) and "direction" in per_window[str(y)][th]]
            if len(dirs) >= 3:
                from collections import Counter
                cnt = Counter(dirs)
                top, top_n = cnt.most_common(1)[0]
                dir_consistency[th] = {"consistent_windows": f"{top_n}/{len(dirs)}", "dominant": top,
                                       "pass": top_n >= max(3, int(0.75 * len(dirs)))}
            else:
                dir_consistency[th] = {"consistent_windows": f"{len(dirs)}/5", "dominant": None, "pass": False}
        # F1-F8 gates (main threshold T1, tested cells only)
        tested = [m for m in matrix if m["status"] == "tested"]
        pvals = np.array([m["p"] for m in tested])
        rej = bh_fdr(pvals.tolist())
        f1_fail = [m for i, m in enumerate(tested) if m["t"] < 2.0]
        f2_fail = [m for m in tested if m["trades"] < 30]
        f3_fail = [m for m in tested if m["net_excess_sum"] <= 0]
        gates = {
            "F1_t_ge_2": {"pass": len(f1_fail) == 0, "fail_cells": [f"{m['regime']}x{m['threshold']}x{m['window']}" for m in f1_fail]},
            "F2_trades_ge_30": {"pass": len(f2_fail) == 0, "fail_cells": [f"{m['regime']}x{m['threshold']}x{m['window']}(trades={m['trades']})" for m in f2_fail]},
            "F3_net_positive": {"pass": len(f3_fail) == 0, "fail_cells": [f"{m['regime']}x{m['threshold']}x{m['window']}(net={m['net_excess_sum']:.6f})" for m in f3_fail]},
            "F4_direction_consistency": {"pass": all(v["pass"] for v in dir_consistency.values()), "detail": dir_consistency},
            "F5_perm_p_lt_0001": {"pass": bool((pvals < 0.001).any()) if len(pvals) else False, "n_below": int((pvals < 0.001).sum()) if len(pvals) else 0},
            "F6_psr_gt_095": {"pass": any(w["T1"]["psr"] > 0.95 for w in per_window.values() if isinstance(w.get("T1"), dict)),
                              "detail": {str(y): w["T1"]["psr"] for y, w in per_window.items() if isinstance(w.get("T1"), dict)}},
            "F7_bh_fdr": {"pass": len(rej) > 0, "n_rejected": len(rej)},
            "F8_dsr_positive": {"pass": any(w["T1"]["dsr"] > 0 for w in per_window.values() if isinstance(w.get("T1"), dict)),
                                "detail": {str(y): w["T1"]["dsr"] for y, w in per_window.items() if isinstance(w.get("T1"), dict)}},
        }
        overall_pass = all(g["pass"] for g in gates.values())
        results["per_market"][sym] = {
            "data_range": {"klines_first": int(kl["openTime"].min()), "klines_last": int(kl["openTime"].max()),
                           "funding_rows": int(len(f)), "funding_first": int(f["ts_norm"].min()),
                           "funding_last": int(f["ts_norm"].max())},
            "per_window": per_window,
            "matrix_45": matrix,
            "gates": gates,
            "overall_pass": overall_pass,
        }
        pd.concat([strats[(th, None)].assign(market=sym, threshold=th) for th in ["T1", "T2", "T3"]],
                  ignore_index=True).to_parquet(os.path.join(R2, f"f6_trades_{sym}.parquet"), index=False)

    # cross-market verdict (prereg §3.4: any market fails -> report failure honestly)
    verdict = {
        "all_markets_pass": all(results["per_market"][s]["overall_pass"] for s in MARKETS),
        "per_market_pass": {s: results["per_market"][s]["overall_pass"] for s in MARKETS},
        "note": "S1 BTC already FAIL 8/8 (04r1); this is the cross-market generalization test under B1 degradation (ETH/SOL)",
    }
    results["verdict"] = verdict
    with open(os.path.join(R2, "f6_backtest_results.json"), "w") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(json.dumps(verdict, ensure_ascii=False))
    for s in MARKETS:
        g = results["per_market"][s]["gates"]
        print(s, {k: v["pass"] for k, v in g.items()})


if __name__ == "__main__":
    main()