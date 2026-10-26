# Step 09: 核验反馈落实 + round-2 迭代 + 最终推送

## 目标
处理 arena T3 核验反馈：让 arena 落实修正产出 round-2（模型修正+报告修订记录+胜率更新），最终推送远程，完成 goal 第一轮闭环。

## 涉及文件
- arena 产出 round-2：两子模块 `outputs/round-2/` + 更新后的 `reports/report.pdf`（含修订记录节）
- `market-alpha/loop-artifacts/review-round1.md`（T3 反馈汇总+落实清单）
- 大仓库 README/INDEX 状态列更新（各子模块当前轮次、胜率）

## 做法
1. `git pull` 拉取 T3 review 产出，汇总到 review-round1.md
2. 发送 T4 修正指令给 arena（或新会话重发）：逐条落实 review 意见——模型 bug 修 src/、假设不成立更新 assumptions.md+敏感性、数据错误修正 config；每条标注采纳/部分采纳/不采纳（附理由）；重跑产出 round-2；更新 tex 修订记录节+结果节重编 PDF
3. 验收 round-2：与 round-1 差异可解释、PDF 重编成功、修订记录完整
4. 更新大仓库 README/INDEX 状态列（轮次=round-2、胜率数字）
5. 最终 commit + push + `git ls-remote` 验证 HEAD 更新
6. 本地 `git pull` 同步 workspace 副本（若 market-alpha 在 workspace 内开发则直接同步）

## 验收标准
- [ ] review-round1.md 含 T3 全部反馈条目的处理结论（无遗漏）
- [ ] 两子模块 round-2 输出存在，与 round-1 差异可解释
- [ ] 两个 PDF 含修订记录节（round-1→round-2 改了什么、为什么）
- [ ] 远程 HEAD 更新，大仓库状态列更新为 round-2

## 后续（goal 持续循环 · goal-template §3.0）
- 按 §3.0 继续：调研技术信息差优化空间 → 评估新子模块候选（其他专业硬件/板块）→ 价格实际变动数据可得时回测 round-1/2 胜率并修正
- goal 未 complete 前不结束；complete 后同回合创建下一 goal（含完整链路规则）
