# origin: ai

# T08 coverage_proof（G2 join）— 03→04 接口覆盖证明

**署名**: T08v2 子代理（v1 e126f040 死亡零落盘后接管）；骨架: Lead 移交
**角色**: coverage_proof / G2 join — 汇总 T01–T07 的 declared artifacts，做跨 artifact 一致性核验 + 列 03→04 未决项（gap），对照 success_condition。
**方法**: 定点核验（grep + 定向 read 关键行），**未**全文重读 7 个 artifact（v1 因全文重读上下文耗尽死亡）。每个 claim 标来源文件+节；未定点核验的点标 **继承(v1/Lead)** 而非 实测。
**核验基准日**: 2026-10-17（字节数与 mtime 复验与 Lead 移交一致）。

---

## §1 节点→产物映射表

复验方式: `ls -la artifacts/`（@2026-10-17），字节数与 mtime 全匹配 Lead 移交，无新增/丢失/篡改。

| 节点 | 任务 | 产物 | 大小 (实测) | 状态 | confidence |
|------|------|------|------|------|------|
| T01 | arXiv:2608.27734 数字+正文直验 | `artifacts/t01-arxiv-260827734-verify.md` | 8935B @15:55 | done（task JSON completed；Lead 内联 PDF 正文级补验）| 0.95 |
| T02 | OI 数据源 A/B/C 三选项预注册决策 | `artifacts/t02-oi-source-decision.md` | 11190B @14:40 | done | 0.70 |
| T02b | Bybit API 可达性预检（本环境）| `artifacts/t02b-api-reachability-precheck.md` | 3320B @15:42 | done（Lead 内联预检，经 T04 §Lead 批注管理，无独立 task JSON）| 无自申报（实证 rc=35/28）|
| T03 | 阴性检索协议（funding 择时 gap）| `artifacts/t03-negative-search-protocol.md` | 18288B @15:49 | done（v1+v2）| 0.75 |
| T04 | 信号架构终版 spec | `artifacts/t04-signal-spec.md` | 25667B @16:25 | done（含 Lead 批注）| 0.72 |
| T05 | 数据管线设计（拉取/PIT/µs 陷阱/成本）| `artifacts/t05-data-pipeline-design.md` | 35119B @17:25 | done | 0.80 |
| T06 | 回测设计（失败判据/45 矩阵）| `artifacts/t06-backtest-design.md` | 26920B @17:22 | done（含 Lead 批注）| 0.85 |
| T07 | 基准选择（文献分层/5基线/三同/trial 120）| `artifacts/t07-benchmark-selection.md` | 38677B @19:14（含 §v2 核验补遗）| done | 0.80 |
| T08 | 本文件（coverage_proof / G2 join）| `artifacts/t08-coverage-proof.md` | （自算，本文件）| done | 自定（见 §5）|

**结论行（节点侧）**: 9 个 declared node（T01–T08），T01–T07 共 7 artifact 全部在盘且字节核验通过，T08 = 本文件。0 个缺失 declared artifact。

---

## §2 跨 artifact 一致性检查

### (1) S2 锚点统一（3669.91 vs 3577.0）— ✅

grep 全 7 artifact（`3669.91` / `3577.0`）:
- `3669.91` = **8 处**，**全部**在 `t05-data-pipeline-design.md`（L18, L49, L126, L127, L131, L137, L362, L463）。为统一锚点（三熊底: 2002-10-09 c776.8 / 2008-03-10 c1273.4 / 2022-10-13 c3669.91；三熊底表在 T05 L135–137，机器可读在 T05 L362 `gspc_anchor.json`）。
- `3577.0` = **7 处**，**全部**在 `t05-data-pipeline-design.md`（L18, L126, L128, L129, L137, L142, L463），且**每一处身份均为"未采用 / 原始值（Yahoo，本环境不可复核）"**（如 L128 "本节点(Yahoo 403 不可达) 无法本环境复核 3577.0"、L463 "Yahoo 3577.0 未采用"）。
- **零泄漏**: T06 / T07 中 `3669.91` 与 `3577.0` 均 0 命中。

