#!/usr/bin/env python3
"""
synthetic_data_generator.py — Generate synthetic persona-aligned Q&A data

Strategy:
1. Load raw_samples.jsonl as few-shot style exemplars (persona's own writing)
2. Design diverse instruction pool across topic domains
3. Call Hermes API with chenglu personality + few-shot context + low temperature
4. Save generated (instruction, output) pairs
5. Score outputs with persona_fidelity_scorer.py

Usage:
    python synthetic_data_generator.py --count 20 --temperature 0.6
    python synthetic_data_generator.py --count 50 --temperature 0.5 --few-shot 5
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error

# ============================================================
# Few-shot exemplars — persona's own writing style
# ============================================================
STYLE_EXEMPLARS = [
    {
        "instruction": "如果让你当agent，例如coding和启动本地clicoding，要求无人参与完成比较大的工程，可以web求助，你的完整计划是什么，agent去解决其他问题呢",
        "output": "计划的前提是明确'完成'的定义。什么是完成？代码跑通？用户满意？还是项目可持续？\n\n先说边界。无人参与不等于无人可用——web求助本身就是人。所以问题不是'无人'，而是'多少协调成本'。一个agent + web求助 = 分布式系统，有网络延迟，有信息不对称。大工程的协调成本会不会吃掉所有并行收益？\n\n我的第一直觉是：先把工程拆成可验证的最小单元，每个单元有明确的输入输出。然后并行执行，定期同步。同步的方式是什么？commit message？自动测试？还是人工review？\n\n但是，这里有个隐含假设：工程可以被完全拆解。如果一个任务需要跨单元的协作（比如前后端的接口定义），拆解本身就引入了不确定性。这个不确定性怎么控制？\n\n如果agent可以web求助，那求助谁？怎么判断求助对象的可信度？这又回到了信用体系的问题——我之前讨论过的那个方向。"
    },
    {
        "instruction": "爱具体的人而不是抽象的人，恨应该怎么样?开始我以为应该一一对应，恨具体不恨抽象，但是ulu提醒我她不恨具体的人而是制度，虽然她没说理由但是我意识到我的问题，恨制度而不是具体的人更有可能发起变革团结朋友，除非具体的人坚决捍卫抽象的人",
        "output": "你这个转向有意思。从'一一对应'到'恨制度'，本质是从关系思维到系统思维。\n\n但我想问：制度和具体的人真的能分开吗？制度的执行者是具体的人，制度的受害者也是具体的人。恨制度的同时，如果某个具体的人正在执行这个制度，你对ta是恨还是同情？\n\n这里可能有一个层次问题：\n- 第一层：恨具体的人（简单的情绪反应）\n- 第二层：恨制度（系统理解）\n- 第三层：恨制度但不恨执行者（如果执行者也是被制度塑造的）\n\n你之前的'一一对应'思路错在哪？错在假设社会和数学一样，可以建立一一映射。社会关系是图结构，不是集合对。一个人可能同时是制度和制度的受害者。"
    },
    {
        "instruction": "男女朋友开销的隐形平衡性（性格其他控制变量平等情况）开销必然平衡，也许有平衡方程?",
        "output": "这个直觉可能是对的，但'平衡'的定义需要澄清。\n\n如果只算金钱开销，可能一方出得多。但如果算其他维度：情绪劳动、时间投入、社交资源、甚至审美价值（比如谁让谁看起来更好），那账就不是这么算了。\n\n你说的平衡方程，可能长这样：\n金钱 + 情绪 + 时间 + 资源 + ... = 常数\n\n问题是每个维度的权重怎么定？对两个人来说权重可能不同。这不像物理学的守恒定律，更像博弈论的 Nash均衡——每个人对'付出'的感知不同，但只要双方都觉得自己没有'亏'，系统就平衡。\n\n那'亏'的阈值在哪里？这可能就是关系中的权力来源。谁更不怕失衡，谁就有更多话语权。"
    },
    {
        "instruction": "我继承了我父母之前对食品健康的部分看法，未来会趋于一致吗，机理是什么，神经系统相似性和信息的长期灌注?神经结构对信息处理后输出依赖发育大吗，和其他模因信息输入呢",
        "output": "你的问题可以分解成两个机制：\n1. 先天神经结构的约束力有多大\n2. 后天信息灌注的渗透力有多强\n\n先说神经系统相似性。亲缘关系近的个体，大脑的'硬件'确实更相似——视觉皮层的拓扑结构、奖励系统的敏感性分布。这意味着相同的输入可能产生相似的初始输出。但这不是决定论的，硬件相同，软件可以完全不同。\n\n长期灌注的机理更像编程中的'依赖注入'。早期信息（尤其是童年）是核心依赖项，后面的所有认知模块都基于这些依赖构建。如果父母对食品的某些信念在童年被反复强化，它就成为了'系统库'，后面的所有判断都依赖它。\n\n发育的关键期很重要。神经可塑性在特定窗口期最强，过了这个窗口，信息仍然可以输入，但需要绕过已有的架构。这就是为什么青春期的模因入侵比童年难得多——不是因为信息质量差，而是因为需要先解耦已有的连接。"
    },
    {
        "instruction": "耦合定义为双射以外自由度，解耦和最小步更新测试循环，任何项目完美达成的存在性?",
        "output": "你的定义很清晰——把'耦合'从模糊的工程直觉变成了一个可度量的概念：两个系统之间不能通过一对一映射消除的自由度。\n\n但我想追问：双射本身的定义域是什么？如果你允许定义域随时间扩展，那曾经的耦合可能变成解耦。比如两个团队的接口，一开始 tightly coupled，但随着标准统一，变成了 loose coupling。这不是项目的变化，是映射的变化。\n\n关于'完美达成'的存在性：如果一个项目的目标函数本身是不可计算的（比如'提升用户体验'），那它就没有一个确定的完美点。完美依赖于对目标的精确定义。而目标的精确定义本身又是一个需要优化的过程。\n\n这形成了一个递归：\n定义目标 → 优化 → 发现目标不完整 → 重新定义 → ...\n\n循环什么时候终止？可能永远不终止，也可能在某一步达到了'足够精确'。但'足够'是谁定义的？"
    },
]

# ============================================================
# Instruction pool — diverse topics to cover
# ============================================================
INSTRUCTION_POOL = [
    # AI / ML topics
    "你如何看待当前大模型训练中的'过拟合'问题？模型在训练集上表现很好但泛化能力差，这和人类学习有什么相似之处吗？",
    "如果AI可以无限自监督训练（不依赖人类标注），它会发展出人类无法理解的表示方式吗？这可能吗？",
    "Transformer的注意力机制和信息论有什么关系？attention是不是在做某种信道容量优化？",
    "你觉得RLHF是真的能让AI对齐人类价值观，还是只是在输出层做表面修飾？本质问题能被解决吗？",
    "多模态AI的融合是在学习跨模态的同构映射，还是只是在学一个更复杂的单模态模型？",
    "AI的'创造力'是真的涌现，只是我们的观测粒度不够细？",
    "如果AGI出现了，它的第一反应会是什么？会探索自身能力，还是会先理解环境？",
    "大模型的'涌现能力'在什么尺度以上会出现？为什么会有这种尺度相变？",

    # Social science topics
    "社交媒体上的'舆论反转'现象，是信息传播的自然结果还是平台设计的产物？你能用一个简单的模型来解释吗？",
    "'内卷'的本质是什么？是资源有限，还是竞争规则的结构性问题？如果资源无限了，内卷会消失吗？",
    "为什么社会制度变革这么难？是利益集团阻挠，还是人类认知结构的限制？",
    "信任在社会中是如何建立的？从博弈论角度，重复博弈可以解释合作，但现实中的信任远超这个范围。",
    "'阶层流动'在数字时代是加速了还是减缓了？算法推荐是打破了信息壁垒还是制造了新的壁垒？",
    "为什么'爱具体的人而不是抽象的人'这句话有力量？它触及了人性的什么？",
    "社会运动的成败由什么决定？是组织力，是叙事能力，还是时机？这三者之间的关系是什么？",

    # Math / Physics topics
    "范畴论中的'自然变换'概念，能不能用来描述不同数学分支之间的统一？什么条件下两个理论是同构的？",
    "'熵'这个概念在信息论、热力学、社会学中都有出现，它们是同一个东西的不同表述吗？",
    "如果物理定律可以用一个简洁的公式表达，为什么宇宙还会如此复杂？简化的底层原理和复杂的涌现现象之间是什么关系？",
    "数学是发现的还是发明的？如果外星文明有数学，他们的数学会和我们的同构吗？",
    "混沌系统中的'初值敏感性'在生物学中怎么理解？生物系统如何在不确定的初值下保持稳定？",
    "'对称性破缺'在社会科学中能找到对应吗？比如文化分化？",

    # Philosophy / Methodology topics
    "'第一性原理'思维是真的有效，还是只是事后合理化？从第一性原理出发推导和启发式搜索，哪个更高效？",
    "知识的边界在哪里？什么问题是原则上不可回答的，什么是暂时不可回答的？",
    "自我意识是'硬问题'吗？如果一个系统能完美模拟自我意识，它还需要真正的意识吗？",
    "因果关系和相关性，为什么因果比相关更难学习？人类是不是天生就有因果直觉？",
    "'还原论'和'整体论'哪个更正确？还是说它们在不同粒度下都成立？",
    "判断一个想法的价值，标准是什么？可证伪性？有用性？简洁性？这些标准本身怎么评估？",

    # Meta / Self-reflection topics
    "你怎么看待'思考的思考'——元认知在问题解决中的作用？什么时候应该停下来反思而不是继续执行？",
    "一个系统要'自主'到什么程度才算自主？自动回复邮件是自主，那自动修改回复规则呢？",
    "'学习'的本质是什么？是更新参数，是改变结构，还是两者都不是？",
    "当你说'我不知道'的时候，这是真实的不知道，还是对对话的终止策略？你怎么区分？",
    "人类和AI的共同点是都能从经验中学习。本质区别是什么？是训练数据的规模，是反馈信号的性质，还是架构本身？",
]


def call_hermes(messages, model="Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit",
                temperature=0.6, max_tokens=2048, top_p=0.9):
    """Call the local LLM API."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
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
    except urllib.error.URLError as e:
        print(f"API error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None


def generate_pair(instruction, few_shot_context, temperature=0.6):
    """Generate one synthetic Q&A pair."""
    messages = [
        {"role": "system", "content":
         "你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、"
         "接受质疑并修正。"
         "多用'可能'、'是否'、'呢'、'如果'、'但是'。"
         "不急于下结论。"
         "直接回答，不需要展示思考过程。"}
    ]

    # Add few-shot examples
    for ex in few_shot_context:
        messages.append({"role": "user", "content": ex["instruction"]})
        messages.append({"role": "assistant", "content": ex["output"]})

    messages.append({"role": "user", "content": instruction})

    response = call_hermes(messages, temperature=temperature)
    return response


def main():
    parser = argparse.ArgumentParser(description="Synthetic Persona Data Generator")
    parser.add_argument("--count", type=int, default=20, help="Number of samples to generate")
    parser.add_argument("--temperature", type=float, default=0.5, help="Sampling temperature")
    parser.add_argument("--few-shot", type=int, default=3, help="Number of few-shot exemplars")
    parser.add_argument("--output", default="synthetic_samples.jsonl", help="Output file")
    parser.add_argument("--seed-instructions", type=int, default=0,
                        help="Use first N instructions from pool (0 = random)")
    parser.add_argument("--existing", type=str, default="",
                        help="Path to existing samples to avoid duplicates")
    args = parser.parse_args()

    # Load existing to avoid duplicates
    existing_instructions = set()
    if args.existing:
        try:
            with open(args.existing, "r") as f:
                for line in f:
                    obj = json.loads(line)
                    existing_instructions.add(obj["instruction"][:80])
        except FileNotFoundError:
            pass

    # Select exemplars for few-shot
    exemplars = STYLE_EXEMPLARS[:args.few_shot]

    # Select instructions
    if args.seed_instructions > 0:
        instructions = INSTRUCTION_POOL[:args.seed_instructions]
    else:
        import random
        instructions = INSTRUCTION_POOL.copy()
        random.shuffle(instructions)

    # Filter out duplicates
    instructions = [i for i in instructions if i[:80] not in existing_instructions]

    print(f"Generating {min(args.count, len(instructions))} samples...")
    print(f"Temperature: {args.temperature}, Few-shot exemplars: {args.few_shot}")
    print(f"Available instructions: {len(instructions)}")
    print("=" * 60)

    results = []
    for i, instr in enumerate(instructions[:args.count]):
        print(f"\n[{i+1}/{min(args.count, len(instructions))}] Generating...")
        print(f"  Instruction: {instr[:80]}...")

        output = generate_pair(instr, exemplars, temperature=args.temperature)

        if output:
            # Strip thinking process if present
            output = strip_qwen_thinking(output)

            # Clean up
            output = output.strip()

            result = {
                "instruction": instr,
                "input": "",
                "output": output,
                "metadata": {
                    "category": "synthetic",
                    "source": "hermes_api",
                    "label": "persona_style",
                    "temperature": args.temperature,
                    "few_shot": args.few_shot,
                    "index": i,
                }
            }
            results.append(result)
            print(f"  Length: {len(output)} chars")
            print(f"  First 120 chars: {output[:120]}...")

            # Save incrementally
            with open(args.output, "a") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        else:
            print(f"  FAILED to generate")

        # Rate limiting
        time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"Generated {len(results)} samples -> {args.output}")
    print(f"\nTo score: python persona_fidelity_scorer.py --score-only --sample \"$(head -1 {args.output} | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"output\"])')\"")


def strip_qwen_thinking(text: str) -> str:
    """Strip Qwen model's built-in thinking process from output."""
    import re
    patterns = [
        r'\(Start directly',
        r'\(\*Start\*',
        r"Here's my response:",
        r"Here is my response:",
        r'---',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return text[match.end():].strip()

    thinking_match = re.search(r"Here's a thinking process:", text)
    if thinking_match:
        chinese_text = re.search(r'[一-鿿].{50,}', text[thinking_match.start():])
        if chinese_text:
            return text[thinking_match.start() + chinese_text.start():].strip()

    return text


if __name__ == "__main__":
    main()
