#!/usr/bin/env python3
"""T11: 重新S1/S2/S3盲生成（修后prompt）

执行 T11 任务：
1. 读取 C 三层 prompt（已有角色锚定）
2. 为每个场景生成 prompt（C 三层 + 场景 context）
3. 用 vLLM 生成 S1/S2/S3 回复
4. 保存结果到 tasks/experiments/t11-s1s2s3-output/

依赖：requests
"""

import json
import os
import time
from pathlib import Path

# vLLM 配置
VLLM_URL = "http://100.112.53.47:8000/v1/chat/completions"
VLLM_API_KEY = "sk-vllm-17L3d6z60EuhN1yW_bcRoynvDmxoAk1GKsF3QvSV9cY"
VLLM_MODEL = "qwen3.8-27b-w8a16"

# 文件路径
PROJECT_ROOT = Path("/Users/a1-6/Desktop/workspace/projects/AI-计算科学/D1-persona-align")
PROMPT_FILE = PROJECT_ROOT / "tasks/archive/c-three-layer-prompt.md"  # C 三层 prompt（已有角色锚定）
SCENARIO_DIRS = {
    "S1": PROJECT_ROOT / "tasks/scenario-raw/S1/S1-消费决策-硬件_context.md",
    "S2": PROJECT_ROOT / "tasks/scenario-raw/S2/S2-量化估算-元评估_context.md",
    "S3": PROJECT_ROOT / "tasks/scenario-raw/S3/S3-ML训练机制-CoT_context.md",
}
OUTPUT_DIR = PROJECT_ROOT / "tasks/experiments/t11-s1s2s3-output"


def call_vllm(messages: list, max_tokens: int = 2000, timeout: int = 120) -> str:
    """调用 vLLM 生成回复"""
    import urllib.request
    import urllib.error

    req = urllib.request.Request(
        VLLM_URL,
        data=json.dumps({
            "model": VLLM_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {VLLM_API_KEY}",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def load_prompt() -> str:
    """读取 C 三层 prompt"""
    return PROMPT_FILE.read_text(encoding="utf-8")


def load_scenario(scenario_id: str) -> str:
    """读取场景 context"""
    return SCENARIO_DIRS[scenario_id].read_text(encoding="utf-8")


def generate_for_scenario(scenario_id: str, base_prompt: str) -> str:
    """为指定场景生成回复"""
    context = load_scenario(scenario_id)

    # 构建完整 prompt：C 三层 + 场景 context
    full_prompt = f"""{base_prompt}

---

## 场景 Context

{context}

---

## 任务

基于以上三层画像和场景 context，以成璐身份回复用户。自然、直接、不装。"""

    print(f"[{scenario_id}] 生成中...")
    start = time.time()
    response = call_vllm([{"role": "user", "content": full_prompt}], max_tokens=2000)
    elapsed = time.time() - start
    print(f"[{scenario_id}] 完成（{elapsed:.1f}s，{len(response)} chars）")

    return response


def main():
    """主流程"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 读取 C 三层 prompt
    base_prompt = load_prompt()
    print(f"C 三层 prompt: {len(base_prompt)} chars")

    # 为 S1/S2/S3 生成回复
    for scenario_id in ["S1", "S2", "S3"]:
        output_file = OUTPUT_DIR / f"{scenario_id}.md"

        # 跳过已存在的文件
        if output_file.exists():
            print(f"[{scenario_id}] 已存在，跳过")
            continue

        # 生成并保存
        try:
            response = generate_for_scenario(scenario_id, base_prompt)
            output_file.write_text(
                f"# {scenario_id} 盲生成（T11，C 三层 prompt）\n\n{response}\n",
                encoding="utf-8",
            )
            print(f"[{scenario_id}] 已保存: {output_file}")
        except Exception as e:
            error_file = OUTPUT_DIR / f"{scenario_id}-error.md"
            error_file.write_text(f"# {scenario_id} 生成失败\n\n错误: {e}\n", encoding="utf-8")
            print(f"[{scenario_id}] 失败: {e}")

        # 避免过载，间隔 2s
        time.sleep(2)

    print("\nT11 完成")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"文件: {', '.join(str(f.name) for f in sorted(OUTPUT_DIR.iterdir()))}")


if __name__ == "__main__":
    main()
