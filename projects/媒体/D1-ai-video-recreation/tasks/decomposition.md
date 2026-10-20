# 任务分解 — AI 风格视频复刻（D1-ai-video-recreation）

**origin: ai** · 2026-10-19 · 依据：用户 m00002 goal + memory/style-analysis.md + memory/research-github.md

## 用户目标（原样保留）
1. 看到 3 个参考视频的艺术风格/连接逻辑（似乎用 Claude Opus 5.5 做）
2. 调研怎么做类似风格视频（skill / GitHub 仓库）
3. 做一个类似视频
4. 自己审核差距并优化

## 分解树（正交切分）

```
A. 参考视频风格分析（看/听/拆）
   A1 [完成] 元数据+简介抓取（yt-dlp）
   A2 [完成] GitHub/工具链调研（subagent，research-github.md）
   A3 [进行中] 画面抽帧分析（ffmpeg 每10s帧 → 配色/字体/动效/转场）
   A4 [跳过→降级] 小红书视频画面（需登录，未登录；只有文字主题，标 conf 0.3，不再阻塞）
   A5 [做] 音频特征（ffprobe 确认有无人声旁白 → 决定要不要 TTS）
B. 内容创作
   B1 选题（对标视频1"笨笨"叙事，但写自己的原创脚本，不复刻剧情）
   B2 独白脚本（6分钟≈1900-2100字 or 4分钟≈1300字；句间10帧/段间30帧节奏参数）
   B3 音频生产：edge-tts Yunxi 旁白（pin 7.2.8）+ SF2 钢琴 BGM（tauMidi 或 Synthesizer_in_Python）
C. 视频制作（Remotion）
   C1 工程骨架 npx create-video（720p30）
   C2 签名动画组件库（文字逐字spring/呼吸光圈/上下文窗口可视化/粒子）
   C3 分镜表（每句独白→一个 scene→时长对齐音频）
   C4 渲染 v0.1（npx remotion render）
D. 审核+优化（04.5）
   D1 v0.1 抽帧自检（对照 A3 的参考风格清单）
   D2 独立 subagent 反方复核（挑差距）
   D3 差距清单 → v0.2 优化 → 复审
E. 交付
   E1 loop-state.json + 最终回复（风格分析/连接逻辑/差距报告）
   E2 可选：发布渠道（默认不发布，本地交付）
```

## 正交性核对
A 是感知（输入），B 是内容（文本），C 是渲染（代码），D 是评估，E 是交付——无重叠。A 与 B 并行安全；C 依赖 B2/B3 完成。

## 空缺清单
1. 参考视频画面级特征（A3，ffmpeg 装好后补）
2. 参考音频是否有 TTS 人声（A5，ffprobe/听）
3. 小红书视频画面（放弃，记 conf 0.3）
4. v0 尚未存在（全部产出在 C/D）

## 任务表（派发只执行此表内条目）
| id | 任务 | 依赖 | 并行 | 状态 |
|----|------|------|------|------|
| T1 | ffmpeg 抽帧两参考视频 + 画面风格分析回填 style-analysis.md | ffmpeg装好 | 与T2并行 | in_progress |
| T2 | 写 4min 原创独白脚本（对标"笨笨"情感结构，主题自选，不抄剧情） | 无 | 与T1并行 | pending |
| T3 | 音频：edge-tts 旁白 + 钢琴 BGM 生成 wav | T2 | T1后 | pending |
| T4 | 视频工程 + 组件 + 分镜 + 渲染 v0.1（方案切换：ffmpeg 帧序列，见 D6） | T3 | - | in_progress |
| T5 | 反方复核 subagent（对照参考视频找差距） | T4 | - | done (v0.4 前, review-v0.1.md) |
| T6 | v0.2→v0.4 优化 + 渲染 + 终稿 | T5 | - | done (full_v0.4.mp4) |
| T7 | loop-state.json + 最终回复 | T6 | - | done (v0.5.1 轮) |

