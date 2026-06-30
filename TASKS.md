**最后更新**: 2026-06-23（loop状态管理改造完成）

---

## ✅ 已完成（2026-06-23）

**Loop 状态管理改造**：
- 各项目 `loop-state.json`（固定路径）
- `projects/ACTIVE.md`（自动聚合面板）
- `scripts/aggregate-active.sh` + `scripts/ralph-sync.sh`
- RALPH stop-hook 集成（项目状态同步）
- AGENTS.md 阅读链路更新（4步→2步）

**2026-06-27 迭代产出**：
- ADSL Phase 2 coord_transform_fields.md — Lie derivative Killing 对称验证完成
- QNM aim_research.md — Dehghan-Safari AIM 论文定位+方法研究完成
- RALPH iteration: 32→34

## ✅ 已完成（2026-06-14）

**项目级 beginner guide**：13 个项目全部完成（`notes/00-beginner-guide.md`）

---

## 🔴 当前 Focus

### D1-goal-investigation — Agent Goal + Loop 状态管理

| 任务 | 状态 | 说明 |
|------|------|------|
| loop 状态管理改造 | ✅ 完成 | 固定入口+双写机制，端到端验证通过 |
| 端到端 session 验证 | 📋 待验证 | 新session能自动到达项目状态 |
| Codex/Hermes 机制对比 | 📋 待开始 | — |
| Prompt 激发 AI 提问风格 | 📋 待开始 | — |

### 论文提交（阻塞）

| 论文 | 状态 | 阻塞 |
|------|------|------|
| DistCat v6 (math.CT) | 📋 就绪 | MITM SSL + 作者确认 |
| BayesFrame v2.0 (q-bio.NC) | 📋 就绪 | MITM SSL + 作者确认 |
| D1-grav-waves v4 (gr-qc) | 📋 就绪 | MITM SSL + 作者确认 |
| anyon-hawking (hep-th) | 📋 就绪 | MITM SSL + 作者确认 |
| EMRI-D26 resonance (gr-qc) | 📋 就绪 | MITM SSL + 作者确认 |
| Chimera v3 (Chaos) | 📋 就绪 | MITM SSL + 作者确认 |
| QBH negative result (gr-qc/hep-th) | 📋 就绪 | MITM SSL + 作者确认 |

---

## 项目任务索引

| 项目 | 任务文件 | 当前状态 |
|------|----------|----------|
| D1-grav-waves | tasks/TASKS.md | arXiv 提交包就绪 |
| D1-persona-align | tasks/TASKS.md | T1-T47 完成 |
| D1-academic-AI | tasks/TASKS.md | DistCat + Chimera + EMRI 就绪 |
| D1-academic (BayesFrame) | bayesian-frame/tasks/ | JCR 论文 arXiv 就绪 |
| D1-anyon-hawking | tasks/TASKS.md | arXiv-ready |
| D1-aging-economics | TASKS.md | Phase 0-7 完成 |
| D1-goal-investigation | tasks/TASKS.md | Agent 行为研究中 |
| D1-area-quantized-black-hole-QNM | tasks/TASKS.md | ✅ I-1~I-6 + paper → 审稿意见:转向Teukolsky+Echoes → P1 conventions ✅, Teukolsky-RW duality ✅, P2 Dehghan-Safari AIM 研究完成, 待实施 Schwarzschild 回归 |
| adsl-spin-connection | workspace/conventions.md | ✅ Phase 0 convention ✅, Phase 1 xact代码+静态黑洞解+EOM验证+变分方程 ✅, Phase 2 coord_transform 场Killing对称验证 ✅, 待推进BTZ pole-skipping |
| D1-memory | — | 归档完成 |
| D1-continuous-agent | — | Hermes Gateway Hook 验证完成 |
| D1-writing | — | 活跃 |
| cosmos-thesis-review | — | 评审通过 |

---

## 阻塞项

| 阻塞项 | 影响 | 需要 |
|--------|------|------|
| **MITM SSL 拦截** | 所有 arXiv 提交, pip 安装 | 切换网络/关闭 SSL 检测/加 CA |
| **作者确认** | 7 篇论文提交 | 成璐批准 |

---

*任务状态以各项目 tasks/ 目录为准。全局 TASKS.md 只保留高层摘要。*
