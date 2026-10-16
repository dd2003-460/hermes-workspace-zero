# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】03SelectLightconeEvents.py —— 周期平铺建光锥（本组最核心）
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/03SelectLightconeEvents.py（原样未改）

这个脚本回答的问题：
    模拟盒子只有 62.5 Mpc/h 大，但我要一个几 Gpc 深的光锥，怎么办？

答案：**周期平铺（periodic tiling）**。把同一个盒子在三个方向上无限复制，
观察者放在原点（盒子角），每个事件的所有镜像副本到原点的距离都算出来，
只保留落在 [inner_radius, outer_radius] 壳层里的副本。

直白类比：你站在一个贴满同样壁纸的房间角落，每面墙后面都有一模一样的房间。
一盏灯在你右前方第 3 个房间亮着，和在你左后方第 5 个房间亮着，对你来说
只是方向不同、距离相同的两个"光源"——周期平铺就是把所有可能的方向都枚举出来。

这和我们项目 1.3 光锥构建是同一个思想（我们有"周期平铺 + 红移壳层"的测试守护）。
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
from collections import defaultdict
import sys
import time

# ---- 宇宙学（Millennium：Ωm=0.25, ΩΛ=0.75, H0=73）----
RS = pd.read_csv('./original data/redshifts.csv')   # 各快照的红移表

c = 2.99792458e5       # km/s
H_0=73                 # km/s/Mpc
h=H_0/100
side_length=62.5/h     # 盒边长换算成 Mpc（62.5 是 Mpc/h 单位）
Omegam=0.25
OmegaLam=0.75


# ---- 共牌距离积分 + 插值表（0-12，步长 0.1）----
def integrand(z):
    return 1 / np.sqrt(OmegaLam + Omegam * (1 + z)**3)

def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return c / H_0 * integral

z_range = np.arange(0, 12, 0.1)
d_c_values = np.array([comoving_distance(z) for z in z_range])
interp_func = interp1d(z_range, d_c_values, kind='linear')
unique_redshifts = np.array(RS['z'])
comoving_distances = interp_func(unique_redshifts)

# ---- 分 36 批处理（每批 50 行，边读边写释放内存，防 OOM）----
for ii in range(0,36):
    if(ii==0):
        headerchoice=True    # 第一批写表头，后续批追加
    else:
        headerchoice=False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, './original data/merging_cases_binary_withdistance.csv')

    # 02 脚本的产物：每个事件带 comoving_distances（内半径）和 ComovingDmax（外半径）
    if(ii==35):
        df=pd.read_csv(file_path)[1700:1739]     # 最后一批（尾数）
    else:
        df=pd.read_csv(file_path)[50*ii:50*(ii+1)]

    # ---- 阶跃函数：step_func(x) = 1 if x>0 else 0 ----
    # 用途见下面"跳过原点盒"的注释
    def step_func(x):
        return np.array(x>0,dtype=int)

    selected_data = []

    # ========================================================================
    # 主循环：对每个事件枚举所有镜像盒，检查壳层归属
    # ========================================================================
    for index, row in df.iterrows():
        redshift=row['redshift']
        inner_radius = row['comoving_distances']   # 内半径：事件当前红移的共动距离
        current_x, current_y, current_z = row['x'], row['y'], row['z']  # 盒内坐标 Mpc/h
        current_index = int(row['snapnum']-10)
        outer_radius = row['ComovingDmax']         # 外半径：下一快照红移的共动距离

        # 镜像枚举范围：外半径能套几个盒子，就每边枚举几圈（+1 保险）
        current_quotient = int(outer_radius / side_length)
        integer_range = range(-current_quotient - 1, current_quotient + 1)

        for i in integer_range:      # x 方向镜像序号
            for j in integer_range:  # y 方向
                for k in integer_range:  # z 方向
                    # ---- 跳过原点所在的盒子（0 号盒）----
                    # step_func(i)+i：i>0 时 = 2i，i<=0 时 = i。
                    # 效果：把 (0,0,0) 这个盒子整体跳过，避免重复计数盒内原始事件
                    # （盒内事件已在 inner/outer 判据里单独处理过）。
                    # 这是一个"打补丁"式的技巧：与其解释清楚不如跳过。
                    if(((step_func(i)+i)**2+(step_func(j)+j)**2+(step_func(k)+k)**2)<(inner_radius/side_length)**2):
                        continue
                    # ---- 镜像坐标 = 原坐标/h（换成 Mpc）+ 平移 i·L ----
                    new_x = current_x/h + i * side_length
                    new_y = current_y/h + j * side_length
                    new_z = current_z/h + k * side_length
                    # ---- 到观察者（原点）的距离 ----
                    new_distance = np.sqrt(new_x**2 + new_y**2 + new_z**2)
                    # ---- 壳层判据：内半径 ≤ 距离 ≤ 外半径 ----
                    # 直白说：这个镜像事件"今天发出的光"到达观察者时，
                    # 它正好处于红移 redshift 到下一快照红移之间。
                    if inner_radius <= new_distance <= outer_radius:
                        selected_data.append({
                            'galaxyid_merged': row['galaxyid_merged'],
                            'haloid_merged': row['haloid_merged'],
                            'galaxyid_1': row['galaxyid_1'],
                            'galaxyid_2': row['galaxyid_2'],
                            'redshift': row['redshift'],
                            'snapnum': row['snapnum'],
                            'x_Mpc': new_x,      # 光锥坐标（Mpc）
                            'y_Mpc': new_y,
                            'z_Mpc': new_z,
                            'blackHoleMass': row['blackHoleMass'],
                            'first_progenitor_blackHoleMass': row['first_progenitor_blackHoleMass'],
                            'next_progenitor_blackHoleMass': row['next_progenitor_blackHoleMass'],
                            'comoving_distance': row['comoving_distances'],
                            'Redshiftmax': row['Redshiftmax'],
                            'ComovingDmax': row['ComovingDmax']
                        })

    selected_df = pd.DataFrame(selected_data)
    # 追加写盘（mode='a'），第一批带表头
    selected_df.to_csv('./lightcone data/lightcone_events_0512.csv', sep=',', index=False, header=headerchoice, mode='a')

    # ---- 释放内存（36 批 × 50 行的流式处理）----
    del df
    del selected_df
    del selected_data
    print('1')


# ==============================================================================
# 【学习笔记】这个脚本的精华和问题
# ==============================================================================
# 精华：
#   1. "周期平铺 + 半径壳层"是光锥构建的经典做法，我们 1.3 用的是同一思想
#      （洋葱皮红移壳层 + 周期平铺，且有 k<2π/L 大尺度模测试守护）；
#   2. 内外半径 = [D_c(z), D_c(z_next)] 的设定，让每个事件按所属红移壳层
#      自动获得正确的径向厚度；
#   3. 分块读写（36 批）体现大数据思维——虽然这里每批只有 50 行，纯粹为防内存炸。
#
# 问题（学习时要注意的）：
#   1. 三重循环 integer_range³ 在高红移（外半径大）时爆炸：q=100 就是 201³≈800 万次/
#      事件。我们项目 1.3 用"洋葱皮"把枚举限制在相邻壳层，没有这个爆炸；
#   2. 盒内原始事件的跳过逻辑（step_func 那个 if）是个 hack，读代码时不要纠结，
#      理解为"避免 0 号盒重复"即可；
#   3. x/h 的单位换算（Mpc/h → Mpc）散落各处，我们项目把单位换算收敛在解析器层。
# ==============================================================================
