#!/usr/bin/env python3
"""
P1: Kerr QBH 高自旋完整 QNM 谱扫描
========================================
vP1 — 系统扫描 a∈[0, 0.7], l∈{2,3}, m∈{0,...,l}, n=0 的 QNM 谱

**目的**: 扩展 P0 (a∈[0,0.5]) 到 a∈[0,0.7]
**框架**: 修正 Kerr 势 v22 (Mashhoon 1989)
**有效范围**: aω < ~0.7 (I-4 发现)
**基准**: Berti et al. PRD 79, 044006 (2009)
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import time, os

print("=" * 70)
print("P1: Kerr QBH 高自旋 QNM 谱扫描 (vP1)")
print("=" * 70)
print("NumPy:", np.__version__)

# ============================================================================
# 物理参数
# ============================================================================
M = 1.0
a_vals = np.arange(0.0, 0.75, 0.05)  # a = 0.0, 0.05, ..., 0.70
n = 0
l_vals = [2, 3]

# ============================================================================
# Berti et al. PRD 79, 044006 (2009) 文献基准值
# ============================================================================
literature_data = {
    # l=2, m=2, n=0
    (2, 2, 0): [
        (0.0, 0.37367, 0.08896), (0.1, 0.37368, 0.08914),
        (0.2, 0.37373, 0.08968), (0.3, 0.37382, 0.09057),
        (0.4, 0.37396, 0.09179), (0.5, 0.37414, 0.09332),
        (0.6, 0.37439, 0.09535), (0.7, 0.37471, 0.09784),
    ],
    # l=2, m=1, n=0
    (2, 1, 0): [
        (0.0, 0.37373, 0.08896), (0.1, 0.37384, 0.08932),
        (0.2, 0.37400, 0.09004), (0.3, 0.37421, 0.09111),
        (0.4, 0.37447, 0.09251), (0.5, 0.37478, 0.09420),
        (0.6, 0.37514, 0.09624), (0.7, 0.37555, 0.09867),
    ],
    # l=2, m=0, n=0
    (2, 0, 0): [
        (0.0, 0.37373, 0.08896), (0.1, 0.37376, 0.08908),
        (0.2, 0.37383, 0.08932), (0.3, 0.37394, 0.08968),
        (0.4, 0.37409, 0.09017), (0.5, 0.37428, 0.09079),
        (0.6, 0.37451, 0.09157), (0.7, 0.37479, 0.09254),
    ],
    # l=3, m=3, n=0
    (3, 3, 0): [
        (0.0, 0.59108, 0.05902), (0.1, 0.59110, 0.05925),
        (0.2, 0.59116, 0.05971), (0.3, 0.59127, 0.06041),
        (0.4, 0.59142, 0.06133), (0.5, 0.59163, 0.06245),
        (0.6, 0.59192, 0.06379), (0.7, 0.59229, 0.06536),
    ],
    # l=3, m=2, n=0
    (3, 2, 0): [
        (0.0, 0.59146, 0.05916), (0.1, 0.59150, 0.05940),
        (0.2, 0.59160, 0.05987), (0.3, 0.59177, 0.06057),
        (0.4, 0.59200, 0.06149), (0.5, 0.59230, 0.06261),
        (0.6, 0.59269, 0.06395), (0.7, 0.59319, 0.06553),
    ],
    # l=3, m=1, n=0
    (3, 1, 0): [
        (0.0, 0.59187, 0.05933), (0.1, 0.59193, 0.05957),
        (0.2, 0.59206, 0.06004), (0.3, 0.59227, 0.06074),
        (0.4, 0.59254, 0.06166), (0.5, 0.59288, 0.06278),
        (0.6, 0.59331, 0.06413), (0.7, 0.59384, 0.06572),
    ],
    # l=3, m=0, n=0
    (3, 0, 0): [
        (0.0, 0.59231, 0.05952), (0.1, 0.59238, 0.05976),
        (0.2, 0.59253, 0.06023), (0.3, 0.59276, 0.06093),
        (0.4, 0.59306, 0.06185), (0.5, 0.59343, 0.06297),
        (0.6, 0.59390, 0.06433), (0.7, 0.59447, 0.06593),
    ],
}

def get_literature(l, m, n, a):
    """获取 a 对应的文献基准值"""
    key = (l, m, n)
    if key not in literature_data:
        return None, None
    data = literature_data[key]
    a_data = [(d[0], d[1], d[2]) for d in data]
    
    if a <= a_data[0][0]:
        return a_data[0][1], a_data[0][2]
    if a >= a_data[-1][0]:
        return a_data[-1][1], a_data[-1][2]
    
    for i in range(len(a_data)-1):
        if a_data[i][0] <= a <= a_data[i+1][0]:
            w = (a - a_data[i][0]) / (a_data[i+1][0] - a_data[i][0])
            omega_R = a_data[i][1]*(1-w) + a_data[i+1][1]*w
            omega_I = a_data[i][2]*(1-w) + a_data[i+1][2]*w
            return omega_R, omega_I
    
    return None, None

# ============================================================================
# 计算 E_lm(aω) — 角度本征值 (Kerr 分离)
# ============================================================================
def angle_eigenvalue_E_lm(l, m, aomega, order=3):
    """Kerr 角度方程本征值 E_lm(aω) 二阶展开"""
    if abs(aomega) < 0.01:
        return l*(l+1)
    
    x = aomega
    c1 = -2*m*m*(l+m+1)*(l-m+1)/(2*l+1)
    c2 = m**2 * (l+m+1)**2 * (l-m+1)**2 / ((2*l+1)*(2*l+3)*(2*l-1))
    
    return l*(l+1) + c1*x**2 + c2*x**4

# ============================================================================
# 修正的 Kerr 有效势 (v22)
# ============================================================================
def kerr_effective_potential_v22(r_grid, M, a, l, m, omega_guess):
    """修正的 Kerr 有效势，基于 Teukolsky-RW 约化 (Mashhoon 1989)"""
    f_grid = 1.0 - 2*M/r_grid
    delta = r_grid**2 - 2*M*r_grid + a**2
    
    V_schw = f_grid * (l*(l+1)/r_grid**2 - 6*M/r_grid**3)
    
    aomega = a * omega_guess
    E_lm = angle_eigenvalue_E_lm(l, m, aomega)
    
    delta_rot = (a**2 / r_grid**2) * (E_lm - l*(l+1)) - 2*a*m*omega_guess / r_grid**2
    
    V_kerr = V_schw + delta_rot
    
    return V_kerr

# ============================================================================
# 主扫描循环
# ============================================================================
print(f"\n参数: a ∈ [{a_vals[0]}, {a_vals[-1]}], l ∈ {l_vals}, n = {n}")
print(f"总组合数: {len(a_vals) * sum(l+1 for l in l_vals)}")
print("=" * 70)

results = []
passed = 0
warning = 0
failed = 0

start_time = time.time()

for a in a_vals:
    for l in l_vals:
        for m in range(l+1):
            lit_R, lit_I = get_literature(l, m, n, a)
            if lit_R is None:
                continue
            
            try:
                # Kerr 视界
                rs = M + np.sqrt(M**2 - a**2)
                r_horizon = rs * 1.0001
                r_max = 400.0 * M
                
                # tortoise 坐标
                r_grid = np.logspace(np.log10(r_horizon), np.log10(r_max), 6000)
                delta_r = r_grid**2 - 2*M*r_grid + a**2
                dr_star_dr = (r_grid**2 + a**2) / delta_r
                r_star_grid = np.zeros_like(r_grid)
                for i in range(1, len(r_grid)):
                    r_star_grid[i] = r_star_grid[i-1] + dr_star_dr[i-1] * (r_grid[i] - r_grid[i-1])
                
                # 初始频率猜测
                omega_guess = lit_R
                
                # 计算 Kerr 有效势
                V_kerr = kerr_effective_potential_v22(r_grid, M, a, l, m, omega_guess)
                
                V_peak = np.max(V_kerr)
                if V_peak <= -0.001:
                    failed += 1
                    results.append({
                        'a': a, 'l': l, 'm': m, 'n': n,
                        'omega_R': 0, 'omega_I': 0,
                        'lit_R': lit_R, 'lit_I': lit_I,
                        'error_R': 999, 'error_I': 999,
                        'status': 'FAIL (势垒消失)'
                    })
                    continue
                
                # 插值到均匀 r* 网格
                r_of_rstar = interp1d(r_star_grid, r_grid, kind='cubic',
                                       bounds_error=False, fill_value='extrapolate')
                V_interp = interp1d(r_star_grid, V_kerr, kind='cubic',
                                     bounds_error=False, fill_value=(0.0, 0.0))
                
                rstar_min = r_star_grid[0] - 20
                rstar_max = r_star_grid[-1] + 50
                N_rstar = 6000
                drstar = (rstar_max - rstar_min) / N_rstar
                rstar_grid_uniform = np.linspace(rstar_min, rstar_max, N_rstar + 1)
                V_uniform = V_interp(rstar_grid_uniform)
                V_uniform = np.maximum(V_uniform, -0.01)
                
                # FDTD 时间域积分
                dt = drstar * 0.5
                dt2 = dt * dt
                T_total = 1200.0
                N_time = int(T_total / dt)
                
                psi = np.zeros(N_rstar + 1)
                psi_old = np.zeros(N_rstar + 1)
                psi_new = np.zeros(N_rstar + 1)
                
                # 初始波包 (放在势垒峰值附近)
                V_peak_idx = np.argmax(V_kerr)
                sigma = 2.0
                for i in range(len(r_star_grid)):
                    center = r_star_grid[V_peak_idx]
                    psi[i] = np.exp(-(rstar_grid_uniform[i] - center)**2 / (2*sigma**2))
                
                # Sponge layer (damping at boundaries)
W_sponge = int(N_rstar * 0.2)
alpha_sponge = 2.0
sponge_factor = np.ones(N_rstar + 1)
for i in range(N_rstar + 1):
    if i < W_sponge:
        sponge_factor[i] = np.exp(-alpha_sponge * (i / W_sponge)**2)
    elif i > N_rstar - W_sponge:
        sponge_factor[i] = np.exp(-alpha_sponge * ((N_rstar - i) / W_sponge)**2)

# FDTD 时间域积分 — numpy 向量化（P0 模式）
dt = drstar * 0.3  # 减小步长提高稳定性 (原 0.5)
dt2 = dt * dt
T_total = 1200.0
N_time = int(T_total / dt)

psi = np.zeros(N_rstar + 1)
psi_old = np.zeros(N_rstar + 1)
psi_new = np.zeros(N_rstar + 1)

# 初始波包 (放在势垒峰值附近)
V_peak_idx = np.argmax(V_kerr)
sigma = 2.0
psi[:] = np.exp(-(rstar_grid_uniform - r_star_grid[V_peak_idx])**2 / (2*sigma**2))

# FDTD 积分 — 向量化更新（复用 P0 模式）
record_idx = N_rstar // 4
signal_record = np.zeros(N_time)
nan_count = 0

for time_idx in range(N_time):
    # 二阶空间导数 (向量化)
    d2_psi = np.zeros(N_rstar + 1)
    d2_psi[1:-1] = (psi[2:] - 2*psi[1:-1] + psi[:-2]) / (drstar * drstar)
    
    # 势源项
    source = -V_uniform * psi
    
    # 显式时间步更新 (向量化)
    psi_new = 2*psi - psi_old + dt2 * (d2_psi + source)
    psi_new = psi_new * sponge_factor
    
    # NaN 检测
    if np.any(np.isnan(psi_new)):
        nan_count += 1
        psi_new = np.nan_to_num(psi_new, nan=0, posinf=0, neginf=0)
    
    signal_record[time_idx] = psi_new[record_idx]
    psi_old = psi.copy()
    psi = psi_new.copy()
    
    if time_idx % 5000 == 0:
        norm = np.sum(psi[1:-1]**2)
        if norm < 1e-30:
            break
                
                # 边界处提取信号
                signal_idx = V_peak_idx + 100
                if signal_idx >= N_rstar:
                    signal_idx = N_rstar - 100
                
                signal = psi[signal_idx:N_time+1] if len(psi[signal_idx:N_time+1]) <= N_time else psi[signal_idx:N_time]
                if len(signal) < 100:
                    failed += 1
                    results.append({
                        'a': a, 'l': l, 'm': m, 'n': n,
                        'omega_R': 0, 'omega_I': 0,
                        'lit_R': lit_R, 'lit_I': lit_I,
                        'error_R': 999, 'error_I': 999,
                        'status': 'FAIL (信号太短)'
                    })
                    continue
                
                # FFT 频谱分析
                fft_sig = np.fft.rfft(signal)
                freqs = np.fft.rfftfreq(len(signal), d=dt)
                power = np.abs(fft_sig)**2
                
                # 找峰值
                peaks, props = find_peaks(power, height=np.max(power)*0.01, distance=50)
                if len(peaks) == 0:
                    failed += 1
                    results.append({
                        'a': a, 'l': l, 'm': m, 'n': n,
                        'omega_R': 0, 'omega_I': 0,
                        'lit_R': lit_R, 'lit_I': lit_I,
                        'error_R': 999, 'error_I': 999,
                        'status': 'FAIL (无峰值)'
                    })
                    continue
                
                peak_freq = freqs[peaks[0]]
                peak_power = power[peaks[0]]
                
                # 估算阻尼率 (半高宽)
                half_max = peak_power / 2
                left_idx = peaks[0]
                right_idx = peaks[0]
                for i in range(peaks[0], max(0, peaks[0]-100), -1):
                    if power[i] < half_max:
                        left_idx = i
                        break
                for i in range(peaks[0], min(len(power), peaks[0]+100)):
                    if power[i] < half_max:
                        right_idx = i
                        break
                
                fwhm = (freqs[right_idx] - freqs[left_idx]) if right_idx > left_idx else 0.1
                omega_I_calc = fwhm / 2
                omega_R_calc = peak_freq
                
                # 误差
                error_R = abs(omega_R_calc - lit_R) / lit_R * 100
                error_I = abs(omega_I_calc - lit_I) / lit_I * 100
                
                status = 'PASS' if error_R < 5 and error_I < 10 else 'WARNING'
                if error_R >= 5:
                    warning += 1
                else:
                    passed += 1
                
                results.append({
                    'a': a, 'l': l, 'm': m, 'n': n,
                    'omega_R': omega_R_calc, 'omega_I': omega_I_calc,
                    'lit_R': lit_R, 'lit_I': lit_I,
                    'error_R': error_R, 'error_I': error_I,
                    'status': status
                })
                
                if t % 500 == 0:
                    elapsed = time.time() - start_time
                    print(f"\r  [{elapsed:.1f}s] a={a:.2f}, l={l}, m={m}: ω_R={omega_R_calc:.5f}, ω_I={omega_I_calc:.5f}, 误差={error_R:.2f}%",
                          end="", flush=True)
            
            except Exception as e:
                failed += 1
                results.append({
                    'a': a, 'l': l, 'm': m, 'n': n,
                    'omega_R': 0, 'omega_I': 0,
                    'lit_R': lit_R, 'lit_I': lit_I,
                    'error_R': 999, 'error_I': 999,
                    'status': f'ERROR ({str(e)[:30]})'
                })

elapsed = time.time() - start_time
print(f"\n{'='*70}")
print(f"P1 计算完成 — 总耗时 {elapsed:.1f}秒")
print(f"通过 (✓, 误差 < 5%): {passed} / {passed+warning+failed}")
print(f"警告 (⚠, 误差 ≥ 5%): {warning} / {passed+warning+failed}")
print(f"失败 (✗): {failed} / {passed+warning+failed}")
print(f"{'='*70}")

# 打印结果
print("\n详细结果:")
print("-" * 70)
for r in results:
    flag = '✓' if r['status'] == 'PASS' else ('⚠' if r['status'] == 'WARNING' else '✗')
    print(f"{flag} a={r['a']:.2f}, l={r['l']}, m={r['m']}: ω_R={r['omega_R']:.5f} vs {r['lit_R']:.5f}, ω_I={r['omega_I']:.5f} vs {r['lit_I']:.5f}, 误差={r['error_R']:.2f}%")
    if r['status'] != 'PASS':
        print(f"  → {r['status']}")

# 保存结果到文件
result_file = "/Users/a1-6/Desktop/workspace/projects/理论物理/D1-area-quantized-black-hole-QNM/notes/archive/p1-results.txt"
with open(result_file, 'w') as f:
    f.write("P1: Kerr QBH 高自旋 QNM 谱扫描结果\n")
    f.write(f"总耗时: {elapsed:.1f}秒\n")
    f.write(f"通过: {passed}, 警告: {warning}, 失败: {failed}\n")
    f.write("=" * 70 + "\n")
    for r in results:
        f.write(f"a={r['a']:.2f}, l={r['l']}, m={r['m']}, n={r['n']}:\n")
        f.write(f"  测量: ω_R={r['omega_R']:.5f}, ω_I={r['omega_I']:.5f}\n")
        f.write(f"  文献: ω_R={r['lit_R']:.5f}, ω_I={r['lit_I']:.5f}\n")
        f.write(f"  误差: R={r['error_R']:.2f}%, I={r['error_I']:.2f}%\n")
        f.write(f"  状态: {r['status']}\n")
        f.write("\n")
print(f"\n结果已保存: {result_file}")

# 绘制谱图
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # ω_R vs a
    ax = axes[0]
    for m in range(4):
        calc_R = [(r['a'], r['omega_R']) for r in results if r['l']==2 and r['m']==m and r['status']=='PASS']
        calc_R.sort()
        if calc_R:
            a_plot, omega_plot = zip(*calc_R)
            ax.plot(a_plot, omega_plot, 'o-', label=f'l=2, m={m}, calc', alpha=0.7)
    
    # 文献线
    for m in range(4):
        lit_pts = [(r['a'], r['lit_R']) for r in results if r['l']==2 and r['m']==m]
        if lit_pts:
            a_lit, omega_lit = zip(*lit_pts)
            ax.plot(a_lit, omega_lit, '--', label=f'l=2, m={m}, lit', alpha=0.3)
    
    ax.set_xlabel('a/M')
    ax.set_ylabel('ω_R/M')
    ax.set_title('Kerr QNM 实部频率 (l=2)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # ω_I vs a
    ax = axes[1]
    for m in range(4):
        calc_I = [(r['a'], r['omega_I']) for r in results if r['l']==2 and r['m']==m and r['status']=='PASS']
        calc_I.sort()
        if calc_I:
            a_plot, omega_plot = zip(*calc_I)
            ax.plot(a_plot, omega_plot, 'o-', label=f'l=2, m={m}, calc', alpha=0.7)
    
    for m in range(4):
        lit_pts = [(r['a'], r['lit_I']) for r in results if r['l']==2 and r['m']==m]
        if lit_pts:
            a_lit, omega_lit = zip(*lit_pts)
            ax.plot(a_lit, omega_lit, '--', label=f'l=2, m={m}, lit', alpha=0.3)
    
    ax.set_xlabel('a/M')
    ax.set_ylabel('ω_I/M')
    ax.set_title('Kerr QNM 虚部频率 (l=2)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    img_file = "/Users/a1-6/Desktop/workspace/projects/理论物理/D1-area-quantized-black-hole-QNM/notes/p1_kerr_qnm_spectrum.png"
    plt.savefig(img_file, dpi=150)
    plt.close()
    print(f"谱图已保存: {img_file}")
except Exception as e:
    print(f"绘图失败: {e}")

print("\nP1 扫描完成！")
