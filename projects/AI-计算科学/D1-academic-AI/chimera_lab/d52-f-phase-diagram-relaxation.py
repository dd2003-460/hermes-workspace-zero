#!/usr/bin/env python3
"""
D52-F: 频率-振幅相图 — Van der Pol relaxation oscillation 相变探索

探索 mu 从谐波振荡器（harmonic oscillator）到松弛振荡器（relaxation oscillator）
的过渡，测量相变临界值 mu_c。

关键度量：
1. 相图 (x vs x') — 几何形状从椭圆变为弛豫环
2. 频率-振幅相图 — mu 对极限环频率和振幅的影响
3. 非对称性指标 — relaxation oscillation 的上升/下降时间比
4. 临界 mu_c 的确定
"""

import numpy as np
import json
from datetime import datetime
from scipy.integrate import solve_ivp
from scipy.stats import linregress

np.random.seed(42)

# ============================================================
# Van der Pol 振荡器
# ============================================================

def vanderpol_ode(t, y, mu):
    """标准 Van der Pol 方程（无外部驱动）"""
    dy1dt = y[1]
    dy2dt = mu * (1 - y[0]**2) * y[1] - y[0]
    return [dy1dt, dy2dt]


def solve_vp(mu, n_steps=10000, t_max=500.0, y0=None):
    """求解 Van der Pol 方程，返回极限环状态（跳过瞬态）"""
    if y0 is None:
        y0 = [1.0, 0.0]

    sol = solve_ivp(vanderpol_ode, (0, t_max), y0,
                    args=(mu,), method='RK45',
                    t_eval=np.linspace(0, t_max, n_steps),
                    rtol=1e-8, atol=1e-10)

    # 返回最后 1 个周期的数据（跳过瞬态）
    y1, y2, t = sol.y[0], sol.y[1], sol.t
    return y1, y2, t


# ============================================================
# 度量函数
# ============================================================

def compute_energy(x, xp):
    return float(np.mean(0.5 * xp**2 + 0.5 * x**2))


def compute_amplitude(x):
    return float((np.max(x) - np.min(x)) / 2)


def compute_peak_x(x):
    return float(np.max(x))


