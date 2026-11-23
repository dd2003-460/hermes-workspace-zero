# CodeARC smoke test：27b 调试策略是语义匹配，非信息论最优（2026-11-20）
# origin: ai
# 来源①：/tmp/codearc-probe 本地跑，output/ 产物 + trace。

## 设置
- CodeARC (arXiv 2503.23145) repo，本地 8787 qwen3.8-27b-mtp
- reasoning_guided 策略，mdr=1（max_debug_rounds=1，只有 1 次 debug check），mi=30
- n=5（P0-P4），anonymous + annotated
- 参照：o3-mini 在 CodeARC 52.7%（论文，debug 轮数更多，非公平对照）

## 结果
- 27b：0/5（0%）。P2/P4 mokav.Equiv=False（differential testing 判不等价）；P0/P1/P3 有 invalid syntax（生成代码语法崩）
- **caveat（2026-11-20 修正）**：mi=30, mdr=1 是 evaluate.py 的**默认配置**（mdr=0 仅 sft_distillation 策略），即论文 o3-mini 52.7% 的同款设定 → **0/5 vs 52.7% 是公平对照**，27b 差距是真实的。n=5 太小，n=20 重跑中（proc_f1d50177bcf5）。

## 核心定性发现（对"理论/实操割裂"问题的实证）
P4（calculate_gcd，符号规则）完整 trace 显示 27b 的调试是**语义模式匹配，不是信息论最优**：
1. 先猜 math.gcd(a,b) → 反例 (7,-3)→-1≠1（符号错）
2. 生成 10 个查询探符号规律
3. 归纳"符号=第二个参数符号"，10 样本全对，自信实现
4. 仍挂：(-5,0) 真值 -5，规则给 +5——没单独探"a负 b=0"边界，语义归纳外推翻车

理论最优策略会系统性独立探每个参数符号，不会栽这种边界。**LLM 不维护错误假设空间、不做二分定位，靠自然语言归纳 + 样本外推**——这正是"理论/实操割裂"的活样本。

## 对 novelty 的诚实判断（未定论）
- 宽泛"理论/实操割裂"：ML 老主题（泛化 gap 等），**不新**（conf 0.8，凭记忆未本轮验证）
- 窄主张"LLM agent 不会自发用信息论最优调试策略"：**可能新，未查文献**——待 collision-research 外查
- 可实证方向：对照 oracle 反馈（单反例 vs 批量结构化反馈），看轮次长尾被压缩多少。若批量显著压长尾 → 割裂实锤（LLM 不自发最优，需外部喂信息）

## 待办
- [ ] collision-research 外查窄主张（arXiv：LLM debugging strategy / information-theoretic optimal exploration / agent oracle design）
- [ ] 若窄主张未撞车 → 立 goal：oracle 反馈信息设计实验（单反例 vs 批量反馈 × 轮次/成功率）
- [x] 公平对照核验：evaluate.py 默认 mi=30, mdr=1 = 论文参考配置 → 0/5 vs 52.7% 公平（2026-11-20 修正，原"mdr=1 苛刻"caveat 错误）
- [ ] n=20 重跑（proc_f1d50177bcf5）拿可靠分数
