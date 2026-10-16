# -*- coding: utf-8 -*-
"""
Created on Fri May  3 16:37:19 2024

@author: Qing
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
side_length=62.5/H_0*100 #模拟区域的边长
# 创建一个新的图像
fig = plt.figure(dpi=300)
# 创建一个3D绘图区域
ax = fig.add_subplot(111, projection='3d')

cols=['frequency','x_Mpc','y_Mpc','z_Mpc']
#RS = pd.read_csv('./original data/redshifts.csv')
df=pd.read_csv('./lightcone data/lightcone_events_withfA_9_0517.csv',chunksize=10000,iterator=True,usecols=cols)

i=0
for chunk in df:
    i+=1
    print(i)
    if(i>10000000):
        break
    #定义并计算参数
    chunknew=chunk[(chunk['x_Mpc']>0) & (chunk['y_Mpc']>0) & (chunk['z_Mpc']>0) & (chunk['z_Mpc']<300) & (chunk['x_Mpc']<300) & (chunk['y_Mpc']<300)]

    xx=chunknew['x_Mpc'].tolist()
    yy=chunknew['y_Mpc'].tolist()
    zz=chunknew['z_Mpc'].tolist()
    
    #print(xx)
    
    

     
    # 绘制散点图
    ax.scatter(xx, yy, zz, color='blue',s=0.1)
    ax.mouse_init(rotate_btn=1, zoom_btn=2)
    #ax.view_init(elev=0, azim=-35)
    
    
    # xx=[10,20,30,40,50,60,70]
    # yy=[10,20,30,40,50,60,70]
    # zz=[10,20,30,40,50,60,70]
    
    # ax.scatter(xx, yy, zz,color='blue')
    # ax.mouse_init(rotate_btn=1, zoom_btn=2)