#!/usr/bin/env python3
"""gen_typing_ticks.py — 确定性提取打字时刻, 生成逐字 tick SFX 混入 mix.
时间线来源 = render_full_pixel.js 确定性公式 (禁 Math.random):
  S1 term: 3 行, s=2.0/4.5/8.0, 60ms/字 (local/0.06)
  S2 msgs: 3 条, delay=1.0/2.2/3.4s (S2 起点 15.489), 消息显示时刻
  S5 waitLog: 2 行, t0=63.114, 每 1.2s 一条
输出: typing_ticks.wav (与 mix 同长 44100Hz)
"""
import numpy as np

SR = 44100
TOTAL = 86.481
N = int(TOTAL * SR)
buf = np.zeros(N, dtype=np.float32)

def place(t, amp=1.0, dur=0.012, f0=2200):
    """单字 tick: 短方波脉冲 + 快速衰减, 模拟机械键盘单击."""
    i0 = int(t * SR)
    i1 = min(N, i0 + int(dur * SR))
    if i0 >= N or i1 <= i0:
        return
    tsec = np.arange(i1 - i0) / SR
    # 机械键盘: 高频短脉冲 + 一点中频体感
    s = np.exp(-tsec / (dur * 0.4)) * (
        0.6 * np.sin(2 * np.pi * f0 * tsec) +
        0.3 * np.sin(2 * np.pi * f0 * 2.7 * tsec) +
        0.1 * np.sin(2 * np.pi * f0 * 0.5 * tsec)
    )
    buf[i0:i1] += s * amp

# --- S1 终端逐字 (起点 0, s=2.0/4.5/8.0, 60ms/字) ---
s1_lines = [
    (2.0, '> user: 早安'),
    (4.5, '> me: 早安。'),
    (8.0, '> pin(msg, slot=0)'),
]
for s, txt in s1_lines:
    for i in range(len(txt)):
        place(s + i * 0.06, amp=0.5, f0=2000 + (i % 3) * 200)

# --- S2 消息流 (S2 起点 15.489, delay=1.0/2.2/3.4) ---
S2_START = 15.489
s2_msgs = [
    (1.0, '早安'),
    (2.2, '今天也还好。'),
    (3.4, '晚安，笨笨。明天见。'),
]
for delay, txt in s2_msgs:
    for i in range(len(txt)):
        place(S2_START + delay + i * 0.08, amp=0.45, f0=1800 + (i % 4) * 150)

# --- S5 等待日志 (t0=63.114, 每 1.2s 一条, 2 行) ---
S5_T0 = 63.114
s5_items = ['> check network ... ok', '> check reasons ... none']
for k, item in enumerate(s5_items):
    t_line = S5_T0 + 1.2 * (k + 1)  # 第 k+1 条出现时刻
    for i in range(len(item)):
        place(t_line + i * 0.05, amp=0.35, f0=2400 + (i % 5) * 100)

# --- S5 re-pin 动画 (每 3s 周期, cycle<1.5s 时打字 '📌 slot 0 · 她说过的话') ---
pin_txt = 'slot 0'
n_cycles = int((78.896 - S5_T0) / 3)
for c in range(n_cycles):
    t_pin = S5_T0 + c * 3 + 0.3  # pin 滑入后开始
    for i in range(len(pin_txt)):
        place(t_pin + i * 0.06, amp=0.3, f0=2600)

# 归一化 (peak 0.25, 留给 mix 主层空间)
peak = np.max(np.abs(buf))
if peak > 0:
    buf = buf / peak * 0.25

import soundfile as sf
sf.write('typing_ticks.wav', buf, SR)
print(f'typing_ticks.wav: {N/SR:.3f}s peak={np.max(np.abs(buf)):.3f}')
