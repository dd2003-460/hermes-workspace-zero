"""
【性质】推导 —— 用真实存在、正在运行的四个GbLI探测器（LIGO Hanford H1、
        LIGO Livingston L1、Virgo V1、KAGRA K1）的公开几何数据，计算
        全部6对组合的强度ORF具体数值
【计算的量】Gamma_GbLI_I 对 (H1,L1),(H1,V1),(H1,K1),(L1,V1),(L1,K1),
        (V1,K1) 六对真实探测器组合
【状态】✅ 完成：全部6对成功计算，运行稳定（各10-15秒左右）
【依赖】本组件"具体计算"文件夹产出(Gamma_GbLI_I)

================================================================================
背景：与手征主线项目的镜像归档
================================================================================
本脚本是手征ORF计算_主线项目同名推导文件
（`阶段3_具体探测器ORF/组件B_地基GbLI/推导/03_真实四探测器网络...`）
的强度(I)专属镜像版本，遵循两项目"结构镜像"的既定惯例。该主线文件
额外计算了手征(V)分量，此处PRD强度复现副本项目职责范围仅覆盖强度部分，
故只保留Gamma_GbLI_I的计算，不重复实现V分量（V分量属于手征ORF计算_
主线项目的扩展内容，不在PRD论文复现范围内）。

选择该网络而非SbLI的原因、数据来源等背景说明与手征主线项目同名文件
完全一致，此处不再重复，详见手征主线项目对应文件的docstring，或本
组件`结论与推导过程.md`第8节。
================================================================================
"""
import numpy as np
import sys
import time

sys.path.insert(0, "../具体计算")
mod_i = __import__("01_Gamma_two组装与GbLI四臂差分")
Gamma_GbLI_I = mod_i.Gamma_GbLI_I

# ---- 真实数据 (LAL标准，ECEF坐标，单位换算为km) ----
# 数据来源：https://gwosc.org/s/param/position.txt (H1,L1,V1)
#          https://lscsoft.docs.ligo.org/lalsuite/lal/group___detector_constants.html (K1)
DETECTORS = {
    'H1': {
        'vertex': np.array([-2.161414928e6, -3.834695183e6, 4.600350224e6]) / 1000,
        'xarm': np.array([-0.22389266154, 0.79983062746, 0.55690487831]),
        'yarm': np.array([-0.91397818574, 0.02609403989, -0.40492342125]),
    },
    'L1': {
        'vertex': np.array([-7.42760447238e4, -5.49628371971e6, 3.22425701744e6]) / 1000,
        'xarm': np.array([-0.95457412153, -0.14158077340, -0.26218911324]),
        'yarm': np.array([0.29774156894, -0.48791033647, -0.82054461286]),
    },
    'V1': {
        'vertex': np.array([4.54637409900e6, 8.42989697626e5, 4.37857696241e6]) / 1000,
        'xarm': np.array([-0.70045821479, 0.20848948619, 0.68256166277]),
        'yarm': np.array([-0.05379255368, -0.96908180549, 0.24080451708]),
    },
    'K1': {
        'vertex': np.array([-3777336.024, 3484898.411, 3765313.697]) / 1000,
        'xarm': np.array([-0.3759040, -0.8361583, 0.3994189]),
        'yarm': np.array([0.7164378, 0.01114076, 0.6975620]),
    },
}
for name, d in DETECTORS.items():
    d['xarm'] = d['xarm'] / np.linalg.norm(d['xarm'])
    d['yarm'] = d['yarm'] / np.linalg.norm(d['yarm'])

c_light = 299792.458  # km/s


def compute_pair(n1, n2, f, L_arm):
    d1, d2 = DETECTORS[n1], DETECTORS[n2]
    sep_vec = d2['vertex'] - d1['vertex']
    dist = np.linalg.norm(sep_vec)
    s_hat = sep_vec / dist
    alpha = 2 * np.pi * f * dist / c_light
    beta = 2 * np.pi * f * L_arm / c_light
    val_I = Gamma_GbLI_I(alpha, beta, beta, s_hat, d1['xarm'], d1['yarm'], d2['xarm'], d2['yarm'])
    return dist, alpha, beta, val_I


if __name__ == "__main__":
    print("=== 正交性验证(数据源正确性检查) ===")
    for name, d in DETECTORS.items():
        dot = d['xarm'] @ d['yarm']
        print(f"{name}: xarm.yarm = {dot:.2e} (应接近0)")

    print("\n=== 非共面性验证 ===")
    triple = DETECTORS['H1']['xarm'] @ np.cross(DETECTORS['L1']['xarm'], DETECTORS['V1']['xarm'])
    print(f"H1_x . (L1_x x V1_x) = {triple:.4f} (非零 => 三个探测器X臂方向非共面)")

    print("\n=== 各探测器间分离距离 ===")
    names = list(DETECTORS.keys())
    for i in range(4):
        for j in range(i + 1, 4):
            n1, n2 = names[i], names[j]
            dist = np.linalg.norm(DETECTORS[n1]['vertex'] - DETECTORS[n2]['vertex'])
            print(f"  {n1}-{n2}: {dist:.1f} km")

    print("\n=== 全部6对真实探测器组合的Gamma_GbLI_I(强度) ===")
    f = 5.0       # Hz, 演示频率
    L_arm = 1e4   # km, 假想臂长(非任何真实探测器的实际4km/3km臂长，用于展示明确非零响应)
    print(f"演示参数: f={f}Hz, 假想臂长L={L_arm}km（非真实值，说明见下方结论）\n")
    print(f"{'Pair':>8} {'dist(km)':>10} {'alpha':>8} {'beta':>8} {'Gamma_I':>24}")
    for i in range(4):
        for j in range(i + 1, 4):
            n1, n2 = names[i], names[j]
            t0 = time.time()
            dist, alpha, beta, val_I = compute_pair(n1, n2, f, L_arm)
            dt = time.time() - t0
            print(f"{n1}-{n2:>3} {dist:>10.1f} {alpha:>8.4f} {beta:>8.5f} {val_I:>24.6e}  ({dt:.0f}s)")

    print("\n【重要限制说明】")
    print("1. 演示参数中的臂长L=1e4km为假想值，非四个探测器的真实臂长(2-4km)。")
    print("   真实臂长下beta极小(<1e-6)，导致Gamma_GbLI数值本身趋于数值噪声量级。")
    print("2. 强度I分量的定性趋势(不同探测器对之间ORF量级差异，随距离/相对")
    print("   朝向变化)仅供定性参照，非严格意义上对已发表文献结果的复现")
    print("   (演示参数非真实探测器臂长/频段)。")
