#!/bin/bash
# S1 BTCUSDT funding monthly download (2020-01..2026-09, 81 files) + .CHECKSUM siblings
set -u
cd "$(dirname "$0")/../cache/S1_binance_vision/funding/um/BTCUSDT" || exit 1
base="https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT"
fail=0
months=()
for y in 2020 2021 2022 2023 2024 2025; do
  for m in 01 02 03 04 05 06 07 08 09 10 11 12; do months+=("$y-$m"); done
done
for m in 01 02 03 04 05 06 07 08 09; do months+=("2026-$m"); done
for ym in "${months[@]}"; do
  f="BTCUSDT-fundingRate-$ym.zip"
  if [ -s "$f" ] && [ -s "$f.CHECKSUM" ]; then continue; fi
  code=""
  for i in 1 2 3; do
    code=$(curl -s -w "%{http_code}" -o "$f" "$base/$f" --max-time 120)
    [ "$code" = "200" ] && break
    sleep 1
  done
  ccode=$(curl -s -w "%{http_code}" -o "$f.CHECKSUM" "$base/$f.CHECKSUM" --max-time 60)
  if [ "$code" != "200" ] || [ "$ccode" != "200" ]; then
    echo "FAIL $f code=$code ccode=$ccode"
    fail=$((fail+1))
  fi
done
echo "download done, fail=$fail, expected=${#months[@]}"
echo "zips: $(ls *.zip 2>/dev/null | wc -l | tr -d ' ')  checksums: $(ls *.CHECKSUM 2>/dev/null | wc -l | tr -d ' ')"
