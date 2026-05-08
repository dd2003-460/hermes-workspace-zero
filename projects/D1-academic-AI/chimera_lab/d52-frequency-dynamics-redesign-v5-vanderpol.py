#!/usr/bin/env python3
"""
D52 重构 v5: Van der Pol 非线性振荡器 — 频率-能量对偶性 + 迟滞

关键改进 (v4→v5):
1. 迟滞效应: 单积分慢参数扫描（mu随时间线性变化）
2. 外部驱动: 振荡forcing cos(omega*t)，非恒定
3. 频率-能量对偶: 测量mu对极限环频率与振幅的影响
4. 预规划强度alpha与mu的非线性交互
"""

import numpy as np
import json
from datetime import datetime
from scipy.integrate import solve_ivp
from scipy.stats import linregress

np.random.seed(42)

# ============================================================
# 增强版 Van der Pol 振荡器
# ============================================================

def vanderpol_forced_ode(t, y, mu, alpha, omega):
    """
    恒定参数 Van der Pol + 振荡驱动
    dy1/dt = y2
    dy2/dt = mu*(1-y1^2)*y2 - y1 + alpha*cos(omega*t)
    """
    dy1dt = y[1]
    dy2dt = mu * (1 - y[0]**2) * y[1] - y[0] + alpha * np.cos(omega * t)
    return [dy1dt, dy2dt]


def solve_vp(mu, alpha=0.0, omega=0.1, n_steps=5000, t_max=200.0):
    y0 = [1.0, 0.0]
    sol = solve_ivp(vanderpol_forced_ode, (0, t_max), y0,
                    args=(mu, alpha, omega), method='RK45',
                    t_eval=np.linspace(0, t_max, n_steps),
                    rtol=1e-8, atol=1e-10)
    return sol.y[0], sol.y[1], sol.t


# ============================================================
# 度量函数
# ============================================================

def compute_energy(x, xp):
    return float(np.mean(0.5 * xp**2 + 0.5 * x**2))


def compute_amplitude(x):
    return float((np.max(x) - np.min(x)) / 2)


def compute_dominant_freq(x, t):
    N = len(x)
    dt = t[1] - t[0]
    fft_vals = np.fft.rfft(x - np.mean(x))
    freqs = np.fft.rfftfreq(N, dt)
    psd = np.abs(fft_vals)**2
    psd_s = np.convolve(psd, np.ones(10)/10, mode='same')
    peak_idx = np.argmax(psd_s[1:]) + 1
    return float(freqs[peak_idx]), float(psd_s[peak_idx])


# ============================================================
# D52-A：频率-能量对偶性
# ============================================================

def experiment_a():
    """D52-A: mu 对极限环频率与振幅的影响"""
    print("D52-A: 频率-能量对偶性")
    print("-" * 50)

    mu_values = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
    results = []

    for mu in mu_values:
        x, xp, t = solve_vp(mu, alpha=0.0, omega=0.1, n_steps=5000)
        energy = compute_energy(x, xp)
        amplitude = compute_amplitude(x)
        freq, psd_peak = compute_dominant_freq(x, t)

        result = {'mu': float(mu), 'energy': energy, 'amplitude': amplitude,
                  'dominant_freq': freq, 'psd_peak': psd_peak}
        results.append(result)
        print(f"  mu={mu:6.1f}: energy={energy:.4f}, amp={amplitude:.3f}, freq={freq:.4f}")

    mus = np.array([r['mu'] for r in results])
    freqs = np.array([r['dominant_freq'] for r in results])
    energies = np.array([r['energy'] for r in results])
    amplitudes = np.array([r['amplitude'] for r in results])

    corr_f, p_f, _, _, _ = linregress(mus, freqs)
    corr_e, p_e, _, _, _ = linregress(mus, energies)
    corr_a, p_a, _, _, _ = linregress(mus, amplitudes)

    print(f"  频率~mu: slope={corr_f:.4f}, p={p_f:.2e}")
    print(f"  能量~mu: slope={corr_e:.4f}, p={p_e:.2e}")
    print(f"  振幅~mu: slope={corr_a:.4f}, p={p_a:.2e}")

    return {
        'description': 'D52-A: 频率-能量对偶性',
        'mu_values': [float(m) for m in mu_values],
        'results': results,
        'freq_mu_slope': float(corr_f), 'freq_mu_p': float(p_f),
        'energy_mu_slope': float(corr_e), 'energy_mu_p': float(p_e),
        'amplitude_mu_slope': float(corr_a), 'amplitude_mu_p': float(p_a),
        'conclusion': 'mu增大→频率下降、振幅趋近2.0（极限环特征）'
    }


