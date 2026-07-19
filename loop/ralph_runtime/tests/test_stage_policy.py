from ralph_runtime.stage_policy import decide_tool
from ralph_runtime.state import create_state


def test_commander_can_dispatch_but_not_edit():
    state = create_state("fixture")
    assert decide_tool(state, "commander", "Agent").decision == "allow"
    assert decide_tool(state, "commander", "Edit", target_path="x.py").decision == "deny"


def test_pending_required_card_is_the_only_first_commander_action():
    state = create_state("fixture")
    decision = decide_tool(
        state,
        "commander",
        "Read",
        target_path="loop-artifacts/contracts/01-r1-stage-contract.md",
    )

    assert decision.decision == "deny"
    assert "PENDING_CARD_FIRST_ACTION" in decision.reason
    assert "RALPH_TASK_CARD=" in decision.reason


def test_commander_bash_is_controller_only():
    state = create_state("fixture")
    assert decide_tool(state, "commander", "Bash", command="ralph status .").decision == "allow"
    state["subagent_cards"] = {}
    decision = decide_tool(state, "commander", "Bash", command="rm -rf x")
    assert decision.decision == "deny"
    assert "Agent" in decision.reason
    assert "RALPH_STAGE_RESULT" in decision.reason


def test_commander_bash_points_to_pending_card_dispatch():
    state = create_state("fixture")
    state["subagent_cards"] = {
        "01-r1-auditor": {
            "id": "01-r1-auditor",
            "status": "pending",
            "card_ref": "loop-artifacts/task-cards/01-r1-auditor.md",
        }
    }
    decision = decide_tool(state, "commander", "Bash", command="python update_state.py")
    assert decision.decision == "deny"
    assert "01-r1-auditor" in decision.reason
    assert "RALPH_TASK_CARD=" in decision.reason


def test_worker_write_is_stage_specific():
    state = create_state("fixture")
    state["stage"]["id"] = "03"
    assert decide_tool(state, "worker", "Write", target_path="output.md").decision == "allow"
    assert decide_tool(state, "worker", "Write", target_path="loop-state.json").decision == "deny"


def test_ask_user_feedback_routes_to_task_card_or_structured_questions():
    state = create_state("fixture")
    decision = decide_tool(state, "commander", "AskUserQuestion")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[ASK_USER_GATE]" in decision.reason
    assert "RALPH_TASK_CARD=" in decision.reason
    assert "不能直接问人" in decision.reason


def test_disallowed_research_tool_routes_to_pending_auditor():
    state = create_state("fixture")
    decision = decide_tool(state, "commander", "Skill")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[PENDING_CARD_DISPATCH]" in decision.reason
    assert "下一次工具调用必须是 Agent" in decision.reason
    assert "RALPH_TASK_CARD=loop-artifacts/task-cards/01-r1-builder-task_spec-context.md" in decision.reason


def test_blocked_human_feedback_stops_further_tool_calls():
    state = create_state("fixture")
    state["status"] = "blocked_human"
    decision = decide_tool(state, "commander", "Read", target_path="notes.md")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[HUMAN_BLOCK_ACTIVE]" in decision.reason
    assert "等待人类回答" in decision.reason
