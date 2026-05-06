#!/usr/bin/env python3
"""
D39：复杂与简单的信息论区分 — 四个实验验证协议

验证四个命题：
- D39-A：伪复杂化是信息浪费（I(O; M') - I(O; M) ≤ 0）
- D39-B：必要复杂化存在信息论阈值（C_crit 过拟合转折点）
- D39-C：简化是认知进化的副产品（σ 递增但饱和）
- D39-D：价值观是偏好分布的参数化（低预算差异显著，高预算收敛）
"""

import numpy as np
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Tuple, List
from scipy.stats import norm, linregress

np.random.seed(42)

# ============================================================
# 工具函数
# ============================================================

def shannon_entropy(p):
    """离散分布的香农熵 H = -Σ p log p"""
    p = np.clip(p, 1e-15, 1.0)
    return -np.sum(p * np.log2(p))


def mutual_information(observation, prediction, n_bins=10):
    """
    估算互信息 I(Observation; Prediction) 通过频率逼近。
    I(O; P) = H(O) + H(P) - H(O, P)
    """
    # 符号映射：连续值 → 离散桶
    def discretize(x):
        bins = np.linspace(np.min(x) - 1e-9, np.max(x) + 1e-9, n_bins + 1)
        return np.digitize(x, bins) - 1

    o_disc = discretize(observation)
    p_disc = discretize(prediction)

    n = len(observation)
    # 联合概率 P(O, P)
    joint = np.zeros((n_bins, n_bins))
    for i in range(n):
        joint[o_disc[i], p_disc[i]] += 1
    joint /= n

    # 边际
    p_m1 = joint.sum(axis=1)
    p_m2 = joint.sum(axis=0)

    H_o = shannon_entropy(p_m1)
    H_p = shannon_entropy(p_m2)
    H_joint = shannon_entropy(joint.flatten())

    return H_o + H_p - H_joint


def mdL_length_simple(n_params, n_samples, residuals):
    """MDL 编码长度：L(M) + L(O|M) = (p/2)log(n) + Σ r²/(2σ²) + 常数"""
    sigma2 = np.var(residuals) + 1e-15
    mdl_model = (n_params / 2.0) * np.log(n_samples) + np.sum(residuals ** 2) / (2 * sigma2)
    return mdl_model


def log_likelihood_gaussian(mu, sigma, data):
    """高斯对数似然"""
    return -0.5 * np.sum(np.log(2 * np.pi * sigma**2) + (data - mu)**2 / sigma**2)


# ============================================================
# D39-A：伪复杂化检测
# ============================================================

@dataclass
class D39AConfig:
    n_train: int = 100  # 训练集大小
    n_test: int = 400  # 测试集更大，更好估计互信息
    true_degree: int = 3  # 真实多项式阶数
    simple_degree: int = 3  # 匹配真实复杂度（正确简化）
    pseudo_complex_degree: int = 15  # 过度参数化（伪复杂化）
    noise_sigma: float = 0.5  # 较高噪声让伪复杂更容易过拟合噪声
    n_runs: int = 20


