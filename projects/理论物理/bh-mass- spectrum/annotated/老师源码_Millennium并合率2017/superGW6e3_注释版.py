# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】superGW6e3.py —— 把小盒子吹成 6 Gpc 大立方体，抽样引力波源
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/superGW6e3.py（原样未改）

第一组的收尾脚本，回答的问题：
    并合率密度有了，但那是"平均每立方 Mpc 多少次"。要模拟一次真实的
    GW 探测目录（哪个方向、多远、什么时候并合），得把事件**随机撒进一个
    足够大的体积**里——而且每个事件的出现概率 = 它的并合率。

做法（老师 2017 年的"超级立方体"）：
    1. 把 62.5 Mpc/h 的小盒子沿 x/y 复制 expand 圈，做成最大 6000 Mpc/h 的立方体；
    2. 对每个事件：算它的共动距离 R，按半径壳层 [r2, r1) 判断它"属于哪层"；
    3. 壳层内用伯努利抽样：randnum <= MRbh[i][0] 就收下（概率 = 并合率）；
    4. 收下的事件记录 (x, y, z, mBH)，最后画 3D 散点 + 一个扇形天图。

和我们项目 1.3 光锥的关系：同一思想（周期平铺 + 壳层判据 + 概率抽样），
但我们是"洋葱皮红移壳层 + 有测试守护"，老师这是"盒内复制 + 半径判据"。
================================================================================
"""

import numpy as np
from pylab import *
from math import *
import mpl_toolkits.mplot3d

# ---- 容器 ----
Snapnum=[]; R=[] #unit:Mpc/h
X=[]; Y=[]; Z=[]
Rr=[]
xs=[]; ys=[]; zs=[]   # 被选中事件的坐标
ms=[]                 # 被选中事件的黑洞质量
sma_len=62.5          # 小盒边长 Mpc/h
lar_len=6000.0        # 大盒目标边长 Mpc/h
lar=6000
xl=lar; yl=lar; zl=sma_len
c=2.99792458e5 #km/s


def radius(snapnum):
    """快照号 → 共动距离 [Mpc/h]
    radius.txt 里存的是每快照的 (c/H0) 型半径，乘 c/100 换成 Mpc/h"""
    r=radiu[snapnum]*c/100 #Mpc/h for H0/h0=100
    return r

def choose_data(i,xx,yy,zz):
    """收下第 i 个事件的 (xx,yy,zz) 镜像坐标 + 它的黑洞质量"""
    xs.append(xx)
    ys.append(yy)
    zs.append(zz)
    ms.append(MRbh[i][1])   # 黑洞质量（allMRBH 的第 1 列）

def reds(snapnum):#redshift
    redshift=info[snapnum][2]
    return redshift

# ---- 读 4 个文件 ----
lines=open('mMR.dat','r').readlines()          # 星系表
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()     # 快照信息
info=[line.strip().split(',') for line in lines]
lines=open('allMRBH.dat','r').readlines()      # R_za 产物：每行 (并合率, mBH)
MRbh=[line.strip().split(',') for line in lines]
lines=open('radius.txt','r').readlines()       # 每快照的半径表
radi=[line.strip().split(',') for line in lines]
print 'finish reading data'

row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])
    data[i][1]=long(data[i][1])
    data[i][2]=long(data[i][2])
    for j in range(3,9):
        data[i][j]=float(data[i][j])
    for j in range(2):
        MRbh[i][j]=float(MRbh[i][j])   # (并合率, 黑洞质量)

for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

for i in range(len(radi)):
    radi[i]=map(float,radi[i])
radiu=radi[1]     # radius.txt 第 1 行是距离表（每快照一个半径）

#arrange
#data.sort()

h0=info[-1][3] # 最后一个快照的 H(z) ≈ H0 = 0.73 km/s/Mpc
H0=100*h0      # 73 km/s/Mpc

# ---- 每条记录的快照号 + 共动距离 ----
for i in range(len(data)):
    Snapnum.append(data[i][0])
    X.append(data[i][3])
    Y.append(data[i][4])
    Z.append(data[i][5])
    R.append(radius(Snapnum[i]))

# ==============================================================================
# 主循环：周期复制 + 半径壳层 + 伯努利抽样
# ==============================================================================
print 'begin to expand this cube'
for i in range(len(Z)):
    if 0<R[i]<=lar_len:            # 只处理距离在 6 Gpc 以内的事件
        expand=int(R[i]/sma_len)+1 # 需要复制的圈数（半径内能套几个盒）
        for l in range(expand):    # x 方向镜像
            for m in range(expand):# y 方向镜像
                XX=X[i]+l*sma_len  # 镜像坐标 = 原坐标 + 圈数×盒长
                YY=Y[i]+m*sma_len
                ZZ=Z[i]            # z 不复制（光锥沿 z 看，只复制横截面）
                r1=R[i]                        # 内半径：当前快照的距离
                r2=radius(Snapnum[i]+1)       # 外半径：下一快照的距离
                # 壳层判据：镜像到原点距离落在 [r2, r1) —— 注意这里 r2<r1
                # （radius 随快照号增大而减小？取决于 radius.txt 的排布）
                if r1>sqrt(XX**2+YY**2+ZZ**2) >= r2:
                    randnum=np.random.random()
                    # 伯努利抽样：概率 = 并合率。直白说就是"按速率扔硬币"
                    if randnum <=     MRbh[i][0]    :#concrete !!!
                        choose_data(i,XX,YY,ZZ)

print len(xs)   # 选中事件总数

# ----（注释掉的）给选中坐标加盒内随机抖动，避免都落在网格点上 ----
'''
xs=xs+(np.random.rand(len(ys))-0.5)*sma_len
ys=ys+(np.random.rand(len(ys))-0.5)*sma_len
zs=zs+(np.random.rand(len(ys))-0.5)*sma_len
'''

# ==============================================================================
# 绘图部分：3D 散点 + x-y/y-z/z-x 三视图 + 一个扇形天图
# ==============================================================================
def plot3D(x,y,z,sca):
    fig = figure(figsize=[20,20])
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, s=sca,color='black')
    ax.set_xlabel('x(Mpc/h)'); ax.set_ylabel('y(Mpc/h)'); ax.set_zlabel('z(Mpc/h)')
    ax.set_xlim(0,xl); ax.set_ylim(0,yl); ax.set_zlim(0,zl)
    title('GW sources distribution 3D')
    savefig('GWsources3D6000s.png')

def plotxy(x,y,sca):
    figure(figsize=[10,10])
    scatter(x,y,s=sca,color='black')
    title('GW sources distribution x-y')
    xlabel('x(Mpc/h)'); ylabel('y(Mpc/h)')
    xlim(0,xl); ylim(0,yl)
    savefig('GWsourcesxy6000s.png')

def plotyz(y,z,sca):
    figure(figsize=[10,10])
    scatter(y,z,s=sca,color='black')
    title('GW sources distribution y-z')
    xlabel('y(Mpc/h)'); ylabel('z(Mpc/h)')
    xlim(0,yl); ylim(0,zl)
    savefig('GWsourcesyz6000s.png')

def plotzx(z,x,sca):
    figure(figsize=[10,10])
    scatter(z,x,s=sca,color='black')
    title('GW sources distribution z-x')
    xlabel('z(Mpc/h)'); xlabel('x(Mpc/h)')
    xlim(0,zl); ylim(0,xl)
    savefig('GWsourceszx6000s.png')

def transfer(x,y,z):#transfer unit
    """直角坐标 → 球坐标 (r, θ, φ)"""
    r=sqrt(x**2+y**2+z**2)
    theta=atan(sqrt(x**2+y**2)/z)
    phi=atan(y/x)
    return r,theta,phi

# ---- 只保留落在某个天区矩形（θ∈(1.56, π/2], φ∈(π/4, 5π/16]）的事件 ----
# 这个天区对应真实探测器视场（如 HXMT/EP 的监测天区），画"如果望远镜
# 朝这个方向看，能收到多少源"
rs=[]; phis=[]
for i in range(len(zs)):
    Rs,Thetas,Phis=transfer(xs[i],ys[i],zs[i])
    if 1.56<Thetas<=pi/2 and pi/4<Phis<=5*pi/16 :
        rs.append(Rs)
        phis.append(Phis)
print 'Plot'

# ---- 扇形天图（floating_axes：极坐标风格的 RA-径向 图）----
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
import mpl_toolkits.axisartist.angle_helper as angle_helper
from matplotlib.projections import PolarAxes
from mpl_toolkits.axisartist.grid_finder import (FixedLocator, MaxNLocator, DictFormatter)
import matplotlib.pyplot as plt

def setup_axes3(fig, rect):
    """搭建一个 (RA, r) 扇形坐标轴：横轴 RA 范围 π/4–5π/16，纵轴 r 0–6000"""
    tr_rotate = Affine2D().translate(-pi/4, 0)      # 把 RA 原点移到视场中心
    tr = tr_rotate + PolarAxes.PolarTransform()
    grid_locator1 = angle_helper.LocatorHMS(4)      # RA 用时分秒格式
    tick_formatter1 = angle_helper.FormatterHMS()
    grid_locator2 = MaxNLocator(3)                  # r 轴 3 个刻度
    ra0, ra1 = pi/4, 5*pi/16
    cz0, cz1 = 0, 6000
    grid_helper = floating_axes.GridHelperCurveLinear(
        tr, extremes=(ra0, ra1, cz0, cz1),
        grid_locator1=grid_locator1, grid_locator2=grid_locator2,
        tick_formatter1=tick_formatter1, tick_formatter2=None)
    ax1 = floating_axes.FloatingSubplot(fig, rect, grid_helper=grid_helper)
    fig.add_subplot(ax1)
    ax1.axis["left"].set_axis_direction("bottom")
    ax1.axis["right"].set_axis_direction("top")
    ax1.axis["bottom"].set_visible(False)
    ax1.axis["top"].set_axis_direction("bottom")
    ax1.axis["top"].toggle(ticklabels=True, label=True)
    ax1.axis["top"].major_ticklabels.set_axis_direction("top")
    ax1.axis["top"].label.set_text(r"r(Mpc/h)")
    ax1.axis["left"].label.set_text(r"$\phi$")
    aux_ax = ax1.get_aux_axes(tr)
    aux_ax.patch = ax1.patch
    ax1.patch.zorder = 0.9
    return ax1, aux_ax

fig = plt.figure(1, figsize=(9, 3))
fig.subplots_adjust(wspace=0.5, left=0.05, right=0.95)
ax3, aux_ax3 = setup_axes3(fig, 111)
aux_ax3.scatter(phis, rs, s=0.5)     # 扇形天图上的散点
plt.savefig('GWsourcessector6000s.png')

plot3D(xs,ys,zs,ms)   # 点大小 ∝ 黑洞质量
plotxy(xs,ys,ms)
plotyz(ys,zs,ms)
plotzx(zs,xs,ms)


# ==============================================================================
# 【学习笔记】"超级立方体"法的优缺点
# ==============================================================================
# + 简单粗暴有效：62.5 Mpc/h 的盒子瞬间变成 6 Gpc，事件数按半径³ 增长；
# + 伯努利抽样把"连续速率"变成"离散事件目录"，可以直接喂给探测器模拟；
# - 横向复制（x/y）+ 纵向不复制（z）的设定意味着这不是真正的三维周期宇宙，
#   而是"一束光锥"——靠近原点的天区会被人为加密（同一事件多个镜像都中选时）；
# - expand 随半径线性增长，6 Gpc 时每事件要试 ~96²≈9200 个镜像，效率低；
#   我们 1.3 的洋葱皮法只枚举相邻壳层，没有这个开销。
# 这类"历史算法"的价值：理解光锥构建的朴素直觉，再看我们的工程版就知道
# 优化在哪。
# ==============================================================================
