#!/usr/bin/env python3
"""
D38 实验重新设计：修正 D 命题的效用函数 artefact

修正内容：
1. 折现率 r=0.01（而非 0.001）
2. V_future 用 V_future/(1+V_future) 而非 sqrt(V_future)（单调、无压缩）
3. U_net 中 attraction 与 V_future 成正比（膨胀动机来自预期价值）

预期：修正后 T* 随 V_future 递增（原假设恢复）
"""

import numpy as np
import json

def acceptance_probability(s, theta, beta=5.0):
    threshold = 0.7
    return 1.0 / (1.0 + np.exp(-beta * (np.mean(s) - threshold)))

def signal_cost(s, theta):
    return np.sum(np.abs(s - theta))

def signal_decay_step(s, theta, gamma, lam, dE, dt, cost):
    dy_dt = -gamma * (s - theta) - lam * (dE / dt)
    s_new = s + dy_dt * dt
    return np.maximum(s_new, 0.01)

def signal_energy_budget(E0, s, cost, dt):
    c_s = np.sum(np.abs(s - 0.5) ** 2) * cost
    return -c_s * dt

def compute_optimal_T(V_future, r=0.01, V_maint=50.0, theta=np.array([0.6, 0.4, 0.5]),
                       gamma=0.005, lam=0.003, cost=0.1):
    """修正后的最优停止时间计算

    修正点：
    - attraction 项与 V_future 成正比（膨胀动机）
    - V_future 用 V_future/(1+V_future) 而非 sqrt
    - r=0.01
    """
    utilities = []

    for T_h in range(1, 365):
        U_net = 0.0
        s_current = np.array([0.9, 0.6, 0.75])  # 初始膨胀

        for t in range(T_h):
            P_a = acceptance_probability(s_current, theta, 5.0)
            burst = np.mean(np.maximum(s_current - theta, 0))

            # 修正1：膨胀动机与 V_future 成正比
            # 预期价值越高，越值得在初期投入更多膨胀
            attraction = P_a * burst * V_future / (1 + V_future)

            dE = signal_energy_budget(1.0, s_current, cost, 1.0)
            sig_cost = abs(dE)

            # 边际递增成本：维持膨胀越来越难
            marginal_cost_multiplier = 1.0 + 0.01 * t
            U_net += attraction - 0.02 * sig_cost * marginal_cost_multiplier

            # 信号衰减
            dE_step = signal_energy_budget(1.0, s_current, cost, 1.0)
            s_current = signal_decay_step(s_current, theta, gamma, lam, dE_step, 1.0, cost)

        # 修正2：V_future 用 sigmoid 缩放而非 sqrt
        discount = np.exp(-r * T_h)
        U_long_term = discount * V_maint * (V_future / (1 + V_future))

        U_total = U_net + U_long_term
        utilities.append((T_h, U_total))

    best_idx = max(range(len(utilities)), key=lambda i: utilities[i][1])
    return int(utilities[best_idx][0]), float(utilities[best_idx][1])


def main():
    print("=" * 60)
    print("D38 实验重新设计 - 修正 D 命题")
    print("=" * 60)

    V_future_values = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    results = {}

    for V_future in V_future_values:
        best_T, best_utility = compute_optimal_T(V_future)
        results[f'V_{V_future}'] = {
            'optimal_T': best_T,
            'best_utility': best_utility,
        }
        print(f"  V_future={V_future:6.1f} -> T*={best_T:3d} 天, U*={best_utility:.2f}")

    # 检查单调性
    T_stars = [results[f'V_{v}']['optimal_T'] for v in V_future_values]
    trend_increasing = all(T_stars[i] <= T_stars[i+1] for i in range(len(T_stars)-1))
    print(f"\n  T* 随 V_future 递增: {'YES' if trend_increasing else 'NO'}")

    # 分析：大 V_future 下 T* 的行为
    print("\n  详细分析：")
    for i, v in enumerate(V_future_values):
        key = f'V_{v}'
        T = results[key]['optimal_T']
        if i > 0:
            delta = T - T_stars[i-1]
            print(f"    V={v} -> T*={T}, delta_from_prev={delta:+d}")

    # 保存结果
    output = {
        'experiment': 'D38-redesign-D',
        'corrections': [
            'r=0.01 (was 0.001)',
            'V_future/(1+V_future) (was sqrt(V_future))',
            'attraction scaled by V_future/(1+V_future)',
        ],
        'results': results,
        'trend_increasing': trend_increasing,
    }

    # Overwrite d38-results.json with redesigned results
    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d38-redesign-results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[Save] Results written to chimera_lab/d38-redesign-results.json")

    return output


if __name__ == '__main__':
    main()
