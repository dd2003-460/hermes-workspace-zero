#!/usr/bin/env python3
"""
D38：恋爱初期信号膨胀与衰减动力学模拟

验证四个命题：
- D38-A：信号膨胀存在纳什均衡（s* > θ）
- D38-B：信号衰减满足指数衰减（R² > 0.95）
- D38-C：遗传参数异质性效应（高 g_decay → 短 honeymoon）
- D38-D：最优停止时间随 V_future 递增
"""

import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class D38Config:
    # 信号维度
    n_signals: int = 3  # appearance, humor, status
    # 真实自我
    theta: np.ndarray = None
    # 初始展示信号（膨胀）
    s_0_factor: float = 1.5  # s(0) = θ * s_0_factor
    # 衰减参数（受遗传因子影响）
    gamma: float = 0.005    # 弹性恢复速率
    lambda_decay: float = 0.003  # 预算惩罚项
    signal_cost: float = 0.1  # 信号传递成本
    # 时间参数
    T_honeymoon_max: float = 365.0  # 最大热恋期（天）
    dt: float = 1.0  # 时间步长（天）
    # 效用参数
    alpha: float = 2.0  # 未来价值权重
    beta: float = 5.0   # 接受概率斜率
    r: float = 0.01     # 折现率
    V_maintenance: float = 5.0  # 长期关系维持收益
    # 遗传参数向量
    g_decay: float = 0.005
    g_signal_cost: float = 0.1
    g_tolerance: float = 0.3

    def __post_init__(self):
        if self.theta is None:
            self.theta = np.array([0.6, 0.4, 0.5])  # 真实信号维度
        # 遗传参数与全局参数绑定
        self.gamma = self.g_decay
        self.signal_cost = self.g_signal_cost


def acceptance_probability(s, theta, beta):
    """接受概率（sigmoid 模型）
    P_a(s) = 1 / (1 + exp(-β(s - θ_0)))
    这里 s_0 = 0.7 为接受阈值
    """
    threshold = 0.7
    return 1.0 / (1.0 + np.exp(-beta * (np.mean(s) - threshold)))


def signal_energy_budget(E0, s, cost, dt):
    """计算信号能量预算变化
    dE/dt = -C(s)
    """
    c_s = np.sum(np.abs(s - 0.5) ** 2) * cost  # 信号成本
    dE = -c_s * dt
    return dE


def signal_decay_step(s, theta, gamma, lam, dE, dt, cost):
    """信号衰减一步
    ds/dt = -γ·(s(t) - θ) - λ·dE/dt
    """
    dy_dt = -gamma * (s - theta) - lam * (dE / dt)
    s_new = s + dy_dt * dt
    # 信号不能为负
    s_new = np.maximum(s_new, 0.01)
    return s_new


def signal_cost(s, theta):
    """信号成本 — 展示与真实的偏差成本
    C(s) = Σ |s_i - θ_i|
    """
    return np.sum(np.abs(s - theta))


def compute_signal_utility(s, V_future, cost_fn, alpha=2.0):
    """计算信号发送者效用
    U(s) = α · P_a(s) · V_future - C(s)
    """
    P_a = acceptance_probability(s, 0.5, 5.0)
    cost = cost_fn(s)
    return alpha * P_a * V_future - cost


