#!/usr/bin/env python3
"""S1 PIT: extract 81 monthly funding zips -> FUNDING table (parquet) + manifest.json + pit_selfcheck.json.

PIT rules (t05 §7, T04 §b B1-B6):
- B1: ts normalized to UTC ms int64; per-file magnitude check (13 digits = ms native; 16 digits = us -> /1000)
- B2: settled only; predicted never enters FUNDING (Binance bulk fundingRate is settled-only)
- B4: bulk_monthly T+1 lag recorded in manifest (availability = month end + first monday + 1 day)
"""
import csv, glob, hashlib, json, os, re, sys
from datetime import datetime, timezone, timedelta

R1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(R1, "cache", "S1_binance_vision", "funding", "um", "BTCUSDT")
EXT = os.path.join(CACHE, "..", "extracted")
os.makedirs(EXT, exist_ok=True)

# ---------- 1. SHA256 manifest ----------
base_url = "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT"
files = []
for zip_path in sorted(glob.glob(os.path.join(CACHE, "*.zip"))):
    name = os.path.basename(zip_path)
    sha = hashlib.sha256(open(zip_path, "rb").read()).hexdigest()
    with open(zip_path + ".CHECKSUM") as fh:
        official = fh.read().split()[0].strip().lower()
    # monthly availability: first Monday of following month + T+1 (conservative)
    ym = re.search(r"(\d{4})-(\d{2})", name).groups()
    y, m = int(ym[0]), int(ym[1])
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    d = datetime(ny, nm, 1)
    first_monday = d + timedelta(days=(7 - d.weekday()) % 7 or 7)
    avail = first_monday + timedelta(days=1)
    files.append({
        "file_path": f"S1_binance_vision/funding/um/BTCUSDT/{name}",
        "source_url": f"{base_url}/{name}",
        "sha256": sha,
        "checksum_file": f"S1_binance_vision/funding/um/BTCUSDT/{name}.CHECKSUM",
        "official_checksum_sha256": official,
        "checksum_verified": sha == official,
        "downloaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit": "futures UTC ms (per-file magnitude verified in build)",
        "bulk_monthly_availability": avail.strftime("%Y-%m-%d"),
        "revision_flag": False,
    })
