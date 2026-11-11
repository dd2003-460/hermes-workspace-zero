# Goal 模板（定位器）

> origin: ai · 2026-10-27 二次瘦身 · 76→60 行
> **触发规则**：用户消息含 `@sop/goal-template.md` = 第一动作立即 `create_goal`。
> 执行顺序：① read 本文件 → ② create_goal（按 §1 格式）→ ③ 才处理用户消息里的具体任务。

## §1 Goal 描述格式（create_goal 必须用此五字段）

```
【目标】1-2 句任务目标
【阶段】什么项目，进行到什么阶段（做完一个更新到下一个）
【SOP 索引】本 goal 走哪些 SOP（只列指针，不贴内容）
【验收标准】量化到可机器检查（指标数量+加权分数阈值），禁用"完整/充分"
【失败降级】按 SOP 降级通道（arena 不可用→本地 conf-0.2，loop 不豁免）
```

## §2 阶段流程（1-loop 六阶段）

**★ 整体外包原则**：loop 六阶段默认整条链路外包 arena 执行（arena 在仓库内走 01→04.5），Lead 只负责发任务书 + 验收产出。本地逐阶段执行 = 效率极低，仅限降级。

| 阶段 | 阶段文件（复制进仓库给 arena 读） | 产出 |
|------|----------------------------------|------|
| 01 目标分解 | `loop/prompt-first/01-goal-decomposition.md` | decomposition.md |
| 02 信息调研 | `loop/prompt-first/02-information-research.md` | research.md |
| 02.5 交叉验证 | `loop/prompt-first/02.5-cross-check.md` | crosscheck.md |
| 03 行动分解 | `loop/prompt-first/03-action-decomposition.md` | actions.md |
| 04 执行验证 | `loop/prompt-first/04-execution-verification.md` | execution-log.md |
| 04.5 反方复核 | `loop/prompt-first/04.5-final-review.md` | review.md |

执行通道 + 3 断点门禁细节见 `sop/arena-loop-pipeline.md`。降级：arena 不可用→本地走完整 loop（conf-0.2），只降通道不降流程。

## §3 质量原则（硬规则）

- 对标领域顶刊/高 star 开源，先复刻再创新，不跳步。
- 一次一个 goal，干完再找下一个。
- 每步产出可验证（指标/文件/分数），未达标不 complete。
- goal 完成后必须 commit + push 留痕。
- 无 goal = 停摆：complete/clear 后同一回合内 create 下一个或明确 blocked。
- create_goal 后必须 get_goal 验证落库值（runtime 会静默钳制 max_goal_rounds）。
- 同一问题想 2 轮无新事实 → 换工具（ego-browser/subagent），不空转。
- acp_rule 加载：建 goal 后读 `sop/acp-rules.json`，对 rules 数组并行调用 `acp_rule` 录入（一轮完成）；工具不存在则跳过。

## §3.5 Subagent 协议（成璐 2026-11-06 指令）

**派发前必做**：把本模板 §1-§5 全文写入 subagent 的 context 字段（不是摘要，是全文）。subagent 不知道自己的上下文里有这套规则 = 等于没注入。

**主动性激发（禁机械检查）**：subagent 的任务描述不得只写"检查 X 是否满足 Y"——机械 prompt 产出的只是打勾清单，没有判断力。正确写法：

- **质量对标**："对标 <具体参照物：顶刊论文 / 高 star 开源项目 / 已有最佳结果>，找出当前产出与参照物的差距，给出 ≥3 条可执行的改进项（每条带预期收益和成本估算）。"
- **实际优化**："不只是发现问题——直接实施 top-1 改进并展示前后对比（分数/指标/代码 diff）。改完跑一遍验证确认没退化。"
- **反方视角**："假设你是审稿人/竞争对手，这个工作最可能被攻击的 3 个弱点是什么？每个弱点给一个具体的防御方案。"

**持续运行**：subagent 返回后 Lead 验收产出（不是验收"完成了"三个字）。产出未达 §4 标准 → 带着具体差距反馈重新派发（最多 2 轮），不降级接受。

**并行**：独立子任务同时派发（≤3 并行），不串行等待。

## §4 验收标准（量化）

- 每个 goal 有明确成功指标（分数/准确率/完成度/引用数）。
- 长目标（max_goal_rounds > 50）：验收必须可机器检查，每 100 轮回读判据防漂移。
- 预测类：准确率 > 基线；调研类：里程碑 ≥10 篇 + conf ≥ 0.7 + 独立源 ≥3；实验类：完成所有 run + 评分汇总。
- **纸面协议防护力为零**（pfb AUDIT G4 S3，2026-11-02 升格）：协议里写了没有 ≠ 有人真的跑过。验收项必须是后者——"已执行+回执落盘"，不是"文档里定义了"。
- **统计量引用强制带口径限定**（pfb AUDIT-report §6 范式，2026-11-02 升格为全局写作规则）：对外宣称任何分数/κ/p 值时，必须同时标注 (a) 聚合口径（per-run vs pooled）、(b) tie-break 规则、(c) judge 族（同族双判 ≠ 真 IRR）。无限定语的孤立数字 = 无效引用。
- 只有验收标准全部达标，goal 才 complete。

## §5 Goal 生命周期

```
创建 → 执行（按 §2 阶段流程）→ 验收（§4）→ complete → 同一回合 create 新 goal
```

- 新 goal 的 objective 必须包含完整链路规则（本模板 §1-§5），不得只写"继续优化"。
- 新目标探索准则落盘 `projects/<项目>/tasks/new-goal-criteria-<日期>.md`（候选 ≥3 + 产投比排序）。

## §6 SOP 指针索引（按需读，不默认全量进上下文）

| SOP | 路径 | 何时读 |
|-----|------|--------|
| Arena Loop 链路（★首选） | `sop/arena-loop-pipeline.md` | 外包 arena 时 |
| **机制修改三问** | `pfb/sop/pfb-domain/modification-rationale.md` | **任何规则/机制改动前必读**：为什么加 + 正交性检查 + 外部依据 + 退出条件 |
| 结构化输出派发 | `sop/structured-dispatch.md` | 派发决策型子任务时 |
| acp-rules 硬规则 | `sop/acp-rules.json` | 建 goal 后第一动作录入 |
| SOP 总索引 | `sop/SOP-INDEX.md` | 找其他 SOP 时 |
