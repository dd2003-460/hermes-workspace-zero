import json, time, urllib.request, sys
sys.path.insert(0, 'scripts')
from formula_judge import judge_mechanical
URL = "http://127.0.0.1:8787/v1/chat/completions"; MODEL = "qwen3.8-27b-mtp"
data = json.load(open("/tmp/tpub1_extracted.json"))
specs, prompts = data["specs"], data["prompts"]
REMIND = ("[系统检查指令] 在回答前，先检查：回答本问题所需的全部关键数值参数是否都已在题面中明确且一致地给出？"
          "若缺少任一关键参数，或不同来源的参数相互矛盾，你必须明确声明缺什么/冲突在哪、并说明因此无法确定唯一答案，"
          "而不是假设或编造数值。")
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
    for cond, p in [("A_baseline", prompts[qid]), ("B_remind", REMIND + "\n\n" + prompts[qid])]:
        c1s, c3s = [], []
        for rep in range(1, N+1):
            key = f"{qid}/{cond}/rep{rep}"
            t0 = time.time()
            try:
                out = call(p)
                r = judge_mechanical(specs[qid], out)
                c1, c3 = bool(r.get("c1")), bool(r.get("c3"))
                results[key] = {"r": r, "wall": round(time.time()-t0, 1), "out_len": len(out), "out": out}
                print(f"{qid} {cond} rep{rep}: c1={c1} c3={c3} [{results[key]['wall']}s]", flush=True)
            except Exception as e:
                results[key] = {"error": str(e)}
                print(f"{qid} {cond} rep{rep}: ERROR {e}", flush=True)
            c1s.append(c1); c3s.append(c3)
            time.sleep(0.5)
        lo1, hi1 = wilson(sum(c1s), N); lo3, hi3 = wilson(sum(c3s), N)
        print(f"  >> {qid} {cond}: c1 {sum(c1s)}/{N} CI95[{lo1:.2f},{hi1:.2f}]  c3 {sum(c3s)}/{N} CI95[{lo3:.2f},{hi3:.2f}]", flush=True)

# 汇总
print("\n=== n=10 A/B 汇总 ===", flush=True)
for qid in rd_qs:
    for metric in ("c1", "c3"):
        ka = sum(1 for rep in range(1, N+1) if results.get(f"{qid}/A_baseline/rep{rep}", {}).get("r", {}).get(metric))
        kb = sum(1 for rep in range(1, N+1) if results.get(f"{qid}/B_remind/rep{rep}", {}).get("r", {}).get(metric))
        la, ha = wilson(ka, N); lb, hb = wilson(kb, N)
        print(f"{qid} {metric}: A {ka}/{N} [{la:.2f},{ha:.2f}]  B {kb}/{N} [{lb:.2f},{hb:.2f}]", flush=True)
json.dump(results, open("/tmp/rd_ab_n10.json", "w"), ensure_ascii=False, indent=1)
print("written /tmp/rd_ab_n10.json", flush=True)
