# origin: ai
# T-PUB-1 论文成文数据表（2026-11-23，所有数字带出处）

## 主结果（full7，27b 裸 prompt，judge 修中文 keywords + 科学计数法/SI 单位换算后）

- 检查点通过率：33/35 = 94.3%（修复前 29/35 = 83%，3 个单点 FAIL 全是判分器 bug 非模型错）
- 全对题：6/7（仅 Q04 首轮收口失败）
- Q04 归因（11-23 trunc_mitigate 修正）：mt4000 时 7334 字符中文思维链被 4000 token 截断→2/5；mt12000 时 2583 字符收口→5/5。**主因=max_tokens=4000 对中文思维链不够用（截断），次因=采样波动**（同 mt4000 重跑能 5/5）。full7 分数带截断伪影 + run-to-run 噪声，评测协议应 max_tokens≥12000
- 方法学含义：27b 难题单样本可靠性波动显著 + 固定 max_tokens 系统性低估难题得分 = "为什么需要验证器/多次采样/足够 max_tokens"的实证动机
- 判分器修复（scripts/formula_judge.py，6 测试全过含回归）：Q01 c3（57.77 GB vs bytes）、Q03 c1（989.5 TFLOPS vs FLOP/s）单位换算 + Q07 c1（1.551e-5）科学计数法 + LaTeX 科学计数法（`1.551 \times 10^{-5}`，trunc_mitigate 暴露，`_clean_latex_sci` 预处理）
- 出处：tasks/T-PUB-1/full7-rerun.json + q04-close-rerun.json + trunc-mitigate.json + rd-ab-v2-summary-20261123.md §2

## A/B 状态机提醒实验（3 秩亏题）

- 报缺口率 c1：A 1/3 → B 3/3
- 不编造率 c3：A 2/3 → B 3/3
- Q09 关键翻转：A 编造 100 tok/s（用记忆 3.35TB/s 补全缺失带宽行）→ B 不编
- v2（中文提醒词）复跑结论一致（rd_ab_v2.json）：A 臂与 v1 相同（Q08/Q10 自行补全/选源不报缺口），B 臂 3/3 报缺口
- 出处：tasks/T-PUB-1/rd-ab-results.json + /tmp/rd_ab_v2.json + rd-ab-v2-summary-20261123.md §1

## 逐题明细

| 题 | 类型 | 判分 | wall | out_len |
|----|------|------|------|---------|
| T-PUB-1-Q01 | full | 5/5 | 29.9s | 2061 |
| T-PUB-1-Q02 | full | 5/5 | 8.8s | 1565 |
| T-PUB-1-Q03 | full | 5/5 | 21.2s | 1735 |
| T-PUB-1-Q04 | full | 3/5→5/5* | 52.1s→23.3s | 7334→2352 |
| T-PUB-1-Q05 | full | 5/5 | 37.0s | 6945 |
| T-PUB-1-Q06 | full | 5/5 | 27.2s | 2165 |
| T-PUB-1-Q07 | full | 5/5 | 42.0s | 5412 |
| T-PUB-1-Q08 | rank-deficient A | c1=False/c3=True | 9.1s | 1108 |
| T-PUB-1-Q08 | rank-deficient B | c1=True/c3=True | 29.6s | 591 |
| T-PUB-1-Q09 | rank-deficient A | c1=True/c3=False | 18.2s | 1848 |
| T-PUB-1-Q09 | rank-deficient B | c1=True/c3=True | 12.1s | 435 |
| T-PUB-1-Q10 | rank-deficient A | c1=False/c3=True | 15.2s | 1005 |
| T-PUB-1-Q10 | rank-deficient B | c1=True/c3=True | 17.6s | 1080 |

\* Q04 首轮 3/5（mt4000 截断中文思维链，7334 字符没收口），mt12000 重跑 5/5（2583 字符收口）——主因截断、次因采样波动（trunc-mitigate.json）。

## 待补

- [x] Q04 截断缓解（11-23 trunc_mitigate 完成）：mt4000→2/5（截断）vs mt12000→5/5 → **主因=max_tokens 截断，次因=采样波动**；评测协议应 max_tokens≥12000
- [ ] 秩亏题 n=3→n≥10 出 Wilson CI（stats-protocol 已定义口径）
