origin: ai
time: 2026-09-29T00:20+08:00
stage: 03 / round: r1 / status: REFERENCE-CASE (cleaned per user rubric · ready to score)

# stage 03 参考案例（clean）= 用户本次对话的分解规范，一手落盘，待用户打分

## 0. 用户规范（逐字，本文件的唯一标准）
> "约束只有**模型**和**显存**，其余包括**成本→TCO**，以及通过**场景决定瓶颈性能 prefill/decode**，然后**显存和 KV-cache 直接可以在并发吞吐里面计算"。

=> 合法硬给定 **P 集合 = { 模型 , 显存 } 仅此两个**。所有别东西 = D（可推导）或 R/U（需研究/空缺）。
=> 本文件把那"其余"的东西 EXPLICITLY 作为推导链，so reviewer 一眼看到：nothing baked-in。

## 1. 给定账（ledger · 这是本参考的 teeth）

| 节点 | 旧 raw 工件标 | 本 clean 标 | 为什么（per 用户规范） |
|------|--------------|------------|----------------------|
| 模型身份 / 参体量(27B-class) | P | **P** ✓ | 用户给定"模型" |
| 显存(VRAM)预算/上限 | 隐含U-GAP04 | **P** ✓ | 用户给定"显存"=硬约束 |
| 具体型号架构(layer/KV-head/head-dim/vocab/MoE) | R | R | 未 given；但**只影响数值**，not 结构 |
| 权重字节 = params×bits/8 | D | **D** ✓ | 从{模型,量化}推导 |
| KV-cache = ctx × per-token-KV-bytes | D | **D** ✓ | 用户："KV 在并发吞吐里计算" |
| 显存占用 = weights+KV+overhead | D | **D** ✓ | 用户："显存…计算" |
| 并发路数 / ctx / in-out 长度 | U-GAP02 | U→(given后=D) | 是**场景**选择，once fixed ⇒ 触发D |
| 瓶颈 regime = prefill vs decode | 隐含 | **D** ✓ | 用户："通过场景决定瓶颈性能" |
| 吞吐(tok/s) | R | R→(after roofline)=D-bound | 由regime+BW推导 |
| 成本 sticker | U-GAP12 | U | market fact |
| TCO = sticker+host+energy·life+resale | D | **D** ✓ | 用户："成本→TCO" |
| 性价比 R_useful = P_useful/TCO | D | **D** ✓ | 定义推导 |

红线自验：**P 列中仅两项 ✓**（模型、显存）。zero 卡名、zero 价格数值、zero 带宽数值、zero 吞吐数值 baked-in。

## 2. 正交 L1 拆（合覆盖 · 五类不同对象两两交集空）

G = 选性价比最优硬件系统 H\* 为「个人开发者·本地·27B」，under 给定 {模型 M, 显存 V}。

| ID | 因素 | 独有职责 | 对象类别 |
|----|------|---------|---------|
| F1 | 交付对象与完成判定 | what done / output form | done-def |
| F2 | 需求约束(P侧) | 用户给条件={M,V}+未回答偏好 | given |
| F3 | 运行配置&资源占用(D侧) | 量化·ctx·并发→内存·regime | process/computed |
| F4 | 硬件候选&成本 | exists × sticker | option |
| F5 | 性价比定义·测量·选择 | R_useful·比较·argmax | criterion |

正性 witness：F3.1(量化)∈F3∉F5；F5.1(numerator def)∈F5∉F3；F2.1(显存V)∈F2∉F3。四/五类两两交集空。
合覆盖：H\*=argmax_{s∈S}R(s)，S={候选 : mem(s)≤V ∧ fits(F2平台)}，mem(s)由F3推导，R由F5 ⇒ 五合定义决策。

## 3. 推导链显式（三链 · 这就是用户"其余可推导"的具体化）

### 链A — 显存 & KV-cache 在并发吞吐里计算 [全部 D]
```
V(显存,given P)
 ├─ 可用_for_weights+KV = V − overhead(框架/激活)[R数值,D结构]
 ├─ weights(s,q) = params(M) × q_bits/8            [D ← {M,q}]
 ├─ KV(concurrency c, ctx n) = c × n × per_tok_kv  [D ← {c,n,arch}]
 │    └─ per_tok_kv = 2·n_layer·n_kv_head·head_dim·dtype_bytes  [D ← arch(R→填后D)]
 └─ 可行(c,q) iff weights+KV+overhead ≤ V          [D 判定 ← 链A自身]
      ⇒ max_concurrency(c) = floor((V−weights−overhead)/per_tok_kv/n)  [D]
```
=> 显存门槛 G_min 与并发上限都 closed-form **derived**, NOT assumed。

