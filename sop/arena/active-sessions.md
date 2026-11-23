# Arena 活跃会话表（派发前唯一必查表）

> 一仓一会话硬约束（r80 + D 2026-11-01）：派发前查本表复用既有会话；仅当该仓库确无同向活跃会话才新开，开完立即登记本表 + `sessions.json`。同仓两个 active = 违规。
> 历史详情（事故/产出/commit）不写这里，写 `session-history.md`。本表每行 ≤2 行。

| 仓库 | 会话 | taskSpace | 当前任务 | 状态 |
|------|------|-----------|---------|------|
| prompt-first-bench | `01a1ca66-5358-7039-bcfa-b2fbf65a5a27` | tpr15-dispatch | T-PR-15/16/17 已交付(11-22) → **T-PUB-1 公式judge论文10题 已交付+核验(11-23, b148b12ed, 指纹一致, 47检查点SymPy自检PASS)**：7 full+3 rank-deficient；Lead 核 gold 发现 Q01 gold 漏 ×16 batch 因子(27b答788.5对)，已修；bool判分库已补(阻塞项#4解除) | ✅ done (11-23) |
| hermes-workspace-zero | `01a1f80e-4bfe-7566-9e03-52d0423a71ef` | arena-os1-dispatch-20261120 | **W6 T-PUB-1 claim强度评审 交付完成 @ df4e5d6d (arena/423a71ef 分支, 11-23 20:05)**; Lead 独立核验通过 (arena-claim-review-verification-20261123.md); 4/5 修复落地 @ 7b593678 (Q04 gold / guess_bound tol=0 / 措辞降级 / 统计修正); 剩扩题+异家族judge (workshop投后) | ✅ done-W6 (11-23) |

## 派发前检查（3 步，防连错仓库最小检查集）

1. `scripts/arena/dispatch-check.sh <repo>` —— 输出该仓活跃会话 + 门禁清单
2. 任务书已 commit+push 到目标仓库分支（`git log -1` 验证 sha）
3. prompt 显式声明目标仓库名 + 任务书路径 + 验收标准（防 agent 跨仓混用）

## 新开会话 SOP（2026-11-06 教训固化）

composer 先点 repo chip 选仓库 → 点 branch chip 选分支 → **再**发消息。直接发 clone 指令会被平台默认绑定（曾误绑 d1-video-recreation 拒执）。开完立即登记本表 + sessions.json。
