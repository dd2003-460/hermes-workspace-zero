# Step 05：阶段 01 收口（prompt-first 工件路径：Markdown 工件 + Reviewer 回执 + DONE 标记，使 stage 01 pass）

## 目标
把 stage 01 收口推进到 stage 02。field-apply 已废弃（m00553），本步改用 prompt-first 自包含路径：**Markdown 工件（含 `<!-- stage-review` 回执块，verdict: pass 且 reviewed_before_done=true）+ 末行 `<!-- stage: done -->` DONE 标记**——不依赖任何 ralph CLI 命令（field-apply/field-status/render/status/task-next 全部不用），新工件中 ralph 字样零出现（旧 ralph 契约标记 `<!-- ralph: done -->` 统一改为 `<!-- stage: done -->`；本项目从未 init prompt-first 游标，无存量解析，改名无风险）。

## 现状（一手核实）
- `loop-artifacts/stages/01/r1/fields.json` 三字段内容**已填齐**：goal=confirmed(1.0)、known=confirmed(0.95)、unknown=research_required(0.8) + research_queue 6 项（GIANT/FinnGen/BBJ 公开下载、TwoSampleMR 免凭据行为、LDL 样本量核对、覆盖表）。
- 旧的 field-centric 工件（state.json status=unclarified、tasks/ 4 组 json+md）= 运行时生成的历史状态，**保留为只读数据源，不删不改**。
- 本项目从未 init 过 prompt-first 游标（无 ralph-loop.md 文件），故新标记（stage-review/stage: done）无存量解析，直接用无风险。
- stage 01 success_condition（沿用既有定义）：三字段填齐、goal⊇known 且 goal⊇unknown、known 与 unknown 词语无重叠、无 pending。
- 01 阶段工件规范 = `loop/prompt-first/01-goal-decomposition.md`（递归分解 + 正交性 + 空缺清单）；审阅标准 = `loop/prompt-first/00-common-review.md`（Step 04 改后的版本，回执标记为 `<!-- stage-review`）。

## 涉及文件
- 读：`loop-artifacts/stages/01/r1/{fields.json,fields.md,state.json,tasks/*.json}`（内容唯一数据源）、`loop/prompt-first/01-goal-decomposition.md` + `00-common-review.md`（工件与回执规范）
- 写（新增）：`loop-artifacts/stages/01/r1/01-goal-decomposition.md`（阶段 01 正式工件：分解树 + 三字段内容 + research_queue 6 项 + 正交性核对 + 空缺清单 + 末尾 `<!-- stage-review` 回执块 + 末行 DONE 标记）
- 回写：`loop-artifacts/stages/01/r1/state.json`（最小注记字段，见做法 2；不动其他键）、`projects/健康长寿/D1-longevity-orthogonal/loop-state.json`（legacy 节追加 stage01_closed 记录：当前阶段指向 02、DONE 标记位置、日期；不动已有键）

## 做法
2-loop：
1. **备份**：`cp -r loop-artifacts/stages/01/r1 /tmp/stage01-r1-bak-$(date +%H%M)`。
2. **执行**：
   - 以 fields.json 既填内容为唯一数据源，写 `01-goal-decomposition.md`：目标分解（正交拆到原子）+【goal】【known】【unknown + research_queue 6 项】+ 正交性核对（known/unknown 无词语重叠，逐项列出）+ 空缺清单（6 项 → 阶段 02 输入）。工件只记录工作、来源、证据、不确定性（00-common-review 协议第 8 条）。
   - **Reviewer 独立复核**（红线 1：核验类工作外包，不自己 AI 琢磨）：优先派独立 subagent 按 00-common-review「Reviewer 判断原则」+ 01 阶段判定标准复核工件，产出回执（verdict + repair_stage + 问题清单）；subagent 通道故障 → 本地独立视角自答，conf-0.2 并在回执标注。
   - 回执写进工件末尾 `<!-- stage-review ... -->` 块：verdict=pass 且工件此前未含 DONE 标记（reviewed_before_done=true）→ 允许写 DONE 标记；verdict=revise → 按 repair_stage 修复工件后重审，不跳过。
   - pass 后把 `<!-- stage: done -->` 写成工件**最后一行**（自包含 DONE 契约，替代已废弃 ralph 路径的解析标记）。
   - state.json 最小注记：加一个 `note` 字段（如 `"stage01 closed via prompt-first artifact 01-goal-decomposition.md, 2026-10-29, field-apply deprecated (m00553)"`），status 键不手改（保持 unclarified 作为 field 路径的历史快照；推进判定以 DONE 标记 + loop-state.json 为准）；python3 json.load 校验 exit=0。
   - loop-state.json：legacy 节追加 stage01_closed 记录，当前阶段指向 02。
3. **review/verify**（机器可查）：
   ```bash
   tail -1 loop-artifacts/stages/01/r1/01-goal-decomposition.md        # = <!-- stage: done -->
   grep -c "verdict: pass" loop-artifacts/stages/01/r1/01-goal-decomposition.md   # ≥1（在 stage-review 块内）
   grep -c "ralph" loop-artifacts/stages/01/r1/01-goal-decomposition.md  # = 0
   python3 -c "import json;json.load(open('loop-artifacts/stages/01/r1/state.json'))"  # exit=0
   python3 -c "import json;json.load(open('loop-state.json'))"          # exit=0
   ```
4. **提交**：本步仅 workspace 内落盘（可逆），workspace git commit 留痕（可随 Step 10 统一提交）；repo 内 loop-artifacts 副本随 Step 10 阶段04.5 的 commit+push 一起上远端。

## 验收标准
- `loop-artifacts/stages/01/r1/01-goal-decomposition.md` 存在，含分解树 + 三字段 + research_queue 6 项 + 正交性核对 + `<!-- stage-review` 块（verdict: pass，reviewed_before_done: true）+ 末行 `<!-- stage: done -->`，且 ralph 字样 0 处。
- Reviewer 回执来自独立 subagent（或故障标注的本地自答 conf-0.2），非自己写自己审。
- state.json / loop-state.json 均 python3 json.load exit=0，当前阶段指向 stage 02。
- 未触碰清单：tasks/ 4 组旧工件、fields.json、fields.md 零改动（diff 为空）；全程无 ralph CLI 调用。
- 若正交性核对失败（known/unknown 有词语重叠）：留在 01，修订分解后重审，不跳过、不伪造 pass。