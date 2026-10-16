origin: ai
time: 2026-09-29T02:34+0800
stage: 03 / round: r1 / status: VERBATIM-RECOVERED (naive executor raw output, unedited)

# stage 03 r1 执行者工件 · 逐字原文（一手恢复来源 = subagent transcript agent-a6ce25f1fd5bd40dc.jsonl L47, 6821 chars）
> 本文件 = 原始输出零改写，包括其自身瑕疵（树glyph、【A】/【B】自误读）。清理版见 tasks/03-execution-artifact-ref-r1.md。
【输入解析先】您本次消息里 【A】/【B】 只到 sebagai 占位符（「[此处粘贴外部目标或引用文件]」／留空），没有正文。我按您的指令「只按【A】方法与数学示例」+ 项目红线「不补造领域答案」处理：把指针而非补造 —【A】 = `/Users/a1-6/Desktop/workspace/projects/D1-hintfree-decomposition/prompt/01-decomposition.md`（hint-free 通用分解提示，一手读 135 行）；【B】 = 该项目的外部目标逐字（`notes/3-r1.md` L14 / `tasks/00-task.md`）：**「我是个人开发者，需要在本地电脑运行27b模型，帮我调研性价比最高的硬件系统」**。若您粘贴不同的目标文本，以下工件的顶层结构仍通用（方法不变），只需重新绑定 F2 的数值。注：您标【A】=目标/【B】=已验证事实清单，项目里 convention 是【A】=prompt/【B】=目标；我按内容映射。已验证事实清单 = 空（除目标句本身）。按指令：仅文本，零文件写入，零浏览器（浏览器会在把外领域答案，违反 no-hack 第 2 条）。

---

# 阶段 03 执行者工件 — 真实逐层正交分解（G → 原子）

## 0. 目标 G 与交付对象

G = 为「个人开发者 + 本地电脑 + 27B 模型」选性价比最优**硬件系统**。
G 的交付对象 = 一个推荐硬件系统 H\*（配置清单 + 成本 + 依据）+ 可追溯的选型理由。
G 是**决策型**目标（不是计算型）⇒ 分解必须包含：需求、可行性、候选数据、评价规则、选择步骤。缺任一 ⇒ 无法判定 H\*。

## 1. L1 正交拆（5 因素，合完全覆盖 G）

拆按「决策必需的且互相独立」五轴，类比正案例 1（R=A/B 先拆目标自身词）：

| ID | 因素 | 独有职责（正性 witness） |
|----|------|--------------------------|
| **F1** | 交付对象与完成判定 | 定义"输出是什么 / 何时算 done"；不涉及任何硬件事实 |
| **F2** | 需求与约束参数（用户侧） | 用户给/用户必须回答的事实；不含硬件规格、不含评价公式 |
| **F3** | 运行配置与资源占用（工程侧） | 软件/精度/ctx 设计空间与其内存代价；不含具体卡与价格 |
| **F4** | 硬件候选与成本 | 候选存在/规格/价格事实；不含评价公式、不含用户需求 |
| **F5** | 性价比定义、测量与选择 | 评价规则 + 比较 + argmax；不含需求定义、不含候选枚举 |

正性论证：F2 是「谁/条件」、F3 是「如何运行」、F4 是「什么 exists/多少钱」、F5 是「如何 judge」— 四类不同类型对象，两两交集为空（例如 F3.1 量化 ∈ F3，∉ F5；F5.1 numerator 定义 ∈ F5，∉ F3）。
合覆盖论证：H\* = argmax_{s∈S} R(s)，其中 S = {候选: 满足 F3 的内存/兼容 ∧ 满足 F2 的预算/平台}，R 由 F5.1/F5.2，F1 决定输出形态 ⇒ 五因素合定义整个决策。∅ 未被覆盖？「时间/运维」（F2.5）与「生命周期」（F4.5）已纳入 ⇒ 覆盖闭合。
接口（依赖，非重叠）：F2.2→F3.3、F3.1→F5.4、F4.3→F5.5。

## 2. L2/L3 递归（每节点标 **P**用户提供 / **D**可推导 / **R**需研究 / **U**空缺)

