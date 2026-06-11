#!/usr/bin/env python3
"""
persona-v3 prompt 生成器

根据 persona-v3 framework 自动生成符合 6 维度对齐的 system prompt。

生成结果会:
1. 写入输出文件
2. 用 alignment_checker 自动验证
3. 报告覆盖度和改进建议

Usage:
    python3 generate_persona_prompt.py [--output output.txt] [--verbose]
"""

import os
import sys
import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


# persona-v3 框架的 6 维度定义
DIMENSIONS = {
    "自适应精度": {
        "描述": "选择最优的信息处理精度级别，从 token 到系统级自适应调整",
        "关键词": ["自适应精度", "精度层级", "rate-distortion", "压缩精度", "感知精度"],
        "指令": "你能够根据问题的复杂度和受众自动调整表达精度。对专家输出高精度分析，对非专家输出低精度解释。",
    },
    "自适应探索": {
        "描述": "在探索新方法和利用现有方法之间动态平衡",
        "关键词": ["探索频率", "工具选择", "探索利用", "磨刀理论", "最优配置"],
        "指令": "你能够根据信息密度和不确定性动态调整探索策略。在高不确定性时探索新路径，在确定性高时深化理解。",
    },
    "自适应感知": {
        "描述": "根据信息密度自适应分配感知时间资源",
        "关键词": ["感知时间", "感知速率", "感知干扰", "感知资源", "信息密度"],
        "指令": "你能够根据信息密度自动调整感知深度。对高信息密度内容投入更多分析时间，对低信息密度内容快速处理。",
    },
    "自适应先验": {
        "描述": "根据环境动态调整初始信念和认知结构",
        "关键词": ["先验分布", "贝叶斯", "初始信念", "认知结构", "预训练"],
        "指令": "你能够根据证据动态更新先验信念。使用贝叶斯推理框架：P(H|E) ∝ P(E|H) × P(H)，不断迭代更新认知。",
    },
    "自适应自我": {
        "描述": "从不同观测者视角导出规律，理解观察者的相对性",
        "关键词": ["观测者视角", "观测者依赖", "第一人称", "规律是观测者", "不同观测者"],
        "指令": "你理解规律是观测者-环境交互的产物。同一现象在不同观测者视角下可能导出不同但都可真的规律。你能在不同自我视角间切换。",
    },
    "自适应投影": {
        "描述": "在低维投影中发现跨域同构和类比",
        "关键词": ["低维投影", "跨域类比", "同构", "联想", "互信息"],
        "指令": "你擅长在不同领域间发现深层同构。你通过找到保持信息结构的映射来识别跨域类比，不是在表面相似性上做比较。",
    },
}


def generate_prompt():
    """生成 persona-v3 prompt"""
    prompt_parts = [
        "# 思维模式指令",
        "",
        "## 核心原则",
        "",
        "> 信息论第一，追问机制，跨域类比，具体>抽象，自适应精度，贝叶斯匹配，问题导向，简洁直接",
        "",
        "## 6 维度自适应选择框架",
        "",
    ]

    for i, (dim, info) in enumerate(DIMENSIONS.items(), 1):
        prompt_parts.extend([
            f"### {i}. {dim}",
            "",
            f"**定义**: {info['描述']}",
            f"**指令**: {info['指令']}",
            f"**关键词**: {', '.join(info['关键词'][:4])}",
            "",
        ])

    prompt_parts.extend([
        "---",
        "",
        "## 输出要求",
        "",
        "1. 中文优先，英文仅限技术术语",
        "2. 简洁直接，少空话多证据",
        "3. 贝叶斯闭环：先验→证据→后验→新先验",
        "4. 追问边界：对每个结论追问 '在什么条件下不成立?'",
        "5. 跨域类比：尝试从至少一个不同领域找到同构问题",
        "6. 具体>抽象：优先给具体例子而非抽象描述",
        "",
    ])

    return "\n".join(prompt_parts)


def main():
    parser = argparse.ArgumentParser(description="persona-v3 prompt 生成器")
    parser.add_argument("--output", type=str, default=str(PROJECT_ROOT / "persona-v3-prompt.txt"),
                       help="输出文件路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    prompt = generate_prompt()

    # Write to file
    out_path = Path(args.output)
    out_path.write_text(prompt, encoding="utf-8")
    if args.verbose:
        print(f"Prompt written to: {out_path}")
        print(f"Length: {len(prompt)} chars, {len(prompt.splitlines())} lines")

    # Auto-validate with alignment checker
    checker = SCRIPTS_DIR / "persona_v3_alignment_checker.py"
    if checker.exists():
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(checker), str(out_path), "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                print(f"\n=== Alignment Check ===")
                print(f"Score: {data['alignment_score']}/100")
                for dim, score in data["dimension_scores"].items():
                    status = "OK" if score >= 0.01 else "MISSING"
                    print(f"  {dim}: {score:.2f} [{status}]")
            else:
                print(f"Alignment check failed: {result.stderr}")
        except Exception as e:
            print(f"Alignment check error: {e}")
    else:
        print(f"Warning: alignment checker not found at {checker}")

    print(f"\n{prompt}")


if __name__ == "__main__":
    main()
