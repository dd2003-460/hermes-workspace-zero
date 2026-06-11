# 全局任务板

**最后更新**: 2026-06-11（ralph-loop iteration 505: 命名规范修复, d1-self-evolution → D1-self-evolution）

---

## ralph-loop 迭代记录

### Iteration 505 — 2026-06-11

**执行内容：**

1. ✅ 读取 ralph-loop.global.md — 确认 TASKS.md 为唯一状态源
2. ✅ 读取 AGENTS.md — 确认分类规范和命名规范
3. ✅ 读取 TASKS.md — 识别可执行任务（跳过作者阻塞项）
4. ✅ 运行 health check — 验证 workspace 结构合规性（10/10 ✅）
5. ✅ 扫描 workspace 结构 — 发现 d1-self-evolution 命名不规范
6. ✅ 重命名 d1-self-evolution → D1-self-evolution — 符合 AGENTS.md 递归编号规范
7. ✅ 更新 projects/INDEX.md — 修复 DSE.1 索引引用

**健康检查结果：**

| 指标 | 值 |
|------|-----|
| 项目数 | 10（D1-* 格式） |
| arXiv tarballs | 10 |
| 编译 PDF | 139 |
| 合规项目 | 10/10 ✅ |
| Health | GOOD |

**结构调整：**

| 操作 | 说明 |
|------|------|
| d1-self-evolution → D1-self-evolution | 符合 AGENTS.md 命名规范（D*-*, d*-*.py） |
| projects/INDEX.md 更新 | 修复 [DSE.1] 索引引用 |

---

### Iteration 501 — 2026-06-11

**执行内容：**

1. ✅ 读取 ralph-loop.global.md — 确认 TASKS.md 为唯一状态源，跳过作者阻塞
2. ✅ 修复 `scripts/project_health_check.sh` — 支持递归搜索嵌套项目（从 0 projects 到 10 projects）
3. ✅ 创建 `D1-aging-economics/tasks/` — 补齐标准项目结构
4. ✅ 创建 `D1-goal-investigation/memory/INDEX.md` + `tasks/TASKS.md` — 补齐空目录
5. ✅ 更新 `projects/INDEX.md` — 删除 loop/ 引用，添加 D1-goal-investigation
6. ✅ 验证最终结构 — 10 个项目全部合规（INDEX.md + memory/ + tasks/）

**健康检查结果：**

| 指标 | 值 |
|------|-----|
| 项目数 | 10 |
| arXiv tarballs | 10 |
| 编译 PDF | 139 |
| 合规项目 | 10/10 ✅ |
| Health | GOOD |

---

## 当前 Focus


### 🔬 Claude Code 动态工作流与团队功能研究

|| 任务 | 状态 | 说明 |
|------|------|------|
| **动态工作流部署** — 研究如何让Claude Code按步骤强制遵循流程 | 📋 调研完成，待验证 | 见下方方案A-D |
| **CC 团队功能验证** — 固定角色分配任务，验证现有 ralph-loop-next 团队配置 | ❌ 配置已丢失 | `~/.claude/teams/ralph-loop-next/config.json` 不存在 |
| **动态工作流 + CC团队 集成验证** — 测试方案A/B与现有团队配置结合 | ❌ 未开始 | 下一步实验方向 |

**研究结论摘要**：

1. **动态工作流** — CC 有4种方案（纯prompt状态对象 → hooks拦截 → CLAUDE.md约束 → 工具化状态管理），可靠性递增。
2. **团队功能** — 原有6角色固定分工配置已丢失（`~/.claude/teams/` 不存在）。需重新建立。
3. **与prompt深度推理研究关联** — 团队角色的固定prompt就是"模板化prompt"实践形态。

---

## 高优先级（需立即执行）

| 任务 | 项目 | 状态 | 阻塞 |
|------|------|------|------|
| Prompt深度推理激发研究 | D1-persona-align | ✅ 已完成 (iteration 234-235) | — |
| arXiv 提交 DistCat v5 (math.CT) | D1-academic-AI | 📋 就绪 (16p, 2 figures, v6 tarball) | 作者确认 |
| arXiv 提交 BayesFrame v2.0 (q-bio.NC) | D1-academic | 📋 就绪 (13p, 5 figures, 0 err) | 作者确认 |
| arXiv 提交 D1-grav-waves v4 (gr-qc) | D1-grav-waves | 📋 就绪 (12p, 2 figures) | 作者确认 |

