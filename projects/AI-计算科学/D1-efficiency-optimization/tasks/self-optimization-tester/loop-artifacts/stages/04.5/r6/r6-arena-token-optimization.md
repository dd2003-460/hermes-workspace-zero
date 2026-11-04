# origin: ai — R6 候选 #3：Arena 通道 Token 重发优化

> 2026-11-04 · 基于 R5.5 bench 发现 + run2 token-counts.txt 实测数据

## 问题定义

run2 (arena 外部执行) M1=25，根因：**每轮全量重发 12,086 o200k tokens 规则负载**。

token-counts.txt 实测：
```
RULE LOAD (loop/prompt-first/*.md + sop/arena-loop-pipeline.md):
  00-common-review.md       4766B → 1238 o200k
  01-goal-decomposition.md  7644B → 2219 o200k
  02-information-research   5610B → 1633 o200k
  02.5-cross-check.md       2574B →  818 o200k
  03-action-decomposition   3714B → 1263 o200k
  04-execution-verification 3988B → 1262 o200k
  04.5-final-review.md      3458B → 1112 o200k
  arena-loop-pipeline.md    8104B → 2541 o200k
  TOTAL                    39858B → 12086 o200k
```

如果 arena 会话跑 T=30 turns，固定规则负载贡献 ≈ 12,086 × 30 = **362,580 tokens**（仅规则重发）。

## 优化方案（按 ROI 排序）

### P0: 阶段门控加载（Stage-Gated Loading）

**核心思路**：不一次性注入全部 7 个 loop 文件，而是只加载当前阶段 + 下一阶段。

| 阶段 | 需要加载的文件 | Token 估算 |
|------|--------------|-----------|
| 01-goal-decomposition | 00-common + 01 + 02 | 1238+2219+1633 = 5090 |
| 02-information-research | 00-common + 02 + 02.5 | 1238+1633+818 = 3689 |
| 02.5-cross-check | 00-common + 02.5 + 03 | 1238+818+1263 = 3319 |
| 03-action-decomposition | 00-common + 03 + 04 | 1238+1263+1262 = 3763 |
| 04-execution-verification | 00-common + 04 + 04.5 | 1238+1262+1112 = 3612 |
| 04.5-final-review | 00-common + 04.5 | 1238+1112 = 2350 |

**效果**：
- 单 turn 规则负载从 12,086 → ~3,700（平均），**降低 69%**
- T=30 turns 时总规则重发从 362,580 → ~111,000 tokens
- M1 量化公式中 R (规则重发惩罚) 从 0.0 → ~0.3-0.5（取决于实现方式）

**实施成本**：
- 修改 arena 任务书模板：不再贴全量规则，改为"先读 tasks/<id>.md 中的阶段路由表，按需 fetch 对应阶段文件"
- 或者：在仓库中创建一个 `loop/prompt-first/INDEX.md` 路由文件（~500 bytes），agent 根据当前阶段只读需要的文件
- 预估工作量：2-4h（写路由逻辑 + 测试 1 个完整 run）

### P1: 规则压缩（Rule Compression）

**核心思路**：将 7 个 loop 文件压缩为 1 个精简版（保留关键约束，删除示例和解释）。

| 文件 | 原始 | 压缩后估算 | 节省 |
|------|------|----------|------|
| 00-common-review.md | 4766B | ~1500B | 69% |
| 01-goal-decomposition.md | 7644B | ~2500B | 67% |
| 02-information-research.md | 5610B | ~1800B | 68% |
| 02.5-cross-check.md | 2574B | ~1000B | 61% |
| 03-action-decomposition.md | 3714B | ~1200B | 68% |
| 04-execution-verification.md | 3988B | ~1300B | 67% |
| 04.5-final-review.md | 3458B | ~1100B | 68% |
| arena-loop-pipeline.md | 8104B | ~2500B | 69% |
| **TOTAL** | **39858B** | **~12,900B** | **68%** |

**效果**：
- 单 turn 规则负载从 12,086 → ~4,000 o200k，**降低 67%**
- 与 P0 可叠加（阶段门控 + 压缩 = 单 turn ~1,300 tokens）

**实施成本**：
- 手动压缩每个文件（保留 hard constraints，删除 examples/explanations）
- 需要验证压缩后 agent 行为不变（跑 1 个对照 run）
- 预估工作量：4-8h（压缩 + 验证）

**风险**：
- 过度压缩可能导致 agent 遗漏关键约束 → 需要 A/B 测试
- 压缩版本维护成本高（原始文件更新时需同步）

### P2: 会话级缓存（Session-Level Caching）

**核心思路**：利用 arena 的 compaction 机制，让规则在第一次加载后进入 "memory" 而非每轮重发。

**现状**：arena 有 compaction（round1 run 笔记确认），但触发条件不明确。

**可能的实现**：
- 在任务书中显式指示："规则已加载，后续轮次不要重复引用，直接按规则执行"
- 或者：利用 arena 的 system prompt 持久化特性（如果支持）

**效果**：不确定（依赖 arena 平台行为）
**实施成本**：低（改任务书措辞）
**风险**：arena 可能不支持 system prompt 持久化，compaction 可能丢弃规则

### P3: 任务书瘦身（Task Brief Slimming）

**核心思路**：run2 的任务书本身 1,890 o200k（3 个 brief 文件），可以进一步精简。

**现状**：
- tasks/003-self-optimization-tester.md: 473 o200k
- bench/r3/run2/task-brief.md: 527 o200k
- bench/self-opt-tester/new-goal-20261023.md: 890 o200k

**优化**：
- 合并 3 个 brief 为 1 个自包含任务卡（~800 o200k）
- 删除冗余背景（agent 可以从仓库中读取）
- 预估节省：~1,000 o200k per turn

**效果**：单 turn 总负载从 13,976 → ~12,976（节省 7%）
**实施成本**：低（重写任务书）
**ROI**：低（相比 P0/P1 的 67-69% 节省）

## 推荐路径

**Phase 1（本周）**：P0 阶段门控加载
- 写 `loop/prompt-first/INDEX.md` 路由文件
- 修改 arena 任务书模板（引用路由表而非全量规则）
- 跑 1 个对照 run（run6），测量实际 token 消耗
- 验收：M1 ≥ 70（从 25 提升）

**Phase 2（下周）**：P1 规则压缩（可选）
- 如果 Phase 1 效果不够（M1 < 70），再做压缩
- 目标：单 turn 规则负载 < 2,000 o200k

**Phase 3（长期）**：P2 会话缓存调研
- 观察 arena compaction 行为
- 如果平台支持，考虑更激进的缓存策略

## 验收标准

- [ ] run6 (arena 通道) M1 ≥ 70
- [ ] 规则重发次数 ≤ 首次加载的 30%（R ≥ 0.7）
- [ ] 上下文膨胀比 ≤ 2.5x（G ≥ 0.57）
- [ ] 总加权分 ≥ 80（从 run2 的 62.4 提升）

## 依赖

- arena 通道可用（ego-browser）
- 至少 1 个完整的 9 步 run（~30-60 min）
- tokenizer 工具（用于精确测量）
