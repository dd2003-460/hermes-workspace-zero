#!/usr/bin/env python3
"""# origin: ai
Build BTCUSDT daily kline table from local Binance vision monthly zips (2020-2025).
PIT: daily bar with openTime T is available at T + 1_day (bulk T+1 alignment,
per T04 B1-B6 / t05 bulk_daily rule). Output: cache/.../klines/.../BTCUSDT-1d-2020_2025.csv
Idempotent: rebuilds from zips every run.
"""
import os, glob, zipfile, pandas as pd, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.dirname(HERE)
ZDIR = os.path.join(R1, "cache", "S1_binance_vision", "klines", "um", "BTCUSDT", "1d")

rows = []
for zpath in sorted(glob.glob(os.path.join(ZDIR, "BTCUSDT-1d-*.zip"))):
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if n.endswith(".csv"):
                with z.open(n) as fh:
                    first = fh.readline()
                if first.startswith(b"open_time"):
                    df = pd.read_csv(z.open(n))
                    df = df.rename(columns={"open_time": "openTime", "close_time": "closeTime",
                                            "quote_volume": "qv", "count": "trades",
                                            "taker_buy_volume": "tbb", "taker_buy_quote_volume": "tbq"})
                    df["ignore"] = 0
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
# keep only the columns we need + volume for reference
kl = kl[["openTime", "open", "high", "low", "close", "volume"]]
# sanity: timestamp magnitude 13-digit ms
assert kl["openTime"].min() > 1e12, "timestamp not in ms"
out = os.path.join(ZDIR, "BTCUSDT-1d-2020_2025.csv")
kl.to_csv(out, index=False)
sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
print("rows", len(kl), "range",
      pd.to_datetime(kl["openTime"].min(), unit="ms", utc=True),
      pd.to_datetime(kl["openTime"].max(), unit="ms", utc=True))
print("sha256", sha)
print("wrote", out)
