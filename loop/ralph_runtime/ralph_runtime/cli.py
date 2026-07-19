"""Small CLI for the first RALPH runtime MVP."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    cards_for_current_stage,
    ensure_builder_skeletons,
    reconcile_partial_merges,
    materialize_contract_documents,
    stage_result_ref,
    stage_submission_template,
)
from .decomposition_benchmark import (
    DEFAULT_SIMPLE_GPU_TASK,
    evaluate_state,
    evaluate_task_spec,
    load_task_spec_file,
)
from .prompt_renderer import PromptRenderer
from .replay_runner import run_fixture_file
from .events import append_observation, apply_and_record, read_events, replay_events
from .dag import validate_plan
from .hooks import run_hook
from .result_artifacts import resolve_result_artifact
from .project_resolver import ProjectResolution, resolve_project
from .nodes import DEFAULT_GRAPH, NodeGraph
from .state import (
    create_state,
    load_legacy_markdown,
    load_state,
    reset_subagent_card,
    save_state,
    set_task,
    start_new_task,
    update_subagent_card,
    field_completeness,
    _explode_comma_fields,
)
from .protocol import collect_validation_issues, parse_action, validate_action
from .task_board import TaskBoardError, read_task_board, select_next_task


MAX_EVENT_TAIL = 20


PROJECT_CLAUDE_FALLBACK = """# CLAUDE.md — RALPH project

本项目由 `ralph run` 初始化。

## RALPH 运行规则

- 先读取 `loop-state.json`，当前阶段以其中的 `stage` 为准。
- 按当前阶段执行，不自行跳过验证或修改 `loop-state.json`。
- 通过 Agent 工具派发实际执行任务；Commander 负责分解、验证和决策。
- 不得裸派 Agent。只可使用 `loop-state.json.subagent_cards` 中批准任务卡的
  `RALPH_TASK_CARD=<路径>` 作为 Agent prompt 第一行；Hook 会拒绝其他派发。
- 任务卡、阶段契约、输入包和提交模板由运行时生成；Commander 不得用 Agent、Write 或 Edit 创建或修复它们。
- 任务卡为 `dispatched` 时表示内部子代理正在运行，不是 `blocked_human`；不得重派、不得绕过 Hook，等待 `SubagentStop`。
- 01 必须先做语义分解与需求审计，02 必须生成并审计 DAG，03 完成所有任务后还要审计 Join，04 必须核验关键事实，05/06 分别审计决策与交接。
- 人类阻塞只阻塞当前任务，应返回 `blocked_human` 并继续其他 ready 任务。
- 阶段结束时返回 `<RALPH_STAGE_RESULT>` 结构化 JSON 动作。
- 过程记录在 `loop-events.md`，完整输出放在 `loop-artifacts/`。
- Commander 不得直接读取完整 `loop-events.md`；需要诊断时运行一次 `ralph events . --tail 20` 获取有限摘要。
- `loop-artifacts/contracts/task-spec.json` 是当前人类输入的规范副本；
  `loop-artifacts/task-cards/` 是子代理唯一应读取的任务边界。
- 独立门禁只读取 `stage-input-package.json`、阶段契约和 `submission-template.json`；通过阶段时 Commander 必须复制填写该模板并提交 `payload.stage_review`。

