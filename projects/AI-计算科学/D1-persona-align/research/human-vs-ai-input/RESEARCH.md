# 人类输入 vs AI 输入对 AI 输出人味的影响

**日期**: 2026-10-21
**状态**: arena 调研完成（2026-10-21）— 机制分析 + arena 联网调研（LMArena agent mode 会话 01a15f07）+ arXiv 原文核实
**调研方式**: ① LMArena agent mode（成功，13K 字符回复，含 6 篇 arXiv + 商业报告 + GitHub repo）② 第二站点交叉验证降级（ChatGPT 页面漂移不可用）→ 改为 arXiv 摘要直接核实（2509.14543 ✓ / 2509.24930 ✓ 标题+摘要与 arena 描述一致）

## 1. 问题定义

成璐发现：AI 模仿他写的回复比真实成璐的话更"设计过"（太整齐、太有结构、太像 assistant 在模仿人）。

核心问题：如果给 AI 看真实人类写的文本（而不是 AI 生成的"人类风格"文本），AI 的输出会不会更有人味？

## 2. 机制分析

### H1: 人类 few-shot 示例 → 输出更"散"
**假设**: AI 看到人类写的 few-shot 后，输出句长方差更大、结构更松、跑题更多。
**机制**: LLM 的 in-context learning 会模仿示例的统计特征。人类文本的句长分布是重尾的（很多短句+偶尔长句），AI 文本的句长分布是窄峰的（大部分中等长度）。如果 few-shot 是人类的，AI 会模仿重尾分布。
**conf**: 0.7 → **0.75**（arena 调研后：few-shot 改风格成立，但来源→burstiness 精确 claim 仍无受控实验）
**预期效果**: 句长 std 从 ~15 提升到 ~20-25

**调研证据（2026-10-21 · LMArena agent mode 会话 01a15f07 · 联网搜索）**:
- ✅ **few-shot 人类样本显著提升风格匹配**：arXiv:2509.14543（Wang et al., 2025-09，40000+ 生成/模型、400+ 作者、news/email/Reddit/blogs）— GPT-4o 5-shot 同作者人类样本 vs zero-shot：email 作者验证 **85.02%→96.15%**，top-5 归因 email **28.62%→59.65%**、blogs **17.22%→39.39%**。（arXiv 原文核实 ✓）
- ⚠️ **「人类 vs AI 示例来源」精确导致句长 burstiness 差异：无受控实验证明**（arena 标 [UNVERIFIED]）。最接近证据=商业报告（60779 对 human/AI 改写：句长 CV 0.449→0.376，SD ~12.0→9.4 词，79.3% 改写更平），但 vendor 报告非受控实验（conf 0.5）。
- **样本数量**：2→10 样本「more examples affect metrics very little」（2509.14543）；1 个人类段落 verifier 匹配 67.6-94.7%，2 段 91-100%（arXiv:2509.24930 Jemama & Kumar，training-free TF-IDF char n-gram + transformer embedding，97.5% accuracy，arXiv 原文核实 ✓）。→ **1-2 个实质性同体裁样本即可**（conf 0.85）。
- **same-topic 选取被证伪**：2509.14543 发现同主题选取反而降低归因（69.33→36.00%）→ 应选**风格多样（非最近主题）**的样本（conf 0.8）。
- **加真实前缀有效**：50 词真实前缀使 GPTZero human 率 email 36.83→46.50%（2509.14543，conf 0.7）。

### H2: AI few-shot 示例 → 输出更"整齐"
**假设**: AI 看到 AI 写的 few-shot 后，输出会强化 assistant 模式（更整齐、更有结构、更像"好的回答"）。
**机制**: AI 文本自带"被优化过"的痕迹（完整句、逻辑连接词、无跑题）。LLM 模仿这些痕迹时会放大它们，产生"过度模仿"效应。
**conf**: 0.8 → **0.85**（arena 调研后：LIMA 反例确认"来源≠风格分布"，人类数据可教整齐性）
**预期效果**: 结构整齐度提升，但人味下降

**调研证据（2026-10-21）**:
- ✅ **AI few-shot 强化 assistant 模式**：与 r15-r21 消融实验一致（结构层是主战场，词表≈0）。
- ⚠️ **LIMA 反例**：arXiv:2305.11206（Zhou et al., 2023，LIMA）— 65B 模型用 **1000 个人类样本** SFT，43% 对比中≥GPT-4。注意其目标是"**uniform response style**"——**人类数据可教整齐性**，来源≠风格分布。→ H2 需细化：不是"AI 示例→整齐"，而是"任何高度一致/优化过的示例→整齐"（conf 0.8）。
- **SFT/RLHF 可改行为层**：InstructGPT arXiv:2203.02155（175B 85±3% 偏好于 base）；Stiennon arXiv:2009.01325（1.3B RLHF 61% 偏好 vs 10x 监督模型 43%）→ 超越 few-shot 表层，可改选择/省略/拒绝行为（conf 0.85）。

