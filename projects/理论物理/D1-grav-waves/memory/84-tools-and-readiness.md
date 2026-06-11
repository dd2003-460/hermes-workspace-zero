---
name: iteration 84-tools-and-readiness
description: arxiv_submit.sh 中文检测增强、papers_readiness.sh 综合检查工具、原创性搜索验证
type: reference
---

## Iteration 84 完成（2026-05-12）

### 工具改进
1. **arxiv_submit.sh v2** — 添加非 ASCII（中文）字符检测，在编译前警告，防止类似 D1-grav-waves v3 的中文引用问题再次进入 tarball
2. **papers_readiness.sh** — 综合就绪度检查工具，一次性检查所有 D1 项目的 tarball、PDF、工具链状态

### 原创性验证
- arXiv 搜索 "2-category + gravitational wave" → 无结果
- arXiv 搜索 "functorial QFT + pulsar timing" → 无结果
- 确认 DistCat + D1-grav-waves 框架的原创性

### 就绪度检查结果
- PASS: 16/16 (D1-grav-waves: 6, D1-academic-AI: 5, 工具链: 5)
- FAIL: 0
- WARN: 0
- 结论: 论文全部就绪，等待作者确认提交

### 待办
- EMRI Paper I ρ_s→0 极限推导 (JCAP 要求，已有方案)
- DistCat 引用命令补全 (\cite{} → 当前只有 inline 编号列表)
