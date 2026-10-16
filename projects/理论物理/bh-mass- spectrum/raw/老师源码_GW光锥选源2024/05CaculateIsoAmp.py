# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 14:50:15 2024

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
from cosmo_model import *
import time
######################################
# MS and MS-II both have H0=73km/s/Mpc, Omegam=0.25, OmegaLam=0.75 
#Mon. Not. R. Astron. Soc. 413, 101–131 (2011)

#x,y,z unit: Mpc/h

#black hole mass unit: 10**10 Msun/h

#box size: 62.5 Mpc/h
######################################

c=2.99792458*10**8#m/s
Mpc=3.08568*10**(22)#m
cMpc=c/Mpc#Mpc/s
ckm=2.99792458*10**5#km/s
OmegaM=0.25
OmegaLam=0.75
n=1#initial spectrum index
h=0.73
Gamma=0.44
H0=100*h#km/s/Mpc
G=6.67*10**(-11)# m^3/(kg*s^2)
Msun=1.989*10**30#kg
GsunMpc=G*Msun/Mpc**3# Mpc^3/(Msun*s^2)


step=0.3
lens=int((-6-(-9))/step)
amplitudetotal=np.zeros(lens)
eventnumber=np.zeros(lens)
lnfrequency=np.linspace(-9,-6-step,lens)
#print(lnfrequency)
# numberr=[9.2547e+04,1.4740e+04,2.2970e+03,3.5200e+02,5.4000e+01,1.0000e+01]
# plt.bar([1,2,3,4,5,6,7,8,9],[2,5,3,7,1,13,2,6,12])
# plt.bar([1,2,3,4,5,6],[1.04847e+05,4.94300e+03,2.00000e+02,1.00000e+01,0.00000e+00,0.00000e+00])
# plt.bar([-9,-8.7,-8.4,-8.1,-7.8,-7.5],numberr,width=0.2)
# amp=np.array([7.14348116e-34,4.85408252e-32,1.50527533e-30,3.01571479e-29,8.28684525e-29,6.99396227e-29,4.13915715e-29,8.00515142e-30,2.57781428e-30,2.51654550e-31])
# plt.plot(lnfrequency,np.log(np.sqrt(amp/0.3))/np.log(10))
# plt.ylim(-20,-13)
# sys.exit()



df=pd.read_csv('./lightcone data/lightcone_events_withfA_01pc_0517.csv',chunksize=10000,iterator=True)
# df2=pd.read_csv('./withfrequency/selected_events_0408_amp.csv',chunksize=100,iterator=True)
# #chunk = pd.read_csv('./withfrequency/selected_events_0408_amp.csv',header=1,skiprows=range(0, start_row), nrows=end_row - start_row + 1)
# #print(chunk)
# # for chunk in df:
# for (chunk,chunk2) in zip(df,df2):
#     frequency=list(chunk['frequency'].values)
#     print(frequency)
#     print('lalalalalalalalalalala')
#     time.sleep(3)
#     #print(chunk)
#     #print(chunk2)
#     # for (index1,row1,index2,row2) in zip(chunk.iterrows(),chunk2.iterrows()):
#     #     print(index1)

#     #     time.sleep(3)
#     # for (row1,row2) in zip(chunk.iterrows(),chunk2.iterrows()):
#     #     print(row1['redshift'])
#     #     print(row2['redshift'])
#     #     print('lalalalala')
#     #     time.sleep(5)
# sys.exit()
for chunk in df:
    for index, row in chunk.iterrows():
        print(index)
        amp=row['Amplitude']
        # print(amp)
        # time.sleep(2)
        # print(amp)
        z=row['redshift']
        f=row['frequency']/(1+z)
        # z=row['redshift']
        # fobs=f/(1+z)
        lnf=np.log(f)/np.log(10)
        #print(lnf)
        if(-9 < lnf < -6):
            num=int((lnf-(-9))/step)
            amplitudetotal[num]+=amp**2
            eventnumber[num]+=1
# print(amplitudetotal)
print('evenum',eventnumber)
amplitude=np.array(amplitudetotal)
print('amp',amplitude)
plt.plot(lnfrequency,np.log(np.sqrt(amplitude/step))/np.log(10))
#plt.bar([-9,-8.5,-8,-7.5,-7,-6.5],[1.04847e+05,4.94300e+03,2.00000e+02,1.00000e+01,0.00000e+00,0.00000e+00])




'''
evenum [1.4554494e+07 1.7529045e+07 1.0277891e+07 3.7433240e+06 8.2532900e+05
 1.3870800e+05 2.1717000e+04 3.5050000e+03 5.4200000e+02 7.3000000e+01]
amp [7.14348116e-34 4.85408252e-32 1.50527533e-30 3.01571479e-29
 8.28684525e-29 6.99396227e-29 4.13915715e-29 8.00515142e-30
 2.57781428e-30 2.51654550e-31]

'''

'''
#start frequency:10**(-9)
evenum [6.30153e+06 9.98413e+05 1.58319e+05 2.49500e+04 3.96700e+03 6.51000e+02
 9.60000e+01 1.70000e+01 9.00000e+00 1.00000e+00]
amp [2.16612490e-30 7.95850744e-31 6.70102583e-31 9.45370913e-32
 3.79617317e-32 8.41306727e-33 9.34508464e-33 8.97992397e-34
 1.33815796e-34 1.71804942e-37]
'''

# amp=np.array([7.14348116e-34,4.85408252e-32,1.50527533e-30,3.01571479e-29,8.28684525e-29,6.99396227e-29,4.13915715e-29,8.00515142e-30,2.57781428e-30,2.51654550e-31])
# plt.plot(lnfrequency,np.log(np.sqrt(amp/0.3))/np.log(10))
# plt.scatter(np.log(3.17098*10**(-8))/np.log(10),np.log(6.4*10**(-15))/np.log(10))

# numberr=[6.30153e+06,9.98413e+05,1.58319e+05,2.49500e+04,3.96700e+03,6.51000e+02,9.60000e+01,1.70000e+01,9.00000e+00,1.00000e+00]
# amp=np.array([2.16612490e-30,7.95850744e-31,6.70102583e-31,9.45370913e-32,3.79617317e-32,8.41306727e-33,9.34508464e-33,8.97992397e-34,1.33815796e-34,1.71804942e-37])
# plt.plot(lnfrequency,np.log(np.sqrt(amp/0.3))/np.log(10))
# plt.scatter(np.log(3.17098*10**(-8))/np.log(10),np.log(6.4*10**(-15))/np.log(10))
# # plt.bar(lnfrequency,numberr,width=0.2,dpi=300)
# print(10**(-15.5))










