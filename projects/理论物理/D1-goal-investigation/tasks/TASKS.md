# D1-goal-investigation — TASKS

**最后更新**: 2026-06-23
**状态**: 实施完成，待 end-to-end session 验证

---

## 任务

| 任务 | 状态 | 说明 |
|------|------|------|
| 当前状态分析 | ✅ 完成 | 4个断裂点已识别 |
| 方案设计 | ✅ 完成 | 固定入口+双写机制 |
| 实现计划 | ✅ 完成 | 4步实施+hook改造 |
| 创建 loop-state.json | ✅ 完成 | 2个项目已创建，智能合并验证通过 |
| 创建聚合脚本 | ✅ 完成 | `scripts/aggregate-active.sh` 正确聚合 |
| 创建 ralph-sync.sh | ✅ 完成 | 全局→项目同步，智能合并保留AI字段 |
| 更新 INDEX.md 入口链 | ✅ 完成 | projects/INDEX.md + 理论物理/INDEX.md 已加 ACTIVE 链接 |
| 更新 AGENTS.md 阅读链路 | ✅ 完成 | 4步压缩到2步 |
| 改造 RALPH stop-hook | ✅ 完成 | stop-hook.sh 追加 ralph-sync.sh 调用（已备份） |
| 端到端 session 验证 | 📋 待开始 | 新session能自动到达项目状态并完成一次完整迭代 |
