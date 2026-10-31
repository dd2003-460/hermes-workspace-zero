# Step 05 — arena 执行跟踪与阶段产出验收

## 目标
跟踪 3 份任务书（T3/T4/T5）在 arena 会话中的逐轮执行，按阶段门禁验收产出：每轮交付物存在且符合任务书内预注册的验收口径才放行下一轮。Lead 只跟踪与验收，不代写产出。

## 涉及文件
- 只读对象：
  - `market-alpha/tasks/T3-kinetic-flow.md` / `T4-supply-chain.md` / `T5-regime-game.md`（step 04 产出，含各轮交付物定义）
  - `agents/arena-loop-pipeline.md`（断点 C 判据：arena 首条消息引用 loop 阶段路径）
  - arena 会话页面（ego-browser 操作，按 `arena-coding-agent-dispatch` skill 规避四坑：单轮任务切小 / 页面收起后点「继续工作」再发下一轮）
- 产出（验收记录，非研究产出）：
  - `market-alpha/loop-artifacts/stages/05-tracking.md`（逐轮跟踪台账：任务 ID × 轮次 × 状态（完成/停滞/返工）× 交付物路径 × 验收结论）

## 做法
1. 按 `arena-coding-agent-dispatch` skill 建/选 arena 会话，挂 market-alpha 仓库，逐份任务书逐轮派活（每轮 = 任务书内声明的一轮交付物）。
2. 每轮结束后验收三查：① 产出文件在 `loop-artifacts/stages/` 下存在且 commit+push 到仓库；② 产出内容与该轮交付物定义逐条对照；③ 断点 C 有效（arena 引用了 loop 阶段路径而非自由发挥）。
3. 停滞处理（红线：不空等）：arena 两轮无新进展 → 按 arena 四坑逐项排查（prompt 过长？单轮过重？挂载问题？composer 收起？）；仍停滞 → 记录停滞原因到跟踪台账，切到可执行的其他任务书轮次，循环不因单一任务书停滞而停。
4. 返工：验收不达标 → 任务书内写明返工点重发该轮，不改任务书已冻结的验收口径（改了 = 计入后续 trial count 风险）。
5. 每轮闭环后更新 `05-tracking.md` 台账并 commit。

## 验收标准（可机器检查）
1. `market-alpha/loop-artifacts/stages/05-tracking.md` 存在，台账行数 ≥ 9（3 任务书 × 3 轮）。
2. 每行台账含 5 列（任务 ID / 轮次 / 状态 / 交付物路径 / 验收结论），状态 ∈ {完成, 返工, 停滞+原因}。
3. 状态为「完成」的行，其交付物路径在仓库内真实存在（`git -C market-alpha ls-files` 可查）。
4. 停滞行（若有）含停滞原因 + 已执行的排查动作（对应四坑中哪条）。
5. 跟踪台账 git commit 落 market-alpha 且已 push（`git ls-remote` HEAD = 本地 HEAD）。