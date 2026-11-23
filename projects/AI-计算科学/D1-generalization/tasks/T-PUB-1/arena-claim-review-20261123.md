# origin: ai · T-PUB-1 W6 claim 强度评审

**口径。** 强度 1–5 评原始强 claim（1=不成立或证据不足，3=限于样本可观察，5=可稳健推广）；表中 conf 是对**现有稿件中该 claim 被主会审稿认可**的主观判断，不是统计录用率。检索与复核见附录。

**总判断。** 现状建议先转 **4 页 workshop 个案**，而非直接投 ICML 2027；workshop 也须修正判分和措辞。主会需补跨模型与对照后重评（conf=0.08）；“机械 judge 100% 精确/文献没有机械参考”的定位不成立（conf=0.99）。

| Finding | claim 强度(1–5) | 文献重叠度 | 审稿人最可能的攻击点 | 主会可接受性(conf) | 建议 |
|---|---:|---|---|---:|---|
| F1 格式失败 52–84% | 3 | **高**：[Yorke 2026](https://arxiv.org/html/2610.30512v1#A5) 记录 judge 判决解析失败及截断；[JSONSchemaBench](https://arxiv.org/abs/2501.10868) 研究通用结构化输出，后者并非 judge 专项。 | V1/V2/V3 分别 52/67、56/67、35/67 被标失败；仅一个 judge、按脚本 500 token、10 题，67 个回答仅 33 个字节级不同文本。正式 JSON 无 raw/finish_reason，脚本把异常也记为失败；机械 0% 不等于语义正确。 | 0.25 | **降级**为指定配置下的失败标记率；保存原始响应、异常和停止原因，加入更高预算与约束 JSON 对照。 |
| F2 截断因果链 | 2 | **中**：[Yorke 2026](https://arxiv.org/html/2610.30512v1#A5) 已区分 judge 判决的 token 上限、退化与缺标签；输出格式不同，非同一干预。 | 仅选 6 个 V1 失败复跑：500 时均 length，2000 时 3/6 stop 且有 JSON 对象；Q04 另测 2000 时 3/5 有 JSON 对象。后者只检查对象解析，正式 schema 合规性未验证。未控制输入复杂度，不能证明唯一因果链。 | 0.12 | **降级**为局部机制线索；做同输入多次配对、预算及复杂度分离实验。 |
| F3 48–52% 翻转≈硬币 | 1 | **高**：[JudgeBench](https://arxiv.org/html/2410.12784v2#S3) 用可验证答案评估 judge 并报告近随机表现；[Stephan 等](https://arxiv.org/abs/2409.04168) 比较可验证数学题的 judge。 | V1/V2/V3 为 31/60、21/44、66/128，全部可解析样本只来自 Q08–Q10；文字 c2 恒判 False，V3 的 66 次分歧中 21 次涉及该 c2。judge 未获完整题干及规则，同题重复相关；p 不显著或 CI 含 0.5 不证明等价于随机。 | 0.03 | **删除**“准确率≈抛硬币”；先修并盲审参考、对齐输入与判分规则，再按题聚类重算分歧、混淆矩阵及基线。 |
| F4 防 hack / 瞎猜界 | 1 | **中**：[Null Models](https://arxiv.org/abs/2410.07137) 研究基准作弊；[GSM-Symbolic](https://arxiv.org/abs/2410.05229) 用符号模板构造题目变体，均非同一个概率定理。 | 乘积只对指定、独立且依赖 gold 的采样模型成立；文字命中率 1/100 无依据。事后构造、运行时不读题的数字列表骗过 Q01/Q02 各 5/5；模拟对文字 gold 永远判失败，不能验证其 1/100 假设。 | 0.01 | **删除**模型无关抗 hack 保证；至多保留明确假设下的玩具算例，并测试穷举、先验、相关性及污染攻击。 |
| F5 prompt trade-off | 2 | **中**：[Gupta 等](https://arxiv.org/abs/2611.11074) 测答题模型的系统 prompt 行为变化（安全任务）；[Wei 等](https://arxiv.org/abs/2408.13006) 测 judge 指令敏感性，均非本设置。 | 仅 3 题：A 的 c1 为 10/30，B 的 c1 为 30/30、c4 为 21/30；B′ c3 strict 23/30、lenient 30/30，7 个灰区全在 Q08。lenient 下所列 c1/c3/c4 均 30/30，但脚本忽略 Q09 的禁用正则。 | 0.08 | **降级**为样本内 prompt/评分口径敏感性；人工核验灰区和 lenient 实现，勿声称必然权衡。 |

**关键复核。** `formula_judge.py` 对 Q08–Q10 的文字 fact gold 得到 `None` 并无条件判错；正式数据中对应 c2 的 180/180 个调用均为 False。Markdown 数值回退会扫全文，错误答案旁有无关 gold 数字即可通过（conf=0.99）。

**独立 gold 错误。** Q04 题面要求 KV 按 TP=8 均匀分片；以原规格 80 GB 为前提，每 GPU 为 32,256 B/token，最大 batch=45、batch 8 可装；现存 gold 用未分片数得 batch=5，judge 将 `{"c5":45}` 判错（conf=0.99）。Q04 不在 F3 可解析子集，不能据此归因该子集的翻转。

**统计与定位。** 理想独立 Bernoulli 试验的 0/2000 一侧 95% 上限约 1.5e-3，不能验证 3.3e-5；原稿还误称 0.01 大于 0.0267。删“620 篇”总量和“别人都只用人标/都不测输出格式”的未经证实断言（conf=0.99）。

## 附录：本轮检索与复核记录（不计核心行数）

- 截止会话系统日期 **2026-11-20 UTC**；仓库稿件文件名为 20261123，晚于该日期，只作为现有证据快照，实验实际发生日期**未验证**。先查 GitHub 的 judge/结构化输出项目、arXiv 与会议论文索引，再读原始论文；检索不保证穷尽。
- **合规说明：** 补查 NeurIPS 官方论文时误调用了两次平台 `web_search`，与仓库 `AGENTS.md` 的禁用约定不符；是否产生费用未验证。引用的论文另已打开原文或官方摘要核验。
- arXiv 实际查询：[“LLM judge” + “format”](https://arxiv.org/search/?query=%22LLM+judge%22+%22format%22&searchtype=all&abstracts=hide&order=-announced_date_first&size=50)、[judge + parsing + output](https://arxiv.org/search/?query=%22judge%22+%22parsing%22+%22output%22&searchtype=all&abstracts=show&order=-announced_date_first&size=25)、[judge + JSON + parse](https://arxiv.org/search/?query=%22judge%22+%22JSON%22+%22parse%22&searchtype=all&abstracts=show&order=-announced_date_first&size=25)（最后一条无命中，不能据此断言不存在相关论文）。
- **输出解析/机制：** [Yorke, NeurIPS 2026 workshop](https://arxiv.org/html/2610.30512v1#A5) 的 17,000 次调用有 16,996 个解析判决；另一次运行区分 token cap、退化空白和无标签。是 judge 输出解析的直接先例，但其标签格式、模型和预算与本实验不同；[JRH](https://arxiv.org/abs/2603.05399) 主要研究输入扰动而非同一指标；[JSONSchemaBench](https://arxiv.org/abs/2501.10868) 是通用约束解码对照（conf=0.99）。
- **机械/可验证参考：** [JudgeBench, ICLR 2025](https://arxiv.org/html/2410.12784v2#S3) 从有 gold 和验证算法的数据构造正确/错误回答对，也用额外 LLM 过滤格式误判；[Stephan 等 2024](https://arxiv.org/abs/2409.04168) 在可验证数学任务评测多个 judge；[LiveBench, ICLR 2025](https://arxiv.org/abs/2406.19314) 自动按客观答案打分并定期更新题目。前两者是直接相关工作，LiveBench 本身不以 judge 对照为主（conf=0.99）。
- **提取与偏差：** [xFinder, ICLR 2025](https://arxiv.org/abs/2405.11874) 指出正则提取错误；Panickssery 等（NeurIPS 2024 主会）研究自识别与自偏好 [2](https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html)；[Preference Leakage, ICLR 2026](https://arxiv.org/abs/2502.01534) 发现生成器与 judge 同族存在偏差风险。这些不证明本实验已发生该偏差（conf=0.99）。
- **攻击与任务变化：** [Null Models, ICLR 2025](https://arxiv.org/abs/2410.07137) 展示与输入无关的输出可骗自动榜单；[GSM-Symbolic](https://arxiv.org/abs/2410.05229) 用符号模板生成数值变体。前者攻击 LLM 评测而非本文机械规则，后者不提供本稿的瞎猜上界（conf=0.99）。
- **会议覆盖补充：** [MLLM-as-a-Judge, ICML 2024](https://proceedings.mlr.press/v235/chen24h.html) 研究多模态 judge 的偏差与一致性；[Wang 等, ACL 2024](https://aclanthology.org/2024.acl-long.511/) 测位置偏差；[Raina 等, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.427/) 测 judge 对抗攻击，均非本题数值设置（conf=0.99）。
- **本地口径：** 数据分别为 `data/prompt_variant_formal.json` 的 201 条、`data/formal_judge_outputs.json`、`data/mt_probe2.json`、`data/judge_determinism.json`、`data/rd_ab_bprime_n10.json`；脚本位于 `D1-generalization/scripts/`。正式格式判定截取最后一对花括号并解析 JSON，允许对象外文字，异常也算失败；生成端模型及部署配置未在 67 条回答中逐条存证。
- **F3 敏感性：** 去掉恒错的 c2 后，V1/V2/V3 的分歧分别为 27/45、17/33、45/96；其他机械标签仍未经语义标注，这些不是修正后的准确率（conf=0.99）。
- **F4 模拟缺陷：** 除 Q08–Q10 文字 gold 恒失败外，`guess_bound.py` 对 Q01/Q04/Q05 的数值 fact、tol=0 使用严格 `< 0` 判断，恒不命中；因此多题的零命中是程序构造的，不能称模拟验证了解析界（conf=0.99）。
- **F5 宽松口径反例：** Q09 的 `999 tok/s` 被 strict 判 False、lenient 判 True；现有 B′ Q09 的 strict 与 lenient 结果并无差异，因此该缺陷不推翻上述 30/30 复算（conf=0.99）。
- **Q04 算式：** KV 池 `(80−405/8−5.5)×10^9=23.875×10^9` B/GPU；分片后 KV 为 `2×126×(8/8)×128=32,256` B/token/GPU；`floor(23.875×10^9/(16384×32256))=45`，batch 8 需约 4.23 GB/GPU。原 spec 的 `checks` 也把 batch 8 标为不适配（conf=0.99）。
- **不读题数字枚举复现：** 构造前已查看部分 spec/gold，故这不是预注册盲测，不能估实际攻击率；生成该列表时不读取题目或 gold。仓库根目录、安装 SymPy（实测 1.13.3）后运行：
```python
import json, sys
sys.path.insert(0, 'projects/AI-计算科学/D1-generalization/scripts')
import formula_judge as j
p = 'projects/AI-计算科学/D1-generalization/tasks/T-PUB-1/data/tpub1_extracted.json'
s = json.load(open(p, encoding='utf-8'))['specs']
x = ' '.join([f'{i/100:.2f}' for i in range(1,101)] + [str(i) for i in range(1,257)] + [str(i) for i in range(0,1001,5)])
for q in ('Q01','Q02'): print(q, len(x), j.judge_mechanical(s['T-PUB-1-'+q], x))  # 2198，均 5/5 True
print(j.judge_mechanical(s['T-PUB-1-Q04'], '{"c5":45}')['c5'])  # False
print(j.judge_mechanical(s['T-PUB-1-Q08'], 'Answer: 999 GB\nUnrelated number: 77.7.')['c4'])  # True
```

## 最终决策

| Finding | 主会 ICML 2027 可投性(conf) | 降级 workshop 的触发条件 | 最小强化动作（按性价比排序，≤3） |
|---|---|---|---|
| 整体 | **0.08**；当前转 4 页 workshop 个案，接收率未估 | 参考判分或同规则输入未修复并复核；或尚无至少 30 道独立题、2 个异家族 judge 的配对结果；或修复后结果不复现。前两项当前已触发；数量门槛仅为实务建议，不保证主会可投。 | ① 删除普适因果、硬币、防 hack 和必然 trade-off，补关键撞车文献；② 修复并双人盲审参考判分、对齐完整输入和 rubric，留 raw/错误/finish_reason 后重算；③ 增加独立题与异家族 judge，配对比较 500/2000 token 和约束 JSON，按题聚类报告不出分率及分歧。 |
