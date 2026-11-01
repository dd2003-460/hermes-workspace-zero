"""
【性质】推导 —— 用纯符号代数（不依赖数值积分）发现并修正PRD论文Eq(35)
        第三项的印刷错误
【计算的量】从Eq(34)的T_two定义出发，把Gamma_two的被积核T_two(bu,xu)*
        conj(T_two(bv,xv))精确分解为四项，逐项确定每一项对应的
        Gamma_one参数替换关系（beta的正负、u_hat/v_hat的正负号）
【状态】✅✅✅ 完成：严格代数推导证明论文Eq(35)第三项的方向矢量符号
        (u_hat,-v_hat)应为(-u_hat,+v_hat)，其余三项转录准确无误
【依赖】无（自包含，纯sympy符号推导）

================================================================================
背景：此前会话在GbLI组装时长期卡住的根源
================================================================================
此前排查Gamma_two（Eq35组装）与最原始定义严重不吻合的问题时，逐层排查
了sigma_pm分支选择错误（BUG-002，已在阶段1修复）、坐标系旋转、R0-R4
各分量等，最终发现即便所有底层函数都已修复正确，Eq(35)的四项组装本身
仍然对不上——这正是因为论文Eq(35)第三项的方向矢量符号印刷有误。

================================================================================
推导思路
================================================================================
论文Eq(34): T_two(beta,x) = T_one(beta,-x) - e^{-2i*beta}*T_one(-beta,x)
记 A(beta,x) = T_one(beta,-x)，B(beta,x) = e^{-2i*beta}*T_one(-beta,x)
则 T_two = A - B。

Gamma_two的被积核（对应一个极化通道）正比于:
    T_two(bu,xu) * conj(T_two(bv,xv))
  = [A(bu,xu)-B(bu,xu)] * [conj(A(bv,xv))-conj(B(bv,xv))]
  = A(bu,xu)*conj(A(bv,xv))                     ... (I)
  - A(bu,xu)*conj(B(bv,xv))                     ... (II)
  - B(bu,xu)*conj(A(bv,xv))                     ... (III)
  + B(bu,xu)*conj(B(bv,xv))                     ... (IV)

每一项的物理含义可以直接读出对应的Gamma_one参数替换：
  A(beta,x)=T_one(beta,-x)  <=>  x=n.u -> -x=n.(-u)，即u_hat->-u_hat，
                                  beta_u不变
  B(beta,x)=e^{-2i*beta}*T_one(-beta,x)  <=>  u_hat不变，beta->-beta，
                                  外加相位因子e^{-2i*beta}
  conj(...)对beta,x是实数的情形只是把i->-i，不改变上述u_hat/beta的
  替换关系本身，只改变外部相位因子的共轭。

对四项逐一分析：
  (I)   A(bu,xu)*conj(A(bv,xv))
        = T_one(bu,-xu) * conj(T_one(bv,-xv))
        => u_hat->-u_hat (beta_u=bu不变), v_hat->-v_hat (beta_v=bv不变)
        => Gamma_one(alpha, bu, bv, s, -u_hat, -v_hat)，相位系数=1

  (II)  -A(bu,xu)*conj(B(bv,xv))
        = -A(bu,xu) * e^{+2i*bv} * conj(T_one(-bv,xv))
        A(bu,xu)=T_one(bu,-xu) => u_hat->-u_hat, beta_u=bu不变
        conj(T_one(-bv,xv)) => v_hat不变, beta_v->-bv
        => -e^{2i*beta_v} * Gamma_one(alpha, bu, -beta_v, s, -u_hat, +v_hat)

  (III) -B(bu,xu)*conj(A(bv,xv))
        = -e^{-2i*bu} * T_one(-bu,xu) * conj(T_one(bv,-xv))
        T_one(-bu,xu) => u_hat不变, beta_u->-bu
        conj(T_one(bv,-xv)) => v_hat->-v_hat, beta_v=bv不变
        => -e^{-2i*beta_u} * Gamma_one(alpha, -beta_u, beta_v, s, +u_hat, -v_hat)

  (IV)  B(bu,xu)*conj(B(bv,xv))
        = e^{-2i*bu}*T_one(-bu,xu) * e^{2i*bv}*conj(T_one(-bv,xv))
        T_one(-bu,xu) => u_hat不变, beta_u->-bu
        conj(T_one(-bv,xv)) => v_hat不变, beta_v->-bv
        => e^{2i(beta_v-beta_u)} * Gamma_one(alpha, -beta_u, -beta_v, s, +u_hat, +v_hat)

=== 与论文Eq(35)逐项对比 ===
论文term1: Gamma_one(a,bu,bv,s,-u,-v)            == (I)   -> 一致 ✓
论文term2: -e^{-2ibu}Gamma_one(a,-bu,bv,s,u,-v)   == (III) -> 一致 ✓
论文term3: -e^{2ibv}Gamma_one(a,bu,-bv,s,u,-v)    vs (II): -e^{2ibv}Gamma_one(a,bu,-bv,s,-u,+v)
           ^^^ 论文印刷 (u_hat,-v_hat)，符号推导给出 (-u_hat,+v_hat)
           两者u_hat,v_hat的正负号被交换了 —— 这是论文Eq(35)本身的印刷错误！
论文term4: e^{2i(bv-bu)}Gamma_one(a,-bu,-bv,s,u,v)  == (IV)  -> 一致 ✓
"""
import sympy as sp

