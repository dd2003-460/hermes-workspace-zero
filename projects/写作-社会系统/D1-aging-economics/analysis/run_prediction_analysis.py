#!/usr/bin/env python3
"""
D1-aging-economics Phase 7 Task 7.1: 预测分析

基于基准回归模型，预测未来 5 年 (2024-2028) 老龄化对区域经济增长的影响。
使用三种情景模拟（低/中/高老龄化率），并对比随机森林预测。

运行: python3 run_prediction_analysis.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings('ignore')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def load_data():
    """加载面板数据"""
    data_path = os.path.join(PROJECT_ROOT, 'raw-data', 'synthetic_panel_2000_2023.csv')
    df = pd.read_csv(data_path, index_col=['province_code', 'year'])
    return df


def generate_scenarios(df):
    """生成低/中/高三条老龄化情景"""

    # Reset index to access province column
    df_reset = df.reset_index()
    provinces = df_reset['province'].unique()
    region_map = dict(zip(df_reset['province'], df_reset['region']))
    prov_code_map = dict(zip(df_reset['province'], df_reset['province_code']))
    years = list(range(2024, 2029))

    scenarios = {}
    sid = 0

    for prov in provinces:
        region = region_map.get(prov, 'East')
        # Base aging rate from last available year
        prov_data = df_reset[df_reset['province'] == prov]
        last_aging = prov_data['aging_rate'].iloc[-1] if len(prov_data) > 0 else 8.0

        for scenario_name, annual_change in [('low', 0.05), ('medium', 0.15), ('high', 0.30)]:
            sid += 1
            # Use unique numeric ID to avoid parsing issues (provinces contain spaces/underscores)
            key = f"S{sid:03d}_{scenario_name}"
            scenario_key = scenario_name  # Store actual scenario name
            rows = []
            prov_code = prov_code_map.get(prov, 0)
            for year in years:
                aging = last_aging + annual_change * (year - 2023)
                aging = max(aging, 2.0)
                rows.append({
                    'province_code': prov_code,
                    'province': prov,
                    'region': region,
                    'year': year,
                    'aging_rate': round(aging, 4),
                    'labor_ratio': max(55.0, 67.0 - 0.5 * (year - 2023)),
                    'savings_rate': max(10.0, 30.0 - 0.3 * (year - 2023)),
                    'urbanization': min(85.0, 48.0 + 1.2 * (year - 2023)),
                    'invest_rate': max(15.0, 32.0 - 0.5 * (year - 2023)),
                    'openness': min(2.0, 0.28 + 0.02 * (year - 2023)),
                })
            scenarios[key] = (pd.DataFrame(rows), prov, scenario_key)

    return scenarios


def train_baseline_model(df):
    """训练基准回归模型"""

    y_name = 'gdp_growth'
    x_vars = ['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']

    clean = df.dropna(subset=[y_name] + x_vars)
    y = clean[y_name]
    X = clean[x_vars]

    mod = PanelOLS(y, X, entity_effects=True, time_effects=True)
    est = mod.fit(cov_type='clustered', cluster_entity=True)

    return est, clean, y_name, x_vars


def predict_with_panel_model(estimator, scenarios, x_vars):
    """使用面板模型预测"""

    predictions = {}
    for key, (sdf, prov, scenario) in scenarios.items():
        try:
            # Set MultiIndex for PanelOLS.predict()
            sdf_indexed = sdf.set_index(['province_code', 'year'])
            y_pred = estimator.predict(sdf_indexed[x_vars])
            predictions[key] = {
                'scenario': scenario,
                'province': prov,
                'predictions': y_pred['predictions'].values,
                'params': estimator.params.to_dict(),
            }
        except Exception:
            continue

    return predictions


def train_random_forest(df, x_vars, y_name):
    """训练随机森林预测模型"""

    clean = df.dropna(subset=[y_name] + x_vars).copy()
    X = clean[x_vars]
    y = clean[y_name]

    # Time series cross-validation
    tscv = TimeSeriesSplit(n_splits=3)
    maes = []
    r2s = []

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)

        maes.append(mean_absolute_error(y_test, y_pred))
        r2s.append(r2_score(y_test, y_pred))

    rf.fit(X, y)  # Retrain on all data

    return rf, maes, r2s


def predict_with_rf(rf, scenarios, x_vars):
    """使用随机森林预测"""

    predictions = {}
    for key, (sdf, prov, scenario) in scenarios.items():
        try:
            y_pred = rf.predict(sdf[x_vars])
            predictions[key] = {
                'scenario': scenario,
                'province': prov,
                'predictions': y_pred,
            }
        except Exception:
            continue

    return predictions


def create_comparison_table(panel_pred, rf_pred, scenarios):
    """创建面板模型与随机森林对比表"""

    rows = []
    years = list(range(2024, 2029))

    for key in panel_pred:
        prov = panel_pred[key]['province']
        scenario = panel_pred[key]['scenario']

        if key not in rf_pred:
            continue

        panel_avg = np.mean(panel_pred[key]['predictions'])
        rf_avg = np.mean(rf_pred[key]['predictions'])
        diff = panel_avg - rf_avg

        rows.append({
            'Province': prov,
            'Scenario': scenario,
            'PanelMean': f"{panel_avg:.4f}",
            'RFMean': f"{rf_avg:.4f}",
            'Diff': f"{diff:.4f}",
        })

    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("PHASE 7.1: Prediction Analysis (2024-2028)")
    print("=" * 60)

    # Load data
    df = load_data()
    x_vars = ['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']
    y_name = 'gdp_growth'

    # Train baseline model
    print("\n--- Training Panel Fixed Effects Model ---")
    estimator, clean_data, _, _ = train_baseline_model(df)
    print(f"  Aging coefficient: {estimator.params['aging_rate']:.4f}")
    print(f"  R-squared: {estimator.rsquared:.4f}")
    print(f"  Sample: {len(clean_data)} obs")

    # Generate scenarios
    print("\n--- Generating Scenarios ---")
    scenarios = generate_scenarios(df)
    low_count = sum(1 for k, (v, _, s) in scenarios.items() if s == 'low')
    med_count = sum(1 for k, (v, _, s) in scenarios.items() if s == 'medium')
    high_count = sum(1 for k, (v, _, s) in scenarios.items() if s == 'high')
    print(f"  {low_count} provinces x 3 scenarios = {len(scenarios)} total")

    # Panel model predictions
    print("\n--- Panel Model Predictions ---")
    panel_preds = predict_with_panel_model(estimator, scenarios, x_vars)
    print(f"  {len(panel_preds)} predictions generated")

    # Random Forest predictions
    print("\n--- Training Random Forest ---")
    rf, maes, r2s = train_random_forest(df, x_vars, y_name)
    print(f"  MAE (cv): {np.mean(maes):.4f} (+/- {np.std(maes):.4f})")
    print(f"  R2 (cv): {np.mean(r2s):.4f} (+/- {np.std(r2s):.4f})")

    rf_preds = predict_with_rf(rf, scenarios, x_vars)
    print(f"  {len(rf_preds)} predictions generated")

    # Comparison
    print("\n" + "=" * 60)
    print("PREDICTION COMPARISON (Panel vs Random Forest)")
    print("=" * 60)

    # Show sample predictions for a few provinces
    sample_provs = ['Beijing', 'Gansu', 'Shanghai']
    for prov in sample_provs:
        print(f"\n--- {prov} ---")
        for key, pred in panel_preds.items():
            if pred['province'] != prov:
                continue
            scenario_name = pred['scenario']
            if key not in rf_preds:
                continue

            panel_avg = np.mean(pred['predictions'])
            rf_avg = np.mean(rf_preds[key]['predictions'])
            panel_trend = pred['predictions'][-1] - pred['predictions'][0]

            print(f"  [{scenario_name.upper()} aging]")
            print(f"    Panel model: mean={panel_avg:.4f}, trend={panel_trend:+.4f}")
            print(f"    RF model:    mean={rf_avg:.4f}")

    # Save comparison table
    comparison_df = create_comparison_table(panel_preds, rf_preds, scenarios)
    print(f"\n\nFull comparison table: {len(comparison_df)} rows")

    # Save results
    results_dir = os.path.join(PROJECT_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Save panel predictions
    panel_summary = []
    for key, pred in panel_preds.items():
        prov = pred['province']
        scenario = pred['scenario']
        pred_arr = pred['predictions']
        for i, year in enumerate(range(2024, 2029)):
            panel_summary.append({
                'province': prov,
                'scenario': scenario,
                'year': year,
                'predicted_gdp_growth': round(pred_arr[i], 4),
            })

    panel_df = pd.DataFrame(panel_summary)
    panel_df.to_csv(os.path.join(results_dir, 'panel_predictions_2024_2028.csv'), index=False)
    print(f"\nPanel predictions saved: {results_dir}/panel_predictions_2024_2028.csv")

    # Save RF predictions
    rf_summary = []
    for key, pred in rf_preds.items():
        prov = pred['province']
        scenario = pred['scenario']
        pred_arr = pred['predictions']
        for i, year in enumerate(range(2024, 2029)):
            rf_summary.append({
                'province': prov,
                'scenario': scenario,
                'year': year,
                'predicted_gdp_growth': round(pred_arr[i], 4),
            })

    rf_df = pd.DataFrame(rf_summary)
    rf_df.to_csv(os.path.join(results_dir, 'rf_predictions_2024_2028.csv'), index=False)
    print(f"RF predictions saved: {results_dir}/rf_predictions_2024_2028.csv")

    # Save comparison
    comparison_df.to_csv(os.path.join(results_dir, 'prediction_comparison.csv'), index=False)
    print(f"Comparison saved: {results_dir}/prediction_comparison.csv")

    # Scenario summary
    print("\n" + "=" * 60)
    print("SCENARIO SUMMARIES (average across all provinces)")
    print("=" * 60)

    for scenario_name in ['low', 'medium', 'high']:
        scenario_preds = [
            np.mean(panel_preds[k]['predictions'])
            for k in panel_preds if panel_preds[k]['scenario'] == scenario_name
        ]
        rf_preds_avg = [
            np.mean(rf_preds[k]['predictions'])
            for k in rf_preds if rf_preds[k]['scenario'] == scenario_name
        ]

        print(f"\n  [{scenario_name.upper()} aging]")
        print(f"    Panel model: mean={np.mean(scenario_preds):.4f}, std={np.std(scenario_preds):.4f}")
        print(f"    RF model:    mean={np.mean(rf_preds_avg):.4f}, std={np.std(rf_preds_avg):.4f}")

    print("\n" + "=" * 60)
    print("PHASE 7.1 PREDICTION ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
