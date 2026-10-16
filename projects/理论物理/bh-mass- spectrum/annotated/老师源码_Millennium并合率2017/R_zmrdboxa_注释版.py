# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】R_zmrdboxa.py —— 并合率 → 并合率密度随红移的分布 MRD(z)
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/R_zmrdboxa.py（原样未改）

第一组的下游脚本：读 R_za 系列产出的 allMRBH.txt（每行一个并合率），
按快照分箱求和，除以盒子体积，得到**并合率密度**（每年每立方 Mpc 多少次并合），
存成 MRDa.dat（红移 + 密度两列），供 superGW6e3.py 抽样用。

直白说：前手算出"每个星系并合得多快"，这个脚本回答"宇宙里平均每立方 Mpc
每年并合多少次"——这是可以和观测/其他模拟对比的量。
================================================================================
"""

import numpy as np
from pylab import *
import math
import mpl_toolkits.mplot3d

# ---- 容器初始化 ----
Snapnum=[]; X=[]; Y=[]; Z=[]
R=[] #unit:Mpc/h
Rr=[]
Count=[] #count

# ---- 观察者坐标（盒子角上 = 原点）----
xc=0; yc=0; zc=0
xs=[]; ys=[]; zs=[]
sma_len=62.5 # 盒边长 Mpc/h —— 分箱时要除掉体积

# ---- 读三个文件 ----
lines=open('mMR.dat','r').readlines()                  # 原始星系表（只要 snapnum 列）
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()             # 快照宇宙学信息
info=[line.strip().split(',') for line in lines]
lines=open('allMRBH.txt','r').readlines()              # ← R_za 系列的产物：每行 (并合率, mBH)
BHMR=[line.strip().split(',') for line in lines]

bhMR=[]
row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])       # snapnum
    data[i][1]=long(data[i][1])      # galaxyID
    data[i][2]=long(data[i][2])      # lastProgenitorId
    for j in range(3,9):
        data[i][j]=float(data[i][j])
    bhMR.append(float(BHMR[i][0]))   # 只取第 0 列（并合率），忽略 mBH

for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

# ---- 快照组边界 ----
def lbt(snapnum):#lookback time
    t=info[snapnum][4]
    return t

def reds(snapnum):#redshift
    """快照号 → 红移（查 snapinfo 表）"""
    redshift=info[snapnum][2]
    return redshift

for i in range(row):
    Snapnum.append(data[i][0])
    if i>0:
        if Snapnum[i]-Snapnum[i-1]>0:
            Count.append(i)   # 新组边界
        elif Snapnum[i]-Snapnum[i-1]<0:
            print 'Please reorder data!'
Count.append(row)

# ==============================================================================
# 核心：按快照分箱算并合率密度
# ==============================================================================
MRD=[]      # 并合率密度列表
Redshift=[] # 对应的红移
for j in range(1,len(Count)):
    MRS=00   # 这个快照的总并合率
    for i in range(Count[j-1],Count[j]):   # 组内所有记录求和
        MRS=MRS+bhMR[i]
    # 除以盒子体积（62.5³ (Mpc/h)³）得密度
    mrd=MRS*sma_len**(-3)#unit change
    MRD.append(mrd)
    Redshift.append(reds(Snapnum[i]))

def nor(mrd):#normlization
    """归一化到 z=0 处的 1e-7（纯画图方便，无物理意义）"""
    return mrd/MRD[-1]*1e-7

print 'R(z=0)=',MRD[-1]
MRD=map(nor,MRD)

# ---- 落盘：每行 "红移 密度" ----
print 'begin saving data'
save=open('MRDa.dat','w')
for i in range(len(MRD)):
    print >> save, Redshift[i], MRD[i]
save.close()


# ==============================================================================
# 【学习笔记】并合率密度 = 什么
# ==============================================================================
# MRD(z) [/(yr·Mpc³)] 是引力波宇宙学的核心观测量之一：
#   - 可以和 LIGO/Virgo 的 GWTC 星表、NANOGrav 的背景上限对比；
#   - Madau & Dickinson (2014) 的 SFR 密度乘一个"每个单位 SFR 产多少并合"
#     就是它的一阶估计（我们项目的 Ṅ = ψ·η 是同一个骨架）；
# 这里的实现是"快照分箱求和 ÷ 盒体积"，**没有做体积的共动修正**——
# 严格做法要除以共动体积 dV/dz（我们 1.1 阶段就有这个函数），
# 以及乘上 1/(1+z) 做时间 dilation。学习时知道这个近似即可。
# ==============================================================================