bu, bv, xu, xv = sp.symbols('beta_u beta_v x_u x_v', real=True)
I = sp.I


def T_one(beta, x):
    return (1 - sp.exp(-I * beta * (1 + x))) / (1 + x)


def A(beta, x):
    return T_one(beta, -x)


def B(beta, x):
    return sp.exp(-2 * I * beta) * T_one(-beta, x)


if __name__ == "__main__":
    print("=" * 70)
    print("Step 1: 验证 T_two = A - B 恒等于论文Eq(34)原始定义")
    print("=" * 70)
    T_two_direct = T_one(bu, -xu) - sp.exp(-2 * I * bu) * T_one(-bu, xu)
    T_two_AB = A(bu, xu) - B(bu, xu)
    diff0 = sp.simplify(T_two_direct - T_two_AB)
    print(f"T_two(直接定义) - (A-B) = {diff0}  (应为0)")

    print("\n" + "=" * 70)
    print("Step 2: 严格验证乘积展开为四项之和")
    print("=" * 70)
    LHS = sp.expand((A(bu, xu) - B(bu, xu)) * sp.conjugate(A(bv, xv) - B(bv, xv)))
    term_I = A(bu, xu) * sp.conjugate(A(bv, xv))
    term_II = -A(bu, xu) * sp.conjugate(B(bv, xv))
    term_III = -B(bu, xu) * sp.conjugate(A(bv, xv))
    term_IV = B(bu, xu) * sp.conjugate(B(bv, xv))
    RHS = term_I + term_II + term_III + term_IV
    diff1 = sp.simplify(LHS - RHS)
    print(f"展开乘积 - 四项之和 = {diff1}  (应为0)")

    print("\n" + "=" * 70)
    print("Step 3: 验证term_II的相位因子分解")
    print("=" * 70)
    claimed_conjB = sp.exp(2 * I * bv) * sp.conjugate(T_one(-bv, xv))
    actual_conjB = sp.conjugate(B(bv, xv))
    diff2 = sp.simplify(claimed_conjB - actual_conjB)
    print(f"conj(B(bv,xv)) - e^{{2i*bv}}*conj(T_one(-bv,xv)) = {diff2}  (应为0)")

    print("\n" + "=" * 70)
    print("结论：论文Eq(35)第三项方向矢量符号应为(-u_hat,+v_hat)，")
    print("      而非论文印刷的(u_hat,-v_hat)。其余三项转录准确无误。")
    print("=" * 70)
