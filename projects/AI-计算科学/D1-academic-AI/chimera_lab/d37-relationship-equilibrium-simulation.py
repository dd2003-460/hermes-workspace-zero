#!/usr/bin/env python3
"""
D37：关系开销均衡动力学模拟

验证四个命题：
- D37-A：Nash 均衡数值模拟
- D37-B：非对称鲁棒性测试
- D37-C：死区阈值测量
- D37-D：迟滞环可视化
"""

import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class D37Config:
    w_A: list = None  # A 的效用权重
    w_B: list = None  # B 的效用权重
    lam_A: float = 0.1  # A 的惯性惩罚
    lam_B: float = 0.1  # B 的惯性惩罚
    mu_A: float = 0.2   # A 的互操作收益
    mu_B: float = 0.2   # B 的互操作收益
    K_A: float = 0.5    # A 的反馈增益
    K_B: float = 0.5    # B 的反馈增益
    K_A_exp: float = 0.5  # A 扩张期增益
    K_A_con: float = 0.3  # A 收缩期增益
    K_B_exp: float = 0.5
    K_B_con: float = 0.3
    epsilon_dead: float = 0.05  # 死区阈值
    dt: float = 0.01      # 时间步长
    T: float = 500        # 总步数
    d: int = 4            # 开销维度
    c_min: float = 0.0    # 开销下界
    c_max: float = 1.0    # 开销上界

    def __post_init__(self):
        if self.w_A is None:
            self.w_A = [0.3, 0.3, 0.2, 0.2]
        if self.w_B is None:
            self.w_B = [0.2, 0.3, 0.3, 0.2]

def clip_costs(c, c_min, c_max):
    """裁剪开销到可行域"""
    return np.clip(c, c_min, c_max)

def gradient_utility(w, c_self, c_other, lam, mu, d):
    """计算效用梯度"""
    w_arr = np.array(w, dtype=float)
    c_self_arr = np.array(c_self, dtype=float)
    c_other_arr = np.array(c_other, dtype=float)
    gradient = w_arr - 2 * lam * (c_self_arr - np.ones(d) * 0.5) + mu * c_other_arr
    return gradient

def compute_imbalance(grad_A, grad_B):
    """计算失衡度"""
    return np.linalg.norm(grad_A - grad_B)

def best_response(w, c_other, lam, mu, d):
    """Nash 最佳响应解析解"""
    # U = w^T c - lam * ||c - 0.5||^2 + mu * (c . c_other)
    # max at: w - 2*lam*(c-0.5) + mu*c_other = 0
    w_arr = np.array(w, dtype=float)
    c_other_arr = np.array(c_other, dtype=float)
    c_opt = (w_arr + 2 * lam * 0.5 + mu * c_other_arr) / (2 * lam)
    return c_opt