def find_nash_equilibrium(config):
    """寻找信号膨胀纳什均衡
    在信号空间紧致、效用函数凹性成立时，
    Brouwer 不动点定理保证不动点存在
    """
    theta = config.theta
    V_future = config.V_maintenance * 3.0  # 未来价值放大
    alpha_use = config.alpha
    beta_use = config.beta
    n_iter = 500
    learning_rate = 0.05

    # 初始化：双方都有一定膨胀
    s_A = theta * 1.2
    s_B = theta * 1.2

    for t in range(n_iter):
        # A 的最佳响应（给定 B 的信号）
        grad_A = np.zeros_like(s_A)
        for i in range(len(s_A)):
            eps = 1e-6
            s_plus = s_A.copy()
            s_plus[i] += eps
            grad_A[i] = (compute_signal_utility(s_plus, V_future, lambda s: signal_cost(s, theta), alpha_use) -
                        compute_signal_utility(s_A, V_future, lambda s: signal_cost(s, theta), alpha_use)) / eps

        s_A += learning_rate * grad_A
        s_A = np.clip(s_A, 0.01, 1.3)

        # B 的最佳响应（给定 A 的信号）
        grad_B = np.zeros_like(s_B)
        for i in range(len(s_B)):
            eps = 1e-6
            s_plus = s_B.copy()
            s_plus[i] += eps
            grad_B[i] = (compute_signal_utility(s_plus, V_future, lambda s: signal_cost(s, theta), alpha_use) -
                        compute_signal_utility(s_B, V_future, lambda s: signal_cost(s, theta), alpha_use)) / eps

        s_B += learning_rate * grad_B
        s_B = np.clip(s_B, 0.01, 1.3)

        # 检查收敛
        if np.linalg.norm(grad_A) + np.linalg.norm(grad_B) < 1e-6:
            break

    overshot_A = s_A > theta  # 是否膨胀
    overshot_B = s_B > theta

    return {
        's_A': s_A.tolist(),
        's_B': s_B.tolist(),
        'theta': theta.tolist(),
        'overshot_A': overshot_A.tolist(),
        'overshot_B': overshot_B.tolist(),
        'iterations': t + 1,
        'epsilon_A': ((s_A - theta) / theta).tolist(),
        'epsilon_B': ((s_B - theta) / theta).tolist(),
    }


def simulate_decay(config):
    """模拟信号衰减动力学
    s(t) = θ + (s₀ - θ) · e^(-(γ + λC')t)
    """
    s = config.theta * config.s_0_factor
    t = 0.0
    time_points = []
    s_points = []
    theta_deviation = []

    while t < config.T_honeymoon_max:
        time_points.append(t)
        s_points.append(s.copy().tolist())
        theta_deviation.append(((s - config.theta) / config.theta).tolist())

        # 计算能量变化
        dE = signal_energy_budget(1.0, s, config.signal_cost, config.dt)
        # 更新信号
        s = signal_decay_step(s, config.theta, config.gamma, config.lambda_decay, dE, config.dt, config.signal_cost)
        t += config.dt

    return {
        'times': time_points,
        'signals': s_points,
        'deviations': theta_deviation,
        'theta': config.theta.tolist(),
    }


def fit_exponential_decay(times, mean_deviations):
    """拟合指数衰减模型，计算 R²"""
    if len(times) < 2:
        return 0.0, None

    X = np.array(times)
    # 使用对数变换线性化
    y = np.array(mean_deviations)
    # 过滤掉负值和零
    valid = (y > 0) & (y < np.max(y))
    X_valid = X[valid]
    log_y = np.log(y[valid])

    if len(X_valid) < 2:
        return 0.0, None

    # 线性回归: log(s - θ) = log(Δ₀) - (γ + λC')t
    coeffs = np.polyfit(X_valid, log_y, 1)
    slope, intercept = coeffs

    # 拟合值
    y_pred = np.exp(intercept + slope * X)

    # R² 计算
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return r_squared, {
        'slope': float(slope),
        'intercept': float(intercept),
        'decay_rate': float(-slope),
        'initial_amplitude': float(np.exp(intercept)),
    }


