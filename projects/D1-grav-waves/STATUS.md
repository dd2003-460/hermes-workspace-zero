<!-- DEPRECATED: 状态已迁移至 tasks/d1-grav-waves-tasks.md 和 INDEX.md -->
# D1-grav-waves 项目状态（废弃 — 见 INDEX.md）

## 当前状态: arXiv 就绪待提交（iteration 35+）

### 已完成
- [x] 领域探索笔记 (r01-r10): NANOGrav, PTA谱指数, 范畴论应用
- [x] 研究计划 (01-research-plan.md)
- [x] 原创性验证报告 (02-originality-verification.md)
- [x] JHEP格式论文 (GW-BacQFT-paper.tex)
- [x] 论文静态审查（12项问题发现 + 10项已修复，iteration 14）
- [x] 三大物理论证修复（Chernoff bound→总变分距离, 宇宙学方差修正, 各向异性定理重构，iteration 15）
- [x] 编译验证 — TinyTeX + pdflatex（10页, 405K PDF，含HD曲线图）
- [x] 许可证声明 — CC BY 4.0 添加
- [x] Figure 1 (HD 曲线) 生成 — PDF+PNG 双格式
- [x] 文献补充 — CrossRef API 发现 8 篇相关论文，新增 Kehagias & Riotto 2024
- [x] 24篇参考文献全部验证存在
- [x] arxiv_tarball.sh 生成提交包（136K）
- [x] arXiv 检查清单通过

### 论文详情
- **标题**: An Extended Functorial QFT Framework for Gravitational-Wave Source Discrimination in Pulsar Timing Arrays
- **位置**: papers/2026-GW-BacQFT/GW-BacQFT-paper.tex
- **对标**: JHEP/ApJL级别
- **页大小**: 10页, 405K（含图）
- **参考文献**: 24篇
- **关键创新**: 
  1. HD相关性从Extended Functorial QFT公理推导
  2. 源判别定理: SMBHB vs 宇宙学背景的代数判别条件
  3. 各向同性定理: O(N_src^-1) vs O(N_src^-2)标度律预测

### 下一步
1. [ ] **提交 arXiv**（gr-qc 分类）→ 等待作者确认
2. [ ] 等待审稿反馈迭代

### arXiv 就绪状态确认
| 检查项 | 状态 |
|--------|------|
| PDF 编译零错误 | ✅ |
| 图片引用正确 | ✅ |
| 参考文献完整可查 | ✅ |
| 许可证声明 | ✅ CC BY 4.0 |
| tarball 生成 | ✅ 136K |
| arxiv-submission-metadata.md | ✅ |