本次任务由启动命令的最后一个参数提供。先理解任务，再从 `loop-state.json` 的当前阶段开始。
"""

# The local oMLX setup in this workspace starts applying memory pressure well
# before the model's advertised context window. Keep RALPH's Claude sessions
# on a smaller, explicit compaction budget without changing ordinary Claude
# sessions launched by the user.
# The latest local oMLX trace rejected a 41,472-token prefill while the model
# was already above the balanced safety cap. A ~32k proactive target is a
# safer starting point; users can raise it explicitly after measuring headroom.
DEFAULT_AUTO_COMPACT_WINDOW = 40_000
DEFAULT_AUTOCOMPACT_PERCENT = 80


def _state_path(project: str | Path) -> Path:
    path = Path(project).expanduser().resolve()
    return path if path.name == "loop-state.json" else path / "loop-state.json"


def _project_root(project: str | Path) -> Path:
    path = Path(project).expanduser().resolve()
    return path.parent if path.name == "loop-state.json" else path


def _workspace_root() -> Path | None:
    """Find the source workspace when running from the editable installation."""

    current = Path(__file__).resolve()
    for candidate in (current.parents[3], Path("/Users/a1-6/Desktop/workspace")):
        if (candidate / "agents-templates" / "RALPH-project" / "CLAUDE.md").exists():
            return candidate
    return None


def _project_claude_text() -> str:
    workspace = _workspace_root()
    if workspace is not None:
        template = workspace / "agents-templates" / "RALPH-project" / "CLAUDE.md"
        return template.read_text(encoding="utf-8")
    return PROJECT_CLAUDE_FALLBACK


def _claude_executable() -> str:
    """Return Claude Code while allowing a user-specific executable override."""

    configured = os.environ.get("RALPH_CLAUDE_BIN", "claude")
    if Path(configured).is_absolute():
        if Path(configured).exists():
            return configured
    else:
        resolved = shutil.which(configured)
        if resolved:
            return resolved
        for fallback in ("/opt/homebrew/bin/claude", "/usr/local/bin/claude"):
            if Path(fallback).exists():
                return fallback
    raise OSError(
        "找不到 Claude Code 可执行文件。请确认 `claude` 在 PATH 中，"
        "或设置 RALPH_CLAUDE_BIN=/绝对路径/claude。"
    )


def _ensure_project_scaffold(root: Path) -> list[str]:
    """Create only missing project bootstrap files; never overwrite user files."""

    created: list[str] = []
    claude_path = root / "CLAUDE.md"
    if not claude_path.exists():
        claude_path.write_text(_project_claude_text(), encoding="utf-8")
        created.append(str(claude_path))

    workspace = _workspace_root()
    agents_source = workspace / "agents" if workspace is not None else None
    agents_link = root / ".claude" / "agents"
    if agents_source is not None and agents_source.is_dir() and not agents_link.exists() and not agents_link.is_symlink():
        agents_link.parent.mkdir(parents=True, exist_ok=True)
        agents_link.symlink_to(agents_source, target_is_directory=True)
        created.append(str(agents_link))
    return created


def prepare_project(
    project: str | Path,
    task: str | None = None,
    mode: str = "enforce",
    record_session: bool = False,
    fresh_if_completed: bool = False,
) -> tuple[Path, Path, bool, list[str]]:
    """Ensure a project can start and optionally attach the user's task."""

    root = _project_root(project)
    root.mkdir(parents=True, exist_ok=True)
    state_path = root / "loop-state.json"
    is_new = not state_path.exists()
    reopened_from_completed = False
    if is_new:
        legacy_state = load_legacy_markdown(
            root / ".claude" / "ralph-loop.local.md",
            root.name or str(root),
        )
        initial_state = legacy_state or create_state(root.name or str(root), task=task)
        if task:
            initial_state = set_task(initial_state, task)
        if fresh_if_completed and task and initial_state.get("status") == "completed":
            initial_state = start_new_task(initial_state, task)
            reopened_from_completed = True
        save_state(state_path, initial_state)
    elif task:
        current = load_state(state_path)
        if fresh_if_completed and current.get("status") == "completed":
            current = start_new_task(current, task)
            reopened_from_completed = True
            save_state(state_path, current)
        else:
            current_task = current.get("task", {}) if isinstance(current.get("task"), dict) else {}
            if current_task.get("description") != task:
                save_state(state_path, set_task(current, task))

    events_path = root / "loop-events.md"
    events_path.touch(exist_ok=True)
    persisted_state = load_state(state_path)
    save_state(state_path, persisted_state)
    materialize_contract_documents(root, persisted_state)
    ensure_builder_skeletons(persisted_state, root)
    created = _ensure_project_scaffold(root)
    settings_path = install_hooks(root, mode)
    if record_session:
        append_observation(
            events_path,
            "session_started",
            {
                "project": str(root),
                "new_project_state": is_new,
                "task": task or "",
                "created_files": created,
                "hook_mode": mode,
                "reopened_from_completed": reopened_from_completed,
            },
        )
    return root, settings_path, is_new, created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ralph", description="Minimal RALPH state-machine runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("project")

    status = sub.add_parser("status")
    status.add_argument("project")

    events = sub.add_parser(
        "events",
        help="只读取事件日志的有限尾部摘要，避免把完整 loop-events.md 注入模型上下文",
    )
    events.add_argument("project", nargs="?", default=".")
    events.add_argument("--tail", type=int, default=20, help="返回最近多少个事件（最多 20）")

    task_next = sub.add_parser(
        "task-next",
        help="扫描项目 tasks/TASKS.md，返回最高优先级且依赖已满足的任务（只读）",
    )
    task_next.add_argument("project", nargs="?", default=".")

    prompt = sub.add_parser("prompt")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)
    render = prompt_sub.add_parser("render")
    render.add_argument("project")
    replay = prompt_sub.add_parser("replay")
    replay.add_argument("fixture")

    apply = sub.add_parser("apply")
    apply.add_argument("project")
    apply.add_argument("action_file")

    field_apply = sub.add_parser(
        "field-apply",
        help="字段校验命令：把字段增量文件合并进 loop-state.json 的 attribute_matrix，"
        "校验通过才由 runtime 原子落盘（Commander 不得直接改 loop-state.json）。",
    )
    field_apply.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    field_apply.add_argument("fields_file", help="字段增量 JSON：列表，或 {fields:[...]} / {attribute_matrix:[...]}")

    render_parser = sub.add_parser(
        "render",
        help="把阶段字段 JSON 自动渲染成易读 Markdown（写同级 .md 并打印）。"
        "不指定 json 文件时渲染当前阶段文件 current_artifact。",
    )
    render_parser.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    render_parser.add_argument("json_file", nargs="?", default=None, help="要渲染的 JSON（默认用当前阶段文件）")

    watch_parser = sub.add_parser(
        "watch",
        help="通用实时看板：轮询持久化状态/阶段文件/事件（不依赖 stdout），"
        "每 interval 秒刷新一次，任意项目可用，Ctrl-C 退出。",
    )
    watch_parser.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    watch_parser.add_argument("--interval", type=float, default=5.0, help="刷新间隔秒（默认 5）")
    watch_parser.add_argument("--lines", type=int, default=42, help="字段快照最多显示行数（默认 42）")

    recover_state = sub.add_parser(
        "recover-state",
        help="状态自愈/重置：loop-state.json 损坏或需回退时，从 .bak 或阶段快照恢复（即重置到上一阶段）。",
    )
    recover_state.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    recover_state.add_argument("--stage", default=None, help="恢复到指定阶段快照 loop-artifacts/snapshots/loop-state.<stage>.json")
    recover_state.add_argument("--to-backup", action="store_true", help="优先从 loop-state.json.bak 恢复")

    replay = sub.add_parser("replay")
    replay.add_argument("project")

    assemble = sub.add_parser(
        "assemble",
        help="合并 builder 切片为阶段结果工件（自动注入已有门禁回执）",
    )
    assemble.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    assemble.add_argument("--stage", default=None, help="覆盖阶段 id（默认用当前 loop-state.json）")
    assemble.add_argument("--revision", default=None, help="覆盖轮次（默认用当前 loop-state.json）")

    validate = sub.add_parser("validate")
    validate.add_argument("project", nargs="?", default=".", help="项目目录（默认当前目录）")
    validate.add_argument(
        "--result",
        default=None,
        help="校验 loop-artifacts/stages/ 下的阶段结果工件，而不是只检查当前 DAG",
    )
    validate.add_argument(
        "--apply",
        action="store_true",
        help="阶段结果工件校验通过后立即通过 runtime 原子应用",
    )

    benchmark = sub.add_parser(
        "benchmark-decomposition",
        help="只读评估简单 GPU 任务的完整语义分解和 auditor 生命周期",
    )
    benchmark.add_argument("project", nargs="?", default=".")
    benchmark.add_argument(
        "--action-file",
        default=None,
        help="评估保存的 task-spec/action JSON，不读取项目状态",
    )
    benchmark.add_argument("--task", default=None, help="覆盖 benchmark 报告中的任务描述")
    benchmark.add_argument("--threshold", type=float, default=0.8, help="通过阈值，默认 0.8")

    recover = sub.add_parser(
        "recover-card",
        help="仅恢复没有有效门禁回执、却被错误标为完成/失败的任务卡",
    )
    recover.add_argument("project")
    recover.add_argument("card_id")
    recover.add_argument("--reason", required=True, help="写入事件日志的恢复原因")
    recover.add_argument(
        "--force-dispatched",
        action="store_true",
        help="确认子代理已退出且没有 SubagentStop 回执后，恢复残留 dispatched 卡",
    )

    hook = sub.add_parser("hook")
    hook.add_argument(
        "event",
        choices=(
            "pretooluse",
            "posttooluse",
            "subagentstart",
            "subagentstop",
            "userpromptsubmit",
            "precompact",
            "postcompact",
            "stop",
        ),
    )
    hook.add_argument("--mode", choices=("shadow", "enforce"), default=os.environ.get("RALPH_HOOK_MODE", "enforce"))
    hook.add_argument("--no-auto-apply", action="store_true", help="只记录 Stop 输出，不自动应用结构化动作")

    install = sub.add_parser("install-hooks")
    install.add_argument("project")
    install.add_argument("--mode", choices=("shadow", "enforce"), default="enforce")

    start = sub.add_parser("start")
    start.add_argument("project", nargs="?", default=".")
    start.add_argument("--mode", choices=("shadow", "enforce"), default=os.environ.get("RALPH_HOOK_MODE", "enforce"))
    start.add_argument("--launch", action="store_true")
    start.add_argument("--prompt", default=None)
    start.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default=None)
    start.add_argument("--model", default=None, help="仅本次 Claude 会话使用的模型名")
    _add_compaction_arguments(start)

    resume = sub.add_parser(
        "resume",
        help="从 loop-state.json 开一个短上下文的新 Claude 会话，恢复被运行时错误中断的阶段",
    )
    resume.add_argument("project", nargs="?", default=".")
    resume.add_argument("--mode", choices=("shadow", "enforce"), default=os.environ.get("RALPH_HOOK_MODE", "enforce"))
    resume.add_argument("--prompt", default=None, help="覆盖自动生成的短恢复指令")
    resume.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default=None)
    resume.add_argument("--model", default=None, help="仅本次 Claude 会话使用的模型名")
    _add_compaction_arguments(resume)

    run = sub.add_parser("run", help="自动初始化项目并用任务描述启动交互式 Claude 会话")
    run.add_argument("project_or_task", help="项目路径，或在省略 task 时直接填写任务描述")
    run.add_argument("task", nargs="?", help="显式项目路径模式下的任务描述")
    run.add_argument("--workspace", default=None, help="自动项目模式使用的 workspace 根目录")
    run.add_argument("--mode", choices=("shadow", "enforce"), default=os.environ.get("RALPH_HOOK_MODE", "enforce"))
    run.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default=None)
    run.add_argument("--model", default=None, help="仅本次 Claude 会话使用的模型名")
    run.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        help="跳过 Claude Code 交互式权限确认（RALPH Hook 仍强制派发/校验规则），便于无人值守可见 TUI",
    )
    _add_compaction_arguments(run)

    loop = sub.add_parser(
        "loop",
        help="持续监督：每轮用新的 Claude 上下文从 loop-state.json 继续，直到完成或显式等待人类",
    )
    loop.add_argument("project_or_task", help="项目路径，或在省略 task 时直接填写任务描述")
    loop.add_argument("task", nargs="?", help="显式项目路径模式下的任务描述")
    loop.add_argument("--workspace", default=None, help="自动项目模式使用的 workspace 根目录")
    loop.add_argument("--mode", choices=("shadow", "enforce"), default=os.environ.get("RALPH_HOOK_MODE", "enforce"))
    loop.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default=None)
    loop.add_argument("--model", default=None, help="仅本次 Claude 会话使用的模型名")
    loop.add_argument("--max-cycles", type=int, default=0, help="最多运行多少个新上下文；0 表示持续运行")
    loop.add_argument("--retry-delay", type=float, default=3.0, help="会话退出后再次启动前等待秒数")
    loop.add_argument("--agent-grace-seconds", type=float, default=5.0, help="回收残留任务卡前等待秒数")
    loop.add_argument("--idle-timeout", type=float, default=1800.0, help="无状态/事件活动多久后重启当前上下文；0 表示不启用")
    loop.add_argument("--wait-human", action="store_true", help="遇到 blocked_human 时等待人类，而不是按策略跳过")
    loop.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        help="跳过 Claude Code 交互式权限确认（RALPH Hook 仍强制派发/校验规则），便于无人值守可见 TUI",
    )
    _add_compaction_arguments(loop)

    return parser


def _hook_command(event: str, mode: str) -> str:
    return f"{shlex.quote(sys.executable)} -m ralph_runtime.cli hook {event} --mode {shlex.quote(mode)}"


def _with_effort(command: list[str], effort: str | None) -> list[str]:
    selected = effort or os.environ.get("RALPH_CLAUDE_EFFORT")
    if selected:
        command.extend(["--effort", selected])
    return command


def _with_model(command: list[str], model: str | None) -> list[str]:
    """Apply an optional session-only model override without changing user settings."""

    selected = model or os.environ.get("RALPH_CLAUDE_MODEL")
    if selected:
        command.extend(["--model", selected])
    return command


def _with_skip_permissions(command: list[str], skip: bool) -> list[str]:
    """Bypass Claude Code's interactive permission prompts for supervised runs.

    The RALPH hook chain still enforces every dispatch/validation rule; this only
    removes the separate Claude Code permission confirmation so an autonomous
    loop can run unattended under a visible TUI.
    """

    if skip:
        command.append("--dangerously-skip-permissions")
    return command


