# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】06MerEventsScatterPlot.py —— 3D 散点图（光锥事件空间分布）
================================================================================
原始文件：raw/老师源码_GW光锥选源2024/06MerEventsScatterPlot.py（原样未改）

2024 组第 6 步，纯绘图：把光锥里的引力波事件按 (x, y, z) 画成 3D 散点。
没有物理计算，代码很短——作用是肉眼看"事件在空间里分布得均不均匀、
有没有沿视线堆积"。
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

c = 3 * 10 ** 5      # km/s（近似值）
H_0=72               # 注意这里写 72（前面脚本是 73）——草稿不一致，不影响定性图
side_length=62.5/H_0*100 # 模拟区域的边长 Mpc（62.5 Mpc/h ÷ 0.72）

# ---- 画布 + 3D 坐标轴 ----
fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, projection='3d')

cols=['frequency','x_Mpc','y_Mpc','z_Mpc']
df=pd.read_csv('./lightcone data/lightcone_events_withfA_9_0517.csv',chunksize=10000,iterator=True,usecols=cols)

i=0
for chunk in df:
    i+=1
    print(i)
    if(i>10000000):   # 安全阀：最多 1000 万块（实际到不了）
        break
    # 只画正八分区、300 Mpc 以内的近距事件（远处太密看不清）
    chunknew=chunk[(chunk['x_Mpc']>0) & (chunk['y_Mpc']>0) & (chunk['z_Mpc']>0) & (chunk['z_Mpc']<300) & (chunk['x_Mpc']<300) & (chunk['y_Mpc']<300)]

    xx=chunknew['x_Mpc'].tolist()
    yy=chunknew['y_Mpc'].tolist()
    zz=chunknew['z_Mpc'].tolist()

    # 逐块往上叠散点（chunksize 流式画图）
    ax.scatter(xx, yy, zz, color='blue',s=0.1)   # s=0.1：点很小，防糊成一团
    ax.mouse_init(rotate_btn=1, zoom_btn=2)      # 鼠标交互：1 旋转 2 缩放


# ==============================================================================
# 【学习笔记】
# ==============================================================================
# 1. 这个脚本没有保存图像的语句（savefig 被注释或漏了），跑完只在窗口显示；
# 2. "只画正八分区 + 300 Mpc"是为了可视清晰——注意这不是数据筛选，
#    物理分析必须用全样本，画图才裁；
# 3. 我们项目 5.2（Observational_Plots）做同样的事时有标校：比如检验
#    大尺度功率谱不为零（周期平铺的验收判据）。
# ==============================================================================
