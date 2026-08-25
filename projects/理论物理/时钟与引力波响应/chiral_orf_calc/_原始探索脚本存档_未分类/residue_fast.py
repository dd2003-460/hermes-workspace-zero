"""
用留数公式 Res_{z=zk} P(z)/Q(z) = P(zk)/Q'(zk)  (对单极点,Q'(zk)!=0情形)
分别代入5个极点求 R_0^V ... R_4^V
"""
import sympy as sp
import pickle
import time

with open('/home/user/chiral_orf_calc/fast_data.pkl','rb') as f:
    d = pickle.load(f)

x, s, z = d['x'], d['s'], d['z']
ux, uz, vx, vy, vz = d['ux'], d['uz'], d['vx'], d['vy'], d['vz']
num_fV, den_fV = d['num_fV'], d['den_fV']

Qz = sp.diff(den_fV, z)

# 5个极点 (s 代表 sqrt(1-x^2))
z0 = sp.Integer(0)
z1 = -(1+uz)*(1+x) / (ux*s)
z2 = -(1-uz)*(1-x) / (ux*s)
z3 = -(1+vz)*(1+x) / ((vx + sp.I*vy)*s)
z4 = -(1-vz)*(1-x) / ((vx + sp.I*vy)*s)

poles = {'0': z0, '1': z1, '2': z2, '3': z3, '4': z4}

residues = {}
for name, zk in poles.items():
    t0 = time.time()
    Pk = num_fV.subs(z, zk)
    Qk = Qz.subs(z, zk)
    res = Pk/Qk
    res = sp.together(res)
    t1 = time.time()
    print(f"R^V_{name} 原始表达式生成完毕，用时 {t1-t0:.2f}s，开始化简...")
    res_simpl = sp.simplify(res)
    t2 = time.time()
    print(f"  化简完成，用时 {t2-t1:.2f}s")
    residues[name] = res_simpl
    print(f"R^V_{name} =")
    sp.pprint(res_simpl)
    print()

with open('/home/user/chiral_orf_calc/residues_final.pkl','wb') as fp:
    pickle.dump(residues, fp)
