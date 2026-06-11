#!/usr/bin/env python3
"""
synthetic_data_generator_v3.py — Fast single-call generation

Strategy: Use a compact prompt that asks the model to answer multiple questions
in one go, formatted as numbered responses that we can parse afterwards.

Also tries a different approach: single high-quality sample with fewer exemplars
to reduce API payload and speed.
"""

import argparse
import json
import sys
import time
import re
import urllib.request
import urllib.error


STYLE_EXEMPLARS = [
    {
        "instruction": "耦合定义为双射以外自由度，解耦和最小步更新测试循环，任何项目完美达成的存在性?",
        "output": "你的定义很清晰——把'耦合'从模糊的工程直觉变成了一个可度量的概念：两个系统之间不能通过一对一映射消除的自由度。\n\n但我想追问：双射本身的定义域是什么？如果你允许定义域随时间扩展，那曾经的耦合可能变成解耦。比如两个团队的接口，一开始 tightly coupled，但随着标准统一，变成了 loose coupling。这不是项目的变化，是映射的变化。\n\n关于'完美达成'的存在性：如果一个项目的目标函数本身是不可计算的（比如'提升用户体验'），那它就没有一个确定的完美点。完美依赖于对目标的精确定义。而目标的精确定义本身又是一个需要优化的过程。\n\n这形成了一个递归：\n定义目标 → 优化 → 发现目标不完整 → 重新定义 → ...\n\n循环什么时候终止？可能永远不终止，也可能在某一步达到了'足够精确'。但'足够'是谁定义的？"
    },
]

