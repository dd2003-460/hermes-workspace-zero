"""Stable Prompt rendering for the action-reproduction MVP."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any, Mapping

# soul 默认画像所在文件（用户数字分身的通用默认偏好）。通用问题缺偏好时
# 一律采用此处，而非某项目特例。可用环境变量 RALPH_SOUL_PATH 覆盖。
SOUL_PATH = Path(os.environ.get("RALPH_SOUL_PATH", "/Users/a1-6/Desktop/workspace/AGENTS.md"))
_SOUL_SECTION = "## 默认决策画像"


def _read_soul_defaults() -> str:
    """提取 soul（AGENTS.md）的「默认决策画像」区块，作为通用默认偏好注入提示。

    返回空串表示未找到（调用方退化为不注入）。
    """
    try:
        text = SOUL_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    idx = text.find(_SOUL_SECTION)
    if idx < 0:
        return ""
    rest = text[idx + len(_SOUL_SECTION):]
    # 截到下一个二级标题为止
    end = rest.find("\n## ")
    block = rest[:end] if end >= 0 else rest
    return block.strip()


def _soul_defaults_bullets() -> list[str]:
    """把 soul 默认画像渲染成 recovery 提示里的缩进行列表。"""
    block = _read_soul_defaults()
    if not block:
        return []
    out: list[str] = ["   soul 默认决策画像（通用默认，缺偏好时直接套用）："]
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        out.append(f"   {line}")
    return out


from .contracts import (
    agent_prompt_for_card,
    cards_for_current_stage,
    stage_contract_ref,
    stage_contract_text,
    stage_input_package_ref,
    stage_submission_template,
    stage_submission_template_ref,
)
from .feedback import protocol_feedback
from .nodes import DEFAULT_GRAPH

DEFAULT_TEMPLATE_PATH = Path(__file__).with_name("templates") / "stage_prompt.md"

# 阶段方法论放在独立的 prompt 文件里（loop/1-loop/<阶段>-*.md）。改这些文件即可改
# 阶段行为，无需动运行时代码。每轮提醒与初始 prompt 都直接读取并注入，方便维护。
_LOOP_1_DIR = Path(__file__).resolve().parents[2] / "1-loop"
STAGE_PROMPT_FILES = {
    "00": "00-综述.md",
    "01": "01-目标与背景分解.md",
    "02": "02-未知信息调研.md",
    "02.5": "02.5-交叉验证.md",
    "03": "03-执行任务分解.md",
    "04": "04-验证与交叉验证.md",
    "04.5": "04.5-交叉验证.md",
    "exploration": "exploration.md",
}


def _read_stage_prompt_file(stage_id: str, limit: int = 4000) -> str:
    """读取阶段方法论 prompt 文件内容（截断到 limit，避免撑爆小模型上下文）。"""

    fname = STAGE_PROMPT_FILES.get(str(stage_id))
    if not fname:
        return ""
    path = _LOOP_1_DIR / fname
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[: limit - 80] + "\n[… 阶段 prompt 文件已截断，完整内容在 " + str(path) + " …]"


def resolve_template_path() -> Path:
    """Select the active stage prompt template.

    Defaults to the original card-centric template so existing behaviour and
    tests stay intact. Set ``RALPH_PROMPT_TEMPLATE`` (absolute path or a file
    name inside the templates directory) to opt into an alternative, e.g. the
    field-centric lightweight template used by the D1-ralph-field-centric
    redesign (``stage_prompt_fieldcentric.md``).
    """
    override = os.environ.get("RALPH_PROMPT_TEMPLATE")
    if not override:
        return DEFAULT_TEMPLATE_PATH
    candidate = Path(override)
    if not candidate.is_absolute():
        candidate = Path(__file__).with_name("templates") / override
    return candidate


@dataclass(frozen=True)
class RenderedPrompt:
    text: str
    sha256: str


def _failing_gate_checks(state: Mapping[str, Any], root: str | Path | None) -> list[dict[str, Any]]:
    """Return the not-passing checks from the current stage's rollback gate review.

    Used to make a clarify prompt targeted: the Commander only has to fix the
    fields the independent auditor actually failed, not re-derive the whole
    task_spec.  Returns [] when no rollback gate review is available.
    """

    base = Path(root) if root else Path.cwd()
    gate_card = None
    for card in (state.get("subagent_cards", {}) or {}).values():
        if (
            isinstance(card, Mapping)
            and card.get("is_stage_gate")
            and card.get("gate_verdict") == "rollback"
            and card.get("status") == "completed"
        ):
            gate_card = card
            break
    if gate_card is None:
        return []
    ref = gate_card.get("gate_review_ref")
    if not ref:
        return []
    path = base / ref if not Path(ref).is_absolute() else Path(ref)
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    checks = review.get("checks", [])
    if not isinstance(checks, list):
        return []
    return [chk for chk in checks if isinstance(chk, Mapping) and str(chk.get("status")) != "pass"]


class PromptRenderer:
    def __init__(self, template_path: str | Path | None = None):
        self.template_path = Path(template_path) if template_path else resolve_template_path()

    @staticmethod
    def _bounded_json(value: Any, limit: int) -> str:
        """Serialize state for in-prompt display without blowing the model window.

        The full, authoritative copy always lives in ``loop-state.json`` on disk
        (and validation reads that file, not this text).  Inlining a multi-MB
        plan/queue/exploration dump into every fresh context is what overflows
        small local-model windows, so the display copy is capped and pointed at
        the file.  This is display-only; it never changes protocol behavior.
        """

        text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
        if len(text) <= limit:
            return text
        keep = max(0, limit - 120)
        return (
            text[:keep]
            + f"\n[… 已截断，原共 {len(text)} 字符；完整内容以 loop-state.json / "
            f"loop-artifacts/ 下对应文件为准，请用 Read 工具读取，不要凭此片段推断。 …]"
        )

    def render(self, state: Mapping[str, Any]) -> RenderedPrompt:
        stage = state.get("stage", {})
        cards = cards_for_current_stage(state)
        task_cards_text = "\n".join(
            "- `{id}`（{status}）：必须使用 Agent 工具派发；其 `prompt` 第一行必须是：\n"
            "  ```text\n{prompt}\n  ```".format(
                id=card["id"],
                status=(
                    f"{card.get('status', 'pending')}; gate_verdict={card.get('gate_verdict')}"
                    if card.get("gate_verdict")
                    else card.get("status", "pending")
                ),
                prompt=agent_prompt_for_card(card),
            )
            for card in cards
        ) or "- 当前阶段没有待派发的子代理任务卡。"
        context = {
            "task_json": self._bounded_json(state.get("task", {}), 4000),
            "stage_id": str(stage.get("id", "")),
            "revision": str(stage.get("revision", "r1")),
            "stage_name": str(stage.get("name", "")),
            "next_stage": str(stage.get("on_success") or ""),
            "stage_contract_ref": stage_contract_ref(
                str(stage.get("id", "")), str(stage.get("revision", "r1"))
            ),
            "submission_template_ref": stage_submission_template_ref(
                str(stage.get("id", "")), str(stage.get("revision", "r1"))
            ),
            "stage_input_package_ref": stage_input_package_ref(
                str(stage.get("id", "")), str(stage.get("revision", "r1"))
            ),
            "task_cards_text": task_cards_text,
            "stage_prompt_doc": _read_stage_prompt_file(str(stage.get("id", ""))),
            "blocked_human_template_json": json.dumps(
                self._blocked_human_template(state), ensure_ascii=False, sort_keys=True, indent=2
            ),
        }
        template = Template(self.template_path.read_text(encoding="utf-8"))
        text = template.safe_substitute(context).replace("\r\n", "\n").rstrip() + "\n"
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return RenderedPrompt(text=text, sha256=digest)

    @staticmethod
    def _blocked_human_template(state: Mapping[str, Any]) -> dict[str, Any]:
        """Give small local models a complete valid non-advance result shape."""

        stage = state.get("stage", {})
        stage_id = str(stage.get("id", ""))
        payload: dict[str, Any] = {}
        if stage_id == "01":
            payload = {
                "questions": [
                    {
                        "question": "填写一个会改变后续任务图或结论的关键问题。",
                        "why_it_matters": "说明缺失答案会如何影响范围、数据、评价或风险。",
                        "recommended_option": "给出明确的默认选项或场景分支。",
                    }
                ]
            }
        return {
            "action": "blocked_human",
            "status": "blocked_human",
            "stage_id": stage_id,
            "revision": str(stage.get("revision", "r1")),
            "next_stage": None,
            "rollback_to": stage_id,
            "evidence": [],
            "artifact_refs": [],
            "message": "说明阻塞原因，以及系统仍可继续处理的非阻塞事项。",
            "payload": payload,
        }

    @staticmethod
    def _clarify_template(state: Mapping[str, Any]) -> dict[str, Any]:
        """Return the explicit stage-01 repair action skeleton."""

        stage = state.get("stage", {})
        stage_id = str(stage.get("id", "01"))
        revision = str(stage.get("revision", "r1"))
        gate = next(
            (
                card for card in (state.get("subagent_cards", {}) or {}).values()
                if isinstance(card, Mapping)
                and str(card.get("stage_id")) == stage_id
                and str(card.get("revision")) == revision
                and card.get("is_stage_gate")
            ),
            {},
        )
        return {
            "action": "clarify",
            "status": "structured_pending_audit",
            "stage_id": stage_id,
            "revision": revision,
            "next_stage": None,
            "rollback_to": None,
            "evidence": [],
            "artifact_refs": [],
            "message": "根据独立审计回滚原因完成语义分解；运行时会递增 revision 并重新派发门禁。",
            "payload": {
                "task_spec": {
                    "semantic_map": {
                        "background": [],
                        "decision_object": [],
                        "objective": [],
                        "comparison_set": [],
                        "constraints": [],
                        "deliverable": [],
                        "uncertainty": [],
                    },
                    "attribute_matrix": [],
                    "constraints": [],
                    "assumptions": [],
                    "open_questions": [],
                    "scenarios": [],
                    "success_criteria": [],
                    "requirements_audit": {
                        "card_id": str(gate.get("id", "")),
                        "artifact_ref": "",
                        "summary": "",
                    },
                },
                "repair": {
                    "auditor_card_id": str(gate.get("id", "")),
                    "auditor_verdict": "rollback",
                    "audit_artifact_ref": "",
                    "reason": "",
                },
            },
        }

    @staticmethod
    def _candidate_action(raw_output: str | None) -> str | None:
        """Recover an intended action without accepting the malformed result."""

        if not raw_output:
            return None
        match = re.search(r'["\']action["\']\s*:\s*["\']([A-Za-z_]+)["\']', raw_output)
        if not match:
            return None
        action = match.group(1)
        return action if action in {
            "advance", "rollback", "blocked_human", "skip_blocked", "candidate",
            "explore", "dispatch", "join", "clarify", "repair_prompt",
        } else None

    @staticmethod
    def _repair_template(state: Mapping[str, Any], action: str | None) -> dict[str, Any]:
        """Choose a repair skeleton that matches the action already attempted."""

        if action == "advance":
            return stage_submission_template(state)
        if action == "blocked_human":
            return PromptRenderer._blocked_human_template(state)
        if action == "clarify":
            return PromptRenderer._clarify_template(state)
        stage = state.get("stage", {})
        stage_id = str(stage.get("id", ""))
        template: dict[str, Any] = {
            "action": action or "advance",
            "status": "填写实际结果状态",
            "stage_id": stage_id,
            "revision": str(stage.get("revision", "r1")),
            "next_stage": None,
            "rollback_to": stage_id if action == "rollback" else None,
            "evidence": [],
            "artifact_refs": [],
            "message": "填写本次动作的事实依据。",
        }
        if action == "skip_blocked":
            template["next_stage"] = stage.get("on_human_block") or stage.get("on_success")
        return template

    @staticmethod
    def _semantic_action_conflict(error: str) -> bool:
        """Distinguish an illegal transition from a merely malformed field."""

        lowered = str(error or "").lower()
        markers = (
            "blocking_findings",
            "rollback or blocked_human",
            "requires state.status",
            "required subagent cards",
            "still has unfinished",
            "does not match current stage",
            "reviewer card is not completed",
            "can advance only",
            "must enter exploration",
            "cannot be executed",
            "not allowed for",
        )
        return any(marker in lowered for marker in markers)

    def repair_prompt(
        self,
        state: Mapping[str, Any],
        error: str,
        raw_output: str | None = None,
    ) -> RenderedPrompt:
        action = self._candidate_action(raw_output)
        semantic_conflict = self._semantic_action_conflict(error)
        cards = [
            card for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping)
        ]
        pending = next((card for card in cards if card.get("status") == "pending"), None)
        dispatched = next((card for card in cards if card.get("status") == "dispatched"), None)
        if pending:
            feedback = protocol_feedback(
                error=error,
                action=action,
                correction=(
                    f"任务卡 `{pending.get('id', '<card>')}` 仍是 pending；协议错误不能替代任务派发，"
                    "不要输出阶段结果。"
                ),
                next_action=(
                    f"立即使用 Agent 派发 `{pending.get('id', '<card>')}`，第一行必须是 "
                    f"`RALPH_TASK_CARD={pending.get('card_ref', '<card-ref>')}`。"
                ),
                expected=(
                    "派发成功后由 Hook 写入 dispatched；不要在本次回复中伪造状态。"
                ),
            )
        elif dispatched:
            feedback = protocol_feedback(
                error=error,
                action=action,
                correction=(
                    f"任务卡 `{dispatched.get('id', '<card>')}` 已 dispatched；当前不能用协议错误触发新动作。"
                ),
                next_action="停止工具调用，等待 SubagentStop 回执。",
                expected=(
                    "不要重派、不要标记 blocked_human、不要循环读取事件日志。"
                ),
            )
        else:
            feedback = protocol_feedback(
                error=error,
                action=action,
                preserve_action=not semantic_conflict,
                correction=(
                    "当前 action 与状态机/门禁条件冲突；不要伪造 advance，按错误信息选择 rollback、"
                    "blocked_human 或其他允许分支。"
                    if semantic_conflict
                    else None
                ),
                expected=(
                    f"当前阶段 `{state.get('stage', {}).get('id', '')}` 使用下面唯一模板；"
                    "如果真实结果是人类阻塞，才改用 blocked_human 模板。"
                ),
            )
        return self.compact_recovery_prompt(
            state,
            reason=error,
            error_kind="protocol",
            action_hint=feedback,
            protocol_template=None if semantic_conflict else self._repair_template(state, action),
        )

    @staticmethod
    def _short_text(value: Any, limit: int) -> str:
        """Keep recovery prompts bounded even when task text is very large."""

        text = str(value or "").replace("\x00", " ").strip()
        if len(text) <= limit:
            return text
        head = max(1, limit - 80)
        return text[:head] + "\n[… 已截断，完整内容在 loop-state.json …]"

    def _field_recovery_prompt(
        self,
        state: Mapping[str, Any],
        *,
        reason: str = "",
        error_kind: str = "continuation",
    ) -> RenderedPrompt:
        """Field-centric continuation prompt: fill the field table, not cards."""

        stage = state.get("stage", {}) if isinstance(state.get("stage"), Mapping) else {}
        task = state.get("task", {}) if isinstance(state.get("task"), Mapping) else {}
        stage_id = str(stage.get("id", ""))
        revision = str(stage.get("revision", "r1"))
        stage_name = str(stage.get("name", ""))
        task_description = self._short_text(task.get("description", ""), 700)
        stage_success = self._short_text(stage.get("success_condition", ""), 200)
        stage_outputs = (
            "、".join(str(o) for o in (stage.get("required_outputs") or []) if str(o).strip())
            or "（见阶段契约）"
        )
        contract_ref = f"loop-artifacts/contracts/{stage_id}-{revision}-stage-contract.md"
        submission_ref = f"loop-artifacts/contracts/{stage_id}-{revision}-submission-template.json"
        stage_doc = _read_stage_prompt_file(stage_id)
        # report only the still-missing fields
        missing = []
        spec = state.get("task_spec") if isinstance(state.get("task_spec"), Mapping) else {}
        matrix = spec.get("attribute_matrix") if isinstance(spec, Mapping) else None
        existing = set()
        if isinstance(matrix, list):
            for index, leaf in enumerate(matrix):
                if not isinstance(leaf, Mapping):
                    continue
                existing.add(str(leaf.get("concept") or "").strip())
                existing.add(str(leaf.get("role") or "").strip())
                disp = leaf.get("disposition")
                if disp in (None, "", "pending"):
                    missing.append(str(leaf.get("concept") or leaf.get("attribute") or f"#{index}"))
        # 阶段 required_outputs 也是交付字段：整条没出现在字段表里就必须提醒补
        for o in (stage.get("required_outputs") or []):
            o = str(o).strip()
            if o and o not in existing:
                missing.append(o)
        missing_line = "；".join(missing) if missing else "（当前无 pending 字段，可直接 advance）"
        # 上一阶段（on_success 指向本阶段的节点）即本阶段的输入来源
        prev_stage = ""
        for nid in DEFAULT_GRAPH.ids():
            node = DEFAULT_GRAPH.get(nid)
            if getattr(node, "on_success", None) == stage_id:
                prev_stage = nid
                break
        artifact_md = f"loop-artifacts/{stage_id}-{revision}.md"
        artifact_json = f"loop-artifacts/{stage_id}-{revision}.json"
        next_stage = str(stage.get("on_success") or "")
        advance_file = f"loop-artifacts/{stage_id}-{revision}.advance.json"
        advance_json = json.dumps(
            {
                "action": "advance",
                "status": "completed",
                "stage_id": stage_id,
                "revision": revision,
                "next_stage": next_stage or "（见节点图）",
                "message": f"完成 {stage_name}，推进到 {next_stage}",
            },
            ensure_ascii=False,
            indent=2,
        )
        text = (
            f"# RALPH 字段中心 · 阶段提醒（{stage_id}-{revision} · {stage_name}）\n"
            f"当前任务：{task_description or '以 loop-state.json 为准'}\n\n"
            "## 1. 本阶段方法论（来自阶段 prompt 文件；**直接改该文件即可调整本阶段行为**，无需动运行时代码）\n"
            f"{stage_doc}\n\n"
            f"## 2. 本阶段目标（运行时校验）：{stage_success or '以阶段契约为准'}；应交付：{stage_outputs}\n"
            f"## 3. 仍需填写的字段（只补这些，不必一次交齐）：{missing_line}\n"
            "## 4. 阶段文件（每阶段只产出一对，命名 `0x-rx`，链式传递）\n"
            f"- **本阶段交付物**：写 `{artifact_md}`（分析/笔记）与 `{artifact_json}`（结构化结果，含本阶段字段）。\n"
            + (
                f"- **本阶段输入**：先读上一阶段交付物 `loop-artifacts/{prev_stage}-{revision}.md` 与 `.json`，再动手（上一阶段输出即本阶段输入）。\n"
                if prev_stage
                else "- **本阶段输入**：从 `loop-state.json` 的任务与已知背景开始（首阶段无前置阶段文件）。\n"
            )
            + "- **提交字段**：把要新增/更新的字段写进本阶段 `.json`（列表，或 `{\"fields\": [...]}`），每条含 "
            "`concept / role / attribute / disposition / rationale / evidence_refs / confidence / impact / reversible`；"
            f"运行 **`ralph field-apply <项目> {artifact_json}`** 校验并原子落盘"
            "（按 `concept` 合并：同 concept 覆盖、新 concept 追加；`{\"concept\": \"...\", \"delete\": true}` 删除）。\n"
            f"- **推进到下一阶段（关键）**：本阶段字段齐全（无 pending、无未带证据的 research_required）后**必须显式推进**"
            f"——**只有阶段 01 会自动推进，02+ 不会**，且聊天里输出 `<RALPH_STAGE_RESULT> advance` 无效（运行时不会解析聊天 token）。"
            f"正确做法：写一份 action 文件 `{advance_file}`：\n"
            "  ```json\n"
            f"{advance_json}\n"
            "  ```\n"
            f"  然后运行 **`ralph apply . {advance_file}`**（或 `ralph validate --result {advance_file} --apply`）即完成推进；"
            "运行时自动校验、原子落盘。\n"
            "- **禁止直接 Write/Edit `loop-state.json`**（易损坏导致循环崩溃）；`loop-state.json` 仅供运行时读取。\n"
            "- 项目路径可用绝对路径 `/Users/a1-6/Desktop/workspace/projects/D1-gpu-inference-hardware`，或当前目录用 `.`。\n"
            "- 状态损坏/需回退：`ralph recover-state <项目>`（或 `--stage <id>` 重置到上一阶段）。\n"
            f"- {'阶段 01 字段完整后运行时自动推进，无需额外命令；' if stage_id == '01' else f'阶段 {stage_id} 字段齐全后必须运行 `ralph apply . {advance_file}` 显式推进，不能只靠聊天输出 advance。'}\n"
        )
        if reason:
            text += f"\n上一轮提示（供参考，不要原样扩写）：{self._short_text(reason, 600)}\n"
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return RenderedPrompt(text=text, sha256=digest)

    def compact_recovery_prompt(
        self,
        state: Mapping[str, Any],
        *,
        reason: str = "",
        error_kind: str = "continuation",
        action_hint: str | None = None,
        fresh_session: bool = False,
        protocol_template: Mapping[str, Any] | None = None,
        root: str | Path | None = None,
    ) -> RenderedPrompt:
        """Render a bounded continuation prompt for Stop Hook and resume.

        The normal stage prompt is intentionally complete and can contain the
        plan, task cards, contracts and queue. It is appropriate for a fresh
        stage, but unsafe to append to an already large Claude transcript.
        Recovery must point at the persisted files instead of copying them
        into the next model request.
        """

        # Field-centric recovery: when the active template is the field-centric one,
        # render a field-table continuation (for every stage) instead of the
        # card-ordering prompt.  Every stage's deliverable is the field surface, so
        # the same "fill the field table" instruction applies across 01-06.  The
        # field gate (RALPH_FIELD_GATE) short-cuts the heavy per-stage contract
        # validation for all stages, so this field-table recovery is valid
        # end-to-end.
        if os.environ.get("RALPH_PROMPT_TEMPLATE", "").endswith("stage_prompt_fieldcentric.md"):
            return self._field_recovery_prompt(state, reason=reason, error_kind=error_kind)

        stage = state.get("stage", {})
        stage = stage if isinstance(stage, Mapping) else {}
        task = state.get("task", {})
        task = task if isinstance(task, Mapping) else {}
        stage_id = self._short_text(stage.get("id", ""), 32)
        revision = self._short_text(stage.get("revision", "r1"), 32)
        stage_name = self._short_text(stage.get("name", ""), 160)
        task_description = self._short_text(task.get("description", ""), 700)
        reason_text = self._short_text(reason, 1200)
        contract_ref = f"loop-artifacts/contracts/{stage_id}-{revision}-stage-contract.md"
        submission_ref = f"loop-artifacts/contracts/{stage_id}-{revision}-submission-template.json"
        pending_cards = [
            card
            for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping) and card.get("status") == "pending"
        ]
        pending_builders = [
            card
            for card in pending_cards
            if isinstance(card, Mapping) and not card.get("is_stage_gate")
        ]
        dispatched_cards = [
            card
            for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping) and card.get("status") == "dispatched"
        ]
        task_spec = state.get("task_spec", {})
        task_spec_status = task_spec.get("status") if isinstance(task_spec, Mapping) else None
        clarify_required = (
            stage_id == "01"
            and task_spec_status in {"unclarified", "structured_pending_audit"}
            and any(
                isinstance(card, Mapping)
                and card.get("is_stage_gate")
                and str(card.get("stage_id")) == stage_id
                and str(card.get("revision")) == revision
                and card.get("status") == "completed"
                and card.get("gate_verdict") == "rollback"
                for card in (state.get("subagent_cards", {}) or {}).values()
            )
        )
        # stage 01 所有必需卡（builder + 审计 gate）都已完成，且 task_spec 已组装 ->
        # 直接派发 advance 即可，无需再读文档或内联巨大 task_spec（运行时已用组装好的）。
        required_cards = [
            card
            for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping)
            and str(card.get("stage_id")) == stage_id
            and str(card.get("revision")) == revision
            and bool(card.get("required_for_advance"))
        ]
        all_required_done = bool(required_cards) and all(
            c.get("status") == "completed" for c in required_cards
        )
        gate_card = next(
            (
                card
                for card in (state.get("subagent_cards", {}) or {}).values()
                if isinstance(card, Mapping)
                and card.get("is_stage_gate")
                and str(card.get("stage_id")) == stage_id
                and str(card.get("revision")) == revision
                and card.get("status") == "completed"
            ),
            None,
        )
        advance_ready = stage_id == "01" and all_required_done and gate_card is not None

        if fresh_session:
            instruction = (
                "这是一个新的 Commander 上下文；从持久化状态继续当前阶段，不复述历史，不读取完整 loop-events.md。"
                "若下面列出 pending 卡，下一次工具调用必须直接使用 Agent 派发该卡（builder 构造卡先于 gate 审计卡）；"
                "不要先用 Bash、Write、Edit 或继续读取文件。dispatched 卡不要重派，等待子代理回执。"
                "Commander 只负责派发子代理，绝不在自身上下文里 Write/Edit 文件或输出大段结构化内容；"
                "每个子代理只填写其任务卡规定的 ≤3 个语义字段，超过 3 个字段的填写必须拆成多个子代理派发。"
                "所有 builder 与 gate 都完成后，运行 `ralph assemble` 合成结果，再 `ralph validate --result <路径>` 复核，"
                "最后 `ralph validate --result <路径> --apply` 提交（或输出对应的 <RALPH_STAGE_RESULT>）。不要把运行时中断当作阶段失败。"
            )
        elif error_kind in {"memory_guard", "connection", "timeout", "api_error", "runtime"}:
            instruction = (
                "这是运行时中断，不代表阶段失败；不要重做任务、复述历史或再次派发同一批子代理。"
                "当前会话应结束，下一次用 `ralph resume <项目路径>` 从持久化状态建立短上下文。"
            )
        elif error_kind == "protocol":
            instruction = action_hint or (
                "只修复结构化动作的字段，不修改 loop-state.json，不新增调研；然后返回一个完整的 RALPH_STAGE_RESULT。"
            )
        else:
            instruction = action_hint or (
                "读取持久化状态后只继续当前阶段，不复述完整计划；完成后只返回一个完整的 RALPH_STAGE_RESULT。"
            )

        first_recovery_rule = (
            "1. 运行时已从持久化状态确认当前阶段和 pending 任务卡；不要读取 loop-state.json 或任何文件，"
            "下一次工具调用直接使用上面指定的 Agent。"
        )
        lines = [
            "# RALPH 短恢复指令",
            "",
            f"当前阶段：{stage_id}-{revision}（{stage_name}）",
            f"项目状态：{self._short_text(state.get('status', 'running'), 40)}",
            f"当前任务：{task_description or '以 loop-state.json 为准'}",
            "",
            "权威输入（不要把完整内容复制进上下文）：",
            "- `loop-state.json`：当前唯一状态和阶段完整条件",
            f"- `{contract_ref}`：当前阶段契约",
            f"- `{submission_ref}`：唯一提交模板",
            "",
            "恢复规则：",
            first_recovery_rule,
            f"2. 只按 `{contract_ref}` 和 `{submission_ref}` 工作。",
            "3. **Commander 禁止用 Read/Grep/Glob 读取任何长文档，也禁止读取 loop-artifacts 下的契约/模板/切片/输入包/任务卡**"
            "（那些由子代理读取）。你的上下文窗口只有 60000 token，一次读取 stage-input-package 就会撑爆它。"
            "所有文档阅读都交给派发的子代理，你只负责派发与汇总。",
            f"4. {instruction}",
            "",
            "5. **通用默认偏好来自 soul（用户画像），不是本项目特例**：任何因素/约束不明确时，一律按 soul 的「默认决策画像」假设并标注 disposition=assume/inferred，**禁止向人类提问**。",
            *_soul_defaults_bullets(),
            "   **绝不允许 AskUserQuestion 或任何向人类/用户提问的动作**。若某偏好确实需要人类拍板，把它写入 `loop-artifacts/open-questions.md`（人类可异步补充），",
            "   然后按 soul 默认偏好继续全面调研、派发 builder 子代理把相关字段填全。多调研、多给出有依据的备选，远比停在提问上强。",
        ]
        if pending_cards:
            if pending_builders:
                builder_refs = ", ".join(
                    str(c.get("id", "")) for c in pending_builders
                )
                lines.extend(
                    [
                        "",
                        "## 第一动作闸门（机械排序，不可违反）",
                        f"还有未派发的构建子卡：{builder_refs}。",
                        "**下一次工具调用必须只派发上述 builder 卡**；"
                        "在全部 builder 变为 completed 之前，**严禁**派发任何 gate / 审计卡"
                        "（gate 必须等 builder 把字段填好才能审计，提前派发会导致死锁且字段永远为空）。",
                        "已 dispatched 的卡不要重派，等待 SubagentStop 回执；"
                        "builder 全部完成后再派发 gate。",
                    ]
                )
            lines.extend(["", "当前 pending 任务卡（只可按此路径派发）："])
            for card in pending_cards:
                card_id = self._short_text(card.get("id", ""), 120)
                card_ref = self._short_text(card.get("card_ref", ""), 240)
                lines.append(
                    f"- `{card_id}`：Agent prompt 第一行必须是 `RALPH_TASK_CARD={card_ref}`"
                )
        if error_kind == "protocol":
            lines.append("")
            if pending_cards:
                lines.extend(
                    [
                        "协议修复优先级：当前有 pending 任务卡，不要输出阶段结果。",
                        "下一次工具调用必须直接使用上方指定的 Agent；不要调用 Bash、cat、echo 或 ralph apply，也不要调用 Write/Edit 或继续读取文件。",
                    ]
                )
            elif dispatched_cards:
                lines.extend(
                    [
                        "协议修复优先级：当前有 dispatched 任务卡，不要输出新阶段动作。",
                        "等待 SubagentStop 回执；不要重派、不要标记 blocked_human、不要循环读取事件日志。",
                    ]
                )
            else:
                if advance_ready:
                    gate_id = self._short_text(gate_card.get("id", ""), 160) if isinstance(gate_card, Mapping) else ""
                    lines.extend(
                        [
                            "阶段 01 的所有必需任务卡（builder + 审计 gate）均已完成，task_spec 已组装。**直接输出一次 advance 阶段结果即可**，不要派发任何卡、不要读取文档、不要内联 task_spec（运行时使用已组装好的）：",
                            "```json",
                            "<RALPH_STAGE_RESULT>",
                            "{",
                            '  "action": "advance",',
                            '  "status": "passed",',
                            '  "stage_id": "01",',
                            f'  "revision": "{revision}",',
                            '  "next_stage": "03",',
                            '  "payload": {',
                            '    "stage_review": {',
                            f'      "reviewer_card_id": "{gate_id}",',
                            '      "context_mode": "bounded_artifacts",',
                            '      "verdict": "pass",',
                            '      "recommended_action": "advance",',
                            '      "summary": "task_spec 已组装完整，7 语义角色与属性矩阵齐备",',
                            f'      "checked_input_refs": ["loop-artifacts/stages/01/{revision}/task_spec.json"],',
                            f'      "checked_output_refs": ["loop-artifacts/stages/01/{revision}/task_spec.json"],',
                            '      "checks": [{"criterion": "task_spec 结构化完整", "status": "pass", "note": "已通过 assemble", "evidence_refs": []}]',
                            "    }",
                            "  }",
                            "}",
                            "</RALPH_STAGE_RESULT>",
                            "```",
                            "（把上面两处 `revision` 替换成当前 revision；verdict 必须是 pass，不要写 blocking_findings。）",
                        ]
                    )
                elif protocol_template is None:
                    lines.extend(
                        [
                            "当前 action 与状态机条件冲突；不要复制旧 action 模板。",
                            "根据上面的允许分支选择 rollback、blocked_human 或其他合法动作，然后直接输出一次完整 RALPH_STAGE_RESULT。",
                            "不要调用 Bash、cat、echo、Write、Edit 或 ralph apply。",
                        ]
                    )
                else:
                    repair_example = json.dumps(
                        protocol_template,
                        ensure_ascii=False,
                        indent=2,
                    )
                    lines.extend(
                        [
                            "协议修复时直接在 Assistant 消息中输出下面的完整结构；不要调用 Bash、cat、echo 或 ralph apply：",
                            "<RALPH_STAGE_RESULT>",
                            repair_example,
                            "</RALPH_STAGE_RESULT>",
                        ]
                    )
        if clarify_required:
            lines.extend(
                [
                    "",
                    "阶段 01 审计 verdict=rollback。处理流程（拆分给子代理，绝不在自身上下文写大段内容）：",
                    "1. 先输出一个**轻量** <RALPH_STAGE_RESULT>，严格按下面模板（status 必须是 structured_pending_audit，不要写 rollback_repair 等别的词）：",
                    "```json",
                    "<RALPH_STAGE_RESULT>",
                    "{",
                    '  "action": "clarify",',
                    '  "status": "structured_pending_audit",',
                    '  "stage_id": "01",',
                    '  "revision": "<当前 stage 的 revision，如 r4>",',
                    '  "repair": {',
                    '    "auditor_card_id": "<当前 rollback gate 卡 id，如 01-r4-requirements-auditor>",',
                    '    "auditor_verdict": "rollback",',
                    '    "reason": "<简述 gate 回滚原因>"',
                    "  }",
                    "}",
                    "</RALPH_STAGE_RESULT>",
                    "```",
                    "**不要带 inline 的 task_spec，repair.audit_artifact_ref 可省略（运行时自动关联）。不要向人类提问**——偏好按上面第 5 条默认偏好假设并标注 disposition。运行时据此递增 revision 并生成 pending 的构建/审计任务卡。",
                    "2. 下一上下文会列出新的 pending `01-<rev>-builder-task_spec-*` 子代理；依次派发它们，每个子代理只填其任务卡规定的 ≤3 个语义角色"
                    "（context 组：background/decision_object/objective；options 组：comparison_set/constraints；output 组：deliverable/uncertainty），用 Edit 写入对应 partial 切片文件。**按默认偏好填写，不要停下来问人。**",
                    "3. 所有 builder 完成后运行 `ralph assemble` 合成 task_spec.json。",
                    "4. 派发 pending 的 `01-<rev>-requirements-auditor` 子代理重新审计。",
                    "5. `ralph validate` 复核；gate 通过则直接输出 <RALPH_STAGE_RESULT> action=advance，否则回到第 1 步换 revision 再填。",
                    "严禁在 Assistant 消息里写满 7 类语义角色或整份 task_spec；任何填写都拆给子代理，单个子代理上限 3 个字段。",
                ]
            )
            failing = _failing_gate_checks(state, root)
            if failing:
                lines.extend(
                    [
                        "",
                        "本轮门禁回执里未通过（status≠pass）的 check 如下；**只针对这些字段重新派发/补充对应的 builder 子代理去填写（每个子代理 ≤3 字段），不要在本会话里 inline 补充**：",
                    ]
                )
                for index, chk in enumerate(failing, start=1):
                    criterion = chk.get("criterion", "")
                    status = chk.get("status", "")
                    note = chk.get("note", "")
                    lines.append(f"{index}. [{status}] {criterion}" + (f" — {note}" if note else ""))
        if reason_text:
            lines.extend(["", "本次恢复原因（仅作诊断，不要原样扩写）：", reason_text])
        text = "\n".join(lines).rstrip() + "\n"
        return RenderedPrompt(
            text=text,
            sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
