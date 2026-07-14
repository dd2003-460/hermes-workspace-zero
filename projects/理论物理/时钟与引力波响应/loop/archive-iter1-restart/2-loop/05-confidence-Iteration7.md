# 2-loop/05-confidence (Iteration 7) — Confidence Assessment

**状态**: completed
**完成时间**: 2026-07-06

## 置信度评估

### 代码实现置信度

| 评估维度 | 置信度 | 说明 |
|---------|--------|------|
| E 变量定义 (CW sum) | 0.95 | 经 _diag_orlando_e.py 验证，符合 Orlando 2021 定义 |
| Sky-max 计算 | 0.90 | 逐像素归一化，Cauchy-Schwarz bound 验证通过 |
| Transfer function 一致性 | 0.90 | taiji TF (Michelson) 与 olc TF (Lou Eq. 2-30) 分别正确 |
| Self-correlation 恒等式 | 0.95 | 数值验证: |Gamma^V| < 1e-18 |
| 对称性检查 | 0.95 | inclination scan 关于 45° 对称 |
| 网格收敛 | 0.70 | 使用 128×256 (sky-max) 和 64×128 (sky-avg)，未做收敛性分析 |

**代码实现整体置信度: 0.88**

### 科学结论置信度

| 结论 | 置信度 | 说明 |
|------|--------|------|
| 单三角 Michelson-like chiral ORF = 0 | 0.95 | 代码验证 + 对称性论证 + 多迭代一致 |
| E 变量打破镜像对称 → 有限手征响应 | 0.90 | 物理机制清晰，数值验证通过 |
| Sky-max norm_V ~ 1.0 (Cauchy-Schwarz bound) | 0.95 | 理论上限，数值达到上限 |
| Orlando |Gamma^V|_max ~ 0.3 为近似 figure 读数 | 0.75 | 解释合理，但无直接证据 |
| 归一化后手征响应频率无关 (纯几何) | 0.85 | 频率扫描平坦，但未做高精度网格 |
| 不同轨道面倾角打破对称 → 非零 chiral | 0.90 | 物理机制清晰，数值验证通过 |
| OLC×LISA 可比性 | 0.60 | OLC 传递函数约定尚存小争议 (Lou Eq. 2-30 vs standard) |

**整体科学置信度: 0.82**

### 与 1-loop 置信度对比

| 轮次 | 置信度 | 变化 |
|------|--------|------|
| Iteration 5 (初始) | 0.71 | baseline |
| Iteration 6 (调查报告) | 0.82 | +0.11 (文献调研 + 物理机制理解) |
| Iteration 7 (2-loop 执行) | 0.82 | 持平 (脚本验证通过但未解决争议) |

### 不确定因素

1. **Orlando 的 0.3**: 可能使用了不同的归一化约定或 sky-max 定义。需要直接阅读原文确认。
2. **OLC 传递函数**: Lou Eq. 2-30 的空间 OLC 与地面 OLC 的传递函数不同。空间版本的确认不充分。
3. **网格分辨率**: sky-max 对网格依赖较大 (128×256 足够，但未做收敛性分析)。

### 进入下一轮的条件

置信度 0.82 >= 0.75 门槛，满足进入下一轮条件。下一轮建议:
1. 直接阅读 Orlando 2021 原文确认归一化和 sky-max 定义
2. 验证空间 OLC 传递函数约定
3. 可扩展到 4+ 星座网络以提升 chiral SNR
