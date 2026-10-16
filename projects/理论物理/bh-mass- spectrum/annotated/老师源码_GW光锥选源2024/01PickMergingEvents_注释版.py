# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】01PickMergingEvents.py —— 从并合树挑"双黑洞并合事件"
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/01PickMergingEvents.py（原样未改）

2024 组流水线的第 1 步。输入 Millennium 的 result.csv（并合树导出），
输出 merging_cases.csv：每一行是一个"两个黑洞并合到一起"的事件。

直白说这个脚本在回答一个问题：
    **树里哪些星系是"并合产物"，而且并合双方都带着黑洞？**
================================================================================
"""

import os
import pandas as pd
import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt
from scipy import interpolate

# ==============================================================================
# 宇宙学参数（Millennium 专用：Ωm=0.25, ΩΛ=0.75, H0=72 km/s/Mpc）
# ⚠️ 和我们项目的 Planck 参数不同，距离换算不能混用
# ==============================================================================
c=2.9979e8            # 光速 m/s
H=72                  # H0，km/s/Mpc
a_dot=H               # 尺度因子导数（用于共动距离积分）
G=6.67e-11
pi=3.14159265359
k=-1                  # R-W 度规的曲率符号（k=-1 开放，但下面被覆写为 0）
rhox0=6.66e-2         # 宇宙学常数项（后被覆写）
rhom0=2.33e-4         # 物质项（后被覆写）
rhoR0=1.23e-3         # 辐射项
rhocr=3*H**2/(8*pi*G) # 临界密度
Omegam=rhom0/rhocr
Omegam=0.3            # ← 注意：先算 0.25 又被硬覆写成 0.3（草稿痕迹，实际生效 0.25/0.75，见下）
Omegax=rhox0/rhocr
Omegax=0.7            # ← 同样被覆写
Omegak=-k/H**2
Omegak=0
OmegaR=1-Omegam-Omegax-Omegak
OmegaR=0              # 辐射项忽略（低红移近似）

# ---- 读数据：result.csv 有 19 行头部说明，跳过；最后 1 行是脚注，跳过 ----
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'result.csv')
header_rows = 19
df = pd.read_csv(file_path,skiprows=header_rows,skipfooter=1)


# ==============================================================================
# 共动距离函数：D_c(z) = ∫c/(a²·ȧ·E(a)) da 从 a_z 到 1
# （用尺度因子 a 积分，等价于教科书的 ∫c/H(z) dz）
# ==============================================================================
def coMovingDistance(z):
    a_z = 1 / (1 + z)
    F = lambda a: c / (a * a * a_dot * np.sqrt(Omegax + Omegam / a**3 + OmegaR / a**4 + Omegak / a**2))
    X, _ = spi.quad(F, a_z, 1)
    return X


merging_cases = []   # 收集所有合格事件

# ==============================================================================
# 主循环：逐行检查每个星系是不是"合格的双黑洞并合事件"
# ==============================================================================
for index, row in df.iterrows():
    # ---- 条件 1：这个星系有第一代祖宗（说明它是并合产物，不是初代星系）----
    first_progenitor_id = row['firstProgenitorId']
    if first_progenitor_id != -1:
        # ---- 条件 2：第一代祖宗还有"兄弟"祖宗 ----
        # 并合树的规则：一个并合产物有多个祖宗分支。firstProgenitorId 指向
        # 第一个分支，它的 nextProgenitorId 指向第二个分支。
        # 如果 nextProgenitorId == -1，说明只有一根分支，没发生并合。
        first_progenitor_row = df[df['galaxyid'] == first_progenitor_id]
        if first_progenitor_row['nextProgenitorId'].values[0] != -1:
            # ---- 取双方祖宗的黑洞质量 ----
            first_progenitor_black_hole_mass = first_progenitor_row['blackHoleMass'].values[0]
            next_progenitor_id = first_progenitor_row['nextProgenitorId'].values[0]
            next_progenitor_row = df[df['galaxyid'] == next_progenitor_id]
            next_progenitor_black_hole_mass = next_progenitor_row['blackHoleMass'].values[0]

            # ---- 条件 3：双方黑洞质量都非零（没黑洞就没有双黑洞并合）----
            if first_progenitor_black_hole_mass != 0 and next_progenitor_black_hole_mass != 0:
                # 三个条件全过 → 记为一个并合事件
                merged_galaxy_distance = coMovingDistance(row['redshift'])
                df.at[index, 'coMovingDistance'] = merged_galaxy_distance
                merging_case = {
                    'galaxyid_merged': row['galaxyid'],          # 并合后星系
                    'haloid_merged': row['haloid'],
                    'galaxyid_1': first_progenitor_id,           # 并合方 1
                    'galaxyid_2': first_progenitor_row['nextProgenitorId'].values[0],  # 并合方 2
                    'redshift': row['redshift'],
                    'snapnum': row['snapnum'],
                    'x': row['x'], 'y': row['y'], 'z': row['z'], # 位置 Mpc/h
                    'stellarMass': row['stellarMass'],
                    'bulgeMass': row['bulgeMass'],
                    'blackHoleMass': row['blackHoleMass'],       # 并合后黑洞质量
                    'first_progenitor_blackHoleMass': first_progenitor_black_hole_mass,  # 并合前 1
                    'next_progenitor_blackHoleMass': next_progenitor_black_hole_mass,    # 并合前 2
                }
                merging_cases.append(merging_case)

# ---- 落盘 ----
merging_cases_df = pd.DataFrame(merging_cases)
merging_cases_df.to_csv('merging_cases.csv', index=False)
print('1')


# ==============================================================================
# 【学习笔记】
# ==============================================================================
# 1. "并合事件"的判据就三条：有第一祖宗 + 第一祖宗有兄弟 + 双方黑洞非零。
#    这是最朴素的二元判据——不区分主并合/次并合，不管质量比，不分层次。
#
# 2. 性能提示：df[df['galaxyid'] == ...] 是 O(N) 查找，放在 O(N) 循环里就是 O(N²)。
#    Millennium result.csv 才几万行跑得动；**换 TNG（千万行）必须先建索引**
#    （df.set_index('galaxyid').loc[...]），这是我们适配 TNG 时要做的第一件事。
#
# 3. 和我们项目的关系：我们项目把"并合"整体列为 P3-OPTIONAL（本期不做）。
#    如果将来要做，这个脚本就是最小实现的原型；要做严格版需加：
#    延时时间分布（DTD）、质量比筛选、层次并合（三级、四级）。
# ==============================================================================
