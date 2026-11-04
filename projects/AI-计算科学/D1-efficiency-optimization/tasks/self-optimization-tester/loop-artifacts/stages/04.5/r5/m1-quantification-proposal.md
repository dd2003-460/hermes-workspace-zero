# origin: ai — M1 Token 效率量化锚点提案（R5.2 P1 修复）

**问题**: 当前 M1 定义"浪费越小分越高"无量化标准，导致 CG(78/25/95) vs DS(55/25/60) mean|Δ|=19.3。

## 量化定义

M1 = 100 × (W_split × S + W_reload × R + W_growth × G)

其中：
- **S (run级切分完整率)**: 0-1
  - 有 per-request input token 日志且可切分到 run 窗口 → 1.0
  - 仅有会话累计、后补切分 → 0.5
  - 无任何 token 数据 → 0.0 (标 unmeasurable)
  
- **R (规则重发惩罚)**: 0-1
  - 每轮规则负载 ≤ 首次加载的 10% → 1.0
  - 每轮全量重发（如 12,086 o200k/轮）→ 0.0
  - 线性插值: R = 1 - (reload_bytes / first_load_bytes)

- **G (上下文膨胀比)**: 0-1
  - growth_ratio = last_request_input / first_request_input
  - ratio ≤ 1.5x → 1.0
  - ratio ≥ 5x → 0.0
  - 线性: G = max(0, (5 - ratio) / 3.5)

权重: W_split=0.4, W_reload=0.35, W_growth=0.25（初始值，n≥5 后校准）

## 示例打分

| Run | S | R | G | M1 |
|-----|---|---|---|-----|
| run1 (后补切分, 无重发, 膨胀~2x) | 0.5 | 1.0 | 0.86 | 100×(0.4×0.5+0.35×1.0+0.25×0.86)=66.5 |
| run2 (无切分, 每轮全量重发, 膨胀~3x) | 0.0 | 0.0 | 0.57 | 100×(0+0+0.143)=14.3 |
| run3 (完整切分, 无重发, 膨胀~1.5x) | 1.0 | 1.0 | 1.0 | 100×(0.4+0.35+0.25)=100 |
| run4 (完整切分, 无重发, 膨胀~1.2x) | 1.0 | 1.0 | 1.0 | 100 |

对比原始分: CG(78/25/95/90) vs DS(55/25/60/—)
→ 量化后两方应给出接近的分值（差异仅来自数据精度）

## 实施条件

1. 证据包必须含 `total_input_tokens`, `request_count`, `run_level_split_available`, `rule_reload_bytes_per_round`, `context_growth_ratio`（已在 evidence-packet-template.md B 节定义）
2. 缺任一字段 → M1 标 unmeasurable，不给默认分
3. 权重 W_* 在 n≥5 runs 后用 Pearson r 校准（同 M1-M6 权重校准流程）

## 与现有 bench 的兼容性

- 不改变 M1-M6 指标集合，只细化 M1 的打分规则
- 旧 run 数据可回算（从已有日志提取 S/R/G）
- 新 run 从证据包模板直接获取所需字段
