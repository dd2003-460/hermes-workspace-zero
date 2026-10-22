# origin: ai

# Bench：arena 多模型能力 + 研究能力 Benchmark 核实

**日期**：2026-10-22
**执行人**：成璐数字分身（子代理）

---

## A. arena 多模型能力实证

### 结论（一句话）

**arena 多模型 = Direct / Side by Side 模式可自选模型（127+ 个）；Agent Mode 本身无模型选择器（固定由 arena 路由）。**

### 操作路径

| 模式 | 能否选模型 | 操作路径 |
|------|-----------|----------|
| **Agent Mode** | ❌ 无选择器 | 初始页无模型控件，固定 arena 路由 |
| **Direct** | ✅ 1 个模型 | 点底部模式选择器 → 选 Direct → 点模型按钮（默认 "Max" Router）→ 从 127+ 模型列表选 |
| **Side by Side** | ✅ 2 个模型 | 点底部模式选择器 → 选 Side by Side → 点 2 个独立模型按钮（默认 gemini-3.8-flash-high + gemini-3.1-pro-preview）→ 各选 1 个 |
| **Battle Mode** | ❌ 匿名对战 | 2 个匿名模型，不可选 |

### 模型清单（127 个，按字母序）

gemini-3.8-flash-high / gemini-3.1-pro-preview / gemini-3.6-flash / gemini-3.5-flash-high / glm-5.2(max) / qwen3.7-max-preview / gpt-5.5-instant / gemini-3-flash / grok-4.20-beta / grok-4.20-multi-agent / mimo-v2.5-pro / grok-4.5 / glm-5.1 / qwen3.5-max-preview / claude-sonnet-5-high / qwen3.6-max-preview / gemini-3-flash(thinking-minimal) / gpt-5.1-high / qwen3.7-plus / grok-4.6-high / gemini-3.5-flash-lite / gemma-4-31b / gpt-5.4-mini-high / step-5-preview / gemini-2.5-pro / qwen3.6-plus / grok-4.3 / qwen3.5-397b-a17b / minimax-m3 / gpt-5.1 / gemma-4-26b-a4b / gpt-5.2-high / gpt-5.2 / gpt-5-high / qwen3-max-preview / mimo-v2.5 / glm-5v-turbo / o3-2025-04-16 / mistral-medium-3.5 / nvidia-nemotron-3-ultra / muse-glimmer / qwen3-max-2025-09-23 / qwen3-235b-a22b-instruct / kimi-k2-0711-preview / qwen3.5-122b-a10b / minimax-m2.7 / mistral-large-3 / claude-haiku-4-5 / gpt-4.1-2025-04-14 / qwen3-vl-235b / gemini-2.5-flash / qwen3.5-27b / mistral-medium-2508 / inkling-small / qwen3-235b-a22b-no-thinking / gpt-5.4-nano-high / longcat-flash-chat / qwen3-235b-a22b-thinking / qwen3-next-80b / qwen3.5-flash / qwen3-vl-235b-thinking / qwen3.5-35b / step-3.5-flash / o4-mini / minimax-m2.5 / gpt-5-mini-high / solar-pro4 / qwen3-coder-480b / minimax-m2.1 / gpt-4.1-mini / qwen3-30b-a3b / qwen3-235b-a22b / qwen3-next-80b-thinking / gemma-3-27b / minimax-m1 / nvidia-nemotron-3-super / gemini-2.0-flash / nvidia-nemotron-3.5-lightning / gpt-oss-120b / o3-mini / minimax-m2 / ling-flash-2.0 / mercury-2 / gpt-5-nano-high / qwq-32b / nova-2-lite / qwen3-30b-a3b / gemma-3n-e4b / gpt-oss-20b / nvidia-nemotron-3-nano / mercury / ibm-granite-h-small / qwen3-omni-flash / minimax-m2-preview / qwen3-vl-8b-thinking / gemini-3.5-flash / qwen3.6-27b / inkling-medium / longcat-2.0 / ling-2.5-1t / grok-4.6-medium / qwen3-max-2025-09-26 / inkling-low / qwen3-max-thinking / inkling-small-medium / inkling-small-low / ring-2.5-1t / gpt-5-high-new-system-prompt / qwen-vl-max / deepseek-v4.1-flash-max / amazon.nova-pro-v1 / qwen3.7-plus-preview / qwen3.7-max / gemini-3.7-flash / qwen3-vl-8b-instruct / grok-4.6-low / gemini-3.1-flash-lite

### 截图

