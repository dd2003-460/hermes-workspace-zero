# Step 02 设计结论：goal-template.md 新结构

> origin: ai · 2026-10-27 · plan-and-execute step-02

## 结论：当前 66 行版本已是最优结构，无需进一步瘦身

### 依据

Step 01 诊断（diagnosis.md Part B）识别的 3 个残留点（P1/P2/P3）已在 commit bb355f7b（76→66 行）全部处理：

| 残留点 | 诊断建议 | 当前状态 |
|--------|---------|---------|
| P1 §2 执行通道细节 | 外移为 1 行指针 | ✅ 行 30 已是 1 行指针"执行通道+3 断点门禁细节见 arena-loop-pipeline.md" |
| P2 acp_rule 段 | 压缩为 1 行 | ✅ 行 41 已是 1 行"acp_rule 加载：建 goal 后读 acp-rules.json…" |
| P3 §6 指针表 | 精简为 4-5 项 | ✅ 行 61-66 已是 4 项核心指针 |

### 当前结构评估

66 行定位器结构：
- §1 五字段模板（9 行）— create_goal 核心格式
- §2 阶段流程（14 行）— 整体外包原则 + 6 阶段表 + 1 行执行指针
- §3 质量原则（11 行）— 8 条硬规则含 acp_rule 加载
- §4 验收标准（6 行）— 量化门禁
- §5 生命周期（8 行）— 防断链规则
- §6 SOP 指针索引（7 行）— 4 个核心指针

**信号-噪声比**：66 行中约 60 行是 A 类（建 goal 必须读），B/C 类混入 <10%。健康。

### Step 03 结论：subagent 不需要 goal-template

**决定：不 давать subagent 读 goal-template.md。**

理由：
1. goal-template 是"建 goal 时 Lead 读"的，subagent 接收的是已建好的 goal（objective 文本）
2. subagent 需要的是任务书（task brief），不是 goal 模板格式
3. 给 subagent 读 goal-template 只会增加 token 消耗，不增加执行质量
4. 如果 subagent 需要走 loop 流程，任务书里直接引用 `loop/prompt-first/` 阶段文件即可

### Step 04 结论：无需实施

当前版本（66 行，commit bb355f7b）已是目标状态。plan-and-execute 计划的前提（255 行→agent 不按流程走）已通过两次瘦身解决：
- 218→76 行（commit f19f2efd，示例外移+结构重写）
- 76→66 行（commit bb355f7b，P1/P2/P3 残留清理）
- 累计 -70%
