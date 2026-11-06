# T17 LoCoMo Memory Benchmark — Decomp

> origin: ai · 2026-11-06 · goal: t17-locomo-memory-bench

## 背景

T17 是 pfb prompt-first 方法论在 memory benchmark 域的泛化验证。此前已完成：
- LoCoMo conv4 baseline: overall 71.3% (rerun#1), entity-guard rerun#2: 82.0% (+10.7pp)
- OD (out-of-distribution) 诊断: 5/8 失败题答案实体不在源文本 → OD ceiling ~43-50%
- 当前 OD 42.9% 已接近实际可达上限
- 核心发现: 概念迁移成功(C1-C3稳) + 形式纪律需显式注入(S2/S3不自发) + 单run噪声≥域间差

**本轮目标**: 不是重跑已有实验，而是把 T17 收口为可复现的 benchmark 套件 + 最终报告，对标顶刊 benchmark paper 标准。

## 分解树

### A. Benchmark 套件完整性（可复现性）
- A1: runner 脚本参数化（model, prompt variant, n_runs, seed, top_k）
- A2: 数据管线固化（LoCoMo conv4 → questions → answers → gold assertions）
- A3: scoring pipeline 版本锁定（rubric version, judge model, temperature）
- A4: 一键复现入口（`run_benchmark.sh --config X.yaml` → runs/ + scores.json + report.md）
- A5: 文档（README: 怎么跑、怎么读结果、已知限制）

### B. 实验矩阵补全（统计效力）
- B1: 当前 n=2/run（baseline + entity-guard），需 ≥3 arms × ≥3 runs/arm
- B2: Arms 设计: S0(no guard) / S1(entity-guard) / S2(guard+discipline-injection)
- B3: 每 arm ≥3 runs（temp=0.1, different seeds）→ mean ± σ
- B4: 显著性检验（paired t-test or Wilcoxon, per-question + pooled）
- B5: [待核验] 是否需要 cross-conversation 验证（conv1/2/3）还是 conv4-only 足够

### C. 报告写作（对标顶刊）
- C1: 方法节（prompt variants 完整描述 + rubric 定义 + judge protocol）
- C2: 结果节（per-arm × per-question table + significance + effect size）
- C3: 分析节（OD ceiling 论证 + 失败模式分类 + 与 pfb stage-ablation 的对照）
- C4: 限制节（n=5 questions, single conversation, same-family judge, OD ceiling）
- C5: [待核验] 目标 venue（arXiv preprint vs. workshop paper）决定格式

### D. 与 pfb 主论文的关联
- D1: T17 作为 pfb paper §5 "Generalization" 节的支撑证据
- D2: 交叉引用（pfb paper 引用 T17 report, T17 report 引用 pfb methodology）
- D3: [待核验] T17 是否独立成文还是作为 pfb appendix

## 缺口清单

| # | 子项 | 缺什么 | 来源 |
|---|------|--------|------|
| G1 | B5 | cross-conversation 必要性判断 | 需读 LoCoMo 数据集结构 + 时间预算评估 |
| G2 | C5 | 目标 venue | 等成璐确认 or 默认 arXiv preprint |
| G3 | A1 | 现有 runner 代码位置 + 接口 | 需 grep tools/memory-benchmarks/ |
| G4 | B1 | 当前 runs 目录结构 + 已有 scores | 需 ls runs/ + read scores.json |
| G5 | D3 | T17 独立 vs. appendix 决策 | 产投比: 独立成文工作量大但影响力高 |

## 正交性自检

- A(套件) ⊥ B(实验): A 是基础设施, B 是用基础设施跑的实验 ✓
- A(套件) ⊥ C(报告): A 产出代码, C 产出文字 ✓
- B(实验) ⊥ C(报告): B 产出数据, C 消费数据 ✓
- C(报告) ⊥ D(关联): C 是 T17 自身, D 是 T17 与外部(pfb)的关系 ✓
- 完备性: 从"能复现"到"能发表"全链路覆盖 ✓

## 优先级排序（产投比）

1. **A4+A5** (一键复现+文档): 最高产投比——让任何人在 5 min 内复现全部结果
2. **B1-B4** (实验矩阵): 中产投比——需要 GPU 时间但产出硬数据
3. **C1-C4** (报告): 中产投比——写作工作, 依赖 B 的数据
4. **D1-D3** (关联): 低优先——等 C 完成后再做
5. **A1-A3** (参数化): 低优先——如果 A4 直接封装了这些

## 执行策略

- 本地 vLLM :8787 (qwen3.8-27b) 跑实验, 不外包 arena (GPU inference 不可外包)
- 报告写作可外包 arena (调研/写作类)
- 预计总时间: A(1h) + B(2-3h GPU) + C(1h) + D(30min) ≈ 5-6h

## Stage 01: 五字段

### 1. 本地背景扫描（4 项）

| # | 查什么 | 证据 |
|---|--------|------|
| B1 | 现有 runner 代码 | `tools/memory-benchmarks/benchmarks/locomo/run.py` + `run-conv4-rerun.sh`（绕过 TUN 代理直连 :8787） |
| B2 | 已有 results | 10 个 JSON (results/locomo/)，最新 full01-eg: 178 evals, top_50=82.0%, top_10=78.1% |
| B3 | mem0 服务状态 | `curl :8888/health` → ok (llm=openai, embedder=fastembed) |
| B4 | vLLM 状态 | `curl :8787/health` → ok (qwen3.8-27b) |

### 2. 调研对象全集

**候选 arms**:
- S0: no entity-guard (baseline, user_id=locomo_4_full01) — 已有 681 evals
- S1: entity-guard (user_id=locomo_4_full01-eg) — 已有 178 evals
- S2: entity-guard + discipline injection [待核验: prompt 变体是否存在]

**排除项**:
- cross-conversation (conv1/2/3): 时间预算不允许（每 conv ~2h GPU），且 decomp G1 标注为待核验
- 不同 model: 超出 T17 范围（T17 是 prompt 方法论验证，不是 model comparison）

### 3. 正交维度拆解

- **Arm 维度** (S0/S1/S2): prompt 结构变体 ✓ 正交
- **Run 维度** (n≥3/arm): 随机性控制 ✓ 正交
- **Cutoff 维度** (top_10/20/50/200): retrieval depth ✓ 正交
- **Category 维度** (multi-hop/temporal/etc.): question type ✓ 正交
- 完备性: arm × run × cutoff × category 覆盖全部变异源 ✓

### 4. 量化定义

- **Overall accuracy** = correct_judgments / total_questions × 100%（per cutoff, per arm, mean over runs）
- **OD rate** = out_of_distribution_failures / total_questions × 100%（答案实体不在源文本中的失败占比）
- **ΔEG** = acc(S1) − acc(S0)（entity-guard effect size, per cutoff）
- **Significance**: paired Wilcoxon signed-rank test (n=178 questions, paired by question_id across arms), p < 0.05
- **Target**: ΔEG ≥ 8pp at top_50, OD ≤ 45%, overall(S1) ≥ 80%

### 5. 任务书

**执行方式**: 本地直接跑（GPU inference 不可外包 arena）
- Step 1: 确认 S0 baseline 完整（681 evals 是否覆盖全部 178 questions × 所有 categories）
- Step 2: 补跑 S0 缺失 questions（如有）+ S1 缺失 questions（178→full set）
- Step 3: 每 arm 跑 3 seeds（temp=0.1, seed=42/1337/2026）
- Step 4: 汇总 scores.json（per arm × per cutoff × per category, mean ± σ）
- Step 5: 显著性检验 + OD 诊断
- Step 6: 写报告（对标顶刊 benchmark paper 格式）

**失败降级**: vLLM 挂 → 重启; mem0 挂 → 重启; 单 run 超时 → resume（脚本已支持 --resume）

### 6. 验收标准

| # | 指标 | 阈值 | 可机器检查 |
|---|------|------|-----------|
| A1 | S1 overall (top_50, mean of 3 runs) | ≥ 80% | scores.json |
| A2 | ΔEG (S1−S0, top_50) | ≥ 8pp | scores.json |
| A3 | OD rate (S1) | ≤ 45% | od-diagnosis.json |
| A4 | Runs per arm | ≥ 3 | ls runs/ |
| A5 | Significance (Wilcoxon, top_50) | p < 0.05 | stats.json |
| A6 | Report exists + word count | > 2000w | wc -w report.md |
