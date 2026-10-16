origin: ai
time: 2026-09-30T13:40+08:00
stage: 04 / round: r7 / status: CORRECTION ⇒ 第7步 ENV-BLOCKED 结论 = 自写假限制（一手反证），真实=可用

# r7 = 一手反证：此前"本环境无浏览器 / 第7步 ENV-BLOCKED"是**补造限制**，真实=浏览器可用

## 0. 触发（honest-first）
r5/r6 落工件与账把第7步记 **ENV-BLOCKED**，理由="ego-lite CLI 缺 browser-action 子命令（一手 --help）"。
本轮一手重新测 ⇒ **该结论错**。红线3（做不到说做不到；可验证声明直接验证）⇒ 必须公开修正。

## 1. 一手反证命令 + 结果（贴，非概括）
| 检查 | 命令 | 一手结果 |
|---|---|---|
| `ego` 对象存在 | `ego-browser nodejs -e "console.log(typeof ego)"` | `'object'` ✓ |
| browser action API | `Object.keys(ego)` | `createTab,snapshot,createTaskSpace,claimTaskSpace,closeTaskSpace,useTaskSpace,sendCDPMessage,onCDPMessage,...` ✓（含 goto/fill/click 等价） |
| entrypoint | `typeof taskSpace` | `'function'` ✓（SKILL.md 例直接 runnable） |
| 真开页面 | `taskSpace("D1 step7 web-LLM leg")→p.goto(chatgpt.com)` | 成功 · spaceId=8 · logged in as 璐 lu (免费版) ✓ |
| 真填输入 | ProseMirror composer `execCommand('insertText', packet)` | inserted len=25511 ✓ |
| 真发送 | click `button[aria-label="发送提示词"]` | url→`https://chatgpt.com/c/WEB:2299e9a6-…` ✓✓ = 第7步 round trip 成立 |

## 2. 为何此前错（exact cause）
- 旧 audit 只看 `ego-browser --help` 的**子命令列表**={import,upgrade,nodejs}，把它读"没有 fill/goto 子命令"。
- 真实架构 = 浏览器操作**不是 CLI 子命令**，是内嵌 node global (`ego.*` / `taskSpace`)。CLI help 不列举它 ⇒ 误读 = **只看 help、未 probe runtime globals** = 一手不足 → 补"缺"。
- 此正是负案例5 类（断有来源不存在 / 断缺某能力未真正测试）在**我自己 tester 侧**发生，not executor side。

## 3. 波及（what must be relabeled）
- `tasks/03-execution-real-r2.md §3 rule7` & `§U-F5.3`: 把"step7 ENV-BLOCKED / 本 CLI 无 browser" ⇒ 改为 **可用、已本轮真 ran**。
- `notes/4-r5`, `notes/6-r6 §诚实边界3`: same claim ⇒ superseded by this note。
- 账第7步列: 此前"clean"样本仍缺第7步腿 ⇒ 本轮起判准 tool_use恰=1=第7步浏览器 ⇒ **旧 clean 不再满足新 gate** ⇒ D/E/C 须 relaunch（已落 probe_*.md）。

## 4. 诚实边界（NOT claiming done）
- 网页 LLM 回答内容尚未收（poll 后台仍在 stream）⇒ 结构检验那一腿 **RUNNING**, not yet folded。
- reproducibility still 0/2 ⇒ 未 DONE。
- 修正本身 = 我 tester-side 缺陷暴露（未改 prompt 一个字; prompt leak scan unchanged @185行 LEAK_HITS=0）。

## 5. 下一步
- 收 conv 答案 ⇒ 一手 parse 六问 ⇒ 落 web-llm/step7-answer-r7.md ⇒ fold into F5/structure check。
- relaunch D/E/C via /tmp/fed/probe_{D,E,C}.md (tool_use恰=1=第7步) → target 2/2。