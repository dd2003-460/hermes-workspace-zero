#!/usr/bin/env python3
"""
D4-S18-r16：时变参数动态实验 — 探索活跃度指数(EAI)验证

核心动机（基于 r16 发现）：
1. K-Scan 无相变信号 → chimera_prob=0.40（恒定）
2. 需要**时变参数**才能观测到系统对扰动的响应
3. EAI = |dI_C/dt| × |d(chimera_prob)/dt| × (I_C - 1)

实验设计：
1. 协议R1：参数震荡（周期调制 K(t) = K₀(1 + α sin(ωt))）
2. 协议R2：阶跃跳跃（K(t) 在临界区附近切换）
3. 协议R3：斜坡扫描（线性梯度变化 K(t) = K₀ + βt）

每个协议同时测量：
- I_C(t)（拓扑不变量）
- chimera_prob(t)（分段同步性）
- EAI(t)（探索活跃度指数）
- avg_sync(t)（全局同步度）
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Chimera 模拟器（时变参数版本）
# ============================================================

class TimeVaryingChimeraSimulator:
    """
    Abrams-Strogatz chimera 模型 — 支持时变耦合参数

    关键区别于静态版本：
    - K_local(t) 可以是时间函数
    - g(t), sigma_env(t) 也可时变
    """

    def __init__(self, n=64, seed=42):
        self.n = n
        np.random.seed(seed)
        self.theta = np.random.uniform(0, 2*np.pi, n)
        self.t = 0  # 时间戳

    def step(self, K_local=1.5, g=0.03, sigma_env=0.0, dt=0.005):
        """单步演化"""
        z_global = np.mean(np.exp(1j * self.theta))
        dtheta = np.zeros(self.n)

        for i in range(self.n):
            # 局部耦合（K_local 可以是时变函数）
            for d in range(-3, 4):
                if d == 0:
                    continue
                j = (i + d) % self.n
                K_i = K_local
                K_ij = 0.5 * (K_i + 1.5)
                dtheta[i] += K_ij * np.sin(self.theta[j] - self.theta[i])

            # 全局耦合
            dtheta[i] += g * z_global.imag

            # 环境耦合
            if sigma_env > 0:
                dtheta[i] += sigma_env * np.sin(self.theta[i] + i/self.n * np.pi/2)

        self.theta = (self.theta + dtheta * dt) % (2*np.pi)
        self.t += 1

    def simulate_with_time_function(self, T, K_fn=None, g_fn=None, sigma_fn=None, dt=0.005):
        """
        使用函数定义参数

        Args:
            T: 总模拟步数
            K_fn: time -> K_local 函数
            g_fn: time -> g 函数
            sigma_fn: time -> sigma_env 函数
        """
        if K_fn is None:
            K_fn = lambda t: 1.5
        if g_fn is None:
            g_fn = lambda t: 0.03
        if sigma_fn is None:
            sigma_fn = lambda t: 0.0

        trajectory = []
        params_record = []

        for t in range(T):
            # 记录当前参数
            K_t = K_fn(t)
            g_t = g_fn(t)
            s_t = sigma_fn(t)
            params_record.append({'t': t, 'K': K_t, 'g': g_t, 'sigma': s_t})

            trajectory.append(self.theta.copy())
            self.step(K_t, g_t, s_t, dt)

        return np.array(trajectory), params_record


# ============================================================
# 测量模块（与 r12 一致）
# ============================================================

def measure_chimera_segments(traj, n_segments=3):
    """测量空间分段的同步性"""
    T, n = traj.shape
    theta_now = traj[-1]

    seg_size = n // n_segments
    seg_sync = np.zeros(n_segments)
    seg_phase = np.zeros(n_segments)

    for s in range(n_segments):
        start = s * seg_size
        end = (s+1) * seg_size
        seg = theta_now[start:end]
        seg_sync[s] = abs(np.mean(np.exp(1j * seg)))
        seg_phase[s] = np.mean(seg)

    return seg_sync, seg_phase

def estimate_topology(traj, n_dim_max=3):
    """基于时间序列的拓扑估计"""
    T, n = traj.shape
    steady_len = min(1000, T)
    if steady_len < 50:
        return np.array([1.0, 0.0, 0.0])

    steady = traj[-steady_len:]
    n_repr = min(10, n)
    sample_agents = np.linspace(0, n-1, n_repr, dtype=int)
    X = steady[:, sample_agents].T  # (n_repr, T_steady)

    if X.shape[0] == 0 or X.shape[1] < 2:
        return np.array([1.0, 0.0, 0.0])

    X_c = X - X.mean(axis=1, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)

    if len(S) == 0 or S[0] == 0:
        return np.array([1.0, 0.0, 0.0])

    n_dim = min(max(2, int(np.sum(S > 0.01*S[0]))), n_dim_max)
    if n_dim < 2:
        return np.array([1.0, 0.0, 0.0])

    if Vt.shape[1] < n_dim:
        return np.array([1.0, 0.0, 0.0])

    emb = X_c @ Vt.T[:, :n_dim]

    if len(emb) < 2:
        return np.array([1.0, 0.0, 0.0])

    dist = squareform(pdist(emb))

    if dist.size == 0:
        return np.array([1.0, 0.0, 0.0])

    eps_low = max(np.percentile(dist, 20), 1e-3)
    eps_high = max(np.percentile(dist, 50), 1e-2)

    parent = np.arange(len(emb))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py: parent[px] = py

    b0s = []
    for eps in [eps_low, eps_high]:
        for i in range(len(emb)):
            for j in range(i+1, len(emb)):
                if dist[i,j] < eps: union(i, j)
        b0s.append(len(set(find(i) for i in range(len(emb)))))

    b0_avg = np.mean(b0s)

    b1 = 0
    if b0_avg < 2 and n_dim >= 2:
        if len(emb) > 1:
            angles = np.arctan2(emb[:, 1], emb[:, 0])
            angle_diff = np.diff(angles)
            angle_diff = ((angle_diff + np.pi) % (2*np.pi)) - np.pi
            b1 = max(1, int(round(np.sum(np.abs(angle_diff)) / (2 * np.pi))))

    b2 = max(0, b0_avg - 1) if b0_avg > 1 else 0

    return np.array([b0_avg, float(b1), b2])

def compute_I_C(betti):
    """计算拓扑不变量 I_C = |χ| + w_2"""
    chi = sum((-1)**i * b for i, b in enumerate(betti))
    w2 = 1 if betti[1] % 2 == 1 else 0
    return abs(chi) + w2, chi, w2

def compute_chimera_prob_from_segments(seg_sync, threshold=(0.2, 0.9)):
    """根据分段同步性判断 chimera 存在性"""
    return any(threshold[0] < s < threshold[1] for s in seg_sync)


# ============================================================
# EAI 指数计算
# ============================================================

def compute_EAI_window(I_C_1, I_C_2, chimera_1, chimera_2):
    """
    探索活跃度指数（EAI）

    EAI = |dI_C/dt| × |d(chimera_prob)/dt| × (I_C - 1)

    核心逻辑：
    - 只有 I_C 变化 AND chimera_prob 变化 同时发生 才算"探索"
    - 静态高 I_C 只是结构性前提，不是实际探索
    """
    dI_C = abs(I_C_2 - I_C_1)
    dchimera = abs(chimera_2 - chimera_1)
    potential = max(0, I_C_1 - 1)

    return dI_C * dchimera * potential

def compute_running_EAI(time_series, window=200, step=100):
    """
    计算滑动窗口下的 EAI 曲线

    Args:
        time_series: list of {'t': T, 'I_C': v, 'chimera': flag}
        window: 窗口大小
        step: 步进

    Returns:
        EAI_curve: list of (t, EAI_value)
    """
    EAI_curve = []

    for t_start in range(0, len(time_series) - window, step):
        # 取窗口两端的快照
        idx1 = t_start
        idx2 = min(t_start + window, len(time_series) - 1)

        I_C_1 = time_series[idx1]['I_C']
        I_C_2 = time_series[idx2]['I_C']
        chimera_1 = time_series[idx1]['chimera']
        chimera_2 = time_series[idx2]['chimera']

        EAI = compute_EAI_window(I_C_1, I_C_2, chimera_1, chimera_2)
        t_center = time_series[(idx1 + idx2) // 2]['t']

        EAI_curve.append({'t': t_center, 'EAI': EAI, 'I_C_1': I_C_1, 'I_C_2': I_C_2})

    return EAI_curve


# ============================================================
# 协议 R1：参数震荡（周期调制）
# ============================================================

def protocol_oscillating_params(K0=1.5, alpha=0.3, omega=0.002,
                                 T=10000, window=500, step=100):
    """
    协议R1：参数震荡实验

    K(t) = K₀ × (1 + α × sin(ωt))

    假设：如果系统存在临界区，周期扰动应该产生共振响应
    """
    print("\n" + "=" * 60)
    print("协议R1：参数震荡实验（周期调制 K(t)）")
    print("=" * 60)
    print(f"K0={K0}, alpha={alpha}, omega={omega}")
    print(f"K_range = [{K0*(1-alpha):.2f}, {K0*(1+alpha):.2f}]")

    K_fn = lambda t: K0 * (1 + alpha * np.sin(omega * t))

    sim = TimeVaryingChimeraSimulator(n=64, seed=42)
    traj, params = sim.simulate_with_time_function(T, K_fn=K_fn)

    # 分段测量
    results = []
    t_range = np.arange(0, T, step)

    for t in t_range:
        w_start = t
        w_end = min(t + window, T)

        traj_window = traj[w_start:w_end]
        if len(traj_window) < 50:
            continue

        # chimera 检测
        seg_sync, _ = measure_chimera_segments(traj_window)
        chimera_flag = compute_chimera_prob_from_segments(seg_sync)

        # 拓扑估计
        betti = estimate_topology(traj_window)
        I_C, chi, w2 = compute_I_C(betti)

        K_now = K_fn(t)

        results.append({
            't': t, 'I_C': float(I_C), 'chimera': int(chimera_flag),
            'K': float(K_now), 'avg_sync': float(np.mean(seg_sync)),
            'betti': betti.tolist()
        })

    # 计算 EAI 曲线
    EAI_curve = compute_running_EAI(results, window=window, step=step)

    # 统计摘要
    I_C_mean = np.mean([r['I_C'] for r in results])
    I_C_std = np.std([r['I_C'] for r in results])
    chimera_rate = np.mean([r['chimera'] for r in results])
    EAI_max = max(e['EAI'] for e in EAI_curve) if EAI_curve else 0

    print(f"\nI_C = {I_C_mean:.3f} ± {I_C_std:.3f}")
    print(f"chimera_rate = {chimera_rate:.3f}")
    print(f"EAI_max = {EAI_max:.3f}")
    print(f"高EAI时段数 (EAI > 0) = {sum(1 for e in EAI_curve if e['EAI'] > 1e-6)}")

    # 检查 I_C 与 K 的相关性
    if len(results) > 10:
        I_C_arr = np.array([r['I_C'] for r in results])
        K_arr = np.array([r['K'] for r in results])
        corr = np.corrcoef(I_C_arr, K_arr)[0, 1]
        print(f"I_C-K 相关性 = {corr:.3f}")

    return {'results': results, 'EAI_curve': EAI_curve}


# ============================================================
# 协议 R2：阶跃跳跃（在可疑临界区切换）
# ============================================================

def protocol_step_hopping(K_low=0.8, K_high=2.0, duration=2500, T=10000):
    """
    协议R2：阶跃跳跃实验

    K(t) = K_low 在 [0, duration)
    K(t) = K_high 在 [duration, 2*duration)
    交替进行...

    假设：如果系统在某个临界 K_c 处有相变，
          阶跃切换应该产生不同的弛豫动力学
    """
    print("\n" + "=" * 60)
    print("协议R2：阶跃跳跃实验（临界区来回切换）")
    print("=" * 60)
    print(f"K 在 [{K_low}, {K_high}] 之间交替")

    K_fn = lambda t: K_high if (t // duration) % 2 == 1 else K_low

    sim = TimeVaryingChimeraSimulator(n=64, seed=42)
    traj, params = sim.simulate_with_time_function(T, K_fn=K_fn)

    # 分段测量
    results = []
    step = 200

    for t in range(0, T, step):
        traj_window = traj[t:min(t+duration, T)]
        if len(traj_window) < 50:
            continue

        seg_sync, _ = measure_chimera_segments(traj_window)
        chimera_flag = compute_chimera_prob_from_segments(seg_sync)
        betti = estimate_topology(traj_window)
        I_C, chi, w2 = compute_I_C(betti)

        state = K_fn(t)

        results.append({
            't': t, 'I_C': float(I_C), 'chimera': int(chimera_flag),
            'K': float(state), 'avg_sync': float(np.mean(seg_sync)),
            'betti': betti.tolist(), 'state': 'high' if state == K_high else 'low'
        })

    # EAI 曲线
    EAI_curve = compute_running_EAI(results, window=duration, step=step)

    # 按状态分组统计
    low_state = [r for r in results if r['state'] == 'low']
    high_state = [r for r in results if r['state'] == 'high']

    if low_state and high_state:
        I_C_low = np.mean([r['I_C'] for r in low_state])
        I_C_high = np.mean([r['I_C'] for r in high_state])
        print(f"\nI_C(K={K_low}) = {I_C_low:.3f}")
        print(f"I_C(K={K_high}) = {I_C_high:.3f}")
        print(f"ΔI_C = {I_C_high - I_C_low:.3f}")

    EAI_max = max(e['EAI'] for e in EAI_curve) if EAI_curve else 0
    print(f"EAI_max = {EAI_max:.3f}")

    return {'results': results, 'EAI_curve': EAI_curve}


# ============================================================
# 协议 R3：斜坡扫描（线性梯度变化）
# ============================================================

def protocol_ramp_scan(K_start=0.5, K_end=3.0, T=15000, step=200):
    """
    协议R3：斜坡扫描（线性渐变）

    K(t) = K_start + (K_end - K_start) × (t / T_max)

    假设：慢速扫描可以捕捉迟滞回线（hysteresis）——
          这是相变的核心特征
    """
    print("\n" + "=" * 60)
    print("协议R3：斜坡扫描（线性渐变，检测迟滞）")
    print("=" * 60)
    print(f"K 从 {K_start} 渐变到 {K_end}")

    K_fn = lambda t: K_start + (K_end - K_start) * (t / T)

    sim = TimeVaryingChimeraSimulator(n=64, seed=42)
    traj, params = sim.simulate_with_time_function(T, K_fn=K_fn)

    # 分段测量
    results = []

    for t in range(0, T, step):
        traj_window = traj[t:min(t+400, T)]
        if len(traj_window) < 50:
            continue

        seg_sync, _ = measure_chimera_segments(traj_window)
        chimera_flag = compute_chimera_prob_from_segments(seg_sync)
        betti = estimate_topology(traj_window)
        I_C, chi, w2 = compute_I_C(betti)

        K_now = K_fn(t)

        results.append({
            't': t, 'I_C': float(I_C), 'chimera': int(chimera_flag),
            'K': float(K_now), 'avg_sync': float(np.mean(seg_sync)),
            'betti': betti.tolist()
        })

    # EAI 曲线
    EAI_curve = compute_running_EAI(results, window=400, step=step)

    # 统计
    I_C_mean = np.mean([r['I_C'] for r in results])
    EAI_max = max(e['EAI'] for e in EAI_curve) if EAI_curve else 0
    high_EAI_count = sum(1 for e in EAI_curve if e['EAI'] > 1e-6)

    print(f"\nI_C 均值 = {I_C_mean:.3f}")
    print(f"EAI_max = {EAI_max:.3f}")
    print(f"高EAI时段数 = {high_EAI_count}")

    # 寻找 EAI 峰值对应的 K 值
    if EAI_curve:
        max_EAI_entry = max(EAI_curve, key=lambda x: x['EAI'])
        max_EAI_t = max_EAI_entry['t']
        # 找到对应的 K
        for r in results:
            if abs(r['t'] - max_EAI_t) < 200:
                print(f"EAI 峰值时 K = {r['K']:.3f}")
                break

    return {'results': results, 'EAI_curve': EAI_curve}


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("D4-S18-r16：时变参数动态实验 — EAI 验证")
    print("基于 r16 核心发现：静态参数无相变，需要动态演化")
    print("=" * 60)

    all_results = {}

    try:
        # 协议 R1：参数震荡
        all_results['R1_oscillation'] = protocol_oscillating_params(
            K0=1.5, alpha=0.3, omega=0.002, T=10000
        )

        # 协议 R2：阶跃跳跃
        all_results['R2_step_hopping'] = protocol_step_hopping(
            K_low=0.8, K_high=2.0, T=10000
        )

        # 协议 R3：斜坡扫描
        all_results['R3_ramp_scan'] = protocol_ramp_scan(
            K_start=0.5, K_end=3.0, T=15000
        )

        # 保存结果
        output = {
            'R1_oscillation': {
                'summary': {
                    'I_C_mean': float(np.mean([r['I_C'] for r in all_results['R1_oscillation']['results']])),
                    'chimera_rate': float(np.mean([r['chimera'] for r in all_results['R1_oscillation']['results']])),
                }
            },
            'R2_step_hopping': {
                'summary': {
                    'I_C_mean': float(np.mean([r['I_C'] for r in all_results['R2_step_hopping']['results']])),
                    'chimera_rate': float(np.mean([r['chimera'] for r in all_results['R2_step_hopping']['results']])),
                }
            },
            'R3_ramp_scan': {
                'summary': {
                    'I_C_mean': float(np.mean([r['I_C'] for r in all_results['R3_ramp_scan']['results']])),
                    'chimera_rate': float(np.mean([r['chimera'] for r in all_results['R3_ramp_scan']['results']])),
                }
            }
        }

        with open('/tmp/r16_timvarying_results.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("\n" + "=" * 60)
        print("结果已保存到 /tmp/r16_timvarying_results.json")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
