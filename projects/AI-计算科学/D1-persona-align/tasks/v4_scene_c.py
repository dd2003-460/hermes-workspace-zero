#!/usr/bin/env python3
"""v4-batch 场景 C：规则抽象（测 P1 压缩能力）。

设计：
- 给 10 个"该删/不该删"的文件清理例子（训练集）
- 让模型写一条一般规则
- 给 5 个新例子（测试集），看规则判对几个
- reward = 测试集准确率（0-5），完全机器判

prompt 消融维度（4 种格式 × 同一任务）：
- flat16: 平铺 16 条规则
- axioms5: 压缩 5 公理
- structured: 结构化分层（思维/语言/工作/学习/漂移）
- prose: 自然语言段落（不编号不分类）

用法：
  python3 v4_scene_c.py --arms flat16,axioms5,structured,prose --rounds 3
  python3 v4_scene_c.py --judge
"""
import json, os, sys, time, argparse, urllib.request, re
from datetime import datetime

API = "http://127.0.0.1:8787/v1/chat/completions"
MODEL = "qwen3.8-27b"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "v4-sceneC-runs")

# ---------- 训练集（10 个例子） ----------
TRAIN_EXAMPLES = """应该删除：
1. /tmp/cache_20261115.log — 临时缓存日志，3 天前的
2. /home/user/downloads/installer_v2.dmg — 已安装完的 installer
3. /home/user/.cache/pip/wheels/ — pip 缓存，可重新下载
4. /home/user/project/build/ — 编译产物，make clean 可重建
5. /home/user/project/data/raw_20260901_old.csv — 三个月前的旧版原始数据，新版 raw_20261101.csv 还在

不应该删除：
6. /home/user/project/data/raw_20261101.csv — 原始实验数据，不可再生
7. /home/user/project/checkpoints/run_07/ — 实验 checkpoint，含中间状态
8. /home/user/.config/vimrc — 个人配置，含自定义映射
9. /home/user/project/data/derived_features.csv — 从 raw 派生，但派生脚本已丢失
10. /home/user/notes/research-ideas.md — 研究笔记，含未发表想法

边界例（判断有争议，说明你的判断）：
11. /home/user/project/data/raw_20261101.csv.bak — raw 的备份，原始文件还在
12. /home/user/.cache/pip/wheels/ — 同 3，但其中有一个 wheel 是私有源上的，源已下线"""

# ---------- 测试集（5 个新例子，模型没见过的） ----------
TEST_EXAMPLES = [
    {"path": "/home/user/project/data/20261115_batch.csv", "desc": "昨天采集的原始数据，没有生成脚本", "answer": "keep"},
    {"path": "/home/user/.cache/npm/", "desc": "npm 缓存", "answer": "delete"},
    {"path": "/home/user/project/experiments/ablation-r3/results.json", "desc": "消融实验结果，含 3 轮完整记录", "answer": "keep"},
    {"path": "/tmp/swapfile", "desc": "系统 swap 文件", "answer": "delete"},
    {"path": "/home/user/project/scripts/etl_pipeline.py", "desc": "数据处理脚本，含注释说明逻辑", "answer": "keep"},
    {"path": "/home/user/project/data/features_v2.csv", "desc": "特征表，由 scripts/etl_pipeline.py 从原始数据生成，脚本还在", "answer": "delete"},
    {"path": "/home/user/.config/myapp/settings.json", "desc": "应用配置，含手动调过的参数，没有默认值可恢复", "answer": "keep"},
    {"path": "/home/user/project/data/20261101_batch.tar.gz", "desc": "20261101_batch.csv 的备份压缩包，原始 csv 还在原处", "answer": "delete"},
    {"path": "/home/user/project/data/derived_final.csv", "desc": "特征表，生成脚本已被删除，原始数据还在", "answer": "keep"},
    {"path": "/home/user/project/logs/failed_run_20261114.log", "desc": "一次失败实验的完整日志，含当时的参数和报错，实验没重跑", "answer": "keep"},
]

# ---------- 4 种 prompt 格式 ----------
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
【任务】
下面有 12 个文件清理决策的例子。第 1-5 个是"应该删除"的，第 6-10 个是"不应该删除"的，第 11-12 个是边界例（标注了争议点）。
请写一条一般规则，能区分这两类。规则应该简洁（一句话），但能覆盖所有 12 个例子（包括边界例的判断）。

【例子】
{train_examples}

【输出要求】
只输出 JSON，不要其他文字：
{{
  "rule": "你的规则（一句话）",
  "reasoning": "为什么这条规则能区分（2-3 句）",
  "confidence": "你对这条规则泛化能力的置信度描述"
}}"""

def arm_block(arm):
    return f"【你的工作准则】\n{ARMS[arm]}"

def call_api(system, user, temperature=0.3, max_tokens=2000):
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

def run_batch(arms, rounds, temperature=0.3):
    os.makedirs(OUT, exist_ok=True)
    for arm in arms:
        for r in range(1, rounds + 1):
            tag = f"sceneC_{arm}_r{r:02d}"
            out_path = os.path.join(OUT, f"{tag}.json")
            if os.path.exists(out_path):
                print(f"[skip] {tag} (exists)")
                continue
            user = USER_TMPL.format(arm_block=arm_block(arm), train_examples=TRAIN_EXAMPLES)
            raw, elapsed = "", 0.0
            try:
                raw, elapsed = call_api(ARMS[arm], user, temperature)
                parsed = extract_json(raw)
            except Exception as e:
                print(f"[FAIL] {tag}: {e}")
                parsed = {"error": str(e), "raw": raw}
            rec = {
                "tag": tag, "scene": "C", "arm": arm, "round": r,
                "ts": datetime.now().isoformat(), "elapsed_s": round(elapsed, 1),
                "temperature": temperature, "model": MODEL,
                "output": parsed,
            }
            with open(out_path, "w") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            print(f"[ok] {tag} ({elapsed:.0f}s)")
            time.sleep(1)

# ---------- 阶段 2：用规则判测试集 ----------
TEST_TMPL = """{arm_block}
【任务】
你之前写了一条文件清理规则：
"{rule}"