## 进行中

| 任务 | 项目 | 状态 | 阻塞 |
|------|------|------|------|
| EMRI-D26 resonance paper v1 | D1-academic-AI | ✅ 就绪 (400+ lines, 14p/392KB) | 作者确认 |
| anyon-hawking paper | D1-anyon-hawking | ✅ arXiv-ready (442 lines, 8p/219KB) | 作者确认 |
| DistCat v5 编译验证 + bug 修复 | D1-academic-AI | ✅ 完成 | — |
| 全量合规补齐 (3 项目 tasks/memory 占位) | workspace | ✅ 完成 | — |
| project_health_check.sh bug 修复 | scripts | ✅ 完成 | — |
| projects/INDEX.md 删除 loop/ 引用 | workspace | ✅ 完成 | — |

## 长期维护

| 任务 | 项目 | 状态 | 阻塞 |
|------|------|------|------|
| D1-persona-align 完整分析体系 | D1-persona-align | ✅ T1-T47 完成 + persona-v3 + MATO DPA v2 + unified_eval + 22 篇研究 + 52 文件增强 + 三层评估 + 系统清理 (迭代 267-360) | — |

---

## 项目任务索引

每个项目的详细任务在其 `tasks/` 目录下：

| 项目 | 任务文件 | 当前状态 |
|------|----------|----------|
| D1-grav-waves | [tasks/TASKS.md](projects/理论物理/D1-grav-waves/tasks/TASKS.md) | arXiv 提交包就绪 |
| D1-persona-align | [tasks/TASKS.md](projects/AI-计算科学/D1-persona-align/tasks/TASKS.md) | T1-T47 完成 + 评估基线 verified |
| D1-academic-AI | [tasks/TASKS.md](projects/AI-计算科学/D1-academic-AI/tasks/TASKS.md) | DistCat v6 arXiv 就绪 (阻塞于作者确认) |
| bayesian-frame | [tasks/bayesian-frame-tasks.md](projects/AI-计算科学/D1-academic/bayesian-frame/tasks/bayesian-frame-tasks.md) | JCR 论文 arXiv 就绪 |
| D1-anyon-hawking | [tasks/TASKS.md](projects/理论物理/D1-anyon-hawking/tasks/TASKS.md) | arXiv-ready v4 |
| D1-aging-economics | [TASKS.md](projects/写作-社会系统/D1-aging-economics/TASKS.md) | Phase 0-7 全部完成 |
| D1-continuous-agent | [INDEX.md](projects/AI-计算科学/D1-continuous-agent/INDEX.md) | Hermes Gateway Hook 验证完成 |
| D1-goal-investigation | [tasks/TASKS.md](projects/AI-计算科学/D1-goal-investigation/tasks/TASKS.md) | 结构已修复，需重新建立探索数据 |

---

## 阻塞项

| 阻塞项 | 影响项目 | 需要 |
|--------|----------|------|
| **MITM SSL 拦截 (系统级)** | 所有 arXiv 提交, pip 包安装 | 切换网络/关闭 SSL 检测/加 CA 到信任库 |
| arXiv 提交需作者确认 | DistCat v5, BayesFrame v2.0, D1-grav-waves v4 | 作者批准 |

### QQ 远程通信

- **用途**：成璐通过 QQ 远程联系 AI（ralph-loop 代理）
- **配置**：`~/.cc-connect/config.toml`（app_id=1903885314）
- **当前状态**：gateway 已连接
- **已知问题**：消息乱序/丢失

### arXiv 提交包更新

| 项目 | 论文状态 | PDF | 说明 |
|------|----------|-----|------|
| DistCat v5 | 📋 就绪 | 16p/846KB, 2 figures | — |
| D1-grav-waves v4 | 📋 就绪 | 12p/1.06MB, 2 figures | — |
| BayesFrame v2.0 | 📋 就绪 | 13p/1.64MB, 5 figures | — |

---

*任务状态以各项目 tasks/ 目录为准。全局 TASKS.md 只保留高层摘要。*
