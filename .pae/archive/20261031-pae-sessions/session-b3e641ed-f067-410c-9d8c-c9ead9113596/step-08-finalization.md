# Step 08 — 收官：04.5 反方复核 + 胜率落库 + 状态回写

## 目标
对整个 market-alpha 金融研究系统做收官：① 对 step 07 回测结论执行 04.5 反方复核（抽测 + 挑战）；② 把各子模块胜率/结论写入大仓库 README 索引表与 decomposition；③ 回写 loop-state.json 与项目级 memory；④ 全仓 commit + push 留痕。完成后向用户汇报「哪些 idea 有效、哪些无效、瓶颈在哪」。

## 涉及文件
- 只读对象：
  - `market-alpha/loop-artifacts/stages/07/07-backtest-summary.md`（回测结论汇总）
  - `market-alpha/loop-artifacts/stages/06/06review.md`（对抗核验裁决汇总）
  - `loop/prompt-first/04.5-final-review.md`（04.5 阶段定义，抽测 + 挑战规范）
  - `projects/金融/D1-financial-market-analysis/loop-state.json`（状态回写格式先例）
- 产出/修改：
  - `market-alpha/loop-artifacts/stages/04.5/review.md`（04.5 反方复核：对回测结论的抽测清单 + 挑战记录 + 复核结论）
  - `market-alpha/README.md`（子模块索引表更新：3 新子模块的状态 / 轮次 / 胜率列填入）
  - `market-alpha/INDEX.md`（补 3 个新子模块条目）
  - `market-alpha/tasks/decomposition.md`（任务表状态回写：已完成 / 空缺清单更新）
  - `market-alpha/loop-state.json`（新建：iter、各子模块阶段、下一轮计划）
  - `projects/金融/INDEX.md` + `projects/INDEX.md`（把 market-alpha 登记为金融领域聚合仓，更新描述含 3 新子模块）
- 产出（memory）：
  - `market-alpha/memory/2026-10-29-financial-system-sop.md`（本轮系统 SOP 建设记录：架构决定 + 回测结论 + 瓶颈清单，供后续轮次回溯）

## 做法
1. **04.5 反方复核**：对 step 07 每个「有效/部分有效」结论做 3 项抽测（随机抽 ≥3 个 OOS 窗口人工核对数值 / 抽 1 个「无效」结论确认其判据命中逻辑正确 / 抽 1 条数据点核对发布戳纪律）+ 1 项挑战（假设自己是反方：该结论在什么条件下会翻转，如实评估稳健性边界）。抽测不通过 → 返工对应 backtest 报告（计入 trial count），通过 → 写复核结论。
2. **胜率落库**：README 索引表 3 个新子模块填入状态（round-1 完成 / 进行中）、当前轮次、胜率（回测显著率或 OOS 正收益占比，无有效信号则记 "0/ N（负结果）"，不空着）。
3. **状态回写**：loop-state.json 含 iter 计数、各子模块当前阶段、下一轮计划（从 decomposition 空缺清单选最高产投比候选）；memory 文件记录本轮决定 + 证据路径 + 瓶颈（数学理论瓶颈 / 个人信息搜集瓶颈清单）。
4. **索引与跨仓登记**：projects/ 两 INDEX 更新 market-alpha 条目（纯索引，不抄内容，符合 AGENTS.md 红线 1 项目分类原则）；market-alpha 全仓 `git status` 干净后 commit + push，`git ls-remote` 核对 HEAD。
5. **汇报**：给用户一份 ≤1 屏的结论：有效 idea 清单（含关键数值）/ 无效 idea 清单（负结果也是交付）/ 未达瓶颈终止的核验状态 / 下一轮最高产投比候选。

## 验收标准（可机器检查）
1. `loop-artifacts/stages/04.5/review.md` 存在，含抽测 ≥3 项 + 挑战 1 项，每项有「通过/返工」结论。
2. README 子模块索引表 3 个新子模块行的「状态/轮次/胜率」三列无空值（负结果记 0/N）。
3. `market-alpha/loop-state.json` 可被 `python3 -c "import json;json.load(open('market-alpha/loop-state.json'))"` 解析，含 iter / stages / next 三键。
4. `git -C market-alpha status --porcelain` 为空（工作区干净）且 `git ls-remote origin HEAD` = `git -C market-alpha rev-parse HEAD`（push 成功）。
5. `projects/INDEX.md` 与 `projects/金融/INDEX.md` 含 market-alpha 条目（grep 可验），且未改 AGENTS.md 任何内容。