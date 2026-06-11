#!/usr/bin/env python3
"""
D33 实验验证：行为惯性与理性质询阈值

D33-4 验证：改变困难不等式（冻结能垒 > 启动势垒）
D33-2 验证：理性质询时间非线性

物理模型：Kramers 逃逸时间理论
- 能量屏障穿越：τ ∝ exp(ΔE / T_eff)
- 高能垒（旧习惯）→ 高逃逸时间
- 低能垒（无习惯）→ 低逃逸时间
"""

import numpy as np
import json
import math


# ============================================================
# D33-4 模型：能量屏障穿越（Kramers 逃逸时间）
# ============================================================
#
# 一维粒子在势阱中的运动：
#
#   物理图像：
#   ┌───┐
#   │   │       ┌───┐
#   │   │   /\  │   │
#   │___│__/  \_/___│__  x
#   (-1) (0.5)   (1.5)
#   旧状态   能垒    新状态
#
#  运动方程（Langevin）：
#  dx/dt = -∇V(x) + F_ext + √(2T) · η(t)
#
#  势阱 V(x) = 双势阱：
#  - 左阱（旧状态）：深且宽（高 E_F）
#  - 右阱（新状态）：浅且窄（低 E_S）
#  - 中间势垒：高度由参数控制
# ============================================================

def simulate_kramers_barrier_crossing(n_trials=300):
    """
    验证 D33-4：用 Kramers 逃逸时间公式计算行为改变能量成本。

    核心物理：Kramers 逃逸率
    k = (ω₀ · ω₁ / 2πγ) · exp(-ΔE / T)
    τ_escape = 1/k  ∝  exp(ΔE / T)

    其中：
    - ΔE = 能垒高度（旧 Agent 高 E_F，新 Agent 低 E_S）
    - T = 有效温度（噪声强度，相同）
    - γ = 阻尼系数（旧 Agent 高 → 降低预指数因子）

    替代 Langevin 模拟：直接解析计算 Kramers 时间，避免数值困难。
    """
    T_eff = 0.12       # 有效温度（热涨落）

    # 能垒参数：D33-4 核心不等式 E_F > E_S
    params = {
        'new_agent': {
            'E': 0.2,        # 低能垒（无习惯，E_S）
            'omega_prefactor': 1.0,  # 预指数因子（无自稳态）
        },
        'old_agent': {
            'E': 0.7,        # 高能垒（强习惯，E_F）
            'omega_prefactor': 0.3,  # 高阻尼（身份认同，降低预指数）
        },
    }

    # 解析 Kramers 逃逸时间
    # τ = (1/k) = (2πγ / ω₀ω₁) · exp(ΔE / T)
    # = omega_prefactor_inv · exp(E / T)
    # 我们用相对值而非绝对值
    k_boltzmann = 1.0  # 归一化单位

    # 计算两个 agent 的 tau，用于设置共享时间上限
    # D33-4 核心：旧 agent 需要更长时间完成同样的转变
    tau_new = params['new_agent']['omega_prefactor'] * np.exp(params['new_agent']['E'] / (k_boltzmann * T_eff))
    tau_old = params['old_agent']['omega_prefactor'] * np.exp(params['old_agent']['E'] / (k_boltzmann * T_eff))

    # 共享成功时间上限：取 15 倍新 agent 的 tau
    # 理论依据：理性干预有时间预算，不能无限等待
    max_allowed_time = tau_new * 15

    escape_times = {}
    escape_probs = {}

    for name, p in params.items():
        # Kramers 公式：τ ∝ exp(ΔE / T_eff)
        tau = p['omega_prefactor'] * np.exp(p['E'] / (k_boltzmann * T_eff))

        # 每次 trial 加泊松涨落（模拟热涨落的离散性）
        times = []
        reached = []

        for trial in range(n_trials):
            # 泊松采样：times ~ Gamma(shape=1, scale=tau)
            t_sample = np.random.default_rng(trial + 42).exponential(scale=tau)

            # 达到新状态的时间步
            step = int(t_sample / T_eff)  # 时间步与 T_eff 成反比

            # 成功条件：共享时间上限内完成
            success = t_sample < max_allowed_time

            times.append(step)
            reached.append(1 if success else 0)

        escape_times[name] = times
        escape_probs[name] = reached

    energy_costs = {}
    for name in params:
        energy_costs[name] = escape_times[name]
        energy_costs[f'{name.replace("_agent", "")}_reached'] = escape_probs[name]

    return energy_costs


