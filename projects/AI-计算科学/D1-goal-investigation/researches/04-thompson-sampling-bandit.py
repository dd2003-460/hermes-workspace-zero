#!/usr/bin/env python3
"""
Thompson Sampling 多臂老虎机实证研究
研究问题: "探索-利用折衷是否可以通过 Thompson sampling 最优求解？"
方法论: Beta-Bernoulli conjugate prior + Monte Carlo 验证
"""
import numpy as np
from scipy import stats
import json

def run_bandit(n_arms=5, n_rounds=1000, n_experiments=500):
    """运行 Thompson Sampling 多臂老虎机实验
    
    Returns: dict with experimental results
    """
    np.random.seed(42)
    true_means = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    
    total_regret_per_round = np.zeros(n_rounds)
    
    for exp in range(n_experiments):
        alpha = np.ones(n_arms)
        beta_param = np.ones(n_arms)
        cumulative_regret = np.zeros(n_rounds)
        regret = 0.0
        
        for round_i in range(n_rounds):
            samples = np.array([
                stats.beta.rvs(alpha[i], beta_param[i])
                for i in range(n_arms)
            ])
            chosen = np.argmax(samples)
            reward = np.random.binomial(1, true_means[chosen])
            alpha[chosen] += reward
            beta_param[chosen] += (1 - reward)
            
            instant_regret = true_means[np.argmax(true_means)] - true_means[chosen]
            regret += instant_regret
            cumulative_regret[round_i] += regret
        
        total_regret_per_round += cumulative_regret
    
    avg_regret = total_regret_per_round / n_experiments
    
    alpha = np.ones(n_arms)
    beta_param = np.ones(n_arms)
    choices_last_100 = []
    for round_i in range(n_rounds):
        samples = np.array([
            stats.beta.rvs(alpha[i], beta_param[i])
            for i in range(n_arms)
        ])
        chosen = np.argmax(samples)
        if round_i >= n_rounds - 100:
            choices_last_100.append(chosen)
        reward = np.random.binomial(1, true_means[chosen])
        alpha[chosen] += reward
        beta_param[chosen] += (1 - reward)
    
    choice_counts = np.bincount(choices_last_100, minlength=n_arms)
    
    return {
        "avg_cumulative_regret": avg_regret.tolist(),
        "optimal_choice_rate_last_100": choice_counts.tolist(),
        "true_means": true_means.tolist(),
        "n_experiments": n_experiments,
        "n_rounds": n_rounds,
        "final_avg_regret": float(avg_regret[-1]),
        "optimal_arm_idx": int(np.argmax(true_means)),
    }

if __name__ == "__main__":
    results = run_bandit()
    print(json.dumps(results, indent=2))
