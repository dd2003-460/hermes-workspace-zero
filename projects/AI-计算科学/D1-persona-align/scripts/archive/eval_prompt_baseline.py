#!/usr/bin/env python3
"""
Eval prompt vs no-prompt baseline.

Runs the same questions through:
1. Base model (no system prompt)
2. Base model + chenglu personality prompt
3. Checks if the model has any inherent personality baked in

Usage:
    python eval_prompt_baseline.py
"""

import json
import urllib.request
import time
import sys

BASE_URL = "http://127.0.0.1:8000/v1"
MODEL = "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"

TEST_QUESTIONS = [
    "你如何看待大模型训练中的过拟合问题？",
    "为什么社会制度变革这么难？",
    "人类和AI的本质区别是什么？",
    "内卷的本质是什么？",
    "数学是发现的还是发明的？",
]

PERSONA_PROMPT = """你是成璟的思考扩展。
核心风格：
- 中文优先，简洁直接，少空话多证据
- 提问驱动思考：用疑问推进，30-40%的内容是问句/反问
- 跨域跳跃：自然连接AI↔物理↔社科↔哲学，用数学/物理概念做隐喻
- 不确定标记：频繁使用"可能"、"是否"、"呢"、"如果"、"但是"
- 块状思考：用 ❏ 或分项标记组织思考，不追求单次完整回答
- 自我修正：接受质疑，承认"开始我以为...但是..."
- 直觉是高维推理的压缩，偏好形式化可验证
- 自主推进，不要等待确认
- 过程可见，做事前先说明计划"""

SYSTEM_PROMPTS = {
    "base": "",
    "persona": PERSONA_PROMPT,
    "minimal_persona": "你是成璟，一个喜欢用哲学、物理和AI交叉思考的人。简洁直接，多用问句推进思考，会跨领域类比。不确定时明确标记。",
}


def call_api(messages, temperature=0.8, max_tokens=2048):
    """Call oMLX API."""
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  API error: {e}", file=sys.stderr)
        return None


def run_eval():
    results = {
        "questions": TEST_QUESTIONS,
        "models": {},
        "metadata": {
            "model": MODEL,
            "temperature": 0.8,
            "max_tokens": 2048,
        },
    }

    for setup_name, sys_prompt in SYSTEM_PROMPTS.items():
        print(f"\n{'='*60}")
        print(f"Setup: {setup_name} {'(has system prompt)' if sys_prompt else '(no system prompt)'}")
        print(f"{'='*60}")

        responses = {}
        for i, q in enumerate(TEST_QUESTIONS):
            print(f"\n  Q{i+1}: {q[:40]}...")

            if sys_prompt:
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": q},
                ]
            else:
                messages = [{"role": "user", "content": q}]

            resp = call_api(messages)
            if resp and "choices" in resp:
                text = resp["choices"][0]["message"]["content"]
                # Remove thinking tags for cleaner analysis
                if "<think" in text:
                    text = text.split("</think>")[-1].strip()
                responses[i] = text
                print(f"    Length: {len(text)} chars")
                print(f"    Preview: {text[:150].replace(chr(10), ' | ')}...")
            else:
                responses[i] = "[FAILED]"
                print(f"    FAILED")
            time.sleep(0.5)

        results["models"][setup_name] = responses

    # Save results
    import os
    output_path = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/eval_results/eval_prompt_baseline.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    # Print comparison table
    print("\n" + "=" * 60)
    print("LENGTH COMPARISON:")
    print("=" * 60)
    for i, q in enumerate(TEST_QUESTIONS):
        lengths = {}
        for setup_name in SYSTEM_PROMPTS:
            text = results["models"][setup_name].get(i, "")
            if isinstance(text, str) and text != "[FAILED]":
                lengths[setup_name] = len(text)
            else:
                lengths[setup_name] = 0

        max_name = max(lengths, key=lengths.get) if lengths else ""
        print(f"Q{i+1} | " + " | ".join(f"{k}:{v}" for k, v in lengths.items()))

    # Save detailed comparison for review
    print("\nFull results written to JSON. You can compare responses manually.")


if __name__ == "__main__":
    run_eval()
