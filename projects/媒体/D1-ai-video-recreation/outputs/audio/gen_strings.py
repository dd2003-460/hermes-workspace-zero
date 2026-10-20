#!/usr/bin/env python3
"""
gen_strings.py — v0.6 弦乐 BGM 层
numpy 加法合成: 弦乐(双簧管+大提琴+小提琴) + 钢琴基础层
输出: strings_layer.wav (86.481s, 44100Hz, mono, 16-bit PCM)
结构: Intro(Cm,0-13s) → Dev(Cm-Ab-Eb-Bb,13-47s) → Climax(Fmaj,47-78s) → Outro(Cm9→Fmaj9,78-86.5s)
"""
import numpy as np
import wave

SR = 44100
DUR = 86.481
N = int(SR * DUR)

def midi_to_hz(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

def synth_string(freq, dur, sr=SR, harmonics=12, decay_rate=1.8, attack_ms=120):
    """加法弦乐: 偶次谐波为主(弦特征), 指数衰减, 短attack"""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for k in range(1, harmonics + 1):
        # 弦乐器: 1/k 幅值衰减, 偶次略强
        amp = 1.0 / k
        if k % 2 == 0:
            amp *= 1.15
        sig += amp * np.sin(2 * np.pi * freq * k * t + np.random.uniform(0, 2*np.pi))
    # 包络: attack + 指数衰减
    attack_n = int(attack_ms / 1000 * sr)
    if attack_n > 0:
        sig[:attack_n] *= np.linspace(0, 1, attack_n)
    sig *= np.exp(-decay_rate * t)
    return sig

def synth_piano(freq, dur, sr=SR, harmonics=20, decay_rate=2.5, attack_ms=5):
    """加法钢琴: 更多谐波(亮), 快速attack, 较快衰减"""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for k in range(1, harmonics + 1):
        amp = 1.0 / (k ** 1.3)
        sig += amp * np.sin(2 * np.pi * freq * k * t)
    attack_n = max(1, int(attack_ms / 1000 * sr))
    sig[:attack_n] *= np.linspace(0, 1, attack_n)
    sig *= np.exp(-decay_rate * t)
    return sig

def place_note(buf, start_s, note):
    """note: (midi, dur_s, synth_fn, vol)"""
    midi, dur, fn, vol = note
    freq = midi_to_hz(midi)
    sig = fn(freq, dur) * vol
    si = int(start_s * SR)
    ei = min(si + len(sig), len(buf))
    si = max(0, si)
    buf[si:ei] += sig[:ei - si]

# 和弦定义 (midi notes)
Cm = [48, 51, 55, 58]       # C E G Bb
Ab = [45, 48, 52, 55]       # Ab C Eb G
Eb = [52, 55, 59, 62]       # Eb G Bb D
Bb = [47, 50, 54, 58]        # Bb D F A
Fmaj = [53, 57, 60, 64]     # F A C E
Cm9 = [48, 51, 55, 58, 62]  # Cm + D
Fmaj9 = [53, 57, 60, 64, 67] # Fmaj + G

def chord_notes(chord, base_vol=0.3):
    """和弦→弦乐 notes (每个音一个长音)"""
    return [(m, 6.0, synth_string, base_vol) for m in chord]

# === 86.5s 时间轴 ===
buf = np.zeros(N, dtype=np.float64)

# Intro 0-13s: 钢琴独奏, Cm 稀疏, ppp
intro_piano = [
    (0.5, [(48, 3.0, synth_piano, 0.15), (55, 3.0, synth_piano, 0.12)]),
    (4.0, [(48, 3.0, synth_piano, 0.15), (51, 3.0, synth_piano, 0.10), (58, 3.0, synth_piano, 0.08)]),
    (8.0, [(48, 4.0, synth_piano, 0.12), (55, 4.0, synth_piano, 0.10), (60, 4.0, synth_piano, 0.06)]),
]
for t0, notes in intro_piano:
    for m, d, fn, v in notes:
        place_note(buf, t0, (m, d, fn, v))

# 大提琴低音 drone (Intro)
place_note(buf, 0.0, (36, 13.0, synth_string, 0.08))  # C2 持续低音

# Development 13-47s: 弦乐加入, Cm-Ab-Eb-Bb 进行
dev_sections = [
    (13.0, Cm, 0.25), (16.5, Ab, 0.22), (20.0, Eb, 0.20), (23.5, Bb, 0.18),
    (27.0, Cm, 0.28), (30.5, Ab, 0.25), (34.0, Eb, 0.23), (37.5, Bb, 0.20),
    (41.0, Cm, 0.30), (44.5, Ab, 0.25),
]
for t0, chord, vol in dev_sections:
    for m in chord:
        place_note(buf, t0, (m, 3.5, synth_string, vol))
    # 钢琴伴奏 (分解和弦)
    for i, m in enumerate(chord):
        place_note(buf, t0 + i * 0.4, (m + 12, 1.5, synth_piano, vol * 0.4))

# 小提琴旋律线 (Development)
violin_melody = [
    (13.5, 72, 2.5, 0.20),  # C5
    (16.5, 71, 2.5, 0.18),  # Bb4
    (20.0, 76, 2.5, 0.18),  # F5
    (23.5, 74, 2.5, 0.16),  # E5
    (27.0, 72, 2.5, 0.22),
    (30.5, 69, 2.5, 0.20),  # A4
    (34.0, 76, 2.5, 0.18),
    (37.5, 71, 2.5, 0.16),
    (41.0, 72, 3.0, 0.25),
    (44.5, 74, 3.0, 0.22),
]
for t0, m, d, v in violin_melody:
    place_note(buf, t0, (m, d, synth_string, v))

# Climax 47-78s: F major 转调, 弦乐八度, 钢琴 cascading
climax_sections = [
    (47.0, Fmaj, 0.35), (51.0, Cm, 0.30), (55.0, Fmaj, 0.38), (59.0, Bb, 0.32),
    (63.0, Fmaj, 0.40), (67.0, Cm, 0.35), (71.0, Fmaj, 0.42), (75.0, Cm9, 0.38),
]
for t0, chord, vol in climax_sections:
    # 弦乐 (低+高八度)
    for m in chord:
        place_note(buf, t0, (m, 4.0, synth_string, vol))
        place_note(buf, t0, (m + 12, 4.0, synth_string, vol * 0.5))
    # 钢琴 cascading
    for i, m in enumerate(chord):
        place_note(buf, t0 + i * 0.15, (m + 12, 2.0, synth_piano, vol * 0.35))
        place_note(buf, t0 + i * 0.15 + 0.1, (m + 24, 1.5, synth_piano, vol * 0.15))

# 小提琴高潮旋律
climax_melody = [
    (47.5, 77, 3.0, 0.30),  # F5
    (51.5, 76, 3.0, 0.28),  # E5
    (55.5, 81, 3.5, 0.32),  # A5
    (59.5, 79, 3.0, 0.28),  # G5
    (63.5, 81, 3.5, 0.35),
    (67.5, 80, 3.0, 0.30),  # Gb5→F5
    (71.5, 81, 4.0, 0.38),
    (75.5, 79, 3.0, 0.35),
]
for t0, m, d, v in climax_melody:
    place_note(buf, t0, (m, d, synth_string, v))

# Outro 78-86.5s: Cm9→Fmaj9, 渐弱, 最后一个钢琴音
outro_chords = [
    (78.0, Cm9, 0.25), (81.0, Fmaj9, 0.22),
]
for t0, chord, vol in outro_chords:
    for m in chord:
        place_note(buf, t0, (m, 5.0, synth_string, vol))
    for i, m in enumerate(chord):
        place_note(buf, t0 + i * 0.3, (m + 12, 3.0, synth_piano, vol * 0.3))

# 最后钢琴音 (C5, 长衰减)
place_note(buf, 84.0, (72, 3.0, synth_piano, 0.20))

# 归一化
peak = np.max(np.abs(buf))
if peak > 0:
    buf = buf / peak * 0.85  # 留 15% headroom

# 写 WAV
out_path = 'strings_layer.wav'
data = (buf * 32767).astype(np.int16)
with wave.open(out_path, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())

print(f'OK: {out_path} {len(data)/SR:.3f}s {SR}Hz mono 16-bit')
