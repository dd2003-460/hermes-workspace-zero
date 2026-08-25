import sympy as sp
import time, pickle

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)
vx, vy, vz = sp.symbols('v_x v_y v_z', real=True)

with open('/home/user/chiral_orf_calc/numV_z1_reduced.pkl','rb') as f:
    d = pickle.load(f)

num, den = d['num'], d['den']

t0=time.time()
num_factored = sp.factor(num)
print("factor(num) done:", time.time()-t0)
print(num_factored)
