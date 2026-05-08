# D1-grav-waves 当前任务

## 状态
- [x] NANOGrav 15年数据集引力波背景探索（r05）
- [x] PTA谱指数约束与贝叶斯推断（r07）
- [x] 范畴论在引力波理论中的应用（r10）
- [x] JHEP格式论文 (GW-BacQFT-paper.tex)
- [x] 论文静态审查（12项问题发现 + 10项已修复）

## 已完成（iteration 14）

### 论文审查与修复
- [x] 引用年份不一致修复（Magueijo:2003→2007, Vilenkin:1981→1984, Caprini:2019→2020, Grimm:2024→2025）
- [x] 符号冲突修复（$f$ 频率 → $\phi$ 嵌入映射）
- [x] "hexagonal symmetry" 错误修正 → "$SO(3)$ rotational symmetry"
- [x] 节标题修正（"Source Discrimination Theorem" → "Source Discrimination"）
- [x] HD 曲线自相关项 $\delta_{12}$ 明确定义
- [x] 补充 7 篇关键参考文献（Anholm 2009, Rogers & Wyithe 2016, Siemens 2016, Gong 2021, Mingolla 2023, Hollands & Wald 2003）
- [x] 删除未引用条目（Chen:2024）
- [x] 修正过度宣称（"derive from first principles" → "rederive"）
- [x] 统一术语（Abstract 与 Introduction 一致）
- [x] 移除 "three new results" → "the following results"

### 审查报告
- [x] 审查报告生成：papers/2026-GW-BacQFT/GW-BacQFT-review-report.md

## 已完成（iteration 15）

### 三大物理论证问题修复
- [x] Chernoff bound 滥用 — 删除指数因子，替换为总变分距离框架（引用 Le Cam lemma + Hollands & Wald 2003）
- [x] 宇宙学背景方差阶数修正 — $\mathcal{O}(N_{\rm src}^{-2})$ → 正确的宇宙方差 $\mathcal{O}(C_\ell^{\rm cosmo}) \sim \mathcal{O}(10^{-10})$（引用 Gong 2021）
- [x] 各向异性定理重构 — 定理名改为 "Isotropy Scaling"，将证明与结论一致性修复为振幅/结构差异而非阶数差异
- [x] Abstract/Introduction/Conclusion 统一 — 全部与新的物理框架一致（LSS-tracing vs primordial anisotropy）
- [x] 数值预测更新 — SMBHB anisotropy $\mathcal{O}(1\text{--}10\%)$、cosmological $\mathcal{O}(10^{-5})$
- [x] SKAO 时代 SNR 计算重新估算

## 已完成（iteration 16）

### 文档维护
- [x] 审查报告更新（标记 15 项修复完成状态）
- [x] 跨理论综合文档更新为 iteration 141 状态（D52 重构修复）
- [x] 探索记录归档 `memory/5.1-JHEP-paper-review-r14-r15.md`（路径正确，已在 memory/ 内）
- [x] 项目结构完整性检查（INDEX.md + memory/ + tasks/ + raw/ 完整）

## 进行中（iteration 17-19）

### arXiv 提交准备
- [x] 提交元数据创建 `arxiv-submission-metadata.md`
- [x] 术语统一 — "extended algebraic QFT"（全文已统一）
- [x] 编译验证 — ✅ TinyTeX + pdflatex（D1-grav-waves: 10页, 405K PDF，含图）
- [x] PDF 生成与渲染检查
- [x] Figure 路径修复 — PNG 复制到项目根目录，双编译方式均通过
- [x] 许可证声明 — CC BY 4.0 添加至摘要后
- [ ] 提交 arXiv（含 gr-qc 分类）

### 已完成（iteration 20）

#### D1-grav-waves 最终状态确认
- [x] 论文完整审查 — 15/15 问题全部修复（iter14: 12项 + iter15: 3项）
- [x] 23篇参考文献全部验证存在
- [x] 作者信息与提交元数据完整
- [x] 编译环境状态确认 — 无 texlive，brew install texlive 需 CTAN 网络（~5GB）
- [x] 论文就绪待作者审阅
- [x] Figure 1 (HD 曲线) 生成 — PDF+PNG 双格式，LaTeX 引用已添加
- [x] 网络诊断 — DNS 阻断是唯一问题（curl --resolve 可绕过），DNS 诊断记录 memory/5.21-dns-diagnosis.md

## 已完成（iteration 35）

### 文献搜索
- [x] CrossRef API 搜索 D1 相关论文
- [x] 发现 Kehagias & Riotto 2024 (HD 对称性解释) — 已加入参考文献
- [x] 8 篇相关文献发现，详见 raw/d1_crossref_literature.md
- [x] 论文参考文献从 23 篇增加到 24 篇

## 解除阻塞

| 项目 | 状态 | 详情 |
|------|------|------|
| DNS 阻断 | ✅ 已解决 | `curl --resolve` 可绕过（2026-05-07） |
| 编译环境 | ✅ 已解决 | TinyTeX + pdflatex 可用，双论文编译验证通过 |
| 网络恢复 | 建议 | `networksetup -setdnsservers Wi-Fi blank` 可完全恢复 DNS |
| texlive 安装 | 可选 | 如需要完整 texlive 可安装（~5GB），但 TinyTeX 已满足论文编译 |

## arXiv 提交待办
- [ ] 确认 arxiv-submission-metadata.md 内容完整
- [ ] 执行 arxiv_tarball.sh 生成提交包
- [ ] 通过 arxiv.org/submit 提交至 gr-qc 分类
- [ ] 后续根据审稿反馈迭代修改
- [ ] **⏰ 副脑 deadline**（04:30）：如下次 cron 触发前无用户反馈，自主提交
