#!/usr/bin/env python3
"""F10-R4 回测: R4-A 条件带宽预测 (degraded: 无 c_套利/拥挤度条件).

规则全部来自 f10-r4-preregistration.md (FROZEN v1), 本脚本不引入新参数。
输入: r6 cache (klines_1h zips, bybit_oi) + funding (BTC extracted / ETH,SOL r2 zips)
输出: data/r4a_results.json, data/trades_r4a.parquet
"""
import glob
import json
import os
import sys
import zipfile

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

R6_SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "r6", "scripts")
sys.path.insert(0, R6_SCRIPTS)
from run_f10_backtest import load_klines, load_funding, atr_series, sharpe_t  # noqa: E402


def load_klines_dedup(sym):
    """R6 loader + 跨月去重 (vision monthly zip 边界重叠导致 ts 重复)."""
    kl = load_klines(sym)
    before = len(kl)
    kl = kl[~kl["ts"].duplicated(keep="last")].reset_index(drop=True)
    if len(kl) != before:
        print(f"  [dedup] {sym}: {before} → {len(kl)} rows", flush=True)
    return kl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # stages/05/r7
DATA = os.path.join(BASE, "data")

# ---- FROZEN params (f10-r4-preregistration.md) ----
COST_ROUNDTRIP = 0.0014      # 往返 0.14%
T_THRESHOLD = 1.5            # 温度 z-score 触发阈值
ROLL_H = 720                 # 30d 滚动窗口 (小时)
HOLD_H = 4                   # 持有 4h
SIGMA_K = 2.0                # 事件阈值 2σ_base
MOM_MIN = 0.001              # |mom24| < 0.1% → 不交易
Y_SQRTQ = 1.0                # √Q 律常数
WF_TRAIN_M = 6               # walk-forward 训练 6m
WF_TEST_M = 3                # 测试 3m
ATR_PERIOD = 14


def build_features(kl, funding):
    """PIT 特征: 全部只用 t 及之前数据 (z-score 窗口含 t 前一根已收盘 bar, 不含 t 自身)。"""
    kl = kl.copy()
    ret1 = kl["close"].pct_change()
    vol = ret1.abs()
    sigma_base = ret1.rolling(ROLL_H).std().shift(1)          # PIT: 截至 t-1
    atr_z = ((atr_series(kl, ATR_PERIOD) - atr_series(kl, ATR_PERIOD).rolling(ROLL_H).mean())
             / atr_series(kl, ATR_PERIOD).rolling(ROLL_H).std()).shift(1)
    vol_z = ((vol - vol.rolling(ROLL_H).mean()) / vol.rolling(ROLL_H).std()).shift(1)
    if funding is not None:
        fr_h = funding["fr"].reindex(kl["ts"], method="ffill")
        fund_z = ((fr_h - fr_h.rolling(ROLL_H).mean()) / fr_h.rolling(ROLL_H).std()).shift(1)
        absfund_z = ((fr_h.abs() - fr_h.abs().rolling(ROLL_H).mean())
                     / fr_h.abs().rolling(ROLL_H).std()).shift(1)
    else:
        fr_h = pd.Series(np.nan, index=kl.index)
        fund_z = absfund_z = pd.Series(np.nan, index=kl.index)
    T = pd.concat([atr_z, fund_z, vol_z], axis=1).max(axis=1)   # NaN 自动忽略
    mom24 = kl["close"].pct_change(24)
    qv = kl["volume"] * kl["close"]                             # quote volume 代理 (base*px)
    qv_med = qv.rolling(ROLL_H).median().shift(1)
    q_over_v = (qv.shift(1) / qv_med).clip(lower=0.0)           # PIT: 用 t-1 bar 的量比
    out = pd.DataFrame({
        "ts": kl["ts"], "open": kl["open"], "high": kl["high"], "low": kl["low"],
        "close": kl["close"],
        "T_atr_z": atr_z, "T_fund_z": fund_z, "T_vol_z": vol_z, "T": T,
        "sigma_base": sigma_base, "mom24": mom24, "absfund_z": absfund_z,
        "q_over_v": q_over_v,
    })
    # funding 缺失的 symbol: 相关特征以 0 填充 (= 该信号源缺席, z-score 中性), 不整行丢弃
    out[["T_fund_z", "absfund_z"]] = out[["T_fund_z", "absfund_z"]].fillna(0.0)
    return out


