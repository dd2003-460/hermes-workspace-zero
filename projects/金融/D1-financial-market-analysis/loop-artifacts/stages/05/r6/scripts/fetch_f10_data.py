#!/usr/bin/env python3
"""F10 数据拉取: Binance 1h klines (vision) + Bybit OI (1d).

落盘:
  cache/klines_1h/<SYMBOL>-1h-YYYY-MM.zip (+ .CHECKSUM)
  cache/bybit_oi/<SYMBOL>_oi_1d.csv  (ts_ms, open_interest)
  data/manifest.json  (完整性清单)

用法: /opt/homebrew/bin/python3 fetch_f10_data.py [symbols_csv]
"""
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # stages/05/r6
CACHE_KL = os.path.join(BASE, "cache", "klines_1h")
CACHE_OI = os.path.join(BASE, "cache", "bybit_oi")
DATA = os.path.join(BASE, "data")
VISION = "https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{ym}.zip"
BYBIT_OI = ("https://api.bybit.com/v5/market/open-interest?category=linear"
            "&symbol={sym}&intervalTime=1d&startTime={st}&endTime={et}&limit=100")

# F10 窗口: R1 需要 DVOL 窗 (2022-04→2025-12), R2 用全部可得; 统一拉 2022-01→2025-12
START = date(2022, 1, 1)
END = date(2025, 12, 31)


def months_between(a, b):
    ym = []
    y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        ym.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return ym


def http_get(url, timeout=30, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "f10-research/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2 * (i + 1))


def fetch_kline(sym, ym):
    y, m = ym
    ym_s = f"{y:04d}-{m:02d}"
    path = os.path.join(CACHE_KL, f"{sym}-1h-{ym_s}.zip")
    cksum_path = path + ".CHECKSUM"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return sym, ym_s, "cached", os.path.getsize(path)
    url = VISION.format(sym=sym, ym=ym_s)
    try:
        blob = http_get(url)
    except Exception as e:
        return sym, ym_s, f"FAIL:{type(e).__name__}", 0
    with open(path, "wb") as f:
        f.write(blob)
    sha = hashlib.sha256(blob).hexdigest()
    with open(cksum_path, "w") as f:
        f.write(f"{sha}  {os.path.basename(path)}\n")
    # sanity: zip must contain the csv
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
        names = zf.namelist()
        if not any(n.endswith(".csv") for n in names):
            return sym, ym_s, "FAIL:not_zip_csv", len(blob)
    except Exception as e:
        return sym, ym_s, f"FAIL:zip:{e}", len(blob)
    return sym, ym_s, "ok", len(blob)


def fetch_bybit_oi(sym):
    """按月分页拉 Bybit 1d OI. 每页实测上限 ~31 行; 逐月请求避免截断."""
    out_rows = {}
    for ym in months_between(START, END):
        y, m = ym
        st = int(datetime_ts(y, m, 1))
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        et = int(datetime_ts(ny, nm, 1)) - 1
        url = BYBIT_OI.format(sym=sym, st=st, et=et)
        try:
            blob = http_get(url, timeout=20, retries=2)
            d = json.loads(blob)
            lst = d.get("result", {}).get("list", [])
        except Exception as e:
            print(f"  [oi] {sym} {ym[0]:04d}-{ym[1]:02d} FAIL {type(e).__name__}", flush=True)
            continue
        for r in lst:
            ts = int(r["timestamp"])
            out_rows[ts] = float(r["openInterest"])
        time.sleep(0.3)
    path = os.path.join(CACHE_OI, f"{sym}_oi_1d.csv")
    rows = sorted(out_rows.items())
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts_ms", "open_interest"])
        w.writerows(rows)
    span = ""
    if rows:
        from datetime import datetime, timezone
        d0 = datetime.fromtimestamp(rows[0][0] / 1000, tz=timezone.utc).date()
        d1 = datetime.fromtimestamp(rows[-1][0] / 1000, tz=timezone.utc).date()
        span = f"{d0}..{d1}"
    return sym, len(rows), span


def datetime_ts(y, m, d):
    from datetime import datetime, timezone
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


def main():
    symbols = sys.argv[1].split(",") if len(sys.argv) > 1 else ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    for d in (CACHE_KL, CACHE_OI, DATA):
        os.makedirs(d, exist_ok=True)
    all_months = months_between(START, END)
    manifest = {"klines": {}, "oi": {}, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    jobs = [(s, ym) for s in symbols for ym in all_months]
    print(f"kline jobs: {len(jobs)} ({len(symbols)} syms x {len(all_months)} months)", flush=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_kline, s, ym): (s, ym) for s, ym in jobs}
        done = 0
        for fut in as_completed(futs):
            s, ym_s, status, size = fut.result()
            done += 1
            if status != "ok" and status != "cached":
                print(f"  [kl] {s} {ym_s} {status}", flush=True)
            manifest["klines"].setdefault(s, []).append({"ym": ym_s, "status": status, "bytes": size})
            if done % 48 == 0:
                print(f"  kl progress {done}/{len(jobs)}", flush=True)

    for s in symbols:
        _, n, span = fetch_bybit_oi(s)
        print(f"[oi] {s}: {n} rows, span={span}", flush=True)
        manifest["oi"][s] = {"rows": int(n), "span": str(span)}

    with open(os.path.join(DATA, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    # summary
    for s in symbols:
        ks = manifest["klines"].get(s, [])
        ok = sum(1 for k in ks if k["status"] in ("ok", "cached"))
        fails = [k["ym"] for k in ks if k["status"] not in ("ok", "cached")]
        print(f"SUMMARY {s}: klines {ok}/{len(ks)} ok; fails={fails[:5]}{'...' if len(fails)>5 else ''}")
    print("manifest written:", os.path.join(DATA, "manifest.json"))


if __name__ == "__main__":
    main()