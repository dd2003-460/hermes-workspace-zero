# Step 08: arena 产出验收 + 核验任务追加

## 目标
验收 arena 对 T1/T2 的产出（模型+报告+PDF），不达标则返工；达标后追加核验任务 T3（反方复核：找模型假设漏洞、方法缺陷、数据错误）。

## 涉及文件
- `market-alpha/tasks/T3-model-verify.md`（核验任务书）
- `market-alpha/loop-artifacts/acceptance-round1.md`（验收记录）

## 做法
1. `git pull` 拉取 arena 产出，逐项对照 T1/T2 验收标准检查：
   - GPU：predictions.json 结构、TCO 复算、report.pdf 编译成功、假设表完整
   - 变压器：思源分解复算一致、目标价表 ≥8 家、report.pdf 成功、全球对比表
2. 不达标项 → 写返工指令发回 arena 会话（列明具体不符项+期望）
3. 达标 → 写 T3 核验任务书（≤50 行）：
   ```
   【任务 T3：两子模块模型反方核验】
   走 1-loop，重点 04.5 反方复核：
   1. GPU 模型：假设是否成立（卡型生命周期/价格口径）、TCO 参数合理性、预测方法逻辑漏洞、回测胜率可信度
   2. 变压器模型：估值假设（目标PE/EPS）、贡献因子分解框架适用性、数据缺口补全建议（海外估值快照/个股历史分位/筹码结构/招标均价/技术面）
   3. 产出 loop-artifacts/stages/04.5/review-gpu.md + review-transformer.md，每条问题给严重度+修正建议
   ```
4. commit + push T3 → arena 会话发送 T3 指令
5. 验收记录落盘 acceptance-round1.md

## 验收标准
- [ ] T1/T2 产出全部通过验收（或返工后通过），acceptance-round1.md 记录逐项结论
- [ ] T3 任务书已推送（断点 B 过）
- [ ] arena 已接收 T3 并开始产出 review 文件
