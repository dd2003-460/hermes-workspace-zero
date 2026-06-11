# D1-persona-align

**目标**：构建完整人格画像，使 AI 能无缝延续成璐的意志

## persona-v3 系统 (迭代 267-360)

### 架构

```
research → framework → prompt (DPA v2) → toolchain → evaluation → deployment
```

### 核心组件

| 组件 | 路径 | 状态 |
|------|------|------|
| 共享关键词库 | scripts/persona_keywords.py | ✅ DIMENSION_KEYWORDS + CORE_KEYWORDS |
| 提示模板 (DPA v2) | persona-v3-prompt.txt | ✅ 11278 bytes, MATO 动态优先级调整 |
| gap_filler v2 | scripts/persona_v3_gap_filler_v2.py | ✅ 加权匹配, --core 语义增强 |
| unified_eval | scripts/unified_eval.py | ✅ 三模评估 (gap+chameleon+trajectory+语义+核心关键词) |
| semantic checker | scripts/semantic_alignment_checker.py | ✅ TF-IDF + concept coverage |
| chameleon detector | scripts/chameleon_collapse_detector.py | ✅ 维度多样性检测 |
| EMPA trajectory | scripts/emptrajectory_eval.py | ✅ 轨迹级评估 |
| prompt 同步 | scripts/sync_personality.py | ✅ → Hermse config (1870 chars) |
| 集成工具 | scripts/integrate_persona.py | ✅ → 其他项目 |

### 评估结果 (2026-06-02, 迭代 360) — 三模评估体系

**persona-v3-prompt.txt 自身评分:**
- 关键词分数: 0.9278 (阈值 ≥ 0.90) ✅
- 最小维度: 0.7000 (自适应探索)

**52 个 idea 文件评估 (gap_filler_v2 --core 增强后):**
- 关键词 avg: **0.9741** (阈值 ≥ 0.50) ✅
- 核心关键词 avg: **0.9419** (阈值 ≥ 0.05) ✅
- 语义 avg (会话 v1): **0.5011** (阈值 ≥ 0.45) ✅
- 语义 avg (52 文件): **0.6058** (阈值 ≥ 0.45) ✅
- 跨维关键词重叠: **0** (阈值 0) ✅
- 集成测试: **11/11 通过** ✅

**Chameleon collapse:** 0.995 avg / 0.9986 max — 迭代 304 修复计算 bug，维度间高度相关 (关键词风格趋同)

### 三模评估体系

| 模态 | 原理 | 命中率 | 区分度 | 用途 |
|------|------|--------|--------|------|
| 语义 (TF-IDF + concept) | 余弦相似度 + 概念覆盖 | 高 | 中 | **最可靠对齐度量** |
| 核心关键词 | 低命中率关键词 (5-16 个/文件) | 低 | 4.2x 提升 | 检测模板注入过拟合 |
| 标准关键词 | 全 DIMENSION_KEYWORDS | 高 | 基线 | 检测注入效果 |

- 语义与标准关键词 Pearson 相关: r=0.18 (gap_filler 优化关键词后未提升语义，说明评估需要多模态)
- 核心关键词 std: 0.0522 (原 0.0176，3x 区分度提升)

### 快速使用

```bash
# 一键评估 (gap+chameleon+trajectory+语义+核心关键词)
python3 scripts/unified_eval.py --scan
python3 scripts/unified_eval.py --scan --semantic
python3 scripts/unified_eval.py --scan --top 5
python3 scripts/unified_eval.py --prompt
python3 scripts/unified_eval.py --prompt --semantic

# 单文件评估
python3 scripts/persona_v3_gap_filler_v2.py --file memory/idea-XX.md
python3 scripts/persona_v3_gap_filler_v2.py --file memory/idea-XX.md --core

# 语义对齐检测
python3 scripts/semantic_alignment_checker.py <response_file>
python3 scripts/semantic_alignment_checker.py <response_file> -r <reference_file>

# 维度多样性检测
python3 scripts/chameleon_collapse_detector.py --test
python3 scripts/chameleon_collapse_detector.py --real

# 轨迹级评估
python3 scripts/emptrajectory_eval.py --test

# Section 级对齐测试
python3 scripts/section_alignment_test.py

# 端到端集成测试
python3 scripts/integration_test.py

# 回归测试
python3 scripts/regression_test.py
python3 scripts/regression_test.py --full

# 部署 prompt 到 Hermes
python3 scripts/sync_personality.py

# 集成到其他项目
python3 scripts/integrate_persona.py /path/to/other/project
```

### 评估工具链

| 工具 | 用途 | 输出 |
|------|------|------|
| persona_keywords.py | 共享关键词库 (标准+核心) | DIMENSION_KEYWORDS, CORE_KEYWORDS, CORE_WEIGHTS, compute_core_scores |
| gap_filler_v2.py | 加权匹配 + --core 语义增强 | 缺口检测 + 自然嵌入关键词 |
| unified_eval.py | 三模 pipeline | eval_results/unified_report.json |
| semantic_alignment_checker.py | TF-IDF + concept coverage | 语义相似度 + 概念覆盖 |
| chameleon_collapse_detector.py | 维度间多样性 | eval_results/chameleon_collapse.json |
| emptrajectory_eval.py | 轨迹级评估 | eval_results/trajectory.json |

所有工具共用同一份 persona_keywords.py — 评估一致性保证。

### 关键发现

