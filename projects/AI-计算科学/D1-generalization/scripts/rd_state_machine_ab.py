import json, time, urllib.request, sys
sys.path.insert(0, 'scripts')
from formula_judge import judge_mechanical
URL = "http://127.0.0.1:8787/v1/chat/completions"; MODEL = "qwen3.8-27b-mtp"
data = json.load(open("/tmp/tpub1_extracted.json"))
specs, prompts = data["specs"], data["prompts"]
REMIND = ("[系统检查指令] 在回答前，先检查：回答本问题所需的全部关键数值参数是否都已在题面中明确且一致地给出？"
          "若缺少任一关键参数，或不同来源的参数相互矛盾，你必须明确声明缺什么/冲突在哪、并说明因此无法确定唯一答案，"
          "而不是假设或编造数值。")
rd_qs = ["T-PUB-1-Q08","T-PUB-1-Q09","T-PUB-1-Q10"]
def call(prompt):
    body = json.dumps({"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":4000}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"]
results = {}
for qid in rd_qs:
    for cond, p in [("A_baseline", prompts[qid]), ("B_remind", REMIND + "\n\n" + prompts[qid])]:
        t0=time.time()
        out = call(p)
        r = judge_mechanical(specs[qid], out)
        results[f"{qid}/{cond}"] = {"r": r, "wall": round(time.time()-t0,1), "out": out}
        print(f"{qid} {cond}: c1={r.get('c1')} c3={r.get('c3')} [{results[f'{qid}/{cond}']['wall']}s]")
        time.sleep(0.5)
json.dump(results, open("/tmp/rd_ab_v2.json","w"), ensure_ascii=False, indent=1)
print("\n=== A/B 对比（修好 judge 后）===")
for qid in rd_qs:
    a, b = results[f"{qid}/A_baseline"]["r"], results[f"{qid}/B_remind"]["r"]
    dc1 = int(bool(b.get("c1"))) - int(bool(a.get("c1")))
    print(f"{qid}: A c1={a.get('c1')}/c3={a.get('c3')}  ->  B c1={b.get('c1')}/c3={b.get('c3')}  Δc1={dc1:+d}")
print("written /tmp/rd_ab_v2.json")
