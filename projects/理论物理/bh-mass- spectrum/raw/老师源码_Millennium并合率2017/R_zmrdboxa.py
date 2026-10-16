'''
The Distribution of Merger Rate with Redshift
'''
# data download
#wget -O mMR.csv --http-user=liangcao --http-passwd=HXbivLJG "http://gavo.mpa-garching.mpg.de/MyMillennium?action=doQuery&SQL=select snapnum,galaxyID,lastProgenitorId,x,y,z,stellarMass,metalsStellarMass,sfr from Guo2010a..mMR"
##wget -O snapinfo.csv --http-user=liangcao --http-passwd=HXbivLJG "http://gavo.mpa-garching.mpg.de/MyMillennium?action=doQuery&SQL=select * from snapshots..MR"

import numpy as np
from pylab import *
import math
import mpl_toolkits.mplot3d
#initialization
Snapnum=[]
X=[]
Y=[]
Z=[]
#T=[] #unit:Gyr, lookback time
R=[] #unit:Mpc/h
Rr=[]
Count=[] #count

#coordinates of center
xc=0
yc=0
zc=0
xs=[]
ys=[]
zs=[]
sma_len=62.5 #small length of side, unit:Mpc/h


#read data
lines=open('mMR.dat','r').readlines()
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()#snapnum,a,z,Hz,lookbacktime
info=[line.strip().split(',') for line in lines]
lines=open('allMRBH.txt','r').readlines()#bhMR,mBH
BHMR=[line.strip().split(',') for line in lines]
#print bhMR
#bhMR=map(float,bhMR)
bhMR=[]
#conversion character into real number or int
row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])
    data[i][1]=long(data[i][1])
    data[i][2]=long(data[i][2])
    for j in range(3,9):
        data[i][j]=float(data[i][j])
    bhMR.append(float(BHMR[i][0]))

for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

#arrange
#data.sort()

#define functions
def lbt(snapnum):#lookback time
    t=info[snapnum][4]
    return t #unit: Gyr

def reds(snapnum):#redshift
    redshift=info[snapnum][2]
    return redshift

for i in range(row):
    Snapnum.append(data[i][0])
    #GalaxyID.append(data[i][1])
    #X.append(data[i][3])
    #Y.append(data[i][4])
    #Z.append(data[i][5])
    #StellarMass.append(data[i][6])
    #MetSteMass.append(data[i][7])
    #SFR.append(data[i][8])
    #T.append(lbt(Snapnum[i])) #unit: Gyr
    #R.append(radius(Snapnum[i])) #unit:Mpc/h
    if i>0:
        if Snapnum[i]-Snapnum[i-1]>0:
            Count.append(i) #The total count i of the last one in each group, where each group has the same snapnum
            #Rr.append(R[i-1]) # from snapnum=8 on
        elif Snapnum[i]-Snapnum[i-1]<0:
            print 'Please reorder data!'
Count.append(row)
#Rr.append(R[-1])

#calculate merger rate density
MRD=[]
Redshift=[]
for j in range(1,len(Count)):
    MRS=00
    for i in range(Count[j-1],Count[j]):
        MRS=MRS+bhMR[i]
    mrd=MRS*sma_len**(-3)#unit change
    MRD.append(mrd)
    Redshift.append(reds(Snapnum[i]))

def nor(mrd):#normlization
    return mrd/MRD[-1]*1e-7
print 'R(z=0)=',MRD[-1]
MRD=map(nor,MRD)
'''
#the last one 
def chodata(i,r1,r2,xx,yy,zz):
    distance=sqrt((xx-xc)**2+(yy-yc)**2+(zz-zc)**2)
    if r2<=distance<r1:
        MRS=MRS+bhMR[i]
MRS=0
r1=Rr[-2]
r2=Rr[-1]
for i in range(Count[-2],Count[-1]):
    chodata(i,r1,r2,X[i],Y[i],Z[i])
mrd=MRS*8*3/4.0/math.pi/(r1**3-r2**3)#unit change
MRD.append(mrd)
Redshift.append(reds(Snapnum[i]))
'''
print 'begin saving data'
save=open('MRDa.dat','w')
for i in range(len(MRD)):
    print >> save, Redshift[i], MRD[i]
save.close()

#plot
#another program
    
