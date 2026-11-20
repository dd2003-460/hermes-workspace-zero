# T-OS-2 K复杂度=结构稳定区域内的拟合 · 滚雪球碰撞调研任务书

> 仓库绑定：dd2003-460/hermes-workspace-zero @ main
> 派发：2026-11-20
> 交付物：`projects/AI-计算科学/D1-persona-align/research/2026-11-20-kcomplexity-structural-stability-collision.md`
> 回执：search-log-os2.json（检索通道/查询/命中/排除 + 雪球轨迹）

## 背景（给 agent 的上下文）

D 的推导（idea-pool #5，凭直觉未经文献验证）：
1. 任何描述 = 码表（检索）+ 规则（计算）两部分；最优描述 = 两部分总成本最小（MDL 的直觉版）
2. 但"结构化"是暂时的：长期稳定的系统可能只是**参数稳定**（参数不变时稳定），不是**结构稳定**（微扰后拓扑不变）
3. 参数漂移超过 bifurcation 临界值 → 混沌 → 描述长度突然变大（结构消失）
4. 所以 **K 复杂度的有效性是物理的（依赖动力系统结构稳定性），不是数学的**；"天才的压缩"（K(idea|context) 小）也依赖 context 在结构稳定区域内
5. 附带 claim：K 复杂度"不可计算"（哥德尔）的软肋被物理一致性先验绕过——演化只留下逻辑一致的子系统，所以 P(一致|演化存活)≈1

D 自己的判断：这像**次生推论**（聪明人大概率做过），核心 query 词感觉得有"存档/landscape/phase transition"这类。任务 = 滚雪球找到一手来源，判决撞车程度。

## 检索方法（强制：滚雪球，不是一次性搜索）

**雪球协议**：种子 query → 找最近邻论文 → 读其 related work / references → 顺藤摸到下一层 → 重复 ≥3 层。每层记录：query / 命中论文 / 为什么选它 / 下一层往哪走。雪球轨迹写进回执 search-log-os2.json 的 `snowball_trace[]`。

## 核心问题（3 个正交子问）

**Q1（结构稳定 vs 参数稳定）**：动力系统文献里，"长期观测稳定 ≠ 结构稳定"这个区分有没有正式表述？
- 种子 query 建议：structural stability vs orbital stability / Lyapunov stability vs topological stability / robustness to parameter perturbation / bifurcation / "structurally stable" dynamical systems
- 要回答：① 两个概念的标准定义和出处（哪本教材/哪篇论文）② 有没有"长期稳定但结构不稳定"的经典反例（如 logistic map 在 r 接近 3.57 时长期看似稳定但微扰后进入混沌）③ 这个区分在**信息论/编码**文献里有没有被引用过（不只是动力系统圈内部）

**Q2（K复杂度/压缩率在混沌与临界点附近的行为）**：有没有人研究过"描述长度/压缩率在 bifurcation 点或混沌边缘的行为"？
- 种子 query 建议：algorithmic complexity near bifurcation / compressibility phase transition / "computational irreducibility" chaos / Kolmogorov complexity chaotic systems / "edge of chaos" complexity / algorithmic information dynamics
- 要回答：① 有没有实测/理论结果支持"混沌化时描述长度突变"（如：临界点附近的序列压缩率变化、critical phenomena + algorithmic information）② 最近邻工作的精确 claim（逐条读原文 abstract + 主定理）③ 有没有人把"K 复杂度失效域"和动力系统相变联系起来

**Q3（撞车判决：核心 claim 有没有先例）**：
- 核心 claim A："K 复杂度的有效性是物理的（依赖结构稳定性），不是数学的"——有没有人说过等价的话？
- 核心 claim B："描述 = 检索 + 计算两极，最优描述 = 两极总成本最小"——电路复杂度（lookup table vs circuit）之外，有没有人用"检索-计算"这对词统一过？
- 核心 claim C："演化/物理一致性先验绕过哥德尔不可判定性"——有没有人论证过"物理系统的一致性来自选择/演化而非逻辑自证"？（候选方向：物理 Church-Turing 论题、量子计算与可计算性、"nature does not compute" 类文献）
- 判决标准：找到一篇文献其核心 claim 与 A/B/C 之一等价 → 该子 claim 撞车，记录对象；只有部分重叠 → 收窄到差异点，给 conf(0-1)；无先例 → 标"未找到"，列出穷尽的 query 清单

## 检索通道（强制，禁纯记忆）

- arXiv API（full-query + sortBy=relevance）
- 直访 arXiv 原文（读 abstract + related work + 主定理节）
- 搜索引擎（ego-browser 可达的）
- 每条来源标：URL + 读到的深度（abstract/全文/related-work）+ 与 Q1/Q2/Q3 的命中关系

## 验收标准

- AC1：雪球 ≥3 层（snowball_trace 长度 ≥3），每层有 query + 命中 + 走向理由
- AC2：≥12 个来源，其中 ≥6 读原文（不止 abstract）
- AC3：Q1/Q2/Q3 各有明确判决（撞车/部分重叠/无先例），撞车的给文献指针，部分重叠的给收窄后的 claim + conf
- AC4：最终一段"撞车地图"：D 的 5 步推导链，每步标"已知(出处)/部分重叠(出处+差异)/未见先例"
- AC5：交付文件不存在 = 任务未完成；回执 JSON 必须含 repo URL + branch + commit_sha

## 长度与格式

- 报告 ≤80 行（核心判决 + 撞车地图 + 关键文献表），过程论证放雪球轨迹回执
- 中文回答；每条结论标 conf(0-1)；不确定的标"未验证"
