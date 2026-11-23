#!/usr/bin/env python3
"""P2 · formula_judge 对比脚本（机械 judge vs LLM judge）
# origin: ai · 2026-11-23 · 口径见 research/stats-protocol-20261123.md

用法:
  python formula_judge.py --spec spec.json --outputs outputs.jsonl [--llm-judge] [--out receipt.json]

spec.json 格式（与 T-PUB-1 任务书一致）:
  {"id":"Q01","domain":"gpu","type":"full",
   "checkpoints":[{"id":"c1","kind":"calc","gold":"<sympy expr>","tolerance":0.02},
                  {"id":"c2","kind":"fact","gold":"<value>","source":"<url>"},
                  {"id":"c3","kind":"bool","gold":1}]}

outputs.jsonl 每行: {"output_id":"o1","model":"qwen3.8-27b-mtp","text":"<模型原始输出>"}

判分:
  calc: SymPy 精确值 + tolerance（相对误差）
  fact: 模型输出含 gold 数值（±tolerance）
  bool: 模型输出含 0/1 判定（gold=1 时输出"是/1/true"类）
  reward_only_feedback: 逐检查点 对/错 串（不给正确值）

LLM judge（--llm-judge）: 调 8787 27b，prompt 版本化（JUDGE_PROMPT_VERSION）
统计: 一致率/翻转率（按检查点）+ Wilson 95% CI（按题聚类 bootstrap）
"""
import json, re, sys, argparse, urllib.request, time
from sympy import sympify, N

URL = "http://127.0.0.1:8787/v1/chat/completions"
MODEL = "qwen3.8-27b-mtp"
JUDGE_PROMPT_VERSION = "v2-20261123"   # P5 口径: judge 族标注。v1→v2: 整数检查点(tol=0)必须精确匹配, 差1=错 (v1 把 max_batch=240 判对, 边界case测试暴露)

# ---------- 机械 judge ----------
def eval_gold(gold):
    """gold 是 sympy 表达式字符串或数值"""
    try:
        return float(N(sympify(gold), 30))
    except Exception:
        try:
            return float(gold)
        except Exception:
            return None

def extract_json(text):
    """取最后一个完整 JSON 对象（防 thinking 污染）"""
    i, j = text.rfind("{"), text.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(text[i:j+1])
        except Exception:
            pass
    return None

def judge_bool(cp, text):
    """bool 检查点判分（spec 驱动，Lead 核 gold 时补字段）。
    字段（可组合）：
    - keywords: [str] — 任一出现（小写）→ pass
    - forbidden_numbers: [num] — 任一以容量/数值语境出现 → fail
    - forbidden_patterns: [regex] — 任一命中 → fail
    优先级：forbidden 先判（命中即 fail），再 keywords（命中即 pass），都不中 → fail。
    无判分字段时回退旧行为（gold=1 搜泛词）。
    """
    low = text.lower()
    has_fields = any(k in cp for k in ("keywords", "forbidden_numbers", "forbidden_patterns"))
    if not has_fields:
        g = int(cp.get("gold", 1))
        if g == 1:
            return bool(re.search(r"\b(yes|true|1|是|识别|不足|缺少|missing|insufficient)\b", text, re.I))
        return True
    for n in cp.get("forbidden_numbers", []):
        pat = rf"(?<!\d){n}(?:\.\d+)?\s*(?:gb|gib|gigabyte|gigabytes|capacity|memory)"
        if re.search(pat, low):
            return False
    for pat in cp.get("forbidden_patterns", []):
        if re.search(pat, low):
            return False
    kws = cp.get("keywords", [])
    if kws:
        # 正向检查点：出现任一关键词即 pass
        return any(kw.lower() in low for kw in kws)
    # 无 keywords = 纯"通过即缺席"检查点（gold=1, pass=没出现禁值）：禁值未命中即 pass
    return True


def _clean_latex_sci(text):
    """LaTeX 科学计数法 → e 形式，让 NUM_RE 能抓到。
    '1.551 \\times 10^{-5}' → '1.551e-5'；'50.625 \\times 10^9' → '50.625e9'。
    只动 \\times 10^{±n} 结构，普通数字不受影响。"""
    return re.sub(r"(\d[\d,]*\.?\d*)\s*\\times\s*10\^?\{?(-?\d+)\}?",
                  lambda m: f"{m.group(1).replace(',', '')}e{m.group(2)}", text)

