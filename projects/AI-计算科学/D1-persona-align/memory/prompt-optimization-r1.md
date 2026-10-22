# prompt 级优化 r1（2026-10-22）

> origin: ai · goal-fb61fede round 9-11 · S5 prompt 级优化

## 一、任务卡 prompt 优化空间分析（3 处）

| # | 优化点 | 实测证据 | 修复 |
|---|--------|---------|------|
| 1 | **交付格式开放** | S1 任务卡"总结瓶颈"太开放，subagent 读了 4/5 后结束 | [交付] 字段必须给具体模板（markdown 表格/JSON schema） |
| 2 | **输出长度无限制** | S2/S3 没限长度，写了 60/93 行，S4 汇总只用了 ~40 行 | [长度] 字段限制"≤50 行"，过程论证放附录 |
| 3 | **问题不够具体** | "读 5 个文件总结瓶颈"→ subagent 不知道聚焦哪个 | [任务] 字段具体到"回答 X 问题"，不开放式 |

## 二、SKILL.md 修订（已执行，1 处）

### 任务卡模板
- 新增 [长度] 字段（≤50 行）
- [任务] 字段加"具体到'回答 X 问题'，不开放式"
- [交付] 字段加"给具体模板"

### 任务卡模板下方
- **任务卡 prompt 优化 3 原则**：交付格式模板化 / 输出长度限制 / 问题具体化（各配实测证据）

## 三、未覆盖项（需全局 SOP，不在 arena skill 范围）

- **git 操作安全**（S1#7）：用 `git add <具体路径>` 替代 `-A`，写入全局 SOP 或 APPROVALS
- **APPROVALS 条目 2**：细粒度拆分规范写入位置，等批

## 四、goal 完成度评估

- **S1 本地证据盘点**：bottleneck-evidence-r1.md（8 事件）✅
- **S2 arena 鲁棒性**：arena-robustness-r1.md（8 失败模式）✅
- **S3 正交完备**：decomposition-orthogonality-r1.md（三问检查法）✅
- **S4 上下文管理**：context-management-r1.md（4 浪费点）✅
- **S5 prompt 级**：prompt-optimization-r1.md（3 优化点）✅
- **SKILL.md 修订 7 处**（69→88 行）：三档超时/落盘硬约束/arena 拆 2 subagent/时长阈值/背景最小化/汇总分层/任务卡 3 原则
- **commit 3 个**：7df4ab32 + b00598e5 + 本轮，全 push 成功

**结论**：goal 目标（系统瓶颈优化 12h 长跑）的 5 个方向（S1-S5）全部覆盖，SKILL.md 修订 7 处，commit 3 个。goal 完成度 ~95%。剩余 5%：APPROVALS 条目 2 等批 + git 安全全局 SOP（需成璐拍板）。
