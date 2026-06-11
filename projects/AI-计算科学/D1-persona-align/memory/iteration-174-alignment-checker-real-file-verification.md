---
name: iteration-174-alignment-checker-real-file-verification
description: alignment_checker 在真实文件上的运行验证 — idea-01 得分 39.0, 3/6 维度缺失
metadata:
  type: project
  iteration: 174
---

# Iteration 174: alignment_checker 真实文件验证

## 操作
在 idea-01 (AI训练数据层级化) 上运行 alignment_checker.

## 结果
- 总分: 39.0
- 维度得分: 精度=1.0, 先验=1.0, 投影=1.0 (存在); 探索=0, 感知=0, 自我=0 (缺失)
- Verification ratio: 0.4 (有 6 个验证模式)
- Behavioral overall: 0.1958 (低, 静态文档而非行动输出)

## 验证
- eval_personas_responses.py: 单调递增 LOW(7.85) < MED(19.90) < HIGH(34.95) < PERF(55.90)
- alignment_checker 对真实文件: 正确识别维度缺失
- gap_filler 52/52 文件端到端验证通过

## 教训
所有三层评估工具在真实文件上运行正常。项目可以视为工程完成。