class D37Simulator:
    def __init__(self, config):
        self.cfg = config
        self.d = config.d

        # 初始化开销向量
        np.random.seed(42)
        self.c_A = np.random.rand(config.d) * (config.c_max - config.c_min) + config.c_min
        self.c_B = np.random.rand(config.d) * (config.c_max - config.c_min) + config.c_min

        # 状态变量
        self.prev_delta = compute_imbalance(
            gradient_utility(config.w_A, self.c_A, self.c_B, config.lam_A, config.mu_A, config.d),
            gradient_utility(config.w_B, self.c_B, self.c_A, config.lam_B, config.mu_B, config.d)
        )
        self.is_expanding = True  # 跟踪扩张/收缩

        # 轨迹
        self.trajectory_A = []
        self.trajectory_B = []
        self.imbalance_traj = []
        self.hysteresis_A = []
        self.hysteresis_B = []

    def update_wealth(self):
        """基于失衡的反馈更新"""
        grad_A = gradient_utility(self.cfg.w_A, self.c_A, self.c_B, self.cfg.lam_A, self.cfg.mu_A, self.d)
        grad_B = gradient_utility(self.cfg.w_B, self.c_B, self.c_A, self.cfg.lam_B, self.cfg.mu_B, self.d)

        delta = compute_imbalance(grad_A, grad_B)

        # 死区效应
        if delta < self.cfg.epsilon_dead:
            return delta

        # 确定扩张/收缩方向
        if delta > self.prev_delta:
            expanding = True
        else:
            expanding = False

        # 方向依赖的增益
        K_A_use = self.cfg.K_A_exp if expanding else self.cfg.K_A_con
        K_B_use = self.cfg.K_B_exp if expanding else self.cfg.K_B_con

        # 负反馈更新
        grad_diff = grad_A - grad_B
        self.c_A -= K_A_use * np.sign(grad_diff) * delta * self.cfg.dt
        self.c_B += K_B_use * np.sign(grad_diff) * delta * self.cfg.dt

        # 裁剪
        self.c_A = clip_costs(self.c_A, self.cfg.c_min, self.cfg.c_max)
        self.c_B = clip_costs(self.c_B, self.cfg.c_min, self.cfg.c_max)

        self.prev_delta = delta
        self.is_expanding = expanding

        return delta

    def nash_iteration_step(self):
        """单步 Nash 最佳响应"""
        self.c_A = clip_costs(best_response(self.cfg.w_A, self.c_B, self.cfg.lam_A, self.cfg.mu_A, self.d), self.cfg.c_min, self.cfg.c_max)
        self.c_B = clip_costs(best_response(self.cfg.w_B, self.c_A, self.cfg.lam_B, self.cfg.mu_B, self.d), self.cfg.c_min, self.cfg.c_max)

    def run_wealth_update(self):
        """运行反馈更新模拟"""
        for t in range(int(self.cfg.T)):
            delta = self.update_wealth()
            self.trajectory_A.append(np.linalg.norm(self.c_A))
            self.trajectory_B.append(np.linalg.norm(self.c_B))
            self.imbalance_traj.append(delta)
            if t % 50 == 0:  # 采样迟滞数据
                self.hysteresis_A.append(self.c_A.copy())
                self.hysteresis_B.append(self.c_B.copy())
        return {
            'traj_A': self.trajectory_A,
            'traj_B': self.trajectory_B,
            'imbalance': self.imbalance_traj,
            'hysteresis_A': [p.tolist() for p in self.hysteresis_A],
            'hysteresis_B': [p.tolist() for p in self.hysteresis_B]
        }

    def run_nash_convergence(self):
        """运行 Nash 收敛模拟"""
        n_iter = 200
        converged = False
        for t in range(n_iter):
            self.nash_iteration_step()
            # 检查收敛
            grad_A = gradient_utility(self.cfg.w_A, self.c_A, self.c_B, self.cfg.lam_A, self.cfg.mu_A, self.d)
            grad_B = gradient_utility(self.cfg.w_B, self.c_B, self.c_A, self.cfg.lam_B, self.cfg.mu_B, self.d)
            delta = compute_imbalance(grad_A, grad_B)
            if delta < 1e-6:
                converged = True
                break
        return {
            'converged': converged,
            'iterations': t + 1,
            'c_A': self.c_A.tolist(),
            'c_B': self.c_B.tolist(),
            'final_imbalance': float(delta)
        }

