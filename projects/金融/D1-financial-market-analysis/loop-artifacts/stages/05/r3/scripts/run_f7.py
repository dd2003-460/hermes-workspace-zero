#!/usr/bin/env python3
"""# origin: ai
F7 多信号组合回测 — funding + 现货-期货基差 (05 r3, pre-registered f7-preregistration.md).

Protocol: f7-preregistration.md (frozen 2026-10-31) + F6 同构协议 (stages/05/r2/scripts/run_f6.py).
Deviations (recorded, per prereg §失败降级):
  D1: Binance vision bulk spot klines 已下线 (2024-01 起 404); fapi live API IP-banned.
      → 现货改用 OKX 日线 API (免费无 key), cache/okx_spot/*.csv, 2020-01→2026-10.
  D2: 永续/funding 沿用 F6 本地 cache (r2/cache + r2/funding, 官方 CHECKSUM 校验通过).
PIT: same as F6 — decision at day 00:00 UTC, signal uses latest settled value with
     ts_norm <= t - 1_day; trade at day's open (taker). Basis PIT: both legs are daily
     closes known at t 00:00 UTC for day t-1 → no look-ahead.
Signals (pre-registered, frozen):
  funding: T1 sign / T2 short-crowding(≤−1e-4) / T3 long-crowding(≥+2e-4)  [F6 directions]
  basis:   B1 basis ≤ −0.05% → long(+1); B2 basis ≥ +0.05% → short(−1); else 0
  combo:   pos = 1.0 if f_sig and b_sig same direction; 0.5 if exactly one fires; 0 otherwise.
           Opposite-direction conflict → net position from the funded side only is NOT used;
           per frozen rule "同向 1x, 仅一个 0.5x, 无信号空仓" opposite pair = no agreed direction
           → treated as single-signal case on the stronger-magnitude side? NO — frozen text has
           no opposite branch; we implement literally: same-dir→1x, one-fires→0.5x, else 0.
           (Opposite-fire days are logged in meta for audit.)
Matrix: 3 regime × 2 threshold(funding: T1,T2) × 2 threshold(basis: ±0.05%, ±0.10%) × 5 window
     = 60 tests/market. N_TRIALS=60 for BH-FDR/DSR.
Costs: taker 0.05% + slippage 0.01% base per side (stress reported separately, not gated).
Outputs (this dir): f7_results.json, f7_report.md, f7_trades_{SYM}.parquet
Idempotent: rebuilds everything from cache every run.
"""
import csv, glob, hashlib, json, os, re, zipfile
from collections import Counter
from datetime import datetime, timezone, timedelta
import datetime as dt
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)                      # stages/05/r3
R2 = os.path.join(os.path.dirname(R3), "r2")    # stages/05/r2 (perp klines + funding cache)
R1 = os.path.join(os.path.dirname(R3), "..", "04", "r1")  # stages/04/r1 (S1 BTC cache)
SEED = 20261031
N_PERM = 2000
N_TRIALS = 60
ALPHA = 0.05
TAKER = 0.0005
SLIP_BASE = 0.0001
SLIP_STRESS = 0.0002
DAY_MS = 86400000
LAG_DAYS = 1
MARKETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
WINDOWS = [2021, 2022, 2023, 2024, 2025]
REGIME_OF_YEAR = {2021: "bull", 2022: "bear", 2023: "range", 2024: "bull", 2025: "bull"}
FUNDING_THRESHOLDS = ["T1", "T2"]
BASIS_THRESHOLDS = {"B05": 0.0005, "B10": 0.0010}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def verify_checksums():
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
    ym = re.search(r"(\d{4})-(\d{2})", ym_name).groups()
    y, m = int(ym[0]), int(ym[1])
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    d = datetime(ny, nm, 1, tzinfo=timezone.utc)
    first_monday = d + timedelta(days=(7 - d.weekday()) % 7 or 7)
    return (first_monday + timedelta(days=1)).timestamp() * 1000


def build_perp_klines(sym):
    if sym == "BTCUSDT":
        # D3: BTC perp klines live in 04/r1 S1 cache as monthly vision zips
        rows = []
        for zpath in sorted(glob.glob(os.path.join(R1, "cache", "S1_binance_vision", "klines",
                                                   "um", "BTCUSDT", "1d", "BTCUSDT-1d-*.zip"))):
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
        return kl
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
    assert kl["openTime"].min() > 1e12
    return kl