### H3: 人味的核心不在句式，在"不完美"
**假设**: 人味的核心是跑题、重复、犹豫、矛盾、自我修正——这些是 AI 几乎不会生成的。
**机制**: AI 的训练目标是"生成有用的回答"，有用 = 相关 + 完整 + 不跑题。所以 AI 天然倾向于去掉"不完美"。人类的"不完美"是思考过程的副产物，不是目标。
**conf**: 0.9 → **0.92**（arena 调研后：arXiv:2509.24930 headline 直接支持 + 无研究证明类人内部认知）
**预期效果**: 即使句式完美匹配，没有"不完美"就不像人

**调研证据（2026-10-21）**:
- ✅ **强支持**：arXiv:2509.24930（Jemama & Kumar）headline：**"high-fidelity imitation does not imply human-like unpredictability"** — GPT-2 perplexity profile-only 8.90/10.46 → 1 段 17.45/19.87 → 2 段 16.43/15.16，人类基线 29.5。→ 高保真风格模仿 ≠ 类人不可预测性（conf 0.9）。
- ✅ **无研究证明模型获得类人内部认知**：arena 明确标注——"deep thinking style" claim 除非经推理任务/错误模式/校准等行为测试否则 [UNVERIFIED]。→ 人味核心在"不完美"（认知过程痕迹），不是句式（conf 0.9，与 r15-r21 消融一致）。
- **AI 检测领域佐证**：GPTZero/Turnitin 使用 perplexity + burstiness 作为核心指标（conf 0.7，AI 检测领域已确认）。

### H4: AI 模仿人 = style transfer，丢失内容层"不完美"
**假设**: 当 AI 做 style transfer（把内容A的风格转成内容B的风格），它只转句式层，不转思维层。
**机制**: Style transfer 是表层操作（词汇替换、句法变换）。但成璐的"人味"不仅在表层，还在：
- 跑题（2.1讲成本，2.2突然问"你觉得你最大的问题是什么"）
- 括号内心独白（"当然大概率是2和3都是我在找茬"）
- 自我修正（"但是也有伪thinking？"）
- 未完成句（"你没这个习惯..？"）
这些是思维过程的痕迹，不是风格特征。Style transfer 无法生成真正的"跑题"，因为它没有真正的"别的想法"。
**conf**: 0.85 → **0.9**（arena 调研后：few-shot/humanizer 证据只及表达层，SFT/RLHF 才可改行为层）

**调研证据（2026-10-21）**:
- ✅ **few-shot/humanizer/paraphrase 证据只及表达层**：blader/humanizer 26 patterns 多为词汇/句法/修辞（conf 0.8）；DIPPER arXiv:2303.13408（DetectGPT 70.3%→4.6%@1% FPR）只证检测器漏洞非人味（conf 0.75）。
- ✅ **SFT/RLHF 可改行为层**：LIMA（1000 样本改 response style）+ InstructGPT/Stiennon（偏好对齐改选择/省略/拒绝）→ 超越表层（conf 0.85）。
- **Style transfer 边界**：跨体裁 transfer 未被受控检验（2509.14543 明示仅限 within-genre）；length-matched ≠ style-matched（conf 0.7）。
- **结论**：成璐人味 50% 表层（句式/词汇/标点）+ 50% 深层（思维跳跃/括号独白/未完成句）— few-shot 只及表层，深层需 SFT/RLHF 或真正的认知过程（conf 0.85）。

## 3. 学术文献（arena 调研后更新 · 2026-10-21）

> 以下文献经 LMArena agent mode 联网调研核实（2026-10-21），arXiv 原文已直接验证（2509.14543 ✓ / 2509.24930 ✓ 标题+摘要一致）。

### 已验证文献

1. **arXiv:2509.14543** — Wang et al., "Catch Me If You Can? Not Yet" (2025-09)
   - 40000+ 生成/模型、400+ 作者、news/email/Reddit/blogs 四域
   - 核心发现：GPT-4o 5-shot 同作者人类样本 vs zero-shot → email 作者验证 85.02%→96.15%，top-5 归因 email 28.62%→59.65%
   - 2/4/6/8/10 嵌套样本「more examples affect metrics very little」
   - same-topic 选取反而降低归因（69.33→36.00%）
   - 加真实前缀 50 词使 GPTZero human 率 email 36.83→46.50%
   - **arXiv 原文核实 ✓**（标题+摘要一致）

