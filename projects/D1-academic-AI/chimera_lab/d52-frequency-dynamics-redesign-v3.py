#!/usr/bin/env python3
"""
D52 重新设计 v3：修复指标和实验设计

核心修正：
1. 过冲用绝对值衡量（而非除以接近零的稳态）
2. 恢复时间检测"收敛到x内"（而非收敛到稳态的x比例）
3. n_steps=5000 确保观测完整收敛动力学
4. 理论测试：记忆核衰减速率 vs 振荡阻尼/频率

D52 核心理论：记忆核衰减速率 μ(t) = μ₀·exp(-λt) 控制探索行为的
阻尼振荡动力学。衰减速率 λ 越大（短记忆）→ 阻尼越小 → 振荡越多。
"""

import numpy as np
import json

def exponential_memory_kernel(tau, mu_0, decay_rate):
    return mu_0 * np.exp(-decay_rate * tau)


def simulate_oscillator(n_steps, zeta, omega_0, mu_0, decay_rate, memory_buffer=20):
    """记忆阻尼振荡器"""
    x = np.zeros(n_steps)
    v = np.zeros(n_steps)
    x[0], v[0] = 1.0, 0.0
    v_history = [v[0]]
    dt = 0.01

    for t in range(1, n_steps):
        # 记忆阻尼
        mu_eff = 0.0
        n_hist = min(len(v_history), memory_buffer)
        for tau_idx in range(n_hist):
            mu_eff += exponential_memory_kernel(tau_idx, mu_0, decay_rate) * v_history[-(tau_idx+1)]
        mu_eff /= max(n_hist, 1)

        zeta_eff = zeta + mu_eff / (2 * omega_0)

        k1_x = v[t-1]
        k1_v = -(2 * zeta_eff * omega_0) * v[t-1] - omega_0**2 * x[t-1]
        k2_x = v[t-1] + 0.5 * dt * k1_v
        k2_v = -(2 * zeta_eff * omega_0) * (v[t-1] + 0.5 * dt * k1_v) - omega_0**2 * (x[t-1] + 0.5 * dt * k1_x)
        k3_x = v[t-1] + 0.5 * dt * k2_v
        k3_v = -(2 * zeta_eff * omega_0) * (v[t-1] + 0.5 * dt * k2_v) - omega_0**2 * (x[t-1] + 0.5 * dt * k3_x)
        k4_x = v[t-1] + dt * k3_v
        k4_v = -(2 * zeta_eff * omega_0) * (v[t-1] + dt * k3_v) - omega_0**2 * (x[t-1] + dt * k3_x)

        x[t] = x[t-1] + dt * (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
        v[t] = v[t-1] + dt * (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6

        v_history.append(v[t])
        if len(v_history) > memory_buffer:
            v_history.pop(0)

    return x, v


def compute_absolute_overshoot(x):
    """绝对过冲：x偏离初始值的最大幅度"""
    return float(np.max(np.abs(x - x[0])))


def compute_convergence_time(x, tol=0.01):
    """收敛时间：首次连续50步 |x(t)| < tol"""
    n = len(x)
    for t in range(n - 50):
        if np.all(np.abs(x[t:t+50]) < tol):
            return float(t)
    return float(n)


def compute_oscillation_characteristics(x):
    """振荡特性：周期和衰减时间常数"""
    # 找过零点
    crossings = np.where(np.diff(np.sign(x)))[0]
    if len(crossings) < 4:
        return {'period': None, 'num_zeros': 0, 'damped': False}

    intervals = np.diff(crossings)
    period = float(np.median(intervals)) * 0.01  # 转换为时间单位

    # 衰减常数：拟合包络线
    peaks = []
    for i in range(1, len(crossings) - 1):
        t_idx = crossings[i]
        if t_idx < len(x) and t_idx > 0:
            peaks.append(abs(x[t_idx]))

    if len(peaks) >= 3:
        log_peaks = np.log(np.array(peaks[:min(10, len(peaks))]))
        if np.std(log_peaks) > 1e-10:
            slope = np.polyfit(np.arange(len(log_peaks)), log_peaks, 1)[0]
            tau = -1.0 / slope if slope < 0 else float('inf')
        else:
            tau = float('inf')
        damped = abs(slope) > 0.001
    else:
        tau = None
        damped = False

    return {
        'period': round(period, 6),
        'num_zeros': len(crossings),
        'damped': damped,
        'decay_constant': round(float(tau), 6) if tau is not None else None,
    }


def main():
    print("=" * 60)
    print("D52 重新设计 v3 — 修正指标")
    print("=" * 60)

    n_steps = 5000
    zeta_base = 0.3
    omega_0 = 2.0

    # ========== D52-A：记忆核衰减速率 vs 过冲 ==========
    print("\n[D52-A] 记忆核衰减速率 vs 绝对过冲")
    configs = [
        ('no_memory', 0.0, 10.0),
        ('fast_decay_0.5', 0.1, 0.5),
        ('fast_decay_1.0', 0.2, 1.0),
        ('medium_decay_0.1', 0.2, 0.1),
        ('medium_decay_0.05', 0.3, 0.05),
        ('slow_decay_0.02', 0.4, 0.02),
    ]

    results_a = {}
    for name, mu_0, decay_rate in configs:
        x, v = simulate_oscillator(n_steps, zeta_base, omega_0, mu_0, decay_rate)

        overshoot = compute_absolute_overshoot(x)
        conv_time = compute_convergence_time(x)
        osc = compute_oscillation_characteristics(x)

        results_a[name] = {
            'mu_0': mu_0,
            'decay_rate': decay_rate,
            'absolute_overshoot': round(overshoot, 6),
            'convergence_time': round(conv_time, 2),
            'oscillation': osc,
        }
        print(f"  {name:20s}: overshoot={overshoot:.6f}, conv={conv_time:.0f}, "
              f"zeros={osc['num_zeros']}, period={osc.get('period', 'N/A')}")

    # ========== D52-B：连续衰减速率扫描 ==========
    print("\n[D52-B] 连续衰减速率扫描")
    decay_scan = np.linspace(0.01, 2.0, 20)
    overshoots = []
    conv_times = []
    periods = []

    for dr in decay_scan:
        x, v = simulate_oscillator(n_steps, zeta_base, omega_0, 0.2, dr)
        overshoots.append(compute_absolute_overshoot(x))
        conv_times.append(compute_convergence_time(x))
        osc = compute_oscillation_characteristics(x)
        periods.append(osc.get('period', None))

    print(f"  过冲范围: [{min(overshoots):.6f}, {max(overshoots):.6f}]")
    print(f"  收敛时间范围: [{min(conv_times):.0f}, {max(conv_times):.0f}]")

    # 相关性
    corr_overshoot = np.corrcoef(decay_scan, overshoots)[0, 1] if np.std(overshoots) > 1e-10 else 0.0
    corr_conv = np.corrcoef(decay_scan, conv_times)[0, 1] if np.std(conv_times) > 1e-10 else 0.0
    print(f"  过冲 vs 衰减速率相关性: {corr_overshoot:.4f}")
    print(f"  收敛时间 vs 衰减速率相关性: {corr_conv:.4f}")

    # ========== D52-C：预规划 vs 即时回调（用阻尼系数衡量）==========
    print("\n[D52-C] 预规划代价 vs 振荡能量")
    alphas = [0.1, 0.3, 0.5, 0.7, 1.0]
    tradeoff = []
    for alpha in alphas:
        x, v = simulate_oscillator(n_steps, zeta_base * alpha, omega_0, 0.2, 0.1)
        energy = float(np.mean(v**2))
        tradeoff.append({'alpha': alpha, 'energy': round(energy, 8), 'oscillation': compute_oscillation_characteristics(x)})
        print(f"  alpha={alpha:.1f}: energy={energy:.8f}, zeros={compute_oscillation_characteristics(x)['num_zeros']}")

    # ========== D52-D：滞后效应（参数正向/反向扫描）==========
    print("\n[D52-D] 滞后效应（zeta 正向/反向扫描）")
    zetas = np.linspace(0.1, 1.0, 15)
    increase_vals = []
    decrease_vals = []

    for z in zetas:
        x, _ = simulate_oscillator(n_steps, z, omega_0, 0.2, 0.1)
        # 在 t=500 处的 x 值（代表系统记忆）
        increase_vals.append(float(x[500]))

    for z in reversed(zetas):
        x, _ = simulate_oscillator(n_steps, z, omega_0, 0.2, 0.1)
        decrease_vals.append(float(x[500]))

    hysteresis = np.sum(np.abs(np.array(increase_vals) - np.array(decrease_vals[::-1]))) / len(zetas)
    print(f"  滞后幅度: {hysteresis:.6f}")

    # 保存结果
    output = {
        'experiment': 'D52-redesign-v3',
        'n_steps': n_steps,
        'params': {'zeta_base': zeta_base, 'omega_0': omega_0},
        'D52-A': results_a,
        'D52-B': {
            'decay_scan': [round(d, 4) for d in decay_scan],
            'overshoot_scan': [round(o, 6) for o in overshoots],
            'conv_scan': [round(c, 2) for c in conv_times],
            'corr_overshoot_decay': round(float(corr_overshoot), 4),
            'corr_conv_decay': round(float(corr_conv), 4),
        },
        'D52-C': tradeoff,
        'D52-D': {
            'hysteresis': round(float(hysteresis), 6),
            'increase_phase': [round(v, 8) for v in increase_vals],
            'decrease_phase': [round(v, 8) for v in decrease_vals],
        },
    }

    def fix_json(obj):
        if isinstance(obj, dict):
            return {k: fix_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [fix_json(x) for x in obj]
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, np.generic):
            return obj.item()
        else:
            return obj

    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d52-redesign-v3-results.json', 'w') as f:
        json.dump(fix_json(output), f, indent=2)
    print(f"\n[Save] chimera_lab/d52-redesign-v3-results.json")


if __name__ == '__main__':
    main()
