# Memory Index

> 最后更新: 2026-11-02

## Active Projects

### 1. GW-BacQFT (D1-grav-waves)
- **状态**: ✅ 完成 — arXiv pack v16 ready，待成璐手动上传
- **核心**: Source Discrimination in PTA via Extended Functorial QFT
- **目录**: `projects/理论物理/D1-grav-waves/papers/2026-GW-BacQFT/`
- **阻塞**: 需登录 arxiv.org/submission 上传

### 2. 手征 ORF 计算主线 (GW_ORF)
- **状态**: ✅ 阶段1-4 全部完成 + 论文含第四部分 + 真实ORF注入恢复验证通过
- **核心**: 引力波背景的手征（圆偏振）ORF 完整计算 + 探测统计量
- **目录**: `projects/理论物理/时钟与引力波响应/GW_ORF_研究项目/手征ORF计算_主线/`
- **关键发现**: Γ^V << Γ^I (4-6 orders)；三通道(X+Y+Z) V增益3→10×；X通道对手征有几何抑制；真实LISA-Taiji注入恢复 I无偏@f>2.5mHz, V亚单位σ@4mHz
- **论文**: `论文_完整组件级_复现与手征推广/` (两篇 MD+PDF，含 Stage 4 交叉引用 + 真实ORF验证行)
- **下一步**: 正式投稿版 LaTeX（可选）；Stage 3 D 混合网络/OLC（优先级最低）

### 3. PFB Rubric-v3 Benchmark
- **状态**: 正式实验完成 (7×3=21 run + 双裁判盲评 + 归因分析)
- **核心**: AI pipeline 评分标准消融实验
- **目录**: `pfb/bench/rubric-v3/`
- **关键结论**: D1 净效应≈0 (sham打掉), D2 边际+5.06 稳健
- **剩余**: G1b 异族 judge (blocked-on-external), batch2 第二域数据

### 4. Motivation Society (写作)
- **状态**: ✅ 全部完成 (Part I-V, 14 chapters, main2.pdf 93pp, 0 errors)
- **目录**: `projects/写作-社会系统/D1-writing/motivation_society/`
- **分支**: test @ f894e44 (main2.pdf rebuilt 2026-11-02)
- **下一步**: 成璐审阅后决定是否合并到 main

### 5. D2 Efficient Propagation Book
- **状态**: 交叉引用闭环，P2 实验计划就绪 (需 30 天实际执行)
- **目录**: `projects/写作-社会系统/D2-efficient-propagation-book/`

### 6. 长寿正交贡献 MR (D1-longevity-orthogonal)
- **状态**: ✅ 阶段2 MR v3 完成 (position-based clumping, 无外部LD参考) — 方向反转确认
- **核心**: GIANT/GLGC 暴露 × FinnGen R13 结局的两样本 MR (IVW/Egger/WMed, 10 pair)
- **关键结果 (v3)**: BMI→CHD Egger OR=0.847; LDL→CHD Egger OR=0.807 (保护性/无效应); 之前 no-clump OR=1.17/1.40 为 LD 块相关 SNP 伪影; 判定=免费数据约束下无稳健因果信号
- **方法限制**: 10Mb 位置窗口替代真 LD clumping (r²=0.001); BMI 67 + LDL 53 instruments
- **阻塞**: 1000G v3 EUR ref (真 LD clumping 验证) + OpenGWAS token (Step3 condition-F)
- **目录**: `projects/健康长寿/D1-longevity-orthogonal/repo/`

### 7. 金融 D1 — Crypto 日频信号探索 (F 系列)
- **状态**: ✅ CLOSED (负面结果) — 8 个独立假设全量回测完成
- **核心结论**: 免费公开数据约束下不存在可交易的日频统计套利/择时信号 (conf 0.85)
- **机制发现**: ① 动量延续 > 超调回归 (胜率 70-87% 翻转后) ② 免费信息高度同源 (ρ=0.3-0.5) ③ 信号以年为单位衰减
- **收口报告**: `projects/金融/D1-financial-market-analysis/loop-artifacts/stages/exploration/f-series-summary-report.md`
- **如需继续**: Deribit IV 采集器 (零成本, 3 个月积累) 或 Glassnode free tier (90 天历史)

## 已归档/阻塞
- DistCat v5 / BayesFrame v2.0: 等 GW-BacQFT 提交后处理
- Batch2 第二域数据: blocked-on-external
- Family-upgrade / kappa-recalibrate: blocked-on-external

### 8. Decomp Bench (T7/T8)
- **状态**: T7 全收口 (T7.3 v2 point=60219, interval_80=[60129,61227]); T8 Part B 文献调研完成 (arena, 7 sources); T8 Part C 待实验设计
- **核心**: prompt-first 消融研究 — L1 组件级 + pipeline 阶段级
- **T7.3 v2**: M4 EWMA+weekday 主模型, holdout MAPE 0.511%, 嵌套覆盖率 miss 如实记录 (regime 切换导致区间偏窄)
- **T8 Part B 关键发现**: Q1 阶段效应不均但非纯 prompt 效应; Q2 critic 有效条件=可定位可执行反馈; Q3 边际递减有例证非通用规律; Q4 L1→pipeline=待测方向不可直接迁移
- **阻塞**: T8 Part C + T17 scoring run 需 arena + ninfer 基础设施
- **目录**: `projects/decomp/`
