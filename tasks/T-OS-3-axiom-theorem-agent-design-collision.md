# T-OS-3 公理-定理式 agent 设计 · 滚雪球碰撞调研任务书

> 仓库绑定：dd2003-460/hermes-workspace-zero @ main
> 派发：2026-11-20
> 交付物：`projects/AI-计算科学/D1-persona-align/research/2026-11-20-axiom-theorem-agent-design-collision.md`
> 回执：search-log-os3.json（检索通道/查询/命中/排除 + 雪球轨迹 snowball_trace[]）

## 背景（给 agent 的上下文）

D 有一套"公轴体系"（persona-axioms.md，v2.2），核心结构：
- **5 条公轴**（P1 理解=压缩 / P2 目标=存在延续 / P3 断言带置信度 / P4 盲点不可自观察 / P5 输出是观察）
- **16 条可执行规则**（R1-R16），每条标来源公轴 + 一句话推导
- **重推测试**：把 8 条 hold 规则藏起来，让模型只从 5 条公轴重推；推得回来 = confirmed，推不回来 = 升格公轴或修订公轴表述。实测 3 次：1 条 3/3 推回，2 条 2/3，5 条 0/3。
- **反向删除实验**：逐条删公轴重推全部 16 条，错误数变多 → 该公轴必要。实测 5 条全必要，无冗余。
- **参数表**：偶然内容（阈值/周期/站点数）不当公理，当参数放配置。
- 应用：这套公轴+规则作为 agent 的 system prompt 规则层，替代长 SOP。

D 的判断：这套东西**形式上就是公理-定理体系**（公轴=公理，规则=定理，重推测试=定理可推回性检验，删除实验=公理独立性检验）。"用最少公理生成最多可执行规则"这个方向大概率有人做过。任务 = 滚雪球找到一手来源，判决撞车程度。

## 检索方法（强制：滚雪球，不是一次性搜索）

**雪球协议**：种子 query → 找最近邻论文/系统 → 读其 related work / references → 顺藤摸到下一层 → 重复。**最多 10 层**，停止条件：连续 2 层无新信息就停，不硬凑层数。每层只追 1 条主线，分叉记录到 snowball_trace 的 `branches[]` 但不追。每层记录：query / 命中 / 为什么选它 / 下一层往哪走。

## 核心问题（3 个正交子问）

**Q1（公理-定理式 agent 设计有没有先例）**：有没有文献/系统把 agent 行为规则形式化为"少量公理 + 推导出的定理/规则"，且用**推导关系**（而非枚举）组织规则？
- 种子 query 建议：axiomatic agent design / principle-based agent architecture / "axioms" "theorems" LLM agent rules / constitutional AI axioms / "derivable" rules prompt / minimal axiom set agent behavior / formal axioms for AI alignment
- 要回答：① 有没有直接先例（公理→规则推导链是核心设计）② 最接近的先例是哪个（如 Constitutional AI 的 principles、Anthropic 的 RSP、任何 "axiomatized" agent 规范）③ 它们的公理条数和推导机制是什么，和"5 公轴→16 规则"比谁更紧凑
- 注意区分：纯哲学规范（不落地为 prompt 规则）算弱先例，落地为可执行 prompt 规则层的才算强先例

**Q2（重推测试/删除实验有没有正式名称和文献）**：把规则藏起来让模型从公理重推（可推回性检验）+ 逐条删公轴看错误数变化（必要性检验）这两个实验，在逻辑学/组合数学/机器学习里有没有正式名称和先例？
- 种子 query 建议：axiom independence test / minimal generating set / "deletion experiment" axioms / "re-derivation" test rules / axiom redundancy / minimal axiomatization / "independent axiom" / compression-based rule discovery / MDL rule selection
- 要回答：① 公理独立性/最小公理集在数理逻辑里的标准定义和检验方法 ② 机器学习里有没有"规则可从更短描述推出才保留"的正式框架（MDL/OCcam 在规则学习里的应用）③ LLM 场景下"让模型重推规则"这个具体实验设计有没有人做过（这个可能是新的——逻辑学里的独立性检验是形式证明，不是让 LLM 生成）
- 关键判决：如果"LLM 重推规则"这个实验设计没人做过，那这是 D 体系的**方法学增量**，不是撞车

**Q3（最小规则集消融有没有先例）**：有没有人做过"给 agent 不同规模的规则集（空白/3条/16条），测行为差异"的消融实验？
- 种子 query 建议：rule ablation LLM agent / "prompt ablation" rules / minimal instruction set agent / "how many rules" agent alignment / instruction hierarchy ablation / system prompt ablation study / rule density agent behavior
- 要回答：① 有没有人量化过"规则条数 vs 行为质量"的关系（存在最优点？边际递减？）② 现有 agent 规则体系（Claude system prompt / GPTs instructions / 各种 framework 的 rules）有没有被消融过 ③ "规则可推导性"（规则间有推导关系 vs 平铺枚举）对 agent 行为的影响有没有被研究过
- 注意：prompt compression（把长 prompt 压短）是相邻但不相同的问题——它压的是措辞不是规则结构，区分清楚

## 交付格式

markdown 报告，≤50 行核心 + 附录：
```
# T-OS-3 碰撞调研
## 判决（先给）
撞车程度：{无先例 / 弱先例(形式相近机制不同) / 强先例(直接撞车)}，conf 0-1
D 体系的增量点：{列表，每条带 conf}
## Q1 先例
| 系统/论文 | 公理数 | 推导机制 | 落地形态 | 与 D 体系差异 | conf | 来源URL |
## Q2 方法学
{正式名称 + 文献 + LLM 场景是否有人做}
## Q3 消融
{规则条数消融先例 + 最接近的实验设计}
## 雪球轨迹
（见 search-log-os3.json）
```

## 约束
- 中文回答；每条结论标 conf(0-1)；给来源 URL；不确定的标"未验证"
- 撞车判决必须给一手来源（论文/系统文档），不接受二手转述
- 文件不存在 = 任务未完成，Lead 不验收
- 完成后回执必须含 repo URL + branch + commit_sha
