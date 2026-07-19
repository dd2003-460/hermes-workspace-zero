# RALPH 当前阶段执行 Prompt（字段中心 · 轻量模式 · 无子代理卡片）

你正在执行固定流程阶段 `$stage_id`（轮次 `$revision`）。阶段名称：$stage_name。

当前任务：

```json
$task_json
```

## 本阶段方法论（来自阶段 prompt 文件；直接改该文件即可调整本阶段行为，无需动运行时代码）

$stage_prompt_doc

## 你只需要做一件事：维护一张「字段表」

本阶段目标是把 `$stage_name` 需要的事实，整理成**一组字段**写进 `loop-state.json` 的 `task_spec.attribute_matrix`。
没有子代理卡片、没有 assemble/validate 命令、没有强制流程。你直接面对字段表工作。

## 字段表怎么来、怎么长（核心机制）

  1. **本阶段交付物（每阶段只一对，命名 `0x-rx`，链式传递）**：你**只需写 `loop-artifacts/$stage_id-$revision.json`**（结构化字段）。可读性 `.md` 由 `ralph render`（或 `field-apply` 落盘时）**自动从 JSON 生成，你不必手写 md**，减轻你的负担也避免 md 与 json 不一致。
     **输入**为上一阶段的 `loop-artifacts/<上一阶段>-r1.json`（上一阶段输出即本阶段输入，读 json 即可；如需人读版看同目录 `.md`）；首阶段从 `loop-state.json` 的任务与已知背景开始。
    **严禁用 Write/Edit 直接改 `loop-state.json`**。字段一律通过 `ralph field-apply` 提交：把本阶段要新增/更新的字段写进 `loop-artifacts/$stage_id-$revision.json`（列表，或 `{ "fields": [...] }`），每条形如：
    `{ "concept": "字段名", "role": "背景/目标/约束/...", "attribute": "具体属性", "disposition": "confirmed|assumed_default|research_required|pending", "rationale": "...", "evidence_refs": [], "confidence": 1.0, "impact": "material", "reversible": true }`
    ，运行 `ralph field-apply <项目> loop-artifacts/$stage_id-$revision.json`，校验通过才原子落盘（按 `concept` 合并：同 concept 覆盖，新 concept 追加；`{ "concept": "...", "delete": true }` 删除）。
2. **填你能确定的**：`confirmed`（已知背景）或 `assumed_default`（不确定偏好→默认全范围，rationale 标注「默认假设」）。soul 默认画像（`AGENTS.md` 默认决策画像）已是通用默认，直接套用。
3. **派单字段 agent 补空缺**：对每个 `research_required` 字段，用 Agent 工具派**只填这一个字段**的调研 subagent，prompt 写清楚：
   「只研究并返回这一个字段：`字段名`。返回格式：`{ "concept": "...", "role": "...", "attribute": "...", "disposition": "research_required", "rationale": "...", "evidence_refs": ["来源"], "confidence": 0.x, "impact": "material", "reversible": true }`。不要读无关文档，只产出这一个字段的 JSON。」
   它查完把这条 JSON 交回，你**合并进** `attribute_matrix`。
4. **差集 = 新字段（自动增殖）**：每回填一个字段，若它引出了新的未知项（例如填了「显卡型号」后冒出「该型号显存」「该型号价格」），就**把这些新项作为新的 `pending` 字段加进同一张表**。重复直到没有 `pending` 字段。
5. **只回传空缺**：系统只告诉你还差哪些 `pending` 字段；你照着补，**不会因为没一次交齐而失败**。

## 四个处置状态（disposition）

- `confirmed`：已知背景 / 已给定条件。
- `assumed_default`：不确定偏好（只知范围）—没人类输入默认全范围。
- `research_required`：未知事实（最新显卡、价格行情…）—派单字段调研 agent 带回 `evidence_refs`。
- `pending`：尚未处理。

## 提交与推进

你**通过 `ralph field-apply <项目> loop-artifacts/$stage_id-$revision.json` 提交本阶段字段**即可（禁止直接 Write/Edit `loop-state.json`）；提交后 `.md` 自动生成，**你无需另写 md**。运行时每轮会：
1. 自动把逗号分隔的属性拆成独立字段（字段自动增殖）；
2. 检查 disposition 完整性。

**推进规则（重要，避免空转）**：
- **阶段 01**：字段完整后运行时**自动推进**，你无需额外操作。
- **阶段 02 / 02.5 / 03 / 04 / 04.5**：**不会自动推进**，且聊天里输出 `<RALPH_STAGE_RESULT> advance` 无效（运行时不会解析聊天 token）。字段齐全后，你必须显式运行推进命令：先写 action 文件 `loop-artifacts/$stage_id-$revision.advance.json`：
  ```json
  {"action":"advance","status":"completed","stage_id":"$stage_id","revision":"$revision","next_stage":"<节点图上本阶段的后继>","message":"完成本阶段，推进"}
  ```
  再运行 **`ralph apply . loop-artifacts/$stage_id-$revision.advance.json`**（或 `ralph validate --result loop-artifacts/$stage_id-$revision.advance.json --apply`）即完成推进。

所以你唯一要做的是：能确定的填 `confirmed` / `assumed_default`；未知的派调研 subagent 补 `evidence_refs`；引出的新未知继续加 `pending` 字段。
- **本阶段契约的 `required_outputs` 是本阶段应交付的字段语义角色（如 01 的 goal_summary/constraints、02 的 task_graph、02.5 的 cross_validation）：把这些角色也作为字段写进 `attribute_matrix`（disposition=inferred/confirmed），齐全后才能 advance。缺哪个角色就补哪个，不要只看「无 pending」。
- **推进**：字段 + required_outputs 齐全后，写 `loop-artifacts/$stage_id-$revision.advance.json` 并 `ralph apply . ...advance.json`（02+ 必须显式；只有 01 自动推进）。
- **反空转（关键）**：如果你连续只跑 `ralph status` / `ralph events` / `ralph render` 而不写文件，说明输入已足够——直接写本阶段字段 + advance 文件，不要再查状态打转。读一遍 `loop-state.json` 当前字段，补 required_outputs，然后 advance。

只有「用户/项目/环境都无答案、不能推断或研究、且会改变硬可行性/硬预算/验收」的字段，才用 `blocked_human` + `payload.questions` 一次性提问；否则不要用 `blocked_human` 卡住。
