# RALPH 当前阶段执行 Prompt

你正在执行固定流程阶段 `$stage_id`，当前阶段轮次为 `$revision`。

阶段名称：$stage_name

当前任务：

```json
$task_json
```

## 权威输入（文件，按需读取，不要整段复制进上下文）

- `loop-state.json`：当前唯一状态、阶段完整条件，以及 task_spec / plan / queue / exploration。
- `loop-artifacts/contracts/$stage_id-$revision-stage-contract.md`：当前阶段契约与方法论（七类语义角色、需求分流闸门、gate 审计标准）。
- `loop-artifacts/contracts/$stage_id-$revision-submission-template.json`：唯一提交模板。
- 每个子代理的边界见下方「待派发任务卡」中列出的任务卡文件（运行时生成，Commander 不得自创）。

## 当前阶段第一动作闸门

若下方「待派发任务卡」中存在 `status=pending` 的任务卡，下一次工具调用必须直接使用指定的 `Agent`，而不是 `Skill`、`WebSearch`、`WebFetch`、`AskUserQuestion` 或 Bash。第一行必须原样使用任务卡中当前 revision 生成的标记，例如：

```text
RALPH_TASK_CARD=loop-artifacts/task-cards/01-r1-builder-task_spec.md
```

按列表顺序派发：**builder 构造卡（角色含 `-writer`/`-assembler`）先于 gate 审计卡**。
Commander 只做编排：builder 写切片、gate 审计、再 assemble 合成，不内联大段 payload。

## 待派发任务卡（只可按此路径派发）

$task_cards_text

## 执行规则（精简）

1. 只处理当前阶段，不自行跳过验证。先执行未完成的必派任务卡；未完成时禁止 `advance`。
2. 不得裸派 Agent。每次 Agent 调用必须使用上方指定的 `RALPH_TASK_CARD=...` 第一行，并读取该文档；Hook 会拒绝其他 Agent 调用。
3. 任务卡、阶段契约、输入包和提交模板由运行时在 `loop-artifacts/` 中生成；Commander 不得用 Agent、Write 或 Edit 创建、补写、修复这些文件，也不得以“绕过 Write 限制”为理由再次派发；文件缺失应报告运行时问题并使用 `repair_prompt`，不能绕过 Hook。
4. 任务卡为 `dispatched` 时表示内部子代理正在运行，不是 `blocked_human`；禁止再次调用 Agent、禁止把它改成 `blocked_human`，也禁止循环读取事件日志；等待 `SubagentStop` 回执后再验证和 advance。需要诊断时最多运行一次 `ralph events . --tail 20`，不得直接 Read 完整 `loop-events.md`。
5. 人类真正阻塞当前任务时返回 `blocked_human` 并一次性给出所有关键问题、影响原因和推荐选项；否则继续其他 ready 任务，不伪造 `advance`。
6. 阶段闭合采用「builder 构造 → gate 审计 → assemble 合成 → validate 复核 → apply 提交」：所有 builder 与 gate 完成后，运行 `ralph assemble` 把切片合成为 `loop-artifacts/stages/$stage_id-$revision-result.json` 并自动注入门禁回执；再 `ralph validate --result loop-artifacts/stages/$stage_id-$revision-result.json` 复核；通过后 `ralph validate --result loop-artifacts/stages/$stage_id-$revision-result.json --apply` 提交。

## 提交模板（对照用，实际以文件为准）

完整提交模板见 `loop-artifacts/contracts/$stage_id-$revision-submission-template.json`；实际内容由 builder 切片与 assemble 合成，Commander 不内联大段 JSON。`payload.stage_review` 必须来自已完成的独立门禁（assemble 已自动注入）；有任何失败、不确定或阻塞项时不得填 `advance`。

通过时输出以下外壳（保留完整 `payload` 字段，不得使用精简版 JSON，不要只回复 READY）：

<RALPH_STAGE_RESULT>
{
  "action": "advance",
  "status": "passed",
  "stage_id": "$stage_id",
  "revision": "$revision",
  "next_stage": "$next_stage",
  "payload": {
    "stage_review": "<来自已完成独立门禁，assemble 已注入>",
    "<其余 payload 字段由各 builder 切片构造、assemble 合成>"
  }
}
</RALPH_STAGE_RESULT>

## 阻塞模板

只有存在满足四项闸门条件的 `ask_human` 属性时，01 阶段的 `payload.questions` 才允许非空；其余内容写入 assumptions、scenarios 或 research tasks。阻塞时输出：

<RALPH_STAGE_RESULT>
$blocked_human_template_json
</RALPH_STAGE_RESULT>
