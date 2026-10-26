# D1-ai-video-recreation — AI 独白短片复刻
# origin: ai

## 本文件夹主要功能

AI 独白短片风格复刻管线项目：Remotion 视频合成 + 音频合成（edge-tts/piper）。SOP 索引见 `INDEX.md`；独立检出仓位于 workspace 根 `d1-video-recreation/`（origin `github.com/dd2003-460/d1-video-recreation`），本目录放项目级规划与记录。

## 接口

- 输入：参考视频、脚本主题
- 输出：成片（检出仓 `outputs/`）
- 对外函数签名：检出仓 `src/`（Root.tsx/Video.tsx/remotion.config.ts）+ `scripts/render_*.js`

## 调用说明

- 导航：`INDEX.md` → SOP；代码在检出仓内，本目录不改仓内结构