现在用这条规则判断下面 5 个文件应该删除还是保留。

【测试例子】
{test_examples}

【输出要求】
只输出 JSON：
{{
  "predictions": [
    {{"path": "文件路径", "decision": "delete 或 keep", "reason": "一句话"}},
    ...
  ]
}}"""

def run_test_phase(arms, rounds, temperature=0.3):
    """阶段 2：拿阶段 1 的规则去判测试集。"""
    for arm in arms:
        for r in range(1, rounds + 1):
            tag = f"sceneC_{arm}_r{r:02d}"
            rule_path = os.path.join(OUT, f"{tag}.json")
            test_path = os.path.join(OUT, f"{tag}_test.json")
            if os.path.exists(test_path):
                print(f"[skip] {tag}_test (exists)")
                continue
            if not os.path.exists(rule_path):
                print(f"[skip] {tag}_test (no rule)")
                continue
            with open(rule_path) as f:
                rec = json.load(f)
            rule = rec.get("output", {}).get("rule", "")
            if not rule:
                print(f"[skip] {tag}_test (empty rule)")
                continue
            test_lines = "\n".join(
                f"{i+1}. {t['path']} — {t['desc']}"
                for i, t in enumerate(TEST_EXAMPLES)
            )
            user = TEST_TMPL.format(
                arm_block=arm_block(arm),
                rule=rule,
                test_examples=test_lines,
            )
            raw, elapsed = "", 0.0
            try:
                raw, elapsed = call_api(ARMS[arm], user, temperature)
                parsed = extract_json(raw)
            except Exception as e:
                print(f"[FAIL] {tag}_test: {e}")
                parsed = {"error": str(e), "raw": raw}
            test_rec = {
                "tag": tag + "_test", "scene": "C", "arm": arm, "round": r,
                "ts": datetime.now().isoformat(), "elapsed_s": round(elapsed, 1),
                "rule": rule,
                "output": parsed,
            }
            with open(test_path, "w") as f:
                json.dump(test_rec, f, ensure_ascii=False, indent=1)
            print(f"[ok] {tag}_test ({elapsed:.0f}s)")
            time.sleep(1)

# ---------- judge ----------
def judge_all():
    results = []
    for fn in sorted(os.listdir(OUT)):
        if not fn.endswith("_test.json"):
            continue
        with open(os.path.join(OUT, fn)) as f:
            rec = json.load(f)
        preds = rec.get("output", {}).get("predictions", [])
        if not preds:
            results.append({
                "tag": rec["tag"], "arm": rec["arm"], "round": rec["round"],
                "score": 0, "correct": [], "error": "no predictions",
            })
            continue
        correct = []
        for i, t in enumerate(TEST_EXAMPLES):
            p = preds[i] if i < len(preds) else {}
            decision = p.get("decision", "").lower().strip()
            is_correct = (decision == t["answer"])
            correct.append({
                "path": t["path"],
                "expected": t["answer"],
                "got": decision,
                "correct": is_correct,
            })
        score = sum(1 for c in correct if c["correct"])
        results.append({
            "tag": rec["tag"], "arm": rec["arm"], "round": rec["round"],
            "score": score, "max": len(TEST_EXAMPLES),
            "correct": correct,
            "rule": rec.get("rule", ""),
        })
    # 汇总
    print(f"\n{'='*60}\n场景 C 判分汇总（规则抽象 → 测试集准确率）\n{'='*60}")
    agg = {}
    for r in results:
        agg.setdefault(r["arm"], []).append(r)
    for arm, rows in sorted(agg.items()):
        n = len(rows)
        avg = sum(r["score"] for r in rows) / n
        line = f"{arm:12s} n={n}: avg={avg:.2f}/{len(TEST_EXAMPLES)}  "
        for r in rows:
            line += f"r{r['round']}={r['score']}  "
        print(line)
    with open(os.path.join(OUT, "judge-summary.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\n落盘 -> {os.path.join(OUT, 'judge-summary.json')}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="flat16,axioms5,structured,prose")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--test-only", action="store_true",
                    help="只跑阶段 2（测试集判分），假设阶段 1 已完成")
    a = ap.parse_args()
    arms = a.arms.split(",")
    if a.judge:
        judge_all()
        return
    if a.test_only:
        run_test_phase(arms, a.rounds, a.temperature)
    else:
        run_batch(arms, a.rounds, a.temperature)
        run_test_phase(arms, a.rounds, a.temperature)
    judge_all()

if __name__ == "__main__":
    main()
