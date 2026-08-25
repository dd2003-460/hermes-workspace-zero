"""
不用 factor()，改用 collect() 按 x 的幂次分组打印，
再肉眼/正则寻找是否有 (1+x)^k 或 (uz+x) 这类因子的规律。
"""
import sympy as sp
import pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)
num = d['num']

collected = sp.collect(num, x)
print("按 x 收集后的多项式:")
sp.pprint(collected)

# 换一种思路：直接代入具体数值，看看能不能识别出简单的封闭形式
# 用 gamma = angle(u,v), delta_u = angle(u,s), delta_v = angle(v,s) 的组合猜测
print("\n\n数值验证：随机取几组 (ux,uz,vx,vy,vz满足单位模长)，")
print("计算 num 的数值，与猜测形式比较")

import random, cmath
random.seed(1)

def rand_unit_2d():
    theta = random.uniform(0,6.28)
    return sp.cos(theta), sp.sin(theta)  # not used directly, keep symbolic-free numeric below

import numpy as np
for trial in range(3):
    duv = random.uniform(0.3, 2.8)   # delta_u
    UX, UZ = np.sin(duv), np.cos(duv)
    vvec = np.random.normal(size=3); vvec/=np.linalg.norm(vvec)
    VX,VY,VZ = vvec
    xv = random.uniform(-0.8,0.8)
    val = num.subs({ux:UX, uz:UZ, vx:VX, vy:VY, vz:VZ, x:xv})
    val = complex(val.evalf())
    print(f"trial {trial}: delta_u={duv:.3f}  v=({VX:.3f},{VY:.3f},{VZ:.3f})  x={xv:.3f}  num={val:.6g}")
