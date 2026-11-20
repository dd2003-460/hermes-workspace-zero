# K^t 压缩-泛化框架 v1
# origin: ai（D 驱动推导 S27-S33，2026-11-21）
# 状态：v1.1 canonical 版（v1.1 = 补条件集 C schema，T8）。操作规则见 ~/.hermes/rules/hierarchy-analysis.md 推论 5（本文是推导源，规则是操作导出）。
# 实证锚：T53b gpu 域 5run 全量 L3/L4=1584 实测（11 模式 / 144x / 信息密度 0.7%）。

## 准则（一条，其余全是它的导出）

**模型的任务 = 在信息完整性约束下 tradeoff 压缩程度；唯一正和的信息来源是新信息 C'。**

- "信息完整性"由目标函数定义为一组正交维度（每维度有机判判据）。
- "压缩程度"用 K^t 量化（Kolmogorov 复杂度 + 有限时间解码约束）。
- "新信息 C'" = 新观测/新条件，是唯一的信息增量入口（H(结论|定律,C')=0，结论本身不携带新信息）。

## 正交树（四分支；分支内条目是准则的导出，不是并列条款——每分支标注它导出自准则的哪一部分）

### I. 压缩域 —— 已有信息，零和 tradeoff
*导出自：准则的"tradeoff 压缩程度"必须可量化、有边界，否则"压缩"不可操作。*

1. **K^t 量化**：K(x) = 生成 x 的最短程序长度（不可计算，用"规则原子数"近似）；K^t(x) = t 步内可解码的最短描述（t→∞ 时 K^t→K）；Pareto 前沿 min α·K^t(x) + β·t（α=验证成本/节点，β=解码成本/次）。
2. **直积结构**：解空间 = 推理结构 ⊗ 实例空间（两因子正交，不平铺）。把 A⊗B 平铺成枚举 A1B1…A11B50 = 反压缩（T53b 实测：1584 节点 ≈ 11 模式 × ~50 实体，中 K^t=565 贴笛卡尔积上界 675）。
3. **推理/计算分离**：LLM 只产效率函数 f(H)（推理产物 K≈14 原子 = 11 函数 + 3 微架构经验系数）；实例化 = 脚本确定性计算（读参数表求值+排序，β≈0）；卡参数表 = 外部数据（K=0，非推理产物）。Pareto 前沿推到左端：K^t≈K（函数描述），t≈0（脚本求值）。
4. **条件集 C（可复用性边界）**：f(H) 附带前提条件集 C（推导时隐含假设：mtp=off、单卡、BF16…）。C' vs C 一致性检验（= 因果推断 transportability + 可迁移学习 distribution shift）：C'⊇C → 直接复用（K^t≈K, t≈0）；有交集不包含 → covariate shift（参数变、骨架不变 → 修正参数、骨架复用）；不兼容 → concept drift（函数本身变 → 重新推导）。

### II. 泛化域 —— 新信息，正和
*导出自：准则的"唯一正和的是新信息"需要说清新信息从哪来、怎么产生。*

5. **解压 = 泛化**：K^t/压缩/损失只覆盖已有信息的 rate-distortion（Shannon source coding：信息已存在，问题是表达效率）。泛化 = 用数学/物理工具在新条件 C' 下展开隐含信息，再压缩成新结论（信息不存在 → inference + compression）。循环：压缩（K^t）→ 条件判断（C' vs C）→ 解压（数学/物理工具）→ 分场景 tradeoff（不同 C' 展开深度不同）→ 压缩成新结论。
6. **新信息在 C' 本身**：给定定律 + C'，结论被唯一决定，H(结论|定律,C')=0。泛化 = 信息转移：把 (压缩定律, 新条件) 里蕴含但未显式写出的结论推导出来再压缩落盘，不是无中生有。"数学和物理可以预测世界" = 定律是压缩描述，预测 = 对压缩描述的确定性执行。
7. **工具选择 = 唯一非确定性判断点**：哪个定律适用 C'（元层决策）+ 有效性判断（定律在 C' 下是否成立，= I.4 的 C' vs C 检验；不成立则展开出的"新结论"是错误外推不是泛化，对应 transportability 的 structural equations 前提）。LLM 边界：定律选择 + 有效性判断；展开计算（代入参数/算数值）全给脚本（β≈0）。

### III. 目标函数 —— 两域的上游
*导出自：准则的"信息完整性"不自明，必须由目标函数定义，且完整性本身需要判据防退化。*

8. **目标函数 → K 下界 → K^t 前沿 → 最优点**：K 下界不是固定量——"最短不可压缩描述"短到什么程度取决于拿描述干什么。目标函数在最上游，没有它 K 下界无从定义、tradeoff 无从做。
9. **正交 + 完备 = 防退化**：不正交则 tradeoff 退化成"只追求压缩"——压缩容易量化（节点数/bit 数），完整性难量化（没有单一数字），不正交时优化器会找便宜的轴刷指标。正交维度把完整性拆成可独立机判的轴：覆盖 / 可靠 / 新鲜 / 适用条件域。缺维度 = K 下界本身错 = tradeoff 在错误空间优化（缺"新鲜度"→ 工程结果压成纯理论；缺"复用次数"→ 科研结果压成一次性）。
10. **研究级 vs 工程级**：科研结果（复用多次、要可靠）→ K 下界 = 公式 + 可验证证明（极度压缩，复用摊薄验证成本，t 可大）；工程结果（贴合实测、要最新）→ K 下界 = 公式 + 实测修正因子（mtp 等特性改算力/带宽 tradeoff 比例，纯理论偏，K 下界必须含实测校准项）。
11. **拆分是阶段性目标（S33）**：目标函数的正交拆分是阶段性手段，终点是研究级完备（"充分到方便优化"）——拆分不是终点，"完备到可以开始优化"才是。阶段性拆分允许不完整（缺口标 [待核验]），但完备性判据（9）始终在，防止阶段性被当成终点。

### IV. 测量口径 —— 操作化
*导出自：准则的量化需要统一测量口径，否则跨版本/跨臂对比不可比。*

12. **信息密度 = 独立推理模式数（K^t 口径）**，不是裸节点数（T53b：11 vs 1584）。Δ 对比在 K^t 口径下才公平——节点数差异只是展开量差异，推理模式数差异才是推理深度差异。
13. **正交维度机判判据**：覆盖（K^t 模式覆盖 vs gold 树）、可靠（验证通过率）、新鲜（条件域漂移检测）、适用条件域（C 集标注完备性）。每轴独立判，不合成单一分数（合成 = 丢正交性 = 9 的退化）。
14. **新鲜度 = 条件域漂移检测**：mtp 发布 → C 变 → 缓存 f(H) 自动失效。

## 条件集 C schema（T8，v1.1 补）

```json
{
  "func_id": "throughput_eff",
  "func_form": "f(H) = base_eff × bw_util × compute_util",
  "conditions": [
    {"name": "mtp",        "value": "off",      "type": "config",   "source": "explicit_param", "sensitivity": "concept",   "drift_sensitive": true},
    {"name": "precision",  "value": "bf16",     "type": "config",   "source": "explicit_param", "sensitivity": "covariate", "drift_sensitive": false},
    {"name": "topology",   "value": "single_gpu", "type": "hardware", "source": "derived",      "sensitivity": "concept",   "drift_sensitive": true},
    {"name": "model_type", "value": "dense",    "type": "workload", "source": "explicit_param", "sensitivity": "covariate", "drift_sensitive": false}
  ],
  "derived_from": "T53b gpu r01-r05",
  "observed_at": "2026-11-21T03:00+08:00"
}
```

字段判据：
- **type**：config（软件配置）/ hardware（硬件形态）/ workload（负载类型）。
- **source**：explicit_param（推导时显式给定）/ derived（从其他条件推出）/ assumed（隐含假设，未显式声明——**unknown unknowns 的主要来源**，推导后必须回填）。
- **sensitivity**：该条件变化时函数怎么变——`concept`（函数结构变，concept drift → 重推）/ `covariate`（只改参数，骨架复用）/ `inert`（不影响）。这是 C' vs C 三分类的机判依据：C' 里某条件值 ≠ C 里对应值 → 查 sensitivity：concept → 重推；covariate → 修正参数；inert → 忽略。C' 有 C 没有的条件 → 新维度，默认按 concept 处理（保守，防错误外推），标 [待标定]。
- **drift_sensitive**：该条件是否随时间漂移（mtp 发布/新硬件上市 → true）。新鲜度检测 = 只扫 drift_sensitive=true 的条件（IV.14 的操作化）。

最小完备性检验：一个 f(H) 的 C 集缺条件 = 该条件被隐含假设了但没声明 = unknown unknown。检验方法：换一个该条件的值重推，若函数结构变而 C 集没标 → C 集不完备，补条件。

## 已知缺口（诚实标注）

- **因果验证**：judge 给相关性判断，transportability 检验需要因果结构（do 操作 vs 观察变量），需要因果图基础设施 [待展开]
- **微架构效率缺口**：系统模型有 Roofline（带宽×算力），无 SM 级效率 [待调研]
- **K 下界 14 原子是 5-run 实测**，62-run 全量复测待做 [T53b D1]
- ~~**条件集 C 的 schema** 未定~~ **已定（v1.1，T8）**：见上节。待验证：62-run 数据上回填 C 集，检验最小完备性

## 版本记录

- **v1（2026-11-21）**：S27（K^t 量化）→ S28（直积+推理/计算分离）→ S29（目标函数=K 下界定义）→ S30（条件集 C）→ S31（压缩域 vs 泛化域）→ S32（目标函数=完整性约束、正交防退化）→ S33（版本化+拆分是阶段性目标）。
- **v1.1（2026-11-21）**：补条件集 C schema（T8）：字段判据（type/source/sensitivity/drift_sensitive）+ C' vs C 三分类机判规则 + 最小完备性检验。待 62-run 数据回填验证。
- 推导过程（D 原话 + 我的错误 + 修正）：`objfunc-signal-log.md` S27-S33。
- 操作规则导出：`~/.hermes/rules/hierarchy-analysis.md` 推论 4-5。
- 实证数据：`pfb/tasks/T53-bus/anomaly-watchlist.md`（K^t 指标节）。
