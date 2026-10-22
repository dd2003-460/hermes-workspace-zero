# P1 arena 通道修复记录（r1 · 2026-10-22）

> origin: ai · 成璐指令"收益最大=decomp，先修 P1"

## 现状

- **4 次 arena subagent 全部失败**（decomp organizer 空等 20min+ / memory-hooks 10min 未落盘 / C0 run2/3 page.fill 故障 / 评分 subagent 无 closing）
- **根因**：我把 arena 当成"远程 LLM API"（把 prompt 贴过去，等回复），**这是错的**
- **Arena 实际能力**：能直接连 GitHub 仓库（clone/读/改/push），像 Claude Code 一样操作代码

## 正确流程（修正）

1. 我把任务写进仓库（tasks/ 目录 + commit + push）
2. 让 arena 连仓库（用 GitHub connector）
3. Arena 自己读任务、执行、commit、push
4. 我验收 + 推进

## 修复进展（r1）

### 1. 页面加载 ✅
- `ego-browser nodejs` + `p1.goto('https://arena.ai/agent')` → 页面正常加载
- 快照 8540 字符，包含完整 DOM

### 2. 输入框 fill ✅
- `document.querySelector('textarea')` 找到输入框（1 个）
- `ta.value = '...'` + `dispatchEvent(new Event('input'))` → fill 成功
- snapshot 验证 `ta.value` 有内容 → F0-2 通过

### 3. 发送按钮定位 ✅
- **正确选择器**：`button[aria-label="Send message"]`（snapshot ref=50）
- 之前的 subagent 用 `page.fill` 失败（"The page.fill didn't work"）→ 应该用 `evaluate` + `ta.value`
- 之前的 subagent 用 `page.click('@104')` 成功（round-02-submit.mjs）→ 但 ref 号会变，应该用 aria-label 更稳定

### 4. 发送机制 ❌（待深入）
- **Enter 键盘事件**：`dispatchEvent(new KeyboardEvent('keydown', {key:'Enter'}))` → 不触发发送
- **点击 Send message 按钮**：`btn.click()` → 不触发发送（20s 后无回复，页面仍显示历史会话）
- **可能原因**：
  1. arena.ai/agent 的发送需要特定事件序列（不是简单的 click/Enter）
  2. 可能需要先聚焦输入框 → 输入 → 再发送
  3. 可能需要调用 arena 的内部 API（不是 DOM 操作）
  4. 可能需要等待页面完全加载（不是 3-4s）

## 下一步

- [ ] 深入调研 arena 发送机制（看源码/API/网络请求）
- [ ] 或者用 Playwright 的 `page.keyboard.press('Enter')`（不是 DOM 事件）
- [ ] 或者用 `page.click('@N')`（snapshot ref，动态查找）
- [ ] 修好后重跑 decomp T4 剩余 19 份 run

## 降级方案（P1 未修完前）

- **decomp T4**：降级自答（conf-0.2），质量低但能推进
- **媒体 Step E**：无阻塞，不依赖 arena，可执行

## 文件

- 测试脚本：`loop-artifacts/ego-browser/p1-fix-test/test-arena.mjs`（已废弃，用内联脚本）
- 之前的成功脚本：`loop-artifacts/tmp-mh-research/ego/round-02-submit.mjs`（用 `page.click('@104')`）
