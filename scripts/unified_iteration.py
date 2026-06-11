#!/usr/bin/env python3
"""Unified Iteration Mechanism — 统一迭代机制

替代 ralph-loop 的 bash 脚本，解决：
1. 状态文件分散不一致（ralph-loop.global.md vs state.json）
2. 迭代记录为空（只有 iteration-1.md）
3. delivery 目标不存在（hermes-cli 无法解析）
4. 缺少 completion_promise 检测导致无限循环

设计原则：
- 单一状态源：state.json 是唯一真相来源
- 每次迭代必须有可验证产出
- 失败自动跳过，不停滞
- 与 dashboard 集成
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/a1-6/Desktop/workspace")
STATE_FILE = WORKSPACE / ".ralph" / "state.json"
ITERATIONS_DIR = WORKSPACE / ".ralph" / "iterations"
BACKUP_DIR = WORKSPACE / ".ralph" / "backups"

ITERATION_TYPES = {
    "research": "研究推进",
    "audit": "审计",
    "infra": "基础设施",
    "review": "审查",
    "cleanup": "清理",
}


def load_state() -> dict:
    """加载状态，如果不存在则创建"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    
    state = {
        "iteration": 0,
        "max_iterations": 0,  # 0 = unlimited
        "status": "idle",  # idle, running, paused, completed
        "current_type": "research",
        "started_at": datetime.now().isoformat(),
        "last_run": None,
        "last_result": None,
        "total_iterations": 0,
        "successful_iterations": 0,
    }
    save_state(state)
    return state


def save_state(state: dict) -> None:
    """保存状态（原子写入）"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    tmp.rename(STATE_FILE)


def create_backup() -> None:
    """创建状态备份"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"state-{timestamp}.json.bak"
    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, backup_file)


def scan_workspace() -> dict:
    """扫描 workspace 状态（供迭代参考）"""
    stats = {
        "project_count": 0,
        "total_files": 0,
        "last_updates": {},
        "pending_tasks": 0,
    }
    
    projects_dir = WORKSPACE / "projects"
    if projects_dir.exists():
        for entry in sorted(projects_dir.iterdir()):
            if entry.is_dir() and entry.name.startswith("D1-"):
                stats["project_count"] += 1
                stats["last_updates"][entry.name] = datetime.fromtimestamp(
                    max(f.stat().st_mtime for f in entry.rglob("*"))
                ).strftime("%Y-%m-%d %H:%M")
                stats["total_files"] += sum(1 for _ in entry.rglob("*"))
    
    return stats


def run_research_iteration(state: dict) -> dict:
    """执行研究推进迭代"""
    # Generate research brief
    brief = scan_workspace()
    
    result = {
        "type": "research",
        "action": "workspace_scan",
        "success": True,
        "findings": [],
    }
    
    # Check for stale projects (no update in 7+ days)
    cutoff = datetime.now() - __import__("datetime").timedelta(days=7)
    for proj, ts_str in brief.get("last_updates", {}).items():
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
            if ts < cutoff:
                result["findings"].append(f"Stale: {proj} (last: {ts_str})")
        except ValueError:
            pass
    
    return result


