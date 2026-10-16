# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】04AddGWfreAmp.py —— 给每个并合事件算引力波频率和振幅
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/04AddGWfreAmp.py（原样未改）

2024 组第 4 步。输入 03 的光锥事件表，给每个事件加两列：
    frequency —— 引力波频率（Hz）
    Amplitude —— 引力波振幅（应变，无量纲）

这是"质量谱 → 可观测量"的最后一环：有了质量和频率，就能算探测器会不会看到。
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
from generateGWfrequency import *    # ⚠️ 外部模块，老师没给！见文末笔记

# ---- 常数（Millennium 宇宙学）----
c=2.99792458*10**8#m/s
Mpc=3.08568*10**(22)#m           # 1 Mpc 的米数
cMpc=c/Mpc#Mpc/s                 # 光速的 Mpc/s
ckm=2.99792458*10**5#km/s
OmegaM=0.25
OmegaLam=0.75
n=1#initial spectrum index
h=0.73
Gamma=0.44
H0=100*h#km/s/Mpc
G=6.67*10**(-11)# m^3/(kg*s^2)
Msun=1.989*10**30#kg
GsunMpc=G*Msun/Mpc**3# Mpc^3/(Msun*s^2)   # 用 Mpc/Msun 单位制的 G

def integrand(z):
    return 1 / np.sqrt(OmegaLam + OmegaM * (1 + z)**3)

def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return ckm / H0 * integral

# ---- 共动距离 → 红移 的反查插值（0-5 范围，200 点）----
zz=np.linspace(0,5,200)
CoDis=[]
for item in zz:
    CoDis.append(comoving_distance(item))
CoDisReds = interp1d(CoDis, zz, kind='linear')   # 注意方向：距离 → 红移


# ==============================================================================
# ★ 引力波振幅公式（爱因斯坦四极矩辐射的标准结果）★
# ==============================================================================
def GWAmplitude(M1,M2,f,D_L):
    # unit: M_c: M_sun ; f0: Hz; dist:Mpc
    M11=M1
    M22=M2
    # ---- 啁啾质量 M_chirp ----
    # 双星系统的"有效质量"：引力波辐射的频率/振幅演化几乎只由它决定。
    # (M1·M2)^(3/5)/(M1+M2)^(1/5)：质量比 1:1 时 = M/2^(1/5)，
    # 质量比悬殊时 → 小质量端（如 10+10⁶ M☉ 的极端质量比旋进）。
    Mchirp=(M11*M22)**(3./5.)/(M11+M22)**(1./5.)
    # ---- 振幅（圆轨道、Hubble 时间尺度的平均应变）----
    # A = √(32/5) · G^(5/3) · M_c^(5/3) · (πf)^(2/3) / c⁴ / D_L
    # 三条标度律背下来就有直觉：
    #   质量翻倍 → 振幅 ×2^(5/3)≈3.2
    #   频率翻倍 → 振幅 ×2^(2/3)≈1.6（并合前频率越来越高，振幅越来越大）
    #   距离翻倍 → 振幅减半
    Amp=np.sqrt(32./5)*GsunMpc**(5./3.)*Mchirp**(5./3.)*(np.pi*f)**(2./3)/cMpc**4/D_L
    return Amp


# ---- 只读需要的列（chunksize 流式处理，防内存炸）----
cols=['redshift','snapnum','x_Mpc','y_Mpc','z_Mpc','blackHoleMass','first_progenitor_blackHoleMass',\
      'nextProgenitor_blackHoleMass','comoving_distance','Redshiftmax','ComovingDmax']


i=0
df=pd.read_csv('./lightcone data/lightcone_events_0512.csv',chunksize=10000,iterator=True,usecols=cols)
for chunk in df:
    i+=1
    if(i==1):
        headerchoice=True
    else:
        headerchoice=False
    frequencytotal=[]
    frequency=[]
    Amplitude=[]
    for index, row in chunk.iterrows():
        # ---- 双方黑洞质量：10^10 Msun/h → Msun ----
        M1=row['first_progenitor_blackHoleMass']*10**10/h
        M2=row['next_progenitor_blackHoleMass']*10**10/h
        MM=(M1+M2)
        # ---- 由光锥坐标反查红移 ----
        x=row['x_Mpc']
        y=row['y_Mpc']
        z=row['z_Mpc']
        CoD=np.sqrt(x**2+y**2+z**2)   # 共动距离 = 光锥坐标的模长
        zz=CoDisReds(CoD)
        DL=CoD*(1+zz)                 # 光度距离 = 共动距离 ×(1+z)
        # ---- 频率：invF_f(随机数, 总质量) ----
        # 物理：给一个随机的 inspiral 时间（0-1 映射到 log 时间），
        # 用 Peters 公式反解出该时刻的 GW 频率。总质量越大，并合频率越低。
        ff=invF_f(np.random.random(),MM)
        # ---- 振幅 ----
        Amp=GWAmplitude(M1,M2,ff,DL)
        frequency.append(ff)
        Amplitude.append(Amp)
        frequencytotal.append({'frequency':ff})
    chunk['frequency']=frequency
    chunk['Amplitude']=Amplitude

    # ---- 追加写盘 ----
    chunk.to_csv('./lightcone data/lightcone_events_withfA_01pc_0517.csv',  sep=',', index=False,header=headerchoice, mode='a')

    del frequencytotal
    del frequency
    del frequencydata
    del Amplitude


# ==============================================================================
# 【学习笔记】
# ==============================================================================
# 1. 缺失的依赖：`from generateGWfrequency import *` —— 这个模块老师没给。
#    从调用方式 invF_f(随机数, 总质量) 推断，它实现的是：
#        Peters (1964) 并合时间公式 t = ... 反解 → 频率 f(t)
#    想复现就自己写：给 log t 均匀采样，用
#        f_gw = (1/π)·(5/256·c³/G·(M1M2/M)^... )^(3/8)... 反解即可
#    （标准参考：Peters & Mathews 1963；或 Maggiore 教科书 §4.3）
#
# 2. 频率没有乘 (1+z) 修正——发射频率直接当探测频率用了。严格做法：
#    观测频率 f_obs = f_emit/(1+z)（05 脚本里补了这个修正）。
#
# 3. 和我们项目的接口：我们 4.2 空间装配产出每个 BH 的位置 + 质量后，
#    这个 GWAmplitude 公式就是"质量谱 → 探测应变"的直接映射。
#    啁啾质量 (M1M2)^(3/5)/(M1+M2)^(1/5) 是必须记住的公式——
#    引力波天文学里几乎所有标度律都以它为核心。
# ==============================================================================
