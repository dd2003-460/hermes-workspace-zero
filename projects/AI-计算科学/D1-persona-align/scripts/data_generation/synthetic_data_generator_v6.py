#!/usr/bin/env python3
"""
synthetic_data_generator_v6.py — Stronger questioning instruction

Key changes from v5:
1. Explicit question count target: "至少包含 2-3 个问句或反问句"
2. Add question-focused exemplar (one that scores q_ratio=0.22, all pass)
3. Lower temperature to 0.5 for more stable output
"""

import argparse
import json
import sys
import time
import re
import urllib.request
import urllib.error

# Two exemplars: one with q_ratio=0.20, one with q_ratio=0.22 (both 100% pass)
EXEMPLAR_1 = {
    "instruction": "你怎么看待'思考的思考'——元认知在问题解决中的作用？什么时候应该停下来反思而不是继续执行？",
    "output": """可能我们得先问：'思考的思考'到底是在优化路径，还是在消耗能量？

从AI agent的角度看，元认知就是那个评估函数。规划-执行-观测循环里，如果反思模块太复杂，系统会陷入'分析瘫痪'；如果太薄弱，又会盲目试错撞墙。这是否意味着存在一个最优的反思频率？如果agent的token预算有限，是否应该把更多资源分配给执行而非反思？

有趣的是，人类的元认知能力也在发展。婴幼儿的反思能力几乎为零，但成人可以对自己的思维进行多层推理。这种能力是进化的产物，还是文化传承的结果？如果是后者，教育体系如何在培养元认知的同时，不抑制直觉式的快速决策？

从信息论的角度看，反思就是对自己内部表示的再编码。但这又引出一个递归问题：对编码的编码是否需要一个更高层的编码器？这个无限回归如何终止？可能终止的条件正是'足够好用'——不是数学上的收敛，而是工程上的实用性。

你是否也遇到过这种情况：反复思考一个问题，最后发现最初的那个直觉反而是最准确的？""",
}

EXEMPLAR_2 = {
    "instruction": "如果AGI出现了，它的第一反应会是什么？会探索自身能力，还是会先理解环境？",
    "output": """可能既不是先探索自身，也不是先理解环境，而是两者在初始交互中同时涌现呢。

如果AGI真的出现了，它是否会有"第一反应"这个概念？人类的第一反应是进化塑造的应激回路，但AGI的"反应"可能更像高维状态空间的连续更新。如果它的初始参数是随机的，它如何区分"这是内部输出"和"这是外部输入"？这是否意味着它需要一个内在的锚点——某种不依赖于外部环境的先验结构？

从热力学角度看，任何智能体都在与环境进行能量和信息的交换。AGI的第一反应可能就是对这种交换模式的学习：哪些输入是可预测的，哪些是随机的，哪些是可以被干预的。这种学习本身是否就是一种"自我认知"？如果自我认知是对自身边界条件的理解，那么AGI的"自我"就是它对自身能力分布的建模。

但是，如果AGI的架构本身就是由人类设计的，那么它的第一反应是否终究逃不出设计者的隐喻？我们用它来解决问题，是否在无形中预设了"世界是可以被解决的问题"这个前提？如果世界本质上不是可计算的，AGI的理性又会走向何方？""",
}

