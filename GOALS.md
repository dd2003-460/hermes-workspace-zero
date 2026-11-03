# GOALS — 目标队列（keepalive L2）

每轮 keepalive 醒来先读这里，按优先级推进。触发条件满足才开工，不满足就等下一个可执行目标或做维护性巡检。

## ★ 行为准则（成璐 2026-11-03 指令）
- **没事时主动找新活 + 发掘成璐的 idea 去调研**，不是发巡检废话。
- 找活来源：① 本文件链式目标 ② `projects/ACTIVE-candidates.md` 候选池（open 优先）③ 成璐原始 idea（raw-human / ai-chats / research-prompt/raw）。
- 选中方向 → 按 `agents/goal-template.md` §1 五字段建 goal（create_goal），整条 loop 外包 arena（§2），Lead 只发任务书+验收。
- 播报只报**实质进展**（新立项/解锁/阻塞变化/关键数字），无变化就闭嘴（stop_hook 已加内容去重兜底）。

## 链式目标

### G1: pfb/decomp 研究完成 → 研究"激发煮东西"
- **前置**：pfb blocked_human（02.5 交叉验证，等 web-llm 登录 ≥2 成功回执）；decomp active（T7 收口 4/4 PASS）。
- **触发条件**：pfb status → done/closed，且 decomp 无新卡点。
- **动作**：stage_init 立项"激发煮东西"——1-loop 信息调研（GitHub/arXiv/网页 LLM 交叉验证）→ 行动分解。范围待成璐补充定义。
- **状态**：waiting（等 pfb 解锁）

### G2: T17 full01 benchmark 跑完 → 出分对比
- **前置**：runner (PID 62585) 健康，conv3 Questions ~94% (569/604, q173)。
- **触发条件**：runner 退出 + 结果目录出现最终汇总文件。
- **动作**：聚合各 cutoff 分数 → 对比表 → 更新 decomp loop-state。
- **状态**：running（监控中，无需干预）

### G3: 金融·正交信号源（候选 #1，open）★当前最高优先可执行
- **来源**：ACTIVE-candidates.md #1（hermes-workspace-zero / D1-financial-market-analysis）。
- **现状**：F7 三市场组合 FAIL（信息冗余），F10 agent-game-model 探索中。
- **本轮动作**：按 goal-template §1 建 goal → 外包 arena 调研「链上资金流 / 期权 skew 数据可得性」→ 定 F8 实验设计。
- **验收**：调研产出 ≥3 独立源 + conf≥0.7 + 数据可得性结论 + F8 实验设计草案落盘。
- **状态**：ready（arena 通道已确认可用：ego-lite 进程活着 + ego-browser CLI 在位）

## 维护性兜底
无可执行目标时：扫 workspace git status / 各项目 loop-state.json / memory 蒸馏，保持台账准确。

---
# origin: ai (2026-11-03, 成璐指令：hook 应是 goal template——没事找新活+发掘 idea 调研，不发巡检废话)
