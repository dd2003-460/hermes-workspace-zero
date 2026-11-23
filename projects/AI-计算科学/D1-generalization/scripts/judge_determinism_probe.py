"""judge 确定性探针：同输入同 mt 跑 5 次，测 run-to-run 方差。
排除服务器状态变化（全部在同一次 run 内）。
若 5 次输出定性一致 → v1/v2 差异是服务器状态；若不一致 → 模型 temp=0 真不确定。
"""
import json, re, urllib.request, sys
sys.path.insert(0, 'scripts')
import formula_judge as fj

outs = {o['output_id']: o for o in json.load(open('/tmp/formal_judge_outputs.json'))}
SPECS = json.load(open('/tmp/tpub1_extracted.json'))['specs']
V1 = "你是严格的数值判分员。逐检查点判\"对/错\"。规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。只输出 JSON：{\"检查点id\": true/false}。禁止解释。"

def judge(text, spec, mt):
    cps = "\n".join(f"{cp['id']}: gold={cp['gold']} tolerance={cp.get('tolerance',0.02)}" for cp in spec["checkpoints"])
    body = json.dumps({"model": fj.MODEL, "messages":[{"role":"user","content":f"检查点:\n{cps}\n\n模型输出:\n{text[:3000]}\n\n{V1}"}],"temperature":0,"max_tokens":mt}).encode()
    with urllib.request.urlopen(urllib.request.Request(fj.URL, data=body, headers={"Content-Type":"application/json"}), timeout=300) as r:
        d = json.loads(r.read())
    ch = d["choices"][0]
    return ch["message"]["content"], ch.get("finish_reason"), fj.extract_json(ch["message"]["content"]) is not None

# 3 类 case: Q04(之前 flaky), Q01(恢复), Q03(仍失败)
cases = ['T-PUB-1-Q04-r1','T-PUB-1-Q01-r1','T-PUB-1-Q03-r1']
NREP = 5
results = {}
for oid in cases:
    o = outs[oid]; spec = SPECS[o['spec_id']]
    for mt in (500, 2000):
        parses, lens, frs = [], [], []
        for rep in range(NREP):
            raw, fr, ok = judge(o['text'], spec, mt)
            parses.append(ok); lens.append(len(raw)); frs.append(fr)
        key = f"{oid}_mt{mt}"
        results[key] = {"parseable": parses, "n_parse": sum(parses), "lens": lens, "frs": frs}
        print(f"{key}: parse={parses} n={sum(parses)}/{NREP} lens={lens} fr={set(frs)}", flush=True)

json.dump(results, open('/tmp/judge_determinism.json','w'), ensure_ascii=False, indent=1)
print("\n=== 判定 ===")
for k,v in results.items():
    if v["n_parse"] in (0, NREP):
        print(f"{k}: 确定性 (全{'失败' if v['n_parse']==0 else '成功'})")
    else:
        print(f"{k}: **非确定性** {v['n_parse']}/{NREP} (run-to-run 翻转)")
print("saved /tmp/judge_determinism.json")
