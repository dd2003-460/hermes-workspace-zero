# -*- coding: utf-8 -*-
"""
================================================================================
【注释学习版】R_zanp.py —— Millennium 黑洞并合率计算（单机主力版）
================================================================================
原始文件：raw/老师源码_Millennium并合率2017/R_zanp.py（原样未改，本文件只加注释）

⚠️ 这是 Python 2 代码，原样跑不了 Python 3。三处要改：
    print 'xxx'  → print('xxx')
    long(...)    → int(...)
    map(f, a, b) → 列表已耗尽，要 list(map(...)) 或 [f(x,y) for x,y in zip(a,b)]

流水线位置（第一组 7 个文件的分工）：
    R_zanp.py       本文件：算每个星系的"推前并合率" + 黑洞质量 → allMRBHn.txt
    R_za.py         同一逻辑的多进程版（用 pp 库，2017 年的并行方案）
    R_zanpN.py      分块版（nn=21 表示第 21 块，21 个进程手工并行）
    R_zanps.py      又一个变体
    R_zmrdboxa.py   下游：把 allMRBH*.txt 按红移加成并合率密度
    superGW6e3.py   下游：把并合率事件撒进 6 Gpc 大盒子并画图
    m_BH_m_ZAMS.py  物理核心的替代实现（Spera 附录 C），见单独注释版

================================================================================
"""

# ==============================================================================
# 数据下载（代码里注释掉的 wget，来自 Millennium 模拟的公开 SQL 接口）
# ==============================================================================
# wget -O mMR.csv "http://gavo.mpa-garching.mpg.de/MyMillennium?...
#   select snapnum,galaxyID,lastProgenitorId,x,y,z,stellarMass,metalsStellarMass,sfr
#   from Guo2010a..mMR"
# wget -O snapinfo.csv "...select * from snapshots..MR"
#
# 两个输入文件（放在脚本同目录）：
#   mMR.dat      每行一个"星系×快照"记录，空格分隔：
#                 [0]snapnum [1]galaxyID [2]lastProgenitorId [3]x [4]y [5]z
#                 [6]stellarMass [7]metalsStellarMass [8]sfr
#   snapinfo.csv 每行一个快照的宇宙学信息，逗号分隔：
#                 [0]snapnum [1]a(尺度因子) [2]z(红移) [3]H(z) [4]lookbacktime
#
# 关键字段解释：
#   lastProgenitorId —— "最后一代祖宗 ID"。Millennium 的星系有 ID 编号规则：
#       一个星系的所有祖宗 ID 都落在 (galaxyID, lastProgenitorId] 区间里。
#       所以"ob_id < data[j][1] <= ob_lpid"就是"j 是 i 的祖宗"的判据。
#   metalsStellarMass / stellarMass —— 金属丰度不是现成字段，是这两个相除现算。

import numpy as np

# ==============================================================================
# 初始化三个全局列表（2017 年风格：全局变量满天飞，读代码时跟着数据流走就行）
# ==============================================================================
T=[] #unit:Gyr, lookback time —— 每条记录所在快照的回顾时间
StellarMass=[]   # 每条记录的恒星质量
MetSteMass=[]    # 每条记录的"锁在恒星里的金属质量"
Count=[] #count  —— 每个快照组的最后一条记录的下标（"组边界"数组）

# ---- 读 mMR.dat：把文本切成二维列表，再逐列转成数字 ----
lines=open('mMR.dat','r').readlines()
data=[line.strip().split(' ') for line in lines]
# ---- 读 snapinfo.csv ----
lines=open('snapinfo.csv','r').readlines()#snapnum,a,z,Hz,lookbacktime
info=[line.strip().split(',') for line in lines]

# ---- 类型转换：前 3 列是整数（快照号+两个 ID），后 6 列是浮点 ----
row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])       # snapnum
    data[i][1]=long(data[i][1])      # galaxyID（Millennium 的 ID 很大，py2 要 long）
    data[i][2]=long(data[i][2])      # lastProgenitorId
    for j in range(3,9):             # x,y,z,stellarMass,metalsStellarMass,sfr
        data[i][j]=float(data[i][j])
