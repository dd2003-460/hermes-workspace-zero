#!/usr/bin/env python3
"""
persona-v3 上下文验证器

模拟 persona-v3 prompt 在实际 Claude Code 会话中的效果：
1. 加载 persona-v3 prompt 作为 system prompt
2. 对一组 benchmark 问题生成回答（通过 API）
3. 用 alignment checker 评估回答的对齐度
4. 对比 method_only / persona / no-prompt 三种策略

Usage:
    python3 validate_persona_in_context.py [--api-key ANTHROPIC_KEY]
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROMPT_FILE = PROJECT_ROOT / "persona-v3-prompt.txt"
MANIFEST_FILE = PROJECT_ROOT / "persona-manifest-v3.txt"
CHECKER = PROJECT_ROOT / "scripts" / "persona_v3_alignment_checker.py"

# Benchmark questions — 来自 eval_complex_reasoning.py 的经典问题
BENCHMARK_QUESTIONS = [
    {
        "id": "math_gender_gap",
        "question": "数学天赋男女差异的生物学解释是否成立？请从统计分布、社会建构、实验证据三方面分析。",
        "expected_dimensions": ["自适应先验", "自适应投影", "自适应精度"],
    },
    {
        "id": "intelligence_definition",
        "question": "什么是智能？信息论视角下能否给出统一的定义？",
        "expected_dimensions": ["自适应自我", "自适应投影", "自适应感知"],
    },
    {
        "id": "probability_dynamics",
        "question": "概率可能是动力学下的信息抹除，这个说法意味着什么？请用数学和哲学双重视角分析。",
        "expected_dimensions": ["自适应精度", "自适应先验", "自适应自我"],
    },
]


def load_persona_prompt():
    if not PROMPT_FILE.exists():
        print("ERROR: persona-v3-prompt.txt not found")
        sys.exit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")


def load_method_only_prompt():
    """加载 method_only 80字符提示词"""
    if not MANIFEST_FILE.exists():
        return ""
    return MANIFEST_FILE.read_text(encoding="utf-8").strip()


def evaluate_response_text(text, benchmark):
    """用 alignment checker 评估单条回答"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        f.write(f"\n\n# Benchmark: {benchmark['id']}\n")
        f.write(f"Expected dimensions: {', '.join(benchmark['expected_dimensions'])}\n")
        tmp_path = f.name

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(CHECKER), tmp_path, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"  Evaluation error: {e}")
        return None
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def dry_run():
    """dry run — 不做 API 调用，只展示验证计划和 prompt 内容"""
    print("=" * 60)
    print("persona-v3 上下文验证器")
    print("=" * 60)

    persona = load_persona_prompt()
    method_only = load_method_only_prompt()

    print(f"\n=== Persona-v3 Prompt ===\n")
    print(persona)
    print(f"\n=== Method-Only Prompt ===\n{method_only}\n")

    print("=" * 60)
    print("Benchmark 问题列表")
    print("=" * 60)
    for bq in BENCHMARK_QUESTIONS:
        print(f"\n[{bq['id']}]")
        print(f"  问题: {bq['question']}")
        print(f"  期望维度: {', '.join(bq['expected_dimensions'])}")

    print(f"\n{'=' * 60}")
    print("验证策略")
    print("=" * 60)
    print("""
此验证器设计为与 Anthropic API 配合使用，流程：

1. 对每个 benchmark 问题，用三种策略分别生成回答：
   a) no_prompt: 无特殊提示词
   b) method_only: 80字符方法论提示词
   c) persona_v3: 完整的 persona-v3 prompt

2. 对每条回答用 alignment_checker 评估 6 维度覆盖度

3. 对比三种策略:
   - 哪种策略覆盖维度最多？
   - 哪种策略在期望维度上得分最高？
   - persona-v3 是否比 method_only 在某些维度上有优势？

4. 迭代改进 prompt

当前为 dry_run 模式。需要设置 ANTHROPIC_API_KEY 才能执行实际验证。

Usage: export ANTHROPIC_API_KEY=sk-ant-... && python3 validate_persona_in_context.py --run
""")

    # Print recommendation
    print("\n" + "=" * 60)
    print("当前结论")
    print("=" * 60)
    print("""
基于离线分析（alignment checker）的结果：

1. persona-v3 prompt 已得 72.08/100，6维度=1.0
2. method_only 在 eval_complex_reasoning 中得 74.66%（最高）
3. chenglu_persona 在 eval_complex_reasoning 中得 70.52%

persona-v3 prompt 的潜在优势：
- 结构化程度更高，可能在复杂问题上引导更深入的分析
- 6维度框架覆盖完整，可验证回答是否涉及预期维度
- 但过长（1053字符），可能占满 context window，反而影响实际推理能力

建议：
- 将 persona-v3 prompt 作为 AGENTS.md 的一部分加载
- 在实际 Claude Code 会话中观察效果（就是当前会话）
- 对比加载 persona-v3 prompt 前后的分析质量
""")


def run_with_api():
    """使用 Anthropic API 执行实际验证"""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        return

    client = anthropic.Anthropic()
    persona = load_persona_prompt()
    method_only = load_method_only_prompt()

    results = {"persona_v3": [], "method_only": [], "no_prompt": []}

    for bq in BENCHMARK_QUESTIONS:
        print(f"\n--- Evaluating: {bq['id']} ---")

        strategies = [
            ("persona_v3", persona),
            ("method_only", method_only),
            ("no_prompt", ""),
        ]

        for strategy_name, system_prompt in strategies:
            print(f"  Strategy: {strategy_name}", end=" ")

            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": bq["question"]}],
                )

                answer_text = response.content[0].text
                print(f"(len={len(answer_text)})")

                eval_result = evaluate_response_text(answer_text, bq)
                if eval_result:
                    results[strategy_name].append({
                        "benchmark_id": bq["id"],
                        "answer_length": len(answer_text),
                        "alignment_score": eval_result["alignment_score"],
                        "dimension_scores": eval_result["dimension_scores"],
                        "answer_preview": answer_text[:200],
                    })
                else:
                    print(f"    [evaluation failed]")
            except Exception as e:
                print(f"[error: {e}]")

    # Save results
    output_path = PROJECT_ROOT / "eval_results" / "context_validation_results.json"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for strategy_name, entries in results.items():
        if entries:
            avg_score = sum(e["alignment_score"] for e in entries) / len(entries)
            avg_length = sum(e["answer_length"] for e in entries) / len(entries)
            print(f"{strategy_name}: avg_alignment={avg_score:.1f}, avg_length={avg_length:.0f}, responses={len(entries)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="persona-v3 上下文验证器")
    parser.add_argument("--run", action="store_true", help="使用 Anthropic API 执行实际验证")
    parser.add_argument("--benchmark-only", action="store_true", help="只打印 benchmark 问题")
    args = parser.parse_args()

    if args.run:
        run_with_api()
    else:
        dry_run()


if __name__ == "__main__":
    main()
