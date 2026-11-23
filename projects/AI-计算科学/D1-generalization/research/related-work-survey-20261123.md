# T-PUB-1 Related Work 调研（arXiv API 直查，2026-11-23）
# origin: ai · W1 交付（骨架缺口 #1）
# 数据: research/related-work-arxiv-20261123.json（4 线 × 10 条，含完整摘要）
# 查询: arXiv API 直连（LLM-as-judge bias 268 条 / RSI verifier 72 / formal eval 162 / judge reliability 620）

## 核心发现（≤20 行）

**1. "LLM judge reliability" 2026 年已是活跃方向（620 条），不能再靠"我们测 reliability 别人只测 bias"差异化。** 撞车最重的 6 篇：
- 2603.05399 Judge Reliability Harness（ICLR 2026 workshop）：开源库，测 binary judgment accuracy + ordinal grading，4 judge × 4 benchmark（safety/persuasion/misuse/agentic）
- 2610.30512 Arena-Hard judge（NeurIPS 2026 JUDGe workshop "Can We Trust the Judge?"）：500 prompts × 8 种 criteria/format/framing 组合，测 aggregate score 掩盖的 verdict 漂移
- 2609.13824 Consistency≠Reliability：本地 LLM judge（LLaMA-3-8B/Qwen2.5-7B）vs 9 人类标注
- 2510.09738 Judge's Verdict（ICLR 2026 在审）：54 LLM × RAG/Agentic 输出 vs 人类 ground truth，Cohen's Kappa
- 2606.15029 Metric Match：从有限人类标注估计 reliability metric
- 2610.05452 VERA：hidden activations 估计 verdict 可靠性

**2. 现有 reliability 工作的 ground truth 全部是"人类标注"或"扰动测试"——没有一篇用机械 judge 当 exact reference。** 这是我们的差异化锚点：可形式化核上机械 judge 是**免费的、100% 精确的、可复现的** ground truth，绕开人类标注成本 + 标注噪声。

**3. 差异化定位（§3 必须讲清的三句话）**：
- (a) 我们测的失败维度是 **format reliability（judge 吐不出可解析判定）**——现有工作全假设 judge 输出了分数，测的是分数准不准（verdict accuracy），没测"judge 根本没法出分"这个前置失败。
- (b) 我们做**机制归因**（截断/输入复杂度/指令遵循三因素分离，偏相关 + finish_reason 直接证据）——现有工作只报相关性（"reliability 随 X 变"），不归因到可操作的机制。
- (c) 我们有**防 hack 理论**（瞎猜概率界，模型无关）——现有 reliability 工作没有防"高分是蒙的"的理论保证。

**4. RSI 验证器赛道（72 条）确认拥挤**：2026-11 单月 10+ 篇 RSI 新论文（Search-RSI/AeroRSI/EVA-RSI/InfraRSI/PhysLoop/NCP/InfraRSI/CARE...），TRUST 2611.10787 在审 ICLR 2027。但 RSI 线测的是"self-improvement 循环是否有效"，不是"judge 本身可靠性"——正交，§3 一段带过即可。

**5. formal verification in eval（162 条）支持机械 judge 路线**：2605.27485（agent-guided tree search 自动化形式化验证，78 页）、2605.03822 KVerus（ASE 2026，Rust 证明生成）——"用形式化工具做 eval"有顶会先例，我们的 SymPy 机械 judge 是这条线在 LLM-judge 场景的实例化。

## 对论文的影响（必须改的）

1. **§1/§3 定位句改**：从"我们测 reliability 别人只测 bias"→"现有 reliability 工作依赖人类标注/扰动测试当 ground truth；我们在可形式化核上用机械 judge 当 exact reference（免费+精确+可复现），并做机制归因 + 防 hack 理论"。
2. **撞车 6 篇必须逐篇 cite + 区分**（§3 表格：工作 / ground truth / 测的维度 / 机制归因 / 防 hack 理论，我们 4 列全有）。
3. **claim 强度降档**：原"LLM judge 不可靠"是已知结论（620 篇都在说），我们的贡献不是"发现不可靠"而是"可形式化核上机械 judge 是免费替代 + 机制可归因 + 防 hack 可证明"——§1 contribution 列表按此重写。
4. **NeurIPS 2026 JUDGe workshop（"Can We Trust the Judge?"）是天然的 venue 备选**：若 ICML 2027 主会撑不住，投该 workshop 系列（2027 届）比 ICLR workshop 更对口。

## 待办（W2-W3）

- [ ] 撞车 6 篇拉 PDF 精读（至少 2603.05399 + 2610.30512），确认 (a)(b)(c) 差异化没被覆盖 → ego-browser 下 PDF
- [ ] TRUST 2611.10787 精读（RSI 赛道代表，§3 差异化定位用）
- [ ] §3 初稿（800-1000 词）：LLM-as-judge bias 线（1 段）+ reliability 线 6 篇逐篇区分（1 段+表）+ RSI 赛道（1 段）+ formal verification 先例（1 段）+ gap 定位（1 段）
