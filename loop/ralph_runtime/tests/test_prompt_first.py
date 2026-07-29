from pathlib import Path
import json

from ralph_runtime import prompt_first
import ralph_runtime.cli as cli


def test_initialize_creates_markdown_cursor_and_stage_one_template(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "完善一份面向大众的动机社会章节")

    assert state["stage"] == "01"
    assert not (tmp_path / "loop-state.json").exists()
    cursor = (tmp_path / "ralph-loop.md").read_text(encoding="utf-8")
    artifact = tmp_path / state["current_artifact"]
    document = artifact.read_text(encoding="utf-8")
    assert "ralph-prompt-state" in cursor
    assert "## 原始任务（请勿改写）" in cursor
    assert "task:" not in cursor
    assert "完整因素分解" in document
    assert "现有条件" in document
    assert "空缺条件与待问问题" in document
    assert prompt_first.DONE_MARKER not in document


def test_default_init_creates_prompt_first_scaffold_then_adopts_first_task(tmp_path: Path):
    project = tmp_path / "new-project"

    assert cli.main(["init", str(project)]) == 0
    assert (project / "ralph-loop.md").exists()
    assert not (project / "loop-state.json").exists()

    adopted = prompt_first.initialize(project, "完整的第一项任务")
    document = (project / adopted["current_artifact"]).read_text(encoding="utf-8")

    assert adopted["task"] == "完整的第一项任务"
    assert "完整的第一项任务" in document


def test_done_marker_advances_without_semantic_validation(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "测试 prompt-first")
    first = tmp_path / state["current_artifact"]
    first.write_text("# 很短但明确的阶段记录\n\n<!-- ralph: done -->\n", encoding="utf-8")

    advanced, changed = prompt_first.advance_if_marked_done(tmp_path)

    assert changed is True
    assert advanced["stage"] == "02"
    assert (tmp_path / advanced["current_artifact"]).is_file()


def test_cursor_tolerates_human_friendly_task_text_without_json_parsing(tmp_path: Path):
    prompt_first.initialize(tmp_path, "原始任务：检查“中文引号”和 emoji 🙂")
    cursor = tmp_path / "ralph-loop.md"
    text = cursor.read_text(encoding="utf-8").replace("“中文引号”", "“替换后的引号”")
    cursor.write_text(text, encoding="utf-8")

    state = prompt_first.load_state(tmp_path)

    assert state["stage"] == "01"
    assert "替换后的引号" in state["task"]


def test_stop_hook_keeps_same_context_and_advances_marked_stage(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "测试 Stop Hook")
    (tmp_path / state["current_artifact"]).write_text("# 阶段一\n\n<!-- ralph: done -->\n", encoding="utf-8")

    response = prompt_first.handle_stop({"cwd": str(tmp_path)})

    assert response["decision"] == "block"
    assert "current Claude context" in response["systemMessage"]
    assert prompt_first.load_state(tmp_path)["stage"] == "02"
    assert "资料搜集" in response["reason"]


def test_prompt_instructs_first_stage_write_not_fragile_template_edit(tmp_path: Path):
    prompt_first.initialize(tmp_path, "测试首写")
    prompt = prompt_first.render_prompt(tmp_path)

    assert prompt.startswith("完成当前阶段所需输入的读取后，下一工具调用必须是 Write")
    assert "直接用 Write 覆盖该阶段模板" in prompt
    assert "不要先对模板调用 Edit" in prompt
    assert "任何浏览器、WebSearch、Fetch 或 Bash 研究调用之前，先完成这次 Write" in prompt
    assert "当前阶段不为未来阶段提前浏览" in prompt
    assert "立刻结束当前轮" in prompt
    assert "绝不删除或重写该标记" in prompt


def test_research_tools_are_scoped_to_stage_two(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "测试浏览器范围")
    first = tmp_path / state["current_artifact"]
    first.write_text("<!-- ralph: done -->\n", encoding="utf-8")
    prompt_first.advance_if_marked_done(tmp_path)

    stage_two_prompt = prompt_first.render_prompt(tmp_path)

    assert "先逐字执行一次 `ralph prompt-first web-llm .`" in stage_two_prompt
    assert "不要为同一空缺反复空搜" in stage_two_prompt
    assert "绝不可写成“搜集到证据”" in stage_two_prompt
    assert "所有 provider 都失败" in stage_two_prompt
    assert "当前阶段不为未来阶段提前浏览" not in stage_two_prompt


def test_final_marker_completes_without_content_gate(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "完成测试")
    for _ in prompt_first.STAGES:
        current = prompt_first.load_state(tmp_path)
        (tmp_path / current["current_artifact"]).write_text("<!-- ralph: done -->\n", encoding="utf-8")
        prompt_first.advance_if_marked_done(tmp_path)

    assert prompt_first.load_state(tmp_path)["status"] == "completed"


def test_final_stage_prompt_forces_one_write_and_no_more_research(tmp_path: Path):
    state = prompt_first.initialize(tmp_path, "最终复核测试")
    for stage_id in ("01", "02", "02.5", "03", "04"):
        current = prompt_first.load_state(tmp_path)
        (tmp_path / current["current_artifact"]).write_text("<!-- ralph: done -->\n", encoding="utf-8")
        prompt_first.advance_if_marked_done(tmp_path)

    prompt = prompt_first.render_prompt(tmp_path)

    assert prompt.startswith("完成当前阶段所需输入的读取后，下一工具调用必须是 Write")
    assert "这是最终阶段：不要再读取其他文件、搜索或扩展分析" in prompt
    assert "同一次写入的末尾追加完成标记" in prompt


def test_prompt_first_settings_only_install_markdown_stop_hook(tmp_path: Path):
    settings_path = cli.install_prompt_first_hooks(tmp_path)
    settings = json.loads(settings_path.read_text(encoding="utf-8"))

    assert set(settings["hooks"]) == {"Stop"}
    assert "prompt-first-stop" in settings["hooks"]["Stop"][0]["hooks"][0]["command"]


def test_new_explicit_loop_defaults_to_prompt_first(tmp_path: Path, monkeypatch):
    captured = {}

    def fake_loop(project, task, **kwargs):
        captured.update({"project": Path(project), "task": task, **kwargs})
        return 0

    monkeypatch.setattr(cli, "prompt_first_loop_project", fake_loop)
    assert cli.main(["loop", str(tmp_path / "new-project"), "写一份高质量调研"]) == 0
    assert captured["project"] == (tmp_path / "new-project").resolve()
    assert captured["task"] == "写一份高质量调研"


def test_prompt_first_loop_injects_short_skill_and_never_installs_tool_gates(tmp_path: Path, monkeypatch):
    launched = {}

    def fake_run(command, **kwargs):
        launched["command"] = command
        launched["kwargs"] = kwargs
        return 0, False

    monkeypatch.setattr(cli, "_claude_executable", lambda: "claude")
    monkeypatch.setattr(cli, "_run_prompt_first_supervised", fake_run)
    assert cli.prompt_first_loop_project(tmp_path, "完成一个最小 Markdown 流程", max_cycles=1) == 0

    command = launched["command"]
    settings = json.loads((tmp_path / ".claude" / "settings.ralph-prompt-first.json").read_text(encoding="utf-8"))
    assert "--append-system-prompt" in command
    assert "RALPH Prompt-First" in command[-1]
    assert set(settings["hooks"]) == {"Stop"}
    assert not (tmp_path / "loop-state.json").exists()