2. **arXiv:2509.24930** — Jemama & Kumar (2025-09)
   - Training-free TF-IDF char n-gram + transformer embedding，97.5% accuracy
   - 1 个人类段落 verifier 匹配 67.6-94.7%，2 段 91-100%
   - GPT-2 perplexity: profile-only 8.90/10.46 → 1 段 17.45/19.87 → 2 段 16.43/15.16，人类基线 29.5
   - Headline: **"high-fidelity imitation does not imply human-like unpredictability"**
   - **arXiv 原文核实 ✓**（标题+摘要一致）

3. **arXiv:2305.11206** — Zhou et al., "LIMA: Less Is More for Alignment" (2023)
   - 65B 模型用 1000 个人类样本 SFT，43% 对比中≥GPT-4
   - 目标："uniform response style" → 人类数据可教整齐性（来源≠风格分布的反例）

4. **arXiv:2203.02155** — Ouyang et al., "InstructGPT" (2022)
   - 175B 模型 RLHF 后 85±3% 偏好于 base model

5. **arXiv:2009.01325** — Stiennon et al., "Learning to Summarize from Human Feedback" (2020)
   - 1.3B RLHF 61% 偏好 vs 10x 监督模型 43%

6. **arXiv:2303.13408** — He et al., "DIPPER" (2023)
   - DetectGPT 70.3%→4.6%@1% FPR（只证检测器漏洞，非人味）

7. **blader/humanizer** (GitHub)
   - 26 patterns，多为词汇/句法/修辞（表层操作）

8. **商业报告**（vendor，非受控实验）
   - 60779 对 human/AI 改写：句长 CV 0.449→0.376，SD ~12.0→9.4 词，79.3% 改写更平
   - conf: 0.5（vendor 报告，非 peer-reviewed）

## 4. 关键指标（从 AI 检测领域借鉴）

| 指标 | 定义 | 人类文本 | AI 文本 | 成璐文本 |
|------|------|---------|---------|---------|
| Perplexity | 文本的"意外程度" | 中等 | 低（太流畅） | 中高（跑题多） |
| Burstiness | 句长方差 / 句长均值 | 高 | 低 | 高（短句+偶尔长句） |
| 跑题频率 | 相邻句子主题切换比例 | 高 | 低 | 高（2.1→2.2 跳题） |
| 犹豫标记 | "其实/大概/可能/.." 频率 | 高 | 低 | 中高（括号内犹豫） |
| 自我修正 | "但是/不过/然而" 后接反向 | 高 | 低 | 高（"但是也有伪thinking？"） |
| 未完成句 | 以"？/.../?" 结尾 | 高 | 低 | 高（"你没这个习惯..？"） |

**核心洞察**: 成璐文本的 burstiness 高 + 跑题频率高 + 未完成句多 = 思考过程的痕迹。这些不是风格，是认知。

## 5. 实验设计

### 实验A: 人类 few-shot vs AI few-shot

**条件**:
- A1: 给 AI 一段 AI 生成的"成璐风格"文本作为 system prompt + 3条 few-shot
- A2: 给 AI 3条真实成璐的文本作为 few-shot（无 system prompt）
- A3: 给 AI 真实成璐文本 + system prompt（混合）

**测量**:
- 句长 std（burstiness）
- 跑题频率（相邻句子主题切换）
- 犹豫标记频率
- 自我修正频率
- 未完成句比例

**预期**: A2 > A3 > A1（人类 few-shot 最有人味）

### 实验B: 思维深度 vs 句式骨架

**条件**:
- B1: 只模仿句式（clonar 原版）
- B2: 模仿句式 + 思维深度（persona 方案）
- B3: 模仿句式 + 思维深度 + 人类 few-shot（clonar v2 + 人类示例）

**测量**:
- 与 GT 的编辑距离
- 人类评估（成璐盲测打分）
- AI 腔调词频率（"等等""本质上""值得确认"等）

**预期**: B3 最接近 GT，但 B3 的思维深度仍不如真实成璐

## 6. 核心结论（初步）

1. **人味的核心不是句式，是认知过程的痕迹**（跑题、犹豫、自我修正、未完成句）。AI 可以模仿句式，但无法生成真正的"跑题"（因为它没有别的想法）。conf: 0.85

2. **人类 few-shot 比 AI few-shot 更有效**，因为人类文本自带"不完美"的统计特征（重尾句长分布、高 burstiness）。AI 文本的"被优化过"痕迹会被放大。conf: 0.7

3. **Style transfer 只转表层，不转深层**。成璐的"人味"50% 在表层（句式、词汇、标点），50% 在深层（思维跳跃、括号独白、未完成句）。Community 方案只抓表层，persona 方案抓了部分深层但"设计过"。conf: 0.8

4. **AI 腔调的核心来源不是词汇，是"过度完整"**。AI 倾向于把每个想法都说完、说完整、说清楚。人类的思维是"说到一半就跳到下一个"。去掉"过度完整"比替换词汇更重要。conf: 0.9（与 r15-r21 消融实验一致：结构层是主战场，词表≈0）

