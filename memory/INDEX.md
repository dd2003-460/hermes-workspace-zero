# Memory Index

> 最后更新: 2026-11-03 (r274)

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
- **状态**: 正式实验完成 (7×3=21 run + 双裁判盲评 + 归因分析); **rubric v3 冻结** (r249f: AC1 0.956/AC2 PASS/AC3 PASS, AC4 移出验收 overall_pass=True); **pilot-matrix 收口** (9 run 三变体 + judge 双判 κ=0.857 n=162 过门禁, O1 κ=0.506 唯一弱项)
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
- **状态**: ✅ 阶段2 MR v3 完成 + paper draft 一致性修复 (9/10 reversed, Thorleifsson) — 方向反转确认
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
- **状态**: T7 全收口 (T7.3 v2 point=60219, interval_80=[60129,61227]); T8 Part B 文献调研完成 (arena, 7 sources); **T8 Part C 探索性收口**（两轮对抗核验 FAIL×2+partial×4 → freeze 段三域负效应方向稳健，确认性实验等四条件）; **T21 收口完成 (r256: flagship-eval S3 按 T21-RR 实测锚定重算 + 主报告 §9.2 发现5 并入)** — GPU 选型主线 T19→T20→T21 闭环; **T17 rubric v2 修正完成 (r261: C4 判据放宽 + scores.json 全量补齐 + T17-REPORT 重新生成)** — 泛化 bench 四域结论稳定; **T17-full LoCoMo 补跑在途 (r29x, 11-04: conv0 修复后重跑 151/152 ~80% top_10, conv1 re-ingest 答题中; checkpoint run_id 校验缺陷已修 13f8be5 — smoke01 残留污染根因闭环; fork main @ 423ec17)**
- **核心**: prompt-first 消融研究 — L1 组件级 + pipeline 阶段级
- **T7.3 v2**: M4 EWMA+weekday 主模型, holdout MAPE 0.511%, 嵌套覆盖率 miss 如实记录 (regime 切换导致区间偏窄)
- **T8 Part B 关键发现**: Q1 阶段效应不均但非纯 prompt 效应; Q2 critic 有效条件=可定位可执行反馈; Q3 边际递减有例证非通用规律; Q4 L1→pipeline=待测方向不可直接迁移
- **阻塞**: T8 Part C 确认性实验等 arena binding 重绑 + ninfer :8000/:8099 恢复（r259 复查仍 down）; 异源 judge (Fleiss κ) 卡 G1b family_check 模型身份披露
- **目录**: `projects/decomp/`

### 9. BH Mass Spectrum (bh-mass-spectrum)
- **状态**: 任务 A (P0-1/P0-2) v2 修复完成 @ 6ab6336; 任务 C (遗迹MF+PISN间隙图) subagent 执行中
- **核心**: TNG 目录黑洞质量函数 + 遗迹推前质量谱 + PISN 间隙带
- **v2 修复**: 种子 BH 排除 (m_bh>=1e-7) + 占据率分母改全晕群体 + LOGM_H_EDGES 单位修正
- **验证**: f_occ(z=0, >1e6) @ logM_h>=1.5 = [0.972, 0.999, 1.0] → PASS
- **GWTC-4.0**: 观测数字表已落盘 (literature/notes/gwtc4-bhmf-numbers.md)
- **卡人项**: 任务 C 取消与否待成璐确认 (projects/理论物理/bh-mass-spectrum/memory/task-c-status-correction.md)
- **目录**: `projects/理论物理/bh-mass-spectrum/bh-mass-spectrum/`

### 10. Persona Prompt Lab (persona-prompt-lab)
- **状态**: ✅ P0 全部关闭 @ 53d478e — testset-v3 (50/50) + BM25 R@5=0.56 + local embedding (MiniLM-L12-v2) R@5=0.58，均未达 80% 线
- **核心**: persona prompt 实验室 (bench/research/memory/tasks)
- **结论**: 80% 召回瓶颈在测试集语义重叠度，非算法；后续改测试集 > 换 bge-m3，低优先级
- **目录**: `projects/persona-prompt-lab/`

### 11. D1 Video Recreation (batch 系列)
- **状态**: ✅ batch-12 完成 (E29-E32, status-table 42) + ✅ batch-13 完成 (r273: E33-E36 4/4 本地降级执行, 三件套 9/9 checks PASSED ×3 + E33 10/10, 1800帧渲染 + mp4, fca6e22 合并, goal d1-batch13-local-E33 completed)
- **核心**: 叙事视频复刻 pipeline（render/check/build_audio 三件套 + overlap check 门禁）
- **教训 (r272)**: arena E2B 沙箱故障 → 本地降级通道验证可用（conf−0.2）；check 脚本常见 bug = BUBBLE 对象解构 / 压暗后颜色容差匹配
- **目录**: `d1-video-recreation/` (main @ a615c4f)

## 全局文件（非项目）

| 文件 | 说明 | 状态 |
|------|------|------|
| `memory/arxiv_submission_status.md` | arXiv 提交台账：GW-BacQFT v16 + GW-ORF + DistCat v5 + BayesFrame v2.0 共 4 篇 tarball 就绪，全部待成璐手动上传 | ⏳ blocked-on-human |
| `memory/arena-audit-report-2026-10-20.md` | hermes-workspace-zero 仓库结构审计（10-20）：研究内容质量高、状态治理失效的完整证据链 | ✅ 历史存档 |
| `memory/fault-index.md` | 故障索引：所有通道/工具/环境故障登记表（链路+具体报错+根因+status），故障结论写入前必查；两条浏览器链路区分规则在此 | 🔄 持续追加 |
| `memory/insights/2026-10-31-cross-repo-findings.md` | 跨仓精彩结论盘点（pfb + decomp）：调研得到 vs 负面结果 + SOP 化去向 + r259/r274 增量 | 🔄 持续追加 |
| `memory/notes/ACADEMIC-STATUS.md` | 全局 arXiv 论文索引（178 篇 across 9 项目，自动生成） | 🔄 定期更新 |
| `memory/research/27b-local-deployment-hardware-2026-10.md` | 27B 本地部署硬件调研 | ✅ 完成 |
| `memory/archive/dashboards/` | 旧仪表板归档（dashboards-all.jsonl 26 条 + 5 个 2026-05 单文件已移入，r274b） | ✅ 归档 |
| `memory/archive/` | 统一归档区（r275 归一：DASHBOARD-2026-05-stale + 2026-05-subbrain 报告×19 + ONBOARDING 陈旧件；原 notes/archive/ 已并入） | ✅ 归档 |
| `memory/notes/cron-adaptive-poll-r185.md` | cron 自适应轮询实现记录（jobs.py 两补丁 + adaptive_poll 标记，r185） | ✅ 完成 |
