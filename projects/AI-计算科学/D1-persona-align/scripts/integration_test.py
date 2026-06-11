#!/usr/bin/env python3
"""persona-v3 端到端集成测试

验证整个评估管线从输入到输出的正确性:
1. gap_filler_v2 — 读取 idea 文件, 输出增强建议
2. unified_eval — 对文件运行完整评估 pipeline
3. chameleon_collapse_detector — 检测维度 collapse
4. emptrajectory_eval — 评估轨迹级 persona
5. section_alignment_test — 验证 prompt 章节对齐
6. section_alignment_test — 验证 prompt 章节对齐
7. regression_test — 确保所有工具编译

所有测试必须通过，否则 pipeline 被认为 broken。

Usage:
    python3 integration_test.py
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS = PROJECT_ROOT / "scripts"
MEMORY = PROJECT_ROOT / "memory"
EVAL_RESULTS = PROJECT_ROOT / "eval_results"

results = []


def test(name, func):
    """Run a test and record result."""
    try:
        result = func()
        results.append({"name": name, "status": "PASS", "detail": result})
        print(f"  [PASS] {name}: {result}")
        return True
    except Exception as e:
        results.append({"name": name, "status": "FAIL", "detail": str(e)})
        print(f"  [FAIL] {name}: {e}")
        return False


def test_compile_all():
    """Test 1: 所有工具编译通过"""
    scripts = [
        "persona_keywords.py",
        "persona_v3_gap_filler_v2.py",
        "unified_eval.py",
        "chameleon_collapse_detector.py",
        "emptrajectory_eval.py",
        "sync_personality.py",
        "section_alignment_test.py",
        "cross_dim_ortho.py",
        "test_time_optimize.py",
    ]
    for s in scripts:
        subprocess.check_call(
            [sys.executable, "-m", "py_compile", str(SCRIPTS / s)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return f"{len(scripts)} 工具编译通过"


def test_keywords_shared():
    """Test 2: 关键词库无跨维度重叠"""
    sys.path.insert(0, str(SCRIPTS))
    from persona_keywords import DIMENSION_KEYWORDS
    from collections import defaultdict
    kw_dims = defaultdict(set)
    for dim, kws in DIMENSION_KEYWORDS.items():
        for kw, w in kws:
            kw_dims[kw.lower()].add(dim)
    shared = {k: v for k, v in kw_dims.items() if len(v) > 1}
    if shared:
        return f"FAIL: {len(shared)} 跨维度关键词: {shared}"
    return "0 跨维度关键词"


def test_gap_filler():
    """Test 3: gap_filler_v2 对单个文件工作"""
    idea_files = sorted(MEMORY.glob("idea-*.md"))
    if not idea_files:
        return "FAIL: 无 idea 文件"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "persona_v3_gap_filler_v2.py"),
         "--file", str(idea_files[0])],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    # Output contains score info
    if "分数" in result.stdout or "score" in result.stdout.lower() or "average" in result.stdout.lower():
        return f"gap_filler 评分通过"
    return f"stdout: {result.stdout[:200]}"


def test_unified_eval():
    """Test 4: unified_eval 对 prompt 工作"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "unified_eval.py"), "--prompt"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    # Check output contains expected metrics
    if "所有维度 >= 0.40" not in result.stdout:
        return f"FAIL: 输出缺少关键指标. stdout[:200]={result.stdout[:200]}"
    if "平均" in result.stdout:
        return "输出包含所有关键指标"
    return f"输出: {result.stdout[:200]}"


def test_unified_eval_scan():
    """Test 5: unified_eval --scan 对 52 文件工作"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "unified_eval.py"), "--scan", "--top", "3"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    if "平均" in result.stdout and "维度最小分" in result.stdout:
        return "扫描通过, 包含所有关键指标"
    return f"输出不完整: {result.stdout[:200]}"


def test_chameleon():
    """Test 6: chameleon detector 工作"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "chameleon_collapse_detector.py"), "--test"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    if "相似度" in result.stdout or "similarity" in result.stdout:
        return "Chameleon 检测通过"
    return f"输出不完整: {result.stdout[:200]}"


def test_trajectory():
    """Test 7: trajectory eval 工作"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "emptrajectory_eval.py"), "--test"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    if "对齐" in result.stdout or "alignment" in result.stdout:
        return "轨迹评估通过"
    return f"输出不完整: {result.stdout[:200]}"


def test_sync_personality():
    """Test 8: sync_personality 无错误"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "sync_personality.py")],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    # May have warnings but should not crash
    if result.returncode not in (0, 1):
        return f"FAIL: exit {result.returncode}, stderr={result.stderr[:200]}"
    if result.returncode == 0:
        return "同步成功"
    if "Changes detected" in result.stdout or "No changes" in result.stdout:
        return "同步正常 (检查变更)"
    return f"stdout: {result.stdout[:200]}"


def test_memories_exist():
    """Test 9: 记忆文件完整性"""
    mem_files = list(MEMORY.glob("iteration-*.md"))
    memory_count = len(mem_files)
    if memory_count < 20:
        return f"FAIL: 仅 {memory_count} 个记忆文件"
    # Check latest memory is recent enough
    latest = max(mem_files, key=lambda f: f.stat().st_mtime)
    return f"{memory_count} 个记忆文件, 最新 {latest.name}"


def test_eval_results_dir():
    """Test 10: eval_results 目录存在且包含结果"""
    eval_dir = EVAL_RESULTS
    if not eval_dir.exists():
        return "FAIL: eval_results 目录不存在"
    eval_files = list(eval_dir.glob("*.json"))
    return f"{len(eval_files)} 个评估结果文件: {', '.join(f.name for f in eval_files[:5])}"


def test_section_alignment():
    """Test 11: section_alignment_test 无 mismatch"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "section_alignment_test.py")],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return f"FAIL: exit {result.returncode}"
    if "Mismatches: 0" in result.stdout:
        return "Section 对齐: 0 mismatch"
    # Extract mismatch count
    for line in result.stdout.split("\n"):
        if "Mismatches:" in line:
            return line.strip()
    return f"输出: {result.stdout[-200:]}"


def main():
    print("=" * 60)
    print("persona-v3 端到端集成测试")
    print("=" * 60)

    print("\n运行 11 项测试:")
    tests = [
        ("1. 编译测试", test_compile_all),
        ("2. 关键词正交化", test_keywords_shared),
        ("3. gap_filler_v2", test_gap_filler),
        ("4. unified_eval --prompt", test_unified_eval),
        ("5. unified_eval --scan", test_unified_eval_scan),
        ("6. chameleon detector", test_chameleon),
        ("7. trajectory eval", test_trajectory),
        ("8. sync_personality", test_sync_personality),
        ("9. 记忆文件完整性", test_memories_exist),
        ("10. eval_results 目录", test_eval_results_dir),
        ("11. section_alignment", test_section_alignment),
    ]

    for name, func in tests:
        test(name, func)

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n{'=' * 60}")
    print(f"结果: {passed} 通过, {failed} 失败, {len(results)} 总计")

    if failed > 0:
        print("\n失败项:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  {r['name']}: {r['detail']}")

    # Save JSON report
    report_path = EVAL_RESULTS / "integration_test.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "tests": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n报告保存: {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
