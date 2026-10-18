# 减少无效思考 / 自适应思考 — 方法与文献调研

# origin: ai
# 日期: 2026-10 会话 (goal round 6+)
# 触发: 用户 m01132 "你有先搜索社区和论文的方法吗，我似乎在agents里面写了不要自己造轮子"

## 背景
目标 (m00002): qwen3.8-27b-w8a16 在 low 思考设定下 decode 是瓶颈；找 prompt 减少思考
或实现自适应思考（按难度给不同预算），不影响质量，不破坏 DSH/服务。

R3 实验自设计了 P0/P1/P5 三个 arm。本文件补上文献侧的方法地图，
把我们的 arm 映射到已有工作，并找出部署侧现成的 lever。

## 1. Qwen3 官方机制（最重要 — 不造轮子的正确姿势）

来源: https://raw.githubusercontent.com/QwenLM/Qwen3/main/README.md (HTTP 200)
      https://qwenlm.github.io/blog/qwen3/ (HTTP 200)
      https://hf-mirror.com/Qwen/Qwen3-8B/raw/main/README.md (HTTP 200)

三个官方 lever（按强度排序）:

1. **enable_thinking=True/False**（硬开关，chat template 参数）
   - `tokenizer.apply_chat_template(messages, enable_thinking=False)`
   - False: 完全不产生 </think> 块 → 真正省 decode token
   - True: API 总是输出 </think> 块（可能为空）
   - 注意: Qwen3-2507 起拆成 Instruct（仅 non-thinking）/ Thinking（仅 thinking）两个模型
     变体 — 对 2507，模式是模型选择而不是 prompt
2. **/think 与 /no_think**（软开关，写在 system/user 消息里）
   - 仅在 enable_thinking=True 时有效
   - 多轮对话遵循最近一次指令
   - 我们的 P1 'Answer only' prompt ≈ 软版 /no_think（prompt 级近似）
3. **Thinking Budget Control**（blog 标题功能）
   - blog: "Qwen3 exhibits scalable and smooth performance improvements that are
     directly correlated with the computational reasoning budget allocated"
   - thinking_budget.png: 平滑可扩展的 accuracy-vs-budget 曲线
   - "users can configure task-specific budgets"
   - 8B 模型卡里没有 thinking_budget 参数名；tech report = arXiv:2505.09388

官方采样建议: thinking T=0.6 TopP=0.95 TopK=20 MinP=0（禁 greedy）;
non-thinking T=0.7 TopP=0.8。
官方数学题 prompt: "Please reason step by step, and put your final answer within \boxed{}."

部署: vLLM `--reasoning-parser qwen3/deepseek_r1`; sglang `--reasoning-parser qwen3`;
OpenAI 兼容 API 会拆 reasoning_content / content。

## 2. DSH 原生 lever（用户部署里现成的 — grep app.asar 验证）

app.asar 是单文件（非目录），直接 grep 文件路径。命中:
- thinking_token_budget ×10
- thinking_budget ×4, thinking_budget_tokens ×5
- enable_thinking ×7
- thinking_level_switch ×6, thinking_effort ×6
- thinking_tokens ×11, thinking_dropped ×8, thinking_turns ×4

→ **DSH 原生暴露 thinking token budget + level/effort 开关**。
结论: prompt 级 P1 只是软近似；用户部署侧真正该测的是 DSH 的
thinking_token_budget（按难度分级）— 这是 serving 级 lever，不需要改 prompt。
（本会话无法从 subagent 侧改 thinking 预算 — subagent 继承会话配置；
该项给用户做部署级 A/B。）

## 3. 文献地图（Semantic Scholar keyless API；arXiv API 全 429 弃用）

主 survey: **"Stop Overthinking: A Survey on Efficient Reasoning for Large Language
Models"** — arXiv:2503.16419 (2025, Yang Sui et al., 清华/北大等)
project: https://github.com/Eclipsess/Awesome-Efficient-Reasoning-LLMs
三分法 taxonomy（与我们 arm 直接对应）:
1. model-based efficient reasoning（训练更省的模型）
2. reasoning-output-based（推理时动态减少步数/长度）← thinking_budget 属此类
3. input-prompts-based（按难度/长度控制 prompt）← P1/P6 属此类

我们的 arm 映射:
- P0 = 基线（show reasoning）
- P1 = direction (3) 的 answer-only 极端
- P5 = direction (3) + 格式纪律（STOP 规则）
- P6 = direction (3)+(2) 混合: 单 prompt 内自判难度 → 路由 easy/hard
- DSH thinking_token_budget = direction (2) serving 级

其他相关（Semantic Scholar 命中，未深读）:
- arXiv:2503.19602 "Innate Reasoning is Not Enough: ICL Enhances RLLMs with Less
  Overthinking" — CoT prompting 对 RLLM: 大模型简单任务提升小、复杂任务提升大；
  one-shot CoT 优于 few-shot；CoT 把 reflection 分布收窄（某些场景 ~90% 减少）
- arXiv:2506.04574 (financial sentiment) — 非推理任务上 CoT 反而有害（反向证据）

## 4. 对本项目的含义

1. **P1 不是自造轮子** — 它是 Qwen3 官方 /no_think 软开关的 prompt 级等价物，
   方向与官方一致；但我们自己测了它在我们模型上的质量边界（A09 类组合计数题
   需要思考时 P5 过紧会出错，P1 answer-only 在 8/8 已测任务 100% 正确）。
2. **P6 = 文献里的 adaptive 方向**（survey direction 3 的 difficulty 分支），
   单 prompt 实现，无额外 LLM 调用。
3. **给用户的最优建议（待 R3 收尾后给）**: 双层方案
   - prompt 层: 易题 P1 / 全题 P6 自适应
   - serving 层: DSH thinking_token_budget 分级（用户自测，我们给配置建议）

## 通道备忘（本次调研可用/不可用）
- web_search: DEAD（no DEEPSEEK_API_KEY）
- arXiv API (export.arxiv.org https): 持续 HTTP 429
- Semantic Scholar API: keyless 可用，低速率，并行 2 查询 1 个 429 — 单发可用
- huggingface.co / modelscope: 403；hf-mirror.com: 可用
- qwenlm.github.io / raw.githubusercontent.com: 可用
