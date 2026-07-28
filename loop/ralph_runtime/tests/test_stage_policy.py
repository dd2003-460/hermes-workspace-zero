from ralph_runtime.stage_policy import decide_tool
from ralph_runtime.state import create_state


def test_commander_can_dispatch_and_edit_non_state_files():
    state = create_state("fixture")
    assert decide_tool(state, "commander", "Agent").decision == "allow"
    assert decide_tool(state, "commander", "Edit", target_path="x.py").decision == "allow"
    assert decide_tool(state, "commander", "Edit", target_path="loop-state.json").decision == "deny"


def test_ready_research_field_is_the_only_first_commander_action():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    state["field_tasks"] = [
        {
            "id": "02-r1-field-01-price",
            "path": "loop-artifacts/stages/02/r1/tasks/02-r1-field-01-price.json",
            "status": "ready",
            "disposition": "research_required",
        }
    ]
    decision = decide_tool(
        state,
        "commander",
        "Read",
        target_path="loop-artifacts/stages/02/r1/fields.json",
    )

    assert decision.decision == "deny"
    assert "FIELD_DISPATCH_FIRST" in decision.reason
    assert "RALPH_FIELD_TASK=loop-artifacts/stages/02/r1/tasks/02-r1-field-01-price.json" in decision.reason


def test_commander_can_submit_incremental_draft_while_research_is_ready():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    state["field_tasks"] = [{
        "id": "02-r1-field-01-price",
        "path": "loop-artifacts/stages/02/r1/tasks/02-r1-field-01-price.json",
        "status": "ready",
        "disposition": "research_required",
    }]
    draft = "loop-artifacts/stages/02/r1/fields.json"
    assert decide_tool(state, "commander", "Write", target_path=draft).decision == "allow"
    assert decide_tool(state, "commander", "Bash", command="ralph field-apply . " + draft).decision == "allow"
    assert decide_tool(state, "commander", "Bash", command="ralph apply . loop-artifacts/stages/02/r1/advance.json").decision == "allow"


def test_commander_bash_is_controller_only():
    state = create_state("fixture")
    assert decide_tool(state, "commander", "Bash", command="ralph status .").decision == "allow"
    decision = decide_tool(state, "commander", "Bash", command="rm -rf x")
    assert decision.decision == "deny"
    assert "field-apply" in decision.reason
    assert "不要用 cat、python、sed、echo" in decision.reason


def test_worker_accepts_absolute_ralph_field_apply_command():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    command = "/Users/a1-6/.local/bin/ralph field-apply . loop-artifacts/stages/02/r1/tasks/x.json"
    assert decide_tool(state, "worker", "Bash", command=command).decision == "allow"


def test_worker_accepts_auditable_web_llm_check_command():
    state = create_state("fixture")
    state["stage"]["id"] = "02.5"
    command = "ralph web-llm-check . loop-artifacts/stages/02.5/r1/tasks/field.json"
    assert decide_tool(state, "worker", "Bash", command=command).decision == "allow"


def test_exploration_field_worker_can_write_and_apply_its_field():
    state = create_state("fixture")
    state["stage"]["id"] = "exploration"
    state["field_tasks"] = [{
        "id": "exploration-r1-field-candidate",
        "path": "loop-artifacts/stages/exploration/r1/tasks/candidate.json",
        "status": "dispatched",
        "disposition": "pending",
        "agent_id": "worker-1",
    }]
    assert decide_tool(
        state,
        "worker",
        "Edit",
        target_path="loop-artifacts/stages/exploration/r1/tasks/candidate.json",
    ).decision == "allow"
    assert decide_tool(
        state,
        "worker",
        "Bash",
        command="ralph field-apply . loop-artifacts/stages/exploration/r1/tasks/candidate.json",
    ).decision == "allow"


def test_worker_accepts_cd_wrapper_for_ralph_field_apply():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    command = "cd /tmp/project && ralph field-apply . loop-artifacts/stages/02/r1/tasks/x.json"
    assert decide_tool(state, "worker", "Bash", command=command).decision == "allow"


def test_worker_accepts_quoted_cd_and_env_wrapper_for_ralph_field_apply():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    command = (
        "cd \"/tmp/project with spaces\" && RALPH_PROJECT=demo "
        "command /Users/a1-6/.local/bin/ralph field-apply . "
        "loop-artifacts/stages/02/r1/tasks/x.json"
    )
    assert decide_tool(state, "worker", "Bash", command=command).decision == "allow"


def test_commander_bash_points_to_ready_field_dispatch():
    state = create_state("fixture")
    state["stage"]["id"] = "02"
    state["field_tasks"] = [{
        "id": "02-r1-field-01-price",
        "path": "loop-artifacts/stages/02/r1/tasks/02-r1-field-01-price.json",
        "status": "ready",
        "disposition": "research_required",
    }]
    decision = decide_tool(state, "commander", "Bash", command="python update_state.py")
    assert decision.decision == "deny"
    assert "02-r1-field-01-price" in decision.reason
    assert "RALPH_FIELD_TASK=" in decision.reason


def test_commander_bash_points_to_incremental_fill_for_pending_field():
    state = create_state("fixture")
    state["stage"]["id"] = "01"
    state["field_tasks"] = [{
        "id": "01-r1-field-01-known",
        "path": "loop-artifacts/stages/01/r1/tasks/01-r1-field-01-known.json",
        "status": "ready",
        "disposition": "pending",
    }]
    decision = decide_tool(state, "commander", "Bash", command="python update_state.py")
    assert decision.decision == "deny"
    assert "pending/assumed_default" in decision.reason
    assert "field-apply" in decision.reason
    assert "下一次工具调用必须是 Agent" not in decision.reason


def test_worker_write_is_stage_specific():
    state = create_state("fixture")
    state["stage"]["id"] = "03"
    assert decide_tool(state, "worker", "Write", target_path="output.md").decision == "allow"
    assert decide_tool(state, "worker", "Write", target_path="loop-state.json").decision == "deny"


def test_ask_user_feedback_routes_to_field_or_open_question():
    state = create_state("fixture")
    decision = decide_tool(state, "commander", "AskUserQuestion")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[ASK_USER_FIELD_GATE]" in decision.reason
    assert "research_required" in decision.reason
    assert "禁止 Commander 向人类提问" in decision.reason


def test_disallowed_tool_routes_to_current_stage_policy():
    state = create_state("fixture")
    decision = decide_tool(state, "commander", "Skill")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[TOOL_STAGE_SCOPE_FIELD]" in decision.reason
    assert "字段中心模式" in decision.reason


def test_blocked_human_feedback_stops_further_tool_calls():
    state = create_state("fixture")
    state["status"] = "blocked_human"
    decision = decide_tool(state, "commander", "Read", target_path="notes.md")
    assert decision.decision == "deny"
    assert "RALPH_FEEDBACK[HUMAN_BLOCK_ACTIVE]" in decision.reason
    assert "等待人类回答" in decision.reason
