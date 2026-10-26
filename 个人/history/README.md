# 个人/history
# origin: ai

## 本文件夹主要功能

审批队列历史存档（AGENTS.md「RALPH — 人类确认机制（m01140 修订）」落点）：人工批复后的审批队列按 `APPROVALS-<YYYYMMDD>-r<轮次>.md` 轮转存档于此，当前队列从 `../APPROVALS-TEMPLATE.md` 重建。

现存：

- `APPROVALS-20261018-r1.md`
- `APPROVALS-20261021-r2.md`

## 接口

- 输入：已批复的 `../APPROVALS.md` 快照
- 输出：只读存档
- 对外函数签名：无（纯文档层）

## 调用说明

- 只追加存档，不改写、不删除任何既有存档
- 命名固定为 `APPROVALS-<YYYYMMDD>-r<轮次>.md`，轮次 r 递增
