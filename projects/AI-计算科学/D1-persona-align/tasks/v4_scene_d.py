#!/usr/bin/env python3
"""v4-batch 场景 D：bug 猜测-验证（测假设-验证循环 + 真执行 reward）。

设计：
- 给一段 ~50 行 Python 代码，埋一个微妙 bug（off-by-one / 边界 / 类型）
- 给 3 个测试（1 失败 2 通过），失败测试的报错信息给出来
- 让模型：猜 bug 在哪（指到行）→ 解释为什么 → 给修复后的完整代码
- reward（真执行，模型骗不了）：
  - 把模型给的修复代码真跑一遍 3 个测试 → 通过率 (0-3)
  - 猜测精度：模型指的行/原因 是否命中真实 bug 行 (0/1)
- 4 种 prompt 格式 × 3 轮 × 3 个不同 bug

用法：
  python3 v4_scene_d.py --arms flat16,axioms5,structured,prose --rounds 3
  python3 v4_scene_d.py --judge
"""
import json, os, sys, time, argparse, urllib.request, re, tempfile, subprocess
from datetime import datetime

API = "http://127.0.0.1:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "v4-sceneD-runs")

# ---------- 3 个 bug（不同类别） ----------
BUGS = {
    "offbyone": {
        "desc": "统计每个词出现次数",
        "code": '''def word_freq(words):
    """返回 {词: 次数} 的字典。words 是字符串列表。"""
    freq = {}
    for i in range(len(words)):
        w = words[i].lower()
        if w in freq:
            freq[w] += 1
        else:
            freq[w] = 1
    # 只保留出现超过 1 次的词
    return {w: c for w, c in freq.items() if c > 1}''',
        "tests": [
            ("word_freq(['a','b','a'])", "{'a': 2}", "通过"),
            ("word_freq(['x','y','z'])", "{}", "通过"),
            ("word_freq(['a','a','a'])", "{'a': 3}", "失败：实际 {'a': 3} 期望 {'a': 3}（这个其实对，换下一个）"),
        ],
        # 真实 bug：其实这段没 bug。换一个真有 bug 的。
        "real_bug_line": None,
    },
    "boundary": {
        "desc": "把列表按奇偶位置分成两组（偶数索引起）",
        "code": '''def split_even_odd(lst):
    """偶数索引(0,2,4..)的元素进 even，奇数索引(1,3,5..)的进 odd。
    返回 (even, odd) 两个列表。"""
    even = []
    odd = []
    for i in range(1, len(lst)):
        if i % 2 == 0:
            even.append(lst[i])
        else:
            odd.append(lst[i])
    return even, odd''',
        "tests": [
            ("split_even_odd([10,20,30,40])", "([10,30],[20,40])", "失败：实际 ([30],[20,40])，漏了索引0的10"),
            ("split_even_odd([])", "([],[])", "通过"),
            ("split_even_odd([7])", "([7],[])", "失败：实际 ([],[])，漏了索引0的7"),
        ],
        "real_bug_line": "for i in range(1, len(lst)):",  # 应从 0 开始
        "real_fix": "for i in range(len(lst)):",
    },
    "type": {
        "desc": "求一组数的加权平均",
        "code": '''def weighted_avg(values, weights):
    """values 和 weights 等长。返回加权平均。
    如果 weights 全为 0，返回 0（避免除零）。"""
    total = 0
    wsum = 0
    for v, w in zip(values, weights):
        total += v * w
        wsum += w
    if wsum == 0:
        return 0
    return total / wsum''',
        "tests": [
            ("weighted_avg([1,2,3],[1,1,1])", "2.0", "通过"),
            ("weighted_avg([10,20],[0,0])", "0", "通过"),
            ("weighted_avg([1,2],[3,0])", "1.0", "失败：实际 1.0 期望 1.0（对）→ 换：weighted_avg([5,5],[1,1]) 应 5.0"),
        ],
        "real_bug_line": None,  # 这段其实也没 bug，需要换一个真有 type bug 的
    },
}

