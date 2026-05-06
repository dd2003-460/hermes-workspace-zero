#!/usr/bin/env python3
"""
D2-1 实验E1 - 模拟验证：阶梯函数 vs S形曲线区分

在运行真实实验前，用合成数据验证统计检验方法的有效性。
生成符合定理2预测的阶梯函数数据，对比sigmoid拟合优度。

依赖：仅Python标准库（无需scipy）
"""

import math
import json
import random
from pathlib import Path
from typing import Callable, Tuple

# ============================================================
# 数学工具（轻量实现，无需scipy）
# ============================================================

def sigmoid(x: float, k: float = 1.0, x0: float = 50.0) -> float:
    """S形曲线：f(x) = 1 / (1 + exp(-k*(x - x0)))"""
    z = k * (x - x0)
    if z > 500: return 1.0
    if z < -500: return 0.0
    return 1.0 / (1.0 + math.exp(-z))

def step_function(x: float, threshold: float = 50.0) -> float:
    """阶梯函数：f(x) = 1 if x > threshold else 0"""

def add_noise(value: float, noise_level: float = 0.05) -> float:
    """添加高斯噪声（Box-Muller变换）"""
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    return value + z * noise_level

def r_squared(y_true: list, y_pred: list) -> float:
    """计算R²拟合优度"""
    n = len(y_true)
    mean_y = sum(y_true) / n
    ss_res = sum((t - p)**2 for t, p in zip(y_true, y_pred))
    ss_tot = sum((t - mean_y)**2 for t in y_true)
    if ss_tot == 0: return 1.0
    return 1 - (ss_res / ss_tot)

def simple_gradient_descent(data_x, data_y, model_fn, params_init, lr=0.01, iterations=1000):
    """简易梯度下降拟合（数值梯度）"""
    params = list(params_init)

    def mse_loss(p):
        predictions = [model_fn(x, *p) for x in data_x]
        return sum((y - p_)**2 for y, p_ in zip(data_y, predictions)) / len(data_x)

    def numerical_gradient(p):
        grad = []
        current_loss = mse_loss(p)
        for i in range(len(p)):
            p_plus = list(p)
            p_plus[i] += 1e-5
            grad.append((mse_loss(p_plus) - current_loss) / 1e-5)
        return grad

    for _ in range(iterations):
        grad = numerical_gradient(params)
        params = [p - lr * g for p, g in zip(params, grad)]

    return params

# ============================================================
# 数据生成：符合定理2预测的合成数据
# ============================================================

def generate_step_data(n_points=5, noise=0.03):
    """生成阶梯函数数据（定理2预测的真实分布）"""
    model_sizes = [8, 13, 34, 70, 405]
    threshold = 20.0  # d_c ≈ 20B
    true_k = 5.0      # 相变sharpness

    y_true = [1.0 if x > threshold else 0.0 for x in model_sizes]
    y_noisy = [add_noise(y, noise) for y in y_true]

    return model_sizes, y_noisy, y_true, threshold, true_k

def generate_sigmoid_data(n_points=5, noise=0.03):
    """生成S形曲线数据（对照）"""
    model_sizes = [8, 13, 34, 70, 405]
    k = 0.1
    x0 = 30.0

    y_true = [sigmoid(x, k, x0) for x in model_sizes]
    y_noisy = [add_noise(y, noise) for y in y_true]

    return model_sizes, y_noisy, y_true, k, x0

# ============================================================
# 曲线拟合与比较
# ============================================================

def fit_step_model(x_data, y_data):
    """拟合阶梯函数参数（threshold + sharpness）"""
    # 简化：枚举可能的threshold，选最佳
    best_threshold = None
    best_r2 = -1

    for threshold in sorted(x_data):
        predictions = [1.0 if x > threshold else 0.0 for x in x_data]
        r2 = r_squared(y_data, predictions)
        if r2 > best_r2:
            best_r2 = r2
            best_threshold = threshold

    return best_threshold, best_r2

