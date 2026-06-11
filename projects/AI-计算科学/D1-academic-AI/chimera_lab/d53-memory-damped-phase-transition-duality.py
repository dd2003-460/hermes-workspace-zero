#!/usr/bin/env python3
"""
D53：记忆阻尼-相变对偶性

基于 D50（冷启动信息扩散/Cahn-Hilliard 相变）与 D52（记忆阻尼振荡探索）
的交叉验证，研究记忆阻尼动力学与相变行为之间的对偶关系。

核心猜想：
1. Cahn-Hilliard 遗忘率 λ 与记忆核衰减速率 μ 控制同一种动力学相变
2. D50 的涌现阈值相变与 D52 的阻尼模式转变是同一对偶结构的两种表现
3. 过冲度 ↔ 信息过冲（过注入）存在定量对应关系

验证四个命题：
- D53-A：λ-μ 对偶相图（记忆核衰减率 vs 遗忘率的统一相图）
- D53-B：临界记忆 → 临界遗忘（λ_c = μ_c × 动力学缩放系数）
- D53-C：过冲度与过注入量的对偶关系
- D53-D：记忆滞后 → 迟滞环（Barklemann ring equivalent）
"""

import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime

np.random.seed(42)

# ============================================================
# 核心函数（来自 D50 + D52 的提炼）
# ============================================================

def ca_ghilliard_info_diffusion(K, lam, alpha, nabla_I, eta_t, dt=1.0):
    """Cahn-Hilliard 信息扩散: dK/dt = -λK + α∇I + η"""
    return K + dt * (-lam * K + alpha * nabla_I + eta_t)


def exponential_memory_kernel(tau, mu_0, decay_rate):
    """指数记忆核: μ(t) = μ₀·exp(-λt)"""
    return mu_0 * np.exp(-decay_rate * tau)


