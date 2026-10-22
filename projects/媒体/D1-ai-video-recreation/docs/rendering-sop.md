# 媒体渲染流程 SOP（ffmpeg 帧序列方案）

> origin: ai · 2026-10-22 · goal-0b22f789 r5
> 方案：Node+canvas 帧序列 + ffmpeg 合成（Remotion 弃用 D6 2026-10-19）

## 1. 方案概述

- **弃用 Remotion**：CHS headless shell 挂起 >20s，Remotion CLI/Node API 全 delayRender timeout，烧 2h+ 无新事实（D6 决策）
- **新方案**：Node+canvas 渲染 720p 帧序列（PNG）→ ffmpeg 合成 + 混音
- **Remotion 代码保留**：`outputs/src/`（Root.tsx/Video.tsx）作帧渲染器的场景/布局参考

## 2. 帧渲染步骤

```bash
cd projects/媒体/D1-ai-video-recreation/outputs/scripts
node render_frames.js
# 输出: frames/*.png（3540 帧 @30fps, 1280x720）
# 依赖: npm install canvas（Node canvas 库）
```

**关键参数**：
- `W=1280, H=720, FPS=30, TOTAL=3540`
- 场景边界：`S[6]`（6 场景，STARTS/DUR 数组定义）
- 全局 token 时间线：`tokenAt(t)`（M-3：缓慢消耗 → 压缩跳水 → 重新积累）

## 3. 音频渲染步骤

```bash
node render_audio.mjs
# 输出: audio/*.wav（人声 + BGM）
# 依赖: Piper TTS（build_audio_piper.py）+ gen_bgm.py
```

**关键脚本**：
- `build_audio_piper.py`：Piper TTS 人声
- `gen_bgm.py` / `gen_emotional_bgm.py` / `gen_typing_bgm.py`：BGM 生成
- `build_final_mix_v04.py`：最终混音

## 4. ffmpeg 合成步骤

```bash
cd projects/媒体/D1-ai-video-recreation/outputs
# 帧序列 → mp4
ffmpeg -framerate 30 -i scripts/frames/%05d.png \
  -c:v libx264 -preset slow -crf 23 \
  -pix_fmt yuv420p \
  -vf scale=1280:720 \
  video_only.mp4

# 混音（视频 + 音频）
ffmpeg -i video_only.mp4 -i audio/final_mix.wav \
  -c:v copy -c:a aac -b:a 192k \
  -shortest \
  full_v1.3.mp4
```

**关键参数**：
- `-framerate 30`：帧率
- `-c:v libx264 -preset slow -crf 23`：H.264 编码（CRF 23 = 视觉无损）
- `-pix_fmt yuv420p`：兼容性
- `-c:v copy`：视频流不重编码
- `-c:a aac -b:a 192k`：音频 AAC 192kbps
- `-shortest`：以最短流为准

## 5. 降级方案

- **渲染超时**：540p（`H=540`）/ 24fps（`FPS=24`）/ 抽帧稀疏（`TOTAL=1770`）
- **canvas 依赖问题**：`npm rebuild canvas`（Node 版本兼容）
- **ffmpeg 缺失**：`brew install ffmpeg`（macOS）

## 6. 故障排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `Error: Cannot find module 'canvas'` | canvas 库未安装 | `npm install canvas` |
| `frames/ 目录为空` | 渲染失败 | 检查 `render_frames.js` 报错 + Node 版本 |
| `ffmpeg: command not found` | ffmpeg 未安装 | `brew install ffmpeg` |
| `video_only.mp4 黑屏` | 帧序列路径错误 | 检查 `-i scripts/frames/%05d.png` 路径 |
| `audio 不同步` | 帧率/音频长度不匹配 | 检查 `-framerate 30` + `-shortest` |

## 7. 输出验证

```bash
# 检查视频
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate \
  -of csv=p=0 full_v1.3.mp4
# 预期: 1280,720,30/1

# 检查音频
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,sample_rate \
  -of csv=p=0 full_v1.3.mp4
# 预期: aac,44100
```

完成: 2026-10-22T12:55+08:00
