# origin: ai
# D1-think-token-budget — 减少无效思考 / 自适应思考预算

## 目标（用户 m00002 直接指令）
模型 = qwen3.8 27b w8a16，在 low 思考设定下 **decode 时间是主要瓶颈**
（prefill 吃不满，decode 压力大）。decode 时间 ∝ 输出 token 数
（思考 token + 答案 token，全部都要 decode）。

用户要求（不许造成 dsh 退出/服务退出的破坏性行为；prompt 可自由在 subagent 上测试）：
1. 找到能**有效减少思考**或实现**自适应思考**的 prompt
   （按问题难度 + 操作可逆性给不同思考预算）。
2. **不影响质量**，尽可能减少无效思考。
3. 质量检测用 HF 官方测试 qwen3.8 27b 的 benchmark，挑难的、易错的。
4. 可用 ego-browser 网上调研方法（若可能影响服务就别动，给结论）。

## 核心洞察（R1 实测，来自 2 个 pilot）
- **subagent 的思考是"可见"的**：其 reasoning 会出现在 "sent a message"
  与 "closing message" 里 → 可以**测量**（chars 作为 output token 的 proxy，≈chars/4）。
- 即使 prompt 写"只给答案"，模型仍会花 token 做**元思考**
  （如 "I'm a subagent sending results back to the parent..."）= 无效思考。
- pilot 同题（10 次抛硬币恰好 6 次正面 = 105/512）：baseline ~750 chars，
  minimal ~300 chars → 输出量差 ~2.5×，两者都对。**答案冗长 + 元思考**是两大可砍源。

## 实验设计
- **任务集**：`tasks/taskset.py` — 12 道 AIME 风格硬数学/逻辑陷阱题，
  每题答案由 Python 计算（ground truth，可自动判分）。easy 3 / medium 4 / hard 5。
- **条件（treatments）**：`prompts/conditions.md`
  - P0 baseline（鼓励推理）
  - P1 minimal（只给答案）
  - P2 oracle（禁元叙述，反 subagent 角色旁白）
  - P3 adaptive（先一行 LEVEL 判档，再按档给思考预算）← 用户要的自适应设计
  - P4 wordcap（≤15 词硬上限）
- **指标**：每条件 × 任务 → surfaced-output chars（≈decode token proxy）+ 正确率。
  找 length-vs-accuracy 前沿：最低 chars 且 (近) 最高正确率的条件胜出。
- **判分**：`tasks/scorer.py <raw_dir>` — 读 `raw/<cond>__<task>.txt`，
  解析 FINAL 行判对错 + 计 chars，输出 CSV + 表。

## 安全边界（用户红线）
- 只在 subagent 上测 prompt；不碰服务端、不碰部署配置、不做任何
  可能导致 dsh/服务退出的操作。纯只读 HTTP 调研 + 本地 Python + subagent。
- 不修改 AGENTS.md（红线文件）。

## 文件
- `tasks/taskset.py` — 任务集 + ground truth（自测全过）
- `tasks/scorer.py` — 判分器
- `prompts/conditions.md` — 5 个 prompt 条件
- `results/round1/raw/` — 原始 subagent 输出（`<cond>__<task>.txt`）
- `results/round1/scores.csv` — 判分结果
- `memory/` — 探索记录

## 结论（滚动更新）
- 见 `memory/findings.md`
