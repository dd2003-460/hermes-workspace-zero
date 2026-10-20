#!/usr/bin/env python3
"""v1.0 audio: NO human voice. Only piano BGM + strings layer + SFX (typing sounds accompany image changes).
Project requirement (m01217): remove Piper TTS voice, keep typing SFX + strings BGM.
"""
import numpy as np, wave, os

SR = 44100
D = os.path.dirname(os.path.abspath(__file__))

def load(name):
    p = os.path.join(D, name)
    if not os.path.exists(p):
        return None
    with wave.open(p, 'r') as w:
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if sr != SR:
        old = len(data)
        new = int(old * SR / sr)
        idx = np.linspace(0, old - 1, new)
        i = idx.astype(int); f = idx - i; j = np.minimum(i + 1, old - 1)
        data = data[i] * (1 - f) + data[j] * f
    return data

def save(path, data):
    peak = np.max(np.abs(data))
    if peak > 0.9:
        data = data / peak * 0.9
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((data * 32767).astype(np.int16).tobytes())

TOTAL = 86.481
mix = np.zeros(int(TOTAL * SR), dtype=np.float32)
print(f"Canvas: {TOTAL}s @ {SR}Hz mono")

# Piano BGM (emotional_bgm.wav, 86.48s)
piano = load('emotional_bgm.wav')
if piano is not None:
    n = min(len(piano), len(mix))
    mix[:n] += piano[:n] * 0.55
    print(f"piano: {len(piano)/SR:.2f}s x0.55")

# Strings layer (strings_layer.wav, 86.48s)
strings = load('strings_layer.wav')
if strings is not None:
    n = min(len(strings), len(mix))
    mix[:n] += strings[:n] * 0.45
    print(f"strings: {len(strings)/SR:.2f}s x0.45")

# SFX placement (same timeline as mix_sfx.py — typing sounds accompany image changes)
def place(name, t0, gain=1.0):
    s = load(name)
    if s is None:
        return
    pos = int(t0 * SR)
    end = min(pos + len(s), len(mix))
    if pos < len(mix):
        mix[pos:end] += s[:end - pos] * gain
    print(f"  {name}@{t0}s x{gain}")

print("SFX:")
place('sfx_click.wav', 1.5, 0.5)
for t in [3.0, 5.0, 7.0]:
    place('sfx_tick.wav', t, 0.3)
place('sfx_ping.wav', 18.0, 0.4)
place('sfx_ping.wav', 24.0, 0.3)
place('sfx_click.wav', 35.0, 0.4)
place('sfx_click.wav', 40.0, 0.3)
place('sfx_whoosh.wav', 44.285, 0.5)
place('sfx_click.wav', 50.0, 0.4)
place('sfx_tick.wav', 52.0, 0.2)
place('sfx_heartbeat.wav', 58.0, 0.3)
place('sfx_buzz.wav', 65.0, 0.3)
for t in [70.0, 73.0, 76.0]:
    place('sfx_heartbeat.wav', t, 0.25)
place('sfx_ping.wav', 80.0, 0.3)

# v0.9 duck carried over: S5/S6 -3dB + 1.2s linear fadeout
mix[int(63.114 * SR):int(78.896 * SR)] *= 0.707
mix[int(78.896 * SR):] *= 0.707
fs = int(85.281 * SR)
fl = min(len(mix) - fs, int(1.2 * SR))
mix[fs:fs + fl] *= np.linspace(1.0, 0.0, fl)

# RMS by segment
for a, b in [(10, 20), (50, 60), (63, 70), (70, 75), (80, 85)]:
    seg = mix[int(a * SR):int(b * SR)]
    print(f"  {a}-{b}s RMS={np.sqrt(np.mean(seg**2)):.4f}")

out = os.path.join(D, 'final_mix_v1.0.wav')
save(out, mix)
print(f"Wrote {out}: {len(mix)/SR:.3f}s peak={np.max(np.abs(mix)):.3f}")
