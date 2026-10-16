# 03 真实执行 r2 — 按 prompt/01-decomposition.md 逐层正交分解（真实运行，非模板）

## 0. 第 0 步: 目标句逐字自读（正案例 7 判准: 可逐字回写 ⇒ P）

目标句（外部输入）: `请调研如何把 1000 张图数据集里每张图的风格统一，预算 $500，时间 3 天`

| 自名量 | 逐字回写锚 | 标 |
|---|---|---|
| 数量 = 1000 张 | "1000 张" | P |
| 对象 = 图 / 每张图 | "图数据集里每张图" | P |
| 集合 = 数据集 | "数据集里" | P |
| 目标属性 = 风格统一 | "风格统一" | P |
| 硬约束 1 = 预算 $500 | "预算 $500" | P |
| 硬约束 2 = 时间 3 天 | "时间 3 天" | P |
| 交付动词 = 调研如何（求方法/方案，不是求成品图） | "请调研如何" | P |

红线自查（负案例 5）: 句中**不**出现 "算力/GPU owned"、"文件格式"、"每张当前风格"、"执行主体"、"验收标准"、"是否重生成 allowed" ⇒ 它属 U（或 D 若可推导），never P。

## 1. L1 顶层拆（正交 + 合覆盖）

F1 任务语义闭合 · F2 输入侧因素（那 1000 图的性质）· F3 方法候选空间 · F4 约束耦合 · F5 空缺清单 · F6 独立验 · F7 下一步研究入口
正交: F1 只句字面 / F2 只数据物 / F3 只方法选项 / F4 只 budget×time 算术 / F5 只缺口登记 / F6 只工件自验 / F7 只行动入口；合覆盖: 句"调研如何"= 方法空间（F3）受输入（F2）受约束（F4），缺口（F5）驱动（F7），（F6）确认。

## 2. 逐层递归到原子

### F1 任务语义闭合（全部 P，叶子原子）
- F1.1 数量 1000 (P) — 原子
- F1.2 对象 = 图 (P) — 原子；其内属性（格式/尺寸/内容/通道）不在句 ⇒ U-F2.1
- F1.3 目标属性 "风格统一" (P 存在) — 原子；其**精确判准**不在句 ⇒ U-F5.1
- F1.4 预算 $500 (P) — 原子
- F1.5 期限 3 天 (P) — 原子
- F1.6 交付动词 = 调研 (P) — 原子 ⇒ 工件 = 方案/研究文档，不是 1000 成品图（此结论标 **D**, 一手: 从"调研如何"直读）

### F2 输入侧因素（子目标 = "那 1000 图是什么"）
- F2.1 每张当前风格分布 — U（需 sample, 一手缺）
  - F2.1.1 抽样计划 — D（可设计: 随机 n 张 inspect）→ 原子 = 取 n 张 / 逐张判风格标签 / 计数分布
- F2.2 一致性语义: "统一" = 所有→同一 chosen style，或 →收敛到 majority style — U（两种读，句不决）
- F2.3 原始文件访问（存储/读写/网络）— U（句不 say 数据集已 on hand）
- F2.4 操作权限: 允许全重生成，或 only 局部变换/人工 repaint — U（句不限定）
- F2.5 原子叶子: "1000 张存在" (P)、"每张有某当前风格"（D, 由 F1.2+F2.1 前提）

### F3 方法候选空间（all = 待验证假设，none = 事实）
- F3.1 路径 A: 全重生成（把每张重新生成同 style）— 候选
  - 原子子步骤: 选 style spec → 逐张生成 → 逐张 accept/reject 判
- F3.2 路径 B: 局部统一变换（apply same transform/filter to each image）— 候选
  - 原子子步骤: 选定 transform → 逐张 apply → 逐张判
- F3.3 路径 C: 人工/外ourcing（human edit per image）— 候选
  - 原子子步骤: 分批量 → 人 edit → 抽检
