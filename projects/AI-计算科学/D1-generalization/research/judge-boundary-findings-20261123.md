# P2 边界 case 测试发现（2026-11-23）
# origin: ai · 来源：① 本轮实跑（8787 27b + formula_judge.py）· 数据：/tmp/judge_boundary_v2.json, /tmp/real_outputs.jsonl, /tmp/hard_outputs.jsonl

## 发现 1：27b 数值题一次过率 100%（10/10），靠"让它算错"制造 judge 分歧这条路样本量不够
- 原型题（10B 吞吐，5 检查点）：A 条件 3/3 one-shot 全对，B 条件 3/3 一轮全对
- 难题（12B KV cache，5 检查点，含科学计数法 6.554e-05）：4/4 全对
- **含义**：judge 对比实验若用 27b 做被评模型，分歧只能来自边界 case，不能来自"模型算错"
- **置信度**：conf 0.8（样本 10 个输出，2 道题；但 27b 是本地默认模型，论文主实验用它，这个性质必须知道）

## 发现 2：judge prompt 敏感性 = 论文要测的核心维度之一
- v1 prompt（只说"2% 容差"，没明确整数规则）：把 max_batch=240（gold 238）判**对**
- v2 prompt（明确"tolerance=0 必须精确匹配，差 1 也算错"）：判**错**
- 同一模型同一输出，只改 prompt，判分翻转
- **含义**：LLM judge 的判分行为由 prompt 措辞驱动，不是稳定函数。这是"机械 judge > LLM judge"的直接证据之一（机械 judge 的整数规则是代码，不受措辞影响）
- **已固化**：JUDGE_PROMPT_VERSION v1→v2，formula_judge.py 整数检查点（tol=0）改精确匹配

## 发现 3：修复后两 judge 在边界 case 完全一致（3/3 case 无分歧）
- baseline_correct 5/5=5/5, near_miss_3pct 3/5=3/5, plausible_wrong 4/5=4/5
- **含义**：当 prompt 足够明确时，27b judge 和机械 judge 判分一致——分歧不是来自"能力差"而是来自"规则模糊"
- **对论文的影响**：核心 claim 要精确化——机械 judge 的优势不是"判得更准"（prompt 明确时两者一样准），而是**"判分行为稳定、可复现、不受 prompt 措辞漂移影响"**。这是可验证的 claim（跑 N 个 prompt 变体看翻转率），比"更准"更可证伪
- **下一步**：prompt 变体实验（同题 5-10 个措辞变体，测 LLM judge 翻转率 vs 机械 judge 0 翻转）——这是论文第一个可跑的核心实验，不依赖 arena 题集

## 发现 4：prompt 变体实验（8 变体 × 3 case × 5 检查点，n=24 调用）——论文第一个核心数字
# 数据：/tmp/prompt_variant_flip_v2.json · 8787 27b · 2026-11-23 实跑

**两个独立维度**（必须分开报，混了会得出错误结论）：

1. **判分准确性：翻转率 0/15**（可解析的 20 次调用里，8 个 prompt 变体在全部 15 个 case×checkpoint 上与机械 judge 完全一致）
   - 含义：prompt 足够明确时，27b judge 判得和机械 judge 一样准
   - **推翻了"机械 judge 判得更准"的朴素 claim**

2. **格式可靠性：LLM judge 17% 格式失败（4/24）vs 机械 judge 0%**
   - 失败模式：输出 `{"id": true}`（键名错）/ `{"correct": true}`（单布尔）/ 键不全
   - 这些失败**不可恢复**（单布尔广播会污染判分：把"全对"广播成 5 个 true，或把"全错"广播成 5 个 false）
   - Wilson 95% CI（n=24, k=4）：17% [6.3%, 38.3%]
   - **这才是机械 judge 的真实优势：格式可靠性 100%（代码保证）vs 83%（prompt 驱动）**

3. **副发现：prompt 严格度与格式合规负相关**
   - V1_严格（指令最细）格式失败 2/3，V4-V8（自然措辞）0/3
   - 含义：把判分规则写进 prompt 越严，模型越容易在格式上出错——规则复杂度和格式合规在竞争同一个输出预算

**论文核心 claim 精确化**（三轮迭代后的最终版）：
- ❌ 朴素版："机械 judge 比 LLM judge 判得更准"（被 0 翻转率推翻）
- ✅ 精确版："机械 judge 的判分行为**确定性可复现**（格式可靠性 100%，0 prompt 敏感性）；LLM judge 判分准确性在明确 prompt 下等价，但格式可靠性仅 83%（Wilson CI [6.3%, 38.3%]），且随 prompt 严格度波动"
- 这个 claim 可证伪：换更强模型 / 换任务域 / 加 n，看格式失败率是否仍显著 > 0

**样本量警告**：n=24 太小，17% 的 CI 很宽。正式实验需要 n≥100（10 题 × 10 输出 × 变体）。当前数字只作 pilot，论文里标 pilot。
