"""
【性质】数值验证 —— TDI Michelson X 通道 ORF：
  本组件 01 号文件的"Γ_one 双重求和 + TDI 延迟相位权重"组装
  vs  01 号黄金标准（逐条单向链路 T_one 响应直接天球积分，同样施加
      TDI 延迟相位权重，完全不经过留数/I1 框架）。
  两者若一致，则 PRD Eq.(37)-(38) 的 SbLI 组装路径在手征版上严格成立，
  旧组件C"框架根本不匹配"的诊断被证伪。

【检验构型】
  检验1（小规模快速）：单个等边三角形星座（臂长 L=2.5e5 km，小于 LISA
       以降低天球积分振荡），TDI-X 自相关的强度 I 分量（应实数、非零、
       低频 ∝ β²）。手征 V 分量对单星座共面应≈0（物理预期，见阶段2）。
  检验2（两星座非共面）：两个相互倾斜、分开的三角形（LISA-Taiji 网络
       玩具构型），TDI-X 互相关的 I 与 V 分量都应非零。
"""
import os, sys, importlib.util
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


asm = _load("asm", os.path.join(_here, "..", "具体计算",
                                "01_TDI通道用单向链路Gamma_one正确组装.py"))
gold = _load("gold", os.path.join(_here,
                                  "01_直接天球积分黄金标准_任意单向链路与TDI通道.py"))

C = gold.C_LIGHT


def tdi_X_gold_terms(r1, r2, r3, L, f):
    """与 asm.tdi_X_terms 完全相同的 8 个几何项，但供黄金标准使用
    （黄金标准虚拟通道：R_X = Σ w R_one(r,d,L)，延迟相位同样在权重里）。"""
    terms = asm.tdi_X_terms(r1, r2, r3, L, f)
    gterms = [dict(r=t["r"], d=t["d"], L=t["L"]) for t in terms]
    weights = [t["w"] for t in terms]
    return gterms, weights


def tri_constellation(center, L, orientation_axis, tilt=0.0):
    """生成等边三角形三星位置（在垂直于 orientation_axis 的平面内），
    卫星1位于 center + L*(某平面内方向)。返回 (r1,r2,r3)。"""
    ax = orientation_axis / np.linalg.norm(orientation_axis)
    # 平面内两个正交基
    tmp = np.array([1.0, 0.0, 0.0]) if abs(ax[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = np.cross(ax, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    if tilt != 0.0:  # 绕 e1 倾斜平面
        ct, st = np.cos(tilt), np.sin(tilt)
        e2 = ct * e2 + st * ax
        ax = -st * e1 * 0 + np.cross(e1, e2)  # 保持正交
        ax = np.cross(e1, e2); ax /= np.linalg.norm(ax)
    R = L / np.sqrt(3)  # 等边三角形外接圆半径 = L/√3
    r1 = center + R * e1
    r2 = center + R * (-0.5 * e1 + np.sqrt(3) / 2 * e2)
    r3 = center + R * (-0.5 * e1 - np.sqrt(3) / 2 * e2)
    return r1, r2, r3


def main():
    f = 0.005  # Hz
    L = 2.5e5  # km（玩具臂长，比 LISA 2.5e6 小 10 倍以加快黄金标准收敛）

    print("=" * 80)
    print("检验1：单个等边三角形 TDI-X 自相关（共面）")
    print("=" * 80)
    r1, r2, r3 = tri_constellation(np.zeros(3), L, np.array([0.0, 0.0, 1.0]))
    # 几何自检：臂长
    for (a, b) in [(r1, r2), (r2, r3), (r3, r1)]:
        print(f"  臂长 = {np.linalg.norm(a-b):.1f} km (目标 {L})")

    terms = asm.tdi_X_terms(r1, r2, r3, L, f)
    gterms, weights = tdi_X_gold_terms(r1, r2, r3, L, f)

    for kind in ["I", "V"]:
        g_res = asm.gamma_TDI_channels(terms, terms, f, kind=kind)
        g_gold = gold.virtual_channel_gamma_gold(gterms, weights, gterms, weights,
                                                 f, kind=kind, epsrel=2e-6)
        denom = max(abs(g_gold), abs(g_res), 1e-30)
        err = abs(g_res - g_gold) / denom
        print(f"  Γ_X^X {kind}  留数双重求和 = {g_res:+.6e}")
        print(f"  Γ_X^X {kind}  黄金标准     = {g_gold:+.6e}   相对误差 = {err:.2e}")

    print()
    print("=" * 80)
    print("检验2：两个分开且相互倾斜的三角形（LISA-Taiji 网络玩具构型，非共面）")
    print("=" * 80)
    c1 = np.array([-3.0e5, 0.0, 0.0])
    c2 = np.array([+3.0e5, 0.0, 2.0e5])
    rA = tri_constellation(c1, L, np.array([0.0, 0.0, 1.0]))
    rB = tri_constellation(c2, L, np.array([0.2, 0.5, 0.84]), tilt=0.6)
    tA = asm.tdi_X_terms(*rA, L, f)
    tB = asm.tdi_X_terms(*rB, L, f)
    gA, wA = tdi_X_gold_terms(*rA, L, f)
    gB, wB = tdi_X_gold_terms(*rB, L, f)
    for kind in ["I", "V"]:
        g_res = asm.gamma_TDI_channels(tA, tB, f, kind=kind)
        g_gold = gold.virtual_channel_gamma_gold(gA, wA, gB, wB, f, kind=kind,
                                                 epsrel=2e-6)
        denom = max(abs(g_gold), abs(g_res), 1e-30)
        err = abs(g_res - g_gold) / denom
        print(f"  Γ_X^X {kind}  留数双重求和 = {g_res:+.6e}")
        print(f"  Γ_X^X {kind}  黄金标准     = {g_gold:+.6e}   相对误差 = {err:.2e}")

    print()
    print("物理预期：检验1 V≈0（单星座共面，手征响应需非共面）；")
    print("          检验2 V 为纯虚数且非零（两星座非共面），I 为实数。")


if __name__ == "__main__":
    main()
