#!/usr/bin/env python3
"""
D38 实验重新设计 v4：正确的贸易-off结构

核心理论：总效用 = honeymoon期净收益 + 折现的长期关系价值
U(T) = int_0^T [A(t) - C(t)] dt + exp(-rT) * V_long(rel_quality)

关键设计：
1. Honeymoon期吸引力和成本：
   A(t) = A_0 * exp(-delta*t) — 新奇性衰减
   C(t) = C_base + C_inc * t — 维持成本递增
   -> 净收益 A(t)-C(t) 会变为负值

2. rel_quality 依赖于 accumulated net_attraction (有上限)
   rel_quality = min(Q_max, kappa * int_0^T A(t) dt)

3. V_long 依赖 rel_quality
   V_long = V_base * (1 + gamma_rel * rel_quality)

4. 折现因子 exp(-rT) 表示延迟进入稳定期的成本

最优 T 满足：dU/dT = 0
=> A(T) - C(T) + exp(-rT) * dV_long/dT = 0
=> A(T) - C(T) = -r * V_long(exp(-rT)) + exp(-rT) * dV_long/dT

简化理解：当 marginal_honeymoon_benefit < marginal_long_term_loss 时停止
"""

import numpy as np
import json

def compute_utility_landscape(T_max, V_future, params):
    """计算 U(T) 在 T=1..T_max 的完整景观

    params: (A_0, delta, C_base, C_inc, r, V_base, kappa, gamma_rel)
    """
    A_0, delta, C_base, C_inc, r, V_base, kappa, gamma_rel = params

    accumulated_A = 0.0
    results = []

    for T in range(1, T_max + 1):
        # 累积吸引力 (用于关系质量)
        # A(t) = A_0 * exp(-delta * t)
        t_vals = np.linspace(0, T-1, T)
        A_vals = A_0 * np.exp(-delta * t_vals)
        accumulated_A = np.sum(A_vals)

        # Honeymoon 净收益
        net_benefit = np.sum(A_vals - (C_base + C_inc * t_vals))

        # 关系质量（有上限）
        rel_quality = min(1.0, kappa * accumulated_A)

        # 长期价值
        V_long = V_base * (1 + gamma_rel * rel_quality) * (V_future / (1 + V_future))

        # 折现
        U_total = net_benefit + np.exp(-r * T) * V_long

        # 边际分析
        marginal_A = A_0 * np.exp(-delta * (T-1))  # 第T天的吸引力
        marginal_C = C_base + C_inc * (T-1)         # 第T天的成本
        marginal_net = marginal_A - marginal_C

        results.append({
            'T': T,
            'U_net': float(net_benefit),
            'U_long': float(np.exp(-r * T) * V_long),
            'U_total': float(U_total),
            'marginal_A': float(marginal_A),
            'marginal_C': float(marginal_C),
            'marginal_net': float(marginal_net),
            'rel_quality': float(rel_quality),
        })

    return results


def main():
    print("=" * 60)
    print("D38 实验重新设计 v4 — 正确贸易-off结构")
    print("=" * 60)

    # 参数：让 marginal benefit 最终 < marginal cost
    base_params = (0.15, 0.03, 0.02, 0.0005, 0.005, 50.0, 0.5, 3.0)

    V_future_values = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    results = {}

    for V_future in V_future_values:
        landscape = compute_utility_landscape(364, V_future, base_params)

        best = max(landscape, key=lambda x: x['U_total'])
        best_T = best['T']
        best_U = best['U_total']

        results[f'V_{V_future}'] = {
            'optimal_T': best_T,
            'best_utility': round(best_U, 4),
        }

        print(f"  V_future={V_future:6.1f} -> T*={best_T:3d}, U*={best_U:10.2f}")
        print(f"    marginal_A(T*)={best['marginal_A']:.4f}, marginal_C(T*)={best['marginal_C']:.4f}, net={best['marginal_net']:.4f}")

    T_stars = [results[f'V_{v}']['optimal_T'] for v in V_future_values]
    trend_increasing = all(T_stars[i] <= T_stars[i+1] for i in range(len(T_stars)-1))
    print(f"\n  T* 随 V_future 递增: {'YES' if trend_increasing else 'NO'}")

    # 详细 landscape (V=5 和 V=50)
    for V_label in [5.0, 50.0]:
        landscape = compute_utility_landscape(364, V_label, base_params)
        print(f"\n  Utility landscape (V={V_label}):")
        print(f"  T    | U_net   | U_long  | U_total | marg_A | marg_C | marg_net")
        for row in [0, 4, 9, 19, 29, 49, 79, 99, 129, 159, 199, 249, 299, 349, 363]:
            if row < len(landscape):
                r = landscape[row]
                print(f"  {r['T']:3d} | {r['U_net']:8.2f} | {r['U_long']:8.2f} | {r['U_total']:8.2f} | {r['marginal_A']:.4f} | {r['marginal_C']:.4f} | {r['marginal_net']:.4f}")

    output = {
        'experiment': 'D38-redesign-v4',
        'model': 'utility_landscape_with_marginal_analysis',
        'corrections': [
            'Proper honeymoon vs stable relationship trade-off',
            'A(t) = A_0 * exp(-delta*t) — novelty decay',
            'C(t) = C_base + C_inc*t — rising cost',
            'V_long depends on accumulated relationship quality (bounded)',
            'Marginal analysis at optimum',
        ],
        'params': {
            'A_0': base_params[0],
            'delta': base_params[1],
            'C_base': base_params[2],
            'C_inc': base_params[3],
            'r': base_params[4],
            'V_base': base_params[5],
            'kappa': base_params[6],
            'gamma_rel': base_params[7],
        },
        'results': results,
        'trend_increasing': trend_increasing,
    }

    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d38-redesign-v4-results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[Save] chimera_lab/d38-redesign-v4-results.json")


if __name__ == '__main__':
    main()