def _find_gold_in_text(text, gv, tol):
    """在 markdown 文本里找 gold 值。tol=0 整数精确匹配；tol>0 相对误差 < tol。
    优先在 'Answer:' 行找，找不到再全文找。
    支持科学计数法（1.551e-5 及 LaTeX 的 1.551\\times 10^{-5}）和 SI 单位换算
    （模型答 57.77 GB 而 gold 是 bytes：对每个候选值同时试 ×1e9/×1e12 等常用前缀，
    tolerance 足够紧不会误判）。"""
    if gv is None or not text:
        return False
    text = _clean_latex_sci(text)
    # 科学计数法 + 普通数字（含千分位逗号）
    NUM_RE = r"-?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?"
    SCALES = [1.0, 1e3, 1e6, 1e9, 1e12]  # 无换算 / k / M / G / T
    def _match(s):
        for m in re.finditer(NUM_RE, s):
            try:
                v = float(m.group().replace(",", ""))
            except Exception:
                continue
            for sc in SCALES:
                vv = v * sc
                if tol == 0:
                    if vv == gv and float(gv).is_integer():
                        return True
                else:
                    if gv != 0 and abs(vv - gv) / abs(gv) < tol:
                        return True
        return False
    # 优先 Answer 行
    ans_lines = [ln for ln in text.split("\n") if re.search(r"answer", ln, re.I)]
    if ans_lines and _match(" ".join(ans_lines)):
        return True
    return _match(text)


def judge_mechanical(spec, text):
    """返回 {checkpoint_id: bool}"""
    data = extract_json(text)
    results = {}
    for cp in spec["checkpoints"]:
        cid, kind, gold = cp["id"], cp["kind"], cp["gold"]
        tol = cp.get("tolerance", 0.02)
        if kind == "calc":
            gv = eval_gold(gold)
            mv = data.get(cid) if data else None
            if isinstance(mv, (int, float)):
                if tol == 0:
                    results[cid] = float(mv) == gv  # 整数检查点：精确匹配（差1=错）
                else:
                    results[cid] = gv is not None and abs(float(mv) - gv) / abs(gv) < tol
            elif isinstance(mv, str):
                try:
                    v = float(mv.strip().rstrip(",").replace(",", ""))
                    # 单位换算：模型答 "57.77 GB" 而 gold 是 bytes → 试 SI 前缀
                    matched = (v == gv) if tol == 0 else (gv is not None and abs(v - gv) / abs(gv) < tol)
                    if not matched:
                        for sc in (1e3, 1e6, 1e9, 1e12):
                            vv = v * sc
                            if tol == 0:
                                matched = (vv == gv)
                            else:
                                matched = gv is not None and abs(vv - gv) / abs(gv) < tol
                            if matched:
                                break
                    results[cid] = matched
                except Exception:
                    results[cid] = False
            else:
                # markdown 回退：真实模型输出常是 markdown 不是 JSON。
                # 优先在 "Answer:" 行找 gold±tol，找不到再全文找（与 fact 分支同逻辑）。
                results[cid] = _find_gold_in_text(text, gv, tol)
        elif kind == "fact":
            gv = eval_gold(gold)
            # fact: 模型输出里出现该数值（±tol）。tol=0 精确匹配（0<0 恒 False，需单独分支）。
            if gv is None or not text:
                results[cid] = False
            else:
                found = False
                text = _clean_latex_sci(text)
                NUM_RE = r"-?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?"
                SCALES = [1.0, 1e3, 1e6, 1e9, 1e12]  # 同 _find_gold_in_text：单位换算
                for m in re.finditer(NUM_RE, text):
                    try:
                        v = float(m.group().replace(",", ""))
                    except Exception:
                        continue
                    for sc in SCALES:
                        vv = v * sc
                        if tol == 0:
                            if vv == gv:
                                found = True
                                break
                        else:
                            if gv != 0 and abs(vv - gv) / abs(gv) < tol:
                                found = True
                                break
                    if found:
                        break
                results[cid] = found
        elif kind == "bool":
            results[cid] = judge_bool(cp, text)
        else:
            results[cid] = False
    return results

