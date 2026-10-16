import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
from collections import defaultdict
import sys
import time

######################################
# MS and MS-II both have H0=73km/s/Mpc, Omegam=0.25, OmegaLam=0.75 
#Mon. Not. R. Astron. Soc. 413, 101–131 (2011)

#x,y,z unit: Mpc/h

#black hole mass unit: 10**10 Msun/h

#box size: 62.5 Mpc/h
######################################

RS = pd.read_csv('./original data/redshifts.csv')

#定义并计算参数
c = 2.99792458e5
H_0=73
h=H_0/100
side_length=62.5/h #模拟区域的边长 Mpc
Omegam=0.25
OmegaLam=0.75

###################共动距离插值函数######################

# 定义共动距离函数的被积函数
def integrand(z):
    return 1 / np.sqrt(OmegaLam + Omegam * (1 + z)**3)

# 定义共动距离函数
def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return c / H_0 * integral

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
print(comoving_distances)

# 输出红移对应的共动距离值列表
#print(comoving_distances)


for ii in range(0,36):
    if(ii==0):
        headerchoice=True
    else:
        headerchoice=False
    ########################读取数据############################################
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建文件的绝对路径
    file_path = os.path.join(script_dir, './original data/merging_cases_binary_withdistance.csv')

    # Read the CSV file into a pandas DataFrame, skipping the header section
    #df = pd.read_csv(file_path)[385:395]
    if(ii==35):
        df=pd.read_csv(file_path)[1700:1739]
    else:
        df=pd.read_csv(file_path)[50*ii:50*(ii+1)]
    
    # df2=df[df['blackHoleMass']>0]
    # df3=df2[df2['blackHoleMass']>0]
    # print(df)


    #########################################挑选光锥之内的数据################################################
    def step_func(x):
        return np.array(x>0,dtype=int)

    # 用来存储符合条件的数据的列表
    selected_data = []

    # 循环迭代每个数据点
    for index, row in df.iterrows():
        print(index)
        #print(row['snapnum'])
        #计算内外半径
        redshift=row['redshift']
        inner_radius = row['comoving_distances']  # 当前数据的共动距离
        current_x, current_y, current_z = row['x'], row['y'], row['z']  # 当前数据的坐标
        current_index = int(row['snapnum']-10)
        # outer_radius = comoving_distances[current_index-1]
        outer_radius = row['ComovingDmax']
        # print(inner_radius,outer_radius,row['ComovingDmax'])
        # time.sleep(1)
        #outer_radius = interp_func(redshift+redshift/100000)
        
        # 计算整数范围
        current_quotient = int(outer_radius / side_length)
        integer_range = range(-current_quotient - 1, current_quotient + 1)
        
        # 计算新坐标并检查是否在范围内
        for i in integer_range:  # 迭代整数范围
            for j in integer_range:
                for k in integer_range:
                    if(((step_func(i)+i)**2+(step_func(j)+j)**2+(step_func(k)+k)**2)<(inner_radius/side_length)**2):
                        continue
                    new_x = current_x/h + i * side_length
                    new_y = current_y/h + j * side_length
                    new_z = current_z/h + k * side_length
                    
                    # 计算新坐标到原点的距离
                    new_distance = np.sqrt(new_x**2 + new_y**2 + new_z**2)
                    #确定范围
                    #range_start = comoving_distances[current_index]
                    #range_end = comoving_distances[current_index-1]
                  
                    # 判断新坐标是否在共动距离的范围内
                    if inner_radius <= new_distance <= outer_radius:
                        selected_data.append({
                            'galaxyid_merged': row['galaxyid_merged'],
                            'haloid_merged': row['haloid_merged'],
                            'galaxyid_1': row['galaxyid_1'],
                            'galaxyid_2': row['galaxyid_2'],
                            'redshift': row['redshift'],
                            'snapnum': row['snapnum'],
                            'x_Mpc': new_x,
                            'y_Mpc': new_y,
                            'z_Mpc': new_z,
                            'blackHoleMass': row['blackHoleMass'],
                            'first_progenitor_blackHoleMass': row['first_progenitor_blackHoleMass'],
                            'next_progenitor_blackHoleMass': row['next_progenitor_blackHoleMass'],
                            'comoving_distance': row['comoving_distances'],
                            'Redshiftmax': row['Redshiftmax'],
                            'ComovingDmax': row['ComovingDmax']
                        })

    # 将符合条件的数据转换为新的DataFrame
    selected_df = pd.DataFrame(selected_data)

    # 定义保存文件的完整路径和文件名
    #save_file_path = r'D:\ruanjian\physics\gravitational_wave\gravitational_wave_drawing.csv'

    # 将挑选好的 DataFrame 存储到指定路径的 CSV 文件中
    selected_df.to_csv('./lightcone data/lightcone_events_0512.csv', sep=',', index=False, header=headerchoice, mode='a')


    #######################################释放内存##############################################
    del df
    del selected_df
    del selected_data

    print('1')
