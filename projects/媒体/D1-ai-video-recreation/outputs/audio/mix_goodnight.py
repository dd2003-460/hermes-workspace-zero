#!/usr/bin/env python3
"""
mix_goodnight.py — 晚安小视频 30s 音频
钢琴 BGM 尾部 30s × 0.55 + 弦乐尾部 30s × 0.45 + 打字 ticks + 末 1.2s 淡出
"""
import wave
import struct
import numpy as np

SR = 44100
TOTAL = 30.0
N = int(SR * TOTAL)

def load_wav(path):
    with wave.open(path, 'rb') as w:
        nch = w.getnchannels()
        sw = w.getsampwidth()
        sr = w.getframerate()
        nf = w.getnframes()
        raw = w.readframes(nf)
    data = np.frombuffer(raw, dtype=np.int16 if sw == 2 else np.int32).astype(np.float64)
    if nch > 1:
        data = data.reshape(-1, nch).mean(axis=1)
    if sw == 2:
        data = data / 32768.0
    else:
        data = data / 2147483648.0
    # resample to 44100 if needed
    if sr != SR:
        ratio = SR / sr
        newlen = int(len(data) * ratio)
        xp = np.linspace(0, len(data) - 1, num=len(data))
        xp_new = np.linspace(0, len(data) - 1, num=newlen)
        data = np.interp(xp_new, xp, data)
    return data

def gen_ticks(t_start, t_end, interval):
    """Generate typing ticks at given interval."""
    ticks = np.zeros(N)
    t = t_start
    while t < t_end and t < TOTAL:
        idx = int(t * SR)
        if idx < N:
            # short click: 5ms decaying sine 4kHz
            dur = int(0.005 * SR)
            end = min(idx + dur, N)
            tt = np.arange(end - idx) / SR
            env = np.exp(-tt * 400)
            sig = np.sin(2 * np.pi * 4000 * tt) * env * 0.3
            ticks[idx:end] += sig
        t += interval
    return ticks

print("Loading piano BGM...")
piano = load_wav('emotional_bgm.wav')
# Take last 30s (from 56.481s to 86.481s)
start = int((86.481 - TOTAL) * SR)
piano_tail = piano[start:start + N]
if len(piano_tail) < N:
    piano_tail = np.pad(piano_tail, (0, N - len(piano_tail)))
print(f"  piano: {len(piano_tail)/SR:.1f}s peak={np.abs(piano_tail).max():.3f}")

print("Loading strings...")
strings = load_wav('strings_layer.wav')
strings_tail = strings[start:start + N]
if len(strings_tail) < N:
    strings_tail = np.pad(strings_tail, (0, N - len(strings_tail)))
print(f"  strings: {len(strings_tail)/SR:.1f}s peak={np.abs(strings_tail).max():.3f}")

# Typing ticks (S1 1.5-8s 60ms, S2 11.5-19s 50ms)
ticks = gen_ticks(1.5, 8.0, 0.06) + gen_ticks(11.5, 19.0, 0.05)

# Mix
mix = piano_tail * 0.55 + strings_tail * 0.45 + ticks

# Fade out last 1.2s
fade_start = int((TOTAL - 1.2) * SR)
fade_len = N - fade_start
fade = np.linspace(1, 0, fade_len)
mix[fade_start:] *= fade

# Normalize
peak = np.abs(mix).max()
if peak > 0:
    mix = mix / peak * 0.85

# Write
out = 'final_mix_goodnight.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    data = (mix * 32767).astype(np.int16)
    w.writeframes(data.tobytes())

print(f"Output: {out} {TOTAL:.1f}s peak={np.abs(mix).max():.3f}")
