# 转向空间基 OLC SNR 分析 — 项目规划

## 决策 (2026-06-29)
- **从**：地面部署 OLC（L=10m, σ_y=10⁻¹⁷），已被 Schaffrath/Gaudio 证伪
- **到**：空间基 OLC SNR 分析，针对 Lou et al. (2026) constellation 参数

## 核心论证
1. 地面 OLC coupling = 0 (trapping 抑制)
2. 空间 OLC coupling 不为零 (自由下落满足测地线方程)
3. Lou 计算了空间 OLC 的 ORF，但**没做完整 SNR**
4. 我们已有的计算框架（ORF solver, SNR solver, noise model）完全可复用
5. **新缺口**：给定 Lou 的 constellation 参数 → 完整 SNR + 频段对比 + 混合网络增益

## 具体任务

### P1: Lou constellation 参数提取 (最高优先级)
- 输入：Lou et al. (2026) arXiv:2602.05714 全文
- 输出：constellation 参数表（臂长数、轨道高度、钟类型、噪声水平）
- 验证：与论文原文逐值对照

### P2: 空间 OLC SNR 计算
- 复用：scripts/olc_snr_solver.py（原脚本，用空间参数覆盖）
- 输入：Lou 参数 + 我们的 ORF solver
- 输出：SNR vs 观测时间曲线（多个 Ω_GW 值）
- 验证：与 LISA 在同一 Ω_GW 下的直接对比

### P3: 频段对比图
- 对比 OLC 空间基 vs LISA vs Taiji 的灵敏度曲线
- 频率范围：10⁻⁵ Hz 到 10³ Hz
- 验证：LISA 曲线与已发表论文对照

### P4: 混合网络增益量化
- 复用：scripts/06-olc-lisa-mixed-network.py
- 改进：用空间参数替代地面参数
- 输出：OLC-LISA 联合 SNR vs 单独 LISA SNR

## 不做的内容
- [C] 不等臂构型：耦合为零时几何优化无意义（在空间基也无效，因为 ORF 已扁平化）
- [G] 各向异性搜索：需要极高 SNR 先决条件
- [D] ORF 构型优化：Lou 已经计算了主要构型

## 时间估算
- P1: 1-2 小时
- P2: 半天
- P3: 半天
- P4: 半天
- **总计：~2-3 天**

## 前提依赖
- [x] Schaffrath/Gaudio 文献验证已完成
- [x] 计算框架（ORF, SNR, noise）可用
- [ ] Lou 论文全文获取（raw/楼明智论文OLC.pdf 可能已有）
- [ ] 用户确认转向（决策需要用户点头，但代码框架可并行搭建）
