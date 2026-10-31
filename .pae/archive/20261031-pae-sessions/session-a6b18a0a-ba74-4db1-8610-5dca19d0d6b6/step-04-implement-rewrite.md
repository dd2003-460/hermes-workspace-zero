# Step 04: 实施重写 goal-template.md + 外移细节

## 目标
实际重写文件并落盘。

## 涉及文件
- `agents/goal-template.md`（重写）
- `agents/goal-template-addon-acp-rule.md`（合并后删除或标记已合并）
- 可能新建执行细节落点文件
- `agents/SOP-INDEX.md`（同步更新指针）

## 做法
1. 按 Step 02 设计重写 goal-template.md
2. 外移的内容写入对应落点（arena-loop-pipeline.md 或新文件）
3. 合并 addon-acp-rule.md
4. 更新 SOP-INDEX.md

## 验收标准
- 新 goal-template.md 可独立工作（建 goal → 定位 SOP → 读 SOP 执行）
- 无信息丢失
- SOP-INDEX 指针一致