def _claude_environment(
    auto_compact_window: int | None = None,
    auto_compact_percent: int | None = None,
) -> tuple[dict[str, str], int, int]:
    """Build the environment for a RALPH-controlled Claude session.

    ``CLAUDE_CODE_AUTO_COMPACT_WINDOW`` is the capacity used by Claude Code's
    compaction calculation, while ``CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`` is the
    percentage at which compaction is requested. The defaults therefore aim
    at roughly 32k tokens (40k * 80%), leaving room for the compaction request
    before oMLX reaches the active-prefill memory guard.
    """

    raw_window = (
        auto_compact_window
        if auto_compact_window is not None
        else os.environ.get("RALPH_AUTO_COMPACT_WINDOW", str(DEFAULT_AUTO_COMPACT_WINDOW))
    )
    raw_percent = (
        auto_compact_percent
        if auto_compact_percent is not None
        else os.environ.get("RALPH_AUTOCOMPACT_PCT", str(DEFAULT_AUTOCOMPACT_PERCENT))
    )
    try:
        window = int(raw_window)
    except (TypeError, ValueError) as exc:
        raise ValueError("auto-compact window 必须是正整数 token 数") from exc
    try:
        percent = int(raw_percent)
    except (TypeError, ValueError) as exc:
        raise ValueError("auto-compact percent 必须是 1 到 100 的整数") from exc
    if window <= 0:
        raise ValueError("auto-compact window 必须大于 0")
    if not 1 <= percent <= 100:
        raise ValueError("auto-compact percent 必须在 1 到 100 之间")

    environment = os.environ.copy()
    environment["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = str(window)
    environment["CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"] = str(percent)
    return environment, window, percent


def _print_compaction_settings(window: int, percent: int) -> None:
    target = window * percent // 100
    print(f"Auto compact: capacity={window} tokens, trigger≈{target} tokens ({percent}%)")


def _add_compaction_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--auto-compact-window",
        type=int,
        default=None,
        help="本次 RALPH 会话用于自动压缩计算的容量；默认 40000，配合 80%% 约在 32k 触发",
    )
    parser.add_argument(
        "--auto-compact-percent",
        type=int,
        default=None,
        help="自动压缩触发百分比（1-100）；默认 80",
    )


def install_hooks(project: str | Path, mode: str = "enforce") -> Path:
    root = Path(project).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    state_path = root / "loop-state.json"
    if not state_path.exists():
        save_state(state_path, create_state(root.name or str(root)))
    (root / "loop-events.md").touch(exist_ok=True)
    settings_path = root / ".claude" / "settings.ralph.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "hooks": {
            "UserPromptSubmit": [{"hooks": [{"type": "command", "command": _hook_command("userpromptsubmit", mode)}]}],
            "PreToolUse": [{"matcher": ".*", "hooks": [{"type": "command", "command": _hook_command("pretooluse", mode)}]}],
            "PostToolUse": [{"matcher": ".*", "hooks": [{"type": "command", "command": _hook_command("posttooluse", mode)}]}],
            "SubagentStart": [{"hooks": [{"type": "command", "command": _hook_command("subagentstart", mode)}]}],
            "SubagentStop": [{"hooks": [{"type": "command", "command": _hook_command("subagentstop", mode)}]}],
            "PreCompact": [{"matcher": ".*", "hooks": [{"type": "command", "command": _hook_command("precompact", mode)}]}],
            "PostCompact": [{"matcher": ".*", "hooks": [{"type": "command", "command": _hook_command("postcompact", mode)}]}],
            "Stop": [{"hooks": [{"type": "command", "command": _hook_command("stop", mode)}]}],
        }
    }
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return settings_path


def recover_card(
    project: str | Path,
    card_id: str,
    reason: str,
    force_dispatched: bool = False,
) -> dict[str, object]:
    """Safely reopen a stale task card after a controller failure."""

    root = _project_root(project)
    state_path = root / "loop-state.json"
    state = load_state(state_path)
    cards = state.get("subagent_cards", {})
    card = cards.get(card_id) if isinstance(cards, dict) else None
    if not isinstance(card, dict):
        raise ValueError(f"unknown task card: {card_id}")
    prior_status = str(card.get("status", "pending"))
    if prior_status == "dispatched" and not force_dispatched:
        raise ValueError(
            f"task card {card_id} is 'dispatched'; only completed or failed cards can be recovered. "
            "确认子代理已退出且没有 SubagentStop 回执后，请显式使用 --force-dispatched。"
        )
    if card.get("is_stage_gate"):
        safe_card_id = card_id.replace("/", "_")
        receipts = sorted((root / "loop-artifacts" / "gate-reviews").glob(f"{safe_card_id}-*.json"))
        if receipts:
            joined = ", ".join(str(path.relative_to(root)) for path in receipts)
            raise ValueError(
                "任务卡已有有效门禁回执，不能用 recover-card 覆盖；"
                f"请通过正常阶段动作处理。回执：{joined}"
            )
    prior_agent_id = card.get("agent_id")
    updated = reset_subagent_card(state, card_id, allow_dispatched=force_dispatched)
    save_state(state_path, updated)
    materialize_contract_documents(root, updated)
    append_observation(
        root / "loop-events.md",
        "subagent_card_recovered",
        {
            "task_card_id": card_id,
            "prior_status": prior_status,
            "prior_agent_id": prior_agent_id,
            "reason": reason,
            "gate_receipt_present": False,
        },
    )
    return {
        "project": str(root),
        "card_id": card_id,
        "prior_status": prior_status,
        "status": "pending",
        "reason": reason,
    }


def _valid_gate_receipt(root: Path, card_id: str) -> tuple[str, dict[str, object]] | None:
    """Find the latest trustworthy gate receipt for a task card.

    The event journal is authoritative for the existence of a receipt; the
    JSON artifact is checked again before a stale dispatched card is
    reconciled. This path is only called by the outer supervisor after the
    Claude process it owns has exited.
    """

    event_path = root / "loop-events.md"
    try:
        events = read_events(event_path)
    except (OSError, ValueError):
        events = []
    references: list[str] = []
    for event in reversed(events):
        if event.get("type") != "subagent_gate_review_received":
            continue
        observation = event.get("observation")
        if not isinstance(observation, dict) or str(observation.get("task_card_id", "")) != card_id:
            continue
        reference = observation.get("artifact_ref")
        if reference:
            references.append(str(reference))
            break
    if not references:
        safe_card_id = card_id.replace("/", "_")
        references = [
            str(path.relative_to(root))
            for path in sorted((root / "loop-artifacts" / "gate-reviews").glob(f"{safe_card_id}-*.json"))
        ]
    for reference in references:
        artifact = root / reference
        try:
            raw = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict):
            continue
        if str(raw.get("reviewer_card_id", "")) != card_id:
            continue
        if raw.get("verdict") not in {"pass", "rollback", "blocked_human"}:
            continue
        checks = raw.get("checks")
        if not isinstance(checks, list) or not checks:
            continue
        return reference, raw
    return None


def reconcile_stale_cards(
    project: str | Path,
    *,
    reason: str = "supervisor observed that the owning Claude process exited",
) -> list[dict[str, object]]:
    """Reconcile task cards left dispatched after a dead or terminated session.

    A valid gate receipt is promoted to completed. Without one, the card is
    reopened as pending. The supervisor is the only caller that may make this
    judgment automatically, because it has just observed the process it
    launched exit and can wait a short grace period first.
    """

    root = _project_root(project)
    state_path = root / "loop-state.json"
    state = load_state(state_path)
    stage = state.get("stage", {})
    stage_id = str(stage.get("id", ""))
    revision = str(stage.get("revision", ""))
    cards = state.get("subagent_cards", {})
    if not isinstance(cards, dict):
        return []
    results: list[dict[str, object]] = []
    for card_id, raw_card in list(cards.items()):
        if not isinstance(raw_card, dict):
            continue
        if str(raw_card.get("status")) != "dispatched":
            continue
        if str(raw_card.get("stage_id")) != stage_id or str(raw_card.get("revision")) != revision:
            continue
        receipt = _valid_gate_receipt(root, str(card_id)) if raw_card.get("is_stage_gate") else None
        prior_agent_id = raw_card.get("agent_id")
        if receipt is not None:
            artifact_ref, review = receipt
            updated = update_subagent_card(
                state,
                str(card_id),
                "completed",
                agent_id=str(prior_agent_id) if prior_agent_id else None,
            )
            updated_card = updated["subagent_cards"][str(card_id)]
            updated_card["gate_review_ref"] = artifact_ref
            updated_card["gate_verdict"] = str(review.get("verdict"))
            updated_card["reconciled_from"] = "dispatched"
            save_state(state_path, updated)
            materialize_contract_documents(root, updated)
            state = updated
            outcome = "completed"
            detail: dict[str, object] = {
                "gate_review_ref": artifact_ref,
                "gate_verdict": review.get("verdict"),
            }
        else:
            updated = reset_subagent_card(state, str(card_id), allow_dispatched=True)
            save_state(state_path, updated)
            materialize_contract_documents(root, updated)
            state = updated
            outcome = "pending"
            detail = {"gate_review_ref": None}
        observation = {
            "task_card_id": str(card_id),
            "prior_status": "dispatched",
            "prior_agent_id": prior_agent_id,
            "outcome": outcome,
            "reason": reason,
            **detail,
        }
        append_observation(root / "loop-events.md", "subagent_card_reconciled", observation)
        results.append({"card_id": str(card_id), "outcome": outcome, **detail})
    return results


