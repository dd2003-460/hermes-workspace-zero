# Step 02: 设计新的 goal-template.md 结构

## 目标
设计瘦身后的 goal-template.md，只保留"定位器"功能。

## 涉及文件
- `agents/goal-template.md`（待重写）
- 可能新建 `agents/goal-template-execution.md`（执行细节外移落点）

## 做法
1. 保留：§3 五字段模板（goal 创建格式）+ §3.0 自主探索原则（精简版）+ 阶段顺序速览
2. 外移：§2.1 降级条件、§2.4 仓库选择、§2.5 系列化生产、§2.6 防复读、§2.4.1 结构化输出 → 各自 SOP 或执行手册
3. 保留指针：SOP 索引一行一指针，agent 定位阶段后按需读
4. 处理 addon-acp-rule.md 的合并（硬规则自动加载节）

## 验收标准
- 新 goal-template.md ≤ 80 行
- 建 goal 的 agent 读完能立即：①按格式建 goal ②知道当前阶段该读哪个 SOP
- 执行细节不丢失（全部有落点）