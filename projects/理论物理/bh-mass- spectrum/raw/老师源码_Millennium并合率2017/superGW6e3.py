'''
rewrite by numpy array, the fastest except plot
'''
import numpy as np
from pylab import *
from math import *
import mpl_toolkits.mplot3d
#initialization
#Count=[]
Snapnum=[]
R=[] #unit:Mpc/h
X=[]
Y=[]
Z=[]
Rr=[]
#sca=1
#coordinates of center

xs=[]
ys=[]
zs=[]
ms=[]
sma_len=62.5 #small length of side, unit:Mpc/h
lar_len=6000.0  #large length of side, unit:Mpc/h
lar=6000
xl=lar
yl=lar
zl=sma_len
c=2.99792458e5 #km/s
#define functions
'''
def Hubble(z):
    h0=0.73
    OmegaL=0.75
    Omegam=0.25
    h=h0*(OmegaL+Omegam*(1+z)**3)**0.5
    return h
'''

def radius(snapnum):
    r=radiu[snapnum]*c/100 #Mpc/h for H0/h0=100
    return r #unit:Mpc/h

def choose_data(i,xx,yy,zz):# redshift,xx, yy, zz are numbers, not lists
    xs.append(xx)#xs,ys,zs choose out all data
    ys.append(yy)
    zs.append(zz)
    ms.append(MRbh[i][1])

def reds(snapnum):#redshift
    redshift=info[snapnum][2]
    return redshift

#read data
lines=open('mMR.dat','r').readlines()
data=[line.strip().split(' ') for line in lines]
lines=open('snapinfo.csv','r').readlines()#snapnum,a,z,Hz,lookbacktime
info=[line.strip().split(',') for line in lines]
lines=open('allMRBH.dat','r').readlines() #all merger rate !!!
MRbh=[line.strip().split(',') for line in lines]
lines=open('radius.txt','r').readlines() 
radi=[line.strip().split(',') for line in lines]
print 'finish reading data'
#conversion character into real number
row=len(data)
for i in range(row):
    data[i][0]=int(data[i][0])
    data[i][1]=long(data[i][1])
    data[i][2]=long(data[i][2])
    for j in range(3,9):
        data[i][j]=float(data[i][j])
    for j in range(2):
        MRbh[i][j]=float(MRbh[i][j])

for i in range(len(info)):
    info[i][0]=int(info[i][0])
    for j in range(1,5):
        info[i][j]=float(info[i][j])

for i in range(len(radi)):
    radi[i]=map(float,radi[i])
radiu=radi[1]

#arrange
#data.sort()

h0=info[-1][3] #0.73km/s/Mpc
H0=100*h0 #73km/s/Mpc

for i in range(len(data)):
    Snapnum.append(data[i][0])
    X.append(data[i][3])
    Y.append(data[i][4])
    Z.append(data[i][5])
    R.append(radius(Snapnum[i]))

print 'begin to expand this cube'
#copy this cube and expand it
'''
def prob(redshift):
    p=0
    for i in range(len(MRDz)):
        if abs(redshift-MRDz[i][0])<1e-3:
            p=MRD[i]#*sma_len**3*5 #5yr
    return p
'''
for i in range(len(Z)):
    if 0<R[i]<=lar_len:
        expand=int(R[i]/sma_len)+1#save many cycles
        for l in range(expand):
            for m in range(expand):
                XX=X[i]+l*sma_len
                YY=Y[i]+m*sma_len
                ZZ=Z[i]
                #print i                    
                r1=R[i]
                r2=radius(Snapnum[i]+1)
                if r1>sqrt(XX**2+YY**2+ZZ**2) >= r2:
                    randnum=np.random.random() 
                    #print randnum
                    if randnum <=     MRbh[i][0]    :#concrete !!!
                        choose_data(i,XX,YY,ZZ)
print len(xs)
'''
xs=xs+(np.random.rand(len(ys))-0.5)*sma_len
ys=ys+(np.random.rand(len(ys))-0.5)*sma_len
zs=zs+(np.random.rand(len(ys))-0.5)*sma_len
'''
#define plot function
def plot3D(x,y,z,sca):
    fig = figure(figsize=[20,20])
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, s=sca,color='black')
    ax.set_xlabel('x(Mpc/h)')
    ax.set_ylabel('y(Mpc/h)')
    ax.set_zlabel('z(Mpc/h)')
    ax.set_xlim(0,xl)
    ax.set_ylim(0,yl)
    ax.set_zlim(0,zl)
    title('GW sources distribution 3D')
    savefig('GWsources3D6000s.png')

