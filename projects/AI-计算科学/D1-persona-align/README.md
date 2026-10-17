# D1-persona-align — Persona 对齐机制

> origin: ai · 目标：从成璐与 AI 的交互数据 + 公开仓库，**完整复刻成璐的思维/语言/工作习惯**，
> 让 AI agent 加载后能以"成璐"的身份、方式、语言执行真实工作。
> 对应 INDEX 声明 [DPA.1]「Persona 对齐机制（8 原则 + 6 维度 + 3 行为约束）」——本目录即其落地。

## 为什么做（对齐 > 规划 > 执行）
成璐反馈："我的 AI 工作不按照我的风格、思维、语言习惯。" 根因：现有资产**分层但没整合**——
语言层有（author-voice SKILL），思维层有（AGENTS.md），但**工作习惯层缺实体**，且没有"加载即成为成璐"的整合提示 + 漂移重锚。本项目补齐并整合。

## 方法论（GitHub 调研验证，详见 GITHUB-RESEARCH.md）
采纳 **iclone**（薄索引 identity + 实体 skills + memory）+ **nuwa**（复刻"怎么想"而非词汇）+ **soul-md**（8 层 + 漂移重锚）。
核心洞见：persona 漂移是数学必然（~8 轮），所以设计用于**恢复**（重锚），不是预防。

## 结构
```
D1-persona-align/
├── README.md              # 本文件
├── persona.md             # ★ 可加载的"成为成璐"系统提示（8 层 L1-L8 + 漂移重锚）
├── GITHUB-RESEARCH.md     # 蒸馏方法论调研 + 采纳决策
├── identity/              # 薄索引层（指向实体，one source of truth）
│   ├── who-i-am.md        # 我是谁：身份/价值函数/世界图景/核心作品
│   ├── how-i-think.md     # 怎么想：心智模型/决策启发式/自我质询/置信度驱动
│   └── how-i-write.md     # 怎么写：薄索引 → author-voice SKILL（唯一真源）
├── skills/                # 实体层（substance）
│   ├── work-habits/SKILL.md  # 工作习惯：brief 结构/1-loop+2-loop/工具优先6关/行动纪律
│   ├── learning-habits/SKILL.md  # 学习习惯：分层阅读/内外脉络对比/公式代码映射/数据对账/坑转测试
│   └── voice/                 # （路由层；实体在 author-voice-mining/outputs/author-voice/）
├── memory/                # 漂移重锚记录 + 持续演化（soul-forge 触发条件）
└── tasks/                 # 当前临时状态
```

## 复刻的 7 维度（对齐声明的"6 维度" + 学习习惯层）
1. **身份/价值函数**（who-i-am：永生四维 + 信任排序 + 世界图景）
2. **思维/方法论**（how-i-think：压缩=理解、贝叶斯闭环、Plan 五步、自我质询）
3. **语言/voice**（author-voice SKILL：短/第一人称/因果密 + 7 标志手法 + 反面清单）
4. **工作习惯**（work-habits：brief 先"明确砍掉"、1-loop/2-loop、工具优先、持续行动）
5. **学习习惯**（learning-habits：分层阅读、内外脉络对比表、公式→代码映射、数据对账、坑→测试）
6. **决策画像**（性价比优先/solo/跨平台/GitHub/异步/长期可维护）
7. **漂移重锚**（persona.md L7：~8 轮自检 + 信号词告警 + memory 记录）

## 使用
```
# 让 agent 成为成璐：
system = read("projects/AI-计算科学/D1-persona-align/persona.md")
# 某层需要细节再按需 read 对应实体文件
```