5. **clonar v2 的改进方向正确**：去掉"重复对方话""自我总结""决策话术"就是去掉"过度完整"。但根本解需要让 AI 真正"想别的"（跑题），而不是"假装想别的"（模拟跑题）。conf: 0.7

## 7. 下一步

1. **执行实验A**: 用 clonar prompt + 人类 few-shot vs AI few-shot，盲测 S1/S3，成璐盲测打分
2. **量化 burstiness**: 对 GT / clonar / clonar-v2 / persona / 真实成璐 计算句长 std + 跑题频率
3. **混合方案**: 社区骨架（clonar 句式）+ persona 深度（信息论类比/编号追问）+ 人类 few-shot（真实成璐文本）
4. **验证 H1**: 如果人类 few-shot 确实提升 burstiness，说明 in-context learning 能模仿统计特征但不能模仿认知过程

## 8. 来源与置信度

| 结论 | conf | 来源 |
|------|------|------|
| 人味核心是认知痕迹不是句式 | 0.92 | r15-r21 消融实验 + arXiv:2509.24930 "high-fidelity imitation does not imply human-like unpredictability" + arena 调研 |
| 人类 few-shot 有效提升风格匹配 | 0.75 | arXiv:2509.14543（85%→96% email 验证）；来源→burstiness 精确 claim 仍 [UNVERIFIED] |
| Style transfer 只转表层 | 0.9 | clonar/perfectly-replicate 输出对比 + arena（few-shot/humanizer 证据只及表达层，SFT/RLHF 才可改行为层） |
| AI 腔调核心是"过度完整" | 0.9 | r15-r21 结构层消融 + v2 改进效果 |
| 1-2 个同体裁样本即可，same-topic 反而变差 | 0.85 | arXiv:2509.14543（2→10 样本 marginal 收益极小）+ 2509.24930（1 段 67.6-94.7%） |
| SFT/RLHF 可改行为层（非纯表面） | 0.85 | LIMA arXiv:2305.11206 + InstructGPT arXiv:2203.02155 + Stiennon arXiv:2009.01325 |

## 9. 调研结论与遗留问题（2026-10-21 · LMArena agent mode）

### 调研方式
- **主通道**: LMArena agent mode（https://arena.ai/agent）— 会话 01a15f07-6891-79c0-9259-aa53df6b2914，13K 字符回复，联网搜索成功
- **交叉验证**: 第二站点降级（ChatGPT 页面漂移不可用）→ 改为 arXiv 摘要页直接核实（2509.14543 ✓ / 2509.24930 ✓ 标题+摘要与 arena 描述一致）
- **web_fetch**: 对 arxiv.org 报 "non-public IP address" 不可用，ego-browser 可访问

### 假设验证总结

| 假设 | 原始 conf | 调研后 conf | 判定 |
|------|----------|-----------|------|
| H1 人类 few-shot → 更散 | 0.7 | 0.75 | **部分支持**：few-shot 改风格成立（85%→96%），但"来源→burstiness"精确 claim 无受控实验 [UNVERIFIED] |
| H2 AI few-shot → 更整齐 | 0.8 | 0.85 | **支持 + 细化**：LIMA 反例证明"来源≠风格分布"，任何高度一致/优化过的示例→整齐 |
| H3 人味核心 = 不完美 | 0.9 | 0.92 | **强支持**：2509.24930 headline 直接支持；无研究证明类人内部认知 |
| H4 ST 只转表层 | 0.85 | 0.9 | **强支持**：few-shot/humanizer 证据只及表达层，SFT/RLHF 才可改行为层 |

### 遗留问题
1. **H1 精确 claim 仍需实验验证**：设计 A 组实验（AI-fewshot vs 真人-fewshot vs 混合），测量句长 std + burstiness，对照 §4 指标表
2. **跨体裁 few-shot 未被受控检验**：2509.14543 仅限 within-genre；成璐样本跨多领域（学术/日常/技术），需补充实验
3. **SFT/RLHF 路线可行性**：65B 用 1000 样本（LIMA）对 solo 开发者不现实；需评估 7B-14B 开源模型 + LoRA 微调是否可复现
4. **"deep thinking style" 行为测试**：需设计推理任务/错误模式/校准测试，验证 few-shot 是否真的只及表层

### 对实验设计 A 的修订建议
- **样本选取**：1-2 个同体裁、**风格多样（非最近主题）** 的真实成璐文本 + zero-shot 基线 + matched AI 示例对照
- **前缀**：加 50 词真实前缀（2509.14543 证实有效）
- **测量**：除句长 std 外，增加 GPTZero human 率 + 作者验证率作为辅助指标
