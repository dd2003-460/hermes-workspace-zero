# S2/S3 优化报告（r2 · 2026-10-22）

> origin: ai · goal-32d9335d round 2 · 质疑 + 调研 + 优化汇总

## 一、质疑结果（7 个矛盾点）

| # | 矛盾点 | 有用性 | 修复方向 |
|---|--------|--------|---------|
| 1 | F1 根因可能是 ego-browser 侧（page.fill 静默失败） | **有用** | F0 提交失败验证 |
| 2 | F2 30s 快检可能误杀正在思考的 agent | 理论 | loading spinner 判据 |
| 3 | F5 多会话冲突本会话从未发生 | 无用 | 合并到 F1 |
| 4 | F8 根因可能是 context 溢出 | 有用 | subagent checkpoint |
| 5 | 正交性 30% 阈值不可操作 | 理论 | 字段级/列定义级 |
| 6 | 时长阈值不是充分条件 | **有用** | 二维矩阵（复杂度×通道） |
| 7 | arena 失败是系统性的 | **有用** | 区分随机/系统性 |

**有用 4 个**（1/4/6/7），**理论 3 个**（2/3/5）。

## 二、对齐 vs 能力归因

- **对齐 57%**（8/14）：假设 vs 意图（7/14）+ 规则 vs 执行（1/14）
- **能力 43%**（6/14）：DSH 功能调研（5/14）+ 方法论内化（1/14）

**最大对齐问题 = 假设 vs 意图**：我按字面意思做，成璐要背后意图。
**最大能力问题 = DSH 功能调研**：hook/compress/思考预算 需要调研，不是"记住"。

## 三、知识库补全

| 文件 | 内容 | 用途 |
|------|------|------|
| `knowledge/decision-preferences.md` | 8 条决策记录 + 4 个模式 | 对齐：收到指令时查偏好 |
| `knowledge/efficiency-bottlenecks.md` | 5 个瓶颈（P1-P5）+ 优先级 | 效率：每轮开始前查 P1 |
| `knowledge/domain-graph.md` | 项目全景 + 依赖 + 阶段 | 导航：确认项目依赖 + 阻塞 |

## 四、agents 更新

- `agents/loop-executor.md`：6 阶段执行流程（01→04.5）+ 约束 + 给 Lead 的建议

## 五、流程改进

### 1. F0 提交失败验证（修复矛盾 1）
- 提交前 snapshot 验证输入框有内容
- 提交后 snapshot 验证 URL 变化/页面有"已提交"标记
- 30s 内无变化 → 判定 F0（提交失败），不是 F1（回复未落页）

### 2. subagent checkpoint（修复矛盾 4）
- 每读 N 个文件先写 checkpoint（避免 context 溢出后丢失写文件步骤）
- checkpoint 格式：`[checkpoint] 已读 X/Y 文件，当前进度 Z`

### 3. 二维矩阵（修复矛盾 6）
- 复杂度（子领域数 × claim 数）× 通道（arena vs 本地）
- 高复杂度 × arena → 拆分（2 subagent）
- 高复杂度 × 本地 → 串行（1 subagent）
- 低复杂度 × 任意 → 串行（1 subagent）

### 4. 区分随机/系统性失败（修复矛盾 7）
- 随机失败（page.fill 故障/超时）→ 拆分有效
- 系统性失败（arena 后端 outage/登录态过期）→ 通道降级（arena → ego 直抓 → 自答）
- 判定：30s probe（最小任务，30s 内落盘=可用，否则降级）

## 六、给 Lead 的建议

1. **每轮开始前**：查 `knowledge/efficiency-bottlenecks.md`，确认 P1（arena 通道）是否已修
2. **P1 未修**：不派 arena subagent，直接走降级（ego 直抓 → 自答 conf-0.2）
3. **派发前**：查 `knowledge/domain-graph.md`，确认项目依赖 + 阻塞
4. **收到指令**：查 `knowledge/decision-preferences.md`，确认决策偏好
5. **loop 流程**：用 `agents/loop-executor.md`，6 阶段执行 + 每阶段落盘

## 七、下一步

- [ ] 修 P1（arena 通道）：F0 提交失败验证 + 30s probe
- [ ] 执行媒体 Step E（无阻塞）
- [ ] decomp 剩余 19 份 run（P1 修完后）
- [ ] persona T45（experiment-design-t45.md MISSING，需先补）
