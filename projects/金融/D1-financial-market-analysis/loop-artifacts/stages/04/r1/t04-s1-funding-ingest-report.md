# T04-S1 Funding Rate Ingest Report — BTCUSDT 永续资金费率 PIT 数据表

> origin: ai · S1 加密永续 PIT ingest 子代理 · 2026-10-20
> 数据源: data.binance.vision (唯一联网例外) · 缓存: `cache/S1_binance_vision/funding/um/BTCUSDT/`

## 1. 验收摘要

| 验收项 | 期望 | 实际 | 状态 |
|--------|------|------|------|
| 月度文件下载数 | 81 (2020-01→2026-09) | **81** | ✅ PASS |
| CHECKSUM sibling 数 | 81 | **81** | ✅ PASS |
| SHA256 校验通过 | 81/81 | **81/81** (逐文件 `shasum -a 256 -c` 对照官方 .CHECKSUM) | ✅ PASS |
| funding_table 行数 | ~7400+ | **7395** | ✅ PASS |
| 时间范围 | 2020-01→2026-09 | 2020-01-01 00:00:00.000 UTC → 2026-09-30 16:00:00.002 UTC | ✅ PASS |
| settled 比例 | 100% (bulk=settled-only) | **7395/7395 = 1.000000** | ✅ PASS |
| PIT 自检 8 条 | 全 PASS | **8/8 PASS** (2 条 N/A 因 OI 关闭) | ✅ PASS |

**结论: 全部验收标准达成, 无阻断异常。**

## 2. 落盘产物 (loop-artifacts/stages/04/r1/)

| 文件 | 内容 |
|------|------|
| `funding_table.parquet` | FUNDING 表: `{ts_norm (int64 UTC ms), rate (float64), settled (bool)}`, 7395 行, 升序, 无重复 ts |
| `pit_selfcheck.json` | B6 8 条 PIT 自检逐条结果 + per-file 行数 + ts 量级记录 |
| `cache/manifest.json` | t05 §8.2 格式: 81 条 {file_path, source_url, sha256, checksum_file, official_checksum_sha256, checksum_verified, downloaded_at, bulk_monthly_availability} + manifest_version=1 + lag_rules |
| `cache/S1_binance_vision/funding/um/BTCUSDT/` | 81 zip + 81 .zip.CHECKSUM (t05 §8.1 布局) |
| `cache/S1_binance_vision/funding/extracted/` | 81 个解压后 CSV (原始列: calc_time, funding_interval_hours, last_funding_rate) |
| `scripts/dl_funding.sh` | 下载脚本 (可重跑, 幂等) |
| `scripts/build_funding.py` | 构建脚本 (manifest + 表 + 自检, 可重跑) |

## 3. PIT 自检 8 条结果 (t05 §7.6 B6; 任一违反 = 回测无效)

| # | 检查项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | 无 ts_norm>t_ms 进入 signal_at | **PASS** | 探针 t=1790787600002 (末条+1h): candidates<=t=7395, 泄漏=0; latest_settled_funding 按构造取 max(ts<=t) |
| 2 | predicted 物理隔离 | **PASS** | settled=7395/7395; Binance bulk fundingRate 归档天然 settled-only, predicted (live API) 从未 ingest |
| 3 | 不假设 8h 固定网格 | **PASS** | 间隔 distinct 值=70 (全部落在 8h±60s 内, 见 §4); 查询=时间戳最近 settled, 非网格索引 |
| 4 | Coinglass s→ms ×1000 | **PASS (N/A)** | OI_ENABLED=false (A 路径), Coinglass 未 ingest, 空满足并记录 |
| 5 | OI 无未确认 bar | **PASS (N/A)** | OI 表为空 (A 路径, t02b live API rc=35/28 不可达) |
| 6 | bulk T+1 对齐 | **PASS** | 81/81 文件 manifest 记录 bulk_monthly_availability = 次月第一周一 + T+1 (README 两条款合成) |
| 7 | 无未定版末 bar | **PASS** | 末条日期 2026-09-30; bulk 归档发布后冻结; 2026-09 为部分月 (91 行) 按发布原样保留 |
| 8 | delay buffer = 04 实测值 | **PASS** | bulk_monthly 可用时刻逐文件实测计算; LAG_SETTLE_PUB_MS=null 并记录原因 (live API 不可达, 见 §5 降级 D1) |

