"""
【性质】探索性尝试（已弃用）—— 尝试用角度参数化 (delta_u, delta_v, gamma) 代替笛卡尔分量
【结论】❌ 此路也不通：引入的嵌套根式 (vy 的表达式含开方) 反而让 sympy 更慢

【思路】
PRD 论文原文提到，ORF 结果只依赖4个参数 alpha, gamma, delta_u, delta_v（自由度从5降到3-4个）。
尝试用这个参数化方式减少变量个数：
    u_x = sin(delta_u),  u_z = cos(delta_u)
    v_z = cos(delta_v)
    v_x = (cos(gamma) - cos(delta_u)*cos(delta_v)) / sin(delta_u)
    v_y = sqrt(sin(gamma)^2 - cos(delta_u)^2 - cos(delta_v)^2 + 2cos(gamma)cos(delta_u)cos(delta_v)) / sin(delta_u)

其中 cos(gamma)=u.v, cos(delta_u)=u.s, cos(delta_v)=v.s。

【为什么失败】
v_y 的表达式里带有一个复杂的嵌套根式 sqrt(...)。当这个根式出现在后续的
theta.v, phi.v 等表达式里、再进行乘法/化简时，sympy 需要处理"根式的根式"，
比笛卡尔分量情形下单纯的 sqrt(1-x^2) 复杂得多，实测比笛卡尔分量方式更慢。
"""
import sympy as sp
import time

x, s = sp.symbols('x s', real=True, positive=True)
z = sp.symbols('z')
du, dv, gam = sp.symbols('delta_u delta_v gamma', real=True, positive=True)

ux = sp.sin(du)
uz = sp.cos(du)
vz = sp.cos(dv)
vx = (sp.cos(gam) - sp.cos(du)*sp.cos(dv)) / sp.sin(du)
vy_sq_arg = sp.sin(gam)**2 - sp.cos(du)**2 - sp.cos(dv)**2 + 2*sp.cos(gam)*sp.cos(du)*sp.cos(dv)
vy = sp.sqrt(vy_sq_arg) / sp.sin(du)

if __name__ == "__main__":
    print("参数化设置完成: ux,uz,vx,vy,vz 均已用 delta_u, delta_v, gamma 表示")
    print("vx =", vx)
    print("vy =", vy)
    print("\n(vy 含有嵌套根式，后续大量乘法运算会让sympy处理更慢，此路径最终放弃)")