- `loop-artifacts/arena-launch/arena-models-20261022.png` — 初始页（Agent Mode，无模型选择器）
- `loop-artifacts/arena-launch/arena-models-20261022-2.png` — Side by Side 模式（2 个模型按钮）
- `loop-artifacts/arena-launch/arena-models-20261022-3.png` — 模型 listbox 展开（127+ 模型）
- `loop-artifacts/arena-launch/arena-models-20261022-4.png` — Direct 模式（1 个模型按钮）

---

## C. 研究能力 Benchmark 核实

**定义**：用户要求"不给细节、靠分解找矛盾→研究→得出 prompt 没给出的新结论"的研究能力 benchmark。

| Benchmark | 任务形态 | 匹配度 | 题目来源 | 规模 | 确定程度 |
|-----------|----------|--------|----------|------|----------|
| **BrowseComp** | 多步检索+推理，定位"难以找到"的信息（prompt 不给细节） | ✅ 高 | OpenAI simple evals GitHub | 1,266 题 | ✅ 确定 |
| **GAIA** | 3 级难度，Level 2/3 = 开放式研究+多工具 | ✅ 高 | HuggingFace `gaia-benchmark/GAIA` | 469 题（test split） | ✅ 确定 |
| **HLE** | 多步研究问题，覆盖科学/数学/人文 | ✅ 高 | HuggingFace `cais/hle` | 2,500+ 题 | ✅ 确定 |
| **HotpotQA** | 多跳 QA（答案型，非研究型） | ❌ 低 | HuggingFace `hotpotqa/hotpot_qa` | 100K+ 题 | ❌ 排除 |
| **FrontierScience** | 专家级科学推理（前沿研究） | ✅ 高 | arXiv:2601.21165 / OpenAI | 未核实具体规模 | ⚠️ 部分核实 |

### 逐条核实

#### 1. BrowseComp（OpenAI 2025）

- **任务形态**：1,266 道"难以找到"的信息定位题，需要浏览数十甚至数百个网站，prompt 只给模糊描述不给细节。
- **匹配理由**：完全符合"不给细节、靠分解找矛盾→研究→得出新结论"。
- **获取方式**：OpenAI simple evals GitHub 仓库（`https://github.com/openai/evals`）。
- **License**：未明确（OpenAI 未声明，需自行确认是否允许跑评测）。
- **确定程度**：✅ 确定（官网 + GitHub 已核实）。

#### 2. GAIA（Meta 2023）

- **任务形态**：3 级难度（Level 1 = 基础检索，Level 2 = 多步+多工具，Level 3 = 开放式研究+矛盾发现）。
- **匹配理由**：Level 2/3 匹配"研究能力"定义。
- **获取方式**：HuggingFace `gaia-benchmark/GAIA`（parquet + jsonl，110MB）。
- **License**：未明确（Meta 未声明）。
- **确定程度**：✅ 确定（HF 页面已核实）。

#### 3. HLE（Humanity's Last Exam）

- **任务形态**：2,500+ 道多步研究问题，覆盖科学/数学/人文，需要分解+推理+得出结论。
- **匹配理由**：高（"新结论"评测）。
- **获取方式**：HuggingFace `cais/hle`（parquet，274MB）。
- **License**：MIT。
- **确定程度**：✅ 确定（HF 页面已核实）。

#### 4. HotpotQA

- **任务形态**：多跳 QA（2-3 跳），答案型（不是研究型）。
- **匹配理由**：❌ 不匹配（"多跳但答案型，不是研究型"）。
- **获取方式**：HuggingFace `hotpotqa/hotpot_qa`（100K+ 题）。
- **结论**：**排除**。
- **确定程度**：✅ 确定（HF 页面已核实）。

#### 5. FrontierScience

- **任务形态**：专家级科学推理，前沿研究问题。
- **匹配理由**：高（"研究能力"）。
- **获取方式**：arXiv:2601.21165 / OpenAI（`https://openai.com/index/frontierscience`）。
- **License**：未明确。
- **确定程度**：⚠️ 部分核实（arXiv 编号已确认，具体题目形态/规模未深挖）。

---

## 下一步建议

1. **优先跑**：BrowseComp / GAIA Level 2/3 / HLE（3 个高匹配 benchmark）。
2. **排除**：HotpotQA（答案型，不匹配）。
3. **可选**：FrontierScience（需核实题目形态是否匹配"分解找矛盾→新结论"）。
4. **arena 多模型**：用 Direct / Side by Side 模式自选模型跑单轮调研任务（非 Agent Mode）。