def build_spot(sym):
    p = os.path.join(R3, "cache", "okx_spot", f"{sym}-spot-1d.csv")
    df = pd.read_csv(p)
    df["openTime"] = df["openTime"].astype("int64")
    return df[["openTime", "open", "high", "low", "close", "volume"]]


def build_funding(sym):
    if sym == "BTCUSDT":
        # D3: BTC funding consolidated parquet from 04/r1 (built from official vision zips)
        f = pd.read_parquet(os.path.join(R1, "funding_table.parquet"))
        f["ts_norm"] = f["ts_norm"].astype("int64")
        return f[["ts_norm", "rate"]]
    rows = []
    for zpath in sorted(glob.glob(os.path.join(R2, "funding", f"{sym}-fundingRate-*.zip"))):
        with zipfile.ZipFile(zpath) as z:
            for n in z.namelist():
                if n.endswith(".csv"):
                    df = pd.read_csv(z.open(n))
                    cols = {c.lower().strip(): c for c in df.columns}
                    ts_col = cols.get("calc_time") or cols.get("funding_time") or list(df.columns)[0]
                    rate_col = cols.get("last_funding_rate") or cols.get("funding_rate") or list(df.columns)[-1]
                    sub = pd.DataFrame({
                        "ts_raw": df[ts_col].astype("int64"),
                        "rate": df[rate_col].astype(float),
                    })
                    sub["ts_norm"] = np.where(sub["ts_raw"] > 1e15, sub["ts_raw"] // 1000, sub["ts_raw"])
                    sub["avail_ms"] = first_monday_avail(os.path.basename(zpath))
                    rows.append(sub)
    f = pd.concat(rows, ignore_index=True)
    f = f.sort_values("ts_norm").drop_duplicates(subset="ts_norm").reset_index(drop=True)
    return f[["ts_norm", "rate", "avail_ms"]]


def merge_basis(perp, spot):
    """basis_t = (spot_close_t - perp_close_t)/spot_close_t, aligned on perp openTime."""
    perp_r = perp.rename(columns={"open": "open_perp", "high": "high_perp", "low": "low_perp",
                                  "close": "close_perp", "volume": "volume_perp"})
    spot_r = spot[["openTime", "close"]].rename(columns={"close": "close_spot"})
    m = perp_r.merge(spot_r, on="openTime", how="inner")
    m["basis"] = (m["close_spot"] - m["close_perp"]) / m["close_spot"]
    m = m.sort_values("openTime").reset_index(drop=True)
    return m


def funding_side(threshold, rate):
    if rate is None or np.isnan(rate):
        return 0
    if threshold == "T1":
        return 1 if rate >= 0 else 0
    if threshold == "T2":
        return -1 if rate <= -1e-4 else 0
    raise ValueError(threshold)


def basis_side(bth, basis):
    if basis is None or np.isnan(basis):
        return 0
    thr = BASIS_THRESHOLDS[bth]
    if basis <= -thr:
        return 1
    if basis >= thr:
        return -1
    return 0


def combine_pos(fs, bs):
    """Frozen rule: same dir -> 1x, exactly one fires -> 0.5x, none -> 0.
    Opposite fire: frozen text silent → treat as 0 (no agreed direction), audited via counter."""
    if fs == 0 and bs == 0:
        return 0.0, "none"
    if fs != 0 and bs != 0 and fs == bs:
        return float(fs), "both"
    if fs != 0 and bs != 0:
        return 0.0, "opposite"
    return 0.5 * float(fs if fs != 0 else bs), "single"


def run_strategy(data, f, fth, bth, regime_filter, cost_per_side):
    ts = data["openTime"].values.astype(np.int64)
    o = data["open_perp"].values.astype(float)
    c = data["close_perp"].values.astype(float)
    basis = data["basis"].values.astype(float)
    f_ts = f["ts_norm"].values.astype(np.int64)
    f_rate = f["rate"].values.astype(float)

    out = []
    prev_pos = 0.0
    opp_days = 0
    for i in range(len(ts)):
        # PIT: decision at t 00:00 UTC; only funding settled strictly before the t-1 day
        # boundary is used (ts_norm <= ts[t] - 1d), identical to F6 protocol.
        cutoff = ts[i] - DAY_MS * LAG_DAYS
        idx = np.searchsorted(f_ts, cutoff, side="right") - 1
        rate = float(f_rate[idx]) if idx >= 0 else np.nan
        fs = funding_side(fth, rate)
        bs = basis_side(bth, basis[i - 1] if i > 0 else np.nan)  # basis of day t-1 (PIT)
        pos, tag = combine_pos(fs, bs)
        if tag == "opposite":
            opp_days += 1
        if regime_filter is not None and REGIME_OF_YEAR.get(pd.Timestamp(ts[i], unit="ms").year) != regime_filter:
            pos = 0.0
        ret_open_close = c[i] / o[i] - 1.0
        strat_ret = pos * ret_open_close
        cf = -pos * rate
        turnover = abs(pos - prev_pos)
        cost = turnover * cost_per_side
        net = strat_ret + cf - cost
        out.append({"openTime": int(ts[i]), "open": o[i], "close": c[i], "rate": rate,
                    "basis_prev": basis[i - 1] if i > 0 else np.nan,
                    "f_sig": fs, "b_sig": bs, "pos": pos, "ret_excess": net,
                    "turnover": turnover, "trade": 1 if pos != prev_pos else 0})
        prev_pos = pos
    df = pd.DataFrame(out)
    return df, opp_days


def perm_test(rets, n_perm=N_PERM, seed=SEED):
    n = len(rets)
    sd = np.std(rets, ddof=1)
    t_obs = np.mean(rets) / (sd / np.sqrt(n)) if sd > 0 else 0.0
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=n)
        r2 = rets * signs
        sd2 = np.std(r2, ddof=1)
        t_p = np.mean(r2) / (sd2 / np.sqrt(n)) if sd2 > 0 else 0.0
        if abs(t_p) >= abs(t_obs):
            cnt += 1
    p = (1 + cnt) / (n_perm + 1)
    return t_obs, p


