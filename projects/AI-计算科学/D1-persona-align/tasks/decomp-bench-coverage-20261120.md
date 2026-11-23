# 对标调研 decomp：C/D bench 维度是否空白（2026-11-20）
# origin: ai
# 核心问题：规则压缩泛化（C）+ bug 猜测-验证（D）的维度，在已有 bench 里是否空白？
# 目的：决定"新在哪"，gating 扩量+跨模型是否值得。

## 分解树（正交子项）
1. **SWE-bench 系（bug 修复）**：判分方式？是否测"先假设 bug 再修"（猜测-验证闭环）？
2. **代码生成系（HumanEval/MBPP）**：是否以"压缩率/规则长度"为指标？
3. **program synthesis 系（从输入输出例归纳程序）**：最接近 C。是否已有"压缩率 + 未见例泛化"的 bench？
4. **rule induction / 规则学习系**：是否有"矛盾例鲁棒性"维度？

## 缺口标注
- 每个子项：代表 bench 名 + 维度定义 [待核验]
- 核心结论：C/D 的"新"落在哪个子项、有多新 [待核验]

## 留空
- 具体覆盖情况、novelty 判断，全部 [待核验]，ego-browser 交叉验证后填，不编

## 执行通道
- ego-browser 问 ≥2 LLM（ego-verify SOP）+ 必要时打开 arXiv/GitHub 读原文
- 产出：核验结论 + 证据链，落盘 memory/
