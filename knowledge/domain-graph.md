# 领域全景图（Domain Graph）

> origin: ai · 2026-10-22 · 成璐指令"帮我进行各种可能用得上的调研"
> 用途：AI 自主创建 goal 时，按优先级选方向

## 1. 现有项目（projects/）

| 项目 | 路径 | 状态 | 优先级 | 备注 |
|------|------|------|--------|------|
| decomp T4 消融 | `projects/decomp/` | 14/33 run（C0 5/C1 3/C2 3/C9-plain 3） | P1 | 剩余 19 份 run（C3-C9 各 3）阻塞于 arena 通道 |
| persona T45 | `projects/AI-计算科学/D1-persona-align/` | BLOCKED（experiment-design-t45.md MISSING） | P2 | 需先写实验设计文档 |
| gpu-inference-hardware | `projects/AI-计算科学/D1-gpu-inference-hardware/` | RALPH 阻塞 | P3 | 需 RALPH loop 推进 |
| 媒体 Step E | `projects/d1-media-pipeline/` | 无阻塞 | P3 | 可直接推进 |
| area-quantized | `projects/AI-计算科学/D1-area-quantized/` | deprecated | - | 已废弃（2026-10-22 成璐指令） |

## 2. 新方向（成璐 2026-10-22 提出）

### P1：金融市场预测（直接、可量化、1-3 周可见效）
- **目标**：显卡价格预测（企业供需主导模型）
- **仓库**：`dd2003-460/finance-prediction`（新建）
- **验收标准**：
  - 准确率 > 基线（随机游走模型，如 80%）
  - 能稳定盈利（连续 3 周正收益）
- **SOP**：arena 外包（选仓库→连接→任务书→执行→push）+ loop 流程
- **时间线**：1-3 周

### P2：贡献履历优化（长期价值，但"容易崩溃"）
- **目标**：推理引擎 prompt 测试/验证/优化（小测试，不做大工程）
- **仓库**：`dd2003-460/persona-prompt-lab`（新建）
- **验收标准**：
  - 验证 3 个 prompt 变体（如 C0/C1/C2 契约大小）
  - 选出最优（Mean 分数最高 + σ 最小）
- **SOP**：arena 外包 + loop 流程
- **时间线**：1-2 周

### P3：经济形势、就业选择（外部环境，低频）
- **目标**：周度监控（cron 触发），不占 goal
- **产出**：`knowledge/economy-trends.md`（趋势 + 机会）
- **SOP**：本地调研（1-loop 02 阶段），不外包
- **时间线**：每周 1 次

### P4：寿命不重叠贡献研究（跨领域，高不确定性）
- **目标**：调研（1-loop 02 阶段），不直接建仓库
- **产出**：`research/lifespan-contribution-survey.md`（里程碑工作 + 置信度最高的方向）
- **验收标准**：
  - 完整搜集里程碑工作（≥10 篇）
  - 选置信度最高的方向（conf ≥ 0.7）
  - 有大量数据支撑（≥3 个独立源）
- **SOP**：本地调研（1-loop 02 阶段），不外包
- **时间线**：2-3 周

## 3. 维护

- 新方向提出 → 更新本文件（优先级 + 仓库 + 验收标准）
- 方向完成 → 标记 complete + 归档
- AI 每次创建 goal 时读本文件，按优先级选方向（P1 > P2 > P3 > P4）
