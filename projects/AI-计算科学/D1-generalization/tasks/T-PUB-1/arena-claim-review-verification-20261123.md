# origin: ai · W6 claim-review 回执核验记录（Lead 独立复核，2026-11-23 20:05）

## 回执核验序列（skill 规定，全走 git）
1. ✅ fetch 显式 refspec：`origin/arena/423a71ef-hermes-workspace-zero`（commit `df4e5d6d`）
   - 注：agent 首轮交付 commit `256a9caf` 在 arena 工作区重置时丢失（agent 自述"HEAD 回到 ea57293，本地对象库和远端均未找到"），
     经 Lead 批准后基于工作区仍存报告文件 recommit → `df4e5d6d`。报告内容经 agent 确认与原稿一致（53 行）。
2. ✅ `git show --stat df4e5d6d`：diff 范围 = 1 file changed, 53 insertions（只有报告文件，无 .hooks/ 等污染）
3. ✅ 任务书指纹独立复算：`git show origin/main:.../arena-claim-review-task-20261123.md | shasum -a 256`
   = `609ad29a106eb7ec…` 与派发记录一致 → agent 读的是正确任务书
4. ✅ 报告全文 53 行完整：F1-F5 逐条（强度/文献重叠/攻击点/conf/建议）+ 检索附录 + 最终决策表

## Lead 独立核验（不信 arena 汇报，复算关键 claim）
### ① Q04 gold 错误（arena conf=0.99）— **独立核验通过**
- 题面原文（data/tpub1_extracted.json prompts.T-PUB-1-Q04）：
  "Weights and KV are sharded evenly across the 8 GPUs by TP" + (d) "KV bytes per token (per GPU, after sharding the KV heads)"
- 复算：KV pool/GPU = (80 − 405/8 − 5.5)×1e9 = 23.875e9 B；分片后 kv/token/GPU = 2×126×(8/8)×128 = 32256 B
  → floor(23.875e9 / (16384×32256)) = **45**
- 现存 spec c5 gold 公式 `126*8*128*2` = 258048（未分片）→ batch=5。**gold 写错，正确答案 45。**
- 交叉证据：q04-close-rerun.json base run（干净 2352 字）模型独立算出 45 且 c1-c5 全 true——
  若 gold=5 则 c5 应 false，judge 判 true 说明 judge 与 gold 不一致（判分逻辑 bug，与 arena 报告一致）。
- 另 arena 指出 spec 的 `checks.batch8_at_16384_fits: 0` 也错（batch 8 实际可装，约 4.23 GB/GPU）。

### ② 2026 年新文献 arXiv ID 真实性（防幻觉引用）
- 2610.30512 = "Behind Aggregate Scores: What Systematically Varying Arena-Hard's LLM Judge Reveals" ✅ 存在，与报告描述（judge 判决解析失败/截断）吻合
- 2603.05399 = "Judge Reliability Harness: Stress Testing the Reliability of LLM Judges" ✅ 存在
- 2611.11074 = "System Prompts Affect Response Bias More Than Discriminability in LLM Safety" ✅ 存在
- 2410.12784 (JudgeBench ICLR'25) / 2409.04168 (Stephan) / 2410.05229 (GSM-Symbolic) / 2410.07137 (Null Models) / 2501.10868 (JSONSchemaBench)：此前核验过存在

### ③ arena 自述方法学缺口（登记，conf 上限限定）
- 检索时误调用两次仓库禁用的 web_search（费用未验证）→ 已登记，结论引用时带"检索不保证穷尽"限定
- 实验实际发生日期未验证（会话系统日期 2026-11-20 早于稿件文件名 20261123）
- "不读题数字枚举"复现非预注册盲测（构造前已看过部分 spec/gold）→ 不能估实际攻击率，只证明机械判分可被构造性骗过

## 评审核心结论（报告原文摘要，详见 arena-claim-review-20261123.md @ df4e5d6d）
- F1-F5 强度 3/2/1/1/2；主会可投性 conf=0.08 → **建议转 4 页 workshop 个案**
- 三个致命点：
  1. F3"翻转≈硬币"：文字 c2 恒判 False 污染分歧率（剔除后 V1 27/45、V2 17/33、V3 45/96，仍非修正后准确率）
  2. F4 瞎猜界：`guess_bound.py` 对数值 fact tol=0 用严格 `<0` 判断恒不命中 → 多题零命中是程序构造的，不能称模拟验证了解析界
  3. 统计：0/2000 的 95% 上限 ≈1.5e-3，不能验证 3.3e-5；原稿误称 0.01 > 0.0267
- 最小强化动作（≤3）：① 删普适因果/硬币/防hack/必然trade-off 措辞 + 补撞车文献 ② 修判分+盲审参考+留 raw 重算 ③ 扩 ≥30 独立题 + 2 异家族 judge 配对

## 待执行（按性价比）— 1-4 已完成 @ 7b593678
1. ✅ **修 Q04 gold**（c5 公式改分片版 32256，checks.batch8 改 1）— 完成
2. ✅ **修 guess_bound.py** tol=0 分支（`<0` → `<=tol` 或对称容差）— 完成
3. ✅ **措辞降级**（F3/F4/F5 按建议改 intro+findings）— 完成（3 处：F4 因果归因、模拟措辞、F3 硬币措辞）
4. ✅ **统计修正**（0/2000 降级为 underpowered；0.01/0.0267 笔误清除）— 完成
5. ⏸ 扩题+异家族 judge（大工程，workshop 投后可做）

## 补充核验（Lead 独立，2026-11-23 20:20）
- **arXiv 文献计数**：intro/related-work 写"600+ papers in 2026 alone"。arXiv API 实测 `all:"LLM judge" AND submittedDate:[2026]` = **1,139 篇**（all-time 1,393）。"600+" 技术上正确（1139>600）但偏低 ~2×，且 arena 未 flag。
  - 处置：不阻塞（非事实错误，是保守表述）；若审稿人挑战可改为"1,000+ papers in 2026"或引用 arXiv 检索式。[待 D 决定是否改]
- **fig3 重跑**：Q04 gold 修正后 guess_bound 界值变化（Q04 从 text-gold 驱动改为 boolean 驱动），fig3-guess-bound.png 已用新 spec 重生成。
