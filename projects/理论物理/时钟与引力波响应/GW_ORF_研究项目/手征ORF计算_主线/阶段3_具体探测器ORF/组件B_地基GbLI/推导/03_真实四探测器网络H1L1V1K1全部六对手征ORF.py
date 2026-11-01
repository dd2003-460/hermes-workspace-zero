"""
【性质】推导 —— 用真实存在、正在运行的四个GbLI探测器（LIGO Hanford H1、
        LIGO Livingston L1、Virgo V1、KAGRA K1）的公开几何数据，计算
        全部6对组合的强度与手征ORF具体数值
【计算的量】Gamma_GbLI_I, Gamma_GbLI_V 对 (H1,L1),(H1,V1),(H1,K1),
        (L1,V1),(L1,K1),(V1,K1) 六对真实探测器组合
【状态】✅ 完成：全部6对成功计算，运行稳定（各19秒左右）
【依赖】阶段3组件B"具体计算"文件夹产出(Gamma_GbLI_I, Gamma_GbLI_V)

================================================================================
背景：为什么选择这个网络而非SbLI
================================================================================
用户提出"是否有更简单非共面构型且实际存在数据的探测器"。经调研确认：
- OLC(光晶格钟)网络虽与Gamma_one框架直接对应，但只是提议中的未来探测器，
  无实测数据，且现有论文(arXiv:2602.05714)只算了强度部分
- SbLI(空间三星六链路/TDI)的完整精确留数法实现远比预期复杂——尝试把
  TDI-X通道用"单向链路线性组合+已验证的Gamma_one/I1框架"重新构造时，
  多次尝试均被严格数值验证证伪（详见对话记录中的失败排查过程），
  根源是往返链路/TDI组合的"方向-位置耦合"结构与Gamma_one/I1框架
  假设的"独立位置参数"存在深层不匹配，需要更大工作量才能解决

**GbLI机制已经完全验证过（阶段3组件B前两节），而LIGO+Virgo+KAGRA
四探测器网络是真实存在、天然非共面、持续产生公开数据的现成GbLI网络**，
直接套用即可，不需要任何新的理论推导——这是当前"实际数据验证"需求
下最优的现成选择。

================================================================================
数据来源
================================================================================
四个探测器的顶点位置(地心地固坐标系ECEF)和X/Y臂方向单位矢量，均来自
LIGO科学合作组织公开发布的LAL标准常量(https://gwosc.org/s/param/position.txt
及 LALSuite LALDetectors.h)，与阶段2组件B第10节、本组件推导02号文件
使用的同一数据源。所有4个探测器的X臂·Y臂点积均已验证为0(正交性检验通过，
误差~1e-6以内)，验证了数据抄录的正确性。
"""
import numpy as np
import sys
import time
sys.path.insert(0, "../../../../PRD强度ORF复现_副本/阶段3_具体探测器ORF/组件B_地基GbLI/具体计算")
sys.path.insert(0, "../具体计算")
mod_i = __import__("01_Gamma_two组装与GbLI四臂差分")
mod_v = __import__("01_Gamma_two组装与GbLI四臂差分手征版")
Gamma_GbLI_I = mod_i.Gamma_GbLI_I
Gamma_GbLI_V = mod_v.Gamma_GbLI_V

# ---- 真实数据 (LAL标准，ECEF坐标，单位换算为km) ----
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
    val_V = Gamma_GbLI_V(alpha, beta, beta, s_hat, d1['xarm'], d1['yarm'], d2['xarm'], d2['yarm'])
    return dist, alpha, beta, val_I, val_V


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

    print("\n=== 全部6对真实探测器组合的Gamma_GbLI_I(强度)与Gamma_GbLI_V(手征) ===")
    f = 5.0       # Hz, 演示频率
    L_arm = 1e4   # km, 假想臂长(非任何真实探测器的实际4km/3km臂长，用于展示明确非零响应)
    print(f"演示参数: f={f}Hz, 假想臂长L={L_arm}km（非真实值，说明见下方结论）\n")
    print(f"{'Pair':>8} {'dist(km)':>10} {'alpha':>8} {'beta':>8} {'Gamma_I':>24} {'Gamma_V':>24}")
    for i in range(4):
        for j in range(i + 1, 4):
            n1, n2 = names[i], names[j]
            t0 = time.time()
            dist, alpha, beta, val_I, val_V = compute_pair(n1, n2, f, L_arm)
            dt = time.time() - t0
            print(f"{n1}-{n2:>3} {dist:>10.1f} {alpha:>8.4f} {beta:>8.5f} {val_I:>24.6e} {val_V:>24.6e}  ({dt:.0f}s)")

    print("\n【重要限制说明】")
    print("1. 演示参数中的臂长L=1e4km为假想值，非四个探测器的真实臂长(2-4km)。")
    print("   真实臂长下beta极小(<1e-6)，导致Gamma_GbLI数值本身趋于数值噪声量级，")
    print("   与阶段2组件B第10节、本组件推导02号文件讨论的情形完全类似。")
    print("2. 手征V分量数值是本项目框架给出的全新预测，没有可对照的实测数据")
    print("   (圆偏振各向同性引力波背景尚未被实验探测到)。")
    print("3. 强度I分量的定性趋势(不同探测器对之间ORF量级差异，随距离/相对")
    print("   朝向变化)可与OLC论文arXiv:2602.05714 Fig.4 展示的LIGO/Virgo/KAGRA")
    print("   六对强度ORF曲线定性对比趋势(该图基于真实4km/3km臂长的完整频率")
    print("   扫描，与本算例的演示参数不同，仅作定性参照)。")
