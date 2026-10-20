#!/usr/bin/env python3
"""v0.9 audio duck: S6 segment strings -3dB + 1.2s fadeout + S5 heartbeat -3dB.
Reads final_mix_v0.6.wav, applies ducking, outputs final_mix_v0.9.wav.
"""
import numpy as np, wave, os

SR = 44100
D = os.path.dirname(__file__)
IN = os.path.join(D, 'final_mix_v0.6.wav')
OUT = os.path.join(D, 'final_mix_v0.9.wav')

def load_wav(path):
    with wave.open(path, 'r') as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return data

def save_wav(path, data):
    peak = np.max(np.abs(data))
    if peak > 0.95:
        data = data / peak * 0.95
    out = (data * 32767).astype(np.int16)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())

mix = load_wav(IN)
total = len(mix) / SR
print(f"Input: {total:.3f}s")

# S5 heartbeat segment: 63.114-78.896s → -3dB (×0.707)
s5_start = int(63.114 * SR)
s5_end = int(78.896 * SR)
mix[s5_start:s5_end] *= 0.707
print(f"S5 duck: 63.1-78.9s ×0.707 (-3dB)")

# S6 segment: 78.896-86.481s → -3dB + 1.2s linear fadeout at end
s6_start = int(78.896 * SR)
s6_end = len(mix)
mix[s6_start:s6_end] *= 0.707
print(f"S6 duck: 78.9-86.5s ×0.707 (-3dB)")

# 1.2s linear fadeout at the very end (85.281-86.481s)
fade_start = int(85.281 * SR)
fade_len = min(s6_end - fade_start, int(1.2 * SR))
fade = np.linspace(1.0, 0.0, fade_len)
mix[fade_start:fade_start + fade_len] *= fade
print(f"Fadeout: 85.3-86.5s linear to 0")

# Verify RMS
for label, a, b in [("S5(63-78s)", 63, 78), ("S6(80-85s)", 80, 85), ("pre-S5(50-60s)", 50, 60)]:
    seg = mix[int(a*SR):int(b*SR)]
    rms = np.sqrt(np.mean(seg**2))
    print(f"  {label}: RMS={rms:.4f}")

save_wav(OUT, mix)
print(f"Wrote {OUT}: {len(mix)/SR:.3f}s")