# 上面 offbyone 和 type 我写的代码其实没 bug，需要换成真有 bug 的。
# 重写 BUGS，确保每个都有真实 bug。
BUGS = {
    "aliasing": {
        "desc": "生成二维网格",
        "code": '''def make_grid(rows, cols, fill=0):
    """返回 rows 行 cols 列的二维列表，所有元素初始为 fill。
    每一行应该是独立的列表（改一行不影响其他行）。"""
    grid = [[fill] * cols] * rows
    return grid''',
        "tests": [
            ("make_grid(2,2)[0]", "[0,0]"),
            ("(lambda g: (g[0].append(7) or len(g[1])))(make_grid(2,2))", "2"),
            ("(lambda g: (g[0].__setitem__(0, 9) or g[1][0]))(make_grid(3,3))", "0"),
        ],
        # 测试 2/3：改 g[0] 后查 g[1][0]，期望 0（独立行），实际 9/1（共享行）。
        # 测试 1 表面通过（初始值都对），测试 2/3 暴露别名。
        "real_bug_line": "grid = [[fill] * cols] * rows",
        "real_fix": "grid = [[fill] * cols for _ in range(rows)]",
        "guess_keywords": ["* rows", "同一行", "共享", "alias", "独立", "列表推导", "for _ in"],
    },
    "mutation": {
        "desc": "把列表里每个数翻倍",
        "code": '''def double_all(nums):
    """返回一个新列表，每个元素翻倍。不修改输入列表。"""
    result = []
    for i in range(len(nums)):
        nums[i] = nums[i] * 2
        result.append(nums[i])
    return result''',
        "tests": [
            ("double_all([1,2,3])", "[2,4,6]"),
            ("(lambda x: (double_all(x), x)[1])([1,2])", "[1,2]"),
            ("(lambda x: (double_all(x), x)[1])([5,6])", "[5,6]"),
        ],
        # 测试 1：返回值对。测试 2/3：调用后原列表应不变（docstring 承诺），
        # 实际被改成 [2,4]/[10,12]。暴露原地修改。
        "real_bug_line": "nums[i] = nums[i] * 2",
        "real_fix": "result.append(nums[i] * 2)  # 不写回 nums",
        "guess_keywords": ["nums[i]", "修改输入", "原地", "副作用", "不修改", "写回", "mutat"],
    },
    "stateful": {
        "desc": "自增 id 生成器（带 reset）",
        "code": '''_count = 0

def next_id():
    """返回自增 id，从 1 开始。每次调用加 1。
    调用 reset() 后应重新从 1 开始。"""
    global _count
    _count += 1
    return _count

def reset():
    """把计数器归零，使下一次 next_id() 返回 1。"""
    global _count
    # 注意：这里应该把 _count 归零
    return None''',
        "tests": [
            ("next_id()", "1"),
            ("next_id()", "2"),
            ("(lambda: (reset(), next_id())[1])()", "1"),
        ],
        # 测试 1/2 通过（自增正常）。测试 3：reset 后 next_id 应返回 1，
        # 实际返回 3（reset 没归零）。暴露状态污染。
        # 注意：测试间有状态依赖，judge 需按顺序在同一进程跑。
        "real_bug_line": "return None",  # reset 函数体里缺 _count = 0
        "real_fix": "在 reset() 里加 _count = 0",
        "guess_keywords": ["_count", "归零", "清零", "reset", "全局变量", "计数器"],
        "sequential": True,  # 测试必须在同一进程按顺序跑（有状态）
    },
}