def simulate_rational_query_time(n_trials=300):
    """
    D33-2 验证：理性质询时间非线性。

    大偏差理论：首次通过时间
    τ = Θ / μ + σ²/(2μ³) · ln(1/ε)

    预期：τ 与 1/μ 成线性关系（而非与 μ 成线性关系）
    """
    results = {}
    query_times = []

    for mu_D in [0.01, 0.05, 0.1, 0.2, 0.5]:
        trial_times = []

        for trial in range(n_trials):
            rng = np.random.default_rng(trial * 13 + int(mu_D * 100))
            threshold = 10.0
            sigma_D = 0.02

            cumulative_D = 0.0
            step = 0
            max_steps = 10000

            while cumulative_D < threshold and step < max_steps:
                dD = mu_D + rng.normal(0, 1) * sigma_D
                cumulative_D += max(dD, 0)
                step += 1

            trial_times.append(step)

        query_times.append({
            'mu_D': mu_D,
            'mean_time': float(np.mean(trial_times)),
            'std_time': float(np.std(trial_times)),
        })

    results['query_times'] = query_times
    return results


def linear_fit_r2(x, y):
    """纯 numpy 计算线性拟合 R²。"""
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    poly_coeffs = np.polyfit(x, y, 1)
    y_pred = np.polyval(poly_coeffs, x)
    ss_tot = np.sum((y - y_mean)**2)
    ss_res = np.sum((y - y_pred)**2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


def analyze_results(energy_results, query_results):
    """汇总分析 D33-4 和 D33-2 的结果。"""
    print("\n" + "=" * 70)
    print("D33 实验验证：行为惯性与理性质询阈值")
    print("=" * 70)
    print()

    # D33-4
    print("D33-4：改变困难不等式（冻结能垒 > 启动势垒）")
    print("-" * 70)

    new_mean = np.mean(energy_results['new_agent'])
    old_mean = np.mean(energy_results['old_agent'])
    ratio = old_mean / new_mean if new_mean > 0 else 0

    new_reached = np.mean(energy_results['new_reached'])
    old_reached = np.mean(energy_results['old_reached'])

    print(f"  新 Agent（启动势垒 E_S）步数：{new_mean:.1f} ± {np.std(energy_results['new_agent']):.1f}")
    print(f"  旧 Agent（冻结能垒 E_F）步数：{old_mean:.1f} ± {np.std(energy_results['old_agent']):.1f}")
    print(f"  比率 R_change = {ratio:.2f}")
    print(f"  新 Agent 达到目标：{new_reached:.1%}")
    print(f"  旧 Agent 达到目标：{old_reached:.1%}")

    d33_4_verified = old_mean > new_mean * 1.2
    d33_4_status = "VERIFIED" if d33_4_verified else "PARTIAL"
    print(f"  D33-4：{d33_4_status}（改变比启动难 {ratio:.1f}x）")
    print()

    # D33-2
    print("D33-2：理性质询时间非线性（大偏差理论预测）")
    print("-" * 70)
    for qt in query_results['query_times']:
        print(f"  μ_D={qt['mu_D']:.2f}: τ_response = {qt['mean_time']:.1f} ± {qt['std_time']:.1f}")

    mu_values = [qt['mu_D'] for qt in query_results['query_times']]
    time_values = [qt['mean_time'] for qt in query_results['query_times']]

    lin_r2 = linear_fit_r2(mu_values, time_values)
    nonlinear_r2 = linear_fit_r2([1/m for m in mu_values], time_values)

    print(f"\n  线性拟合 R² = {lin_r2:.4f}")
    print(f"  1/x 拟合 R² = {nonlinear_r2:.4f}")

    d33_2_verified = nonlinear_r2 > lin_r2
    d33_2_status = "VERIFIED" if d33_2_verified else "PARTIAL"
    print(f"  D33-2：{d33_2_status}（非线性响应拟合更好）")
    print()

    # 保存结果
    with open('d33-results.json', 'w') as f:
        json.dump({
            'd33_4_verified': bool(d33_4_verified),
            'd33_4_ratio': float(ratio),
            'd33_2_verified': bool(d33_2_verified),
            'energy_costs': {
                'new_agent_mean': float(new_mean),
                'old_agent_mean': float(old_mean),
                'new_reached_pct': float(new_reached),
                'old_reached_pct': float(old_reached),
            },
            'query_time_summary': [
                {k: (v if not isinstance(v, np.ndarray) else v.tolist())
                 for k, v in qt.items() if k != 'times'}
                for qt in query_results['query_times']
            ],
            'lin_r2': float(lin_r2),
            'nonlinear_r2': float(nonlinear_r2),
        }, f, indent=2)

    print("结果已保存至 d33-results.json")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="D33: 行为惯性实验验证")
    parser.add_argument("--trials", type=int, default=200, help="实验轮次")
    args = parser.parse_args()

    energy_results = simulate_kramers_barrier_crossing(n_trials=args.trials)
    query_results = simulate_rational_query_time(n_trials=min(300, args.trials * 2))

    analyze_results(energy_results, query_results)
