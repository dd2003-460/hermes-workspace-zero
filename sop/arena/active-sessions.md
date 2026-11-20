# Arena 活跃会话表（派发前唯一必查表）

> 一仓一会话硬约束（r80 + D 2026-11-01）：派发前查本表复用既有会话；仅当该仓库确无同向活跃会话才新开，开完立即登记本表 + `sessions.json`。同仓两个 active = 违规。
> 历史详情（事故/产出/commit）不写这里，写 `session-history.md`。本表每行 ≤2 行。

| 仓库 | 会话 | taskSpace | 当前任务 | 状态 |
|------|------|-----------|---------|------|
| prompt-first-bench | `01a1ca66-5358-7039-bcfa-b2fbf65a5a27` | tpr15-dispatch | T-PR-15 Goodhart 调研 | 🔄 active (11-16) |
| hermes-workspace-zero | `01a1f80e-4bfe-7566-9e03-52d0423a71ef` | arena-os1-dispatch-20261120 | T-OS-1 完成(Q1-Q4, 撞车ICAL conf0.97); T-OS-2 11-20 19:05 派发, 疑似跑完但未 commit+push (页面 diff 有 4 个 Unknown file +190/+1038 行, 远端无交付物); **arena daily limit 撞墙, 明天 16:26 重置**; T-OS-3 公轴-定理agent设计碰撞调研 任务书已 push @42334c3a (sha256 b07c9244) 排队待发 | ⏸️ blocked-limit (11-20) |

## 派发前检查（3 步，防连错仓库最小检查集）

1. `scripts/arena/dispatch-check.sh <repo>` —— 输出该仓活跃会话 + 门禁清单
2. 任务书已 commit+push 到目标仓库分支（`git log -1` 验证 sha）
3. prompt 显式声明目标仓库名 + 任务书路径 + 验收标准（防 agent 跨仓混用）

## 新开会话 SOP（2026-11-06 教训固化）

composer 先点 repo chip 选仓库 → 点 branch chip 选分支 → **再**发消息。直接发 clone 指令会被平台默认绑定（曾误绑 d1-video-recreation 拒执）。开完立即登记本表 + sessions.json。
