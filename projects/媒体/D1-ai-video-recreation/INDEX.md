# D1-ai-video-recreation — 媒体/AI视频复刻

**origin: ai**（任务源自 m00002 用户指令）

调研并复刻"AI 独白短片"类视频风格（参考：B站《每天和AI说话的那个人，突然不来了》《压缩》+ 小红书 AI 幻觉讲解视频，均为 Claude Opus 5.5 驱动生成）。

- `tasks/` — 分解与任务状态
- `memory/` — 探索记录（调研、风格分析、差距审计）
- `outputs/` — 产出（脚本、素材、成片）

## SOP 索引（2026-10-21）

| SOP | 落点 |
|------|------|
| 渲染管线 | Remotion 工程根 = `outputs/src/`（Root.tsx/Video.tsx/remotion.config.ts），渲染脚本 `outputs/scripts/render_*.js`，音频 `outputs/scripts/gen_*.py` + `build_audio_piper.py`；里程碑记录 `memory/milestone-full-*.md` |
| loop 核验/调研外包 | skill `arena-outsource`（`.claude/skills/arena-outsource/SKILL.md`） |
| 网页 LLM 交叉验证 | skill `ego-verify`（`.claude/skills/ego-verify/SKILL.md`） |
| 项目结构体检 | `scripts/project-tidy/` |