def simulate_damped_oscillator(n_steps, zeta, omega_0, mu_0, decay_rate, noise_level,
                               initial_val=1.0, memory_buffer=10):
    """记忆阻尼振荡器"""
    x = np.zeros(n_steps)
    v = np.zeros(n_steps)
    x[0], v[0] = initial_val, 0.0
    v_history = [v[0]]
    dt = 0.1

    for t in range(1, n_steps):
        mu_eff = 0.0
        n_hist = min(len(v_history), memory_buffer)
        for tau_idx in range(n_hist):
            mu_eff += exponential_memory_kernel(tau_idx, mu_0, decay_rate) * v_history[-(tau_idx+1)]
        mu_eff /= max(n_hist, 1)

        k1_x = v[t-1]
        k1_v = -(2 * zeta * omega_0 + mu_eff) * v[t-1] - omega_0**2 * x[t-1]
        k2_x = v[t-1] + 0.5 * dt * k1_v
        k2_v = -(2 * zeta * omega_0 + mu_eff) * (v[t-1] + 0.5 * dt * k1_v) - omega_0**2 * (x[t-1] + 0.5 * dt * k1_x)
        k3_x = v[t-1] + 0.5 * dt * k2_v
        k3_v = -(2 * zeta * omega_0 + mu_eff) * (v[t-1] + 0.5 * dt * k2_v) - omega_0**2 * (x[t-1] + 0.5 * dt * k2_x)
        k4_x = v[t-1] + dt * k3_v
        k4_v = -(2 * zeta * omega_0 + mu_eff) * (v[t-1] + dt * k3_v) - omega_0**2 * (x[t-1] + dt * k3_x)

        x_new = x[t-1] + dt * (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
        v_new = v[t-1] + dt * (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6
        x[t] = np.clip(x_new, -0.5, 0.5)
        v[t] = np.clip(v_new, -1.0, 1.0)
        v_history.append(v[t])
        if len(v_history) > memory_buffer:
            v_history.pop(0)

    return x, v


def compute_overshoot(x, window=0.3):
    """测量过冲度"""
    n = len(x)
    if n < 20:
        return 0.0
    final = np.mean(x[-int(n * window):])
    conv_window = max(int(n * (1 - window)), 5)
    post_convergence = x[:n - conv_window]
    if len(post_convergence) == 0:
        return 0.0
    exceeds = np.abs(post_convergence) > np.abs(final) * 1.1
    return float(np.mean(exceeds))


def compute_emergence_time(K_history, threshold=0.3):
    """能力涌现时间: 首次进入稳定高能力状态的时间"""
    n = len(K_history)
    final_avg = np.mean(K_history[-20:])
    for t in range(n - 10):
        if np.all(np.abs(K_history[t:t+10] - final_avg) < threshold) and final_avg > threshold:
            return float(t)
    return float(n)


def info_over_shoot(K_current, K_0, gamma):
    """信息过冲: |能力增益| - 阈值"""
    mi_k0 = np.clip(K_0, 0, 1).sum() / len(K_0)
    mi_kt = np.clip(K_current, 0, 1).sum() / len(K_current)
    return float(mi_kt - mi_k0 - gamma)


# ============================================================
# D53-A：λ-μ 对偶相图
# ============================================================

def experiment_a(n_trials=50, n_steps=200):
    """
    验证 D53-1：遗忘率 λ 与记忆核衰减速率 μ 在统一相图中表现为同一种相变

    方法：在参数空间 (λ, μ_decay) 中扫描，
    以系统动力学状态（遗忘率系统→能力涌现/不足；振荡器→收敛/振荡）
    绘制对偶相图。
    """
    lam_range = np.linspace(0.01, 0.5, 10)
    mu_decay_range = np.linspace(0.01, 0.5, 10)

    phase_states = np.zeros((len(lam_range), len(mu_decay_range)), dtype=float)

    for i, lam in enumerate(lam_range):
        for j, mu_decay in enumerate(mu_decay_range):
            emerged_count = 0
            oscillation_count = 0

            for _ in range(n_trials):
                # Cahn-Hilliard 部分（遗忘率扫描）
                K = np.zeros(n_steps)
                K[0] = 0.1
                for t in range(1, n_steps):
                    K[t] = ca_ghilliard_info_diffusion(
                        K[t-1], lam, alpha=0.3,
                        nabla_I=np.random.randn() * 0.2,
                        eta_t=np.random.randn() * 0.05
                    )
                if K[-1] > 0.15:  # 涌现
                    emerged_count += 1

                # 振荡器部分（记忆衰减扫描）
                x, _ = simulate_damped_oscillator(n_steps, zeta=0.3, omega_0=0.8,
                                                   mu_0=0.3, decay_rate=mu_decay,
                                                   noise_level=0.02)
                if compute_overshoot(x) > 0.05:
                    oscillation_count += 1

            phase_states[i, j] = (emerged_count / n_trials + oscillation_count / n_trials) / 2

    # 寻找相变线：状态值在 0.2-0.8 之间的边界
    transition_boundary = []
    for i in range(len(lam_range) - 1):
        for j in range(len(mu_decay_range) - 1):
            v1 = phase_states[i, j]
            v2 = phase_states[i+1, j]
            v3 = phase_states[i, j+1]
            if (0.15 < v1 < 0.85 and v2 < 0.15) or (0.15 < v1 < 0.85 and v3 < 0.15):
                transition_boundary.append((lam_range[i], mu_decay_range[j]))

    # 拟合对偶关系：λ_c ≈ k × μ_c（线性）
    if len(transition_boundary) > 3:
        lam_vals = [b[0] for b in transition_boundary]
        mu_vals = [b[1] for b in transition_boundary]
        if np.std(mu_vals) > 0:
            slope, intercept = np.polyfit(mu_vals, lam_vals, 1)
            r_squared = np.corrcoef(lam_vals, mu_vals)[0, 1]**2
        else:
            slope, intercept, r_squared = 0.0, 0.0, 0.0
    else:
        slope, intercept, r_squared = 0.0, 0.0, 0.0

    return {
        'description': 'D53-A：遗忘率λ与记忆核衰减速率μ的对偶相图',
        'validation': 'D53-1',
        'phase_transition_map': phase_states.tolist(),
        'boundary_points': [(float(b[0]), float(b[1])) for b in transition_boundary],
        'duality_fit': {
            'predicted_relation': 'lambda_c = k * mu_c',
            'estimated_slope': float(slope),
            'estimated_intercept': float(intercept),
            'r_squared': float(r_squared),
            'n_boundary_points': len(transition_boundary)
        },
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# D53-B：临界记忆 → 临界遗忘
# ============================================================

def experiment_b(n_trials=100, K_dim=10, max_time=200):
    """
    验证 D53-2：D52 的记忆衰减临界值 μ_c 与 D50 的遗忘率临界值 λ_c
    存在严格的比例关系：λ_c ≈ c × μ_c

    两种相变同源于 damped_oscillator 动力学特征
    """
    lam_range = np.linspace(0.01, 0.3, 20)
    mu_range = np.linspace(0.01, 0.3, 20)

    # 临界遗忘率
    lambda_critical = []
    for lam in lam_range:
        emerged = 0
        for _ in range(n_trials):
            K = np.random.randn(K_dim) * 0.05
            K_0 = K.copy()
            for t in range(max_time):
                K = ca_ghilliard_info_diffusion(K, lam, 0.3, np.random.randn(K_dim)*0.1, np.random.randn(K_dim)*0.02)
                K = np.clip(K, -1, 1)
            if K_0.sum() < K.sum() * 0.5:  # 能力增长超过阈值
                emerged += 1
        if emerged / n_trials > 0.5:
            lambda_critical.append(float(lam))

    # 临界记忆衰减
    mu_critical = []
    for mu_decay in mu_range:
        overshoot_count = 0
        for _ in range(n_trials):
            x, _ = simulate_damped_oscillator(max_time, 0.3, 0.8, 0.3, mu_decay, 0.02)
            if compute_overshoot(x) > 0.1:
                overshoot_count += 1
        if overshoot_count / n_trials > 0.5:
            mu_critical.append(float(mu_decay))

    # 拟合比例
    if len(lambda_critical) > 0 and len(mu_critical) > 0:
        lam_avg = np.mean(lambda_critical)
        mu_avg = np.mean(mu_critical)
        ratio = float(lam_avg / max(mu_avg, 1e-10))
        scale_error = abs(lam_avg - ratio * mu_avg)
    else:
        ratio = 0.0
        scale_error = float('inf')

    return {
        'description': 'D53-B：临界记忆衰减→临界遗忘比例关系',
        'validation': 'D53-2',
        'lambda_critical_estimate': float(np.mean(lambda_critical)) if lambda_critical else None,
        'mu_critical_estimate': float(np.mean(mu_critical)) if mu_critical else None,
        'ratio_lambda_over_mu': float(ratio),
        'scale_error': float(scale_error),
        'lambda_scan_values': [float(l) for l in lambda_critical[:5]],
        'mu_scan_values': [float(m) for m in mu_critical[:5]],
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# D53-C：过冲度与过注入量的对偶关系
# ============================================================

def experiment_c(n_trials=50, A=5.0, v=0.5, max_time=150):
    """
    验证 D53-3：探索行为的过冲度与 D50 的信息过注入量
    存在对偶关系（均为过冲现象在不同维度）

    D50 过注入：α 过大导致信息注入超过涌现阈值，反退化
    D52 过冲：μ_0 过大导致探索偏离，记忆过强反降
    """
    # D50 过注入曲线
    alpha_range = np.linspace(0.05, 0.8, 15)
    d50_performance = []
    for alpha in alpha_range:
        success_rate = 0
        for _ in range(n_trials):
            K = np.random.randn(int(A)) * 0.05
            for t in range(max_time):
                K = ca_ghilliard_info_diffusion(K, 0.05, alpha, np.random.randn(int(A))*0.2, np.random.randn(int(A))*0.05)
                K = np.clip(K, -1, 1)
            if np.mean(K) > 0.15:  # 涌现
                success_rate += 1
        d50_performance.append(success_rate / n_trials)

    # D52 过冲曲线
    mu_0_range = np.linspace(0.0, 0.6, 15)
    d52_overshoot = []
    for mu_0 in mu_0_range:
        avg_overshoot = 0
        for _ in range(n_trials):
            x, _ = simulate_damped_oscillator(max_time, 0.3, 0.8, mu_0, 0.05, 0.02)
            avg_overshoot += compute_overshoot(x)
        d52_overshoot.append(avg_overshoot / n_trials)

    # 对偶：D50 在α过大时性能下降 ↔ D52 在μ_0过大时过冲增加
    d50_peak_idx = int(np.argmax(d50_performance))
    d52_peak_idx = int(np.argmax(d52_overshoot))
    d50_at_peak = d50_performance[d50_peak_idx]
    d52_at_peak = d52_overshoot[d52_peak_idx]

    # 测量过注入的退化效应
    d50_deterioration = d50_performance[-1] / max(d50_performance[0], 1e-10) if len(d50_performance) > 1 else 1.0
    d52_overshoot_final = d52_overshoot[-1]

    # 寻找对偶相关性：两个曲线的拐点是否在相同"标准化"参数值处
    alpha_normalized = (np.array(d50_performance) - np.min(d50_performance)) / (np.max(d50_performance) - np.min(d50_performance) + 1e-10)
    overshoot_normalized = (np.array(d52_overshoot) - np.min(d52_overshoot)) / (np.max(d52_overshoot) - np.min(d52_overshoot) + 1e-10)

    if len(alpha_normalized) == len(overshoot_normalized) and np.std(overshoot_normalized) > 0:
        dual_corr = float(np.corrcoef(alpha_normalized, overshoot_normalized)[0, 1])
    else:
        dual_corr = 0.0

    return {
        'description': 'D53-C：过冲度与过注入量对偶关系',
        'validation': 'D53-3',
        'd50_alpha_scan': [(float(a), float(p)) for a, p in zip(alpha_range.tolist(), d50_performance)],
        'd52_mu0_scan': [(float(m), float(o)) for m, o in zip(mu_0_range.tolist(), d52_overshoot)],
        'd50_peak_performance': float(d50_at_peak),
        'd52_peak_overshoot': float(d52_at_peak),
        'd50_deterioration_ratio': float(d50_deterioration),
        'dual_correlation': float(dual_corr),
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# D53-D：记忆滞后 → 迟滞环
# ============================================================

def experiment_d(n_trials=30, max_time=200):
    """
    验证 D53-4：记忆滞后效应导致迟滞环（Barklemann ring）

    记忆核有记忆惯性，改变后需要时间适应
    D50 遗忘率增加时能力下降快，减少时恢复慢 → 迟滞
    D52 记忆增强时过冲多，减弱时收敛慢 → 迟滞
    """
    # D50 滞后环
    lam_increase = np.linspace(0.01, 0.3, 10)
    lam_decrease = np.linspace(0.3, 0.01, 10)

    lag_increase = []
    lag_decrease = []

    for lam in lam_increase:
        K_avg = 0
        for _ in range(n_trials):
            K = np.random.randn(5) * 0.05
            for t in range(max_time):
                K = ca_ghilliard_info_diffusion(K, lam, 0.3, np.random.randn(5)*0.2, np.random.randn(5)*0.05)
                K = np.clip(K, -1, 1)
            K_avg += np.mean(K)
        lag_increase.append(K_avg / n_trials)

    for lam in lam_decrease:
        K_avg = 0
        for _ in range(n_trials):
            K = np.random.randn(5) * 0.05
            for t in range(max_time):
                K = ca_ghilliard_info_diffusion(K, lam, 0.3, np.random.randn(5)*0.2, np.random.randn(5)*0.05)
                K = np.clip(K, -1, 1)
            K_avg += np.mean(K)
        lag_decrease.append(K_avg / n_trials)

    # 迟滞环面积（近似）
    lag_hysteresis = sum(abs(a - b) for a, b in zip(lag_increase, lag_decrease))
    has_hysteresis = lag_hysteresis > 0.1

    # D52 滞后环
    mu_increase = np.linspace(0.0, 0.4, 10)
    mu_decrease = np.linspace(0.4, 0.0, 10)
    overshoot_increase = []
    overshoot_decrease = []

    for mu_decay in mu_increase:
        avg_os = 0
        for _ in range(n_trials):
            x, _ = simulate_damped_oscillator(max_time, 0.3, 0.8, 0.3, mu_decay, 0.02)
            avg_os += compute_overshoot(x)
        overshoot_increase.append(avg_os / n_trials)

    for mu_decay in mu_decrease:
        avg_os = 0
        for _ in range(n_trials):
            x, _ = simulate_damped_oscillator(max_time, 0.3, 0.8, 0.3, mu_decay, 0.02)
            avg_os += compute_overshoot(x)
        overshoot_decrease.append(avg_os / n_trials)

    # 迟滞环面积
    d52_hysteresis = sum(abs(a - b) for a, b in zip(overshoot_increase, overshoot_decrease))
    d52_has_hysteresis = d52_hysteresis > 0.01

    # 比较
    ratio = float(d52_hysteresis / max(lag_hysteresis, 1e-10))

    return {
        'description': 'D53-D：记忆滞后导致的迟滞环对偶性',
        'validation': 'D53-4',
        'd50_hysteresis': {
            'increase_phase': lag_increase,
            'decrease_phase': lag_decrease,
            'total_hysteresis': float(lag_hysteresis),
            'has_significant_hysteresis': has_hysteresis
        },
        'd52_hysteresis': {
            'increase_phase': overshoot_increase,
            'decrease_phase': overshoot_decrease,
            'total_hysteresis': float(d52_hysteresis),
            'has_significant_hysteresis': d52_has_hysteresis
        },
        'hysteresis_ratio_d52_over_d50': float(ratio),
        'timestamp': datetime.now().isoformat()
    }


# ============================================================
# 主函数
# ============================================================

def main():
    results = {}

    print("Running D53-A: λ-μ dual phase diagram...")
    results['D53-A'] = experiment_a()

    print("Running D53-B: Critical memory → critical forgetting...")
    results['D53-B'] = experiment_b()

    print("Running D53-C: Overshoot-overinjection duality...")
    results['D53-C'] = experiment_c()

    print("Running D53-D: Memory hysteresis → hysteresis rings...")
    results['D53-D'] = experiment_d()

    output = {
        'theory': 'D53：记忆阻尼-相变对偶性',
        'results': results,
        'timestamp': datetime.now().isoformat()
    }

    numpy_encoder = lambda o: float(o) if isinstance(o, (np.integer, np.floating, np.bool_)) else str(o)
    with open('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d53-results.json', 'w') as f:
        json.dump(output, f, indent=2, default=numpy_encoder)

    print("Done. Results saved to d53-results.json")
    return output


if __name__ == '__main__':
    main()