def event_label(df):
    """E_t = max(|ret_{t+1..t+4}|) > 2*sigma_base[t]; 未来收益只用于标签, 不进特征。"""
    fwd_max = pd.concat([(df["close"].shift(-j) / df["close"] - 1).abs() for j in range(1, HOLD_H + 1)],
                        axis=1).max(axis=1)
    ev = fwd_max > SIGMA_K * df["sigma_base"]
    ev.iloc[-HOLD_H:] = False  # 尾部无完整窗口
    return ev.fillna(False), fwd_max


def binom_two_sided(wins, n):
    from math import lgamma
    def lbinom(n, k):
        return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    log_half = -n * 0.6931471805599453
    p_one = float(sum(2.718281828459045 ** (lbinom(n, k) + log_half) for k in range(wins, n + 1)))
    return float(min(1.0, 2 * p_one))


def run_r4a(sym, kl, funding):
    df = build_features(kl, funding)
    ev, fwd_max = event_label(df)
    feats = ["T_atr_z", "T_fund_z", "T_vol_z", "mom24", "absfund_z"]
    X_all = df[feats].replace([np.inf, -np.inf], np.nan)

    # ---- walk-forward logistic, 6m train / 3m test rolling ----
    rows = []
    cur = df["ts"].min().normalize()
    full_end = df["ts"].max()
    while cur < full_end:
        w_end = cur + pd.Timedelta(days=WF_TRAIN_M * 30)
        t_end = min(w_end + pd.Timedelta(days=WF_TEST_M * 30), full_end + pd.Timedelta(days=1))
        tr = df[(df["ts"] >= cur) & (df["ts"] < w_end)]
        te = df[(df["ts"] >= w_end) & (df["ts"] < t_end)]
        trX = X_all.loc[tr.index].dropna()
        tr_y = ev.loc[trX.index]
        if len(trX) >= 200 and tr_y.sum() >= 10:
            model = LogisticRegression(max_iter=2000)
            model.fit(trX.values, tr_y.values.astype(float))
            if len(te):
                teX = X_all.loc[te.index].fillna(0.0)
                p_hat = model.predict_proba(teX.values)[:, 1]
                base_p = float(tr_y.mean())  # 无条件基准 = 训练窗频率
                for idx, p in zip(te.index, p_hat):
                    rows.append({"ts": df["ts"].iloc[idx], "sym": sym, "p_hat": p,
                                 "base_p": base_p, "ev": bool(ev.iloc[idx]),
                                 "T": df["T"].iloc[idx], "mom24": df["mom24"].iloc[idx],
                                 "sigma_base": df["sigma_base"].iloc[idx],
                                 "q_over_v": df["q_over_v"].iloc[idx],
                                 "open": df["open"].iloc[idx],
                                 "high": df["high"].iloc[idx], "low": df["low"].iloc[idx],
                                 "close": df["close"].iloc[idx],
                                 "fwd_max": fwd_max.iloc[idx]})
        cur = w_end
    oos = pd.DataFrame(rows)
    # 预热期: 首个完整训练窗结束前的 bar 没有 OOS 预测 (特征窗口未填满), 如实记录
    warmup_end = df["ts"].min() + pd.Timedelta(days=WF_TRAIN_M * 30)
    if oos.empty:
        return {"symbol": sym, "rule": "R4-A-degraded", "status": "NO_OOS_DATA"}, None

    # ---- 主判据: Brier 对比 (校准) ----
    brier_cond = float(((oos["p_hat"] - oos["ev"]) ** 2).mean())
    brier_uncond = float(((oos["base_p"] - oos["ev"]) ** 2).mean())
    res = {
        "symbol": sym, "rule": "R4-A-degraded",
        "n_oos_bars": len(oos),
        "oos_start": str(oos["ts"].min()), "oos_end": str(oos["ts"].max()),
        "brier_conditional": brier_cond, "brier_unconditional": brier_uncond,
        "calibration_pass": bool(brier_cond < brier_uncond),
        "event_rate_oos": float(oos["ev"].mean()),
        "mean_p_hat": float(oos["p_hat"].mean()),
    }

    # ---- 次判据: 方向正确率 (触发且 |mom24|≥MOM_MIN 的交易) ----
    trig = oos[(oos["T"] >= T_THRESHOLD) & (oos["mom24"].abs() >= MOM_MIN)].copy().reset_index(drop=True)
    dfi = {ts: i for i, ts in enumerate(df["ts"])}  # ts → 原始 bar 位置 (df 已去重, 唯一)
    trades = []
    busy_until = None
    for _, r in trig.iterrows():
        if busy_until is not None and r["ts"] < busy_until:
            continue
        pos = dfi.get(r["ts"])
        if pos is None:
            continue
        direction = int(np.sign(r["mom24"]))
        entry_px = r["open"]
        sb = r["sigma_base"]
        if not np.isfinite(sb) or sb <= 0 or entry_px <= 0:
            continue
        stop_dist = Y_SQRTQ * sb * np.sqrt(r["q_over_v"])
        # 下限保护 (冻结): 止损距离不得小于成本往返的 2 倍, 否则止损出场必亏成本、信号无意义;
        # 这是执行层可行性约束, 不改 √Q 律本身 (常态 q/v≈1 时 stop≈σ≈3-4×cost, 不触发下限)
        stop_dist = max(stop_dist, 2.0 * COST_ROUNDTRIP)
        stop = entry_px - direction * stop_dist
        exit_pos = min(pos + HOLD_H, len(df) - 1)
        hit_stop, gross = False, None
        for j in range(pos + 1, exit_pos + 1):
            adverse = df["low"].iloc[j] if direction == 1 else df["high"].iloc[j]
            if adverse <= stop:
                hit_stop = True
                break
        if hit_stop:
            gross = (stop / entry_px - 1) * direction
            exit_ts = df["ts"].iloc[j]
        else:
            gross = (df["close"].iloc[exit_pos] / entry_px - 1) * direction
            exit_ts = df["ts"].iloc[exit_pos]
        net = gross - COST_ROUNDTRIP
        correct = (gross > 0)
        trades.append({"ts": r["ts"], "direction": direction, "entry": entry_px,
                       "gross": gross, "net": net, "stopped": hit_stop,
                       "correct": correct, "exit_ts": exit_ts,
                       "p_hat": r["p_hat"], "T": r["T"], "mom24": r["mom24"],
                       "ev_realized": bool(r["ev"]), "symbol": sym})
        busy_until = exit_ts + pd.Timedelta(hours=1)

    tdf = pd.DataFrame(trades)
    res["n_triggers"] = len(trig)
    res["n_trades"] = len(tdf)
    if len(tdf) >= 8:
        sh, tstat, n = sharpe_t(tdf["net"])
        res.update(sharpe=sh, t_stat=tstat, n=n, win_rate=float((tdf["net"] > 0).mean()))
        wins = int(tdf["correct"].sum())
        res["dir_correct_rate"] = wins / len(tdf)
        if len(tdf) >= 30:
            res["binom_p"] = binom_two_sided(wins, len(tdf))
            res["direction_pass"] = bool(res["dir_correct_rate"] > 0.55 and res["binom_p"] < 0.05)
        else:
            res["binom_p"] = None
            res["direction_pass"] = None  # insufficient
        res["avg_net_pct"] = float(tdf["net"].mean() * 100)
        res["total_net_pct"] = float(tdf["net"].sum() * 100)
        res["stop_rate"] = float(tdf["stopped"].mean())
        # 事件命中率: 触发时实际出现 >2σ 的比例 (对照全样本基线)
        res["trigger_event_hit"] = float(tdf["ev_realized"].mean())
        res["baseline_event_rate"] = float(oos["ev"].mean())
    dp = res.get("direction_pass")
    res["PASS"] = bool(res["calibration_pass"] and (dp is True))
    return res, tdf


def main():
    symbols = sys.argv[1].split(",") if len(sys.argv[1:]) else ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    results, all_trades = {}, []
    for sym in symbols:
        print(f"== {sym} ==", flush=True)
        kl = load_klines_dedup(sym)
        funding = load_funding(sym)
        try:
            res, tdf = run_r4a(sym, kl, funding)
            results[sym] = res
            if tdf is not None and len(tdf):
                all_trades.append(tdf)
            print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
                              for k, v in res.items()}, default=str), flush=True)
        except Exception as e:
            results[sym] = {"symbol": sym, "rule": "R4-A-degraded", "error": repr(e)}
            print(f"  ERROR: {e!r}", flush=True)
    with open(os.path.join(DATA, "r4a_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    if all_trades:
        pd.concat(all_trades, ignore_index=True).to_parquet(os.path.join(DATA, "trades_r4a.parquet"))
    print("results written to", DATA)


if __name__ == "__main__":
    main()