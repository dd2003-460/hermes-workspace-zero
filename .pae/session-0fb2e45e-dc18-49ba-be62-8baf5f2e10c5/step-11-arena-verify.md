# Step 11: arena 核验任务书 + 派发

## 目标
按 arena-loop-pipeline SOP 向 arena 派发核验任务：核验两个子模块的模型问题（假设漏洞、方法缺陷、数据错误），arena 走 1-loop 流程执行。

> ⚠️ 外部动作：向 arena 派活，需用户确认。

## 涉及文件
- `market-alpha/sop/arena-loop-pipeline.md`（从 workspace agents/ 复制）
- `market-alpha/loop/prompt-first/`（7 个阶段文件，从 workspace loop/ 复制）
- `market-alpha/tasks/T1-gpu-model-verify.md`（GPU 模型核验任务书）
- `market-alpha/tasks/T2-transformer-model-verify.md`（变压器模型核验任务书）
- 推送以上文件到远程（断点 A/B 门禁）

## 做法
1. 复制 loop + SOP 到仓库（rsync loop/prompt-first/ + cp SOP），commit + push，ls-remote 验证
2. 写两张任务书（≤50 行/张），顶部含强制段（必读 sop/arena-loop-pipeline.md + loop 阶段）：
   - T1：核验 GPU 价格预测模型——假设是否成立、TCO 参数是否合理、预测方法有无逻辑漏洞、回测胜率是否可信；产出 loop-artifacts/stages/04.5/review-gpu.md
   - T2：核验变压器估值模型——估值假设、贡献因子分解框架、数据缺口补全建议；产出 review-transformer.md
3. commit + push 任务书，验证 `git log -1 -- tasks/T1-*.md`
4. ego-browser 打开 arena.ai/agent 新会话 @market-alpha，发送任务指令（引用 tasks/T1、T2）
5. 记录 arena 会话 URL 到 `market-alpha/loop-artifacts/arena-session.md`

## 验收标准
- [ ] 远程仓库含 loop/prompt-first/（7 文件）+ sop/ + tasks/T1、T2
- [ ] 任务书顶部强制段存在（4 条必读）
- [ ] arena 新会话已创建并发送指令，会话 URL 记录落盘
- [ ] push 后 ls-remote hash 更新（断点 A/B 都过）