### 链B — 瓶颈 regime 由场景决定 [D ← 场景]
```
scenario = {交互?(TTFT敏感) | batch?, 并发 c, in/out 长度}   [U-GAP02 → 用户答后 = P-input]
 ├─ decode phase: per-token 成本 ∝ weights bytes / BW   → memory-bound  [D roofline]
 ├─ prefill phase: 一次 compute over prompt tokens       → compute-bound  [D roofline]
 ├─ regime = dominant( 1/(tok·decode_cost) , 1/prefill_cost )  [D ← scenario]
 └─ 若 interactive low-c → decode-mem-bound dominates ⇒ BW 是主 axis  [D]
    若 high-c batched   → arithmetic/aggregate shifts ⇒ capacity+BW mix  [D]
```
=> H\* 是 **regime-dependent**：结论是 derived consequence of scenario, not a named card。

### 链C — 成本 → TCO [D ← composition]
```
TCO = sticker(F4.3,R)
     + host BOM premium(F4.5, consumer vs server class)[R/D结构]
     + energy·lifetime = $/kWh × TDP·duty × yrs        [D ← {电价R,GAP05}]
     − resale(F4.6)                                      [D sign]
     × replica count(F2 SLA,U-GAP)                    [D multiplicity]
⇒ R_useful = P_useful(链B throughput × quality权重F3.1.2) / TCO  [D 定义]
```
=> 关键（我 prior meta-audit 已证）：per-token energy parity ≠ lifetime-total parity；faster card serves ~2× tokens ⇒ 总电费~2×。双derate 不 double-count。

## 4. 三态标注纪律（P 只有两 · 一切数值 R/U · 公式 D）
- **P**: F2.1.1(模型=27B-class)、F2.2(显存=V)。仅两个。
- **D**: 所有公式 & 上面三链结构 & R_useful argmax rule & robustness flip-condition。
- **R**: arch facts(GAP01)、spec sheet(GAP11)、live price(GAP12)、$ kWh(GAP15)、eval delta(GAP07)。
- **U**: 用户偏好未回答(GAP02/03/04/05/06/10)、一手实测(ENV-BLOCKED)。

## 5. 空缺清单（each → blocked judgment → 一手入口）— 数值全部 open，结构全部 closed
GAP01 arch→链A per_tok_kv; GAP02 scenario→链B regime&链A c; GAP03 budget→链C sticker; GAP04 platform→S准入; GAP05 duty-cycle→链C energy; GAP06 second-hand/resale→链C sign; GAP07 eval→R_useful weight; GAP08 calib→F3.1 feasible; GAP09 engine→F3.4; GAP10 "本地"严格?→F4.1 space; GAP11 spec→链A/B gate&roofline; GAP12 price→链C sticker; GAP13 stock→buyable; GAP14 host BOM→链C scope; GAP15 kWh/life→链C TCO; GAP16 一手throughput→链B一手(ENV-BLOCKED)。

## 6. 六问回答
- **交付**: H\* config + TCO + 依据 + 缺口标注。
- **受哪些因素**: F1–F5 五正交轴。
- **已确定条件**: ONLY {模型, 显存}（P）+ 所有公式&三链结构（D）。
- **缺失条件**: GAP01–16（all numbers/preferences）。
- **缺失阻塞**: S 空(GAP01/04/11)、regime 歧(GAP02→链B)、TCO 口径(GAP03/05/06/14/15)、一手(GAP16 ENV)。
- **下一步优先**: (1)用户问答 GAP02/03/04/05/06/10 一次对话 → 解锁链B regime+链A concurrency；(2)GAP01 arch → 锁链A per_tok_kv；(3)GAP11+12 spec+dated quote → 锁链C。

## 7. PROVENANCE 诚实边界（this decides the SCORE）
- raw 工件（tasks/03-execution-verbatim-r1.md）文本本身 **zero concrete card/price/BW/throughput**（一手 grep ✓, COUNT=2 仅 = 字词 "roofline"/"vLLM" 术语, no number）。
- BUT executor 有 live `Read/Bash` 并 pulled my `D1-gpu-research-2026/memory/04.5-r6-roofline-bound-conclusion.md`(14477 chars, concrete cards+numbers) + `notes/3-r1.md`. ⇒ **"完全-naive independent rediscovery" 假设 VIOLATED**。
- 故 raw 不能 count as Generality-evidence. Per 用户规则 "包含泄露信息 ⇒ 只能及格": here 泄露 = 间接（via FS access），text clean but provenance dirty ⇒ **self-score = 及格(pass)**, not full credit.
- **FIX for a TRUE naive probe**: sandbox executor = deny ALL filesystem except the two fed blobs; no Bash, no Read outside prompt+target; browser-only-if-allowed. Then re-run → if skeleton still matches ⇒ genuine Generality Demonstrated. (queued, ENV-stalled 03b/03c still pending.)

## 8. review 判定
`review: 03-r1 | ref | pass-with-cap | text-leak-free但provenance-contaminated(FS-read域file)⇒cap=及格 | 修复阶段: 03(sandbox re-run)`

## 下一步(precise)
- sandboxed naive re-probe（deny FS）→ 若跨-domain(B训练/C理财)+域A同schema匹配 → Generality genuine。
- 等用户打分此参考。