# RALPH Prompt-First Loop

<!-- ralph-prompt-state
stage: 01
revision: r1
status: running
current_artifact: loop-artifacts/prompt-first/01-factor-decomposition.md
review_status: idle
review_stage: 
review_artifact_sha256: 
review_attempt: 0
review_return_code: 
-->

## 原始任务（请勿改写）

STAT COMMANDn/private/tmp/ralph-gpu-herdr-review-v52.zgoQ0f 为中国大陆个人开发者完成一份可执行的本地 AI GPU 性价比调研：按 1 万、2 万、3 万元预算提出硬件方案；核对显存、性能、功耗、当前价格与来源；使用网页 AI Playwright 做交叉询问；所有关键主张经过多来源交叉验证；完成全部阶段并记录每阶段 Markdown、Reviewer 回执和事件日志。

## 机械说明

这个文件只保存阶段游标，不评价内容质量。阶段内容全部写在当前 Markdown 工件中。
主工件停止写入后，Stop Hook 自动启动独立 Reviewer。Reviewer 读取 loop/prompt-first 中的规则和当前工件，输出问题、证据缺口与 pass/revise 路由。
只有当前工件对应的 Reviewer 明确 pass，且之后写入 `<!-- ralph: done -->`，才进入下一阶段；revise、缺失、过期或无效回执都留在当前阶段。
不要手动编辑本文件的阶段游标或原始任务；它由 Stop Hook 机械维护。普通项目工件可自由读取和写入。
