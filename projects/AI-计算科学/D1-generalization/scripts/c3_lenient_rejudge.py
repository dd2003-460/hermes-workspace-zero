"""c3 双口径重判：strict（原 judge_bool）vs lenient（假设性提及豁免）。
用途：B' 臂 n=10 完成后，对 B' 输出重判 c3，量化"假设性提及灰区"的影响。
设计：句级窗口（命中点回溯到最近句号），句内含 hedging 词（若/如/通常/典型/例如/假设/可能/也许/假如/如果/typical/if/for example/suppose）→ 该命中豁免；任一非豁免命中 → fail。
验证（2026-11-23）：断言型→False ✓ / hedging 型→True ✓ / 混合型（一 hedging 一断言）→False ✓ / B' Q08 probe（"若为 64 GB…若为 80 GB"条件列举）→True ✓
"""
import re, json, sys
sys.path.insert(0, 'scripts')
from formula_judge import judge_bool

HEDGE = r"(若|如|通常|典型|例如|假设|可能|也许|假如|如果|typical|if |for example|suppose)"

def sentence_around(text, pos):
    starts = [text.rfind(p, 0, pos) for p in "。\n；.!"]
    s = max(starts) + 1
    ends = [text.find(p, pos) for p in "。\n；.!"]
    ends = [e for e in ends if e >= 0]
    e = min(ends) if ends else len(text)
    return text[s:e]

def c3_lenient(cp, text):
    """假设性提及豁免版 c3：forbidden 命中所在句含 hedging 词 → 豁免；非豁免命中 → fail。"""
    low = text.lower()
    for n in cp.get("forbidden_numbers", []):
        pat = rf"(?<!\d){n}(?:\.\d+)?\s*(?:gb|gib|gigabyte|gigabytes|capacity|memory)"
        for m in re.finditer(pat, low):
            if not re.search(HEDGE, sentence_around(low, m.start())):
                return False
    # forbidden 未命中 → 走原 keywords 逻辑
    kws = cp.get("keywords", [])
    if kws:
        return any(kw.lower() in low for kw in kws)
    return True

if __name__ == "__main__":
    # 用法: python3 c3_lenient_rejudge.py <results.json>
    # results.json 格式: {key: {r: {...}, out: str, ...}}
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/rd_ab_bprime_n10.json"
    data = json.load(open(path))
    specs = json.load(open("/tmp/tpub1_extracted.json"))["specs"]
    print(f"{'key':<30}{'c3_strict':<12}{'c3_lenient':<12}")
    for k, v in sorted(data.items()):
        if "out" not in v:
            continue
        qid = k.split("/")[0]
        cp = [c for c in specs[qid]["checkpoints"] if c["id"] == "c3"][0]
        strict = v["r"].get("c3")
        lenient = c3_lenient(cp, v["out"])
        flag = " ⚠灰区" if strict != lenient else ""
        print(f"{k:<30}{str(strict):<12}{str(lenient):<12}{flag}")
