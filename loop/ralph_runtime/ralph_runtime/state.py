"""Minimal loop-state.json persistence and pure action application."""

from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .contracts import ensure_stage_cards
from .machine import transition_for_action
from .nodes import DEFAULT_GRAPH, NodeGraph
from .protocol import ActionResult, ProtocolError, validate_action


DEFAULT_ALLOWED_ACTIONS = [
    "advance", "rollback", "blocked_human", "skip_blocked", "candidate",
    "explore", "dispatch", "join", "clarify", "repair_prompt",
]

CURRENT_SCHEMA_VERSION = 4


def _initial_task_spec(task: str, source: str | None) -> dict[str, Any]:
    """Create the canonical input record before clarification is complete.

    In field-centric mode (``RALPH_FIELD_GATE`` set) the attribute_matrix is
    seeded with the task itself as a ``confirmed`` background field, so the
    field gate has a real starting point ("已知背景字段就是已有条件") and the
    Commander only fills the remaining gaps.
    """

    attribute_matrix: list[dict[str, Any]] = []
    if os.environ.get("RALPH_FIELD_GATE") and task:
        attribute_matrix.append({
            "concept": "用户原始任务",
            "role": "background",
            "attribute": "任务描述",
            "disposition": "confirmed",
            "rationale": "用户初始任务输入，作为本阶段已知背景字段。",
            "evidence_refs": ["user:initial_task"],
            "confidence": 1.0,
            "impact": "material",
            "reversible": False,
        })
    return {
        "status": "unclarified",
        "authoritative_inputs": [
            {"kind": "initial_task", "source": source, "text": task}
        ] if task else [],
        "semantic_map": {},
        "attribute_matrix": attribute_matrix,
        "constraints": [],
        "assumptions": [],
        "open_questions": [],
        "scenarios": [],
        "success_criteria": [],
    }


