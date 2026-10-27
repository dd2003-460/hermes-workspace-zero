# 效率优化 R1 结果：SOP/loop 瘦身实验

> origin: ai · 2026-10-26 · goal-ffa691bf 自主循环

## 实验目的
验证 goal-template 瘦身 + loop 阶段文件示例外移是否减少 token 占用。

## 结果

| 优化项 | 旧（字符/token） | 新（字符/token） | 减少 |
|--------|-----------------|-----------------|------|
| goal-template.md | 19336 / 4834 | 4623 / 1155 | 76% |
| loop 阶段文件（6 个核心流程） | 26988 / 6747 | 17138 / 4284 | 36% |
| **合计** | **46324 / 11581** | **21761 / 5439** | **53%** |

## 方法
- 字符数 ÷ 4 估算 token 数（中文混合文本近似）
- 旧版从 git 备份（goal-template.md.bak-20261026 / git show f19f2efd）
- 新版为当前工作区文件

## 结论
- goal-template 瘦身效果显著（76%），定位器式结构（五字段+指针）有效
- loop 示例外移减少 36% 核心流程文本，数学示例（324 行）按需读取
- 每次创建 goal + arena 执行 loop 时，注入文本减少约 53%（约 6142 token）

## 副作用检查
- ✅ 新 goal 按五字段模板创建成功（goal-ffa691bf）
- ✅ 阶段文件结构完整（操作流程→Reviewer 标准→示例指针→通用原则）
- ✅ SOP-INDEX 和 arena-loop-pipeline 同步更新
- ✅ acp_rule 硬规则自动加载段已合并回 goal-template §3

## commit 记录
- f19f2efd: goal-template 瘦身 + git 清理
- 57148237: loop 示例外移
- 6d5a7f77: SOP-INDEX 更新
- 55d81a4d: arena-loop-pipeline 更新
- bc3d97b4: acp_rule 合并
- 9fb98e3f: addon 标记已合并