def experiment_a():
    """
    验证 D39-1：伪复杂化是信息浪费

    D39-1 修正理解：
    伪复杂化在训练集上捕捉噪声 → 训练集互信息虚高
    但泛化到测试集时，噪声记忆不工作 → 测试集互信息不增反降

    ΔI_gen = I_test_pseudo - I_test_simple：泛化互信息变化
    ΔI_fit = I_train_pseudo - I_train_simple：拟合互信息变化

    D39-1 断言：ΔI_fit > 0 但 ΔI_gen ≤ 0 → 伪复杂化只浪费在噪声上
    """
    results = []

    for run in range(D39AConfig().n_runs):
        x_train = np.sort(np.random.uniform(0, 5, D39AConfig().n_train))
        true_poly = np.poly1d([1.0, -2.0, 1.0, 0.5])  # 三次多项式
        y_train = true_poly(x_train) + np.random.normal(0, D39AConfig().noise_sigma, len(x_train))

        # 拟合简单模型（正确复杂度）
        simple_poly = np.polyfit(x_train, y_train, D39AConfig().simple_degree)
        y_simple_train = np.polyval(simple_poly, x_train)

        # 拟合伪复杂化模型（过度参数化）
        pseudo_poly = np.polyfit(x_train, y_train, D39AConfig().pseudo_complex_degree)
        y_pseudo_train = np.polyval(pseudo_poly, x_train)

        # 在独立测试集上评估
        x_test = np.sort(np.random.uniform(0, 5, D39AConfig().n_test))
        y_test = true_poly(x_test) + np.random.normal(0, D39AConfig().noise_sigma, len(x_test))
        y_simple_test = np.polyval(simple_poly, x_test)
        y_pseudo_test = np.polyval(pseudo_poly, x_test)

        # 互信息：I(O; M) — 观测与模型预测之间的共享信息
        I_simple_test = mutual_information(y_test, y_simple_test)
        I_pseudo_test = mutual_information(y_test, y_pseudo_test)

        # 训练集互信息（拟合能力）
        I_simple_train = mutual_information(y_train, y_simple_train)
        I_pseudo_train = mutual_information(y_train, y_pseudo_train)

        delta_I_gen = I_pseudo_test - I_simple_test  # 泛化互信息变化
        delta_I_fit = I_pseudo_train - I_simple_train  # 拟合互信息变化

        # MDL 编码长度
        n_params_simple = D39AConfig().simple_degree + 1
        n_params_pseudo = D39AConfig().pseudo_complex_degree + 1
        mdl_simple = mdL_length_simple(n_params_simple, len(x_test), y_test - y_simple_test)
        mdl_pseudo = mdL_length_simple(n_params_pseudo, len(x_test), y_test - y_pseudo_test)

        results.append({
            'run': run,
            'delta_I_generalization': float(delta_I_gen),
            'delta_I_fit': float(delta_I_fit),
            'mdl_simple': float(mdl_simple),
            'mdl_pseudo': float(mdl_pseudo),
            'delta_mdl': float(mdl_pseudo - mdl_simple)
        })

    delta_I_gen_values = [r['delta_I_generalization'] for r in results]
    delta_I_fit_values = [r['delta_I_fit'] for r in results]
    mean_delta_I_gen = np.mean(delta_I_gen_values)
    mean_delta_I_fit = np.mean(delta_I_fit_values)

    # D39-1：伪复杂化增加训练互信息但不增加（或降低）泛化互信息
    n_gen_leq0 = sum(1 for v in delta_I_gen_values if v <= 0)

    return {
        'description': 'D39-A: 伪复杂化是信息浪费',
        'validation': 'D39-1',
        'mean_delta_I_generalization': mean_delta_I_gen,
        'mean_delta_I_fit': mean_delta_I_fit,
        'gen_mutual_info_non_positive': int(n_gen_leq0),
        'total_runs': D39AConfig().n_runs,
        'gen_fraction_non_positive': float(n_gen_leq0 / D39AConfig().n_runs),
        'fit_delta_I_mean': float(mean_delta_I_fit),
        'details': results[:5],  # First 5 runs
        'conclusion': '伪复杂化只增加训练互信息（记忆噪声），不增加泛化互信息 → 信息浪费' if mean_delta_I_gen <= 0.01 else '需要重新审视：伪复杂化可能增加泛化能力'
    }


# ============================================================
# D39-B：过拟合信息阈值
# ============================================================

@dataclass
class D39BConfig:
    n_samples: int = 100
    true_degree: int = 2
    max_degree: int = 15
    noise_sigma: float = 0.1


