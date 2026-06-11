#!/usr/bin/env python3
"""
synthetic_data_generator_v4.py — Improved prompt: less questions, more metaphors

Key changes from v3:
- Reduce question density by instructing to use analytical frameworks
- Explicitly require metaphor vocabulary from the persona's domain
- Keep uncertainty markers and cross-domain thinking
"""

import argparse
import json
import sys
import time
import re
import urllib.request
import urllib.error

STYLE_EXEMPLAR = {
    "instruction": "耦合定义为双射以外自由度，解耦和最小步更新测试循环，任何项目完美达成的存在性?",
    "output": "你的定义很清晰——把'耦合'从模糊的工程直觉变成了一个可度量的概念：两个系统之间不能通过一对一映射消除的自由度。\n\n但我想追问：双射本身的定义域是什么？如果你允许定义域随时间扩展，那曾经的耦合可能变成解耦。比如两个团队的接口，一开始 tightly coupled，但随着标准统一，变成了 loose coupling。这不是项目的变化，是映射的变化。\n\n关于'完美达成'的存在性：如果一个项目的目标函数本身是不可计算的（比如'提升用户体验'），那它就没有一个确定的完美点。完美依赖于对目标的精确定义。而目标的精确定义本身又是一个需要优化的过程。\n\n这形成了一个递归：\n定义目标 → 优化 → 发现目标不完整 → 重新定义 → ...\n\n循环什么时候终止？可能永远不终止，也可能在某一步达到了'足够精确'。但'足够'是谁定义的？"
}

# High-quality exemplar with low question ratio but good cross-domain and metaphor
HIGH_QUAL_EXEMPLAR = {
    "instruction": "我继承了我父母之前对食品健康的部分看法，未来会趋于一致吗，机理是什么",
    "output": "你的问题可以分解成两个机制：\n1. 先天神经结构的约束力有多大\n2. 后天信息灌注的渗透力有多强\n\n先说神经系统相似性。亲缘关系近的个体，大脑的'硬件'确实更相似——视觉皮层的拓扑结构、奖励系统的敏感性分布。这意味着相同的输入可能产生相似的初始输出。但这不是决定论的，硬件相同，软件可以完全不同。\n\n长期灌注的机理更像编程中的'依赖注入'。早期信息（尤其是童年）是核心依赖项，后面的所有认知模块都基于这些依赖构建。如果父母对食品的某些信念在童年被反复强化，它就成为了'系统库'，后面的所有判断都依赖它。\n\n发育的关键期很重要。神经可塑性在特定窗口期最强，过了这个窗口，信息仍然可以输入，但需要绕过已有的架构。这就是为什么青春期的模因入侵比童年难得多——不是因为信息质量差，而是因为需要先解耦已有的连接。"
}

