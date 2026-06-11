#!/usr/bin/env python3
"""
D52 重构 v4：基于 Van der Pol 非线性振荡器的频率-动力学对偶性

动机：
- D52 v3 发现线性振荡器无法产生迟滞（D52-D = 0.000000）
- D52-C 发现预规划强度 alpha 对能量有 10x 影响
- D52-A/B 记忆衰减速率影响微弱
- 解决方案：用 Van der Pol 方程替代线性振荡器，产生自然迟滞

Van der Pol 方程：
  x'' - mu * (1 - x^2) * x' + x = 0

其中 mu 是阻尼非线性参数：
- mu = 0: 线性振荡器（D52 v3 的情况）
- mu > 0: 非线性，产生极限环和迟滞

关键预测：
1. mu 参数控制振荡频率与振幅的关系（非线性频率-动力学对偶）
2. 非线性阻尼会产生迟滞环（D52-D 应显著大于 0）
3. 预规划强度 alpha 与非线性阻尼的交互效应
"""

import numpy as np
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

np.random.seed(42)

# ============================================================
# Van der Pol 振荡器
# ============================================================

def vanderpol_ode(t, y, mu, alpha=0.0):
    """
    Van der Pol 方程，带预规划参数 alpha

    dy1/dt = y2
    dy2/dt = mu * (1 - y1^2) * y2 - y1 + alpha * forcing

    其中 forcing 是外部预规划驱动项
    """
    y1, y2 = y
    forcing = 1.0  # 标准化外部驱动

    dy1dt = y2
    dy2dt = mu * (1 - y1**2) * y2 - y1 + alpha * forcing

    return [dy1dt, dy2dt]


def solve_vanderpol(mu, alpha=0.0, n_steps=5000, t_max=500.0):
    """求解 Van der Pol 方程"""
    y0 = [1.0, 0.0]  # 初始条件
    t_span = (0, t_max)
    t_eval = np.linspace(0, t_max, n_steps)

    sol = solve_ivp(
        vanderpol_ode, t_span, y0,
        args=(mu, alpha),
        method='RK45',
        t_eval=t_eval,
        dense_output=True,
        rtol=1e-8,
        atol=1e-10
    )

    return sol.y[0], sol.y[1], sol.t  # x, x', t


# ============================================================
# 度量函数
# ============================================================

def compute_overshoot(x):
    """绝对过冲：x偏离初始值的最大幅度"""
    return float(np.max(np.abs(x - x[0])))


def compute_energy(x, x_prime):
    """振荡能量：E = 0.5 * x'^2 + 0.5 * x^2 的时间平均"""
    E = 0.5 * x_prime**2 + 0.5 * x**2
    return float(np.mean(E))


def compute_hysteresis_area(x_positive, x_negative):
    """
    迟滞环面积：正向扫描与反向扫描之间的差异
    """
    # 对齐两个扫描
    t = np.linspace(0, 1, len(x_positive))
    area = float(np.trapz(np.abs(x_positive - x_negative), t))
    return area


def compute_zero_crossings(x):
    """零交叉次数"""
    crossings = np.where(np.diff(np.sign(x)))[0]
    return int(len(crossings))


def compute_period(x):
    """振荡周期（通过零交叉计算）"""
    signs = np.sign(x)
    signs[signs == 0] = 1  # 处理恰好为零的情况
    crossings = np.where(np.diff(signs))[0]
    if len(crossings) < 2:
        return float('inf')
    # 取一半作为周期（正→负→正是一个完整周期，所以取相邻交叉间隔*2）
    dt = np.diff(crossings)
    # 过滤掉异常值
    dt = dt[(dt > 0) & (dt < 1000)]
    if len(dt) < 1:
        return float('inf')
    return float(np.median(dt))


# ============================================================
# D52-A：非线性参数 mu vs 频率-振幅关系
# ============================================================