def fit_sigmoid_model(x_data, y_data):
    """拟合S形曲线参数"""
    # 初始猜测
    init_params = [0.1, 30.0]  # k, x0

    def sigmoid_with_params(x, k, x0):
        return sigmoid(x, k, x0)

    try:
        params = simple_gradient_descent(
            x_data, y_data, sigmoid_with_params, init_params,
            lr=0.001, iterations=5000
        )
        predictions = [sigmoid_with_params(x, *params) for x in x_data]
        r2 = r_squared(y_data, predictions)
        return params, r2
    except Exception:
        return init_params, -1

# ============================================================
# 主实验
# ============================================================

def run_simulation(n_trials=100):
    """运行多次模拟，统计阶梯函数 vs S形曲线的区分能力"""

    results = {
        "step_true": {"step_r2_mean": 0, "sigmoid_r2_mean": 0},
        "sigmoid_true": {"step_r2_mean": 0, "sigmoid_r2_mean": 0},
    }

    for trial in range(n_trials):
        # 生成符合阶梯函数假设的数据（定理2预测）
        x_data, y_noisy, _, _, _ = generate_step_data()

        # 拟合两种模型
        step_threshold, step_r2 = fit_step_model(x_data, y_noisy)
        sigmoid_params, sigmoid_r2 = fit_sigmoid_model(x_data, y_noisy)

        # 记录
        results["step_true"]["step_r2_mean"] += step_r2
        results["step_true"]["sigmoid_r2_mean"] += sigmoid_r2

        # 生成符合S形假设的数据（对照）
        x_data2, y_noisy2, _, _, _ = generate_sigmoid_data()

        step_r2_2, _ = fit_step_model(x_data2, y_noisy2)
        sigmoid_params_2, sigmoid_r2_2 = fit_sigmoid_model(x_data2, y_noisy2)

        results["sigmoid_true"]["step_r2_mean"] += step_r2_2
        results["sigmoid_true"]["sigmoid_r2_mean"] += sigmoid_r2_2

    # 取平均
    for key in results:
        results[key]["step_r2_mean"] /= n_trials
        results[key]["sigmoid_r2_mean"] /= n_trials

    return results

def main():
    random.seed(42)  # 可复现性

    print("="*60)
    print("D2-1 实验E1 - 模拟验证")
    print("="*60)

    # 运行模拟
    results = run_simulation(n_trials=100)

    print("\n" + "="*60)
    print("结果：当真实分布是阶梯函数时（定理2预测）")
    print("="*60)
    print(f"  阶梯函数拟合 R²: {results['step_true']['step_r2_mean']:.4f}")
    print(f"  S形曲线拟合 R²:  {results['step_true']['sigmoid_r2_mean']:.4f}")
    print(f"  差异: {results['step_true']['step_r2_mean'] - results['step_true']['sigmoid_r2_mean']:.4f}")

    print("\n" + "="*60)
    print("结果：当真实分布是S形曲线时（对照）")
    print("="*60)
    print(f"  阶梯函数拟合 R²: {results['sigmoid_true']['step_r2_mean']:.4f}")
    print(f"  S形曲线拟合 R²:  {results['sigmoid_true']['sigmoid_r2_mean']:.4f}")
    print(f"  差异: {results['sigmoid_true']['step_r2_mean'] - results['sigmoid_true']['sigmoid_r2_mean']:.4f}")

    # 保存结果
    results_dir = Path("loop/experiment/results/e1-step-function")
    results_dir.mkdir(parents=True, exist_ok=True)

    output_file = results_dir / "simulation_verification.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n结果已保存: {output_file}")

    # 结论
    if results['step_true']['step_r2_mean'] > results['step_true']['sigmoid_r2_mean']:
        print("\n✓ 结论：统计检验能够有效区分阶梯函数和S形曲线")
        print("  → 真实实验可以使用此方法检验定理2预测")
    else:
        print("\n✗ 结论：统计检验区分能力不足，需要改进方法")

if __name__ == "__main__":
    main()
