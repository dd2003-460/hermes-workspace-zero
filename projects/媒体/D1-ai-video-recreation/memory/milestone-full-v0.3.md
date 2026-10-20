# origin: ai
# Milestone: full_v0.3 (Piper 神经音色 + 时间轴重建 + 机器人动效)
日期: 2026-10-20

## 本版交付
- outputs/full_v0.3.mp4 — 86.481s, 1280x720@60fps, h264+aac, 2.3MB, 5189 帧 (无丢帧)
- 相对 full_v0.2 的三项升级:
  1. 语音: macOS say Tingting → **Piper TTS 神经音色** (zh_CN-huayan-medium, 本地免费, 自然度大幅提升)
  2. 时间轴: 按 Piper 实际语音时长重建 (117.833s → 86.481s, 节奏更紧凑, 更贴近参考片)
  3. (承 v0.5) 笨笨机器人 + 环境动效 (扫描线漂移/输入光标闪烁/代码逐行打字/slot0 呼吸/金句前机器人)

## 音频管线 (outputs/build_audio_piper.py)
- 16 句 LINES → Piper synthesize_wav → 逐句去静音 (threshold 0.012, pad 0.14) 实测时长
- 重排 STARTS: GAP=2.2s, 首句 1.5s, 尾 1.8s → 总 86.481s
- 敲击 BGM (audio/typing_bgm.wav) loop, 电平 0.30, 旁白峰值 0.85, 淡入 0.4s/淡出 1.2s
- 产出: outputs/audio/final_mix_piper.wav (44100Hz mono 16bit, 86.481s) + timeline_piper.json
- 各句时长(s): [2.299,3.704,1.386,2.090,4.390,2.032,1.605,2.964,4.516,2.214,4.410,3.604,1.019,3.892,4.272,5.785]

## 新时间轴 (渲染器已同步)
- TOTAL=86.481, NFRAMES=5189, FPS=60
- STARTS[16]=[1.5,5.999,11.903,15.489,19.779,26.368,30.6,34.405,39.569,46.285,50.699,57.309,63.114,66.332,72.424,78.896]
- 场景边界 S1..S5 = 15.489/30.6/46.285/63.114/78.896, S6=86.481
- 已更新硬编码点: S1 终端(2.0/4.5/8.0)、S3 sStart=30.6+逐行(0.8+i*1.7)、S4 空行(46.285)/09:00(49.5)、S5 token(63.114)、S6 local(78.896)、SCENES 边界

## 自审 (诚实差距)
已达: 6 场景叙事完整 / 神经级中文 TTS / 像素文字清晰 / 60fps 流畅 / 机器人+动效 / 敲击音 BGM / 字幕逐字同步 (已抽 7 个场景边界帧验证同步)
差距 (对标参考片《AI会难过吗》《压缩》):
1. 画风: 我方像素风 vs 参考片暖色手绘插画 (用户明确要像素, 属风格取舍, 非缺陷)
2. 音乐: 敲击音 BGM 偏"功能", 参考片有完整情绪配乐 (钢琴/弦乐) — 下版可做成品 BGM
3. 视觉密度: 我方 UI 隐喻场景较"干净", 参考片画面元素更丰富 (贴纸/便签/温度计等叙事道具)
4. 情绪曲线: 参考片结尾情绪更"沉", 我方金句收尾偏"暖" (可接受, 是创作选择)

## 下一版方向 (full_v0.4 候选)
- 成品情绪 BGM (钢琴/环境音) 替换或叠在敲击音之下
- 更多叙事道具 (便签/贴纸) 提升视觉密度
- (可选) 参考片手绘风对照版

## 关键文件
- outputs/render_full_pixel.js (渲染器, 373 行)
- outputs/build_audio_piper.py (音频管线)
- outputs/full_v0.3.mp4 (本版交付)
- outputs/audio/final_mix_piper.wav / timeline_piper.json
- voices/zh_CN-huayan-medium.onnx (Piper 音色)
- .ttsenv/ (Piper python 环境)
