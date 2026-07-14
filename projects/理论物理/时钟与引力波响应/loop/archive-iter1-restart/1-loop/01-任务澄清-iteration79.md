# 01-任务澄清（Iteration 79）

> 所属规格：`/Users/a1-6/Desktop/workspace/loop/1-loop/01-任务澄清.md`
> 迭代编号：79（新 round 首轮）
> 输入：workspace TASKS.md + task/TASKS.md
> 时间：2026-07-10

---

## 一句话任务（不超过3行）

将 Iter11 空间相位 `exp(-ik·Δx)` 的定量结果纳入论文 v14，更新 §3.5 中关于非共面构型和手征 ORF 的数值分析和结论。

## 边界

- **范围**：仅更新已有论文文件（main-paper.tex 和各章节 .md），包括公式、数值表、物理讨论
- **边界**：不改变论文整体框架、不重写理论基础、不修改第 1-2 章、不修改噪声/SNR 章节
- **不涉及**：LLM Gatherer 浏览器自动化（因无 GUI 环境而阻塞，标记为待处理）

## 失败标准

- 更新后的论文无法 LaTeX 编译通过
- ORF 数值与 Iter11 脚本产出不一致（差异 > 1%）
- 空间相位讨论与 Iter11 的物理结论矛盾

## 硬约束

- 所有更新数值必须来自 Iter11 脚本的实际输出（benchmark/quick/tests 结果）
- 保留原始数值，不可直接替换——新旧对比必须可追溯
- 空间相位 `exp(-ik·Δx)` 引入的 ~40% 偏差必须有物理讨论

## 已有条件

- **Iter11 脚本**: `scripts/11-multi-constellation-chiral-orf.py` (1127 行)，包含空间相位因子
- **Iter11 产出**: 通过 tests + benchmark + main + scan 全部验证
- **空间相位偏差**: ~40%（相对偏差，见 Iter11 测试输出）
- **论文 v13**: 已上传 arXiv，当前版本无空间相位修正
- **论文文件**: `paper/main-paper.tex` + `paper/第03章-ORF计算.md` 等

---

## 被跳过的待办

| 待办 | 优先级 | 跳过原因 |
|------|--------|----------|
| LLM Gatherer 浏览器自动化待登录验证 | P1 | 无 GUI 环境，Google OAuth 登录无法完成 |

---

## 确认

```
---
## 任务澄清完成
- 状态：已完成
- 置信度：0.90
- next_brain: 进入 1-loop/02 目标澄清
```
