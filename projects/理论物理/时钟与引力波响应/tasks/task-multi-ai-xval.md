# 任务：多平台 AI 交叉核验 — JCAP 手征引力波公式

## 目标
通过 **4 个外部 AI 平台** 对 JCAP 手征引力波理论中的关键公式（b^V_0, b^V_1, Γ^V 结构）进行交叉验证，确保实现正确性。

## 使用平台

| 平台 | URL | 模型 | 用途 |
|------|-----|------|------|
| Arena AI | https://arena.ai/agent | 多模型 | 公式核验 + 代码审查 |
| 智谱 GLM-5.2 | https://bigmodel.cn/trialcenter/modeltrial/text?modelCode=glm-5.2 | GLM-5.2 | 公式推导验证 |
| Google Gemini | https://aistudio.google.com/prompts/new_chat | Gemini | 物理概念解释 |
| ChatGPT | https://chatgpt.com/ | GPT-4 | 代码逻辑审查 |

## 工作流

### Step 1: 准备提示词（Prompt）

```
以下是 JCAP 05(2025)050 中手征引力波宇称反对称重叠减少函数 Γ^V 的解析表达式（Appendix B）：

Γ^V = Σ_n (i^(2n+1))/(2n+1) [b^V_n(ψ) · S^V_n]

其中关键系数 [JCAP Eq. 2.16]:
b^V_0(ψ) = 4/5 · (j_1(ψ) - j_3(ψ))
b^V_1(ψ) = 4/35 · j_3(ψ)

j_n 是球贝塞尔函数。

问题：
1. 这两个系数是否正确？与 Hu PRD 111.084065 的通用 ORF 框架是否一致？
2. 为什么共面探测器网络的 Γ^V = 0？
3. b^V_0 中的 j_1 - j_3 组合是否合理？（j_1 来自偶极，j_3 来自四极？）
4. 系数 4/5 和 4/35 是否能从场论第一性原理推导？
```

### Step 2: 上传代码文件

将 `scripts/chiral_orf_jcap_analytical.py` 的关键部分（b_V0, b_V1 函数，cross_first_index 函数）上传让 AI 审查。

### Step 3: 收集回复

记录每个平台的回复，特别是：
- 对公式正确性的判断（正面确认 / 指出错误 / 不确定）
- 任何与 JCAP 公式的冲突
- 对物理直觉的解释

### Step 4: 汇总分析

- 如果 3+ 个平台确认公式正确 → 置信度提升
- 如果有平台指出错误 → 需要重新检查 JCAP 原文
- 如果意见不一致 → 增加更多平台的验证

## 状态

- [ ] Step 1: 准备提示词
- [ ] Step 2: 在 Arena AI 上提交
- [ ] Step 3: 在智谱 GLM-5.2 上提交
- [ ] Step 4: 在 Google Gemini 上提交
- [ ] Step 5: 在 ChatGPT 上提交
- [ ] Step 6: 汇总分析所有回复
- [ ] Step 7: 更新任务状态和置信度

## 关键文件

- `raw/JCAP2025_Chiral.txt` — JCAP 原文（公式来源）
- `scripts/chiral_orf_jcap_analytical.py` — 已实现代码（b_V0, b_V1 已修正）
- `note/P1-2-chiral-orf.md` — 手征 ORF 理解笔记