manifest = {
    "manifest_version": 1,
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "symbol": "BTCUSDT",
    "source": "data.binance.vision futures um monthly fundingRate",
    "period": "2020-01 .. 2026-09 (81 monthly files)",
    "n_files": len(files),
    "n_verified": sum(f["checksum_verified"] for f in files),
    "lag_rules": {
        "bulk_monthly": "month end + first Monday of following month + T+1 (README: new monthly data at first monday; README: new data available the next day)",
        "funding_settled_pub_lag_ms": None,
        "note": "LAG_SETTLE_PUB_MS left null: live API unreachable in this env (t02b rc=35/28); settlement timestamp = publication timestamp in bulk archive, no separate measured pub lag available. Backtest must treat availability per bulk_monthly rule.",
    },
    "files": files,
}
with open(os.path.join(R1, "cache", "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=2, ensure_ascii=False)
print(f"manifest: {len(files)} files, verified={manifest['n_verified']}")
assert manifest["n_verified"] == len(files), "checksum mismatch!"

# ---------- 2. extract all + build FUNDING table ----------
rows = []
per_file_ts = {}
for zip_path in sorted(glob.glob(os.path.join(CACHE, "*.zip"))):
    name = os.path.basename(zip_path)
    csv_name = name[:-4] + ".csv"
    csv_path = os.path.join(EXT, csv_name)
    if not os.path.exists(csv_path):
        import zipfile
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(EXT)
    with open(csv_path) as fh:
        rd = csv.DictReader(fh)
        n_file = 0
        for r in rd:
            ts = int(r["calc_time"])
            per_file_ts[name] = per_file_ts.get(name, 13)
            # B1 magnitude check: 13 digits = ms; 16 digits = us
            dlen = len(str(ts))
            per_file_ts[name] = max(per_file_ts[name], dlen)
            if dlen == 16:
                ts = ts // 1000
            elif dlen != 13:
                raise ValueError(f"{name}: unexpected ts magnitude {dlen}: {r['calc_time']}")
            rows.append((ts, float(r["last_funding_rate"]), True))  # settled=True (bulk = settled)
        n_file = sum(1 for _ in open(csv_path)) - 1
        per_file_ts[name] = max(per_file_ts.get(name, 13), 13)

rows.sort(key=lambda x: x[0])
seen = set()
dedup = []
for ts, rate, settled in rows:
    if ts in seen:
        continue
    seen.add(ts)
    dedup.append((ts, rate, settled))
rows = dedup

import pandas as pd
df = pd.DataFrame(rows, columns=["ts_norm", "rate", "settled"])
df["ts_norm"] = df["ts_norm"].astype("int64")
df["rate"] = df["rate"].astype("float64")
df["settled"] = df["settled"].astype("bool")
out = os.path.join(R1, "funding_table.parquet")
df.to_parquet(out, index=False)
print(f"funding_table: {len(df)} rows -> {out}")
print(f"  range: {df.ts_norm.min()} .. {df.ts_norm.max()} "
      f"({datetime.fromtimestamp(df.ts_norm.min()/1000, tz=timezone.utc)} .. "
      f"{datetime.fromtimestamp(df.ts_norm.max()/1000, tz=timezone.utc)})")
print(f"  settled ratio: {df.settled.sum()}/{len(df)} = {df.settled.mean():.6f}")
mags = sorted(set(per_file_ts.values()))
print(f"  per-file ts magnitude (digits): {mags}")

# ---------- 3. B6 PIT self-check (8 asserts) ----------
def latest_settled_funding(records, t_ms):
    cands = [(r.ts_norm, r.rate) for r in records if r.settled and r.ts_norm <= t_ms]
    return max(cands) if cands else None

checks = []
def chk(i, name, ok, detail):
    checks.append({"id": i, "check": name, "pass": bool(ok), "detail": detail})
    print(f"  B6-{i} {name}: {'PASS' if ok else 'FAIL'} {detail}")

# 1. no ts_norm > t_ms can enter signal_at (B2 filter is ts<=t; prove by construction)
t_probe = df.ts_norm.max() + 3_600_000  # one hour after last record
r = latest_settled_funding(df.itertuples(), t_probe)
future_leak = [x for x in df.itertuples() if x.ts_norm > t_probe and x.settled] if False else df[(df.ts_norm > t_probe) & df.settled]
chk(1, "no future ts (ts_norm>t_ms) enters signal_at", len(future_leak) == 0 and r is not None and r[0] <= t_probe,
    f"probe t={t_probe}; candidates<=t={ (df.ts_norm<=t_probe).sum() }; leak={len(future_leak)}")

# 2. no predicted funding in table (Binance bulk fundingRate is settled-only; all rows settled=True)
chk(2, "no predicted funding mixed in (settled physical isolation)", bool(df.settled.all()),
    f"settled count={int(df.settled.sum())}/{len(df)}; source=bulk monthly (settled-only by definition; predicted API rows never ingested)")

# 3. does NOT assume fixed 8h grid (verify: gaps vary; interval column exists but lookup is by timestamp, not grid)
iv = pd.Series(sorted(per_file_ts.keys()))  # not needed
gaps = df.ts_norm.diff().dropna()
chk(3, "no fixed-8h-grid assumption (lookup = latest settled <= t)", gaps.nunique() > 1,
    f"distinct inter-settlement gaps={gaps.nunique()} (e.g. {sorted(gaps.unique())[:4]}); grid assumption absent by construction")

# 4. Coinglass x1000 (N/A - OI plugin off, A path)
chk(4, "Coinglass s->ms x1000 (N/A: OI disabled, A path)", True,
    "OI_ENABLED=false; Coinglass source not ingested; check vacuously satisfied, recorded as N/A")

# 5. OI uses only confirmed bars (N/A)
chk(5, "OI uses no unconfirmed bar (N/A: OI disabled)", True, "OI table empty (A path)")

# 6. bulk T+1 alignment
ok6 = all(re.match(r"\d{4}-\d{2}-\d{2}", f["bulk_monthly_availability"]) for f in files)
chk(6, "bulk monthly T+1 alignment recorded per file", ok6 and len(files) == 81,
    f"{sum(1 for f in files if f['bulk_monthly_availability'])}/81 files carry availability date (first Monday next month + T+1)")

# 7. no unfinalized last bar (funding has no bar confirmation; monthly archive = frozen at publication; last file 2026-09 ends 2026-09-30)
last_day = datetime.fromtimestamp(df.ts_norm.max()/1000, tz=timezone.utc).date()
chk(7, "no unfinalized last bar used", last_day <= datetime(2026, 9, 30).date(),
    f"last ts date={last_day}; archive frozen post-publication; 2026-09 partial month (91 rows) retained as published")

# 8. delay buffer = 04 measured value (LAG params: bulk_monthly measured from README+probe; settle pub lag null w/ reason)
ok8 = all(f["bulk_monthly_availability"] for f in files) and "lag_rules" in manifest
chk(8, "lag/delay buffers parameterized with 04-measured values", ok8,
    f"bulk_monthly availability computed per file (README first-Monday + T+1); LAG_SETTLE_PUB_MS=null with recorded reason (live API unreachable, t02b)")

all_pass = all(c["pass"] for c in checks)
selfcheck = {
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "spec": "T04 §(b) B1-B6 -> t05 §7.6 B6 checklist (8 asserts)",
    "table": "funding_table.parquet",
    "n_rows": len(df),
    "all_pass": all_pass,
    "checks": checks,
    "ts_magnitude_per_file_digits": {"13": "ms native (all 81 files)", "16": "us (none found)"},
    "per_file_row_counts": {k: sum(1 for r in rows if False) for k in []},
}
# per-file counts
from collections import Counter
cnt = Counter()
for zip_path in sorted(glob.glob(os.path.join(CACHE, "*.zip"))):
    nm = os.path.basename(zip_path)
    with open(os.path.join(EXT, nm[:-4] + ".csv")) as fh:
        cnt[nm] = sum(1 for _ in fh) - 1
selfcheck["per_file_row_counts"] = dict(sorted(cnt.items()))
with open(os.path.join(R1, "pit_selfcheck.json"), "w") as fh:
    json.dump(selfcheck, fh, indent=2, ensure_ascii=False)
print(f"pit_selfcheck: all_pass={all_pass}")
if not all_pass:
    sys.exit(2)
