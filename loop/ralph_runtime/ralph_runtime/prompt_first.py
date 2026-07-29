"""Prompt-first RALPH workflow with Markdown as the only user-facing state.

This path deliberately does *not* judge the semantics of a factor breakdown,
research note, plan, or review.  It keeps only a tiny durable cursor so an
inline Stop Hook can remind the same Claude context what to do next.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


STATE_FILE = "ralph-loop.md"
ARTIFACT_DIR = Path("loop-artifacts") / "prompt-first"
DONE_MARKER = "<!-- ralph: done -->"
PENDING_TASK = "待填写：请用 `ralph loop <项目目录> <任务>` 提供明确任务。"


@dataclass(frozen=True)
class PromptStage:
    id: str
    slug: str
    title: str
    instruction: str
    sections: tuple[str, ...]


STAGES: tuple[PromptStage, ...] = (
    PromptStage(
        "01",
        "factor-decomposition",
        "目标、因素与空缺条件",
        "完整分解目标的影响因素；把已有条件与尚缺条件明确分开。不要先开始搜集资料。",
        ("完整因素分解", "现有条件", "空缺条件与待问问题", "优先级与边界"),
    ),
    PromptStage(
        "02",
        "research",
        "资料搜集与网页 AI 交叉询问",
        "从阶段 01 的空缺条件出发搜集资料。必须尝试一次用浏览器或 Playwright 向网页 AI 提问；若工具、登录或页面不可用，如实记录尝试方式、结果和局限后继续。外部事实记录来源、日期、观察和不确定性；网页 AI 回答只作线索并与来源区分。",
        ("研究问题", "来源与观察", "网页 AI 交叉询问", "暂定结论", "仍未解决的空缺"),
    ),
    PromptStage(
        "02.5",
        "cross-check",
        "交叉核验与矛盾",
        "比较独立来源与网页 AI 线索，记录一致处、矛盾处、可能原因和残余不确定性。",
        ("关键主张", "一致证据", "矛盾与解释", "残余不确定性"),
    ),
    PromptStage(
        "03",
        "action-plan",
        "具体行动分解",
        "只在现有证据基础上把行动拆成可执行步骤。每步写依赖、预期写入物、验收方式和失败时的替代路径；并行与汇合关系用普通 Markdown 表格或清单表达即可。",
        ("行动目标", "步骤与依赖", "预期写入物", "验收与替代路径"),
    ),
    PromptStage(
        "04",
        "execution-review",
        "执行与结果核对",
        "执行当前可做的步骤，记录实际产生的文件、命令或观察；逐项对照阶段 03 的验收方式，诚实记录未完成项。",
        ("执行记录", "实际写入物", "验收对照", "未完成项"),
    ),
    PromptStage(
        "04.5",
        "independent-review",
        "独立复核与下一步",
        "从反方角度复核结论和行动结果，列出矛盾、证据薄弱点、残余风险与最有价值的下一步。",
        ("独立复核", "矛盾与薄弱点", "残余风险", "下一步"),
    ),
)

_STAGE_BY_ID = {stage.id: stage for stage in STAGES}
_STATE_START = "<!-- ralph-prompt-state"
_STATE_END = "-->"


def state_path(root: str | Path) -> Path:
    return Path(root).expanduser().resolve() / STATE_FILE


def stage_for(stage_id: str) -> PromptStage:
    try:
        return _STAGE_BY_ID[str(stage_id)]
    except KeyError as exc:
        raise ValueError(f"unknown prompt-first stage: {stage_id}") from exc


def artifact_relative(stage_id: str) -> str:
    stage = stage_for(stage_id)
    return str(ARTIFACT_DIR / f"{stage.id}-{stage.slug}.md")


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def _encode_state(state: Mapping[str, str]) -> str:
    lines = [
        "# RALPH Prompt-First Loop",
        "",
        _STATE_START,
        f"stage: {state['stage']}",
        f"revision: {state['revision']}",
        f"status: {state['status']}",
        f"current_artifact: {state['current_artifact']}",
        _STATE_END,
        "",
        "## 原始任务（请勿改写）",
        "",
        state["task"],
        "",
        "## 机械说明",
        "",
        "这个文件只保存阶段游标，不评价内容质量。阶段内容全部写在当前 Markdown 工件中。",
        "Claude 完成本阶段后，在工件末尾单独写入 `<!-- ralph: done -->`；Stop Hook 只据此切换提示，不作语义校验。",
        "不要手动编辑本文件的阶段游标或原始任务；它由 Stop Hook 机械维护。普通项目工件可自由读取和写入。",
        "",
    ]
    return "\n".join(lines)


def load_state(root: str | Path) -> dict[str, str]:
    path = state_path(root)
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"<!-- ralph-prompt-state\s*\n(.*?)\n-->", raw, re.DOTALL)
    if match is None:
        raise ValueError(f"{path} is missing the prompt-first state header")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    required = ("stage", "revision", "status", "current_artifact")
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise ValueError(f"{path} is missing: {', '.join(missing)}")
    stage_for(values["stage"])
    task_match = re.search(
        r"^## 原始任务（请勿改写）\s*\n\n(.*?)(?=\n## 机械说明\s*\n|\Z)",
        raw,
        re.DOTALL | re.MULTILINE,
    )
    task = task_match.group(1).strip() if task_match else ""
    if not task:
        task = "原始任务正文不可读；以当前阶段工件与已记录证据为准，勿编造缺失事实。"
    return {
        "stage": values["stage"],
        "revision": values["revision"],
        "status": values["status"],
        "task": task,
        "current_artifact": values["current_artifact"],
    }


def _stage_document(stage: PromptStage, task: str) -> str:
    rendered_sections: list[str] = []
    for section in stage.sections:
        if stage.id == "02" and section == "网页 AI 交叉询问":
            rendered_sections.append(
                "## 网页 AI 交叉询问\n\n"
                "- 必须先运行：`ralph prompt-first web-llm .`\n"
                "- 回执路径或真实失败：待填写\n"
            )
        else:
            rendered_sections.append(f"## {section}\n\n")
    sections = "\n\n".join(rendered_sections)
    return (
        f"# 阶段 {stage.id} · {stage.title}\n\n"
        f"任务：{task}\n\n"
        f"本阶段要求：{stage.instruction}\n\n"
        f"{sections}\n"
        "## 阶段完成\n\n"
        "正文中的不确定性直接如实写出；不要因自我复核删除完成标记。完成后按当前 RALPH 提示追加完成标记。\n"
    )


def ensure_stage_document(root: str | Path, state: Mapping[str, str]) -> Path:
    project = Path(root).expanduser().resolve()
    relative = state["current_artifact"]
    path = project / relative
    if not path.exists():
        _atomic_write(path, _stage_document(stage_for(state["stage"]), state["task"]))
    return path


def initialize(root: str | Path, task: str) -> dict[str, str]:
    project = Path(root).expanduser().resolve()
    path = state_path(project)
    if path.exists():
        state = load_state(project)
        if task.strip() and state["task"] == PENDING_TASK:
            # ``ralph init`` may create a task-less Markdown scaffold.  Its
            # first explicit loop task is the task, not a late refinement.
            state = {**state, "task": task.strip()}
            _atomic_write(path, _encode_state(state))
            document = ensure_stage_document(project, state)
            if state["stage"] == "01" and DONE_MARKER not in document.read_text(encoding="utf-8"):
                _atomic_write(document, _stage_document(stage_for("01"), state["task"]))
        elif task.strip() and state["task"].strip() != task.strip():
            # Preserve the original task and write the new wording into the
            # current artifact rather than silently replacing an in-progress
            # decomposition.
            document = ensure_stage_document(project, state)
            existing = document.read_text(encoding="utf-8")
            note = f"\n## 最新人类补充\n\n{task.strip()}\n"
            if note.strip() not in existing:
                _atomic_write(document, existing.rstrip() + note)
        return state
    cleaned = task.strip() or PENDING_TASK
    state = {
        "stage": "01",
        "revision": "r1",
        "status": "running",
        "task": cleaned,
        "current_artifact": artifact_relative("01"),
    }
    _atomic_write(path, _encode_state(state))
    ensure_stage_document(project, state)
    return state


def render_prompt(root: str | Path, *, reason: str = "继续当前阶段") -> str:
    state = load_state(root)
    stage = stage_for(state["stage"])
    if stage.id == "02":
        tool_scope = (
            "3. 仅本阶段可搜集外部资料。先逐字执行一次 `ralph prompt-first web-llm .`；"
            "它会用当前任务自动生成问题、调用已获人类授权的本地 Playwright/API 网页 LLM，并把真实回执写到 `loop-artifacts/prompt-first/02-web-llm-cross-check.md`。"
            "无论成功、登录受限还是工具不可用，都在本阶段 Markdown 中记录回执路径、结果和局限。网页 AI 只是线索。\n"
            "   若回执中的所有 provider 都失败，立即把“网页 AI 不可用”写入当前 Markdown 并结束资料搜集，直接进入暂定结论与未解决空缺；此时不要再调用 WebSearch 或 Fetch。\n"
            "   只有至少一个 provider 成功时，才可针对一个明确空缺补充一次独立来源；不要把网页 AI 回答当来源。\n"
            "   若任一额外外部查询返回零结果或错误，立即把该观察写入当前 Markdown 并继续本阶段；不要为同一空缺反复空搜。\n"
            "   `Did 0 searches`、空 Fetch 或工具错误不是资料，绝不可写成“搜集到证据”；只有具体 URL/标题/日期可写入来源与观察。\n"
        )
    else:
        tool_scope = (
            "3. 当前阶段不为未来阶段提前浏览、搜索或询问网页 AI；只处理本阶段要求的输入与工件。\n"
        )
    final_stage_scope = ""
    if stage.id == "04.5":
        final_stage_scope = (
            "这是最终阶段：不要再读取其他文件、搜索或扩展分析。下一次工具调用必须直接 Write 当前工件，"
            "在四个标题下各写至少一条复核内容，并在同一次写入的末尾追加完成标记；写完立即结束。\n\n"
        )
    return (
        f"完成当前阶段所需输入的读取后，下一工具调用必须是 Write `{state['current_artifact']}`，直接写入本阶段完整 Markdown；不要先解释、额外搜索或 Edit 模板。\n\n"
        f"{final_stage_scope}"
        "# RALPH Prompt-First\n"
        "保持当前 Claude 会话连续工作；不要等待人工确认，也不要重启、创建字段任务或输出 JSON 协议。\n\n"
        f"当前阶段：{stage.id} · {stage.title}\n"
        f"当前工件：`{state['current_artifact']}`\n"
        f"任务：{state['task']}\n\n"
        f"本阶段要求：{stage.instruction}\n\n"
        "立即执行：\n"
        "1. Read `ralph-loop.md` 与当前工件；只读，不要改写其中的阶段游标或原始任务。\n"
        "2. 第一次填写当前阶段时，直接用 Write 覆盖该阶段模板，写入标题和完整 Markdown；不要先对模板调用 Edit。任何浏览器、WebSearch、Fetch 或 Bash 研究调用之前，先完成这次 Write。\n"
        "   后续增补才用 Edit；若 Edit 因文本不匹配失败，立即回到 Write 重写当前阶段文件并保留已有内容，不要停在错误消息上。\n"
        f"{tool_scope}"
        "4. 不要用 `ralph field-*`、`graph-apply`、字段 role/disposition 或 `loop-state.json`。\n"
        f"5. 各标题已经得到完整 Markdown、且不确定性已如实留在正文时，立刻把 `{DONE_MARKER}` 作为对 `{state['current_artifact']}` 的最后一次写入。阶段 02 必须先在“网页 AI 交叉询问”写入真实回执路径或真实失败，不能写成承诺。写入后绝不删除或重写该标记；立刻结束当前轮，不要总结、不要开始下一阶段、不要再调用工具。Stop Hook 会在同一 TUI 中给出下一阶段提示。\n\n"
        f"本次提醒原因：{reason}\n"
    )


def advance_if_marked_done(root: str | Path) -> tuple[dict[str, str], bool]:
    """Advance solely on the explicit Markdown marker, never on semantics."""

    project = Path(root).expanduser().resolve()
    state = load_state(project)
    if state["status"] == "completed":
        return state, False
    document = ensure_stage_document(project, state)
    if DONE_MARKER not in document.read_text(encoding="utf-8"):
        return state, False
    position = next(index for index, stage in enumerate(STAGES) if stage.id == state["stage"])
    if position + 1 >= len(STAGES):
        state = {**state, "status": "completed"}
    else:
        next_stage = STAGES[position + 1]
        state = {
            **state,
            "stage": next_stage.id,
            "current_artifact": artifact_relative(next_stage.id),
        }
    _atomic_write(state_path(project), _encode_state(state))
    if state["status"] != "completed":
        ensure_stage_document(project, state)
    return state, True


def handle_stop(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw_root = payload.get("cwd") or payload.get("workspace")
    if not isinstance(raw_root, str) or not raw_root.strip():
        return {}
    root = Path(raw_root).expanduser()
    if not state_path(root).exists():
        return {}
    state, advanced = advance_if_marked_done(root)
    if state["status"] == "completed":
        return {}
    reason = render_prompt(
        root,
        reason="上一阶段已由 Markdown 完成标记推进" if advanced else "尚未看到完成标记；继续补完当前 Markdown",
    )
    return {
        "decision": "block",
        "reason": reason[:12000],
        "systemMessage": "RALPH prompt-first continuation: keep the current Claude context and continue from Markdown state.",
    }


def status_summary(root: str | Path) -> dict[str, str | bool]:
    state = load_state(root)
    artifact = ensure_stage_document(root, state)
    return {
        **state,
        "artifact_exists": artifact.is_file(),
        "done_marker_present": DONE_MARKER in artifact.read_text(encoding="utf-8"),
    }


def system_prompt() -> str:
    return (
        "Use the RALPH prompt-first workflow. After reading the inputs needed for the current stage, make the requested Write tool call before prose or extra search. "
        "Markdown is the task record; do not invent JSON state machines, field roles, or semantic validation. Follow the "
        "short stage prompt, preserve prior Markdown, never manually edit ralph-loop.md (the Stop Hook maintains its cursor). Put uncertainty in the stage Markdown rather than withholding or removing its done marker. After appending that marker, end the turn immediately: do not begin the next stage; the Stop Hook will continue the same session."
    )
