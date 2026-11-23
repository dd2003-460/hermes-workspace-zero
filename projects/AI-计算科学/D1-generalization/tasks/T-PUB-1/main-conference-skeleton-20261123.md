# decomp: T-PUB-1 主会论文骨架（ICML 2027, 9 页 + 附录, 截止 2027-01-14 abstract / 01-22 paper, 60 天）
# origin: ai · 2026-11-23
# 对象: T-PUB-1 formula_judge 轨（机械验证器 vs LLM judge 可靠性测量）——不是 metacog 轨（27B research agent 两轴测量，骨架在 pfb/tasks/metacog-main-conference-skeleton-20261123.md）
# 数据源（全部已落盘，见 tasks/T-PUB-1/paper-data-table-20261123.md）:
#   ① 三臂 prompt 变体正式实验 n=201 (/tmp/prompt_variant_formal.json)
#   ② 三臂 A/B/B' rank-deficient 行为实验 n=30 (/tmp/rd_ab_bprime_n10.json)
#   ③ 截断机制探针 n=6 + finish_reason 直接证据 (scripts/mt_truncation_probe.py)
#   ④ 瞎猜概率界解析+模拟 (scripts/guess_bound.py)
#   ⑤ c3 双口径重判 (scripts/c3_lenient_rejudge.py)
# 目标: 9 页 ICML 格式 ≈ 7000-8000 词正文 + 附录

## 核心 claim（一句话，2026-11-23 related work 调研后修正）

**现有 LLM judge reliability 工作（620 篇，2026 活跃方向）依赖人类标注/扰动测试当 ground truth；我们在可形式化核上用机械 judge 当 exact reference（免费 + 100% 精确 + 可复现），测出 LLM judge 双维度失败（格式可靠性 52-84% + 判分翻转 ≈50%），做机制归因（截断/输入复杂度/指令遵循三因素分离），并给防 hack 理论保证（瞎猜概率界）。**

差异化三支柱（§3 逐篇对比用）：(a) format reliability 维度——现有工作全假设 judge 出了分，没测"judge 根本没法出分"的前置失败；(b) 机制归因——现有只报相关性，我们归因到可操作机制（偏相关 + finish_reason 直接证据）；(c) 防 hack 理论——现有无"高分非蒙的"保证，我们有模型无关的瞎猜概率界。

撞车 6 篇（必须 cite + 区分，详见 research/related-work-survey-20261123.md）：2603.05399 Judge Reliability Harness / 2610.30512 Arena-Hard judge / 2609.13824 Consistency≠Reliability / 2510.09738 Judge's Verdict / 2606.15029 Metric Match / 2610.05452 VERA。

## 字数预算（9 页 ≈ 7500 词正文）

| 节 | 目标词数 | 内容 | 数据源 |
|----|---------|------|--------|
| Abstract | 150-200 | 1 句 hook（LLM judge 是 agent 评测标配但不可靠）+ 1 句方法（10 题 × 3 prompt × 67 输出 + 机械对照）+ 1 句核心 finding（52-84% 格式失败 + 50% 翻转 + 截断主因） | ① |
| 1. Introduction | 900-1000 | ①agent 评测现状（LLM-as-judge 普及 + 已知 bias 文献）②gap：可形式化核上 LLM judge 是否必要？（如果机械可判，为什么用 LLM？）③contribution 列表 3 条：(a) 可靠性双维度测量（格式+判分）(b) 机制归因（截断/注意力/指令遵循三因素 + 偏相关分离）(c) 防 hack 理论（瞎猜概率界）④与 RSI 验证器赛道（TRUST 等）差异化：我们测的是 judge 本身可靠性，不是 agent | ①③④ |
| 2. Setup & Method | 1200-1500 | ①题集构造：10 题（7 full + 3 rank-deficient）× 4-5 检查点，gold 由 SymPy 符号验证 + datasheet 锚点 ②judge 设计：LLM judge 3 prompt 变体（V1_strict/V2_loose/V3_engineer）vs 机械 judge（SymPy 数值 + 正则 bool）③测量协议：67 真实输出（27b 生成）× 3 变体 = 201 次调用，翻转率定义，双口径（strict/lenient）④27b 部署（127.0.0.1:8787 vLLM, max_tokens=500 默认） | ①②⑤ |
| 3. Related work | 800-1000 | ①LLM-as-a-judge 线（judge bias 文献：position/verbosity/self-preference）②RSI 验证器赛道（TRUST 2611.10787 在审 ICLR 2027 + 3 篇同方向）③mechanical/formal verification 线（SymPy/SMT 在 eval 中的先例）④**gap 定位：现有工作测 judge bias（系统性偏差），我们测 judge reliability（随机失败率）+ 机制归因** | 需 arena 调研 |
| 4. Findings | 2500-3000 | **F1 格式可靠性**：三臂 52-84% 失败 vs 机械 0%；台阶 604 字符阈值；**F2 机制归因**：截断主因（83% 恢复率 + finish_reason=length 直接证据）+ 输入复杂度独立效应（偏相关 0.436）+ 指令遵循 17%；**F3 判分准确性**：翻转率 48-52% ≈ 抛硬币；**F4 防 hack**：瞎猜概率界 1e-10~3e-5，rank-deficient 高 3 量级；**F5 prompt trade-off**：A/B/B' 修 c1 引入 c3 副作用（条件列举 hedging 7/30 灰区） | ①②③④⑤ |
| 5. Implications | 400-500 | ①可形式化核上优先机械 judge（免费、100% 可靠、可复现）②LLM judge 保留给不可形式化核（解释质量/风格）③harness 设计：max_tokens 必须 ≥ 输出长度分布 P99 + JSON-only 解码 ④benchmark 设计：检查点数不是防 hack 主杠杆，gold 复杂度才是 | ①④ |
| 6. Limitations | 300-400 | ①n=67 输出/10 题（单模型 27b，跨模型泛化未测）②max_tokens=500 是默认配置（生产环境可能不同）③rank-deficient 题只有 3 道 ④fact gold 到规格页级未逐份 PDF 校验（followups #1） | followups.md |
| 附录 | 3000-4000 | 完整统计表（逐检查点 × 逐变体）/ 10 题全文 + gold 推导 / 瞎猜模型定义 + 解析界推导 / c3 双口径算法 + 灰区 7 case 全文 / 3 prompt 变体全文 / 27b 部署细节 | 全部 |

