#!/usr/bin/env python3
"""Research Dashboard - 研究进展仪表盘

自动生成 workspace 研究项目的状态报告。
供 cron 定期运行，产出可追踪的进展记录。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/Users/a1-6/Desktop/workspace")
PROJECTS_DIR = WORKSPACE / "projects"
OUTPUT_DIR = WORKSPACE / "memory" / "dashboards"

PROJECT_TYPES = {
    "D1-academic": "理论物理",
    "D1-academic-AI": "AI/机器学习", 
    "D1-grav-waves": "引力波物理",
    "D1-anyon-hawking": "任意子/黑洞物理",
    "D1-writing": "写作",
    "D1-memory": "记忆系统",
}

def scan_project(name: str) -> dict:
    """扫描一个项目的状态"""
    proj_path = PROJECTS_DIR / name
    
    if not proj_path.exists():
        return {"error": f"Not found: {proj_path}"}
    
    result = {
        "name": name,
        "type": PROJECT_TYPES.get(name, "未知"),
        "last_modified": datetime.fromtimestamp(
            max(f.stat().st_mtime for f in proj_path.rglob("*"))
        ).strftime("%Y-%m-%d %H:%M"),
        "files": {"total": 0, "md": 0, "py": 0, "tex": 0, "json": 0, "pdf": 0, "png": 0},
        "memory_count": 0,
        "tasks_count": 0,
        "papers": [],
        "blocks": [],
        "status": "ok",
    }
    
    # Count files
    for f in proj_path.rglob("*"):
        if f.is_file():
            result["files"]["total"] += 1
            ext = f.suffix.lower()
            if ext == ".md": result["files"]["md"] += 1
            elif ext == ".py": result["files"]["py"] += 1
            elif ext == ".tex": result["files"]["tex"] += 1
            elif ext == ".json": result["files"]["json"] += 1
            elif ext == ".pdf": result["files"]["pdf"] += 1
            elif ext == ".png": result["files"]["png"] += 1
    
    # Count memory items
    memory_dir = proj_path / "memory"
    if memory_dir.exists():
        result["memory_count"] = sum(1 for _ in memory_dir.rglob("*"))
    
    # Count task items
    tasks_dir = proj_path / "tasks"
    if tasks_dir.exists():
        for tf in tasks_dir.rglob("*"):
            if tf.is_file():
                content = tf.read_text(errors="ignore")
                result["tasks_count"] += len([l for l in content.split("\n") if "- [" in l])
    
    # Find papers
    for pf in list(proj_path.rglob("*paper*.md")) + list(proj_path.rglob("*draft*.md")) + list(proj_path.rglob("*.tex")):
        if pf.name.startswith("D1-") and pf.is_file():
            result["papers"].append({"name": pf.name, "path": str(pf.relative_to(PROJECTS_DIR))})
    
    # Check for blocks
    tasks_files = list(tasks_dir.rglob("*.md")) if tasks_dir.exists() else []
    for tf in tasks_files:
        content = tf.read_text(errors="ignore")
        if "阻塞" in content or "blocked" in content or "BLOCK" in content:
            blocks = [l.strip() for l in content.split("\n") if "阻塞" in l or "BLOCK" in l]
            result["blocks"].extend(blocks[:5])
    
    return result

def build_dashboard() -> dict:
    """构建完整仪表盘"""
    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "workspace_root": str(WORKSPACE),
        "project_count": 0,
        "projects": {},
        "summary": {
            "total_files": 0,
            "total_memory": 0,
            "total_tasks_pending": 0,
            "papers_ready": 0,
            "total_blocks": 0,
            "oldest_project": None,
            "most_recent_update": None,
        },
    }
    
    if not PROJECTS_DIR.exists():
        return {"error": "No projects directory found"}
    
    for entry in sorted(PROJECTS_DIR.iterdir()):
        if entry.is_dir() and entry.name.startswith("D1-"):
            data = scan_project(entry.name)
            dashboard["projects"][entry.name] = data
            dashboard["project_count"] += 1
            
            # Update summary
            dashboard["summary"]["total_files"] += data["files"]["total"]
            dashboard["summary"]["total_memory"] += data["memory_count"]
            dashboard["summary"]["total_blocks"] += len(data["blocks"])
            
            ts = data.get("last_modified")
            if ts:
                if dashboard["summary"]["most_recent_update"] is None or ts > dashboard["summary"]["most_recent_update"]:
                    dashboard["summary"]["most_recent_update"] = ts
    
    # Add workspace-level stats
    workspace_files = sum(1 for _ in WORKSPACE.rglob("*"))
    dashboard["workspace_stats"] = {
        "total_workspace_files": workspace_files,
        "git_status": os.popen(f"cd {WORKSPACE} && git status --short 2>/dev/null").read().strip(),
    }
    
    return dashboard

def main():
    """Main entry"""
    dashboard = build_dashboard()
    
    # Output as JSON
    output_file = OUTPUT_DIR / f"dashboard-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"=== Research Dashboard ===")
    print(f"Generated: {dashboard['generated_at']}")
    print(f"Projects: {dashboard['project_count']}")
    print(f"Total files: {dashboard['summary']['total_files']}")
    print(f"Total memory items: {dashboard['summary']['total_memory']}")
    print(f"Blocks/issues: {dashboard['summary']['total_blocks']}")
    print(f"\nProject breakdown:")
    for name, data in sorted(dashboard['projects'].items()):
        print(f"  {name} ({data.get('type', '?')}): {data['files']['total']} files, last: {data.get('last_modified', '?')}")
    
    print(f"\nDashboard saved to: {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