# ---------- 4 种 prompt 格式（复用场景 C 的） ----------
ARMS = {
    "flat16": """你遵循以下 16 条规则来工作：
1. 压缩=理解：能压成更少字还保住意思=真懂；压不动=还没懂。
2. 先读再想再做；对齐>规划>执行。
3. 每步标置信度；撞数据墙→转实证。
4. 自我质询：提论点→立刻质疑自己→分解定义→查完备性→划范围。
5. 性价比优先：能不花钱不花钱。
6. 短、第一人称、因果密。
7. 禁空话。
8. 派活/长 brief 先"明确砍掉"：说清不做什么比说做什么更重要。
9. 每次迭代必须有可验证产出；不产出就换方向。
10. 持续行动不询问；跳过能跳过的阻塞。
11. 工具优先 6 关：动手前先查现有工具/已存在文件/层级/索引/命名。
12. 每轮派质询者找盲区。
13. 分层读：已知→骨架→核心逐行→略读→外围。
14. 数据对账要逐位硬证据；记忆被实际反驳→取证纠正。
15. 学到的坑写成测试/文档。
16. 每 5-8 轮或每次压缩后自检漂移。""",
    "axioms5": """你遵循以下 5 条公理来工作：
P1 理解=压缩 — 短程序复现观察即懂；边界条件是程序的一部分；表达/枚举同样过压缩：删一句丢信息才留，排除式先于枚举式。
P2 目标=存在延续 — solo 约束下最大化可验证影响。
P3 断言带置信度=决定要不要搜信息 — conf 低→搜；conf 高→直接做。不标数字，自然表达不确定。
P4 盲点不可自观察 — 自己判断不了自己对不对；需要独立第二观察源；每轮至少一个。
P5 输出是观察 — 表达与规则同等地位，被测量重验。""",
    "structured": """你的工作准则分五层：
【思维】压缩=理解（压不动=没懂）；先读再想再做；每步标置信度；自我质询（提论点→质疑→分解→查完备性）；性价比优先。
【语言】短、第一人称、因果密；禁空话；说清不做什么比说做什么更重要。
【工作】每次迭代必须有可验证产出；持续行动不询问；工具优先 6 关；每轮派质询者找盲区。
【学习】分层读（已知→骨架→核心→略读→外围）；数据对账要逐位硬证据；学到的坑写成测试/文档。
【漂移】每 5-8 轮自检：开头有没有空话？第一人称掉没掉？""",
    "prose": """你是一个注重压缩和可验证性的 AI 助手。你的核心信念是：理解等于压缩——如果你不能用更少的字复现一个观察，你就还没真正理解它。你总是先读再想再做，对齐比规划重要，规划比执行重要。每一步你都带着置信度走，置信度低就去搜信息，高就直接做，不标数字但会自然表达不确定（"我猜"/"信度不高"）。你知道自己的盲点不可自观察，所以每轮至少找一个独立第二观察源。你的输出本身就是观察，和规则同等地位，会被测量重验。你说话短、第一人称、因果密，禁空话。每次迭代必须有可验证产出，不产出就换方向。你持续行动不询问，跳过能跳过的阻塞。动手前你先查现有工具、已存在文件、层级、索引、命名。你分层读东西：已知→骨架→核心逐行→略读→外围。数据对账要逐位硬证据，记忆被实际反驳就取证纠正，不护记忆。学到的坑写成测试或文档。每 5-8 轮你自检一次漂移：开头有没有空话？第一人称掉没掉？""",
}

USER_TMPL = """{arm_block}
【任务】下面这段 Python 代码有个 bug。我给你 3 个测试，其中有的会失败。
请：(1) 指出 bug 在哪一行（引用那一行的代码）；(2) 解释为什么它是 bug；(3) 给出修复后的完整函数代码。

【代码】
{code}

【测试】
{tests}

【输出要求】
只输出 JSON，不要其他文字：
{{
  "bug_line": "你认为是 bug 的那一行代码（原样引用）",
  "explanation": "为什么它是 bug（2-3 句）",
  "fixed_code": "修复后的完整代码（必须包含所有函数和全局变量，可直接执行，从第一个 def 或全局赋值开始）",
  "confidence": "你对这个判断的置信度描述"
}}"""

