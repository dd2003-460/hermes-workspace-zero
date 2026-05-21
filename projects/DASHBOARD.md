# D1 项目仪表板 — 持续监控

> **最后更新**: 2026-05-20 (iteration 34)
> **状态**: persona-align T1-T11 ✅ (113 samples, LoRA pipeline complete, 5 iters trained, inference verified)

---

## 论文状态

| 论文 | 版本 | 状态 | tarball | PDF | Figures | 进度 |
|------|------|------|---------|-----|---------|------|
| DistCat v5 | v5/v6 | arXiv-ready | 356K | 846K/16p | 2 | 100% |
| D1-grav-waves | v4 | arXiv-ready | 127K | 1.06MB/12p | 2 | 100% |
| BayesFrame | v2.0 | arXiv-ready | 1341K | 1.64MB/13p | 5 | 100% |
| D40 | v2 | arXiv-ready | 12K | 800K/15p | 0 | 100% |
| EMRI-D26 | v0.9.0 | arXiv-ready (w/Appendix A + 2 figures) | 276K | 392K/14p | 2 | 85% |
| anyon-hawking | v0.1 | arXiv-ready (English abstract) | — | 219K/8p | 0 | 65% |

## 工具链

| 工具 | 状态 | 更新 |
|------|------|------|
| compile_paper.sh | ✅ 编译验证 | 2026-05-17 |
| arxiv_submit.sh | ✅ | 2026-05-12 |
| arxiv_submission_checklist.sh | ✅ | 2026-05-17 |
| arxiv_cat.py | ✅ 论文搜索 | 2026-05-17 |
| arxiv_cats.py | ✅ 分类推荐 | 2026-05-17 |
| arxiv_prepare.py | ✅ 提交包准备 | 2026-05-17 |
| project_health_check.sh | ✅ | 2026-05-17 |
| index_verifier.py | ✅ 索引校验 | 2026-05-17 |
| search_web.py | ✅ | 2026-05-16 |

## 探索记录

| 数量 | 项目 | 最新文件 |
|------|------|----------|
| 21 | D1-grav-waves | 探索笔记 |
| 62 | D1-academic-AI | 86-emri-appendixA-integrated |
| 1 | D1-anyon-hawking | anyon-hawking-paper.pdf |
| 0 | D1-persona-align | T6: Hermes chenglu personality deployed |
| 2 | bayesian-frame | 探索记录 |
| 0 | D1-academic | INDEX.md (新建) |
| 0 | D1-continuous-agent | INDEX.md (新建) |
| 0 | D1-writing | INDEX.md (新建) |

## 路线图

| 阶段 | 行动 | 状态 |
|------|------|------|
| 现在 | persona-align: T6 完成, T5b LoRA 数据收集 (需要更多对话样本) | 就绪 |
| 现在 | arXiv 等待作者确认 + MITM SSL 修复 | 阻塞 |
| MITM 解决后 | 三篇论文 arXiv 提交 | 就绪 |
| arXiv IDs 获取后 | 桥梁论文 (2-Cat Classification) 起草 | 规划中 |
| 并行 | EMRI Appendix A 整合 | ✅ 完成 (已整合入 EMRI-D26 paper) |
| 并行 | anyon-hawking 论文 | 编译通过 (376KB, 需英文翻译) |

## 健康检查

- 项目标准结构: 7/7 PASS (INDEX.md + memory/ + tasks/ + raw/)
- 递归索引: D1-academic/学术/ 12/12, D1-writing/写作/ 5/5 ✅
- 编译: 所有论文 0 错误
- __pycache__: 12K (忽略)
- .bak 文件: 1 (最新状态快照)
- persona-align: T1-T6 ✅ (92 samples LoRA dataset, scorer calibrated 3-test PASS, chenglu eval 100%, training script ready)
- 重复文件: 已清理
- stale tarballs: 4 removed (DISTCAT v2-v5)
- project_health_check.sh: bug fixed (tasks detection)

---

*Ralph Loop 持续运行中。Iteration 12 (自动运行)。所有系统合规。*