for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

# ==============================================================================
# 函数定义
# ==============================================================================
def lbt(snapnum):#lookback time
    """回顾时间查找： info[snapnum][4] 是第 snapnum 号快照距今天多久（Gyr） """
    t=info[snapnum][4]
    return t #unit: Gyr

def imfbh(metalsStellarMass,stellarMass):# m is stellar mass(), metal means metalicity
    """
    ★ 物理核心函数 1/2：IMF 采样 ★
    输入一个星系的（锁在恒星里的金属质量, 恒星质量），返回：
        phi —— 抽中的前身星在 IMF 上的密度值（作为并合率权重）
        mBH —— 抽中的黑洞质量（M☉）

    直白说：**按这个星系的金属丰度，从 IMF 里随机抽一颗恒星，把它当作黑洞前身星**。
    """
    #constant definition
    metalSun=0.0134   # 太阳金属丰度（质量分数）。注意：这是 Asplund 老值，
                      # 我们项目用 0.02（Spera 口径）——两套约定不能混
    A=0.3             # IMF 归一化尺度参数
    beta=0.8          # IMF 高质端幂指数 β（dN/dm ∝ m^-β，此处高质端斜率 -2.35 由
                      # 1.35/(β+1)=0.75 与低质端拼成，见下）
    gamma=0.2         # 金属丰度影响强度

    if stellarMass==0:
        phi=0
        mBH=0          # 没恒星就没黑洞，直接返回 0
    else:
        # ---- 第 1 步：算金属丰度（质量分数）----
        metal=metalsStellarMass/stellarMass
        # ---- 第 2 步：造"随金属丰度变形"的 IMF ----
        # cons 是一个复合常数：金属越多 → cons 越大 → IMF 转折质量越高。
        # 直白说：**金属多的环境倾向于产生更大质量的恒星**（这是简化假设，
        # 我们项目的决策是 IMF 不随 Z 变，见 discussion_core.md "Z 两入口"）。
        cons=40*(((metal/0.01/metalSun)**gamma+1)/40.0/A)**(1/(beta+1))
        # ---- 第 3 步：IMF 归一化常数 ----
        # 强制 IMF 在 3–100 M☉ 区间积分为 1 来定 phi0：
        # ∫φ0·m^-2.35 dm 从 3 到 100 = 1 → phi0 = 1.35 / (100^(-0.75) - 3^(-0.75)) / cons^1.35
        # （代码用等价代数形式写出）
        phi0=-1.35*cons**1.35/(100**(-1.35/(beta+1))-3**(-1.35/(beta+1)))
        # ---- 第 4 步：逆 CDF 采样抽一颗恒星 ----
        # ran ∈ [0,1] 是累计概率；解 "ran = ∫φ dm 从 3 到 m" 反解出 m——
        # 这就是"从 IMF 抽质量"的标准做法（逆变换采样）。
        ran=np.random.rand()
        mBH=(3**(-1.35/(beta+1))-1.35*ran*cons**1.35/phi0)**(-(beta+1)/1.35)
        # ---- 第 5 步：把抽中的质量代回 IMF 得密度权重 ----
        m=cons*mBH**(1/(beta+1))# unit as Msun
        phi=phi0*m**(-2.35)
    return phi,mBH

