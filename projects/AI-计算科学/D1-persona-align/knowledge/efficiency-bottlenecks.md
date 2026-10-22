# 效率瓶颈清单（按优先级排序）

> origin: ai · goal-32d9335d round 2 · 成璐当前最痛的 3-5 个瓶颈

## P1: arena 通道系统性失败
- **现象**：4 次 arena subagent 全部失败（decomp organizer 空等 20min+ / memory-hooks 10min 未落盘 / C0 run2/3 page.fill 故障 / 评分 subagent 无 closing）
- **根因**：ego-browser 侧 page.fill 静默失败（16ffc349: "The page.fill didn't work"），不是 arena 后端
- **影响**：每次浪费 20min+ 空等，降级自答 conf-0.2
- **修复**：F0 提交失败验证（提交前 snapshot 验证输入框有内容 + 提交后 snapshot 验证 URL 变化）
- **状态**：待修

## P2: goal 结束太快
- **现象**：m01051 "goal就这样结束了？其余可以做的仓库的调研呢？"
- **根因**：goal 只做了 S1-S5（5 步），没做"仓库所有可推进的调研/实验"
- **影响**：成璐要"独立推进"，我按"完成当前任务"做了
- **修复**：goal 目标要包含"全仓库"范围，不是"当前任务"
- **状态**：已修（goal-0b22f789 包含全仓库范围）

## P3: 项目优先级不对
- **现象**：m01404 "qnm算了，老项目而且目前没兴趣" + "效率提高优先级放最高"
- **根因**：我按"项目优先级"做（decomp → persona → gpu-inference → 媒体 → area-quantized），成璐要"效率优先"
- **影响**：area-quantized 花了 r13 检查（1 轮），应该标记 deprecated 跳过
- **修复**：先修工具链（arena 通道），再做项目
- **状态**：已修（area-quantized 标记 deprecated）

## P4: subagent 并发限制（硬上限 3）
- **现象**：m00531 派 comparison subagent 失败 "subagent limit reached (active child limit: 3)"
- **根因**：DSH 硬限制，3 个 teammate 占满后无法派新 subagent
- **影响**：无法并行派多个 subagent，需要等 teammate 结束后才能派
- **修复**：无法修复（DSH 硬限制），需要串行派发
- **状态**：不可修

## P5: 思考 token 预算
- **现象**：m00980 "不是让你解决思考太长问题吗"
- **根因**：思考预算（L0/L1/L2）需要内化，不是"记住"
- **影响**：每轮思考 token 消耗过多，效率低
- **修复**：内化思考预算（L0 直接做 / L1 1 行 / L2 推演一次）
- **状态**：已内化（AGENTS.md 思考预算节）

## 优先级排序

| # | 瓶颈 | 优先级 | 状态 |
|---|------|--------|------|
| P1 | arena 通道系统性失败 | **最高** | 待修 |
| P2 | goal 结束太快 | 高 | 已修 |
| P3 | 项目优先级不对 | 高 | 已修 |
| P4 | subagent 并发限制 | 中 | 不可修 |
| P5 | 思考 token 预算 | 中 | 已内化 |

## 给 Lead 的建议

- 每轮开始前，查本清单，确认 P1 是否已修
- P1 未修 → 不派 arena subagent，直接走降级（ego 直抓 → 自答）
- P2/P3 已修 → 确认 goal 包含全仓库范围 + 效率优先
