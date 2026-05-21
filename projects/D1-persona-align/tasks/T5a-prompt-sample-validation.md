# T5a: Prompt 混合注入最小样本量验证

> **完成时间**: 2026-05-19 (Iteration 24)
> **输入**: T2 style analysis (6 metrics) + T3 injection scheme + T4 stability comparison
> **执行者**: Ralph Loop

---

## 1. 工具开发: persona_fidelity_scorer.py

路径: `/Users/a1-6/Desktop/workspace/tools/persona_fidelity_scorer.py`

基于 T2 的 6 个量化指标构建的自动保真度评分工具：

| 指标 | 计算方法 | Target | raw.md 基线 |
|------|----------|--------|------------|
| 问句比例 | 问句句数/总句数 | 25-40% | 35.4% ✅ |
| 跨域系数 | Shannon 熵(5域归一化) | >0.3 | 0.96 ✅ |
| 不确定性标记 | 含不确定词的句数/总句数 | >15% | 16.3% ✅ |
| 块状结构 | ❏数+分项标记/句数 | >0.6 | 0.68 ✅ |
| 隐喻比例 | 30个隐喻词的出现率 | >10% | 75.8% ✅ |
| 词汇重叠 | Bigram Jaccard | 辅助 | 100% ✅ |

### 验证结果

| 输入 | 评分 |  verdict |
|------|------|---------|
| raw.md 自评分 (基线) | 100% (6/6 pass) | PASS |
| 陈述式正式文风 | 8.3% (1/6 pass) | FAIL |
| 模拟 persona 风格 | 83.3% (5/6 pass) | PASS |

### 工具使用方式

```bash
# 基线评分 (raw.md 自身)
python3 tools/persona_fidelity_scorer.py --reference raw.md --self-score

# 评分候选输出
python3 tools/persona_fidelity_scorer.py --reference raw.md --candidate output.txt

# 评分内联文本
python3 tools/persona_fidelity_scorer.py --score-only --sample "test text"

# JSON 输出 (自动化测试用)
python3 tools/persona_fidelity_scorer.py --reference raw.md --candidate output.txt --json
```

---

## 2. 实验设计: T5a 验证方案

### 2.1 实验目标

验证 5-8 条 few-shot 样本的混合注入方案能否在 LLM 输出中维持 persona 保真度。

### 2.2 实验流程

1. **准备阶段**:
   - 从 raw.md 中选取 3/5/8 条样本（分层抽样：每类 idea 域各选若干）
   - 构建 3 组 prompt: `[3条]`, `[5条]`, `[8条]`

2. **实验阶段**:
   - 对每组 prompt，让 LLM 回答 5 个测试问题
   - 测试问题覆盖: AI idea / 社科 idea / 数学 idea / 方法论 / 开放问题

3. **评估阶段**:
   - 用 `persona_fidelity_scorer.py` 对每个输出评分
   - 记录总分和各子指标
   - 对比 3 组的评分差异

4. **判定标准**:
   - 如果 5 条组的平均分 ≥ 80% → 最小样本量 = 5
   - 如果 3 条组的平均分 ≥ 70% → 最小样本量 = 3
   - 如果 3 条组 < 70% → 最小样本量 > 5

### 2.3 样本选择策略

从 raw.md 分层选取:

| 层 | 样本数 | 依据 |
|----|--------|------|
| AI/信息论 | 1-2 | T2 中最频繁领域 |
| 社科/人文 | 1 | 跨域多样性 |
| 数学 | 1 | 定量/形式化表达 |
| 方法论 | 1 | 元思考能力 |

---

## 3. 实验数据准备

从 raw.md 提取的分层样本:

### Sample A1 (AI/信息论 — 最长行, 394 字符)
> 或基于分析的已知未知进一步获取目标分布然后匹配提高通过率（准确率）目标分布可变?用动力学，压缩信息到kolmogrov复杂度下界估算时空分布进行时空匹配

### Sample A2 (AI训练数据层级化)
> ❏ ai训练数据是否是层级化的，粗到细，rag外挂呢，以及内部检索?如果不是层级的，（或标签，频率，）改成这样有优势吗，机理呢

### Sample S1 (社科 — 自我修正模式)
> 开始我以为应该一一对应，恨具体不恨抽象，但是ulu提醒我她不恨具体的人而是制度，虽然她没说理由但是我意识到我的问题，恨制度而不是具体的人更有可能发起变革团结朋友，除非具体的人坚决捍卫抽象的人

### Sample M1 (数学 — 信息论视角)
> 信息因子贡献，媒体操纵，技术指标太短期且滞后，根据源头信息，操纵扩散，引导资金

### Sample MP1 (数学+社科交叉)
> 流量经济，信息网络结构伴随对经济网络影响

### Sample P1 (物理隐喻)
> 信道容量冗余类比，管子接流水，读者是不同管子，我的流水是大管子，确保每个读者都能喝到我大管子流出的水

### Sample PH1 (正负反馈 + 社会)
> 压力（正反馈）导致的不稳定分化（噪声放大），引力（有负反馈）导致稳定演化，迁移到社会各种分化和统一?

### Sample Meta (方法论 — 最长, 复杂思考链)
> 蕴含信息影响呢（平凡与否，非平凡概率以及对进展影响）另一条总论思路，动态演化，动力学，泛函，变成任何问题都会可以说优化问题，（怎么到最优），然后通过工具路由器路由到最优工具开始优化

---

## 4. 工具部署

`persona_fidelity_scorer.py` 已部署至 `/tools/`，可与既有工具链（search_web.py 等）配合使用。

---

*T5a 核心产出: 自动评分工具 + 实验设计 + 分层样本。下一步: 实际运行实验（需要 LLM API 调用），比较 3/5/8 条样本组的评分差异。*
