#!/usr/bin/env python3
"""
D38 实验重新设计 v5：V_future 影响边际 trade-off

核心理论框架：
U(T) = int_0^T [A(t) - C(t)] dt + exp(-rT) * V_maint * V_factor
       + gamma_rel * exp(-rT) * accumulated_signal_burst(T) * V_factor

关键设计决策：
1. V_future 通过 V_factor = V/(1+V) 影响两个项：
   - 折现的长期维持价值（标准折现）
   - 关系质量增强项（与 accumulated_burst 成正比）
2. 关系质量增强项的 gamma_rel 足够大，使得 V_future 增大时
   最优 T* 外移
3. 边际吸引力 A(t) = A_0 * exp(-delta*t) 衰减
4. 成本 C(t) = C_base + C_inc * t 递增

分析：dU/dT = A(T) - C(T) - r*exp(-rT)*V_maint*V_factor
                + gamma_rel * exp(-rT) * (d/accumulated_dT) * V_factor

第三项 d(accumulated_burst)/dT = A_0 * exp(-delta*T) = A(T)

所以：dU/dT = A(T) - C(T) - r*exp(-rT)*V_maint*V_factor
             + gamma_rel * exp(-rT) * A(T) * V_factor

FOC: A(T) * [1 + gamma_rel * exp(-rT) * V_factor]
      = C(T) + r * exp(-rT) * V_maint * V_factor

当 V_factor 增大时：
- 左边增长（信号吸引力的价值增加了，因为有更高的关系质量回报）
- 右边也增长（延迟成本增加）
- 但左边的 A(T) 项乘以 gamma_rel，影响更大
- -> 更高的 V_future -> 更高的 T* 使得 A(T) 较低但仍能平衡

注意：gamma_rel 是放大因子，使得 V_future 的变化主要影响左边
"""

import numpy as np
import json

def compute_utility_v5(T, V_future, params):
    """计算 U(T)

    params: (A_0, delta, C_base, C_inc, r, V_maint, gamma_rel)
    """
    A_0, delta, C_base, C_inc, r, V_maint, gamma_rel = params
    V_factor = V_future / (1 + V_future)

    t_vals = np.linspace(0, T - 1, T)
    A_vals = A_0 * np.exp(-delta * t_vals)
    C_vals = C_base + C_inc * t_vals

    accumulated_A = np.sum(A_vals)
    net_benefit = np.sum(A_vals - C_vals)

    # 长期价值：基础 + 关系质量增强
    rel_quality = min(1.0, accumulated_A)
    V_long = V_maint * (1.0 + gamma_rel * rel_quality) * V_factor

    U_total = net_benefit + np.exp(-r * T) * V_long

    return U_total, net_benefit, np.exp(-r * T) * V_long


def main():
    print("=" * 60)
    print("D38 实验重新设计 v5 — 关系质量依赖的 V_future 模型")
    print("=" * 60)

    # 参数：A_0 > C_base at t=0, A(t) decays, C(t) rises
    # -> interior marginal optimum
    base_params = (0.15, 0.03, 0.02, 0.0005, 0.005, 50.0, 5.0)

    V_future_values = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    results = {}

    for V_future in V_future_values:
        utilities = []
        for T in range(1, 365):
            U_total, U_net, U_long = compute_utility_v5(T, V_future, base_params)
            utilities.append((T, U_total))

        best_idx = max(range(len(utilities)), key=lambda i: utilities[i][1])
        best_T, best_U = utilities[best_idx]

        results[f'V_{V_future}'] = {
            'optimal_T': best_T,
            'best_utility': round(best_U, 4),
        }

        print(f"  V_future={V_future:6.1f} -> T*={best_T:3d}, U*={best_U:10.2f}")

    T_stars = [results[f'V_{v}']['optimal_T'] for v in V_future_values]
    trend_increasing = all(T_stars[i] <= T_stars[i+1] for i in range(len(T_stars)-1))
    print(f"\n  T* 随 V_future 递增: {'YES' if trend_increasing else 'NO'}")

    # Detailed landscape for V=5 and V=50
    for V_label in [5.0, 50.0]:
        print(f"\n  Utility landscape (V={V_label}):")
        print(f"  T    | U_net   | U_long  | U_total | marginal_net")
        for T_h in [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 150, 200, 250, 300, 364]:
            U_total, U_net, U_long = compute_utility_v5(T_h, V_label, base_params)
            marginal_A = base_params[0] * np.exp(-base_params[1] * (T_h - 1))
            marginal_C = base_params[2] + base_params[3] * (T_h - 1)
            marginal_net = marginal_A - marginal_C
            print(f"  {T_h:3d} | {U_net:8.2f} | {U_long:8.2f} | {U_total:8.2f} | {marginal_net:+.4f}")

    output = {
        'experiment': 'D38-redesign-v5',
        'model': 'V_future_through_relationship_quality',
        'corrections': [
            'U(T) = int(A-C) + exp(-rT) * V_maint * (1 + gamma_rel * rel_quality) * V_factor',
            'rel_quality = accumulated_signal_burst (bounded)',
            'V_future affects relationship quality value, not just discount',
            'gamma_rel = 5 (strong relationship quality multiplier)',
        ],
        'params': {
            'A_0': base_params[0],
            'delta': base_params[1],
            'C_base': base_params[2],
            'C_inc': base_params[3],
            'r': base_params[4],
            'V_maint': base_params[5],
            'gamma_rel': base_params[6],
        },
        'results': results,
        'trend_increasing': trend_increasing,
    }

    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d38-redesign-v5-results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[Save] chimera_lab/d38-redesign-v5-results.json")


if __name__ == '__main__':
    main()
