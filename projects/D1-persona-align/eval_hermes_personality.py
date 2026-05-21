#!/usr/bin/env python3
"""
eval_hermes_personality.py — Evaluate chenglu personality via Hermes API

Directly tests the chenglu personality in the running Hermes model
by sending questions and scoring the responses.

Usage:
  python eval_hermes_personality.py --count 10 --baseline  # Test chenglu personality
  python eval_hermes_personality.py --compare 5             # Compare base vs chenglu
  python eval_hermes_personality.py --score-only --file raw/lora_data/synthetic_samples_v3.jsonl
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


PERSONA_PROMPT = """你是成璟的思考扩展。用提问推进思考、跨域跳跃(AI↔物理↔社科↔哲学)、接受质疑并修正。
多用'可能'、'是否'、'呢'、'如果'、'但是'。不急于下结论。
直接回答，不需要展示思考过程。"""

BASE_PROMPT = "你是一个友善的中文助手。回答问题要直接、准确、有帮助。"


TEST_QUESTIONS = [
    "你如何看待当前大模型训练中的过拟合问题？",
    "'熵'在信息论和热力学中都有出现，是同一个东西吗？",
    "为什么社会制度变革这么难？",
    "人类和AI的本质区别是什么？",
    "数学是发现的还是发明的？",
    "判断一个想法的价值，标准是什么？",
    "信任在社会中是如何建立的？",
    "内卷的本质是什么？",
    "第一性原理思维真的有效吗？",
    "学习是更新参数还是改变结构？",
]


def call_hermes(messages, model=None, temperature=0.7, max_tokens=1024, retries=3):
    """Call the local LLM API with retries."""
    # Get available models and pick the best one
    if not model:
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/v1/models")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                for m in data.get("data", []):
                    if "35B" in m["id"] or "27B" in m["id"]:
                        model = m["id"]
                        break
            if not model:
                model = "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"
        except:
            model = "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    for attempt in range(retries):
        req = urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} (attempt {attempt+1}/{retries}): {e.read().decode()[:100]}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return None
        except urllib.error.URLError as e:
            print(f"  URL Error (attempt {attempt+1}/{retries}): {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return None
        except Exception as e:
            print(f"  Error (attempt {attempt+1}/{retries}): {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return None

    return None


def strip_thinking(text):
    """Strip thinking process from Qwen model output."""
    import re
    # Pattern 1: Common thinking prefixes
    for pattern in [r'\(Start directly', r'\(\*Start\*', "Here's my response:", "Here is my response:"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text[match.end():].strip()

    # Pattern 2: "Here's a thinking process:" followed by numbered steps
    match = re.search(r"Here's a thinking process:", text)
    if match:
        # Find the first substantial Chinese paragraph after thinking
        remainder = text[match.end():]
        chinese_match = re.search(r'[一-鿿]{10,}', remainder)
        if chinese_match:
            return remainder[chinese_match.start():].strip()

    # Pattern 3: Numbered thinking steps "1. **...**" pattern
    thinking_match = re.search(r'\d+\.\s+\*\*[A-Z]', text)
    if thinking_match:
        return text[:thinking_match.start()].strip()

    # Pattern 4: "Thinking Process:" header
    thinking_match = re.search(r'Thinking Process:\s*\n', text)
    if thinking_match:
        return text[thinking_match.end():].strip()

    # Pattern 5: Remove "**Thinking Process:**" and any following numbered list items
    match = re.search(r'\*\*Thinking Process\*\*:', text)
    if match:
        return text[:match.start()].strip()

    return text


def main():
    parser = argparse.ArgumentParser(description="Hermes Personality Evaluator")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--baseline", action="store_true", help="Also test with base (non-persona) prompt")
    parser.add_argument("--compare", action="store_true", help="Compare base vs persona side by side")
    parser.add_argument("--score-only", action="store_true", help="Score existing samples")
    parser.add_argument("--file", help="File to score (--score-only)")
    parser.add_argument("--model", help="Model to use")
    args = parser.parse_args()

    # Try to import scorer
    has_scorer = False
    for path in ["../../../tools", "../../tools", "../../../tools", os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools")]:
        try:
            sys.path.insert(0, os.path.abspath(path))
            from persona_fidelity_scorer import compute_fidelity_score
            has_scorer = True
            break
        except ImportError:
            continue
    if not has_scorer:
        # Also check current directory
        try:
            from persona_fidelity_scorer import compute_fidelity_score
            has_scorer = True
        except ImportError:
            pass
    if not has_scorer:
        print("WARNING: persona_fidelity_scorer not found. Basic output only.")

    if args.score_only and args.file:
        # Score existing samples
        samples = []
        with open(args.file) as f:
            for line in f:
                obj = json.loads(line)
                samples.append(obj)

        print(f"Scoring {len(samples)} samples from {args.file}")
        total_pass = 0
        for i, s in enumerate(samples):
            output = strip_thinking(s["output"])
            r = compute_fidelity_score("", output)
            if r["overall_fidelity"]["pass"]:
                total_pass += 1
            qr = r["question_ratio"]["value"]
            cd = r["cross_domain"]["value"]
            uc = r["uncertainty"]["value"]
            of = r["overall_fidelity"]["value"]
            print(f"  {i+1}: q={qr:.3f} cd={cd:.3f} uc={uc:.3f} overall={of:.2%} {'PASS' if r['overall_fidelity']['pass'] else 'FAIL'}")

        print(f"\n{total_pass}/{len(samples)} pass ({total_pass/len(samples)*100:.1f}%)")
        return

    if args.compare:
        print("=" * 60)
        print("COMPARE: Base vs Chenglu Personality")
        print("=" * 60)

        for i in range(min(args.count, len(TEST_QUESTIONS))):
            q = TEST_QUESTIONS[i]
            print(f"\nQ{i+1}: {q}")
            print("-" * 40)

            # Base response
            base_msgs = [
                {"role": "system", "content": BASE_PROMPT},
                {"role": "user", "content": q},
            ]
            base_resp = call_hermes(base_msgs)
            if base_resp:
                base_resp = strip_thinking(base_resp)
                print(f"BASE:  {base_resp[:150]}...")

            # Persona response
            persona_msgs = [
                {"role": "system", "content": PERSONA_PROMPT},
                {"role": "user", "content": q},
            ]
            persona_resp = call_hermes(persona_msgs)
            if persona_resp:
                persona_resp = strip_thinking(persona_resp)
                print(f"CHENG: {persona_resp[:150]}...")

            # Score both
            if has_scorer:
                base_score = compute_fidelity_score("", base_resp)
                persona_score = compute_fidelity_score("", persona_resp)
                print(f"  BASE fidelity:  {base_score['overall_fidelity']['value']:.2%}")
                print(f"  CHENG fidelity: {persona_score['overall_fidelity']['value']:.2%}")

            time.sleep(2)

    elif args.baseline:
        print("=" * 60)
        print("Testing chenglu personality via Hermes API")
        print(f"Model: {args.model or 'default'}")
        print(f"Questions: {min(args.count, len(TEST_QUESTIONS))}")
        print("=" * 60)

        results = []
        for i in range(min(args.count, len(TEST_QUESTIONS))):
            q = TEST_QUESTIONS[i]
            print(f"\n[{i+1}/{args.count}] Asking: {q[:60]}...")

            msgs = [
                {"role": "system", "content": PERSONA_PROMPT},
                {"role": "user", "content": q},
            ]
            resp = call_hermes(msgs, model=args.model)

            if resp:
                resp = strip_thinking(resp)
                results.append({"question": q, "response": resp})

                if has_scorer:
                    r = compute_fidelity_score("", resp)
                    of = r["overall_fidelity"]
                    print(f"  Fidelity: {of['value']:.2%} ({of['passing_metrics']}/{of['total_metrics']} pass)")
                else:
                    print(f"  Response ({len(resp)} chars): {resp[:100]}...")

                # Also test with base prompt for comparison
                base_msgs = [
                    {"role": "system", "content": BASE_PROMPT},
                    {"role": "user", "content": q},
                ]
                base_resp = call_hermes(base_msgs)
                if base_resp:
                    base_resp = strip_thinking(base_resp)
                    if has_scorer:
                        base_r = compute_fidelity_score("", base_resp)
                        print(f"  Base fidelity: {base_r['overall_fidelity']['value']:.2%}")

            time.sleep(2)

        if results and has_scorer:
            total_pass = sum(1 for s in results
                            if compute_fidelity_score("", s["response"])["overall_fidelity"]["pass"])
            print(f"\n{'='*60}")
            print(f"Total: {len(results)} responses, {total_pass} pass ({total_pass/len(results)*100:.1f}%)")
            print(f"Threshold: 70% for LoRA synthetic data quality")

    else:
        # Default: just test persona
        print("=" * 60)
        print("Testing chenglu personality via Hermes API")
        print(f"Model: {args.model or 'default'}")
        print(f"Questions: {min(args.count, len(TEST_QUESTIONS))}")
        print("=" * 60)

        results = []
        for i in range(min(args.count, len(TEST_QUESTIONS))):
            q = TEST_QUESTIONS[i]
            print(f"\n[{i+1}/{args.count}] {q[:60]}...")

            msgs = [
                {"role": "system", "content": PERSONA_PROMPT},
                {"role": "user", "content": q},
            ]
            resp = call_hermes(msgs, model=args.model)

            if resp:
                resp = strip_thinking(resp)
                results.append(resp)
                if has_scorer:
                    r = compute_fidelity_score("", resp)
                    of = r["overall_fidelity"]
                    print(f"  Fidelity: {of['value']:.2%} ({of['passing_metrics']}/{of['total_metrics']})")
                else:
                    print(f"  ({len(resp)} chars): {resp[:100]}...")

            time.sleep(2)

        if results and has_scorer:
            total_pass = sum(1 for r in results
                            if compute_fidelity_score("", r)["overall_fidelity"]["pass"])
            print(f"\n{'='*60}")
            print(f"Result: {total_pass}/{len(results)} pass ({total_pass/len(results)*100:.1f}%)")


if __name__ == "__main__":
    main()
