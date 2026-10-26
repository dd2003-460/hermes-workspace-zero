# Step 12: arena 核验结果处理 + 模型修正 + 再推送

## 目标
处理 arena 的核验反馈：落实修正意见到两个子模块的模型和报告，产出 round-2，更新胜率记录，推送远程。

## 涉及文件
- `market-alpha/gpu-price-prediction/outputs/round-2/`（修正后预测）
- `market-alpha/transformer-sector-valuation/outputs/round-2/`（修正后估值）
- 两个子模块的 `reports/report.tex`（加"修订记录"节：round-1 → round-2 改了什么、为什么）
- `market-alpha/loop-artifacts/review-round1.md`（arena 反馈汇总 + 落实清单）
- 重新编译的两个 PDF

## 做法
1. 拉取 arena 的 review 产出（git pull 或 arena 会话内读取），汇总到 review-round1.md
2. 逐条处理反馈：
   - 模型 bug/逻辑漏洞 → 修 src/ 代码
   - 假设不成立 → 更新 assumptions.md + 敏感性分析
   - 数据错误 → 修正 config/data
   - 每条标注：采纳/部分采纳/不采纳（附理由）
3. 重跑 main.py 产出 round-2 结果，对比 round-1 变化
4. 更新 tex 报告（修订记录节 + 更新结果节），重新编译 PDF
5. 更新大仓库 INDEX/README 的状态列（各子模块当前轮次、胜率）
6. commit + push + ls-remote 验证

## 验收标准
- [ ] review-round1.md 含 arena 全部反馈条目的处理结论（无遗漏）
- [ ] round-2 输出存在且与 round-1 有可解释的差异
- [ ] 两个 PDF 重新编译成功，含修订记录节
- [ ] 远程 HEAD 更新（ls-remote hash 变化），仓库状态列更新

## 后续（goal 持续循环）
- 按 goal-template §3.0：继续调研技术信息差优化空间 → 新子模块候选（如其他专业硬件/板块）→ 每轮预测后检验胜率
- 下一轮预测触发：价格实际变动数据可得时，回测 round-1/2 胜率并修正
