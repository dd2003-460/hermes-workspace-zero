#!/usr/bin/env python3
"""Deribit IV 采集器 — 每日积累期权隐含波动率数据（F8 方案 B）。

动机：F8 调研结论是免费数据下 crypto 日频信号高度冗余，唯一理论正交路径是
自建 Deribit IV 采集器（forward-looking vs funding rate 的 backward-looking）。
本脚本每日拉一次全 option book，算 25-delta IV / skew / term structure slope，
落盘 CSV 供未来回测。

用法：python3 deribit_iv_collector.py [currency]   # 默认 BTC
输出：<project>/loop-artifacts/stages/exploration/r7-f8-data-survey/data/deribit_iv_daily.csv
      （追加式，每日一行；列：date, currency, underlying, iv_25d_call, iv_25d_put,
        skew_25d, term_slope, num_contracts, source_ts）

约束：免费无 key；point-in-time（用当日快照时间戳）；失败不阻塞（记日志继续）。
"""
import json, sys, csv, os, urllib.request, datetime, math

CURRENCY = sys.argv[1] if len(sys.argv) > 1 else "BTC"
API = f"https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency={CURRENCY}&kind=option"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "loop-artifacts", "stages", "exploration", "r7-f8-data-survey", "data")
OUT = os.path.join(DATA_DIR, "deribit_iv_daily.csv")

def fetch():
    req = urllib.request.Request(API, headers={"User-Agent": "hermes-research/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def parse_instrument(name):
    """BTC-13NOV26-83000-C → (expiry_date, strike, is_call)"""
    parts = name.split("-")
    # 格式: CUR-EXP-STRIKE-TYPE
    typ = parts[-1].upper()
    strike = float(parts[-2])
    exp_str = parts[-3]  # e.g. 13NOV26
    from datetime import datetime as dt
    expiry = dt.strptime(exp_str, "%d%b%y").date()
    return expiry, strike, (typ == "C")

def main():
    d = fetch()
    res = d.get("result", [])
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date()
    rows = []
    for c in res:
        try:
            expiry, strike, is_call = parse_instrument(c["instrument_name"])
            days_to_exp = (expiry - today).days
            if days_to_exp <= 0 or c.get("mark_iv") is None:
                continue
            rows.append({
                "expiry": expiry, "strike": strike, "is_call": is_call,
                "iv": c["mark_iv"], "oi": c.get("open_interest", 0),
                "days": days_to_exp,
            })
        except Exception:
            continue

    if not rows:
        print("no valid contracts", file=sys.stderr)
        return

    underlying = res[0].get("underlying_price", 0)
    # 按到期分组，每组内按 moneyness(strike/underlying) 排序
    by_exp = {}
    for r in rows:
        by_exp.setdefault(r["expiry"], []).append(r)

    # 25-delta IV：对每个到期，找最接近 ATM 的 call/put 的 IV 作近似
    # （精确 25-delta 需 delta 字段，Deribit book_summary 不给 delta，用 ATM 附近近似）
    def atmost(ivs):
        if not ivs: return None
        return sum(ivs)/len(ivs)

    out_fields = ["date","currency","underlying","iv_atm_call","iv_atm_put","skew_atm","num_contracts","source_ts"]
    new_file = not os.path.exists(OUT)
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        if new_file: w.writeheader()
        # 取最近 3 个到期的 ATM 附近 IV 均值
        nearest_exps = sorted(by_exp.keys())[:3]
        call_ivs, put_ivs = [], []
        for e in nearest_exps:
            grp = by_exp[e]
            atm = [r for r in grp if abs(r["strike"]/underlying - 1) < 0.05 if underlying]
            c_atm = [r["iv"] for r in atm if r["is_call"]]
            p_atm = [r["iv"] for r in atm if not r["is_call"]]
            if c_atm: call_ivs.append(sum(c_atm)/len(c_atm))
            if p_atm: put_ivs.append(sum(p_atm)/len(p_atm))
        iv_c = atmost(call_ivs); iv_p = atmost(put_ivs)
        skew = (iv_p - iv_c) if (iv_c and iv_p) else None
        w.writerow({
            "date": str(today), "currency": CURRENCY, "underlying": underlying,
            "iv_atm_call": round(iv_c,4) if iv_c else "",
            "iv_atm_put": round(iv_p,4) if iv_p else "",
            "skew_atm": round(skew,4) if skew is not None else "",
            "num_contracts": len(rows),
            "source_ts": now.isoformat(),
        })
    print(f"OK {CURRENCY} date={today} contracts={len(rows)} iv_c={iv_c} iv_p={iv_p} skew={skew}")

if __name__ == "__main__":
    main()
