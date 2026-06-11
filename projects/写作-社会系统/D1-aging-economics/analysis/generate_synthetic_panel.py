#!/usr/bin/env python3
"""
D1-aging-economics Phase 2: 合成面板数据生成

生成分省面板数据 (2000-2023)，用于验证计量方法。
真实数据获取后替换此文件的数据源。

运行: python3 generate_synthetic_panel.py

输出: raw-data/synthetic_panel_2000_2023.csv
"""

import numpy as np
import pandas as pd
import os

def generate_province_data():
    """生成中国 31 省份 2000-2023 年面板数据"""

    np.random.seed(42)

    provinces = [
        'Beijing', 'Tianjin', 'Hebei', 'Shanxi', 'Inner Mongolia',
        'Liaoning', 'Jilin', 'Heilongjiang', 'Shanghai', 'Jiangsu',
        'Zhejiang', 'Anhui', 'Fujian', 'Jiangxi', 'Shandong',
        'Henan', 'Hubei', 'Hunan', 'Guangdong', 'Guangxi',
        'Hainan', 'Chongqing', 'Sichuan', 'Guizhou', 'Yunnan',
        'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang'
    ]

    province_codes = [11, 12, 13, 14, 15, 21, 22, 23, 31, 32,
                      33, 34, 35, 36, 37, 41, 42, 43, 44, 45,
                      46, 50, 51, 52, 53, 54, 61, 62, 63, 64, 65]

    years = list(range(2000, 2024))

    # Region classification (per National Bureau of Statistics)
    regions = {
        'East': ['Beijing', 'Tianjin', 'Hebei', 'Liaoning', 'Shanghai', 'Jiangsu',
                 'Zhejiang', 'Fujian', 'Shandong', 'Guangdong'],
        'Central': ['Shanxi', 'Heilongjiang', 'Anhui', 'Jiangxi', 'Henan',
                    'Hubei', 'Hunan', 'Guangxi', 'Hainan'],
        'West': ['Inner Mongolia', 'Chongqing', 'Sichuan', 'Guizhou', 'Yunnan',
                 'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang']
    }

    rows = []

    for prov_idx, prov in enumerate(provinces):
        region = 'East' if prov in regions['East'] else ('Central' if prov in regions['Central'] else 'West')

        # Base characteristics vary by region
        if region == 'East':
            base_gdp = np.random.lognormal(10.5, 0.3)  # ~400B base GDP
            base_urban = np.random.uniform(0.45, 0.65)
            base_edu = np.random.uniform(8000, 15000)
            aging_baseline = np.random.uniform(0.06, 0.10)
        elif region == 'Central':
            base_gdp = np.random.lognormal(10.0, 0.3)  # ~180B base GDP
            base_urban = np.random.uniform(0.30, 0.45)
            base_edu = np.random.uniform(5000, 9000)
            aging_baseline = np.random.uniform(0.05, 0.09)
        else:
            base_gdp = np.random.lognormal(9.5, 0.4)  # ~80B base GDP
            base_urban = np.random.uniform(0.25, 0.40)
            base_edu = np.random.uniform(3000, 7000)
            aging_baseline = np.random.uniform(0.04, 0.08)

        for t_idx, year in enumerate(years):
            time_factor = 1.0 + 0.06 * (year - 2000)  # ~6% annual growth trend
            time_shock = np.random.randn() * 0.02

            # === Core Variables ===

            # Aging rate: slowly increasing (aging population trend)
            aging_rate = aging_baseline + 0.0015 * (year - 2000) + np.random.randn() * 0.003
            aging_rate = max(0.02, min(0.25, aging_rate))

            # 15-64 population ratio: slowly decreasing
            labor_ratio = 0.72 - 0.002 * (year - 2000) + np.random.randn() * 0.005
            labor_ratio = max(0.55, min(0.82, labor_ratio))

            # GDP per capita (constant 2000 yuan)
            gdp_per_capita = base_gdp / (1 + aging_rate) * time_factor * (1 + time_shock)
            gdp_growth = time_factor - 1 + time_shock + np.random.randn() * 0.01

            # === Mechanism Variables ===

            # Savings rate: declining with aging (life-cycle hypothesis)
            savings_rate = 0.35 - 0.5 * aging_rate + np.random.randn() * 0.02
            savings_rate = max(0.10, min(0.50, savings_rate))

            # Urbanization: increasing over time
            urbanization = base_urban + 0.012 * (year - 2000) + np.random.randn() * 0.005
            urbanization = max(0.15, min(0.85, urbanization))

            # === Control Variables ===

            # Investment rate: negatively correlated with aging
            invest_rate = 0.40 - 0.8 * aging_rate + np.random.randn() * 0.03
            invest_rate = max(0.15, min(0.65, invest_rate))

            # Education per student (constant yuan)
            education = base_edu * (1 + 0.05 * (year - 2000)) + np.random.randn() * 500

            # Openness: trade-to-GDP ratio
            openness = np.random.uniform(0.05, 0.60) * (1 + 0.02 * (year - 2000))
            openness = min(openness, 2.0)

            # Consumption structure (service consumption share)
            consumption_structure = 0.30 + 0.5 * urbanization + 0.01 * (year - 2000)
            consumption_structure = max(0.15, min(0.70, consumption_structure))

            rows.append({
                'province_code': province_codes[prov_idx],
                'province': prov,
                'region': region,
                'year': year,
                'gdp_per_capita': gdp_per_capita,
                'gdp_growth': gdp_growth,
                'aging_rate': aging_rate,
                'labor_ratio': labor_ratio,
                'savings_rate': savings_rate,
                'urbanization': urbanization,
                'invest_rate': invest_rate,
                'education': education,
                'openness': openness,
                'consumption_structure': consumption_structure,
            })

    df = pd.DataFrame(rows)
    df['gdp_growth'] = (df['gdp_growth'] * 100).round(4)  # Convert to percentage
    df['aging_rate'] = (df['aging_rate'] * 100).round(4)  # Convert to percentage
    df['savings_rate'] = (df['savings_rate'] * 100).round(4)  # Convert to percentage
    df['labor_ratio'] = (df['labor_ratio'] * 100).round(4)
    df['urbanization'] = (df['urbanization'] * 100).round(4)

    return df