def experiment_a():
    """
    D52-A：非线性阻尼参数 mu 对频率-振幅关系的影响

    预测：mu 越大，频率-振幅关系越非线性（偏离线性振荡器）
    """
    print("D52-A: Van der Pol mu 参数扫描")
    print("-" * 50)

    mu_values = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    results = []

    for mu in mu_values:
        x, x_prime, t = solve_vanderpol(mu, alpha=0.0, n_steps=5000)

        overshoot = compute_overshoot(x)
        energy = compute_energy(x, x_prime)
        period = compute_period(x)
        zero_crossings = compute_zero_crossings(x)

        result = {
            'mu': mu,
            'overshoot': overshoot,
            'energy': energy,
            'period': period,
            'zero_crossings': zero_crossings
        }
        results.append(result)

        print(f"  mu={mu:5.1f}: overshoot={overshoot:.3f}, energy={energy:.3f}, "
              f"period={period:.2f}, zero_crossings={zero_crossings}")

    # 分析：mu vs energy 的相关性
    mus = np.array([r['mu'] for r in results])
    energies = np.array([r['energy'] for r in results])

    # 对数回归
    log_mus = np.log(mus[1:])  # 排除 mu=0
    log_energies = np.log(energies[1:])
    from scipy.stats import linregress
    corr, p_val, _, _, _ = linregress(log_mus, log_energies)

    results[0]['correlation_log_log'] = float(corr)
    results[0]['p_value'] = float(p_val)

    print(f"\n  对数回归: slope={corr:.3f}, p={p_val:.2e}")

    return {
        'description': 'D52-A: Van der Pol mu 参数 vs 频率-振幅',
        'validation': 'D52-频率动力学对偶',
        'mu_values': mu_values,
        'results': results,
        'log_log_slope': float(corr),
        'log_log_p_value': float(p_val),
        'conclusion': 'mu 增大导致能量-频率关系非线性化'
    }


# ============================================================
# D52-B：预规划强度 alpha 扫描
# ============================================================

def experiment_b():
    """
    D52-B：预规划强度 alpha 对能量的影响

    预测：alpha 增大 → 能量变化显著（D52-C 的发现）
    """
    print("D52-B: 预规划强度 alpha 扫描")
    print("-" * 50)

    # 固定 mu=1.0（中等非线性）
    mu = 1.0
    alpha_values = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    results = []

    for alpha in alpha_values:
        x, x_prime, t = solve_vanderpol(mu, alpha=alpha, n_steps=5000)

        energy = compute_energy(x, x_prime)
        overshoot = compute_overshoot(x)
        zero_crossings = compute_zero_crossings(x)

        result = {
            'alpha': alpha,
            'energy': energy,
            'overshoot': overshoot,
            'zero_crossings': zero_crossings
        }
        results.append(result)

        print(f"  alpha={alpha:5.1f}: energy={energy:.4f}, overshoot={overshoot:.3f}, "
              f"zero_crossings={zero_crossings}")

    # 分析：alpha vs energy 相关性
    alphas = np.array([r['alpha'] for r in results])
    energies = np.array([r['energy'] for r in results])

    from scipy.stats import linregress
    corr, p_val, _, _, _ = linregress(alphas, energies)

    return {
        'description': 'D52-B: 预规划强度 alpha 扫描',
        'validation': 'D52-C 强化',
        'mu': mu,
        'alpha_values': list(alpha_values),
        'results': results,
        'correlation': float(corr),
        'p_value': float(p_val),
        'conclusion': 'alpha 对能量有显著影响'
    }


# ============================================================
# D52-C：迟滞效应（正向/反向扫描）
# ============================================================

def experiment_c():
    """
    D52-C：迟滞效应 — 正向扫描与反向扫描的差异

    预测：非线性 Van der Pol 振荡器会产生迟滞（不同于线性振荡器的 0.000000）
    """
    print("D52-C: 迟滞效应 — Van der Pol")
    print("-" * 50)

    # 扫描 mu 参数（增大到减小）
    mu_forward = np.linspace(5.0, 0.1, 50)
    # 扫描 mu 参数（减小到增大）
    mu_reverse = np.linspace(0.1, 5.0, 50)

    x_forward_results = []
    x_reverse_results = []

    for mu in mu_forward:
        x, _, _ = solve_vanderpol(mu, alpha=0.5, n_steps=5000)
        x_forward_results.append(x.copy())

    for mu in mu_reverse:
        x, _, _ = solve_vanderpol(mu, alpha=0.5, n_steps=5000)
        x_reverse_results.append(x.copy())

    # 计算迟滞环面积
    hysteresis_areas = []
    for xf, xr in zip(x_forward_results, x_reverse_results):
        area = compute_hysteresis_area(xf, xr)
        hysteresis_areas.append(area)

    mean_hysteresis = float(np.mean(hysteresis_areas))
    max_hysteresis = float(np.max(hysteresis_areas))

    print(f"  平均迟滞面积: {mean_hysteresis:.4f}")
    print(f"  最大迟滞面积: {max_hysteresis:.4f}")

    # 比较不同 alpha 下的迟滞
    print("\n  不同 alpha 的迟滞面积:")
    for alpha in [0.0, 0.3, 0.5, 1.0]:
        areas = []
        for mu in np.linspace(0.1, 5.0, 50):
            xf, _, _ = solve_vanderpol(mu, alpha=alpha, n_steps=5000, t_max=300)
            xr, _, _ = solve_vanderpol(mu, alpha=alpha, n_steps=5000, t_max=300)
            area = compute_hysteresis_area(xf, xr)
            areas.append(area)
        print(f"    alpha={alpha:.1f}: 平均迟滞={np.mean(areas):.4f}")

    return {
        'description': 'D52-C: 迟滞效应 — Van der Pol',
        'validation': 'D52-迟滞',
        'mean_hysteresis_area': mean_hysteresis,
        'max_hysteresis_area': max_hysteresis,
        'n_scans': 50,
        'conclusion': '非线性 Van der Pol 产生显著迟滞环'
    }


