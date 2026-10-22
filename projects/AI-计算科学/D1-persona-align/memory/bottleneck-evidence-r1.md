# S1 本地证据盘点（r1 · 2026-10-22）

> origin: ai · goal-fb61fede round 1 · S1 本地证据盘点
> 数据来源：loop-state.json(33条change_log) / RESEARCH.md(207行) / SKILL.md(69行) / APPROVALS.md / TEST-CATALOG.md(107行)

## 事件清单

| # | 事件 | 根因 | 当前SOP是否覆盖 | 覆盖位置 |
|---|------|------|----------------|---------|
| 1 | decomp organizer subagent 挂（arena 提交成功但回复未落页，空等 20min+） | arena agent mode 页面异常（疑似 GitHub outage），subagent 无超时纪律，假设"提交成功=回复已落" | ✅ 已覆盖 | SKILL.md §失败处理 #1（落页校验 5min 超时） |
| 2 | persona researcher 87min 才落盘，期间无中间痕迹 | 单 subagent 领多子领域长任务，无 checkpoint 机制，挂掉后无法判断进度 | ✅ 已覆盖 | SKILL.md §失败处理 #5（>15min 先写 checkpoint） |
| 3 | persona researcher 交叉验证降级 ad-hoc（ChatGPT 页面漂移→arXiv 直核） | 无标准化降级路径，靠 subagent 临场判断 | ✅ 已覆盖 | SKILL.md §失败处理 #4（交叉验证降级记回执） |
| 4 | memory-hooks researcher 完成但交付物未落盘 | subagent 结束前未执行写文件步骤 | ⚠️ 部分覆盖 | SKILL.md §SOP 第5步（落盘），但无强制校验 |
| 5 | subagent 长任务（20-90min）挂 2 次/3 次 | 任务粒度过大，失败模式多，不可断点恢复 | ✅ 已覆盖 | SKILL.md §拆分优先（短任务多并行） |
| 6 | decomp TEST-CATALOG 降级自整理（arena 不可用） | 同 #1，arena 页面异常 | ✅ 已覆盖 | SKILL.md §失败处理 #2（降级阶梯） |
| 7 | git add -A 误提交 node_modules/.npmcache | 无 .gitignore 保护，盲加 | ❌ 未覆盖 | 无 SOP |
| 8 | qwen3.8-27b-w8a16 不回报 cache tokens | 引擎限制，fork 缓存收益本侧不可验证 | N/A（硬件层） | APPROVALS 条目2 背景段 |

## SOP 覆盖矩阵

### 已覆盖（5/8）
- 落页校验（#1）
- 长任务 checkpoint（#2）
- 交叉验证降级（#3）
- 降级阶梯（#6）
- 拆分优先/短任务并行（#5）

### 未覆盖（2/8）
- **交付物落盘强制校验**（#4）：SOP 第 5 步说"落盘"，但 subagent 可以结束而不写文件。需要：subagent 任务卡加硬约束"文件不存在=任务未完成"，Lead 侧加"收到完成通知后先 ls 确认文件存在"。
- **git 操作安全**（#7）：无 SOP 防止 `git add -A` 误提交构建产物。需要：派发前检查 .gitignore，或用 `git add <具体路径>` 替代 `-A`。

### 不适用（1/8）
- 引擎层 cache tokens（#8）：非 SOP 可解，已记 APPROVALS。

## 给 Lead 的建议

### S2 应该重点查什么
- arena agent mode 的**完整失败模式集**：除了"回复未落页"，还有哪些？（提交成功但 agent 没跑/跑了但输出格式错/会话被重置/多会话冲突）
- **成熟工具先例**：GitHub/LMArena/其他平台的 agent 任务流有没有类似 SOP？（搜索 "LMArena agent mode timeout" / "arena.ai agent workflow"）
- **ego-browser 侧的超时机制**：ego-browser 本身有没有 waitForFunction 超时/重试？还是全靠 subagent 自己写？

### S3 应该重点查什么
- "3-7 正交子领域"这个标准**本身对不对**：有没有更细（1 个 subagent 1 个 claim）或更粗（1 个 subagent 1 个领域）的业界实践？
- **分解树完备性检查方法**：怎么验证"拆完了"？（检查清单/正交性判据/覆盖率指标）
- **短任务 vs 长任务的阈值**：多少分钟算"短"？有没有实证数据？（本会话：≤15min 全部落盘，>20min 挂 2 次）
