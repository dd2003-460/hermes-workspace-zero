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
- **执行者**：ralph loop（claude 子进程，16:17 启动）
- **前置**：runner 16:10 重启后恢复，conv3 q195/604 (98%)。
- **触发条件**：runner 退出 + 结果目录出现最终汇总文件。
- **动作**：ralph 聚合各 cutoff 分数 → 对比表 → 更新 decomp loop-state。
- **状态**：running（2026-11-03 23:00 恢复：runner 曾被 SIGKILL@conv4 q19，已 resume 重启 pid 37261；ralph claude 死于 tool_reference 400，已带降级预案重启。剩 conv4尾+conv5-9 ≈13h）

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