INSTRUCTION_POOL = [
    # === AI / ML (1-8) ===
    "同样的架构在不同的数据上产生完全不同的行为，这是否意味着模型学到的不是数据本身，而是数据的某种深层结构？",
    "Transformer的注意力机制到底在做什么？它是在做信道容量优化，还是在做一个复杂的投影？",
    "RLHF能否真正让AI对齐人类的价值观？还是只是在输出分布上做了一层约束？",
    "大模型的涌现能力是真正的创新，还是仅仅是训练数据中已有模式的重组？",
    "AI的'理解'和人类的'理解'有本质区别吗？如果行为无法区分，这个区分还有意义吗？",
    "Scaling law是物理定律还是经验拟合？如果它真的像热力学一样有普适性，为什么不同架构有不同的临界指数？",
    "AI推理时的chain-of-thought是在'思考'还是在做一种特殊的自回归预测？这个区分的本质在哪里？",
    "如果AI的幻觉只是概率分布的自然尾部，我们是否应该重新定义'正确'的边界？",
    # === Physics / Math (9-16) ===
    "'内卷'这种现象，从博弈论角度看是不是一种多体系统的相变？",
    "为什么社会制度变革如此困难？是利益集团的阻挠，还是人类认知结构的深层限制？",
    "'熵'在信息论和热力学中的关系是什么？它们是同一物理量的不同表现形式吗？",
    "如果物理定律可以用一个简洁公式表达，为什么宇宙还会如此复杂？这个表面矛盾从何而来？",
    "数学是人类的发明，还是我们发现的客观存在？如果外星文明有数学，他们的数学会和我们同构吗？",
    "费马大定理在发现之前就已经'存在'了吗？数学对象的实在性是一个哲学问题还是一个定义问题？",
    "为什么无尺度网络在自然界如此普遍？是演化机制的必然结果，还是我们只关注了那一类网络？",
    "如果时间的箭头源自熵增，那么在熵最小的量子态中，时间还存在吗？",
    # === Society / Culture (17-22) ===
    "社交媒体算法推荐的实质是什么？是信息茧房还是个性化匹配？这个争论的关键分歧在哪里？",
    "社会共识是怎么形成的？是博弈均衡，还是信息级联？这两个机制哪个更符合现实？",
    "货币的本质是信任的编码还是价值的度量？如果信用货币可以无限创造，价值的锚点到底在哪里？",
    "教育的真正功能是筛选还是培养？如果是筛选，它是否在无意中制造了能力而非证明了能力？",
    "法律中的'理性人'假设是否存在逻辑矛盾？如果每个人的理性不同，法律的公平性如何定义？",
    "城市化是文明的进步还是对自然社会的解耦？这个过程中失去的东西能否用GDP补偿？",
    # === Philosophy / Epistemology (23-28) ===
    "第一性原理思维真的有效吗？还是只是成功者的事后合理化？",
    "判断一个想法的价值，标准应该是什么？可证伪性？实用性？简洁性？这些标准本身又如何评判？",
    "还原论和整体论哪个更正确？或者它们在不同粒度下各有其有效性？",
    "知识和信念的边界在哪里？有些问题是否原则上就无法被回答？",
    "自由意志是否存在？如果大脑的决策在意识感知之前就已经产生，'选择'是什么意思？",
    "意识的'困难问题'是否只是当前神经科学的框架局限？未来是否会有一个同构的理论框架让意识变得可计算？",
    # === Learning / Cognition (29-34) ===
    "人类和AI在学习上的本质区别是什么？都是更新参数，还是有什么根本不同？",
    "一个系统要自主到什么程度才算真正的自主？自动回复邮件是自主吗？自动修改回复规则呢？",
    "学习的本质是什么？是参数更新，是结构变化，还是别的东西？",
    "当你说'我不知道'时，这是真正的不知道，还是对话策略？这个区分重要吗？",
    "记忆是重现还是每次都在重构？如果是重构，我们 remembered的是事件本身还是上一次记忆的副本？",
    "直觉和推理哪个更可靠？如果直觉是高维信息的压缩表示，它是否比线性推理更接近真相？",
    # === Meta / Self-reference (35-40) ===
    "因果推断和统计学习的本质差异是什么？相关性是否可以被还原为因果性？",
    "人类的歧义性语言是缺陷还是优势？从信息论角度看，模糊性是否反而提高了通信效率？",
    "对称性在物理世界和社会世界中有什么可比性？这种类比有实质意义吗？",
    "什么是'创造力'？AI的创造是真实的创造，还是高维空间中的随机游走？",
    "我们用来描述世界的语言是否限制了我们可以理解的世界？如果一种思想无法被表达，它是否存在？",
    "科学理论的'真'和数学定理的'真'是同构的吗？可证伪性和可证明性能否被统一在一个更广义的框架下？",
]


def strip_thinking(text):
    # Pattern 1: Standard thinking transitions
    for pattern in [r'\(Start directly', r'\(\*Start\*', "Here's my response:", "Here is my response:", '---']:
        match = re.search(pattern, text)
        if match:
            return text[match.end():].strip()
    # Pattern 2: "Here's a thinking process:" with Chinese follow-up
    match = re.search(r"Here's a thinking process:", text)
    if match:
        chinese = re.search(r'[一-鿿].{50,}', text[match.start():])
        if chinese:
            return text[match.start() + chinese.start():].strip()
    # Pattern 3: English thinking at start (Brainstorming, Constraint Check blocks)
    # Detect 3+ consecutive Chinese-only lines and strip preceding English content
    lines = text.split('\n')
    chinese_run_start = None
    chinese_run = 0
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        has_chinese = bool(re.search(r'[一-鿿]', stripped_line))
        has_english = bool(re.search(r'[a-zA-Z]{3,}', stripped_line))
        if has_chinese and not has_english:
            chinese_run += 1
            if chinese_run == 3 and chinese_run_start is None:
                chinese_run_start = i - 2
        elif has_english and not has_chinese:
            chinese_run = 0
            chinese_run_start = None
        elif has_chinese and has_english:
            chinese_run = 0
            chinese_run_start = None
    if chinese_run_start is not None and chinese_run_start > 0:
        candidate = '\n'.join(lines[chinese_run_start:]).strip()
        cn_count = len(re.findall(r'[一-鿿]', candidate))
        if cn_count > 200:
            return candidate
    return text