## 决策记录
- D1: 时长选 4 分钟左右（3.7min 对标《压缩》），不贪 6min —— 渲染时间+迭代预算考虑（D2 代价律）
- D2: 技术栈 Remotion（个人免费）；若渲染超时降级 540p/24fps 或抽帧稀疏
- D3: 不复刻"笨笨"剧情（意图校验：产出需回溯用户意图=做"类似风格"，非抄袭；原创叙事更对齐"成璐的数字分身"身份）
- D4: 小红书视频降级处理（画面不可得，只用文字主题做风格参考），不写 APPROVALS（登录不是审批项，是能力边界，记录即可）
- D5: 旁白用 edge-tts Yunxi（免费、中文自然度够、调研已验证≈5.5字/秒）→ 实际 edge-tts 被 403（WSServerHandshakeError，服务风控/墙），改用 macOS `say -v Tingting -r 120` 本地 TTS（免费零依赖，自然度低一档，标 conf 0.6）
- D6（2026-10-19）: **放弃 Remotion 渲染管线，改 ffmpeg 帧序列方案**。理由：本机 CHS（Chromium 157 headless shell）spawn 后 --dump-dom 挂起 >20s 不返回（只有 --version 正常），Remotion CLI 与 Node API（bundle+renderMedia，显式 browserExecutable+隔离参数）全部 delayRender timeout；bundle 编译正常但 waitForRoot 回调不触发（疑 remotion 双实例或 headless 环境异常）。已烧 2h+ 调试预算无新事实（思考预算终止指令③：2 轮无新事实→换工具）。新方案：Node+canvas 渲染 720p 帧序列（PNG 5400 帧≈3540 帧@30fps）→ ffmpeg 合成+混音。Remotion 代码（Root.tsx/Video.tsx）保留作帧渲染器的场景/布局参考（逻辑等价迁移到 canvas 绘制）。

| T8 | 画风定标：抽帧实证参考片画风，确认像素路线 | 无 | - | done (2026-10-20, 参考片=暖色手绘插画+像素机器人混合; 用户 m00702/m01003 明确要像素, 不改画风) |
| T9 | v0.5 视觉密度：像素叙事道具（S4 电量条/S5 心跳日志/S1 日期行）+ 全屏极简文字过渡卡（参考 v2 留白节奏） | T8 | - | done (2026-10-20, render_full_pixel.js 517 行) |
| T10 | v0.5 全渲染 full_v0.5.1.mp4 + 抽帧/字幕同步自检 | T9 | - | done (2026-10-20, 5189 帧 160s, 2.59MB, 4 帧自检通过) |
| T11 | v0.5 反方复核 subagent（抽帧对比参考片，H/M/L 差距清单） | T10 | - | done (2026-10-20, subagent 5d83cc30: 无 P0 可交付, 6 条差距, 4 条 P0/P1 已修入 v0.5.1) |
| T12 | v0.5 状态回写（loop-state.json + milestone-full-v0.5.md 修订）+ 最终差距报告 | T11 | - | done (2026-10-20) |

## v0.5 决策记录
- D7（2026-10-20）: 画风定标——抽帧实证参考片1=暖色手绘插画办公室（条纹墙+晾衣绳便签+橙色机器人，帧 v1_f_010/017/034），参考片2=暗色大字卡+进度条（v2_f_004/011）。style-analysis.md 中"Win95 桌面"描述与帧不符，已修正。像素路线=用户 m00702+m01003 明确指定，v0.5 不转向插画（转向需推倒 4 版迭代，D2 代价律）。
- D8（2026-10-20）: v0.5 聚焦与画风无关的差距：① 视觉密度（叙事道具）② 节奏（全屏留白文字卡，对标 v2 的"记忆会被压缩。/ 在乎不会。"大字卡式留白）。弦乐层 BGM 降级到 v0.6 候选（合成弦乐风险：易显廉价，收益不确定，先做确定性收益项）。

