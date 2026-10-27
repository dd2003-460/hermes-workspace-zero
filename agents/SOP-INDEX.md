# SOP 索引（Standard Operating Procedures）

> origin: ai · 2026-10-22 · 成璐指令"留个 SOP 索引"
> 用途：AI 快速查找所有标准操作流程，避免重复造轮子

## 1. 网页 AI 调研与核验

| SOP | 路径 | 说明 |
|-----|------|------|
| ego-browser Skill Index | `agents/ego-browser-index.md` | ego-browser 用法、命令、注意事项 |
| 网页 LLM 交叉验证流程 | `AGENTS.md` §网页 LLM 交叉验证流程 | 站点清单、回执格式、门禁 |

**核心**：关键结论必须 ≥2 个不同 LLM 服务验证（ego-browser 驱动已登录会话）。

## 2. Arena 外包

| SOP | 路径 | 说明 |
|-----|------|------|
| **Arena Loop 链路（★ 唯一入口）** | `agents/arena-loop-pipeline.md` | 6 步链路+3 断点门禁+任务书强制段+仓库映射/连接/降级（2026-10-22 起） |
| arena-outsource skill（提交机制） | `.claude/skills/arena-outsource/SKILL.md` | 任务卡模板+ego-browser 提交+失败处理与降级阶梯 |
| ~~agents/arena-outsource.md~~ | 已并入链路 SOP · 仅存档 | goal 不再索引 |

**核心**：
- 选仓库：按任务选对应仓库（decomp→decomp-bench / 风格蒸馏→persona-distill / 论文校对→academic-AI / 媒体 pipeline→d1-media-pipeline / AI 视频复刻→d1-video-recreation，2026-10-26 修正：媒体映射原写 d1-media-pipeline（假设），视频复刻实际仓库为 d1-video-recreation）
- 连接：GitHub App 授权（all repositories，一次授权所有私有仓库）
- 失败降级：arena 通道不可用 → Lead 本地自答（conf-0.2），不阻塞

## 3. Loop 流程（1-loop）

| SOP | 路径 | 说明 |
|-----|------|------|
| loop-executor agent | `agents/loop-executor.md` | 6 阶段执行流程（01→04.5） |
| 1-loop 阶段定义 | `loop/prompt-first/` | 01-goal-decomposition → 04.5-final-review（操作流程+判定标准） |
| 1-loop 操作示例 | `loop/prompt-first/examples/` | 各阶段方法示范+正负案例（2026-10-26 外移，按需读取） |

**核心**：所有理论研究任务必须经过 1-loop（目标分解→信息调研→交叉验证→行动分解→执行验证→最终复核）。

## 4. Goal 模板

| SOP | 路径 | 说明 |
|-----|------|------|
| Goal 模板（定位器） | `agents/goal-template.md` | 五字段模板 + 阶段流程指针 + SOP 索引（2026-10-26 瘦身重写） |
| 结构化输出派发 | `agents/structured-dispatch.md` | 决策型子任务结构化返回（从 goal-template §2.4.1 外移） |

**核心**：
- 质量原则：对标顶级刊物、充分调研、先复刻再创新、严格检验标准
- 防遗忘机制：goal 是 AI 短期记忆，不设置 goal → AI 忘记原则
- 每次创建 goal 时引用本模板

## 5. 其他 SOP

| SOP | 路径 | 说明 |
|-----|------|------|
| 思考预算 | `projects/AI-计算科学/D1-persona-align/thinking-budget.md` | L0/L1/L2 分级 + 终止指令 |
| 人类确认机制 | `个人/APPROVALS.md` | 不可逆 × 偏好不明 → 写审批不阻塞 |
| 问题台账 | `projects/AI-计算科学/D1-persona-align/memory/qanda-ledger.md` | 成璐问过的每个问题 |

## 6. 维护

- 新增 SOP → 更新本索引
- SOP 变更 → commit + 更新历史
- AI 每次创建 goal 时读本索引，引用对应 SOP
