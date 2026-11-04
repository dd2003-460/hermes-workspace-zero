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

### G2: T17 泛化 bench → done
- **结论**（T17-REPORT.md, 10 runs 全出分）：四域 ms 16.5 / infra 16.5 / rag 16.0 / methodology 18.0。概念迁移成功（C1-C3 跨域稳）；形式纪律需显式注入（S2/S3 不自发）；单 run 噪声 ≥ 域间差 → 域排序不可信；rubric v2 修 C4 判据完成。
- **诚实边界**：n=2/域、同族判官（自偏好风险）、绝对分受天花板限制。异源 judge 是下一步。
- **状态**：done（2026-11-04 确认 runner 已结束，报告已落盘）

### G4: F10-R5 → H1 回测执行 — prereg 草案就绪，等冻结确认
- **背景**：F10-R5 宏观调研完成（@ main 6304ab54），H_macro 文献层面不成立。但 S5 (Shek 2026) 发现 funding 极值按当日方向分组 +3.62pp gap，是 R2 漏掉的维度。
- **当前状态**：H1 预注册草案已写好（bb65e8ba, r8/f10-r5-h1-preregistration-draft.md）。数据本地已有（Binance funding/OI/kline）。APPROVALS r291 已登记等成璐冻结确认。
- **触发条件**：成璐回复 APPROVALS r291 选项 A（确认冻结）。
- **动作**：标记 prereg FROZEN → 执行回测脚本（复用 R2 基础设施 + 新增方向分组）→ 报告结果 → 更新 TASKS.md + candidates。
- **预计耗时**：1-2h（数据已在盘，主要是跑 walk-forward + bootstrap）。
- **状态**：waiting（等 r291 sign-off）

### G3: 金融·正交信号源（F8）— 已收口 + 采集器启动
- **结论（负面结果）**：免费+PIT+2020-2026日线约束下，crypto 日频信号高度冗余，无可验证正交源。TVL ρ=0.43 冗余；期权IV/OI/多空比/链上流全没免费历史。详见 `tasks/decomposition.md`。
- **本轮动作（已完成 2026-11-03）**：
  1. ✅ F8 负面结果正式落盘 `tasks/decomposition.md`（权威记录）
  2. ✅ Deribit IV 采集器 `scripts/deribit_iv_collector.py` 写好并跑通（848合约，ATM IV=45.17）
  3. ✅ Hermes cron job `iv-collector-daily` 挂好（每日 09:00 UTC+8 采 BTC+ETH）
- **下一步**：等积累 ≥90 天 IV 数据后做 F8 组合实验设计（F8-4）。当前无需干预，cron 自动跑。
- **待成璐决策**：是否接受「免费数据下 crypto 日频信号高度冗余」作为 F8 正式结论（负面结果本身有价值），还是等 IV 采集器积累后再做组合实验。
- **状态**：done（调研+采集器）→ monitoring（等 IV 数据积累）

## 维护性兜底
无可执行目标时：扫 workspace git status / 各项目 loop-state.json / memory 蒸馏，保持台账准确。

---
# origin: ai (2026-11-03, 成璐指令：hook 应是 goal template——没事找新活+发掘 idea 调研，不发巡检废话)
