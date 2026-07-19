from ralph_runtime.protocol import parse_action
from ralph_runtime.state import apply_action, create_state, update_subagent_card


def test_exploration_can_create_marked_candidate_and_resume():
    state = apply_action(
        create_state("fixture"),
        parse_action('{"action":"explore","status":"exploring","stage_id":"01","revision":"r1"}'),
    )
    assert state["status"] == "exploration"
    candidate = parse_action(
        '{"action":"candidate","status":"candidate","stage_id":"exploration","revision":"r1",'
        '"payload":{"title":"candidate task","research_summary":"evidence","reason":"why",'
        '"scope":"只研究一个可验证问题","preference_brief":"偏好可复现、低风险的下一步",'
        '"scanned_sources":["tasks/TASKS.md"]}}'
    )
    state = apply_action(state, candidate)
    assert state["queue"]["candidates"][0]["status"] == "candidate"
    assert state["last_exploration"]["preference_brief"] == "偏好可复现、低风险的下一步"
    gate = next(card for card in state["subagent_cards"].values() if card["stage_id"] == "exploration")
    state = update_subagent_card(state, gate["id"], "completed")
    resume = parse_action(
        '{"action":"advance","status":"passed","stage_id":"exploration","revision":"r1","next_stage":"01",'
        '"payload":{"stage_review":{"reviewer_card_id":"exploration-r1-exploration-auditor",'
        '"context_mode":"bounded_artifacts","verdict":"pass","recommended_action":"advance",'
        '"checked_input_refs":["loop-artifacts/contracts/exploration-r1-stage-input-package.json"],'
        '"checked_output_refs":["loop-artifacts/contracts/exploration-r1-submission-template.json"],'
        '"checks":[{"criterion":"任务板扫描完成","status":"pass","evidence_refs":[],"note":"ok"}],'
        '"blocking_findings":[],"summary":"ok"},'
        '"exploration":{"preference_brief":"继续处理已有任务","scanned_sources":["tasks/TASKS.md"],'
        '"selection_mode":"task_board","selected_task":{"task_id":"T1","title":"selected task",'
        '"source":"task_board","source_path":"tasks/TASKS.md","priority":"P1","reason":"ready"},'
        '"candidate_tasks":[]}}}'
    )
    state = apply_action(state, resume)
    assert state["stage"]["id"] == "01"
    assert state["task_intake"]["task_id"] == "T1"
    assert state["task"]["description"] == "selected task"


def test_candidate_without_research_is_rejected():
    from ralph_runtime.protocol import ProtocolError
    import pytest
    from ralph_runtime.state import create_state
    from ralph_runtime.protocol import validate_action

    with pytest.raises(ProtocolError):
        validate_action(
            parse_action('{"action":"candidate","status":"candidate","stage_id":"01","revision":"r1","payload":{"title":"incomplete"}}'),
            create_state("fixture"),
        )
