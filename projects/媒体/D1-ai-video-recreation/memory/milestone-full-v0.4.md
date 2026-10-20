# origin: ai
# Milestone: full_v0.4 (场景情绪钢琴 BGM)
日期: 2026-10-20

## 本版交付
- outputs/full_v0.4.mp4 — 86.481s, 1280x720@60fps, h264+aac, 2.6MB, 5189 帧 (无丢帧)
- 相对 full_v0.3 的升级:
  - 新增**场景情绪钢琴 BGM**: 纯 numpy 合成 (本地免费, 无外部依赖), 稀疏空旷"环境钢琴"音色,
    跟随 6 场景情绪弧线: S1 希望(C add9) / S2 陪伴(Am) / S3 日常(F) / S4 不安(Dm,更暗更稀疏) /
    S5 寻找(Bb 挂留, 紧张不吵) / S6 释怀(C + D 的 add9 色彩, 温暖带一丝酸)
  - 混音: 情绪钢琴低电平铺底 (gain 0.32), 叠在敲击音 + Piper 旁白之下; tanh 软限幅, 峰值 0.88
  - 视频帧不变 (承 v0.3 的 5189 帧), 仅重合成音频轨

## 情绪 BGM 管线 (outputs/gen_emotional_bgm.py + outputs/build_final_mix_v04.py)
- 音色: 钢琴近似 = 基频+6 次谐波(高频衰减快) + 软起音 8ms + 指数衰减 + pad 极慢颤音(相位调制)
- 空间感: 双分支反馈延迟混响 (330ms + 1.618x, feedback 0.36)
- 和声 (MIDI): 每场景 = pad 持续音(起 0.8s/落 1.2s) + 3-5 个稀疏琶音音符(带时值/电平)
- 归一化峰值 0.62 → 混入终混 gain 0.32 → 终混 peak 0.88 / rms 0.128
- 产出: outputs/audio/emotional_bgm.wav (86.481s) → outputs/audio/final_mix_v04.wav (44100Hz mono)

## 混音验证 (旁白间隙抽测, 差值≈纯 BGM)
- pre-narration (1.0-1.4s, 开场): BGM rms 0.043 — 开场钢琴手势清晰可闻
- gap S1 (3.9-5.9s): BGM rms 0.011 — 旁白临近时退居其后
- S6 tail (84.5-86.4s): BGM rms 0.0025 — 结尾温柔收束
- 结论: BGM 是"托底"而非"抢戏", 旁白清晰度未受影响

## 自审 (诚实差距, 更新 v0.3 的差距表)
已达: 6 场景叙事 / 神经级 TTS / 像素文字 / 60fps / 机器人+动效 / 敲击音 / 字幕同步 / **场景情绪配乐**
仍存差距 (对标参考片):
1. 画风: 像素 vs 暖色手绘 (用户明确要像素, 风格取舍)
2. 视觉密度: 我方 UI 隐喻场景偏"干净", 参考片叙事道具更丰富 (贴纸/便签/温度计)
3. 配乐完成度: 现为合成钢琴(可控但非"成品乐"), 参考片有完整编曲 (钢琴+弦乐+动态)
4. 情绪曲线: 我方金句收尾偏"暖", 参考片更"沉" (创作选择)

## 下一版方向 (full_v0.5 候选)
- 更多叙事道具 (便签/贴纸/温度计) 提升视觉密度 — 当前最高优先
- 配乐加弦乐层 / 动态 (随情绪起伏的编曲变化)
- (可选) 参考片手绘风对照版

## 关键文件
- outputs/render_full_pixel.js (渲染器, 373 行)
- outputs/build_audio_piper.py (旁白+敲击音管线)
- outputs/gen_emotional_bgm.py (情绪钢琴 BGM 合成, 本版新增)
- outputs/build_final_mix_v04.py (v0.4 终混, 本版新增)
- outputs/full_v0.4.mp4 (本版交付)
- outputs/audio/emotional_bgm.wav / final_mix_v04.wav
- voices/zh_CN-huayan-medium.onnx (Piper 音色) / .ttsenv/
