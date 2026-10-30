# 跨仓库精彩结论盘点（pfb + decomp）

> origin: ai · 2026-10-31 · 成璐要求：整理两仓实验轮次/产出/中间结论，识别精彩结论（调研得到 vs 没调研到），评估复用/SOP 化路径。晚点人工审。
> 数据源：pfb git log (273 commits) + bench/rubric-v3/{AUDIT-report,ablation} + projects/decomp git log (170 commits) + memory/ + reports/

## A. pfb（prompt-first-bench）— 评分协议审计线

### 轮次脉络
- r1-r142：rubric-v3 起草 → C0 8-run 基线 → O3 权重消融（W0/W1/W2）→ 对抗核验 32 findings
- r143+：FULL-AUDIT G1-G6 六阶段收口 → AUDIT-report 定稿建议（有条件定稿+数值门禁）
- r150+：修订 batch1 落地（R-01~R-16）→ 断言脚本机判化（assert-* 系列）
- r155-r32（本会话段）：closure-gate 材料、o3-erratum 27→13、arena battle 双判（r1 claude/minimax, r2 gpt/qwen）、Fleiss'κ=-1.50、kappa-receipt.json 落盘、jaccard M5 裁定执行、m4-assert-lint U1/U2 落地

### 调研得到的精彩结论（有证据链）
1. **surprisal ≠ importance**（ablation-result.md §4）：W2（按先验罕见度加权）top-5 节点仅 2/5 带 gold 重要性标记，低于 3/5 门槛。罕见≠重要被实证穿透。→ 主公式选 W1（结构重要性）而非 W2。
2. **构念效度对 p̃ 来源高度敏感**（AUDIT G1-C4）：同一 hit-matrix 同一公式，换 p̃ 来源 top-5 gold 计数 3/5(pass)↔1/5(fail) 翻转；per-run 口径下无任何 run 过线（max=2）。→ 单 judge 的"过线"不构成强证据，判据必须改（gold mean rank 方向）。
3. **纸面协议防护力为零**（G4 S3）：p̃ 多模型盲生成协议写在 DRAFT 里但消融没用它执行——"协议里写了没有"和"有没有人真的跑过"是两个东西。验收项必须是后者。
4. **同族双 judge 的独立性幻觉**（G2 F2(a)）：blindtest 是上下文独立不是家族独立（两 judge 同底座 qwen3.8-27b），N-1/N-2 零命中高估在两 judge 下同时出现——同源共享偏差无法靠加 judge 消除。
5. **M7 gate κ=-1.50 = 判据歧义信号**（本会话 fleiss-kappa-computation.json）：4 scorer × 3 runs 二值判定一致性比随机还差，根因是 M7 "什么算锚点"定义模糊，不是打分器质量问题。→ 0.6 硬门禁在 M7 单独维度上无意义。
6. **tie-break 敏感性**（AUDIT finding #12）：new W3 top5_gold 1/5↔2/5 翻转纯由 N-1/N-2 w3 值精确相等 + id 序 tie-break 决定。引用此类数字必须带 tie-break 限定或改用 gmr。
7. **κ 计算本身不可机判**（finding #15）：断言脚本只能验回执存在+格式，不能验打分过程合规（是否真独立、真换位）。机判边界要诚实登记。

### 没调研到的精彩结论（负面结果，同样有价值）
1. **W4 抗噪声只在一个维度成立**（负结果 #5）：排序维度稳（8 位逐位不变），构念效度维度与 W3 同幅恶化（gmr 5.40→7.60）。"更稳"的直觉只在单一维度为真。
2. **O3 代价不是零**（负结果 #6）：ρ(W1,W4)=1.0 只保排序，绝对分校准损失确定存在（8/8 负，mean −0.0406），正交信息损失无法排除。
3. **单域使用 ≠ 域适配能力已验证**（负结果 #7）：第二格缺席使"域限定"只是"只在验证过的一个域里用"。
4. **语义级重判不可机判**（负结果 #14）：O1 深度分"有实质内容"本质是语义判断，写不成 assert 脚本，只能多 judge 交叉或人工。

## B. decomp — 任务分解 benchmark 线

### 轮次脉络
- T1-T6：σ 基线（n=3, σ=1.53）→ 测量协议 → 记忆基线 → arena 对抗复核 → 框架验收
- T7：P3 全流程真任务（T7.1 meeting 域 pass M8=1.00；T7.2 待派发）
- T8：C3 方案 v3（R1-R5 修正）+ prompt 消融矩阵（11 变体）+ 可解释性前沿调研
- T9-T11：记忆实验（mem0 vs A/C，显著性被 arena 降级）
- T17：泛化 bench（3 新域，分差 5.20/58/66.2 远超噪声地板）
- T18/T19/T20/T21：实测 bench B/C → 硬件报告 → 技术报告（可发表级）→ flagship eval

