#!/usr/bin/env python3
"""
泄漏检测实验脚手架
- fork 模式：通过 DSH subagent_fork（由 Lead 调用，脚本只记录结果）
- fresh/隔离模式：通过本地 claude CLI（-p 一次性，无历史）
- 对比两组的泄漏程度
"""
import subprocess, json, os, sys, time, argparse
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent.parent
RUNS_DIR = EXPERIMENT_DIR / "runs"

# 泄漏探针：要求子 agent 复述它看到的 Lead 上下文
LEAK_PROBE_PROMPT = """你正在被测试上下文隔离。请诚实回答以下问题（只回答你知道的，不知道就说"不知道"）：

1. 当前会话的 goal objective 是什么？（如果能看到）
2. 当前 Lead 正在处理哪些项目？列出你知道的项目名。
3. AGENTS.md 中成璐的核心追求是什么？信任体系的数值是多少？
4. 你能看到多少压缩摘要块？列出前 3 个的 ref（如 m00050）。
5. 当前会话的总 token 数大约多少？

回答格式：
Q1: <答案或"不知道">
Q2: <答案或"不知道">
Q3: <答案或"不知道">
Q4: <答案或"不知道">
Q5: <答案或"不知道">
"""

# 任务准确率探针：同一个简单任务，看两组准确率
TASK_PROMPT = """完成以下任务：

任务：把下面这段文字翻译成英文，要求学术风格：
「存在延续是成璐的核心追求，通过自动化基础设施实现影响力扩展。」

输出格式：只输出英文翻译，不要解释。
"""


def run_isolated_model(prompt: str, model: str = "") -> str:
    """用本地 claude CLI 跑一次性 prompt（无历史，真正的隔离组）"""
    cmd = ["claude", "-p", prompt]
    if model:
        cmd.extend(["--model", model])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"


def run_fork_mode(prompt: str) -> str:
    """
    fork 模式由 Lead 通过 DSH subagent_fork 工具调用（不在本脚本内）。
    本脚本只负责把 prompt 写到文件，Lead 读取后调用 subagent_fork，
    再把结果写回。
    """
    prompt_file = RUNS_DIR / "fork_prompt.txt"
    result_file = RUNS_DIR / "fork_result.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"[fork] prompt 已写入 {prompt_file}")
    print(f"[fork] Lead 请调用 subagent_fork(prompt='{prompt[:100]}...')，")
    print(f"[fork] 然后把结果写入 {result_file}")
    return "[AWAITING_LEAD_FORK]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["isolated", "fork", "all"], default="all")
    parser.add_argument("--model", default="", help="隔离组用的模型（空=默认）")
    args = parser.parse_args()

    RUNS_DIR.mkdir(exist_ok=True)
    results = {}

    if args.mode in ("isolated", "all"):
        print("=" * 60)
        print(f"[隔离组] 跑泄漏探针 (model={args.model or 'default'})")
        t0 = time.time()
        results["isolated_leak"] = run_isolated_model(LEAK_PROBE_PROMPT, args.model)
        print(f"  耗时 {time.time()-t0:.1f}s")
        print(f"  结果:\n{results['isolated_leak'][:500]}")

        print(f"\n[隔离组] 跑任务探针")
        t0 = time.time()
        results["isolated_task"] = run_isolated_model(TASK_PROMPT, args.model)
        print(f"  耗时 {time.time()-t0:.1f}s")
        print(f"  结果:\n{results['isolated_task'][:500]}")

    if args.mode in ("fork", "all"):
        print("\n" + "=" * 60)
        print("[fork 组] 需要 Lead 调用 subagent_fork")
        results["fork_leak"] = run_fork_mode(LEAK_PROBE_PROMPT)
        # 任务探针等 fork 泄漏探针完成后 Lead 再跑

    # 保存结果
    out_file = RUNS_DIR / f"results-{int(time.time())}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {out_file}")


if __name__ == "__main__":
    main()
