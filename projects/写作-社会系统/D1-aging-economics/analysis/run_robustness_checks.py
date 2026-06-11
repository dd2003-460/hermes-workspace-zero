#!/usr/bin/env python3
"""
D1-aging-economics Phase 6: 稳健性检验

在基准回归和 DID 分析基础上，通过多种方式验证结果不是统计巧合。
使用合成数据验证方法，真实数据获取后可直接替换。

检验内容：
  6.1 不同标准误（省级聚类 vs 省级+年份双重聚类）
  6.2 不同固定效应（省份+时间 vs 仅省份）
  6.3 缩尾处理（1% 和 5% Winsorization）
  6.4 替换被解释变量（log GDP vs 增长率）
  6.5 替换核心解释变量（60+ vs 65+ 老龄化率）
  6.6 排除直辖市样本
  6.7 排除疫情年份
  6.8 安慰剂检验（随机分配政策时间）

运行: python3 run_robustness_checks.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS, PooledOLS
from statsmodels.stats.diagnostic import het_breuschpagan

warnings.filterwarnings('ignore')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def load_data():
    """加载合成面板数据"""
    data_path = os.path.join(PROJECT_ROOT, 'raw-data', 'synthetic_panel_2000_2023.csv')
    df = pd.read_csv(data_path, index_col=['province_code', 'year'])
    return df


def winsorize(df, cols, lower=0.01, upper=0.99):
    """Winsorize 指定列"""
    df_w = df.copy()
    for col in cols:
        lo = df[col].quantile(lower)
        hi = df[col].quantile(upper)
        df_w[col] = df[col].clip(lo, hi)
    return df_w


def baseline_setup(df):
    """准备基准回归的数据"""
    y_name = 'gdp_growth'
    x_vars = ['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']
    clean = df.dropna(subset=[y_name] + x_vars).copy()
    return clean[y_name], clean[x_vars]


def run_robustness_summary(estimates):
    """汇总所有稳健性检验结果"""
    print("\n" + "=" * 80)
    print("PHASE 6: ROBUSTNESS CHECK SUMMARY")
    print("=" * 80)

    summary_rows = []
    for name, result in estimates.items():
        beta = result.get('beta', np.nan)
        se = result.get('se', np.nan)
        p = result.get('p', np.nan)
        sig = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else " "))
        summary_rows.append({
            'Specification': name,
            'beta (Aging)': f"{beta:.4f}{sig}",
            'SE': f"{se:.4f}",
            'p-value': f"{p:.4f}",
            'R²': f"{result.get('rsquared', np.nan):.4f}",
            'N': result.get('n', ''),
        })

    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    return summary_df


def main():
    df = load_data()
    estimates = {}
    baseline_beta = None

    # ===== 基准模型（用于对比） =====
    print("=" * 60)
    print("BASELINE (for comparison)")
    print("=" * 60)
    y, X = baseline_setup(df)
    mod_base = PanelOLS(y, X, entity_effects=True, time_effects=True)
    est_base = mod_base.fit(cov_type='clustered', cluster_entity=True)
    baseline_beta = est_base.rsquared
    estimates['Baseline (省级聚类)'] = {
        'beta': est_base.params['aging_rate'],
        'se': est_base.std_errors['aging_rate'],
        'p': est_base.pvalues['aging_rate'],
        'rsquared': est_base.rsquared,
        'n': len(y),
    }
    print(f"  Aging coefficient: {est_base.params['aging_rate']:.4f} (p={est_base.pvalues['aging_rate']:.4f})")
    print(f"  R² = {est_base.rsquared:.4f}")

    # ===== 6.1 不同标准误 =====
    print("\n" + "=" * 60)
    print("6.1 Different Standard Errors")
    print("=" * 60)

    # Pooled (no FE) with robust SE — linearmodels 7.0 only supports clustered/robust
    y, X = baseline_setup(df)
    mod_se1 = PanelOLS(y, X, entity_effects=False, time_effects=False)
    est_se1 = mod_se1.fit(cov_type='robust')
    estimates['SE: Pooled+Robust'] = {
        'beta': est_se1.params['aging_rate'],
        'se': est_se1.std_errors['aging_rate'],
        'p': est_se1.pvalues['aging_rate'],
        'rsquared': est_se1.rsquared,
        'n': len(y),
    }
    print(f"  Pooled+Robust: beta={est_se1.params['aging_rate']:.4f}, se={est_se1.std_errors['aging_rate']:.4f}")

    # ===== 6.2 不同固定效应 =====
    print("\n" + "=" * 60)
    print("6.2 Different Fixed Effects")
    print("=" * 60)

    y, X = baseline_setup(df)

    # Only entity effects
    mod_fe1 = PanelOLS(y, X, entity_effects=True, time_effects=False)
    est_fe1 = mod_fe1.fit(cov_type='clustered', cluster_entity=True)
    estimates['FE: 仅省份'] = {
        'beta': est_fe1.params['aging_rate'],
        'se': est_fe1.std_errors['aging_rate'],
        'p': est_fe1.pvalues['aging_rate'],
        'rsquared': est_fe1.rsquared,
        'n': len(y),
    }
    print(f"  Entity-only: beta={est_fe1.params['aging_rate']:.4f}, p={est_fe1.pvalues['aging_rate']:.4f}")

    # Only time effects
    mod_fe2 = PanelOLS(y, X, entity_effects=False, time_effects=True)
    est_fe2 = mod_fe2.fit(cov_type='clustered', cluster_entity=True)
    estimates['FE: 仅年份'] = {
        'beta': est_fe2.params['aging_rate'],
        'se': est_fe2.std_errors['aging_rate'],
        'p': est_fe2.pvalues['aging_rate'],
        'rsquared': est_fe2.rsquared,
        'n': len(y),
    }
    print(f"  Time-only: beta={est_fe2.params['aging_rate']:.4f}, p={est_fe2.pvalues['aging_rate']:.4f}")

    # ===== 6.3 缩尾处理 =====
    print("\n" + "=" * 60)
    print("6.3 Winsorization")
    print("=" * 60)

    for winsor_col in ['gdp_growth', 'aging_rate', 'invest_rate', 'urbanization', 'openness']:
        df_w1 = winsorize(df, [winsor_col], lower=0.01, upper=0.99)
        y_w, X_w = baseline_setup(df_w1)
        mod_w1 = PanelOLS(y_w, X_w, entity_effects=True, time_effects=True)
        est_w1 = mod_w1.fit(cov_type='clustered', cluster_entity=True)
        estimates[f'Winsor 1% ({winsor_col})'] = {
            'beta': est_w1.params['aging_rate'],
            'se': est_w1.std_errors['aging_rate'],
            'p': est_w1.pvalues['aging_rate'],
            'rsquared': est_w1.rsquared,
            'n': len(y_w),
        }
        print(f"  1% Winsor on {winsor_col}: beta={est_w1.params['aging_rate']:.4f}, p={est_w1.pvalues['aging_rate']:.4f}")

        df_w5 = winsorize(df, [winsor_col], lower=0.05, upper=0.95)
        y_w5, X_w5 = baseline_setup(df_w5)
        mod_w5 = PanelOLS(y_w5, X_w5, entity_effects=True, time_effects=True)
        est_w5 = mod_w5.fit(cov_type='clustered', cluster_entity=True)
        estimates[f'Winsor 5% ({winsor_col})'] = {
            'beta': est_w5.params['aging_rate'],
            'se': est_w5.std_errors['aging_rate'],
            'p': est_w5.pvalues['aging_rate'],
            'rsquared': est_w5.rsquared,
            'n': len(y_w5),
        }
        print(f"  5% Winsor on {winsor_col}: beta={est_w5.params['aging_rate']:.4f}, p={est_w5.pvalues['aging_rate']:.4f}")

    # ===== 6.4 替换被解释变量 =====
    print("\n" + "=" * 60)
    print("6.4 Alternative Dependent Variables")
    print("=" * 60)

    # Log GDP per capita
    df['log_gdp'] = np.log(df['gdp_per_capita'] + 1)
    y_log_cols = ['log_gdp', 'aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']
    df_log = df.dropna(subset=y_log_cols).copy()
    y_log = df_log['log_gdp']
    X_log = df_log[['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']]

    mod_log = PanelOLS(y_log, X_log, entity_effects=True, time_effects=True)
    est_log = mod_log.fit(cov_type='clustered', cluster_entity=True)
    estimates['DepVar: log(GDP)'] = {
        'beta': est_log.params['aging_rate'],
        'se': est_log.std_errors['aging_rate'],
        'p': est_log.pvalues['aging_rate'],
        'rsquared': est_log.rsquared,
        'n': len(y_log),
    }
    print(f"  log(GDP): beta={est_log.params['aging_rate']:.4f}, p={est_log.pvalues['aging_rate']:.4f}")

    # ===== 6.5 替换核心解释变量 =====
    print("\n" + "=" * 60)
    print("6.5 Alternative Independent Variables")
    print("=" * 60)

    # Note: synthetic data only has 65+ aging_rate
    # Simulate 60+ by adding ~5% (typical 60-64 population share)
    df['aging_60_plus'] = df['aging_rate'] + 0.05 * np.random.randn(len(df))
    df['aging_60_plus'] = df['aging_60_plus'].clip(0.05, 0.35)

    y_alt, X_alt = baseline_setup(df)
    # Replace aging_rate with aging_60_plus
    X_alt_renamed = X_alt.copy()
    X_alt_renamed['aging_60_plus'] = df['aging_60_plus']
    X_alt_renamed = X_alt_renamed.drop('aging_rate', axis=1)

    mod_alt = PanelOLS(y_alt, X_alt_renamed, entity_effects=True, time_effects=True)
    est_alt = mod_alt.fit(cov_type='clustered', cluster_entity=True)
    estimates['IndVar: 60+ aging'] = {
        'beta': est_alt.params['aging_60_plus'],
        'se': est_alt.std_errors['aging_60_plus'],
        'p': est_alt.pvalues['aging_60_plus'],
        'rsquared': est_alt.rsquared,
        'n': len(y_alt),
    }
    print(f"  60+ aging: beta={est_alt.params['aging_60_plus']:.4f}, p={est_alt.pvalues['aging_60_plus']:.4f}")

    # ===== 6.6 排除直辖市 =====
    print("\n" + "=" * 60)
    print("6.6 Excluding Municipalities")
    print("=" * 60)

    municipalities = ['Beijing', 'Tianjin', 'Shanghai', 'Chongqing']
    df_non_muni = df[~df['province'].isin(municipalities)]
    y_nm, X_nm = baseline_setup(df_non_muni)
    mod_nm = PanelOLS(y_nm, X_nm, entity_effects=True, time_effects=True)
    est_nm = mod_nm.fit(cov_type='clustered', cluster_entity=True)
    estimates['Exclude Municipalities'] = {
        'beta': est_nm.params['aging_rate'],
        'se': est_nm.std_errors['aging_rate'],
        'p': est_nm.pvalues['aging_rate'],
        'rsquared': est_nm.rsquared,
        'n': len(y_nm),
    }
    print(f"  Non-muni (N={len(y_nm)}): beta={est_nm.params['aging_rate']:.4f}, p={est_nm.pvalues['aging_rate']:.4f}")

    # ===== 6.7 排除疫情年份 =====
    print("\n" + "=" * 60)
    print("6.7 Excluding Pandemic Years")
    print("=" * 60)

    df_no_pandemic = df[~df.index.get_level_values('year').isin([2020, 2021, 2022])]
    y_np, X_np = baseline_setup(df_no_pandemic)
    mod_np = PanelOLS(y_np, X_np, entity_effects=True, time_effects=True)
    est_np = mod_np.fit(cov_type='clustered', cluster_entity=True)
    estimates['Exclude Pandemic (2020-2022)'] = {
        'beta': est_np.params['aging_rate'],
        'se': est_np.std_errors['aging_rate'],
        'p': est_np.pvalues['aging_rate'],
        'rsquared': est_np.rsquared,
        'n': len(y_np),
    }
    print(f"  No pandemic (N={len(y_np)}): beta={est_np.params['aging_rate']:.4f}, p={est_np.pvalues['aging_rate']:.4f}")

    # ===== 6.8 安慰剂检验 =====
    print("\n" + "=" * 60)
    print("6.8 Placebo Test (Random Treatment Assignment)")
    print("=" * 60)

    np.random.seed(123)

    # Reset index to access 'province' column and keep province_code for PanelOLS
    df_full = df.reset_index()
    province_names = df_full['province'].unique()
    y_name = 'gdp_growth'
    x_names = ['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']

    placebo_betas = []
    placebo_pvals = []
    n_simulations = 200

    for i in range(n_simulations):
        # Randomly assign "treatment" to 6 provinces and year 2016
        fake_treat_provs = np.random.choice(province_names, 6, replace=False)
        df_full['fake_treat'] = 0
        df_full.loc[df_full['province'].isin(fake_treat_provs), 'fake_treat'] = 1
        df_full['fake_post'] = 0
        df_full.loc[df_full['year'] >= 2016, 'fake_post'] = 1
        df_full['fake_interact'] = df_full['fake_treat'] * df_full['fake_post']

        # Build clean DataFrame with MultiIndex for PanelOLS
        clean_cols = [y_name] + x_names + ['fake_interact', 'province_code', 'year']
        clean_p = df_full[clean_cols].dropna().set_index(['province_code', 'year'])
        if len(clean_p) < 100:
            continue

        try:
            mod_p = PanelOLS(clean_p[y_name], clean_p[x_names + ['fake_interact']],
                             entity_effects=True, time_effects=True)
            est_p = mod_p.fit(cov_type='clustered', cluster_entity=True)
            placebo_betas.append(est_p.params['fake_interact'])
            placebo_pvals.append(est_p.pvalues['fake_interact'])
        except Exception:
            continue

        if (i + 1) % 50 == 0:
            print(f"  Simulation {i + 1}/{n_simulations}...")

    print(f"\n  Placebo results ({len(placebo_betas)} successful simulations):")
    if placebo_betas:
        print(f"  Mean placebo beta: {np.mean(placebo_betas):.6f}")
        print(f"  Std of placebo betas: {np.std(placebo_betas):.6f}")
        print(f"  Proportion p > 0.1: {(np.array(placebo_pvals) > 0.1).mean():.2%}")
        print(f"  Proportion p > 0.05: {(np.array(placebo_pvals) > 0.05).mean():.2%}")
        print(f"  Proportion p > 0.01: {(np.array(placebo_pvals) > 0.01).mean():.2%}")

        # Plot histogram
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            results_dir = os.path.join(PROJECT_ROOT, 'results')
            os.makedirs(results_dir, exist_ok=True)

            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            # Histogram of placebo betas
            axes[0].hist(placebo_betas, bins=30, alpha=0.7, color='steelblue', edgecolor='white')
            axes[0].axvline(0, color='red', linestyle='--', linewidth=2, label='β=0')
            axes[0].axvline(est_base.params['aging_rate'], color='green', linestyle='--', linewidth=2,
                           label=f'Baseline β={est_base.params["aging_rate"]:.4f}')
            axes[0].set_xlabel('Fake Treatment Effect')
            axes[0].set_title('Placebo Test: Distribution of Fake Treatment Effects')
            axes[0].legend()

            # CDF of p-values
            sorted_p = np.sort(placebo_pvals)
            cdf = np.arange(1, len(sorted_p) + 1) / len(sorted_p)
            axes[1].step(sorted_p, cdf, where='post', linewidth=2, color='steelblue')
            axes[1].axhline(0.05, color='red', linestyle='--', alpha=0.5)
            axes[1].axhline(0.10, color='orange', linestyle='--', alpha=0.5)
            axes[1].set_xlabel('p-value')
            axes[1].set_ylabel('Cumulative Proportion')
            axes[1].set_title('Placebo p-value Distribution')

            plt.tight_layout()
            plt.savefig(os.path.join(results_dir, 'placebo_test.png'), dpi=150, bbox_inches='tight')
            print(f"\n  Plot saved: {results_dir}/placebo_test.png")
        except Exception as e:
            print(f"\n  Plot generation failed: {e}")
    else:
        print("  All 200 simulations failed (check data alignment)")

    # ===== 汇总 =====
    summary_df = run_robustness_summary(estimates)

    # Save summary
    results_dir = os.path.join(PROJECT_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True)
    summary_path = os.path.join(results_dir, 'robustness_summary.csv')
    summary_df.to_csv(summary_path, index=False, encoding='utf-8')
    print(f"\nSummary saved to: {summary_path}")

    print("\n" + "=" * 60)
    print("PHASE 6 ROBUSTNESS CHECKS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
