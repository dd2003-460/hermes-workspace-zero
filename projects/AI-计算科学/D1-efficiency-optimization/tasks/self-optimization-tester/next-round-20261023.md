# 第 3 轮 Goal 草案（防忘落盘 · §3.0 规则）

> origin: ai · 2026-10-23 · 由 goal-7f13fc7f rev2 完成后落盘；Lead 创建 goal 时以本文件为底稿

## 目标（P-1 自身优化）
消除 bench 的 n=1 自评折损 + 落地 M7 gate：在 3 次独立 run 上重跑 §3.0 链路，报告 M1-M6 方差 + M7 验证溯源率，使总加权分 conf ≥ 0.9。

## 五字段（goal-template §3）
1. 【目标】M1-M6 跨 run 方差 + M7 gate 实现（Verification Traceability Rate 作为硬门槛）
2. 【质量原则】充分调研（已有 r2 双源回执，引用 web-llm/cross-check-r2.json 不重查）；先复刻再创新
3. 【SOP 索引】agents/arena-loop-pipeline.md + stages/04.5/bench.md（指标固定落点，引用不重定）
4. 【验收标准】
   - n≥3 run，M1-M6 各指标 std 报告；总加权分均值 conf≥0.9
   - M7 gate 进 loop 工件：每步声称成功必须挂 ≥1 个不可伪造锚点（测试返回值/ls-remote 回执/fs diff），无锚点=该步不得声称成功
   - 权重校准：M1×M5 相关系数实测（消除"加权重复奖励同一行为"缺陷）
   - push pfb + ls-remote 验证
5. 【失败降级】arena 通道不可用 → 本地 run（conf 降档）；阻塞跳过不中断循环

## 自主探索循环（§3.0 全节）
[0] 持 goal → 找目标（P-1）→ arena 通道（ego-browser arena.ai/agent）→ 连仓库 dd2003-460/prompt-first-bench（ls-remote 验证）→ 中转模式（pull→rsync→cp sop→tasks 任务书含强制段→push→ls-remote→arena 拉取）→ arena 走 loop 01→04.5（断点 A/B/C）→ 交叉验证（≥2 LLM）+ 推理矛盾漏洞 → 拿漏洞迭代（conf≥0.7）→ 0.9 比例指标+总加权高于开源 bench（落点 stages/04.5/bench.md）→ 发布（commit+push+ls-remote）→ 找新目标（新 goal 含完整链路规则）

## 优先级
P-1 自身优化 > P-2 外部项目 > P-3 新目标探索。同一问题 2 轮无新事实 → 换工具。