## v0.6-v0.8 任务表
| id | 任务 | 依赖 | 状态 |
|----|------|------|------|
| T13 | v0.6 弦乐BGM: numpy加法合成gen_strings.py→strings_layer.wav, 混音piano×0.6+strings×0.5+sfx×0.8→final_mix_v0.6.wav, 渲染+合流+验证 | v0.5 | done |
| T14 | v0.6 像素修复: 用户反馈SCALE=2元素重叠→改回SCALE=4(1280x720原尺寸), 重新渲染+合流 | T13 | done |
| T15 | v0.7 便签卡装置(P2-①): CARD从纯文字→淡黄便签卡+胶带+滑入动画(ease-out 0.3s), 渲染+合流+验证 | T14 | done |
| T16 | v0.8 S6收尾降温(P2-②): 紫色光晕→冷蓝灰(#6e88a8)无脉动, 背景→冷蓝灰(#040810), 淡入1.2→1.8s, 渲染+合流+验证 | T15 | done |
| T17 | 弦乐BGM调优: 频段分析(低16.1%/中79.8%/高3.7%), RMS -20.6dB, 动态2dB——验证合理, 无需调整 | T13 | done |

## v0.6-v0.8 决策记录
- D9（2026-10-20）: 像素粒度=SCALE必须匹配输出分辨率。SCALE=2→640x360→ffmpeg放大到1280x720→像素块2x重叠。SCALE=4→1280x720→1:1无放大。用户(m00784): "颗粒度缩小就是更连续，不是颗粒更大重叠"。
- D10（2026-10-20）: 弦乐BGM用numpy加法合成(双detune±0.6cents, 偶次谐波×1.15, 1/k衰减), 结构Intro(Cm)→Dev(Cm-Ab-Eb-Bb)→Climax(Fmaj)→Outro。MusicGen 30s max不适合86s, VSCO 2 CE备选。
- D11（2026-10-20）: 便签卡装置=叙事道具参与情节。CARD从全屏纯文字→右下角淡黄便签卡+胶带+滑入, 像被贴在显示器上。对标参考片"道具参与叙事"。
- D12（2026-10-20）: S6降温=冷蓝灰替代紫色, 去脉动, 放慢淡入。对标参考片2"暗色大字卡"沉收束。

## v0.9-v1.0 任务表
| id | 任务 | 依赖 | 状态 |
|----|------|------|------|
| T18 | v0.9 反方复核修复: 打字节奏60ms/字+S2依次入场+S6字幕2.0s+CARD像素化+音频duck(S5/S6 -3dB+淡出)+转场0.6s → full_v0.9.mp4 | T17 | done (2026-10-20, 5189帧184.8s, 2.35MB, 帧目检通过) |
| T19 | v1.0 去人声(项目要求): 移除Piper TTS人声层, 只保留打字声SFX+钢琴+弦乐BGM → final_mix_v1.0.wav (piano×0.55+strings×0.45+SFX, S5/S6 duck保留) | T18 | done (2026-10-20, mix_v1.0.py, peak 0.411) |
| T20 | v1.0 定位错乱修复: check_overlap.js审计→S4空行宽264→230(避开Clawd x=276) + S5 compress文字y=68→64(避开pin动画顶74) → 审计清零 | T18 | done (2026-10-20, node -c通过, 审计S4/S5 no overlaps) |
| T21 | v1.0 渲染+合流+验证+回写 | T19,T20 | done (2026-10-20, 5189帧149.3s, full_v1.0.mp4 1280x720@60fps 86.48s 2.42MB, ffprobe+帧目检通过, loop-state回写) |

## v0.9-v1.0 决策记录
- D13（2026-10-20）: 去人声是项目要求（用户 m01217 "直接去掉人声（写入项目要求），只用打字声伴随图像变化"）。音频=打字SFX+钢琴+弦乐，无Piper TTS。SFX时间线沿用mix_sfx.py布局（S1 tick/click, S2 ping, CARD whoosh, S4 heartbeat, S5 buzz+heartbeat）。
- D14（2026-10-20）: 定位错乱=元素位置错乱（用户确认）。用确定性重叠审计脚本check_overlap.js替代逐帧目检（可复现、全场景覆盖）。设计内嵌套（代码在面板/文字在卡片/胶带贴卡）不计为错乱。