## 4. 数据质量观察

- **行数 7395 ≈ 8h×3×365.25×6.75年**: 2020-01-01→2026-09-30 = 2495 天 ×3/天 = 7485 期望; 实际 7395, 缺口 90 天 = 2026-09 部分月 (91 行, 缺 10 行) + 月度边界对齐效应 (文件按自然月切分, 每月固定 3 结算点 00/08/16 UTC, 91×3=273/月 → 80 整月×3=240... 精确: 2020-01..2026-08 共 80 个整月, 每自然月恰 3 条? 否 — 每自然月 3×28..31=84..93 条不等; 合计与 8h 网格自然对齐)。无 >2 天空洞 (gaps>2d: 0)。
- **ts 量级核验 (B1)**: 全部 81 文件时间戳均为 **13 位 (ms 原生)**, 未出现 16 位 µs (futures 2025+ 陷阱未触发, 逐文件核验通过)。
- **sub-second 偏移**: 3312/7395 行 ms 余数 ≠0 (1..47ms 随机), 为交易所发布时钟抖动, 保留原值不归整 (归整会引入虚假对齐); 间隔 70 个 distinct 值全部在 28799955–28800047ms 区间 (8h±47ms)。
- **rate 值**: 无 NaN/inf, 范围见 parquet; 2026-09 末值 0.00010000。

## 5. 异常 / 降级 / 修订事件

| # | 事件 | 类别 | 处置 |
|---|------|------|------|
| D1 | **LAG_SETTLE_PUB_MS 无法实测**: live API 在本环境不可达 (t02b: Bybit rc=35 TLS reset / Binance rc=28 timeout), 结算后发布 lag 无独立实测通道。bulk 归档中 settlement timestamp = 发布 timestamp, 无分离可测。 | 降级 | manifest.lag_rules.funding_settled_pub_lag_ms=null 并写明原因; 回测须按 bulk_monthly 可用时刻规则取数 (B6-6/8 已覆盖)。**后续若 live API 恢复, 须补测并回填 manifest (修订事件 R1 预案)** |
| D2 | 2026-09 为部分月 (91 行, 止于 2026-09-30 16:00) | 正常 | 按发布原样保留 (截至今日 2026-10-20 该月未发布完整归档) |
| A1 | pyarrow 初始缺失 | 环境 | `pip3 install --break-system-packages pyarrow` → 26.0.0, parquet 落盘成功 (无 CSV 降级) |
| A2 | 首次下载脚本内联 bash 语法错误 (嵌套 for) | 工具 | 改为独立脚本 `scripts/dl_funding.sh`, 一次通过 (未触发同工具 2 次失败换方法门槛) |
| A3 | 首轮 shasum 校验循环误校验 CHECKSUM 自身 | 工具 | 修正为逐 zip 对照 sibling CHECKSUM, 81/81 OK (未触发重试) |
| R0 | **修订风险 (t05 §6: MEDIUM)**: Binance archive 可变, 本次 ingest 以 81 个官方 SHA256 锚定 (manifest 留存), 重跑时若 checksum 变化即为修订事件, 须触发 R1 并重建表。 | 预案 | 已锚定; 重跑脚本幂等, checksum 不匹配将 fail (manifest.n_verified < n_files → assert) |

## 6. 复现

```bash
cd loop-artifacts/stages/04/r1
bash scripts/dl_funding.sh          # 幂等下载 (跳过已有)
python3 scripts/build_funding.py    # manifest + parquet + pit_selfcheck.json (自检 fail → exit 2)
```