**判定**: ✅ 3669.91 为唯一统一锚点，3577.0 只以"未采用原始值"身份出现，无冲突。

### (2) T05 ↔ T06（窗口 / PIT B0-B6 / 数据源）— ✅

- **数据源**: 一致。S1 = `data.binance.vision`（fundingRate 2020-01→，T05 L16/L66/L461）；S2 = 新浪 `hq.sinajs.cn`（锚点源，可达；非日线，T05 L50 `gb_ixic` 200 可达 / `gb_$inx` 空串）；S3 = 腾讯 ifzq `sh000300` qfq（T05 L57/L223/L437/L464）。T06 引用同一组源。
- **PIT 规则 B0–B6**: 一致。T06 §8 L211 "PIT 伪代码（B1–B5）+ B6 违规检查清单（8 条）" **委托** T04 §(b)；T05 L454 "B1 normalize_ts" 载 µs 陷阱；T07 L364 "引用 T04 §(b) B0-B6 基线与 funding 同一套不放宽"。三方引用同一 PIT owner（T04 §(b)），无分叉。
- **窗口**: 一致（无硬冲突）。S1 funding 2020-01→；S2 锚点制（起点 last-known，见 (5) 的 nuanced 处理）；S3 ifzq 可观测起点 2018-07-17、单次 cap≈2000（T05 L57/L227/L437/L464；T06 引用同一边界）。
- **注**: on-disk T05 的 S2 起点表述为 "last-known 1950, not first-verified in this env"（T05 L206/L47/L68），与 T06 §1.1 "04 前预注册写入" 的窗口下界存在措辞张力 → 归入 (5) 与 §4 gap 6/8，**非硬冲突**（T05 自标 not first-verified，T06 留 04 预注册位）。

**判定**: ✅ 窗口 / PIT / 数据源三方一致，PIT 单一 owner（T04 §(b)）。

### (3) T06 ↔ T07（基线清单 + 检验家族 / trial count）— ❌(drift) + ✅

**(a) 基线清单 — ❌ 清单不一致（drift 非 conflict）**:
- **T06 §8 L212**（基线行，引文精确）: "T07 `t07-benchmark-selection.md`（并行，待落盘）| 朴素基准集：buy & hold / 动量 / 趋势跟随 / funding 朴素规则 / **制度分解**（public-benchmarks 建议输入#1）+ 已核验 arXiv 锚（1912.03270 / 2212.06888）"。—— 含"制度分解"作第 5 项、**无 RSI-14**、显式"并行，待落盘"委托 T07。
- **T07 终版 5 基线**（T07 L16, L134–147, L180, L186–187, L361）: buy-and-hold / momentum-12-1(L=252,S=21) / **RSI-14**(Wilder N=14, <30 入 long / >70 出 flat) / trend-MA(50/200 EMA 金叉死叉) / funding 朴素(25/75 分位反向 + 符号跟随)。RSI-14 加入；regime 分解按 T07 L187（§3.7）降为**评估维度**而非第 6 基线。
- **判定**: ❌ 清单不一致（T06 朴素 5 集合 vs T07 终版 5 基线: RSI-14 入、regime 分解出）。但 T06 L212 明确"并行，待落盘"委托 T07 → **drift 非 conflict**，**04 以 T07 终版为准**。引文行号复验 = T06 L212 精确。

**(b) 检验家族 / trial count — ✅ 兼容（加注释）**:
- T06 §4.4: "45 测试家族 BH-FDR α=0.05"，红线 "04 不得事后扩大家族或下调 α"（T06 L139, L143, L228），trial count = 45 预注册 + "04 事后新增全记录"（T06 L74）。
- T07 §4（L216–223）: trial 扩展 **120 = 45(funding) + 75(基线 cell 5 spec × 5 窗 × 3 regime 上限保守计数)**；备选 **50**（若 buy-hold 等固定 spec 计 1 非 15）。这是 **03 预注册**（T07 在 03 阶段产出），**非 04 事后扩家族**。
- **判定**: ✅ 兼容。T07 的 120 是 03 阶段预注册的保守上限计数，不违反 T06"04 不得事后扩家族或降 α"红线（那是针对 04 执行期的事后行为，03 预注册合法）。**注释**: T07 120 = 保守上限 cell count（非最小充分数），04 可冻结 120 或降备选 50，须 pre-04 锁定。