def run_audit_iteration(state: dict) -> dict:
    """执行审计迭代"""
    import subprocess
    result = {
        "type": "audit",
        "action": "health_check",
        "success": True,
        "checks": [],
        "findings": [],
    }

    # Check workspace health
    workspace_files = sum(1 for _ in WORKSPACE.rglob("*"))
    result["checks"].append({
        "check": "workspace_files",
        "value": workspace_files,
        "status": "ok" if workspace_files < 50000 else "warning",
    })

    # Check .bak files
    bak_count = sum(1 for _ in WORKSPACE.rglob("*.bak"))
    result["checks"].append({
        "check": "bak_files",
        "value": bak_count,
        "status": "ok" if bak_count < 100 else "alert",
    })

    # Check crons
    try:
        output = subprocess.run(
            ["python3", "-c", "import json; print(json.dumps(json.loads(open('/Users/a1-6/.hermes/cron/jobs.json').read()))[:500])"],
            capture_output=True, text=True, timeout=5
        )
        result["checks"].append({"check": "cron_system", "value": "accessible", "status": "ok"})
    except Exception as e:
        result["checks"].append({"check": "cron_system", "value": str(e)[:200], "status": "error"})

    # Check iteration file integrity
    existing_iters = sorted(ITERATIONS_DIR.glob("iteration-*.md"))
    expected = state.get("iteration", 0)
    missing = []
    for i in range(1, expected + 1):
        if not (ITERATIONS_DIR / f"iteration-{i}.md").exists():
            missing.append(i)
    if missing:
        result["findings"].append(f"Missing iteration files: {missing} (total {len(missing)} of {expected})")
    else:
        result["findings"].append("All iteration files present")

    # Check state consistency
    state_file_content = STATE_FILE.read_text()
    state_data = json.loads(state_file_content)
    actual_file_count = len(existing_iters)
    if state_data.get("iteration", 0) != actual_file_count:
        # Not all iterations produce .md files — note this
        result["findings"].append(
            f"State iteration={state_data.get('iteration')}, but only {actual_file_count} .md files exist"
        )

    return result


def run_infra_iteration(state: dict) -> dict:
    """执行基础设施迭代 — 检查cron、state consistency、文件健康"""
    import subprocess
    result = {
        "type": "infra",
        "action": "infrastructure_check",
        "success": True,
        "checks": [],
        "findings": [],
    }

    # Check cron jobs configuration
    cron_path = Path("/Users/a1-6/.hermes/cron/jobs.json")
    try:
        if cron_path.exists():
            cron_data = json.loads(cron_path.read_text())
            active = [j for j in cron_data.get("jobs", []) if j.get("enabled", True)]
            result["checks"].append({"check": "active_cron_jobs", "value": len(active), "status": "ok" if len(active) > 0 else "warning"})
            cron_names = [j["name"] for j in active]
            result["findings"].append(f"Active cron jobs: {', '.join(cron_names[:5])}")
        else:
            result["checks"].append({"check": "cron_config", "value": "not found", "status": "error"})
    except Exception as e:
        result["checks"].append({"check": "cron_config", "value": str(e)[:200], "status": "error"})

    # Check .ralph/ directory health
    ralph_dir = WORKSPACE / ".ralph"
    if ralph_dir.exists():
        dir_items = list(ralph_dir.iterdir())
        total_size = sum(f.stat().st_size for f in ralph_dir.rglob("*") if f.is_file())
        result["checks"].append({"check": "ralph_dir_items", "value": len(dir_items), "status": "ok"})
        result["checks"].append({"check": "ralph_dir_size_bytes", "value": total_size, "status": "ok"})
        result["findings"].append(f".ralph/ directory: {len(dir_items)} items, {total_size / 1024:.1f} KB total")
    else:
        result["checks"].append({"check": "ralph_dir", "value": "missing", "status": "error"})

    # Check projects directory
    projects_dir = WORKSPACE / "projects"
    if projects_dir.exists():
        stale_threshold = datetime.now() - __import__("datetime").timedelta(days=7)
        stale_projects = []
        for entry in sorted(projects_dir.iterdir()):
            if entry.is_dir() and entry.name.startswith("D1-"):
                latest = max((f.stat().st_mtime for f in entry.rglob("*")), default=0)
                latest_dt = datetime.fromtimestamp(latest)
                if latest_dt < stale_threshold:
                    stale_projects.append(f"{entry.name} (last: {latest_dt.strftime('%m-%d')})")
        result["checks"].append({"check": "stale_projects_7d", "value": len(stale_projects), "status": "warning" if stale_projects else "ok"})
        if stale_projects:
            result["findings"].append(f"Stale projects (7d): {'; '.join(stale_projects)}")
    else:
        result["checks"].append({"check": "projects_dir", "value": "missing", "status": "error"})

    # Check disk space
    try:
        stat = os.statvfs(str(WORKSPACE))
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        result["checks"].append({"check": "disk_free_gb", "value": round(free_gb, 1), "status": "ok" if free_gb > 5 else "warning"})
        result["findings"].append(f"Disk: {free_gb:.1f} GB free of {total_gb:.1f} GB total")
    except Exception as e:
        result["checks"].append({"check": "disk", "value": str(e)[:100], "status": "error"})

    # Check iteration file integrity
    existing_iters = sorted(ITERATIONS_DIR.glob("iteration-*.md"))
    expected = state.get("iteration", 0)
    missing = []
    for i in range(1, expected + 1):
        if not (ITERATIONS_DIR / f"iteration-{i}.md").exists():
            missing.append(i)
    if missing:
        result["findings"].append(f"Missing iteration files: {missing} ({len(missing)} of {expected})")
    else:
        result["findings"].append("All iteration files present")

    return result


