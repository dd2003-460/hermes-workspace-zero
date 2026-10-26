# 个人
# origin: ai

## 本文件夹主要功能

个人层（identity / 决策审批 / 异步队列）：`APPROVALS.md`（不可逆×偏好不明 的集中审批队列，AGENTS.md m01140 机制落点）、`APPROVALS-TEMPLATE.md`（审批队列模板，存档后从模板重建）、`ASYNC.md`（异步事项队列）、`identity/`（数字分身动机、soul 默认决策画像）、`history/`（审批队列历史存档）、`persona-claude-longterm.md`（长期 persona）。

## 接口

- 输入：各会话的不可逆操作待审批项、identity 修订
- 输出：审批队列（含「人类回复：」留白）、存档文件
- 对外函数签名：无（纯文档层）

## 调用说明

- 写入审批项：按 `APPROVALS-TEMPLATE.md` 格式追加条目，不阻塞后续可逆工作
- 轮转：人工批复后存档至 `history/APPROVALS-<YYYYMMDD>-r<轮次>.md`，再从模板重建
- 红线：AGENTS.md 本体禁改（除非用户明确要求），拟修改走本目录审批队列