def cycle(i):
    """
    ★ 物理核心函数 2/2：对第 i 条记录算"推前并合率" ★
    模型（直白版）：
        目标星系 i 在今天的质量，是它所有祖宗历代"生娃"攒出来的。
        假设每颗祖宗星系生下的黑洞前身星**全部在目标时刻并合**（零延时），
        那么 i 在时刻 t_snap 的并合率 = Σ_祖宗j [ SFR_j × IMF_j × 1/Δt_j × Δt_j ]
        其中 Δt_j 是祖宗 j 存在的时间段，1/Δt 把"这段时间攒的前身星数"
        摊成"单位时间的并合率"。
    """
    ob_id=data[i][1] #galaxyID —— 目标星系
    ob_lpid=data[i][2] #lastProgenitorId —— 目标星系的最后祖宗 ID
    snap=data[i][0]    # 目标快照
    mergerRate=0
    # num1 = 快照编号小于 snap 的所有记录的条数。
    # Count[snap-snap0-1] 是"snap 之前那个组的最后一条下标"——
    # 因为数据按快照排序，snap 之前的记录全是潜在祖宗。
    num1=Count[snap-snap0-1]
    for j in range(num1):#only progenitor galaxies —— 只遍历祖宗区
        # ID 区间判据：data[j][1] ∈ (ob_id, ob_lpid] → j 是 i 的祖宗
        if ob_id < data[j][1] <= ob_lpid:
            # SFR_j × IMF_j × (1/Δt) × Δt：
            #   data[j][8]          = SFR_j（每年新形成的恒星质量）
            #   IMFbh[j][0]         = IMF 权重（前身星数密度）
            #   1/(T[j]-lbt(snap))  = 摊到单位时间
            #   (T[j]-lbt(data[j][0]+1)) = 祖宗 j 存活时长
            # ★ 注意这里用的是 SFR 不是 stellarMass——和我们项目的硬性禁令一致：
            #   诞生率必须用"率"，不能用"存量"。
            mergerRate=mergerRate+data[j][8]*IMFbh[j][0]*(1/(T[j]-lbt(snap)))*(T[j]-lbt(data[j][0]+1))
    return mergerRate, IMFbh[i][1]#(merger rate, mass of BH)

# ==============================================================================
# 主流程
# ==============================================================================
# 先扫一遍全表：填 T（回顾时间）、StellarMass、MetSteMass，
# 同时检测快照边界填 Count 数组
for i in range(row):
    StellarMass.append(data[i][6])
    MetSteMass.append(data[i][7])
    T.append(lbt(data[i][0])) #unit: Gyr
    if i>0:
        if data[i][0]-data[i][0-1]>0:      # 快照号跳增 → 新组边界
            Count.append(i)
        elif data[i][0]-data[i][0-1]<0:    # 快照号回退 → 数据没排序，报警
            print 'Please reorder data!'
Count.append(row)   # 最后一组边界 = 总行数
snap0=data[0][0]    # 最小快照号（Count 数组的基准）

# 对每条记录抽一次 IMF/mBH（向量化前先算好，避免 cycle 里重复抽）
IMFbh=map(imfbh,MetSteMass,StellarMass) #[list(tuple)]

# ---- 分块算并合率（每块 5 万条，41 块覆盖 200 万条）----
bhMR=[(0,0) for i in range(2)] #merger rate
Number=[Count[0]]                                   # 第一块起点
Number.extend(range(50000,2000001,50000))           # 中间块起点：5万,10万,...,200万
Number.append(row)                                  # 最后一块起点
for i in range(41):
    bhMR.extend(map(cycle,range(Number[i],Number[i+1])))

# ---- 落盘：每行 (mergerRate, mBH)，逗号分隔 ----
print 'save data'
np.savetxt('allMRBHn.txt',bhMR,delimiter=',')

# ==============================================================================
# 【学习笔记】这个脚本的"现代等价物"就是我们项目的 4.1 推前
# ==============================================================================
# 老师的做法（2017）：
#     星系树 → 祖宗区遍历 → SFR×IMF 摊时间 → 并合率
#     假设：零延时、IMF 随 Z 变形、单颗前身星
#
# 我们项目的做法（2026，4.1_Pushforward_Inference）：
#     同样的输入（SFR 场 + 位置），但：
#     - IMF 固定 Salpeter（不随 Z 变形）；
#     - 遗迹质量走 Spera 附录 C 全轨迹（不是 IMF 里抽一颗）；
#     - "非单调映射的所有分支都要加"（Jensen 敏感性守护）；
#     - 有 MW 标定点（Ṽ_BH = 4.547182e-3 /yr）和 41 项测试守护。
#     结果：更严格、可复现、有误差预算；代价是丢了老师那种"快糙猛"。
#
# 学习建议：把 cycle() 的求和式和 4.1 的推前公式并排看，
# 能看懂"半解析"是怎么变成"概率推前"的。
# ==============================================================================