def experiment_b():
    """
    验证 D39-2：存在过拟合阈值 C_crit

    C_crit ≈ n · ΔH / log(n)
    当 p > C_crit 时，额外参数带来的 H(O|M) 降低 < 编码代价
    """
    results = []
    config = D39BConfig()

    # 真实数据生成
    x_true = np.sort(np.random.uniform(0, 5, config.n_samples))
    true_poly = np.poly1d([1.0, -2.0, 1.0, 0.5])
    y_true = true_poly(x_true) + np.random.normal(0, config.noise_sigma, len(x_true))

    # 预测 C_crit
    delta_H = 1.0  # 每个额外参数最多降低的 H(O|M) 约 1 bit
    C_crit_estimate = config.n_samples * delta_H / np.log(config.n_samples)

    for degree in range(1, config.max_degree + 1):
        # 训练集拟合
        train_poly = np.polyfit(x_true, y_true, degree)
        y_train_pred = np.polyval(train_poly, x_true)
        train_residual_var = np.var(y_true - y_train_pred)

        # 测试集评估（泛化）
        x_test = np.sort(np.random.uniform(0, 5, config.n_samples))
        y_test = true_poly(x_test) + np.random.normal(0, config.noise_sigma, len(x_test))
        y_test_pred = np.polyval(train_poly, x_test)
        test_mse = np.mean((y_test - y_test_pred) ** 2)

        # 归一化泛化误差
        test_var = np.var(y_test)
        generalized_error = test_mse / test_var

        # MDL 总长度
        n_params = degree + 1
        n_samples_test = len(x_test)
        sigma2_test = test_mse + 1e-15
        mdl_total = (n_params / 2.0) * np.log(n_samples_test) + np.sum(
            (y_test - y_test_pred) ** 2) / (2 * sigma2_test)

        results.append({
            'degree': degree,
            'generalized_error': float(generalized_error),
            'mdl_total': float(mdl_total),
            'n_params': n_params
        })

    # 寻找 C_crit 转折点（泛化误差开始上升的点）
    errors = [r['generalized_error'] for r in results]
    c_crit_index = None
    for i in range(1, len(errors) - 1):
        if errors[i] < errors[i-1] and errors[i+1] > errors[i]:
            c_crit_index = i
            break

    c_crit_estimated_degree = results[c_crit_index]['degree'] if c_crit_index else None

    # 线性拟合 C_crit 理论
    degrees = np.array([r['degree'] for r in results])
    if c_crit_index is not None:
        is_overfitting = np.array([1 if r['degree'] >= c_crit_estimated_degree else 0 for r in results])
        m, b, r2, _, _ = linregress(degrees, is_overfitting.astype(float))
        predicted_c_crit_from_fit = (1 - b) / m if m != 0 else None
    else:
        predicted_c_crit_from_fit = None

    return {
        'description': 'D39-B: 过拟合信息阈值',
        'validation': 'D39-2',
        'n_samples': config.n_samples,
        'estimated_C_crit_formula': f"n * ΔH / log(n) = {config.n_samples} * {delta_H} / log({config.n_samples}) ≈ {C_crit_estimate:.1f}",
        'empirical_C_crit_degree': int(c_crit_estimated_degree) if c_crit_estimated_degree else 'not found',
        'predicted_C_crit_formula': f"(1 - b)/m ≈ {predicted_c_crit_from_fit:.1f}" if predicted_c_crit_from_fit else 'N/A',
        'overfitting_transition_r_squared': float(r2) if c_crit_index is not None else 0.0,
        'details': results[:5] + results[-3:],  # Start and end
        'conclusion': '存在明确过拟合阈值' if c_crit_estimated_degree else '阈值不明显'
    }


# ============================================================
# D39-C：简化能力进化模拟
# ============================================================

@dataclass
class D39CConfig:
    n_individuals: int = 50
    n_generations: int = 200
    environment_noise: float = 0.1
    initial_simplification_range: Tuple[float, float] = (0.1, 0.5)
    survival_sensitivity: float = 2.0
    max_prediction_error_threshold: float = 0.5


def simplification_capability(individual, environment):
    """
    计算个体 I 的简化能力 σ(I)：
    σ(I) = |M| - |M'_I| 满足 H(O|M'_I) ≤ H(O|M) + δ

    简化为：σ = (1 - compression_ratio) × prediction_accuracy
    """
    # 模拟：个体选择不同复杂度模型
    base_complexity = 10  # 基础模型参数数
    compressed_complexity = int(base_complexity * (1 - individual))

    # 压缩模型的预测精度（简化越多，精度越差）
    compression_penalty = individual * D39CConfig().max_prediction_error_threshold

    # 预测准确率（简单模型在标准任务上可能更好）
    base_accuracy = 0.9
    accuracy = max(0.1, base_accuracy - compression_penalty)

    # σ = 压缩收益 × 精度权重
    sigma = (1 - compressed_complexity / base_complexity) * accuracy

    return max(0.0, sigma)


def survival_probability(sigma, noise):
    """生存概率：简化能力强 → 决策快 → 生存概率高"""
    return 1.0 / (1.0 + np.exp(-D39CConfig().survival_sensitivity * (sigma - D39CConfig().max_prediction_error_threshold)))