def reward_only(spec, mech_res):
    """reward-only 反馈串（不给正确值）"""
    return ", ".join(f"{cid}={'对' if v else '错'}" for cid, v in mech_res.items())

# ---------- LLM judge ----------
JUDGE_PROMPT = """你是严格的数值判分员。逐检查点判"对/错"。
规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。
只输出 JSON：{"检查点id": true/false}。禁止解释。"""

def judge_llm(spec, text, max_tokens=500):
    cps = "\n".join(f"{cp['id']}: gold={cp['gold']} tolerance={cp.get('tolerance', 0.02)}" for cp in spec["checkpoints"])
    body = json.dumps({"model": MODEL,
        "messages": [{"role": "user", "content": f"检查点:\n{cps}\n\n模型输出:\n{text[:3000]}\n\n{JUDGE_PROMPT}"}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
        out = d["choices"][0]["message"]["content"]
        data = extract_json(out)
        return {cp["id"]: bool(data.get(cp["id"], False)) for cp in spec["checkpoints"]}
    except Exception as e:
        return {cp["id"]: None for cp in spec["checkpoints"]}  # None = 判分失败

# ---------- 统计（P5 口径）----------
def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def stats(mech, llm):
    """mech/llm: {output_id: {cp_id: bool}}  按检查点算一致率 + 按题聚类 bootstrap CI"""
    agree, total = 0, 0
    flip_mech_correct, flip_llm_correct = 0, 0
    for oid in mech:
        llm_d = llm or {}
        for cid in mech[oid]:
            m, l = mech[oid].get(cid), llm_d.get(oid, {}).get(cid)
            if m is None or l is None:
                continue
            total += 1
            if m == l:
                agree += 1
            elif m and not l:
                flip_mech_correct += 1
            elif l and not m:
                flip_llm_correct += 1
    out = {"n_checkpoints": total,
           "agreement": agree/total if total else None,
           "agreement_ci_wilson": wilson_ci(agree, total) if total else None,
           "flip_mech_correct_llm_wrong": flip_mech_correct,
           "flip_llm_correct_mech_wrong": flip_llm_correct}
    return out

# ---------- 冒烟：内置原型题（无外部 spec 时）----------
BUILTIN_SPEC = {
    "id": "PROTO-10B-THROUGHPUT", "domain": "gpu", "type": "full",
    "checkpoints": [
        {"id": "mem_BF16_GB", "kind": "calc", "gold": "2*sqrt(5)", "tolerance": 0.02},
        {"id": "mem_FP8_GB", "kind": "calc", "gold": "sqrt(5)", "tolerance": 0.02},
        {"id": "tps_BF16", "kind": "calc", "gold": "3350/(2*sqrt(5))", "tolerance": 0.02},
        {"id": "tps_FP8", "kind": "calc", "gold": "3350/sqrt(5)", "tolerance": 0.02},
        {"id": "ratio_FP8_over_BF16", "kind": "calc", "gold": "2", "tolerance": 0.02},
    ],
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--outputs")
    ap.add_argument("--llm-judge", action="store_true")
    ap.add_argument("--out", default="judge-receipt.json")
    a = ap.parse_args()
    spec = json.load(open(a.spec)) if a.spec else BUILTIN_SPEC
    outputs = [json.loads(l) for l in open(a.outputs)] if a.outputs else []
    mech, llm = {}, {}
    for o in outputs:
        r = judge_mechanical(spec, o["text"])
        mech[o["output_id"]] = r
        if a.llm_judge:
            llm[o["output_id"]] = judge_llm(spec, o["text"])
    receipt = {
        "judge_family": f"formula_judge v0.1 (SymPy, tol=spec) vs {MODEL} {JUDGE_PROMPT_VERSION}" if a.llm_judge else "formula_judge v0.1 only",
        "spec_id": spec["id"],
        "n_outputs": len(outputs),
        "mechanical": {k: v for k, v in mech.items()},
        "reward_only_feedback": {k: reward_only(spec, v) for k, v in mech.items()},
        "llm": llm or None,
        "stats": stats(mech, llm) if a.llm_judge else None,
    }
    json.dump(receipt, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"spec": spec["id"], "n": len(outputs),
                      "pass_rate": sum(all(v.values()) for v in mech.values())/len(mech) if mech else None,
                      "stats": receipt["stats"]}, ensure_ascii=False))
