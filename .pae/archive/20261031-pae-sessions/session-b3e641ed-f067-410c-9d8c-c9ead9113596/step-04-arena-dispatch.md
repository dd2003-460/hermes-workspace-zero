# Step 04 — arena 任务书编写与仓库派发（3 断点门禁）

## 目标
按 `agents/arena-loop-pipeline.md` 的 6 步链路 + 3 断点门禁，把 step 03 产出的 3 个子模块任务写成 arena 任务书，push 到 github 远程仓库，使 arena agent 可直接拉取执行。本步完成 = 派发就绪，不验收 arena 产出。

## 涉及文件
- 只读对象：
  - `agents/arena-loop-pipeline.md`（6 步链路 / 断点 A/B/C / 任务书强制段 §2 / 复制 push 命令模板 §4.1）
  - `agents/arena-coding-agent-dispatch` skill 记录的四坑（超长 prompt / 单轮任务过重 / 仓库挂载 sudo 2FA / 收起 composer 需点继续工作）——派发时按坑规避
- 产出：
  - `market-alpha/tasks/T3-kinetic-flow.md`（M1 任务书：核验 D23 五命题在真实数据上的条件与有效性 + 17 源数据可用性复核）
  - `market-alpha/tasks/T4-supply-chain.md`（M2 任务书：产业链供需→板块预测的事件信号定义 + 无未来回测设计）
  - `market-alpha/tasks/T5-regime-game.md`（M3 任务书：regime × 策略类型博弈矩阵 + 各背景下资金策略的预注册设计）
  - `market-alpha/loop-artifacts/push-verification.md`（断点 A 硬门禁证据：commit hash + `git ls-remote` 输出）

## 做法
1. **断点 A**：按 §4.1 模板同步 `loop/prompt-first/`（7 个阶段文件 + examples/）+ `sop/arena-loop-pipeline.md` 到远程仓库（market-alpha 本地仓已有，先 pull 对齐），push 后记录 commit hash + `git ls-remote https://github.com/dd2003-460/market-alpha.git HEAD` 到 `loop-artifacts/push-verification.md`。
2. **任务书强制段**（每份任务书顶部，§2 原文要求）：① 先读 `loop/prompt-first/01→04.5` 全部阶段文件；② 按阶段推进并在 `loop-artifacts/stages/` 落产出；③ 完成后 commit + push（含全部 loop-artifacts/）。
3. **单轮任务切分**（规避 arena 四坑之「单轮任务过重」）：每份任务书内部再分 ≥3 轮，每轮一个明确交付物（如 T3 第 1 轮 = 五命题逐条找验证条件与文献锚点；第 2 轮 = 数据源可用性复核；第 3 轮 = 预注册检验设计），写明「本轮只做第 N 轮，完成后停下汇报」。
4. **断点 B/C**：3 份任务书 + 强制段 commit + push 后，`git log -1 -- tasks/T3-kinetic-flow.md` 有提交即断点 B 过；任务书顶部强制段存在即断点 C 过。
5. 本步不启动 arena 会话（启动 + 跟踪是 step 05 的事），避免一步塞入外部动作与长时任务。

## 验收标准（可机器检查）
1. `loop-artifacts/push-verification.md` 含远程 HEAD hash 与 `git ls-remote` 原始输出（断点 A 过）。
2. 3 份任务书存在，每份顶部含 3 条强制段（grep "loop/prompt-first" 与 "commit + push" 可验）。
3. 每份任务书含 ≥3 轮切分且每轮有独立交付物描述（grep "第 1 轮/第 2 轮/第 3 轮" 或等价标记）。
4. `git -C market-alpha log --oneline -8` 可见任务书提交且工作区 clean（无未提交变更）。
5. 3 份任务书与 step 03 的 decomposition.md 任务表一一对应（引用其任务 ID，不发明表外任务）。