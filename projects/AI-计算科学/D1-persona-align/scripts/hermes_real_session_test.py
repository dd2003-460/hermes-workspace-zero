#!/usr/bin/env python3
"""Real Hermse Session Test — via actual Gateway API.

Usage:
    python3 scripts/hermes_real_session_test.py
"""

import json
import os
import sys
import urllib.request
import urllib.error

GATEWAY_URL = "http://127.0.0.1:8642/v1/chat/completions"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("Real Hermse Session Test via Gateway API")
    print("=" * 60)

    # Load persona-v3 prompt
    prompt_path = os.path.join(PROJECT_ROOT, "persona-v3-prompt.txt")
    print(f"\n[1] Loading persona-v3-prompt.txt...")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    print(f"    Length: {len(system_prompt)} chars")

    # User query
    query = "你觉得 persona-v3 对齐到成璐的意志，这个方向的真正价值是什么？"
    print(f"\n[2] User query: {query}")

    # Build request
    request_body = json.dumps({
        "model": "default",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    }, ensure_ascii=False).encode("utf-8")

    print(f"\n[3] Sending request to {GATEWAY_URL}...")
    print(f"    Request body: {len(request_body)} bytes")

    req = urllib.request.Request(
        GATEWAY_URL,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"    ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse response
    print(f"\n[4] Response received")
    choices = result.get("choices", [])
    if not choices:
        print(f"    ERROR: No choices in response", file=sys.stderr)
        print(f"    Full response: {json.dumps(result, ensure_ascii=False)[:500]}", file=sys.stderr)
        sys.exit(1)

    assistant_msg = choices[0].get("message", {})
    response_text = assistant_msg.get("content", "")
    print(f"    Assistant reply: {len(response_text)} chars")
    print(f"\n    --- Response preview ---")
    print(f"    {response_text[:500]}...")
    print(f"    --- End preview ---")

    usage = result.get("usage", {})
    print(f"\n    Tokens: prompt={usage.get('prompt_tokens')}, "
          f"completion={usage.get('completion_tokens')}, "
          f"total={usage.get('total_tokens')}")

    # Save response
    os.makedirs(os.path.join(PROJECT_ROOT, "eval_results"), exist_ok=True)
    response_record = {
        "test_type": "real_hermes_session",
        "gateway": "127.0.0.1:8642",
        "query": query,
        "system_prompt_length": len(system_prompt),
        "response_text": response_text,
        "response_length": len(response_text),
        "usage": usage,
        "timestamp": "2026-06-02",
    }
    record_path = os.path.join(PROJECT_ROOT, "eval_results", "hermes_real_session.json")
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(response_record, f, ensure_ascii=False, indent=2)
    print(f"\n[5] Response saved: {record_path}")

    # Save for evaluation
    response_file = os.path.join(PROJECT_ROOT, "eval_results", "hermes_real_response.txt")
    with open(response_file, "w", encoding="utf-8") as f:
        f.write(response_text)
    print(f"    Response text: {response_file}")

    print(f"\n" + "=" * 60)
    print(f"Real session test completed. Next: evaluate response.")
    print(f"Run: python3 unified_eval.py --prompt {response_file}")
    print(f"     python3 persona_v3_alignment_checker.py --score --file {response_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
