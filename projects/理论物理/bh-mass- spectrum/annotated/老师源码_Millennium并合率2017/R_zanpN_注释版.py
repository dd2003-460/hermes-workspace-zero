# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】R_zanpN.py —— 手工分块版（"我是第 N 块"）
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/R_zanpN.py（原样未改）

R_zanp 的**手工并行变体**：改一个数字 nn=21，这个进程就算第 21 块。
在没有任务调度器的年代（2017），做法是开 21 个终端，每个里改一次 nn 再跑——
输出文件按块编号命名（allMRBH21.txt），最后手动拼接。

除了并行方式，物理逻辑和 R_zanp 完全相同（imfbh + cycle 一模一样），
**读 R_zanp_注释版.py 即可**，这里只看分块的差别。
================================================================================
"""

import numpy as np

# ---- 以下到 cycle() 结束，与 R_zanp.py 逐行相同（读那边注释）----
# 容器：T（回顾时间）、StellarMass、MetSteMass、Count（快照组边界）
T=[]
StellarMass=[]
MetSteMass=[]
Count=[]

# ---- 读数据（与 R_zanp 相同）----
lines=open('mMR.dat','r').readlines()
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()
info=[line.strip().split(',') for line in lines]

row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])
    data[i][1]=long(data[i][1])      # py2：大整数要 long
    data[i][2]=long(data[i][2])
    for j in range(3,9):
        data[i][j]=float(data[i][j])
for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

def lbt(snapnum):#lookback time
    t=info[snapnum][4]
    return t

def imfbh(metalsStellarMass,stellarMass):
    """同 R_zanp：金属丰度 → 变形 IMF → 抽前身星，返回 (phi, mBH)"""
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
    """同 R_zanp：祖宗区遍历，SFR×IMF 摊时间得并合率"""
    ob_id=data[i][1]
    ob_lpid=data[i][2]
    snap=data[i][0]
    mergerRate=0
    num1=Count[snap-snap0-1]
    for j in range(num1):
        if ob_id < data[j][1] <= ob_lpid:
            mergerRate=mergerRate+data[j][8]*IMFbh[j][0]*(1/(T[j]-lbt(snap)))*(T[j]-lbt(data[j][0]+1))
    return mergerRate, IMFbh[i][1]

# ---- 预处理（与 R_zanp 相同）----
for i in range(row):
    StellarMass.append(data[i][6])
    MetSteMass.append(data[i][7])
    T.append(lbt(data[i][0]))
    if i>0:
        if data[i][0]-data[i][0-1]>0:
            Count.append(i)
        elif data[i][0]-data[i][0-1]<0:
            print 'Please reorder data!'
Count.append(row)
snap0=data[0][0]

IMFbh=map(imfbh,MetSteMass,StellarMass)

# ==============================================================================
# 与 R_zanp 的唯一差别：手工分块
# ==============================================================================
'''
# 被注释掉的旧版：固定算前 10 万条
bhMR=[(0,0) for i in range(2)]
bhMR.extend(map(cycle,range(Count[0],100001)))
print 'save data'
np.savetxt('allMRBH01.txt',bhMR,delimiter=',')
'''

number=100000     # 每块 10 万条
bhMR=[]
nn=21             # ★ 我是第 21 块（1-21）。开 21 个进程就改这里 ★
bhMR.extend(map(cycle,range((nn-1)*number,row)))   # 算 [(nn-1)*10万, 总行数)
print 'save data'
np.savetxt('allMRBH'+str(nn)+'.txt',bhMR,delimiter=',')


# ==============================================================================
# 【学习笔记】手工并行的三个坑
# ==============================================================================
# 1. 块边界不整齐：第 21 块实际算的是 [200万, row)——如果 row=230万，
#    第 21 块有 30 万条，其他块 10 万条，负载不均；
# 2. 结果顺序 = 进程启动顺序，没有任何机制保证；
# 3. 任何一块 OOM/崩溃，不会有人知道——没有调度器、没有重试。
# 这就是 2017 年"穷人并行"的真实面貌。现代等价物一行搞定：
#    from multiprocessing import Pool
#    with Pool(21) as p: results = p.map(cycle, range(row), chunksize=10000)
# 而且 numpy 向量化后这个脚本的绝大部分工作可以去掉循环（我们 4.1 的做法）。
# ==============================================================================
