# theories/chimera-dynamics/ — Chimera 动力学理论

## 理论文档（按演进顺序）

### 多相凝聚相变系列（D4-S18-r18）
- [D4-S18-r18.md](D4-S18-r18.md) — 原始理论：多相凝聚相变定理（M≥2 中间态假设）
- [D4-S18-r18b-experiment.md](D4-S18-r18b-experiment.md) — M 相实验报告（高 K 下总是 M=1）
- [D4-S18-r18c-final.md](D4-S18-r18c-final.md) — 最终理论修正：直接相变（实验否定 M≥2）

### Chimera 严格重现系列
- [D4-S18-r19-summary.md](D4-S18-r19-summary.md) — 理论综合报告（均匀耦合不产生严格 chimera）
- [D4-S18-r20-strict-chimera-confirmation.md](D4-S18-r20-strict-chimera-confirmation.md) — 严格 chimera 重现确认（N≥500 实验成功）

### Chimera 参数空间扫描
- [D4-S18-r21-param-scan-analysis.md](D4-S18-r21-param-scan-analysis.md) — 参数空间扫描分析：K0 × eps 平面上的 chimera 泛在性（r01）

### 梯度锁相诊断（D4-S18-r22）
- [D4-S18-r22-gradient-locking.md](D4-S18-r22-gradient-locking.md) — r21 现象诊断：频率梯度导致 gradient-locking，非真正 chimera

### Chimera 时间行为实验
- [D4-S18-r23-temporal-analysis.md](D4-S18-r23-temporal-analysis.md) — chimera vs 梯度锁相时间行为测试（发现两者均收敛到稳态）

### Chimera 形式化诊断（D4-S18-r23）
- [D4-S18-r23-chimera-diagnostic-formalization.md](D4-S18-r23-chimera-diagnostic-formalization.md) — chimera 定义升级：三种诊断不变量（MPI/SCI/TFD）+ 双阶段协议

### 相关代码
- [../../labs/simulations/detect_m_phase.py](../../labs/simulations/detect_m_phase.py) — M 相凝聚检测器（k-means + 密度阈值）
- [../../labs/simulations/phase_chimera_correct_detection.py](../../labs/simulations/phase_chimera_correct_detection.py) — 多拓扑 chimera/多相凝聚检测
- [../../labs/simulations/experiment_chimera_spatial_coupling.py](../../labs/simulations/experiment_chimera_spatial_coupling.py) — 空间 chimera 实验（Abrams-Strogatz）
- [../../labs/simulations/quick_chimera_test.py](../../labs/simulations/quick_chimera_test.py) — chimera 快速测试（3 runs）
- [../../labs/simulations/experiment_m_phase_transition.py](../../labs/simulations/experiment_m_phase_transition.py) — M 相过渡实验
- [../../labs/simulations/experiment_m_phase_fine.py](../../labs/simulations/experiment_m_phase_fine.py) — M 相精细扫描
- [../../labs/simulations/scan_chimera_parameter_space.py](../../labs/simulations/scan_chimera_parameter_space.py) — Chimera 参数空间扫描（K0 × eps）
- [../../labs/simulations/scan_chimera_parameter_space](../../labs/simulations/scan_chimera_parameter_space) — 扫描器
- [../../labs/simulations/experiment_verify_chimera_vs_freq_gradient.py](../../labs/simulations/experiment_verify_chimera_vs_freq_gradient.py) — chimera vs 梯度锁相（D4-S18-r22）
- [../../labs/simulations/experiment_chimera_temporal_fluctuations.py](../../labs/simulations/experiment_chimera_temporal_fluctuations.py) — chimera 时间涨落（D4-S18-r23）
- [../../labs/simulations/chimera_diagnostic_v2.py](../../labs/simulations/chimera_diagnostic_v2.py) — chimera 诊断 v2（双阶段认证协议，D4-S18-r23）
- [../../chimera_lab/d53-memory-damped-phase-transition-duality.py](../../chimera_lab/d53-memory-damped-phase-transition-duality.py) — D53 记忆阻尼-相变对偶实验（D50/D52 交叉）

### 相关理论（D50-D52 交叉）
- [D53-memory-damped-phase-transition-duality.md](D53-memory-damped-phase-transition-duality.md) — D53：记忆阻尼-相变对偶性（λ_c/μ_c ≈ 1.11 对偶 + 迟滞环验证）
