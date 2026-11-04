# origin: ai — M2/M5 客观化方案（R5.2 P1 修复）

**问题**: M2(任务书纪律) mean|Δ|=33.3, M5(迭代经济性) mean|Δ|=26.7。根因：DS 证据包缺任务书行数/轮数 → "无法判断"→给 50/60 默认分。

## 核心原则

**M2/M5 不应由评分器主观判断，应从文件/git log 直接提取。** 评分器只负责 M1/M3/M4/M6（需要判断力的指标）。

## M2 任务书纪律 → 客观计算

```python
def score_m2(task_brief_path):
    """从文件直接计算，不需要评分器。"""
    lines = len(open(task_brief_path).readlines())
    if lines <= 50:
        return 100
    elif lines <= 200:
        # 线性衰减：50行=100, 200行=60
        return 100 - (lines - 50) * (40 / 150)
    else:
        # >200行：每多50行扣10分，floor 20
        return max(20, 60 - (lines - 200) * (10 / 50))
```

**数据来源**: `wc -l < task_brief_path>`（已在 evidence-packet-template.md A 节定义）

**回算验证**:
| Run | 行数 | M2(客观) | CG原始 | DS原始 |
|-----|------|----------|--------|--------|
| run1 | 49 | **100** | 100 | 50 ← DS 错（缺信息→默认50） |
| run2 | 25 | **100** | 100 | 50 ← DS 错 |
| run3 | 25 | **100** | 100 | 100 ✓ |

→ 客观化后 M2 mean|Δ|=0（消除全部分歧）

## M5 迭代经济性 → 客观计算

```python
def score_m5(iteration_count, rework_events):
    """从会话日志/git log 直接计算。"""
    if iteration_count == 1 and not rework_events:
        return 100
    elif iteration_count == 1:
        # 有返工但一轮完成
        return 80 - len(rework_events) * 5
    elif iteration_count <= 3:
        return 80 - (iteration_count - 1) * 10 - len(rework_events) * 5
    else:
        return max(20, 50 - (iteration_count - 3) * 10)
```

**数据来源**: 
- `iteration_count`: 会话日志中该 run 的 turn 数（或 git commit 数）
- `rework_events`: 日志中标记为"修复/重跑"的事件数

**回算验证**:
| Run | 轮数 | 返工 | M5(客观) | CG原始 | DS原始 |
|-----|------|------|----------|--------|--------|
| run1 | 1 | 0 | **100** | 100 | 60 ← DS 错（缺轮数信息） |
| run2 | 1 | 2 | **90** | 100 | 100 |
| run3 | 1 | 0 | **100** | 100 | 60 ← DS 错 |

→ 客观化后 M5 mean|Δ| 大幅缩小（DS 的 60/100/60 → 100/90/100）

## 对 κ 的预期影响

当前 CG vs DS κ=0.064（n=18, 5-bucket）。

如果 M2/M5 改为客观计算（两方拿同一份数据→同一分数）：
- M2: Δ 从 [50,50,0] → [0,0,0]
- M5: Δ 从 [40,0,40] → [10,0,10]（run2 有 2 次返工，CG 可能没注意到）
- 剩余 4 指标 mean|Δ| ≈ 14.8 → κ 预计提升到 0.3-0.4 区间

## 实施步骤

1. 证据包模板已含 `task_brief_lines`（A节）和 `iteration_count`/`rework_events`（E节）✓
2. 下一轮 bench 执行时，Lead 直接从文件提取 M2/M5 分数，不发给评分器
3. 评分器 prompt 只要求打 M1/M3/M4/M6（4 指标 × n_runs）
4. 最终总分 = 客观 M2 + 客观 M5 + 评分器 M1/M3/M4/M6（加权求和）
5. κ 只在 M1/M3/M4/M6 上计算（消除客观指标的"假一致"）
