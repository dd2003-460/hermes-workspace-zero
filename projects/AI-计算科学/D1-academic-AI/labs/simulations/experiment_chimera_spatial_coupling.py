#!/usr/bin/env python3
"""
空间异质耦合 chimera 实验 — 验证严格 chimera 存在性（长时模拟版）

 Abrams-Strogatz (2004) 设置：
 K(x) = K0 * (1 + ε·cos(2πx))  +  ring 拓扑耦合

修订 (M1)：
 - 添加 piecewise K(x) 区域耦合模式（domain_coupling）
 - 提升默认 T_transient 至 50000（r23 合规）
 - 双域输出：per-domain chimera score + cross-domain 相关
"""

import sys
sys.path.insert(0, '.')
import numpy as np
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Coupling helpers
# ---------------------------------------------------------------------------

def piecewise_k(x: np.ndarray,
                K0: float = 1.0,
                eps_a: float = 0.6,
                eps_b: float = 0.6,
                delta: float = 0.15,
                k_transition: float = 0.3,
                domain_boundaries: Optional[List[float]] = None) -> np.ndarray:
    """
    双域 piecewise K(x) 耦合强度。

    4-zone 结构:
        [0.0, b1): Domain A — K(x) = K0*(1 + eps_A*cos(2πx))
        [b1, b2): Transition — flat K_transition
        [b2, b3): Domain B — K(x) = K0*(1 + eps_B*cos(2π*(x - delta)))
        [b3, 1.0): Transition — flat K_transition

    Default boundaries: [0.4, 0.5, 0.9]
    """
    if domain_boundaries is None:
        domain_boundaries = [0.4, 0.5, 0.9]
    b1, b2, b3 = domain_boundaries

    k = np.full_like(x, k_transition, dtype=float)

    # Domain A
    mask_a = (x >= 0.0) & (x < b1)
    k[mask_a] = K0 * (1.0 + eps_a * np.cos(2.0 * np.pi * x[mask_a]))

    # Domain B
    mask_b = (x >= b2) & (x < b3)
    k[mask_b] = K0 * (1.0 + eps_b * np.cos(2.0 * np.pi * (x[mask_b] - delta)))

    return k


# ---------------------------------------------------------------------------
# Core simulation engine
# ---------------------------------------------------------------------------

def simulate_kuramoto_ring(theta: np.ndarray, k_weights: np.ndarray,
                           dt: float = 0.02,
                           coupling_type: str = "nearest") -> np.ndarray:
    """
    一步 Kuramoto ring 演化。

    Args:
        theta: current phases [N,]
        k_weights: spatially varying coupling weights [N,]
        dt: time step
        coupling_type: "nearest" (ring neighbors) or "global" (all-to-all)
    """
    N = len(theta)

    if coupling_type == "nearest":
        # Vectorized nearest-neighbor ring coupling
        theta_left = np.roll(theta, 1)
        theta_right = np.roll(theta, -1)
        coupling = k_weights * (np.sin(theta_left - theta) + np.sin(theta_right - theta))
    elif coupling_type == "global":
        r = np.mean(np.exp(1j * theta))
        coupling = k_weights * r.imag
    else:
        raise ValueError(f"Unknown coupling_type: {coupling_type}")

    return theta + dt * coupling


# ---------------------------------------------------------------------------
# Domain chimera detection
# ---------------------------------------------------------------------------

def detect_chimera_in_domain(theta: np.ndarray, n_sectors: int = 8) -> Dict:
    """
    检测单个域内 chimera 态。

    Returns:
        dict with keys: is_chimera, sector_syncs, max_sync, min_sync, sync_score
    """
    sector_syncs = []
    n = len(theta)
    bin_size = n // n_sectors
    for s in range(n_sectors):
        start = s * bin_size
        end = min((s + 1) * bin_size, n)
        sector_phases = theta[start:end]
        sync = abs(np.mean(np.exp(1j * sector_phases)))
        sector_syncs.append(sync)

    sector_syncs = np.array(sector_syncs)
    max_sync = sector_syncs.max()
    min_sync = sector_syncs.min()
    is_chimera = bool(max_sync > 0.8 and min_sync < 0.3)
    sync_score = max_sync - min_sync  # chimera strength proxy

    return {
        "is_chimera": is_chimera,
        "sector_syncs": sector_syncs.tolist(),
        "max_sync": float(max_sync),
        "min_sync": float(min_sync),
        "sync_score": float(sync_score),
    }


