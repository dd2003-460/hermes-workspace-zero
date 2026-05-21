#!/usr/bin/env python3
"""
Quick baseline: test base model vs persona prompt with oMLX API.

Runs 3 questions to get a quick feel for the difference.
"""

import json
import urllib.request
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8000/v1"
MODEL = "Qwen3.6-35B-A3B-Abliterated-Heretic-MLX-6bit"

# Use only 3 quick questions for baseline
TEST_QUESTIONS = [
    ("philosophy", "人类和AI的本质区别是什么？"),
    ("science", "数学是发现的还是发明的？"),
    ("society", "内卷的本质是什么？"),
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


def call_api(messages, temperature=0.8, max_tokens=1024):
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


# Run baseline
results = {}

for label, question in TEST_QUESTIONS:
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    # No persona
    resp_no = call_api([{"role": "user", "content": question}])
    if resp_no and "choices" in resp_no:
        text_no = resp_no["choices"][0]["message"]["content"]
        # Strip thinking
        if "</think>" in text_no:
            text_no = text_no.split("</think>", 1)[1].strip()
        results[f"no_persona_{label}"] = text_no
        print(f"\n  [NO PERSONA] {len(text_no)} chars")
        print(f"  Preview: {text_no[:200]}")
    else:
        results[f"no_persona_{label}"] = "[FAILED]"

    time.sleep(1)

    # With persona
    resp_yes = call_api([
        {"role": "system", "content": PERSONA_SYSTEM},
        {"role": "user", "content": question},
    ])
    if resp_yes and "choices" in resp_yes:
        text_yes = resp_yes["choices"][0]["message"]["content"]
        if "</think>" in text_yes:
            text_yes = text_yes.split("</think>", 1)[1].strip()
        results[f"with_persona_{label}"] = text_yes
        print(f"\n  [WITH PERSONA] {len(text_yes)} chars")
        print(f"  Preview: {text_yes[:200]}")
    else:
        results[f"with_persona_{label}"] = "[FAILED]"

    time.sleep(0.5)

# Save
output = os.path.join(os.path.dirname(__file__), "eval_results", "quick_baseline.json")
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to: {output}")

# Length comparison
print(f"\n{'='*60}")
print("LENGTH COMPARISON")
print(f"{'='*60}")
for label, _ in TEST_QUESTIONS:
    no_p = len(results.get(f"no_persona_{label}", ""))
    with_p = len(results.get(f"with_persona_{label}", ""))
    print(f"  {label}: no_persona={no_p}, with_persona={with_p}, diff={with_p - no_p}")