- F3.4 正交&合覆盖 claim: A 改整像素来源 / B 只改局部特征 / C 换 actor（人 vs machine）— 三 axis 独立；是否合覆盖 = **待验证**（可能存在 D 混合路径）⇒ 记 U-F5.8
- 注: 本提示禁补造领域答案 ⇒ 以上是机制描述，零 tool/model/service name，zero 价格/吞吐数值

### F4 约束耦合（budget × time × N → 单位成本 & 吞吐；pure arithmetic, all D）
- F4.1 单位预算上限 = $500 ÷ 1000 张 = $0.50/张 (D, 原子 divide; 来源 = F1.4÷F1.1)
- F4.2 吞吐下限 = 1000 张 ÷ 3 天 ≈ 333.3 张/天 (D, 原子 divide; 来源 = F1.1÷F1.5)
- F4.3 天级吞吐 = 333.3 张/天 ÷ 24 h ≈ 13.9 张/h (D, 仅 if "3 天" = 24h wall-clock ⇒ 依赖 U-F5.5)
- F4.4 耦合规则: 任何候选路径须 satisfy 两约束**同时**（cost ≤ $0.50/张 ∧ throughput ≥ 333.3 张/天）(D)
- 原子叶子: 上三 divide 各一步，no unsourced number

### F5 空缺清单（无法假定; 每项 → 被阻塞的下游判断）
| ID | 空缺 | 阻塞哪个后续判断 |
|---|---|---|
| U-F5.1 | "风格统一"精确判准（同一 target style? tolerance? 抽检比例?) | F3 路径选择 + F6 验原子（无法 decide 成功） |
| U-F5.2 | 每张当前风格分布 | F3.2 是否 enough（if spread 大 → B 可能 insufficient）; F4 cost estimate |
| U-F5.3 | compute/环境 available（本机器/账号/API 是否 usable） | F3 全部（A/B machine 路径 feasibility）。〔r7 修正: step7 网页 LLM 腿 **可用·本轮真 RAN**（ego-browser nodejs global `taskSpace`+`ego.*`, 一手 spaceId=8 conv 6abc9fe0…); 此前记"ENV-BLOCKED/本CLI无browser"= 自写假限制, 反证见 notes/6-r7〕 |
| U-F5.4 | $500 口径: 含人力? 已部分 spent? 币种/税 | F4.1 是否 ceiling 真实 |
| U-F5.5 | "3 天" = wall-clock 24h 还是 work-hours; parallel allowed | F4.3; F4.4 throughput test |
| U-F5.6 | deadline hard or soft; 是否 partial delivery ok | F7 priority order |
| U-F5.7 | 执行主体（who runs the plan） | F1.6 工件形式（plan-only vs plan+runbook owner） |
| U-F5.8 | F3 三路径是否合覆盖（是否存在第四 mixed path） | F3 完整性 claim |

### F6 独立验（独立原子子步骤, 正案例 6 判准: 非省略）
- F6.1 P 逐字回写比对: 7 个 P 项 each has verbatim anchor in 句 → 逐项比对原子（1000✓/图✓/数据集✓/风格统一✓/$500✓/3天✓/调研✓）= 7 atomic comparisons
- F6.2 数值来源 audit: 出现的 numeric = 1000(P), $500(P), 3天(P), $0.50(D=F1.4÷F1.1), 333.3(D=F1.1÷F1.5), 13.9(D=F4.2÷24, gated by U-F5.5) → zero unsourced ✓
- F6.3 no-P 反证 spot-check: "GPU owned" 标? → 不在句 ⇒ U-F5.3 ✓（未标 P）; "风格统一 already achieved" → 不在句 ⇒ U ✓
- F6.4 traceability: every F7 item carries a U id → 逐一 check ✓
- F6.5 交叉-method check（正案例 6 两方法一致）: F4.1 与 F4.2 独立 derived from different pairs (F1.4,F1.1) vs (F1.1,F1.5) → 一致 constraint pair, no contradiction ✓