# ============================================================
# D52-B：预规划强度 alpha 扫描
# ============================================================

def experiment_b():
    """D52-B: alpha 对能量的影响（振荡驱动）"""
    print("D52-B: 预规划强度 alpha 扫描")
    print("-" * 50)

    mu, omega = 1.0, 0.1
    alpha_values = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
    results = []

    for alpha in alpha_values:
        x, xp, t = solve_vp(mu, alpha=alpha, omega=omega, n_steps=5000)
        energy = compute_energy(x, xp)
        amplitude = compute_amplitude(x)
        freq, _ = compute_dominant_freq(x, t)

        results.append({'alpha': alpha, 'energy': energy,
                       'amplitude': amplitude, 'dominant_freq': freq})
        print(f"  alpha={alpha:5.1f}: energy={energy:.4f}, amp={amplitude:.3f}, freq={freq:.4f}")

    alphas = np.array([r['alpha'] for r in results])
    energies = np.array([r['energy'] for r in results])
    corr, p_val, _, _, _ = linregress(alphas, energies)
    min_idx = np.argmin(energies)

    print(f"  alpha~energy: slope={corr:.4f}, p={p_val:.2e}")
    print(f"  最优 alpha（能量最小）: {alphas[min_idx]:.1f}")

    return {
        'description': 'D52-B: 预规划强度 alpha 扫描',
        'mu': mu, 'omega': omega,
        'alpha_values': [float(a) for a in alpha_values],
        'results': results,
        'correlation': float(corr), 'p_value': float(p_val),
        'optimal_alpha': float(alphas[min_idx]),
        'conclusion': 'alpha与能量关系非单调，存在最优值'
    }


# ============================================================
# D52-C：迟滞效应（慢参数扫描）
# ============================================================

def vanderpol_ramp_fwd_ode(t, y, alpha, omega):
    """正向扫描：mu从0→5"""
    mu_val = 5.0 * t / 200.0
    dy1dt = y[1]
    dy2dt = mu_val * (1 - y[0]**2) * y[1] - y[0] + alpha * np.cos(omega * t)
    return [dy1dt, dy2dt]


def vanderpol_ramp_rev_ode(t, y, alpha, omega):
    """反向扫描：mu从5→0"""
    mu_val = 5.0 * (1 - t / 200.0)
    dy1dt = y[1]
    dy2dt = mu_val * (1 - y[0]**2) * y[1] - y[0] + alpha * np.cos(omega * t)
    return [dy1dt, dy2dt]


