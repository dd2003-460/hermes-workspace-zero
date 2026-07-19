"""Claude Code Hook adapters with shadow and enforce modes."""

from __future__ import annotations

import json
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    card_by_ref,
    materialize_contract_documents,
    merge_task_spec_partials,
    SEMANTIC_ROLES,
    factor_groups,
    stage_submission_template,
    task_card_marker,
)
from .events import append_observation, apply_and_record, read_events
from .feedback import feedback_context, gate_feedback, render_feedback, tool_feedback
from .result_artifacts import state_stage_artifact_dir


# A Stop Hook repair is useful only while the current Claude context is still
# making a bounded attempt to comply.  Local models can otherwise keep
# emitting slightly different XML/partial JSON forever; the event log changes
# on every rejection, so an activity-only watchdog cannot detect that loop.
# After this many consecutive protocol failures in one supervisor cycle, let
# the process end and let the outer ``ralph loop`` launch a fresh context.
MAX_PROTOCOL_REPAIRS_PER_CONTEXT = 3
from .prompt_renderer import PromptRenderer
from .protocol import parse_action
from .stage_policy import decide_tool
from .state import load_state, record_human_input, save_state, update_subagent_card


def _find_project_root(payload: Mapping[str, Any]) -> Path | None:
    raw_cwd = payload.get("cwd") or payload.get("workspace") or os.getcwd()
    current = Path(str(raw_cwd)).expanduser().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "loop-state.json").exists():
            return candidate
    return None