## 缺口清单（主会 vs 现有数据差什么）

1. **Related work 调研**（§3 的 800-1000 词）：LLM-as-judge bias 文献 + RSI 验证器赛道最新 + formal verification in eval 先例 → **走 arena-outsource**（W1）
2. **跨模型验证**（Limitations ①的升级项，可选）：若 W3 前有余力，用 1-2 个其他本地/免费模型重跑 V1 子集（n=20）证明"52-84% 失败"不是 27b 特有 → 没有则留 Limitations
3. **图/表**：3 图（格式失败率 vs 输出长度台阶图 / 三臂失败率柱状 / 瞎猜概率界 log 图）+ 2 表（三臂汇总 / 机制归因汇总）→ 数据全有，W3-W4 画
4. **统计严谨性**：翻转率 50% 的 CI（n=60/44/128 可解析调用）+ 台阶阈值 bootstrap CI → W5
5. **匿名化**：ICML 双盲，去作者/机构/内部路径（127.0.0.1:8787 等）→ 提交前 checklist

## 60 天排期（2026-11-23 → 2027-01-22）

| 周 | 日期 | 任务 | 依赖 |
|----|------|------|------|
| W1 | 11/23-11/29 | ①related work 调研 ✅ ②§4 Findings 初稿 ✅ ③图 1-2 ✅（figures/fig1+fig2, 已 vision 核验） | 无 |
| W2 | 11/30-12/06 | ①§1 Intro 初稿 ✅ ②§2 Setup 初稿 ✅ ③理论节初稿 ✅（瞎猜界正式证明）④§4 补 F5 ✅ | W1 |
| W3 | 12/07-12/13 | ①§3 Related work 初稿 ✅（防撞车区分句+三支柱定位表+机械judge定位）②跨模型验证子集（可选，缺口 2）③图 3 + 表 1 | W2 |
| W4 | 12/14-12/20 | ①§5 Implications ②§6 Limitations ③表 2 ④附录初稿 | W3 |
| W5 | 12/21-12/27 | ①统计严谨性（CI + bootstrap）②附录完整化 ③全文通读 + 字数控制 | W4 |
| W6 | 12/28-01/03 | ①内部 review（arena 交叉验证 claim 强度）②修订 ③匿名化 checklist | W5 |
| W7 | 01/04-01/10 | ①abstract 压缩 200 词 ②final proofread ③**ICML 2027 abstract 提交 (01/14 AoE)** | W6 |
| W8 | 01/11-01/22 | ①full paper 终稿 ②**ICML 2027 paper 提交 (01/22 AoE)** | W7 |

## 风险

- **claim 强度**：单模型（27b）单题集（10 题）→ 主会 reviewer 大概率问泛化。缓解：Limitations 明确 scoping + 跨模型子集（若跑）+ 瞎猜概率界是模型无关的（理论节兜底）
- **赛道拥挤**：TRUST 等 4 篇 RSI 验证器在审 ICLR 2027 → 差异化定位必须在 §1/§3 讲清（judge reliability vs judge bias，mechanical vs LLM）
- **workshop 保底**：若 W5 发现 claim 撑不起主会 → 降级 4 页 workshop 短文（publication-strategy 轨 B：10 题 × 2 judge 翻转率 + 瞎猜界 + 1 自修复案例），ICLR 2027 workshop 截止 2027-02~03 仍来得及
- **与 metacog 轨资源竞争**：两轨同窗口（ICML 2027），T-PUB-1 数据层已齐（写作为主），metacog 还在实验层 → 本轨 W1-W4 写作不占实验资源，可并行