class D37Experiment:
    def __init__(self):
        self.results = {}

    def experiment_A(self):
        print("\n[D37-A] Nash 均衡数值模拟")
        print("=" * 60)
        config = D37Config()
        sim = D37Simulator(config)
        result = sim.run_nash_convergence()
        print(f"  收敛: {result['converged']}, 迭代: {result['iterations']}, 最终失衡: {result['final_imbalance']:.2e}")
        print(f"  c_A*: {result['c_A']}")
        print(f"  c_B*: {result['c_B']}")
        self.results['A'] = result
        return result

    def experiment_B(self):
        print("\n[D37-B] 非对称鲁棒性测试")
        print("=" * 60)
        results = {}
        for asym_level in [0.0, 0.3, 0.6, 0.9]:
            w_A = [0.3 + asym_level * x for x in [1, -1, 0.5, -0.5]]
            w_B = [0.2 - asym_level * x for x in [1, -1, 0.5, -0.5]]
            w_A = [max(0, v) for v in w_A]  # 非负
            w_B = [max(0, v) for v in w_B]
            norm_A = sum(w_A)
            norm_B = sum(w_B)
            w_A = [v / norm_A for v in w_A]
            w_B = [v / norm_B for v in w_B]

            config = D37Config(w_A=w_A, w_B=w_B)
            sim = D37Simulator(config)
            result = sim.run_nash_convergence()

            key = f"asym_{asym_level:.1f}"
            results[key] = {
                'converged': result['converged'],
                'iterations': result['iterations'],
                'final_imbalance': result['final_imbalance']
            }
            print(f"  非对称={asym_level}: 收敛={result['converged']}, 迭代={result['iterations']}")

        self.results['B'] = results
        return results

    def experiment_C(self):
        print("\n[D37-C] 死区阈值测量")
        print("=" * 60)
        results = {}
        for eps_dead in [0.01, 0.05, 0.10, 0.20]:
            config = D37Config(epsilon_dead=eps_dead)
            sim = D37Simulator(config)
            traj = sim.run_wealth_update()

            # 测量响应活跃度（有更新的比例）
            delta_arr = np.array(traj['imbalance'])
            # 统计 delta > epsilon_dead 时的更新
            active_ratio = np.mean([i < len(traj['imbalance'])-1 for i in range(len(traj['imbalance']))])
            # 实际测量：迭代中途的总变化量
            mid = len(traj['imbalance']) // 2
            early_avg = np.mean(traj['imbalance'][:mid]) if mid > 0 else 0
            late_avg = np.mean(traj['imbalance'][mid:]) if mid < len(traj['imbalance']) else 0

            key = f"eps_{eps_dead}"
            results[key] = {
                'epsilon_dead': eps_dead,
                'early_imbalance_avg': float(early_avg),
                'late_imbalance_avg': float(late_avg),
                'imbalance_ratio': float(early_avg / max(late_avg, 1e-10))
            }
            print(f"  epsilon={eps_dead}: 早期失衡={early_avg:.4f}, 晚期失衡={late_avg:.4f}, 比率={early_avg/max(late_avg, 1e-10):.2f}")

        self.results['C'] = results
        return results

    def experiment_D(self):
        print("\n[D37-D] 迟滞环可视化")
        print("=" * 60)

        # 第一阶段：扩张（增加失衡）
        config_exp = D37Config(K_A_exp=1.0, K_A_con=0.3, K_B_exp=1.0, K_B_con=0.3)
        sim = D37Simulator(config_exp)
        sim.prev_delta = 0.1  # 初始失衡
        sim.is_expanding = True

        # 模拟扩张期
        for t in range(100):
            delta = sim.update_wealth()
            sim.prev_delta = delta
            if delta > 0.3:  # 施加外部失衡增量
                delta = min(delta + 0.01, 0.5)
                sim.prev_delta = delta

        # 记录扩张峰值
        c_A_exp = sim.c_A.copy()
        c_B_exp = sim.c_B.copy()
        norm_A_exp = float(np.linalg.norm(c_A_exp))
        norm_B_exp = float(np.linalg.norm(c_B_exp))

        # 第二阶段：收缩（减少失衡）
        sim.prev_delta = sim.prev_delta + 0.1
        sim.is_expanding = False

        for t in range(100):
            delta = sim.update_wealth()
            sim.prev_delta = max(delta - 0.005, 0.05)  # 减小失衡
            if delta <= 0.05:
                break

        # 记录收缩终点
        c_A_con = sim.c_A.copy()
        c_B_con = sim.c_B.copy()
        norm_A_con = float(np.linalg.norm(c_A_con))
        norm_B_con = float(np.linalg.norm(c_B_con))

        hysteresis_area_A = abs(norm_A_exp - norm_A_con)
        hysteresis_area_B = abs(norm_B_exp - norm_B_con)

        results = {
            'norm_A_expansion': norm_A_exp,
            'norm_A_contraction': norm_A_con,
            'hysteresis_area_A': hysteresis_area_A,
            'norm_B_expansion': norm_B_exp,
            'norm_B_contraction': norm_B_con,
            'hysteresis_area_B': hysteresis_area_B,
            'total_hysteresis': hysteresis_area_A + hysteresis_area_B
        }

        print(f"  扩张期 A: {norm_A_exp:.4f}")
        print(f"  收缩期 A: {norm_A_con:.4f}")
        print(f"  迟滞面积 A: {hysteresis_area_A:.4f}")
        print(f"  扩张期 B: {norm_B_exp:.4f}")
        print(f"  收缩期 B: {norm_B_con:.4f}")
        print(f"  迟滞面积 B: {hysteresis_area_B:.4f}")
        print(f"  总迟滞面积: {results['total_hysteresis']:.4f}")

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
            elif obj is None:
                return "N/A"
            else:
                return obj

        data = fix_serialization(self.results)
        data['metadata'] = {
            'date': datetime.now().isoformat(),
            'experiment': 'D37-Relationship-Cost-Equilibrium',
            'propositions': ['D37-1: Nash Equilibrium Existence', 'D37-2: Asymmetry Robustness',
                           'D37-3: Dead Zone Threshold', 'D37-4: Hysteresis Path Dependence']
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n[Save] Results written to {output_path}")
        return data

def main():
    experiment = D37Experiment()
    experiment.experiment_A()
    experiment.experiment_B()
    experiment.experiment_C()
    experiment.experiment_D()
    experiment.save_results('/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d37-results.json')

if __name__ == '__main__':
    main()