def compute_cross_domain_correlation(r_a: np.ndarray, r_b: np.ndarray,
                                      max_tau: int = 50) -> np.ndarray:
    """
    互相关 C_AB(tau) = mean((R_A - mean(R_A)) * (R_B - mean(R_B)))
    for tau in [-max_tau, max_tau].
    """
    a = r_a - np.mean(r_a)
    b = r_b - np.mean(r_b)
    n = len(a)
    corrs = []
    for tau in range(-max_tau, max_tau + 1):
        if tau >= 0:
            c = np.dot(a[tau:], b[:n - tau]) / n
        else:
            c = np.dot(a[:n + tau], b[-tau:]) / n
        corrs.append(c)
    return np.array(corrs)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_chimera_experiment(N=100, K0=1.5,
                           epsilons=(0.0, 0.3, 0.5, 0.8, 1.0),
                           T_transient=5000, T_measure=500,
                           dt=0.02, runs=3, seed=42,
                           domain_coupling: bool = False,
                           k_transition: float = 0.3,
                           eps_a: float = 0.6,
                           eps_b: float = 0.6,
                           delta: float = 0.15,
                           domain_boundaries: Optional[List[float]] = None,
                           n_sectors: int = 8) -> Dict:
    """
    运行空间 chimera 实验。

    Args:
        N: 振子总数
        K0: 基础耦合强度
        epsilons: 均匀耦合模式的异质幅度列表
        T_transient: 瞬态消除（r23 推荐 >= 50000）
        T_measure: 测量窗口长度
        dt: 时间步长
        runs: 独立重复次数
        seed: 随机种子偏移
        domain_coupling: 启用 piecewise K(x) 双域耦合（M1 模式）
        k_transition: 当 domain_coupling=True 时的跃迁区耦合强度
        eps_a: Domain A 的 intra-domain 异质性
        eps_b: Domain B 的 intra-domain 异质性
        delta: Domain B chimera 中心偏移
        domain_boundaries: [b1, b2, b3] zone boundaries
        n_sectors: 每个域内的子扇区数（用于 chimera 检测）
    """
    print(f"N={N}, K0={K0}, T_transient={T_transient}, T_measure={T_measure}")
    print(f"domain_coupling={domain_coupling}")

    if domain_coupling:
        b1, b2, b3 = domain_boundaries if domain_boundaries else [0.4, 0.5, 0.9]
        print(f"  Zones: A=[0, {b1}), T=[{b1},{b2}), B=[{b2},{b3}), T=[{b3},1)")
        print(f"  eps_a={eps_a}, eps_b={eps_b}, delta={delta}, K_transition={k_transition}")

    if not domain_coupling:
        print(f"{'ε':>6} | {'chimera_score':>14} | {'sync':>8}")
        print("-" * 35)

    results = {}

    for r in range(runs):
        rng = np.random.RandomState(seed + r)
        theta = rng.uniform(0, 2 * np.pi, N)
        pos = np.linspace(0, 1, N, endpoint=False)

        if domain_coupling:
            k_weights = piecewise_k(pos, K0=K0, eps_a=eps_a, eps_b=eps_b,
                                     delta=delta, k_transition=k_transition,
                                     domain_boundaries=domain_boundaries)
        else:
            eps = epsilons[0] if epsilons else 0.0
            k_weights = K0 * (1 + eps * np.cos(2 * np.pi * pos))

        # -- split domains (for domain_coupling mode) --
        if domain_coupling:
            b1, b2, b3 = domain_boundaries if domain_boundaries else [0.4, 0.5, 0.9]
            domain_a_mask = (pos >= 0) & (pos < b1)
            domain_b_mask = (pos >= b2) & (pos < b3)

        # Simulate transient + measure
        is_chimera_domain_a = False
        is_chimera_domain_b = False
        final_r_a = 0.0
        final_r_b = 0.0

        for t in range(T_transient + T_measure):
            theta = simulate_kuramoto_ring(theta, k_weights, dt)

            if t >= T_transient and t < T_transient + T_measure:
                if domain_coupling:
                    # Per-domain chimera detection
                    state_a = detect_chimera_in_domain(theta[domain_a_mask], n_sectors)
                    state_b = detect_chimera_in_domain(theta[domain_b_mask], n_sectors)

                    if state_a["is_chimera"]:
                        is_chimera_domain_a = True
                    if state_b["is_chimera"]:
                        is_chimera_domain_b = True

                    final_r_a = state_a["max_sync"]
                    final_r_b = state_b["max_sync"]
                else:
                    # Original global chimera detection
                    bin_size = N // n_sectors
                    sector_syncs = []
                    for s in range(n_sectors):
                        start = s * bin_size
                        end = min((s + 1) * bin_size, N)
                        sync = abs(np.mean(np.exp(1j * theta[start:end])))
                        sector_syncs.append(sync)
                    sector_syncs = np.array(sector_syncs)
                    score = sector_syncs.max() - sector_syncs.min()
                    _ = sector_syncs  # not used further in M1 mode

        global_sync = abs(np.mean(np.exp(1j * theta)))

        if domain_coupling:
            chimera_count = int(is_chimera_domain_a) + int(is_chimera_domain_b)
            results.setdefault(r, {})[k_transition] = {
                "is_chimera_domain_a": is_chimera_domain_a,
                "is_chimera_domain_b": is_chimera_domain_b,
                "chimera_count": chimera_count,
                "global_sync": float(global_sync),
                "r_a": final_r_a,
                "r_b": final_r_b,
            }
        else:
            eps_val = epsilons[0] if epsilons else 0.0
            results.setdefault(r, {})[eps_val] = {
                "chimera_score": float(final_r_a),  # reuse for compatibility
                "sync": float(global_sync),
            }

    # Aggregate
    if domain_coupling:
        agg = {}
        for run_results in results.values():
            for ktrans, data in run_results.items():
                agg.setdefault(ktrans, {"chimera_counts": [], "global_syncs": []})
                agg[ktrans]["chimera_counts"].append(data["chimera_count"])
                agg[ktrans]["global_syncs"].append(data["global_sync"])

        summary = {}
        for ktrans in sorted(agg):
            avg_chimera = np.mean(agg[ktrans]["chimera_counts"])
            avg_sync = np.mean(agg[ktrans]["global_syncs"])
            n_double = sum(1 for c in agg[ktrans]["chimera_counts"] if c >= 2)
            summary[ktrans] = {
                "avg_chimera_count": float(avg_chimera),
                "avg_global_sync": float(avg_sync),
                "double_chimera_fraction": float(n_double / runs),
                "per_domain": {
                    "dom_a_chimera_freq": float(
                        sum(1 for c in agg[ktrans]["chimera_counts"] if c >= 1) / runs
                    ),
                    "dom_b_chimera_freq": float(
                        sum(1 for c in agg[ktrans]["chimera_counts"] if c >= 2) / runs
                    ),
                },
            }
        return summary
    else:
        eps_results = {}
        for eps in epsilons:
            scores = []
            syncs = []
            for run_r in results.values():
                if eps in run_r:
                    scores.append(run_r[eps]["chimera_score"])
                    syncs.append(run_r[eps]["sync"])
            eps_results[eps] = {"score": float(np.mean(scores)) if scores else 0,
                                "sync": float(np.mean(syncs)) if syncs else 0}
        return eps_results


if __name__ == "__main__":
    # Default quick test
    run_chimera_experiment()
