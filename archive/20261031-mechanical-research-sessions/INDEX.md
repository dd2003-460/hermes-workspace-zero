# origin: ai — 机械任务书调研会话归档（2026-10-31）

成璐指令：所有"没有用户痕迹的、机械任务书的调研"全部归档，保留最新活跃项目让 AI 持久交互。
本目录 = ego/arena 通道的一次性批次产物（脚本 + 日志 + 截图），全部 origin: ai，无用户手写内容。

## 归档清单

| 目录 | 原路径 | 内容 | 时间 |
|---|---|---|---|
| arena-b8-20261024/ | ego/ | pfb bench b8 批次提交/检查脚本 + 14 轮 round-N.mjs + 截图 | 2026-10-24 |
| arena-cleanup-20261024/ | ego/ | b8 批次清理记录 | 2026-10-24 |
| channel-check-20261023/ | ego/ | arena 通道连通性检查（r1-r4 脚本 + 截图） | 2026-10-23 |
| market-alpha-step05-20261028/ | ego/ | T3/T4 任务书 prompt 注入文本（step-05 双 02.5 续推） | 2026-10-28 |
| ego-b11-20261026/ | 顶层 | d1-video batch-11 Opus 5.5 对标素材采集（B站调研 round-01~05 + yt-dlp refs + E25-E28 渲染日志） | 2026-10-26 |

## 保留未动（活跃工作线，非一次性调研）

- `market-alpha/` — 独立 git 仓，T3/T4 step-05 续推中（最后 commit 2026-10-30），是"最新的"持续工作线之一
- `d1-video-recreation/` — 独立 git 仓，batch-12（E29-E32）待执行，下一步明确
- `pfb/` — ralph-loop runner 主战场，stop-hook 活跃 goal 在此
- ~~`ego/` 剩余 .mjs 顶层脚本~~ — **2026-10-31 已追加归档**：33 个一次性注入/探查脚本收进 `ego/arena-archive-20261031/mech-scripts/`（含 arena 注入操作教训 README），ego 顶层现只剩 README + archive 目录
- `.pae/archive/20261031-pae-sessions/` — 上一轮已归档的 8 个 PAE 会话

## 追加归档（2026-10-31 r74）

market-alpha T3-R3/T4-R1 双阻塞解除时产生的 33 个一次性浏览器自动化脚本（probe/inject/check/click 系列 + arena-b8 旧批次脚本），从 ego/ 顶层移入 `ego/arena-archive-20261031/mech-scripts/`。
唯一保留信息：该目录 README.md 里的 4 条 arena.ai 会话注入操作教训（先点"继续工作"才出编辑器、必须 CDP 真实键盘、长文本多次发送触发 reCAPTCHA、可用模板 inject-t3-final.mjs）。
