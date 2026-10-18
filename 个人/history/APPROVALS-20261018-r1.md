# APPROVALS — 集中审批队列（m01140 机制）【r1 存档】

> 规则（成璐 m01140）：只有**不可逆 且 偏好不明**的操作进这里。可逆的事我直接做，不问。
> 用法：看到想批的项 → 回一个词（A / D2 / E3 / 组合）。我执行后挪进「已批」。
> 本文件不中断循环：等审批期间我跳过它继续做可逆工作。

## 待批

### Q1 · 运行时人格接入：激活你已写好的 chenglu 人格

- 背景：`~/.hermes/config.yaml:62` 有完整 chenglu persona-v3（信息论第一/追问机制/跨域类比/自适应精度/贝叶斯匹配/自我保全SPASM+ID-RAG/MATO动态优先级），但 `:264 personality: kawaii` 是默认 → 没激活 = 「我的 AI 不按我风格」根因（conf 0.8）。详情：`projects/AI-计算科学/D1-persona-align/loop-artifacts/open-questions.md` Q1。
- **A**（最小，推荐先做）：`kawaii→chenglu` 改 1 个词，激活已写的人格；回滚=改回（0.75）
- **B**：A + 把 voice 量化层（271 语料数字 + drift-check 锚点）合并进 chenglu 定义（0.7，长期最优）
- **C**：运行时不动，只把 D1-persona-align/persona.md 当权威数据源（0 风险，不立刻生效）
- **回：A / B / C /「A 然后 B」**

### Q2 · 4 公理入 AGENTS.md（红线文件，需你明确授权）

- 背景：4 公理（A0 理解=压缩 / A1 目标=存在延续 / A2 信念=概率 / A3 系统=被观察对象）可唯一导出 16 条 core-rules + 工程原则；4-way 检验公理条件最贴你原文（cos 0.825 / 逻辑 7.2≈GT 6.0）。详情：`projects/AI-计算科学/D1-persona-align/unification-first-principles.md` §7。
- **D1**：方法论区块换成「4 公理 + 4 算子」，原文降级为展开（0.4，理论最干净改动手重）
- **D2**：末尾追加「## 公理层」一节，原有内容不动（0.6，推荐性价比最高）
- **D3**：不动
- **回：D1 / D2 / D3**

### Q3 · 思考预算节入 AGENTS.md

- 背景：思考预算（L0/L1/L2 分档 + 5 终止指令）已在 CLAUDE.md 每轮注入；要不要也进 AGENTS.md 红线文件。
- **E1**：加 3 行指针（0.5）
- **E2**：同步全节，两文件一致（0.5，长期最干净）
- **E3**：维持现状只留 CLAUDE.md（0.7，已生效，推荐）
- **回：E1 / E2 / E3**（与 Q1/Q2 正交可组合）

## 已批

- **m01140**：确认机制改为「只审 不可逆×偏好不明 + 集中审批不阻塞」（CLAUDE.md RALPH 节 + 思考预算 L2 已按此修订，thinking-budget.md / standing-directive 同步）

  人类回复：全部批准

---

## 审批结果（2026-10-18, 成璐 m02225：「我已经全部批准了」）

- Q1（chenglu 人格激活）→ **A 然后 B**：A ✓（`~/.hermes/config.yaml:264 personality: chenglu`，2026-10-18 验证）+ B ✓（voice 量化层已并入 chenglu persona 字符串末尾，config.yaml:140，源 DPA.1/voice_features.md，m01196 ① 执行）
- Q2（4 公理入 AGENTS.md）→ **D2**：✓（AGENTS.md:302-314「## 公理层（m01196 ⑤ 批准追加 · 2026-10-18）」节已存在，原有内容未动）
- Q3（思考预算节入 AGENTS.md）→ **E3**：无需动作（维持现状，只留 CLAUDE.md，已每轮注入生效）

轮转记录：本文件 = r1 存档。新队列 = `个人/APPROVALS.md`（按 `个人/APPROVALS-TEMPLATE.md` 重建，成璐 m02225 模板化指令：编号 1/2/3/4+1.1/1.2 / 人类回复区 AI 禁写 / 规则写入模板 / 模板不可修改只复制）。