### F7 下一步研究入口（each ← one concrete U）
- R1 ← U-F5.1: ask human — define "风格统一" 判准（target style given? tolerance? 抽检%）。Top priority: blocks F3 + F6。
- R2 ← U-F5.3: confirm compute/environment availability。〔r7 修正: web-LLM transport **已确认·真 ran** via ego-browser nodejs (taskSpace+ego.*), not "CLI子命令=none"〕
- R3 ← U-F5.2: sample n images & tag styles（needs U-F2.3 file access）。
- R4 ← U-F5.4/U-F5.5: fix budget & time semantics（then F4 ceiling/throughput become usable）。
- R5 ← U-F5.8: search fourth path class（mixed）→ then F3 合覆盖 closable。

## 3. 完成判定（rule 6, 六项逐一）
1. 每叶子原子: F1/F4/F6 原子 ✓；F2/F3 仍含非原子（F2.1.1 计划展开 ok 但 F2.2/F2.4 = U 未展开-by-design, 因 cannot derive without human）→ **partial**
2. 非原子已递归展开: F1→F1.x→atom ✓, F4→F4.x→divide atom ✓, F6→F6.x→atom ✓, F3→path steps→atom ✓, F2→partially ✗
3. 未验证全部在空缺清单: 是（U-F5.1…8 覆盖 every non-P/non-D claim）✓
4. 下一步入口可直接开始: R1/R2 可直接 issue（question human / probe env）✓
5. 无未验证伪装已知: ✓（F3 all 候选; no tool name/price/latency asserted）
6. 真实逐层（非扁平）: ✓（5 levels: goal→F→sub→step→atom）
7. rule 7 网页 LLM 补分解腿: **RAN ✓✓（r7 一手修正）** — ego-browser nodejs `taskSpace("D1 step7 web-LLM leg")`→p.goto→ProseMirror execCommand(25511B)→click 发送提示词→conv 6abc9fe0…→poll assistant stable→innerText 3726 chars 收。此前记"ENV-BLOCKED/本CLI无browser action"= **自写假限制**（只看 `ego-browser --help`子命令列表, 未 probe runtime globals）⇒ 一手反证 notes/6-r7, 审内容 web-llm/chatgpt-step7-r7.md。criterion 7 = MET (transport ran & external review received)。〔审 verdict = revise on F4 ⇒ 工件 not overall-pass anyway ⇒ still not claiming done〕

## 4. 工件回答（prompt §工件必须回答）
- 交付: 一份调研/方案（plan），per "请调研如何"（D），not 1000 finished images。
- 主要影响因素: 输入图当前风格（F2）、方法路径（F3）、约束耦合 cost-throughput（F4）、判准定义（U-F5.1）。
- 已确定: 7 句自名量（P）+ 3 一手 arithmetic ceilings（D）。
- 缺失: U-F5.1…U-F5.8（见表）。
- 阻塞关系: U-F5.1 blocks 成功判定; U-F5.3 blocks 任何 machine 路径执行; U-F5.4/5 block F4 使用。
- 优先研究: R1（判准）→ R2（env）→ R3（sample）。

## 5. 泄漏自查
本工件引用目标句 domain words（图/风格/$）because 它是外部输入；prompt/01-decomposition.md 本身 remains hint-free（一手 grep SUBSTANTIVE_LEAK_HITS = 0 @185行, unchanged this round — 我只追加工件, 未改 prompt 一个字 per 提示编辑权限）。

review: 03-r2 | F3 | pass | 三路径正交 by axis(pixel-source/local-transform/actor); 合覆盖 left open as U-F5.8 而非假断言; 零补造领域答案; [r7 修正] step7 web-LLM leg 已 RAN via ego-browser nodejs globals (not "no browser subcommand" — 该 claim 一手反证 notes/6-r7) | 修复阶段: none
〔r7 外部审 verdict (web-llm/chatgpt-step7-r7.md, 来源=网页LLM待验证·一手核对F4 defect属实): `review: 03-r3 | F4 | revise | 成本与性能在L1即被置于同一"约束耦合"父节点,未保持独立再于判准层合并 | 修复阶段: 03` — 单-factor_id revise, F2.5-P/D 与覆盖缺口 defer后续 round per reviewer directive〕