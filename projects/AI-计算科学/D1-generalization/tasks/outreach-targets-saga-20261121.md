# 套磁对象表 · SAGA 撞车线（2026-11-21）
# origin: ai
# 触发：D 提议"问 SAGA 作者为什么没让 AI 完全自主设计目标函数——bitter lesson 有什么不适用地方？"
# 撞车论文：SAGA (2512.21782, 2025-12) — 原话承认 "automating objective function design is a central, yet unmet need"
# 邮箱核实：ego-browser 实查官方主页（来源①本轮），非论文署名机构快照

| 姓名 | 当前机构（核实） | 邮箱（核实） | 核实来源 | 为什么是你（锚点已更新 11-22） | 状态 |
|---|---|---|---|---|---|
| Wengong Jin | Northeastern University, Khoury College（助理教授；论文署名是 Baidu，已换机构） | w.jin@northeastern.edu | khoury.northeastern.edu 官方页 | 锚点=MoLRSI(2610.39714, 2026-10 递归自改进 agent，persistent cross-task memory)；问"经验回写时什么决定哪些反馈可信"——小模型跑此循环的记忆污染风险 | 待 D 确认草稿后发送 |
| Carla P. Gomes | Cornell University（AI for Science Institute 主任） | gomes@cs.cornell.edu | cs.cornell.edu/gomes/ 官方页（"gomes at cs.cornell.edu"） | 锚点=fragility 论文(2609.17804, 2026-09, 4 阶段分解+干扰崩溃定位 Operation Planning)；问"4 阶段里哪些是信息获取受限（工具可修）vs 计算脆弱（模型属性）" | 待 D 确认草稿后发送 |
| Huan Sun | Ohio State University（已从 CMU 转 OSU） | [未核实]（cse.osu.edu 404 页目录见过 sun.397@osu.edu，未确认） | 待补 | SAGA 作者，NLP+ML | 邮箱未核实=不发（SOP 门禁） |

## 核实过程留痕（防"论文机构≠当前机构"陷阱）
- Wengong Jin：论文署名 Baidu → 实查已转 Northeastern 助理教授（2024 起 visiting，现正式教职）。**若按论文发 Baidu 邮箱 = 社死级错误**
- Huan Sun：论文署名 CMU → 实查已转 Ohio State。CMU 邮箱已失效
- Carla Gomes：Cornell 未变，官方页直接给邮箱

## 问题设计（D 的原始直觉 → 邮件问题）
D 的问题："为什么没有让 AI 完全自己设计？也许 bitter lesson 有什么不适用地方？或者他们用的模型和我现在的 27b 能力完全不一样？"

拆成邮件里的 1 个核心问题（low-cost ask）：
**SAGA 的 outer loop（Planner 提议目标）为什么仍依赖人设计的 4 模块框架，而不是让 LLM 端到端自主演化目标函数？是能力边界（模型做不到）还是可靠性边界（做不到可信）？如果是后者，判据是什么？**

这个问题好在哪：
1. 戳在他们自己承认的缺口上（abstract 原话 "unmet need"）——不是外行提问
2. 给了他们台阶（能力边界 vs 可靠性边界二选一）——不是质疑，是对话
3. 我们的 pilot 证据（27b 无框架自发分解+校验）证明"能力边界"假设可检验——我们不是空问