def _explode_comma_fields(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """v2 field proliferation: split a field whose ``attribute`` contains
    commas into independent sub-fields sharing the same concept.

    This is the deterministic, model-free half of field growth: the Commander
    writes one comma-separated dimension string (e.g. "性价比, 显存, 功耗"),
    and the runtime explodes it into separate fields the Commander then labels
    with a disposition. Idempotent: already-split fields (no comma) pass through.
    """

    if not isinstance(matrix, list):
        return matrix
    out: list[dict[str, Any]] = []
    for leaf in matrix:
        if not isinstance(leaf, Mapping):
            out.append(leaf)
            continue
        attr = leaf.get("attribute")
        if isinstance(attr, str) and "," in attr:
            parts = [p.strip() for p in attr.split(",") if p.strip()]
            for part in parts:
                child = dict(leaf)
                child["attribute"] = part
                if not child.get("disposition"):
                    child["disposition"] = "pending"
                out.append(child)
        else:
            out.append(leaf)
    return out


def field_completeness(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the v2 completion verdict used by the field gate.

    - splittable: fields whose ``attribute`` still contains a comma.
    - researching: fields still ``research_required`` without evidence.
    - pending: fields not yet dispositioned.
    - complete: none of the above remain.
    """

    splittable: list[str] = []
    researching: list[str] = []
    pending: list[str] = []
    if isinstance(matrix, list):
        for leaf in matrix:
            if not isinstance(leaf, Mapping):
                continue
            concept = str(leaf.get("concept") or leaf.get("attribute") or "?")
            attr = leaf.get("attribute")
            if isinstance(attr, str) and "," in attr:
                splittable.append(concept)
                continue
            disp = leaf.get("disposition")
            if disp in (None, "", "pending"):
                pending.append(concept)
            elif disp == "research_required":
                refs = leaf.get("evidence_refs")
                if not isinstance(refs, list) or not refs:
                    researching.append(concept)
    return {
        "splittable": splittable,
        "researching": researching,
        "pending": pending,
        "complete": not (splittable or researching or pending),
    }


def create_state(
    project_id: str,
    graph: NodeGraph = DEFAULT_GRAPH,
    task: str | None = None,
) -> dict[str, Any]:
    node = graph.get("01")
    task_text = task or ""
    task_source = "ralph run" if task else None
    state = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "project_id": project_id,
        "task": {
            "description": task_text,
            "source": task_source,
        },
        "task_spec": _initial_task_spec(task_text, task_source),
        "status": "running",
        "stage": {
            "id": node.id,
            "revision": "r1",
            **node.to_dict(),
        },
        "plan": {"revision": "r1", "nodes": [], "parallel_groups": [], "joins": []},
        "queue": {"ready": [], "blocked_human": [], "candidates": []},
        "task_intake": None,
        "task_intake_history": [],
        "exploration_history": [],
        "clarification_history": [],
        "last_exploration": None,
        "active_tasks": {},
        "allowed_actions": list(DEFAULT_ALLOWED_ACTIONS),
        "last_action": None,
        "last_result": None,
        "last_event_id": None,
        "history": [],
        "run_history": [],
        "subagent_cards": {},
    }
    return ensure_stage_cards(state)


def migrate_state(raw: Mapping[str, Any], graph: NodeGraph = DEFAULT_GRAPH) -> dict[str, Any]:
    if isinstance(raw.get("stage"), Mapping) and raw.get("schema_version"):
        state = copy.deepcopy(dict(raw))
        state["schema_version"] = CURRENT_SCHEMA_VERSION
        state.setdefault("task", {"description": "", "source": None})
        task = state["task"] if isinstance(state["task"], Mapping) else {"description": "", "source": None}
        state["task"] = dict(task)
        state.setdefault(
            "task_spec",
            _initial_task_spec(str(task.get("description", "")), task.get("source")),
        )
        allowed_actions = state.setdefault("allowed_actions", list(DEFAULT_ALLOWED_ACTIONS))
        if isinstance(allowed_actions, list):
            for action_name in DEFAULT_ALLOWED_ACTIONS:
                if action_name not in allowed_actions:
                    allowed_actions.append(action_name)
        queue = state.setdefault("queue", {"ready": [], "blocked_human": [], "candidates": []})
        if isinstance(queue, dict):
            queue.setdefault("ready", [])
            queue.setdefault("blocked_human", [])
            queue.setdefault("candidates", [])
        state.setdefault("plan", {"revision": "r1", "nodes": [], "parallel_groups": [], "joins": []})
        state.setdefault("history", [])
        state.setdefault("run_history", [])
        state.setdefault("task_intake", None)
        state.setdefault("task_intake_history", [])
        state.setdefault("exploration_history", [])
        state.setdefault("last_exploration", None)
        state.setdefault("clarification_history", [])
        state.setdefault("subagent_cards", {})
        return ensure_stage_cards(state)

    phase = str(raw.get("loop_phase", raw.get("stage_id", "01")))
    stage_id = phase if phase in graph else "01"
    state = create_state(str(raw.get("project_id", raw.get("owner_project", "unknown"))), graph)
    state["legacy"] = copy.deepcopy(dict(raw))
    state["status"] = "running" if raw.get("status") in (None, "active") else str(raw["status"])
    node = graph.get(stage_id)
    state["stage"] = {"id": node.id, "revision": "r1", **node.to_dict()}
    state["iteration"] = raw.get("iteration", 0)
    return state


def load_legacy_markdown(
    path: str | Path,
    project_id: str,
    graph: NodeGraph = DEFAULT_GRAPH,
) -> dict[str, Any] | None:
    """Read the small key/value header used by the legacy Ralph plugin.

    Legacy projects often have useful completed-loop information but no
    ``loop-state.json``.  This migration is deliberately limited to the
    machine-readable header; the original Markdown file remains untouched and
    is also retained under ``state['legacy']`` by :func:`migrate_state`.
    """

    legacy_path = Path(path)
    if not legacy_path.exists():
        return None
    raw: dict[str, Any] = {}
    for line in legacy_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$", line)
        if match:
            raw[match.group(1)] = match.group(2)
    if not raw:
        return None

    raw["project_id"] = project_id
    phase = str(raw.get("loop_phase", "01"))
    phase_match = re.search(r"(?:1|2)-loop/(\d{1,2})", phase)
    if phase_match:
        raw["loop_phase"] = phase_match.group(1).zfill(2)
    raw["status"] = "completed" if "COMPLETED" in phase.upper() else raw.get("status", "active")
    return migrate_state(raw, graph)


def set_task(state: Mapping[str, Any], task: str, source: str = "ralph run") -> dict[str, Any]:
    """Attach the user's current task without changing the workflow stage."""

    updated = copy.deepcopy(dict(state))
    updated["task"] = {"description": task, "source": source}
    updated["task_spec"] = _initial_task_spec(task, source)
    stage = updated.get("stage", {})
    stage_id = str(stage.get("id", "")) if isinstance(stage, Mapping) else ""
    revision = str(stage.get("revision", "")) if isinstance(stage, Mapping) else ""
    cards = updated.get("subagent_cards", {})
    if isinstance(cards, Mapping):
        updated["subagent_cards"] = {
            card_id: card
            for card_id, card in cards.items()
            if not (
                isinstance(card, Mapping)
                and str(card.get("stage_id")) == stage_id
                and str(card.get("revision")) == revision
                and str(card.get("status")) in {"pending", "dispatched"}
            )
        }
    return ensure_stage_cards(updated)


def record_human_input(
    state: Mapping[str, Any], text: str, source: str = "UserPromptSubmit"
) -> dict[str, Any]:
    """Append a user clarification to the canonical task input, never to history only."""

    cleaned = text.strip()
    if not cleaned:
        return copy.deepcopy(dict(state))
    updated = copy.deepcopy(dict(state))
    task_spec = updated.setdefault("task_spec", _initial_task_spec("", None))
    if not isinstance(task_spec, dict):
        task_spec = _initial_task_spec("", None)
        updated["task_spec"] = task_spec
    inputs = task_spec.setdefault("authoritative_inputs", [])
    if not isinstance(inputs, list):
        inputs = []
        task_spec["authoritative_inputs"] = inputs
    entry = {"kind": "human_input", "source": source, "text": cleaned}
    if not inputs or inputs[-1] != entry:
        inputs.append(entry)
    if updated.get("status") == "blocked_human":
        updated["status"] = "running"
    return ensure_stage_cards(updated)


def update_subagent_card(
    state: Mapping[str, Any],
    card_id: str,
    status: str,
    *,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Persist card lifecycle evidence and unlock dependent DAG tasks when done."""

    if status not in {"pending", "dispatched", "completed", "failed"}:
        raise ValueError(f"unsupported task-card status: {status}")
    updated = copy.deepcopy(dict(state))
    cards = updated.get("subagent_cards", {})
    if not isinstance(cards, dict) or card_id not in cards or not isinstance(cards[card_id], Mapping):
        raise KeyError(f"unknown task card: {card_id}")
    card = dict(cards[card_id])
    # Task-card lifecycle is monotonic for ordinary Hook observations.  A
    # late PostToolUse event must never turn a completed gate back into
    # dispatched/pending (the exact regression that used to deadlock the
    # Commander).  Explicit recovery uses reset_subagent_card instead.
    prior_status = str(card.get("status", "pending"))
    if prior_status in {"completed", "failed"} and status != prior_status:
        status = prior_status
    card["status"] = status
    if agent_id:
        card["agent_id"] = agent_id
    cards[card_id] = card
    task_id = card.get("task_id")
    if status == "completed" and task_id:
        plan = updated.get("plan", {})
        if isinstance(plan, Mapping):
            plan_copy = copy.deepcopy(dict(plan))
            completed = list(plan_copy.get("completed", []))
            if task_id not in completed:
                completed.append(task_id)
            plan_copy["completed"] = completed
            updated["plan"] = plan_copy
    return ensure_stage_cards(updated)


def reset_subagent_card(
    state: Mapping[str, Any],
    card_id: str,
    allow_dispatched: bool = False,
) -> dict[str, Any]:
    """Make one incorrectly terminal task card eligible for a clean re-dispatch.

    This is deliberately narrower than a workflow rollback: it is for a
    controller/runtime error where a card was marked completed or failed
    without a trustworthy result.  The caller must provide the safety policy
    (for example, checking that a stage-gate receipt does not exist) and
    journal the reason.  We retain the previous worker identity as evidence
    but clear the live binding so a future ``SubagentStart`` can bind safely.
    """

    updated = copy.deepcopy(dict(state))
    cards = updated.get("subagent_cards", {})
    if not isinstance(cards, dict) or card_id not in cards or not isinstance(cards[card_id], Mapping):
        raise KeyError(f"unknown task card: {card_id}")
    card = dict(cards[card_id])
    prior_status = str(card.get("status", "pending"))
    allowed_statuses = {"completed", "failed"}
    if allow_dispatched:
        allowed_statuses.add("dispatched")
    if prior_status not in allowed_statuses:
        raise ValueError(
            f"task card {card_id} is {prior_status!r}; only completed or failed cards can be recovered"
        )
    if card.get("agent_id"):
        card["last_agent_id"] = str(card["agent_id"])
    card.pop("agent_id", None)
    card["status"] = "pending"
    card["recovery_count"] = int(card.get("recovery_count", 0)) + 1
    cards[card_id] = card

    # A re-opened DAG worker must no longer be counted as complete.  Stage
    # gates do not have task_id, but handling both keeps this primitive safe
    # for future runtime recovery paths.
    task_id = card.get("task_id")
    if task_id:
        plan = updated.get("plan", {})
        if isinstance(plan, Mapping):
            plan_copy = copy.deepcopy(dict(plan))
            plan_copy["completed"] = [
                item for item in plan_copy.get("completed", []) if str(item) != str(task_id)
            ]
            updated["plan"] = plan_copy
    return ensure_stage_cards(updated)


def start_new_task(
    state: Mapping[str, Any],
    task: str,
    graph: NodeGraph = DEFAULT_GRAPH,
    source: str = "ralph run",
) -> dict[str, Any]:
    """Reopen a completed project for an explicit new ``ralph run``."""

    previous = copy.deepcopy(dict(state))
    project_id = str(previous.get("project_id") or "unknown")
    fresh = create_state(project_id, graph, task=task)
    fresh["task"]["source"] = source
    prior_runs = list(previous.get("run_history", []))
    prior_runs.append(
        {
            "task": copy.deepcopy(previous.get("task", {})),
            "status": previous.get("status"),
            "stage": copy.deepcopy(previous.get("stage", {})),
            "iteration": previous.get("iteration"),
        }
    )
    fresh["run_history"] = prior_runs
    fresh["task_intake_history"] = copy.deepcopy(previous.get("task_intake_history", []))
    fresh["exploration_history"] = copy.deepcopy(previous.get("exploration_history", []))
    if "legacy" in previous:
        fresh["legacy"] = copy.deepcopy(previous["legacy"])
    return fresh


def start_task_from_exploration(
    state: Mapping[str, Any],
    selection: Mapping[str, Any],
    exploration: Mapping[str, Any] | None = None,
    graph: NodeGraph = DEFAULT_GRAPH,
) -> dict[str, Any]:
    """Start a selected task as a fresh stage-01 run and retain intake lineage."""

    title = str(selection.get("title", "")).strip()
    task_id = str(selection.get("task_id", "")).strip()
    source_path = str(selection.get("source_path", "")).strip()
    if not title or not task_id or not source_path:
        raise ProtocolError("exploration selected_task requires task_id, title and source_path")
    source = str(selection.get("source", "task_board")).strip() or "task_board"
    intake = copy.deepcopy(dict(selection))
    intake["source"] = source
    intake["status"] = "selected"
    intake["selected_from"] = "exploration"
    fresh = start_new_task(
        state,
        title,
        graph=graph,
        source=f"tasks:{source_path}",
    )
    fresh["task"]["board_task_id"] = task_id
    fresh["task"]["board_ref"] = source_path
    prior_queue = state.get("queue", {})
    if isinstance(prior_queue, Mapping):
        fresh["queue"]["candidates"] = copy.deepcopy(list(prior_queue.get("candidates", [])))
    fresh["task_intake"] = intake
    history = list(state.get("task_intake_history", []))
    fresh["task_intake_history"] = history + [copy.deepcopy(intake)]
    exploration_record = copy.deepcopy(dict(exploration or {}))
    exploration_record["selected_task"] = copy.deepcopy(intake)
    exploration_record["selected_at_stage"] = "exploration"
    exploration_history = list(state.get("exploration_history", []))
    fresh["exploration_history"] = exploration_history + [exploration_record]
    fresh["last_exploration"] = exploration_record
    fresh["task_spec"]["authoritative_inputs"].append(
        {
            "kind": "task_board_selection" if source == "task_board" else "candidate_selection",
            "source": source_path,
            "task_id": task_id,
            "text": title,
        }
    )
    return fresh


def _stage_artifact_dir(root: Path) -> Path:
    """Directory holding one JSON file per (stage, revision) with that stage's
    heavy intermediate process (subagent cards).  loop-state.json only keeps a
    pointer; the verbose per-stage working state lives here."""

    d = root / "loop-artifacts" / "stages"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_segment(stage_id: str, revision: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", f"{stage_id}-{revision}")


def _persist_stage_cards(root: Path, state: Mapping[str, Any]) -> None:
    """Write each stage's subagent cards to its own artifact file and drop them
    from the in-memory copy we serialize into loop-state.json."""

    cards = state.get("subagent_cards")
    if not isinstance(cards, Mapping) or not cards:
        return
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for cid, card in cards.items():
        if not isinstance(card, Mapping):
            continue
        key = (str(card.get("stage_id") or "unknown"), str(card.get("revision") or "r1"))
        groups.setdefault(key, {})[cid] = card
    for (sid, rev), group in groups.items():
        segment = _safe_segment(sid, rev)
        out = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "stage_id": sid,
            "revision": rev,
            "subagent_cards": group,
        }
        encoded = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        target = _stage_artifact_dir(root) / f"{segment}.json"
        fd, tmp_name = tempfile.mkstemp(prefix=f".{segment}.", suffix=".tmp", dir=target.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, target)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)


def _load_stage_cards(root: Path, state: dict[str, Any]) -> None:
    """Merge persisted per-stage card files back into ``state['subagent_cards']``
    (on top of any cards already present, e.g. legacy inline cards)."""

    d = root / "loop-artifacts" / "stages"
    if not d.is_dir():
        return
    merged = dict(state.get("subagent_cards") or {})
    for f in sorted(d.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, Mapping):
            cards = data.get("subagent_cards")
            if isinstance(cards, Mapping):
                merged.update(cards)
    state["subagent_cards"] = merged


def _snapshot_dir(root: Path) -> Path:
    d = root / "loop-artifacts" / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _attach_stage_artifact(path: Path, state: dict[str, Any], raw: Mapping[str, Any]) -> None:
    """Re-merge the trimmed ``task_spec`` back from its stage artifact.

    ``save_state`` strips ``task_spec`` out of ``loop-state.json`` into
    ``loop-artifacts/<stage>-<rev>.json`` (the 0x-rx.json).  On load we read it
    back so the in-memory state keeps the full field table for the gate/prompts,
    while the on-disk ``loop-state.json`` stays minimal."""

    if not isinstance(raw, Mapping) or "task_spec" in raw:
        return
    ca = raw.get("current_artifact")
    if not ca:
        return
    artifact = path.parent / str(ca)
    try:
        spec = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return
    if isinstance(spec, Mapping):
        state["task_spec"] = spec


def _recover_state_file(path: Path, graph: NodeGraph, exc: Exception) -> dict[str, Any] | None:
    """Self-heal a corrupt ``loop-state.json``.

    Tries, in order: the previous good ``.bak``, then the most recent
    per-stage snapshot under ``loop-artifacts/snapshots``.  On a successful
    recovery the good content is written back over the corrupt main file so
    subsequent loads are clean.  Returns ``None`` when nothing usable exists
    (caller should then re-raise)."""

    candidates: list[Path] = []
    bak = path.with_name(path.name + ".bak")
    if bak.exists():
        candidates.append(bak)
    snap_dir = path.parent / "loop-artifacts" / "snapshots"
    if snap_dir.is_dir():
        candidates.extend(sorted(snap_dir.glob("loop-state.*.json"), reverse=True))
    if not candidates:
        return None
    last_err: Exception = exc
    for cand in candidates:
        try:
            text = cand.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, json.JSONDecodeError, ValueError) as inner:
            last_err = inner
            continue
        if not isinstance(data, Mapping):
            continue
        # Repair the corrupt main file in place so later loads are clean.
        try:
            path.write_text(text, encoding="utf-8")
        except OSError:
            pass
        state = migrate_state(data, graph)
        _attach_stage_artifact(path, state, data)
        _load_stage_cards(path.parent, state)
        return state
    raise last_err


def load_state(path: str | Path, graph: NodeGraph = DEFAULT_GRAPH) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return create_state(str(path.parent), graph)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        recovered = _recover_state_file(path, graph, exc)
        if recovered is not None:
            return recovered
        raise
    if not isinstance(raw, Mapping):
        raise ValueError(f"state file must contain a JSON object: {path}")
    state = migrate_state(raw, graph)
    _attach_stage_artifact(path, state, raw)
    _load_stage_cards(path.parent, state)
    return state


def save_state(path: str | Path, state: Mapping[str, Any]) -> None:
    path = Path(path)
    root = path.parent
    root.mkdir(parents=True, exist_ok=True)
    # Persist the heavy per-stage intermediate process outside loop-state.json,
    # then serialize a slim copy without subagent_cards.
    _persist_stage_cards(root, state)
    slim = dict(state)
    slim.pop("subagent_cards", None)
    # 把最占体积的 task_spec（含 attribute_matrix）剥离到本阶段的「阶段文件」
    # loop-artifacts/<stage>-<rev>.json（即 0x-rx.json），loop-state.json 只保留
    # 状态标记 + 指针，磁盘上极小、不易损坏。内存态仍保留 task_spec 供字段门禁/提示使用。
    stage = state.get("stage") if isinstance(state, Mapping) else None
    if isinstance(stage, Mapping) and isinstance(state.get("task_spec"), Mapping) and state["task_spec"]:
        seg = _safe_segment(str(stage.get("id", "unknown")), str(stage.get("revision", "r1")))
        artifact_path = root / "loop-artifacts" / f"{seg}.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            json.dumps(state["task_spec"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        slim.pop("task_spec", None)
        slim["current_artifact"] = f"loop-artifacts/{seg}.json"
    encoded = json.dumps(slim, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    # Keep a ``.bak`` of the previously-persisted (valid) content so a future
    # corrupt write can self-heal.  Only back up content that parses, so we
    # never overwrite a good ``.bak`` with a corrupt main.
    if path.exists():
        try:
            prev = path.read_text(encoding="utf-8")
            json.loads(prev)
            bak = path.with_name(path.name + ".bak")
            bak.write_text(prev, encoding="utf-8")
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    # Per-stage snapshot: the latest saved state while in a given stage.  Used by
    # `ralph recover-state --stage <id>` to "reset to the previous stage".
    stage = state.get("stage") if isinstance(state, Mapping) else None
    stage_id = str(stage.get("id", "")) if isinstance(stage, Mapping) else ""
    if stage_id:
        _snapshot_dir(root) / f"loop-state.{stage_id}.json"
        (_snapshot_dir(root) / f"loop-state.{stage_id}.json").write_text(
            encoded, encoding="utf-8"
        )

    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _next_revision(current: str) -> str:
    try:
        return f"r{int(current.lstrip('r')) + 1}"
    except (AttributeError, ValueError):
        return "r1"


def apply_action(
    state: Mapping[str, Any],
    action: ActionResult,
    graph: NodeGraph = DEFAULT_GRAPH,
    *,
    enforce_contracts: bool = True,
) -> dict[str, Any]:
    validate_action(action, state, enforce_contracts=enforce_contracts)
    updated = copy.deepcopy(dict(state))
    current_stage = str(updated["stage"]["id"])
    prior_status = str(updated.get("status", "running"))

    if action.action == "skip_blocked":
        if prior_status != "blocked_human":
            raise ProtocolError("skip_blocked requires state.status=blocked_human")
        next_stage = action.next_stage
    else:
        next_stage = action.next_stage

    if (
        not enforce_contracts
        and action.action == "advance"
        and current_stage == "06"
        and next_stage == "completed"
    ):
        # Historical event logs were allowed to terminate directly at 06.
        # Keep those logs replayable while rejecting the shortcut for all new
        # live actions in protocol.py.
        internal = "completed"
    elif action.action in {"advance", "rollback", "blocked_human", "skip_blocked", "explore"}:
        machine_status = prior_status if action.action == "skip_blocked" else (
            "exploration" if current_stage == "exploration" else "running"
        )
        internal = transition_for_action(current_stage, machine_status, action.action, next_stage, action.rollback_to)
    else:
        internal = "exploration" if current_stage == "exploration" else f"stage_{current_stage}"

    if action.action == "advance":
        if current_stage == "01" and action.payload and isinstance(action.payload.get("task_spec"), Mapping):
            applied_spec = copy.deepcopy(dict(action.payload["task_spec"]))
            matrix = applied_spec.get("attribute_matrix")
            if isinstance(matrix, list):
                applied_spec["attribute_matrix"] = _explode_comma_fields(matrix)
            updated["task_spec"] = applied_spec
            updated["task_spec"]["status"] = "clarified"
        if current_stage == "02" and action.payload and isinstance(action.payload.get("plan"), Mapping):
            updated["plan"] = copy.deepcopy(dict(action.payload["plan"]))
        if current_stage == "03" and action.payload and isinstance(action.payload.get("execution_summary"), Mapping):
            updated["execution_summary"] = copy.deepcopy(dict(action.payload["execution_summary"]))
        if current_stage == "04" and action.payload and isinstance(action.payload.get("verification"), Mapping):
            updated["verification"] = copy.deepcopy(dict(action.payload["verification"]))
        if current_stage == "05" and action.payload and isinstance(action.payload.get("decision"), Mapping):
            updated["decision"] = copy.deepcopy(dict(action.payload["decision"]))
        if current_stage == "06" and action.payload and isinstance(action.payload.get("handoff"), Mapping):
            updated["handoff"] = copy.deepcopy(dict(action.payload["handoff"]))
        if current_stage == "exploration" and action.payload and isinstance(action.payload.get("exploration"), Mapping):
            exploration_payload = copy.deepcopy(dict(action.payload["exploration"]))
            queue = updated.setdefault("queue", {})
            candidates = queue.setdefault("candidates", [])
            for candidate in exploration_payload.get("candidate_tasks", []):
                if not isinstance(candidate, Mapping):
                    continue
                candidate_record = {
                    **dict(candidate),
                    "status": "candidate",
                    "stage_id": "exploration",
                }
                candidate_key = str(candidate_record.get("id") or candidate_record.get("title") or "")
                if not any(
                    str(existing.get("id") or existing.get("title") or "") == candidate_key
                    for existing in candidates
                    if isinstance(existing, Mapping)
                ):
                    candidates.append(candidate_record)
            selection = exploration_payload.get("selected_task")
            if isinstance(selection, Mapping):
                updated = start_task_from_exploration(
                    updated,
                    selection,
                    exploration=exploration_payload,
                    graph=graph,
                )
            else:
                # ``enforce_contracts=False`` is used by historical event
                # replay.  New live actions are rejected by protocol.py.
                node = graph.get(str(next_stage))
                updated["status"] = "running"
                updated["stage"] = {"id": node.id, "revision": "r1", **node.to_dict()}
        elif next_stage == "completed":
            updated["status"] = "completed"
        else:
            node = graph.get(str(next_stage))
            updated["status"] = "exploration" if next_stage == "exploration" else "running"
            updated["stage"] = {"id": node.id, "revision": "r1", **node.to_dict()}
    elif action.action == "rollback":
        node = graph.get(str(action.rollback_to))
        updated["status"] = "running"
        updated["stage"] = {
            "id": node.id,
            "revision": action.revision,
            **node.to_dict(),
        }
    elif action.action == "clarify":
        # ``clarify`` is a controlled write-back after a stage-01 auditor has
        # rejected an empty/incomplete task_spec.  It deliberately does not
        # advance to stage 02.  The new revision receives a fresh auditor
        # card, so the same independent gate must approve the repaired
        # decomposition before an ``advance`` can be accepted.
        payload = action.payload or {}
        task_spec = payload.get("task_spec") if isinstance(payload, Mapping) else None
        # ``action.revision`` may be either the current revision or the
        # one-step revision a model wrote on the repaired package.  The
        # persisted state is authoritative: always increment from the
        # revision currently stored on the stage.
        current_revision = str(updated.get("stage", {}).get("revision", action.revision))
        next_revision = _next_revision(current_revision)
        if isinstance(task_spec, Mapping):
            updated["task_spec"] = copy.deepcopy(dict(task_spec))
            updated["task_spec"]["status"] = "structured_pending_audit"
        else:
            # Lightweight clarify: no inline spec.  The new revision is refilled
            # by re-dispatched builder subagents (each <=3 fields).  Reset the
            # in-state spec so the gate re-evaluates the rebuilt package from
            # scratch; preserve the authoritative task inputs.
            prior_inputs = (
                updated.get("task_spec", {}).get("authoritative_inputs")
                if isinstance(updated.get("task_spec"), Mapping)
                else None
            )
            updated["task_spec"] = {
                "status": "unclarified",
                "authoritative_inputs": prior_inputs if isinstance(prior_inputs, list) else [],
            }
        repair = payload.get("repair") if isinstance(payload, Mapping) else None
        history = updated.setdefault("clarification_history", [])
        if not isinstance(history, list):
            history = []
            updated["clarification_history"] = history
        history.append(
            {
                "from_stage": f"{current_stage}-{current_revision}",
                "to_stage": f"{current_stage}-{next_revision}",
                "audit": copy.deepcopy(dict(repair)) if isinstance(repair, Mapping) else {},
                "message": action.message,
            }
        )
        node = graph.get(current_stage)
        updated["status"] = "running"
        updated["stage"] = {
            "id": node.id,
            "revision": next_revision,
            **node.to_dict(),
        }
    elif action.action == "blocked_human":
        updated["status"] = "blocked_human"
        updated.setdefault("queue", {}).setdefault("blocked_human", []).append(
            {"stage_id": current_stage, "revision": action.revision, "message": action.message}
        )
    elif action.action == "skip_blocked":
        node = graph.get(str(next_stage))
        updated["status"] = "exploration" if next_stage == "exploration" else "running"
        updated["stage"] = {"id": node.id, "revision": "r1", **node.to_dict()}
    elif action.action == "explore":
        updated["status"] = "exploration"
        updated["stage"] = {"id": "exploration", "revision": action.revision, **graph.get("exploration").to_dict()}
    elif action.action == "candidate":
        candidate_payload = dict(action.payload or {})
        updated.setdefault("queue", {}).setdefault("candidates", []).append(
            {**candidate_payload, "status": "candidate", "stage_id": current_stage}
        )
        if current_stage == "exploration":
            updated["last_exploration"] = {
                "preference_brief": candidate_payload.get("preference_brief", ""),
                "scanned_sources": list(candidate_payload.get("scanned_sources", [])),
                "selection_mode": "candidate",
                "candidate_tasks": [candidate_payload],
            }
    elif action.action == "repair_prompt":
        updated["status"] = "needs_repair"
    elif action.action in {"dispatch", "join"}:
        task_id = action.task_id or f"stage-{current_stage}"
        updated.setdefault("active_tasks", {})[task_id] = {
            "status": "dispatched" if action.action == "dispatch" else "joined",
            "message": action.message,
            "artifact_refs": list(action.artifact_refs),
        }

    updated["last_action"] = action.action
    updated["last_result"] = action.to_dict()
    updated.setdefault("history", []).append(
        {"action": action.action, "stage_id": current_stage, "revision": action.revision, "internal_state": internal}
    )
    return ensure_stage_cards(updated)
