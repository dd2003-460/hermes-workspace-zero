#!/usr/bin/env python3
"""
策略比较: ε-greedy vs UCB vs Thompson Sampling
验证 Thompson sampling 的优越性
"""
import numpy as np
from scipy import stats
import json

def run_epsilon_greedy(true_means, n_arms, n_rounds, epsilon=0.1):
    rewards = np.zeros(n_arms)
    counts = np.zeros(n_arms)
    cumulative_regret = 0.0
    
    for r in range(n_rounds):
        if np.random.random() < epsilon:
            chosen = np.random.randint(n_arms)
        else:
            chosen = np.argmax(rewards / (counts + 1))
        
        reward = np.random.binomial(1, true_means[chosen])
        rewards[chosen] += reward
        counts[chosen] += 1
        cumulative_regret += (true_means[np.argmax(true_means)] - true_means[chosen])
    
    return cumulative_regret

def run_ucb(true_means, n_arms, n_rounds):
    rewards = np.zeros(n_arms)
    counts = np.zeros(n_arms)
    cumulative_regret = 0.0
    total_counts = 0
    
    for r in range(n_rounds):
        if any(counts == 0):
            chosen = np.where(counts == 0)[0][0]
        else:
            ucb_vals = rewards / counts + np.sqrt(2 * np.log(total_counts + 1) / counts)
            chosen = np.argmax(ucb_vals)
        
        reward = np.random.binomial(1, true_means[chosen])
        rewards[chosen] += reward
        counts[chosen] += 1
        total_counts += 1
        cumulative_regret += (true_means[np.argmax(true_means)] - true_means[chosen])
    
    return cumulative_regret

def run_thompson_sampling(true_means, n_arms, n_rounds):
    alpha = np.ones(n_arms)
    beta_param = np.ones(n_arms)
    cumulative_regret = 0.0
    
    for r in range(n_rounds):
        samples = np.array([stats.beta.rvs(alpha[i], beta_param[i]) for i in range(n_arms)])
        chosen = np.argmax(samples)
        reward = np.random.binomial(1, true_means[chosen])
        alpha[chosen] += reward
        beta_param[chosen] += (1 - reward)
        cumulative_regret += (true_means[np.argmax(true_means)] - true_means[chosen])
    
    return cumulative_regret

if __name__ == "__main__":
    np.random.seed(42)
    true_means = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    n_arms, n_rounds, n_exps = 5, 1000, 200
    
    strategies = {
        "epsilon_greedy_01": [],
        "epsilon_greedy_001": [],
        "ucb": [],
        "thompson_sampling": [],
    }
    
    for exp in range(n_exps):
        strategies["epsilon_greedy_01"].append(
            run_epsilon_greedy(true_means, n_arms, n_rounds, epsilon=0.1))
        strategies["epsilon_greedy_001"].append(
            run_epsilon_greedy(true_means, n_arms, n_rounds, epsilon=0.01))
        strategies["ucb"].append(
            run_ucb(true_means, n_arms, n_rounds))
        strategies["thompson_sampling"].append(
            run_thompson_sampling(true_means, n_arms, n_rounds))
    
    results = {}
    for name, regrett in strategies.items():
        results[name] = {
            "mean_regret": float(np.mean(regrett)),
            "std_regret": float(np.std(regrett)),
            "median_regret": float(np.median(regrett)),
        }
    
    results["meta"] = {
        "n_experiments": n_exps,
        "n_rounds": n_rounds,
        "true_means": true_means.tolist(),
    }
    
    print(json.dumps(results, indent=2))