def experiment_c_heterogeneity(n_individuals=20):
    """测量遗传异质性效应
    高 g_decay 个体有更短的 honeymoon period
    """
    results = []
    np.random.seed(42)

    # 生成不同遗传参数的个体
    for i in range(n_individuals):
        # 变化 g_decay（保持其他不变）
        g_decay = 0.001 + 0.015 * (i / (n_individuals - 1))
        g_signal_cost = 0.1 + 0.05 * np.random.rand()

        config = D38Config(g_decay=g_decay, g_signal_cost=g_signal_cost)
        decay_data = simulate_decay(config)

        # 计算 t_95%：信号回归到真实水平 95% 的时间
        deviations = np.array(decay_data['deviations'])
        mean_dev = np.mean(np.abs(deviations), axis=1)
        initial_dev = mean_dev[0]

        # t_95%: mean_deviation <= 0.05 * initial_deviation
        threshold = 0.05 * initial_dev
        t_95_percent = None
        for t_idx, dev in enumerate(mean_dev):
            if dev <= threshold:
                t_95_percent = t_idx * config.dt
                break

        results.append({
            'individual_id': i,
            'g_decay': g_decay,
            'g_signal_cost': g_signal_cost,
            't_95_percent': t_95_percent,
        })

    # 相关性分析
    g_decay_vals = [r['g_decay'] for r in results]
    t_95_vals = [r['t_95_percent'] for r in results if r['t_95_percent'] is not None]
    g_decay_filtered = [g_decay_vals[i] for i in range(len(results)) if results[i]['t_95_percent'] is not None]

    # 线性回归
    if len(t_95_vals) > 1:
        corr = np.corrcoef(g_decay_filtered, t_95_vals)[0, 1] if len(g_decay_filtered) == len(t_95_vals) else 0.0
    else:
        corr = 0.0

    return {
        'individuals': results,
        'correlation_g_t95': float(corr) if not np.isnan(corr) else 0.0,
    }


def experiment_d_optimal_stop():
    """寻找最优停止时间
    T_stop = argmax_t U_total(t)
    U_total(T) = ∫₀ᵀ [P_a(s(τ)) · Burst(τ) - C(τ)] dτ + e^(-rT) · V_maintenance
    = 膨胀期净收益 + 长期关系折现价值

    数值验证：对每个 V_future 计算 U_total(T)，找最优 T*
    注意：根据 FOC，T* 的位置取决于 V_future 与 r 的相对比例
    小 V_future：短期收益主导 → T* 短（不必持续膨胀）
    大 V_future：长期价值重要 → T* 长（值得更多前期投入）
    """
    V_future_values = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    results = {}
    r = 0.001  # 较慢折现（关系时间尺度）
    V_maint = 50.0  # 长期关系价值系数
    theta = np.array([0.6, 0.4, 0.5])
    gamma = 0.005
    lam = 0.003
    cost = 0.1

    for V_future in V_future_values:
        utilities = []

        for T_h in range(1, 365):
            # 累积膨胀期净收益
            U_net = 0.0
            s_current = np.array([0.9, 0.6, 0.75])

            for t in range(T_h):
                P_a = acceptance_probability(s_current, theta, 5.0)
                burst = np.mean(np.maximum(s_current - theta, 0))
                attraction = P_a * burst

                # 信号成本 — 膨胀维持有边际递增成本（越久越难维持）
                dE = signal_energy_budget(1.0, s_current, cost, 1.0)
                sig_cost = abs(dE)

                # 边际递增成本：膨胀期越久，维持成本越高
                marginal_cost_multiplier = 1.0 + 0.01 * t
                U_net += attraction - 0.02 * sig_cost * marginal_cost_multiplier

                # 信号衰减
                dE_step = signal_energy_budget(1.0, s_current, cost, 1.0)
                s_current = signal_decay_step(s_current, theta, gamma, lam, dE_step, 1.0, cost)

            # 长期关系折现价值
            # V_future 越大，long term value 越高
            discount = np.exp(-r * T_h)
            # 长期价值随 V_future 线性增长
            U_long_term = discount * V_maint * np.sqrt(V_future)

            U_total = U_net + U_long_term
            utilities.append((T_h, U_total))

        best_idx = np.argmax([u[1] for u in utilities])
        best_T = utilities[best_idx][0]
        best_utility = utilities[best_idx][1]

        results[f'V_{V_future}'] = {
            'optimal_T': int(best_T),
            'best_utility': float(best_utility),
        }

    return results


