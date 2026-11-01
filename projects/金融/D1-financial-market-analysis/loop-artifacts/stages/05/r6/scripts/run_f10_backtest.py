#!/usr/bin/env python3
"""F10 回测: R1 (DVOL regime shift) + R2 (funding+OI cascade).

输入:
  data/manifest.json, cache/klines_1h/*.zip, cache/bybit_oi/*_oi_1d.csv
  ../r4/data/dvol_daily.json                      (R1 DVOL)
  ../../04/r1/cache/S1_binance_vision/funding/um/extracted/BTCUSDT-fundingRate-*.csv 等
输出:
  data/r1_results.json, data/r2_results.json, data/trades_r1.parquet, data/trades_r2.parquet
  f10_report.md (由 run_f10_backtest.py --report 生成骨架)

规则全部来自预注册文件 (f10-r1-preregistration.md / f10-r2-preregistration.md), 本脚本不引入新参数。
"""
import glob
import io
import json
import os
import sys
import zipfile
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # stages/05/r6
CACHE_KL = os.path.join(BASE, "cache", "klines_1h")
CACHE_OI = os.path.join(BASE, "cache", "bybit_oi")
DATA = os.path.join(BASE, "data")
DVOL_PATH = os.path.join(BASE, "..", "r4", "data", "dvol_daily.json")
FUNDING_ROOT = os.path.join(BASE, "..", "..", "04", "r1", "cache", "S1_binance_vision", "funding", "um")

COST_ROUNDTRIP = 0.0014  # 往返 0.14% (预注册冻结)
ATR_PERIOD = 14
ATR_STOP_MULT = 2.0


def load_klines(sym, start=date(2022, 1, 1), end=date(2025, 12, 31)):
    rows = []
    ym = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        ym.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    for s in ym:
        path = os.path.join(CACHE_KL, f"{sym}-1h-{s}.zip")
        if not os.path.exists(path):
            continue
        with zipfile.ZipFile(path) as zf:
            name = [n for n in zf.namelist() if n.endswith(".csv")][0]
            df = pd.read_csv(zf.open(name))
        rows.append(df)
    if not rows:
        raise RuntimeError(f"no klines for {sym}")
    out = pd.concat(rows, ignore_index=True)
    out["ts"] = pd.to_datetime(out["open_time"], unit="ms").dt.tz_localize(None)  # ms epoch 已是 UTC
    out = out.sort_values("ts").reset_index(drop=True)
    out = out[~out["ts"].duplicated()]
    return out[["ts", "open", "high", "low", "close", "volume"]].assign(
        open=out["open"].astype(float), high=out["high"].astype(float),
        low=out["low"].astype(float), close=out["close"].astype(float),
        volume=out["volume"].astype(float))


def load_dvol():
    d = json.load(open(DVOL_PATH))
    ts = [datetime.fromtimestamp(r[0] / 1000, tz=timezone.utc).replace(tzinfo=None) for r in d]
    return pd.DataFrame({"ts": ts, "dvol": [float(r[1]) for r in d]}).set_index("ts").sort_index()


def load_funding(sym):
    """Binance vision monthly funding CSV → settled funding series.

    目录布局: extracted/ 只有 BTCUSDT; ETH/SOL 在 r2/funding 的 zip 里 (按需解压).
    列: calc_time(ms), funding_interval_hours, last_funding_rate — calc_time = 结算时刻.
    """
    rows = []
    files = sorted(glob.glob(os.path.join(FUNDING_ROOT, "extracted", f"{sym}-fundingRate-*.csv")))
    if not files:
        zips = sorted(glob.glob(os.path.join(BASE, "..", "r2", "funding", f"{sym}-fundingRate-*.zip")))
        for z in zips:
            try:
                with zipfile.ZipFile(z) as zf:
                    name = [n for n in zf.namelist() if n.endswith(".csv")][0]
                    df = pd.read_csv(zf.open(name))
                    rows.append(df)
            except Exception:
                continue
    else:
        for f in files:
            try:
                rows.append(pd.read_csv(f))
            except Exception:
                continue
    if not rows:
        return None
    out = pd.concat(rows, ignore_index=True)
    col_ts = next((c for c in out.columns if "time" in c.lower()), None)
    col_fr = next((c for c in out.columns if "rate" in c.lower()), None)
    if col_ts is None or col_fr is None:
        print(f"[funding] {sym}: cannot identify columns {list(out.columns)}", flush=True)
        return None
    out["ts"] = pd.to_datetime(out[col_ts], unit="ms").dt.tz_localize(None)
    out["fr"] = pd.to_numeric(out[col_fr], errors="coerce")
    out = out.dropna(subset=["ts", "fr"]).sort_values("ts")
    out = out[~out["ts"].duplicated(keep="last")]
    return out.set_index("ts")[["fr"]]


