#!/usr/bin/env python3
"""persona-v3 评估工具链回归测试。

用法:
    python3 regression_test.py              # 运行所有编译测试
    python3 regression_test.py --full       # 运行完整测试 (含运行时)
"""

import subprocess
import sys

TOOLS = [
    "persona_keywords.py",
    "persona_v3_gap_filler_v2.py",
    "unified_eval.py",
    "chameleon_collapse_detector.py",
    "emptrajectory_eval.py",
    "sync_personality.py",
    "section_alignment_test.py",
    "cross_dim_ortho.py",
    "test_time_optimize.py",
    "integration_test.py",
]

def compile_test():
    """测试所有工具能正确编译。"""
    print("=== 编译测试 ===")
    all_pass = True
    for tool in TOOLS:
        path = f"scripts/{tool}"
        result = subprocess.run(
            [sys.executable, "-c", f'import py_compile; py_compile.compile("{path}", doraise=True)'],
            capture_output=True, text=True
        )
        status = "[OK]" if result.returncode == 0 else "[FAIL]"
        print(f"  {status} {tool}")
        if result.returncode != 0:
            all_pass = False
    return all_pass


def runtime_test():
    """运行时测试 — 各工具实际运行。"""
    print("\n=== 运行时测试 ===")

    # persona_keywords
    result = subprocess.run(
        [sys.executable, "-c",
         "from persona_keywords import compute_dimension_scores; print(compute_dimension_scores('测试'))"],
        capture_output=True, text=True, cwd="scripts"
    )
    status = "[OK]" if result.returncode == 0 else "[FAIL]"
    print(f"  {status} persona_keywords compute_dimension_scores")

    # chameleon
    result = subprocess.run(
        [sys.executable, "chameleon_collapse_detector.py", "--test"],
        capture_output=True, text=True, cwd="scripts"
    )
    status = "[OK]" if result.returncode == 0 else "[FAIL]"
    print(f"  {status} chameleon --test")

    # unified_eval prompt
    result = subprocess.run(
        [sys.executable, "unified_eval.py", "--prompt"],
        capture_output=True, text=True, cwd="scripts"
    )
    status = "[OK]" if result.returncode == 0 else "[FAIL]"
    print(f"  {status} unified_eval --prompt")

    return True


def main():
    compile_ok = compile_test()

    full = "--full" in sys.argv
    if full:
        runtime_ok = runtime_test()
        compile_ok = compile_ok and runtime_ok

    print()
    if compile_ok:
        print("=== 所有回归测试通过 ===")
    else:
        print("=== 部分测试失败 ===")
    return 0 if compile_ok else 1


if __name__ == "__main__":
    sys.exit(main())
