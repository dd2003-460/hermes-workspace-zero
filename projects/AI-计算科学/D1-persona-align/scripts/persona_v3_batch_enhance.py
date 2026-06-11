#!/usr/bin/env python3
"""
persona-v3 批量增强脚本

批量对优先级修复列表中的文件运行 gap_filler --apply。
输出报告: 哪些文件成功增强, 增强前后分数对比。

用法:
    python3 persona_v3_batch_enhance.py --all              # 增强所有 idea 分析
    python3 persona_v3_batch_enhance.py --top N             # 增强最弱 N 个文件
    python3 persona_v3_batch_enhance.py --file memory/xxx.md # 增强指定文件
    python3 persona_v3_batch_enhance.py --json              # JSON 输出
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
GAP_FILLER = SCRIPTS_DIR / "persona_v3_gap_filler.py"
CHECKER = SCRIPTS_DIR / "persona_v3_alignment_checker.py"


def run_gap_filler(file_path, persist=False):
    """运行 gap_filler --apply 并返回结果。"""
    cmd = [sys.executable, str(GAP_FILLER), "--file", str(file_path), "--apply"]
    if persist:
        cmd.append("--persist")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if persist:
        # With --persist, the original file IS the enhanced file
        enhanced_exists = True
    else:
        enhanced_path = str(file_path).replace(".md", "-enhanced.md")
        enhanced_exists = Path(enhanced_path).exists()
    return {
        "file": str(file_path),
        "original_text": file_path.read_text(encoding="utf-8"),
        "enhanced_exists": enhanced_exists,
        "stdout": result.stdout[-500:] if not result.stdout[:100].strip() else result.stdout[:500],
        "stderr": result.stderr[-200:] if result.stderr and not enhanced_exists else "",
        "returncode": result.returncode,
    }


def run_checker(file_path):
    """运行 alignment_checker 并返回分数。"""
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--json", str(file_path)],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return {
            "score": data.get("alignment_score", -1),
            "behavioral_overall": data.get("behavioral_overall", -1),
        }
    except json.JSONDecodeError:
        return {"score": -1, "behavioral_overall": -1}


def enhance_file(file_path, persist=False):
    """增强单个文件并返回结果。"""
    file_path = Path(file_path)

    # Original score (before enhancement)
    orig = run_checker(file_path)

    # Enhance
    enhance_result = run_gap_filler(file_path, persist=persist)

    if not enhance_result["enhanced_exists"]:
        return {
            "file": file_path.name,
            "original_score": orig["score"],
            "enhanced_score": orig["score"],
            "improvement": 0,
            "enhanced_exists": False,
            "error": "gap_filler did not generate enhanced file",
        }

    if persist:
        # Original file was overwritten
        enhanced = run_checker(file_path)
    else:
        enhanced_path = Path(file_path).parent / (Path(file_path).stem + "-enhanced.md")
        enhanced = run_checker(enhanced_path)
        enhanced_path.unlink(missing_ok=True)

    return {
        "file": file_path.name,
        "original_score": orig["score"],
        "enhanced_score": enhanced["score"],
        "improvement": round(enhanced["score"] - orig["score"], 2),
        "enhanced_exists": True,
    }


def main():
    parser = argparse.ArgumentParser(description="persona-v3 批量增强工具")
    parser.add_argument("--all", action="store_true", help="增强所有 idea 分析文件")
    parser.add_argument("--top", type=int, help="增强最弱 N 个文件")
    parser.add_argument("--file", help="增强指定文件")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--baseline", help="使用 baseline 确定最弱文件")
    parser.add_argument("--persist", action="store_true", help="保留增强文件（默认仅验证后删除）")

    args = parser.parse_args()

    if not any([args.all, args.top, args.file]):
        parser.print_help()
        sys.exit(1)

    results = []

    if args.file:
        results.append(enhance_file(args.file, persist=args.persist))

    elif args.all:
        memory_dir = Path("memory")
        files = sorted(memory_dir.glob("idea-*.md"))
        for f in files:
            results.append(enhance_file(f, persist=args.persist))
        enhanced_count = sum(1 for r in results if r["enhanced_exists"])
        for r in results:
            if r["enhanced_exists"]:
                print(f"  [ENHANCED] {r['file']}", file=sys.stderr)
            else:
                print(f"  [SKIP] {r['file']}", file=sys.stderr)
        print(f"\n  Batch complete: {enhanced_count}/{len(files)} enhanced", file=sys.stderr)

    elif args.top:
        # Get dashboard to find weakest files
        if args.baseline:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "persona_v3_dashboard.py"),
                 "--json", "--top", str(args.top), "--baseline", args.baseline],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "persona_v3_dashboard.py"),
                 "--json", "--top", str(args.top)],
                capture_output=True, text=True
            )

        try:
            weak_files = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("Failed to parse dashboard output", file=sys.stderr)
            sys.exit(1)

        for f_info in weak_files:
            file_path = f_info["file"]
            if Path(file_path).exists():
                results.append(enhance_file(file_path, persist=args.persist))
                print(f"  [ENHANCED] {Path(file_path).name}", file=sys.stderr)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("  Batch Enhancement Report")
        print("=" * 60)
        enhanced_count = sum(1 for r in results if r["enhanced_exists"])
        avg_improvement = sum(r["improvement"] for r in results if r["enhanced_exists"]) / max(enhanced_count, 1)
        print(f"  Total: {len(results)}, Enhanced: {enhanced_count}, Avg improvement: {avg_improvement:.1f}")
        print()
        for r in results:
            flag = "+" if r["enhanced_exists"] else " "
            print(f"  [{flag}] {r['file'][:50]}: {r['original_score']:.1f} -> {r['enhanced_score']:.1f} ({r['improvement']:+.1f})")

    return results


if __name__ == "__main__":
    main()