def run_review_iteration(state: dict) -> dict:
    """执行审查迭代 — 审查迭代质量、项目进展、阻塞项"""
    result = {
        "type": "review",
        "action": "iteration_quality_review",
        "success": True,
        "findings": [],
        "quality_metrics": {},
    }

    # Review last 5 iteration files for content quality
    existing_iters = sorted(ITERATIONS_DIR.glob("iteration-*.md"))
    recent = existing_iters[-5:] if len(existing_iters) >= 5 else existing_iters

    if recent:
        total_lines = 0
        types_seen = set()
        has_findings = 0
        has_empty_findings = 0

        for it_file in recent:
            content = it_file.read_text()
            lines = len(content.strip().split("\n"))
            total_lines += lines
            types_seen.add(content.split("type:")[1].strip().split("\n")[0].strip() if "type:" in content else "unknown")

            if "Findings" in content:
                findings_section = content.split("## Findings")[1] if "## Findings" in content else ""
                finding_items = [l for l in findings_section.split("\n") if l.strip().startswith("- ")]
                if finding_items:
                    has_findings += 1
                else:
                    has_empty_findings += 1
            else:
                has_empty_findings += 1

        avg_lines = total_lines / len(recent)
        result["quality_metrics"]["avg_lines_per_iter"] = avg_lines
        result["quality_metrics"]["types_in_rotation"] = list(types_seen)

        if has_empty_findings > 0:
            result["findings"].append(f"⚠ {has_empty_findings}/{len(recent)} recent iterations have empty/missing findings — quality concern")

        if avg_lines < 10:
            result["findings"].append(f"⚠ Low content in recent iterations (avg {avg_lines:.0f} lines) — may indicate no-op runs")

        result["findings"].append(f"Last {len(recent)} iterations avg {avg_lines:.0f} lines, covering types: {', '.join(types_seen)}")
    else:
        result["findings"].append("No iteration files found for review")

    # Check for long-stale projects (>14 days)
    projects_dir = WORKSPACE / "projects"
    if projects_dir.exists():
        stale_threshold = datetime.now() - __import__("datetime").timedelta(days=14)
        very_stale = []
        for entry in sorted(projects_dir.iterdir()):
            if entry.is_dir() and entry.name.startswith("D1-"):
                latest = max((f.stat().st_mtime for f in entry.rglob("*")), default=0)
                latest_dt = datetime.fromtimestamp(latest)
                if latest_dt < stale_threshold:
                    days = (datetime.now() - latest_dt).days
                    very_stale.append(f"{entry.name} ({days}d stale)")
        if very_stale:
            result["findings"].append(f"⚠ Long-stale projects (>14d): {'; '.join(very_stale)}")
        else:
            result["findings"].append("No projects stale beyond 14 days")

    return result


