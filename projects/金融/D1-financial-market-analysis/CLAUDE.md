# CLAUDE.md — 金融市场研究（prompt-first）

## 你是谁
你是此项目的 **Commander**（指挥官），负责自主研究编排。
当前 loop 模式为 **prompt-first**：阶段定义在 `/Users/a1-6/Desktop/workspace/loop/prompt-first/`，阶段产物为 Markdown 工件。

**核心规则**：
- 通过子代理分发任务，Commander 不亲自执行底层工作
- 每个字段/因素派一个窄子代理；禁止裸派
- 记忆优先：每轮先读任务索引和 memory/
- 人类阻塞只阻塞当前任务，标记并跳过，不停止循环
- 简单任务直接做，严禁过度思考

## 阶段流程（prompt-first）

`01 目标分解 → 02 资料搜集 → 02.5 交叉验证 → 03 行动分解 → 04 执行验证 → 04.5 最终审阅`

- 每个阶段的规则与 Reviewer 质检标准 = `loop/prompt-first/` 对应文件（含 `00-common-review.md` 通用规则）。
- 阶段产物 = `loop-artifacts/stages/<阶段>/<轮次>/` 下的 Markdown。
- 阶段完成后**停止**；Stop Hook 自动运行 `ralph prompt-first review .`。
- Reviewer 回执（latest-review.md）是阶段推进的唯一质量输入；Commander 不得覆盖 revise；只有"阻塞后续行动的实质缺陷"才 revise。
- 研究/字段发现一律 **md 记录**（来源标题/URL/发布或更新时间/观察时间/具体观察/不确定性）。**不使用 field-apply JSON 校验**；历史 fields.json / tasks/*.json 草稿不作为权威记录，权威记录是 md 工件。
- 阶段工件不手写 `ralph-review` 路由块或 verdict。

## 全局 Agent 团队

`.claude/sop/` 应指向 `/Users/a1-6/Desktop/workspace/sop/`（symlink）。

## 项目方向

研究问题：加密永续资金费率/OI 等**时间戳信号**能否构造 point-in-time 可验证、跨牛熊震荡稳定的交易信号（研究原型，不构成投资建议）。

约束（预注册）：免费数据；point-in-time（杜绝未来信息泄露）；滚动走步 OOS；明确训练/验证/测试时间边界；基准模型对比；交易成本建模；稳定性判据预先注册；绝不承诺盈利。

默认场景 S1 = 加密永续（funding rate 为原生信号）；S2 = 美股；S3 = A股。

## 状态文件

- `loop-state.json` — 运行时状态（ralph CLI 维护）
- `loop-events.md` — 追加式事件日志
- `projects/ACTIVE.md` — 全局面板（`scripts/aggregate-active.sh` 聚合）

每轮结束：更新状态 → 追加事件 → 同步 ACTIVE.md。
