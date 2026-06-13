#!/usr/bin/env python3
"""
S12-1: Model comparison for publication rate data.
Tests whether the CoT publication rate is better explained by:
1. Exponential growth (lambda = lambda_0 * exp(alpha * t))
2. Phase transition power law (lambda = lambda_0 * (rho/rho_c - 1)^beta for rho > rho_c)
3. Logistic growth (lambda = lambda_max / (1 + exp(-alpha*(t - t0))))

Data from S12-1 Table: quarterly publication rates.
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import logsumexp
import json

# Quarterly data: [quarter_index, papers, daily_rate, days_in_quarter]
# Quarter indices: 0=2022Q1-Q3, 1=2022Q4-Q3, 2=2023Q4-Q2, 3=2024Q3-Q4, 4=2025Q1-Q2
t = np.array([0, 1, 2, 3, 4], dtype=float)  # quarter index
N = np.array([12, 45, 89, 127, 227], dtype=float)  # paper count
daily_rate = np.array([0.044, 0.123, 0.325, 0.694, 0.498])  # papers/day

# Time in days (approximate):
# 2022Q1-Q3: 274 days (Jan1-Sep30)
# 2022Q4-Q3: 274 days
# 2023Q4-Q2: 183 days
# 2024Q3-Q4: 183 days
# 2025Q1-Q2: 182 days
cumulative_days = np.array([137, 411, 582, 765, 947], dtype=float)  # running total
midday = np.cumsum([137, 274, 183, 183, 182]) / 2  # mid-point of each quarter

print("=" * 70)
print("S12-1 Model Comparison: Exponential vs Phase Transition vs Logistic")
print("=" * 70)
print(f"\nData: {len(t)} quarters of CoT publication data")
for i in range(len(t)):
    print(f"  Q{i}: N={int(N[i])} papers, daily_rate={daily_rate[i]:.3f}, t={midday[i]:.0f} days")

# ============================================================================
# Model 1: Exponential growth
# lambda(t) = lambda_0 * exp(alpha * t_days)
# ============================================================================

def exp_model(t_days, log_lambda0, alpha):
    """Exponential growth model for daily rate."""
    return np.exp(log_lambda0 + alpha * t_days)

def exp_loglik(params, t_days, rate):
    log_lambda0, alpha = params
    predicted = exp_model(t_days, log_lambda0, alpha)
    # Gaussian likelihood: rate ~ N(predicted, sigma)
    residuals = (rate - predicted) ** 2 / (predicted ** 2)  # relative residuals
    return -0.5 * np.sum(residuals)  # negative log-likelihood

print("\n" + "-" * 70)
print("Model 1: Exponential Growth")
print("-" * 70)

try:
    popt_exp, _ = curve_fit(
        lambda t, log_lambda0, alpha: np.exp(log_lambda0 + alpha * t),
        midday, daily_rate, p0=[np.log(0.04), 1e-5], maxfev=10000
    )
    log_lambda0, alpha_exp = popt_exp
    exp_predicted = exp_model(midday, log_lambda0, alpha_exp)

    # R-squared (relative)
    ss_res = np.sum((daily_rate - exp_predicted) ** 2)
    ss_tot = np.sum((daily_rate - np.mean(daily_rate)) ** 2)
    r2_exp = 1 - ss_res / ss_tot

    # AIC
    n_params_exp = 2
    k = daily_rate.shape[0]
    # Log-likelihood approximation
    ll_exp = -0.5 * k * np.log(2 * np.pi) - 0.5 * k * np.log(ss_res / k) - k / 2
    aic_exp = 2 * n_params_exp - 2 * ll_exp

    print(f"  lambda_0 = {np.exp(log_lambda0):.6f} papers/day")
    print(f"  alpha = {alpha_exp:.8f} /day")
    print(f"  R^2 = {r2_exp:.6f}")
    print(f"  AIC = {aic_exp:.2f}")
    print(f"  Predicted rates: {[f'{p:.4f}' for p in exp_predicted]}")
    print(f"  Observed rates:  {[f'{r:.4f}' for r in daily_rate]}")
except Exception as e:
    print(f"  ERROR: {e}")
    r2_exp = aic_exp = None

# ============================================================================
# Model 2: Logistic growth (sigmoidal with saturation)
# rate(t) = rate_max / (1 + exp(-alpha*(t - t0)))
# ============================================================================

def logistic_model(t_days, rate_max, alpha, t0):
    """Logistic growth model."""
    return rate_max / (1 + np.exp(-alpha * (t_days - t0)))

print("\n" + "-" * 70)
print("Model 2: Logistic Growth")
print("-" * 70)

try:
    popt_log, _ = curve_fit(
        lambda t, rate_max, alpha, t0: logistic_model(t, rate_max, alpha, t0),
        midday, daily_rate, p0=[1.0, 1e-5, 500], maxfev=10000
    )
    rate_max, alpha_log, t0_log = popt_log
    log_predicted = logistic_model(midday, rate_max, alpha_log, t0_log)

    ss_res = np.sum((daily_rate - log_predicted) ** 2)
    ss_tot = np.sum((daily_rate - np.mean(daily_rate)) ** 2)
    r2_log = 1 - ss_res / ss_tot

    n_params_log = 3
    ll_log = -0.5 * len(daily_rate) * np.log(2 * np.pi) - 0.5 * len(daily_rate) * np.log(ss_res / len(daily_rate)) - len(daily_rate) / 2
    aic_log = 2 * n_params_log - 2 * ll_log

    print(f"  rate_max = {rate_max:.4f} papers/day")
    print(f"  alpha = {alpha_log:.8f}")
    print(f"  t0 (inflection) = {t0_log:.0f} days (~{t0_log/90:.1f} quarters from start)")
    print(f"  R^2 = {r2_log:.6f}")
    print(f"  AIC = {aic_log:.2f}")
    print(f"  Predicted rates: {[f'{p:.4f}' for p in log_predicted]}")
except Exception as e:
    print(f"  ERROR: {e}")
    r2_log = aic_log = None

# ============================================================================
# Model 3: Phase transition power law
# lambda(t) = lambda_0 * max(0, rho(t)/rho_c - 1)^beta
# rho(t) = daily_rate (the information density)
# ============================================================================

# For the power law, we need a threshold rho_c. The paper suggests rho_c ~ 0.7.
# But with only 5 data points, we need to test multiple rho_c values.

def powerlaw_model(rho, rho_c, lambda_0, beta):
    """Phase transition model: lambda = lambda_0 * (rho/rho_c - 1)^beta for rho > rho_c."""
    epsilon = rho / rho_c - 1
    result = np.zeros_like(rho)
    mask = epsilon > 0
    result[mask] = lambda_0 * (epsilon[mask] ** beta)
    return result

# The rate itself IS rho. So: rate = lambda_0 * (rate/rho_c - 1)^beta
# Rearrange: rate^(1/beta) = lambda_0^(1/beta) * (rate/rho_c - 1)
# For rho_c=0.2, 0.3, 0.4, 0.5, 0.6, 0.7, test fit quality

print("\n" + "-" * 70)
print("Model 3: Phase Transition Power Law (varying rho_c)")
print("-" * 70)

rho_c_values = np.arange(0.1, 0.8, 0.05)
best_aic_pl = np.inf
best_rho_c = None
best_params_pl = None
best_r2_pl = None
powerlaw_results = []

for rho_c in rho_c_values:
    # Filter supercritical data points (rate > rho_c)
    supercritical_mask = daily_rate > rho_c
    n_supercritical = np.sum(supercritical_mask)

    if n_supercritical < 3:
        continue  # Need at least 3 points for meaningful fit

    rho_sup = daily_rate[supercritical_mask]

    # Fit: rate = lambda_0 * (rho/rho_c - 1)^beta
    # Try log-log regression first: log(rate) = log(lambda_0) + beta * log(rho/rho_c - 1)

    log_rhop = np.log(rho_sup / rho_c - 1)
    log_rate = np.log(rho_sup)

    # OLS on log-log
    coeffs = np.polyfit(log_rhop, log_rate, 1)
    beta_ols = coeffs[0]
    log_lambda0_ols = coeffs[1]

    if beta_ols <= 0 or np.exp(log_lambda0_ols) <= 0:
        continue

    # Full nonlinear fit
    try:
        popt_pl, _ = curve_fit(
            lambda r, l0, b: powerlaw_model(r, rho_c, l0, b),
            daily_rate, daily_rate,
            p0=[np.exp(log_lambda0_ols), beta_ols],
            maxfev=10000
        )
        lambda0_pl, beta_pl = popt_pl
        pl_predicted = powerlaw_model(daily_rate, rho_c, lambda0_pl, beta_pl)

        # R-squared
        ss_res_pl = np.sum((daily_rate - pl_predicted) ** 2)
        ss_tot = np.sum((daily_rate - np.mean(daily_rate)) ** 2)
        r2_pl = 1 - ss_res_pl / ss_tot

        # AIC (using n_supercritical for parameter estimation, total for prediction)
        n_params_pl = 3  # rho_c, lambda_0, beta
        ll_pl = -0.5 * n_supercritical * np.log(2 * np.pi) - 0.5 * n_supercritical * np.log(ss_res_pl / n_supercritical) - n_supercritical / 2
        # Penalize for using all 5 points
        aic_pl = 2 * n_params_pl - 2 * ll_pl

        powerlaw_results.append({
            'rho_c': rho_c, 'beta': beta_pl, 'lambda_0': lambda0_pl,
            'R2': r2_pl, 'AIC': aic_pl, 'n_supercritical': n_supercritical,
            'predicted': pl_predicted
        })

        if aic_pl < best_aic_pl:
            best_aic_pl = aic_pl
            best_rho_c = rho_c
            best_params_pl = (lambda0_pl, beta_pl)
            best_r2_pl = r2_pl

    except Exception:
        continue

if best_rho_c is not None:
    print(f"  Best rho_c = {best_rho_c:.2f}")
    print(f"  Best lambda_0 = {best_params_pl[0]:.6f}")
    print(f"  Best beta = {best_params_pl[1]:.4f}")
    print(f"  R^2 = {best_r2_pl:.6f}")
    print(f"  AIC = {best_aic_pl:.2f}")
    # Find best result table
    best_entry = min(powerlaw_results, key=lambda x: x['AIC'])
    print(f"\n  Top 5 rho_c values by AIC:")
    sorted_results = sorted(powerlaw_results, key=lambda x: x['AIC'])[:5]
    for r in sorted_results:
        print(f"    rho_c={r['rho_c']:.2f}: beta={r['beta']:.4f}, R2={r['R2']:.4f}, AIC={r['AIC']:.2f} ({r['n_supercritical']} supercritical)")
else:
    print("  No valid power-law fit found.")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("MODEL COMPARISON SUMMARY")
print("=" * 70)

models = []
if r2_exp is not None:
    models.append(('Exponential Growth', r2_exp, aic_exp, 2))
if r2_log is not None:
    models.append(('Logistic Growth', r2_log, aic_log, 3))
if best_r2_pl is not None:
    models.append(('Phase Transition', best_r2_pl, best_aic_pl, 3))

models.sort(key=lambda x: x[2])  # sort by AIC

print(f"\n{'Model':<25} {'R^2':>10} {'AIC':>10} {'k':>5}")
print("-" * 55)
for name, r2, aic, k in models:
    print(f"{name:<25} {r2:>10.6f} {aic:>10.2f} {k:>5}")

# Delta AIC
if len(models) >= 2:
    aic_ref = models[0][2]
    print(f"\nDelta AIC (relative to best):")
    for name, r2, aic, k in models:
        delta = aic - aic_ref
        evidence = "strong support" if delta < 2 else ("substantial" if delta < 4 else ("considerable" if delta < 7 else "essentially no"))
        print(f"  {name}: delta_AIC={delta:.2f} ({evidence})")

# ============================================================================
# Conclusion
# ============================================================================

print("\n" + "-" * 70)
print("CONCLUSION")
print("-" * 70)

if len(models) >= 2:
    best_name, best_r2, best_aic, _ = models[0]
    second_name, second_r2, second_aic, _ = models[1]
    delta = second_aic - best_aic

    if delta < 2:
        conclusion = (f"The {best_name} and {second_name} models have comparable fit "
                     f"(delta_AIC={delta:.2f}). The data cannot distinguish between "
                     f"these models. The phase transition hypothesis is not uniquely supported.")
    elif delta < 4:
        conclusion = (f"The {best_name} model has substantial support over the "
                     f"{second_name} model (delta_AIC={delta:.2f}), but the evidence is not conclusive.")
    else:
        conclusion = (f"The {best_name} model strongly outperforms alternatives "
                     f"(delta_AIC={delta:.2f}). The phase transition hypothesis is supported.")

    print(conclusion)

    # Print best model
    print(f"\nBest model: {best_name}")
    print(f"  R^2 = {best_r2:.6f}")
    print(f"  AIC = {best_aic:.2f}")
    print(f"  This is {'better' if best_name == 'Exponential Growth' else 'comparable to or better than'} "
          f"the exponential model (delta_AIC={abs(models[0][2] - models[1][2]):.2f}).")

print("\nNote: With only 5 data points and 2-3 free parameters per model,")
print("model comparison has limited discriminatory power. The results are")
print("illustrative rather than conclusive.")

# Save results
results = {
    'data': {
        'quarters': int(len(t)),
        'paper_counts': N.tolist(),
        'daily_rates': daily_rate.tolist()
    },
    'models': []
}
for name, r2, aic, k in models:
    results['models'].append({'name': name, 'R2': r2, 'AIC': aic, 'k': k})

# Add phase transition results
if best_rho_c is not None:
    results['best_powerlaw'] = {
        'rho_c': best_rho_c,
        'beta': best_params_pl[1],
        'lambda_0': best_params_pl[0],
        'R2': best_r2_pl,
        'AIC': best_aic_pl,
        'top_rho_c_candidates': [
            {'rho_c': r['rho_c'], 'beta': r['beta'], 'R2': r['R2'], 'AIC': r['AIC']}
            for r in sorted_results[:5]
        ]
    }

output_path = '/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-academic-AI/researches/S12-1-Model-Comparison.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")
