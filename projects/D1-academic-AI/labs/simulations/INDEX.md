# labs/simulations/ — 仿真代码库

## 活跃代码
- [experiment_strict_chimera.py](./experiment_strict_chimera.py) — 严格 chimera 重现实验（N≥500，Abrams-Strogatz 设置，D4-S18-r19 未来方向）
- [phase_chimera_correct_detection.py](./phase_chimera_correct_detection.py) — 多拓扑 chimera/多相凝聚检测
- [detect_m_phase.py](./detect_m_phase.py) — M 相凝聚区计数（D4-S18-r18 定理实现）
- [experiment_chimera_spatial_coupling.py](./experiment_chimera_spatial_coupling.py) — 空间 chimera 实验（中等规模）
- [scan_chimera_parameter_space.py](./scan_chimera_parameter_space.py) — Chimera 参数空间扫描（K0 × eps，D4-S18-r21）
- [experiment_verify_chimera_vs_freq_gradient.py](./experiment_verify_chimera_vs_freq_gradient.py) — Chimera vs 梯度锁相 区分实验（D4-S18-r22）
- [experiment_chimera_temporal_fluctuations.py](./experiment_chimera_temporal_fluctuations.py) — chimera 时间涨落测试（D4-S18-r23）
- [experiment_curvature_predictability.py](./experiment_curvature_predictability.py) — S17 语言信息几何实验 2

## 测试结果（实验产出）
- [chimera_strict_results.json](./chimera_strict_results.json) — D4-S18-r20 严格 chimera 原始数据
- [chimera_parameter_scan_results.json](./chimera_parameter_scan_results.json) — D4-S18-r21 参数扫描数据
- [curvature_predictability_results.json](./curvature_predictability_results.json) — S17 曲率-可预测性相关性
- [chimera_vs_freq_gradient_results.json](./chimera_vs_freq_gradient_results.json) — D4-S18-r22 chimera vs 梯度锁相实验数据
- [chimera_temporal_analysis_results.json](./chimera_temporal_analysis_results.json) — D4-S18-r23 chimera 时间涨落实验

## 测试/快速代码
- [quick_chimera_test.py](./quick_chimera_test.py) — chimera 快速测试（N=100，3 runs）
- [experiment_m_phase_transition.py](./experiment_m_phase_transition.py) — M 相过渡实验
- [experiment_m_phase_fine.py](./experiment_m_phase_fine.py) — M 相精细扫描

## 历史代码
- [chimera_detector.py](./chimera_detector.py) — chimera 检测器（r04）
- [multi_chimera.py](./multi_chimera.py) — 多 chimera 检测（r04）
- [phase_extraction.py](./phase_extraction.py) — 相位提取（r04）
- [multi_chimera_strogatz.py](./multi_chimera_strogatz.py) — Strogatz 多 chimera（r10）
- [wkb_curvature_entropy.py](./wkb_curvature_entropy.py) — WKB 曲率熵（r07）