def generate_ltc_pilot_data():
    """生成 LTC 试点政策变量"""

    # Two waves of pilot cities
    wave_1_2016 = ["Shanghai", "Chengdu", "Qinhuangdao", "Tai'an", "Hefei", "Nantong"]
    wave_2_2020 = ["Guangzhou", "Shenzhen", "Qingdao", "Jinan", "Nanchang", "Zhongshan"]

    cities = wave_1_2016 + wave_2_2020
    all_provinces = [
        'Beijing', 'Tianjin', 'Hebei', 'Shanxi', 'Inner Mongolia',
        'Liaoning', 'Jilin', 'Heilongjiang', 'Shanghai', 'Jiangsu',
        'Zhejiang', 'Anhui', 'Fujian', 'Jiangxi', 'Shandong',
        'Henan', 'Hubei', 'Hunan', 'Guangdong', 'Guangxi',
        'Hainan', 'Chongqing', 'Sichuan', 'Guizhou', 'Yunnan',
        'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang'
    ]
    years = list(range(2000, 2024))

    rows = []
    for prov in all_provinces:
        for year in years:
            treat = 0
            if prov in wave_1_2016 and year >= 2016:
                treat = 1
            elif prov in wave_2_2020 and year >= 2020:
                treat = 1
            rows.append({
                'province': prov,
                'year': year,
                'ltc_pilot': treat,
            })

    return pd.DataFrame(rows)


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw-data')
    os.makedirs(output_dir, exist_ok=True)

    print("Generating synthetic provincial panel data (2000-2023)...")

    panel_df = generate_province_data()
    ltc_df = generate_ltc_pilot_data()

    # Merge
    merged = panel_df.merge(ltc_df, on=['province', 'year'], how='left')
    merged['ltc_pilot'] = merged['ltc_pilot'].fillna(0).astype(int)

    # Set MultiIndex
    merged = merged.set_index(['province_code', 'year'])

    # Save
    output_path = os.path.join(output_dir, 'synthetic_panel_2000_2023.csv')
    merged.to_csv(output_path)

    print(f"Saved to: {output_path}")
    print(f"Shape: {merged.shape}")
    print(f"Provinces: {merged.index.get_level_values('province_code').unique().shape[0]}")
    print(f"Years: {merged.index.get_level_values('year').unique().shape[0]}")
    print()
    print("Descriptive statistics:")
    numeric_cols = ['gdp_growth', 'aging_rate', 'labor_ratio', 'savings_rate',
                    'urbanization', 'invest_rate', 'openness', 'consumption_structure']
    print(merged[numeric_cols].describe().round(4))

    # LTC summary
    print()
    print("LTC Pilot Summary:")
    merged['ltc_post'] = merged['ltc_pilot']
    print(f"  Total pilot-obs: {(merged['ltc_pilot'] == 1).sum()}")
    print(f"  Non-pilot obs: {(merged['ltc_pilot'] == 0).sum()}")
    print(f"  Wave 1 (2016): Shanghai, Chengdu, Qinhuangdao, Tai'an, Hefei, Nantong")
    print(f"  Wave 2 (2020): Guangzhou, Shenzhen, Qingdao, Jinan, Nanchang, Zhongshan")


if __name__ == "__main__":
    main()
