#!/usr/bin/env python3
"""# origin: ai
F7 现货-期货基差数据构建 (05 r3, pre-registered f7-preregistration.md).

Binance vision bulk spot klines 已下线（2024-01 起 404），fapi live API 被 IP ban
至 ~22:58 UTC。按预注册失败降级条款：改用 OKX 现货日线 API（免费，无需 key）。

OKX history-candles: instId=BTC-USDT/ETH-USDT/SOL-USDT, bar=1D, limit=100/页,
before 参数向前翻页。SOL-USDT 上市 2020-08-11。
输出: cache/okx_spot/{SYM}-spot-1d.csv (openTime,open,high,low,close,volume) + manifest.json
幂等：已有 CSV 则跳过下载，仅重建 manifest。
"""
import csv, json, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
CACHE = os.path.join(R3, "cache", "okx_spot")
os.makedirs(CACHE, exist_ok=True)

MARKETS = {
    "BTCUSDT": ("BTC-USDT", "2020-01-01"),
    "ETHUSDT": ("ETH-USDT", "2020-01-01"),
    "SOLUSDT": ("SOL-USDT", "2020-09-01"),
}
DAY_MS = 86400000


def fetch_page(inst, after_ms):
    # history-candles pages BACKWARDS: 'after' = timestamp, returns candles OLDER than it.
    url = (f"https://www.okx.com/api/v5/market/history-candles"
           f"?instId={inst}&bar=1D&limit=100")
    if after_ms:
        url += f"&after={after_ms}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-backtest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    if d.get("code") != "0":
        raise RuntimeError(f"OKX error {d.get('code')}: {d.get('msg')}")
    return d["data"]


def download(sym, inst, start_date):
    out = os.path.join(CACHE, f"{sym}-spot-1d.csv")
    if os.path.exists(out):
        print(f"{sym}: cached, skip")
        return out
    start_ms = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")) * 1000)
    rows, after, pages = [], None, 0
    while True:
        data = fetch_page(inst, after)
        pages += 1
        if not data:
            break
        for row in data:
            ts = int(row[0])
            if ts < start_ms:
                continue
            rows.append([ts] + [float(x) for x in row[1:6]])
        oldest = int(data[-1][0])
        # history-candles is capped at ~100 most-recent candles; page strictly
        # backwards (after=oldest) until the window closes or we stop moving.
        if len(data) < 100 or oldest <= start_ms or (after is not None and oldest >= int(after)):
            break
        after = str(oldest)
        time.sleep(0.15)
    rows.sort(key=lambda r: r[0])
    seen, dedup = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            dedup.append(r)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["openTime", "open", "high", "low", "close", "volume"])
        w.writerows(dedup)
    print(f"{sym}: {len(dedup)} days from {time.strftime('%Y-%m-%d', time.gmtime(dedup[0][0]/1000))} "
          f"to {time.strftime('%Y-%m-%d', time.gmtime(dedup[-1][0]/1000))} ({pages} pages)")
    return out


def main():
    manifest = {}
    for sym, (inst, start) in MARKETS.items():
        p = download(sym, inst, start)
        n = sum(1 for _ in open(p)) - 1
        manifest[sym] = {"file": p, "rows": n, "source": f"OKX {inst} 1D history-candles"}
    with open(os.path.join(CACHE, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()