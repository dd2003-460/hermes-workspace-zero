"""Pure stage/role/tool policy used by future Hook adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .feedback import tool_feedback
import os


def _field_gate_active(state: Mapping[str, Any]) -> bool:
    """True when the runtime is in field-centric mode for this project.

    Field mode is enabled by ``RALPH_FIELD_GATE``.  It is suppressed while the
    persisted ``subagent_cards`` still carry enforced builder/gate cards from a
    previous (enforce) run; in that case the cards stay authoritative until they
    are cleared, so a half-migrated project does not get two conflicting rule
    sets at once.
    """
    if not os.environ.get("RALPH_FIELD_GATE"):
        return False
    cards = state.get("subagent_cards")
    if isinstance(cards, Mapping) and cards:
        return False
    return True


@dataclass(frozen=True)
class ToolDecision:
    decision: str
    reason: str


@dataclass(frozen=True)
class StagePolicy:
    stage_id: str
    commander_tools: tuple[str, ...]
    worker_tools: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    read_only: bool = False


DEFAULT_STAGE_POLICIES = {
    # 01/02 intentionally allow only the bounded audit Agent.  hooks.py
    # checks the task-card marker, so this is not a blanket permission to
    # dispatch arbitrary research agents.
    # 01/02/04/05/06 worker_tools include Write/Edit so the approved builder
    # subagent can write its payload slice; the independent gate reviewers are
    # bounded_context and instructed never to write, and loop-state.json is
    # still protected by the dedicated target-path guard in decide_tool.
    "01": StagePolicy("01", ("Agent", "Read", "Glob", "Grep", "Bash", "Write", "Edit"), ("Read", "Glob", "Grep", "Write", "Edit"), ("advance", "rollback", "clarify", "blocked_human", "explore")),
    "02": StagePolicy("02", ("Agent", "Read", "Glob", "Grep", "Bash", "Write", "Edit"), ("Read", "Glob", "Grep", "Write", "Edit"), ("advance", "rollback", "blocked_human", "candidate", "explore")),
    # Cross-validation stages: the Commander dispatches per-field subagents that
    # consult various web LLMs + authoritative sources, and may also research
    # directly.  Web tools are required here.
    "02.5": StagePolicy("02.5", ("Agent", "Read", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "Write", "Edit"), ("Read", "Glob", "Grep", "WebSearch", "WebFetch", "Write", "Edit"), ("advance", "rollback", "blocked_human", "explore")),
    "04.5": StagePolicy("04.5", ("Agent", "Read", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "Write", "Edit"), ("Read", "Glob", "Grep", "WebSearch", "WebFetch", "Write", "Edit"), ("advance", "rollback", "blocked_human", "explore")),
    # Broad discovery belongs only to execution.  It remains evidence
    # acquisition, not a substitute for the later verification stage.
    "03": StagePolicy("03", ("Agent", "Read", "Glob", "Grep", "Bash", "Skill", "WebSearch", "WebFetch"), ("Read", "Glob", "Grep", "Bash", "Write", "Edit", "Skill", "WebSearch", "WebFetch"), ("advance", "rollback", "blocked_human", "dispatch", "join")),
    "04": StagePolicy("04", ("Agent", "Read", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "Write", "Edit"), ("Read", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "Write", "Edit"), ("advance", "rollback", "blocked_human", "explore")),
    "05": StagePolicy("05", ("Agent", "Read", "Glob", "Grep", "Bash", "Write", "Edit"), ("Read", "Glob", "Grep", "Write", "Edit"), ("advance", "rollback", "blocked_human", "explore")),
    "06": StagePolicy("06", ("Agent", "Read", "Glob", "Grep", "Bash", "Write", "Edit"), ("Read", "Glob", "Grep", "Write", "Edit"), ("advance", "rollback", "blocked_human", "explore")),
    "exploration": StagePolicy("exploration", ("Agent", "Read", "Glob", "Grep", "Bash"), ("Read", "Glob", "Grep"), ("advance", "candidate", "blocked_human", "explore"), read_only=True),
}


def decide_tool(
    state: Mapping[str, Any],
    role: str,
    tool_name: str,
    *,
    target_path: str | None = None,
    command: str | None = None,
) -> ToolDecision:
    stage_id = str(state.get("stage", {}).get("id", "01"))
    policy = DEFAULT_STAGE_POLICIES.get(stage_id)
    if policy is None:
        return ToolDecision(
            "deny",
            tool_feedback(
                "STAGE_POLICY_MISSING",
                detected=f"当前阶段 `{stage_id}` 没有可执行的工具策略。",
                correction="不要继续试探工具权限，也不要修改状态。",
                next_action="停止当前会话并报告运行时配置缺失。",
                forbidden="绕过 Hook、直接修改 loop-state.json 或自行创建阶段策略。",
            ),
        )
    if state.get("status") in {"completed", "stopped"}:
        return ToolDecision("deny", f"state is {state['status']}")
    if state.get("status") == "blocked_human":
        return ToolDecision(
            "deny",
            tool_feedback(
                "HUMAN_BLOCK_ACTIVE",
                detected="当前阶段已经由状态机标记为 blocked_human，等待人类回答。",
                correction="停止当前工具调用；人类输入会由 UserPromptSubmit 写回并重新打开阶段。",
                next_action="结束当前会话，等待人类回答后再用 `ralph resume <项目路径>`。",
                forbidden="继续 Read/Agent/AskUserQuestion、重派任务或自行执行探索。",
            ),
        )
    allowed = policy.commander_tools if role == "commander" else policy.worker_tools
    if role == "commander" and tool_name in {"Write", "Edit"}:
        # Commander is NEVER allowed to write loop-state.json directly.  A full
        # hand-rewrite of the file is what repeatedly produced invalid JSON and
        # killed the loop.  The only sanctioned write path is the runtime: the
        # Commander emits a small delta file and runs `ralph field-apply` (which
        # validates + merges atomically), or advances via the
        # <RALPH_STAGE_RESULT> action.  Other project files (open-questions.md,
        # etc.) stay writable.
        if target_path and target_path.endswith("loop-state.json"):
            return ToolDecision(
                "deny",
                tool_feedback(
                    "STATE_FILE_PROTECTED",
                    detected="工具目标是 loop-state.json。",
                    correction="禁止直接 Write/Edit loop-state.json。字段更新：把改动写成小增量 JSON，运行 "
                    "`ralph field-apply <项目> <字段文件>`（校验通过才原子落盘）。阶段推进用 "
                    "`<RALPH_STAGE_RESULT> advance` 或 `ralph apply`。",
                    next_action="不要改文件，改用字段校验命令。需要重置时运行 `ralph recover-state <项目>`。",
                    forbidden="Write/Edit/cat/echo 修改 loop-state.json。",
                ),
            )
        return ToolDecision("allow", "Commander may write non-state files directly")
    # Field-centric mode: the Commander drives a field table, not a deck of
    # enforced task cards.  The env guard is authoritative, but we also refuse to
    # force-dispatch any orphaned cards so a freshly-migrated project does not
    # deadlock on stale enforce artifacts.
    if role == "commander" and _field_gate_active(state):
        # loop-state.json stays write-protected even in field mode: the matrix is
        # committed atomically via the <RALPH_STAGE_RESULT> action, never via Edit.
        if tool_name in {"Write", "Edit"} and target_path and target_path.endswith("loop-state.json"):
            return ToolDecision(
                "deny",
                tool_feedback(
                    "STATE_FILE_PROTECTED_FIELD",
                    detected="工具目标是 loop-state.json。",
                    correction="字段只能由结构化动作经过 runtime 原子写入（输出 <RALPH_STAGE_RESULT> advance，payload.task_spec.attribute_matrix 即新字段表）。",
                    next_action="返回结构化动作，不要直接改文件。",
                    forbidden="Write/Edit/cat/echo 修改 loop-state.json。",
                ),
            )
        if tool_name == "AskUserQuestion":
            return ToolDecision(
                "deny",
                tool_feedback(
                    "ASK_USER_FIELD_GATE",
                    detected=f"{tool_name} 不属于字段中心模式的直接交互工具；框架禁止 Commander 向人类提问。",
                    correction="通用偏好一律采用 soul（AGENTS.md）「默认决策画像」（disposition=assume/assumed_default）；"
                    "未知事实派单字段调研 subagent 带回 evidence_refs；真正需要人类拍板的事项写入 loop-artifacts/open-questions.md。",
                    next_action="把该因素作为字段写入 task_spec.attribute_matrix，或派 Agent 只填这一个 research_required 字段。",
                    forbidden="用 AskUserQuestion 把可推断字段包装成选择题，或绕过阶段契约直接弹出问题。",
                ),
            )
        # Field-centric research: external facts (latest GPU, price quotes) are
        # filled by narrow single-field subagents, but the Commander may also use
        # web research directly when the field context is small.  Both are allowed.
        if tool_name in allowed or tool_name in {"WebSearch", "WebFetch"}:
            return ToolDecision("allow", "tool allowed in field-centric mode")
        return ToolDecision(
            "deny",
            tool_feedback(
                "TOOL_STAGE_SCOPE_FIELD",
                detected=f"{tool_name} 不允许由 {role} 在阶段 `{stage_id}`（字段中心模式）使用。",
                correction="遵守当前阶段的工具白名单；字段中心模式下 Commander 直接维护字段表，不强制卡片。",
                next_action="选择阶段允许的工具，或直接输出 <RALPH_STAGE_RESULT> advance。",
                forbidden="试探其他工具、把工具调用改写成 Bash，或修改状态文件。",
            ),
        )
    if tool_name not in allowed:
        if tool_name == "AskUserQuestion":
            pending_cards = [
                card
                for card in (state.get("subagent_cards", {}) or {}).values()
                if isinstance(card, Mapping) and card.get("status") == "pending"
            ]
            next_action = "直接派发当前 pending 任务卡"
            if pending_cards:
                next_action = (
                    f"直接使用 Agent 派发 `{pending_cards[0].get('id', '<card>')}`，"
                    f"并在第一行写 `RALPH_TASK_CARD={pending_cards[0].get('card_ref', '<card-ref>')}`。"
                )
            else:
                next_action = (
                    "**不要向人类提问**。把该偏好/因素写入 `loop-artifacts/open-questions.md`（人类可异步补充），"
                    "按 soul（AGENTS.md）「默认决策画像」通用默认假设并标注 disposition=assume，继续全面调研或派发 builder 子代理把字段填全，"
                    "随后直接输出完整 RALPH_STAGE_RESULT。"
                )
            return ToolDecision(
                "deny",
                tool_feedback(
                    "ASK_USER_GATE",
                    detected=f"{tool_name} 不属于阶段 `{stage_id}` 的直接交互工具，且本框架禁止 Commander 向人类提问（不能直接问人）。",
                    correction="先按需求分流闸门判断：通用偏好一律采用 soul（AGENTS.md）「默认决策画像」，技术栈/预算/集成/优先级等均可按该默认假设或交子代理调研，不可问人。"
                    "需要选偏好时去 soul 查，确实需要人类拍板的事项写入 `loop-artifacts/open-questions.md`，不要弹出问题。",
                    next_action=next_action,
                    forbidden="用 AskUserQuestion 把可推断字段包装成选择题，或绕过阶段契约直接弹出问题。",
                ),
            )
        if role == "commander":
            pending_cards = [
                card
                for card in (state.get("subagent_cards", {}) or {}).values()
                if isinstance(card, Mapping) and card.get("status") == "pending"
            ]
            if pending_cards:
                card = pending_cards[0]
                card_id = str(card.get("id", "<card>"))
                card_ref = str(card.get("card_ref", "loop-artifacts/task-cards/<card>.md"))
                return ToolDecision(
                    "deny",
                    tool_feedback(
                        "PENDING_CARD_DISPATCH",
                        detected=f"{tool_name} 在阶段 `{stage_id}` 被拒绝，且批准任务卡 `{card_id}` 仍为 pending。",
                        correction="当前阶段的第一工作动作不是调研或提问，而是先完成已批准的独立审计派发。",
                        next_action=(
                            f"下一次工具调用必须是 Agent；第一行必须写 "
                            f"`RALPH_TASK_CARD={card_ref}`，只按任务卡执行。"
                        ),
                        forbidden="Skill、WebSearch、WebFetch、AskUserQuestion、Bash 绕过和重复规划。",
                    ),
                )
        return ToolDecision(
            "deny",
            tool_feedback(
                "TOOL_STAGE_SCOPE",
                detected=f"{tool_name} 不允许由 {role} 在阶段 `{stage_id}` 使用。",
                correction="遵守当前阶段的工具白名单，不要用相近工具绕过权限。",
                next_action="选择当前阶段允许的唯一工作动作，或直接返回结构化 RALPH_STAGE_RESULT。",
                forbidden="试探其他工具、把工具调用改写成 Bash，或修改状态文件。",
            ),
        )
    if (
        role == "commander"
        and tool_name != "Agent"
        and not (tool_name == "Bash" and command and command.startswith("ralph "))
    ):
        pending_cards = [
            card
            for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping)
            and card.get("status") == "pending"
            and str(card.get("stage_id")) == stage_id
            and str(card.get("revision")) == str(state.get("stage", {}).get("revision", "r1"))
            and bool(card.get("required_for_advance"))
        ]
        if pending_cards:
            card = pending_cards[0]
            card_id = str(card.get("id", "<card>"))
            card_ref = str(card.get("card_ref", "loop-artifacts/task-cards/<card>.md"))
            return ToolDecision(
                "deny",
                tool_feedback(
                    "PENDING_CARD_FIRST_ACTION",
                    detected=(
                        f"当前阶段 `{stage_id}` 的必派任务卡 `{card_id}` 仍为 pending；"
                        f"{tool_name} 不能先于 Agent 使用。"
                    ),
                    correction="先完成独立门禁派发，避免在未审计的输入上继续推理、提问或调研。",
                    next_action=(
                        f"下一次工具调用必须是 Agent，第一行必须写 "
                        f"`RALPH_TASK_CARD={card_ref}`。"
                    ),
                    forbidden="Read、Glob、Grep、Bash、Skill、WebSearch、WebFetch、AskUserQuestion 和重复规划。",
                ),
            )
    if tool_name == "Bash" and command and not command.startswith("ralph ") and role == "commander":
        pending_cards = [
            card
            for card in (state.get("subagent_cards", {}) or {}).values()
            if isinstance(card, Mapping) and card.get("status") == "pending"
        ]
        if pending_cards:
            card = pending_cards[0]
            card_ref = str(card.get("card_ref", "loop-artifacts/task-cards/<card>.md"))
            return ToolDecision(
                "deny",
                tool_feedback(
                    "PENDING_CARD_ACTION",
                    detected=f"Commander 正在用 Bash 绕过 pending 任务卡 `{card.get('id', '<card>')}`。",
                    correction="任务卡已经由 runtime 生成，不需要创建、补写或伪造。",
                    next_action=(
                        f"立即使用 Agent 派发 `{card.get('id', '<card>')}`；prompt 第一行必须是 "
                        f"`RALPH_TASK_CARD={card_ref}`。"
                    ),
                    forbidden="Bash 写状态、cat/echo 生成任务卡、Write/Edit 或重复派发。",
                ),
            )
        return ToolDecision(
            "deny",
            tool_feedback(
                "COMMANDER_BASH_SCOPE",
                detected="Commander 使用 Bash 执行了非 ralph 控制器命令。",
                correction="Bash 只用于受控 ralph 诊断/控制命令，阶段结果由 Assistant 协议提交。",
                next_action="直接输出一次完整 `<RALPH_STAGE_RESULT>`，或调用已经批准任务卡对应的 Agent。",
                forbidden="cat/echo 伪造结果、直接写 loop-state.json、创建任务卡或用 Bash 代替 Agent。",
            ),
        )
    if tool_name in {"Write", "Edit"} and policy.read_only:
        return ToolDecision(
            "deny",
            tool_feedback(
                "READ_ONLY_STAGE",
                detected=f"阶段 `{stage_id}` 是只读阶段，不能使用 {tool_name}。",
                correction="只读取已有 artifact 并完成审计/结构化回执。",
                next_action="直接返回当前阶段要求的结构化结果。",
                forbidden="修改业务文件、契约、任务卡或 loop-state.json。",
            ),
        )
    if tool_name in {"Write", "Edit"} and target_path and target_path.endswith("loop-state.json"):
        return ToolDecision(
            "deny",
            tool_feedback(
                "STATE_FILE_PROTECTED",
                detected="工具目标是 loop-state.json。",
                correction="状态只能由结构化动作经过 runtime 原子写入。",
                next_action="返回结构化动作，不要直接改文件。",
                forbidden="Write/Edit/cat/echo 修改 loop-state.json。",
            ),
        )
    return ToolDecision("allow", "tool is allowed by role and stage policy")
