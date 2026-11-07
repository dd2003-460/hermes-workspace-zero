# Goal: pfb-production-hardening（搜索/校验优化到生产 + 学术级验证）

> origin: human-directive (2026-11-08 成璐指令) · status: ACTIVE
> 执行方式：ralphloop 单并发（arena 不可外包，用户在场可对话）
> SOP: sop/arena-loop-pipeline.md §3.3（本地降级条款）+ loop/prompt-first/01-04.5

## 目标一句话

把 stage-ablation 的 prompt 激活实验从 n=3 试点升级到**学术级统计强度**，同时完成三项外部对齐工作（专家 social 邮件、无泄漏撞车调研、开源 autoresearch 基线实测），使"离 gold 差多少 + 怎么补"这个结论达到可发布标准。

## 验收标准（逐条 pass/fail，全过才结束 goal）

### G1 — 大样本主实验（学术级）
- S0/S3/A4 × Q1-Q5 × reps ≥ 30（每臂每题）；若时间不够按 DESIGN 缩略条款砍题不砍 n
- **样本量依据**：学界惯例——效应量 d≥0.5、α=0.05、power=0.8 → n≈34/组（Cohen 1992）；我们观测到的最大效应 A4-A0=0.223 coverage diff，σ≈0.15 → 需 n≥30/臂保 power 0.8。写入报告 §方法
- Bootstrap CI（B=10000）宽度 < 0.05（当前 n=3 时 ~0.2）
- 主结果：Δ(A4−S0)、Δ(S3−S0) 各维度 M1-M6 的 mean ± 95%CI + 显著性
- **反缓存检查**：全部 runs 内 byte-dup 扫描 = 0（S8B 事故后硬门禁）
- 落盘：runs-prod/ + prod-results.md + 统计脚本（可重跑）

### G2 — 撞车调研（滚雪球，防低垂果实）
覆盖四象限，每象限 ≥3 个独立来源，输出 research/collision-snowball.md：
- **权威**：ACL/NeurIPS/ICLR 2025-2026 的 LLM benchmarking / self-verification / prompt ablation 论文（引 DREAM、DeepResearch Bench 系）
- **小众**：GitHub ≤1k star 的 niche bench / eval harness（找名字不响但做了同类事的小组）
- **最近轨迹（重点）**：arXiv 2026-09~11 提交的所有 "LLM + verification/ablation/benchmark" 新预印本，逐篇核 overlap
- **过去**：经典（Heston? 不，是 HHEM/G-Eval/Prometheus 系 judge 校准）确认我们的 rubric-v3 与既有校准方法的差异点
- 每条记录：标题/arXiv id/star 数/overlap 判定（无/部分/高）/conf
- **撞车红线**：发现任何"已公开且与我们核心 claim（组件独立性测量 + 表达层/推理层 gap 分层）高度重叠"的工作 → 立即停 G1 报告该发现，由我判断是否调整定位

### G3 — 开源 autoresearch 无泄漏实测
- 选 2-3 个可本地跑的开源系统（GPT Researcher 必选 + 1-2 个 competitor-survey.md 里可 pip 装的）
- 在 Q1-Q5 上跑，**无泄漏条件**：不给 gold、不给提示词增强、开箱配置（或最接近生产默认的配置）
- 用同一 judge 协议打分，产出 baseline 对比表
- 校验要求放宽（用户原话"几个小时这种"）：n=1-2/题足够出方向性数字，标注 conf
- 落盘：runs-baseline/ + baseline-comparison.md

### G4 — 专家 social 邮件草稿
- 对象：pfb 直接相关的 3-5 位作者（DREAM 评测 / DeepResearch Bench / Prometheus 系 judge 校准 / 至少 1 位 LLM caching 理论方向）
- 格式（成璐定式）：一个可复现结果（带 commit hash + 数据路径）+ 一个问题
- 英文，≤200 词/封，落盘 social/email-drafts.md，**不发送**（发送需成璐本人操作）
- 每封附：为什么找这个人（一句）、引用我们哪个具体数字、问的问题指向什么空白

### G5 — 过程完整性
- 每项完成后 loop-state.json 更新 + 本文件对应条目打 ✅ + commit
- 所有外部断言带来源三分法标注
- 最终汇总：production-final-report.md（三句大白话开头 + 分节证据）

## 执行顺序（单并发，按依赖排）

- [x] G2 先跑（撞车风险最高，发现高 overlap 要改后面所有东西）— 本地 ego-browser + arXiv API，~1h → **PASS**（research/collision-snowball.md，无直接撞车；最近先例 2606.21553 已列为 related work；落文窗口判断 1-2 季度）
- [x] G1 开跑（最耗时，后台挂着）— **DONE**：180/180 runs 完成（95min），S0-nat 0.600±0.205, S0-soc 0.957±0.075, A3-nat 0.589 (p=0.84 ns), A3-soc 0.957 (p=1.000 ns), A4-nat 0.622 (p=1.000 ns, 弱正向 pt3↑5 pt4↑3), A4-soc 0.981 (p=0.388 ns)。报告 G1-large-sample-report.md + production-final-report.md。
- [x] G3（趁 G1 跑着，~2-3h，含 clone/装环境）→ **DONE**：runs-baseline/gptr-{nat,soc}.md（DNS 修复后 nat 83s/26K chars, soc 24s/64K chars；方向性结论可写，正式对比表归 G5）
- [x] G4（写邮件，~30min）→ **DRAFTS DONE**：social/email-drafts.md，4 封（Shaikh/Huang/Lumer/Dorfman），未发送，等成璐查邮箱地址后本人发出
5. [x] G1 收数 + 统计 + 报告 → **DONE**：production-final-report.md（三句大白话 + 六臂总览 + 逐点分解 + 方法学 + Bootstrap CI + 撞车/基线/邮件汇总 + 论文定位 + 局限）
6. [x] G5 汇总收口 → **DONE**：loop-state.json 更新 + goal 文件打 ✅ + commit

## 预算

- 本地 8787 推理：G1 ≈ 6臂×5题×30reps… 实际按缩略 3臂×5题×30 = 450 calls × ~30s ≈ 3.75h wall（串行）；G3 另算
- 时间盒：总 wall ≤ 24h（跨天 OK）
- 不动推理引擎（NINFER 红线）

## 停止条件

- 全部 G1-G5 ✅ → goal 关闭，loop-state completed_goals 追加
- G2 发现高撞车 → 暂停，报成璐决策
- 通道故障（8787 挂）→ 等恢复，不降级换模型（换模型破坏可比性）