### (4) T02 → T04 → T05 OI 三方 — ✅ 全一致

- **B 默认 conf**: T02 `conf=0.70`（T02 L88）。
- **C 三预注册条件**（逐字一致 T02 L55–57 = T04 L39–41）:
  1. **价值**: ΔS = S_oi − S_base，|ΔS|≥+0.20 **且** 95% bootstrap CI（≥3 折）下界 > 0；退化判据 OOI IC ≥ +0.05 且跨折 ≥3 同号（T02 L67 / T04 L39）。
  2. **免费源瓶颈**: 有效 OI bar 覆盖率 < 95% **或** Bybit 延迟警示触发率 > 5% 回测 bar（T02 L56 / T04 L40）。
  3. **成本**: ≤ $30/mo（$29 满足；涨 > $50 不启用）（T02 L57 / T04 L41）。
- **A 起步 + 降级事件已记录**: T04 L278（Lead 批注）"04 在本环境直接从 A（funding-only）起步并记录降级事件；B 为条件路径；C 三触发条件不变"；T05 L17 "本环境 04 从 A 起步并记录降级事件；OI 源可选插件默认关闭（OI_ENABLED=false）"。degradation_event = t02b rc=35/rc=28, 2026-10-17（T05 L78）。
- **T05 OI_ENABLED=false 默认关闭**: T05 L17, L87–88, L92, L322, L326, L456；T04 L148 `oi=latest_oi(...) if OI_ENABLED else None`。
- **T02b 实证**（t02b L13–20, L25）: rc=35 = Bybit `/market/time` 3/3 TLS 握手 reset by peer + Binance spot `/ping` TLS error；rc=28 = Binance fapi `/ping` 10s timeout；`data.binance.vision` 归档 CDN 200 可达。规律: live API 域全不可达，归档 CDN 可达。

**判定**: ✅ B conf 0.70 / A 起步(降级已记录) / C 三触发(三条件逐字一致) / OI_ENABLED=false 默认关闭，三方完全一致。

### (5) S2 新浪下限（2004-01-02 / 5737 bars）— ⚠️ 无冲突，但 04 须 re-probe

- **on-disk T05 (35119B) 实测 grep**: `5737` = **0 命中**；`2004-01-02` = **0 命中**。T05 L206 原文: "S2 实际起点不可复核(unreachable)，起点值 = last-known 1950（Yahoo 回填惯例），not first-verified in this env"。T05 L47/L16/L68/L463 一致 "last-known 1950（本环境 403 不可复核）"。
- **2004-01-02 出现位置**: T06 L254（tension 注，引 `_lead-notes-p1-precheck.md` 副脑 v4 第 3 点）+ Lead 交接（T05v2 closing，零落盘）。
- **5737 bars 出现位置**: 仅 Lead 交接（T05v2 closing，827782bf 发现，零落盘）—— **唯一记录**。
- **核验结论**: 无冲突。T05 自标 "not first-verified"，T06 §1.1 留 "04 前预注册写入" 位，二者不矛盾。**2004-01-02 与 5737-bar 值均为 继承(T05v2/Lead)，非 on-disk T05 实测**（on-disk T05 写 last-known 1950）。
- **04 动作**: 预注册 S2 下限 = 2004-01-02，**且须 re-probe / re-record 5737-bar 值**（provenance gap，见 §4 gap 8）。
- **2002-10-09 锚点 776.8**: 早于新浪日线起点 2004-01-02，本环境（Yahoo 403）**不可复核** → 锚点 776.8 依赖 02.5 记录 + 新浪锚点源复核，非日线值。

**判定**: ⚠️ 无硬冲突，但 5737/2004-01-02 值 provenance 悬空（仅存 T05v2 closing + T06 L254）→ 列 gap 6 + gap 8。

