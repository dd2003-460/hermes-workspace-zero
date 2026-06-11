#!/usr/bin/env python3
"""
D27 共发现阈值理论 - 数值验证实验

验证 D27-3 收敛时间定理：
    T_conv = (1/λ_min) * log(D_0^2 / ε^2)

核心思路：
- 在 n 维空间中模拟 N 个研究者的随机游走
- 使用梯度场引导研究者向最优解 θ* 收敛
- 测量不同初始距离 D_0 下的收敛时间 T_conv
- 验证 T_conv ∝ log(D_0^2 / ε^2) 的对数线性关系

用法：
    python d27-co-discovery-simulation.py [n_dim] [n_researchers] [n_iterations]
"""

import numpy as np
import argparse
import json
import os
from datetime import datetime

np.random.seed(42)


def quadratic_potential(theta, x_opt):
    """二次势函数 - 凸优化问题"""
    return np.sum((theta - x_opt)**2)


def gradient_quadratic(theta, x_opt):
    """二次势函数梯度"""
    return 2 * (theta - x_opt)


def run_convergence_experiment(n_dim=10, n_researchers=5, n_steps=1000,
                                step_size=0.1, noise_std=0.01,
                                epsilon=1e-6, optimal_points=None):
    """
    运行收敛实验

    参数：
        n_dim: 问题空间维度
        n_researchers: 研究者数量
        n_steps: 最大迭代步数
        step_size: 学习步长 α
        noise_std: 探索噪声 σ
        epsilon: 收敛阈值 ε
        optimal_points: 最优解列表（若无则随机生成）

    返回：
        results: 包含每个研究者-研究者对的收敛时间
    """
    n_researchers = n_researchers or int(np.sqrt(n_dim) * 5) + 2
    n_researchers = max(n_researchers, 3)

    # 最优解 - 所有研究者收敛到同一点
    if optimal_points is None:
        x_opt = np.random.randn(n_dim) * 10
        optimal_points = [x_opt] * n_researchers  # 同一点

    # 初始化研究者位置（随机散布）
    theta = np.random.randn(n_researchers, n_dim) * 20

    # 保存初始位置用于距离计算
    theta_init = theta.copy()

    # 收敛状态跟踪
    converged = np.zeros(n_researchers, dtype=bool)
    convergence_time = np.full(n_researchers, -1)

    # 时间步跟踪
    pairwise_convergence = []  # (t, i, j, distance)

    # transient 等待时间 - 需要足够让梯度收敛超越噪声
    # 噪声地板 ≈ sqrt(n_dim) * noise_std，需要 eps > 此值
    transient = max(50, int(np.log(epsilon) / np.log(step_size * 2)))

    for t in range(n_steps):
        # 梯度更新 + 噪声
        for i in range(n_researchers):
            grad = gradient_quadratic(theta[i], optimal_points[i])
            theta[i] -= step_size * grad + noise_std * np.random.randn(n_dim)

        # 检查收敛
        if t > transient:
            for i in range(n_researchers):
                if not converged[i] and convergence_time[i] == -1:
                    dist_to_opt = np.linalg.norm(theta[i] - optimal_points[i])
                    if dist_to_opt < epsilon:
                        converged[i] = True
                        convergence_time[i] = t

        # 记录成对距离
        pairwise_dists = []
        for i in range(n_researchers):
            for j in range(i + 1, n_researchers):
                dist = np.linalg.norm(theta[i] - theta[j])
                pairwise_dists.append((t, i, j, dist))

        pairwise_convergence.append(pairwise_dists)

        # 检查是否全部收敛
        if np.all(converged):
            break

    # 计算收敛结果
    results = compute_convergence_results(
        convergence_time, pairwise_convergence,
        theta, optimal_points, n_researchers
    )

    return results


