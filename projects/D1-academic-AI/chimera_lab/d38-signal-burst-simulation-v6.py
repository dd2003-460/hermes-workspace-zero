#!/usr/bin/env python3
"""
D38 实验重新设计 v6：V_future 通过信号振幅影响 honeymoon 动力学

核心理论：高价值关系 → 更大初始信号膨胀（A_0 随 V_future 增长）
信号振幅放大策略：与其延长膨胀时间，不如在短期内更高强度展示

A_0(V) = A_base * (1 + alpha * V_future/(1 + V_future))
-> 高 V_future 的 A_0 更大，产生更陡峭的边际曲线

同时：
- accumulated_burst 与 A_0^2 成正比（高振幅积累更快）
- 关系质量 = min(1, kappa * accumulated_burst)
- V_long = V_maint * (1 + gamma_rel * rel_quality) * V_factor

Trade-off:
- 高 A_0 -> 边际吸引力更强 -> 可以承受更长的 T（在边际变为负之前）
- 但高 A_0 也意味着高成本（维持高强度更难）
-> 产生不同的 optimal T*

理论预测：高 V_future -> 更高 A_0 -> 更"短而强"（T* 可能更短但效用更高）
或者：高 V_future -> 更强积累 -> T* 更长（建立更深关系）
让数据说话。
"""

import numpy as np
import json

def compute_landscape(T_max, V_future, params):
    """计算完整 U(T) 景观

    params: (A_base, delta, C_base, C_inc, r, V_maint, kappa, gamma_rel, alpha)
    alpha 控制 V_future 对振幅的放大
    """
    A_base, delta, C_base, C_inc, r, V_maint, kappa, gamma_rel, alpha = params

    V_factor = V_future / (1 + V_future)
    A_0 = A_base * (1 + alpha * V_factor)  # V_future 放大振幅

    results = []
    accumulated_A = 0.0

    for T in range(1, T_max + 1):
        t_vals = np.linspace(0, T - 1, T)
        A_vals = A_0 * np.exp(-delta * t_vals)
        C_vals = C_base + C_inc * t_vals

        accumulated_A = float(np.sum(A_vals))
        net_benefit = float(np.sum(A_vals - C_vals))

        # 关系质量
        rel_quality = min(1.0, kappa * accumulated_A)

        # 长期价值
        V_long = V_maint * (1.0 + gamma_rel * rel_quality) * V_factor
        U_long = float(np.exp(-r * T) * V_long)

        U_total = net_benefit + U_long
        marginal_net = float(A_0 * np.exp(-delta * (T - 1)) - (C_base + C_inc * (T - 1)))

        results.append({
            'T': T,
            'U_net': round(net_benefit, 4),
            'U_long': round(U_long, 4),
            'U_total': round(U_total, 4),
            'marginal_net': round(marginal_net, 4),
            'A_0': round(A_0, 4),
        })

    return results


def main():
    print("=" * 60)
    print("D38 实验重新设计 v6 — V_future 通过振幅影响")
    print("=" * 60)

    # 参数
    # A_base=0.15: 基础吸引力
    # delta=0.03: 衰减率
    # C_base=0.02, C_inc=0.0005: 成本
    # r=0.005: 折现率（较低，关系尺度）
    # V_maint=50: 基础长期价值
    # kappa=0.3: 累积到关系质量的转换率
    # gamma_rel=3: 关系质量对长期价值的增强
    # alpha=3: V_future 对振幅的放大系数（关键参数！）
    base_params = (0.15, 0.03, 0.02, 0.0005, 0.005, 50.0, 0.3, 3.0, 3.0)

    V_future_values = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    results = {}

    for V_future in V_future_values:
        landscape = compute_landscape(364, V_future, base_params)
        best = max(landscape, key=lambda x: x['U_total'])

        results[f'V_{V_future}'] = {
            'optimal_T': best['T'],
            'best_utility': best['U_total'],
            'A_0': best['A_0'],
        }

        print(f"  V_future={V_future:6.1f} -> T*={best['T']:3d}, U*={best['U_total']:10.2f}, A_0={best['A_0']:.3f}")

    T_stars = [results[f'V_{v}']['optimal_T'] for v in V_future_values]
    trend_increasing = all(T_stars[i] <= T_stars[i+1] for i in range(len(T_stars)-1))
    print(f"\n  T* 随 V_future 递增: {'YES' if trend_increasing else 'NO'}")
    print(f"  U* 随 V_future 递增: {'YES' if all(results[f'V_{V_future_values[i]}']['best_utility'] <= results[f'V_{V_future_values[i+1]}']['best_utility'] for i in range(len(V_future_values)-1)) else 'NO'}")

    # 详细 landscape (V=1 和 V=100)
    for V_label in [1.0, 100.0]:
        landscape = compute_landscape(364, V_label, base_params)
        print(f"\n  Utility landscape (V={V_label}, A_0={landscape[0]['A_0']:.3f}):")
        print(f"  T    | U_net   | U_long  | U_total | marg_net")
        for row_idx in [0, 4, 9, 14, 19, 24, 29, 39, 49, 60, 80, 100, 150, 200, 250, 300, 349]:
            if row_idx < len(landscape):
                r = landscape[row_idx]
                print(f"  {r['T']:3d} | {r['U_net']:8.2f} | {r['U_long']:8.2f} | {r['U_total']:8.2f} | {r['marginal_net']:+.4f}")

    output = {
        'experiment': 'D38-redesign-v6',
        'model': 'V_future_amplifies_honeymoon_signal',
        'key_mechanism': 'A_0(V) = A_base * (1 + alpha * V/(1+V))',
        'results': results,
        'trend_increasing': trend_increasing,
        'params': {
            'A_base': base_params[0],
            'delta': base_params[1],
            'C_base': base_params[2],
            'C_inc': base_params[3],
            'r': base_params[4],
            'V_maint': base_params[5],
            'kappa': base_params[6],
            'gamma_rel': base_params[7],
            'alpha': base_params[8],
        },
    }

    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d38-redesign-v6-results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[Save] chimera_lab/d38-redesign-v6-results.json")


if __name__ == '__main__':
    main()
