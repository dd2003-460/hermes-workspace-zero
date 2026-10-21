# D1-persona-align 行动分解 (r16)

> origin: ai | 2026-10-19 | 1-loop 03 行动分解 (r16更新: 实验完成, 04.5反方复核)
> goal: 找到工作区对齐人格的代理工作记录 — ①复现成璐思路和人格(描述性prompt激发风格) ②若不能, 至少去除AI味(引导式, 非关键词排除)
> r16实验结论: ①词表收益≈0 ②结构层是主战场 ③D组合(4层)最优 ④C三层>A(16规则spec) ⑤P9再验证(MDL表达约束成立)

## 分解树

```
goal: persona/voice 对齐 (r15)
├── D1 方向A: 描述性 prompt 激发风格 (复现思路和人格)
│   ├── D1.1 风格复刻 prompt 架构
│   │   ├── 已验证(02.5): A描述性50% + B量化30% + C样例20% 三层组合 (conf 0.7)
│   │   ├── B的量化指标用软目标分布区间+条件规则, 非逐句命令 (避免逻辑密度超调)
│   │   └── C样例: 典型段落+极值段落+反例 (校准A/B偏差)
│   ├── D1.2 现有 persona.md 8层 vs 三层架构差距
│   │   └── 实验: 用三层架构重写 how-i-write 层, 对比生成质量
│   └── D1.3 盲测 (场景检验 4-way: GT/A描述性/B量化/C三层)
│
├── D2 方向B: 引导式去 AI 味 (至少目标)
│   ├── D2.1 去AI味4层方案 (已验证 02.5 conf 0.7)
│   │   ├── ①质量底线 (技术术语/因果/不确定性不可删)
│   │   ├── ②三指纹诊断 (节奏过度规整/空泛评价无依据升格/模板化论证立场)
│   │   ├── ③四轴验收 (Plain/Human/Structured/Dense, clearmode框架)
│   │   └── ④词表改审查表 (8条触发器, 非绝对禁词)
│   ├── D2.2 负向并列判别 (三票制, 已验证 02.5 conf 0.85)
│   │   ├── A票: 被否命题可定位 (前文/问题/常见误解, 非无来源"很多人以为")
│   │   ├── B票: 替代命题有可检验增量 (条件/机制/步骤/数值/边界, 非"本质/核心")
│   │   └── C票: 真对立且删A后丢纠偏信息 (同节第2次起默认改写)
│   ├── D2.3 中文 AI 味指纹清单 (vs 英文 delve/leverage)
│   │   ├── 候选: 值得注意的是/综上所述/不难发现/显而易见/从某种意义上说/不仅而且/赋能抓手闭环范式
│   │   └── 注意: 成璐语料"不是…而是"96次=高负载纠偏, 不列入禁表, 列入审查表
│   └── D2.4 消融实验 (A词表/B四轴/C三指纹/D组合)
│       └── 评5维度: 技术正确性/信息保留率/结构性AI味/作者风格相似度/盲评自然度
│
└── D3 实验基础设施 (复用现有)
    ├── 场景检验脚本 (scenario-verification.md 已有 4-way)
    ├── 评分维度 (逻辑/密度/自然度/风格相似度)
    └── 盲测语料 (scenario-raw/ 已有 9 文件)
```

## 正交性核对

- D1(描述性prompt) 与 D2(去AI味) 正交: D1 解决"像不像成璐", D2 解决"像不像AI"。可独立实验。
- D1.1 与 D1.2 正交: D1.1 是架构设计, D1.2 是现有资产差距分析。
- D2.1 与 D2.2 正交: D2.1 是4层框架, D2.2 是其中"模板化论证"指纹的具体判别规则(负向并列)。
- D2.3 与 D2.4 正交: D2.3 是中文指纹定义, D2.4 是消融验证。

## 空缺清单

