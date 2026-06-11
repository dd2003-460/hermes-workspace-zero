#!/usr/bin/env python3
"""
Eval baseline: compare base model vs persona prompt vs (potential) LoRA.

Tests the same questions with:
1. Base model (no persona)
2. Base model + chenglu personality prompt
3. With LoRA if LM Studio supports it

Usage:
    python eval_baseline.py
"""

import json
import urllib.request
import urllib.error
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


def call_api(messages, temperature=0.8, max_tokens=2048, adapter=None):
    """Call LM Studio API."""
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if adapter:
        data["lora_adapter"] = adapter

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"API error: {e}", file=sys.stderr)
        return None


def eval_setup():
    """Test each setup and save results."""
    results = {
        "questions": TEST_QUESTIONS,
        "models": {},
    }

    # --- Setup 1: Base model ---
    print("=" * 60)
    print("Setup 1: Base model (no persona)")
    print("=" * 60)
    base_responses = {}
    for i, q in enumerate(TEST_QUESTIONS):
        print(f"\nQ{i+1}: {q[:40]}...")
        messages = [{"role": "user", "content": q}]
        resp = call_api(messages)
        if resp and "choices" in resp:
            text = resp["choices"][0]["message"]["content"]
            base_responses[i] = text
            print(f"  Length: {len(text)} chars")
            print(f"  First 200: {text[:200]}...")
        else:
            print("  FAILED")
        time.sleep(1)
    results["models"]["base"] = base_responses

    # --- Setup 2: + Persona prompt ---
    print("\n" + "=" * 60)
    print("Setup 2: Base model + Chenglu Persona Prompt")
    print("=" * 60)
    persona_responses = {}
    for i, q in enumerate(TEST_QUESTIONS):
        print(f"\nQ{i+1}: {q[:40]}...")
        messages = [
            {"role": "system", "content": PERSONA_PROMPT},
            {"role": "user", "content": q},
        ]
        resp = call_api(messages)
        if resp and "choices" in resp:
            text = resp["choices"][0]["message"]["content"]
            persona_responses[i] = text
            print(f"  Length: {len(text)} chars")
            print(f"  First 200: {text[:200]}...")
        else:
            print("  FAILED")
        time.sleep(1)
    results["models"]["persona_prompt"] = persona_responses

    # --- Setup 3: With LoRA (if supported) ---
    # LM Studio LoRA API support depends on version. Try it.
    print("\n" + "=" * 60)
    print("Setup 3: With LoRA adapter (testing support)")
    print("=" * 60)

    lora_path = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/lora_training/adapters.safetensors"
    lora_responses = {}

    # First, test if the API accepts lora_adapter parameter
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/models",
            data=json.dumps({}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            models_data = json.loads(resp.read())
            print(f"Available models: {len(models_data.get('data', []))}")
    except Exception as e:
        print(f"Could not list models: {e}")

    # Try to load the adapter
    print(f"\nTrying to load LoRA: {lora_path}")
    print(f"Adapter size: {122} MB")

    for i, q in enumerate(TEST_QUESTIONS):
        print(f"\nQ{i+1}: {q[:40]}...")
        messages = [{"role": "user", "content": q}]

        # Try with LoRA
        resp = call_api(messages, adapter=lora_path)
        if resp and "choices" in resp:
            text = resp["choices"][0]["message"]["content"]
            lora_responses[i] = text
            print(f"  Length: {len(text)} chars")
            print(f"  First 200: {text[:200]}...")
        else:
            # If LoRA failed, try without
            print("  LoRA may not be supported, trying without...")
            resp = call_api(messages)
            if resp and "choices" in resp:
                text = resp["choices"][0]["message"]["content"]
                lora_responses[i] = text + " [LORA_NOT_APPLIED]"
                print(f"  (No LoRA) Length: {len(text)} chars")
            else:
                print("  FAILED")
        time.sleep(1)
    results["models"]["lora"] = lora_responses

    # Save results
    output_path = "/Users/a1-6/Desktop/workspace/projects/D1-persona-align/eval_results/eval_baseline_results.json"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n\nResults saved to: {output_path}")

    # Print quick comparison
    print("\n" + "=" * 60)
    print("Quick length comparison:")
    print("=" * 60)
    for i, q in enumerate(TEST_QUESTIONS):
        base_len = len(base_responses.get(i, ""))
        persona_len = len(persona_responses.get(i, ""))
        lora_len = len(lora_responses.get(i, ""))
        print(f"Q{i+1}: base={base_len}, persona={persona_len}, lora={lora_len}")


if __name__ == "__main__":
    eval_setup()