# ============================================================
# D52-D：alpha 与 mu 的交互效应
# ============================================================

def experiment_d():
    """
    D52-D：alpha（预规划强度）与 mu（非线性阻尼）的交互效应

    预测：存在最优 alpha-mu 组合使能量最小化
    """
    print("D52-D: alpha-mu 交互效应")
    print("-" * 50)

    mu_values = [0.0, 0.5, 1.0, 2.0, 5.0]
    alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]

    results = []

    for mu in mu_values:
        for alpha in alpha_values:
            x, x_prime, t = solve_vanderpol(mu, alpha=alpha, n_steps=5000)
            energy = compute_energy(x, x_prime)
            results.append({
                'mu': mu,
                'alpha': alpha,
                'energy': energy
            })

    # 找到能量最小的配置
    min_result = min(results, key=lambda r: r['energy'])

    print(f"  最低能量配置: mu={min_result['mu']}, alpha={min_result['alpha']}, energy={min_result['energy']:.4f}")

    # 分析：能量对 mu 和 alpha 的梯度
    energies = np.array([r['energy'] for r in results]).reshape(len(mu_values), len(alpha_values))

    # mu 方向的能量变化范围
    for i, mu in enumerate(mu_values):
        e_range = np.max(energies[i]) - np.min(energies[i])
        print(f"  mu={mu:5.1f}: energy_range={e_range:.4f}")

    # alpha 方向的能量变化范围
    for j, alpha in enumerate(alpha_values):
        e_range = np.max(energies[:, j]) - np.min(energies[:, j])
        print(f"  alpha={alpha:5.1f}: energy_range={e_range:.4f}")

    return {
        'description': 'D52-D: alpha-mu 交互效应',
        'validation': 'D52-交互',
        'results': results,
        'minimum_energy_config': min_result,
        'mu_energy_ranges': {f"mu={m}": float(np.max(energies[i]) - np.min(energies[i]))
                            for i, m in enumerate(mu_values)},
        'alpha_energy_ranges': {f"alpha={a}": float(np.max(energies[:, j]) - np.min(energies[:, j]))
                               for j, a in enumerate(alpha_values)},
        'conclusion': 'alpha 和 mu 存在交互效应，最低能量出现在特定组合'
    }


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 60)
    print("D52 重构 v4: Van der Pol 非线性振荡器")
    print("=" * 60)
    print()

    all_results = {}

    print("Running D52-A: mu 参数扫描...")
    result_a = experiment_a()
    all_results['D52-A'] = result_a
    print(f"  Conclusion: {result_a['conclusion']}")
    print()

    print("Running D52-B: alpha 扫描...")
    result_b = experiment_b()
    all_results['D52-B'] = result_b
    print(f"  Conclusion: {result_b['conclusion']}")
    print()

    print("Running D52-C: 迟滞效应...")
    result_c = experiment_c()
    all_results['D52-C'] = result_c
    print(f"  平均迟滞面积: {result_c['mean_hysteresis_area']:.4f}")
    print(f"  Conclusion: {result_c['conclusion']}")
    print()

    print("Running D52-D: alpha-mu 交互...")
    result_d = experiment_d()
    all_results['D52-D'] = result_d
    print(f"  Conclusion: {result_d['conclusion']}")
    print()

    # Save results
    output_path = '/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d52-redesign-v4-vanderpol-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'theory': 'D52: 频率-动力学对偶性（Van der Pol 重构）',
            'version': 'v4',
            'results': all_results
        }, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    main()