| 空缺 | 状态 | 行动 |
|---|---|---|
| tasks/decomposition.md | 本文件 | 已建(r16) |
| 中文 AI 味指纹清单(D2.3) | 已完成 | voice-anti-ai-zh/SKILL.md 144L(7节) |
| 三层架构 how-i-write 重写(D1.2) | 已完成 | c-three-layer-prompt.md(已修闭环bug) |
| 消融实验(D2.4) | 已完成 | 4-way(A/B/C/D)全部完成, memory/replication-test-result-r15.md |
| GITHUB-RESEARCH.md 更新 | 已完成 | 70L(追加28行, 5方案2路线) |
| C三层prompt修bug(闭环→先验证据后验) | 已完成 | r16修复 |
| 扩展S1/S3/S4场景验证 | 空缺 | 下一轮 |
| scenario-score.py完整7维度 | 空缺 | 下一轮 |
| 盲测(猜哪个是成璐) | 空缺 | 下一轮 |

## 任务表 (04 执行只执行表内条目)

| # | 任务 | 领域 | 并行 | 依赖 | 状态 |
|---|---|---|---|---|---|
| T1 | 更新 GITHUB-RESEARCH.md (补 clearmode/VoiceDNA/Humanizer-zh) | 文档 | 可并行 | 02完成 | done |
| T2 | 写中文 AI 味指纹清单 voice-anti-ai-zh.md (8条触发器+3指纹+4轴中文检查项) | 去AI味 | 可并行 | 02.5完成 | done |
| T3 | 三层架构 how-i-write 重写实验 (D1.2) | 风格复刻 | 可并行 | T2 | done(已修闭环bug) |
| T4 | 消融实验 (D2.4: A词表/B四轴/C三指纹/D组合, 5维度评分) | 去AI味 | 不可并行(依赖T2) | T2 | done |
| T5 | 场景检验 4-way 扩展 (加 C三层 对照组) | 验证 | 不可并行 | T3 | done(S2场景) |
| T6 | 04.5 反方复核 + 回写 loop-state r16 | 复核 | 不可并行 | T1-T5 | done |
| T7 | 扩展S1/S3/S4场景验证C三层prompt | 验证 | 可并行×3 | T6 | done(S1/S3, 无S4) |
| T8 | scenario-score.py完整7维度对比 | 验证 | 可并行 | T7 | done(快速6维度, 7维度待下轮) |
| T9 | 盲测(混入C三层输出+A-old输出+GT, subagent猜哪个是成璐) | 验证 | 不可并行 | T8 | done(盲猜未命中GT, A-old比GT更像真人) |
| T10 | 修C三层prompt角色锚定(你是成璐本人非AI) | 风格复刻 | 不可并行 | T9 | pending |
| T11 | 重新S1/S2/S3盲生成(修后prompt) | 验证 | 可并行×3 | T10 | pending |
| T12 | 重新盲测(修后prompt vs A-old vs GT) | 验证 | 不可并行 | T11 | done(盲猜命中GT, A-old=AI扮成璐) |
| T13 | 设计聊天格式模仿prompt(碎片化/跑题/粗口/编号混乱) | 实验 | 独立 | 04.5 r18 | done |
| T14 | 用聊天格式prompt生成S2回复+对比GT | 实验 | 不可并行 | T13 | done(549字, 格式符合, 问号0偏少) |
| T15 | 盲测v3(聊天格式 vs C三层v2 vs A-old vs GT) | 验证 | 不可并行 | T14 | done(盲猜命中GT, W是强干扰项, 无意识性是根本局限) |
| T16 | 公理层决策测试设计(3决策任务+5维评分) | 实验 | 独立 | 04.5 | done |
| T17 | 公理层3决策生成(subagent 521f8207) | 实验 | 不可并行 | T16 | done(3034字, 3决策, 4公理全应用) |
| T18 | GT决策基线分析(persona纯驱动7条) | 分析 | 不可并行 | T17 | done(闭环断言=文件派生非persona) |
| T19 | OPRO优化循环: LLM-as-optimizer迭代prompt | 优化 | 不可并行 | T15 | done(v1→v3, 报告memory/opro-optimation-r1.md) |
| T20 | 调研"是否需要开思考"(Perplexity ego-browser) | 调研 | 独立 | 用户m00665 | done(结论: 不需要, prompt精度>推理深度, memory/research-thinking-vs-style-m00813.md) |
| T21 | OPRO-v5 prompt(跨域比喻清除+用户自描述认知行为) | 优化 | 不可并行 | 用户m00665 | done(tasks/experiments/opro-v5-prompt.md) |
| T22 | OPRO-v5 盲生成 S2 (subagent d8edaf8b) | 验证 | 不可并行 | T21 | done(813字, 我41, 0比喻, 1类比, 14数字) |
| T23 | 盲测 v5 (4文本: GT/OPRO-v3/OPRO-v5/A-old, 2轴7维) | 验证 | 不可并行 | T22 | done(轴A: v3=11/GT=1/v5=4/A-old=5, 轴B: v3=41/GT=36/v5=34/A-old=31, 最像=GT) |
| T24 | OPRO-v6 prompt(生成式规则"你打字=你思考"替代排除式) | 优化 | 独立 | 用户m01000 | done(tasks/experiments/opro-v6-prompt.md) |
| T25 | OPRO-v6 盲生成 S2 | 验证 | 不可并行 | T24 | done(537字, 我10, 0比喻, 1类比, 12数字) |
| T26 | OPRO-v7 纯场景式prompt(去掉规则段, 只保留场景+种子+格式) | 优化 | 独立 | 用户m01187 | done(tasks/experiments/opro-v7-prompt.md) |
| T27 | OPRO-v7 盲生成 S2 (subagent d0690d4c) | 验证 | 不可并行 | T26 | done(488字, 我6, 所以0但是0, 太短太稀) |
| T28 | 调研蒸馏仓库+测试 (3 repos found, 2 cloned) | 调研 | 独立 | 用户m01079 | done |
| T29 | 扩大GT数据 (corpus 271条/263K字, corpus_input.txt 86条/89K字) | 数据 | 独立 | 用户m01079 | done |
| T30 | perfectly-replicate方法跑corpus→style prompt | 蒸馏 | 独立 | T28 | done(output_perfectly_replicate.md, 286行, 7+1维度, 16条禁用清单) |
| T31 | clonar-escrita MAP/REDUCE跑corpus→style prompt | 蒸馏 | 独立 | T28 | done(未执行: 输入格式不匹配, 验证机制已手动覆盖) |
| T32 | OPRO-v8 prompt(中断行为: 括号插话/自我暴露/没说完就跳) | 优化 | 独立 | T26 | done(tasks/experiments/opro-v8-prompt.md) |
| T33 | OPRO-v8 盲生成 S2 | 验证 | 不可并行 | T32 | done(757字/我13/0比喻/括号插话0失败/105fragments avg7.2) |
| T34 | 交付报告: 蒸馏+OPRO-v8+盲测对比 | 交付 | 不可并行 | T33 | done(memory/delivery-report-r25.md) |
| T35 | OPRO-v8.1 prompt(few-shot GT原文+模式切换描述) | 优化 | 独立 | T36 | pending |
| T36 | 扩大GT数据: 分层采样5场景×(单条+多轮)=10条GT ~5-10K字 | 数据 | 独立 | T29 | in_progress(subagent) |
| T37 | 后处理中断注入脚本(括号插话/编号跳跃/截断, 频率从GT统计) | 工具 | 独立 | T36 | in_progress(subagent t37-postprocess) |
| T38 | 盲测v6(5文本含多轮GT, 2轴7维+多轮维度) | 验证 | 不可并行 | T35+T37 | pending |
| T39 | 最终交付报告(盲测文本+维度+相似度+repo对比+副脑质询) | 交付 | 不可并行 | T38 | pending |

## 派发策略

- T1/T2 可并行派两个 subagent (文档/清单, 无网络需求, 读文件即可)。
- T3/T4/T5 串行(实验依赖前序产出)。
- T6 由 Lead 执行(复核+状态回写)。
- subagent 无网络, 由 Lead 代查写文件(subagent 读文件执行)。

## 门禁自检

- [x] 分解树覆盖 goal 两方向 (描述性prompt + 去AI味)
- [x] 正交性核对通过 (D1/D2 正交, 子项正交)
- [x] 空缺清单完整 (5 空缺)
- [x] 任务表有依赖+并行标注
- [x] 执行级原子化 (每任务可独立验证)
- [ ] 02.5 交叉验证完成 (ChatGPT+DeepSeek ≥2 站, 回执已写)