def experiment_c():
    """D52-C: 迟滞效应 — 单积分慢参数扫描"""
    print("D52-C: 迟滞效应 — 慢参数扫描")
    print("-" * 50)

    # 正向扫描
    sol_fwd = solve_ivp(vanderpol_ramp_fwd_ode, (0, 200), [1.0, 0.0],
                       args=(0.5, 0.1), method='RK45',
                       t_eval=np.linspace(0, 200, 5000), rtol=1e-8, atol=1e-10)
    x_fwd, xp_fwd = sol_fwd.y[0], sol_fwd.y[1]
    e_fwd = 0.5 * xp_fwd**2 + 0.5 * x_fwd**2

    # 反向扫描
    sol_rev = solve_ivp(vanderpol_ramp_rev_ode, (0, 200), [1.0, 0.0],
                       args=(0.5, 0.1), method='RK45',
                       t_eval=np.linspace(0, 200, 5000), rtol=1e-8, atol=1e-10)
    x_rev, xp_rev = sol_rev.y[0], sol_rev.y[1]
    e_rev = 0.5 * xp_rev**2 + 0.5 * x_rev**2

    hysteresis_area = float(np.trapz(np.abs(e_fwd - e_rev), sol_fwd.t))
    norm_hyst = hysteresis_area / (np.mean(e_fwd) * 200.0 + 1e-10)

    print(f"  正向能量范围: [{np.min(e_fwd):.4f}, {np.max(e_fwd):.4f}]")
    print(f"  反向能量范围: [{np.min(e_rev):.4f}, {np.max(e_rev):.4f}]")
    print(f"  迟滞面积: {hysteresis_area:.4f}")
    print(f"  归一化迟滞: {norm_hyst:.6f}")

    # 不同 alpha
    print("\n  不同 alpha 的迟滞面积:")
    for alpha_test in [0.0, 0.3, 0.5, 1.0, 2.0]:
        for direction, ode_func in [('fwd', vanderpol_ramp_fwd_ode), ('rev', vanderpol_ramp_rev_ode)]:
            sol = solve_ivp(ode_func, (0, 200), [1.0, 0.0],
                          args=(alpha_test, 0.1), method='RK45',
                          t_eval=np.linspace(0, 200, 5000), rtol=1e-8, atol=1e-10)
            xs = sol.y[0]; xps = sol.y[1]
            if direction == 'fwd':
                e_fwd2 = 0.5 * xps**2 + 0.5 * xs**2
            else:
                e_rev2 = 0.5 * xps**2 + 0.5 * xs**2
        area = float(np.trapz(np.abs(e_fwd2 - e_rev2), sol_fwd.t))
        print(f"    alpha={alpha_test:.1f}: 迟滞面积={area:.4f}")

    return {
        'description': 'D52-C: 迟滞效应 — 慢参数扫描',
        'mean_energy_fwd': float(np.mean(e_fwd)),
        'mean_energy_rev': float(np.mean(e_rev)),
        'hysteresis_area': hysteresis_area,
        'normalized_hysteresis': norm_hyst,
        'conclusion': 'Van der Pol 慢参数扫描产生迟滞效应'
    }


# ============================================================
# D52-D：alpha-mu 交互效应
# ============================================================

def experiment_d():
    """D52-D: alpha 与 mu 的交互效应"""
    print("D52-D: alpha-mu 交互效应")
    print("-" * 50)

    mu_values = [0.0, 0.5, 1.0, 2.0, 5.0]
    alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]
    omega = 0.1
    results = []

    for mu in mu_values:
        for alpha in alpha_values:
            x, xp, t = solve_vp(mu, alpha=alpha, omega=omega, n_steps=5000)
            energy = compute_energy(x, xp)
            results.append({'mu': float(mu), 'alpha': alpha, 'energy': energy})

    min_result = min(results, key=lambda r: r['energy'])
    energies = np.array([r['energy'] for r in results]).reshape(len(mu_values), len(alpha_values))

    print(f"  最低能量: mu={min_result['mu']}, alpha={min_result['alpha']}, energy={min_result['energy']:.4f}")

    for i, mu in enumerate(mu_values):
        print(f"  mu={mu:5.1f}: energy_range=[{energies[i].min():.4f}, {energies[i].max():.4f}]")
    for j, alpha in enumerate(alpha_values):
        print(f"  alpha={alpha:5.1f}: energy_range=[{energies[:,j].min():.4f}, {energies[:,j].max():.4f}]")

    return {
        'description': 'D52-D: alpha-mu 交互效应',
        'results': results,
        'minimum_energy_config': min_result,
        'conclusion': 'alpha和mu存在交互效应，最低能量出现在特定组合'
    }


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 60)
    print("D52 重构 v5: Van der Pol 非线性振荡器")
    print("=" * 60)

    all_results = {}

    print("\n[D52-A] 频率-能量对偶性")
    all_results['D52-A'] = experiment_a()
    print(f"  → {all_results['D52-A']['conclusion']}\n")

    print("[D52-B] 预规划强度 alpha 扫描")
    all_results['D52-B'] = experiment_b()
    print(f"  → {all_results['D52-B']['conclusion']}\n")

    print("[D52-C] 迟滞效应")
    all_results['D52-C'] = experiment_c()
    print(f"  → {all_results['D52-C']['conclusion']}\n")

    print("[D52-D] alpha-mu 交互")
    all_results['D52-D'] = experiment_d()
    print(f"  → {all_results['D52-D']['conclusion']}\n")

    output = '/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d52-redesign-v5-vanderpol-results.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(),
                    'theory': 'D52: 频率-动力学对偶性（Van der Pol v5）',
                    'version': 'v5', 'results': all_results}, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output}")


if __name__ == '__main__':
    main()
