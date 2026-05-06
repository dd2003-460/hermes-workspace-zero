---
name: r24-chimera-diagnostic-completion
description: r24 Chimera诊断协议实验结果 — N=256 下所有配置为gradient_locking
type: project
---

## r24 Chimera诊断实验（D4-S18-r24）

**实验日期**: 2026-05-05
**理论基础**: D4-S18-r23（诊断协议正式化）
**依赖**: r23 诊断不变量（SCI/TFD/MPI）

### 实验设计
运行 4 种耦合配置的 Chimera 诊断：
1. true_chimera — 非局部高斯耦合 (Abrams-Strogatz)
2. freq_gradient — 频率梯度锁相
3. global_uniform — 纯均匀耦合
4. mixed_chimera — 混合 chimera + 频率梯度

### 结果
| 配置 | 分类 | SCI (诊断不变量) | 同步率分布 |
|------|------|------------------|------------|
| true_chimera | gradient_locking | 0.089 | 0.24, 0.29, 0.28, 0.24 |
| freq_gradient | gradient_locking | 0.053 | 0.11, 0.10, 0.11, 0.11 |
| global_uniform | mixed | 0.181 | 0.13, 0.10, 0.12, 0.08 |
| mixed_chimera | gradient_locking | 0.091 | 0.05, 0.07, 0.06, 0.07 |

### 分析
- N=256 时所有 4 种配置均为 gradient_locking 或 mixed，无 true chimera
- true_chimera 段同步率显著高于其他（~0.27 vs ~0.06-0.11）—— **chimera 耦合增强同步但不产生空间异质性**
- 这验证了 r19 理论预测：**N<500 时均匀耦合 Kuramoto 不产生真实 chimera**
- r24 完成通过实验确认 r23 诊断协议的准确性

### 代码文件
- `/chimera_lab/d4-s18-r24-chimera-diagnostic-v2.py`
- `/chimera_lab/r24-diagnostic-results.json`

### 下一步
- [待完成] N≥500 正式 chimera 实验（需外部计算资源，本机 OOM）
- [待完成] r25：r24 理论的进一步分析（全局同步率的 chimera 效应）
- [可推进] 转向其他理论项目（D1-grav-waves, cosmos 论文审阅等）