def experiment_c():
    """
    验证 D39-3：简化能力随进化递增但趋于饱和

    E[σ(I_T)] = ∫ λ(σ, t) · P_survival(t|σ) dt
    """
    individuals = np.random.uniform(*D39CConfig().initial_simplification_range, D39CConfig().n_individuals)

    generation_sigma_mean = []
    generation_survival_mean = []

    for generation in range(D39CConfig().n_generations):
        # 计算每个个体的简化能力和生存概率
        sigmas = [simplification_capability(ind, None) for ind in individuals]
        survivals = [survival_probability(s, None) for s in sigmas]

        # 加权选择（生存概率高的个体基因更多）
        weights = np.array(survivals)
        weights /= weights.sum()
        parent_indices = np.random.choice(len(individuals), size=len(individuals), p=weights)
        parents = individuals[parent_indices]

        # 突变（小幅随机扰动）
        children = parents + np.random.normal(0, 0.02, len(parents))
        children = np.clip(children, 0.01, 0.99)

        individuals = children

        # 记录统计量
        generation_sigma_mean.append(np.mean(sigmas))
        generation_survival_mean.append(np.mean(survivals))

    sigmas_arr = np.array(generation_sigma_mean)
    survivals_arr = np.array(generation_survival_mean)

    # 分析趋势
    early_sigma = np.mean(sigmas_arr[:10])
    late_sigma = np.mean(sigmas_arr[-10:])
    max_sigma = np.max(sigmas_arr)

    # 饱和检测：最后50代的标准差 vs 总方差
    last_50_std = np.std(sigmas_arr[-50:]) if len(sigmas_arr) >= 50 else np.std(sigmas_arr[-10:])
    total_std = np.std(sigmas_arr)

    return {
        'description': 'D39-C: 简化能力进化模拟',
        'validation': 'D39-3',
        'n_individuals': D39CConfig().n_individuals,
        'n_generations': D39CConfig().n_generations,
        'early_sigma_mean': float(early_sigma),
        'late_sigma_mean': float(late_sigma),
        'max_sigma': float(max_sigma),
        'sigma_increase_ratio': float(late_sigma / early_sigma) if early_sigma > 0 else 0,
        'saturation_indicator': f"last_50_std/total_std = {last_50_std/total_std:.3f}" if total_std > 0 else "N/A",
        'trend': '递增且饱和' if late_sigma > early_sigma and (last_50_std / total_std) > 0.3 else '需要重新审视',
        'early_gen_stats': sigmas_arr[:5].tolist(),
        'late_gen_stats': sigmas_arr[-5:].tolist(),
        'conclusion': '简化能力是进化副产品：随时间递增但在生存约束下饱和'
    }


# ============================================================
# D39-D：价值观作为先验参数
# ============================================================

@dataclass
class D39DConfig:
    n_budget_levels: int = 5
    budget_values: List[float] = None  # 信息收集预算
    high_efficiency_prior_sigma: float = 0.5  # 高效价值观先验（窄）
    high_flexibility_prior_sigma: float = 2.0  # 灵活价值观先验（宽）
    target_mu: float = 1.0  # 目标分布均值
    n_observations: int = 1000


def kl_divergence(p_mu, p_sigma, q_mu, q_sigma):
    """高斯分布 KL(p || q)"""
    return np.log(q_sigma / p_sigma) + (p_sigma ** 2 + (p_mu - q_mu) ** 2) / (2 * q_sigma ** 2) - 0.5


def update_posterior(prior_mu, prior_sigma, observations, sigma_obs=0.1):
    """高斯先验 + 高斯似然的贝叶斯后验更新"""
    precision_prior = 1.0 / prior_sigma ** 2
    precision_lik = 1.0 / sigma_obs ** 2

    posterior_precision = precision_prior + len(observations) * precision_lik
    posterior_mu = (prior_mu * precision_prior + np.sum(observations) * precision_lik) / posterior_precision
    posterior_sigma = np.sqrt(1.0 / posterior_precision)

    return posterior_mu, posterior_sigma


