# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】R_zanps.py —— R_zanp 的又一变体（s = small/单块？）
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/R_zanps.py（原样未改）

和 R_zanp 逐行相同（读那边注释），差别只在**文件末尾的执行部分被截断/不同
（原始文件在 cycle 定义后内容与 R_zanp 一致，尾部执行段略有差异）**。
命名规律：R_za（多进程）→ R_zanp（+mBH 输出）→ R_zanpN（分块）→ R_zanps（s 后缀，
猜测是 serial 或 small 的调试版）。

学习价值：这是真实的科研代码常态——一个脚本改来改去产生一串近似副本。
**抓最早/最完整的版本（R_zanp）读透，其余对照 diff 看**。
================================================================================
"""

import numpy as np

# ---- 与 R_zanp.py 完全相同的前半部分（数据读取 + imfbh + cycle）----
T=[]
StellarMass=[]
MetSteMass=[]
Count=[]

lines=open('mMR.dat','r').readlines()
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()
info=[line.strip().split(',') for line in lines]

row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])
    data[i][1]=long(data[i][1])
    data[i][2]=long(data[i][2])
    for j in range(3,9):
        data[i][j]=float(data[i][j])
for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

def lbt(snapnum):
    t=info[snapnum][4]
    return t

def imfbh(metalsStellarMass,stellarMass):
    """同 R_zanp：金属丰度 → 变形 IMF → 抽前身星 → (phi, mBH)"""
    metalSun=0.0134
    A=0.3
    beta=0.8
    gamma=0.2
    if stellarMass==0:
        phi=0
        mBH=0
    else:
        metal=metalsStellarMass/stellarMass
        cons=40*(((metal/0.01/metalSun)**gamma+1)/40.0/A)**(1/(beta+1))
        phi0=-1.35*cons**1.35/(100**(-1.35/(beta+1))-3**(-1.35/(beta+1)))
        ran=np.random.rand()
        mBH=(3**(-1.35/(beta+1))-1.35*ran*cons**1.35/phi0)**(-(beta+1)/1.35)
        m=cons*mBH**(1/(beta+1))
        phi=phi0*m**(-2.35)
    return phi,mBH

def cycle(i):
    """同 R_zanp：推前并合率（零延时）+ 自身黑洞质量"""
    ob_id=data[i][1]
    ob_lpid=data[i][2]
    snap=data[i][0]
    mergerRate=0
    num1=Count[snap-snap0-1]
    for j in range(num1):
        if ob_id < data[j][1] <= ob_lpid:
            mergerRate=mergerRate+data[j][8]*IMFbh[j][0]*(1/(T[j]-lbt(snap)))*(T[j]-lbt(data[j][0]+1))
    return mergerRate, IMFbh[i][1]

# ---- 预处理同 R_zanp（略，见 R_zanp_注释版.py 对应段）----

# ==============================================================================
# 【学习笔记】从这串副本能学到什么
# ==============================================================================
# 1. 命名即历史：za → zanp → zanpN → zanps，每次改动加个后缀，舍不得删旧的——
#    这是没有版本管理的年代的"穷人 git"。我们项目用 git + 模块编号，
#    就是不想再留这种 spaghetti；
# 2. 调试方法论：先小数据（zanps?）→ 单机全量（zanp）→ 多进程（za）→
#    手工分块（zanpN）。这个"放大路径"本身是对的，只是工具老了；
# 3. 如果只想跑一遍看结果：用 R_zanp_注释版.py 改好的 Python 3 版，
#    不要碰这四个副本。
# ==============================================================================
