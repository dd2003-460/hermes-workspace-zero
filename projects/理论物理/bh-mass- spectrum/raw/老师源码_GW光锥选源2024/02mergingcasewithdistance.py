# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 20:58:02 2024

@author: Qing
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
from collections import defaultdict
######################################
# MS and MS-II both have H0=73km/s/Mpc, Omegam=0.25, OmegaLam=0.75 
#Mon. Not. R. Astron. Soc. 413, 101–131 (2011)

#x,y,z unit: Mpc/h

#black hole mass unit: 10**10 Msun/h

#box size: 62.5 Mpc/h
######################################

c=2.99792458*10**8#m/s
Mpc=3.08568*10**(22)#m
pc=3.08568*10**(16)#m
cMpc=c/Mpc#Mpc/s
ckm=2.99792458*10**5#km/s
OmegaM=0.25
OmegaLam=0.75
n=1#initial spectrum index
h=0.73
Gamma=0.44
H0=100*h#km/s/Mpc
G=6.77*10**(-11)# m^3/(kg*s^2)
Msun=1.989*10**30#kg
GsunMpc=G*Msun/Mpc**3# Mpc^3/(Msun*s^2)


# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)
# 构建文件的绝对路径
file_path = os.path.join(script_dir, '/original data/merging_cases_binary.csv')
#print(file_path)
# Read the CSV file into a pandas DataFrame, skipping the header section
#df = pd.read_csv(file_path)[385:395]
df=pd.read_csv('./original data/merging_cases_binary.csv')
RS = pd.read_csv('./original data/redshifts.csv')

###################共动距离插值函数######################

# 定义共动距离函数的被积函数
def integrand(z):
    return 1 / np.sqrt(OmegaLam + OmegaM * (1 + z)**3)

# 定义共动距离函数
def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return ckm / H0 * integral

# 定义红移范围和步长
z_range = np.arange(0, 12, 0.1)

# 计算函数值
d_c_values = np.array([comoving_distance(z) for z in z_range])

# 构建插值函数
interp_func = interp1d(z_range, d_c_values, kind='linear')

# 提取并排序唯一的红移值列
#unique_redshifts = sorted(df['redshift'].unique())
unique_redshifts = np.array(RS['z'])

# 计算红移对应的共动距离值列表
comoving_distances = interp_func(unique_redshifts)
print(comoving_distances[46])

# 输出红移对应的共动距离值列表
#print(comoving_distances)

#########################################筛选########################################

#comoving_distances=list(range(1739))
#comoving_distances=np.linspace(1, 100,1739)
#print(comoving_distances)

ComovingDistance=[]
ComovingDmax=[]
Redshiftmax=[]
for index, row in df.iterrows():
    ComovingDistance.append(comoving_distance(row['redshift']))
    current_index = int(row['snapnum']-10)
    Redshiftmax.append(unique_redshifts[current_index-1])
    ComovingDmax.append(comoving_distance(unique_redshifts[current_index-1]))
df['comoving_distances']=ComovingDistance
df['Redshiftmax']=Redshiftmax
df['ComovingDmax']=ComovingDmax
print(df)
df.to_csv('./original data/merging_cases_binary_withdistance.csv', index=False)

ampliconst=np.sqrt(32./5.)*(np.pi*10**(-8))**(2./3.)*GsunMpc**(5./3.)/cMpc**4

aaa=ampliconst*(df['blackHoleMass']*10**10)**(5./3.)/df['ComovingDmax']
print(df[aaa>10**(-15.5)])
