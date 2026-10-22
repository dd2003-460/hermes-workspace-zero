# S2 arena 通道鲁棒性（r1 · 2026-10-22）

> origin: ai · goal-fb61fede round 1 · arena 不可用（#1 事件后降级），自答 conf -0.2
> 数据来源：bottleneck-evidence-r1.md（8 事件）/ SKILL.md 全文 69 行 / TEST-CATALOG.md 降级标注格式

## 失败模式全集

| # | 失败模式 | 本会话实证 | 触发条件 | 当前 SOP 覆盖 | 建议修复 |
|---|---------|-----------|---------|--------------|---------|
| F1 | 提交成功但回复未落页 | decomp organizer 空等 20min+（#1） | arena agent mode 页面异常 / GitHub outage / 后端超时 | ✅ 失败处理 #1（5min 超时 re-snapshot） | 超时阈值可考虑 3min（arena 正常响应 <2min）；re-snapshot 后若页面空白 → 直接进降级阶梯第 2 级，不再等 |
| F2 | agent 没跑（提交后无输出） | 未实测，理论可能 | 输入框定位错误 / 发送按钮未点中 / 页面未加载完 | ⚠️ 部分（SOP 第 2 步有 waitForFunction 但未区分"没跑"vs"跑了没输出"） | 提交后 30s 内无新 DOM 节点 → 判定"没跑"，re-snapshot 重新定位输入框+发送按钮，重试 1 次 |
| F3 | 跑了但输出格式错 | 未实测，理论可能 | 任务卡约束不够具体 / arena 模型随机性 | ❌ 未覆盖 | 任务卡模板加"格式校验"行：交付物必须是 markdown 表格/JSON，否则要求重写；Lead 侧收到后先 grep 关键字段 |
| F4 | 会话被重置 | 未实测，理论可能 | arena 后端重启 / 登录态过期 / 浏览器 profile 重置 | ❌ 未覆盖 | 提交前先 snapshot 确认登录态（页面有"退出"按钮=已登录）；任务卡标"若会话重置请从第 1 步重新开始" |
| F5 | 多会话冲突 | 未实测，理论可能 | 同一 ego-browser taskSpace 内开多 page 并发提交 | ❌ 未覆盖 | 同一时间只用 1 个 page 提交；多任务串行提交，等回复落页再提交下一个 |
| F6 | 长任务中途挂（subagent 侧） | persona researcher 87min 无痕迹（#2） | 单 subagent 领多子领域 / 无 checkpoint | ✅ 失败处理 #5（>15min 先写 checkpoint） | 已覆盖，无需改 |
| F7 | 交叉验证第二站不可用 | ChatGPT 页面漂移（#3） | 站点未登录 / 页面改版 / 地区限制 | ✅ 失败处理 #4（降级记回执） | 已覆盖，无需改 |
| F8 | 交付物未落盘 | memory-hooks researcher 结束未写文件（#4） | subagent 结束前未执行写文件步骤 / 任务卡未强制 | ⚠️ 部分（SOP 第 5 步"落盘"但无强制校验） | 任务卡加硬约束"文件不存在=任务未完成，Lead 不验收"；Lead 收到完成通知后先 `ls` 确认文件存在+行数>0 |

## 成熟 SOP 先例（自答，conf -0.2）

> 以下基于通用 LLM agent 工作流经验，未实际检索 arena.ai 官方文档或 GitHub issue。arena 不可用，无法验证是否有现成 SOP。

- **LMArena 官方**：arena.ai/agent 是 2025 年新功能，未见官方 SOP 文档（conf 0.3，未验证）。
- **GitHub LMArena 工作流**：社区有少量 blog post 提到"LMArena agent 适合多步调研任务"，但无标准化超时/降级 SOP（conf 0.3，未验证）。
- **ego-browser 侧**：ego-browser 本身提供 `waitForFunction` / `waitForSelector` / `waitForLoadState` 等超时机制，但**无内置"arena agent mode 专用"超时配置**——全靠 subagent 自己写超时逻辑（conf 0.7，基于 SKILL.md 代码块推断）。
- **通用 LLM agent 超时模式**（conf 0.6，行业通用）：
  - 提交后 30s 内无输出 → 判定"没跑"，重试 1 次
  - 3min 内无输出 → 判定"超时"，进降级
  - 5min 内无输出 → 判定"卡死"，杀进程+降级
  - 本会话 SOP 只定义了 5min 一档，建议细化为 3 档

## 给 Lead 的建议

### 降级阶梯是否需要调整
- **不需要改阶梯顺序**（agent mode → Battle → ego 直抓 → 自答），但建议：
  - F1 超时后直接跳 Battle（不 re-snapshot 第二次），节省 5min
  - F2"没跑"重试 1 次后若仍无输出 → 直接跳 Battle
  - 自答时 conf −0.2 已足够，但建议**在文件头加"降级原因"一行**（本文件已示范）

### 落页校验阈值是否需要调整
- **5min → 3min**（arena 正常响应 <2min，5min 太宽松）
- **加 30s 快检**：提交后 30s 内无新 DOM 节点 → 判定"没跑"，立即 re-snapshot
- **加 1min 中检**：30s 有输出但 1min 内无新输出 → 判定"跑慢"，继续等到 3min
- 三档：30s（没跑）/ 1min（跑慢）/ 3min（超时）→ 降级

### 新增 SOP 建议（未写入 SKILL.md，待 Lead 决策）
1. **F3 格式校验**：任务卡模板加"[格式校验] 交付物必须是 <markdown 表格/JSON>，否则要求重写"
2. **F4 登录态检查**：提交前 snapshot 确认"退出"按钮存在
3. **F5 串行提交**：同一 taskSpace 内多任务串行，不并发
4. **F8 落盘硬约束**：任务卡加"文件不存在=任务未完成"；Lead 侧 `ls` 确认

## 未覆盖 gap 汇总

| gap | 失败模式 | 严重度 | 建议 |
|-----|---------|--------|------|
| G1 | F2 没跑 | 中 | 30s 快检+重试 1 次 |
| G2 | F3 格式错 | 低 | 任务卡格式校验行 |
| G3 | F4 会话重置 | 低 | 登录态检查 |
| G4 | F5 多会话冲突 | 低 | 串行提交 |
| G5 | F8 落盘未强制 | 高 | 任务卡硬约束+Lead `ls` 确认 |