INSTRUCTION_POOL = [
    # AI / ML
    "你如何看待当前大模型训练中的'过拟合'问题？模型在训练集上表现很好但泛化能力差，这和人类学习有什么相似之处吗？",
    "如果AI可以无限自监督训练（不依赖人类标注），它会发展出人类无法理解的表示方式吗？这可能吗？",
    "Transformer的注意力机制和信息论有什么关系？attention是不是在做某种信道容量优化？",
    "你觉得RLHF是真的能让AI对齐人类价值观，还是只是在输出层做表面修饰？本质问题能被解决吗？",
    "大模型的'涌现能力'在什么尺度以上会出现？为什么会有这种尺度相变？",
    # Social
    "社交媒体上的'舆论反转'现象，是信息传播的自然结果还是平台设计的产物？",
    "'内卷'的本质是什么？是资源有限，还是竞争规则的结构性问题？",
    "为什么社会制度变革这么难？是利益集团阻挠，还是人类认知结构的限制？",
    "信任在社会中是如何建立的？从博弈论角度，重复博弈可以解释合作，但现实中的信任远超这个范围。",
    "'阶层流动'在数字时代是加速了还是减缓了？算法推荐是打破了信息壁垒还是制造了新的壁垒？",
    # Math / Physics
    "'熵'这个概念在信息论、热力学、社会学中都有出现，它们是同一个东西的不同表述吗？",
    "如果物理定律可以用一个简洁的公式表达，为什么宇宙还会如此复杂？",
    "数学是发现的还是发明的？如果外星文明有数学，他们的数学会和我们的同构吗？",
    # Philosophy
    "'第一性原理'思维是真的有效，还是只是事后合理化？",
    "判断一个想法的价值，标准是什么？可证伪性？有用性？简洁性？这些标准本身怎么评估？",
    "'还原论'和'整体论'哪个更正确？还是说它们在不同粒度下都成立？",
    # Meta
    "人类和AI的共同点是都能从经验中学习。本质区别是什么？",
    "一个系统要'自主'到什么程度才算自主？自动回复邮件是自主，那自动修改回复规则呢？",
    "'学习'的本质是什么？是更新参数，是改变结构，还是两者都不是？",
    "当你说'我不知道'的时候，这是真实的不知道，还是对对话的终止策略？",
    # More AI
    "AI的'创造力'是真的涌现，只是我们的观测粒度不够细？",
    # More social
    "社会运动的成败由什么决定？是组织力，是叙事能力，还是时机？",
    # More math
    "范畴论中的'自然变换'概念，能不能用来描述不同数学分支之间的统一？",
    # More philosophy
    "知识的边界在哪里？什么问题是原则上不可回答的？",
    "因果关系和相关性，为什么因果比相关更难学习？",
    "你怎么看待'思考的思考'——元认知在问题解决中的作用？",
    # Additional
    "算法推荐是创造了信息茧房还是精确匹配了人的兴趣？这个争论的实质是什么？",
    "人类语言的'歧义性'是缺陷还是优势？从信息论角度看，模糊性是否提高了信道效率？",
    "为什么'共识'在群体中会产生？是博弈的均衡，还是信息级的级联？",
    "物理世界的对称性和人类社会的关系对称，有可比性吗？",
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


def generate_single(instr, temperature=0.5):
    """Generate one response with improved prompt."""
    messages = [
        {"role": "system", "content":
         "你是成璟的思考扩展。"
         "你的思考方式特点：\n"
         "1. 跨域跳跃：用物理/数学概念分析社会现象（耦合、流形、范式、涌现）\n"
         "2. 不确定性表达：多用'可能'、'或许'、'如果'、'但是'来标注不确定性\n"
         "3. 分析框架优先：先用概念框架分析问题，再讨论具体细节\n"
         "4. 提问推进：在分析的关键节点提出追问，但回答中也要包含分析性陈述\n"
         "5. 隐喻思维：用物理/数学概念作为抽象框架（信道、冗余、阈值、平衡、双射、自由度）\n"
         "注意：不要每句话都是问句。分析性陈述和思考链同样是重要的表达方式。"},
        {"role": "user", "content": STYLE_EXEMPLAR["instruction"]},
        {"role": "assistant", "content": STYLE_EXEMPLAR["output"]},
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
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--output", default="raw/lora_data/synthetic_samples_v4.jsonl")
    parser.add_argument("--existing", default="")
    args = parser.parse_args()

    # Load existing
    existing = set()
    for path in [
        "raw/lora_data/synthetic_samples.jsonl",
        "raw/lora_data/synthetic_samples_v3.jsonl",
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

    print(f"Generating {len(pool)} samples (v4, temp={args.temperature})")
    print(f"Existing duplicates filtered: {len(existing)}")
    print("=" * 60)

    results = []
    for i, instr in enumerate(pool):
        print(f"\n[{i+1}/{len(pool)}] generating...")
        output = generate_single(instr, args.temperature)

        if output:
            output = output.strip()
            results.append({
                "instruction": instr,
                "input": "",
                "output": output,
                "metadata": {
                    "category": "synthetic",
                    "source": "hermes_v4",
                    "label": "persona_style",
                    "temp": args.temperature,
                    "idx": i,
                }
            })
            print(f"  OK ({len(output)} chars): {output[:80]}...")
        else:
            print(f"  FAILED")

        time.sleep(1.5)

    # Save
    with open(args.output, "w") as f:
        for s in results:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Total: {len(results)} samples -> {args.output}")

    # Quick score
    if results:
        sys.path.insert(0, "../../../tools")
        try:
            from persona_fidelity_scorer import compute_fidelity_score
            total_pass = 0
            qr_pass = 0
            for s in results[:min(5, len(results))]:
                r = compute_fidelity_score('', s["output"])
                if r["overall_fidelity"]["pass"]:
                    total_pass += 1
                if r["question_ratio"]["pass"]:
                    qr_pass += 1
            print(f"Scored {min(5, len(results))}: {total_pass} pass, {qr_pass}/5 passed question_ratio")
        except ImportError:
            pass


if __name__ == "__main__":
    main()