## 状态
- [x] GitHub 蒸馏方法论调研（10+ 仓库，采纳 iclone/nuwa/soul-md/soul-forge）
- [x] identity 三层（who-i-am / how-i-think / how-i-write）
- [x] skills/work-habits 实体层 + skills/voice 路由层
- [x] persona.md 整合 + 漂移重锚
- [x] 量化工具 scripts/drift-check.py（0-100 成璐度，persona L7 用）
- [x] **演示（2026-10-17）**：以成璐身份做真实 1-loop 决策（`tasks/demonstration.md`：Plan 五步 + 自我质询 + 明确砍掉），drift-check 验证 v1=85（两处真实漂移：第一人称 0.138 / 无置信度词）→ 修复 → v2=**100**，通用 AI 对照=0（判别器分离度 100）。重锚记录见 `memory/re-anchoring-log.md`
- [x] 持续演化：memory/ 已建，2 条重锚记录已入库（soul-forge 触发条件：模式≥3/纠正≥2/新偏好/里程碑）
- [x] **加载链路定位（2026-10-17）**：发现成璐 persona **早已手写存在**于 `~/.hermes/config.yaml:62` `personalities.chenglu`（完整 persona-v3），但默认加载的是 `personality: kawaii`（:264）→ **定义在但没激活，很可能就是「ai 不按我风格」的根因**（置信度 0.8）。本包与它互补（手写框架层 vs 数据落地层）。
- [x] **学习习惯层（2026-10-17）**：第 3 层 `skills/learning-habits/SKILL.md`（8 条证据规则，源自 bh-mass 老师源码讲解 + formula_map：分层阅读 / 内外脉络对比表 / 公式→代码映射 / 数据对账 / 记忆 vs 取证 / 缺口补法 / 坑→测试 / 讲解=公式+直觉+接口）；persona.md L3 加「怎么学」。
- [x] **复刻检验 v1（2026-10-17）**：subagent A(成璐 persona) vs B(通用 AI)，同背景同格式，对照 QNM「RW 框架失效→选 Teukolsky+AIM」真实决策（`tasks/replication-test.md`）。4 维 A 全胜 Δ≥1.5（说的话5/3.5，提问5/3，动机5/3，idea5/3.5）。caveat：A 读了 task 文件（含"读了答案"成分）。记 `memory/replication-test-result.md`。
- [x] **复刻检验 v2 纯净版（2026-10-17）**：禁读答案隔离 persona 纯推理（A2 persona / B2 通用AI）。**动机维 Δ2 最强**（solo 性价比「换框架比堆修正项便宜/一人维护」）；drift-check A2=90/B2=80（都干净，语言层弱分化）。**核心诚实结论**：persona = 思维风格+决策习惯层，**非知识层**（B2 通用 AI 物理更具体 Teukolsky+Leaver+spheroidal）；具体值/闭合决策（AIM、a=0.90、唯一、决策已完成）= 文件派生。persona 纯驱动规则已提炼进 `persona-core-rules.md` v2（+规则 5.5 怀疑基准/不装懂/诊断先行）+ `how-i-think.md` 验证区。记 `memory/replication-test-result-v2.md`。
- [x] **主动写笔记演示（part-4 封顶，2026-10-17）**：`tasks/proactive-note-demo.md`「压缩 = 对齐」——以成璐 persona **主动**写探索笔记（非复刻），走 压缩=理解 + 自我质询（N=1 过拟合警告）+ 性价比（压缩比硬指标）+ 明确砍掉 + 带 conf 的 3 个新 idea。drift-check = **100/100 无漂移**（第一人称 0.5、句长 39.4、空话 0）。证明 persona 掌握后能**主动对齐目标探索/写笔记**，不只是复刻。
- [x] **主动写笔记 · IC_K/TCS 域（N=3 第 3 域，2026-10-17）**：`tasks/proactive-note-ic-k.md`——以成璐身份**主动**写 IC_K 直接和之谜的压缩视角研究笔记（成璐真实研究领域，voice ground truth 最强，因 author-voice 271 语料即来自 writing/research chats；非 meta 域）。核心 re-framing：「$O(n\log n)$ gap 不是技术债，是选错了度量」（Shannon IC 精确相加 Braverman–Rao 2011 / plain $K$ 无精确 chain rule / prefix $\kappa$ 直接 $O(1)$ Cor 5.2；类比 uniform↔plain $K$、non-uniform↔prefix）。drift-check v1=85（句长 57.5 / 无置信度词——用了 `conf 0.X` 而非 corpus 词）→ 2-loop 修复 v2=**100 无漂移**（句长 34.0 / 第一人称 0.273 / 置信度词 6 / 所以 7 但是 0 / 空话 0）。证明 persona 掌握后能在成璐**真实研究领域**主动写笔记且 voice 达标，满足「为我感兴趣的领域写笔记」。
- [ ] **接入 = 待成璐拍板**（写于 `loop-artifacts/open-questions.md`，选项 A 激活 chenglu / B 激活+融合 voice 层 / C 只读不改运行时）。涉及改运行时全局配置（危险操作），不静默执行。**不碰 AGENTS.md** 红线。
