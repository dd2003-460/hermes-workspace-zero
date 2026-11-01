"""
【性质】推导 —— 用真实LIGO Hanford(H1)/Livingston(L1)公开几何数据构造
        完整GbLI（含X臂+Y臂），计算强度与手征ORF的具体数值算例
【计算的量】Gamma_GbLI_I(alpha,beta,beta,s_hat,u1,u2,v1,v2)、
        Gamma_GbLI_V(同样参数) —— 与阶段2组件B第10节"两条单链路"算例
        不同，这里是**完整的两臂差分GbLI探测器**产出，是本项目对
        "实际探测器组合"最终能给出的具体数值
【状态】✅ 完成，正常运行(~10秒每次调用)
【依赖】阶段3组件B"具体计算"文件夹产出(Gamma_GbLI_I, Gamma_GbLI_V)

数据来源：LIGO H1/L1公开的顶点位置+X臂+Y臂方向单位矢量（LAL标准坐标，
与阶段2组件B第10节使用的同一数据源）。
"""
import numpy as np
import sys
sys.path.insert(0, "../../../../PRD强度ORF复现_副本/阶段3_具体探测器ORF/组件B_地基GbLI/具体计算")
sys.path.insert(0, "../具体计算")
mod_i = __import__("01_Gamma_two组装与GbLI四臂差分")
mod_v = __import__("01_Gamma_two组装与GbLI四臂差分手征版")
Gamma_GbLI_I = mod_i.Gamma_GbLI_I
Gamma_GbLI_V = mod_v.Gamma_GbLI_V

# ---- 真实数据 (LAL标准，ECEF坐标) ----
H1_vertex = np.array([-2.161414928e6, -3.834695183e6, 4.600350224e6])
H1_xarm = np.array([-0.2239, 0.7998, 0.5569])
H1_yarm = np.array([-0.9140, 0.0261, -0.4049])
L1_vertex = np.array([-7.427604472e4, -5.496283720e6, 3.224257018e6])
L1_xarm = np.array([-0.9546, -0.1416, -0.2622])
L1_yarm = np.array([0.2977, -0.4879, -0.8205])

u1 = H1_xarm / np.linalg.norm(H1_xarm)
u2 = H1_yarm / np.linalg.norm(H1_yarm)
v1 = L1_xarm / np.linalg.norm(L1_xarm)
v2 = L1_yarm / np.linalg.norm(L1_yarm)
sep_vec = L1_vertex - H1_vertex
sep_dist = np.linalg.norm(sep_vec)
s_hat = sep_vec / sep_dist
c = 299792.458  # km/s


if __name__ == "__main__":
    print("=== 真实H1-L1完整GbLI几何数据 ===")
    print(f"H1 X臂: {u1}, H1 Y臂: {u2}")
    print(f"L1 X臂: {v1}, L1 Y臂: {v2}")
    print(f"分离距离: {sep_dist/1000:.2f} km")

    # 用小的alpha,beta做快速演示(真实4km臂长对应的beta在探测频段内极小，
    # 与阶段2组件B第10节相同的考量，这里用假想的中等alpha,beta展示非零响应)
    alpha, beta = 0.3, 0.2
    print(f"\n演示参数: alpha={alpha}, beta_u=beta_v={beta} (假想值，非真实LIGO 4km臂长对应值)")

    val_I = Gamma_GbLI_I(alpha, beta, beta, s_hat, u1, u2, v1, v2)
    val_V = Gamma_GbLI_V(alpha, beta, beta, s_hat, u1, u2, v1, v2)
    print(f"Gamma_GbLI_I = {val_I}")
    print(f"Gamma_GbLI_V = {val_V}")

    print("\n【重要限制说明】本算例中alpha,beta为演示性假想值(非真实LIGO 4km")
    print("臂长对应值——真实值下beta极小,GbLI ORF数值会接近数值噪声量级，")
    print("与阶段2组件B第10节讨论的情形完全类似)。手征V分量数值属于本项目")
    print("框架的新预测,没有可对照的实测数据(圆偏振各向同性背景尚未被探测到)。")
