# P2 实验数据收集模板

# origin: ai

> 成璐选渠道后直接用这个模板收集数据。Google 表格 / 本地 CSV 都行。

## 数据结构

| 字段 | 类型 | 说明 |
|------|------|------|
| reader_id | int | 读者编号 (1-30) |
| channel | str | 招募渠道 (A/B/C/D) |
| signup_date | date | 报名日期 |
| pre_score | float | 前测打分 (0-10, 对"KPI = Δ信念/Δ成本"命题) |
| chapters_read | int | 读完章节数 (0-14) |
| post_score_30d | float | 第 30 天后测打分 (0-10) |
| post_score_90d | float | 第 90 天留存测打分 (0-10) |
| notes | str | 备注 (可选) |

## 初始化脚本

```python
import csv
from datetime import datetime

# 创建空模板
fields = ['reader_id', 'channel', 'signup_date', 'pre_score', 
          'chapters_read', 'post_score_30d', 'post_score_90d', 'notes']

with open('p2-data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

print("p2-data.csv created. Add readers as they sign up.")
```

## 分析脚本（数据齐后跑）

```python
import csv
import statistics

with open('p2-data.csv') as f:
    rows = [r for r in csv.DictReader(f) if r['reader_id']]

n = len(rows)
print(f"Readers: {n}/30")

# 前测均值
pre_scores = [float(r['pre_score']) for r in rows if r['pre_score']]
pre_mean = statistics.mean(pre_scores) if pre_scores else None
print(f"Pre-test mean: {pre_mean:.2f}" if pre_mean else "No pre-scores yet")

# 后测均值 (30d)
post30 = [float(r['post_score_30d']) for r in rows if r['post_score_30d']]
if post30:
    post30_mean = statistics.mean(post30)
    delta = post30_mean - pre_mean
    print(f"Post-30d mean: {post30_mean:.2f}")
    print(f"Belief change rate: {delta:.2f} (gate: ≥4.0)")
    
    # 阅读完成率
    completed = sum(1 for r in rows if int(r['chapters_read']) >= 14)
    completion_rate = completed / n
    print(f"Completion rate: {completed}/{n} ({completion_rate*100:.1f}%) (gate: ≥50%)")
    
    # KPI
    kpi = delta / completion_rate if completion_rate > 0 else None
    print(f"KPI: {kpi:.2f}" if kpi else "KPI: N/A")
else:
    print("No post-30d scores yet")

# 留存率 (90d)
post90 = [float(r['post_score_90d']) for r in rows if r['post_score_90d']]
if post90 and post30:
    retention = statistics.mean(post90) / statistics.mean(post30)
    print(f"90d retention: {retention*100:.1f}% (gate: ≥30%)")
else:
    print("No 90d data yet")

# 判死条件检查
print("\n--- Gate Checks ---")
if completion_rate is not None:
    print(f"✓ Completion ≥50%: {'PASS' if completion_rate >= 0.5 else 'FAIL'}")
if delta is not None:
    print(f"✓ Belief change ≥4.0: {'PASS' if delta >= 4.0 else 'FAIL'}")
if retention is not None:
    print(f"✓ Retention ≥30%: {'PASS' if retention >= 0.3 else 'FAIL'}")
```

## 使用流程

1. 成璐选渠道 → 发招募文案
2. 读者报名 → 填 reader_id + channel + signup_date + pre_score
3. 30 天后 → 填 chapters_read + post_score_30d
4. 90 天后 → 填 post_score_90d
5. 跑分析脚本 → 看 gate 是否过