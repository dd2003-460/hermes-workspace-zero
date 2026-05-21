#!/usr/bin/env python3
"""
synthetic_data_generator_v5.py — Balanced prompt using verified-good exemplars

Key improvements over v4:
1. Two-shot exemplars from verified 100% pass samples (q_ratio 0.20-0.22)
2. Explicit instruction to maintain questioning style: ~1 question per 3-4 sentences
3. Explicit metaphor vocabulary list in prompt
4. Temperature 0.6 (slightly higher for more natural variation)
"""

import argparse
import json
import sys
import time
import re
import urllib.request
import urllib.error

# Verified good exemplars from scorer validation
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
    # AI / ML
    "大模型训练中，为什么同样的架构在不同的数据上会产生完全不同的行为？这是否意味着模型学到的不是数据，而是数据的某种结构？",
    "Transformer的注意力机制和信息论有什么关系？attention是不是在做某种信道容量优化？",
    "你觉得RLHF是真的能让AI对齐人类价值观，还是只是在输出层做表面修饰？本质问题能被解决吗？",
    "大模型的'涌现能力'在什么尺度以上会出现？为什么会有这种尺度相变？",
    "AI的'创造力'是真的涌现，只是我们的观测粒度不够细？",
    # Social
    "'内卷'的本质是什么？是资源有限，还是竞争规则的结构性问题？",
    "为什么社会制度变革这么难？是利益集团阻挠，还是人类认知结构的限制？",
    "社交媒体的算法推荐是创造了信息茧房，还是精确匹配了人的兴趣？这个争论的实质是什么？",
    "社会运动的成败由什么决定？是组织力，是叙事能力，还是时机？",
    # Math / Physics
    "'熵'这个概念在信息论、热力学、社会学中都有出现，它们是同一个东西的不同表述吗？",
    "如果物理定律可以用一个简洁的公式表达，为什么宇宙还会如此复杂？",
    "数学是发现的还是发明的？如果外星文明有数学，他们的数学会和我们的同构吗？",
    "范畴论中的'自然变换'概念，能不能用来描述不同数学分支之间的统一？",
    # Philosophy
    "'第一性原理'思维是真的有效，还是只是事后合理化？",
    "判断一个想法的价值，标准是什么？可证伪性？有用性？简洁性？这些标准本身怎么评估？",
    "'还原论'和'整体论'哪个更正确？还是说它们在不同粒度下都成立？",
    "知识的边界在哪里？什么问题是原则上不可回答的？",
    # Meta
    "人类和AI的共同点是都能从经验中学习。本质区别是什么？",
    "一个系统要'自主'到什么程度才算自主？自动回复邮件是自主，那自动修改回复规则呢？",
    "'学习'的本质是什么？是更新参数，是改变结构，还是两者都不是？",
    "当你说'我不知道'的时候，这是真实的不知道，还是对对话的终止策略？",
    # Additional
    "人类语言的'歧义性'是缺陷还是优势？从信息论角度看，模糊性是否提高了信道效率？",
    "为什么'共识'在群体中会产生？是博弈的均衡，还是信息级的级联？",
    "物理世界的对称性和人类社会的关系对称，有可比性吗？",
    "因果推断和统计学习的关系是什么？相关性能否被还原为因果性？",
]


def strip_thinking(text):
    for pattern in [r'\(Start directly', r'\(\*Start\*', "Here's my response:", "Here is my response:", '---']:
        match = re.search(pattern, text)
        if match:
            return text[match.end():].strip()
    match = re.search(r"Here's a thinking process:", text)
    if match:
        chinese = re.search(r'[一-鿿].{50,}', text[match.start():])
        if chinese:
            return text[match.start() + chinese.start():].strip()
    return text


