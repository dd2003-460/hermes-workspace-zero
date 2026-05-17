# 全局任务板

**最后更新**: 2026-05-17（DistCat v5 最终编译修复 + arXiv v6 提交包 + 三篇论文就绪）

---

## 当前 Focus

### 高优先级（需立即执行）

| 任务 | 项目 | 状态 | 阻塞 |
|------|------|------|------|
| arXiv 提交 DistCat v5 (math.CT) | D1-academic-AI | 📋 就绪 (v6 tarball 356KB) | 作者确认 |
| arXiv 提交 BayesFrame v2.0 (q-bio.NC) | D1-academic | 📋 就绪 (0 err, 9 warn, 11p) | 作者确认 |
| arXiv 提交 D1-grav-waves v4 (gr-qc) | D1-grav-waves | 📋 就绪 (0 err, 1 warn, 10p) | 作者确认 |
| DistCat v5 编译验证 + bug 修复 | D1-academic-AI | ✅ 完成 (0 err, 0 warn, 15p) | — |
| D1-grav-waves v4 figure/Unicode 修复 | D1-grav-waves | ✅ 完成 (0 err, 1 warn, 10p) | — |
| DistCat v5 arXiv 提交包 v6 更新 | D1-academic-AI | ✅ 完成 (v6 356KB, 含 5/16 修复) | — |

### 进行中

| 任务 | 项目 | 状态 | 阻塞 |
|------|------|------|------|
| 项目索引系统重构 | workspace | 🔄 进行中 | 无 |
| 搜索工具链部署 | workspace | ✅ 完成 | 无 |

---

## 项目任务索引

每个项目的详细任务在其 `tasks/` 目录下：

| 项目 | 任务文件 | 当前状态 |
|------|----------|----------|
| D1-grav-waves | [tasks/d1-grav-waves-tasks.md](D1-grav-waves/tasks/d1-grav-waves-tasks.md) | arXiv 提交包就绪 |
| D1-academic-AI | [tasks/D1-academic-AI-tasks.md](D1-academic-AI/tasks/D1-academic-AI-tasks.md) | DistCat v5 构建中 |
| bayesian-frame | [bayesian-frame/tasks/](D1-academic/bayesian-frame/tasks/) | JCR 论文就绪 |
| D1-anyon-hawking | [tasks/](D1-anyon-hawking/tasks/) | 原始研究 |

---

## 已完成（近期）

| 任务 | 项目 | 完成时间 |
|------|------|----------|
| DistCat v5 最终编译修复 (194+, 0 err, 0 warn, 15p) + arXiv v6 提交包 | D1-academic-AI | 2026-05-17 |
| DistCat 2-范畴严格证明（12 项公理验证） | D1-academic-AI | 2026-05-13 |
| D1-grav-waves v4 figure/Unicode 修复 (0 err, 1 warn) | D1-grav-waves | 2026-05-17 |
| BayesFrame v2.0 编译验证 (0 err, 9 warn) | D1-academic | 2026-05-17 |
| BayesFrame JCR 论文 v2.0（11p/871K, 0 errors） | D1-academic | 2026-05-13 |
| D1-grav-waves arXiv 提交包 v4（10p/303K, 24 refs） | D1-grav-waves | 2026-05-13 |
| 搜索工具链部署（search_web.py） | workspace | 2026-05-16 |
| 项目索引分类修复 | workspace | 2026-05-16 |

---

## 阻塞项

|| 阻塞项 | 影响项目 | 需要 |
||--------|----------|------|
|| **MITM SSL 拦截** | 所有 arXiv 提交 | 切换网络/关闭 SSL 检测/加 CA 到信任库 |
|| arXiv 提交需作者确认 | DistCat v5, BayesFrame v2.0, D1-grav-waves v4 | 作者批准 |

---

## 2026-05-17 审计修复

### 新增原则（已加入 AGENTS.md）

**核心期望**：ralph-loop.global.md — 像一个真正的人一样思考和推进，不是像工具一样等待确认。

**分类：**
1. **读取优先级**（最高优先级）— ralph-loop.global.md > AGENTS.md > loop/ > memory/
2. **行为红线** — 遇到用户阻塞时跳过（§5），永远不要 LOOP COMPLETE，每次迭代必须有可验证产出
3. **自主执行** — 不要问"你选哪条"，用置信度驱动决策，边界内默认自主执行

### 修复完成

- [x] AGENTS.md 加入 ralph-loop.global.md 最高优先级读取
- [x] AGENTS.md 加入"像人一样思考"行为原则
- [x] AGENTS.md 加入 "没有 LOOP COMPLETE" 红线
- [x] AGENTS.md 加入 "每次迭代必须有可验证产出" 要求

### 待执行（下一步）

- [ ] ralph-loop.global.md iteration 150 为什么只有 iteration-1.md 产出？需要检查 .ralph/ 状态
- [ ] 副脑循环需要重启或重建
- [ ] 三篇论文在 MITM 问题时可先推进（做图/数值/讨论扩展，不是干等提交）

---

*任务状态以各项目 tasks/ 目录为准。全局 TASKS.md 只保留高层摘要。*
