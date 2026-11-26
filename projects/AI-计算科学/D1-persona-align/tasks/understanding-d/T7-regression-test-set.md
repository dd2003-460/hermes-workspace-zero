# origin: ai
# T7 任务卡：D 原话回归测试集 v0（understanding-d 验收锚点）

## 目标
从现有语料构造"像 D 怎么测"的第一版：一组判断场景。用法=把场景（不含 D 的结论）喂给系统，看它推出的判断与 D 历史判断的一致率。本卡只负责造测试集，不负责跑测试。

## 输入（只读这 3 个，不读其他文件）
1. `projects/AI-计算科学/D1-persona-align/memory/objfunc-signal-log.md`（118 条信号，835 行；D 的反问/建议/纠正，每条带 D 原话）
2. `/Users/a1-6/WorkBuddy/AI对话抓取归档/data/ai_chats/corpus/hermes/像完整的我一样思考：质疑-猜想-验证的开关__20261125.md`（高质量对话，3.7KB）
3. `projects/AI-计算科学/D1-persona-align/tasks/understanding-d/persona-map-skeleton.md`（只读六大轴定义，用于"关联轴"字段）

## 输出
`projects/AI-计算科学/D1-persona-align/tasks/understanding-d/regression-test-set-v0.md`

头部写：# origin: ai / 用途 / 输入来源 / 构造日期 / 阈值状态（待定，首轮跑完看分布再定）。

每条场景格式：
```
### R01 <主题≤5字>
- 场景：<情境描述，自包含，≥3 句，给足判断所需背景；严禁出现 D 的结论或原话关键词>
- Ground truth：<D 当时的实际判断/行动 + 原话引用≤30字>
- 来源：<文件 + 章节标题或行号>
- 判别力：<一句话：为什么这个场景能区分"像D"和"通用AI">
- 关联轴：<压缩/分解/目标函数/校准/形式化/验证 之一>
```

## 选材判据（场景合格线）
- D 做了明确判断/决策/纠正的场景（不是陈述事实、不是情绪表达）
- 判断可情境化：另一个系统面对同样情境可能给出不同判断
- 排除答案显然的（任何合格 AI 都会同样判断的，无判别力）
- 优先：反直觉判断、对通用 AI 行为的纠正、价值权衡（纯度/自主/性价比/简洁）
- 轴覆盖：≥4 条轴各有 ≥1 条场景

## 验收标准
- ≥10 条场景（目标 12）
- ground truth 原话引用 100% grep 命中源文件（脚本自检，报告命中率）
- 盲测自检：场景段落里不得出现 ground truth 原话的关键词（脚本检查，报告通过率）
- 覆盖 ≥4/6 轴
- 完成后 commit（回执带 commit hash）

## 执行纪律
- 纯执行任务：本卡是唯一指令来源；不联网；不发明输入外的内容
- 增量写入：每批 ≤5 条场景 append + 即 commit（防输出上限，27b 大写入多次踩坑）
- 收尾回执 JSON：{"total_scenarios": N, "commit_hash": "...", "axis_coverage": ["..."], "quote_grep_pass": "x/y", "blind_test_pass": "x/y"}
