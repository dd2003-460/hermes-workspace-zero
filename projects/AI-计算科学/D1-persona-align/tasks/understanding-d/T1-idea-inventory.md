# origin: ai
# T1 任务卡 — 工作区 idea/猜想盘点（understanding-d goal）
# 执行方: subagent（纯读文件，无网络，不碰 8787）

【执行前必读】
1. 本任务是纯执行盘点：只读下面列出的目录/文件，不读其他文件，不发明新内容
2. 产出唯一文件：/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-persona-align/tasks/understanding-d/idea-inventory-v1.md
3. 完成后 commit（git add 该文件 + decomposition.md 状态行，commit message 前缀 "understanding-d T1:"）
4. 读文件用 python open(encoding='utf-8', errors='replace')，编码混杂是常态

## 盘点范围（全量扫，不抽样）
1. pfb/modules/IDEA-INDEX.md（68 行，idea 索引）
2. knowledgebase/pfb-research/（54 文件，重点：2026-11-07-idea-list.md, 2026-11-11-idea-research.md, 2026-11-15-idea48-activation-subgraph.md, longterm-vision-survey.md, theory-compression-intelligence.md, persona-activation-directions-survey.md）
3. note/（8 文件：long-insight-and-moe-agent-ideas-2026-11-07.md, compression-unified-view-2026-11-07.md, reasoning-core-and-node-tree-2026-11-08.md）
4. projects/AI-计算科学/D1-academic-AI/memory/（找 7 个原创研究猜想，文件名可能不含 idea 字样，读 README/INDEX 定位）
5. pfb/lit-survey/ 和 pfb/tasks/ 下带 idea 字样的目录（idea53-goal 等）

## 产出格式（idea-inventory-v1.md）
# origin: ai
# D 的 idea/猜想盘点 v1（understanding-d T1）
每条 idea 一个三级标题：
### <N>. <idea 标题>
- 一句话：<这个 idea 说什么>
- 来源：<文件路径>
- 原文引用：<≤30 字，逐字，不得改写>
- 状态：<已做/在做/未做/已发表/已放弃>（从上下文判断，判断不了标 [待核验]）
- 关联：<与其他 idea 的关联，无则 - >

结尾统计段：总数、按状态分布、按领域分布（压缩/推理/记忆/评测/其他）。

## 验收
- 文件存在，`grep -c "^### " idea-inventory-v1.md` ≥ 40
- 随机抽 5 条的"原文引用"能在源文件 grep 命中（逐字匹配）
- 状态分布和领域分布两段齐全

## 失败降级
某目录读不到 → 在产出里标 [读取失败: 路径]，继续其他目录，不中断。
