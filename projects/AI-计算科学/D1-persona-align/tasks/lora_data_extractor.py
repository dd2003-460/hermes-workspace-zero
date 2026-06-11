#!/usr/bin/env python3
"""
lora_data_extractor.py — T5b LoRA 训练数据提取器

从对话存档中提取可用于 LoRA 微调的对话样本。

输出格式: instruction-output pairs (适合 alpaca/llama-fine-tune 格式)

Usage:
    python3 lora_data_extractor.py --input <conversation_json> --output <output.jsonl>
    python3 lora_data_extractor.py --input raw.md --output lora_samples.jsonl
    python3 lora_data_extractor.py --sources-dir <dir> --output all_samples.jsonl
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def extract_from_raw_md(filepath: str) -> list:
    """从 raw.md 提取训练样本。

    raw.md 是 55 条 bullet 点的想法集合。
    每条可视为 [context -> thought question -> partial answer + new question] 格式。

    这恰好符合 T2 分析的模式: [上下文] → [问题序列] → [部分回答+新疑问]
    """
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Track context category and build pairs
    current_context = ""
    current_context_items = []
    category = None

    for line in lines:
        stripped = line.strip()

        # Detect category header (e.g., "ai，信息论，优化idea")
        if stripped and not stripped.startswith('❏') and not stripped.startswith('https'):
            if stripped.endswith('idea') or stripped.endswith('交叉'):
                category = stripped

        # Extract ❏ items
        if stripped.startswith('❏'):
            item = stripped.lstrip('❏ ').strip()
            if item and len(item) > 10:  # Skip very short items
                # Create instruction-output pair
                # The ❏ item is both input (the idea) and output (the persona thinking)
                # We frame it as: "如何看待这个想法？" -> <original thinking>
                samples.append({
                    "instruction": f"关于【{category or '未知'}】，如何看待这个想法？\n\n{item}",
                    "output": item,
                    "category": category or "unknown",
                    "source": "raw.md",
                    "label": "persona_thought"
                })

    return samples


def extract_from_conversations(filepath: str) -> list:
    """从对话 JSON 提取训练样本。"""
    samples = []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'conversations' in data:
        convs = data.get('conversations', [])
        for conv in convs:
            rounds = conv.get('rounds', [])
            if isinstance(rounds, list) and len(rounds) >= 2:
                # Each round is [number, question, response]
                for round_data in rounds[:20]:  # Max 20 rounds per conversation
                    if (isinstance(round_data, list) and len(round_data) == 3):
                        _, question, response = round_data
                        samples.append({
                            "instruction": str(question)[:1000],
                            "output": str(response)[:2000],
                            "category": conv.get('topic', 'unknown')[:100],
                            "source": conv.get('file', 'unknown'),
                            "label": "conversation"
                        })

    return samples


def build_alpaca_format(samples: list) -> str:
    """转换为 alpaca 格式 (适合 llama-fine-tune / unsloth)。"""
    output = []
    for i, s in enumerate(samples):
        entry = {
            "instruction": s["instruction"],
            "input": "",
            "output": s["output"],
            "metadata": {
                "category": s.get("category", "unknown"),
                "source": s.get("source", "unknown"),
                "label": s.get("label", "unknown")
            }
        }
        output.append(json.dumps(entry, ensure_ascii=False))
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description="LoRA 训练数据提取器 (T5b)")
    parser.add_argument("--input", help="输入文件 (raw.md 或 conversation JSON)")
    parser.add_argument("--sources-dir", help="从目录下所有 JSON 提取")
    parser.add_argument("--output", required=True, help="输出 JSONL 文件")
    parser.add_argument("--sample-count", type=int, default=9999, help="最大样本数 (默认: 不限制)")

    args = parser.parse_args()

    all_samples = []

    if args.input:
        path = Path(args.input)
        if path.suffix == '.md':
            print(f"从 {args.input} (raw.md) 提取...")
            all_samples.extend(extract_from_raw_md(args.input))
        elif path.suffix == '.json':
            print(f"从 {args.input} (JSON) 提取...")
            all_samples.extend(extract_from_conversations(args.input))

    if args.sources_dir:
        print(f"从目录 {args.sources_dir} 提取...")
        sources_dir = Path(args.sources_dir)
        for json_file in sources_dir.glob("**/*.json"):
            try:
                all_samples.extend(extract_from_conversations(str(json_file)))
            except Exception as e:
                print(f"  跳过 {json_file}: {e}")

    # Limit samples
    if len(all_samples) > args.sample_count:
        all_samples = all_samples[:args.sample_count]

    # Build output
    output_text = build_alpaca_format(all_samples)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"\n完成: 共 {len(all_samples)} 条样本，写入 {args.output}")

    # Summary
    categories = {}
    sources = {}
    for s in all_samples:
        cat = s.get('category', 'unknown')[:20]
        src = s.get('source', 'unknown')[:30]
        categories[cat] = categories.get(cat, 0) + 1
        sources[src] = sources.get(src, 0) + 1

    print(f"\n按类别分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat}: {count}")
    print(f"\n按来源分布:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1])[:10]:
        print(f"  {src}: {count}")


if __name__ == "__main__":
    main()