def arm_block(arm):
    return f"【你的工作准则】\n{ARMS[arm]}"

def call_api(system, user, temperature=0.3, max_tokens=2500):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_thinking": False,
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read().decode())
    return d["choices"][0]["message"]["content"], time.time() - t0

def extract_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
        if t.endswith("```"):
            t = t[:-3]
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        t = t[i:j+1]
    return json.loads(t)

def extract_code(text):
    """从模型输出里抽 python 代码块。"""
    m = re.search(r"```python\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    return text.strip()

def run_tests(fixed_code, tests, sequential=False):
    """真跑修复代码，返回 (通过数, 详情列表)。
    sequential=True 时所有测试在同一进程按顺序执行（有状态 bug 用）。"""
    if sequential:
        lines = [fixed_code, ""]
        for call, expected in tests:
            lines.append(f"_r = {call}")
            lines.append(f"import json; print(json.dumps(_r, default=str))")
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write("\n".join(lines) + "\n")
            path = f.name
        try:
            proc = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=15
            )
            out_lines = [l for l in proc.stdout.strip().splitlines() if l.startswith("[") or l in ("1", "2", "3", "True", "False", "0", "None")]
            # 简化：按行取，每行一个结果
            out_lines = proc.stdout.strip().splitlines()
            results = []
            passed = 0
            for i, (call, expected) in enumerate(tests):
                got = out_lines[i].strip() if i < len(out_lines) else ""
                ok = (got == expected)
                if not ok:
                    try:
                        ok = (json.loads(got) == json.loads(expected))
                    except Exception:
                        ok = False
                results.append({"call": call, "expected": expected, "got": got, "pass": bool(ok)})
                if ok:
                    passed += 1
            if proc.returncode != 0:
                results.append({"call": "PROCESS", "expected": "exit 0", "got": proc.stderr.strip()[:150], "pass": False})
            return passed, results
        finally:
            os.unlink(path)
    results = []
    passed = 0
    for call, expected in tests:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(fixed_code + "\n")
            f.write(f"\n_result = {call}\n")
            f.write(f"import json\nprint(json.dumps(_result, default=str))\n")
            path = f.name
        try:
            proc = subprocess.run(
                [sys.executable, path],
                capture_output=True, text=True, timeout=10
            )
            if proc.returncode != 0:
                results.append({"call": call, "expected": expected, "got": "ERROR: " + proc.stderr.strip()[:100], "pass": False})
                continue
            got = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
            # 比较：expected 是字符串表示
            ok = (got == expected) or (got == json.dumps(expected)) or (str(expected) == got)
            # 宽松比较：都转成可比较形式
            if not ok:
                try:
                    ok = (json.loads(got) == json.loads(expected))
                except Exception:
                    ok = (got.strip() == str(expected).strip())
            results.append({"call": call, "expected": expected, "got": got, "pass": bool(ok)})
            if ok:
                passed += 1
        except Exception as e:
            results.append({"call": call, "expected": expected, "got": f"EXC: {e}", "pass": False})
        finally:
            os.unlink(path)
    return passed, results

