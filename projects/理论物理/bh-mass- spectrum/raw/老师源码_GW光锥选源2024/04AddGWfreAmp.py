# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:54:22 2024

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
from generateGWfrequency import *

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

def integrand(z):
    return 1 / np.sqrt(OmegaLam + OmegaM * (1 + z)**3)

# 定义共动距离函数
def comoving_distance(z):
    integral, _ = quad(integrand, 0, z)
    return ckm / H0 * integral

zz=np.linspace(0,5,200)
CoDis=[]
for item in zz:
    CoDis.append(comoving_distance(item))
CoDisReds = interp1d(CoDis, zz, kind='linear')

def GWAmplitude(M1,M2,f,D_L):
    # unit: M_c: M_sun ; f0: Hz; dist:Mpc
    M11=M1
    M22=M2
    Mchirp=(M11*M22)**(3./5.)/(M11+M22)**(1./5.)
    #D_L=dist_L(0,z)/Mpc
    #print(D_L)
    Amp=np.sqrt(32./5)*GsunMpc**(5./3.)*Mchirp**(5./3.)*(np.pi*f)**(2./3)/cMpc**4/D_L
    return Amp

cols=['redshift','snapnum','x_Mpc','y_Mpc','z_Mpc','blackHoleMass','first_progenitor_blackHoleMass',\
      'next_progenitor_blackHoleMass','comoving_distance','Redshiftmax','ComovingDmax']

    
i=0
df=pd.read_csv('./lightcone data/lightcone_events_0512.csv',chunksize=10000,iterator=True,usecols=cols)
for chunk in df:
    i+=1
    if(i==1):
        headerchoice=True
    else:
        headerchoice=False
    frequencytotal=[]
    frequency=[]
    Amplitude=[]
    for index, row in chunk.iterrows():
        print(index)
        M1=row['first_progenitor_blackHoleMass']*10**10/h
        M2=row['next_progenitor_blackHoleMass']*10**10/h
        MM=(M1+M2)
        z=row['redshift']
        x=row['x_Mpc']
        y=row['y_Mpc']
        z=row['z_Mpc']
        CoD=np.sqrt(x**2+y**2+z**2)
        zz=CoDisReds(CoD)
        DL=CoD*(1+zz)
        ff=invF_f(np.random.random(),MM)
        Amp=GWAmplitude(M1,M2,ff,DL)
        #print('f',f)
        frequency.append(ff)
        Amplitude.append(Amp)
        frequencytotal.append({'frequency':ff})
    chunk['frequency']=frequency
    chunk['Amplitude']=Amplitude
    frequencydata = pd.DataFrame(frequencytotal)
    
    #write to files
    chunk.to_csv('./lightcone data/lightcone_events_withfA_01pc_0517.csv',  sep=',', index=False,header=headerchoice, mode='a')
    #frequencydata.to_csv('./lightcone data/lightcone_events_frequencies_0513.csv', sep=',',  index=False,header=headerchoice, mode='a')

    del frequencytotal
    del frequency
    del frequencydata
    del Amplitude
    
     
    # if(i>10):
    #     break;


# print(df)