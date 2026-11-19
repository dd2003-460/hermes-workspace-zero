# intent-align-recall 分解 (r1)

> origin: ai | 2026-11-20 | goal intent-align-recall 00-decomp
> 用户原始要求（D 2026-11-20）：解决所有会感觉困惑/奇怪的以及影响功能的东西，包括 bug；
> 工程化思路：定位→整理线索→改动→对照验证。
> 本轮聚焦三个子目标：①意图对齐 ②对齐提醒（规则注入）有效性 ③规则 recall。

## 分解树

```
goal: 消除 D 的困惑/奇怪/功能影响 + 规则 recall 稳定
├── A 注入链路盘点（机制层：什么东西以什么身份进 context）
│   ├── A1 inject-rules.py 便签注入（routing.json 常驻+随机）— 已便签化 515 chars，机制清楚
│   ├── A2 stop_hook 两条注入路径（INBOX + continue message）— 已加来源标注 (a8db8d1)
│   ├── A3 proxy.mjs ZH tail（伪装 user 轮）— 已停用 (return false)，恢复路径已注释
│   ├── A4 USER.md/MEMORY.md system 层注入 — 每轮无条件加载，最稳定
│   └── A5 auto_continue_hook 的 INBOX 消费实现 — [待核验] 只找到 stop_hook 侧写入，
│       消费端（gateway 层怎么把 INBOX 变成 user message）未定位
│
├── B 对齐提醒有效性（行为层：注入了模型跟不跟）
│   ├── B1 注入审计日志（inject-rules.py 451 行起 JSONL）— 有送达证据，缺"模型是否执行"证据
│   ├── B2 已知失效案例：中文规则便签化后仍靠 USER.md 才稳定 → 便签层效力 < system 层
│   ├── B3 已知失效案例：proxy 尾部 user 轮被当用户指令回"收到"（本次乌龙）→ 身份伪装反噬
│   └── B4 量化基线：rule-injection-bench（runner.py/analyze.py/rubric.md 已有）— 未跑过 [待核验]
│
├── C 规则 recall（召回层：该想起的规则想不起来）
│   ├── C1 现象：用户报告"召回很不稳定，唯一稳定的是 USER.md 层的中文规则"
│   ├── C2 机制假设：system 层（每轮加载）> 便签层（条件/随机注入）> 按需 read_file
│   │   └── 验证方法：对同一规则做三位置 A/B（system/便签/仅索引），测遵循率 [待核验]
│   ├── C3 routing.json 随机轮询（autonomy 4-6轮/source-trace 5-8轮）— 命中间隔内 = 规则缺席
│   └── C4 便签 vs 全文的 trade-off：便签省 84% chars 但可能丢细节 → 哪些规则必须全文？
│
├── D 意图对齐（目标层：agent 做 D 想要的事）
│   ├── D1 D 的"想要"从哪来：USER.md 偏好 + qanda-ledger 历史问题 + 当前会话上下文
│   ├── D2 现有机制：goal-template 优先级/产投比 + autonomy.md 自主决策 + 自问便签
│   ├── D3 缺口：没有"主动做 D 会惊喜的事"的机制 — D 原话"做我想要的事情，或者会觉得惊喜的事情"
│   └── D4 便签换位思考实验（D 提议）：便签改成"你知道我想要什么吗/做到哪了/接下来还有什么"
│       → 让便签驱动自主对齐而非被动提醒 [待核验 可行性]
│
└── E 验证基础设施（对照层：改动前后怎么证明有效）
    ├── E1 复用 rule-injection-bench（已有 runner+analyze+rubric）
    ├── E2 最小对照实验设计：同一规则 × 三位置（system/便签/索引）× N 轮 → 遵循率
    └── E3 来源标注的验证：注入消息头部 [来源:...] 后，模型不再回"收到"（观察法，无量化）
```

## 正交性自检

- A（机制：什么进来）/ B（行为：跟不跟）/ C（召回：想不想得起来）/ D（目标：做对的事）/ E（验证：怎么证明）
- 逐对：A∩B 边界 = A 管"送达"，B 管"送达后执行"；A∩C 边界 = A 管注入链路，C 管召回策略；
  B∩C 边界 = B 是单条规则效力，C 是跨轮召回稳定性；D 独立（目标层）；E 独立（方法层）✓

## 缺口清单

1. [待核验] A5：auto_continue_hook 消费 INBOX 的实现位置（gateway 层，只找到写入侧）
2. [待核验] B4：rule-injection-bench 是否可跑通（runner.py 依赖什么模型/环境）
3. [待核验] C2：三位置 A/B 实验的遵循率基线（没跑过，纯假设）
4. [待核验] D4：便签换位思考的可行性（D 提议，未实验）
5. [待核验] gateway 重复投递（D 说重复消息是 gateway 问题，未验证具体机制）
6. [残留] proxy ZH tail 停用后中文思考是否还保持（停用是防乌龙，但原需求"中文思考"未解决）

## 任务表（03-exec 只执行表内条目）

| # | 任务 | 阶段 | 依赖 |
|---|------|------|------|
| T1 | A5 定位 INBOX 消费端 | 01-diagnose | - |
| T2 | B4 bench 跑通性检查 + 基线跑一轮 | 01-diagnose | - |
| T3 | C 三位置 A/B 实验设计 | 02-design | T2 |
| T4 | D4 便签换位思考便签文案 + 灰度 | 02-design | - |
| T5 | 按 design 执行改动（留备份+commit） | 03-exec | T3,T4 |
| T6 | 前后对照验证（verify.md） | 04-verify | T5 |
