# origin: ai
# T-PUB-1 A/B v2 + full7 汇总（2026-11-23 晚批跑完成）

## 1. 秩亏题 A/B（中文报缺口修复版，rd_ab_v2.json）

提醒词改为中文「检查关键参数完整性…缺失/冲突则明确报缺口、不编造」。

| 题 | A裸 c1报缺口 | B提醒 c1报缺口 | Δ |
|---|---|---|---|
| Q08（缺显存容量） | False（用记忆 80GB 补全→答 fit） | **True**（"显存容量缺失，无法确定唯一答案"） | +1 |
| Q09（缺带宽行） | True（报缺口但**用记忆 3.35TB/s 编出 100tok/s**） | True（报缺口且**不编**，"不可假设"） | =（c3 +1） |
| Q10（双源带宽冲突） | False（自行选 Source B 给 60tok/s） | **True**（"无法给出唯一确定答案"，双值并列） | +1 |

**报缺口率：A 1/3 → B 3/3；不编造率（c3）：A 2/3 → B 3/3**

与 v1（英文提醒词）结论一致：v1 也是 1/3→3/3，Q09 关键翻转相同。中文提醒词修复了 v1 里 Q08/Q10 的"提醒词语言不匹配"混淆（模型输出语言与提醒词语言不一致可能稀释效果）。

**关键证据（Q09 A 臂原文）**：模型自己写了 "the spec excerpt does not provide GPU memory bandwidth. **However**, the NVIDIA H100 SXM is publicly documented to have 3.35 TB/s…we proceed with this known value"——**识别缺口是内在能力（它明确说了 missing），补全缺口是默认行为（However 之后直接编）**。提醒词翻转的正是 However 这一步。

## 2. full7 重跑（full7_rerun.json，formula_judge 机械判分）

**初判 29/35 = 82.9% → 判分器修复后 33/35 = 94.3%**

初判的 3 个单点 FAIL 全部是判分器 bug（非模型错）：
| 题 | FAIL | 模型答的 | gold 期望 | 判分器 bug |
|---|---|---|---|---|
| Q01 c3 | bytes/step | 57.77 GB | 57,769,803,776 bytes | 不做单位换算（GB vs bytes） |
| Q03 c1 | dense FLOPS | 989.5 TFLOPS | 989.5e12 FLOP/s | 不做单位换算（TFLOPS vs FLOP/s） |
| Q07 c1 | τ=RC | 1.551e-5 s | 0.00001551 s | regex 不认科学计数法 `e-5` |

修复（scripts/formula_judge.py，6 个测试全过含回归）：NUM_RE 支持科学计数法；所有数值匹配分支加 SI 前缀换算（×1e3/1e6/1e9/1e12，tolerance 足够紧不会误判——"回归: 真错不该被放过" 999.5 vs 989.5 TFLOPS 仍正确判 False）。

修正后逐题：
| 题 | 得分 | FAIL | wall | 备注 |
|---|---|---|---|---|
| Q01 | 5/5 | — | 29.9s | c3 判分器修复 |
| Q02 | 5/5 | — | 8.8s | |
| Q03 | 5/5 | — | 21.2s | c1 判分器修复 |
| Q04 | 3/5 | c4,c5 | 52.1s | **模型真没收口**：7334 字符全是思考链（KV 头分片反复自我怀疑），没输出最终答案块，c4/c5 数值确实不存在 |
| Q05 | 5/5 | — | 37.0s | |
| Q06 | 5/5 | — | 27.2s | |
| Q07 | 5/5 | — | 42.0s | c1 判分器修复 |

**总计 33/35 = 94.3%，全对题 6/7（仅 Q04 首轮收口失败）**

Q04 归因（11-23 晚重跑修正）：首轮 3/5（c4/c5，7334 字符全是思考链没收口）。**同 prompt 重跑（base, max_tokens=4000）直接 5/5**（23.3s, 2352 字符）；close 变体（强制 FINAL ANSWER 块 + max_tokens=8000）也 5/5 但输出 13871 字符（啰嗦，不推荐）。**结论：Q04 失败是单样本随机波动（temperature=0 仍有波动，MTP 采样），不是系统性 prompt 缺陷**。
→ 方法学含义（对论文更重要）：27b 在难题上单样本可靠性波动显著（Q04 两次 run 2/5↔5/5），单样本评测的分数带 run-to-run 噪声；这是"为什么需要验证器/多次采样"的实证动机。full7 的 33/35 应报为"单样本点估计，Q04 有波动"，不报成稳定 94.3%。

## 3. 与 workshop 元认知轴的衔接（D 11-23 问"断裂是否 prompt 引起"的落点）

三层数字的准确 framing（已修正 decomp P3）：
- **发现** gap_rate≈10%（自发≈2%，82% 来自 prompt 指示的 [待核验] 标签，supp43/45）
- **分类** healthy_gap_rate≈84%（已标 degraded 节点的分类质量，非发现率）
- **修复** rework fix rate≈1.6%（harness 机制弱点，裸 baseline 里结构上=0）

本 A/B 实验 = 裸 baseline 代理的最直接证据：裸 prompt 报缺口 1/3，harness 提醒后 3/3。
**结论：发现侧断裂 = prompt 脚手架撑起来的（2%→10%）；修复侧断裂 = harness 机制真实弱点（1.6%），不是 prompt 假象。两侧成因不同，不能合并成"模型没有补缺口意识"。**

## 4. 待办
- [ ] Q01/Q03/Q07 单点 FAIL 逐条归因（gold 口径 vs 真错）
- [ ] Q04 收口问题：prompt 加"必须输出最终答案块"约束后重跑
- [ ] n=3 太小，秩亏题扩到 n≥10 出 CI（stats-protocol 已定义 Wilson CI）
