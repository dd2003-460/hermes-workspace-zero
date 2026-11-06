# Decomp: D2 全书质量门禁（drift-check + 交叉引用）

# origin: ai · 2026-11-06 · goal d2-book-quality-gate

## 分解树

```
D2 质量门禁
├── A. drift-check 全章扫描
│   ├── A1. 跑 15 章 drift-check.py（ch1 已验证 100/100，剩 ch2-ch15）
│   ├── A2. 汇总分数表（章节 × 得分 × 漂移信号词）
│   └── A3. <90 的章节：定位具体漂移句 + 修复建议
├── B. 交叉引用一致性
│   ├── B1. 提取所有"第 N 章"引用 → 核对目标章存在且主题匹配
│   ├── B2. FULL-BOOK.md 目录 vs 实际章节标题一致性
│   └── B3. P1-P8 前提表引用（memory/book-skeleton.md）vs 各章实际引用
└── C. 交付
    ├── C1. quality-gate-report.md（分数表 + 问题清单 + 修复建议）
    └── C2. commit + push workspace
```

正交性自检：A（语言层：voice drift）⊥ B（结构层：引用完整性）⊥ C（交付）。完备性：v3-finalization-checklist §1 的两项（drift-check + 交叉引用终检）全覆盖。

## 缺口清单

| # | 子项 | 缺什么 |
|---|------|--------|
| G1 | A1 | ch2-ch15 的 drift 分数未跑 [待核验] |
| G2 | A3 | 哪些章节会 <90 未知 [待核验] |
| G3 | B3 | book-skeleton.md 的 P1-P8 表是否仍存在、格式是否可读 [待核验] |
| G4 | B1 | "第 N 章"引用的总数和分布未知 [待核验] |

## 执行说明

纯本地任务（drift-check.py 无第三方依赖），不需要 arena。直接 terminal 批量跑。

## 阶段 01 · 五字段分析

### 1. 本地背景扫描（4 项）
| # | 查什么 | 证据 |
|---|--------|------|
| B1 | drift-check.py 可用？ | `python3 scripts/drift-check.py ch1` → 100/100 ✓（无第三方依赖） |
| B2 | 15 章文件存在？ | `ls drafts/*.md` → 15 个章节文件 + FULL-BOOK.md ✓ |
| B3 | book-skeleton.md 存在？ | [待核验] G3 |
| B4 | 已有 quality report？ | `find -name "*quality*"` → 无 ✓（首次跑） |

### 2. 调研对象全集
候选 = 15 章 .md 文件（ch1-ch15）。排除：FULL-BOOK.md（是合并版，逐章跑更精确）、tasks/、memory/。无排除争议。

### 3. 正交维度
- A: 语言层（drift score per chapter）
- B: 结构层（cross-reference integrity）
- C: 交付层（report + git）
正交性：A 改文字不影响 B 的引用关系；B 发现问题不需要 A 重跑。完备性：v3 checklist §1 两项全覆盖。

### 4. 量化定义
- drift_score(ch_i) = drift-check.py 输出的 0-100 整数
- PASS_A: ∀i∈[1,15], drift_score(ch_i) ≥ 90
- cross_ref_count = |{ "第 N 章" patterns in all chapters }|
- broken_refs = |{ ref to non-existent or mismatched chapter }|
- PASS_B: broken_refs = 0

### 5. 任务书（本地执行，非 arena）
Step 1: for i in 1..15: python3 drift-check.py drafts/ch{i}.md > scores/{i}.txt
Step 2: parse scores → table
Step 3: grep "第.*章" across all chapters → verify targets
Step 4: write quality-gate-report.md
Step 5: commit + push
失败降级：drift-check.py 对某章报错 → 记录错误信息，该章标 N/A，不阻塞其他章。

### 验收标准
- [ ] A1: 15 行分数表落盘（chapter × score × top_drift_signals）
- [ ] A2: 每个 <90 章节有具体句子级修复建议
- [ ] A3: broken_refs = 0（或列出所有断链）
- [ ] A4: quality-gate-report.md committed + pushed