def run_cleanup_iteration(state: dict) -> dict:
    """执行清理迭代 — 清理临时文件、检查冗余"""
    result = {
        "type": "cleanup",
        "action": "cleanup_scan",
        "success": True,
        "findings": [],
        "actions": [],
    }

    # Check for .bak files
    bak_files = list(WORKSPACE.rglob("*.bak"))
    if bak_files:
        bak_size = sum(f.stat().st_size for f in bak_files)
        result["findings"].append(f".bak files: {len(bak_files)} total, {bak_size / 1024:.1f} KB")
    else:
        result["findings"].append("No .bak files found")

    # Check for .tmp files
    tmp_files = list(WORKSPACE.rglob("*.tmp"))
    if tmp_files:
        tmp_size = sum(f.stat().st_size for f in tmp_files)
        result["findings"].append(f".tmp files: {len(tmp_files)} total, {tmp_size / 1024:.1f} KB")
    else:
        result["findings"].append("No .tmp files found")

    # Check for empty directories in projects
    empty_dirs = []
    projects_dir = WORKSPACE / "projects"
    if projects_dir.exists():
        for proj in projects_dir.iterdir():
            if proj.is_dir() and proj.name.startswith("D1-"):
                contents = list(proj.rglob("*"))
                if not contents:
                    empty_dirs.append(proj.name)

    if empty_dirs:
        result["findings"].append(f"Empty project dirs: {', '.join(empty_dirs)}")
    else:
        result["findings"].append("No empty project directories")

    # Check .ralph/backups count
    backup_dir = WORKSPACE / ".ralph" / "backups"
    if backup_dir.exists():
        backup_files = list(backup_dir.iterdir())
        if len(backup_files) > 30:
            result["findings"].append(f"⚠ Backup files accumulated: {len(backup_files)} — consider pruning (>30)")
        else:
            result["findings"].append(f"Backup files: {len(backup_files)} (within limits)")

    # Check for orphans — project dirs with no corresponding tasks or output
    if projects_dir.exists():
        for proj in projects_dir.iterdir():
            if proj.is_dir() and proj.name.startswith("D1-"):
                latest = max((f.stat().st_mtime for f in proj.rglob("*")), default=0)
                days_stale = (datetime.now() - datetime.fromtimestamp(latest)).days
                if days_stale > 21:
                    result["findings"].append(f"⚠ Project {proj.name} is {days_stale} days stale — consider cleanup or reactivation")

    if not [f for f in result["findings"] if "⚠" in f]:
        result["findings"].append("No cleanup actions needed — workspace is healthy")

    return result