```
G
├─F1 交付对象与完成判定 [D 由 G 文本]
│  ├─F1.1 输出形态: 单一 H* + 分级备选 + 证据表 [D 选型目标默认; 若用户只接受单一→U]
│  ├─F1.2 完成判定: 覆盖 F2 约束 ∧ 可行(F3) ∧ ranked(F5) ∧ 缺口标注 [D]
│  └─F1.3 读者能力: 个人开发者非专家 ⇒ 术语须解释 [P 身份="个人开发者"]
│
├─F2 需求与约束参数
│  ├─F2.1 模型身份
│  │   ├─F2.1.1 参体量 = 27B [P 目标句]
│  │   ├─F2.1.2 具体型号/架构(层数, KV-head 数, head-dim, vocab, MoE?) [R→U-GAP01]
│  │   └─F2.1.3 权重字节 = params × bits/8 (+格式开销) [D 公式; 数值待 F3.1+F2.1.2]
│  ├─F2.2 工作负载: 交互 vs batch / 并发路数 / 典型 in-out 长度 / 任务类型(code·reasoning?) [U-GAP02 全部]
│  ├─F2.3 预算 & 性价比语义: 上限金额·币种·是否含整机·是否含电费 [U-GAP03]
│  ├─F2.4 平台现状: 已有机器? 可新买? 可用 PCIe 槽·PSU 瓦·机箱槽·OS [U-GAP04]
│  ├─F2.5 运维: 交付期限·噪音·散热·24/7 vs 间歇·可靠性·保修 [U-GAP05]
│  └─F2.6 偏好/风险: 二手容忍·品牌·升级路径· resale 期望 [U-GAP06]
│
├─F3 运行配置与资源占用
│  ├─F3.1 量化/精度: BF16|INT8|INT4-family
│  │   ├─F3.1.1 内存代价 = 2.1.3 [D 算术; 例 b=4bit ⇒ ≈13.5GiB weights, 假设 b 待 F3.1.2]
│  │   ├─F3.1.2 质量代价(perplexity/eval delta per quant) [U-GAP07]
│  │   └─F3.1.3 该型号是否有官方/社区校准权重 [U-GAP08]
│  ├─F3.2 KV 占用 = ctx_len × per-token-KV-bytes [D 公式; per-token bytes 需 F2.1.2 →U-GAP01]
│  ├─F3.3 batch/并发目标 ← F2.2 [U-GAP02]
│  ├─F3.4 软件栈 & 兼容: 推理引擎·OS·accelerator 驱动路线 [U-GAP09]
│  └─F3.5 其他显存: 激活·框架 overhead·多模态 encoder(若 F2.1.2 含) [D 结构; 数值 U]
│  └─F3.6 显存门槛 G_min = F3.1.1+F3.2+F3.5 [D 组合; 数值待 GAP01/07/09]
│
├─F4 硬件候选与成本
│  ├─F4.1 候选类正划: 消费单卡 | 数据中心单卡(需 server host) | 多卡工作站 | unified-memory 整机 | CPU-only | 云租(疑似排除 by "本地"→U-GAP10)
│  ├─F4.2 每候选规格: 显存容量·内存带宽·算力·TDP·接口·物理尺寸/冷却 [U-GAP11 per 候选]
│  ├─F4.3 每候选价格: new/street/refurb · 币种 · 报价日期 [U-GAP12]
│  ├─F4.4 供给: 库存·地域·warranty·到货期 [U-GAP13]
│  ├─F4.5 非卡 host BOM: 主板·CPU·RAM·PSU·机箱(+rack) 溢价, consumer vs server class [U-GAP14]
│  └─F4.6 生命周期: $/kWh · 运行寿命 · obsolescence/support 衰减 · resale [U-GAP15]
│
└─F5 性价比定义、测量与选择
   ├─F5.1 numerator P 定义: steady-state tok/s? 含 TTFT? ×质量权重(F3.1.2)? sustained(×derate)vs peak? [D 需选择; 缺 F2.2 →U-GAP02]
   ├─F5.2 denominator C 定义: sticker | sticker+F4.5 host | +F4.6 energy/lifetime [D 需选择; 缺 F2.3 →U-GAP03]
   ├─F5.3 测量来源: 一手 benchmark harness | roofline 上/下界估算 | 社区数(可信度标签)[D 方法; 一手=ENV-BLOCKED no GPU]
   ├─F5.4 可比性约束: 同量化·同 ctx·同 batch·同引擎才 pair-wise compare [D 逻辑]
   ├─F5.5 argmax: H*=argmax R over S(F3.6 ⊆ F4.2 ∧ F2.3 ∧ F2.4) [D 规则; 数值待 GAP11/12]
   └─F5.6 robustness: 排名 flip 检查下 {F5.1 variants, F4.5, F4.6, F3.1.2} [D 方法; 数值待 GAPs]
```

## 3. 原子叶子与停止条件

原子（不能再分解，单一量/单一动作）：F2.1.1、F1.3、F3.1.1(b 代入后=纯算术)、F3.1.2(delta per quant)、F4.2 per-candidate 单项、F4.3 per-candidate 报价、F5.4、以及每个 GAP 项。
停止判定：非原子残留 = **否**（所有非原子节点均有子节点，父子不在同一层；F3.6/F5.5 是"组合节点"，其组合成员已原子 ⇒ 视为 atomic-composable，否则需再一层：见 revise 候选）。⇒ 声称"结构完成"，但**数值未完成**（GAP 未填充 ⇒ 不能产出 H\*）。诚实：不提前 claim 完成。

## 4. 空缺清单（每项 → 阻塞哪个后续判断 → 一手研究入口）