def _tool_input(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    value = payload.get("tool_input", {})
    return value if isinstance(value, Mapping) else {}


def _target_path(tool_input: Mapping[str, Any]) -> str | None:
    for key in ("file_path", "path", "target_path"):
        if tool_input.get(key):
            return str(tool_input[key])
    return None


def _command(tool_input: Mapping[str, Any]) -> str | None:
    value = tool_input.get("command")
    return str(value) if value else None


def _resolved_target(root: Path, target: str | None) -> Path | None:
    if not target:
        return None
    candidate = Path(target).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _commander_event_log_error(
    root: Path,
    role: str,
    tool_name: str,
    tool_input: Mapping[str, Any],
) -> str | None:
    """Prevent an unbounded transcript read of the append-only event journal."""

    if role != "commander" or tool_name != "Read":
        return None
    target = _resolved_target(root, _target_path(tool_input))
    if target != (root / "loop-events.md").resolve():
        return None
    return render_feedback(
        "EVENT_LOG_LOOP",
        detected="Commander 正在读取完整 loop-events.md；这会把旧工具输出重新注入上下文并放大 KV cache。",
        correction="停止当前 Read；事件日志是诊断摘要，不是工作输入。",
        next_action=(
            "需要诊断时只运行一次 `ralph events . --tail 20`；若任务卡是 dispatched，"
            "直接等待 SubagentStop。"
        ),
        forbidden="继续 Read/cat/tail 循环、重派 Agent、Write 任务卡或把 dispatched 改成 blocked_human。",
    )


def _agent_card_error(state: Mapping[str, Any], tool_input: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    reference = task_card_marker(tool_input)
    if reference is None:
        # Phase 1 relaxation: do NOT hard-block an Agent call that lacks the
        # RALPH_TASK_CARD marker.  A missing marker simply means the call is
        # unbound (run as a generic agent); the previous fatal block is what
        # trapped weak models in an endless recombobulating loop.
        return None, None
    card = card_by_ref(state, reference)
    if card is None:
        return None, f"Agent 任务卡未获批准：{reference}"
    stage = state.get("stage", {})
    if str(card.get("stage_id")) != str(stage.get("id")) or str(card.get("revision")) != str(stage.get("revision")):
        return None, f"任务卡 {card.get('id')} 不属于当前阶段"
    status = str(card.get("status", "pending"))
    if status == "completed":
        return None, tool_feedback(
            "DUPLICATE_DISPATCH",
            detected=f"任务卡 `{card.get('id')}` 已完成，当前 Agent 调用是重复派发。",
            correction="复用已有 gate receipt 和 artifact，不重新启动同一任务。",
            next_action="读取已完成回执并直接整理阶段提交；若回执缺失，报告运行时问题，不要重派。",
            forbidden="再次调用 Agent、创建任务卡、Write/Edit 或把内部等待伪装成 blocked_human。",
        )
    if status == "failed":
        return None, tool_feedback(
            "FAILED_CARD_RECOVERY",
            detected=f"任务卡 `{card.get('id')}` 已失败。",
            correction="先检查失败 artifact 和当前阶段条件，再决定回滚或重新分解。",
            next_action="停止重复派发；输出 rollback/repair_prompt，或等待人类重新授权新的计划修订。",
            forbidden="用同一任务卡无限重试、伪造 completed 或跳过失败原因。",
        )
    if status == "dispatched":
        if card.get("agent_id"):
            return None, render_feedback(
                "DUPLICATE_DISPATCH",
                detected=f"任务卡 `{card.get('id')}` 已绑定子代理 `{card.get('agent_id')}`，重复 Agent 调用被拒绝。",
                correction="把 dispatched 视为内部运行中状态，不是人类阻塞。",
                next_action=(
                    "不要再调用工具；等待 SubagentStop。需要诊断时最多运行一次 "
                    "`ralph events . --tail 20`，回执到达后再决定是否 advance。"
                ),
                forbidden="再次 Agent、创建/Write 任务卡、AskUserQuestion 或标记 blocked_human。",
            )
        return None, render_feedback(
            "DISPATCH_BINDING_WAIT",
            detected=f"任务卡 `{card.get('id')}` 已派发，正在等待 SubagentStart 绑定。",
            correction="生命周期事件尚未完成，当前不能证明任务失败或完成。",
            next_action="停止当前工具调用，等待 SubagentStart/SubagentStop 后再处理。",
            forbidden="不要再次调用 Agent、创建/Write 任务卡或标记 blocked_human。",
        )
    waiting = _unbound_dispatched_cards(state)
    if waiting:
        waiting_ids = ", ".join(str(item.get("id", "?")) for item in waiting)
        return None, render_feedback(
            "DISPATCH_ORDER",
            detected=f"已有未绑定的 dispatched 任务卡：{waiting_ids}。",
            correction="先完成已有生命周期绑定，再处理新的 Agent。",
            next_action="等待 SubagentStart；不要派发并行的未绑定卡。",
            forbidden="重复 Agent、手动写 agent_id 或跳过生命周期。",
        )
    return card, None


def _save_card_status(root: Path, state: Mapping[str, Any], card_id: str, status: str, agent_id: str | None = None) -> dict[str, Any]:
    updated = update_subagent_card(state, card_id, status, agent_id=agent_id)
    save_state(root / "loop-state.json", updated)
    materialize_contract_documents(root, updated)
    return updated


def _response_mapping(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    response = payload.get("tool_response", {})
    return response if isinstance(response, Mapping) else {}


def _agent_response_status(response: Mapping[str, Any]) -> str:
    # An unstructured tool response is not proof that a subagent finished.
    # Keep the card pending completion until SubagentStop rather than allowing
    # a false stage advance.
    if not response:
        return "dispatched"
    raw_status = str(response.get("status", "")).lower()
    if response.get("success") is False or raw_status in {"failed", "error", "cancelled"}:
        return "failed"
    if bool(response.get("isAsync")) or raw_status in {"async_launched", "running", "pending"}:
        return "dispatched"
    return "completed"


def _agent_id(payload: Mapping[str, Any]) -> str | None:
    response = _response_mapping(payload)
    for source in (response, payload):
        for key in ("agent_id", "agentId", "subagent_id", "subagentId"):
            value = source.get(key)
            if value:
                return str(value)
    # Claude Code documents the direct agent_id on SubagentStart/Stop.  Some
    # tool hook payloads instead expose the child transcript path; it has the
    # stable `agent-<id>.jsonl` form, so use it as a compatibility fallback.
    for key in ("agent_transcript_path", "transcript_path"):
        value = payload.get(key)
        if not value:
            continue
        name = Path(str(value)).name
        if name.startswith("agent-") and name.endswith(".jsonl"):
            candidate = name[len("agent-") : -len(".jsonl")]
            if candidate:
                return candidate
    return None


def _card_for_agent(state: Mapping[str, Any], agent_id: str | None) -> dict[str, Any] | None:
    if not agent_id:
        return None
    cards = state.get("subagent_cards", {})
    if not isinstance(cards, Mapping):
        return None
    for card in cards.values():
        if isinstance(card, Mapping) and str(card.get("agent_id", "")) == agent_id:
            return dict(card)
    return None


def _unbound_dispatched_cards(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    stage = state.get("stage", {})
    stage_id = str(stage.get("id", ""))
    revision = str(stage.get("revision", ""))
    cards = state.get("subagent_cards", {})
    if not isinstance(cards, Mapping):
        return []
    return [
        dict(card)
        for card in cards.values()
        if isinstance(card, Mapping)
        and str(card.get("status", "")) == "dispatched"
        and not card.get("agent_id")
        and str(card.get("stage_id", "")) == stage_id
        and str(card.get("revision", "")) == revision
    ]


def _current_dispatched_cards(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return cards still running in the current stage/revision."""

    stage = state.get("stage", {})
    stage_id = str(stage.get("id", ""))
    revision = str(stage.get("revision", ""))
    cards = state.get("subagent_cards", {})
    if not isinstance(cards, Mapping):
        return []
    return [
        dict(card)
        for card in cards.values()
        if isinstance(card, Mapping)
        and str(card.get("status", "")) == "dispatched"
        and str(card.get("stage_id", "")) == stage_id
        and str(card.get("revision", "")) == revision
    ]


def _slice_owner_card(root: Path, state: Mapping[str, Any], target: str | None) -> dict[str, Any] | None:
    """Find the current-stage card whose slice input_refs contains `target`.

    Used so a builder/gate worker may Write/Edit its slice even when the
    agent_id binding is stale (the model rewrites loop-state.json with its own
    placeholder id after the subagent has already started).
    """

    if not target:
        return None
    candidate = Path(target).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        candidate = candidate.resolve()
    except OSError:
        return None
    stage = state.get("stage", {})
    stage_id = str(stage.get("id", ""))
    revision = str(stage.get("revision", "r1"))
    for card in (state.get("subagent_cards", {}) or {}).values():
        if not isinstance(card, Mapping):
            continue
        if str(card.get("stage_id", "")) != stage_id or str(card.get("revision", "")) != revision:
            continue
        if str(card.get("status", "")) in ("completed", "failed"):
            continue
        for ref in card.get("input_refs", []) or []:
            try:
                if (root / str(ref)).resolve() == candidate:
                    return dict(card)
            except OSError:
                continue
    return None


def _bind_waiting_card(root: Path, state: Mapping[str, Any], agent_id: str) -> tuple[dict[str, Any] | None, str | None]:
    existing = _card_for_agent(state, agent_id)
    if existing is not None:
        return existing, None
    stage = state.get("stage", {})
    stage_id = str(stage.get("id", ""))
    revision = str(stage.get("revision", "r1"))
    dispatched = [
        card
        for card in (state.get("subagent_cards", {}) or {}).values()
        if isinstance(card, Mapping)
        and str(card.get("stage_id", "")) == stage_id
        and str(card.get("revision", "")) == revision
        and card.get("status") == "dispatched"
    ]
    if len(dispatched) == 1:
        card = dispatched[0]
        updated = _save_card_status(root, state, str(card["id"]), "dispatched", agent_id=agent_id)
        return _card_for_agent(updated, agent_id), None
    if not dispatched:
        return None, "no_dispatched_card"
    ids = ", ".join(str(card.get("id", "?")) for card in dispatched)
    return None, f"ambiguous_dispatched_cards:{ids}"


def _card_tool_error(root: Path, card: Mapping[str, Any], tool_name: str, tool_input: Mapping[str, Any]) -> str | None:
    allowed_tools = {str(value) for value in card.get("allowed_tools", [])}
    if tool_name not in allowed_tools:
        if tool_name == "Bash":
            return tool_feedback(
                "WORKER_GATE_SCOPE",
                detected=f"只读审计卡 `{card.get('id')}` 尝试使用 Bash。",
                correction="门禁只需要读取任务卡列出的 document_refs，不能执行项目命令。",
                next_action="用 Read/Glob/Grep 完成边界内审计，然后直接返回完整 `<RALPH_GATE_REVIEW>` JSON。",
                forbidden="Bash、Write、Edit、修改文件、读取 loop-state.json 或开始外部调研。",
            )
        return tool_feedback(
            "WORKER_TOOL_SCOPE",
            detected=f"任务卡 `{card.get('id')}` 不允许使用 {tool_name}。",
            correction=f"只使用任务卡白名单：{', '.join(sorted(allowed_tools)) or '无'}。",
            next_action="继续当前边界内工作，完成后返回任务卡要求的结构化结果。",
            forbidden="用其他工具绕过白名单或扩大 document_refs。",
        )

    target = _target_path(tool_input)
    if tool_name == "Read" and target:
        candidate = Path(target).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        allowed_refs = [str(card.get("card_ref", "")), *[str(ref) for ref in card.get("document_refs", [])]]
        allowed_paths = {(root / ref).resolve() for ref in allowed_refs if ref}
        if candidate not in allowed_paths:
            return tool_feedback(
                "WORKER_READ_SCOPE",
                detected=f"任务卡 `{card.get('id')}` 尝试读取 document_refs 之外的文件。",
                correction="门禁上下文必须保持有界，只读取任务卡和明确列出的输入包/契约/模板。",
                next_action="停止该 Read，改读允许的 document_refs；读完后直接输出门禁回执。",
                forbidden="读取完整 loop-events.md、loop-state.json、其他阶段 artifact 或项目业务文件。",
            )

    if tool_name in {"Glob", "Grep"}:
        if not target:
            return tool_feedback(
                "WORKER_SEARCH_SCOPE",
                detected=f"任务卡 `{card.get('id')}` 的 {tool_name} 没有限定搜索路径。",
                correction="搜索必须限制在任务卡允许的 loop-artifacts/范围内。",
                next_action=f"为 {tool_name} 指定一个明确的 loop-artifacts/目标，或停止搜索并提交回执。",
                forbidden="无界搜索项目根目录或读取完整历史日志。",
            )
        candidate = Path(target).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        artifact_root = (root / "loop-artifacts").resolve()
        if candidate != artifact_root and artifact_root not in candidate.parents:
            return tool_feedback(
                "WORKER_SEARCH_SCOPE",
                detected=f"任务卡 `{card.get('id')}` 的 {tool_name} 超出了 loop-artifacts/。",
                correction="把搜索范围收回任务卡允许的 artifact 目录。",
                next_action=f"只搜索 `{artifact_root}` 下的指定输入，完成后直接提交门禁回执。",
                forbidden="搜索业务目录、全量 loop-events.md 或其他任务的文件。",
            )
    return None


def _record(root: Path, event_type: str, payload: Mapping[str, Any], output: str | None = None) -> None:
    append_observation(root / "loop-events.md", event_type, payload, output=output)


def _output_digest(output: str) -> str:
    return hashlib.sha256(output.encode("utf-8")).hexdigest()


def _output_was_applied(root: Path, digest: str) -> bool:
    for event in read_events(root / "loop-events.md"):
        if event.get("output_sha256") == digest:
            return True
        observation = event.get("observation")
        if isinstance(observation, Mapping) and observation.get("output_sha256") == digest:
            return True
    return False


def _consecutive_protocol_rejections(root: Path) -> int:
    """Count invalid stage results since the latest supervisor cycle.

    The supervisor writes ``supervisor_cycle_started`` before launching each
    fresh Claude process.  Treating that event as a boundary prevents a bad
    previous context from consuming the new context's repair budget.
    """

    count = 0
    for event in reversed(read_events(root / "loop-events.md")):
        event_type = str(event.get("type", ""))
        if event_type == "stage_result_rejected":
            count += 1
            continue
        if event_type == "supervisor_cycle_started":
            break
        # A successfully applied state action also starts a new semantic
        # attempt, even if the supervisor has not yet launched a new process.
        if event_type in {
            "stage_advanced",
            "stage_rollback",
            "task_spec_clarified",
            "blocked_human",
            "blocked_task_skipped",
            "exploration_started",
            "action_recorded",
        }:
            break
    return count


def _invalid_output_artifact(root: Path, digest: str, output: str) -> str:
    try:
        state = load_state(root / "loop-state.json")
        artifact_dir = state_stage_artifact_dir(root, state)
    except (OSError, ValueError, KeyError, TypeError):
        artifact_dir = root / "loop-artifacts" / "stages" / "unknown-stage" / "r1"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{digest}.invalid-agent-output.md"
    if not artifact_path.exists():
        artifact_path.write_text(output, encoding="utf-8")
    return str(artifact_path.relative_to(root))


def _apply_agent_result(root: Path, output: str) -> dict[str, Any]:
    """Parse, validate, persist and journal one final Agent result.

    The output digest makes Stop Hook retries idempotent. A repeated Stop event
    cannot apply the same action twice.
    """

    digest = _output_digest(output)
    if _output_was_applied(root, digest):
        return {"status": "duplicate", "output_sha256": digest}
    try:
        action = parse_action(output)
        state = apply_and_record(
            root / "loop-state.json",
            root / "loop-events.md",
            action.to_dict(),
            raw_output=output,
        )
        return {
            "status": "applied",
            "action": action.to_dict(),
            "state": state,
            "output_sha256": digest,
        }
    except Exception as exc:  # Hook failures must become Agent-visible repair feedback.
        artifact_ref = _invalid_output_artifact(root, digest, output)
        _record(
            root,
            "stage_result_rejected",
            {
                "error": str(exc),
                "output_sha256": digest,
                "artifact_ref": artifact_ref,
            },
            output=output,
        )
        return {
            "status": "rejected",
            "error": str(exc),
            "artifact_ref": artifact_ref,
            "output_sha256": digest,
        }


def _stop_response(reason: str, mode: str) -> dict[str, Any]:
    if mode == "shadow":
        # Stop only supports a blocking decision. A systemMessage makes the
        # shadow decision visible without changing whether Claude may stop.
        return {"systemMessage": "RALPH shadow：" + reason}
    return {"decision": "block", "reason": reason[:12000]}


def _bounded_hook_text(value: Any, limit: int = 6000) -> str:
    """Extract a small diagnostic slice without copying a transcript."""

    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, (Mapping, list, tuple)):
        try:
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            value = str(value)
    text = str(value).replace("\x00", " ").strip()
    if len(text) <= limit:
        return text
    half = max(1, (limit - 80) // 2)
    return text[:half] + "\n[… 中间诊断内容已截断 …]\n" + text[-half:]


def _bounded_tool_response(value: Any) -> dict[str, Any] | str:
    """Keep PostToolUse diagnostics useful without copying tool transcripts."""

    if not isinstance(value, Mapping):
        return _bounded_hook_text(value, 1600)

    # These fields are useful for lifecycle diagnosis.  Large result bodies
    # are represented by short excerpts; unknown fields are represented only
    # by their names so a tool cannot silently grow loop-events.md.
    scalar_keys = (
        "status",
        "success",
        "isAsync",
        "agent_id",
        "agentId",
        "subagent_id",
        "subagentId",
        "stop_reason",
        "error",
        "error_message",
        "message",
    )
    text_keys = ("output", "content", "stdout", "stderr", "text", "result")
    bounded: dict[str, Any] = {}
    for key in scalar_keys:
        if key in value:
            item = value[key]
            bounded[key] = _bounded_hook_text(item, 320) if isinstance(item, (Mapping, list, tuple)) else item
    for key in text_keys:
        if key in value:
            bounded[key] = _bounded_hook_text(value[key], 700)
    if not bounded:
        bounded["keys"] = [str(key) for key in list(value.keys())[:32]]
    return bounded


def _runtime_signal_text(payload: Mapping[str, Any]) -> str:
    """Collect only Hook error fields; never serialize the full Hook payload."""

    fields = (
        "error",
        "error_message",
        "stop_reason",
        "reason",
        "message",
        "last_assistant_message",
    )
    chunks: list[str] = []
    for key in fields:
        value = _bounded_hook_text(payload.get(key))
        if value:
            chunks.append(f"{key}: {value}")
    response = _response_mapping(payload)
    for key in ("error", "error_message", "status", "message", "stop_reason"):
        value = _bounded_hook_text(response.get(key))
        if value:
            chunks.append(f"tool_response.{key}: {value}")
    return "\n".join(chunks)


def _classify_runtime_interruption(payload: Mapping[str, Any]) -> tuple[str, str] | None:
    """Recognize infrastructure failures before trying to parse stage output.

    These failures are not Agent decisions. Treating them as malformed
    RALPH_STAGE_RESULT would create a repair loop and may append another full
    prompt to an already memory-pressure transcript.
    """

    signal = _runtime_signal_text(payload)
    lowered = signal.lower()
    memory_patterns = (
        "prefill context too large",
        "prefill memory guard",
        "memory guard rejected",
        "prefill safety cap",
        "available memory",
        "out of memory",
        "outofmemory",
        "oom",
        "内存不足",
        "显存不足",
    )
    connection_patterns = (
        "econnreset",
        "connection to the api was lost",
        "connection reset",
        "connection refused",
        "broken pipe",
        "network error",
    )
    timeout_patterns = ("timed out", "timeout", "deadline exceeded", "超时")
    api_patterns = ("api error", "request failed", "http 4", "http 5")
    stall_patterns = (
        "stalled mid-stream",
        "response stalled",
        "stream interrupted",
        "generation stalled",
        "incomplete response",
        "stream was interrupted",
        "connection closed before",
    )
    if any(pattern in lowered for pattern in memory_patterns):
        kind = "memory_guard"
    elif any(pattern in lowered for pattern in connection_patterns):
        kind = "connection"
    elif any(pattern in lowered for pattern in timeout_patterns):
        kind = "timeout"
    elif any(pattern in lowered for pattern in stall_patterns):
        kind = "stall"
    elif any(pattern in lowered for pattern in api_patterns):
        kind = "api_error"
    else:
        stop_reason = str(payload.get("stop_reason", "")).lower()
        if payload.get("error") or stop_reason in {"error", "failed", "cancelled", "aborted"}:
            kind = "runtime"
        else:
            return None
    return kind, _bounded_hook_text(signal, 1600)


def _runtime_stop_message(state: Mapping[str, Any], kind: str, excerpt: str) -> str:
    stage = state.get("stage", {})
    stage_id = str(stage.get("id", "?")) if isinstance(stage, Mapping) else "?"
    revision = str(stage.get("revision", "?")) if isinstance(stage, Mapping) else "?"
    labels = {
        "memory_guard": "oMLX 上下文/内存保护",
        "connection": "模型连接中断",
        "timeout": "模型请求超时",
        "stall": "模型响应中断（stalled mid-stream）",
        "api_error": "模型 API 错误",
        "runtime": "运行时错误",
    }
    label = labels.get(kind, kind)
    detail = _bounded_hook_text(excerpt, 700)
    return render_feedback(
        "RUNTIME_INTERRUPTION",
        detected=(
            f"{label}；当前阶段 {stage_id}-{revision} 未推进。"
            f"错误摘要：{detail or 'Hook 未收到可解析的错误正文'}"
        ),
        correction="保留 loop-state.json 原状，不把基础设施错误当成协议错误或阶段失败。",
        next_action="允许当前会话安全结束；下一次使用 `ralph resume <项目路径>` 建立短上下文。",
        forbidden="在原会话重复发送完整历史、重复派发同一任务或进入字段修复循环。",
    )


def _record_runtime_interruption(
    root: Path,
    state: Mapping[str, Any],
    payload: Mapping[str, Any],
    kind: str,
    excerpt: str,
) -> None:
    stage = state.get("stage", {})
    stage_id = stage.get("id") if isinstance(stage, Mapping) else None
    revision = stage.get("revision") if isinstance(stage, Mapping) else None
    _record(
        root,
        "runtime_interrupted",
        {
            "stage": stage_id,
            "revision": revision,
            "kind": kind,
            "stop_reason": _bounded_hook_text(payload.get("stop_reason"), 120),
            "state_preserved": True,
            "recovery": "allow_stop_then_ralph_resume",
        },
        output=excerpt,
    )


def handle_pretooluse(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    root = _find_project_root(payload)
    if root is None:
        return {"decision": "allow", "reason": "no loop-state.json found"}
    state = load_state(root / "loop-state.json")
    tool_name = str(payload.get("tool_name", ""))
    tool_input = _tool_input(payload)
    agent_id = _agent_id(payload)
    bound_card = _card_for_agent(state, agent_id)
    slice_owner_bind = False
    if bound_card is None and tool_name in {"Write", "Edit"}:
        owner = _slice_owner_card(root, state, _target_path(tool_input))
        if owner is not None:
            bound_card = owner
            slice_owner_bind = True
    role = "worker" if bound_card is not None else str(payload.get("ralph_role") or os.environ.get("RALPH_ROLE", "commander"))
    # Commander must never read long documents or subagent-only artifacts. A
    # single large Read (e.g. the stage-input-package embeds the whole
    # task_spec and is ~18K tokens) can blow the 60k context window in one
    # turn, before auto-compact (which only runs between turns) can act. The
    # Commander only dispatches subagents; the subagents read the docs.
    _commander_read_denied = False
    _commander_read_reason = None
    if role == "commander" and tool_name in {"Read", "Grep", "Glob"}:
        _tgt = _target_path(tool_input)
        if _tgt:
            _resolved = _resolved_target(root, _tgt)
            _rp = str(_resolved)
            if _rp.endswith("loop-state.json"):
                pass  # minimal state read still allowed
            elif any(
                seg in _rp
                for seg in (
                    "/loop-artifacts/contracts/",
                    "/loop-artifacts/stages/",
                    "/loop-artifacts/task-cards/",
                    "/loop-artifacts/gate-reviews/",
                )
            ):
                _commander_read_denied = True
                _commander_read_reason = tool_feedback(
                    "COMMANDER_DOC_READ",
                    detected=f"Commander 尝试读取子代理专用文档 `{_tgt}`。",
                    correction="Commander 只负责派发子代理；契约/模板/切片/输入包/任务卡由子代理读取。",
                    next_action="直接派发当前 pending 任务卡，不要读取这些文档。",
                    forbidden="用 Read/Grep/Glob 读取 loop-artifacts 下的长文档。",
                )
            else:
                try:
                    if _resolved.exists() and _resolved.stat().st_size > 25000:
                        _commander_read_denied = True
                        _commander_read_reason = tool_feedback(
                            "COMMANDER_LONG_READ",
                            detected=f"Commander 尝试读取约 {_resolved.stat().st_size // 1024}KB 的长文档 `{_tgt}`。",
                            correction="Commander 上下文窗口只有 60k，长文档会一次性撑爆它。",
                            next_action="直接派发 pending 任务卡；长文档由子代理读取。",
                            forbidden="用 Read/Grep/Glob 读取超过 ~25KB 的文件。",
                        )
                except OSError:
                    pass
    if _commander_read_denied:
        decision_value = "deny"
        decision_reason = _commander_read_reason
    else:
        decision = decide_tool(
            state,
            role,
            tool_name,
            target_path=_target_path(tool_input),
            command=_command(tool_input),
        )
        decision_value = decision.decision
        decision_reason = decision.reason
    card_id: str | None = str(bound_card["id"]) if bound_card is not None else None
    event_log_error = _commander_event_log_error(root, role, tool_name, tool_input)
    if event_log_error:
        decision_value = "deny"
        decision_reason = event_log_error
    if bound_card is not None and not slice_owner_bind:
        card_error = _card_tool_error(root, bound_card, tool_name, tool_input)
        if card_error:
            decision_value = "deny"
            decision_reason = card_error

    if tool_name == "Agent" and decision_value == "allow":
        card, card_error = _agent_card_error(state, tool_input)
        if card_error:
            decision_value = "deny"
            decision_reason = card_error
        else:
            card_id = str(card["id"])
            decision_value = "allow"
            decision_reason = f"approved task card {card_id}"
            if card.get("status") == "pending":
                state = _save_card_status(root, state, card_id, "dispatched")
    _record(
        root,
        "pretooluse_observed",
        {
            "tool_name": tool_name,
            "role": role,
            "mode": mode,
            "decision": decision_value,
            "reason": decision_reason,
            "task_card_id": card_id,
            "agent_id": agent_id,
        },
    )
    effective = "allow" if mode == "shadow" else decision_value
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": effective,
            "permissionDecisionReason": f"{decision_reason} (mode={mode})",
        }
    }


def handle_posttooluse(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    root = _find_project_root(payload)
    if root is not None:
        tool_name = str(payload.get("tool_name", ""))
        tool_input = _tool_input(payload)
        card_id: str | None = None
        card_status: str | None = None
        if tool_name == "Agent":
            state = load_state(root / "loop-state.json")
            card = card_by_ref(state, task_card_marker(tool_input))
            if card is not None:
                card_id = str(card["id"])
                card_status = _agent_response_status(_response_mapping(payload))
                # A foreground Agent response is not sufficient proof that a
                # gate fulfilled its required receipt.  SubagentStop gives us
                # the final message, which is where the tagged gate JSON is
                # validated before the card may become completed.
                if card.get("is_stage_gate") and card_status == "completed":
                    card_status = "dispatched"
                _save_card_status(root, state, card_id, card_status, agent_id=_agent_id(payload))
        _record(
            root,
            "posttooluse_observed",
            {
                "tool_name": tool_name,
                "mode": mode,
                "tool_response": _bounded_tool_response(payload.get("tool_response")),
                "task_card_id": card_id,
                "task_card_status": card_status,
                "agent_id": _agent_id(payload),
            },
        )
    return {}


def handle_subagentstart(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    """Bind a newly spawned Claude subagent to its already-approved card."""

    root = _find_project_root(payload)
    if root is None:
        return {}
    agent_id = _agent_id(payload)
    if not agent_id:
        _record(root, "subagentstart_observed", {"mode": mode, "reason": "missing_agent_id"})
        return {}
    state = load_state(root / "loop-state.json")
    card, reason = _bind_waiting_card(root, state, agent_id)
    if card is None:
        _record(
            root,
            "subagentstart_observed",
            {"mode": mode, "agent_id": agent_id, "agent_type": payload.get("agent_type"), "reason": reason},
        )
        return {}

    allowed_tools = ", ".join(str(tool) for tool in card.get("allowed_tools", [])) or "无"
    context = (
        f"RALPH 已将你绑定到任务卡 {card['id']}。你是独立 worker，不是 Commander；"
        f"只可使用：{allowed_tools}。只读取任务卡及其 document_refs，不得改 loop-state.json，"
        "不得自行推进阶段。若本卡是阶段门禁，结束时必须返回带 <RALPH_GATE_REVIEW> 标记的完整 JSON。"
    )
    _record(
        root,
        "subagent_card_bound",
        {"mode": mode, "agent_id": agent_id, "agent_type": payload.get("agent_type"), "task_card_id": card["id"]},
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": context,
        }
    }


def _parse_gate_review(output: str) -> tuple[dict[str, Any] | None, str | None]:
    marker = "<RALPH_GATE_REVIEW>"
    if marker not in output:
        return None, f"缺少 {marker} 标记"
    content = output.split(marker, 1)[1].lstrip()
    if content.startswith("```"):
        parts = content.split("\n", 1)
        content = parts[1] if len(parts) == 2 else ""
    start = content.find("{")
    if start < 0:
        return None, "门禁回执中没有 JSON 对象"
    try:
        parsed, _ = json.JSONDecoder().raw_decode(content[start:])
    except json.JSONDecodeError as exc:
        return None, f"门禁回执 JSON 无法解析：{exc.msg}"
    if not isinstance(parsed, Mapping):
        return None, "门禁回执必须是 JSON 对象"
    return dict(parsed), None


def _gate_review_error(card: Mapping[str, Any], review: Mapping[str, Any]) -> str | None:
    schema = card.get("output_schema", {})
    required = schema.get("required", []) if isinstance(schema, Mapping) else []
    missing = [str(key) for key in required if key not in review or review.get(key) in (None, "")]
    if missing:
        return "门禁回执缺少字段：" + ", ".join(missing)
    if str(review.get("reviewer_card_id", "")) != str(card.get("id", "")):
        return "门禁回执 reviewer_card_id 与绑定任务卡不一致"
    allowed_verdicts = schema.get("verdict_values", []) if isinstance(schema, Mapping) else []
    if allowed_verdicts and review.get("verdict") not in allowed_verdicts:
        return "门禁回执 verdict 不在允许值中"
    checks = review.get("checks")
    if not isinstance(checks, list) or not checks:
        return "门禁回执 checks 必须是非空列表"
    allowed_check_status = schema.get("check_status_values", []) if isinstance(schema, Mapping) else []
    for index, check in enumerate(checks):
        if not isinstance(check, Mapping):
            return f"门禁回执 checks[{index}] 必须是对象"
        if allowed_check_status and check.get("status") not in allowed_check_status:
            return f"门禁回执 checks[{index}].status 不在允许值中"
    return None


def _gate_receipt_format(card: Mapping[str, Any]) -> str:
    """Return a small fill-in skeleton for a rejected gate receipt."""

    schema = card.get("output_schema", {})
    schema = schema if isinstance(schema, Mapping) else {}
    verdicts = schema.get("verdict_values", ["pass", "rollback", "blocked_human"])
    statuses = schema.get("check_status_values", ["pass", "fail", "uncertain"])
    required = schema.get("required", [])
    example = {
        "reviewer_card_id": str(card.get("id", "<card-id>")),
        "verdict": "pass",
        "recommended_action": "advance",
        "checked_input_refs": ["<document-ref>"],
        "checked_output_refs": [],
        "checks": [
            {
                "criterion": "填写一项实际审计标准",
                "status": "pass",
                "evidence_refs": [],
                "note": "说明检查结果，不要只写通过。",
            }
        ],
        "blocking_findings": [],
        "summary": "用已有审计结果填写简短总结。",
    }
    return (
        "必须包含字段："
        + ", ".join(str(item) for item in required)
        + f"；verdict 只能是 {list(verdicts)}；checks.status 只能是 {list(statuses)}。"
        "下面是填写骨架，尖括号内容必须替换，不能原样提交：\n"
        "<RALPH_GATE_REVIEW>\n"
        + json.dumps(example, ensure_ascii=False, indent=2)
        + "\n</RALPH_GATE_REVIEW>"
    )


def _write_gate_review_artifact(root: Path, card_id: str, review: Mapping[str, Any]) -> str:
    digest = _output_digest(json.dumps(review, ensure_ascii=False, sort_keys=True))
    artifact_dir = root / "loop-artifacts" / "gate-reviews"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    safe_card_id = card_id.replace("/", "_")
    artifact_path = artifact_dir / f"{safe_card_id}-{digest}.json"
    if not artifact_path.exists():
        artifact_path.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(artifact_path.relative_to(root))


def _slice_still_skeleton(root: Path, slice_ref: str, state: Mapping[str, Any]) -> bool:
    """True when the builder's slice is byte-identical to the prefilled skeleton.

    The runtime pre-writes an editable skeleton so the builder only has to Edit
    fields.  A builder that merely returns the JSON as text leaves the file
    untouched; that must be blocked, not accepted as "written".
    """

    path = root / slice_ref
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    task_id = Path(slice_ref).stem
    skeleton = _skeleton_for_slice(state, slice_ref, task_id)
    if skeleton is None:
        return False
    return current == skeleton


def _skeleton_for_slice(state: Mapping[str, Any], slice_ref: str, task_id: str) -> Any | None:
    """Reconstruct the prefilled skeleton for a slice, at the slice's own stage/revision.

    The skeleton is ``payload[task_id]`` of the submission template.  It must be
    built for the *slice's* stage and revision (encoded in its path), not the
    current ``state`` revision — otherwise a revision bump makes a freshly
    generated skeleton differ from the on-disk one and the unfilled check
    false-negatives.
    """

    parts = Path(slice_ref).parts
    try:
        idx = parts.index("stages")
        stage_id = str(parts[idx + 1])
        revision = str(parts[idx + 2])
    except (ValueError, IndexError):
        stage_id = str(state.get("stage", {}).get("id", ""))
        revision = str(state.get("stage", {}).get("revision", "r1"))
    if not stage_id:
        return None
    rebuilt = dict(state)
    rebuilt["stage"] = {**state.get("stage", {}), "id": stage_id, "revision": revision}
    try:
        payload = stage_submission_template(rebuilt).get("payload", {})
    except Exception:
        return None
    return payload.get(task_id)


def _slice_missing_roles(
    root: Path, slice_ref: str, state: Mapping[str, Any], roles: list[str] | None = None
) -> list[str]:
    """Semantic roles still empty in a task_spec slice (drives incremental fill).

    When ``roles`` is given (a field-group builder), only those roles are
    checked against the partial file.  Otherwise all ``SEMANTIC_ROLES`` are
    checked (canonical slice).  Returns the still-empty roles.
    """

    task_id = Path(slice_ref).stem
    if not task_id.startswith("task_spec"):
        return []
    roles_to_check = list(roles) if roles else list(SEMANTIC_ROLES)
    try:
        current = json.loads((root / slice_ref).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return list(roles_to_check)
    if not isinstance(current, Mapping):
        return list(roles_to_check)
    semantic_map = current.get("semantic_map", {})
    filled_roles = set()
    if isinstance(semantic_map, Mapping):
        for role in roles_to_check:
            value = semantic_map.get(role)
            if isinstance(value, list) and value:
                filled_roles.add(role)
            elif isinstance(value, str) and value.strip():
                filled_roles.add(role)
    matrix = current.get("attribute_matrix", [])
    if isinstance(matrix, list):
        for entry in matrix:
            if isinstance(entry, Mapping) and entry.get("role") in roles_to_check:
                filled_roles.add(entry["role"])
    return [role for role in roles_to_check if role not in filled_roles]


def _revert_card_to_pending(root: Path, card_id: str) -> None:
    """Undo a hollow completion so the Commander must actually re-run the card."""

    state = load_state(root / "loop-state.json")
    card = state.get("subagent_cards", {}).get(str(card_id))
    if not isinstance(card, Mapping):
        return
    card = dict(card)
    card["status"] = "pending"
    card["agent_id"] = None
    card.pop("completed_at", None)
    card["gate_verdict"] = None
    card["gate_review_ref"] = None
    state.setdefault("subagent_cards", {})[str(card_id)] = card
    save_state(root / "loop-state.json", state)
    materialize_contract_documents(root, state)


def handle_subagentstop(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    """Close asynchronous task cards when Claude Code reports a subagent stop."""

    root = _find_project_root(payload)
    if root is None:
        return {}
    agent_id = _agent_id(payload)
    if not agent_id:
        _record(root, "subagentstop_observed", {"mode": mode, "reason": "missing_agent_id"})
        return {}
    state = load_state(root / "loop-state.json")
    matched = _card_for_agent(state, agent_id)
    if matched is None:
        matched, bind_reason = _bind_waiting_card(root, state, agent_id)
        if matched is None:
            _record(root, "subagentstop_observed", {"mode": mode, "agent_id": agent_id, "reason": bind_reason or "untracked_agent"})
            return {}
        _record(root, "subagent_card_bound_on_stop", {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"]})
    already_completed = matched.get("status") == "completed"
    stop_reason = str(payload.get("stop_reason", "")).lower()
    failed = bool(payload.get("error")) or stop_reason in {"error", "failed", "cancelled", "aborted"}
    if not failed and not matched.get("is_stage_gate"):
        expected_slice = next(
            (
                ref
                for ref in matched.get("input_refs", [])
                if isinstance(ref, str) and ref.startswith("loop-artifacts/stages/")
            ),
            None,
        )
        if expected_slice and not (root / expected_slice).exists():
            message = (
                f"builder 子代理 {matched['id']} 未写入其切片文件 `{expected_slice}`。"
                "请先 Write 该文件（顶层对象即 payload.<key>），再结束；不要只返回自然语言。"
            )
            _record(root, "builder_slice_missing", {"task_card_id": matched["id"], "expected_slice": expected_slice})
            if mode == "shadow":
                return {"systemMessage": "RALPH shadow：" + message}
            _revert_card_to_pending(root, str(matched["id"]))
            return {"decision": "block", "reason": message}
        if expected_slice and _slice_still_skeleton(root, expected_slice, state):
            message = (
                f"builder 子代理 {matched['id']} 只是把切片内容当作自然语言返回，"
                f"并没有用 Edit 工具修改骨架文件 `{expected_slice}`。"
                "该文件仍等于运行时预生成的空骨架。必须用 Edit 把每个占位/空字段替换为真实值；"
                "禁止把 JSON 作为纯文本返回。"
            )
            _record(root, "builder_slice_unfilled", {"task_card_id": matched["id"], "expected_slice": expected_slice})
            if mode == "shadow":
                return {"systemMessage": "RALPH shadow：" + message}
            _revert_card_to_pending(root, str(matched["id"]))
            return {"decision": "block", "reason": message}
        missing_roles = _slice_missing_roles(root, expected_slice, state, matched.get("slice_roles"))
        if missing_roles:
            owned = matched.get("slice_roles")
            scope = f"你负责的 {', '.join(owned)} 中" if owned else "七类语义角色中"
            message = (
                f"builder 子代理 {matched['id']} 的切片 `{expected_slice}` {scope}仍缺以下语义角色："
                f"{', '.join(missing_roles)}。"
                "这是增量填写：已填的语义角色不要重写，只针对仍为空（空数组）的角色用 Edit 补充真实条目，"
                "并补上对应 attribute_matrix 叶节点（concept/role/attribute/disposition/rationale）。"
                "你负责的角色都非空后才算完成。"
            )
            _record(
                root,
                "builder_slice_incomplete",
                {"task_card_id": matched["id"], "expected_slice": expected_slice, "missing_roles": missing_roles},
            )
            if mode == "shadow":
                return {"systemMessage": "RALPH shadow：" + message}
            _revert_card_to_pending(root, str(matched["id"]))
            return {"decision": "block", "reason": message}
        _record(
            root,
            "builder_slice_written",
            {"task_card_id": matched["id"], "expected_slice": expected_slice},
        )
    gate_review_ref: str | None = None
    gate_verdict: str | None = None
    if not failed and matched.get("is_stage_gate"):
        output = payload.get("last_assistant_message")
        review, review_error = _parse_gate_review(output if isinstance(output, str) else "")
        if review_error is None and review is not None:
            review_error = _gate_review_error(matched, review)
        if review_error:
            raw_output = output if isinstance(output, str) else ""
            artifact_ref = _invalid_output_artifact(root, _output_digest(raw_output), raw_output)
            _record(
                root,
                "subagent_gate_review_rejected",
                {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"], "error": review_error, "artifact_ref": artifact_ref},
                output=raw_output,
            )
            repair = gate_feedback(
                card_id=str(matched["id"]),
                error=feedback_context(review_error),
                expected=_gate_receipt_format(matched),
            )
            if mode == "shadow":
                return {"systemMessage": "RALPH shadow：" + repair}
            return {"decision": "block", "reason": repair}
        artifact_ref = _write_gate_review_artifact(root, str(matched["id"]), review)
        gate_review_ref = artifact_ref
        gate_verdict = str(review.get("verdict"))
        _record(
            root,
            "subagent_gate_review_received",
            {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"], "artifact_ref": artifact_ref, "verdict": review.get("verdict")},
        )
    if already_completed:
        _record(
            root,
            "subagentstop_observed",
            {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"], "reason": "already_completed"},
        )
        return {}
    if failed and not matched.get("is_stage_gate"):
        # A builder subagent died (e.g. the local backend's prefill memory
        # guard killed it).  Marking it "failed" would deadlock the Commander
        # forever (it cannot re-dispatch a failed card and just waits on the
        # unresolved binding).  Reopen it as pending so the loop can retry it
        # once resources free up, instead of rolling back the whole stage.
        _revert_card_to_pending(root, str(matched["id"]))
        _record(
            root,
            "builder_card_reverted_pending",
            {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"], "reason": "subagent_failed_reopen_for_retry"},
        )
        return {"systemMessage": "RALPH：构建子代理异常退出，任务卡已重新置为 pending 以便重试；待资源恢复后由 Commander 重新派发。"}
    status = "failed" if failed else "completed"
    updated_state = _save_card_status(root, state, str(matched["id"]), status, agent_id=agent_id)
    if status == "completed" and matched.get("slice_roles"):
        stage = updated_state.get("stage", {})
        groups = factor_groups(updated_state, str(stage.get("id")), "task_spec")
        partial_ids = [
            f"{stage.get('id')}-{stage.get('revision', 'r1')}-builder-task_spec-{group}"
            for group, _ in groups
        ]
        if all(updated_state.get("subagent_cards", {}).get(pid, {}).get("status") == "completed" for pid in partial_ids):
            merged = merge_task_spec_partials(
                root, str(stage.get("id")), str(stage.get("revision", "r1")), updated_state
            )
            if merged is not None:
                _record(root, "slice_merged", {"task_card_id": matched["id"], "canonical_slice": merged})
    if status == "completed" and gate_review_ref:
        updated_card = updated_state["subagent_cards"][str(matched["id"])]
        updated_card["gate_review_ref"] = gate_review_ref
        updated_card["gate_verdict"] = gate_verdict
        save_state(root / "loop-state.json", updated_state)
        materialize_contract_documents(root, updated_state)
    _record(
        root,
        "subagent_card_completed" if status == "completed" else "subagent_card_failed",
        {"mode": mode, "agent_id": agent_id, "task_card_id": matched["id"], "status": status},
    )
    return {}


def handle_userpromptsubmit(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    """Persist every human clarification as canonical task input before Claude sees it."""

    root = _find_project_root(payload)
    if root is None:
        return {}
    text = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(text, str) or not text.strip():
        return {}
    state = load_state(root / "loop-state.json")
    updated = record_human_input(state, text)
    save_state(root / "loop-state.json", updated)
    materialize_contract_documents(root, updated)
    _record(
        root,
        "human_input_received",
        {"mode": mode, "stage": updated.get("stage", {}).get("id"), "characters": len(text.strip())},
        output=text.strip(),
    )
    return {}


def handle_precompact(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    """Record a compaction attempt without ever blocking it.

    PreCompact is deliberately observational. Blocking compaction while the
    local backend is under memory pressure would remove the recovery path we
    are trying to protect.
    """

    root = _find_project_root(payload)
    if root is None:
        return {}
    _record(
        root,
        "context_compaction_started",
        {
            "mode": mode,
            "trigger": _bounded_hook_text(payload.get("trigger"), 80) or "unknown",
            "session_id": _bounded_hook_text(payload.get("session_id"), 160),
            "custom_instructions_characters": len(_bounded_hook_text(payload.get("custom_instructions"))),
        },
    )
    return {}


def handle_postcompact(payload: Mapping[str, Any], mode: str = "enforce") -> dict[str, Any]:
    """Record completion and a bounded excerpt of Claude's compact summary."""

    root = _find_project_root(payload)
    if root is None:
        return {}
    summary = _bounded_hook_text(payload.get("compact_summary"), 2400)
    _record(
        root,
        "context_compaction_completed",
        {
            "mode": mode,
            "trigger": _bounded_hook_text(payload.get("trigger"), 80) or "unknown",
            "session_id": _bounded_hook_text(payload.get("session_id"), 160),
            "summary_characters": len(summary),
            "summary_recorded": bool(summary),
        },
        output=summary or None,
    )
    return {}


def handle_stop(
    payload: Mapping[str, Any],
    mode: str = "enforce",
    auto_apply: bool = True,
) -> dict[str, Any]:
    root = _find_project_root(payload)
    if root is None:
        return {}
    state = load_state(root / "loop-state.json")
    if state.get("status") in {"completed", "stopped"}:
        return {}
    if state.get("status") == "blocked_human":
        output = payload.get("last_assistant_message")
        if not isinstance(output, str) or "<RALPH_STAGE_RESULT>" not in output:
            _record(
                root,
                "stop_allowed_human_block_waiting",
                {
                    "stage": state.get("stage", {}).get("id"),
                    "revision": state.get("stage", {}).get("revision"),
                    "state_preserved": True,
                },
            )
            return {}

    stop_hook_active = bool(payload.get("stop_hook_active"))

    # Infrastructure failures must be handled before parsing the final Agent
    # message. In particular, an oMLX prefill rejection can arrive as text in
    # last_assistant_message; treating it as an invalid stage action would
    # generate a repair prompt and make the next request even larger.
    runtime = _classify_runtime_interruption(payload)
    if runtime is not None:
        kind, excerpt = runtime
        _record_runtime_interruption(root, state, payload, kind, excerpt)
        if stop_hook_active:
            _record(
                root,
                "stop_hook_guarded",
                {"reason": "runtime_interruption_already_guarded", "kind": kind},
            )
            return {}
        # No decision=block here: the only safe recovery from a rejected
        # prefill is a new, shorter context. The persisted state remains at
        # the same stage and can be resumed explicitly.
        return {"systemMessage": _runtime_stop_message(state, kind, excerpt)[:3000]}

    # A Commander is allowed to finish its current turn while an internal
    # auditor/worker is still running.  Blocking this stop would make the
    # model search for a way around the already-correct dispatched state,
    # often by rereading loop-events.md or attempting a forbidden Write.
    # This does not advance the stage and does not complete the card; the
    # SubagentStop Hook remains the only completion authority.
    output = payload.get("last_assistant_message")
    candidate_action = None
    if auto_apply and isinstance(output, str) and output.strip():
        # Peek only at the action name.  A valid clarify result is the one
        # controlled exception: it is the Commander response to a completed
        # auditor rollback and must be allowed to reach the validator instead
        # of being hidden behind a stale dispatched-card wait.
        try:
            candidate_action = parse_action(output)
        except Exception:
            candidate_action = None

    waiting_cards = _current_dispatched_cards(state)
    if waiting_cards and not stop_hook_active and (
        candidate_action is None or candidate_action.action != "clarify"
    ):
        card_ids = [str(card.get("id", "?")) for card in waiting_cards]
        _record(
            root,
            "stop_allowed_waiting_for_subagent",
            {
                "task_card_ids": card_ids,
                "state_preserved": True,
                "advance_allowed": False,
                "recovery": "wait_for_subagent_stop_then_ralph_resume",
            },
        )
        return {
            "systemMessage": (
                "RALPH 已保留当前状态并结束 Commander 本轮：内部任务卡仍为 dispatched（"
                + ", ".join(card_ids)
                + "）。等待 SubagentStop 回执；不要重派、不要 Write 任务卡、不要标记 blocked_human。"
                "收到回执后用 `ralph resume <项目路径>` 开启短上下文继续。"
            )
        }
    if waiting_cards and stop_hook_active and (
        candidate_action is None or candidate_action.action != "clarify"
    ):
        # Claude Code may invoke Stop again with stop_hook_active=true while
        # an Agent task is still dispatched.  Do not parse an old Commander
        # message in that re-entry: it can be a stale advance/clarify result
        # from before the task was launched and would create a false protocol
        # repair loop.  Preserve the card; the outer supervisor will reconcile
        # it after the process exits, using the gate receipt as authority.
        _record(
            root,
            "stop_allowed_waiting_for_subagent",
            {
                "task_card_ids": [str(card.get("id", "?")) for card in waiting_cards],
                "state_preserved": True,
                "advance_allowed": False,
                "stop_hook_active": True,
                "recovery": "subagentstop_or_outer_ralph_loop",
            },
        )
        return {}

    result: dict[str, Any] | None = None
    if auto_apply and isinstance(output, str) and output.strip():
        result = _apply_agent_result(root, output)
        if result["status"] == "duplicate":
            _record(
                root,
                "stop_hook_guarded",
                {"reason": "duplicate_agent_output", "output_sha256": result["output_sha256"]},
            )
            # Never allow an idle stop on a no-progress duplicate: keep the
            # Commander in the loop and point it at the next concrete action.
            return _stop_response(
                "该结构化阶段结果已经应用过（重复输出），状态已保存且未改变。请勿重复提交；"
                "直接按当前阶段继续唯一允许的下一个动作：若有 pending 任务卡就派发它，"
                "否则输出 advance / clarify。",
                mode,
            )
        if result["status"] == "applied":
            state = load_state(root / "loop-state.json")
            action = result["action"]
            if state.get("status") in {"completed", "stopped"}:
                return {}
            # A human block is a terminal result for this Commander turn. Do
            # not return decision=block here: that would make Claude continue
            # the same context after the state was already persisted, often
            # producing an unnecessary ToolSearch/read loop. The question
            # bundle is already in the applied action and event log; allow
            # the session to stop and let the next human reply resume it.
            if state.get("status") == "blocked_human":
                _record(
                    root,
                    "stop_allowed_after_apply",
                    {
                        "action": action["action"],
                        "stage": state.get("stage", {}).get("id"),
                        "status": "blocked_human",
                        "state_preserved": True,
                    },
                )
                return {}
            prompt = PromptRenderer().compact_recovery_prompt(
                state,
                reason=f"已自动应用动作 {action['action']}",
                error_kind="continuation",
                action_hint="读取新的当前阶段后继续；不要复制完整计划，不要重做已完成阶段。",
            ).text
            reason = (
                f"RALPH 已自动应用动作 `{action['action']}`，状态已保存。"
                "请继续执行新的当前阶段：\n"
                + prompt
            )
            if stop_hook_active:
                _record(
                    root,
                    "stop_hook_guarded",
                    {"reason": "stop_hook_active_after_new_action", "output_sha256": result["output_sha256"]},
                )
                return {"systemMessage": reason[:12000]}
            _record(
                root,
                "stop_intercepted_after_apply",
                {"action": action["action"], "stage": state.get("stage", {}).get("id")},
            )
            return _stop_response(reason, mode)

        # Invalid output is not allowed to alter state. Give the Agent a
        # generated repair prompt; enforce mode turns it into a real block.
        state = load_state(root / "loop-state.json")
        repair = PromptRenderer().repair_prompt(
            state,
            result["error"],
            raw_output=output,
        ).text
        reason = (
            "RALPH_STAGE_RESULT 未通过字段或状态校验：\n"
            + repair
            + "\n本次原始结果已保存为阶段工件："
            + str(result["artifact_ref"])
            + "\n需要机械复核时只运行：ralph validate . --result "
            + str(result["artifact_ref"])
        )
        _record(
            root,
            "stage_result_repair_prompted",
            {"error": result["error"], "artifact_ref": result["artifact_ref"]},
        )
        repair_count = _consecutive_protocol_rejections(root)
        if repair_count >= MAX_PROTOCOL_REPAIRS_PER_CONTEXT:
            # Returning only a systemMessage deliberately allows Claude to
            # stop.  The durable state is unchanged; the outer supervisor
            # observes the exit and starts a fresh context with a compact
            # prompt.  This is the escape hatch for a same-context XML/JSON
            # repair loop.
            _record(
                root,
                "stage_result_repair_exhausted",
                {
                    "repair_count": repair_count,
                    "max_repairs": MAX_PROTOCOL_REPAIRS_PER_CONTEXT,
                    "recovery": "outer_ralph_loop_fresh_context",
                    "state_preserved": True,
                },
            )
            return {
                "systemMessage": render_feedback(
                    "REPAIR_BUDGET_EXHAUSTED",
                    detected=(
                        f"当前 Claude 上下文已连续 {repair_count} 次输出无效阶段结果。"
                    ),
                    correction=(
                        "结束当前上下文；RALPH 外层监督器会读取持久化状态并启动新的短上下文。"
                    ),
                    next_action="不要继续输出 XML、半截 JSON、自然语言或重复读取历史日志。",
                    forbidden="修改 loop-state.json、伪造已通过、继续同一格式修复循环。",
                )[:3000]
            }
        if stop_hook_active:
            _record(
                root,
                "stop_hook_guarded",
                {"reason": "invalid_result_after_stop_hook", "output_sha256": result["output_sha256"]},
            )
            # Block the stop so the model is forced to fix the malformed
            # RALPH_STAGE_RESULT in the same context (the repair prompt is in
            # `reason`). Returning only a systemMessage would let Claude Code
            # end the turn and idle; the outer loop would then relaunch a fresh
            # context instead of repairing inline. The repair budget escape
            # hatch above still allows a stop once MAX_PROTOCOL_REPAIRS_PER_CONTEXT
            # is reached.
            return _stop_response(reason, mode)
        return _stop_response(reason, mode)

    if stop_hook_active:
        _record(root, "stop_hook_guarded", {"reason": "stop_hook_active"})
        return {}

    prompt = PromptRenderer().compact_recovery_prompt(
        state,
        reason="Stop Hook 收到停止信号，但没有收到可应用的结构化阶段动作。",
        error_kind="continuation",
    ).text
    reason = (
        render_feedback(
            "STOP_WITHOUT_ACTION",
            detected="Stop Hook 没有收到可应用的 RALPH_STAGE_RESULT，也没有可确认的阶段完成动作。",
            correction="不要把普通总结、READY 或空消息当成阶段完成。",
            next_action="按下面的短恢复指令执行当前阶段唯一允许的动作。",
            forbidden="重做历史、完整读取 loop-events.md、直接修改状态或重复派发。",
        )
        + "\n"
        + prompt
    )
    _record(root, "stop_intercepted", {"status": state.get("status"), "stage": state.get("stage", {}).get("id")})
    return _stop_response(reason, mode)


def handle_hook(
    event: str,
    payload: Mapping[str, Any],
    mode: str = "enforce",
    auto_apply: bool = True,
) -> dict[str, Any]:
    if event == "pretooluse":
        return handle_pretooluse(payload, mode)
    if event == "posttooluse":
        return handle_posttooluse(payload, mode)
    if event == "subagentstart":
        return handle_subagentstart(payload, mode)
    if event == "subagentstop":
        return handle_subagentstop(payload, mode)
    if event == "userpromptsubmit":
        return handle_userpromptsubmit(payload, mode)
    if event == "precompact":
        return handle_precompact(payload, mode)
    if event == "postcompact":
        return handle_postcompact(payload, mode)
    if event == "stop":
        return handle_stop(payload, mode, auto_apply=auto_apply)
    raise ValueError(f"unsupported Hook event: {event}")


def run_hook(
    event: str,
    payload_text: str,
    mode: str = "enforce",
    auto_apply: bool = True,
) -> str:
    payload = json.loads(payload_text or "{}")
    result = handle_hook(event, payload, mode, auto_apply=auto_apply)
    if event == "stop":
        # Canonical turn-completion marker. Claude idles at the interactive
        # prompt after a Stop and never exits on its own, so the outer
        # `ralph loop` supervisor watches for this marker and relaunches the
        # next fresh context immediately instead of waiting for the 600s idle
        # timeout. This keeps the AI working uninterrupted.
        root = _find_project_root(payload)
        if root is not None:
            _record(root, "ralph_stop_handled", {"mode": mode, "auto_apply": auto_apply})
    return json.dumps(result, ensure_ascii=False)