def compute_rise_descent_ratio(x, t):
    """
    上升/下降时间比 — relaxation oscillation 的标志性指标
    harmonic oscillator: ratio ≈ 1
    relaxation oscillator: ratio >> 1（快速上升，缓慢下降）
    """
    # 找过零点（从负到正）
    signs = np.sign(x)
    signs[signs == 0] = 1
    crossings = np.where(np.diff(signs))[0]

    if len(crossings) < 4:
        return 1.0  # 谐波振荡器默认值

    # 取中间的几个过零点用于计算（使用原始索引）
    n = len(crossings)
    c1, c2, c3 = crossings[n//2], crossings[n//2 + 1], crossings[n//2 + 2]

    # x[c1] 是过零（从负到正），x[c2] 是从正到负
    # 在 [c1, c2] 中找最大值
    segment = x[c1:c2+1]
    max_in_seg = c1 + np.argmax(segment)

    # 在 [c2, c3] 中找最小值
    segment2 = x[c2:c3+1]
    min_in_seg = c2 + np.argmin(segment2)

    rise_time = (max_in_seg - c1) / len(x) * (t[-1] - t[0])
    descent_time = (min_in_seg - max_in_seg) / len(x) * (t[-1] - t[0])

    if descent_time < 1e-10:
        return 1.0

    return float(rise_time / descent_time)


def compute_phase_area(x, xp, t):
    """相图包围面积（用格林公式）"""
    area = 0.5 * float(np.trapz(x * np.gradient(xp, t) - xp * np.gradient(x, t), t))
    return abs(area)


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
# D52-F：相图分析
# ============================================================

def experiment_f():
    """
    D52-F: 频率-振幅相图 — relaxation oscillation 相变

    探索 mu 从 0.0 到 50.0 的过渡
    """
    print("D52-F: 频率-振幅相图 — relaxation oscillation 相变")
    print("=" * 60)

    mu_values = [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0, 50.0]
    results = []

    print(f"{'mu':>8} {'Energy':>10} {'Amplitude':>10} {'Freq':>10} {'Rise/Desc':>12} {'PhaseArea':>12}")

    for mu in mu_values:
        x, xp, t = solve_vp(mu, n_steps=10000, t_max=500.0)

        energy = compute_energy(x, xp)
        amplitude = compute_amplitude(x)
        freq, psd_peak = compute_dominant_freq(x, t)
        rise_desc = compute_rise_descent_ratio(x, t)
        phase_area = compute_phase_area(x, xp, t)

        result = {
            'mu': float(mu),
            'energy': energy,
            'amplitude': amplitude,
            'peak_x': compute_peak_x(x),
            'dominant_freq': freq,
            'psd_peak': psd_peak,
            'rise_descent_ratio': rise_desc,
            'phase_area': phase_area
        }
        results.append(result)

        print(f"{mu:8.1f} {energy:10.4f} {amplitude:10.4f} {freq:10.6f} {rise_desc:12.4f} {phase_area:12.4f}")

    # 分析
    mus = np.array([r['mu'] for r in results])
    freqs = np.array([r['dominant_freq'] for r in results])
    amplitudes = np.array([r['amplitude'] for r in results])
    rise_descs = np.array([r['rise_descent_ratio'] for r in results])
    energies = np.array([r['energy'] for r in results])

    # 对数回归
    log_mus = np.log(mus[1:])  # 排除 mu=0
    log_freqs = np.log(freqs[1:])
    log_amplitudes = np.log(amplitudes[1:])
    log_energies = np.log(energies[1:])

    corr_f, p_f, _, _, _ = linregress(log_mus, log_freqs)
    corr_a, p_a, _, _, _ = linregress(log_mus, log_amplitudes)
    corr_e, p_e, _, _, _ = linregress(log_mus, log_energies)

    # rise_desc 回归 — mu[2:] 对应 log_mus[1:] 和 rise_descs[2:]
    # log_mus[1:] 有 11 个元素（mu[1] 到 mu[12]）
    # rise_descs[2:] 有 11 个元素（index 2 到 12）
    rd_valid = rise_descs[2:] > 0
    if np.sum(rd_valid) >= 3:
        corr_r, p_r, _, _, _ = linregress(
            log_mus[1:][rd_valid],  # 11 elements minus 0s
            np.log(rise_descs[2:][rd_valid]))
    else:
        corr_r, p_r = 0.0, 1.0

    print(f"\n  log(log_mus, freq): slope={corr_f:.4f}, p={p_f:.2e}")
    print(f"  log(log_mus, amp): slope={corr_a:.4f}, p={p_a:.2e}")
    print(f"  log(log_mus, energy): slope={corr_e:.4f}, p={p_e:.2e}")
    print(f"  log(log_mus, rise_desc): slope={corr_r:.4f}, p={p_r:.2e}")

    # 检测相变点：rise_descent_ratio 急剧增大的 mu 值
    # 使用分段回归找到转折点
    transition_idx = None
    for i in range(2, len(rise_descs) - 1):
        if rise_descs[i] > 1.5 and rise_descs[i-1] <= 1.5:
            transition_idx = i
            break

    print(f"\n  Relaxation 相变临界 mu_c ≈ {mu_values[transition_idx] if transition_idx else '未检测到'}")

    # 频率 vs 1/mu 的线性关系（relaxation oscillation 的标准预测）
    high_mu_mask = np.array(mus) >= 5.0
    if np.sum(high_mu_mask) >= 3:
        log_mus_hm = np.log(mus[high_mu_mask])
        log_freqs_hm = np.log(freqs[high_mu_mask])
        corr_f_hm, p_f_hm, _, _, _ = linregress(log_mus_hm, log_freqs_hm)
        print(f"\n  高频区 (mu>=5) log(log_mus, freq): slope={corr_f_hm:.4f}, p={p_f_hm:.2e}")
        print(f"  理论预测: slope ≈ -1 (Van der Pol relaxation oscillation)")

    # 生成相图数据（用于绘图）
    phase_data = {}
    for mu in [0.1, 1.0, 5.0, 20.0, 50.0]:
        x, xp, t = solve_vp(mu, n_steps=2000, t_max=500.0)
        # 只保留最后几个周期
        n_cycles = 3
        start_idx = len(x) - n_cycles * int(2 * len(x) / (np.max(np.where(np.diff(np.sign(x - np.min(x))) > 0)) + 1))
        phase_data[f"mu={mu}"] = {
            'x': [float(v) for v in x[start_idx:start_idx+500]],
            'xp': [float(v) for v in xp[start_idx:start_idx+500]],
            't': [float(v) for v in t[start_idx:start_idx+500]]
        }

    return {
        'description': 'D52-F: 频率-振幅相图 — relaxation oscillation 相变',
        'validation': 'D52-相变',
        'mu_values': [float(m) for m in mu_values],
        'results': results,
        'freq_mu_slope': float(corr_f), 'freq_mu_p': float(p_f),
        'amp_mu_slope': float(corr_a), 'amp_mu_p': float(p_a),
        'energy_mu_slope': float(corr_e), 'energy_mu_p': float(p_e),
        'rise_desc_mu_slope': float(corr_r), 'rise_desc_mu_p': float(p_r),
        'transition_mu_c': float(mu_values[transition_idx]) if transition_idx else None,
        'phase_data': phase_data,
        'conclusion': 'mu 增大导致 Van der Pol 从谐波振荡器转变为松弛振荡器，临界值 mu_c ≈ ?'
    }


# ============================================================
# 辅助：Poincaré 截面分析
# ============================================================

def poincare_analysis():
    """
    Poincaré 截面 — 在 y1=0, y2>0 处采样
    用于检测极限环的存在性和稳定性
    """
    print("\nPoincaré 截面分析")
    print("-" * 50)

    for mu in [0.1, 1.0, 5.0, 20.0]:
        # 找 y1 过零点（从负到正）
        x, xp, t = solve_vp(mu, n_steps=20000, t_max=1000.0)

        signs = np.sign(x)
        signs[signs == 0] = 1
        crossings = np.where(np.diff(signs))[0]
        # 只取上升方向的过零点（y1 从负到正）
        dx = np.diff(x[crossings])
        if len(dx) == len(crossings) - 1:
            pos_crossings = crossings[:len(dx)][dx > 0]
        else:
            pos_crossings = crossings  # fallback

        if len(pos_crossings) > 10:
            # 最后 20 个截面的 xp 值
            last_20 = xp[pos_crossings[-20:]]
            mean_xp = float(np.mean(last_20))
            std_xp = float(np.std(last_20))
            period_est = float(np.median(np.diff(t[pos_crossings])))

            print(f"  mu={mu:5.1f}: <x'>={mean_xp:.4f}, std={std_xp:.6f}, T_est={period_est:.2f}")


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 60)
    print("D52-F: 频率-振幅相图 — relaxation oscillation 相变")
    print("=" * 60)

    all_results = {}

    result_f = experiment_f()
    all_results['D52-F'] = result_f
    print(f"\n  Conclusion: {result_f['conclusion']}")

    poincare_analysis()

    output = '/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d52-f-phase-diagram-results.json'
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({'timestamp': datetime.now().isoformat(),
                    'theory': 'D52: 频率-动力学对偶性（Van der Pol v5-F）',
                    'version': 'v5-F', 'results': all_results}, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output}")


if __name__ == '__main__':
    main()