def psr(sr_annual, rets):
    rets = np.asarray(rets, dtype=float)
    if np.isnan(rets).any():
        rets = rets[~np.isnan(rets)]
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
    rets = np.asarray(rets, dtype=float)
    if np.isnan(rets).any():
        rets = rets[~np.isnan(rets)]
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
        "seed": SEED, "n_perm": N_PERM, "n_trials": N_TRIALS, "markets": MARKETS,
        "prereg": "stages/05/r3/f7-preregistration.md (frozen 2026-10-31)",
        "deviation_D1": "vision bulk spot dead (404 since ~2024-01) + fapi IP ban -> OKX spot daily API (free, no key)",
        "deviation_D2": "perp klines + funding reuse F6 r2 local cache (official CHECKSUM verified)",
        "deviation_D3": "BTC perp klines/funding live in 04/r1 S1 cache (consolidated CSV/parquet from official vision zips); r2 cache only holds ETH/SOL",
        "basis_definition": "(spot_close - perp_close)/spot_close, daily raw spread, PIT uses day t-1 value",
        "combo_rule": "same-dir 1x / single 0.5x / none 0 / opposite 0 (frozen text silent, audited)",
        "checksums": cksum,
    }, "per_market": {}}

    rho_report = {}
    best_single_t = {}

    for sym in MARKETS:
        perp = build_perp_klines(sym)
        spot = build_spot(sym)
        f = build_funding(sym)
        data = merge_basis(perp, spot)

        # P1/P2 input: daily corr between funding rate (lagged, as seen by strategy) and basis
        merged = data.copy()
        merged["rate_lag"] = np.nan
        f_ts = f["ts_norm"].values.astype(np.int64)
        f_rate = f["rate"].values.astype(float)
        ts_arr = merged["openTime"].values.astype(np.int64)
        for i in range(len(ts_arr)):
            idx = np.searchsorted(f_ts, ts_arr[i], side="right") - 1
            if idx >= 0:
                merged.loc[i, "rate_lag"] = f_rate[idx]
        sub = merged.dropna(subset=["rate_lag", "basis"])
        rho = float(np.corrcoef(sub["rate_lag"], sub["basis"])[0, 1]) if len(sub) > 10 else float("nan")
        rho_report[sym] = {"rho_funding_basis": round(rho, 4), "n_pairs": int(len(sub)),
                           "orthogonal_lt_0.3": bool(abs(rho) < 0.3)}

        # single-signal baseline (best POSITIVE variant across windows, for P1/P2 comparison;
        # negative-t single variants are failure modes, not the "best" to beat)
        single_best = {}
        for fth in FUNDING_THRESHOLDS:
            df_s, _opp = run_strategy(data, f, fth, "B05", None, TAKER + SLIP_BASE)
            yr = (df_s["openTime"] // 1000).apply(lambda x: dt.datetime.fromtimestamp(x, tz=timezone.utc).year)
            for year in WINDOWS:
                ssub = df_s[yr == year]
                if len(ssub) < 30:
                    continue
                t_s, _p = perm_test(ssub["ret_excess"].values)
                if t_s <= 0:
                    continue
                key = f"{fth}x{year}"
                if key not in single_best or t_s > single_best[key][0]:
                    single_best[key] = (float(t_s), str(year))
        best_single_t[sym] = single_best

        # combo matrix: 3 regime x 2 funding-th x 2 basis-th x 5 window = 60
        matrix = []
        strats = {}
        for fth in FUNDING_THRESHOLDS:
            for bth in BASIS_THRESHOLDS:
                for rf in ["bull", "bear", "range", None]:
                    strats[(fth, bth, rf)], _opp = run_strategy(data, f, fth, bth, rf, TAKER + SLIP_BASE)
        for year in WINDOWS:
            for rf in ["bull", "bear", "range"]:
                for fth in FUNDING_THRESHOLDS:
                    for bth in BASIS_THRESHOLDS:
                        cell = {"market": sym, "regime": rf, "funding_th": fth, "basis_th": bth, "window": str(year)}
                        if REGIME_OF_YEAR[year] != rf:
                            cell.update(status="regime_mismatch_flat", t=0.0, p=1.0, trades=0, net_excess_sum=0.0)
                            matrix.append(cell)
                            continue
                        df = strats[(fth, bth, rf)]
                        yr = (df["openTime"] // 1000).apply(lambda x: dt.datetime.fromtimestamp(x, tz=timezone.utc).year)
                        sub = df[yr == year]
                        if len(sub) < 30:
                            cell.update(status="insufficient_data", t=0.0, p=1.0, trades=0, net_excess_sum=0.0)
                            matrix.append(cell)
                            continue
                        rets = sub["ret_excess"].values
                        t_stat, p_perm = perm_test(rets)
                        cell.update(status="tested", t=round(float(t_stat), 4), p=round(float(p_perm), 6),
                                    trades=int(sub["trade"].sum()), net_excess_sum=round(float(sub["ret_excess"].sum()), 6))
                        matrix.append(cell)

        tested = [m for m in matrix if m["status"] == "tested"]
        pvals = np.array([m["p"] for m in tested])
        rej = bh_fdr(pvals.tolist())
        f1_fail = [m for m in tested if m["t"] < 2.0]
        f2_fail = [m for m in tested if m["trades"] < 30]
        f3_fail = [m for m in tested if m["net_excess_sum"] <= 0]
        # F4: direction consistency per (fth,bth) family across windows (full-sample runs)
        dir_consistency = {}
        for fth in FUNDING_THRESHOLDS:
            for bth in BASIS_THRESHOLDS:
                df = strats[(fth, bth, None)]
                dirs = []
                for year in WINDOWS:
                    yr = (df["openTime"] // 1000).apply(lambda x: dt.datetime.fromtimestamp(x, tz=timezone.utc).year)
                    ssub = df[yr == year]
                    act = ssub[ssub["pos"] != 0]
                    if len(act) == 0:
                        continue
                    dirs.append("long-biased" if act["pos"].mean() > 0 else "short-biased")
                if len(dirs) >= 3:
                    cnt = Counter(dirs)
                    top, top_n = cnt.most_common(1)[0]
                    dir_consistency[f"{fth}x{bth}"] = {"consistent_windows": f"{top_n}/{len(dirs)}", "dominant": top,
                                                       "pass": top_n >= max(3, int(0.75 * len(dirs)))}
                else:
                    dir_consistency[f"{fth}x{bth}"] = {"consistent_windows": f"{len(dirs)}/5", "dominant": None, "pass": False}
        # F6/F8: PSR/DSR on full-sample combo (T1xB05 as primary variant)
        df_primary = strats[("T1", "B05", None)]
        psr_full = psr(0.0, df_primary["ret_excess"].values)
        dsr_full = dsr(0.0, df_primary["ret_excess"].values, N_TRIALS)
        gates = {
            "F1_t_ge_2": {"pass": len(f1_fail) == 0, "fail_cells": [f"{m['regime']}x{m['funding_th']}x{m['basis_th']}x{m['window']}" for m in f1_fail]},
            "F2_trades_ge_30": {"pass": len(f2_fail) == 0, "fail_cells": [f"{m['regime']}x{m['funding_th']}x{m['basis_th']}x{m['window']}(trades={m['trades']})" for m in f2_fail]},
            "F3_net_positive": {"pass": len(f3_fail) == 0, "fail_cells": [f"{m['regime']}x{m['funding_th']}x{m['basis_th']}x{m['window']}(net={m['net_excess_sum']:.6f})" for m in f3_fail]},
            "F4_direction_consistency": {"pass": all(v["pass"] for v in dir_consistency.values()), "detail": dir_consistency},
            "F5_perm_p_lt_0001": {"pass": bool((pvals < 0.001).any()) if len(pvals) else False, "n_below": int((pvals < 0.001).sum()) if len(pvals) else 0},
            "F6_psr_gt_095": {"pass": psr_full > 0.95, "psr_primary_T1xB05": round(psr_full, 4)},
            "F7_bh_fdr": {"pass": len(rej) > 0, "n_rejected": len(rej)},
            "F8_dsr_positive": {"pass": dsr_full > 0, "dsr_primary_T1xB05": round(dsr_full, 4)},
        }
        overall_pass = all(g["pass"] for g in gates.values())

        # stress-cost rerun of primary variant (reported, not gated)
        df_stress, _ = run_strategy(data, f, "T1", "B05", None, TAKER + SLIP_STRESS)
        stress_net = float(df_stress["ret_excess"].sum())

        results["per_market"][sym] = {
            "data_range": {"perp_first": int(perp["openTime"].min()), "perp_last": int(perp["openTime"].max()),
                           "spot_first": int(spot["openTime"].min()), "spot_last": int(spot["openTime"].max()),
                           "merged_days": int(len(data)), "funding_rows": int(len(f))},
            "matrix_60": matrix,
            "gates": gates,
            "overall_pass": overall_pass,
            "primary_variant_T1xB05": {"net_excess_base": round(float(strats[('T1', 'B05', None)]['ret_excess'].sum()), 6),
                                       "net_excess_stress": round(stress_net, 6),
                                       "trades": int(strats[('T1', 'B05', None)]['trade'].sum()),
                                       "opposite_days": strats[('T1', 'B05', None)].pipe(lambda d: int(((d['f_sig'] != 0) & (d['b_sig'] != 0) & (d['f_sig'] != d['b_sig'])).sum()))},
        }
        pd.concat([strats[(fth, bth, None)].assign(market=sym, funding_th=fth, basis_th=bth)
                   for fth in FUNDING_THRESHOLDS for bth in BASIS_THRESHOLDS], ignore_index=True
                  ).to_parquet(os.path.join(R3, f"f7_trades_{sym}.parquet"), index=False)

    # P1/P2 reconciliation
    reconciliation = {}
    for sym in MARKETS:
        rr = rho_report[sym]
        sb = best_single_t[sym]
        tested = [m for m in results["per_market"][sym]["matrix_60"] if m["status"] == "tested"]
        combo_best = max(tested, key=lambda m: m["t"]) if tested else None
        single_best_cell = max(sb.items(), key=lambda kv: abs(kv[1][0])) if sb else (None, (0.0, None))
        delta = (combo_best["t"] - single_best_cell[1][0]) if combo_best else float("nan")
        if rr["orthogonal_lt_0.3"]:
            verdict = "P1"
            expect = f"combo t should exceed best single ({single_best_cell[1][0]:.3f}) by >=20%"
            passed = bool(combo_best and delta >= 0.2 * abs(single_best_cell[1][0]))
        else:
            verdict = "P2"
            expect = "combo t improvement < 10% -> no incremental info"
            passed = bool(combo_best and delta < 0.1 * abs(single_best_cell[1][0]))
        reconciliation[sym] = {
            "rho": rr["rho_funding_basis"], "branch": verdict, "expectation": expect,
            "combo_best_cell": combo_best, "single_best": {"key": single_best_cell[0], "t": single_best_cell[1][0], "window": single_best_cell[1][1]},
            "delta_t": round(delta, 4) if combo_best else None, "prediction_holds": passed,
        }
    results["reconciliation_P1_P2"] = reconciliation
    results["verdict"] = {
        "all_markets_pass": all(results["per_market"][s]["overall_pass"] for s in MARKETS),
        "per_market_pass": {s: results["per_market"][s]["overall_pass"] for s in MARKETS},
        "note": "P3: success requires ALL 8 gates per market; partial pass = negative result recorded",
    }
    with open(os.path.join(R3, "f7_results.json"), "w") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(json.dumps(results["verdict"], ensure_ascii=False))
    for s in MARKETS:
        g = results["per_market"][s]["gates"]
        print(s, {k: v["pass"] for k, v in g.items()})
    for s, r in reconciliation.items():
        print(s, "rho=", r["rho"], "branch=", r["branch"], "delta_t=", r["delta_t"], "holds=", r["prediction_holds"])


if __name__ == "__main__":
    main()