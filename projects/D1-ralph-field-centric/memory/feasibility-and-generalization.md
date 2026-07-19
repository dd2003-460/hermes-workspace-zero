# 可行性 + 泛化评估（是否已可实现 + 能否用于任务分解 + 是否提升稳定性/质量）

> 这是对你三个核心问题的直接回答。结论先给：可以实现，且增量成本低；泛化到粗→细任务分解天然成立；稳定性提升确定，质量提升在「外部信息充足」前提下成立，但需 benchmark 验证。

## Q1：能否写入项目计划 / 能否实现

**可以，且主要是「把已有原语解放」而非重写。**

已实现且可直接复用：
- `RALPH_HOOK_MODE=shadow`（`loop/ralph_runtime/cli.py:315`）：Phase 1 止血几乎零成本，把 enforce→shadow 即解除致命阻断。
- 字段 disposition 四态 `{confirmed,inferred,assume,research}` + `attribute_matrix`（`contracts.py:383,920`、`decomposition_benchmark.py:206`）：节点=字段集合的模型已存在。
- `factor_groups()`（`contracts.py:60`）：按 `task_spec.factor_roles` 动态分桶，动态新增条件已具备骨架。
- `decomposition_benchmark.py`：现成评分器，可直接做前后对比。

需要新写/改造：
- `stage_prompt.md`：把刚性「5 步协议 + 强制 RALPH_TASK_CARD 首行」改为「你只需填一张字段表，模板在 X 路径」。这是陌生 agent 能否直接操作的关键——当前模板对新手不友好（根因）。
- `protocol.py` 门禁：从「卡片集合」改为「required_fields 非 pending」。
- `state.py`：字段级写入 + 跨节点透传（父节点 confirmed → 子节点起点）。
- subagent 模板：从「整卡」改为「单字段参数」（极窄任务，弱模型成功率高）。

风险点：
- 字段膨胀 / 无限拆词 → 用停止规则约束。
- 纯机械门禁可能放过低质量证据 → 保留 `research_required` 的 confidence 阈值。
- 主 agent 填字段循环 → 字段去重 + idempotency。

## Q2：能否泛化到任务分解（粗→细、分支条件）

**天然成立，这是字段模型最大的价值。**

- 粗→细：顶层节点字段少而抽象 → 每个字段展开成子节点（自带字段）→ 递归，直到字段可证据化填满。与现有 `factor_groups` 动态分桶同源。
- 分支条件：字段值触发不同子字段集（gpu_vendor=NVIDIA→cuda_version / AMD→rocm_version），即节点展开。状态机 `nodes.py` 的 `on_success/on_failure/on_human_block` 已是显式转移，分支只是「字段值 → 选哪条转移」。
- 执行分解：字段最终收敛为 `action` 字段（具体可执行步骤），同一机制派发执行 subagent → 从「研究分解」平滑过渡到「动作/架构分解」，无需换一套编排。
- 适用性：对任意「目标→需填条件→派发调研/执行」类任务通用，不限于 GPU 调研。

## Q3：是否提升普通 agent（弱模型）的稳定性与最终质量

**稳定性：确定提升（机制层面）。**
- 结构化字段契约替代自由协议 → 弱模型「能做错的地方」变少。
- `assumed_default` 全范围 → 几乎消除 `ask_human` 阻断（弱模型最易卡在追问）。
- 每 subagent 只填一个字段 → 上下文不溢出、成功率高。
- 偏离从「致命阻断」降级为「字段未填满」→ 不再死循环（这正是 D1-ralph-smoke-matrix 卡死根因）。

**质量：在「外部信息充足」前提下提升（需 benchmark 验证）。**
- 调研 subagent 带 `evidence_refs` 回填 → 每个结论可溯源。
- 门禁机械保证「无 required 字段遗漏」→ 分解完整性可验证。
- soul 默认画像保证偏好一致性，避免弱模型随机假设。
- 反例/边界：若外部信息不足（离线、无 WebSearch），`research_required` 字段无法填满 → 质量受限于信息可得性；此时 `assumed_default` 占比高，结果偏「通用默认」而非用户真实偏好。**这是「外部信息充足」前提成立的原因——必须显式标注。**

**最重要的结论**：这套机制提升的是「在给定约束下不漏、不卡、可溯源」的稳定性，而非「无中生有」的创造性质量。质量上限仍由信息可得性 + 模型能力决定；它把弱模型的「执行下限」显著抬升，并让强模型更快收敛。

## 验证路径（建议先做哪个）

最小可行验证 = 只做 Phase 1：把 `D1-ralph-smoke-matrix` 用 `RALPH_HOOK_MODE=shadow` 重跑，看是否推进过 stage 01 r1。若通过，再投入 Phase 2-5。这能在不改动一行核心代码的情况下，先验证「放宽限制即可止血」的假设。
