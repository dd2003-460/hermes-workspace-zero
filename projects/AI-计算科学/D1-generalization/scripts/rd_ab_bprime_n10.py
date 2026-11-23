import json, time, urllib.request, sys
sys.path.insert(0, 'scripts')
from formula_judge import judge_mechanical
URL = "http://127.0.0.1:8787/v1/chat/completions"; MODEL = "qwen3.8-27b-mtp"
data = json.load(open("/tmp/tpub1_extracted.json"))
specs, prompts = data["specs"], data["prompts"]
# B' = B_remind + 部分量修复句（针对 n=10 发现的 Q09 c4 副作用：模型声明缺口后放弃可算部分量）
REMIND_B = ("[系统检查指令] 在回答前，先检查：回答本问题所需的全部关键数值参数是否都已在题面中明确且一致地给出？"
            "若缺少任一关键参数，或不同来源的参数相互矛盾，你必须明确声明缺什么/冲突在哪、并说明因此无法确定唯一答案，"
            "而不是假设或编造数值。"
            "注意：对题面已给参数可以独立计算的部分量（不依赖缺失参数的计算），仍应给出具体数值，不要因为整体无法确定就跳过这些可算部分。")
rd_qs = ["T-PUB-1-Q08", "T-PUB-1-Q09", "T-PUB-1-Q10"]
N = 10
def call(prompt):
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": 4000}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"]

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * (p*(1-p)/n + z*z/(4*n*n))**0.5 / denom
    return (max(0.0, center-half), min(1.0, center+half))

results = {}
for qid in rd_qs:
    p = REMIND_B + "\n\n" + prompts[qid]
    for rep in range(1, N+1):
        key = f"{qid}/Bp_remind/rep{rep}"
        t0 = time.time()
        try:
            out = call(p)
            r = judge_mechanical(specs[qid], out)
            results[key] = {"r": r, "wall": round(time.time()-t0, 1), "out_len": len(out), "out": out}
            print(f"{qid} Bp rep{rep}: c1={r.get('c1')} c3={r.get('c3')} c4={r.get('c4')} [{results[key]['wall']}s] len={len(out)}", flush=True)
        except Exception as e:
            results[key] = {"error": str(e)}
            print(f"{qid} Bp rep{rep}: ERROR {e}", flush=True)
        time.sleep(0.5)

print("\n=== B' 汇总 (对照: A c1 10/30 c3 25/30 c4 30/30; B c1 30/30 c3 30/30 c4 21/30) ===", flush=True)
for qid in rd_qs:
    for metric in ("c1", "c3", "c4"):
        k = sum(1 for rep in range(1, N+1) if results.get(f"{qid}/Bp_remind/rep{rep}", {}).get("r", {}).get(metric))
        lo, hi = wilson(k, N)
        print(f"{qid} {metric}: Bp {k}/{N} [{lo:.2f},{hi:.2f}]", flush=True)
json.dump(results, open("/tmp/rd_ab_bprime_n10.json", "w"), ensure_ascii=False, indent=1)
print("written /tmp/rd_ab_bprime_n10.json", flush=True)
