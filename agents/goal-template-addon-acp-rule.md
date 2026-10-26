# goal-template.md 补充段：硬规则自动加载（✅ 已合并 2026-10-26）

> 已合并进 `agents/goal-template.md` §3 质量原则。本文件保留设计说明供参考。

---

## 硬规则自动加载（acp_rule）

建 goal 后的第一个动作：读 `agents/acp-rules.json`，对 `rules` 数组中每条文本
**在一条消息内并行调用 acp_rule 工具**录入（DSH 支持并行工具调用，一轮完成，
无需一个一个来）。若工具不存在（未启用），跳过并在首条回复中说明。

规则维护纪律：改规则只改 `agents/acp-rules.json` 一个地方，然后
`acp_rule {clear:true}` 后按文件重录。禁止在对话里临时发明硬规则——
要补规则就补进 JSON，让下一个会话也能加载到。

完整规则主体（AGENTS.md / 各类 SOP）按需 read，不默认全量进上下文。

---

## 附：为什么这样设计（给改模板的会话参考）

- acp_rule 每轮重新注入系统提示，是唯一抗压缩的硬规则通道（compress/acp_rule
  两个工具本身永不被压缩）
- 配置只能开开关（enabled/maxRules/maxRuleChars），不能预置规则内容——
  代码实锤，所以"默认加载"必须靠模板指令行为实现
- 指针摘要规则已写入 acp-rules.json 第 3 条：压缩前先落盘，摘要只写
  "已归档至 X；要点：Y" 一行，禁止多层蒸馏