### (6) S3（ifzq / qfq / cap / API 起点 + 指数错位）— ✅ 一致 + ⚠️ GAP

- **ifzq qfq / 单次 cap≈2000 / API 可观测起点 2018-07-17**: T05 与 T06 表述一致（T05 L57, L223, L227, L437, L464；T06 引用同一组参数）。
- **⚠️ 指数错位（GAP，必须列）**: T05 v1 选 **`sh000300`（沪深300）**，贯穿 T05（L16, L52, L56, L60, L69, L208, L213–216, L364, L437, L464）。grep 全 03-r1 artifact: `sh000001`（上证综指）= **0 命中**（02.5 六节点 ±2% 验证用 sh000001，是跨阶段错位）。
- **04 动作**: 必须定夺主用指数（sh000300 沪深300 vs sh000001 上证综指），03-r1 统一 sh000300 但 02.5 历史验证用 sh000001。

**判定**: ✅ ifzq 参数一致；⚠️ 指数错位 = 04 开放问题（gap 5）。

---

## §3 Flag 核验（T05 审读 3 flags）

### F1 — µs 陷阱（SPOT 2025-01-01 起 = 微秒）— ✅ 未忽略（委托承接）

- **T05 原文**（F1 owner）: T05 L38 "README 明文 'The timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds'；futures 未被 README 明示改 µs → 04 须逐文件核验 fundingRateTimestamp / kline openTime 量级（13 位 = ms / 16 位 = µs）"。量级陷阱表 T05 L287–291（S1 SPOT 2025+ µs → ÷1000 反向陷阱；FUTURES 2025+ 04 逐文件核验；Coinglass 秒 → ×1000）。另见 T05 L392, L410, L454, L461。
- **T06 / T07 核验**: grep `µs|微秒|16位|13位|时间戳量级` 于 T06 / T07 = **0 命中**。即 T06/T07 **不复述** µs 陷阱，但二者均**委托** T04 §(b) B1 normalize（T06 L211 "PIT 伪代码（B1–B5）"；T07 L364 "引用 T04 §(b) B0-B6"），而 µs 陷阱正落在 B1 normalize_ts 层（T05 L454 载于 B1）。
- **判定**: ✅ T06/T07 未忽略——ts 归一化由 T05（数据管线 owner，载 µs 陷阱）+ T04 §(b) B1（PIT 归一层）承接，T06/T07 作为回测/基准设计节点正确地委托而非重复。04 动作"逐文件量级核验 13/16 位"由 T05 §6.1 / B1 + T04 §(b) 承接。

### F2 — updates/ 文件数 2 vs 3 — ✅ MEDIUM 评级不变

- **on-disk T05 (35119B) 实测**: README 口径 = **2 文件全 spot**（T05 L20, L39, L237, L240–241: `2022-08-08_kline_updates.zip` + `2022-04-21_aggregate_trade_updates.zip`，均 spot）。grep `28,558|2022-10-04` 于 T05 = **0 命中**（第 3 文件不在 on-disk T05）。
- **T05v2 GitHub API 复测**（零落盘，仅存交接/closing）: **3 文件**，含 `2022-10-04_aggregate_trade_updates.csv` 28,558B（spot）→ README 不全。**标 继承(T05v2)**。
- **判定**: ✅ 两口径（README 2 文件 / GitHub API 3 文件）**均全 spot、零 futures** → "零 futures 污染"结论不受文件数差异影响，**MEDIUM 评级不变**。04 建议以 GitHub API 为准复验文件全集（见 gap 10）。

### F3 — S2 执行阻塞（Yahoo 不可达）— ✅ 两处引用一致