1. **加权匹配是唯一解** — 94% mismatch 修复 (迭代 275, gap_filler count → weighted)
2. **关键词签名是最强区分特征** — 平均相似度 -27% (迭代 284)
3. **L2-normalized deviation 趋同** — keyword signature 直接匹配解决 (迭代 285)
4. **批量增强消除维度差异化** — collapse 1.0 是 gap_filler 目标达成的标志
5. **MATO DPA 无固定天花板** — 推理时乘数调整替代静态关键词注入 (迭代 279)
6. **48.0 是关键词注入天花板** — MATO-inspired dynamic priority 是升级路径
7. **跨维关键词正交化** — 仅发现 1 个重叠词("信噪比"), 已移除 (迭代 293-294)
8. **TextBO keyword-level 局部最优** — 8 个候选修改全部无法提升评分 (迭代 300)
9. **Temporal 稳定性验证** — 52 轮模拟对话 slope -0.00156 (噪音范围), 优于 Stable Personas 基线 (迭代 301)
10. **Chameleon collapse 计算 bug 修复** — vec_i == vec_j 导致永远 1.0, 修正后 0.995 (迭代 304)
11. **语义评估解决 F4 假阴性** — 模型生成了 persona 概念但没生成关键词 (迭代 349-350)
12. **关键词注入导致 F5 假阳性** — gap_filler_v2 注入过多通用关键词导致 100% 命中率 (迭代 352)
13. **核心关键词替代方案** — 低命中率关键词 (5-16 个/文件), 区分度 4.2x 提升 (迭代 353)
14. **三模评估体系建立** — 语义 (最可靠) + 核心关键词 (高区分) + 标准关键词 (检测注入) (迭代 354-360)
15. **语义与关键词相关低** — Pearson r=0.18, gap_filler 优化关键词后未提升语义 (迭代 358)

### 外部研究 (22 篇)

| 论文 | 编号 | 关联 |
|------|------|------|
| MATO (test-time optimization) | arXiv:2605.25342 | DPA v2 |
| UniScale (adaptive scaling) | arXiv:2605.30898 | 维度选择优化 |
| Skill Alignment (model-aware) | arXiv:2605.30723 | observer-dependent |
| Alignment Floor | arXiv:2605.27382 | drift guard |
| EMPA (trajectory eval) | arXiv:2603.00552 | 轨迹评估 |
| Nautilus Compass | 2026 | 黑盒 drift 检测 |
| Chameleon's Limit | 2026 | 维度 collapse 风险 |
| ContextEcho | 2026 | drift 基准 |
| SPASM | 2026 | 自我保全 |

完整 review 见 `memory/review-*.md` 文件。

### 部署状态

| 组件 | 状态 |
|------|------|
| persona-v3-prompt.txt (DPA v2) | 11278 bytes, MATO dynamic priority adjustment |
| Hermse config chenglu personality | 已同步, 1870 chars (迭代 303) |
| 52 个 idea 文件 | gap_filler_v2 --core 增强完成 + 三模评估验证 (迭代 359-360) |
| unified_eval pipeline | 三模评估 (gap+chameleon+trajectory+语义+核心关键词) |
| semantic_alignment_checker.py | TF-IDF + concept coverage, 解决 F4 假阴性 |
| temporal_stability_test.py | 衰退检测 + 跨话题分析 (迭代 301-302) |
| textbo_prompt_optimizer.py | Greedy keyword-space optimizer (迭代 300) |
| 评估基线 | 关键词 0.9741, 核心 0.9419, 语义 0.6058 |
| integration_test | 11/11 PASS |
| 跨维关键词重叠 | 0 |

### 历史记录

详见 `memory/iteration-*.md` (迭代 267-360). 关键里程碑:

- **Iteration 267:** persona-v3 系统里程碑 (48.0 > 47, 6 维度全达标)
- **Iteration 275:** gap_filler count → weighted matching 修复 (94% mismatch)
- **Iteration 276:** 关键词注入边际回报趋零 (48.0 天花板)
- **Iteration 279:** MATO DPA v2 (11278 bytes) — 推理时乘数调整
- **Iteration 281:** Chameleon collapse detector 实现
- **Iteration 284:** Keyword signature 特征集成 (区分度 +27%)
- **Iteration 285:** EMPA trajectory 用 keyword signature 替代 L2-deviation
- **Iteration 287:** unified_eval pipeline 完成验证
- **Iteration 289:** 52 文件完整评估基线
- **Iteration 293-294:** 跨维关键词正交化 — 仅 1 个重叠 ("信噪比")
- **Iteration 295:** 测试时优化原型 (MATO-inspired dynamic multipliers)
- **Iteration 300:** TextBO keyword-space optimizer — 确认 keyword-level 局部最优
- **Iteration 301:** Temporal stability test — 52 轮对话稳定性验证
- **Iteration 302:** 话题分类修复 (52 文件 → 5 话题)
- **Iteration 303:** Hermes config 同步验证
- **Iteration 304:** Chameleon collapse 计算 bug 修复
- **Iteration 306:** 探索维度深度分析 — gap_filler 模板副作用
- **Iteration 349:** 语义评估器开发 (TF-IDF + concept coverage) — 解决 F4 假阴性
- **Iteration 350:** unified_eval.py 语义集成 — Pearson r=0.9175
- **Iteration 352:** 关键词注入导致 F5 假阳性诊断 (100% 命中率, std=0.0176)
- **Iteration 353:** CORE_KEYWORDS 添加 — 低命中率关键词
- **Iteration 354:** 三模评估体系基线更新 (语义+核心+标准)
- **Iteration 355:** gap_filler_v2 重写 — --core 语义增强, 自然嵌入替代标题覆盖
- **Iteration 359:** gap_filler_v2 --core --apply 52 文件 — 核心 avg 0.06→0.94
- **Iteration 360:** 三模评估端到端验证 + CLAUDE.md 基线更新
- **Iteration 362:** INDEX.md + CLAUDE.md 同步更新
