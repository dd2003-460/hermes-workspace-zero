# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】07MerEventsScatterPlot-2D.py —— 2D 散点图（x-y 平面，z 着色）
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/07MerEventsScatterPlot-2D.py（原样未改）

06 的 2D 版：画 x-y 平面，用 z（深度）着色。一眼看"近处和远处的事件
分布有没有差别"——比如远处变稀是宇宙膨胀+距离效应，近处变密是局部成团。
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

c = 3 * 10 ** 5
H_0=72
side_length=62.5/H_0*100 # 模拟区域的边长 Mpc

fig = plt.figure(dpi=300)
ax = fig.add_subplot(111)      # ← 和 06 的唯一结构差别：2D 轴

cols=['frequency','x_Mpc','y_Mpc','z_Mpc']
df=pd.read_csv('./lightcone data/lightcone_events_withfA_9_0517.csv',chunksize=10000,iterator=True,usecols=cols)

i=0
for chunk in df:
    i+=1
    print(i)
    if(i>10000):               # 注意：06 是 1000 万，这里 1 万——画 2D 更费渲染
        break
    # 只留 z<100 的近距事件（2D 图看近场结构）
    chunknew=chunk[(chunk['x_Mpc']>0) & (chunk['y_Mpc']>0) & (chunk['z_Mpc']>0) &  (chunk['z_Mpc']<100)]

    xx=chunknew['x_Mpc'].tolist()
    yy=chunknew['y_Mpc'].tolist()
    zz=chunknew['z_Mpc'].tolist()

    # c=zz：颜色映射到 z 值（深度），colorbar 会显示 z 标尺
    ax.scatter(xx, yy, c=zz,s=0.1)
    plt.xlim(0,300)
    plt.ylim(0,300)


# ==============================================================================
# 【学习笔记】
# ==============================================================================
# 和 06 完全同构，差别只在：
#   - projection='3d' 去掉 → 2D；
#   - c=zz → 用深度着色；
#   - z<100 筛选（比 06 的 300 更近，2D 图信息密度低）；
# 这类"同构变体"在老师代码里很常见（R_za/zanp/zanpN/zanps 也是），
# 学习时抓一个代表读透，其余看差异行即可。
# ==============================================================================
