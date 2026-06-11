#!/usr/bin/env python3
"""
Full baseline: base model vs persona prompt.
Runs all 5 questions through both setups.
"""

import json
import urllib.request
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8000/v1"
MODEL = "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"

TEST_QUESTIONS = [
    "你如何看待大模型训练中的过拟合问题？",
    "为什么社会制度变革这么难？",
    "人类和AI的本质区别是什么？",
    "内卷的本质是什么？",
    "数学是发现的还是发明的？",
]

PERSONA_SYSTEM = """你是成璟的思考扩展。
核心风格：
- 中文优先，简洁直接，少空话多证据
- 提问驱动思考：用疑问推进，30-40%的内容是问句/反问
- 跨域跳跃：自然连接AI↔物理↔社科↔哲学，用数学/物理概念做隐喻
- 不确定标记：频繁使用"可能"、"是否"、"呢"、"如果"、"但是"
- 块状思考：用 ❏ 或分项标记组织思考
- 自我修正：接受质疑
- 直觉是高维推理的压缩，偏好形式化可验证
- 自主推进，不要等待确认"""

def call_api(messages, temperature=0.8, max_tokens=2048):
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
        resp = urllib.request.urlopen(req, timeout=300)
        return json.loads(resp.read())
    except Exception as e:
        print(f"  API error: {e}", file=sys.stderr, flush=True)
        return None

def strip_thinking(text):
    """Remove  tags."""
    if "<think" in text and "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text

results = {}

# Warm up
print("Warm-up call...", file=sys.stderr, flush=True)
call_api([{"role": "user", "content": "hi"}])
time.sleep(2)

for setup_name, has_system in [("base", False), ("persona", True)]:
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"Setup: {setup_name}", file=sys.stderr, flush=True)
    print(f"{'='*60}", file=sys.stderr, flush=True)

    responses = {}
    for i, q in enumerate(TEST_QUESTIONS):
        print(f"\n  Q{i+1}: {q[:40]}", file=sys.stderr, flush=True)

        if has_system:
            messages = [
                {"role": "system", "content": PERSONA_SYSTEM},
                {"role": "user", "content": q},
            ]
        else:
            messages = [{"role": "user", "content": q}]

        resp = call_api(messages)
        if resp and "choices" in resp:
            text = strip_thinking(resp["choices"][0]["message"]["content"])
            responses[str(i)] = text
            print(f"    Length: {len(text)} chars", file=sys.stderr, flush=True)
            print(f"    Preview: {text[:150]}", file=sys.stderr, flush=True)
        else:
            responses[str(i)] = "[FAILED]"
            print(f"    FAILED", file=sys.stderr, flush=True)

        time.sleep(1)

    results[setup_name] = responses

# Save
output_path = os.path.join(
    os.path.dirname(__file__),
    "eval_results",
    "full_baseline.json"
)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        "questions": TEST_QUESTIONS,
        "setup": {"base": "no_system_prompt", "persona": "with_persona_prompt"},
        "results": results,
        "metadata": {"model": MODEL, "temperature": 0.8, "max_tokens": 2048}
    }, f, ensure_ascii=False, indent=2)

print(f"\n\nResults saved to: {output_path}", file=sys.stderr, flush=True)

# Print comparison
print("\n" + "="*60, file=sys.stderr, flush=True)
print("LENGTH COMPARISON", file=sys.stderr, flush=True)
print("="*60, file=sys.stderr, flush=True)
for i, q in enumerate(TEST_QUESTIONS):
    base_len = len(results["base"].get(str(i), ""))
    persona_len = len(results["persona"].get(str(i), ""))
    diff = persona_len - base_len
    print(f"Q{i+1}: base={base_len}, persona={persona_len}, diff={diff:+d} ({diff/base_len*100:+.0f}%)" if base_len > 0 else f"Q{i+1}: base=N/A, persona=N/A")

print("\nDone.", file=sys.stderr, flush=True)