- **on-disk T05 实测**: Yahoo `query1` + `query2` 均 **HTTP 403**（size 3369，返 `<title>Yahoo</title>` 的 JS/consent 壳非 JSON，2 次尝试；T05 L16, L50, L68, L204–205, L433–434）。费率页 `www.binance.com/en/fee/trade` **HTTP 000 / rc=28 TIMEOUT**（4 通道全败；T05 L19, L157, L440–441）→ 成本参数 = uncertain + 最后已知值（spot taker 0.1000% / futures 0.0500% / maker 0.0200%）+ 日期 2026-10-17（未一手核验）。
- **T05v2 变体**: Yahoo 429 "Edge: Too Many Requests"（on-disk T05 = 403，429 为 v2 复测变体；**标 继承(T05v2)**）。
- **两处引用一致**: T05 §5 / F3（历史深度探针 + 自测表）与 T06 L254（Lead 批注 S2 窗口张力）均指向同一事实: **S2 Yahoo 本环境不可达 + 04 须预注册诚实 fallback 窗口边界**。
- **判定**: ✅ 两处引用一致，04 预注册诚实 fallback（S2 下限 2004-01-02 + 锚点走新浪）。

---

## §4 gap 列表（03 → 04 未决项）

核验种子 7 项 + 补充 3 项。全部为 **03→04 开放项（drift / 待冻结 / provenance），无硬冲突**。

| # | gap | 来源 | 04 动作 |
|---|-----|------|---------|
| 1 | T01 残余 provenance 风险 | T01 | arXiv 单库两镜像，无第三方独立索引（非 arXiv 渠道）交叉验证；结论依赖 arXiv 自身。04 引用时标"单库 provenance"。 |
| 2 | T03 检索范围限定 | T03 | 仅 arXiv 公开预印本；SSRN / 付费期刊未覆盖；"funding rate" 术语歧义 = 易与 **Federal Funds Rate**（传统货币政策利率）混淆，检索已加过滤词。04 阴性结论限域于"arXiv 公开预印本"，不外推。 |
| 3 | T02 Bybit API 可达性 | T02 / T02b | t02b 预检 = 本环境不可达（rc=35 TLS reset）。B 路径条件保留（04 若无阻断网络则启用）。**Coinglass C 三触发条件 04 必须做成机械步骤**（ΔS≥+0.20 且 95% bootstrap CI 下界>0 且 ≥3 折 / 覆盖<95% 或延迟警示>5% / 月费≤$30），非人工判断。 |
| 4 | 03 提交门禁缺口 | 契约 | CLAUDE.md 要求人类 `CONFIRMED 1`（03 任务分解阶段），但 03 契约门禁当前 = **AI auditor 唯一**。→ 确认文件须呈用户（本 artifact 已呈；用户 CONFIRMED 前 04 不视为门禁闭合）。 |
| 5 | S3 指数错位 sh000300 vs sh000001 | T05 / 02.5 | 03-r1 统一 `sh000300`（沪深300），02.5 六节点 ±2% 验证用 `sh000001`（上证综指）。**04 必须定夺主用指数**并统一。 |
| 6 | S2 下限 2004-01-02 + 锚点不可复核 | T05 / T06 §1.1 | 04 预注册 S2 下限 = 2004-01-02；2002-10-09 锚点 776.8 早于新浪日线窗口，本环境（Yahoo 403）不可复核 → 锚点 776.8 依赖 02.5 记录。 |
| 7 | trial count 45 vs 120 待 04 冻结 | T06 §4.4 / T07 §4 | T06 预注册 45（04 不得事后扩家族/降 α）；T07 §4 保守 120（=45+75 cell 上限），备选 50。**04 pre-执行前冻结**一个值，不得事后改。 |
| 8 | S2 日线 5737-bar / 2004-01-02 first-verified provenance gap | T05v2（零落盘）/ T06 L254 | on-disk T05 写 "last-known 1950, not first-verified"；**5737 bars / 2004-01-02 值仅存 T05v2 closing + T06 L254**（继承，非实测）。**04 须 re-probe 或显式 re-record 该值后方可预注册 S2 下限**，否则 S2 窗口起点 provenance 悬空。 |
| 9 | T06 §8 L212 "制度分解"列作基线第 5 项 vs T07 排除 | T06 / T07 §3.7 | T06 朴素 5 集合含"制度分解"；T07 终版将其降为评估维度（非基线）+ 加入 RSI-14。04 按 T07 定夺（drift，T06 已委托 T07）。 |
| 10 | updates/ 文件数 on-disk 2 vs T05v2 3 | T05 / T05v2 | on-disk T05 = 2 文件（README）；T05v2 GitHub API = 3 文件（含 2022-10-04 csv 28,558B，零落盘）。**04 应 GitHub API 复验文件全集**；零 futures 结论两口径均成立（MEDIUM 不变）。 |

