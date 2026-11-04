# origin: ai — R6 结果摘要

> 2026-11-04 · arena agent 执行，Lead 验收

## 结论

**CONDITIONAL-PASS**：P0（阶段门控加载）在任务书定义下达标（M1=78.2 ≥ 70），但在单会话实际行为下不达标（M1=62.0 < 70）。

## 关键数字

| 指标 | run2 baseline | run6 Model A | run6 Model B |
|------|-------------|-------------|-------------|
| 单 turn 规则负载 | 12,086 tok | 3,023 tok (-75%) | 6,878 tok (-43%) |
| S (切分完整率) | 0.0 | 0.6 | 0.6 |
| R (规则重发惩罚) | 0.0 | 0.833 | 0.479 |
| G (膨胀比) | 0.57 | 1.000 | 0.848 |
| **M1** | **14.3/25** | **78.2** | **62.0** |

## 两个口径的差异

- **Model A**（阶段包口径）：harness 每 turn 只注入当前阶段 → 均值 3,023 tok
- **Model B**（单会话累计）：arena agent mode 实际行为，读入的规则不卸载 → 末态 11,011 tok（仅省 8.9%）

**核心洞察**：9 步走完全部 6 个阶段后，最终必然触达全部文件。门控只在中间阶段有效，末态收敛回全量。

## Arena agent 的额外发现

1. **路由表 v1.0 漏了 examples 层**（7 个文件，4,211 tok）→ 修正为 v1.1
2. **check-route-coverage.py**：漏载检测器，可挂 CI 门禁
3. **count-rule-tokens.js**：o200k 计量器，可复跑

## 下一步

- **P1（规则压缩）**：Model B 缺口 8 分。目标：单 turn 规则负载 < 2,000 tok
  - 最大文件：01-goal-decomposition (1,755) + 02-information-research (1,237)
  - 示例层 4,211 tok 也可瘦身
- **Harness 验证**：确认 arena 是否支持"按阶段重写任务书/重置上下文"（~10 turn 小 run）
- **S 分量天花板**：无服务端日志 → S ≤ 0.7 → M1 ≤ 82

## 交付物（pfb main @ 1a79bc2）

- `loop/prompt-first/INDEX.md`（v1.1 路由表）
- `sop/arena-loop-pipeline.md` §2（阶段门控指令）
- `tasks/_TEMPLATE-arena-task-brief.md`（新模板）
- `bench/self-opt-tester/runs/r6/*`（账本、打分、分析、检测器）