def load_oi_bybit(sym):
    p = os.path.join(CACHE_OI, f"{sym}_oi_1d.csv")
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    df["ts"] = pd.to_datetime(df["ts_ms"], unit="ms").dt.tz_localize(None)
    return df.set_index("ts")["open_interest"].sort_index()


def atr_series(kl, period=ATR_PERIOD):
    tr = pd.concat([
        kl["high"] - kl["low"],
        (kl["high"] - kl["close"].shift(1)).abs(),
        (kl["low"] - kl["close"].shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def sharpe_t(rets):
    rets = np.asarray(rets, dtype=float)
    rets = rets[np.isfinite(rets)]
    if len(rets) < 8:
        return np.nan, np.nan, len(rets)
    mu, sd = rets.mean(), rets.std(ddof=1)
    ann = np.sqrt(6 * 365)  # 1h bars ≈ 6 per day
    sh = mu / sd * ann if sd > 0 else np.nan
    tstat = mu / (sd / np.sqrt(len(rets))) if sd > 0 else np.nan
    return sh, tstat, len(rets)


# ---------------- R1 ----------------

def run_r1(sym, kl, dvol, wf_train_months=6, wf_test_months=3):
    kl = kl.reset_index()  # ts 变普通列, searchsorted 用 iloc 位置索引
    kl["ts"] = pd.to_datetime(kl["ts"].astype(str))  # 统一 datetime64[ns], 避免跨单位比较炸
    kl["atr"] = atr_series(kl)
    close = kl["close"]
    # 前 24h 动量 (截至触发日 00:00 的入场 bar 之前)
    mom24 = close.pct_change(24)

    dv = dvol["dvol"].copy()
    trig = {}  # entry_ts -> direction (+1 long / -1 short) ; only 超调 type
    dv_mean = dv.rolling(20).mean()
    dv_std = dv.rolling(20).std()
    z = (dv - dv_mean) / dv_std
    for ts_day, zv in z.items():
        if not np.isfinite(zv) or zv <= 1.5:
            continue
        entry_ts = pd.Timestamp(ts_day) + pd.Timedelta(days=1)  # PIT: 次日 00:00 UTC 开盘入场
        # 找入场 bar (entry_ts 那根 1h)
        idx = kl["ts"].searchsorted(entry_ts)
        if idx >= len(kl) or kl["ts"].iloc[idx] != entry_ts:
            continue
        m = mom24.iloc[idx]
        if not np.isfinite(m):
            continue
        if m > 0:
            trig[entry_ts] = -1   # 前涨 + IV 跳升 → 做空超调
        elif m < 0:
            trig[entry_ts] = +1   # 前跌 + IV 跳升 → 做多超调
        else:
            continue

    trades = []
    busy_until = None
    for i, row in kl.iterrows():
        ts = row["ts"]
        if ts not in trig:
            continue
        if busy_until is not None and ts < busy_until:
            continue
        direction = trig[ts]
        entry_px = row["open"]
        a = row["atr"]
        if not np.isfinite(a) or entry_px <= 0:
            continue
        stop = entry_px - direction * ATR_STOP_MULT * a
        exit_i = min(i + 4, len(kl) - 1)
        exit_ts = kl["ts"].iloc[exit_i]
        # 盘中止损检查 (i+1..i+4)
        hit_stop = False
        for j in range(i + 1, exit_i + 1):
            adverse = kl["low"].iloc[j] if direction == 1 else kl["high"].iloc[j]
            if adverse <= stop:
                hit_stop = True
                break
        if hit_stop:
            gross = (stop / entry_px - 1) * direction
        else:
            gross = (kl["close"].iloc[exit_i] / entry_px - 1) * direction
        net = gross - COST_ROUNDTRIP
        trades.append({
            "ts": ts, "direction": direction, "entry": entry_px,
            "gross": gross, "net": net, "stopped": hit_stop,
            "exit_ts": exit_ts, "mom24": mom24.iloc[i],
        })
        busy_until = exit_ts + pd.Timedelta(hours=1)

    tdf = pd.DataFrame(trades)
    result = {"symbol": sym, "rule": "R1", "n_triggers": len(trig), "n_trades": len(tdf)}
    if len(tdf) >= 8:
        sh, t, n = sharpe_t(tdf["net"])
        result.update(sharpe=sh, t_stat=t, n=n, win_rate=float((tdf["net"] > 0).mean()))
        # binomial test on direction correctness (gross sign vs predicted direction already baked into gross>0)
        from math import comb, lgamma
        wins = int((tdf["gross"] > 0).sum())
        nn = len(tdf)
        # two-sided exact binomial p
        p_one = sum(comb(nn, k) * 0.5 ** nn for k in range(wins, nn + 1))
        p_val = min(1.0, 2 * p_one)
        result["binom_p"] = float(p_val)
        # |ret| > 2σ event rate (验证偏离出现本身)
        sig = tdf["gross"].abs()
        base_sd = close.pct_change().std()
        result["pct_gt_2sigma"] = float((sig > 2 * base_sd).mean())
        result["avg_net_pct"] = float(tdf["net"].mean() * 100)
        result["total_net_pct"] = float(tdf["net"].sum() * 100)
    # walk-forward
    wf = []
    if len(tdf) >= 20:
        tdf = tdf.sort_values("ts")
        windows = []
        cur_start = tdf["ts"].min()
        full_end = tdf["ts"].max()
        while cur_start < full_end:
            w_end = cur_start + pd.Timedelta(days=wf_train_months * 30)
            t_end = w_end + pd.Timedelta(days=wf_test_months * 30)
            tr = tdf[(tdf["ts"] >= cur_start) & (tdf["ts"] < w_end)]
            te = tdf[(tdf["ts"] >= w_end) & (tdf["ts"] < t_end)]
            if len(te) >= 5:
                sh_tr, t_tr, _ = sharpe_t(tr["net"]) if len(tr) >= 5 else (np.nan, np.nan, 0)
                sh_te, t_te, n_te = sharpe_t(te["net"])
                windows.append({
                    "train_start": str(cur_start.date()), "test_start": str(w_end.date()),
                    "test_end": str(min(t_end, full_end).date()),
                    "n_train": len(tr), "n_test": int(n_te),
                    "sharpe_train": sh_tr, "t_train": t_tr,
                    "sharpe_test": sh_te, "t_test": t_te,
                    "win_test": float((te["net"] > 0).mean()),
                })
            cur_start = w_end
        wf = windows
        oos = tdf[tdf["ts"] >= tdf["ts"].min() + pd.Timedelta(days=wf_train_months * 30)]
        if len(oos) >= 8:
            sh_oos, t_oos, _ = sharpe_t(oos["net"])
            result["walk_forward_windows"] = wf
            result["oos_sharpe"] = sh_oos
            result["oos_t"] = t_oos
            result["PASS"] = bool(np.isfinite(sh_oos) and sh_oos > 1.0 and t_oos > 2.0
                                  and result.get("win_rate", 0) > 0.52)
    else:
        result["walk_forward_windows"] = []
        result["PASS"] = False
    return result, tdf


# ---------------- R2 ----------------

def run_r2(sym, kl, funding, oi, hold_hours=24, wf_train_months=6, wf_test_months=3):
    if funding is None:
        return {"symbol": sym, "rule": "R2", "status": "NO_FUNDING"}, None
    fr = funding["fr"].copy()
    # rolling 90d p95 (PIT: 用 t 日之前数据算阈值, shift(1) 避免含当日)
    thr_pos = fr.rolling(90).quantile(0.95).shift(1)
    thr_neg = fr.rolling(90).quantile(0.05).shift(1)
    extreme = (fr >= thr_pos) | (fr <= thr_neg)
    side = np.where(fr >= thr_pos, 1, -1)  # +1 多头拥挤

    oi_d = None
    drop_h = None
    if oi is not None:
        oi_d = oi.resample("1D").last().ffill()
        oi_drop = oi_d.pct_change(3) <= -0.05

    kl2 = kl.copy()
    kl2["atr"] = atr_series(kl2)
    close = kl2["close"]
    fr_h = fr.reindex(kl2["ts"], method="ffill")  # 已结算值, 无未来信息
    side_h = pd.Series(side, index=fr.index).reindex(kl2["ts"], method="ffill")
    ext_h = extreme.reindex(kl2["ts"], method="ffill")
    drop_h = (oi_drop.reindex(kl2["ts"].dt.normalize(), method="ffill") if oi_d is not None else None)

    triggers = []  # (entry_ts, direction, has_oi_cond)
    seen_days = set()
    for i, ts in enumerate(kl2["ts"]):
        if ts.hour != 9 or ts.minute != 0:  # 决策 08:00 后, 09:00 bar open 入场
            continue
        day = pd.Timestamp(ts).normalize()
        if day in seen_days:
            continue
        if not bool(ext_h.iloc[i]):
            continue
        s = side_h.iloc[i]
        if not np.isfinite(s) or s == 0:
            continue
        has_oi = False
        if drop_h is not None:
            d = drop_h.iloc[i]
            has_oi = bool(d) if np.isfinite(d) else False
        else:
            has_oi = None  # OI 不可得 → 对照组
        seen_days.add(day)
        direction = -int(s)  # 多头拥挤→做空; 空头拥挤→做多
        triggers.append({"entry_ts": ts, "direction": direction, "has_oi": has_oi, "idx": i})

    def backtest_subset(trigs, label):
        trades = []
        busy_until = None
        for t in trigs:
            ts = t["entry_ts"]
            if busy_until is not None and ts < busy_until:
                continue
            i = t["idx"]
            direction = t["direction"]
            entry_px = kl2["open"].iloc[i]
            a = kl2["atr"].iloc[i]
            if not np.isfinite(a) or entry_px <= 0:
                continue
            stop = entry_px - direction * ATR_STOP_MULT * a
            exit_i = min(i + hold_hours, len(kl2) - 1)
            hit_stop = False
            for j in range(i + 1, exit_i + 1):
                adverse = kl2["low"].iloc[j] if direction == 1 else kl2["high"].iloc[j]
                if adverse <= stop:
                    hit_stop = True
                    break
            gross = ((stop / entry_px - 1) if hit_stop else (kl2["close"].iloc[exit_i] / entry_px - 1)) * direction
            net = gross - COST_ROUNDTRIP
            trades.append({"ts": ts, "direction": direction, "gross": gross, "net": net,
                           "stopped": hit_stop, "label": label,
                           "exit_ts": kl2["ts"].iloc[exit_i]})
            busy_until = kl2["ts"].iloc[exit_i] + pd.Timedelta(hours=1)
        tdf = pd.DataFrame(trades)
        out = {"label": label, "n_trades": len(tdf)}
        if len(tdf) >= 8:
            sh, t, n = sharpe_t(tdf["net"])
            out.update(sharpe=sh, t_stat=t, n=n, win_rate=float((tdf["net"] > 0).mean()))
            from math import comb
            wins = int((tdf["gross"] > 0).sum())
            nn = len(tdf)
            p_one = sum(comb(nn, k) * 0.5 ** nn for k in range(wins, nn + 1))
            out["binom_p"] = float(min(1.0, 2 * p_one))
            out["avg_net_pct"] = float(tdf["net"].mean() * 100)
            out["total_net_pct"] = float(tdf["net"].sum() * 100)
        return out, tdf

    main_trigs = [t for t in triggers if t["has_oi"] is True]
    ctrl_trigs = [t for t in triggers if t["has_oi"] is None]
    result = {"symbol": sym, "rule": "R2", "hold_hours": hold_hours,
              "n_triggers_total": len(triggers),
              "n_with_oi": len(main_trigs), "n_no_oi_control": len(ctrl_trigs)}
    all_trades = []
    if main_trigs:
        r_main, td_main = backtest_subset(main_trigs, "funding+OI")
        result["main"] = r_main
        all_trades.append(td_main)
    if ctrl_trigs:
        r_ctrl, td_ctrl = backtest_subset(ctrl_trigs, "funding-alone-control")
        result["control"] = r_ctrl
        all_trades.append(td_ctrl)
    tdf_all = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    # PASS 判据: 主组 (有 OI) 或 若 OI 深度不足则对照组降级判定
    grp = result.get("main") if result.get("main") else result.get("control")
    if grp and "sharpe" in grp:
        result["PASS"] = bool(grp["sharpe"] > 1.0 and grp["t_stat"] > 2.0 and grp["win_rate"] > 0.52)
        result["pass_group"] = "main" if result.get("main") else "control(degraded)"
    else:
        result["PASS"] = False
    return result, tdf_all


def main():
    symbols = sys.argv[1].split(",") if len(sys.argv) > 1 else ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    dvol = load_dvol()
    r1_all, r2_all = {}, {}
    r1_trades, r2_trades = [], []
    for sym in symbols:
        print(f"== {sym} ==", flush=True)
        kl = load_klines(sym)
        print(f"  klines 1h: {len(kl)} rows {kl['ts'].min()} → {kl['ts'].max()}", flush=True)
        # R1
        try:
            res, tdf = run_r1(sym, kl, dvol)
            r1_all[sym] = res
            if tdf is not None and len(tdf):
                r1_trades.append(tdf.assign(symbol=sym))
            print(f"  R1: n_trig={res.get('n_triggers')} n_trades={res.get('n_trades')} "
                  f"sharpe={res.get('sharpe')} t={res.get('t_stat')} PASS={res.get('PASS')}", flush=True)
        except Exception as e:
            r1_all[sym] = {"symbol": sym, "rule": "R1", "error": repr(e)}
            print(f"  R1 ERROR: {e!r}", flush=True)
        # R2
        funding = load_funding(sym)
        oi = load_oi_bybit(sym)
        try:
            res, tdf = run_r2(sym, kl, funding, oi)
            r2_all[sym] = res
            if tdf is not None and len(tdf):
                r2_trades.append(tdf.assign(symbol=sym))
            print(f"  R2: {json.dumps({k: v for k, v in res.items() if k not in ('main','control')}, default=str)}", flush=True)
            for gname in ("main", "control"):
                if res.get(gname):
                    g = res[gname]
                    print(f"    [{gname}] n={g.get('n_trades')} sharpe={g.get('sharpe')} t={g.get('t_stat')} "
                          f"win={g.get('win_rate')}", flush=True)
        except Exception as e:
            r2_all[sym] = {"symbol": sym, "rule": "R2", "error": repr(e)}
            print(f"  R2 ERROR: {e!r}", flush=True)

    with open(os.path.join(DATA, "r1_results.json"), "w") as f:
        json.dump(r1_all, f, indent=2, default=str)
    with open(os.path.join(DATA, "r2_results.json"), "w") as f:
        json.dump(r2_all, f, indent=2, default=str)
    if r1_trades:
        pd.concat(r1_trades, ignore_index=True).to_parquet(os.path.join(DATA, "trades_r1.parquet"))
    if r2_trades:
        pd.concat(r2_trades, ignore_index=True).to_parquet(os.path.join(DATA, "trades_r2.parquet"))
    print("results written to", DATA)


if __name__ == "__main__":
    main()