---

## §5 结论 — success_condition 逐项对照

**success_condition 原文**: "结构化任务图分解到最小执行单元且所有节点已写出 declared artifacts 并经 graph-apply 回写，接口清晰对准模块化解耦无遗漏无冲突"

| 条件子项 | 判定 | 证据 |
|----------|------|------|
| 结构化任务图分解到**最小执行单元** | ✅ | T01–T08 各为单一最小单元（一个产物 / 一个 owner 域）；T02b 为 T02 的预检子节点（Lead 内联，无独立 task JSON）。 |
| 所有节点已写出 **declared artifacts** | ✅ | T01–T07 共 7 artifact 全部在盘（§1 字节核验通过）；T08 = 本文件。0 缺失 declared artifact。 |
| 经 **graph-apply 回写** | ⏳(Commander) | task JSONs 存在（`tasks/03-r1-node-T0*.json`）；本节点 T08 JSON 由本 agent 回填（output/evidence/status=done）；graph-apply 回写由 **Commander** 执行，非本 research-worker 职责范围。 |
| **接口清晰对准** | ✅ | PIT B0-B6 → T04 §(b) 单一 owner；成本参数 → T05 唯一 owner（T05 L10）；基线 → T07 权威；OI → T02/T04/T05 三方一致（§2.4）。接口无悬空。 |
| **模块化解耦 无遗漏 无冲突** | ✅(基本) + 2 drift | 无**硬冲突**。存在 2 处 **drift**（非 conflict，均 03→04 可解）: ① 基线清单 T06 §8 vs T07 终版（T06 已委托 T07，04 以 T07 为准）；② S2 窗口 2002-10-09（锚点）vs 2004-01-02（新浪日线 first-verified）。另有 §4 共 10 项 gap（03→04 开放项 / 待冻结 / provenance）。 |

### 总体判定

- **conclusion**: **N gaps**（N = 10，见 §4；全为 03→04 开放项 / drift / provenance，**无硬冲突**）。
- **总体**: coverage proof **PASS with 10 gaps for 04** —— 03 阶段节点分解、declared artifacts、接口对准**全部达标**；残余 10 项均为 03 设计阶段**有意留待 04 冻结/执行**的开放项（drift 非 conflict），不构成 03 交付缺陷。
- **confidence**: **0.80**（扣减项: ① 2 处 drift 待 04 定夺 ② gap 8 的 5737/2004-01-02 provenance 悬空 ③ T02b 无独立 task JSON ④ graph-apply 回写尚未由 Commander 执行 ⑤ 本核验为定点 grep 非全文重读，极小概率遗漏非关键行的隐性不一致）。

### 04 行动清单（按优先级）

1. **冻结 trial count**（gap 7: 45 / 120 / 50 选一，pre-执行锁定）。
2. **定夺 S3 主用指数**（gap 5: sh000300 vs sh000001）。
3. **re-probe S2 5737-bar / 2004-01-02**（gap 8: provenance 补齐后方可预注册 S2 下限）。
4. **Coinglass C 三触发做成机械步骤**（gap 3: 非人工判断）。
5. **以 T07 终版 5 基线为准**（gap 9: 弃 T06 §8 朴素 5 集合 + "制度分解"基线身份）。
6. **µs 量级逐文件核验**（F1: 13 位 ms / 16 位 µs，T05 §6.1 + T04 §(b) B1）。
7. **GitHub API 复验 updates/ 文件全集**（gap 10: 2 vs 3）。
8. **呈用户 CONFIRMED**（gap 4: 03 提交门禁闭合前置）。