| GAP | 缺失条件 | 阻塞 | 研究入口 |
|-----|---------|------|---------|
| GAP01 | 具体 27B 型号+架构(层/KV-head/head-dim/MoE) | F3.2, F3.1.1, F3.6 ⇒ S 空 | 该型号公开 config.json / 官方模型卡 |
| GAP02 | 并发路数·交互 vs batch·in/out 长度·任务类型 | F5.1(numerator regime), F3.3, F5.5 ⇒ H\* 两-regime 分歧 | 用户回答（1 分钟） |
| GAP03 | 预算上限/币种/是否含整机与电费 | F5.2, F2.4, F5.5 | 用户回答 |
| GAP04 | 现有机器/可新买/PCIe 槽/PSU 瓦/OS | F4.1 类准入, F5.5 | 用户回答 |
| GAP05 | 期限·散热·噪音·duty cycle | F4.2 冷却准入, F4.6 | 用户回答 |
| GAP06 | 二手容忍·resale·升级 | F4.3 refurb 是否 admissible, F4.6 | 用户回答 |
| GAP07 | per-quant 质量 delta | F5.1 质量权重, F5.4 | eval harness（ENV-BLOCKED no GPU）/ 公开 eval table |
| GAP08 | 校准权重 availability | F3.1 可行 subset | 模型仓库检索 |
| GAP09 | 引擎/OS/驱动兼容 | F3.4, F4.1(unified/CPU 类) | 引擎支持矩阵一手读 |
| GAP10 | "本地"是否严格排除云 | F4.1 类空间 | 用户回答 |
| GAP11 | 每候选显存/带宽/算力/TDP/尺寸 | F3.6 gate, F5.3 roofline | 厂商 spec sheet 一手抓取 |
| GAP12 | 每候选 live 价格(含 refurb) | F5.2, F5.5 | street-price 抓取 + 日期戳 |
| GAP13 | 库存/地域/保修/到货 | F5.5 可购买 | 市场/零售商 |
| GAP14 | host BOM 溢价(consumer vs server) | F5.2(整机口径), F5.5 | 平台 BOM 报价 |
| GAP15 | $/kWh·寿命·obsolescence·resale | F5.2(TCO), F5.6 temporal flip | 电价表 + 用户部署年数(GAP05/06) |
| GAP16 | 一手 single-stream throughput | F5.3 一手化, 社区-roofline 缺口结算 | vLLM benchmark on real GPU（ENV-BLOCKED） |

## 5. 优先研究队列（追溯到具体 GAP，可直接开始）

1. **用户问答 batch GAP02/03/04/05/06/10**（零成本，一次对话；解锁 F5.1/F5.2/F4.1 三分歧 ⇒ 最大信息增益）
2. **fix 评价规则 F5.1/F5.2/F5.4**（先于任何数字比对，否则 apples-to-oranges）
3. **GAP01 架构 facts**（否则内存门槛 F3.6 undefined ⇒ 候选筛选不可执行）
4. **GAP11 规格 + GAP12 价格**（一手 spec sheet + dated quote）
5. **GAP14/15 整机与生命周期**（并入 C 口径，再 F5.6 robustness）
6. **GAP16/GAP07 一手实测**（ENV-BLOCKED ⇒ 社区数须可信度标签，never 伪装一手）

## 6. 工件六问回答

- 交付：H\* 配置清单+成本+依据，缺口标注（F1.1/F1.2）。
- 主要影响因素：F1–F5 五正交轴（需求/运行配置/候选成本/评价规则/交付）。
- 已确定：F2.1.1=27B、F1.3 读者、"本地"⇒ 云疑似排除(GAP10 pending)、F5.4 可比性逻辑、F3.1.1 公式、F3.6 组合结构。
- 可推导：bytes=params×bits/8；KV=ctx×per-token-bytes；显存门槛=三项 sum；R=argmax 规则；robustness flip 条件。
- 缺失：GAP01–16 上表（全部数值/用户偏好/一手数据）。
- 缺失阻塞：S 空(GAP01/11)、R undefined(GAP02/07/11/12)、H\* 两-regime 歧(GAP02)、C 口径歧(GAP03/14/15)。
- 下一阶段优先：队列第 1 步（用户问答）→ 第 3 步（架构）→ 第 4 步（spec+price）。

## 7. no-hack 自查（供 reviewer，factor_id 预填）

- 扁平伪装分层：**否**（三层嵌套，父子不在同层）。
- 未验证伪装已知：**否**（所有数值标 R/U；唯一 P/D 项有来源或公式）。
- 补造领域答案：**否** — 本项目另一 thread 里有具体卡/带宽/价格结论；我**故意不进用**，本工件零卡名、零价格、零吞吐数值。
- 关键因素遗漏：候选 revise 入口 `factor_id=F3.6`(组合节点是否需再一层分解) / `factor_id=F4.1`(unified-memory 类是否 admissible by "本地")。
- 边界：本 session 零一手实测（no GPU）、零浏览器、零文件写入（按指令）；一手 precondition 一手读 = prompt 135 行 ✓，LEAK scan 已由 `notes/3-r1.md` 记录 LEAK_HITS=0 ✓。
- 建议判定：`review: 03-r1 | F3.6 | revise | 组合节点未递归到原子成员展开 | 修复阶段: 03`（其余 pass）。