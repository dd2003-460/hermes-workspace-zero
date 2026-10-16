'''
The Distribution of Merger Rate with Redshift
2017.7.25 a modify
change mBH=30 into the distribution of mBH
7.26 add mBH output
'''
# data download
#wget -O mMR.csv --http-user=liangcao --http-passwd=HXbivLJG "http://gavo.mpa-garching.mpg.de/MyMillennium?action=doQuery&SQL=select snapnum,galaxyID,lastProgenitorId,x,y,z,stellarMass,metalsStellarMass,sfr from Guo2010a..mMR"
##wget -O snapinfo.csv --http-user=liangcao --http-passwd=HXbivLJG "http://gavo.mpa-garching.mpg.de/MyMillennium?action=doQuery&SQL=select * from snapshots..MR"
#import sys, time
#import pp
import numpy as np


#initialization
T=[] #unit:Gyr, lookback time
StellarMass=[]
MetSteMass=[]
Count=[] #count
#read data
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

#define functions 
def lbt(snapnum):#lookback time
    t=info[snapnum][4]
    return t #unit: Gyr

def imfbh(metalsStellarMass,stellarMass):# m is stellar mass(), metal means metalicity
    #constant definition
    #mSun=2.0e33
    metalSun=0.0134
    A=0.3
    beta=0.8
    gamma=0.2
    if stellarMass==0:
        phi=0
        mBH=0
    else:
        metal=metalsStellarMass/stellarMass
        cons=40*(((metal/0.01/metalSun)**gamma+1)/40.0/A)**(1/(beta+1)) #a complex constant
        phi0=-1.35*cons**1.35/(100**(-1.35/(beta+1))-3**(-1.35/(beta+1))) # IMF constant
        ran=np.random.rand() # a random number on [0,1]
        mBH=(3**(-1.35/(beta+1))-1.35*ran*cons**1.35/phi0)**(-(beta+1)/1.35) # in the unit of solar mass
        m=cons*mBH**(1/(beta+1))# unit as Msun
        phi=phi0*m**(-2.35)
    return phi,mBH

def cycle(i):
    ob_id=data[i][1] #galaxyID
    ob_lpid=data[i][2] #lastProgenitorId
    snap=data[i][0]
    mergerRate=0
    num1=Count[snap-snap0-1] #num1 is total count i of all data whose Snapnum[i]<snap
    for j in range(num1):#only progenitor galaxies
        if ob_id < data[j][1] <= ob_lpid:
            mergerRate=mergerRate+data[j][8]*IMFbh[j][0]*(1/(T[j]-lbt(snap)))*(T[j]-lbt(data[j][0]+1))# SFR*IMF*1/t_d*dt_d
    return mergerRate, IMFbh[i][1]#(merger rate, mass of BH)

for i in range(row):
    StellarMass.append(data[i][6])
    MetSteMass.append(data[i][7])
    T.append(lbt(data[i][0])) #unit: Gyr
    if i>0:
        if data[i][0]-data[i-1][0]>0:
            Count.append(i) #The total count i of the last one in each group, where each group has the same snapnum
        elif data[i][0]-data[i-1][0]<0:
            print 'Please reorder data!'
Count.append(row)
snap0=data[0][0]

#print 'calculate IMF'
IMFbh=map(imfbh,MetSteMass,StellarMass) #[list(tuple)]
'''
bhMR=[(0,0) for i in range(2)] #merger rate

bhMR.extend(map(cycle,range(Count[0],100001))) 
print 'save data'
np.savetxt('allMRBH01.txt',bhMR,delimiter=',')
'''
number=100000
bhMR=[] #merger rate
nn=21
bhMR.extend(map(cycle,range((nn-1)*number,row))) 
print 'save data'
np.savetxt('allMRBH'+str(nn)+'.txt',bhMR,delimiter=',')

