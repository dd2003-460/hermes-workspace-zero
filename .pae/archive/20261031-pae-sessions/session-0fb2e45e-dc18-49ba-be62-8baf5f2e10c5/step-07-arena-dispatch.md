# Step 07: arena 派发执行（T1 + T2）

## 目标
用 ego-browser 打开 arena.ai/agent 新会话 @market-alpha，派发 T1（GPU）和 T2（变压器）任务书，让 arena 走 1-loop 执行。

> ⚠️ 外部动作：向 arena 派活，需用户确认。

## 涉及文件
- `market-alpha/loop-artifacts/arena-session.md`（会话 URL + 派发记录）

## 做法
1. ego-browser 打开 `https://arena.ai/agent`，新建会话，选择/连接 `dd2003-460/market-alpha` 仓库
2. 验证 arena 能读到仓库：让其 `cat tasks/T1-gpu-price-model.md` 成功（断点 C 验证）
3. 发送 T1 指令：「执行 tasks/T1-gpu-price-model.md，先读 sop/arena-loop-pipeline.md 和 loop/prompt-first/ 走完整 1-loop」
4. T1 完成（或单会话停摆超 3min）后：按 §2.1 判定——单会话停摆→重开会话重发；T1 产出 push 后再发 T2（或同会话继续）
5. 发送 T2 指令（同格式）
6. 记录会话 URL、派发时间、任务状态到 arena-session.md
7. **降级条件**（§2.1 硬顺序）：① 单会话停摆→重开会话重发任务卡 ② 重开仍失败（通道级）→降级本地执行完整 loop ③ 本地也受阻→APPROVALS 跳过。禁止对单会话停摆直接判降级。

## 验收标准
- [ ] arena 新会话已创建并连接 market-alpha 仓库
- [ ] T1、T2 指令已发送，arena 首条回复引用了 loop 阶段路径（断点 C 过）
- [ ] arena-session.md 落盘含 URL 和状态
- [ ] 派发后 arena 开始产出 loop-artifacts/stages/01/（观察首轮产出确认流程启动）
