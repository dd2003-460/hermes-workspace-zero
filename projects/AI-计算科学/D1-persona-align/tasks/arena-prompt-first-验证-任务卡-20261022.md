# origin: ai · 2026-10-22 · 目标 2026-10-22T18:54（成璐 goal：prompt-first 提升验证调研任务卡）

> 渠道：LMArena agent mode（arena-outsource SOP · `.claude/skills/arena-outsource/SKILL.md`）。
> 目标仓库：`dd2003-460/prompt-first-bench`，任务书 push 到 `tasks/002-prompt-first-verify.md`（仓库不存在/未连接 → 走降级阶梯，见 `agents/arena-loop-pipeline.md` §3.3，loop 不豁免）。
> 执行前必读：`sop/arena-loop-pipeline.md` + `loop/prompt-first/00..04.5`（仓库内）。

```
【执行前必读】
1. 本任务必须走 1-loop：先读 sop/arena-loop-pipeline.md + loop/prompt-first/00-common-review.md + 01..04.5（仓库内）。
2. 每阶段产出落盘 loop-artifacts/stages/<N>/，阶段判定 pass 才进下一阶段。
3. 完成后 commit + push（含全部 loop-artifacts/）。
4. 通道故障（403/沙箱）→ 报告 Lead，由 Lead 降级本地执行，不得静默跳过 loop。

[任务] 回答三个问题：Q1 任务拆解（decomposition）对最终成功率有多大影响？Q2 "正交分解+完备性检查"类要求对成功率/质量的边际提升？Q3 强模型 vs 弱模型的差异化收益（强模型是否不需要拆解就更好？弱模型是否更依赖拆解？）。
[背景] 我们有 prompt-first 流程（01 目标分解→02 信息调研→02.5 交叉验证→03 行动分解→04 执行验证→04.5 最终复核；核心要求=正交分解+完备性检查+原子化）。内部数据：完整说明书 C0 Mean 15.2 σ0.45 (5run) vs 白话版 C9-plain 15.3 σ1.53 (3run)——均值无差异、方差低 3.4 倍（提示：价值可能在稳定性而非提分）。
[约束] 中文；每条结论标 conf(0-1)；给来源 URL（GitHub repo / arXiv id）；不确定的标"未验证"。
[交付] markdown 表格：列=问题(Q1/Q2/Q3) | 结论 | 证据(来源+关键数字) | conf；核心 ≤50 行，过程论证放附录。若公开证据不足（预期不足），附「小型实验方案」节：对照=裸 prompt vs 走 prompt-first 01–04.5；模型=强/中/弱各 ≥1；每格 runs≥3；rubric 沿用 decomp-bench 18 分制；列出具体任务集与判分标准。
[长度] 核心 ≤50 行。
[落盘约束] 文件不存在=任务未完成，Lead 不验收。交付文件：tasks/002-prompt-first-verify.md（仓库内）或报告 Lead 指定路径。
```

## Lead 执行备忘（不发给 arena）

- 对照调研方向：GitHub 开源 agent 框架（LangGraph planner、ReWOO、AutoGPT 系分解）+ arXiv agent planning / task-decomposition 工作（2024–2026）。
- 交叉验证门禁（02.5/04.5）：关键 claim ≥2 独立回答；arena + 另一站点，或同一 arena 会话多轮对战。
- 降级阶梯：arena agent mode → arena Battle → ego-browser 直抓 → 自答（conf−0.2，文件头标「arena 不可用」）。
- 本卡为草稿（workspace 落盘）；push 进仓库时按链路 SOP 断点 B/C 门禁验证（`git log -1 -- tasks/002-*.md` + arena `cat` 成功）。