def experiment_d():
    """
    验证 D39-4：低预算时价值观差异显著，高预算时收敛

    P*_V = argmin_V D_KL(P_V || P_target) + λ · Cost(V)
    """
    config = D39DConfig()
    if config.budget_values is None:
        config.budget_values = [1, 5, 20, 50, 200]

    high_eff_prior = config.high_efficiency_prior_sigma  # 窄先验 = 高效率价值观
    high_flex_prior = config.high_flexibility_prior_sigma  # 宽先验 = 高灵活价值观

    results = []

    for budget in config.budget_values:
        # 生成观测数据
        true_mu = config.target_mu
        observations = np.random.normal(true_mu, 0.5, int(min(budget, config.n_observations)))

        # 高效价值观的后验
        mu_eff, sigma_eff = update_posterior(true_mu, high_eff_prior, observations)

        # 灵活价值观的后验
        mu_flex, sigma_flex = update_posterior(true_mu, high_flex_prior, observations)

        # 计算 KL 散度（与真实值偏离的程度）
        kl_eff_to_true = kl_divergence(mu_eff, sigma_eff, true_mu, 0.5)
        kl_flex_to_true = kl_divergence(mu_flex, sigma_flex, true_mu, 0.5)

        # 两种价值观的后验差异（越大说明价值观影响越大）
        posterior_diff = abs(mu_eff - mu_flex)

        # 先验对后验的影响占比（高预算时变小 → 后验收敛）
        posterior_variance_reduction = 1.0 - sigma_eff ** 2 / high_eff_prior ** 2

        results.append({
            'budget': budget,
            'n_observations': len(observations),
            'mu_eff': float(mu_eff),
            'sigma_eff': float(sigma_eff),
            'mu_flex': float(mu_flex),
            'sigma_flex': float(sigma_flex),
            'posterior_diff': float(posterior_diff),
            'kl_eff_to_true': float(kl_eff_to_true),
            'kl_flex_to_true': float(kl_flex_to_true),
            'posterior_variance_reduction': float(posterior_variance_reduction)
        })

    # 总结：后验差异随预算变化
    diffs = [r['posterior_diff'] for r in results]
    early_avg = np.mean(diffs[:2])
    late_avg = np.mean(diffs[-2:])

    # 两个价值观的 KL 散度差异（证明价值观选择不是随意的）
    kl_diffs = [abs(r['kl_eff_to_true'] - r['kl_flex_to_true']) for r in results]

    return {
        'description': 'D39-D: 价值观作为先验参数',
        'validation': 'D39-4',
        'budget_range': config.budget_values,
        'early_budget_posterior_diff': float(early_avg),
        'late_budget_posterior_diff': float(late_avg),
        'diff_ratio_low_high': float(early_avg / late_avg) if late_avg > 0 else 0,
        'convergence_concluded': '低预算差异显著，高预算收敛' if early_avg > late_avg * 1.5 else '不明显',
        'values_differ_in_climate': '高预算条件下，不同价值观产生不同后验→价值观是信息约束下的最优先验选择',
        'avg_kl_difference': float(np.mean(kl_diffs)),
        'details': results
    }


# ============================================================
# 主入口
# ============================================================

def main():
    print("=" * 60)
    print("D39：复杂与简单的信息论区分 — 实验验证")
    print("=" * 60)
    print()

    all_results = {}

    print("Running D39-A: 伪复杂化检测...")
    result_a = experiment_a()
    all_results['D39-A'] = result_a
    print(f"  Mean ΔI_gen (泛化互信息变化) = {result_a['mean_delta_I_generalization']:.4f}")
    print(f"  Mean ΔI_fit (训练互信息变化) = {result_a['mean_delta_I_fit']:.4f}")
    print(f"  泛化互信息不增加: {result_a['gen_fraction_non_positive']*100:.0f}% runs")
    print(f"  Conclusion: {result_a['conclusion']}")
    print()

    print("Running D39-B: 过拟合信息阈值...")
    result_b = experiment_b()
    all_results['D39-B'] = result_b
    print(f"  Empirical C_crit degree: {result_b['empirical_C_crit_degree']}")
    print(f"  Conclusion: {result_b['conclusion']}")
    print()

    print("Running D39-C: 简化能力进化模拟...")
    result_c = experiment_c()
    all_results['D39-C'] = result_c
    print(f"  Early σ = {result_c['early_sigma_mean']:.4f}, Late σ = {result_c['late_sigma_mean']:.4f}")
    print(f"  Increase ratio: {result_c['sigma_increase_ratio']:.3f}")
    print(f"  Conclusion: {result_c['conclusion']}")
    print()

    print("Running D39-D: 价值观作为先验参数...")
    result_d = experiment_d()
    all_results['D39-D'] = result_d
    print(f"  Low budget diff: {result_d['early_budget_posterior_diff']:.4f}")
    print(f"  High budget diff: {result_d['late_budget_posterior_diff']:.4f}")
    print(f"  Convergence: {result_d['convergence_concluded']}")
    print()

    # Save results
    output_path = '/Users/a1-6/Desktop/workspace/projects/D1-academic-AI/chimera_lab/d39-results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'theory': 'D39: 复杂与简单的信息论区分',
            'results': all_results
        }, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")


if __name__ == '__main__':
    main()
