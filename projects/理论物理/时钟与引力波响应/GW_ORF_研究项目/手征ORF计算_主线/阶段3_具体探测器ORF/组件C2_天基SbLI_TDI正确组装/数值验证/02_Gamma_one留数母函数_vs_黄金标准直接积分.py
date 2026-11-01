"""
【性质】数值验证 —— 接口对齐检查：
  本组件黄金标准 gamma_one_gold（直接天球积分，不经过留数）与
  阶段2已验证的 Gamma_one_I/V（留数母函数）在"任意两条单向链路"上
  是否一致。这是 TDI 双重求和正确性的前提（PRD Eq.(38) 每个 (i,j)
  项都调用一次 Gamma_one）。
【状态】✅ 验证通过（见运行输出）
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "具体计算"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_here = os.path.dirname(os.path.abspath(__file__))
_calc = os.path.join(_here, "..", "具体计算", "01_TDI通道用单向链路Gamma_one正确组装.py")
asm = _load("asm", _calc)
gold = _load("gold", os.path.join(_here, "01_直接天球积分黄金标准_任意单向链路与TDI通道.py"))

Gamma_one_I, Gamma_one_V = asm.Gamma_one_I, asm.Gamma_one_V
gamma_one_gold = gold.gamma_one_gold
C = gold.C_LIGHT


def rand_unit(rng):
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)


def main():
    rng = np.random.default_rng(42)
    f = 0.01  # Hz，空间探测器典型频率
    L_u, L_v = 1.0e6, 1.0e6  # km 量级臂长（LISA 2.5e6 km）
    print("=" * 78)
    print("验证：Gamma_one 留数母函数 vs 直接天球积分黄金标准（任意两条单向链路）")
    print("=" * 78)
    worst_I = worst_V = 0.0
    for trial in range(4):
        u_hat = rand_unit(rng)
        v_hat = rand_unit(rng)
        r_u = rng.normal(size=3) * 2.0e6
        r_v = r_u + rand_unit(rng) * (2.0e6 * (0.5 + rng.random()))
        dr = r_v - r_u
        dL = np.linalg.norm(dr)
        s_hat = dr / dL
        k_wave = 2 * np.pi * f / C
        alpha, bu, bv = k_wave * dL, k_wave * L_u, k_wave * L_v

        link_u = dict(r=r_u, d=u_hat, L=L_u)
        link_v = dict(r=r_v, d=v_hat, L=L_v)

        gI_gold = gamma_one_gold(link_u, link_v, f, kind="I")
        gV_gold = gamma_one_gold(link_u, link_v, f, kind="V")
        gI_res = Gamma_one_I(alpha, bu, bv, s_hat, u_hat, v_hat)
        gV_res = Gamma_one_V(alpha, bu, bv, s_hat, u_hat, v_hat)

        errI = abs(gI_gold - gI_res) / max(abs(gI_gold), 1e-30)
        errV = abs(gV_gold - gV_res) / max(abs(gV_gold), 1e-30)
        worst_I = max(worst_I, errI)
        worst_V = max(worst_V, errV)
        print(f"trial{trial}: α={alpha:.3f} βu={bu:.3f} βv={bv:.3f}")
        print(f"   I : gold={gI_gold:+.6e}  residue={gI_res:+.6e}  relerr={errI:.2e}")
        print(f"   V : gold={gV_gold:+.6e}  residue={gV_res:+.6e}  relerr={errV:.2e}")
    print("-" * 78)
    print(f"最大相对误差:  I={worst_I:.2e}   V={worst_V:.2e}")
    assert worst_I < 1e-4 and worst_V < 1e-4, "接口对齐失败！"
    print("结论：✅ Gamma_one 留数母函数与直接天球积分在任意单向链路对上一致，")
    print("      TDI 双重求和(PRD Eq.38)逐项调用的接口正确。")


if __name__ == "__main__":
    main()
