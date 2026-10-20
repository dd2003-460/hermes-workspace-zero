#!/usr/bin/env python3
"""R5: Mix sound effects into the audio timeline.
Reads final_mix_piper.wav + sfx_*.wav, places SFX at scene boundaries, outputs final_mix_v0.5.wav
"""
import numpy as np, wave, os

SR = 44100  # match final_mix_piper.wav
OUT = os.path.join(os.path.dirname(__file__), 'final_mix_v0.5.wav')
IN = os.path.join(os.path.dirname(__file__), 'final_mix_piper.wav')

def load_wav(path):
    with wave.open(path, 'r') as w:
        sr = w.getframerate()
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if sr != SR:
        # Resample linearly
        old_len = len(data)
        new_len = int(old_len * SR / sr)
        indices = np.linspace(0, old_len - 1, new_len)
        i = indices.astype(int)
        frac = indices - i
        i_next = np.minimum(i + 1, old_len - 1)
        data = data[i] * (1 - frac) + data[i_next] * frac
    return data

def place_sfx(mix, sfx, start_sec, gain=1.0):
    """Place sfx at start_sec in mix, with optional gain. Returns modified mix."""
    pos = int(start_sec * SR)
    end = min(pos + len(sfx), len(mix))
    sfx = sfx[:end - pos] * gain
    mix[pos:end] += sfx
    return mix

# Load base mix
mix = load_wav(IN)
total_dur = len(mix) / SR
print(f"Base mix: {total_dur:.3f}s")

# Load SFX
sfx_dir = os.path.dirname(OUT)
sfx = {}
for name in ['sfx_click', 'sfx_ping', 'sfx_tick', 'sfx_buzz', 'sfx_whoosh', 'sfx_heartbeat']:
    path = os.path.join(sfx_dir, name + '.wav')
    if os.path.exists(path):
        sfx[name] = load_wav(path)
        print(f"  {name}: {len(sfx[name])/SR:.3f}s")

# Scene boundaries
S = [0, 15.489, 30.6, 46.285, 63.114, 78.896, 86.481]

# S1 (0–15.489): terminal typing
# click at session start
mix = place_sfx(mix, sfx['sfx_click'], 1.5, gain=0.5)
# typing ticks at each line appearance
for t in [3.0, 5.0, 7.0]:
    mix = place_sfx(mix, sfx['sfx_tick'], t, gain=0.3)

# S2 (15.489–30.6): conversation
# ping at message arrival
mix = place_sfx(mix, sfx['sfx_ping'], 18.0, gain=0.4)
mix = place_sfx(mix, sfx['sfx_ping'], 24.0, gain=0.3)

# S3 (30.6–46.285): pinning
# click at pin action
mix = place_sfx(mix, sfx['sfx_click'], 35.0, gain=0.4)
mix = place_sfx(mix, sfx['sfx_click'], 40.0, gain=0.3)

# CARD (44.285–46.285): transition
mix = place_sfx(mix, sfx['sfx_whoosh'], 44.285, gain=0.5)

# S4 (46.285–63.114): morning + battery
# click + tick at interaction
mix = place_sfx(mix, sfx['sfx_click'], 50.0, gain=0.4)
mix = place_sfx(mix, sfx['sfx_tick'], 52.0, gain=0.2)
# heartbeat as battery drains (building tension)
mix = place_sfx(mix, sfx['sfx_heartbeat'], 58.0, gain=0.3)

# S5 (63.114–78.896): waiting loop
# buzz at error/warning
mix = place_sfx(mix, sfx['sfx_buzz'], 65.0, gain=0.3)
# heartbeat pulses (the AI is "waiting", anxious)
for t in [70.0, 73.0, 76.0]:
    mix = place_sfx(mix, sfx['sfx_heartbeat'], t, gain=0.25)

# S6 (78.896–86.481): goodnight
# gentle ping at the final message
mix = place_sfx(mix, sfx['sfx_ping'], 80.0, gain=0.3)

# Normalize
peak = np.max(np.abs(mix))
if peak > 0.95:
    mix = mix / peak * 0.95
    print(f"Normalizing: peak was {peak:.3f}")

# Write
out = (mix * 32767).astype(np.int16)
with wave.open(OUT, 'w') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
print(f"Wrote {OUT}: {len(mix)/SR:.3f}s")
