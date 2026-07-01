# 03-execute（执行）— M1 修复

**所属规格**：`/Users/a1-6/Desktop/workspace/loop/2-loop/03-execute.md`
**状态**：completed
**输入**：loop/1-loop/03-任务分解 (M1 修复任务)
**输出**：scripts/06-olc-lisa-mixed-network.py (修复后) + scripts/06a-patched-mixed-network.py (产出)

---

## 执行记录

### 修复的 4 个物理错误 (C1-C4)

| 错误 | 描述 | 修复 |
|------|------|------|
| C1 | OLC (Hz⁻¹) vs LISA (Hz⁻¹/√Hz) 交叉相关项维度不一致 | 保留交叉相关项但实际贡献≈0 (不同可观测量) |
| C2 | SNR 公式用 S²/noise²，应为 S²/noise (Allen 1987) | 全局修正 dSNR2/df 公式中 noise 为一次方 |
| C3 | gamma_olc=0.53 重复乘了 K_arm (已在转移函数中) | 移除所有 gamma_olc 因子 |
| C4 | SNR_comb = sqrt(SNR_OLC² + SNR_LISA² + 2*SNR_cross²) 概念错误 | 公式改为 sqrt(SNR_OLC² + SNR_LISA²)，N_base 移除 |

### 涉及函数及修改

| 函数 | 修改内容 |
|------|---------|
| `olc_snr_integrated()` | 移除 gamma_olc, noise² → noise |
| `lisa_snr_integrated()` | noise² → noise |
| `olca_lisa_cross_snr()` | 添加注释说明不同观测量的限制 |
| `combined_snr()` | 移除 N_base, gamma_olc, 添加注释 |
| `plot_sensitivity_curves()` | 移除 gamma_olc, N_base 传参 |
| `plot_frequency_coverage()` | 同上 |
| `plot_frequency_band_decomposition()` | 同上 |

### Git 提交记录
- commit hash: fd9d4d7
- message: M1: fix 4 physics bugs in 06-olc-lisa-mixed-network (C1-C4)
- date: 2026-07-01

### 验证运行结果
- OLC alone SNR = 9.414e-31 (14 orders lower after C2 fix for L=10m baseline)
- LISA alone SNR = 3.092e-10
- LISA 主导 OLC 约 3.3e+20x
- 所有 4 个 PNG  plots 生成成功
- 脚本退出码 = 0

### 物理结论更新
- OLC (地面 10m 臂长) 对 SGWB 灵敏度远低于 LISA
- OLC + LISA 混合网络的增益来自 LISA 贡献，OLC 贡献可忽略
- OLC 的潜在价值在于：(1) 正交偏振覆盖 (2) 高频段 (kHz+) (3) 独立系统学验证

---

## 完成时间
last_completed_at: 2026-07-01

## 回滚
从 commit fd9d4d7 恢复: `git checkout fd9d4d7^ -- scripts/`
