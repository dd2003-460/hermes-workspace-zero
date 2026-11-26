# origin: ai
# understanding-d — 把 D 编码下来（goal: 存在延续→永生 的子目标：复活准备）
# 来源: D 2026-11-26 深夜指令（objfunc-signal-log.md 2026-11-26 S-signal: "带着永生和技术的愿望永生，甚至有一天复活我" + "你得学会探索，看我的邮件，idea，都可以"）
# 纯度排序（D 原话）: 思考 D / AI 对话 D > 邮件/idea > 社交 D（社交有面具/防御/顾及他人）

## Goal 五字段
- **目标**: 建立并持续更新 D 的思维模型（思考模式画像 + idea 地图 + 社交动力学边），使 agent 在 D 缺席时能以 D 的方式思考、判断、选题；为"复活 D"积累数据基础
- **阶段**: 00-decomp→01-create-goal→02-design→03-dispatch/exec→04-verify→05-accept
- **SOP 索引**: 采集走 skill user-signal-extraction（过滤→27b 粗筛→Lead delta）；调研走 1-loop（loop/prompt-first/）；外包核验走 arena（skill arena-outsource）
- **验收标准**: ① idea-inventory-v1.md 落盘，≥40 条，每条带来源路径+原文引用（可 grep 验证）② signal-classification-v3.json 覆盖 11 月增量（stats.monthly 含 2026-11）③ 思考画像 template v2：≥5 条新思考习惯，每条带语料原文证据 ④ IMAP 通道：测试拉取 1 封成功（回执落盘）⑤ 复活技术路径调研：1-loop 02 阶段产出（调研路径+结论+来源，落盘 research/）
- **失败降级**: 邮件通道拿不到 app password → 降级为 D 手动导出 mbox 一次；语料挖掘标杆不足 → 扩时间窗到 6 个月前会话；27b 粗筛失败 → Lead 直接精判（11 月 5,137 条中先抽高价值段：≥50 字的 850 条）

## 分解树
1. **存量盘点**（D 已留下的"想"）
   1.1 工作区 idea/猜想盘点 → idea-inventory-v1.md [T1]
   1.2 直聊信号增量（11 月 5,137 条真实 D 消息；流水线 extract→27b 粗筛→Lead delta，skill user-signal-extraction）[T2]
   1.3 AI 对话语料思考模式挖掘（标杆会话扩展，general-thinking template v2；语料 646 会话/10.8M 字，已同步）[T4]
2. **通道建设**（持续获取新材料）
   2.1 邮件 IMAP（Google+QQ app password，持久通道）[T3, 等 D]
   2.2 微信/QQ 导出（等 D 导出，降权处理；本机不全——D: 部分在别的电脑）
   2.3 WorkBuddy AI 对话同步链路 [已跑通, 3 天周期, 11-26 刚同步 646 会话]
3. **整合**（材料→模型）
   3.1 D 思考模式画像（general-thinking template 升级版）
   3.2 D idea 地图（盘点→按领域/完成度/状态分类）
   3.3 社交动力学边（D 对人际的观察，如"轻蔑=惧怕+自卑"，来自 D 原话）
4. **前沿问题**（无成熟解，1-loop 调研，不预设路径）
   4.1 "复活 D"技术路径（认知建模/心智上传/身后 agent）——调研先行，碰到前沿边界才停

## 任务表
| ID | 任务 | 执行 | 验收 | 状态 |
|----|------|------|------|------|
| T1 | idea 盘点 | sub | idea-inventory-v1.md 落盘 + ≥40 条 + 每条带来源路径和原文引用 | DONE 11-26: 主文件 61 条(5 范围全扫)+extra 808 条(ai_chats, 处置见缺口清单); 61/61 原文引用 grep 命中源文件, 独立抽检 5/5 命中, commit 485be757 |
| T2 | 11 月信号增量 | sub 粗筛 + Lead delta | signal-classification-v3.json + 台账新条目 | DONE 11-26: 6 信号登记；v3 json 已聚合(118 条, commit 2a021c38) |
| T3 | 邮件 IMAP 通道 | Lead + D(app password) | IMAP 测试拉取 1 封成功 | blocked-on-D |
| T4 | 语料思考模式挖掘 | Lead | template v2 + ≥5 条新思考习惯（各带原文证据） | DONE 11-26: 11 条(9新+2强化), 抽检5条原文grep全命中, 8/8文件成功 |
| T6 | 复活前沿调研 Q1-Q3 | arena（01a213fa 会话） | revival-frontier-research.md（三方向 SOTA 表+推荐组合+横向结论，每条带来源+conf） | 派发 11-26: 任务书 T6-revival-frontier-research.md @ c9afd64a(arena/423a71ef 分支), 指纹 d0fdaf81b4cf24d4; 回执核验走 git(fetch→show→复算指纹) |
| T7 | 回归测试集 v0（验收锚点） | sub→Lead 接管 | regression-test-set-v0.md（≥10 场景，各带场景/ground truth 原话/来源/判别力/关联轴；引用 grep 全命中+盲测自检） | DONE 11-26: 12 场景 6/6 轴, 原话 grep 12/12 命中, 盲测 PASS; sub 两次死于 27b 输出上限→Lead 直接执行（T4a 先例） |
| T5 | 思考对话收录管道 | Lead（持续） | skill hq-dialogue-capture 判据 + corpus/hermes/ 落盘 | 管道建成 11-26: 首条已落盘(质疑猜想验证/死亡永生段); 每次思考对话触发收录 |

## 缺口清单
- 邮件登录态: 真实 Edge profile 的 Google 会话疑似服务端已失效（证据: 真实 profile 恢复的标签页里含 Google 登录页，早于本轮操作）[待核验: D 在真实 Edge 打开 mail.google.com 一次即可定案]
- QQ 邮箱: 真实 profile 有 30 个 qq/tencent cookie，登录态 [待核验]
- "复活"技术定义: T6 调研已派发 arena（01a213fa, 11-26），Q1-Q3 三方向 SOTA 调研中
- extra 808 条（ai_chats 历史挖掘）处置决定: 不并入主盘点（主文件=任务卡 5 范围，口径保持）；作为内容层扩展池，做更深聚类/时间轴分析时用
- 微信/QQ 本机不全（D: 部分记录在别的电脑，还有未同步部分），等 D 导出
- 语料库 646 会话中"思考类"会话占比 [待核验]（T4 挖掘时统计）