INSTRUCTION_POOL = [
    # AI / ML
    "你如何看待当前大模型训练中的'过拟合'问题？模型在训练集上表现很好但泛化能力差，这和人类学习有什么相似之处吗？",
    "如果AI可以无限自监督训练（不依赖人类标注），它会发展出人类无法理解的表示方式吗？这可能吗？",
    "Transformer的注意力机制和信息论有什么关系？attention是不是在做某种信道容量优化？",
    "你觉得RLHF是真的能让AI对齐人类价值观，还是只是在输出层做表面修饰？本质问题能被解决吗？",
    "多模态AI的融合是在学习跨模态的同构映射，还是只是在学一个更复杂的单模态模型？",
    "大模型的'涌现能力'在什么尺度以上会出现？为什么会有这种尺度相变？",
    # Social
    "社交媒体上的'舆论反转'现象，是信息传播的自然结果还是平台设计的产物？",
    "'内卷'的本质是什么？是资源有限，还是竞争规则的结构性问题？",
    "为什么社会制度变革这么难？是利益集团阻挠，还是人类认知结构的限制？",
    "信任在社会中是如何建立的？从博弈论角度，重复博弈可以解释合作，但现实中的信任远超这个范围。",
    # Math / Physics
    "'熵'这个概念在信息论、热力学、社会学中都有出现，它们是同一个东西的不同表述吗？",
    "如果物理定律可以用一个简洁的公式表达，为什么宇宙还会如此复杂？",
    "数学是发现的还是发明的？如果外星文明有数学，他们的数学会和我们的同构吗？",
    "混沌系统中的'初值敏感性'在生物学中怎么理解？生物系统如何保持稳定？",
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
    "如果AGI出现了，它的第一反应会是什么？会探索自身能力，还是会先理解环境？",
    # More social
    "'阶层流动'在数字时代是加速了还是减缓了？算法推荐是打破了信息壁垒还是制造了新的壁垒？",
    "社会运动的成败由什么决定？是组织力，是叙事能力，还是时机？",
    # More math
    "范畴论中的'自然变换'概念，能不能用来描述不同数学分支之间的统一？",
    "混沌系统和生物系统的稳定性，这两个方向有什么共同的数学框架？",
    # More philosophy
    "知识的边界在哪里？什么问题是原则上不可回答的？",
    "因果关系和相关性，为什么因果比相关更难学习？",
    "你怎么看待'思考的思考'——元认知在问题解决中的作用？",
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
    """Generate one response for one instruction."""
    messages = [
        {"role": "system", "content":
         "你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、"
         "接受质疑并修正。多用'可能'、'是否'、'呢'、'如果'、'但是'。"
         "不急于下结论。直接回答，不需要展示思考过程。"},
        {"role": "user", "content": STYLE_EXEMPLARS[0]["instruction"]},
        {"role": "assistant", "content": STYLE_EXEMPLARS[0]["output"]},
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


def generate_batch_compact(instructions, temperature=0.5):
    """
    Compact batch: present all questions in a structured format,
    ask model to answer all in one response.
    """
    system_prompt = (
        "你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、"
        "接受质疑并修正。多用'可能'、'是否'、'呢'、'如果'、'但是'。"
        "不急于下结论。直接回答，不需要展示思考过程。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "请依次回答以下问题，每个回答都体现你的思考风格：\n\n" +
             "\n\n".join(f"{i+1}. {q}" for i, q in enumerate(instructions))},
    ]

    payload = json.dumps({
        "model": "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 8192,
        "top_p": 0.9,
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return None


def parse_batched_response(response, expected_count):
    """
    Parse a response where the model is expected to give numbered answers.
    Split by patterns like "回答 N:" or "N. " at the start of a line.
    """
    text = strip_thinking(response)

    # Try splitting by "回答 N:" pattern
    parts = re.split(r'回答\s+\d+[:：]\s*', text)
    if len(parts) >= expected_count:
        return [p.strip() for p in parts[:expected_count]]

    # Try splitting by "N. " at start of line (but not part of list items)
    parts = re.split(r'\n\d+\.\s+', text)
    # Clean up the numbers from the parts
    if len(parts) >= expected_count:
        return [p.strip() for p in parts[:expected_count]]

    # Try splitting by consecutive newlines + pattern
    # The model might format as "回答1" "回答2" without space
    parts = re.split(r'(?:^|\n)(?:回答)?\d+(?:、|[:：.])\s*', text)
    if len(parts) >= expected_count:
        return [p.strip() for p in parts[:expected_count]]

    # Fallback: return as one block
    return [text.strip()] if text.strip() else []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--mode", choices=["single", "batch"], default="batch",
                        help="single = one API call per sample; batch = all in one call")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--output", default="raw/lora_data/synthetic_samples_v3.jsonl")
    parser.add_argument("--existing", default="")
    args = parser.parse_args()

    # Load existing to avoid duplicates
    existing = set()
    for path in ["raw/lora_data/synthetic_samples.jsonl", "raw/lora_data/synthetic_samples_v2.jsonl", args.existing]:
        if path:
            try:
                with open(path) as f:
                    for line in f:
                        obj = json.loads(line)
                        existing.add(obj["instruction"][:80])
            except (FileNotFoundError, json.JSONDecodeError):
                pass

    # Filter
    pool = [i for i in INSTRUCTION_POOL if i[:80] not in existing]
    pool = pool[:args.count]

    if not pool:
        print("No new instructions available.")
        return

    print(f"Mode: {args.mode}")
    print(f"Generating {len(pool)} samples (temp={args.temperature})")
    print(f"Available pool: {len(INSTRUCTION_POOL)}, existing: {len(existing)}")
    print("=" * 60)

    results = []

    if args.mode == "single":
        for i, instr in enumerate(pool):
            print(f"\n[{i+1}/{len(pool)}] single call...")
            output = generate_single(instr, args.temperature)
            if output:
                output = output.strip()
                results.append({"instruction": instr, "input": "", "output": output,
                                "metadata": {"category": "synthetic", "source": "hermes_single",
                                            "label": "persona_style", "temp": args.temperature, "idx": i}})
                print(f"  OK ({len(output)} chars): {output[:80]}...")
            time.sleep(1.5)

    elif args.mode == "batch":
        # Try multiple batch calls
        batch_size = 5
        for batch_start in range(0, len(pool), batch_size):
            batch = pool[batch_start:batch_start + batch_size]
            idx = batch_start // batch_size + 1

            print(f"\nBatch {idx} ({len(batch)} questions):")
            for q in batch:
                print(f"  - {q[:70]}...")

            response = generate_batch_compact(batch, args.temperature)

            if response:
                outputs = parse_batched_response(response, len(batch))

                for i, instr in enumerate(batch):
                    output = outputs[i] if i < len(outputs) else ""
                    if not output:
                        continue

                    results.append({"instruction": instr, "input": "", "output": output.strip(),
                                    "metadata": {"category": "synthetic", "source": "hermes_batch_v3",
                                                "label": "persona_style", "temp": args.temperature,
                                                "batch_idx": idx, "in_batch": i}})
                    print(f"\n  [OK] {len(output.strip())} chars: {output.strip()[:80]}...")
            time.sleep(2)

    # Save
    with open(args.output, "w") as f:
        for s in results:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Total: {len(results)} samples -> {args.output}")

    # Quick score the first few
    if results:
        sys.path.insert(0, "../../../tools")
        from persona_fidelity_scorer import compute_fidelity_score

        total_pass = 0
        for i, s in enumerate(results[:min(5, len(results))]):
            score_result = compute_fidelity_score('', s["output"])
            if score_result["overall_fidelity"]["pass"]:
                total_pass += 1
        print(f"First {min(5, len(results))} scored: {total_pass}/{min(5, len(results))} pass")


if __name__ == "__main__":
    main()
