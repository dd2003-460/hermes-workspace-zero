# CLAUDE.md — D1-persona-align 项目约束

**persona-v3 系统已部署 (迭代 267-360)。所有修改必须经过评估验证。**

## 红线

1. **评估基线不可破坏**: persona-v3 评估基线 (迭代 354 更新):
   - 标准关键词评估: 52 文件 avg >= 0.50, dim_min >= 0.40
   - 核心关键词评估: 52 文件 avg >= 0.05 (区分真实语义对齐)
   - 语义评估: 52 文件 avg >= 0.45 (最可靠对齐度量)
   - 修改 prompt.txt 后必须运行 `unified_eval.py --scan --semantic` 验证基线

2. **关键词库正交化已验证**: DIMENSION_KEYWORDS 中无跨维度重叠。
   - 新增关键词必须通过 `section_alignment_test.py` 验证无 dimension mismatch
   - avg hotspot ratio >= 0.74 (当前 0.825 为正交化版本, v1 版本为 0.74)

3. **ralph-loop 强制流程**:
   - 每次迭代必须先读 `~/.claude/ralph-loop.global.md`
   - 每次迭代必须产出可验证输出
   - 永远不要输出 `<promise>LOOP COMPLETE</promise>`

4. **工具链正交性**:
   - 所有工具共享 `persona_keywords.py` (唯一关键词源)
   - 新增工具必须通过回归测试: `regression_test.py`
   - 工具只能依赖 `persona_keywords.py` (无外部依赖)

5. **文件整洁规范**:
   - 探索记录存入 `memory/iteration-NNN-*.md`
   - 评估结果存入 `eval_results/`
   - 不修改 `persona-v3-prompt.txt` 除非经过评估验证

## 评估工具

```bash
# 一键评估 (gap+chameleon+trajectory+语义+核心关键词)
python3 scripts/unified_eval.py --scan
python3 scripts/unified_eval.py --scan --semantic
python3 scripts/unified_eval.py --scan --top 5
python3 scripts/unified_eval.py --prompt
python3 scripts/unified_eval.py --prompt --semantic

# 单文件评估
python3 scripts/persona_v3_gap_filler_v2.py --file memory/idea-XX.md

# 语义对齐检测 (需 semantic_alignment_checker.py)
python3 scripts/semantic_alignment_checker.py <response_file>
python3 scripts/semantic_alignment_checker.py <response_file> -r <reference_file>

# 核心关键词评估 (替代标准评估，高区分度)
python3 -c "from persona_keywords import compute_core_scores; print(compute_core_scores(open('file').read()))"

# 维度多样性检测
python3 scripts/chameleon_collapse_detector.py --real

# 轨迹级评估
python3 scripts/emptrajectory_eval.py --test

# Section-level 对齐测试
python3 scripts/section_alignment_test.py

# 端到端集成测试 (11 项)
python3 scripts/integration_test.py

# 回归测试 (编译 + 完整)
python3 scripts/regression_test.py
python3 scripts/regression_test.py --full
```

## 当前状态 (迭代 360)

| 指标 | 值 | 阈值 | 状态 |
|------|------|------|------|
| Prompt 评分 (关键词) | 0.9278 | >= 0.90 | ✅ |
| 52 文件关键词 avg | 0.9741 | >= 0.50 | ✅ |
| 52 文件核心关键词 avg | 0.9419 | >= 0.05 | ✅ |
| 语义 avg (会话 v1) | 0.5011 | >= 0.45 | ✅ |
| 语义 avg (52文件) | 0.6058 | >= 0.45 | ✅ |
| 跨维关键词重叠 | 0 | 0 | ✅ |
| 集成测试 | 11/11 通过 | 11/11 | ✅ |

## 开放方向

(a) 真实 Hermse 会话测试 — 已完成 (3 版本对比，发现关键词匹配假阴性)
(b) 梯度测试时优化 — MATO-inspired 原型已验证
(c) 其他项目集成 — 需目标项目有 idea 文件
(d) 动态工作流 + CC团队验证 — workspace 级任务