def run_iteration() -> None:
    """运行一次迭代（核心逻辑）"""
    ITERATIONS_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state()
    create_backup()

    # Increment iteration counter
    state["iteration"] = state.get("iteration", 0) + 1
    state["total_iterations"] = state.get("total_iterations", 0) + 1
    state["status"] = "running"
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    current_iter = state["iteration"]

    # Determine iteration type
    iter_types = list(ITERATION_TYPES.keys())
    current_type = iter_types[(current_iter - 1) % len(iter_types)]
    state["current_type"] = current_type

    print(f"=== Iteration {current_iter} [{ITERATION_TYPES.get(current_type, '?')}] ===")

    try:
        # Execute appropriate iteration type
        if current_type == "research":
            result = run_research_iteration(state)
        elif current_type == "audit":
            result = run_audit_iteration(state)
        elif current_type == "infra":
            result = run_infra_iteration(state)
        elif current_type == "review":
            result = run_review_iteration(state)
        elif current_type == "cleanup":
            result = run_cleanup_iteration(state)
        else:
            result = {"type": current_type, "success": True, "findings": [f"No implementation for {current_type}"]}

        if result.get("success"):
            state["successful_iterations"] = state.get("successful_iterations", 0) + 1
            state["last_result"] = {"status": "success", "type": current_type}
        else:
            state["last_result"] = {"status": "failed", "type": current_type}

    except Exception as e:
        state["last_result"] = {"status": "error", "type": current_type, "error": str(e)[:500]}
        print(f"ERROR: {e}", file=sys.stderr)
    
    # Build last_run_details for state.json
    ws = scan_workspace()
    findings_summary = "; ".join(result.get("findings", [])[:3])
    last_run_details = {
        "timestamp": datetime.now().isoformat(),
        "description": f"Iteration {current_iter}: {ITERATION_TYPES.get(current_type, '?')}. "
                       f"Projects: {ws.get('project_count', 0)}, Files: {ws.get('total_files', 0)}. "
                       f"{findings_summary}",
        "findings": result.get("findings", []),
    }

    # Write iteration report
    lines = [
        f"---",
        f"iteration: {current_iter}",
        f"started_at: {state['last_run']}",
        f"type: {ITERATION_TYPES.get(current_type, '?')}",
        f"total: {state['total_iterations']}",
        f"successful: {state['successful_iterations']}",
        f"---",
        f"",
        f"# Iteration {current_iter}",
        f"",
        f"**Type**: {ITERATION_TYPES.get(current_type, '?')} ({current_type})",
        f"",
    ]

    # Add workspace scan summary
    lines.append(f"## Workspace Summary")
    lines.append(f"- Projects: {ws.get('project_count', 0)}")
    lines.append(f"- Total files: {ws.get('total_files', 0)}")
    for proj, ts in ws.get('last_updates', {}).items():
        lines.append(f"- {proj}: last updated {ts}")

    lines.append(f"")
    lines.append(f"## Result")
    for k, v in result.items():
        lines.append(f"- **{k}**: {v}")

    # Add stale project warnings
    if result.get("findings"):
        lines.append(f"")
        lines.append(f"## Findings")
        for f in result["findings"]:
            lines.append(f"- {f}")

    lines.append(f"")
    report_content = "\n".join(lines)

    report_file = ITERATIONS_DIR / f"iteration-{current_iter}.md"
    report_file.write_text(report_content)

    # Update state with last_run_details and success_count for dashboard compatibility
    state["last_run_details"] = last_run_details
    state["success_count"] = state["successful_iterations"]

    save_state(state)
    
    print(f"Iteration {current_iter} complete. Success rate: {state['successful_iterations']}/{state['total_iterations']}")
    print(f"State: {state['iteration']} iters, {state['successful_iterations']}/success")


def show_status() -> None:
    """显示当前状态"""
    if not STATE_FILE.exists():
        print("No state file found. Run 'iteration.py run' first.")
        return
    
    state = load_state()
    print(f"=== Unified Iteration Status ===")
    print(f"Current iteration: {state.get('iteration', 0)}")
    print(f"Total iterations: {state.get('total_iterations', 0)}")
    print(f"Successful: {state.get('successful_iterations', 0)}")
    print(f"Status: {state.get('status', 'unknown')}")
    print(f"Current type: {state.get('current_type', '?')}")
    print(f"Last run: {state.get('last_run', 'never')}")
    
    # Show iteration history
    iter_dir = ITERATIONS_DIR
    if iter_dir.exists():
        iters = sorted(iter_dir.glob("iteration-*.md"))
        print(f"\nIteration files: {len(iters)}")
        for it in iters[-5:]:  # Last 5
            print(f"  {it.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: unified_iteration.py [run|status|reset]")
        print("  run    - Run one iteration")
        print("  status - Show current status")
        print("  reset  - Reset iteration counter")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        run_iteration()
    elif cmd == "status":
        show_status()
    elif cmd == "reset":
        if STATE_FILE.exists():
            state = load_state()
            state["iteration"] = 0
            state["total_iterations"] = 0
            state["successful_iterations"] = 0
            state["status"] = "idle"
            save_state(state)
            print("State reset. Iteration counter cleared.")
        else:
            print("No state file to reset.")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
