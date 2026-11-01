# 组件D：端到端 Pipeline

## 目标

把 A（数据生成）+ B（估计量）+ C（统计量）串成完整流程，接入阶段3 C2 的真实 LISA-Taiji ORF。

## 流程

```
阶段3 C2 (真实 Γ^I, Γ^V) → A (模拟数据) → B (反解 Î, V̂) → C (Z-score, p-value, SNR)
```

## 输入

- 阶段3 C2: `02_真实LISA_Taiji网络手征ORF全频率计算.py` 中的 `asm.gamma_TDI_channels()`
- 噪声模型: LISA + Taiji 各臂噪声 S_n(f)（文献值）

## 输出

- 灵敏度曲线（真实 ORF）
- 注入-恢复演示（给定信号参数 → 报告是否探测到、误差多大）
- 与 JCAP Fig.5 场景的量级对比
