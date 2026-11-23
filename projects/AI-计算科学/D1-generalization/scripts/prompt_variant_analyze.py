"""T-PUB-1 正式 prompt 变体实验结果分析（含长度混淆控制）。
D 2026-11-23 指出：格式失败率可能被输出长度混淆（长输出→judge 注意力稀释→更易不可解析）。
本脚本分离两个效应:
  1. prompt 效应: 同一输出跨 3 变体 (长度固定, 干净)
  2. 长度效应: 格式失败率 vs 输出长度 (分桶 + 分位)
判别量: 同一输出内 3 变体是否一起失败
  - 3/3 全挂为主 → 长度驱动 (输出决定失败, 非 prompt)
  - 1/3 或 2/3 混合为主 → prompt 驱动 (同输出不同措辞不同结果)
输入: /tmp/prompt_variant_formal.json + /tmp/formal_judge_outputs.json (取长度)
"""
import json, sys
from collections import defaultdict

def wilson_ci(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k/n; denom = 1+z*z/n
    center = (p+z*z/(2*n))/denom
    half = z*((p*(1-p)/n+z*z/(4*n*n))**0.5)/denom
    return (max(0.0,center-half), min(1.0,center+half))

path = sys.argv[1] if len(sys.argv)>1 else "/tmp/prompt_variant_formal.json"
d = json.load(open(path))
outs = json.load(open('/tmp/formal_judge_outputs.json'))
lens = {o['output_id']: len(o['text']) for o in outs}
variants = list(d['results'].keys())

print(f"judge: {d['judge_family']}  n_outputs={d['n_outputs']}  variants={variants}  calls={d['total_calls']}\n")

# --- 1. 每变体格式失败率 + Wilson CI ---
print("=== 每变体格式失败率 (长度是混杂, 仅描述) ===")
print(f"{'variant':<14}{'n':<6}{'fail':<6}{'rate':<8}{'Wilson95':<20}")
for v in variants:
    vres = d['results'][v]
    n = len(vres); k = sum(1 for r in vres.values() if not r['parseable'])
    lo,hi = wilson_ci(k,n)
    print(f"{v:<14}{n:<6}{k:<6}{k/n:<8.3f}[{lo:.3f},{hi:.3f}]")

# --- 2. 长度分桶: 格式失败率 vs 长度 ---
print("\n=== 格式失败率 vs 输出长度 (长度效应) ===")
buckets = [(0,1000,'<1k'),(1000,3000,'1-3k'),(3000,5000,'3-5k'),(5000,10**9,'>5k')]
print(f"{'bucket':<8}{'n_calls':<9}{'fail':<6}{'rate':<8}{'mean_len':<10}")
for lo_b,hi_b,label in buckets:
    n=k=0; lsum=0
    for v in variants:
        for oid,r in d['results'][v].items():
            if lo_b <= lens.get(oid,0) < hi_b:
                n+=1; lsum+=lens[oid]
                if not r['parseable']: k+=1
    if n: print(f"{label:<8}{n:<9}{k:<6}{k/n:<8.3f}{lsum/n:<10.0f}")

# --- 3. 关键判别: 同一输出内 3 变体失败模式 ---
print("\n=== 同输出内 3 变体失败模式 (长度 vs prompt 判别) ===")
mode_count = defaultdict(int)
mixed_examples = []
for oid in lens:
    fails = [not d['results'][v][oid]['parseable'] for v in variants]
    nfail = sum(fails)
    mode_count[nfail] += 1
    if 0 < nfail < 3:
        mixed_examples.append((oid, lens[oid], {v:(not d['results'][v][oid]['parseable']) for v in variants}))
total_out = len(lens)
print(f"{'0/3 全过':<12}{mode_count[0]:<6}  ({mode_count[0]/total_out:.1%})")
print(f"{'1/3 混合':<12}{mode_count[1]:<6}  ({mode_count[1]/total_out:.1%})  <- prompt 驱动信号")
print(f"{'2/3 混合':<12}{mode_count[2]:<6}  ({mode_count[2]/total_out:.1%})  <- prompt 驱动信号")
print(f"{'3/3 全挂':<12}{mode_count[3]:<6}  ({mode_count[3]/total_out:.1%})  <- 长度驱动信号")
total_fail_outputs = mode_count[1]+mode_count[2]+mode_count[3]
if total_fail_outputs:
    print(f"\n失败输出中: 混合(1/3或2/3)={mode_count[1]+mode_count[2]}/{total_fail_outputs} "
          f"({(mode_count[1]+mode_count[2])/total_fail_outputs:.1%}), 全挂(3/3)={mode_count[3]}/{total_fail_outputs} "
          f"({mode_count[3]/total_fail_outputs:.1%})")
    print("解读: 混合占比高->prompt 驱动; 全挂占比高->长度驱动")
print(f"\n混合示例 (前5):")
for oid,ln,pat in mixed_examples[:5]:
    print(f"  {oid} (len={ln}): {pat}")

# --- 4. 长度-失败相关 (按长度分 5 分位看失败率趋势) ---
print("\n=== 长度-失败相关 (按长度 5 分位) ===")
sorted_ids = sorted(lens, key=lambda x: lens[x])
q = len(sorted_ids)//5
for i in range(5):
    seg = sorted_ids[i*q:(i+1)*q if i<4 else len(sorted_ids)]
    n=k=0
    for oid in seg:
        for v in variants:
            n+=1
            if not d['results'][v][oid]['parseable']: k+=1
    if n: print(f"  Q{i+1} len[{lens[seg[0]]}-{lens[seg[-1]]}]: fail {k}/{n} = {k/n:.3f}")

# --- 5. 翻转率 (只在可解析调用上, 长度同样混杂但翻转是判分准确性维度) ---
print("\n=== 翻转率 (可解析调用, LLM vs 机械) ===")
for v in variants:
    n_cp=n_flip=0
    for oid,r in d['results'][v].items():
        if not r['parseable']: continue
        for cid,m in r['mech'].items():
            l=r['llm'].get(cid)
            if m is None or l is None: continue
            n_cp+=1
            if m!=l: n_flip+=1
    print(f"  {v}: flip {n_flip}/{n_cp} = {(n_flip/n_cp if n_cp else 0):.3f}")