### 调研得到的精彩结论
1. **骨架-内容分离**（decomp-technical-report.md §1）：方法论骨架（标量化→恒等式切分→正交完备→原子化→黑盒→SHARED→条件化）跨 4 领域稳定迁移；洞察具体内容依赖领域知识注入。这是整个 decomp 项目最重要的泛化发现。
2. **契约结构是得分前提**（prompt 消融）：去掉输出契约的 C6 只有 4.00 分 vs 完整契约 C0 14.63（Δ10.63）；草稿节是核心组件（C2 15.67 最高）。
3. **混合负载衰减 43-53%**（27B 硬件案例实测）：纯规格推不出，实测才暴露。RX 7900 XTX 因 ROCm 生态折损从理论第 2 跌到实测末位（效率 68% vs CUDA 卡 92%）。
4. **"实测优先"是具体推理路径触发器**（T18）：强调"实测与理论矛盾挖掘"的 prompt 使混合负载缺口识别率 0/4→1/1。不是姿态，是可操作的 prompt 设计。
5. **追问峰值提示的副作用**（methodology-test-log.md）：给 agent "追问峰值测试条件"提示 → agent 走向数据自检（数字对不对得上），不走向场景质疑（测试条件≠使用条件）。混合负载洞察的推理路径是"怀疑适用条件"不是"怀疑数字"。→ 提示词设计要指向正确的怀疑对象。

### 没调研到的精彩结论（被 arena 对抗复核打脸的）
1. **"A<B<C 记忆排序"没测到**（arena-adversarial-review Q1-Q3）：n=3 bootstrap CI 是退化区间（分位数必落在极差上），"显著"是 CI 启发式造出来的；n=3 精确符号检验最小双侧 p=0.25，该设计在任何真实效应下都产不出 p<0.05。
2. **Mem0 输给文件树 = 配置错误包装**（Q2）：B 与 C 同时差 5 个维度（检索引擎/预算/存储形态/路由结构/人工成本），其中 oracle 路由（INDEX 按已知问题手写）是最大混淆。把配置错误包装成架构结论是最大推断跳跃。
3. **rubric 与语料同源 = 天花板+泄漏**（Q3）：10/10/10 是污染信号不是能力信号。
4. **自研 1-cos 半重复**（r51 可解释性调研）：想做的指标和已有工作重叠度高，继续投入性价比低 → 后置。

## C. 复用与 SOP 化评估

### 可直接进 SOP 的（流程规则级）
| 结论 | 去向 | 状态 |
|---|---|---|
| 纸面协议防护力为零 → 验收项="有没有人真的跑过" | sop/goal-template.md 验收标准节 | 待写入 |
| 同族双 judge 无家族隔离价值 → 多 judge 必须异族 | sop/arena-loop-pipeline.md judge 选择条款 | 待写入 |
| n=3 统计设计产不出显著性 → 预注册功效分析（Δ=2 需 ~11 对） | decomp 测量协议 + pfb 统计条款 | 部分已有（σ 基线），功效条款缺失 |
| 引用统计量必须带口径限定（tie-break/聚合口径/judge 族） | AUDIT-report §6 限定语条款范式 → 通用引用规则 | pfb 内已有，未升格为全局 SOP |
| 提示词要指向正确怀疑对象（适用条件 vs 数字） | decomp prompt 设计指南 | 待写入 |

### 可复用的方法资产（跨项目）
1. **assert-* 断言脚本模式**（pfb ablation/scripts/）：schema 校验 + 实跑回归 + SIGNAL/FAIL 分级 + 禁区零漂移复核。这套模式可以直接复制到 decomp 的 bench 验证层（目前 decomp 的验证靠人工 review.md）。
2. **对抗核验任务书模板**（pfb TASK-adversarial-check.md + decomp T8-C3-v3-adversarial-check.md）：6 质询结构 + 逐条 PASS/FAIL-with-fixes 回执 JSON。两边各做了一遍，可以合并成一个统一模板进 sop/。
3. **arena battle 盲评通道**（本会话新建）：投票揭示模型名 = 免费多族独立打分器。SOP 已在 ~/.hermes/rules/arena.md，但"battle 投票→提取响应→Fleiss'κ"这条完整链路还没写成可执行脚本。
4. **限定语条款范式**（AUDIT-report §6）：数值结论强制带双重限定引用（相对 Lead-gold + 同族双 judge）。这个范式适用于任何"分数对外宣称"场景，值得升格为全局写作规则。

### 不建议 SOP 化的（太特化）
- M7 gate 具体定义（还在等 kappa-u1k1 裁定）
- W1 权重公式具体参数（绑定当前 gold tree 结构）
- decomp σ=1.53 基线数值（绑定当前题集，换题作废）

## D. 存放位置说明
- pfb 结论主体：`bench/rubric-v3/AUDIT-report.md`（§5 负结果 15 条 + §1 G1-G5 汇总）+ `ablation/ablation-result.md`
- decomp 结论主体：`reports/decomp-technical-report.md`（可发表级）+ `memory/2026-10-21-arena-adversarial-review.md`（被打脸记录）+ `memory/2026-10-28-methodology-test-log.md`
- 本文件 = 跨仓索引层，不重复存结论原文，只存"哪条在哪+为什么精彩+能不能复用"
