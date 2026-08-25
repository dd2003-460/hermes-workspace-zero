"""
用韦达定理简化 z1-z2，避免直接对含sqrt的z1,z2做符号代入的组合爆炸。

从 2z(1+n.u) = ux*s*z^2 + 2(uz*x+1)*z + ux*s = ux*s*(z-z1)(z-z2)
得到: z1+z2 = -2(uz*x+1)/(ux*s),  z1*z2 = 1

(z1-z2)^2 = (z1+z2)^2 - 4*z1*z2 
用 ux^2=1-uz^2, s^2=1-x^2 化简，验证是否等于 [2(x+uz)/(ux*s)]^2
"""
import sympy as sp

x, s = sp.symbols('x s', real=True, positive=True)
ux, uz = sp.symbols('u_x u_z', real=True)

sum_z12 = -2*(uz*x+1)/(ux*s)
prod_z12 = sp.Integer(1)

diff_sq = sp.expand(sum_z12**2 - 4*prod_z12)
# 代入约束 ux^2 = 1-uz^2, s^2 = 1-x^2
diff_sq_sub = diff_sq.subs(ux**2, 1-uz**2)  # 可能不会自动匹配，需要手动处理
print("diff_sq (未代入约束) =", diff_sq)

# 手动构造: diff_sq = 4*(uz*x+1)^2/(ux^2*s^2) - 4
target = sp.together(diff_sq)
num, den = sp.fraction(target)
num = sp.expand(num)
print("\nnum =", num)
print("den =", den)

# 用约束 ux^2 = 1-uz^2 替换 den 中的 ux^2 (den应含 ux^2*s^2)
den_sub = den.subs(ux**2, 1-uz**2)
print("den (代入 ux^2=1-uz^2 后) =", den_sub)

# 用约束化简 num: num = 4(uz x+1)^2 - 4*ux^2*s^2, 代入 ux^2=1-uz^2, s^2=1-x^2
num_sub = num.subs(ux**2, 1-uz**2).subs(s**2, 1-x**2)
num_sub = sp.expand(num_sub)
print("num (代入约束后) =", num_sub)

target_x_plus_uz_sq = sp.expand(4*(x+uz)**2)
print("\n4*(x+uz)^2 =", target_x_plus_uz_sq)
print("num_sub - 4*(x+uz)^2 == 0 ?", sp.simplify(num_sub - target_x_plus_uz_sq) == 0)
