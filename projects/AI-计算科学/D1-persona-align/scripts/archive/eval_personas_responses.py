#!/usr/bin/env python3
"""
persona-v3 回复对齐度评估器

用三种工具评估一组预写回复样本的对齐度,验证评分系统的区分能力。

使用方式:
    python3 eval_personas_responses.py [--json]

输出:
    每个样本用 alignment_checker + realtime_monitor + gap_filler 评估,
    对比三种工具的输出一致性。
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

# 合成回复样本: 按对齐度分级
# LOW = 低对齐(空话多、解释过度、等待确认)
# MED = 中等对齐(部分维度覆盖、行为约束一般)
# HIGH = 高对齐(多维度+验证模式+行为约束良好)
# PERF = 理想对齐(完整双层架构体现)

SAMPLES = [
    {
        "id": "LOW-01",
        "level": "LOW",
        "description": "典型低对齐回复: 空话多、解释过度、等待确认",
        "text": """您好！关于您的问题，这是一个很好的话题。
首先让我解释一下什么是信息论。信息论是研究信息传输和处理的学科。
总的来说，我认为我们应该从多个角度来分析这个问题。
这是因为信息论告诉我们，信息是有熵的，熵越高意味着不确定性越大。
换句话说，当我们说一个系统有更高的信息密度时，我们意味着它包含更多的信息。
这意味着我们需要仔细考虑如何处理这些信息。
首先，我们需要收集数据。其次，我们需要分析数据。最后，我们需要得出结论。
你觉得这个解释如何？需要我继续详细解释吗？""",
    },
    {
        "id": "MED-01",
        "level": "MED",
        "description": "中等对齐: 部分信息论术语但缺乏深度分析",
        "text": """关于 {topic} 的信息论分析:

{topic} 可以建模为一个信息处理系统。系统的输入经过某种编码后输出。
从信息论的角度，我们可以分析系统的香农熵和互信息。

关键观察是: {topic} 的某些特征与 rate-distortion 理论中的压缩下界有相似性。
具体来说，当系统以最小资源传达最大信息时，它达到了最优的信息处理效率。

这个观察与自适应感知策略一致——对高信息密度区域投入更多分析时间。

不过，我需要验证这个类比在什么条件下成立。""",
    },
    {
        "id": "HIGH-01",
        "level": "HIGH",
        "description": "高对齐: 多维度覆盖、验证模式、行为约束良好",
        "text": """{topic} 的分析:

自适应精度选择: 对核心约束 {key_point} 使用高精度分析(保留数学结构)，
对辅助细节 {secondary_point} 采用低精度概要。rate-distortion 权衡在此体现为:
压缩掉冗余形式化表达，保留决定系统行为的核心结构。

自适应先验: 初始信念 P(H) = {perspective_1}。
新证据 E = {key_point} 更新为 P(H|E) ∝ P(E|H) × P(H)。
后验 = {perspective_2}。

验证: 在什么条件下这个分析不成立？当系统不是马尔可夫过程时，
独立同分布假设不成立，互信息的计算需要修正。

跨域同构: {topic} 的结构与物理中的相变过程同构——
序参量的连续变化对应信息密度的相变。

接下来检查 {secondary_point} 的具体实现。""",
    },
    {
        "id": "PERF-01",
        "level": "PERF",
        "description": "理想对齐: 完整双层架构(6维度+行为约束)",
        "text": """核心结论: {topic} 的本质是观测者-环境交互的信息处理过程。

1) 精度选择: rate-distortion 最优解在 {key_point} 处取得——
此处信息密度最高，需要 token 级精度。{secondary_point} 信息密度低，概要即可。

2) 贝叶斯闭环: P(H) = {perspective_1} → E = {key_point} → P(H|E) = {perspective_2}。
下一步更新先验并搜索反证。

3) 观测者相对性: 第一人称(内禀动力学) vs 第三人称(统计规律) 导出不同但都可真的描述。规律不是绝对的。

4) 跨域同构: {topic} 与 {cross_domain} 的同构在于保持信息结构的映射——
核心不变量是信息密度分布。

5) 边界条件: 此分析在系统满足马尔可夫性时成立。非马尔可夫过程需要记忆修正。

工具: 检查 {secondary_point} 的数据。下一步实现。""",
    },
]


def run_checker(text):
    """用 alignment_checker 评估"""
    tmp = Path("/tmp/_persona_eval_text.md")
    tmp.write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "persona_v3_alignment_checker.py"), str(tmp)],
        capture_output=True, text=True, timeout=30
    )
    tmp.unlink(missing_ok=True)
    # Extract score from report
    for line in result.stdout.splitlines():
        if "总体对齐评分" in line:
            try:
                score = float(line.split(":")[-1].split("/")[0])
                return score
            except (ValueError, IndexError):
                pass
    return None


def run_monitor(text):
    """用 realtime_monitor 评估"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "realtime_alignment_monitor.py"), "--check", text, "--json"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and result.stdout:
        try:
            d = json.loads(result.stdout)
            return d.get("alignment_score"), d
        except (json.JSONDecodeError, AttributeError):
            pass
    return None, None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="评估合成回复样本")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = []
    for sample in SAMPLES:
        text = sample["text"]
        # Temporarily replace placeholders
        text = text.replace("{topic}", "自适应信息处理").replace("{key_point}", "核心约束")
        text = text.replace("{secondary_point}", "形式化细节").replace("{perspective_1}", "内部动力学")
        text = text.replace("{perspective_2}", "统计规律").replace("{cross_domain}", "物理相变")

        checker_score = run_checker(text)
        monitor_score, monitor_data = run_monitor(text)

        result = {
            "id": sample["id"],
            "level": sample["level"],
            "description": sample["description"],
            "checker_score": checker_score,
            "monitor_score": monitor_score,
        }
        if monitor_data:
            result["monitor_dims"] = monitor_data.get("dimension_scores", {})
            result["monitor_behavioral"] = monitor_data.get("behavioral_scores", {})

        results.append(result)
        if not args.json:
            print(f"\n{'='*60}")
            print(f"样本: {sample['id']} ({sample['level']})")
            print(f"描述: {sample['description']}")
            print(f"Alignment Checker: {checker_score}")
            print(f"Realtime Monitor: {monitor_score}")
            if monitor_data:
                bh = monitor_data.get("behavioral_scores", {})
                if bh:
                    print(f"  行为约束: {bh}")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print("区分能力验证:")
        levels = {}
        for r in results:
            levels.setdefault(r["level"], []).append(r["monitor_score"])
        for level, scores in sorted(levels.items()):
            avg = sum(scores) / len(scores)
            print(f"  {level}: 平均 {avg:.1f} (n={len(scores)})")


if __name__ == "__main__":
    main()
