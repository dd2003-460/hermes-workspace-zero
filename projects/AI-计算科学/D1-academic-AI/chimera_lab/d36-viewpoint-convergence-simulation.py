#!/usr/bin/env python3
"""
D36：代际观点收敛动力学模拟

验证四个命题：
- D36-A：代际观点收敛模拟（Lyapunov 吸引子）
- D36-B：遗传-环境权重转换
- D36-C：关键期效应
- D36-D：环境相似度逆转
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class D36Config:
    alpha: float = 0.5       # 遗传同构性
    beta: float = 0.1        # 信息惩罚权重
    chi0: float = 0.1        # 初始信息灌注
    v: float = 0.05          # 信息灌注速率
    tau_plastic: float = 20  # 可塑性时间常数（年）
    dt: float = 0.1          # 时间步长
    T: float = 100           # 总时间（年）
    d: int = 5               # 观点维度
    Sigma_alpha_base: float = 0.3
    Sigma_env: float = 0.5

class D36Simulator:
    def __init__(self, config: D36Config):
        self.cfg = config
        self.t_vec = np.linspace(0, config.T, int(config.T / config.dt))
        np.random.seed(42)
        self.phi_p = np.random.randn(config.d)
        self.phi_c = self.phi_p + np.random.randn(config.d) * 0.5
        self.trajectory = []
        self.K_trajectory = []

    def info_infusion(self, t):
        return self.cfg.chi0 + self.cfg.v * t

    def plasticity_decay(self, t):
        return np.exp(-t / self.cfg.tau_plastic)

    def kalman_gain(self, t):
        Sigma_alpha = self.cfg.Sigma_alpha_base * (1 - self.cfg.alpha)
        chi = self.info_infusion(t)
        return Sigma_alpha / (Sigma_alpha + self.cfg.Sigma_env / max(chi, 1e-6))

    def step(self, t, dt):
        alpha = self.cfg.alpha
        grad_V_c = 2 * (1 - alpha) * (self.phi_c - self.phi_p)
        K = self.kalman_gain(t)
        phi_genetic = self.phi_p * (1 - K) + np.random.randn(len(self.phi_p)) * self.cfg.Sigma_alpha_base
        dphi_c = dt * (-grad_V_c + K * (phi_genetic - self.phi_c))
        self.phi_c += dphi_c
        dist = np.linalg.norm(self.phi_c - self.phi_p)
        self.trajectory.append(float(dist))
        self.K_trajectory.append(float(K))

    def run(self):
        for i in range(len(self.t_vec)):
            t = i * self.cfg.dt
            self.step(t, self.cfg.dt)
        return {
            't': self.t_vec,
            'dist': self.trajectory,
            'K': self.K_trajectory
        }

def fit_exponential_decay(t, dist):
    """拟合 dist(t) = d0 * exp(-lambda * t) + d_inf"""
    from scipy.optimize import curve_fit

    def exp_decay(t_val, d0, lam, d_inf):
        return d0 * np.exp(-lam * t_val) + d_inf

    try:
        popt, _ = curve_fit(exp_decay, t, dist)
        r_squared = 1 - np.sum((dist - exp_decay(t, *popt))**2) / np.sum((dist - np.mean(dist))**2)
        return float(popt[0]), float(popt[1]), float(popt[2]), float(r_squared)
    except:
        return 0.0, 0.0, 0.0, 0.0

class D36Experiment:
    def __init__(self):
        self.results = {}

    def experiment_A(self):
        print("\n[D36-A] 代际观点收敛模拟 — Lyapunov 吸引子验证")
        print("=" * 60)
        results = {}
        for alpha in [0.3, 0.5, 0.7, 0.9]:
            config = D36Config(alpha=alpha)
            sim = D36Simulator(config)
            traj = sim.run()

            d0, lam, d_inf, r_sq = fit_exponential_decay(traj['t'], traj['dist'])

            results[f'alpha_{alpha}'] = {
                'convergence_rate_lambda': lam,
                'asymptotic_distance': d_inf,
                'fit_r_squared': r_sq,
                'final_distance': float(traj['dist'][-1]),
                'initial_distance': float(traj['dist'][0])
            }
            print(f"  alpha={alpha}: lambda={lam:.4f}, d_inf={d_inf:.4f}, R-squared={r_sq:.4f}")
        self.results['A'] = results
        return results

    def experiment_B(self):
        print("\n[D36-B] 遗传-环境权重转换验证")
        print("=" * 60)
        results = {}
        for alpha in [0.3, 0.5, 0.7, 0.9]:
            config = D36Config(alpha=alpha)
            sim = D36Simulator(config)
            traj = sim.run()

            K_arr = np.array(traj['K'])
            t_arr = np.array(traj['t'])

            # 找 K=0.5 附近的点
            crossing_idx = np.where(np.abs(K_arr - 0.5) < 0.08)[0]

            if len(crossing_idx) > 0:
                chi_c = float(config.chi0 + config.v * t_arr[crossing_idx[0]])
                t_cross = float(t_arr[crossing_idx[0]])
            else:
                chi_c = None
                t_cross = None

            results[f'alpha_{alpha}'] = {
                'chi_c': chi_c,
                't_at_K0.5': t_cross,
                'K_initial': float(K_arr[0]),
                'K_final': float(K_arr[-1])
            }
            chi_str = f"{chi_c:.4f}" if chi_c is not None else "N/A"
            print(f"  alpha={alpha}: chi_c={chi_str}, K_early={float(K_arr[0]):.3f}, K_late={float(K_arr[-1]):.3f}")
        self.results['B'] = results
        return results

    def experiment_C(self):
        print("\n[D36-C] 关键期效应验证")
        print("=" * 60)
        t_pre = 10
        t_post = 40
        config = D36Config()
        sim = D36Simulator(config)

        for i in range(int(t_post / config.dt)):
            t = i * config.dt
            if t >= t_post:
                break
            sim.step(t, config.dt)

        psi_pre = sim.plasticity_decay(t_pre)
        psi_post = sim.plasticity_decay(t_post)
        ratio = float(psi_pre / psi_post) if psi_post > 1e-6 else 999.9

        results = {
            't_pre': t_pre,
            't_post': t_post,
            'psi_pre': float(psi_pre),
            'psi_post': float(psi_post),
            'sensitivity_ratio': ratio,
            'expected_ratio': float(np.exp(t_post / config.tau_plastic) / np.exp(t_pre / config.tau_plastic))
        }
        print(f"  t={t_pre}: psi={psi_pre:.4f}")
        print(f"  t={t_post}: psi={psi_post:.4f}")
        print(f"  灵敏度比: {ratio:.2f} (预期 {results['expected_ratio']:.2f})")
        self.results['C'] = results
        return results

    def experiment_D(self):
        print("\n[D36-D] 环境相似度逆转验证")
        print("=" * 60)
        results = {'low_alpha': {}, 'high_alpha': {}}

        np.random.seed(123)
        for rho in [0.2, 0.5, 0.8]:
            config = D36Config(alpha=0.3)
            sim = D36Simulator(config)
            sim.phi_p = np.random.randn(config.d) * rho
            sim.phi_c = sim.phi_p + np.random.randn(config.d) * (1 - rho) * 0.5
            for i in range(int(config.T / config.dt)):
                t = i * config.dt
                if t >= config.T:
                    break
                sim.step(t, config.dt)
            results['low_alpha'][f'rho_{rho}'] = round(sim.trajectory[-1], 4)

        np.random.seed(123)
        for rho in [0.2, 0.5, 0.8]:
            config = D36Config(alpha=0.9)
            sim = D36Simulator(config)
            sim.phi_p = np.random.randn(config.d) * rho
            sim.phi_c = sim.phi_p + np.random.randn(config.d) * (1 - rho) * 0.5
            for i in range(int(config.T / config.dt)):
                t = i * config.dt
                if t >= config.T:
                    break
                sim.step(t, config.dt)
            results['high_alpha'][f'rho_{rho}'] = round(sim.trajectory[-1], 4)

        for alpha_label, alpha_results in results.items():
            print(f"  {alpha_label}:")
            for rho_key, final_dist in alpha_results.items():
                print(f"    {rho_key}: {final_dist:.4f}")
        self.results['D'] = results
        return results

    def save_results(self, output_path):
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

        data = fix_serialization(self.results)
        data['metadata'] = {
            'date': datetime.now().isoformat(),
            'experiment': 'D36-Intergenerational-Viewpoint-Convergence',
            'propositions': ['D36-1: Lyapunov Attractor', 'D36-2: Genetic Lower Bound',
                           'D36-3: Critical Period', 'D36-4: Environment Reversal']
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n[Save] Results written to {output_path}")
        return data

def main():
    experiment = D36Experiment()
    experiment.experiment_A()
    experiment.experiment_B()
    experiment.experiment_C()
    experiment.experiment_D()
    experiment.save_results('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d36-results.json')

if __name__ == '__main__':
    main()
