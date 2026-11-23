"""截断机制探针 v2：保存 finish_reason + raw 尾部，区分
  (A) JSON 被截断 (finish_reason=length, 尾部=半个JSON)
  (B) 推理链耗尽 token (finish_reason=length, 尾部=推理文本, JSON 根本没开始)
  (C) 模型主动拒绝/格式错 (finish_reason=stop, 但 JSON 不可解析)
"""
import json, re, urllib.request, sys
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
        d = json.loads(r.read())
    ch = d["choices"][0]
    return ch["message"]["content"], ch.get("finish_reason"), fj.extract_json(ch["message"]["content"]) is not None

rows = []
for oid in fail_ids:
    o = outs.get(oid)
    if not o: continue
    spec = SPECS[o['spec_id']]
    for mt in (500, 2000):
        raw, fr, ok = judge(o['text'], spec, mt)
        tail = raw[-120:].replace('\n','\\n')
        rows.append({"oid": oid, "mt": mt, "finish_reason": fr, "parseable": ok, "raw_len": len(raw), "tail": tail})
        print(f"{oid} mt={mt} fr={fr} parse={ok} len={len(raw)}\n  tail: {tail}\n", flush=True)

json.dump(rows, open('/tmp/mt_probe2.json','w'), ensure_ascii=False, indent=1)
print("saved /tmp/mt_probe2.json")
