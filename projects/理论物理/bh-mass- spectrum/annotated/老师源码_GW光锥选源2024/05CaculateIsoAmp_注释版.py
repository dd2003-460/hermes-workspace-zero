# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】05CaculateIsoAmp.py —— 把成千上万个源的振幅叠成背景曲线
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/05CaculateIsoAmp.py（原样未改）

2024 组第 5 步。输入 04 的频率+振幅表，输出各向同性应变（背景）曲线：
    按 log 频率分箱（10⁻⁹–10⁻⁶ Hz，PTA 频段，每箱 0.3 dex），
    每箱累加所有源振幅的平方，最后画 log10√(ΣA²/Δf)。

物理：单个源的振幅太小看不见，但**成千上万个微弱信号非相干叠加**就形成
可探测的随机引力波背景。平方和而不是直接相加，因为各源相位随机——
这正是 PTA（脉冲星计时阵列）探测超大质量双黑洞并合背景的标准预期方法。
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
from cosmo_model import *     # ⚠️ 同样缺失的外部模块（宇宙学距离函数库）
import time

# ---- 常数（Millennium 宇宙学）----
c=2.99792458*10**8#m/s
Mpc=3.08568*10**(22)#m
cMpc=c/Mpc#Mpc/s
ckm=2.99792458*10**5#km/s
OmegaM=0.25
OmegaLam=0.75
n=1#initial spectrum index
h=0.73
Gamma=0.44
H0=100*h#km/s/Mpc
G=6.67*10**(-11)# m^3/(kg*s^2)
Msun=1.989*10**30#kg
GsunMpc=G*Msun/Mpc**3# Mpc^3/(Msun*s^2)

# ---- 分箱设置 ----
step=0.3                                          # 每箱 0.3 dex（对数频率）
lens=int((-6-(-9))/step)                          # 箱数 = 3/0.3 = 10 箱
amplitudetotal=np.zeros(lens)                     # 每箱的 ΣA²
eventnumber=np.zeros(lens)                        # 每箱的事件数
lnfrequency=np.linspace(-9,-6-step,lens)          # 箱中心：-9, -8.7, ..., -6.3

# ---- 流式读 04 的产物 ----
df=pd.read_csv('./lightcone data/lightcone_events_withfA_01pc_0517.csv',chunksize=10000,iterator=True)

for chunk in df:
    for index, row in chunk.iterrows():
        amp=row['Amplitude']
        z=row['redshift']
        # ---- 关键修正：发射频率 → 观测频率 ----
        # 宇宙膨胀把引力波拉长：f_obs = f_emit/(1+z)。
        # 04 脚本漏了这个修正，这里补上。
        f=row['frequency']/(1+z)
        lnf=np.log(f)/np.log(10)                  # log10 f_obs
        # ---- 只收 PTA 频段（10⁻⁹–10⁻⁶ Hz）----
        if(-9 < lnf < -6):
            num=int((lnf-(-9))/step)              # 落箱编号
            amplitudetotal[num]+=amp**2           # 非相干叠加：振幅平方和
            eventnumber[num]+=1

# ---- 输出：特征应变 √(ΣA²/Δf)，转 log10 ----
print('evenum',eventnumber)                       # 每箱事件数（诊断用）
amplitude=np.array(amplitudetotal)
print('amp',amplitude)
plt.plot(lnfrequency,np.log(np.sqrt(amplitude/step))/np.log(10))

# 注释里留着历史运行结果，可以直接对比复现：
# evenum [1.4554494e+07 1.7529045e+07 1.0277891e+07 3.7433240e+06 ...]
# amp [7.14348116e-34 4.85408252e-32 1.50527533e-30 3.01571479e-29 ...]


# ==============================================================================
# 【学习笔记】"背景应变"是什么
# ==============================================================================
# 1. 单个 10⁹ M☉ 双黑洞在 nHz 频段的应变 ~10⁻¹⁶–10⁻¹⁵，LIGO（10⁻¹⁰ Hz 频段）
#    看不到，PTA（nHz）正是为这个频段设计的；
# 2. 非相干叠加：ΣA² 而不是 (ΣA)²——各源相位随机，直接相加会互相抵消；
# 3. √(ΣA²/Δf) 就是"特征应变" h_c 的简易版，论文里画背景曲线都用它；
# 4. 事件数分布（1.5e7 个在最低频箱）直接反映质量函数——大质量双黑洞多、
#    频率低。如果我们项目的 BH 质量谱要出"可探测性"结论，这个分箱叠加
#    就是标准动作。
# ==============================================================================
