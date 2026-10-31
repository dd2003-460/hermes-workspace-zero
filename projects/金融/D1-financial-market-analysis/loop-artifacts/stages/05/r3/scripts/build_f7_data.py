#!/usr/bin/env python3
"""# origin: ai
F7 现货-期货基差数据构建 (05 r3, pre-registered f7-preregistration.md).

Binance vision bulk spot klines 已下线（2024-01 起 404），fapi live API 被 IP ban
至 ~22:58 UTC。按预注册失败降级条款：改用 OKX 现货日线 API（免费，无需 key）。

OKX history-candles: instId=BTC-USDT/ETH-USDT/SOL-USDT, bar=1D, limit=100/页。
翻页实证（2026-10-31）：before 参数无效（恒返最新页）；after=ts 返回 ts 之前的行
（不含锚点），可翻到全历史（BTC 至 2019-10，SOL 最早 2020-09-29）。
输出: cache/okx_spot/{SYM}-spot-1d.csv (openTime,open,high,low,close,volume) + manifest.json
      cache/perp_klines/{SYM}-1d-*.zip（BTCUSDT 补缺下载 Binance vision futures um daily；
      ETH/SOL 复用 r2 cache 已校验 zip）+ perp_manifest.json
幂等：已有完整 CSV/zip 则跳过下载，仅重建 manifest。
PIT 残余风险: OKX 为 live API，历史日 K 可能含修订（Binance vision 归档不可用时的降级代价），
对基差信号（阈值 ±0.05% ≈ 2σ）的影响记入 f7_report.md。
"""
import csv, json, os, shutil, time, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
R2 = os.path.join(R3, "..", "r2")
CACHE = os.path.join(R3, "cache", "okx_spot")
PERP_CACHE = os.path.join(R3, "cache", "perp_klines")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(PERP_CACHE, exist_ok=True)

MARKETS = {
    "BTCUSDT": ("BTC-USDT", "2020-01-01"),
    "ETHUSDT": ("ETH-USDT", "2020-01-01"),
    "SOLUSDT": ("SOL-USDT", "2020-09-01"),
}
DAY_MS = 86400000


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "research-backtest/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_page(inst, after_ms):
    # history-candles pages BACKWARDS: 'after' = timestamp, returns candles OLDER than it.
    url = (f"https://www.okx.com/api/v5/market/history-candles"
           f"?instId={inst}&bar=1Dutc&limit=100")  # 1Dutc = UTC day boundary, aligns with Binance vision
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
    # idempotency: skip if cached file already covers the requested range
    if os.path.exists(out):
        rows = list(csv.reader(open(out)))[1:]
        if rows and int(rows[0][0]) <= int(time.mktime(time.strptime(start_date, "%Y-%m-%d")) * 1000) + DAY_MS:
            print(f"{sym}: cached ({len(rows)} days), skip")
            return out
        os.remove(out)  # stale partial file (e.g. from buggy before-pagination run)
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
        # history-candles pages strictly backwards (after=oldest). The API only
        # serves a finite recent window (~2500 daily candles); stop when the
        # page stops moving or we pass the requested start.
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


def ensure_perp(sym):
    """Perp daily klines zips: ETH/SOL copied from r2 cache (checksum-verified there);
    BTCUSDT downloaded missing months from Binance vision futures um monthly klines."""
    src_dir = os.path.join(R2, "cache")
    files = sorted(f for f in os.listdir(src_dir) if f.startswith(f"{sym}-1d-") and f.endswith(".zip"))
    copied = []
    for fn in files:
        dst = os.path.join(PERP_CACHE, fn)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(src_dir, fn), dst)
            copied.append(fn)
    # BTCUSDT gap-fill: 04/r1 only cached a subset; download all months 2020-01..2026-10
    if sym == "BTCUSDT":
        have = {f.split("-1d-")[1].rsplit(".", 1)[0] for f in os.listdir(PERP_CACHE) if f.startswith("BTCUSDT-1d-")}
        ym_list = [(y, m) for y in range(2020, 2027) for m in range(1, 13)
                   if (y, m) <= (2026, 10)]
        got = []
        for y, m in ym_list:
            tag = f"{y}-{m:02d}"
            if tag in have:
                continue
            url = f"https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{tag}.zip"
            try:
                data = http_get(url)
            except Exception as e:
                print(f"  BTCUSDT {tag}: download failed ({getattr(e, 'code', e)}), skip")
                continue
            with open(os.path.join(PERP_CACHE, f"BTCUSDT-1d-{tag}.zip"), "wb") as fh:
                fh.write(data)
            got.append(tag)
        if got:
            print(f"BTCUSDT perp: downloaded {len(got)} missing months")
    return len([f for f in os.listdir(PERP_CACHE) if f.startswith(f"{sym}-1d-") and f.endswith(".zip")])


def main():
    manifest = {}
    for sym, (inst, start) in MARKETS.items():
        p = download(sym, inst, start)
        n = sum(1 for _ in open(p)) - 1
        manifest[sym] = {"file": p, "rows": n,
                         "source": f"OKX {inst} 1D history-candles (live API, after-pagination)"}
    perp_manifest = {sym: {"zips": ensure_perp(sym),
                           "source": "Binance vision futures um daily klines (r2 cache + gap-fill)"}
                     for sym in MARKETS}
    with open(os.path.join(CACHE, "manifest.json"), "w") as fh:
        json.dump({"spot": manifest, "perp": perp_manifest}, fh, indent=2)
    print(json.dumps(manifest, indent=2))
    print(json.dumps(perp_manifest, indent=2))


if __name__ == "__main__":
    main()