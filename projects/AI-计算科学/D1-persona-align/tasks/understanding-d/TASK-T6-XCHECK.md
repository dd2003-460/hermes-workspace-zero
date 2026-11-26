# 任务卡 T6-XCHECK：T6 推荐 × D 思考习惯交叉核对

# origin: ai · 2026-11-26 · 补齐 T6 缺口（arena 沙箱里 thinking-patterns-v1.md 不可达，误判"缺失"；实际在 main）

## 背景（自包含）
T6 复活前沿调研已交付（`projects/AI-计算科学/D1-persona-align/tasks/understanding-d/revival-frontier-research.md`，137 行）。
其"适配建议/推荐组合"当时因思考习惯原文缺失而无法对照 D 验证。现在原文有了：
- `thinking-patterns-v1.md`（100 行，v1 基线习惯）
- `T4-thinking-patterns.md`（11 条新习惯=9 新+2 强化，各带原文证据）
本任务 = 把 T6 的推荐逐条对照这两份习惯文件，判对齐/冲突/不可判。

## 只读输入（同目录下）
1. `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/revival-frontier-research.md`
2. `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/thinking-patterns-v1.md`
3. `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/T4-thinking-patterns.md`

## 唯一产出
`projects/AI-计算科学/D1-persona-align/tasks/understanding-d/t6-xcheck-vs-thinking-patterns.md`，结构：
1. **逐条核对表**：T6 的每条推荐/断言（含 conf）× 相关思考习惯（标文件+条目号）→ 判定 ∈ {对齐 / 冲突 / 部分对齐 / 不可判} + 一行理由
2. **冲突清单**：冲突项单独列出 + 建议裁决方向（改 T6 推荐 or 标注例外）
3. **T6 推荐里被习惯强支持但 T6 没提的点**（若有）
4. **残余缺口**：哪些 T6 断言仍无法用习惯验证（如依赖 27b 实验的）

## 执行纪律
- 全程离线零 LLM、不碰 vLLM 8787、不联网。
- 三个文件都很短（137/100/~150 行），一次读完即可，无截断风险；推理从简每步一行。
- 判定必须引两边原文（T6 推荐句 + 习惯条目），不凭印象。
- 写完立即 commit（workdir 主仓 main 分支，commit message 前缀 `understanding-d T6-xcheck:`）。
- done = md 落盘 + 1 commit。最终汇报 ≤8 行：文件路径 + 核对条数 + 对齐/冲突/不可判分布 + commit hash。

## 验收（Lead 对照核）
- [ ] 核对表覆盖 T6 全部推荐/断言（漏一条 = 不合格）
- [ ] 每判定带双侧原文引用
- [ ] 1 个 commit，无 LLM 调用痕迹
