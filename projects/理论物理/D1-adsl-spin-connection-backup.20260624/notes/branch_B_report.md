# Branch B Report: Dual connection transformation

> Date: 2026-04-01 09:33

## Finding

论文的 D_ω 用的是对偶联络 ω^a（dual），脚本直接使用 ω^a 是正确的。
ω^a_b = ε^{abc}ω_c 给出的"标准联络"与从 ω_{bc} = (1/2)ε_{bcd}ω^d 反推的不同——
说明两套表示不等价，但论文明确使用对偶表示，所以脚本的做法无误。

## Conclusion

Branch B 未发现新的 bug。对偶联络不是问题来源。