def plotxy(x,y,sca):
    figure(figsize=[10,10])
    scatter(x,y,s=sca,color='black')
    title('GW sources distribution x-y')
    xlabel('x(Mpc/h)')
    ylabel('y(Mpc/h)')
    xlim(0,xl)
    ylim(0,yl)
    savefig('GWsourcesxy6000s.png')

def plotyz(y,z,sca):
    figure(figsize=[10,10])
    scatter(y,z,s=sca,color='black')
    title('GW sources distribution y-z')
    xlabel('y(Mpc/h)')
    ylabel('z(Mpc/h)')
    xlim(0,yl)
    ylim(0,zl)
    savefig('GWsourcesyz6000s.png')

def plotzx(z,x,sca):
    figure(figsize=[10,10])
    scatter(z,x,s=sca,color='black')
    title('GW sources distribution z-x')
    xlabel('z(Mpc/h)')
    ylabel('x(Mpc/h)')
    xlim(0,zl)
    ylim(0,xl)
    savefig('GWsourceszx6000s.png')

def transfer(x,y,z):#transfer unit
    r=sqrt(x**2+y**2+z**2)
    theta=atan(sqrt(x**2+y**2)/z)
    phi=atan(y/x)
    return r,theta,phi


rs=[]
phis=[]
for i in range(len(zs)):
    Rs,Thetas,Phis=transfer(xs[i],ys[i],zs[i])
    if 1.56<Thetas<=pi/2 and pi/4<Phis<=5*pi/16 :
        rs.append(Rs)
        phis.append(Phis)
print 'Plot'
#########################################################
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
import mpl_toolkits.axisartist.angle_helper as angle_helper
from matplotlib.projections import PolarAxes
from mpl_toolkits.axisartist.grid_finder import (FixedLocator, MaxNLocator,
                                                 DictFormatter)
import matplotlib.pyplot as plt

def setup_axes3(fig, rect):
    """
    Sometimes, things like axis_direction need to be adjusted.
    """

    # rotate a bit for better orientation
    tr_rotate = Affine2D().translate(-pi/4, 0)

    # scale degree to radians
    #tr_scale = Affine2D().scale(np.pi/180., 1.)

    tr = tr_rotate + PolarAxes.PolarTransform()

    grid_locator1 = angle_helper.LocatorHMS(4)
    tick_formatter1 = angle_helper.FormatterHMS()

    grid_locator2 = MaxNLocator(3)
    #ra0, ra1 = 0, pi/16
    ra0, ra1 = pi/4, 5*pi/16
    cz0, cz1 = 0, 6000
    grid_helper = floating_axes.GridHelperCurveLinear(
        tr, extremes=(ra0, ra1, cz0, cz1),
        grid_locator1=grid_locator1,
        grid_locator2=grid_locator2,
        tick_formatter1=tick_formatter1,
        tick_formatter2=None)

    ax1 = floating_axes.FloatingSubplot(fig, rect, grid_helper=grid_helper)
    fig.add_subplot(ax1)

    # adjust axis
    ax1.axis["left"].set_axis_direction("bottom")
    ax1.axis["right"].set_axis_direction("top")

    ax1.axis["bottom"].set_visible(False)
    ax1.axis["top"].set_axis_direction("bottom")
    ax1.axis["top"].toggle(ticklabels=True, label=True)
    ax1.axis["top"].major_ticklabels.set_axis_direction("top")
    ax1.axis["top"].label.set_axis_direction("top")

    ax1.axis["left"].label.set_text(r"r(Mpc/h)")
    ax1.axis["top"].label.set_text(r"$\phi$")

    # create a parasite axes whose transData in RA, cz
    aux_ax = ax1.get_aux_axes(tr)

    aux_ax.patch = ax1.patch  # for aux_ax to have a clip path as in ax
    ax1.patch.zorder = 0.9  # but this has a side effect that the patch is
    # drawn twice, and possibly over some other
    # artists. So, we decrease the zorder a bit to
    # prevent this.

    return ax1, aux_ax


##########################################################
fig = plt.figure(1, figsize=(9, 3))
fig.subplots_adjust(wspace=0.5, left=0.05, right=0.95)

ax3, aux_ax3 = setup_axes3(fig, 111)


aux_ax3.scatter(phis, rs, s=0.5)

plt.savefig('GWsourcessector6000s.png')

plot3D(xs,ys,zs,ms)
plotxy(xs,ys,ms)
plotyz(ys,zs,ms)
plotzx(zs,xs,ms)