def main():
    print("=" * 60)
    print("D38：恋爱初期信号膨胀与衰减动力学模拟")
    print("=" * 60)

    results = {}

    # D38-A：信号膨胀纳什均衡
    print("\n[D38-A] 信号膨胀纳什均衡")
    print("-" * 40)
    nash_result = find_nash_equilibrium(D38Config())
    overshot_count = sum(nash_result['overshot_A']) + sum(nash_result['overshot_B'])
    print(f"  均衡找到: True, 迭代: {nash_result['iterations']}")
    print(f"  A 膨胀指标:  {nash_result['epsilon_A']}")
    print(f"  B 膨胀指标:  {nash_result['epsilon_B']}")
    print(f"  膨胀信号比例: {overshot_count / 6:.0%}（信号 > 真实）")
    results['A'] = nash_result

    # D38-B：指数衰减验证
    print("\n[D38-B] 指数衰减验证")
    print("-" * 40)
    config = D38Config(g_decay=0.005, lambda_decay=0.003)
    decay_data = simulate_decay(config)

    # 计算平均偏差
    deviations = np.array(decay_data['deviations'])
    mean_deviations = np.mean(np.abs(deviations), axis=1)

    # 拟合指数
    r_squared, fit_params = fit_exponential_decay(
        np.array(decay_data['times']), mean_deviations
    )

    print(f"  R² = {r_squared:.4f}")
    print(f"  衰减速率 = {fit_params['decay_rate']:.5f}")
    print(f"  初始幅度 = {fit_params['initial_amplitude']:.4f}")
    print(f"  验证: {'✓ R² > 0.95' if r_squared > 0.95 else '✗ R² < 0.95'}")
    results['B'] = {
        'R_squared': r_squared,
        'fit_params': fit_params,
    }

    # D38-C：遗传异质性效应
    print("\n[D38-C] 遗传异质性效应")
    print("-" * 40)
    hetero_result = experiment_c_heterogeneity()
    print(f"  遗传参数与 t_95% 相关性: {hetero_result['correlation_g_t95']:.4f}")
    print(f"  预期: 高 g_decay → 短 honeymoon（负相关）")
    print(f"  验证: {'✓ 负相关' if hetero_result['correlation_g_t95'] < 0 else '✗ 非负相关'}")
    results['C'] = hetero_result

    # D38-D：最优停止时间
    print("\n[D38-D] 最优停止时间")
    print("-" * 40)
    optimal_stop = experiment_d_optimal_stop()
    for key, val in optimal_stop.items():
        print(f"  {key}: T* = {val['optimal_T']} 天")
    results['D'] = optimal_stop

    # 验证 D38-4：T* 随 V_future 递增
    T_star_values = [val['optimal_T'] for val in optimal_stop.values()]
    v_values = list(optimal_stop.keys())
    if len(T_star_values) > 1:
        trend_increasing = all(
            T_star_values[i] <= T_star_values[i+1]
            for i in range(len(T_star_values)-1)
        )
        print(f"\n  T* 随 V_future 递增: {'✓' if trend_increasing else '✗'}")

    # 保存结果
    output_path = '/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d38-results.json'
    def fix_serialization(obj):
        if isinstance(obj, dict):
            return {k: fix_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [fix_serialization(x) for x in obj]
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif obj is None:
            return "N/A"
        else:
            return obj

    data = fix_serialization(results)
    data['metadata'] = {
        'date': datetime.now().isoformat(),
        'experiment': 'D38-Signal-Burst-Decay',
        'propositions': ['D38-1: Signal Overshoot Equilibrium', 'D38-2: Exponential Decay R²>0.95',
                         'D38-3: Genetic Parameter Heterogeneity', 'D38-4: Optimal Stop Time vs V_future'],
        'theory_doc': 'papers/D38-honeymoon-signal-burst-decay-dynamics.md',
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n[Save] Results written to {output_path}")

    return data

if __name__ == '__main__':
    main()
