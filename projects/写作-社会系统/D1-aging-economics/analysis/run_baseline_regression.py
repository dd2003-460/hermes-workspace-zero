#!/usr/bin/env python3
"""
D1-aging-economics Phase 3: 基准回归 + DID 分析

使用合成数据验证计量方法。真实数据获取后可直接替换数据源。

运行: python3 run_baseline_regression.py
"""

import os
import sys
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS, PooledOLS
from linearmodels.iv import IV2SLS

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def load_data():
    """加载合成面板数据"""
    data_path = os.path.join(PROJECT_ROOT, 'raw-data', 'synthetic_panel_2000_2023.csv')
    df = pd.read_csv(data_path, index_col=['province_code', 'year'])
    return df


def run_baseline_regression(df):
    """运行基准回归: GDP_growth ~ Aging + Controls"""

    print("=" * 60)
    print("PHASE 3: Baseline Regression")
    print("=" * 60)

    # Select variables
    y_name = 'gdp_growth'
    x_vars = ['aging_rate', 'labor_ratio', 'invest_rate', 'urbanization', 'openness']

    # Drop NaN
    df_clean = df.dropna(subset=[y_name] + x_vars).copy()

    print(f"\nSample: {df_clean.shape[0]} obs, {df_clean.index.get_level_values('province_code').unique().shape[0]} entities, "
          f"{df_clean.index.get_level_values('year').unique().shape[0]} time periods")

    # Model 1: Simple (aging only)
    print("\n--- Model 1: Aging only ---")
    y1 = df_clean['gdp_growth']
    x1 = df_clean[['aging_rate']]
    mod1 = PanelOLS(y1, x1, entity_effects=True, time_effects=True)
    est1 = mod1.fit(cov_type='clustered', cluster_entity=True)
    print(est1.summary)

    # Model 2: + Controls
    print("\n--- Model 2: + Controls ---")
    y2 = df_clean['gdp_growth']
    x2 = df_clean[x_vars]
    mod2 = PanelOLS(y2, x2, entity_effects=True, time_effects=True)
    est2 = mod2.fit(cov_type='clustered', cluster_entity=True)
    print(est2.summary)

    return est2


def run_did_analysis(df):
    """运行 DID 分析: LTC 试点效果"""

    print("\n" + "=" * 60)
    print("PHASE 4: DID Analysis (LTC Pilot)")
    print("=" * 60)

    # Create treatment variable
    df['ltc_post'] = df['ltc_pilot']

    # Filter to cities that are either treated or have non-zero treatment
    df_pilot = df[df['ltc_pilot'].isin([0, 1])]

    # Merge wave information
    df_pilot['wave'] = 0
    pilot_cities_1 = ['Shanghai', 'Chengdu', 'Qinhuangdao', 'Tai\'an', 'Hefei', 'Nantong']
    pilot_cities_2 = ['Guangzhou', 'Shenzhen', 'Qingdao', 'Jinan', 'Nanchang', 'Zhongshan']
    df_pilot.loc[df_pilot['province'].isin(pilot_cities_1), 'wave'] = 1
    df_pilot.loc[df_pilot['province'].isin(pilot_cities_2), 'wave'] = 2

    # DID specification
    # Y = α + β·Treat×Post + Controls + FE + ε
    df_pilot['treat_x_post'] = df_pilot['ltc_pilot'] * df_pilot['ltc_post']

    y_did = df_pilot['gdp_growth']
    x_did = df_pilot[['treat_x_post', 'aging_rate', 'labor_ratio', 'invest_rate', 'urbanization']]

    clean_did = pd.DataFrame({'gdp_growth': y_did, **x_did}).dropna()
    clean_did.index = df_pilot.dropna(subset=['gdp_growth']).index

    print(f"\nSample: {len(clean_did)} obs")
    print(f"Treated obs: {(df_pilot.dropna(subset=['gdp_growth'])['ltc_pilot'] == 1).sum()}")
    print(f"Treated×Post mean: {df_pilot.dropna(subset=['gdp_growth'])['treat_x_post'].mean():.4f}")

    # Run DID regression
    try:
        mod_did = PanelOLS(clean_did['gdp_growth'], clean_did[['treat_x_post', 'aging_rate', 'labor_ratio', 'invest_rate', 'urbanization']],
                           entity_effects=True, time_effects=True)
        est_did = mod_did.fit(cov_type='clustered', cluster_entity=True)
        print(est_did.summary)
    except Exception as e:
        print(f"DID regression error: {e}")
        print("Note: May need to remove collinear variables")


def run_mechanism_test(df):
    """机制分析: 储蓄率和劳动力供给"""

    print("\n" + "=" * 60)
    print("PHASE 5: Mechanism Analysis")
    print("=" * 60)

    df_clean = df.dropna(subset=['gdp_growth', 'aging_rate', 'savings_rate', 'labor_ratio']).copy()

    # Mechanism 1: Aging → Savings Rate → GDP Growth
    print("\n--- Mechanism 1: Savings Rate ---")
    savings_model = PanelOLS(df_clean['savings_rate'], df_clean[['aging_rate']],
                              entity_effects=True, time_effects=True)
    savings_est = savings_model.fit(cov_type='clustered', cluster_entity=True)
    print("Aging → Savings Rate:")
    print(savings_est.summary)

    # Mechanism 2: Aging → Labor Ratio → GDP Growth
    print("\n--- Mechanism 2: Labor Ratio ---")
    labor_model = PanelOLS(df_clean['labor_ratio'], df_clean[['aging_rate']],
                            entity_effects=True, time_effects=True)
    labor_est = labor_model.fit(cov_type='clustered', cluster_entity=True)
    print("Aging → Labor Ratio:")
    print(labor_est.summary)


def main():
    df = load_data()
    run_baseline_regression(df)
    run_did_analysis(df)
    run_mechanism_test(df)

    print("\n" + "=" * 60)
    print("ALL PHASE 3-5 CHECKS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
