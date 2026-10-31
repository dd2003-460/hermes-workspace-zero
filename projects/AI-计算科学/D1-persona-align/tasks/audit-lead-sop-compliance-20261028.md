# 审计报告：Lead 对 arena-loop-pipeline.md SOP 的遵循情况

- 审计时间: 2026-10-28（CST）
- 审计对象: Lead agent 推进 decomp-bench 仓库 T17/T18 的过程
- 审计方式: 独立核查仓库 git 历史、stage-gate 状态文件、任务书原文、SOP 原文，不采信 Lead 自述
- SOP 基准: `/Users/a1-6/Desktop/workspace/sop/arena-loop-pipeline.md`（122 行，与仓库 `sop/` 内副本逐字节一致）

## 结论（明确）

**部分遵循。**

- 断点 A（loop+sop 同步 push）、断点 B（任务书 commit/push）**真实通过**，有可核对证据。
- 但 SOP 核心不变量「loop 是流程骨架，每阶段产出落盘 `loop-artifacts/stages/<N>/`」**在执行侧未被遵循**；
- arena 首选通道**疑似被本地执行替代且无降级记录**；
- T18 任务书的断点 C 防护（强制段）**首次提交时缺失、事后补上**；
- stage-gate 01–03 阶段的门禁自检与仓库证据**基本吻合，无虚假推进**；04-arena-exec 门禁按当前证据**不应判过**。

已知疑点裁决：
- 「T17 任务书缺少【执行前必读】强制段」→ **不成立**。T17 含完整 4 条强制段（`tasks/T17-generalization-bench.md` L3-L7），43 行。
- 「Lead 早期跳过 SOP 阅读直接操作」→ **无法直接证明读没读**；但 sync commit 消息精确匹配 SOP §4.1 模板（`1a0b0f6` "sync: loop/prompt-first + sop (workspace 20261028)"），断点 A 验证文件齐备，setup 阶段行为与 SOP 一致。T18 强制段事后补上说明 checkpoint 意识存在但非首次到位。

## 一、SOP 硬门禁与断点要求（提取自 SOP 原文）

| 门禁 | 要求 | SOP 位置 |
|------|------|---------|
| 断点 A | push 后验证 `loop/prompt-first/*.md` 7 文件 + `sop/arena-loop-pipeline.md` 存在；**且**在 workspace `projects/AI-计算科学/D1-persona-align/tasks/` 记录 commit hash + `git ls-remote` 输出到验证文件 | §1 步骤4 (L22) |
| 断点 B | 任务书 `git log -1 -- tasks/<id>.md` 有提交；arena 会话 `cat` 成功 | §1 步骤5 (L23) |
| 断点 C | 任务书顶部写入 §2 强制段（4 条）；arena 首条消息引用 loop 阶段路径 | §1 步骤6 (L24) + §2 (L28-36) |
| loop 落盘 | 6 阶段每阶段产出落盘 `loop-artifacts/stages/<N>/`，判定 pass 才进下一阶段；回退降级也不豁免 | §0.2 (L10-13) + §4 (L75-86) |
| 任务卡 | ≤50 行；含失败降级 | §4 (L86) + §5 |
| arena 首选 | 调研/核验/执行类任务默认走 arena；降级须记 `knowledge/efficiency-bottlenecks.md` + conf-0.2 | §0.1 (L9) + §3.3 (L63-71) |
| 仓库映射 | decomp 类任务 → `dd2003-460/decomp-bench` | §3.1 (L44) |

## 二、仓库实际状态核查（/tmp/decomp-bench，origin/main = f366342）

| 检查项 | 结果 | 证据 |
|--------|------|------|
| loop/prompt-first 7 文件 | ✅ 00/01/02/02.5/03/04/04.5 共 7 个 .md + examples/，与 workspace `diff -rq` 完全一致 | `git show 1a0b0f6 --stat`（15 文件 848 行） |
| sop/ 存在 | ✅ `sop/arena-loop-pipeline.md` 8689B，与 workspace 源文件 `diff` IDENTICAL | 同上 |
| 任务书强制段 | T17 ✅（L3-L7 四条）；T18-B/C ✅ 但**系事后补上**（见 V3） | `tasks/T17*.md`、`git show 33838fe:tasks/T18-measured-bench-B.md`（头部无强制段） |
| loop-artifacts/stages/ | ❌ **不存在**。仓库唯一 loop-artifacts 是 `archive/D1-ai-agent-hardware/` 旧项目遗留 | `ls: loop-artifacts: No such file or directory`；`git ls-tree -r origin/main` |
| bench 产出结构 | `bench/experiments/`（agent1-6 拆解 + 方法论测试日志）、`bench/gold-{model-selection,inference-infra,rag-vs-longctx}/`（T17 golds）、`bench/data-measured/`（T18 数据 5 文件）、`bench/agent-runs/t18-C.md`（314 行） | `find bench -maxdepth 2` |
| 工作区干净 | ✅ `git status` 无未提交改动 | — |

## 三、stage-gate 状态 vs 仓库 commit 一致性

