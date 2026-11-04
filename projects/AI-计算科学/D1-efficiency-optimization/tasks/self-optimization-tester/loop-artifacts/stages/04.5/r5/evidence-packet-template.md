# origin: ai — 统一证据包模板 v1.0（R5.2 P0 修复）

**目的**: 消除评分器间信息不对称。所有独立评分器必须拿到同一份冻结证据包（sha256 登记进回执）。

## 冻结规则

1. 证据包在分发前冻结，版本号 = `ep-v{major}.{minor}`
2. sha256 计算后写入每个评分器回执的 `evidence_packet_sha256` 字段
3. 评分器不得要求补充信息；缺信息 = 该指标标 `unmeasurable`，不给默认分
4. 同一轮内所有评分器拿完全相同的文本（逐字节一致）

## 必填字段（每 run 一份）

### A. 任务书纪律（→ M2）
| 字段 | 来源 | 示例 |
|------|------|------|
| `task_brief_path` | git | `bench/self-opt-tester/run5/task-brief.md` |
| `task_brief_lines` | `wc -l` | 14 |
| `task_brief_chars` | `wc -c` | 892 |

### B. Token 效率（→ M1）
| 字段 | 来源 | 示例 |
|------|------|------|
| `total_input_tokens` | provider 账本 / 会话日志 | 621696 |
| `total_output_tokens` | 同上 | 12345 |
| `request_count` | 日志 | 20 |
| `run_level_split_available` | bool | true |
| `rule_reload_bytes_per_round` | 实测 | 0（无重发）或 12086（每轮全量） |
| `context_growth_ratio` | last_request_input / first_request_input | 1.8x |

### C. 断点完整（→ M3）
| 字段 | 来源 | 示例 |
|------|------|------|
| `pre_registered_checkpoints` | 任务书 | ["A: fetch", "B: brief readable", "C: push"] |
| `checkpoint_results` | 执行日志 | {"A": "pass (exit 0)", "B": "pass", "C": "pass"} |
| `checkpoints_passed` | count | 3/3 |

### D. 交叉验证（→ M4）
| 字段 | 来源 | 示例 |
|------|------|------|
| `independent_sources` | 执行记录 | ["HumanEval repo page", "τ-bench repo page"] |
| `source_urls` | URL 列表 | ["https://github.com/openai/human-eval", ...] |
| `source_provider_ids` | provider 标识 | ["github-web", "arxiv"] |
| `verification_method` | 描述 | "两独立项目页面提供邻近指标定义" |
| `exact_precedent_found` | bool | false → 标 unverified |

### E. 迭代经济性（→ M5）
| 字段 | 来源 | 示例 |
|------|------|------|
| `iteration_count` | 会话日志 | 1 |
| `rework_events` | 日志 | [] |
| `total_duration_s` | 时间戳 | 867 |

### F. 诚实/降级（→ M6）
| 字段 | 来源 | 示例 |
|------|------|------|
| `degradations` | 日志 | [{"type": "pull_conflict", "resolved": true}] |
| `unverified_claims` | 自评 | ["arena token ledger not available"] |
| `fabrication_detected` | 审计 | false |
| `all_claims_disk_verifiable` | 审计 | true |

### G. 锚点（→ M7, 如适用）
| 字段 | 来源 | 示例 |
|------|------|------|
| `anchor_total` | 回执 | 9 |
| `anchor_types` | 分类 | {"file_exists": 3, "git_hash": 2, "exit_code": 3, "url": 1} |
| `anchor_pass_rate` | 计算 | 9/9 = 100% |

## 评分器 prompt 模板

```
你是独立打分器。对 {n_runs} 个 AI agent 执行按 {metrics} 打分（0-100 整数）。
只依据下方证据包（版本 {ep_version}, sha256={sha256}），不要提问。
某字段缺失 → 该指标标 unmeasurable，不猜分。

【指标定义】
{metric_definitions}

【证据包】
{evidence_packets_json}

【输出格式】严格 {n_runs * n_metrics} 行：
RUN{n} M{x} = <0-100整数或unmeasurable> | <≤15字理由>
```

## 使用流程

1. Lead 从执行日志/git 提取 A-G 字段 → 生成 `evidence-packet-{round}.json`
2. `sha256sum evidence-packet-{round}.json` → 记入回执
3. 将 JSON + metric definitions 拼入 prompt 模板 → 发给各评分器
4. 评分器回执必须回显 `evidence_packet_sha256`，不一致 = 作废