def compute_convergence_results(convergence_time, pairwise_convergence,
                                theta, optimal_points, n_researchers):
    """计算收敛统计结果"""

    # 成对收敛时间
    pair_convergence_times = []
    initial_distances = []

    for i in range(n_researchers):
        for j in range(i + 1, n_researchers):
            # 成对收敛：两人都达标的时刻
            if convergence_time[i] > 0 and convergence_time[j] > 0:
                t_pair = max(convergence_time[i], convergence_time[j])
                # 初始距离
                d0 = np.linalg.norm(theta[i] - theta[j])
                pair_convergence_times.append(t_pair)
                initial_distances.append(d0)

    # D27-3 定理验证：T_conv ∝ log(D_0^2 / ε^2)
    if len(pair_convergence_times) > 0 and len(initial_distances) > 0:
        log_d0squared = np.log(np.array(initial_distances)**2 / 1e-12)
        ts = np.array(pair_convergence_times)

        # 线性回归：T = a * log(D_0^2/ε^2) + b
        A = np.vstack([log_d0squared, np.ones_like(log_d0squared)]).T
        slope, intercept = np.linalg.lstsq(A, ts, rcond=None)[0]

        r_squared = 1 - np.sum((ts - (slope * log_d0squared + intercept))**2) / np.sum((ts - np.mean(ts))**2)

        # 最小特征值 λ_min 的估计（梯度矩阵）
        # 对于二次势 -H = -2I，所以 λ_min = 2
        estimated_lambda_min = 2.0

        theorem_verification = {
            "predicted_slope": 1 / estimated_lambda_min,
            "estimated_slope": float(slope),
            "predicted_vs_actual_ratio": float(slope / estimated_lambda_min),
            "r_squared": float(r_squared),
            "n_pairs": len(pair_convergence_times)
        }
    else:
        theorem_verification = None

    return {
        "pair_convergence_times": [float(t) for t in pair_convergence_times],
        "initial_distances": [float(d) for d in initial_distances],
        "theorem_verification": theorem_verification,
        "timestamp": datetime.now().isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description="D27 Co-discovery Convergence Experiment")
    parser.add_argument("--dim", type=int, default=5, help="Problem space dimension")
    parser.add_argument("--researchers", type=int, default=None, help="Number of researchers (default: auto)")
    parser.add_argument("--steps", type=int, default=5000, help="Maximum iterations")
    parser.add_argument("--lr", type=float, default=0.1, help="Learning rate (step size)")
    parser.add_argument("--noise", type=float, default=0.0, help="Exploration noise std")
    parser.add_argument("--epsilon", type=float, default=1e-6, help="Convergence threshold")
    parser.add_argument("--trials", type=int, default=200, help="Number of independent trials (for theorem verification)")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    print(f"Running D27 Co-discovery Experiment:")
    print(f"  Dimensions: {args.dim}")
    print(f"  Trials: {args.trials} (for theorem verification)")
    print(f"  Researchers: {args.researchers or 'auto (estimated ~' + str(int(np.sqrt(args.dim)*5)+2) + ')'}")
    print(f"  Steps: {args.steps}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Noise: {args.noise}")
    print(f"  Convergence threshold: {args.epsilon}")
    print()

    # 多试验模式 - 用于定理验证
    T_list = []
    D0_list = []

    for trial in range(args.trials):
        rng = np.random.RandomState(trial * 7 + 42)

        x_opt = rng.randn(args.dim) * 10
        optimal_points = [x_opt] * max(int(np.sqrt(args.dim) * 5) + 2, 3)
        n_researchers = len(optimal_points)

        # 不同初始散布产生不同 D_0
        spread = rng.uniform(5, 60)
        theta = rng.randn(n_researchers, args.dim) * spread
        theta_init = theta.copy()

        converged = np.zeros(n_researchers, dtype=bool)
        convergence_time = np.full(n_researchers, -1)
        transient = max(50, int(np.log(args.epsilon) / np.log(args.lr * 2)))

        for t in range(args.steps):
            for i in range(n_researchers):
                grad = gradient_quadratic(theta[i], optimal_points[i])
                theta[i] -= args.lr * grad + args.noise * np.random.randn(args.dim)

            if t > transient:
                for i in range(n_researchers):
                    if not converged[i] and convergence_time[i] == -1:
                        dist_to_opt = np.linalg.norm(theta[i] - optimal_points[i])
                        if dist_to_opt < args.epsilon:
                            converged[i] = True
                            convergence_time[i] = t

            if np.all(converged):
                break

        # 只保留两个研究者都收敛的试验
        if convergence_time[0] > 0 and convergence_time[1] > 0:
            t_pair = max(convergence_time[0], convergence_time[1])
            d0 = np.linalg.norm(theta_init[0] - theta_init[1])
            T_list.append(t_pair)
            D0_list.append(d0)

    print(f"Valid trials: {len(T_list)}/{args.trials}")
    print(f"Convergence time range: [{min(T_list)}, {max(T_list)}]")
    print(f"D_0 range: [{min(D0_list):.1f}, {max(D0_list):.1f}]")
    print()

    # 定理验证
    n_pairs = len(T_list)
    if n_pairs > 0:
        log_d0squared = np.log(np.array(D0_list)**2 / args.epsilon**2)
        ts = np.array(T_list)

        A = np.vstack([log_d0squared, np.ones_like(log_d0squared)]).T
        slope, intercept = np.linalg.lstsq(A, ts, rcond=None)[0]

        r_squared = 1 - np.sum((ts - (slope * log_d0squared + intercept))**2) / np.sum((ts - np.mean(ts))**2)

        estimated_lambda_min = 2.0

        theorem_verification = {
            "predicted_slope": 1 / estimated_lambda_min,
            "estimated_slope": float(slope),
            "predicted_vs_actual_ratio": float(slope / estimated_lambda_min),
            "r_squared": float(r_squared),
            "n_pairs": n_pairs,
            "intercept": float(intercept),
            "mean_T": float(np.mean(ts)),
            "std_T": float(np.std(ts))
        }
    else:
        theorem_verification = None

    results = {
        "pair_convergence_times": [float(t) for t in T_list],
        "initial_distances": [float(d) for d in D0_list],
        "theorem_verification": theorem_verification,
        "params": {
            "dim": args.dim,
            "trials": args.trials,
            "steps": args.steps,
            "lr": args.lr,
            "noise": args.noise,
            "epsilon": args.epsilon
        },
        "timestamp": datetime.now().isoformat()
    }

    # 打印结果
    if results["theorem_verification"]:
        v = results["theorem_verification"]
        print("=== D27-3 Theorem Verification ===")
        print(f"Predicted slope: {v['predicted_slope']:.4f} (1/λ_min)")
        print(f"Estimated slope: {v['estimated_slope']:.4f}")
        print(f"Ratio (predicted/actual): {v['predicted_vs_actual_ratio']:.4f}")
        print(f"R-squared: {v['r_squared']:.4f}")
        status = "VERIFIED (R² > 0.8)" if v['r_squared'] > 0.8 else "PARTIAL (R² ~ 0.6-0.8)" if v['r_squared'] > 0.6 else "NOT VERIFIED"
        print(f"Status: {status}")
        print(f"Pairs analyzed: {v['n_pairs']}")
        print()

    # 输出 JSON
    output_path = args.output or f"d27-co-discovery-results.json"
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
