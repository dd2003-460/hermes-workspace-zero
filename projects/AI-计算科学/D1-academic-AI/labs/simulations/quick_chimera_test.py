#!/usr/bin/env python3
"""Quick chimera spatial coupling test"""
import numpy as np

N, K0, dt = 100, 1.5, 0.02
T_trans, T_meas = 1000, 200

for eps in [0.0, 0.5, 1.0]:
    rng = np.random.RandomState(42)
    theta = rng.uniform(0, 2*np.pi, N)
    pos = np.linspace(0, 1, N)
    k_spatial = K0 * (1 + eps * np.cos(2 * np.pi * pos))
    scores = []
    for t in range(T_trans + T_meas):
        coupling = np.zeros(N)
        for i in range(N):
            for j in [(i-1)%N, (i+1)%N]:
                coupling[i] += k_spatial[i] * np.sin(theta[j] - theta[i])
        theta += dt * coupling
        if t >= T_trans:
            bsize = N // 10
            slist = []
            for s in range(10):
                p = theta[s*bsize:(s+1)*bsize]
                z = np.mean(np.exp(1j * p))
                slist.append(abs(z))
            scores.append(max(slist) - min(slist))
    print(f'eps={eps:.1f}: score={np.mean(scores):.3f}')