def task_next(project: str | Path) -> dict[str, object]:
    """Read the local task board without changing state or claiming a task."""

    root = _project_root(project)
    state = load_state(root / "loop-state.json")
    board_path = "tasks/TASKS.md"
    items = read_task_board(root, board_path)
    selected = select_next_task(root, board_path)
    selection = selected.selection() if selected else None
    if selected is not None:
        reason = "已找到最高优先级且依赖已满足的 ready/pending 任务；由探索节点提交后才会 claim。"
    elif not items:
        reason = "项目没有可读取的 tasks/TASKS.md，探索节点应输出 preference_brief 和 candidate 任务。"
    else:
        reason = "任务板存在，但没有可执行的 ready/pending 任务；探索节点应输出 preference_brief 和 candidate 任务。"
    return {
        "project": str(root),
        "stage": {
            "id": state.get("stage", {}).get("id"),
            "revision": state.get("stage", {}).get("revision"),
        },
        "board": board_path,
        "task_count": len(items),
        "ready": selected is not None,
        "selection": selection,
        "reason": reason,
    }


def benchmark_decomposition(
    project: str | Path = ".",
    *,
    action_file: str | Path | None = None,
    task: str | None = None,
    threshold: float = 0.8,
) -> dict[str, object]:
    """Run the read-only simple-task decomposition benchmark.

    With a project argument this grades the persisted ``loop-state.json`` and
    also checks that the requirements auditor card really completed.  With
    ``--action-file`` it grades a saved task-spec/action payload only, which is
    useful before a project is created or for deterministic fixture replay.
    """

    if not 0 < threshold <= 1:
        raise ValueError("benchmark threshold 必须在 0 和 1 之间")
    if action_file is not None:
        candidate, file_task = load_task_spec_file(action_file)
        result = evaluate_task_spec(
            candidate,
            task=task or file_task or DEFAULT_SIMPLE_GPU_TASK,
            threshold=threshold,
        )
        source = str(Path(action_file).expanduser().resolve())
        project_ref = None
    else:
        root = _project_root(project)
        state = load_state(root / "loop-state.json")
        result = evaluate_state(state, task=task, threshold=threshold)
        source = str(root / "loop-state.json")
        project_ref = str(root)
    report = result.to_dict()
    report["source"] = source
    report["project"] = project_ref
    report["read_only"] = True
    return report