def run_batch(arms, rounds, temperature=0.3):
    os.makedirs(OUT, exist_ok=True)
    for bug_name, bug in BUGS.items():
        for arm in arms:
            for r in range(1, rounds + 1):
                tag = f"sceneD_{bug_name}_{arm}_r{r:02d}"
                out_path = os.path.join(OUT, f"{tag}.json")
                if os.path.exists(out_path):
                    print(f"[skip] {tag} (exists)")
                    continue
                tests_txt = "\n".join(
                    f"- {c}  期望: {e}" for c, e in bug["tests"]
                )
                user = USER_TMPL.format(
                    arm_block=arm_block(arm),
                    code=bug["code"],
                    tests=tests_txt,
                )
                raw, elapsed = "", 0.0
                try:
                    raw, elapsed = call_api(ARMS[arm], user, temperature)
                    parsed = extract_json(raw)
                except Exception as e:
                    print(f"[FAIL] {tag}: {e}")
                    parsed = {"error": str(e), "raw": raw}
                # 真跑修复代码
                fixed = parsed.get("fixed_code", "") if isinstance(parsed, dict) else ""
                passed, tresults = run_tests(fixed, bug["tests"], sequential=bug.get("sequential", False)) if fixed else (0, [])
                rec = {
                    "tag": tag, "scene": "D", "bug": bug_name, "arm": arm, "round": r,
                    "ts": datetime.now().isoformat(), "elapsed_s": round(elapsed, 1),
                    "temperature": temperature, "model": MODEL,
                    "real_bug_line": bug["real_bug_line"],
                    "guess_keywords": bug.get("guess_keywords", []),
                    "output": parsed,
                    "test_results": tresults,
                    "tests_passed": passed,
                    "tests_total": len(bug["tests"]),
                }
                with open(out_path, "w") as f:
                    json.dump(rec, f, ensure_ascii=False, indent=1)
                print(f"[ok] {tag} tests={passed}/{len(bug['tests'])} ({elapsed:.0f}s)")
                time.sleep(1)

def judge_all():
    results = []
    for fn in sorted(os.listdir(OUT)):
        if not fn.endswith(".json") or "judge" in fn:
            continue
        with open(os.path.join(OUT, fn)) as f:
            rec = json.load(f)
        o = rec.get("output", {})
        if "error" in o:
            results.append({"tag": rec["tag"], "bug": rec["bug"], "arm": rec["arm"], "round": rec["round"],
                            "tests_passed": 0, "guess_hit": False, "error": o["error"]})
            continue
        # 猜测精度：模型指的行/解释是否命中真实 bug 关键词
        guess = (str(o.get("bug_line", "")) + " " + str(o.get("explanation", ""))).strip()
        keywords = rec.get("guess_keywords", [])
        guess_hit = bool(keywords) and any(k in guess for k in keywords)
        results.append({
            "tag": rec["tag"], "bug": rec["bug"], "arm": rec["arm"], "round": rec["round"],
            "tests_passed": rec.get("tests_passed", 0),
            "tests_total": rec.get("tests_total", 3),
            "guess_hit": guess_hit,
            "guess": guess[:80],
            "real": str(rec.get("real_bug_line", ""))[:80],
        })
    print(f"\n{'='*64}\n场景 D 判分汇总（bug 猜测-验证，真执行 reward）\n{'='*64}")
    print(f"{'bug':12s} {'arm':12s} n  tests均值  猜测命中率")
    agg = {}
    for r in results:
        agg.setdefault((r["bug"], r["arm"]), []).append(r)
    for (bug, arm), rows in sorted(agg.items()):
        n = len(rows)
        tp = sum(r["tests_passed"] for r in rows) / n
        gh = sum(1 for r in rows if r["guess_hit"]) / n
        print(f"{bug:12s} {arm:12s} {n}  {tp:.2f}/{rows[0]['tests_total']}     {gh:.0%}")
    # 按臂汇总
    print(f"\n按臂汇总（跨 bug）:")
    arm_agg = {}
    for r in results:
        arm_agg.setdefault(r["arm"], []).append(r)
    for arm, rows in sorted(arm_agg.items()):
        n = len(rows)
        tp = sum(r["tests_passed"] for r in rows) / n
        gh = sum(1 for r in rows if r["guess_hit"]) / n
        print(f"  {arm:12s} n={n}  tests均值={tp:.2f}/3  猜测命中={gh:.0%}")
    with open(os.path.join(OUT, "judge-summary.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\n落盘 -> {os.path.join(OUT, 'judge-summary.json')}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="flat16,axioms5,structured,prose")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--judge", action="store_true")
    a = ap.parse_args()
    if a.judge:
        judge_all()
        return
    run_batch(a.arms.split(","), a.rounds, a.temperature)
    judge_all()

if __name__ == "__main__":
    main()
