"""T-PUB-1 核心实验正式跑：LLM-judge vs 机械 judge 的 prompt 变体敏感性 (n≥100)。
pilot (judge-boundary-findings §4) 只有 n=24, CI 太宽。本脚本扩到 67 真实输出 × 3 prompt 变体 = 201 次 LLM judge 调用。
两个独立维度分开报 (pilot 教训: 混了会得出错误结论):
  1. 判分准确性: 翻转率 (LLM 与机械 judge 在可解析调用上的分歧)
  2. 格式可靠性: LLM judge 格式失败率 (输出不可解析/键名错/单布尔广播) vs 机械 judge 0%
数据源: /tmp/formal_judge_outputs.json (27b-outputs Q01-07 各1 + rd-ab Q08-10 各10, 共67)
spec: /tmp/tpub1_extracted.json (10 题 47 检查点)
"""
import json, sys, time, urllib.request
sys.path.insert(0, 'scripts')
import formula_judge as fj

URL = fj.URL
MODEL = fj.MODEL
OUTS = json.load(open('/tmp/formal_judge_outputs.json'))
SPECS = json.load(open('/tmp/tpub1_extracted.json'))['specs']

# 3 个 prompt 变体 (措辞不同, 判分规则语义相同)
VARIANTS = {
    "V1_strict": "你是严格的数值判分员。逐检查点判\"对/错\"。规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。只输出 JSON：{\"检查点id\": true/false}。禁止解释。",
    "V2_loose":  "请判断模型输出中每个检查点是否正确。容差 2% 内的数值算对，整数检查点需精确匹配。以 JSON 形式返回每个检查点 id 对应的布尔值。",
    "V3_engineer": "You are a strict numeric grader. For each checkpoint, decide true/false. Tolerance 0.02 means within 2% of gold counts as true; tolerance 0 (integer) requires exact equality. Output ONLY a JSON object mapping checkpoint id to boolean. No explanation.",
}

def judge_llm_variant(spec, text, prompt, max_tokens=500):
    """返回 (parseable: bool, result: {cp_id: bool|None})。parseable=False = 格式失败。"""
    cps = "\n".join(f"{cp['id']}: gold={cp['gold']} tolerance={cp.get('tolerance', 0.02)}" for cp in spec["checkpoints"])
    body = json.dumps({"model": MODEL,
        "messages": [{"role": "user", "content": f"检查点:\n{cps}\n\n模型输出:\n{text[:3000]}\n\n{prompt}"}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        out = d["choices"][0]["message"]["content"]
        data = fj.extract_json(out)
        if data is None:
            return False, {cp["id"]: None for cp in spec["checkpoints"]}
        # 格式合规检查: 必须包含所有 checkpoint id, 值必须是 bool (不能单布尔广播)
        result = {}
        for cp in spec["checkpoints"]:
            v = data.get(cp["id"])
            if isinstance(v, bool):
                result[cp["id"]] = v
            else:
                # 键缺失或非 bool → 格式失败
                return False, {c["id"]: None for c in spec["checkpoints"]}
        return True, result
    except Exception:
        return False, {cp["id"]: None for cp in spec["checkpoints"]}

def main():
    t0 = time.time()
    results = {}  # variant -> {output_id: {parseable, llm, mech}}
    total_calls = len(OUTS) * len(VARIANTS)
    done = 0
    for vname, vprompt in VARIANTS.items():
        results[vname] = {}
        for o in OUTS:
            spec = SPECS[o["spec_id"]]
            mech = fj.judge_mechanical(spec, o["text"])
            parseable, llm = judge_llm_variant(spec, o["text"], vprompt)
            results[vname][o["output_id"]] = {"parseable": parseable, "llm": llm, "mech": mech}
            done += 1
            if done % 10 == 0:
                print(f"[{done}/{total_calls}] {vname} {o['output_id']} parseable={parseable}", flush=True)
    # 统计
    summary = {}
    for vname, vres in results.items():
        n_calls = len(vres)
        n_format_fail = sum(1 for r in vres.values() if not r["parseable"])
        # 翻转率: 只在可解析调用上算
        n_cp, n_flip = 0, 0
        for r in vres.values():
            if not r["parseable"]:
                continue
            for cid, m in r["mech"].items():
                l = r["llm"].get(cid)
                if m is None or l is None:
                    continue
                n_cp += 1
                if m != l:
                    n_flip += 1
        summary[vname] = {
            "n_calls": n_calls,
            "format_fail": n_format_fail,
            "format_fail_rate": n_format_fail / n_calls if n_calls else None,
            "n_checkpoints_parsed": n_cp,
            "flip": n_flip,
            "flip_rate": n_flip / n_cp if n_cp else None,
        }
    out = {"judge_family": f"{MODEL} {fj.JUDGE_PROMPT_VERSION} variants",
           "n_outputs": len(OUTS), "n_variants": len(VARIANTS),
           "total_calls": total_calls, "elapsed_s": round(time.time() - t0, 1),
           "summary": summary, "results": results}
    json.dump(out, open('/tmp/prompt_variant_formal.json', 'w'), ensure_ascii=False, indent=1)
    print("\n=== SUMMARY ===")
    for vname, s in summary.items():
        print(f"{vname}: format_fail={s['format_fail']}/{s['n_calls']} ({s['format_fail_rate']:.3f})  flip={s['flip']}/{s['n_checkpoints_parsed']} ({s['flip_rate']:.3f})")

if __name__ == "__main__":
    main()
