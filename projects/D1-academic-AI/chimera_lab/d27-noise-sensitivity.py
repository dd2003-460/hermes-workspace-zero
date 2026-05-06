#!/usr/bin/env python3
"""D27 噪声敏感度分析"""
import numpy as np
import json
from datetime import datetime

n_trials = 100
n_dim = 5
n_researchers = 13
step_size = 0.1

results = []
for noise in [0.0, 0.01, 0.05, 0.1, 0.2]:
    epsilon = 0.1 if noise > 0 else 1e-6
    T_list, D0_list = [], []
    for trial in range(n_trials):
        rng = np.random.RandomState(trial * 7 + 42)
        x_opt = rng.randn(n_dim) * 10
        optimal_points = [x_opt] * n_researchers
        spread = rng.uniform(5, 60)
        theta = rng.randn(n_researchers, n_dim) * spread
        theta_init = theta.copy()
        
        converged = np.zeros(n_researchers, dtype=bool)
        convergence_time = np.full(n_researchers, -1)
        
        for t in range(3000):
            for i in range(n_researchers):
                grad = 2 * (theta[i] - optimal_points[i])
                theta[i] -= step_size * grad + noise * np.random.randn(n_dim)
            if t > 100:
                for i in range(n_researchers):
                    if not converged[i] and convergence_time[i] == -1:
                        dist = np.linalg.norm(theta[i] - optimal_points[i])
                        if dist < epsilon:
                            converged[i] = True
                            convergence_time[i] = t
            if np.all(converged):
                break
        
        if convergence_time[0] > 0 and convergence_time[1] > 0:
            T_list.append(max(convergence_time[0], convergence_time[1]))
            D0_list.append(np.linalg.norm(theta_init[0] - theta_init[1]))
    
    if len(T_list) > 10:
        log_d0 = np.log(np.array(D0_list)**2 / epsilon**2)
        ts = np.array(T_list)
        A = np.vstack([log_d0, np.ones_like(log_d0)]).T
        slope, intercept = np.linalg.lstsq(A, ts, rcond=None)[0]
        ss_res = np.sum((ts - (slope * log_d0 + intercept))**2)
        ss_tot = np.sum((ts - np.mean(ts))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else (1.0 if np.std(ts) < 0.5 else 0.0)
    else:
        r_squared, slope, intercept = 0.0, 0.0, 0.0
    
    results.append({
        'noise': float(noise),
        'valid_trials': len(T_list),
        'r_squared': float(r_squared),
        'slope': float(slope),
        'intercept': float(intercept),
        'mean_T': float(np.mean(ts)) if len(T_list) > 0 else 0.0,
        'std_T': float(np.std(ts)) if len(T_list) > 0 else 0.0,
        'epsilon_used': float(epsilon)
    })

output = {
    'config': {'n_trials': n_trials, 'n_dim': n_dim, 'n_researchers': n_researchers, 'step_size': step_size},
    'results': results,
    'timestamp': datetime.now().isoformat()
}

with open('d27-noise-sensitivity.json', 'w') as f:
    json.dump(output, f, indent=2)

print('D27 Noise Sensitivity Analysis:')
print(f'{"Noise":>8} | {"Valid":>7} | {"R²":>8} | {"Slope":>8} | {"Mean T":>7}')
print('-' * 60)
for r in results:
    print(f'{r["noise"]:8.2f} | {r["valid_trials"]:7d} | {r["r_squared"]:8.4f} | {r["slope"]:8.4f} | {r["mean_T"]:7.1f}')
print('\nSaved to: d27-noise-sensitivity.json')
