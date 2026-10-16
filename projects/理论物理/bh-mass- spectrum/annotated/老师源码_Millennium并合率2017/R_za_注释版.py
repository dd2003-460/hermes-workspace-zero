# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】R_za.py —— 并合率计算的多进程版（pp 并行）
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/R_za.py（原样未改）

和 R_zanp.py（已详细注释）是**同一套逻辑**，差别只有两点：
    1. 用 pp（parallel python）把 200 万条记录切成 21 块分给多个 CPU 核；
    2. 不输出 mBH，只输出并合率（allMRBH.txt 每行一个数）。
学习这个文件只需看"怎么并行"，物理看 R_zanp 注释版即可。

⚠️ Python 2 + pp 库，两者都已停止维护。现代等价物：multiprocessing.Pool
   或 numpy 向量化（我们项目全部走向量化 + 可选 numba）。
================================================================================
"""

import sys, time
import pp
import numpy as np

def mainp(number):
    """
    每个 worker 进程的入口：参数 number 是这块数据的起始行号。
    注意 global 声明：pp 的 worker 会把函数序列化到子进程，全局变量
    （data/info/Count/IMF/T/row/snap0）在每个子进程里独立初始化一份——
    这就是为什么下面每个 worker 都要重新读一遍文件（21 个进程读 21 遍）。
    """
    global data, info, Count, IMF, T, row, snap0
    #initialization
    T=[] #unit:Gyr, lookback time
    StellarMass=[]
    MetSteMass=[]
    Count=[] #count
    #read data（每个 worker 各读一遍——2017 年的朴素做法，浪费但简单）
    lines=open('mMR.dat','r').readlines()
    data=[line.strip().split(' ') for line in lines]
    lines=open('snapinfo.csv','r').readlines()#snapnum,a,z,Hz,lookbacktime
    info=[line.strip().split(',') for line in lines]
    #conversion character into real number or int
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

    # ---- 填 T（回顾时间）+ Count（快照组边界）----
    for i in range(row):
        StellarMass.append(data[i][6])
        MetSteMass.append(data[i][7])
        T.append(lbt(data[i][0])) #unit: Gyr
        if i>0:
            if data[i][0]-data[i][0-1]>0:
                Count.append(i)
            elif data[i][0]-data[i][0-1]<0:
                print 'Please reorder data!'
    Count.append(row)
    snap0=data[0][0]

    # ---- 算 IMF（每条记录抽一次前身星）----
    IMF=map(imf,MetSteMass,StellarMass) #[list(tuple)]

    return larcycle(number)


def lbt(snapnum):#lookback time
    """回顾时间查找（同 R_zanp）"""
    t=info[snapnum][4]
    return t #unit: Gyr

def imf(metalsStellarMass,stellarMass):
    """
    ★ 同 R_zanp 的 imfbh()，但不返回 mBH，只返回 phi ★
    物理完全一样：金属丰度 → 变形 IMF → 逆 CDF 抽一颗前身星 → 返回 IMF 密度值。
    """
    metalSun=0.0134
    A=0.3
    beta=0.8
    gamma=0.2
    if stellarMass==0:
        phi=0
    else:
        metal=metalsStellarMass/stellarMass
        cons=40*(((metal/0.01/metalSun)**gamma+1)/40.0/A)**(1/(beta+1))
        phi0=-1.35*cons**1.35/(100**(-1.35/(beta+1))-3**(-1.35/(beta+1)))
        ran=np.random.rand()
        mBH=(3**(-1.35/(beta+1))-1.35*ran*cons**1.35/phi0)**(-(beta+1)/1.35)
        m=cons*mBH**(1/(beta+1))
        phi=phi0*m**(-2.35)
    return phi

def cycle(i):
    """同 R_zanp 的 cycle()：祖宗区遍历求推前并合率（零延时近似）"""
    ob_id=data[i][1] #galaxyID
    ob_lpid=data[i][2] #lastProgenitorId
    snap=data[i][0]
    mergerRate=0
    num1=Count[snap-snap0-1]
    for j in range(num1):#only progenitor galaxies
        if ob_id < data[j][1] <= ob_lpid:
            mergerRate=mergerRate+data[j][8]*IMF[j]*(1/(T[j]-lbt(snap)))*(T[j]-lbt(data[j][0]+1))
    return mergerRate

def larcycle(number):
    """
    分块执行器：把 [number, number+100000) 这 10 万条交给 cycle 算。
    三个分支处理三种边界情况（起点太靠前/太靠后/正常）。
    """
    if Count[0]<number<2000000:
        result=map(cycle,range(number,number+100000))
    elif number<=Count[0]:
        result=map(cycle,range(Count[0],number+100000))
    else:
        result=map(cycle,range(number,row))
    return result


bhMR=[0 for i in range(2)] #merger rate

# ---- pp 并行主控 ----
inputs = range(0,2000001,100000)# 21 CPUs —— 21 个块，每块 10 万条
ppservers = ()                  # 可填 ("10.0.0.1",) 做多机集群
if len(sys.argv) > 1:
    ncpus = int(sys.argv[1])
    job_server = pp.Server(ncpus, ppservers=ppservers)   # 按命令行参数定核数
else:
    job_server = pp.Server(ppservers=ppservers)          # 自动探测核数
print "pp cores numbers", job_server.get_ncpus(), "workers"
start_time = time.time()
# 每个 worker 提交 mainp（number），并声明依赖的函数（lbt/imf/cycle/larcycle）
# pp 会把依赖函数一起序列化到子进程
jobs = [(input, job_server.submit(mainp,(input,), (lbt,imf,cycle,larcycle))) for input in inputs]
for input, job in jobs:
    bhMR.extend(job())     # 收集各块结果
print "time multi:", time.time() - start_time, "s"
job_server.print_stats()
print 'save data'
np.savetxt('allMRBH.txt',bhMR,delimiter=',')


# ==============================================================================
# 【学习笔记】2017 年的并行方案 vs 现在
# ==============================================================================
# 老师的选择（pp）：
#   + 函数级提交，代码改动小；
#   - 每个 worker 重复读全量数据（21 份内存）；
#   - pp 库停止维护，Python 3 不可用；
#   - 结果顺序依赖 inputs 顺序（extend 的先后），隐式假设。
# 现代做法：
#   multiprocessing.Pool.map + 每 worker 用 numpy memmap 读自己那一片；
#   或干脆向量化：cycle 的祖宗区求和可以写成"按 lastProgenitorId 分组的
#   矩阵乘法"（我们项目 4.1 就是这么干的，见 4.1_Pushforward_Inference）。
# ==============================================================================
