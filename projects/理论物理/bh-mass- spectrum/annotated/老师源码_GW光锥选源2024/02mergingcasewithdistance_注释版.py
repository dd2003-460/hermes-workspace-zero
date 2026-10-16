# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】02mergingcasewithdistance.py —— 给并合事件加距离信息
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/02mergingcasewithdistance.py（原样未改）

2024 组第 2 步。输入 01 的 merging_cases_binary.csv，给每个事件加三列：
    comoving_distances —— 事件当前红移的共动距离（光锥"内半径"）
    Redshiftmax        —— 下一个快照的红移
    ComovingDmax       —— 下一个快照红移的共牌距离（光锥"外半径"）

内外半径的物理含义（重要）：
    一个星系在快照 snap 被记录为"并合产物"，它实际并合的时刻可能在这两个
    快照之间的任何时刻。所以这个事件在光锥里可能占据的径向厚度就是
    [D_c(z_snap), D_c(z_snap+1)]——**一个快照间隔**。
    03 脚本选光锥事件时用的就是这对内外半径。
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
from collections import defaultdict

# ---- Millennium 宇宙学：H0=73, Ωm=0.25, ΩΛ=0.75（Boylan-Kolchin 2011 参数）----
c=2.99792458*10**8#m/s
Mpc=3.08568*10**(22)#m
pc=3.08568*10**(16)#m
cMpc=c/Mpc#Mpc/s
ckm=2.99792458*10**5#km/s
OmegaM=0.25
OmegaLam=0.75
n=1#initial spectrum index
h=0.73
Gamma=0.44          # 功率谱形状参数 Γ=Ωm·h
H0=100*h#km/s/Mpc
G=6.77*10**(-11)# m^3/(kg*s^2)
Msun=1.989*10**30#kg
GsunMpc=G*Msun/Mpc**3# Mpc^3/(Msun*s^2)

# ---- 读 01 的产物 + 红移表 ----
df=pd.read_csv('./original data/merging_cases_binary.csv')
RS = pd.read_csv('./original data/redshifts.csv')

# ==============================================================================
# 共动距离：D_c(z) = c/H0 · ∫₀^z dz'/√(ΩΛ+Ωm(1+z')³)
# 用 0-12 步长 0.1 的插值表近似（比逐个 quad 快几百倍）
# ==============================================================================
def integrand(z):
    return 1 / np.sqrt(OmegaLam + OmegaM * (1 + z)**3)

def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return ckm / H0 * integral

z_range = np.arange(0, 12, 0.1)
d_c_values = np.array([comoving_distance(z) for z in z_range])
interp_func = interp1d(z_range, d_c_values, kind='linear')
unique_redshifts = np.array(RS['z'])
comoving_distances = interp_func(unique_redshifts)

# ==============================================================================
# 主循环：给每行加距离三列
# ==============================================================================
ComovingDistance=[]
ComovingDmax=[]
Redshiftmax=[]
for index, row in df.iterrows():
    ComovingDistance.append(comoving_distance(row['redshift']))      # 内半径
    # snapnum → 红移表下标：snapnum-10 是因为 Millennium 的红移表从 snap 10 开始有意义
    # （snap 0-9 对应极高红移，共动距离积分到 12 就截断了）
    current_index = int(row['snapnum']-10)
    Redshiftmax.append(unique_redshifts[current_index-1])            # 下一快照红移
    ComovingDmax.append(comoving_distance(unique_redshifts[current_index-1]))  # 外半径
df['comoving_distances']=ComovingDistance
df['Redshiftmax']=Redshiftmax
df['ComovingDmax']=ComovingDmax
df.to_csv('./original data/merging_cases_binary_withdistance.csv', index=False)

# ==============================================================================
# 振幅粗估（草稿代码，验证数量级用）
# ==============================================================================
# 同样的啁啾质量公式，但这里直接用 ComovingDmax 当距离，没做 (1+z) 修正——
# 是快速估算，正式版在 04 里。
ampliconst=np.sqrt(32./5.)*(np.pi*10**(-8))**(2./3.)*GsunMpc**(5./3.)/cMpc**4
aaa=ampliconst*(df['blackHoleMass']*10**10)**(5./3.)/df['ComovingDmax']
print(df[aaa>10**(-15.5)])   # 打印振幅 > 3e-16 的事件（PTA 大致灵敏度量级）


# ==============================================================================
# 【学习笔记】
# ==============================================================================
# 1. "内外半径 = 相邻快照的共动距离"这个设计很聪明：不用显式定义事件年龄，
#    快照间隔天然就是时间分bin。我们 1.3 的洋葱皮用的是同样的壳层思想。
# 2. snapnum-10 的索引偏移是 Millennium 数据表的怪癖，换数据（TNG 从 snap 0
#    开始连续）不能照抄。
# 3. comoving_distance 在循环里逐个 quad 很慢（每行一次积分）；插值表建好了
#    却只用于 unique_redshifts。工程改进：直接 interp_func(row['redshift'])。
# ==============================================================================