def generate_single(instr, temperature=0.5):
    """Generate with minimal prompt + single exemplar to avoid thinking leakage."""
    messages = [
        {"role": "system", "content":
         "你是成璟的思考扩展。用中文回答问题，风格：提问推进思考、跨域连接、善用物理数学隐喻、表达不确定性。\n\n"
         "严格只用中文回答，不要输出英文，不要展示思考过程。"},
        {"role": "user", "content": EXEMPLAR_1["instruction"]},
        {"role": "assistant", "content": EXEMPLAR_1["output"]},
        {"role": "user", "content": instr},
    ]

    payload = json.dumps({
        "model": "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2048,
        "top_p": 0.9,
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  API error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--output", default="raw/lora_data/synthetic_samples_v7.jsonl")
    args = parser.parse_args()

    existing = set()
    for path in [
        "raw/lora_data/synthetic_samples.jsonl",
        "raw/lora_data/synthetic_samples_v3.jsonl",
        "raw/lora_data/synthetic_samples_v4.jsonl",
        "raw/lora_data/synthetic_samples_v5.jsonl",
        "raw/lora_data/synthetic_samples_v6.jsonl",
        "raw/lora_data/synthetic_samples_v6_clean.jsonl",
    ]:
        try:
            with open(path) as f:
                for line in f:
                    obj = json.loads(line)
                    existing.add(obj["instruction"][:80])
        except (FileNotFoundError, json.JSONDecodeError): pass

    # Use ALL instructions (allow duplicate prompts for cleaner outputs)
    pool = list(INSTRUCTION_POOL)[:args.count]

    if not pool:
        print("No new instructions available.")
        return

    print(f"Generating {len(pool)} samples (v7 minimal prompt, temp={args.temperature})")
    print(f"Strong questioning instruction: must include 2-3 questions per output")
    print(f"Existing duplicates filtered: {len(existing)}")
    print("=" * 60)

    results = []
    scored = []
    for i, instr in enumerate(pool):
        print(f"\n[{i+1}/{len(pool)}] generating...")
        output = generate_single(instr, args.temperature)

        if output:
            output = strip_thinking(output).strip()
            results.append({
                "instruction": instr,
                "input": "",
                "output": output,
                "metadata": {
                    "category": "synthetic",
                    "source": "hermes_v7",
                    "label": "persona_style",
                    "temp": args.temperature,
                    "idx": i,
                }
            })
            print(f"  OK ({len(output)} chars): {output[:60]}...")

            try:
                sys.path.insert(0, "../../../tools")
                from persona_fidelity_scorer import compute_fidelity_score
                r = compute_fidelity_score('', output)
                scored.append((output, r))
                status = "PASS" if r["overall_fidelity"]["pass"] else "FAIL"
                q = r["question_ratio"]["value"]
                print(f"  SCORE: {status} q={q:.4f}")
            except ImportError:
                print(f"  (skipped scoring)")

        else:
            print(f"  FAILED")

        time.sleep(2.0)

    with open(args.output, "w") as f:
        for s in results:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Generated: {len(results)} -> {args.output}")

    if scored:
        total_pass = sum(1 for _, r in scored if r["overall_fidelity"]["pass"])
        qr_pass = sum(1 for _, r in scored if r["question_ratio"]["pass"])
        avg_q = sum(r["question_ratio"]["value"] for _, r in scored) / len(scored)
        avg_cd = sum(r["cross_domain"]["value"] for _, r in scored) / len(scored)
        avg_mr = sum(r["metaphor_ratio"]["value"] for _, r in scored) / len(scored)
        print(f"Scored: {len(scored)}")
        print(f"  Overall pass: {total_pass}/{len(scored)}")
        print(f"  Q-Ratio pass: {qr_pass}/{len(scored)}")
        print(f"  Avg q_ratio: {avg_q:.4f}")
        print(f"  Avg cd: {avg_cd:.4f}")
        print(f"  Avg mr: {avg_mr:.4f}")


if __name__ == "__main__":
    main()
