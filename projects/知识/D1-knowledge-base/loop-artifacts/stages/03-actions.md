# 03-action-decomposition — KB.1 第6篇写作动作分解

## 执行顺序（本地直写，单文件）

| # | 动作 | 产出 | 判据 |
|---|------|------|------|
| A1 | 写 `notes/vector-database-cosine-similarity.md`：A 名词表 10 概念×4 字段 + B 成璐视角段 + 可证伪预测收尾 | note 文件落盘 | 结构完整，每概念 4 字段齐全 |
| A2 | drift-check.py 跑分 | 分数输出 | 第一人称≥0.2 / 句长<55 / 空话 0 |
| A3 | 不过则织入第一人称/拆长句重跑（最多 3 轮） | 修订版 | 三项全过 |
| A4 | INDEX.md 加一行登记 | 索引更新 | 新行存在且格式对齐 |
| A5 | loop-state.json current_task/stage 更新 | 状态同步 | JSON 合法，stage 指向本篇 |
| A6 | git commit + push（workspace root repo） | 留痕 | push 成功，git status 干净 |
| A7 | stage-gate 推进 04→05，验收后 complete | goal 收口 | 五字段验收标准逐条达标 |

## 概念块清单（与 01 一致，写作时按此序）
1. embedding · 2. 余弦相似度 · 3. top-k 检索 · 4. 暴力搜索的墙 · 5. HNSW · 6. recall@k vs 延迟 · 7. 重排 · 8. 切块 · 9. 本地方案成本模型 · 10. agent 记忆里的位置

## 风险与对策
- 术语堆叠 → 每个术语第一次出现给一句话定义（KB README 硬规则）
- 百科腔 → B 段强制"我的判断/我砍掉的/我猜"结构，A 段疑问字段必须是我自己的质询不是百科补充
- 数字失实 → 只引用已读素材里的数字（run-b 的 1.2TB/1TB RAM、recall 差 5-10%），外部数字标量级