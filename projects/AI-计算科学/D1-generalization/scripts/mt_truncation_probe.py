"""max_tokens 截断探针：对 V1_strict 失败 case 用 mt500 vs mt2000 重判。
目的：区分格式失败的驱动因素——截断(长度→推理链→撞max_tokens) vs 指令遵循(模型不肯只输出JSON)。
恢复率高→截断驱动; 恢复率低→指令遵循问题。
"""
import json, sys, re, time, urllib.request
sys.path.insert(0, 'scripts')
import formula_judge as fj

log = open('/tmp/prompt_variant_formal.log').read()
pat = re.compile(r'\[\d+/201\] V1_strict (\S+) parseable=False')
fail_ids = list(dict.fromkeys(pat.findall(log)))[:6]
outs = {o['output_id']: o for o in json.load(open('/tmp/formal_judge_outputs.json'))}
SPECS = json.load(open('/tmp/tpub1_extracted.json'))['specs']
V1 = "你是严格的数值判分员。逐检查点判\"对/错\"。规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。只输出 JSON：{\"检查点id\": true/false}。禁止解释。"

def judge(text, spec, mt):
    cps = "\n".join(f"{cp['id']}: gold={cp['gold']} tolerance={cp.get('tolerance',0.02)}" for cp in spec["checkpoints"])
    body = json.dumps({"model": fj.MODEL, "messages":[{"role":"user","content":f"检查点:\n{cps}\n\n模型输出:\n{text[:3000]}\n\n{V1}"}],"temperature":0,"max_tokens":mt}).encode()
    with urllib.request.urlopen(urllib.request.Request(fj.URL, data=body, headers={"Content-Type":"application/json"}), timeout=300) as r:
        out = json.loads(r.read())["choices"][0]["message"]["content"]
    return fj.extract_json(out) is not None, len(out)

print(f"{'oid':<34}{'out_len':<8}{'mt500':<7}{'mt2000':<8}{'raw_len':<8}", flush=True)
n_flip = 0
rows = []
for oid in fail_ids:
    o = outs.get(oid)
    if not o: continue
    spec = SPECS[o['spec_id']]
    ok500, l500 = judge(o['text'], spec, 500)
    ok2000, l2000 = judge(o['text'], spec, 2000)
    if not ok500 and ok2000: n_flip += 1
    rows.append((oid, len(o['text']), ok500, ok2000, l2000))
    print(f"{oid:<34}{len(o['text']):<8}{str(ok500):<7}{str(ok2000):<8}{l2000:<8}", flush=True)
print(f"\nmt500失败→mt2000恢复: {n_flip}/{len(rows)}", flush=True)
print("解读: 恢复率高→截断驱动; 恢复率低→指令遵循问题", flush=True)
