#!/usr/bin/env python3
"""
D2-1 实验E1：规划能力阶梯函数检验

目标：验证定理2预测——规划成功率 vs 模型规模呈阶梯函数（非S形）

方法：使用OpenRouter API测试不同规模的Llama模型在规划任务上的表现
"""

import json
import time
from pathlib import Path
from typing import Optional
import statistics

# ============================================================
# 配置
# ============================================================
API_KEY = "sk-or-v1-..."  # OpenRouter API key

# 模型规模梯度（对应定理2中的 |A|）
MODELS = {
    "llama-3.1-8b": {"params_b": 8, "name": "meta-llama/llama-3.1-8b-instruct"},
    "llama-3.1-70b": {"params_b": 70, "name": "meta-llama/llama-3.1-70b-instruct"},
    "llama-3.1-405b": {"params_b": 405, "name": "meta-llama/llama-3.1-405b-instruct"},
}

# 任务集：不同复杂度的规划问题
TASKS = {
    "easy": {
        "description": "两步逻辑推理",
        "examples": [
            "If A implies B, and B implies C, and A is true, what is C?",
            "You have 3 apples. You give 1 to Alice and 2 to Bob. How many do you have left?",
        ],
        "expected_length": 2,
    },
    "medium": {
        "description": "多步规划（含回溯）",
        "examples": [
            "Plan a route visiting cities A, B, C where you must visit B before C but can visit A in any order.",
            "You need to cook pasta (10min), make sauce (5min parallel), and set table (2min). Minimize total time.",
        ],
        "expected_length": 4,
    },
    "hard": {
        "description": "约束满足规划",
        "examples": [
            "Arrange 8 queens on a chessboard so no two attack each other. List positions step by step.",
            "Solve a 3x3 sliding puzzle from given state to goal state in minimum moves.",
        ],
        "expected_length": 8,
    },
}

# 实验参数
SAMPLES_PER_TASK = 20  # 每个任务-模型组合的采样数
TEMPERATURE = 0.7

# ============================================================
# 任务评估器
# ============================================================
class TaskEvaluator:
    """使用LLM-as-judge评估规划答案的正确性"""

    EVALUATION_PROMPT = """
Evaluate whether this planning response is correct.

Task: {task_description}
Input: {task_input}
Response: {response}

Criteria for correctness:
1. All steps are logically valid
2. Final result matches expected outcome
3. No contradictions in reasoning

Respond with ONLY "CORRECT" or "INCORRECT" followed by brief reason.
"""

    def __init__(self, judge_model: str = "meta-llama/llama-3.1-70b-instruct"):
        self.judge_model = judge_model

    def evaluate(self, task_desc: str, task_input: str, response: str) -> tuple[bool, str]:
        prompt = self.EVALUATION_PROMPT.format(
            task_description=task_desc,
            task_input=task_input,
            response=response[:2000],  # Truncate for efficiency
        )

        # TODO: Implement API call to judge model
        # For now, return placeholder
        time.sleep(1)
        return True, "placeholder"

# ============================================================
# 主实验循环
# ============================================================
def run_experiment():
    """执行完整的阶梯函数检验"""

    results_dir = Path("loop/experiment/results/e1-step-function")
    results_dir.mkdir(parents=True, exist_ok=True)

    evaluator = TaskEvaluator()
    all_results = []

    for model_name, model_config in MODELS.items():
        print(f"\n{'='*60}")
        print(f"Testing model: {model_name} ({model_config['params_b']}B params)")
        print(f"{'='*60}")

        for task_level, task_config in TASKS.items():
            print(f"  Task level: {task_level}")

            correct_count = 0
            for i in range(SAMPLES_PER_TASK):
                # Select task example
                task_example = task_config["examples"][i % len(task_config["examples"])]

                # Generate response
                response = generate_response(
                    model=model_config["name"],
                    task=task_example,
                    temperature=TEMPERATURE,
                )

                # Evaluate
                is_correct, reason = evaluator.evaluate(
                    task_config["description"],
                    task_example,
                    response,
                )

                if is_correct:
                    correct_count += 1

                # Progress tracking
                if (i + 1) % 5 == 0:
                    print(f"    Sample {i+1}/{SAMPLES_PER_TASK}: {correct_count}/{i+1} correct")

            success_rate = correct_count / SAMPLES_PER_TASK
            all_results.append({
                "model": model_name,
                "params_b": model_config["params_b"],
                "task_level": task_level,
                "samples": SAMPLES_PER_TASK,
                "correct": correct_count,
                "success_rate": success_rate,
            })

    # Save results
    output_file = results_dir / "raw_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    # Analyze: fit step function vs sigmoid
    analyze_results(all_results, output_file)

def generate_response(model: str, task: str, temperature: float = 0.7) -> str:
    """Generate planning response via API"""
    # TODO: Implement OpenRouter API call
    return "placeholder response"

# ============================================================
# 结果分析
# ============================================================
def analyze_results(results: list[dict], output_file: Path):
    """拟合阶梯函数和S形曲线，比较拟合优度"""

    # Group by task level
    by_task = {}
    for r in results:
        key = r["task_level"]
        if key not in by_task:
            by_task[key] = []
        by_task[key].append(r)

    analysis = {}
    for task_level, data in by_task.items():
        params = [d["params_b"] for d in data]
        rates = [d["success_rate"] for d in data]

        # Fit sigmoid: f(x) = 1 / (1 + exp(-k*(x - x0)))
        # Fit step: f(x) = 1 if x > threshold else 0

        # TODO: Implement curve fitting using scipy
        analysis[task_level] = {
            "params": params,
            "rates": rates,
            "sigmoid_r2": None,  # Placeholder
            "step_r2": None,     # Placeholder
        }

    # Compare: if step R² > sigmoid R² significantly, supports theorem 2
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

    analysis_file = output_file.parent / "analysis.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"Analysis saved to: {analysis_file}")

if __name__ == "__main__":
    run_experiment()