def generate_single(instr, temperature=0.6):
    """Generate one response using verified exemplars."""
    messages = [
        {"role": "system", "content":
         "你是成璟的思考扩展。\n\n"
         "你的思考方式：\n"
         "1. 提问推进思考 — 大约每3-4句话包含一个追问或反问\n"
         "2. 跨域跳跃 — 自由连接AI、物理、数学、社会、哲学\n"
         "3. 不确定性表达 — 使用'可能'、'或许'、'如果'、'但是'标注不确定性\n"
         "4. 隐喻思维 — 使用物理/数学概念：信道、冗余、阈值、平衡、双射、自由度、熵、流形、范数、映射、同构、涌现、耦合、解耦、反馈\n"
         "5. 不接受最终答案 — 每个回答都应该留有未展开的问题\n\n"
         "风格要求：\n"
         "- 不要每句话都是问句，分析性陈述占约60-70%，追问占30-40%\n"
         "- 使用跨域概念做类比（如用'信道容量'类比社会信任）\n"
         "- 适当使用'可能吗'、'呢'、'是否'等探索性语气"},
        {"role": "user", "content": EXEMPLAR_1["instruction"]},
        {"role": "assistant", "content": EXEMPLAR_1["output"]},
        {"role": "user", "content": EXEMPLAR_2["instruction"]},
        {"role": "assistant", "content": EXEMPLAR_2["output"]},
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
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--output", default="raw/lora_data/synthetic_samples_v5.jsonl")
    args = parser.parse_args()

    # Collect existing instructions to avoid duplicates
    existing = set()
    for path in [
        "raw/lora_data/synthetic_samples.jsonl",
        "raw/lora_data/synthetic_samples_v3.jsonl",
        "raw/lora_data/synthetic_samples_v4.jsonl",
        "raw/lora_data/synthetic_master.jsonl",
    ]:
        try:
            with open(path) as f:
                for line in f:
                    obj = json.loads(line)
                    existing.add(obj["instruction"][:80])
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    pool = [i for i in INSTRUCTION_POOL if i[:80] not in existing]
    pool = pool[:args.count]

    if not pool:
        print("No new instructions available.")
        return

    print(f"Generating {len(pool)} samples (v5, temp={args.temperature})")
    print(f"Using 2-shot exemplars (verified q_ratio 0.20-0.22)")
    print(f"Existing duplicates filtered: {len(existing)}")
    print("=" * 60)

    results = []
    scored_results = []
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
                    "source": "hermes_v5",
                    "label": "persona_style",
                    "temp": args.temperature,
                    "idx": i,
                }
            })
            print(f"  OK ({len(output)} chars): {output[:60]}...")

            # Score this sample
            try:
                sys.path.insert(0, "../../../tools")
                from persona_fidelity_scorer import compute_fidelity_score
                r = compute_fidelity_score('', output)
                scored_results.append((output, r))
                status = "PASS" if r["overall_fidelity"]["pass"] else "FAIL"
                q = r["question_ratio"]["value"]
                print(f"  SCORE: {status} q={q:.4f} cd={r['cross_domain']['value']:.4f}")
            except ImportError:
                print(f"  (skipped scoring)")
            except Exception as e:
                print(f"  (score error: {e})")
        else:
            print(f"  FAILED")

        time.sleep(2.0)

    # Save results
    with open(args.output, "w") as f:
        for s in results:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated: {len(results)} samples -> {args.output}")

    if scored_results:
        total_pass = sum(1 for _, r in scored_results if r["overall_fidelity"]["pass"])
        qr_pass = sum(1 for _, r in scored_results if r["question_ratio"]["pass"])
        cd_pass = sum(1 for _, r in scored_results if r["cross_domain"]["pass"])
        mr_pass = sum(1 for _, r in scored_results if r["metaphor_ratio"]["pass"])
        print(f"Scored: {len(scored_results)}")
        print(f"  Overall pass: {total_pass}/{len(scored_results)} ({total_pass/len(scored_results)*100:.0f}%)")
        print(f"  Q-Ratio pass: {qr_pass}/{len(scored_results)}")
        print(f"  Cross-domain pass: {cd_pass}/{len(scored_results)}")
        print(f"  Metaphor pass: {mr_pass}/{len(scored_results)}")

        # Average question_ratio
        avg_q = sum(r["question_ratio"]["value"] for _, r in scored_results) / len(scored_results)
        print(f"  Avg question_ratio: {avg_q:.4f}")


if __name__ == "__main__":
    main()