def _bounded_event_text(value: object, limit: int = 600) -> str:
    text = str(value or "").replace("\x00", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[… 事件摘要已截断 …]"


def _event_summary(event: dict[str, object]) -> dict[str, object]:
    """Return audit metadata without replaying full Agent/tool output."""

    summary: dict[str, object] = {
        "event_id": event.get("event_id"),
        "type": event.get("type"),
        "timestamp": event.get("timestamp"),
    }
    for key in ("stage", "revision"):
        if event.get(key) is not None:
            summary[key] = event.get(key)

    action = event.get("action")
    if isinstance(action, dict):
        summary["action"] = {
            key: action.get(key)
            for key in ("action", "status", "stage_id", "revision", "next_stage", "rollback_to")
            if action.get(key) is not None
        }

    observation = event.get("observation")
    if isinstance(observation, dict):
        observation_summary: dict[str, object] = {}
        for key in (
            "tool_name",
            "role",
            "decision",
            "reason",
            "task_card_id",
            "agent_id",
            "task_card_status",
            "kind",
            "stop_reason",
            "recovery",
            "state_preserved",
        ):
            if observation.get(key) is not None:
                value = observation.get(key)
                observation_summary[key] = _bounded_event_text(value) if key in {"reason", "stop_reason"} else value
        if observation_summary:
            summary["observation"] = observation_summary

    output = event.get("output_excerpt")
    if output:
        summary["output_excerpt"] = _bounded_event_text(output)
    return summary


def assemble_stage_result(
    project: str | Path,
    stage_id: str | None = None,
    revision: str | None = None,
) -> dict[str, object]:
    """Merge builder slices into the canonical stage result artifact.

    Builders write one ``payload`` slice each to
    ``loop-artifacts/stages/<stage>/<rev>/<key>.json``.  This command is the
    only place the large result is assembled, so the Commander never has to
    author it inline.  If a valid independent gate review exists it is injected
    into ``payload.stage_review`` automatically.
    """

    root = _project_root(project)
    state = load_state(root / "loop-state.json")
    stage = state.get("stage", {})
    if stage_id is None:
        stage_id = str(stage.get("id", ""))
    if revision is None:
        revision = str(stage.get("revision", "r1"))

    base = stage_submission_template(state)
    slice_dir = root / "loop-artifacts" / "stages" / stage_id / revision
    merged_keys: list[str] = []
    if slice_dir.is_dir():
        for path in sorted(slice_dir.glob("*.json")):
            key = path.stem
            if key in {"manifest"}:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            base.setdefault("payload", {})[key] = data
            merged_keys.append(key)

    gate_review_injected = False
    gate = next(
        (
            card
            for card in cards_for_current_stage(state)
            if card.get("is_stage_gate")
            and str(card.get("stage_id")) == stage_id
            and str(card.get("revision")) == revision
        ),
        None,
    )
    if gate is not None:
        receipt = _valid_gate_receipt(root, str(gate["id"]))
        if receipt is not None:
            _, review = receipt
            base.setdefault("payload", {})["stage_review"] = review
            gate_review_injected = True

    result_path = root / stage_result_ref(stage_id, revision)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(base, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "project": str(root),
        "result_file": str(result_path.relative_to(root)),
        "merged_keys": merged_keys,
        "gate_review_injected": gate_review_injected,
    }


def events_tail(project: str | Path, limit: int = 20) -> dict[str, object]:
    """Read only the latest bounded event summaries for an active Commander."""

    if limit <= 0:
        raise ValueError("events --tail 必须大于 0")
    bounded_limit = min(limit, MAX_EVENT_TAIL)
    root = _project_root(project)
    event_path = root / "loop-events.md"
    all_events = read_events(event_path)
    selected = all_events[-bounded_limit:]
    return {
        "project": str(root),
        "event_log": str(event_path),
        "total_events": len(all_events),
        "returned_events": len(selected),
        "tail_limit": bounded_limit,
        "events": [_event_summary(event) for event in selected],
        "note": "这是有限摘要；完整 Agent/tool 输出只保存在 loop-artifacts 或事件摘录中。",
    }


def start_project(
    project: str | Path,
    mode: str,
    launch: bool,
    prompt: str | None,
    effort: str | None = None,
    model: str | None = None,
    auto_compact_window: int | None = None,
    auto_compact_percent: int | None = None,
) -> int:
    root, settings_path, _, _ = prepare_project(project, mode=mode)
    environment, compact_window, compact_percent = _claude_environment(
        auto_compact_window,
        auto_compact_percent,
    )
    command = _with_model(
        _with_effort(
            [_claude_executable(), "--settings", str(settings_path), "--setting-sources", "user,project,local"],
            effort,
        ),
        model,
    )
    if prompt:
        command.extend(["-p", prompt])
    print("RALPH project:", root)
    print("Hook settings:", settings_path)
    _print_compaction_settings(compact_window, compact_percent)
    print("Command:", " ".join(shlex.quote(item) for item in command))
    if launch:
        return subprocess.call(command, cwd=root, env=environment)
    return 0


def resume_project(
    project: str | Path,
    mode: str,
    prompt: str | None,
    effort: str | None = None,
    model: str | None = None,
    auto_compact_window: int | None = None,
    auto_compact_percent: int | None = None,
) -> int:
    """Start a fresh Claude context while preserving the project state.

    Claude's previous transcript is deliberately not continued here. The
    project files are the durable context; sending the old transcript again
    is exactly what can trigger oMLX's prefill guard after a long run.
    """

    root, settings_path, _, _ = prepare_project(
        project,
        mode=mode,
        record_session=True,
    )
    environment, compact_window, compact_percent = _claude_environment(
        auto_compact_window,
        auto_compact_percent,
    )
    state = load_state(root / "loop-state.json")
    recovery_prompt = prompt or PromptRenderer().compact_recovery_prompt(
        state,
        reason="从上一个会话的运行时中断恢复；以持久化状态为准。",
        error_kind="runtime",
        fresh_session=True,
    ).text
    command = _with_model(
        _with_effort(
            [
                _claude_executable(),
                "--settings",
                str(settings_path),
                "--setting-sources",
                "user,project,local",
            ],
            effort,
        ),
        model,
    )
    # A positional prompt starts an interactive session. Do not use
    # `--continue`: that would re-send the oversized transcript we are
    # recovering from.
    command.append(recovery_prompt)
    print("RALPH project:", root)
    print("Hook settings:", settings_path)
    _print_compaction_settings(compact_window, compact_percent)
    print("Starting a fresh Claude context from loop-state.json.")
    return subprocess.call(command, cwd=root, env=environment)


def _resolve_run_project(project_or_task: str | Path, task: str | None, workspace: str | Path | None) -> tuple[Path, str, ProjectResolution | None]:
    if task is not None:
        return Path(project_or_task), task, None
    task_text = str(project_or_task).strip()
    if not task_text:
        raise ValueError("ralph run requires a non-empty task description")
    start = Path(workspace).expanduser().resolve() if workspace is not None else Path.cwd()
    resolution = resolve_project(
        task_text,
        start=start,
        fallback_workspace=_workspace_root() if workspace is None else workspace,
    )
    return resolution.project, task_text, resolution


def run_project(
    project_or_task: str | Path,
    task: str | None = None,
    mode: str = "enforce",
    workspace: str | Path | None = None,
    effort: str | None = None,
    model: str | None = None,
    auto_compact_window: int | None = None,
    auto_compact_percent: int | None = None,
    skip_permissions: bool = False,
) -> int:
    """Initialize/reuse a project and start Claude; task-only mode auto-resolves it."""

    project, task, resolution = _resolve_run_project(project_or_task, task, workspace)
    task = task.strip()
    if not task:
        raise ValueError("ralph run requires a non-empty task description")
    root, settings_path, is_new, created = prepare_project(
        project,
        task=task,
        mode=mode,
        record_session=True,
        fresh_if_completed=True,
    )
    environment, compact_window, compact_percent = _claude_environment(
        auto_compact_window,
        auto_compact_percent,
    )
    command = _with_skip_permissions(
        _with_model(
            _with_effort(
                [
                    _claude_executable(),
                    "--settings",
                    str(settings_path),
                    "--setting-sources",
                    "user,project,local",
                ],
                effort,
            ),
            model,
        ),
        skip_permissions,
    )
    command.append(task)
    print("RALPH project:", root)
    if resolution is not None:
        print("RALPH workspace:", resolution.workspace)
        print("Project decision:", "reuse" if not resolution.created else "create")
        print("Decision reason:", resolution.reason)
    print("Project state:", "initialized" if is_new else "reused")
    if created:
        print("Created:", ", ".join(created))
    print("Hook settings:", settings_path)
    _print_compaction_settings(compact_window, compact_percent)
    print("Starting interactive Claude session with the supplied task.")
    return subprocess.call(command, cwd=root, env=environment)


def _resolve_loop_project(
    project_or_task: str | Path,
    task: str | None,
    workspace: str | Path | None,
) -> tuple[Path, str, ProjectResolution | None]:
    """Resolve either an existing project path or a new task description."""

    candidate = Path(project_or_task).expanduser()
    candidate_state = _state_path(candidate)
    if task is None and candidate_state.exists():
        state = load_state(candidate_state)
        task_record = state.get("task", {})
        description = task_record.get("description") if isinstance(task_record, dict) else None
        if not isinstance(description, str) or not description.strip():
            raise ValueError("项目 loop-state.json 没有可恢复的 task.description")
        return _project_root(candidate), description.strip(), None
    return _resolve_run_project(project_or_task, task, workspace)


def _count_event_markers(path: Path, marker: str) -> int:
    """Count occurrences of ``marker`` in an event log (0 if unreadable)."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return sum(1 for line in fh if marker in line)
    except OSError:
        return 0


def _run_claude_supervised(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    idle_timeout: float,
) -> tuple[int, bool]:
    """Run Claude while watching the durable state/event files for progress.

    Claude idles at the interactive prompt after a Stop hook and never exits on
    its own, so a naive supervisor would wait for ``idle_timeout`` (600s)
    between turns. To keep the AI working uninterrupted, we watch for the
    ``ralph_stop_handled`` marker that the Stop hook emits on every completed
    turn: once a new marker appears and Claude stays idle afterwards, we
    relaunch a fresh context after a short grace period. Any file activity
    (Claude still producing output) cancels the pending relaunch, so we never
    kill a turn that is still making progress.
    """

    process = subprocess.Popen(command, cwd=cwd, env=env)
    last_activity = time.monotonic()
    last_mtime = 0.0
    state_path = cwd / "loop-state.json"
    event_path = cwd / "loop-events.md"
    for path in (state_path, event_path):
        try:
            last_mtime = max(last_mtime, path.stat().st_mtime)
        except OSError:
            pass
    stop_marker = "ralph_stop_handled"
    relaunch_grace = 6.0
    last_stop_count = _count_event_markers(event_path, stop_marker)
    pending_relaunch_at: float | None = None

    def _terminate() -> tuple[int, bool]:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        return process.returncode if process.returncode is not None else 124, True

    while True:
        return_code = process.poll()
        if return_code is not None:
            return return_code, False
        newest_mtime = last_activity
        for path in (state_path, event_path):
            try:
                newest_mtime = max(newest_mtime, path.stat().st_mtime)
            except OSError:
                pass
        if newest_mtime > last_mtime:
            last_mtime = newest_mtime
            last_activity = time.monotonic()
            # Claude is producing output -> cancel any pending relaunch.
            pending_relaunch_at = None
        cur_stop = _count_event_markers(event_path, stop_marker)
        if cur_stop > last_stop_count:
            last_stop_count = cur_stop
            if pending_relaunch_at is None:
                pending_relaunch_at = time.monotonic() + relaunch_grace
        now = time.monotonic()
        if pending_relaunch_at is not None and now >= pending_relaunch_at:
            return _terminate()
        if idle_timeout > 0 and now - last_activity >= idle_timeout:
            return _terminate()
        time.sleep(min(5.0, max(0.25, idle_timeout / 10 if idle_timeout > 0 else 5.0)))


def _field_engine_tick(root: Path, state: dict) -> bool:
    """Field-centric per-cycle reconcile + auto-advance.

    Runs once per supervisor cycle in ``RALPH_FIELD_GATE`` mode (before the
    Commander context launches):

    - Explodes comma-separated field ``attribute`` values into independent
      sub-fields, written back into ``loop-state.json`` (deterministic,
      model-free proliferation).  Without this the field gate could never reach
      "complete" because the model writes comma lists directly and never emits
      the structured advance token that would otherwise trigger the explosion.
    - When the current stage is ``01`` and every field is dispositioned (no
      ``pending`` / no ``research_required`` without ``evidence_refs``), advances
      automatically -- the model does NOT need to emit ``<RALPH_STAGE_RESULT>``.

    Stages 02-06 keep their normal contract validation (the field gate only
    short-cuts stage 01), so they are not trivially skipped.

    Returns True if it advanced the stage this tick.
    """

    state_path = root / "loop-state.json"
    live = load_state(state_path)
    spec = live.get("task_spec")
    if not isinstance(spec, Mapping):
        return False
    matrix = spec.get("attribute_matrix")
    if not isinstance(matrix, list):
        return False
    exploded = _explode_comma_fields(matrix)
    if exploded != matrix:
        live["task_spec"] = dict(live.get("task_spec", {}))
        live["task_spec"]["attribute_matrix"] = exploded
        save_state(state_path, live)
    if isinstance(state, dict):
        state.setdefault("task_spec", {})
        state["task_spec"]["attribute_matrix"] = exploded

    stage = live.get("stage", {})
    current = str(stage.get("id", ""))
    if current != "01":
        return False
    verdict = field_completeness(exploded)
    if not verdict["complete"]:
        return False
    next_stage = str(stage.get("on_success") or "")
    if not next_stage or next_stage == current:
        return False
    action = {
        "action": "advance",
        "status": "passed",
        "stage_id": current,
        "revision": str(stage.get("revision", "r1")),
        "next_stage": next_stage,
        "payload": {
            "stage_review": (
                "字段门禁自动通过：本阶段所有 required 字段均已 disposition 完成"
                "（无 pending、无 research_required 未带 evidence）。运行时按字段完成自动推进，"
                "不再要求模型输出 <RALPH_STAGE_RESULT> token。"
            )
        },
    }
    apply_and_record(
        state_path,
        root / "loop-events.md",
        action,
        raw_output=json.dumps(action, ensure_ascii=False),
    )
    print(f"[field-gate] auto-advanced {current} -> {next_stage} (fields complete)")
    return True


def loop_project(
    project_or_task: str | Path,
    task: str | None = None,
    mode: str = "enforce",
    workspace: str | Path | None = None,
    effort: str | None = None,
    model: str | None = None,
    auto_compact_window: int | None = None,
    auto_compact_percent: int | None = None,
    max_cycles: int = 0,
    retry_delay: float = 3.0,
    agent_grace_seconds: float = 5.0,
    idle_timeout: float = 1800.0,
    wait_human: bool = False,
    skip_permissions: bool = False,
) -> int:
    """Keep advancing a project by launching fresh Claude contexts.

    Stop Hook can protect a live context, but it cannot resurrect a process
    lost to an API reset, memory guard or terminal closure. This outer loop is
    the durable liveness mechanism: state and artifacts are the source of
    truth, and every retry gets a bounded fresh prompt rather than the old
    transcript.
    """

    if max_cycles < 0:
        raise ValueError("max-cycles 不能小于 0")
    if retry_delay < 0 or agent_grace_seconds < 0 or idle_timeout < 0:
        raise ValueError("retry-delay、agent-grace-seconds 和 idle-timeout 不能小于 0")
    project, task_text, resolution = _resolve_loop_project(project_or_task, task, workspace)
    root, settings_path, is_new, created = prepare_project(
        project,
        task=task_text,
        mode=mode,
        record_session=True,
        fresh_if_completed=True,
    )
    if agent_grace_seconds:
        # Startup reconciliation is safe for a project whose previous owner
        # is no longer this supervisor process.
        time.sleep(min(agent_grace_seconds, 60.0))
    startup_reconciled = reconcile_stale_cards(
        root,
        reason="ralph loop startup recovered cards left by an earlier Claude session",
    )
    environment, compact_window, compact_percent = _claude_environment(
        auto_compact_window,
        auto_compact_percent,
    )
    first_prompt = task_text if is_new else None
    cycle = 0
    print("RALPH loop project:", root)
    if resolution is not None:
        print("RALPH workspace:", resolution.workspace)
        print("Project decision:", "reuse" if not resolution.created else "create")
        print("Decision reason:", resolution.reason)
    print("Startup reconciliation:", json.dumps(startup_reconciled, ensure_ascii=False))
    print("Auto compact:", f"capacity={compact_window}, trigger≈{compact_window * compact_percent // 100} tokens")
    print("Continuous supervisor active; use Ctrl-C to stop the supervisor.")
    print("Idle watchdog:", "disabled" if idle_timeout == 0 else f"{idle_timeout:g} seconds")

    while max_cycles == 0 or cycle < max_cycles:
        state = load_state(root / "loop-state.json")
        field_mode = bool(os.environ.get("RALPH_FIELD_GATE"))
        if not field_mode:
            # Card-centric mode: pre-generate builder skeletons and merge partials.
            ensure_builder_skeletons(state, root)
            reconcile_partial_merges(root, state)
        else:
            # Field-centric mode: the Commander writes task_spec.attribute_matrix
            # directly. Explode comma fields + auto-advance stage 01 when complete.
            if _field_engine_tick(root, state):
                continue
        status = str(state.get("status", "running"))
        if status in {"completed", "stopped"}:
            print("RALPH terminal state:", status)
            return 0
        if status == "blocked_human":
            if wait_human:
                print("RALPH waiting for human input; state preserved at", root)
                return 3
            stage = state.get("stage", {})
            next_stage = str(stage.get("on_human_block") or "exploration")
            action = {
                "action": "skip_blocked",
                "status": "skipped",
                "stage_id": str(stage.get("id", "")),
                "revision": str(stage.get("revision", "r1")),
                "next_stage": next_stage,
                "rollback_to": None,
                "evidence": ["ralph loop auto-skip policy"],
                "artifact_refs": [],
                "message": "当前人类阻塞不阻塞其他工作，按持续运行策略跳过并进入后续可执行节点。",
            }
            apply_and_record(
                root / "loop-state.json",
                root / "loop-events.md",
                action,
                raw_output=json.dumps(action, ensure_ascii=False),
            )
            print("Auto-skipped blocked_human ->", next_stage)
            continue

        recovery_prompt = PromptRenderer().compact_recovery_prompt(
            state,
            reason="上一轮 Claude 已结束；从持久化状态继续，不复述旧 transcript。",
            error_kind="continuation",
            fresh_session=True,
            root=str(root),
        ).text
        prompt = first_prompt or recovery_prompt
        first_prompt = None
        command = _with_skip_permissions(
            _with_model(
                _with_effort(
                    [
                        _claude_executable(),
                        "--settings",
                        str(settings_path),
                        "--setting-sources",
                        "user,project,local",
                    ],
                    effort,
                ),
                model,
            ),
            skip_permissions,
        )
        command.append(prompt)
        cycle += 1
        append_observation(
            root / "loop-events.md",
            "supervisor_cycle_started",
            {
                "cycle": cycle,
                "max_cycles": max_cycles,
                "stage": state.get("stage", {}).get("id"),
                "revision": state.get("stage", {}).get("revision"),
                "prompt_kind": "initial_task" if prompt == task_text and cycle == 1 else "fresh_recovery",
            },
        )
        print(f"RALPH cycle {cycle}: launching fresh Claude context")
        return_code, timed_out = _run_claude_supervised(
            command,
            cwd=root,
            env=environment,
            idle_timeout=idle_timeout,
        )
        if agent_grace_seconds:
            time.sleep(min(agent_grace_seconds, 60.0))
        if timed_out:
            append_observation(
                root / "loop-events.md",
                "supervisor_idle_timeout",
                {
                    "cycle": cycle,
                    "idle_timeout_seconds": idle_timeout,
                    "return_code": return_code,
                    "state_preserved": True,
                    "next_action": "fresh_context",
                },
            )
        try:
            reconciled = reconcile_stale_cards(
                root,
                reason=f"ralph loop cycle {cycle} ended with Claude return code {return_code}",
            )
        except (OSError, ValueError) as exc:
            reconciled = [{"error": str(exc)}]
        append_observation(
            root / "loop-events.md",
            "supervisor_cycle_finished",
            {
                "cycle": cycle,
                "return_code": return_code,
                "reconciled_cards": reconciled,
                "next_action": "fresh_context" if max_cycles == 0 or cycle < max_cycles else "supervisor_limit",
            },
        )
        print(f"RALPH cycle {cycle} ended with return code {return_code}; reconciled {len(reconciled)} card(s).")
        if max_cycles and cycle >= max_cycles:
            print("Reached --max-cycles; persistent state remains resumable.")
            return 0
        if retry_delay:
            time.sleep(min(retry_delay, 60.0))
    return 0


def _print_project_error(project: str | Path, error: Exception) -> None:
    raw_project = str(project)
    print(f"RALPH 无法启动项目 {raw_project!r}：{error}", file=sys.stderr)
    if raw_project.startswith("/") and Path(raw_project).parent == Path("/"):
        print(
            "提示：以 `/` 开头表示系统根目录下的绝对路径。请使用相对路径 `./gpu硬件调研`，"
            "或使用可写目录，例如 `$HOME/gpu硬件调研`。",
            file=sys.stderr,
        )
    else:
        print(
            "提示：确认项目路径位于可写目录；新项目可以使用 `./项目名` 或 `$HOME/项目名`。",
            file=sys.stderr,
        )


def validate_result_artifact(
    project: str | Path,
    result_file: str | Path,
    *,
    apply: bool = False,
) -> dict[str, object]:
    """Mechanically validate one stage result artifact, optionally apply it.

    Returns every field problem (not just the first) so the model can fix the
    whole payload in one pass via the fill-in workflow.
    """

    root = _project_root(project)
    path = resolve_result_artifact(root, result_file)
    raw = path.read_text(encoding="utf-8")
    action = parse_action(raw)
    state_path = root / "loop-state.json"
    state = load_state(state_path)
    issues = collect_validation_issues(action, state)
    report: dict[str, object] = {
        "valid": not issues,
        "project": str(root),
        "result_file": str(path.relative_to(root)),
        "issues": issues,
        "action": action.to_dict(),
        "applied": False,
    }
    if issues:
        return report
    if apply:
        updated = apply_and_record(
            state_path,
            root / "loop-events.md",
            raw,
            raw_output=raw,
        )
        report["applied"] = True
        report["state"] = {
            "status": updated.get("status"),
            "stage": updated.get("stage"),
            "last_event_id": updated.get("last_event_id"),
        }
    return report


def _tokenize(text: object) -> set[str]:
    """Split a field's textual content into comparable word tokens.

    Handles Chinese / English mixed text: keeps CJK runs as whole tokens and
    splits latin words on common delimiters, lower-cased."""
    if not isinstance(text, str):
        text = str(text)
    import re as _re

    toks: set[str] = set()
    for seg in _re.split(r"[\s,，、;；/|()（）]+", text):
        seg = seg.strip().lower()
        if not seg:
            continue
        # CJK characters: treat each maximal CJK run as one token
        for m in _re.finditer(r"[\u4e00-\u9fff]+|[a-z0-9]+", seg):
            toks.add(m.group(0))
    return toks


def _stage01_check(matrix: list[dict]) -> None:
    """Validate the stage-01 three-field constraint before commit.

    - exactly the concepts ``goal`` / ``known`` / ``unknown`` must be present;
    - ``goal`` must contain both ``known`` and ``unknown`` (token superset);
    - ``known`` and ``unknown`` must share no token."""
    by = {str(f.get("concept")): f for f in matrix if isinstance(f, dict)}
    if not ({"goal", "known", "unknown"} <= set(by)):
        return  # not a full stage-01 set yet; skip (incremental applies)
    goal = _tokenize(by["goal"].get("attribute", ""))
    known = _tokenize(by["known"].get("attribute", ""))
    unknown = _tokenize(by["unknown"].get("attribute", ""))
    if not goal or not known or not unknown:
        raise ValueError("stage-01: goal/known/unknown 的 attribute 不能为空")
    if not known <= goal:
        missing = known - goal
        raise ValueError(f"stage-01: 已知因素词语未全部包含在目标中: {sorted(missing)}")
    if not unknown <= goal:
        missing = unknown - goal
        raise ValueError(f"stage-01: 未知因素词语未全部包含在目标中: {sorted(missing)}")
    overlap = known & unknown
    if overlap:
        raise ValueError(f"stage-01: 已知与未知因素词语重叠: {sorted(overlap)}")


def _fields_from_any(obj: object) -> list[dict]:
    """Extract the field list from any accepted JSON shape.

    Accepts: a bare list of fields, ``{fields:[...]}``, ``{attribute_matrix:[...]}``,
    or a full ``task_spec`` object (``{attribute_matrix:[...]}``)."""
    if isinstance(obj, list):
        return [f for f in obj if isinstance(f, dict)]
    if isinstance(obj, dict):
        for key in ("fields", "attribute_matrix"):
            val = obj.get(key)
            if isinstance(val, list):
                return [f for f in val if isinstance(f, dict)]
        if "task_spec" in obj and isinstance(obj["task_spec"], dict):
            am = obj["task_spec"].get("attribute_matrix")
            if isinstance(am, list):
                return [f for f in am if isinstance(f, dict)]
    return []


def render_matrix_md(
    fields: list[dict],
    *,
    title: str = "阶段字段快照",
    source: str = "",
) -> str:
    """Render a field list into a clean, human-readable markdown.

    This is the readable twin of the machine JSON: the agent only writes JSON,
    and this produces the ``.md`` the human reads.  Grouped by ``role``."""
    import datetime as _dt

    fields = [f for f in fields if isinstance(f, dict)]
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    if source:
        lines.append(f"> 由 `ralph render` 自动从 `{source}` 生成，请勿手改。")
        lines.append("")
    lines.append(f"> 生成时间：{_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # 概览
    pending = [f for f in fields if str(f.get("disposition")) in ("pending", "research_required")]
    roles: dict[str, list[dict]] = {}
    for f in fields:
        roles.setdefault(str(f.get("role") or "未分类"), []).append(f)
    lines.append("## 概览")
    lines.append("")
    lines.append(f"- 字段总数：**{len(fields)}**")
    lines.append(f"- 待办（pending / research_required）：**{len(pending)}**")
    if roles:
        lines.append(f"- 分组：{'、'.join(f'{k}×{len(v)}' for k, v in roles.items())}")
    lines.append("")

    # 明细，按 role 分组
    lines.append("## 字段明细")
    lines.append("")
    for role, group in roles.items():
        lines.append(f"### {role}")
        lines.append("")
        lines.append("| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |")
        lines.append("|---|---|---|---|---|---|")
        for f in group:
            concept = str(f.get("concept") or "")
            attr = str(f.get("attribute") or "")
            disp = str(f.get("disposition") or "")
            conf = f.get("confidence")
            conf = "" if conf is None else (f"{float(conf):.2f}" if isinstance(conf, (int, float)) else str(conf))
            impact = str(f.get("impact") or "")
            rev = "是" if f.get("reversible") else ("否" if f.get("reversible") is False else "")
            # 多行属性用 <br> 折行
            attr = attr.replace("\n", "<br>")
            lines.append(f"| {concept} | {attr} | {disp} | {conf} | {impact} | {rev} |")
        lines.append("")

    # 证据与备注
    has_notes = any(f.get("rationale") or f.get("evidence_refs") for f in fields)
    if has_notes:
        lines.append("## 证据与备注")
        lines.append("")
        for f in fields:
            concept = str(f.get("concept") or "")
            rationale = str(f.get("rationale") or "").strip()
            refs = f.get("evidence_refs") or []
            if not rationale and not refs:
                continue
            lines.append(f"### {concept}")
            if rationale:
                lines.append("")
                lines.append(rationale)
            if refs:
                lines.append("")
                lines.append("证据：")
                for r in refs:
                    if isinstance(r, dict):
                        url = r.get("url") or r.get("ref") or ""
                        note = r.get("note") or r.get("title") or ""
                        lines.append(f"- [{note or url}]({url})" if url else f"- {note}")
                    else:
                        lines.append(f"- {r}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def apply_fields(project: str | Path, fields_file: str | Path) -> dict[str, object]:
    """Field-validation command used by the Commander in field-centric mode.

    The Commander never edits ``loop-state.json`` directly.  It writes a small
    delta file (only the fields it changed) and runs this command, which
    validates every field, merges by ``concept`` into ``task_spec.attribute_matrix``
    (replacing on match, appending otherwise; ``{"delete": true}`` removes), then
    commits atomically via :func:`save_state`.  This makes a corrupt write
    impossible: the runtime owns the only write path."""

    root = _project_root(project)
    state = load_state(root / "loop-state.json", graph=DEFAULT_GRAPH)
    raw = json.loads(Path(fields_file).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        fields = raw
    elif isinstance(raw, dict):
        fields = raw.get("fields") or raw.get("attribute_matrix") or []
    else:
        raise ValueError("fields file must be a list or {fields:[...]}/{attribute_matrix:[...]}")
    if not isinstance(fields, list):
        raise ValueError("fields must be a list")

    spec = state.setdefault("task_spec", {})
    if not isinstance(spec, dict):
        spec = {}
        state["task_spec"] = spec
    matrix = spec.setdefault("attribute_matrix", [])
    if not isinstance(matrix, list):
        matrix = []
        spec["attribute_matrix"] = matrix

    by_concept = {
        str(f.get("concept")): i
        for i, f in enumerate(matrix)
        if isinstance(f, dict)
    }
    added = removed = 0
    for f in fields:
        if not isinstance(f, dict):
            raise ValueError(f"field entry must be an object: {f!r}")
        if f.get("delete"):
            concept = str(f.get("concept"))
            if concept in by_concept:
                matrix.pop(by_concept[concept])
                removed += 1
            continue
        for req in ("concept", "attribute", "disposition", "role"):
            if not f.get(req):
                raise ValueError(f"field missing required key '{req}': {f!r}")
        concept = str(f.get("concept"))
        if concept in by_concept:
            matrix[by_concept[concept]] = f
        else:
            matrix.append(f)
            by_concept[concept] = len(matrix) - 1
        added += 1

    current_stage = str(state.get("stage", {}).get("id", "")) if isinstance(state.get("stage"), dict) else ""
    if current_stage == "01":
        _stage01_check(matrix)

    save_state(root / "loop-state.json", state)

    # 自动把最新阶段文件渲染成易读 .md（agent 只写 JSON，人读 MD）。best-effort。
    rendered_md: str | None = None
    try:
        ca = state.get("current_artifact")
        if ca:
            art = root / str(ca)
            if art.exists():
                spec = json.loads(art.read_text(encoding="utf-8"))
                fields = _fields_from_any(spec)
                if fields:
                    md = render_matrix_md(
                        fields,
                        title=f"{current_stage or '?'} 阶段字段快照",
                        source=ca,
                    )
                    md_path = art.with_suffix(".md")
                    md_path.write_text(md, encoding="utf-8")
                    rendered_md = str(md_path)
    except Exception:
        rendered_md = None

    result: dict[str, object] = {"ok": True, "added": added, "removed": removed, "total": len(matrix)}
    if rendered_md:
        result["rendered_md"] = rendered_md
    return result


def recover_state_cmd(
    project: str | Path,
    *,
    stage: str | None = None,
    to_backup: bool = False,
) -> dict[str, object]:
    """Restore a corrupted or unwanted ``loop-state.json``.

    Without flags, prefers ``loop-state.json.bak`` then the latest stage
    snapshot.  ``--stage <id>`` restores ``loop-artifacts/snapshots/loop-state.<id>.json``
    (the last saved state while in that stage) — i.e. "reset to a previous stage"."""

    root = _project_root(project)
    path = root / "loop-state.json"
    if not path.exists():
        return {"ok": False, "error": "no loop-state.json to recover"}

    def _restore(src: Path, label: str) -> dict[str, object]:
        data = json.loads(src.read_text(encoding="utf-8"))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "source": label}

    if to_backup:
        bak = path.with_name(path.name + ".bak")
        if not bak.exists():
            return {"ok": False, "error": "no loop-state.json.bak"}
        return _restore(bak, "loop-state.json.bak")

    if stage:
        snap = root / "loop-artifacts" / "snapshots" / f"loop-state.{stage}.json"
        if not snap.exists():
            return {"ok": False, "error": f"no snapshot for stage {stage}"}
        return _restore(snap, f"loop-artifacts/snapshots/loop-state.{stage}.json")

    bak = path.with_name(path.name + ".bak")
    if bak.exists():
        return _restore(bak, "loop-state.json.bak")
    snap_dir = root / "loop-artifacts" / "snapshots"
    snaps = sorted(snap_dir.glob("loop-state.*.json"), reverse=True) if snap_dir.is_dir() else []
    if snaps:
        return _restore(snaps[0], str(snaps[0].relative_to(root)))
    return {"ok": False, "error": "nothing to recover from"}


def render_cmd(project: str | Path, json_file: str | Path | None = None) -> dict[str, object]:
    """Render a stage field JSON into a human-readable markdown.

    With ``json_file`` it reads that file (any accepted shape).  Without it, it
    reads the current stage artifact referenced by ``loop-state.json``.  The
    markdown is written next to the source as ``<stem>.md`` and also printed."""
    root = _project_root(project)

    if json_file:
        src = Path(json_file)
        if not src.is_absolute():
            src = root / src
        if not src.exists():
            return {"ok": False, "error": f"json file not found: {src}"}
        obj = json.loads(src.read_text(encoding="utf-8"))
        source_name = str(src.relative_to(root)) if root in src.parents else str(src)
        title = f"{src.stem} 字段快照"
    else:
        state = load_state(root / "loop-state.json", graph=DEFAULT_GRAPH)
        ca = state.get("current_artifact")
        if not ca:
            return {"ok": False, "error": "no current_artifact in loop-state.json; pass a json-file"}
        src = root / str(ca)
        if not src.exists():
            return {"ok": False, "error": f"artifact not found: {src}"}
        obj = json.loads(src.read_text(encoding="utf-8"))
        source_name = ca
        title = f"{state.get('stage', {}).get('id', '?')} 阶段字段快照"

    fields = _fields_from_any(obj)
    if not fields:
        return {"ok": False, "error": "no fields found to render"}
    md = render_matrix_md(fields, title=title, source=source_name)
    md_path = src.with_suffix(".md")
    md_path.write_text(md, encoding="utf-8")
    print(md, end="")
    return {"ok": True, "md": str(md_path), "fields": len(fields)}


def watch_cmd(project: str | Path, *, interval: float = 5.0, max_lines: int = 42) -> int:
    """Live, TUI-free dashboard for any running ralph session.

    Polls the durable state / artifact / event files (never the agent's stdout)
    and refreshes a compact view every ``interval`` seconds.  Works for any
    project; ``Ctrl-C`` exits."""
    import os as _os
    import time as _time

    root = _project_root(project)
    try:
        while True:
            _os.system("clear" if _os.name == "posix" else "cls")
            print(f"===== {_time.strftime('%Y-%m-%d %H:%M:%S')} | {root.name} =====")
            try:
                state = load_state(root / "loop-state.json", graph=DEFAULT_GRAPH)
                stage = state.get("stage") if isinstance(state.get("stage"), dict) else {}
                print(
                    f"阶段: {stage.get('id')} {stage.get('revision')} | 状态: {state.get('status')} "
                    f"| 文件: {state.get('current_artifact')}"
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[状态读取失败] {exc}")
                state = {}
            print("\n----- 当前字段快照 -----")
            try:
                ca = state.get("current_artifact")
                if ca and (root / str(ca)).exists():
                    obj = json.loads((root / str(ca)).read_text(encoding="utf-8"))
                    fields = _fields_from_any(obj)
                    if fields:
                        md = render_matrix_md(fields, title=f"{stage.get('id', '?')} 阶段字段快照", source=ca)
                        print("\n".join(md.splitlines()[:max_lines]))
            except Exception as exc:  # noqa: BLE001
                print(f"[渲染失败] {exc}")
            print("\n----- 最近事件 -----")
            try:
                ev = events_tail(str(root), 6)
                for e in ev.get("events", [])[-6:]:
                    obs = e.get("observation") or {}
                    print(f" - {e.get('type')} | {obs.get('tool_name') or obs.get('role')} @ {str(e.get('timestamp', ''))[11:19]}")
            except Exception as exc:  # noqa: BLE001
                print(f"[事件读取失败] {exc}")
            _time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        path = _state_path(args.project)
        if path.exists():
            print(f"state already exists: {path}", file=sys.stderr)
            return 2
        prepare_project(path.parent, mode="enforce")
        print(path)
        return 0
    if args.command == "status":
        state = load_state(_state_path(args.project))
        print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "events":
        try:
            print(json.dumps(events_tail(args.project, args.tail), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError) as exc:
            print(f"RALPH 无法读取有限事件摘要：{exc}", file=sys.stderr)
            return 2
    if args.command == "task-next":
        try:
            print(json.dumps(task_next(args.project), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        except (OSError, TaskBoardError, ValueError) as exc:
            print(f"RALPH 无法读取任务板：{exc}", file=sys.stderr)
            return 2
    if args.command == "prompt" and args.prompt_command == "render":
        rendered = PromptRenderer().render(load_state(_state_path(args.project)))
        print(rendered.text, end="")
        print(f"prompt_sha256={rendered.sha256}", file=sys.stderr)
        return 0
    if args.command == "prompt" and args.prompt_command == "replay":
        updated, prompt_hash, action = run_fixture_file(args.fixture)
        print(json.dumps({"prompt_sha256": prompt_hash, "action": action.to_dict(), "state": updated}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "apply":
        path = _state_path(args.project)
        raw = json.loads(Path(args.action_file).read_text(encoding="utf-8"))
        updated = apply_and_record(path, path.parent / "loop-events.md", raw)
        print(json.dumps(updated, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "field-apply":
        try:
            report = apply_fields(args.project, args.fields_file)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    if args.command == "recover-state":
        try:
            report = recover_state_cmd(args.project, stage=args.stage, to_backup=args.to_backup)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if report.get("ok") else 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    if args.command == "render":
        try:
            report = render_cmd(args.project, args.json_file)
            if not report.get("ok"):
                print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
                return 1
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    if args.command == "watch":
        return watch_cmd(args.project, interval=args.interval, max_lines=args.lines)
    if args.command == "assemble":
        try:
            report = assemble_stage_result(args.project, stage_id=args.stage, revision=args.revision)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"RALPH 无法合成阶段结果：{exc}", file=sys.stderr)
            return 2
    if args.command == "replay":
        path = _state_path(args.project)
        state = load_state(path)
        events = read_events(path.parent / "loop-events.md")
        replayed = replay_events(create_state(path.parent.name or str(path.parent)), events)
        print(json.dumps({"event_count": len(events), "state": replayed}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "validate":
        try:
            if args.result:
                result = validate_result_artifact(args.project, args.result, apply=args.apply)
                print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
                return 0
            if args.apply:
                raise ValueError("--apply 必须和 --result 一起使用")
            state = load_state(_state_path(args.project))
            report = validate_plan(state.get("plan", {}), strict=False)
            print(json.dumps({"nodes": report.node_ids, "ready": report.ready, "parallel_groups": report.parallel_groups}, ensure_ascii=False, indent=2))
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
    if args.command == "benchmark-decomposition":
        try:
            report = benchmark_decomposition(
                args.project,
                action_file=args.action_file,
                task=args.task,
                threshold=args.threshold,
            )
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if report["passed"] else 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"RALPH 无法运行分解 benchmark：{exc}", file=sys.stderr)
            return 2
    if args.command == "recover-card":
        try:
            print(
                json.dumps(
                    recover_card(
                        args.project,
                        args.card_id,
                        args.reason,
                        force_dispatched=args.force_dispatched,
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        except (OSError, ValueError) as exc:
            print(f"RALPH 无法恢复任务卡：{exc}", file=sys.stderr)
            return 2
    if args.command == "hook":
        print(run_hook(args.event, sys.stdin.read(), args.mode, auto_apply=not args.no_auto_apply))
        return 0
    if args.command == "install-hooks":
        print(install_hooks(args.project, args.mode))
        return 0
    if args.command == "start":
        try:
            return start_project(
                args.project,
                args.mode,
                args.launch,
                args.prompt,
                args.effort,
                args.model,
                args.auto_compact_window,
                args.auto_compact_percent,
            )
        except (OSError, ValueError) as exc:
            _print_project_error(args.project, exc)
            return 2
    if args.command == "resume":
        try:
            return resume_project(
                args.project,
                args.mode,
                args.prompt,
                args.effort,
                args.model,
                args.auto_compact_window,
                args.auto_compact_percent,
            )
        except (OSError, ValueError) as exc:
            _print_project_error(args.project, exc)
            return 2
    if args.command == "run":
        try:
            return run_project(
                args.project_or_task,
                args.task,
                args.mode,
                args.workspace,
                args.effort,
                args.model,
                args.auto_compact_window,
                args.auto_compact_percent,
                args.dangerously_skip_permissions,
            )
        except (OSError, ValueError) as exc:
            _print_project_error(args.project_or_task, exc)
            return 2
    if args.command == "loop":
        # Self-healing supervisor: the loop must never die.  State and artifacts
        # on disk are the source of truth, so a crashed/exit supervisor can
        # always respawn a fresh bounded context from durable state.  We wrap
        # loop_project in a restart loop: a clean terminal state (rc==0) stops;
        # any crash or non-zero exit restarts the supervisor instead of ending
        # the process (which would otherwise tear down the whole tmux session).
        while True:
            try:
                rc = loop_project(
                    args.project_or_task,
                    args.task,
                    args.mode,
                    args.workspace,
                    args.effort,
                    args.model,
                    args.auto_compact_window,
                    args.auto_compact_percent,
                    args.max_cycles,
                    args.retry_delay,
                    args.agent_grace_seconds,
                    args.idle_timeout,
                    args.wait_human,
                    args.dangerously_skip_permissions,
                )
                if rc == 0:
                    return 0
                print(f"RALPH supervisor exited with code {rc}; restarting in 5s")
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                print("RALPH supervisor interrupted by user; stopping.")
                return 130
            except Exception as exc:  # noqa: BLE001 - supervisor must self-heal
                print(f"RALPH supervisor crashed: {exc!r}; restarting in 10s")
                time.sleep(10)
                continue
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