| goal | 阶段 | 声称证据 | 独立核对 | 判定 |
|------|------|---------|---------|------|
| decomp-research | 02-setup-repo | commit 1a0b0f6，ls-remote HEAD=1a0b0f6… | `git log` 确认 1a0b0f6 = "sync: loop/prompt-first + sop"；验证文件 `stage-gate-decomp-research-02-verify.md` 含正确 hash + ls-remote | ✅ 一致（evidence 文本有 "Alpaca" 字样损坏，见 V6） |
| decomp-research | 03-dispatch | T17 commit c1abd1b，43 行，强制段 4 条 | `git log` 确认 c1abd1b = "tasks: T17 generalization bench task card"；文件实测 43 行、强制段 4 条 | ✅ 一致 |
| 27b-hw-costperf-decomp | 02-setup-repo | commit a21e606，ls-remote HEAD=a21e606… | a21e606 实为 "T18 rubric"，**非** loop/sop 同步 commit（同步是 1a0b0f6）；loop/sop 确已 push，门禁实质通过，但引用 commit 错误（见 V4） | ⚠️ 实质过、证据不准 |
| 27b-hw-costperf-decomp | 03-dispatch | T18-B/C 含强制段，33/32 行，commit 28f660d | `git log` 确认 28f660d = "T18 tasks: add mandatory 1-loop preamble"；文件实测 33/32 行、强制段齐全 | ✅ 一致（但首版缺强制段，见 V3） |
| gpu-27b-cost | 01-create-goal | history 为空，current_index=0 | 未推进，无虚假声明 | ✅ 无违规（但与 27b-hw-costperf-decomp 目标重叠，见 V8) |

**无虚假推进**：三个状态机的 current_index 均与 history 长度匹配，没有跳过门禁 advance 的痕迹。

## 四、T17/T18 任务书质量

| 项 | T17（43 行） | T18-B（33 行） | T18-C（32 行） |
|----|--------------|----------------|----------------|
| ≤50 行 | ✅ | ✅ | ✅ |
| 【执行前必读】强制段 | ✅ 4 条齐全 | ✅（28f660d 补） | ✅（28f660d 补） |
| 失败降级 | ✅ L7「通道故障→报告 Lead 降级」 | ✅ 同 | ✅ 同 |
| 数据源限制 | ❌ 无显式「只允许读/禁止读」清单 | ✅ 5 文件白名单 + 禁止读 gold/experiments/其他 tasks | ✅ 4 文件白名单 + 禁止读 mixed-load/gold/experiments |

T18 数据源白名单与 `bench/data-measured/` 实际文件一一对应（specs/decode-peak/context-scaling/concurrency/mixed-load 5 文件实测存在）。T17 作为泛化任务由 Lead 先造 gold、再派 agent，未设读取限制，存在 agent 读到 `bench/experiments/` 等资产的风险（见 V5）。

## 五、违规项清单（按严重度排序）

### V1【高】loop 阶段产出未落盘 loop-artifacts/stages/ —— SOP 核心不变量被破坏
- **要求**: SOP §0.2/§4「每阶段产出必须落盘 `loop-artifacts/stages/<N>/`」；04-arena-exec 门禁「loop-artifacts/ 有产出？」
- **证据**: 仓库无 `loop-artifacts/` 目录（`ls` 报错 No such file or directory）；T18-C 执行产出仅落 `bench/agent-runs/t18-C.md`（commit f366342，314 行单文件交付，无阶段化工件、无 loop 阶段引用）；更早的 agent1-6 方法论实验同样只落 `bench/experiments/`。
- **影响**: 27b 目标 04-arena-exec 门禁「loop-artifacts/ 有产出」按当前证据**不通过**；无法验证执行者是否真读了 loop/prompt-first 各阶段。
- **修复**: 要求执行方按 6 阶段补落 `loop-artifacts/stages/01..04.5/` 工件（ decomposition/research/crosscheck/actions/execution-log/review），或按 §3.3 正式降级并补 conf-0.2 标记；Lead 在 04 门禁核对时逐项检查该目录，空目录不得判过。

### V2【高】arena 首选通道疑似被本地执行替代，且无降级记录
- **要求**: SOP §0.1「arena 外包 = 必须首选通道」；§3.3 降级须记 `knowledge/efficiency-bottlenecks.md` + conf-0.2。
- **证据**: T18-C 执行 commit f366342（03:21:21）author = `xxmacbookpro`，与 Lead 全部 commit 同一 git 身份（arena 执行通常有不同 author）；03:09 派发 → 03:21 产出仅 12 分钟；仓库无 `knowledge/` 目录、无 efficiency-bottlenecks 记录、产出无 conf-0.2 标记。
- **置信度**: 高（基于 author + 时序 + 无降级记录的间接证据，非 100% 确证）。
- **影响**: 若为本地自答，违反 arena-first 硬规则且降级流程完全未走；T18-C 产出不能作为「arena 通道 + loop」的验证样本。
- **修复**: 核实 f366342 实际执行通道；若为本地执行，补记故障/降级原因到 `knowledge/efficiency-bottlenecks.md`，产出标 conf-0.2，并重新用 arena 通道跑 T18-B/C 作为对照。

### V3【中】T18 任务书首版缺【执行前必读】强制段，断点 C 防护事后补齐
- **要求**: SOP §1 步骤6/§2：任务书顶部强制段是断点 C 防护，必须随任务书首次提交。
- **证据**: `git show 33838fe:tasks/T18-measured-bench-B.md` 头部直接是「## 任务」，无强制段；`git show 28f660d --stat` 显示 8 分钟后以 "add mandatory 1-loop preamble (breakpoint C prevention)" 补 +7 行/文件。
- **影响**: 若 33838fe～28f660d 窗口内已有 arena 会话读到任务书，断点 C 即触发（任务书没被完整读到）。
- **修复**: 派发流程加一步「commit 前 grep 任务书头部含【执行前必读】」；已派发的 T18-B/C 要求执行方确认读到的是 28f660d 版本。

### V4【中】27b 02-setup-repo 门禁引用错误 commit
- **要求**: SOP §1 步骤4 硬门禁：验证文件记录**同步** commit hash + ls-remote 输出。
- **证据**: stage-gate `27b-hw-costperf-decomp.json` 02 evidence 与验证文件 `verify-decomp-bench-setup-20261028.md` 均记录 `a21e606`（实为 "T18 rubric"）；真正的 loop/sop 同步 commit 是 `1a0b0f6`。
- **影响**: 门禁实质通过（loop/sop 确已 push 且验证过），但断点 A 证据链指向错误 commit，回溯时会造成误判。
- **修复**: 验证文件补充/更正为 1a0b0f6（同步 commit），a21e606 仅作「验证时点 HEAD」备注。

### V5【中】T17 任务书无显式数据源限制
- **要求**: 任务书应明确执行方可读范围（T18 已做到，SOP §5 任务书质量原则）。
- **证据**: `tasks/T17-generalization-bench.md` 全文 43 行，无「只允许读/禁止读」清单；仓库内 `bench/experiments/`、`bench/gold*/` 对执行 agent 全部可见。
- **影响**: 泛化测试中 agent 可能读到方法论实验结论或既有 gold，污染「独立分解」的测试有效性。
- **修复**: T17 补数据源白名单（如仅 `bench/gold/` + `bench/TEST-CATALOG.md` + 新领域公开资料），禁止读 `bench/experiments/`、`bench/gold-<新领域>/`（造好前）。

### V6【低】decomp-research 02 evidence 文本损坏
- **证据**: `decomp-research.json` 02 evidence 含 "ls-remote HEAD = 1a0b0 **Alpaca**1a0b0f603f63fa32f4c9fa23d8ccaf5385c582ed"，夹杂无关字样。
- **影响**: hash 本身可核对无误，但证据文本可信度受损，疑似复制粘贴污染。
- **修复**: 重写该条 evidence，只保留可验证字段。

### V7【低】执行产出缺 `# origin:` 标记
- **证据**: `bench/agent-runs/t18-C.md` 无 origin 标记（AGENTS.md 意图校验原则要求产出标记 origin: human/ai）。
- **修复**: 产出模板加 origin 头。

### V8【低】gpu-27b-cost 与 27b-hw-costperf-decomp 目标重叠
- **证据**: `gpu-27b-cost.json` 停在 01-create-goal、history 为空（创建于 10-27 21:12），与 10-28 00:10 创建的 27b-hw-costperf-decomp 覆盖同一 27B 硬件选型任务。
- **影响**: 目标管理冗余，易造成状态机漂移。
- **修复**: 关闭或合并 gpu-27b-cost。

## 六、通过项（平衡记录）

- 断点 A 实质通过且双 goal 各有验证文件（`stage-gate-decomp-research-02-verify.md`、`verify-decomp-bench-setup-20261028.md`），含 commit hash + ls-remote 输出。
- 断点 B 通过：T17（c1abd1b）、T18（28f660d）均 commit+push，`git ls-remote origin HEAD` 可达（f366342）。
- loop/prompt-first 7 文件 + sop 与 workspace 源逐字节一致（diff 验证），同步范围正确（未 rsync 整个 loop/）。
- 任务卡全部 ≤50 行、含失败降级；T18 数据源限制明确且与实物文件吻合。
- stage-gate 01–03 门禁自检与仓库证据吻合，无跳过门禁的虚假推进。
- T17 强制段齐全（已知疑点不成立）。

## 七、对 Lead 的总评

Lead 在**流程外壳**（选仓库、同步 loop/sop、断点 A/B 验证文件、stage-gate 推进记录）上基本遵循 SOP，自检证据经得起核对；但在**流程内核**上失守：loop 阶段化落盘这一核心要求在执行侧完全没发生，arena 首选通道疑似被本地执行替代且降级流程未走，断点 C 防护首次未到位。04-arena-exec 阶段的门禁若按仓库现有证据严格核对，**不应判过**——尤其「loop-artifacts/ 有产出」一项当前为假。
